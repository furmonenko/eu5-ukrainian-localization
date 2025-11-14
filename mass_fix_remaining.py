#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Масове виправлення всіх решти файлів з [country|e] та [location|e]
"""

import os
import re
from pathlib import Path

def fix_file(filepath):
    """Виправити один файл"""
    try:
        #Читаємо файл
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        original = content

        # Лічильники
        country_count = 0
        location_count = 0

        # Патерни для НЕ заміни (технічні змінні)
        skip_patterns = [r'\[ROOT\.', r'\[THIS\.', r'\[SCOPE\.', r'\[SELECT_', r'\[GetDataModelSize']

        def should_skip(text, pos):
            """Перевірка чи це технічна змінна"""
            for pattern in skip_patterns:
                if re.match(pattern, text[pos:pos+20]):
                    return True
            return False

        # Заміна [country|e] → [Concept('country','держава')|e]
        def replace_country(match):
            nonlocal country_count
            pos = match.start()
            if should_skip(content, pos):
                return match.group(0)
            country_count += 1
            return "[Concept('country','держава')|e]"

        # Заміна [countries|e] → [Concept('countries','держави')|e]
        def replace_countries(match):
            nonlocal country_count
            pos = match.start()
            if should_skip(content, pos):
                return match.group(0)
            country_count += 1
            return "[Concept('countries','держави')|e]"

        # Заміна [location|e] → [Concept('location','район')|e]
        def replace_location(match):
            nonlocal location_count
            pos = match.start()
            if should_skip(content, pos):
                return match.group(0)
            location_count += 1
            return "[Concept('location','район')|e]"

        # Заміна [locations|e] → [Concept('locations','райони')|e]
        def replace_locations(match):
            nonlocal location_count
            pos = match.start()
            if should_skip(content, pos):
                return match.group(0)
            location_count += 1
            return "[Concept('locations','райони')|e]"

        # Виконуємо заміни
        content = re.sub(r'\[country\|e\]', replace_country, content)
        content = re.sub(r'\[countries\|e\]', replace_countries, content)
        content = re.sub(r'\[location\|e\]', replace_location, content)
        content = re.sub(r'\[locations\|e\]', replace_locations, content)

        # Якщо були зміни - зберігаємо
        if content != original:
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            return country_count, location_count

        return 0, 0

    except Exception as e:
        print(f"ПОМИЛКА в {filepath}: {e}")
        return 0, 0

def main():
    base_dir = Path("/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english")

    total_country = 0
    total_location = 0
    fixed_files = []

    # Обробляємо всі .yml файли
    for yml_file in base_dir.rglob("*.yml"):
        country_count, location_count = fix_file(yml_file)
        if country_count > 0 or location_count > 0:
            total_country += country_count
            total_location += location_count
            fixed_files.append((str(yml_file.relative_to(base_dir)), country_count, location_count))
            print(f"✓ {yml_file.name}: {country_count} country + {location_count} location")

    # Звіт
    print("\n" + "="*70)
    print("ПІДСУМОК ВИПРАВЛЕНЬ")
    print("="*70)
    print(f"Всього файлів виправлено: {len(fixed_files)}")
    print(f"Всього [country|e] → Concept: {total_country}")
    print(f"Всього [location|e] → Concept: {total_location}")
    print(f"ЗАГАЛОМ ВИПРАВЛЕНЬ: {total_country + total_location}")

    if fixed_files:
        print("\nТоп-10 файлів з найбільшою кількістю виправлень:")
        sorted_files = sorted(fixed_files, key=lambda x: x[1] + x[2], reverse=True)[:10]
        for file, c, l in sorted_files:
            print(f"  {file}: {c+l} виправлень ({c} country + {l} location)")

if __name__ == "__main__":
    main()
