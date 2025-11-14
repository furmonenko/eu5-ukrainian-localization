#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

file_path = "/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/modifier_types_l_english.yml"

with open(file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Останні заміни
content = re.sub(r'\bбудут\b', 'будуть', content)
content = re.sub(r' между ', ' між ', content)
content = re.sub(r' нашей ', ' нашої ', content)
content = re.sub(r' этот ', ' цей ', content)
content = re.sub(r' это ', ' це ', content)

with open(file_path, 'w', encoding='utf-8-sig') as f:
    f.write(content)

print("Останні виправлення застосовано!")

# Перевірка
russian_words = ['будут', 'между', 'нашей', 'этот', 'которую', 'может']
found = {}
for word in russian_words:
    count = len(re.findall(r'\b' + word + r'\b', content, re.IGNORECASE))
    if count > 0:
        found[word] = count

if found:
    print("\nЗалишилися:")
    for word, count in found.items():
        print(f"  '{word}': {count}")
else:
    print("\nВідмінно! Всі цільові слова виправлено.")
