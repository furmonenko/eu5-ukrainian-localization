#!/usr/bin/env python3
"""
GUI інструмент для редагування локалізації EU5.
Використовує Tkinter для простоти встановлення.
"""

import re
import sys
import json
import codecs
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass


@dataclass
class LocalizationEntry:
    """Рядок локалізації."""
    file_path: str
    line_number: int
    key: str
    version: str
    value: str
    category: str
    is_translated: bool


# Regex patterns
# Формат:  KEY:0 "value" або  KEY: "value" (без версії)
LINE_PATTERN = re.compile(r'^(\s*)([A-Za-z0-9_]+):(\d*)\s*"(.*)"\s*$')
CYRILLIC_PATTERN = re.compile(r'[а-яА-ЯіІїЇєЄґҐ]')
TAG_PATTERNS = [
    re.compile(r'\$[^$]+\$'),  # $VAR$, $flavor_eng.240.historical_info$, $var|format$ тощо
    re.compile(r'\[.*?\]'),  # [GetName], [ROOT.GetCountry.Custom('...')] тощо
    re.compile(r'#[A-Z]+(?::[^\s\]]+)?'),  # #R, #ONCLICK:..., #TOOLTIP:... тощо
    re.compile(r'#!'),  # #! закриваючий тег
    re.compile(r'@[a-z_]+!'),  # @icon!
    re.compile(r'\\n'),  # \n переноси рядків
]

# Шлях до файлу конфігурації
CONFIG_FILE = Path(__file__).parent / '.localization_gui_config.json'

# Доступні мови для референсу
AVAILABLE_LANGUAGES = ['english', 'french', 'german', 'spanish', 'russian', 'chinese', 'japanese', 'korean']


def is_technical_string(value: str) -> bool:
    """Перевіряє чи рядок є технічним (не потребує перекладу)."""
    stripped = value.strip()

    if not stripped:
        return True

    # Перевіряємо чи рядок складається тільки з тегів
    clean = stripped
    for pattern in TAG_PATTERNS:
        clean = pattern.sub('', clean)

    # Видаляємо пробіли та пунктуацію що залишились між тегами
    clean = re.sub(r'[\s\,\.\:\;\-\+\=\%\(\)\/\\\'\"]+', '', clean)

    if not clean:
        return True

    # UPPER_SNAKE_CASE
    if re.match(r'^[A-Z][A-Z0-9_]*$', clean):
        return True

    # lower_snake_case
    if re.match(r'^[a-z][a-z0-9_]*$', clean):
        return True

    # Mixed case without spaces - code identifier
    if re.match(r'^[A-Za-z][A-Za-z0-9_]*$', clean) and ' ' not in stripped:
        return True

    # Тільки цифри
    if re.match(r'^[\d]+$', clean):
        return True

    return False


def get_category(file_path: str) -> str:
    """Визначає категорію файла."""
    path_lower = file_path.lower().replace('\\', '/')

    if '/events/dhe/' in path_lower:
        return 'events/DHE'
    elif '/events/character/' in path_lower:
        return 'events/character'
    elif '/events/culture/' in path_lower:
        return 'events/culture'
    elif '/events/' in path_lower:
        return 'events/other'
    elif '/interfaces/' in path_lower:
        return 'interfaces'
    elif '/locations/' in path_lower:
        return 'locations'
    elif '/missions/' in path_lower:
        return 'missions'
    elif '/government/' in path_lower:
        return 'government'
    elif '/modifiers/' in path_lower:
        return 'modifiers'
    elif '/units/' in path_lower:
        return 'units'
    else:
        return 'other'


def is_translated(value: str) -> bool:
    """Перевіряє чи рядок перекладений або не потребує перекладу."""
    if is_technical_string(value):
        return True

    if CYRILLIC_PATTERN.search(value):
        return True

    clean = value
    for pattern in TAG_PATTERNS:
        clean = pattern.sub('', clean)
    clean = re.sub(r'[\s\d\W]', '', clean)

    if not clean:
        return True

    return False


def find_tags(text: str) -> List[str]:
    """Знаходить теги в тексті."""
    tags = []
    for pattern in TAG_PATTERNS:
        tags.extend(pattern.findall(text))
    return tags


class OriginalTextsDatabase:
    """База даних оригінальних текстів з гри."""

    def __init__(self):
        self.texts: Dict[str, str] = {}  # key -> value

    def scan(self, root_dir: Path, language: str = 'english', progress_callback=None) -> int:
        """Сканує оригінальні файли локалізації."""
        self.texts.clear()

        # Шукаємо файли для обраної мови
        pattern = f'*_l_{language}.yml'
        yml_files = list(root_dir.rglob(pattern))
        total = len(yml_files)

        for i, yml_file in enumerate(yml_files):
            if progress_callback:
                progress_callback(i + 1, total, str(yml_file.name))

            self._parse_file(yml_file)

        return len(self.texts)

    def _parse_file(self, file_path: Path):
        """Парсить один YML файл."""
        try:
            with open(file_path, 'rb') as f:
                raw = f.read()

            has_bom = raw.startswith(codecs.BOM_UTF8)
            content = raw[3:].decode('utf-8') if has_bom else raw.decode('utf-8')

            for line in content.splitlines():
                match = LINE_PATTERN.match(line)
                if match:
                    key = match.group(2)
                    value = match.group(4)
                    # Зберігаємо тільки якщо ще немає (перший знайдений має пріоритет)
                    if key not in self.texts:
                        self.texts[key] = value

        except Exception as e:
            print(f"Помилка читання {file_path}: {e}", file=sys.stderr)

    def get(self, key: str) -> Optional[str]:
        """Повертає оригінальний текст за ключем."""
        return self.texts.get(key)


