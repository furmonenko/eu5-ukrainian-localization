#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для виправлення старих форматів відмінків у файлі modifier_types_l_english.yml
"""

import re
import sys

def fix_modifiers(input_file, output_file):
    """Виправляє старі формати відмінків на нові з правильними українськими відмінками"""

    # Читаємо файл з UTF-8 BOM
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Словник замін для різних концептів та їх відмінків
    # Формат: старий_патерн -> новий_формат_з_правильним_відмінком

    replacements = {
        # country -> держава (591 входжень)
        r'\[country\|e\]': "держава",  # Базова форма - буде уточнена контекстом

        # location -> район (345 входжень)
        r'\[location\|e\]': "район",  # Базова форма

        # locations -> райони/районах
        r'\[locations\|e\]': "районах",  # Зазвичай "у всіх районах"

        # war -> війна
        r'\[war\|e\]': "війну",  # Зазвичай "оголосити війну"

        # unit -> підрозділ/відділ
        r'\[unit\|e\]': "підрозділ",

        # battle -> битва
        r'\[battle\|e\]': "битві",  # Зазвичай "у битві"

        # food -> їжа
        r'\[food\|e\]': "їжі",  # Зазвичай родовий

        # pops -> населення
        r'\[pops\|e\]': "населення",

        # regiment -> полк
        r'\[regiment\|e\]': "полка",  # Часто родовий

        # ship -> корабель
        r'\[ship\|e\]': "корабля",  # Часто родовий

        # army -> армія
        r'\[army\|e\]': "армія",

        # navy -> флот
        r'\[navy\|e\]': "флот",

        # seazone -> акваторія
        r'\[seazone\|e\]': "акваторію",

        # seazones -> акваторії
        r'\[seazones\|e\]': "акваторіями",

        # province -> провінція
        r'\[province\|e\]': "провінції",

        # provinces -> провінції
        r'\[provinces\|e\]': "провінціях",

        # building -> споруда
        r'\[building\|e\]': "споруди",

        # buildings -> споруди
        r'\[buildings\|e\]': "споруд",
    }

    # Застосовуємо базові заміни (це тільки перший прохід)
    # for old, new in replacements.items():
    #     content = re.sub(old, new, content)

    # Тепер робимо контекстні заміни з правильним форматом Concept
    # На основі російського еталону

    context_replacements = [
        # country -> держава
        (r'a \[country\|e\]', "Concept('country','державі')"),
        (r'of a \[country\|e\]', "Concept('country','держави')"),
        (r'in a \[country\|e\]', "Concept('country','державі')"),
        (r'for a \[country\|e\]', "Concept('country','держави')"),
        (r'that \[country\|e\]', "Concept('country','держава')"),
        (r'this \[country\|e\]', "Concept('country','державі')"),
        (r'our \[country\|e\]', "Concept('country','держави')"),
        (r'the \[country\|e\]', "Concept('country','держава')"),
        (r'\[country\|e\] can', "Concept('country','держава')"),
        (r'\[country\|e\] gets', "Concept('country','держава')"),
        (r'\[country\|e\] has', "Concept('country','держава')"),
        (r'\[country\|e\] to have', "Concept('country','держави')"),
        (r'\[country\|e\] to capitulate', "Concept('country','держава')"),
        (r'\[country\|e\] \[owns\|e\]', "Concept('country','держава')"),
        (r'\[country\|e\] \[controls\|e\]', "Concept('country','держава')"),
        (r'\[country\|e\] shows', "Concept('country','держава')"),
        (r'\[country\|e\] actively', "Concept('country','держава')"),

        # location -> район
        (r'a \[location\|e\]', "Concept('location','район')"),
        (r'of a \[location\|e\]', "Concept('location','району')"),
        (r'in a \[location\|e\]', "Concept('location','районі')"),
        (r'in this \[location\|e\]', "Concept('location','районі')"),
        (r'this \[location\|e\]', "Concept('location','район')"),
        (r'from a \[location\|e\]', "Concept('location','району')"),
        (r'from this \[location\|e\]', "Concept('location','району')"),
        (r'through a \[location\|e\]', "Concept('location','район')"),
        (r'through this \[location\|e\]', "Concept('location','район')"),
        (r'to this \[location\|e\]', "Concept('location','район')"),
        (r'can propagate a \[location\|e\]', "Concept('location','район')"),
        (r'if this \[location\|e\]', "Concept('location','район')"),

        # locations -> райони
        (r'all \[locations\|e\]', "Concept('locations','районах')"),
        (r'in all \[locations\|e\]', "Concept('locations','районах')"),
        (r'between \[locations\|e\]', "Concept('locations','районами')"),
        (r'\[locations\|e\] in a', "Concept('locations','районів')"),
        (r'\[locations\|e\] of a', "Concept('locations','районів')"),
        (r'\[locations\|e\] of the country', "Concept('locations','районах')"),
        (r'\[locations\|e\] of this', "Concept('locations','районах')"),
        (r'\[locations\|e\] owned', "Concept('locations','районів')"),
        (r'\[locations\|e\] we', "Concept('locations','районах')"),
        (r'\[locations\|e\]\.', "Concept('locations','районах')."),
        (r'between \[locations\|e\]', "Concept('locations','районами')"),

        # war -> війна
        (r'a \[war\|e\]', "Concept('war','війну')"),
        (r'during a \[war\|e\]', "Concept('war','війни')"),

        # unit -> підрозділ
        (r'a \[unit\|e\]', "Concept('unit','підрозділ')"),
        (r'that a \[unit\|e\]', "Concept('unit','підрозділ')"),
        (r'if the \[unit\|e\]', "Concept('unit','підрозділ')"),

        # battle -> битва
        (r'a \[battle\|e\]', "Concept('battle','битві')"),
        (r'in a \[battle\|e\]', "Concept('battle','битві')"),
        (r'in \[battle\|e\]', "Concept('battle','битві')"),

        # food -> їжа
        (r'how much \[food\|e\]', "Concept('food','їжі')"),
        (r'of \[food\|e\]', "Concept('food','їжі')"),

        # pops -> населення
        (r'\[pops\|e\] can live', "Concept('pops','населення')"),
        (r'\[pops\|e\] \[promote\|e\]', "Concept('pops','населення')"),
        (r'\[pops\|e\] \[demote\|e\]', "Concept('pops','населення')"),
        (r'\[pops\|e\] \[migrate\|e\]', "Concept('pops','населення')"),
        (r'\[pops\|e\] \[convert\|e\]', "Concept('pops','населення')"),
        (r'\[pops\|e\] \[assimilate\|e\]', "Concept('pops','населення')"),
        (r'\[pops\|e\] want', "Concept('pops','населення')"),
        (r'\[pops\|e\] gathering', "Concept('pops','населення')"),
        (r'of \[pops\|e\]', "Concept('pops','населення')"),
        (r'for \[pops\|e\]', "Concept('pops','населення')"),
        (r'many \[pops\|e\]', "Concept('pops','населення')"),

        # regiment -> полк
        (r'a \[regiment\|e\]', "Concept('regiment','полка')"),
        (r'of a \[regiment\|e\]', "Concept('regiment','полка')"),
        (r'that a \[regiment\|e\]', "Concept('regiment','полк')"),

        # ship -> корабель
        (r'a \[ship\|e\]', "Concept('ship','корабля')"),
        (r'of a \[ship\|e\]', "Concept('ship','корабля')"),
        (r'that a \[ship\|e\]', "Concept('ship','корабель')"),

        # army -> армія
        (r'an \[army\|e\]', "Concept('army','армія')"),
        (r'that an \[army\|e\]', "Concept('army','армія')"),

        # navy -> флот
        (r'a \[navy\|e\]', "Concept('navy','флот')"),
        (r'that a \[navy\|e\]', "Concept('navy','флот')"),

        # seazone -> акваторія
        (r'a \[seazone\|e\]', "Concept('seazone','акваторію')"),
        (r'in the \[seazone\|e\]', "Concept('seazone','акваторії')"),

        # seazones -> акваторії
        (r'in all \[seazones\|e\]', "Concept('seazones','акваторіях')"),
        (r'adjacent \[seazones\|e\]', "Concept('seazones','акваторіях')"),

        # province -> провінція
        (r'in the \[province\|e\]', "Concept('province','провінції')"),

        # provinces -> провінції
        (r'in all \[provinces\|e\]', "Concept('provinces','провінціях')"),

        # building -> споруда
        (r'of the \[building\|e\]', "Concept('building','споруди')"),
        (r'of this \[building\|e\]', "Concept('building','споруди')"),

        # buildings -> споруди
        (r'and \[buildings\|e\]', "Concept('buildings','споруд')"),
    ]

    print(f"Виправлення файлу {input_file}...")
    print(f"Розмір початкового файлу: {len(content)} байт")

    # Тепер читаємо український файл рядок за рядком та застосовуємо контекстні заміни
    lines = content.split('\n')
    fixed_lines = []
    changes_count = 0

    for line_num, line in enumerate(lines, 1):
        original_line = line

        # Пропускаємо перший рядок та технічні рядки
        if line_num == 1 or line.strip() == '' or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue

        # Застосовуємо контекстні заміни
        for old_pattern, new_value in context_replacements:
            if re.search(old_pattern, line):
                line = re.sub(old_pattern, f'[{new_value}|e]', line)
                if line != original_line:
                    changes_count += 1

        fixed_lines.append(line)

    result = '\n'.join(fixed_lines)

    # Записуємо результат з BOM
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        f.write(result)

    print(f"Виправлено {changes_count} рядків")
    print(f"Результат збережено у {output_file}")

    return changes_count

if __name__ == "__main__":
    input_file = "/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/modifier_types_l_english.yml"
    output_file = "/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/modifier_types_l_english.yml.new"

    changes = fix_modifiers(input_file, output_file)
    print(f"\nВсього виправлень: {changes}")
