#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Виявлення російських слів у перекладених файлах
"""

import re
from pathlib import Path

# Список очевидно російських слів для швидкої перевірки
RUSSIAN_WORDS = {
    # Часто використовувані слова
    'всегда', 'никогда', 'должно', 'если', 'когда', 'было', 'будет',
    'может', 'должен', 'можно', 'нужно', 'надо', 'было', 'были',
    'сейчас', 'только', 'очень', 'много', 'мало', 'больше', 'меньше',
    'лучше', 'хуже', 'выше', 'ниже', 'раньше', 'позже',

    # Дієслова
    'используется', 'обладает', 'обсуждается', 'является', 'находится',
    'принадлежит', 'исповедует', 'говорит', 'открывает', 'требуется',
    'составляет', 'заседает', 'выполняется', 'присутствие',

    # Іменники
    'война', 'мир', 'страна', 'государство', 'правительство', 'армия',
    'население', 'культура', 'религия', 'торговля', 'отец', 'мать',
    'династия', 'ранг', 'столица', 'район', 'здание', 'закон',
    'политика', 'союз', 'враг', 'сосед', 'владелец', 'правитель',
    'парламент', 'собрание', 'совет', 'действие', 'способность',
    'улучшение', 'исследование', 'очередь', 'дорога', 'привилегия',
    'эпоха', 'время', 'возрождение', 'открытие', 'революция',
    'абсолютизм', 'реформация', 'традиция',

    # Прикметники
    'основной', 'главный', 'новый', 'старый', 'большой', 'малый',
    'высокий', 'низкий', 'сильный', 'слабый', 'быстрый', 'медленный',
    'ближайший', 'дальний', 'первый', 'последний', 'следующий',
    'предыдущий', 'положительный', 'отрицательный', 'абсолютный',
    'относительный', 'еретический', 'языческий',

    # Прийменники та сполучники
    'из', 'от', 'до', 'для', 'при', 'над', 'под', 'перед', 'после',
    'через', 'между', 'среди', 'вокруг', 'около', 'возле', 'внутри',
    'снаружи', 'вверх', 'вниз', 'вперед', 'назад',

    # Інше
    'склонность', 'доверять', 'испытывать', 'неприязнь', 'голосовать',
    'совокупное', 'доля', 'меняющееся', 'контроль', 'вероятность',
    'появление', 'импорт', 'внедрён', 'открытия', 'вопрос', 'право',
    'власть', 'строительство', 'силы', 'империя', 'монархия',
    'республика', 'движение', 'общество', 'знание', 'искусство',
    'прогресс', 'континент', 'королевство', 'централизованный',
}

# Російські закінчення слів
RUSSIAN_ENDINGS = [
    'ый', 'ий', 'ой',  # прикметники чоловічого роду
    'ая', 'яя',  # прикметники жіночого роду
    'ое', 'ее',  # прикметники середнього роду
    'ые', 'ие',  # прикметники множини
    'ого', 'его',  # родовий відмінок прикметників
    'ому', 'ему',  # давальний відмінок
    'ым', 'им',  # орудний відмінок
    'ет', 'ит',  # дієслова 3-я особа
    'ут', 'ют', 'ат', 'ят',  # дієслова множина
    'ться', 'тся',  # зворотні дієслова
]

def has_russian_words(text):
    """Перевірка чи містить текст російські слова"""
    # Видаляємо технічні частини
    text = re.sub(r'\[.*?\]', '', text)  # Видаляємо [Concept(...)]
    text = re.sub(r'\$.*?\$', '', text)  # Видаляємо змінні $VAR$
    text = re.sub(r'#.*?#', '', text)  # Видаляємо теги #TAG#

    # Lowercase для порівняння
    words = re.findall(r'\b[а-яёА-ЯЁ]+\b', text.lower())

    russian_found = []
    for word in words:
        # Перевірка в списку російських слів
        if word in RUSSIAN_WORDS:
            russian_found.append(word)
            continue

        # Перевірка закінчень
        for ending in RUSSIAN_ENDINGS:
            if word.endswith(ending) and len(word) > len(ending) + 2:
                # Додаткова перевірка - чи це не українське слово
                if not word.endswith('ий') or not word.endswith('ої'):  # "який", "якої" - українські
                    russian_found.append(word)
                    break

    return russian_found

def analyze_file(filepath):
    """Аналіз одного файлу"""
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        issues = []
        total_lines = 0

        for i, line in enumerate(lines, 1):
            # Пропускаємо коментарі та заголовок
            if line.strip().startswith('#') or 'l_english:' in line:
                continue

            # Пропускаємо порожні рядки
            if not line.strip():
                continue

            total_lines += 1

            # Шукаємо частину після ":"
            match = re.match(r'\s*[^:]+:\s*"(.+)"', line)
            if match:
                text = match.group(1)
                russian = has_russian_words(text)
                if russian:
                    issues.append({
                        'line': i,
                        'text': text[:100],  # Перші 100 символів
                        'russian_words': russian[:5]  # Перші 5 російських слів
                    })

        return total_lines, issues

    except Exception as e:
        print(f"Помилка в {filepath}: {e}")
        return 0, []

def main():
    files_to_check = [
        "triggers_l_english.yml",
        "advances_l_english.yml",
        "diplomacy_l_english.yml",
        "laws_and_policies_l_english.yml",
        "units_l_english.yml"
    ]

    base_dir = Path("/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english")

    print("=" * 80)
    print("АНАЛІЗ ЯКОСТІ ПЕРЕКЛАДУ - ВИЯВЛЕННЯ РОСІЙСЬКИХ СЛІВ")
    print("=" * 80)

    total_all_lines = 0
    total_all_issues = 0

    for filename in files_to_check:
        filepath = base_dir / filename
        if not filepath.exists():
            print(f"\n⚠ Файл не знайдено: {filename}")
            continue

        print(f"\n{'─' * 80}")
        print(f"Файл: {filename}")
        print(f"{'─' * 80}")

        total_lines, issues = analyze_file(filepath)
        total_all_lines += total_lines
        total_all_issues += len(issues)

        print(f"Всього рядків: {total_lines}")
        print(f"Рядків з російськими словами: {len(issues)} ({len(issues)*100//total_lines if total_lines else 0}%)")

        if issues:
            print(f"\nПриклади (перші 10):")
            for issue in issues[:10]:
                words_str = ", ".join(issue['russian_words'])
                print(f"  Рядок {issue['line']}: [{words_str}]")
                print(f"    {issue['text']}")

    # Підсумок
    print(f"\n{'=' * 80}")
    print(f"ПІДСУМОК")
    print(f"{'=' * 80}")
    print(f"Всього рядків перевірено: {total_all_lines}")
    print(f"Рядків з російськими словами: {total_all_issues}")
    print(f"Якість перекладу: {100 - (total_all_issues*100//total_all_lines if total_all_lines else 0)}%")

    if total_all_issues > total_all_lines * 0.3:  # Більше 30% проблем
        print("\n⚠ КРИТИЧНА ПРОБЛЕМА: Більше 30% тексту містить російські слова!")
        print("Рекомендується повністю переробити переклад.")
    elif total_all_issues > total_all_lines * 0.1:  # Більше 10% проблем
        print("\n⚠ СЕРЕДНЯ ПРОБЛЕМА: 10-30% тексту містить російські слова.")
        print("Рекомендується покращити словник перекладу.")
    else:
        print("\n✓ Якість перекладу прийнятна (менше 10% російських слів).")

if __name__ == "__main__":
    main()
