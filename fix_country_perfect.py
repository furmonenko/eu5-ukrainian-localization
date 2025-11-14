#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для заміни [country|e] на правильні відмінки української мови.
Базується на ТОЧНОМУ аналізі російського еталону та лінгвістиці української мови.
"""

import re

def analyze_case(line):
    """
    Визначає відмінок слова "держава" в контексті речення.

    Українські відмінки:
    1. Називний (хто? що?) - держава
    2. Родовий (кого? чого?) - держави
    3. Давальний (кому? чому?) - державі
    4. Знахідний (кого? що?) - державу
    5. Орудний (ким? чим?) - державою
    6. Місцевий (на чому? де?) - державі
    """

    line_lower = line.lower()

    # === МІСЦЕВИЙ ВІДМІНОК (де? у чому?) - "у/в державі" ===
    # Паттерни: "в нашій [country", "у нашій [country", "в іншій [country"
    if re.search(r'\b(в|у)\s+(нашій|іншій|цій)\s+\[country\|e\]', line_lower):
        return 'державі'

    # "що знаходиться в нашій [country"
    if 'знаходиться' in line_lower and re.search(r'\b(в|у)\s+нашій\s+\[country\|e\]', line_lower):
        return 'державі'

    # "був у нашій [country"
    if re.search(r'був\s+(в|у)\s+нашій\s+\[country\|e\]', line_lower):
        return 'державі'

    # === РОДОВИЙ ВІДМІНОК (кого? чого?) - "держави" ===
    # "втрату $OLD" - втрата кого? чого?
    if 'втрату' in line_lower and '\[country\|e\]' in line:
        return 'держави'

    # "частиною нашої [country" - частина чого?
    if re.search(r'частиною\s+нашої\s+\[country\|e\]', line_lower):
        return 'держави'

    # "для нашої [country" - для чого?
    if re.search(r'для\s+нашої\s+\[country\|e\]', line_lower):
        return 'держави'

    # "від нашої [country" - від чого?
    if re.search(r'від\s+(нашої|іншої)\s+\[country\|e\]', line_lower):
        return 'держави'

    # "іншої [country" після іменника (контекст родового)
    if re.search(r'(з|від)\s+іншої\s+\[country\|e\]', line_lower):
        return 'держави'

    # "величие нашей державы" = "велич нашої держави"
    if 'наш' in line_lower and re.search(r'(велич|користь|користі)\s.*?\[country\|e\]', line_lower):
        return 'держави'

    # "оборону [country" - оборона чого?
    if 'оборону' in line_lower and '\[country\|e\]' in line:
        return 'держави'

    # "до [country" -> "до держави" (родовий після "до")
    # НЕ ПЛУТАТИ з "до нашої [country" яке є давальним

    # "з іншої [religious_school] до нашої [country"
    if ' до нашої \[country\|e\]' in line_lower:
        return 'держави'

    # === ОРУДНИЙ ВІДМІНОК (ким? чим?) - "державою" ===
    # "керується через" = "керується чим?"
    if 'керується' in line_lower and '\[country\|e\]' in line:
        return 'державою'

    # "керування нашою [country" = "керування чим?"
    if re.search(r'керування\s+(нашою|великою)\s+\[country\|e\]', line_lower):
        return 'державою'

    # "правление державой" = "правління державою"
    if 'правлен' in line_lower:
        return 'державою'

    # "з іншою [country" у війні - орудний
    if re.search(r'з\s+іншою\s+\[country\|e\]\s+(в|у)\s+нашій', line_lower):
        return 'державою'

    # === ДАВАЛЬНИЙ ВІДМІНОК (кому? чому?) - "державі" ===
    # "іншій [country]" після "до", "дарувати"
    if re.search(r'(подарунок|надсилаємо)\s+(іншій|другій)\s+\[country\|e\]', line_lower):
        return 'державі'

    # === ЗНАХІДНИЙ ВІДМІНОК (кого? що?) - "державу" ===
    # "розглядає нашу [country" - розглядає що?
    if re.search(r'розглядає\s+нашу\s+\[country\|e\]', line_lower):
        return 'державу'

    # "нашу [country" - знахідний
    if re.search(r'\bнашу\s+\[country\|e\]', line_lower):
        return 'державу'

    # "в нашу [country" - в що?
    if re.search(r'\b(в|у)\s+нашу\s+\[country\|e\]', line_lower):
        return 'державу'

    # === НАЗИВНИЙ ВІДМІНОК (хто? що?) - "держава" (за замовчуванням) ===
    # "інша [country] приймає" - підмет, тому називний
    # "Коли [country] робить щось"
    # "незалежна [country]" - означення в називному

    # Якщо жодна умова не спрацювала - називний відмінок
    return 'держава'

def fix_country_references():
    """
    Замінює всі [country|e] на правильний формат з відмінками
    """

    input_file = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/messages_l_english.yml'

    # Читаємо файл з BOM
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    new_lines = []
    stats = {
        'держава': 0,
        'держави': 0,
        'державі': 0,
        'державу': 0,
        'державою': 0
    }

    replacements_details = []

    for line_num, line in enumerate(lines, 1):
        if '[country|e]' in line:
            # Визначаємо відмінок
            case = analyze_case(line)
            stats[case] += 1

            # Виконуємо заміну
            new_line = line.replace('[country|e]', f"[Concept('country','{case}')|e]")

            replacements_details.append({
                'line': line_num,
                'case': case,
                'old': line.rstrip('\n'),
                'new': new_line.rstrip('\n')
            })

            new_lines.append(new_line)
        else:
            new_lines.append(line)

    # Виводимо детальний звіт
    print("=" * 100)
    print("ЗВІТ ПРО ВИПРАВЛЕННЯ ВІДМІНКІВ СЛОВА 'ДЕРЖАВА'")
    print("=" * 100)
    print(f"\nВсього знайдено входжень [country|e]: {sum(stats.values())}\n")

    print("СТАТИСТИКА ПО ВІДМІНКАХ:")
    print("-" * 60)
    for case, count in sorted(stats.items(), key=lambda x: -x[1]):
        percentage = (count / sum(stats.values()) * 100) if sum(stats.values()) > 0 else 0
        print(f"  {case:15} : {count:4} входжень ({percentage:5.1f}%)")

    print("\n" + "=" * 100)
    print("ПЕРШІ 50 ЗАМІН (для перевірки):")
    print("=" * 100)

    for detail in replacements_details[:50]:
        print(f"\n[Рядок {detail['line']}] → Відмінок: {detail['case']}")
        print(f"  БУЛО:  {detail['old']}")
        print(f"  СТАЛО: {detail['new']}")

    # Зберігаємо файл з BOM
    with open(input_file, 'w', encoding='utf-8-sig') as f:
        f.writelines(new_lines)

    print("\n" + "=" * 100)
    print(f"✓ Файл успішно збережено: {input_file}")
    print(f"✓ Виконано {sum(stats.values())} замін")
    print("=" * 100)

    return sum(stats.values())

if __name__ == '__main__':
    total = fix_country_references()
    print(f"\n✓ ЗАВЕРШЕНО! Замінено {total} входжень [country|e] на правильні відмінки")
