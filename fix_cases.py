#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для виправлення старих форматів відмінків в українському файлі локалізації.
Замінює старі теги типу [country|e] на нові формати Concept з правильними відмінками.
"""

import re

def read_file(filepath):
    """Читає файл з BOM"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return f.read()

def write_file(filepath, content):
    """Записує файл з BOM"""
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(content)

def process_file(ukrainian_path):
    """Обробляє український файл"""

    content = read_file(ukrainian_path)

    # Статистика замін
    replacements = {}

    # Список замін (старий_шаблон, новий_шаблон, опис)
    # Порядок важливий! Спочатку більш специфічні, потім загальні

    simple_replacements = [
        # Складні випадки спочатку (щоб не конфліктували з простими)
        # markets|E з великої літери (використовується в середині речення після прикметника)
        (r'\[markets\|E\]', "[Concept('markets','ринки')|e]", "markets|E -> ринки"),
        (r'\[merchants\|E\]', "[Concept('merchants','купці')|e]", "merchants|E -> купці"),
        (r'\[locations\|E\]', "[Concept('locations','локації')|e]", "locations|E -> локації"),

        # subject_loyalty -> лояльність
        (r'\[subject_loyalty\|e\]', "[Concept('subject_loyalty','лояльність')|e]", "subject_loyalty"),

        # overlord -> сюзерен (в контексті "towards their overlord" = "до сюзерена" - родовий)
        (r'\[overlord\|e\]', "[Concept('overlord','сюзерена')|e]", "overlord"),

        # subject -> васал
        (r'\[subject\|e\]', "[Concept('subject','васала')|e]", "subject"),
        (r'\[subjects\|e\]', "[Concept('subjects','васалів')|e]", "subjects"),

        # country - найчастіше використовується як "в державі" (місцевий) або просто "держава"
        (r'\[country\|e\]', "[Concept('country','державі')|e]", "country"),

        # countries -> держави (множина, найчастіше родовий - "кількох держав")
        (r'\[countries\|e\]', "[Concept('countries','держав')|e]", "countries"),

        # merchants -> купці
        (r'\[merchants\|e\]', "[Concept('merchants','купців')|e]", "merchants"),

        # merchant_power -> купецька могутність
        (r'\[merchant_power\|e\]', "[Concept('merchant_power','купецька могутність')|e]", "merchant_power"),

        # markets -> ринки (найчастіше родовий - "доступ ринків")
        (r'\[markets\|e\]', "[Concept('markets','ринків')|e]", "markets"),

        # market -> ринок
        (r'\[market\|e\]', "[Concept('market','ринок')|e]", "market"),

        # market_access -> доступ
        (r'\[market_access\|e\]', "[Concept('market_access','доступ')|e]", "market_access"),

        # military_access -> військовий прохід
        (r'\[military_access\|e\]', "[Concept('military_access','військовий прохід')|e]", "military_access"),

        # fleet_basing_rights -> права базування флоту
        (r'\[fleet_basing_rights\|e\]', "[Concept('fleet_basing_rights','права базування флоту')|e]", "fleet_basing_rights"),

        # food_access -> доступ до продовольства
        (r'\[food_access\|e\]', "[Concept('food_access','доступ до продовольства')|e]", "food_access"),

        # guarantee
        (r'\[guarantee\|e\]', "[Concept('guarantee','гарантію')|e]", "guarantee"),
        (r'\[guaranteed\|e\]', "[Concept('guaranteed','гарантовані')|e]", "guaranteed"),
        (r'\[guaranteeing\|e\]', "[Concept('guaranteeing','гарантування')|e]", "guaranteeing"),

        # sound_tolls/sound_toll -> зундські мита
        (r'\[sound_tolls\|e\]', "[Concept('sound_tolls','зундські мита')|e]", "sound_tolls"),
        (r'\[sound_toll\|e\]', "[Concept('sound_toll','зундське мито')|e]", "sound_toll"),

        # armies -> армії
        (r'\[armies\|e\]', "[Concept('armies','армії')|e]", "armies"),

        # alliance -> союз
        (r'\[alliance\|e\]', "[Concept('alliance','союз')|e]", "alliance"),

        # ports -> порти
        (r'\[ports\|e\]', "[Concept('ports','порти')|e]", "ports"),

        # privateers -> корсари
        (r'\[privateers\|e\]', "[Concept('privateers','корсарів')|e]", "privateers"),

        # ships -> кораблі
        (r'\[ships\|e\]', "[Concept('ships','кораблів')|e]", "ships"),

        # provinces -> провінції
        (r'\[provinces\|e\]', "[Concept('provinces','провінцій')|e]", "provinces"),

        # buildings -> споруди
        (r'\[buildings\|e\]', "[Concept('buildings','споруди')|e]", "buildings"),
        (r'\[building\|e\]', "[Concept('building','будувати')|e]", "building"),
        (r'\[foreign_buildings\|e\]', "[Concept('foreign_buildings','іноземні споруди')|e]", "foreign_buildings"),

        # stability -> стабільність
        (r'\[stability\|e\]', "[Concept('stability','стабільність')|e]", "stability"),

        # isolated -> ізольований
        (r'\[isolated\|e\]', "[Concept('isolated','ізольованими')|e]", "isolated"),

        # import/export
        (r'\[import\|e\]', "[Concept('import','імпорт')|e]", "import"),
        (r'\[imports\|e\]', "[Concept('imports','імпорт')|e]", "imports"),
        (r'\[export\|e\]', "[Concept('export','експорт')|e]", "export"),
        (r'\[exports\|e\]', "[Concept('exports','експорт')|e]", "exports"),

        # trade -> торгівля
        (r'\[trade\|e\]', "[Concept('trade','торгівлю')|e]", "trade"),

        # gold -> золото
        (r'\[gold\|e\]', "[Concept('gold','золото')|e]", "gold"),

        # character -> персонаж
        (r'\[character\|e\]', "[Concept('character','персонажа')|e]", "character"),

        # union -> унія
        (r'\[union\|e\]', "[Concept('union','унія')|e]", "union"),

        # power_projection -> проєкція влади
        (r'\[power_projection\|e\]', "[Concept('power_projection','проєкція влади')|e]", "power_projection"),

        # heir -> спадкоємець
        (r'\[heir\|e\]', "[Concept('heir','спадкоємця')|e]", "heir"),
        (r'\[heir_selection\|e\]', "[Concept('heir_selection','вибір спадкоємця')|e]", "heir_selection"),

        # war -> війна
        (r'\[war\|e\]', "[Concept('war','війну')|e]", "war"),
        (r'\[wars\|e\]', "[Concept('wars','війни')|e]", "wars"),

        # rebels -> повстанці
        (r'\[rebels\|e\]', "[Concept('rebels','повстанців')|e]", "rebels"),

        # locations -> локації
        (r'\[locations\|e\]', "[Concept('locations','локації')|e]", "locations"),

        # goods -> товари
        (r'\[goods\|e\]', "[Concept('goods','товари')|e]", "goods"),

        # dynasty -> династія
        (r'\[dynasty\|e\]', "[Concept('dynasty','династія')|e]", "dynasty"),

        # institutions -> інституції
        (r'\[institutions\|e\]', "[Concept('institutions','інституції')|e]", "institutions"),

        # casus_belli -> привід до війни
        (r'\[casus_belli\|e\]', "[Concept('casus_belli','привід до війни')|e]", "casus_belli"),

        # cabinet_efficiency -> ефективність кабінету
        (r'\[cabinet_efficiency\|e\]', "[Concept('cabinet_efficiency','ефективність кабінету')|e]", "cabinet_efficiency"),

        # annexed -> анексовані
        (r'\[annexed\|e\]', "[Concept('annexed','анексовані')|e]", "annexed"),
    ]

    # Застосовуємо заміни
    modified_content = content
    for old_pattern, new_pattern, description in simple_replacements:
        count = len(re.findall(old_pattern, modified_content))
        if count > 0:
            modified_content = re.sub(old_pattern, new_pattern, modified_content)
            replacements[description] = count
            print(f"✓ {description}: {count} замін")

    return modified_content, replacements

def main():
    ukrainian_path = "/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/scripted_relations_l_english.yml"

    print("Починаю обробку файлу...")
    print("=" * 80)

    modified_content, replacements = process_file(ukrainian_path)

    # Зберігаємо результат
    write_file(ukrainian_path, modified_content)

    print("=" * 80)
    print(f"\n✅ Файл успішно оброблено!")
    print(f"Всього зроблено замін: {sum(replacements.values())}")
    print("\nДеталі:")
    for description, count in sorted(replacements.items(), key=lambda x: -x[1]):
        print(f"  - {description}: {count}")

if __name__ == "__main__":
    main()
