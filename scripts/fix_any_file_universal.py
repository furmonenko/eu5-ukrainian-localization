#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

if len(sys.argv) < 2:
    print("Usage: python3 fix_any_file_universal.py <filename>")
    sys.exit(1)

filename = sys.argv[1]
target_file = f"/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/{filename}"

# Збираємо всі відомі переклади з виправлених файлів
reference_files = [
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/government_l_english.yml",
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/general_tooltips_l_english.yml",
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/diplomacy_l_english.yml",
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/alerts_l_english.yml",
]

# Витягуємо всі Concept() з reference файлів
known_translations = {}
concept_pattern = r"Concept\('([^']+)','([^']+)'\)"

for ref_file in reference_files:
    try:
        with open(ref_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            for match in re.finditer(concept_pattern, content):
                key = match.group(1)
                translation = match.group(2)
                if key not in known_translations:
                    known_translations[key] = translation
    except FileNotFoundError:
        continue

print(f"📚 Зібрано {len(known_translations)} відомих перекладів з попередніх файлів")

# Читаємо target файл
try:
    with open(target_file, 'r', encoding='utf-8-sig') as f:
        target_content = f.read()
except FileNotFoundError:
    print(f"❌ Файл не знайдено: {target_file}")
    sys.exit(1)

# Знаходимо всі старі формати
old_format_pattern = r'\[([a-z_]+)\|e\]'
old_formats_found = set(re.findall(old_format_pattern, target_content))

before_count = len(re.findall(old_format_pattern, target_content))
print(f"🔍 Знайдено {before_count} старих форматів ({len(old_formats_found)} унікальних)")

# Створюємо заміни
replacements_made = 0
missing_translations = []

for concept_key in sorted(old_formats_found):
    old_format = f'[{concept_key}|e]'

    if concept_key in known_translations:
        translation = known_translations[concept_key]
        new_format = f"[Concept('{concept_key}','{translation}')|e]"

        count_before = target_content.count(old_format)
        target_content = target_content.replace(old_format, new_format)
        count_after = target_content.count(old_format)
        actual = count_before - count_after

        if actual > 0:
            replacements_made += actual
            if actual >= 5:
                print(f"✓ [{concept_key}|e]: {actual} замін → '{translation}'")
    else:
        missing_translations.append(concept_key)

# Зберігаємо
with open(target_file, 'w', encoding='utf-8-sig') as f:
    f.write(target_content)

after_count = len(re.findall(old_format_pattern, target_content))

print(f"\n✅ Зроблено {replacements_made} замін")
print(f"📊 {before_count} → {after_count} старих форматів")

if missing_translations:
    print(f"\n⚠️  Залишилось {len(missing_translations)} концептів без відомих перекладів")
    print(f"   Перші 10: {', '.join(missing_translations[:10])}")
