#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для заміни старих форматів [country|e] та [location|e]
на новий формат Concept в triggers_l_english.yml
"""

import re

def fix_triggers_file(filepath):
    """Виправляє формати відмінків у файлі"""

    # Читаємо файл з UTF-8 BOM
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    original_content = content
    total_replacements = 0

    # Словник замін для country
    country_replacements = [
        # Прямі заміни з урахуванням контексту
        (r'\[country\|e\]', r"[Concept('country','держава')|e]"),
        (r'\[countries\|e\]', r"[Concept('countries','держави')|e]"),
    ]

    # Словник замін для location
    location_replacements = [
        (r'\[location\|e\]', r"[Concept('location','район')|e]"),
        (r'\[locations\|e\]', r"[Concept('locations','райони')|e]"),
    ]

    # Виконуємо заміни для country
    for pattern, replacement in country_replacements:
        matches = re.findall(pattern, content)
        count = len(matches)
        if count > 0:
            content = re.sub(pattern, replacement, content)
            total_replacements += count
            print(f"✓ Замінено {count} входжень: {pattern}")

    # Виконуємо заміни для location
    for pattern, replacement in location_replacements:
        matches = re.findall(pattern, content)
        count = len(matches)
        if count > 0:
            content = re.sub(pattern, replacement, content)
            total_replacements += count
            print(f"✓ Замінено {count} входжень: {pattern}")

    # Перевіряємо чи залишились старі формати
    remaining_country = len(re.findall(r'\[country\|e\]', content))
    remaining_location = len(re.findall(r'\[location\|e\]', content))

    print(f"\n{'='*60}")
    print(f"Всього виправлено: {total_replacements}")
    print(f"Залишилось [country|e]: {remaining_country}")
    print(f"Залишилось [location|e]: {remaining_location}")
    print(f"{'='*60}\n")

    if content != original_content:
        # Створюємо резервну копію
        backup_path = filepath + '.backup'
        with open(backup_path, 'w', encoding='utf-8-sig') as f:
            f.write(original_content)
        print(f"✓ Створено резервну копію: {backup_path}")

        # Записуємо виправлений файл
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        print(f"✓ Файл збережено: {filepath}")
    else:
        print("! Змін не знайдено")

    return total_replacements

if __name__ == '__main__':
    filepath = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/triggers_l_english.yml'
    print(f"Обробка файлу: {filepath}\n")
    total = fix_triggers_file(filepath)
    print(f"\n✓✓✓ Завершено! Виправлено {total} входжень ✓✓✓")
