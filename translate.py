#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def translate_russian_to_ukrainian(text):
    """
    Translate Russian text to Ukrainian following the rules:
    - "ы" -> "и"
    - "э" -> "е"
    - "ё" -> "йо"
    """

    result = []
    i = 0
    while i < len(text):
        char = text[i]

        # Handle "ё" -> "йо"
        if char == 'ё':
            result.append('йо')
            i += 1
        elif char == 'Ё':
            result.append('Йо')
            i += 1
        # Handle "ы" -> "и"
        elif char == 'ы':
            result.append('и')
            i += 1
        elif char == 'Ы':
            result.append('И')
            i += 1
        # Handle "э" -> "е"
        elif char == 'э':
            result.append('е')
            i += 1
        elif char == 'Э':
            result.append('Е')
            i += 1
        else:
            result.append(char)
            i += 1

    return ''.join(result)

def translate_with_preservation(text):
    """
    Translate text while preserving [Concept(...)] tags and $variable$ patterns
    """

    # Find all [Concept(...)] tags and $...$ variables with their positions
    concept_pattern = r'\[Concept\([^)]*\)\]'
    variable_pattern = r'\$[^$]*\$'

    # Temporarily replace protected patterns with placeholders
    placeholders = {}
    placeholder_counter = 0

    # Store Concept tags
    protected_text = text
    for match in re.finditer(concept_pattern, text):
        placeholder = f"__CONCEPT_{placeholder_counter}__"
        placeholders[placeholder] = match.group(0)
        protected_text = protected_text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1

    # Store variables
    for match in re.finditer(variable_pattern, protected_text):
        placeholder = f"__VAR_{placeholder_counter}__"
        placeholders[placeholder] = match.group(0)
        protected_text = protected_text.replace(match.group(0), placeholder, 1)
        placeholder_counter += 1

    # Now translate the protected text
    translated = translate_russian_to_ukrainian(protected_text)

    # Restore protected content
    for placeholder, original in placeholders.items():
        translated = translated.replace(placeholder, original)

    return translated

def process_file(input_path, output_path):
    """Process the modifier_types file with translation rules"""

    translated_lines = []

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines read: {len(lines)}")

    for i, line in enumerate(lines):
        # Remove trailing newline for processing, we'll add it back
        original_line = line.rstrip('\n\r')

        if original_line.strip() == '':
            # Skip completely empty lines
            continue

        # Rule from user: Skip lines that start with whitespace AND don't contain proper content
        # We want to process all lines that have key: "value" format
        if original_line.startswith(' ') and 'l_english:' not in original_line:
            # Check if line is just whitespace or has significant content
            stripped = original_line.lstrip()
            # Only skip if it looks like a comment or empty line
            if not stripped or stripped.startswith('#'):
                continue

        # Process any line that contains quoted strings (which need translation)
        # This includes both NAME and DESC lines
        match = re.search(r'"([^"]*)"', original_line)
        if match:
            original_text = match.group(1)
            # Translate the content
            translated_text = translate_with_preservation(original_text)
            # Replace in the line
            new_line = original_line.replace(f'"{original_text}"', f'"{translated_text}"', 1)
            translated_lines.append(new_line)
        else:
            # Keep other lines as is
            translated_lines.append(original_line)

    print(f"Lines to write: {len(translated_lines)}")

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in translated_lines:
            f.write(line + '\n')

    print(f"Translation completed: {output_path}")

if __name__ == '__main__':
    input_file = '/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/modifier_types_chunks/chunk_aj'
    output_file = '/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/modifier_types_chunks/chunk_aj_fixed.txt'

    process_file(input_file, output_file)
