#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Валідатор перекладених YAML файлів

Перевіряє:
- YAML синтаксис
- Правильність Concept() конструкцій
- Технічні теги ($VALUE$, #T, #!, тощо)
- BOM маркер
- Відсутність російських літер ё, ъ

Використання:
    python3 validate_translation.py <file.yml>
"""
import os
import sys
import re
import argparse

def validate_yaml_syntax(file_path):
    """Перевіряє базовий YAML синтаксис"""
    errors = []

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    # Перевірка заголовка
    if not lines or not lines[0].strip().startswith('l_english:'):
        errors.append("❌ Відсутній або неправильний заголовок 'l_english:'")

    # Перевірка структури рядків
    for i, line in enumerate(lines[1:], 2):
        line = line.rstrip('\n')
        if not line.strip() or line.strip().startswith('#'):
            continue

        # Базова перевірка формату key: "value"
        if ':' in line and not line.strip().startswith('#'):
            if not re.search(r'^\s*[a-zA-Z0-9_]+:\s*"', line):
                errors.append(f"❌ Рядок {i}: можлива помилка формату (очікується key: \"value\")")

    return errors

def validate_concepts(file_path):
    """Перевіряє правильність Concept() конструкцій"""
    errors = []
    warnings = []

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        lines = content.split('\n')

    # Перевірка правильності Concept()
    concept_pattern = r'\[Concept\([\'"]([^"\']+)[\'"],\s*[\'"]([^"\']+)[\'"]\)\|e\]'

    for i, line in enumerate(lines, 1):
        # Знаходимо всі Concept()
        concepts = re.finditer(concept_pattern, line)
        for match in concepts:
            key = match.group(1)
            value = match.group(2)

            # Перевірка наявності українського тексту
            if not re.search(r'[а-яіїєґ]', value, re.IGNORECASE):
                warnings.append(f"⚠️  Рядок {i}: Concept('{key}','{value}') не містить українських літер")

    # Перевірка старих тегів без Concept()
    old_tags = re.finditer(r'\[([a-z_]+)\|e\]', content)
    for match in old_tags:
        if match.group(0) not in ['[e]', '|e]']:  # Ігноруємо кінцівки
            tag = match.group(1)
            # Знаходимо рядок
            pos = match.start()
            line_num = content[:pos].count('\n') + 1
            warnings.append(f"⚠️  Рядок {line_num}: [{tag}|e] без Concept() - краще додати переклад")

    return errors, warnings

def validate_technical_tags(file_path):
    """Перевіряє збереження технічних тегів"""
    errors = []

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # Перевірка незакритих тегів
        if line.count('#T') != line.count('#!'):
            errors.append(f"❌ Рядок {i}: незбалансовані теги #T та #!")

        # Перевірка правильності змінних
        if '$' in line:
            # Базова перевірка формату змінних
            if re.search(r'\$[^$\s]+\$', line):
                pass  # Правильний формат
            elif '$' in line and not re.search(r'\$\$', line):
                errors.append(f"❌ Рядок {i}: можлива помилка в змінній $ (перевірте формат)")

    return errors

def validate_russian_letters(file_path):
    """Перевіряє відсутність російських літер"""
    errors = []

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # Шукаємо російські літери ё та ъ
        if 'ё' in line.lower():
            errors.append(f"❌ Рядок {i}: знайдено російську літеру 'ё'")
        if 'ъ' in line.lower():
            errors.append(f"❌ Рядок {i}: знайдено російську літеру 'ъ'")

    return errors

def validate_bom(file_path):
    """Перевіряє наявність BOM маркера"""
    with open(file_path, 'rb') as f:
        start = f.read(3)

    if start != b'\xef\xbb\xbf':
        return ["⚠️  Відсутній BOM маркер (UTF-8 with BOM). Це може спричинити проблеми в грі."]
    return []

def main():
    parser = argparse.ArgumentParser(
        description='Валідувати перекладений YAML файл'
    )
    parser.add_argument('file', help='YAML файл для перевірки')
    parser.add_argument('--strict', action='store_true', help='Строгий режим (warnings = errors)')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ Файл не знайдено: {args.file}")
        sys.exit(1)

    print("=" * 80)
    print(f"ВАЛІДАЦІЯ: {args.file}")
    print("=" * 80)

    all_errors = []
    all_warnings = []

    # 1. YAML синтаксис
    print("\n📋 Перевірка YAML синтаксису...")
    errors = validate_yaml_syntax(args.file)
    all_errors.extend(errors)
    if errors:
        for err in errors:
            print(err)
    else:
        print("✅ YAML синтаксис правильний")

    # 2. Concept() конструкції
    print("\n🔍 Перевірка Concept() конструкцій...")
    errors, warnings = validate_concepts(args.file)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for err in errors:
            print(err)
    if warnings:
        for warn in warnings:
            print(warn)
    if not errors and not warnings:
        print("✅ Всі Concept() правильні")

    # 3. Технічні теги
    print("\n⚙️  Перевірка технічних тегів...")
    errors = validate_technical_tags(args.file)
    all_errors.extend(errors)
    if errors:
        for err in errors:
            print(err)
    else:
        print("✅ Технічні теги збережені")

    # 4. Російські літери
    print("\n🔤 Перевірка російських літер...")
    errors = validate_russian_letters(args.file)
    all_errors.extend(errors)
    if errors:
        for err in errors:
            print(err)
    else:
        print("✅ Російські літери відсутні")

    # 5. BOM маркер
    print("\n📄 Перевірка BOM маркера...")
    warnings = validate_bom(args.file)
    all_warnings.extend(warnings)
    if warnings:
        for warn in warnings:
            print(warn)
    else:
        print("✅ BOM маркер присутній")

    # Підсумок
    print("\n" + "=" * 80)
    print("ПІДСУМОК")
    print("=" * 80)

    total_issues = len(all_errors) + (len(all_warnings) if args.strict else 0)

    if total_issues == 0:
        print("✅ Валідація пройшла успішно!")
        print("   Файл готовий до використання.")
        return 0
    else:
        print(f"❌ Знайдено проблем: {len(all_errors)} помилок, {len(all_warnings)} попереджень")
        if all_errors:
            print("\nПомилки (потрібно виправити):")
            for err in all_errors[:10]:  # Показуємо перші 10
                print(f"  {err}")
            if len(all_errors) > 10:
                print(f"  ... та ще {len(all_errors) - 10} помилок")

        if all_warnings:
            print("\nПопередження (рекомендується виправити):")
            for warn in all_warnings[:10]:  # Показуємо перші 10
                print(f"  {warn}")
            if len(all_warnings) > 10:
                print(f"  ... та ще {len(all_warnings) - 10} попереджень")

        return 1 if all_errors or args.strict else 0

if __name__ == '__main__':
    sys.exit(main())
