#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Універсальний скрипт для об'єднання перекладених частин в один файл

Використання:
    python3 merge_translation.py <chunks_dir> [--output output_file.yml] [--suffix fixed]

Приклади:
    python3 merge_translation.py events_chunks
    python3 merge_translation.py chunks --output result.yml
    python3 merge_translation.py chunks --suffix translated
"""
import os
import sys
import glob
import json
import argparse
from pathlib import Path

def merge_chunks(chunks_dir, output_file=None, suffix='fixed'):
    """Об'єднує перекладені частини в один файл"""

    print(f"📁 Шукаю перекладені частини в: {chunks_dir}")

    # Читаємо метадані якщо є
    metadata_file = os.path.join(chunks_dir, 'metadata.json')
    metadata = None
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"📖 Знайдено метадані: {metadata_file}")

    # Знаходимо всі перекладені файли
    pattern = os.path.join(chunks_dir, f'chunk_*_{suffix}.txt')
    translated_files = sorted(glob.glob(pattern))

    if not translated_files:
        print(f"❌ Не знайдено перекладених файлів ({pattern})")
        print(f"   Переклади спочатку всі chunk_XXX.txt та збережи як chunk_XXX_{suffix}.txt!")
        return False

    print(f"📊 Знайдено {len(translated_files)} перекладених частин")

    # Визначаємо вихідний файл
    if output_file is None:
        if metadata and 'input_file' in metadata:
            output_file = metadata['input_file']
        else:
            # Генеруємо назву на основі папки
            base_name = Path(chunks_dir).stem.replace('_chunks', '')
            output_file = f"main_menu/localization/english/{base_name}_l_english.yml"

    print(f"📝 Вихідний файл: {output_file}")

    # Об'єднуємо
    all_lines = []
    header_added = False

    for i, translated_file in enumerate(translated_files, 1):
        print(f"📖 [{i}/{len(translated_files)}] Читаю: {os.path.basename(translated_file)}")

        with open(translated_file, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # Перша частина має заголовок
        if i == 1:
            all_lines.extend(lines)
            header_added = True
        else:
            # Інші частини - пропускаємо заголовок якщо є
            if lines and lines[0].strip().startswith('l_english:'):
                all_lines.extend(lines[1:])
            else:
                all_lines.extend(lines)

    # Створюємо папку якщо не існує
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"\n✍️ Записую об'єднаний файл...")
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        f.writelines(all_lines)

    print(f"✅ ГОТОВО! Об'єднано {len(all_lines)} рядків")
    print(f"📄 Файл збережено: {output_file}")

    # Зберігаємо звіт
    report_file = os.path.join(chunks_dir, 'merge_report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ЗВІТ ПРО ОБ'ЄДНАННЯ\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Дата: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Папка з частинами: {chunks_dir}\n")
        f.write(f"Вихідний файл: {output_file}\n")
        f.write(f"Об'єднано частин: {len(translated_files)}\n")
        f.write(f"Всього рядків: {len(all_lines)}\n\n")
        f.write("Перекладені файли:\n")
        for tf in translated_files:
            f.write(f"  - {os.path.basename(tf)}\n")

    print(f"📋 Звіт збережено: {report_file}")

    return True

def main():
    parser = argparse.ArgumentParser(
        description='Об\'єднати перекладені частини в один файл',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Приклади:
  %(prog)s events_chunks
  %(prog)s chunks --output result.yml
  %(prog)s chunks --suffix translated
        '''
    )

    parser.add_argument('chunks_dir', help='Папка з перекладеними частинами')
    parser.add_argument('--output', help='Вихідний файл (за замовчуванням з metadata.json або генерується)')
    parser.add_argument('--suffix', default='fixed', help='Суфікс перекладених файлів (за замовчуванням: fixed)')

    args = parser.parse_args()

    # Перевірка існування папки
    if not os.path.exists(args.chunks_dir):
        print(f"❌ Помилка: Папка не знайдена: {args.chunks_dir}")
        sys.exit(1)

    success = merge_chunks(args.chunks_dir, output_file=args.output, suffix=args.suffix)

    if success:
        print("\n" + "=" * 80)
        print("🎉 УСПІШНО ОБ'ЄДНАНО!")
        print("=" * 80)
        print("\nТепер можна перевірити результат та закомітити зміни:")
        print("  git add <output_file>")
        print("  git commit -m 'Переклад завершено'")
        print("  git push")
    else:
        print("\n" + "=" * 80)
        print("❌ ПОМИЛКА!")
        print("=" * 80)
        sys.exit(1)

if __name__ == '__main__':
    main()
