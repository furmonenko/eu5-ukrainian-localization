#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

if len(sys.argv) < 2:
    print("Usage: python3 auto_translate_from_russian.py <filename>")
    sys.exit(1)

filename = sys.argv[1]
ukr_file = f"/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english/{filename}"
rus_file = f"/mnt/d/SteamLibrary/steamapps/common/Europa Universalis V/game/main_menu/localization/russian/{filename.replace('_english', '_russian')}"

# Базовий словник російське → українське
TRANSLATION_MAP = {
    'страны': 'країни', 'стране': 'країні', 'страну': 'країну', 'страной': 'країною',
    'стран': 'країн', 'страна': 'країна',
    'державы': 'держави', 'государства': 'держави', 'государств': 'держав',
    'районом': 'локацією', 'района': 'локації', 'районе': 'локації', 'районы': 'локації',
    'попов': 'населення', 'попам': 'населенню', 'население': 'населення',
    'армии': 'армії', 'армий': 'армій', 'армией': 'армією', 'войска': 'військ',
    'совета': 'ради', 'совету': 'раді',
    'религии': 'релігії', 'религию': 'релігію',
    'культуры': 'культури', 'культуре': 'культурі',
    'провинции': 'провінції', 'провінцію': 'провінцію',
    'здания': 'будівлі', 'зданий': 'будівель',
    'закона': 'закону', 'законов': 'законів',
    'товара': 'товару', 'товаров': 'товарів', 'товары': 'товари',
    'флота': 'флоту', 'флоты': 'флоти',
    'корабля': 'корабля', 'кораблей': 'кораблів', 'корабли': 'кораблі',
}

def transliterate(word):
    """Базова транслітерація"""
    word = word.replace('ы', 'и')
    word = word.replace('э', 'е')
    word = word.replace('ъ', '')
    return word

def translate_russian_to_ukrainian(russian_word):
    """Переклад російського на українське"""
    if russian_word in TRANSLATION_MAP:
        return TRANSLATION_MAP[russian_word]
    return transliterate(russian_word)

# Читаємо російський файл та витягуємо Concept()
try:
    with open(rus_file, 'r', encoding='utf-8-sig') as f:
        rus_content = f.read()
    rus_concepts = {}
    for match in re.finditer(r"Concept\('([^']+)','([^']+)'\)", rus_content):
        key = match.group(1)
        rus_value = match.group(2)
        # Перекладаємо російське на українське
        ukr_value = translate_russian_to_ukrainian(rus_value)
        rus_concepts[key] = ukr_value
    print(f"📚 Витягнуто {len(rus_concepts)} концептів з російського файлу")
except FileNotFoundError:
    print(f"⚠️  Російський файл не знайдено, використовую тільки наявні переклади")
    rus_concepts = {}

# Читаємо український файл
with open(ukr_file, 'r', encoding='utf-8-sig') as f:
    ukr_content = f.read()

# Знаходимо старі формати
old_formats = set(re.findall(r'\[([a-z_]+)\|e\]', ukr_content))
before_count = len(re.findall(r'\[[a-z_]+\|e\]', ukr_content))

print(f"🔍 Знайдено {before_count} старих форматів ({len(old_formats)} унікальних)")

replacements_made = 0
for concept_key in sorted(old_formats):
    old_format = f'[{concept_key}|e]'

    if concept_key in rus_concepts:
        translation = rus_concepts[concept_key]
        new_format = f"[Concept('{concept_key}','{translation}')|e]"

        count = ukr_content.count(old_format)
        ukr_content = ukr_content.replace(old_format, new_format)
        replacements_made += count
        if count >= 3:
            print(f"✓ [{concept_key}|e]: {count} → '{translation}'")

# Зберігаємо
with open(ukr_file, 'w', encoding='utf-8-sig') as f:
    f.write(ukr_content)

after_count = len(re.findall(r'\[[a-z_]+\|e\]', ukr_content))
print(f"\n✅ Зроблено {replacements_made} замін з російського файлу")
print(f"📊 {before_count} → {after_count} старих форматів залишилось")
