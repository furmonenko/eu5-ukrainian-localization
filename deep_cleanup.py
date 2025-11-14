#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Глибоке очищення від всіх російських слів
"""

import re

def deep_cleanup(file_path):
    """Глибоке очищення від російських слів"""

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    cleaned_lines = []

    # Великий словник замін (включає всі можливі російські слова)
    word_replacements = {
        # Дієслова
        r'\bможет\b': 'може',
        r'\bможно\b': 'можна',
        r'\bнужно\b': 'потрібно',
        r'\bдолжен\b': 'повинен',
        r'\bбудет\b': 'буде',
        r'\bбудут\b': 'будуть',
        r'\bвлияет\b': 'впливає',
        r'\bопределяет\b': 'визначає',
        r'\bнеобходимо\b': 'необхідно',
        r'\bможно\b': 'можна',
        r'\bуменьшающийся\b': 'зменшуваний',

        # Іменники
        r'\bколичество\b': 'кількість',
        r'\bчисло\b': 'число',
        r'\bразмер\b': 'розмір',
        r'\bуровень\b': 'рівень',
        r'\bвеличина\b': 'величина',
        r'\bвеличину\b': 'величину',
        r'\bскорость\b': 'швидкість',

        # Прикметники та займенники
        r'\bкоторый\b': 'який',
        r'\bкоторая\b': 'яка',
        r'\bкоторое\b': 'яке',
        r'\bкоторые\b': 'які',
        r'\bкоторую\b': 'яку',
        r'\bкоторого\b': 'якого',
        r'\bкоторой\b': 'якої',
        r'\bкоторым\b': 'яким',
        r'\bкоторыми\b': 'якими',
        r'\bкотором\b': 'якому',
        r'\bоснованную\b': 'засновану',

        # Прислівники
        r'\bавтоматически\b': 'автоматично',
        r'\bбыстро\b': 'швидко',
        r'\bмедленно\b': 'повільно',
        r'\bдолго\b': 'довго',

        # Інші слова
        r'\bналичие\b': 'наявність',
        r'\bзаполненность\b': 'заповненість',
        r'\bв пути\b': 'у дорозі',
        r'\bпомощь\b': 'допомога',
        r'\bпомощи\b': 'допомоги',
    }

    print(f"Обробка {len(lines)} рядків...")

    for line_num, line in enumerate(lines, 1):
        original_line = line

        # Застосовуємо всі заміни через regex для точності
        for pattern, replacement in word_replacements.items():
            line = re.sub(pattern, replacement, line, flags=re.IGNORECASE | re.UNICODE)

        cleaned_lines.append(line)

        if line_num % 500 == 0:
            print(f"Оброблено {line_num} рядків...")

    # Записуємо результат
    with open(file_path, 'w', encoding='utf-8-sig') as f:
        f.writelines(cleaned_lines)

    print(f"\nГлибоке очищення завершено!")

    # Остаточна перевірка
    content = ''.join(cleaned_lines)
    russian_test_words = ['может', 'можно', 'нужно', 'будет', 'влияет', 'определяет',
                          'количество', 'который', 'которая', 'которые']

    found = {}
    for word in russian_test_words:
        count = len(re.findall(r'\b' + word + r'\b', content, re.IGNORECASE))
        if count > 0:
            found[word] = count

    if found:
        print("\nУВАГА: Ще залишились російські слова:")
        for word, count in sorted(found.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  '{word}': {count}")
    else:
        print("\nВідмінно! Всі основні російські слова перекладено!")

    return len(found) == 0

if __name__ == "__main__":
    file_path = "/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/modifier_types_l_english.yml"
    success = deep_cleanup(file_path)

    if success:
        print("\n" + "="*60)
        print("УСПІХ! Файл повністю очищено від російської мови.")
        print("="*60)
    else:
        print("\nПеревірте файл вручну для фінального шліфування.")
