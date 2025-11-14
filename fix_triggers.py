#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для виправлення старих форматів відмінків у triggers_l_english.yml
Замінює [country|e] та [location|e] на новий формат Concept
"""

import re
import sys

def fix_triggers_file(filepath):
    """Виправляє формати відмінків у файлі"""

    # Читаємо файл з UTF-8 BOM
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    original_content = content
    replacements_count = 0

    # Шаблони заміни для country
    country_patterns = [
        # "Any [country|e]" → "Будь-яка [Concept('country','держава')|e]"
        (r'\[country\|e\](?!\s*getting|\s*\[)', r"[Concept('country','держава')|e]"),
        # "in [country|e]" → "у [Concept('country','державі')|e]"
        (r'у \[country\|e\]', r"у [Concept('country','державі')|e]"),
        (r'в \[country\|e\]', r"у [Concept('country','державі')|e]"),
        # "of [country|e]" → "[Concept('country','держави')|e]" (родовий)
        (r'of \[country\|e\]', r"[Concept('country','держави')|e]"),
    ]

    # Шаблони заміни для location
    location_patterns = [
        # "Any [location|e]" → "Будь-який [Concept('location','район')|e]"
        (r'\[location\|e\](?!\s+in)', r"[Concept('location','район')|e]"),
        # "in [location|e]" або після прийменників
        (r'у \[location\|e\]', r"у [Concept('location','районі')|e]"),
        (r'в \[location\|e\]', r"у [Concept('location','районі')|e]"),
    ]

    # Виконуємо заміни
    for pattern, replacement in country_patterns:
        new_content = re.sub(pattern, replacement, content)
        count = len(re.findall(pattern, content))
        if count > 0:
            print(f"Замінено {count} входжень: {pattern} → {replacement}")
            replacements_count += count
            content = new_content

    for pattern, replacement in location_patterns:
        new_content = re.sub(pattern, replacement, content)
        count = len(re.findall(pattern, content))
        if count > 0:
            print(f"Замінено {count} входжень: {pattern} → {replacement}")
            replacements_count += count
            content = new_content

    # Тепер обробляємо залишки [country|e] та [location|e]
    # які не потрапили під попередні правила

    # Підрахунок залишків
    remaining_country = len(re.findall(r'\[country\|e\]', content))
    remaining_location = len(re.findall(r'\[location\|e\]', content))

    if remaining_country > 0:
        print(f"\nЗалишилось [country|e]: {remaining_country}")
        # Показуємо контекст
        for match in re.finditer(r'.{0,50}\[country\|e\].{0,50}', content):
            print(f"  → {match.group()}")

    if remaining_location > 0:
        print(f"\nЗалишилось [location|e]: {remaining_location}")
        # Показуємо контекст
        for match in re.finditer(r'.{0,50}\[location\|e\].{0,50}', content):
            print(f"  → {match.group()}")

    # Записуємо результат з UTF-8 BOM
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        print(f"\n✓ Файл збережено. Всього замін: {replacements_count}")
    else:
        print("\n! Змін не знайдено")

    return replacements_count, remaining_country, remaining_location

if __name__ == '__main__':
    filepath = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/triggers_l_english.yml'
    fix_triggers_file(filepath)
