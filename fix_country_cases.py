#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для заміни [country|e] на правильні відмінки української мови
"""

import re
import sys

def determine_case(line):
    """
    Визначає потрібний відмінок на основі контексту

    Відмінки:
    - держава (називний) - хто? що?
    - держави (родовий) - кого? чого?
    - державі (давальний/місцевий) - кому? чому? / на чому? де?
    - державу (знахідний) - кого? що?
    - державою (орудний) - ким? чим?
    """

    line_lower = line.lower()

    # Місцевий відмінок "у/в державі" (on/in our country)
    if re.search(r'\bв\s+.*?\[country\|e\]', line_lower) or \
       re.search(r'\bу\s+.*?\[country\|e\]', line_lower) or \
       re.search(r'в\s+нашій\s+\[country\|e\]', line_lower) or \
       re.search(r'у\s+нашій\s+\[country\|e\]', line_lower) or \
       re.search(r'в\s+іншій\s+\[country\|e\]', line_lower) or \
       re.search(r'у\s+іншій\s+\[country\|e\]', line_lower):
        return 'державі'

    # Родовий відмінок (of/from country)
    if re.search(r'втрату\s+.*?\[country\|e\]', line_lower) or \
       re.search(r'з\s+\[country\|e\]', line_lower) or \
       re.search(r'від\s+\[country\|e\]', line_lower):
        return 'держави'

    # Орудний відмінок (with country, by country)
    if re.search(r'керується\s+.*?\[country\|e\]', line_lower) or \
       re.search(r'з\s+нашою\s+\[country\|e\]', line_lower) or \
       re.search(r'керування\s+.*?\[country\|e\]', line_lower):
        return 'державою'

    # Знахідний відмінок (винний відмінок)
    # За замовчуванням для "іншої країни приймає/отримує"

    # Називний відмінок (subject of sentence) - за замовчуванням
    # "інша держава", "наша держава"
    return 'держава'

def fix_country_cases(input_file, output_file):
    """
    Замінює всі [country|e] на Concept з правильним відмінком
    """

    replacements_count = 0

    with open(input_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        original_line = line

        # Знайти всі входження [country|e]
        if '[country|e]' in line:
            case = determine_case(line)
            # Замінити на новий формат
            new_line = line.replace('[country|e]', f"[Concept('country','{case}')|e]")

            if new_line != original_line:
                replacements_count += 1
                print(f"Line {len(new_lines)+1}: {case}")
                print(f"  OLD: {original_line.strip()}")
                print(f"  NEW: {new_line.strip()}")
                print()

            new_lines.append(new_line)
        else:
            new_lines.append(line)

    # Записати результат
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        f.writelines(new_lines)

    print(f"\n{'='*80}")
    print(f"Заміни виконано: {replacements_count}")
    print(f"Файл збережено: {output_file}")
    print(f"{'='*80}")

    return replacements_count

if __name__ == '__main__':
    input_file = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/messages_l_english.yml'
    output_file = input_file  # Перезаписуємо оригінальний файл

    fix_country_cases(input_file, output_file)
