#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Масове виправлення ВСІХ решти старих форматів відмінків
З правильними українськими перекладами
"""

import os
import re
from pathlib import Path

# Словник перекладів (базові форми - називний відмінок)
TRANSLATIONS = {
    # Люди та населення
    'pops': 'населення',
    'character': 'персонаж',
    'characters': 'персонажі',
    'ruler': 'правитель',

    # Військо
    'war': 'війна',
    'wars': 'війни',
    'army': 'армія',
    'armies': 'армії',
    'battle': 'битва',
    'battles': 'битви',

    # Релігія та культура
    'religion': 'віра',
    'religions': 'віри',
    'culture': 'культура',
    'cultures': 'культури',

    # Економіка
    'market': 'ринок',
    'markets': 'ринки',
    'food': 'їжа',
    'trade': 'торгівля',
    'merchants': 'купці',
    'merchant': 'купець',

    # Територія
    'province': 'провінція',
    'provinces': 'провінції',
    'building': 'будівля',
    'buildings': 'будівлі',

    # Інше
    'core': 'ядро',
    'cores': 'ядра',
    'unit': 'підрозділ',
    'units': 'підрозділи',
    'subject': 'васал',
    'subjects': 'васали',
    'overlord': 'сюзерен',
    'overlords': 'сюзерени',
    'alliance': 'союз',
    'alliances': 'союзи',
    'rival': 'суперник',
    'rivals': 'суперники',
    'enemy': 'ворог',
    'enemies': 'вороги',
    'neighbor': 'сусід',
    'neighbors': 'сусіди',
    'capital': 'столиця',
    'capitals': 'столиці',
    'goods': 'товари',
    'gold': 'золото',
    'manpower': 'людські ресурси',
    'sailors': 'моряки',
    'ships': 'кораблі',
    'ship': 'корабель',
    'fleet': 'флот',
    'fleets': 'флоти',
    'regiment': 'полк',
    'regiments': 'полки',
    'institution': 'інституція',
    'institutions': 'інституції',
    'age': 'епоха',
    'ages': 'епохи',
    'era': 'ера',
    'eras': 'ери',
    'dynasty': 'династія',
    'dynasties': 'династії',
    'estate': 'стан',
    'estates': 'стани',
    'rebel': 'повстанець',
    'rebels': 'повстанці',
    'colony': 'колонія',
    'colonies': 'колонії',
    'truce': 'перемир\'я',
    'truces': 'перемир\'я',
    'peace': 'мир',
    'claim': 'претензія',
    'claims': 'претензії',
    'law': 'закон',
    'laws': 'закони',
    'policy': 'політика',
    'policies': 'політики',
    'idea': 'ідея',
    'ideas': 'ідеї',
    'advisor': 'радник',
    'advisors': 'радники',
    'modifier': 'модифікатор',
    'modifiers': 'модифікатори',
    'event': 'подія',
    'events': 'події',
    'mission': 'місія',
    'missions': 'місії',
}

def fix_file(filepath):
    """Виправити один файл"""
    try:
        # Читаємо файл
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        original = content
        total_fixes = 0
        fixes_by_concept = {}

        # Патерни для НЕ заміни (технічні змінні)
        skip_patterns = [
            r'\[ROOT\.', r'\[THIS\.', r'\[SCOPE\.', r'\[SELECT_',
            r'\[GetDataModelSize', r'\[GetName', r'\[Get[A-Z]',
            r'\[Show', r'\[Calculate', r'\[Has[A-Z]', r'\[Is[A-Z]'
        ]

        def should_skip(text, pos):
            """Перевірка чи це технічна змінна"""
            for pattern in skip_patterns:
                if re.match(pattern, text[pos:pos+30]):
                    return True
            return False

        # Створюємо функції заміни для кожного концепту
        for concept, translation in TRANSLATIONS.items():
            pattern = re.escape(f'[{concept}|e]')

            def make_replacer(trans, conc):
                def replacer(match):
                    nonlocal total_fixes
                    pos = match.start()
                    if should_skip(content, pos):
                        return match.group(0)
                    total_fixes += 1
                    if conc not in fixes_by_concept:
                        fixes_by_concept[conc] = 0
                    fixes_by_concept[conc] += 1
                    return f"[Concept('{conc}','{trans}')|e]"
                return replacer

            content = re.sub(pattern, make_replacer(translation, concept), content)

        # Якщо були зміни - зберігаємо
        if content != original:
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            return total_fixes, fixes_by_concept

        return 0, {}

    except Exception as e:
        print(f"ПОМИЛКА в {filepath}: {e}")
        return 0, {}

def main():
    base_dir = Path("/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english")

    total_fixes = 0
    all_fixes_by_concept = {}
    fixed_files = []

    print("Починаю масове виправлення всіх старих форматів...")
    print("=" * 70)

    # Обробляємо всі .yml файли
    for yml_file in base_dir.rglob("*.yml"):
        file_fixes, fixes_by_concept = fix_file(yml_file)
        if file_fixes > 0:
            total_fixes += file_fixes
            fixed_files.append((str(yml_file.relative_to(base_dir)), file_fixes))

            # Збираємо статистику по концептах
            for concept, count in fixes_by_concept.items():
                if concept not in all_fixes_by_concept:
                    all_fixes_by_concept[concept] = 0
                all_fixes_by_concept[concept] += count

            print(f"✓ {yml_file.name}: {file_fixes} виправлень")

    # Звіт
    print("\n" + "=" * 70)
    print("ПІДСУМОК ВИПРАВЛЕНЬ")
    print("=" * 70)
    print(f"Всього файлів виправлено: {len(fixed_files)}")
    print(f"ЗАГАЛОМ ВИПРАВЛЕНЬ: {total_fixes}")

    print("\nВиправлень по концептах:")
    sorted_concepts = sorted(all_fixes_by_concept.items(), key=lambda x: x[1], reverse=True)
    for concept, count in sorted_concepts:
        translation = TRANSLATIONS.get(concept, concept)
        print(f"  [{concept}|e] → {translation}: {count}")

    if fixed_files:
        print("\nТоп-20 файлів з найбільшою кількістю виправлень:")
        sorted_files = sorted(fixed_files, key=lambda x: x[1], reverse=True)[:20]
        for i, (file, count) in enumerate(sorted_files, 1):
            print(f"  {i}. {file}: {count} виправлень")

if __name__ == "__main__":
    main()
