#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

hints_file = "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/hints_l_english.yml"

# Збираємо всі відомі переклади з виправлених файлів
reference_files = [
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/government_l_english.yml",
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/general_tooltips_l_english.yml",
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/diplomacy_l_english.yml",
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/alerts_l_english.yml",
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/economy_l_english.yml",
    "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/actions_l_english.yml",
]

# Витягуємо всі Concept()
known_translations = {}
for ref_file in reference_files:
    try:
        with open(ref_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            for match in re.finditer(r"Concept\('([^']+)','([^']+)'\)", content):
                key = match.group(1)
                translation = match.group(2)
                if key not in known_translations:
                    known_translations[key] = translation
    except FileNotFoundError:
        continue

print(f"📚 Зібрано {len(known_translations)} перекладів")

# Читаємо hints
with open(hints_file, 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Знаходимо всі _with_icon та інші формати
old_formats = set(re.findall(r'\[([a-z_]+)\|e\]', content))

replacements_made = 0
for concept_key in sorted(old_formats):
    old_format = f'[{concept_key}|e]'

    # Спробуємо знайти базовий ключ (без _with_icon та інших суфіксів)
    base_key = concept_key

    # Перевіряємо різні варіанти
    if base_key.endswith('_with_icon'):
        base_key = base_key.replace('_with_icon', '')
    elif base_key.endswith('_short'):
        base_key = base_key.replace('_short', '')

    # Пошук перекладу
    translation = None
    if concept_key in known_translations:
        translation = known_translations[concept_key]
    elif base_key in known_translations:
        translation = known_translations[base_key]
    elif base_key + 's' in known_translations:  # Спроба знайти plural
        translation = known_translations[base_key + 's']
    elif base_key.endswith('s') and base_key[:-1] in known_translations:  # Спроба singular
        translation = known_translations[base_key[:-1]]

    if translation:
        new_format = f"[Concept('{concept_key}','{translation}')|e]"
        count = content.count(old_format)
        content = content.replace(old_format, new_format)
        replacements_made += count
        if count > 0:
            print(f"✓ [{concept_key}|e]: {count} → '{translation}'")

# Зберігаємо
with open(hints_file, 'w', encoding='utf-8-sig') as f:
    f.write(content)

remaining = len(re.findall(r'\[[a-z_]+\|e\]', content))
print(f"\n✅ Зроблено {replacements_made} замін")
print(f"📊 Залишилось {remaining} старих форматів")
