#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Універсальний скрипт для розділення YAML файлів на частини для перекладу

Використання:
    python3 split_for_translation.py <input_file> [--tokens 15000] [--output-dir chunks]

Приклади:
    python3 split_for_translation.py main_menu/localization/english/events_l_english.yml
    python3 split_for_translation.py file.yml --tokens 20000 --output-dir my_chunks
"""
import os
import sys
import argparse
import json
from pathlib import Path

def count_tokens_approx(text):
    """Приблизний підрахунок токенів (1 токен ≈ 3 символи для кирилиці)"""
    return len(text) // 3

def split_file(input_file, max_tokens=15000, output_dir=None):
    """Розділяє файл на частини"""

    # Якщо output_dir не вказано, створюємо на основі назви файлу
    if output_dir is None:
        base_name = Path(input_file).stem.replace('_l_english', '')
        output_dir = f"{base_name}_chunks"

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

        print(f"✅ Частина {chunk_num}: {len(current_chunk)} рядків, ~{current_tokens} токенів")

    print(f"\n🎉 Розділено на {len(chunks)} частин!")
    print(f"📁 Частини збережені в: {output_dir}/")

    # Зберігаємо метадані
    metadata = {
        'input_file': input_file,
        'output_dir': output_dir,
        'total_chunks': len(chunks),
        'max_tokens': max_tokens,
        'chunks': chunks
    }

    metadata_file = os.path.join(output_dir, 'metadata.json')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"💾 Метадані збережені: {metadata_file}")

    # Створюємо інструкцію
    instruction_file = os.path.join(output_dir, 'ІНСТРУКЦІЯ.txt')
    with open(instruction_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ІНСТРУКЦІЯ З ПЕРЕКЛАДУ\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Файл: {input_file}\n")
        f.write(f"Розділено на {len(chunks)} частин.\n\n")
        f.write("Кроки для перекладу:\n")
        f.write("1. Відкрий кожен файл chunk_XXX.txt\n")
        f.write("2. Переклади його (вручну або через Claude)\n")
        f.write("3. Збережи переклад як chunk_XXX_fixed.txt (або chunk_XXX_translated.txt)\n")
        f.write("4. Після перекладу всіх частин запусти:\n")
        f.write(f"   python3 tools/merge_translation.py {output_dir}\n\n")
        f.write("Список частин:\n")
        for chunk in chunks:
            f.write(f"  - {chunk['file']} ({chunk['lines']} рядків, ~{chunk['tokens']} токенів)\n")

    print(f"📋 Інструкція збережена: {instruction_file}")

    return chunks

def main():
    parser = argparse.ArgumentParser(
        description='Розділити YAML файл на частини для перекладу',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Приклади:
  %(prog)s events_l_english.yml
  %(prog)s file.yml --tokens 20000
  %(prog)s file.yml --output-dir my_chunks
        '''
    )

    parser.add_argument('input_file', help='Вхідний YAML файл')
    parser.add_argument('--tokens', type=int, default=15000,
                       help='Максимальна кількість токенів на частину (за замовчуванням: 15000)')
    parser.add_argument('--output-dir', help='Папка для збереження частин (за замовчуванням: <filename>_chunks)')

    args = parser.parse_args()

    # Перевірка існування файлу
    if not os.path.exists(args.input_file):
        print(f"❌ Помилка: Файл не знайдено: {args.input_file}")
        sys.exit(1)

    chunks = split_file(args.input_file, max_tokens=args.tokens, output_dir=args.output_dir)

    print("\n" + "=" * 80)
    print("✅ ГОТОВО!")
    print("=" * 80)
    print(f"\nРозділено на {len(chunks)} частин.")
    output_dir = args.output_dir or f"{Path(args.input_file).stem.replace('_l_english', '')}_chunks"
    print(f"Частини знаходяться в папці: {output_dir}/")
    print(f"\nНаступний крок: переклади всі chunk_XXX.txt та збережи як chunk_XXX_fixed.txt")
    print(f"Потім запусти: python3 tools/merge_translation.py {output_dir}")

if __name__ == '__main__':
    main()
