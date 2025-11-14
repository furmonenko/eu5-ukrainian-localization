#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Вручну перекладені рядки units_l_english.yml
Я сам пишу кожен переклад
"""

import re

# Ручні переклади рядок за рядком
MANUAL_TRANSLATIONS = {
    # Описи категорій військ (рядки 277-284)
    'army_artillery_desc': "Зброя далекого бою, якою керує розрахунок спеціалістів і яка запускає снаряди, призначені головним чином для прориву та руйнування укріплень.",
    'army_auxiliary_desc': "Допоміжні війська являють собою надзвичайно різноманітний набір загонів, метою яких є підтримка основних сил армії.",
    'army_cavalry_desc': "Кавалерія — загони вершників, які відрізняються високою маневреністю та ударною силою.",
    'army_infantry_desc': "Піхота — загони солдатів, які воюють у пішому строю і зазвичай становлять основну масу регулярного війська.",
    'navy_galley_desc': "Галери — це судна з невеликою осадкою, які приводяться в рух переважно веслами. Найчастіше використовуються в прибережних районах.",
    'navy_heavy_ship_desc': "Важкі кораблі — великі судна, оснащені кількома щоглами та палубами, які використовуються для ведення війни та демонстрації сили по всьому світу.",
    'navy_light_ship_desc': "Легкі судна — невеликі та відносно дешеві судна з малою осадкою, орієнтовані на швидкість, маневреність та простоту навігації.",
    'navy_transport_desc': "Транспорт — змішані пасажирські та торгові судна, що використовуються для перевезення військ через моря.",
}

def apply_translations(filepath):
    """Застосувати ручні переклади"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    new_lines = []
    changes = 0

    for line in lines:
        modified = False
        for key, translation in MANUAL_TRANSLATIONS.items():
            # Шукаємо рядок з цим ключем
            pattern = f'^(\\s*){re.escape(key)}:\\s*"(.+)"(.*)$'
            match = re.match(pattern, line.rstrip())
            if match:
                indent, _, suffix = match.groups()
                new_lines.append(f'{indent}{key}: "{translation}"{suffix}\n')
                modified = True
                changes += 1
                break

        if not modified:
            new_lines.append(line)

    # Зберігаємо
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.writelines(new_lines)

    print(f"✓ Застосовано {changes} ручних перекладів")

if __name__ == "__main__":
    filepath = "/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/units_l_english.yml"
    apply_translations(filepath)
