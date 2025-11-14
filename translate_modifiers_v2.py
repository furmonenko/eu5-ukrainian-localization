#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Покращений скрипт для перекладу modifier_types з російської на українську
з використанням повного словника перекладів
"""

import re
import sys
from full_translation_dict import TRANSLATIONS

def translate_text(text):
    """Переклад тексту з російської на українську"""
    result = text

    # Застосовуємо заміни зі словника (від довших до коротших)
    for ru, uk in TRANSLATIONS:
        # Використовуємо прості заміни (не regex) для швидкості
        result = result.replace(ru, uk)

    return result

def process_file(russian_file, output_file):
    """Обробка російського файлу та створення українського"""

    print(f"Читання російського файлу {russian_file}...")

    # Читаємо російський файл
    try:
        with open(russian_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ПОМИЛКА: Файл {russian_file} не знайдено!")
        return False

    print(f"Розмір файлу: {len(content)} байт")

    # Обробляємо рядок за рядком
    lines = content.split('\n')
    translated_lines = []

    print(f"Починаємо переклад {len(lines)} рядків...")

    for line_num, line in enumerate(lines, 1):
        # Перший рядок змінюємо на l_english
        if line_num == 1:
            translated_lines.append('l_english:')
            continue

        # Пропускаємо порожні рядки та коментарі
        if not line.strip() or line.strip().startswith('#'):
            translated_lines.append(line)
            continue

        # Перекладаємо рядок
        translated_line = translate_text(line)
        translated_lines.append(translated_line)

        # Показуємо прогрес
        if line_num % 500 == 0:
            print(f"Оброблено {line_num}/{len(lines)} рядків ({line_num*100//len(lines)}%)...")

    result = '\n'.join(translated_lines)

    # Записуємо результат з BOM
    try:
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write(result)
        print(f"\nПереклад завершено успішно!")
        print(f"Результат збережено у {output_file}")
        print(f"Всього перекладено {len(lines)} рядків")
        return True
    except Exception as e:
        print(f"ПОМИЛКА при збереженні: {e}")
        return False

if __name__ == "__main__":
    russian_file = "/Users/furmonenko/Desktop/eu5-ukrainian-localization/reference/russian/modifier_types_l_russian.yml"
    output_file = "/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/modifier_types_l_english.yml"

    success = process_file(russian_file, output_file)

    if success:
        print("\n" + "="*60)
        print("ГОТОВО! Переклад створено.")
        print("="*60)

        # Перевірка кількості залишкових російських слів
        print("\nПеревірка якості перекладу...")
        with open(output_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # Підрахунок популярних російських слів що могли залишитися
        russian_words = [
            "который", "которая", "которые", "которую", "которого",
            "может", "могут", "будет", "будут", "нужно", "необходимо",
            "влияет", "изменяет", "определяет",
        ]

        found_russian = []
        for word in russian_words:
            count = content.lower().count(word.lower())
            if count > 0:
                found_russian.append((word, count))

        if found_russian:
            print("\nУВАГА: Знайдено російські слова, які потребують додаткового перекладу:")
            for word, count in found_russian[:10]:  # Показуємо перші 10
                print(f"  '{word}': {count} входжень")
        else:
            print("\nВідмінно! Основні російські слова перекладено.")
    else:
        print("\nПОМИЛКА: Переклад не вдався.")
        sys.exit(1)
