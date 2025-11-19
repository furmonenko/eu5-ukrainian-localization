#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# Таблиця заміни російських літер на українські
LETTER_REPLACEMENTS = {
    'ы': 'и',
    'Ы': 'И',
    'э': 'е',
    'Э': 'Е',
    'ё': 'йо',
    'Ё': 'Йо',
}

# Словник перекладу російських слів на українські
WORD_TRANSLATIONS = {
    'принадлежащих': 'належних',
    'судостроительных': 'суднобудівних',
    'дополнительных': 'додаткових',
    'огнестрельного': 'вогнепальної',
    'ювелирных': 'ювелірних',
    'лесоматериалов': 'лісоматеріалів',
    'слоновой': 'слонової',
    'прядильных': 'волокнистих',
    'тропической': 'тропічної',
    'общественной': 'громадської',
    'кириситанской': 'кіріситанської',
    'религиозного': 'релігійного',
    'поддержания': 'збереження',
    'распространения': 'поширення',
    'расширения': 'розширення',
    'предоставления': 'надання',
    'уничтожения': 'знищення',
    'требования': 'вимоги',
    'материалов': 'матеріалів',
    'инструментов': 'інструментів',
    'Запретить': 'Заборонити',
    'запретить': 'заборонити',
    'Блокирует': 'Блокує',
    'блокирует': 'блокує',
    'Влияет': 'Впливає',
    'влияет': 'впливає',
    'Стоимость': 'Вартість',
    'стоимость': 'вартість',
    'получения': 'отримання',
    'должности': 'посади',
    'сёгуна': 'сьогуна',
    'Имперского': 'Імперського',
    'имперского': 'імперського',
    'от': 'від',
    'суда': 'суду',
    'умиротворения': 'умиротворення',
    'аристократов': 'аристократів',
    'ополчения': 'ополчення',
    'повышения': 'підвищення',
    'налогов': 'податків',
    'выплат': 'виплат',
    'действия': 'дії',
    'крестьян': 'селян',
    'снижения': 'зниження',
    'риска': 'ризику',
    'мятежа': 'повстання',
    'убежища': 'притулку',
    'оплотов': 'оплотів',
    'икко': 'іккі',
    'грамотности': 'грамотності',
    'священников': 'священиків',
    'поддержки': 'підтримки',
    'буддизма': 'буддизму',
    'культа': 'культу',
    'ками': 'камі',
    'баланса': 'балансу',
    'между': 'між',
    'крещения': 'хрещення',
    'правителя': 'правителя',
    'проведения': 'проведення',
    'мессы': 'месси',
    'заключения': 'укладання',
    'договора': 'договору',
    'договор': 'договір',
    'кириситан': 'кіріситан',
    'ограничения': 'обмеження',
    'движения': 'руху',
    'экспорт': 'експорт',
    'импорт': 'імпорт',
    'хлопка': 'бавовни',
    'сахара': 'цукру',
    'табака': 'тютюну',
    'лошадей': 'коней',
    'глины': 'глини',
    'песка': 'піску',
    'угля': 'вугілля',
    'железа': 'заліза',
    'меди': 'міді',
    'золота': 'золота',
    'серебра': 'срібла',
    'камня': 'каменю',
    'олова': 'олова',
    'свинца': 'свинцю',
    'шерсти': 'вовни',
    'шёлка': 'шовку',
    'красителей': 'барвників',
    'благовоний': 'пахощів',
    'чая': 'чаю',
    'какао': 'какао',
    'кофе': 'кави',
    'культур': 'культур',
    'кости': 'кістки',
    'меха': 'хутра',
    'соли': 'солі',
    'древесины': 'деревини',
    'лекарств': 'ліків',
    'жемчуга': 'перлів',
    'янтаря': 'бурштину',
    'селитры': 'селітри',
    'квасцов': 'галунів',
    'вина': 'вина',
    'слонов': 'слонів',
    'рабов': 'рабів',
    'дичи': 'дичини',
    'рыбы': 'риби',
    'пшеницы': 'пшениці',
    'кукурузы': 'кукурудзи',
    'риса': 'рису',
    'проса': 'просо',
    'бобовых': 'бобових',
    'картофеля': 'картоплі',
    'скота': 'худоби',
    'оливок': 'оливок',
    'фруктов': 'фруктів',
    'дёгтя': 'дьогтю',
    'фарфора': 'фарфору',
    'оружия': 'зброї',
    'пушек': 'гармат',
    'стекла': 'скла',
    'стали': 'сталі',
    'текстиля': 'текстилю',
    'сукна': 'сукна',
    'алкоголя': 'алкоголю',
    'пива': 'пива',
    'бумаги': 'паперу',
    'книг': 'книг',
    'изделий': 'виробів',
    'кожи': 'шкіри',
    'рынков': 'ринків',
    'рынки': 'ринки',
    'рынка': 'ринку',
    'рынке': 'ринку',
    'со': 'зі',
    'всех': 'усіх',
    'аристократов': 'аристократів',
    'ополчения': 'ополчення',
    'налогов': 'податків',
    'крестьян': 'селян',
    'мятежа': 'повстання',
    'убежища': 'притулку',
    'грамотности': 'грамотності',
    'священников': 'священиків',
    'буддизма': 'буддизму',
    'культа': 'культу',
    'баланса': 'балансу',
    'мессы': 'месси',
}

