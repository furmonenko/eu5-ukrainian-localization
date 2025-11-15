#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перевірки стану перекладу файлів локалізації EU5
Перевіряє, чи файли містять українську, російську чи англійську мову
"""

import os
import re
from pathlib import Path

# Патерни для визначення мови
UKRAINIAN_PATTERNS = [
    'є', 'ї', 'і', 'ґ',  # Унікальні українські літери
    'тися', 'ться',      # Українські закінчення
    'держава', 'держави', 'держав',
    'має', 'маємо', 'мають',
    'було', 'буде', 'будуть',
]

RUSSIAN_PATTERNS = [
    'ы', 'э', 'ъ',       # Російські літери (не в українській)
    'тся', 'ться',       # Російські форми (але є і в укр)
    'держава', 'державы',
    'либо', 'своей', 'своим',
    'что', 'этот', 'который',
]

ENGLISH_PATTERNS = [
    'the ', 'and ', 'of ', 'to ', 'in ',
    'country', 'province', 'war', 'peace',
    'government', 'military', 'economic',
]

def detect_language(text):
    """Визначає мову тексту на основі патернів"""
    if not text or len(text) < 20:
        return "EMPTY"

    text_lower = text.lower()

    # Підрахунок збігів для кожної мови
    ukrainian_score = 0
    russian_score = 0
    english_score = 0

    # Перевірка українських патернів
    for pattern in UKRAINIAN_PATTERNS:
        if pattern in text_lower:
            ukrainian_score += text_lower.count(pattern)

    # Перевірка російських патернів
    for pattern in RUSSIAN_PATTERNS:
        if pattern in text_lower:
            russian_score += text_lower.count(pattern)

    # Перевірка англійських патернів
    for pattern in ENGLISH_PATTERNS:
        if pattern in text_lower:
            english_score += text_lower.count(pattern)

    # Визначення мови на основі балів
    scores = {
        'UKRAINIAN': ukrainian_score,
        'RUSSIAN': russian_score,
        'ENGLISH': english_score
    }

    # Якщо українська і російська близькі (кирилиця), але є англійська
    if english_score > ukrainian_score + russian_score:
        return 'ENGLISH'

    # Якщо є унікальні українські літери
    if any(char in text for char in ['є', 'ї', 'ґ']):
        return 'UKRAINIAN'

    # Якщо є унікальні російські літери
    if any(char in text for char in ['ы', 'э', 'ъ']):
        return 'RUSSIAN'

    # За балами
    max_lang = max(scores, key=scores.get)
    if scores[max_lang] > 0:
        return max_lang

    return "UNKNOWN"

def check_file(filepath):
    """Перевіряє один файл"""
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # Визначення мови
        language = detect_language(content)

        # Підрахунок рядків
        lines = content.split('\n')
        total_lines = len(lines)

        # Підрахунок рядків локалізації (не коментарі, не порожні)
        loc_lines = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and ':' in line:
                loc_lines += 1

        return {
            'file': os.path.basename(filepath),
            'path': filepath,
            'language': language,
            'total_lines': total_lines,
            'loc_lines': loc_lines,
            'size_kb': os.path.getsize(filepath) / 1024
        }
    except Exception as e:
        return {
            'file': os.path.basename(filepath),
            'path': filepath,
            'language': 'ERROR',
            'total_lines': 0,
            'loc_lines': 0,
            'size_kb': 0,
            'error': str(e)
        }

def main():
    # Шлях до папки з локалізацією
    base_path = Path('/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english')

    # Знайти всі yml файли (виключаючи events)
    yml_files = []
    for yml_file in base_path.glob('*.yml'):
        if yml_file.is_file():
            yml_files.append(yml_file)

    yml_files.sort()

    print(f"Знайдено {len(yml_files)} файлів для перевірки...")
    print("=" * 80)

    # Статистика
    stats = {
        'UKRAINIAN': [],
        'RUSSIAN': [],
        'ENGLISH': [],
        'EMPTY': [],
        'UNKNOWN': [],
        'ERROR': []
    }

    # Перевірка кожного файлу
    for i, filepath in enumerate(yml_files, 1):
        result = check_file(filepath)
        stats[result['language']].append(result)

        # Виведення прогресу
        if i % 10 == 0 or i == len(yml_files):
            print(f"Перевірено: {i}/{len(yml_files)}", end='\r')

    print("\n" + "=" * 80)

    # Виведення результатів
    print("\n📊 СТАТИСТИКА:\n")
    print(f"✅ УКРАЇНСЬКА:  {len(stats['UKRAINIAN'])} файлів")
    print(f"🇷🇺 РОСІЙСЬКА:   {len(stats['RUSSIAN'])} файлів")
    print(f"🇬🇧 АНГЛІЙСЬКА:  {len(stats['ENGLISH'])} файлів")
    print(f"⚪ ПОРОЖНІ:      {len(stats['EMPTY'])} файлів")
    print(f"❓ НЕВІДОМО:     {len(stats['UNKNOWN'])} файлів")
    print(f"❌ ПОМИЛКИ:      {len(stats['ERROR'])} файлів")
    print(f"\nВСЬОГО:         {len(yml_files)} файлів")

    # Збереження детального звіту
    report_path = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/TRANSLATION_STATUS_REPORT.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ДЕТАЛЬНИЙ ЗВІТ ПРО СТАН ПЕРЕКЛАДУ\n")
        f.write("=" * 80 + "\n\n")

        for lang in ['UKRAINIAN', 'RUSSIAN', 'ENGLISH', 'EMPTY', 'UNKNOWN', 'ERROR']:
            if stats[lang]:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"{lang}: {len(stats[lang])} файлів\n")
                f.write(f"{'=' * 80}\n\n")

                for item in sorted(stats[lang], key=lambda x: x['file']):
                    f.write(f"  {item['file']:<50} | {item['loc_lines']:>5} рядків | {item['size_kb']:>7.1f} KB\n")

    print(f"\n💾 Детальний звіт збережено: {report_path}")

    # Створення CSV для аналізу
    csv_path = '/Users/furmonenko/Desktop/eu5-ukrainian-localization/translation_status.csv'
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("Файл,Мова,Рядків локалізації,Розмір (KB),Шлях\n")
        for lang in stats:
            for item in stats[lang]:
                f.write(f"{item['file']},{lang},{item['loc_lines']},{item['size_kb']:.1f},{item['path']}\n")

    print(f"💾 CSV звіт збережено: {csv_path}")

    print("\n" + "=" * 80)
    print("\n✅ ЗАВЕРШЕНО!\n")

if __name__ == '__main__':
    main()
