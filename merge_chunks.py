#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для об'єднання перекладених частин в один файл
"""
import os
import glob

def merge_chunks(chunks_dir, output_file):
    """Об'єднує перекладені частини в один файл"""

    print(f"📁 Шукаю перекладені частини в: {chunks_dir}")

    # Знаходимо всі перекладені файли
    uk_files = sorted(glob.glob(os.path.join(chunks_dir, 'chunk_*_uk.txt')))

    if not uk_files:
        print("❌ Не знайдено перекладених файлів (chunk_*_uk.txt)")
        print("   Переклади спочатку всі частини!")
        return False

    print(f"📊 Знайдено {len(uk_files)} перекладених частин")

    # Об'єднуємо
    all_lines = []
    header_added = False

    for i, uk_file in enumerate(uk_files, 1):
        print(f"📖 Читаю: {os.path.basename(uk_file)}")

        with open(uk_file, 'r', encoding='utf-8-sig') as f:
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

    print(f"\n✍️ Записую об'єднаний файл...")
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        f.writelines(all_lines)

    print(f"✅ ГОТОВО! Об'єднано {len(all_lines)} рядків")
    print(f"📄 Файл збережено: {output_file}")

    return True

def main():
    chunks_dir = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/government_names_chunks'
    output_file = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/government_names_l_english.yml'

    success = merge_chunks(chunks_dir, output_file)

    if success:
        print("\n" + "=" * 80)
        print("🎉 УСПІШНО ОБ'ЄДНАНО!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ ПОМИЛКА!")
        print("=" * 80)

if __name__ == '__main__':
    main()