def apply_letter_replacements(text):
    """Застосувати заміну літер"""
    for russian, ukrainian in LETTER_REPLACEMENTS.items():
        text = text.replace(russian, ukrainian)
    return text

def translate_russian_text(text):
    """Перекласти російський текст на українську мову"""
    # Спочатку замінити літери
    text = apply_letter_replacements(text)

    # Замінити слова (від довших до коротших для точності)
    for russian, ukrainian in sorted(WORD_TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        # Замінити з дотриманням слівних границь
        pattern = r'\b' + re.escape(russian) + r'\b'
        text = re.sub(pattern, ukrainian, text)

    return text

def translate_line(line):
    """Перекласти один рядок"""
    original_line = line
    line = line.rstrip('\n')

    # Перевірити, чи це пустий рядок (але не рядок, що починається з пробілу)
    if not line.strip():
        return original_line

    # Якщо рядок містить l_english, не перекладаємо
    if 'l_english' in line:
        return original_line

    # Якщо рядок починається з пробілу без l_english: - повертаємо як є
    if line and line[0] == ' ' and ':' not in line:
        return original_line

    # Розділити ключ і значення за першим ':'
    if ':' not in line:
        return original_line

    parts = line.split(':', 1)
    key = parts[0]
    value_part = parts[1]

    # Видалити лапки та отримати текст
    value_str = value_part.strip()
    if not value_str.startswith('"') or not value_str.endswith('"'):
        return original_line

    text = value_str[1:-1]  # Видалити лапки

    # Знайти та замінити [Concept(...)] на плейсхолдери
    concepts = {}
    concept_pattern = r'\[Concept\([^)]+\)\]'
    for i, match in enumerate(re.finditer(concept_pattern, text)):
        placeholder = f"__CONCEPT_{i}__"
        concept_text = match.group()
        # Перекласти текст всередину Concept
        concept_text = concept_text.replace("'costs'", "'витрати'")
        concept_text = concept_text.replace("'export'", "'експорт'")
        concept_text = concept_text.replace("'import'", "'імпорт'")
        concept_text = concept_text.replace("'country'", "'країна'")
        concept_text = concept_text.replace("'markets'", "'ринки'")
        concepts[placeholder] = concept_text

    for placeholder, concept in concepts.items():
        text = text.replace(concept, placeholder, 1)

    # Знайти та замінити $змінні$ на плейсхолдери
    variables = {}
    var_pattern = r'\$[^$]+\$'
    for i, match in enumerate(re.finditer(var_pattern, text)):
        placeholder = f"__VAR_{i}__"
        variables[placeholder] = match.group()

    for placeholder, var in variables.items():
        text = text.replace(var, placeholder, 1)

    # Знайти та замінити #...# на плейсхолдери (для TOOLTIP та інших тегів)
    tooltips = {}
    tooltip_pattern = r'#[^#]+#'
    for i, match in enumerate(re.finditer(tooltip_pattern, text)):
        placeholder = f"__TOOLTIP_{i}__"
        tooltips[placeholder] = match.group()

    for placeholder, tooltip in tooltips.items():
        text = text.replace(tooltip, placeholder, 1)

    # Перекласти текст
    text = translate_russian_text(text)

    # Повернути оригінальні теги
    for placeholder, concept in concepts.items():
        text = text.replace(placeholder, concept)

    for placeholder, var in variables.items():
        text = text.replace(placeholder, var)

    for placeholder, tooltip in tooltips.items():
        text = text.replace(placeholder, tooltip)

    # Зберегти оригінальний формат з пробілом на початку рядка, якщо він був
    if key and key[0] == ' ':
        return f"{key}: \"{text}\"\n"
    else:
        return f"{key}: \"{text}\"\n"

def main():
    input_file = '/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/modifier_types_chunks/chunk_ai'
    output_file = '/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/modifier_types_chunks/chunk_ai_fixed.txt'

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        translated_lines = []
        for line in lines:
            translated_line = translate_line(line)
            translated_lines.append(translated_line)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)

        print(f"Переклад завершено. Файл збережено в {output_file}")

    except Exception as e:
        print(f"Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
