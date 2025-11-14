#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для заміни [country|e] на правильні відмінки української мови.
Базується на детальному аналізі контекстів з файлу.
"""

import re

def determine_case_context(line_num, full_line):
    """
    Визначає потрібний відмінок на основі номера рядка та контексту.

    Відмінки:
    - держава (називний - Nominative) - хто? що?
    - держави (родовий - Genitive) - кого? чого?
    - державі (давальний/місцевий - Dative/Locative) - кому? чому? / де?
    - державу (знахідний - Accusative) - кого? що?
    - державою (орудний - Instrumental) - ким? чим?
    """

    line = full_line.lower()

    # === МІСЦЕВИЙ ВІДМІНОК (у/в державі) ===
    # "в нашій [country|e]", "у нашій [country|e]", "в іншій [country|e]"
    if re.search(r'\b(в|у)\s+(нашій|іншій)\s+\[country\|e\]', line):
        return 'державі'

    # "що знаходиться в нашій [country|e]"
    if re.search(r'знаходиться\s+(в|у)\s+нашій\s+\[country\|e\]', line):
        return 'державі'

    # "був у нашій [country|e]"
    if re.search(r'був\s+(в|у)\s+нашій\s+\[country\|e\]', line):
        return 'державі'

    # "в нашій [war|e]" context потребує знахідного, але це винятки
    # "з іншою [country|e] в нашій [war|e]" - тут друге входження - місцевий
    if ' в нашій [war' in line and '[country|e]' in line:
        # Перевіряємо чи [country|e] перед " в нашій [war"
        country_pos = line.find('[country|e]')
        war_pos = line.find(' в нашій [war')
        if country_pos < war_pos:
            # [country|e] знаходиться ПЕРЕД "в нашій [war", тому це знахідний
            pass  # Не місцевий
        else:
            # не застосовується
            pass

    # === РОДОВИЙ ВІДМІНОК (держави) ===
    # "втрату держави"
    if 'втрату' in line and '[country|e]' in line:
        return 'держави'

    # "від держави", "з держави"
    if re.search(r'\b(від|з)\s+\[country\|e\]', line):
        return 'держави'

    # "частиною нашої [country|e]"
    if 'частиною нашої' in line and '[country|e]' in line:
        return 'держави'

    # "більше не є нашою [core|e] частиною нашої [country|e]"
    if 'частиною нашої [country|e]' in line:
        return 'держави'

    # "оборону [country|e]"
    if 'оборону [country|e]' in line:
        return 'держави'

    # === ОРУДНИЙ ВІДМІНОК (державою) ===
    # "керується через", "керування"
    if 'керується' in line or 'керування' in line:
        return 'державою'

    # === ДАВАЛЬНИЙ ВІДМІНОК (державі) ===
    # "до нашої [country|e]"
    if 'до нашої [country|e]' in line:
        return 'держави'  # Насправді родовий "до чого?"

    # "іншій [country|e]" (кому? чому?) - після "до", "подарунок іншій"
    if re.search(r'(подарунок|до)\s+іншій\s+\[country\|e\]', line):
        return 'державі'

    # === ЗНАХІДНИЙ ВІДМІНОК (державу) ===
    # "іншу [country|e]" в знахідному
    if 'розглядає нашу [country|e]' in line:
        return 'державу'

    # "нашу [country|e]"
    if re.search(r'нашу\s+\[country\|e\]', line):
        return 'державу'

    # === НАЗИВНИЙ ВІДМІНОК (держава) - за замовчуванням ===
    # "інша [country|e] приймає", "інша [country|e] отримує"
    # "коли [country|e] робить щось" - підмет, тому називний

    return 'держава'

def fix_file():
    """
    Основна функція для виправлення файлу
    """

    input_file = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/messages_l_english.yml'

    # Читаємо файл
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    new_lines = []
    replacements = []

    for i, line in enumerate(lines, 1):
        if '[country|e]' in line:
            # Визначаємо відмінок
            case = determine_case_context(i, line)

            # Замінюємо
            new_line = line.replace('[country|e]', f"[Concept('country','{case}')|e]")

            replacements.append({
                'line_num': i,
                'case': case,
                'old': line.strip(),
                'new': new_line.strip()
            })

            new_lines.append(new_line)
        else:
            new_lines.append(line)

    # Виводимо звіт
    print("="*100)
    print(f"ЗВІТ ПРО ЗАМІНИ")
    print("="*100)
    print(f"\nВсього знайдено входжень [country|e]: {len(replacements)}\n")

    # Статистика по відмінках
    cases_stats = {}
    for r in replacements:
        case = r['case']
        cases_stats[case] = cases_stats.get(case, 0) + 1

    print("\nСТАТИСТИКА ПО ВІДМІНКАХ:")
    print("-" * 50)
    for case, count in sorted(cases_stats.items(), key=lambda x: -x[1]):
        print(f"  {case:15} : {count:4} входжень")

    print("\n" + "="*100)
    print("ДЕТАЛІ ЗАМІН (перші 30):")
    print("="*100)

    for r in replacements[:30]:
        print(f"\nРядок {r['line_num']}: відмінок = {r['case']}")
        print(f"  БУЛО: {r['old']}")
        print(f"  СТАЛО: {r['new']}")

    # Записуємо результат
    with open(input_file, 'w', encoding='utf-8-sig') as f:
        f.writelines(new_lines)

    print("\n" + "="*100)
    print(f"✓ Файл успішно збережено!")
    print(f"✓ Виконано {len(replacements)} замін")
    print("="*100)

    return len(replacements)

if __name__ == '__main__':
    count = fix_file()
    print(f"\n✓ Завершено! Замінено {count} входжень [country|e]")