class LocalizationDatabase:
    """База даних локалізації."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.entries: List[LocalizationEntry] = []
        self.file_cache: Dict[str, Tuple[List[str], bool]] = {}

    def scan(self, progress_callback=None) -> int:
        """Сканує всі файли локалізації."""
        self.entries.clear()
        self.file_cache.clear()

        yml_files = list(self.root_dir.rglob('*_l_english.yml'))
        total = len(yml_files)

        for i, yml_file in enumerate(yml_files):
            if progress_callback:
                progress_callback(i + 1, total, str(yml_file.name))

            self._parse_file(yml_file)

        return len(self.entries)

    def _parse_file(self, file_path: Path):
        """Парсить один YML файл."""
        try:
            with open(file_path, 'rb') as f:
                raw = f.read()

            has_bom = raw.startswith(codecs.BOM_UTF8)
            content = raw[3:].decode('utf-8') if has_bom else raw.decode('utf-8')
            lines = content.splitlines(keepends=True)

            self.file_cache[str(file_path)] = (lines, has_bom)

            category = get_category(str(file_path))

            for line_num, line in enumerate(lines):
                match = LINE_PATTERN.match(line)
                if match:
                    key = match.group(2)
                    version = match.group(3)
                    value = match.group(4)

                    entry = LocalizationEntry(
                        file_path=str(file_path),
                        line_number=line_num,
                        key=key,
                        version=version,
                        value=value,
                        category=category,
                        is_translated=is_translated(value)
                    )
                    self.entries.append(entry)

        except Exception as e:
            print(f"Помилка читання {file_path}: {e}", file=sys.stderr)

    def search(self, query: str = "", category: str = "all",
               untranslated_only: bool = False) -> List[LocalizationEntry]:
        """Шукає рядки за критеріями."""
        results = []
        query_lower = query.lower()

        for entry in self.entries:
            if category != "all" and entry.category != category:
                continue

            if untranslated_only and entry.is_translated:
                continue

            if query:
                if (query_lower not in entry.key.lower() and
                    query_lower not in entry.value.lower()):
                    continue

            results.append(entry)

        return results

    def get_context(self, entry: LocalizationEntry, lines_count: int = 3) -> List[Tuple[int, str, bool]]:
        """Отримує контекст навколо рядка."""
        if entry.file_path not in self.file_cache:
            return []

        lines, _ = self.file_cache[entry.file_path]
        start = max(0, entry.line_number - lines_count)
        end = min(len(lines), entry.line_number + lines_count + 1)

        result = []
        for i in range(start, end):
            is_current = (i == entry.line_number)
            result.append((i + 1, lines[i].rstrip(), is_current))

        return result

    def update_entry(self, entry: LocalizationEntry, new_value: str) -> bool:
        """Оновлює значення рядка."""
        if entry.file_path not in self.file_cache:
            return False

        lines, has_bom = self.file_cache[entry.file_path]

        match = LINE_PATTERN.match(lines[entry.line_number])
        if not match:
            return False

        indent = match.group(1)
        new_line = f'{indent}{entry.key}:{entry.version} "{new_value}"\n'
        lines[entry.line_number] = new_line

        try:
            content = ''.join(lines)
            with open(entry.file_path, 'wb') as f:
                if has_bom:
                    f.write(codecs.BOM_UTF8)
                f.write(content.encode('utf-8'))

            entry.value = new_value
            entry.is_translated = is_translated(new_value)

            return True
        except Exception as e:
            print(f"Помилка збереження: {e}", file=sys.stderr)
            return False

    def get_stats(self) -> Tuple[int, int]:
        """Повертає (всього, перекладено)."""
        total = len(self.entries)
        translated = sum(1 for e in self.entries if e.is_translated)
        return total, translated


class LocalizationApp:
    """Головний клас GUI застосунку."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("EU5 Локалізація - Редактор")

        self.db: Optional[LocalizationDatabase] = None
        self.originals_db: Optional[OriginalTextsDatabase] = None
        self.current_results: List[LocalizationEntry] = []
        self.current_entry: Optional[LocalizationEntry] = None
        self.modified_files: set = set()
        self.has_unsaved_changes: bool = False
        self.original_value: str = ""
        self._previous_selection: Optional[str] = None

        # Сортування
        self.sort_column: str = ""
        self.sort_reverse: bool = False

        self._load_config()
        self._setup_ui()
        self._setup_context_menus()
        self._bind_events()
        self._auto_detect_directories()
        self.root.after(500, self._auto_scan_on_startup)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_config(self):
        """Завантажує конфігурацію з файлу."""
        self.config = {
            'window_geometry': '1200x800',
            'mod_directory': '',
            'game_directory': '',
            'reference_language': 'english',
            'auto_scan': True,
        }
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.config.update(saved)
        except Exception:
            pass

        self.root.geometry(self.config['window_geometry'])
        self.root.minsize(900, 600)  # Мінімальний розмір вікна

    def _save_config(self):
        """Зберігає конфігурацію у файл."""
        try:
            self.config['window_geometry'] = self.root.geometry()
            self.config['mod_directory'] = self.mod_dir_var.get()
            self.config['game_directory'] = self.game_dir_var.get()
            self.config['reference_language'] = self.lang_var.get()
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def _on_close(self):
        """Обробка закриття вікна."""
        if self.has_unsaved_changes:
            result = messagebox.askyesnocancel(
                "Незбережені зміни",
                "Є незбережені зміни. Зберегти перед виходом?"
            )
            if result is None:
                return
            if result:
                self._save_entry()

        # Попередження про незакомічені файли
        if self.modified_files:
            files_count = len(self.modified_files)
            result = messagebox.askyesno(
                "Незакомічені зміни",
                f"Є {files_count} змінених файлів без git commit.\n\n"
                "Вийти без commit?"
            )
            if not result:
                return

        self._save_config()
        self.root.destroy()

    def _setup_ui(self):
        """Налаштування UI."""
        # Головний контейнер з grid для кращого масштабування
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Налаштовуємо grid weights для масштабування
        main_frame.grid_rowconfigure(2, weight=1)  # Результати + Редагування
        main_frame.grid_columnconfigure(0, weight=1)

        # === Панель директорій ===
        dirs_frame = ttk.LabelFrame(main_frame, text="Директорії", padding="5")
        dirs_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))

        # Рядок 1: Папка мода
        mod_row = ttk.Frame(dirs_frame)
        mod_row.pack(fill=tk.X, pady=2)

        ttk.Label(mod_row, text="Папка мода:", width=15).pack(side=tk.LEFT)
        self.mod_dir_var = tk.StringVar(value=self.config.get('mod_directory', ''))
        ttk.Entry(mod_row, textvariable=self.mod_dir_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(mod_row, text="Огляд...", command=self._browse_mod_directory).pack(side=tk.LEFT)

        # Рядок 2: Папка гри (оригінали)
        game_row = ttk.Frame(dirs_frame)
        game_row.pack(fill=tk.X, pady=2)

        ttk.Label(game_row, text="Папка гри:", width=15).pack(side=tk.LEFT)
        self.game_dir_var = tk.StringVar(value=self.config.get('game_directory', ''))
        ttk.Entry(game_row, textvariable=self.game_dir_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(game_row, text="Огляд...", command=self._browse_game_directory).pack(side=tk.LEFT)

        # Рядок 3: Мова референсу + Сканувати
        lang_row = ttk.Frame(dirs_frame)
        lang_row.pack(fill=tk.X, pady=2)

        ttk.Label(lang_row, text="Мова референсу:", width=15).pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.config.get('reference_language', 'english'))
        lang_combo = ttk.Combobox(lang_row, textvariable=self.lang_var, values=AVAILABLE_LANGUAGES,
                                   state='readonly', width=15)
        lang_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(lang_row, text="Сканувати (F5)", command=self._scan_all).pack(side=tk.LEFT, padx=20)

        self.status_label = ttk.Label(lang_row, text="")
        self.status_label.pack(side=tk.RIGHT)

        # === Панель пошуку ===
        search_frame = ttk.LabelFrame(main_frame, text="Пошук", padding="5")
        search_frame.grid(row=1, column=0, sticky='ew', pady=(0, 5))

        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill=tk.X, pady=2)

        ttk.Label(search_row1, text="Запит:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_row1, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(search_row1, text="Категорія:").pack(side=tk.LEFT, padx=(10, 0))
        self.category_var = tk.StringVar(value="all")
        self.category_combo = ttk.Combobox(search_row1, textvariable=self.category_var, width=20,
                                           state='readonly')
        self.category_combo['values'] = [
            'all', 'events/DHE', 'events/character', 'events/culture', 'events/other',
            'interfaces', 'locations', 'missions', 'government', 'modifiers', 'units', 'other'
        ]
        self.category_combo.pack(side=tk.LEFT, padx=5)

        self.untranslated_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(search_row1, text="Тільки неперекладені",
                        variable=self.untranslated_var).pack(side=tk.LEFT, padx=10)

        ttk.Button(search_row1, text="Пошук", command=self._do_search).pack(side=tk.LEFT, padx=5)

        # Прогрес-бар
        self.progress_frame = ttk.Frame(search_frame)
        self.progress_frame.pack(fill=tk.X, pady=(5, 0))

        self.progress_label = ttk.Label(self.progress_frame, text="Прогрес: --")
        self.progress_label.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(self.progress_frame, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=10)

        self.progress_percent = ttk.Label(self.progress_frame, text="")
        self.progress_percent.pack(side=tk.LEFT)

        # === PanedWindow для результатів та редагування ===
        paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned.grid(row=2, column=0, sticky='nsew', pady=(0, 5))

        # === Результати ===
        results_frame = ttk.LabelFrame(paned, text="Результати", padding="5")
        paned.add(results_frame, weight=1)

        tree_container = ttk.Frame(results_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ('key', 'value', 'category', 'file', 'status')
        self.results_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=12)

        self.results_tree.heading('key', text='Ключ', command=lambda: self._sort_column('key'))
        self.results_tree.heading('value', text='Значення', command=lambda: self._sort_column('value'))
        self.results_tree.heading('category', text='Категорія', command=lambda: self._sort_column('category'))
        self.results_tree.heading('file', text='Файл', command=lambda: self._sort_column('file'))
        self.results_tree.heading('status', text='Статус', command=lambda: self._sort_column('status'))

        self.results_tree.column('key', width=200)
        self.results_tree.column('value', width=300)
        self.results_tree.column('category', width=100)
        self.results_tree.column('file', width=150)
        self.results_tree.column('status', width=70)

        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(xscrollcommand=h_scrollbar.set)

        self.results_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        self.results_tree.tag_configure('translated', background='#d4edda')
        self.results_tree.tag_configure('untranslated', background='#f8d7da')

        self.results_count_label = ttk.Label(results_frame, text="")
        self.results_count_label.pack(side=tk.BOTTOM, fill=tk.X)

        # === Панель редагування ===
        edit_frame = ttk.LabelFrame(paned, text="Редагування", padding="5")
        paned.add(edit_frame, weight=1)

        # Контекст
        context_frame = ttk.Frame(edit_frame)
        context_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        ttk.Label(context_frame, text="Контекст (файл мода):").pack(anchor=tk.W)
        context_container = ttk.Frame(context_frame)
        context_container.pack(fill=tk.BOTH, expand=True)

        self.context_text = tk.Text(context_container, height=4, font=('Consolas', 9),
                                     state=tk.DISABLED, wrap=tk.NONE)
        context_h_scroll = ttk.Scrollbar(context_container, orient=tk.HORIZONTAL,
                                          command=self.context_text.xview)
        context_v_scroll = ttk.Scrollbar(context_container, orient=tk.VERTICAL,
                                          command=self.context_text.yview)
        self.context_text.configure(xscrollcommand=context_h_scroll.set,
                                     yscrollcommand=context_v_scroll.set)

        self.context_text.grid(row=0, column=0, sticky='nsew')
        context_v_scroll.grid(row=0, column=1, sticky='ns')
        context_h_scroll.grid(row=1, column=0, sticky='ew')
        context_container.grid_rowconfigure(0, weight=1)
        context_container.grid_columnconfigure(0, weight=1)

        # Дві колонки: Оригінал (референс) | Переклад (редагування)
        editor_row = ttk.Frame(edit_frame)
        editor_row.pack(fill=tk.BOTH, expand=True, pady=5)

        # Налаштовуємо grid для рівномірного розподілу
        editor_row.grid_columnconfigure(0, weight=1, uniform="editor")
        editor_row.grid_columnconfigure(1, weight=1, uniform="editor")
        editor_row.grid_rowconfigure(0, weight=1)

        # Оригінал з гри (read-only)
        orig_frame = ttk.Frame(editor_row)
        orig_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))

        orig_header = ttk.Frame(orig_frame)
        orig_header.pack(fill=tk.X)
        ttk.Label(orig_header, text="Оригінал (з гри):").pack(side=tk.LEFT)
        self.orig_lang_label = ttk.Label(orig_header, text="[english]", foreground='gray')
        self.orig_lang_label.pack(side=tk.RIGHT)

        self.original_text = tk.Text(orig_frame, height=5, font=('Consolas', 11),
                                      state=tk.DISABLED, wrap=tk.WORD, bg='#f5f5f5')
        self.original_text.pack(fill=tk.BOTH, expand=True)

        # Переклад (editable)
        trans_frame = ttk.Frame(editor_row)
        trans_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))

        trans_header = ttk.Frame(trans_frame)
        trans_header.pack(fill=tk.X)
        ttk.Label(trans_header, text="Переклад:").pack(side=tk.LEFT)
        self.char_count_label = ttk.Label(trans_header, text="[0 символів]")
        self.char_count_label.pack(side=tk.RIGHT)

        self.translation_text = tk.Text(trans_frame, height=5, font=('Consolas', 11),
                                         wrap=tk.WORD, undo=True)
        self.translation_text.pack(fill=tk.BOTH, expand=True)

        # Теги
        tags_row = ttk.Frame(edit_frame)
        tags_row.pack(fill=tk.X)

        self.tags_label = ttk.Label(tags_row, text="Теги: (немає)")
        self.tags_label.pack(side=tk.LEFT)

        ttk.Button(tags_row, text="Копіювати теги", command=self._copy_tags).pack(side=tk.RIGHT, padx=5)

        # Кнопки
        buttons_frame = ttk.Frame(edit_frame)
        buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(buttons_frame, text="Зберегти (Ctrl+S)", command=self._save_entry).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Зберегти і далі (Ctrl+Enter)",
                   command=self._save_and_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="← Копіювати оригінал", command=self._copy_original).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="← (Ctrl+P)", command=self._prev_entry).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="(Ctrl+N) →", command=self._next_entry).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Git Commit...", command=self._git_commit).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="Відкрити у редакторі",
                   command=self._open_in_editor).pack(side=tk.RIGHT, padx=5)

        # Статус-бар
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.statusbar_file = ttk.Label(self.statusbar, text="Файл: --", anchor=tk.W)
        self.statusbar_file.pack(side=tk.LEFT, padx=5)

        self.statusbar_position = ttk.Label(self.statusbar, text="Позиція: --", anchor=tk.CENTER)
        self.statusbar_position.pack(side=tk.LEFT, padx=20)

        self.statusbar_status = ttk.Label(self.statusbar, text="", anchor=tk.E)
        self.statusbar_status.pack(side=tk.RIGHT, padx=5)

        # Теги для підсвічування
        self.original_text.tag_configure('tag', foreground='#0066cc', font=('Consolas', 11, 'bold'))
        self.translation_text.tag_configure('tag', foreground='#0066cc', font=('Consolas', 11, 'bold'))
        self.context_text.tag_configure('current', background='#ffffcc')

    def _setup_context_menus(self):
        """Створює контекстні меню."""
        self.translation_menu = tk.Menu(self.root, tearoff=0)
        self.translation_menu.add_command(label="Вирізати (Ctrl+X)", command=self._cut_text)
        self.translation_menu.add_command(label="Копіювати (Ctrl+C)", command=self._copy_text)
        self.translation_menu.add_command(label="Вставити (Ctrl+V)", command=self._paste_text)
        self.translation_menu.add_separator()
        self.translation_menu.add_command(label="Вибрати все (Ctrl+A)", command=self._select_all)
        self.translation_menu.add_separator()
        self.translation_menu.add_command(label="Скасувати (Ctrl+Z)", command=self._undo)
        self.translation_menu.add_command(label="Повторити (Ctrl+Y)", command=self._redo)

        self.readonly_menu = tk.Menu(self.root, tearoff=0)
        self.readonly_menu.add_command(label="Копіювати (Ctrl+C)", command=self._copy_from_readonly)

    def _bind_events(self):
        """Прив'язка подій."""
        self.results_tree.bind('<<TreeviewSelect>>', self._on_result_select)
        self.results_tree.bind('<Double-1>', self._on_double_click)
        self.results_tree.bind('<Up>', self._on_tree_key_up)
        self.results_tree.bind('<Down>', self._on_tree_key_down)

        self.search_entry.bind('<Return>', lambda e: self._do_search())

        self.root.bind('<Control-s>', lambda e: self._save_entry())
        self.root.bind('<Control-n>', lambda e: self._next_entry())
        self.root.bind('<Control-p>', lambda e: self._prev_entry())
        self.root.bind('<Control-Return>', lambda e: self._save_and_next())
        self.root.bind('<F5>', lambda e: self._scan_all())
        self.root.bind('<Control-f>', lambda e: self._focus_search())
        self.root.bind('<Control-Home>', lambda e: self._go_to_first())
        self.root.bind('<Control-End>', lambda e: self._go_to_last())
        self.root.bind('<Escape>', lambda e: self._on_escape())

        self.translation_text.bind('<Control-c>', lambda e: self._copy_text())
        self.translation_text.bind('<Control-v>', lambda e: self._paste_text())
        self.translation_text.bind('<Control-x>', lambda e: self._cut_text())
        self.translation_text.bind('<Control-a>', lambda e: self._select_all())
        self.translation_text.bind('<Control-z>', lambda e: self._undo())
        self.translation_text.bind('<Control-y>', lambda e: self._redo())

        self.translation_text.bind('<Button-3>', self._show_translation_menu)
        self.original_text.bind('<Button-3>', self._show_readonly_menu)

        self.translation_text.bind('<KeyRelease>', self._on_translation_change)
        self.translation_text.bind('<KeyRelease>', self._highlight_tags_in_translation, add='+')

    # === Контекстне меню ===

    def _show_translation_menu(self, event):
        try:
            self.translation_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.translation_menu.grab_release()

    def _show_readonly_menu(self, event):
        self._readonly_widget = event.widget
        try:
            self.readonly_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.readonly_menu.grab_release()

    def _cut_text(self):
        try:
            self.translation_text.event_generate('<<Cut>>')
        except tk.TclError:
            pass
        return 'break'

    def _copy_text(self):
        try:
            self.translation_text.event_generate('<<Copy>>')
        except tk.TclError:
            pass
        return 'break'

    def _paste_text(self):
        try:
            self.translation_text.event_generate('<<Paste>>')
        except tk.TclError:
            pass
        return 'break'

    def _select_all(self):
        self.translation_text.tag_add('sel', '1.0', 'end')
        return 'break'

    def _undo(self):
        try:
            self.translation_text.edit_undo()
        except tk.TclError:
            pass
        return 'break'

    def _redo(self):
        try:
            self.translation_text.edit_redo()
        except tk.TclError:
            pass
        return 'break'

    def _copy_from_readonly(self):
        if hasattr(self, '_readonly_widget'):
            try:
                self._readonly_widget.event_generate('<<Copy>>')
            except tk.TclError:
                pass

    # === Навігація ===

    def _on_double_click(self, event):
        self.translation_text.focus_set()
        self.translation_text.tag_add('sel', '1.0', 'end')

    def _on_tree_key_up(self, event):
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            prev_item = self.results_tree.prev(item)
            if prev_item:
                self.results_tree.selection_set(prev_item)
                self.results_tree.see(prev_item)
                self._on_result_select(None)
        return 'break'

    def _on_tree_key_down(self, event):
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            next_item = self.results_tree.next(item)
            if next_item:
                self.results_tree.selection_set(next_item)
                self.results_tree.see(next_item)
                self._on_result_select(None)
        return 'break'

    def _on_escape(self):
        if self.has_unsaved_changes:
            result = messagebox.askyesno("Незбережені зміни", "Скасувати зміни?")
            if result:
                self.has_unsaved_changes = False
                self._update_title()
                if self.current_entry:
                    self._show_entry(self.current_entry)
        else:
            self.results_tree.focus_set()

    def _focus_search(self):
        """Фокусує поле пошуку (Ctrl+F)."""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
        return 'break'

    def _go_to_first(self):
        """Переходить до першого результату (Ctrl+Home)."""
        children = self.results_tree.get_children()
        if children:
            first_item = children[0]
            self.results_tree.selection_set(first_item)
            self.results_tree.see(first_item)
            self._on_result_select(None)
        return 'break'

    def _go_to_last(self):
        """Переходить до останнього результату (Ctrl+End)."""
        children = self.results_tree.get_children()
        if children:
            last_item = children[-1]
            self.results_tree.selection_set(last_item)
            self.results_tree.see(last_item)
            self._on_result_select(None)
        return 'break'

    def _prev_entry(self):
        selection = self.results_tree.selection()
        if not selection:
            return
        item = selection[0]
        prev_item = self.results_tree.prev(item)
        if prev_item:
            self.results_tree.selection_set(prev_item)
            self.results_tree.see(prev_item)
            self._on_result_select(None)

    def _next_entry(self):
        selection = self.results_tree.selection()
        if not selection:
            return
        item = selection[0]
        next_item = self.results_tree.next(item)
        if next_item:
            self.results_tree.selection_set(next_item)
            self.results_tree.see(next_item)
            self._on_result_select(None)

    # === Редактор ===

    def _on_translation_change(self, event=None):
        if not self.current_entry:
            return

        current_text = self.translation_text.get('1.0', 'end-1c')
        char_count = len(current_text)
        self.char_count_label['text'] = f"[{char_count} символів]"

        if char_count > 1000:
            self.char_count_label['foreground'] = 'red'
        elif char_count > 500:
            self.char_count_label['foreground'] = 'orange'
        else:
            self.char_count_label['foreground'] = ''

        if current_text != self.original_value:
            if not self.has_unsaved_changes:
                self.has_unsaved_changes = True
                self._update_title()
        else:
            if self.has_unsaved_changes:
                self.has_unsaved_changes = False
                self._update_title()

    def _highlight_tags_in_translation(self, event=None):
        self.translation_text.tag_remove('tag', '1.0', tk.END)
        text = self.translation_text.get('1.0', tk.END)
        for pattern in TAG_PATTERNS:
            for match in pattern.finditer(text):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.translation_text.tag_add('tag', start_idx, end_idx)

    def _update_title(self):
        title = "EU5 Локалізація - Редактор"
        if self.has_unsaved_changes:
            title = "* " + title
        self.root.title(title)

    def _copy_tags(self):
        if not self.current_entry:
            return
        # Беремо теги з оригіналу гри, якщо є
        source = self.originals_db.get(self.current_entry.key) if self.originals_db else None
        if not source:
            source = self.current_entry.value
        tags = find_tags(source)
        if tags:
            self.root.clipboard_clear()
            self.root.clipboard_append(' '.join(tags))
            self.statusbar_status['text'] = f"Скопійовано {len(tags)} тегів"
            self.root.after(2000, lambda: self.statusbar_status.config(text=""))

    def _save_and_next(self):
        if self._save_entry():
            self._next_entry()

    def _copy_original(self):
        """Копіює оригінал з гри в поле перекладу."""
        if not self.current_entry:
            return
        original = None
        if self.originals_db:
            original = self.originals_db.get(self.current_entry.key)
        if original:
            self.translation_text.delete('1.0', tk.END)
            self.translation_text.insert('1.0', original)
            self._highlight_tags_in_translation()
            self._on_translation_change()

    # === Сортування ===

    def _sort_column(self, col):
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        for c in ('key', 'value', 'category', 'file', 'status'):
            text = {'key': 'Ключ', 'value': 'Значення', 'category': 'Категорія',
                    'file': 'Файл', 'status': 'Статус'}[c]
            if c == col:
                text += ' ▲' if self.sort_reverse else ' ▼'
            self.results_tree.heading(c, text=text)

        if col == 'status':
            self.current_results.sort(key=lambda e: e.is_translated, reverse=self.sort_reverse)
        elif col == 'key':
            self.current_results.sort(key=lambda e: e.key.lower(), reverse=self.sort_reverse)
        elif col == 'value':
            self.current_results.sort(key=lambda e: e.value.lower(), reverse=self.sort_reverse)
        elif col == 'category':
            self.current_results.sort(key=lambda e: e.category, reverse=self.sort_reverse)
        elif col == 'file':
            self.current_results.sort(key=lambda e: Path(e.file_path).name, reverse=self.sort_reverse)

        self._refresh_results_display()

    def _refresh_results_display(self):
        self.results_tree.delete(*self.results_tree.get_children())
        for entry in self.current_results[:1000]:
            short_value = entry.value[:80] + "..." if len(entry.value) > 80 else entry.value
            short_file = Path(entry.file_path).name
            status = "✓" if entry.is_translated else "✗"
            tag = 'translated' if entry.is_translated else 'untranslated'
            self.results_tree.insert('', tk.END, values=(
                entry.key, short_value, entry.category, short_file, status
            ), tags=(tag,))

    # === Директорії ===

    def _auto_detect_directories(self):
        """Автоматично визначає директорії."""
        script_dir = Path(__file__).resolve().parent

        # Папка мода
        if not self.mod_dir_var.get():
            possible_mod = [
                script_dir.parent / 'main_menu' / 'localization' / 'dlc' / 'english',
            ]
            for path in possible_mod:
                if path.exists():
                    self.mod_dir_var.set(str(path))
                    break

        # Папка гри
        if not self.game_dir_var.get():
            possible_game = [
                Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/localization'),
                Path('C:/Program Files/Steam/steamapps/common/Europa Universalis V/game/localization'),
                Path.home() / '.steam/steam/steamapps/common/Europa Universalis V/game/localization',
            ]
            for path in possible_game:
                if path.exists():
                    self.game_dir_var.set(str(path))
                    break

    def _browse_mod_directory(self):
        directory = filedialog.askdirectory(title="Виберіть папку мода з локалізацією")
        if directory:
            self.mod_dir_var.set(directory)

    def _browse_game_directory(self):
        directory = filedialog.askdirectory(title="Виберіть папку гри з локалізацією")
        if directory:
            self.game_dir_var.set(directory)

    def _auto_scan_on_startup(self):
        mod_dir = self.mod_dir_var.get()
        if mod_dir and Path(mod_dir).exists() and self.config.get('auto_scan', True):
            self._scan_all()

    def _scan_all(self):
        """Сканує мод та оригінали."""
        mod_dir = self.mod_dir_var.get()
        game_dir = self.game_dir_var.get()
        lang = self.lang_var.get()

        if not mod_dir or not Path(mod_dir).exists():
            messagebox.showerror("Помилка", "Вкажіть існуючу папку мода")
            return

        # Прогрес-вікно
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Сканування...")
        progress_window.geometry("400x120")
        progress_window.transient(self.root)

        progress_label = ttk.Label(progress_window, text="Сканування...")
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(progress_window, length=350, mode='determinate')
        progress_bar.pack(pady=10)

        file_label = ttk.Label(progress_window, text="")
        file_label.pack()

        def update_progress(current, total, filename):
            progress_bar['maximum'] = total
            progress_bar['value'] = current
            file_label['text'] = filename
            progress_window.update()

        def scan():
            # Скануємо оригінали гри
            if game_dir and Path(game_dir).exists():
                progress_label['text'] = f"Сканування оригіналів ({lang})..."
                self.originals_db = OriginalTextsDatabase()
                orig_count = self.originals_db.scan(Path(game_dir), lang, update_progress)
            else:
                self.originals_db = None
                orig_count = 0

            # Скануємо мод
            progress_label['text'] = "Сканування мода..."
            self.db = LocalizationDatabase(Path(mod_dir))
            mod_count = self.db.scan(update_progress)

            progress_window.destroy()

            # Статистика
            total, translated = self.db.get_stats()
            untranslated = total - translated

            status_parts = [f"Мод: {mod_count} рядків ({untranslated} неперекл.)"]
            if orig_count > 0:
                status_parts.append(f"Оригінали: {orig_count}")
            self.status_label['text'] = " | ".join(status_parts)

            # Оновлюємо label мови
            self.orig_lang_label['text'] = f"[{lang}]"

            self._update_progress_display()
            self._do_search()

        self.root.after(100, scan)

    def _update_progress_display(self):
        if not self.db:
            return
        total, translated = self.db.get_stats()
        if total == 0:
            return
        percent = (translated / total) * 100
        self.progress_label['text'] = f"Прогрес: {translated} з {total}"
        self.progress_bar['maximum'] = total
        self.progress_bar['value'] = translated
        self.progress_percent['text'] = f"({percent:.1f}%)"

    def _do_search(self):
        if not self.db:
            messagebox.showinfo("Інформація", "Спочатку проскануйте директорію")
            return

        query = self.search_var.get()
        category = self.category_var.get()
        untranslated_only = self.untranslated_var.get()

        self.current_results = self.db.search(query, category, untranslated_only)

        self.sort_column = ""
        for c in ('key', 'value', 'category', 'file', 'status'):
            text = {'key': 'Ключ', 'value': 'Значення', 'category': 'Категорія',
                    'file': 'Файл', 'status': 'Статус'}[c]
            self.results_tree.heading(c, text=text)

        self._refresh_results_display()

        count = len(self.current_results)
        shown = min(count, 1000)
        self.results_count_label['text'] = f"Знайдено: {count} (показано: {shown})"

    def _on_result_select(self, event):
        selection = self.results_tree.selection()
        if not selection:
            return

        new_item = selection[0]

        if self.has_unsaved_changes:
            result = messagebox.askyesnocancel("Незбережені зміни", "Зберегти зміни перед переходом?")
            if result is None:
                # Відновлюємо попереднє виділення при Cancel
                if self._previous_selection:
                    self.results_tree.selection_set(self._previous_selection)
                    self.results_tree.see(self._previous_selection)
                return
            if result:
                self._save_entry()
            self.has_unsaved_changes = False
            self._update_title()

        # Зберігаємо поточне виділення
        self._previous_selection = new_item
        item = new_item
        index = self.results_tree.index(item)

        if index < len(self.current_results):
            self.current_entry = self.current_results[index]
            self._show_entry(self.current_entry)
            self._update_statusbar()

    def _update_statusbar(self):
        if self.current_entry:
            self.statusbar_file['text'] = f"Файл: {Path(self.current_entry.file_path).name}"
            selection = self.results_tree.selection()
            if selection:
                index = self.results_tree.index(selection[0])
                total = len(self.current_results)
                self.statusbar_position['text'] = f"Позиція: {index + 1} з {total}"
        else:
            self.statusbar_file['text'] = "Файл: --"
            self.statusbar_position['text'] = "Позиція: --"

    def _show_entry(self, entry: LocalizationEntry):
        """Показує рядок для редагування."""
        self.original_value = entry.value
        self.has_unsaved_changes = False
        self._update_title()

        # Контекст
        self.context_text.config(state=tk.NORMAL)
        self.context_text.delete('1.0', tk.END)
        for line_num, line_text, is_current in self.db.get_context(entry):
            tag = 'current' if is_current else None
            self.context_text.insert(tk.END, f"{line_num:4}: {line_text}\n", tag)
        self.context_text.config(state=tk.DISABLED)

        # Оригінал з гри
        self.original_text.config(state=tk.NORMAL)
        self.original_text.delete('1.0', tk.END)
        original_value = None
        if self.originals_db:
            original_value = self.originals_db.get(entry.key)
        if original_value:
            self._insert_with_tags(self.original_text, original_value)
        else:
            self.original_text.insert('1.0', "(не знайдено в оригіналах)")
        self.original_text.config(state=tk.DISABLED)

        # Переклад - завантажуємо поточне значення з файлу
        self.translation_text.delete('1.0', tk.END)
        self.translation_text.insert('1.0', entry.value)
        self.translation_text.edit_reset()
        self._highlight_tags_in_translation()

        # Лічильник
        char_count = len(self.translation_text.get('1.0', 'end-1c'))
        self.char_count_label['text'] = f"[{char_count} символів]"
        self.char_count_label['foreground'] = ''

        # Теги (з оригіналу гри, якщо є)
        source = original_value if original_value else entry.value
        tags = find_tags(source)
        if tags:
            self.tags_label['text'] = f"Теги (зберегти!): {', '.join(tags)}"
        else:
            self.tags_label['text'] = "Теги: (немає)"

    def _insert_with_tags(self, text_widget: tk.Text, text: str):
        """Вставляє текст з підсвічуванням тегів."""
        tag_positions = []
        for pattern in TAG_PATTERNS:
            for match in pattern.finditer(text):
                tag_positions.append((match.start(), match.end()))
        tag_positions.sort()

        pos = 0
        for start, end in tag_positions:
            if start > pos:
                text_widget.insert(tk.END, text[pos:start])
            text_widget.insert(tk.END, text[start:end], 'tag')
            pos = end
        if pos < len(text):
            text_widget.insert(tk.END, text[pos:])

    def _save_entry(self) -> bool:
        if not self.current_entry or not self.db:
            return False

        new_value = self.translation_text.get('1.0', 'end-1c')

        if not new_value:
            messagebox.showerror("Помилка", "Значення не може бути порожнім")
            return False

        # Перевірка тегів (порівнюємо з оригіналом гри, якщо є)
        source = None
        if self.originals_db:
            source = self.originals_db.get(self.current_entry.key)
        if not source:
            source = self.current_entry.value

        original_tags = set(find_tags(source))
        new_tags = set(find_tags(new_value))

        missing_tags = original_tags - new_tags
        if missing_tags:
            result = messagebox.askyesno(
                "Попередження",
                f"Відсутні теги: {', '.join(missing_tags)}\n\nЗберегти все одно?"
            )
            if not result:
                return False

        if self.db.update_entry(self.current_entry, new_value):
            self.modified_files.add(self.current_entry.file_path)
            self.has_unsaved_changes = False
            self.original_value = new_value
            self._update_title()

            self.statusbar_status['text'] = "Збережено!"
            self.root.after(2000, lambda: self.statusbar_status.config(text=""))

            # Оновлюємо дерево
            selection = self.results_tree.selection()
            if selection:
                item = selection[0]
                short_value = new_value[:80] + "..." if len(new_value) > 80 else new_value
                status = "✓" if self.current_entry.is_translated else "✗"
                tag = 'translated' if self.current_entry.is_translated else 'untranslated'
                self.results_tree.item(item, values=(
                    self.current_entry.key, short_value,
                    self.current_entry.category, Path(self.current_entry.file_path).name,
                    status
                ), tags=(tag,))

            self._update_progress_display()
            return True
        else:
            messagebox.showerror("Помилка", "Не вдалось зберегти")
            return False

    def _open_in_editor(self):
        if not self.current_entry:
            return

        file_path = self.current_entry.file_path
        line_number = self.current_entry.line_number + 1

        try:
            editors = [
                ['code', '-g', f'{file_path}:{line_number}'],
                ['notepad++', '-n' + str(line_number), file_path],
                ['notepad', file_path],
            ]

            for editor_cmd in editors:
                try:
                    subprocess.Popen(editor_cmd, shell=False)
                    self.statusbar_status['text'] = "Відкрито у редакторі"
                    self.root.after(2000, lambda: self.statusbar_status.config(text=""))
                    return
                except FileNotFoundError:
                    continue

            messagebox.showwarning("Попередження", "Не знайдено зовнішній редактор")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалось відкрити редактор: {e}")

    def _find_git_root(self, start_path: Path) -> Optional[Path]:
        """Шукає git root директорію вгору по дереву."""
        current = start_path.resolve()
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        # Перевіряємо корінь
        if (current / '.git').exists():
            return current
        return None

    def _git_commit(self):
        if not self.modified_files:
            messagebox.showinfo("Інформація", "Немає змін для commit")
            return

        commit_window = tk.Toplevel(self.root)
        commit_window.title("Git Commit")
        commit_window.geometry("500x300")
        commit_window.transient(self.root)

        ttk.Label(commit_window, text="Змінені файли:").pack(anchor=tk.W, padx=10, pady=5)

        files_text = tk.Text(commit_window, height=8, state=tk.NORMAL)
        files_text.pack(fill=tk.X, padx=10)
        for f in sorted(self.modified_files):
            files_text.insert(tk.END, f"{Path(f).name}\n")
        files_text.config(state=tk.DISABLED)

        ttk.Label(commit_window, text="Commit message:").pack(anchor=tk.W, padx=10, pady=5)

        message_var = tk.StringVar(value="Переклад: ")
        message_entry = ttk.Entry(commit_window, textvariable=message_var, width=60)
        message_entry.pack(fill=tk.X, padx=10)

        def do_commit():
            message = message_var.get()
            if not message:
                messagebox.showerror("Помилка", "Вкажіть commit message")
                return

            try:
                for f in self.modified_files:
                    subprocess.run(['git', 'add', f], check=True, cwd=Path(f).parent)

                # Знаходимо git root
                first_file = Path(list(self.modified_files)[0])
                git_root = self._find_git_root(first_file.parent)
                if not git_root:
                    messagebox.showerror("Помилка", "Не знайдено git репозиторій")
                    return

                result = subprocess.run(
                    ['git', 'commit', '-m', message],
                    capture_output=True, text=True,
                    cwd=git_root
                )

                if result.returncode == 0:
                    messagebox.showinfo("Успіх", "Commit створено!")
                    self.modified_files.clear()
                    commit_window.destroy()
                else:
                    messagebox.showerror("Помилка", f"Git error:\n{result.stderr}")

            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка git: {e}")

        ttk.Button(commit_window, text="Commit", command=do_commit).pack(pady=10)


def main():
    root = tk.Tk()
    app = LocalizationApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
