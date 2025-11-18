#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для розділення interfaces_l_english.yml на частини
"""
import os
import math

def count_tokens_approx(text):
    """Приблизний підрахунок токенів (1 токен ≈ 4 символи для кирилиці)"""
    return len(text) // 3

def split_file(input_file, max_tokens=30000, output_dir='interfaces_chunks'):
    """Розділяє файл на частини"""

    # Створюємо папку для частин
    os.makedirs(output_dir, exist_ok=True)

    print(f"📖 Читаю файл: {input_file}")
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    print(f"📊 Знайдено {len(lines)} рядків")

    # Розділяємо на частини
    chunks = []
    current_chunk = []
    current_tokens = 0
    chunk_num = 1

    # Додаємо заголовок до першої частини
    header = lines[0]

    for i, line in enumerate(lines[1:], 1):  # Пропускаємо заголовок
        line_tokens = count_tokens_approx(line)

        if current_tokens + line_tokens > max_tokens and current_chunk:
            # Зберігаємо поточну частину
            chunk_file = os.path.join(output_dir, f'chunk_{chunk_num:03d}.txt')

            # Перша частина має заголовок
            if chunk_num == 1:
                chunk_content = header + ''.join(current_chunk)
            else:
                chunk_content = ''.join(current_chunk)

            with open(chunk_file, 'w', encoding='utf-8-sig') as f:
                f.write(chunk_content)

            chunks.append({
                'num': chunk_num,
                'file': chunk_file,
                'lines': len(current_chunk),
                'tokens': current_tokens
            })

            print(f"✅ Частина {chunk_num}: {len(current_chunk)} рядків, ~{current_tokens} токенів")

            # Починаємо нову частину
            chunk_num += 1
            current_chunk = []
            current_tokens = 0

        current_chunk.append(line)
        current_tokens += line_tokens

    # Зберігаємо останню частину
    if current_chunk:
        chunk_file = os.path.join(output_dir, f'chunk_{chunk_num:03d}.txt')

        if chunk_num == 1:
            chunk_content = header + ''.join(current_chunk)
        else:
            chunk_content = ''.join(current_chunk)

        with open(chunk_file, 'w', encoding='utf-8-sig') as f:
            f.write(chunk_content)

        chunks.append({
            'num': chunk_num,
            'file': chunk_file,
            'lines': len(current_chunk),
            'tokens': current_tokens
        })

        print(f"✅ Частина {chunk_num}: {len(current_chunk)} рядків, ~{current_tokens} токenів")

    print(f"\n🎉 Розділено на {len(chunks)} частин!")
    print(f"📁 Частини збережені в: {output_dir}/")

    return chunks

def main():
    input_file = '/home/user/eu5-ukrainian-localization/main_menu/localization/english/interfaces_l_english.yml'
    output_dir = '/home/user/eu5-ukrainian-localization/interfaces_chunks'

    chunks = split_file(input_file, max_tokens=15000, output_dir=output_dir)

    print("\n" + "=" * 80)
    print("✅ ГОТОВО!")
    print("=" * 80)
    print(f"\nРозділено на {len(chunks)} частин.")
    print(f"Частини знаходяться в папці: {output_dir}/")

if __name__ == '__main__':
    main()
