#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для виправлення конкретних помилок у відмінках після першого проходу
"""

import re

# Список точкових виправлень на основі аналізу російського еталону
FIXES = [
    # Рядок 83: керується має бути орудний відмінок
    {
        'old': r"керується через \$REGENCY\$\.",
        'old_case': "держава",
        'new_case': "державою",
        'reason': "керується ким/чим? - орудний відмінок"
    },
    # Рядок 149: керування нашою великою має бути орудний відмінок
    {
        'old': r"керування нашою великою \[Concept\('country','держава'\)\|e\]",
        'old_case': "держава",
        'new_case': "державою",
        'reason': "керування ким/чим? - орудний відмінок"
    },
    # Рядок 242: до держави - родовий після "до"
    {
        'old': r"до \[Concept\('country','держава'\)\|e\]\.",
        'old_case': "держава",
        'new_case': "держави",
        'reason': "до кого/чого? - родовий відмінок"
    },
    # Рядок 842: до нашої - родовий
    {
        'old': r"до нашої \[Concept\('country','держава'\)\|e\]\.",
        'old_case': "держава",
        'new_case': "держави",
        'reason': "до чого? - родовий відмінок"
    },
]

def apply_specific_fixes():
    """
    Застосувати конкретні виправлення
    """

    input_file = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/messages_l_english.yml'

    with open(input_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    fixes_applied = 0

    for fix in FIXES:
        pattern = fix['old']
        old_concept = f"[Concept('country','{fix['old_case']}')|e]"
        new_concept = f"[Concept('country','{fix['new_case']}')|e]"

        # Знайти всі входження
        matches = list(re.finditer(pattern, content))

        if matches:
            for match in matches:
                # Замінити старий відмінок на новий у знайденому фрагменті
                matched_text = match.group(0)
                new_text = matched_text.replace(old_concept, new_concept)
                content = content.replace(matched_text, new_text, 1)
                fixes_applied += 1

                print(f"✓ Виправлено: {fix['reason']}")
                print(f"  Було:  {matched_text}")
                print(f"  Стало: {new_text}")
                print()

    # Зберегти
    with open(input_file, 'w', encoding='utf-8-sig') as f:
        f.write(content)

    print("=" * 80)
    print(f"Застосовано виправлень: {fixes_applied}")
    print("=" * 80)

    return fixes_applied

if __name__ == '__main__':
    apply_specific_fixes()
