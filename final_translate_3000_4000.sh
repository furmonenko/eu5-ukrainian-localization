#!/bin/bash
# Масовий переклад російських рядків 3000-4000

FILE="/Users/furmonenko/Desktop/eu5-ukrainian-localization/main_menu/localization/english/advances_l_english.yml"

# Функція для перекладу одного ключа
translate_key() {
    local key="$1"
    local value="$2"
    
    # Виконуємо заміну в файлі
    python3 -c "
import sys, re

# Читаємо файл
with open('$FILE', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Робимо заміну
old_pattern = ' $key: \"$value\"'
new_pattern = ' $key: \"$value\"'

content = content.replace(old_pattern, new_pattern)

# Записуємо назад
with open('$FILE', 'w', encoding='utf-8-sig') as f:
    f.write(content)
"
}

echo "Початок масового перекладу..."
echo "======================================"

