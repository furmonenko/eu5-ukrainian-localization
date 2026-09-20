# -*- coding: utf-8 -*-
"""Transliterate Italian (and its dialect spellings) into Ukrainian Cyrillic.

Ukrainian orthography, not the Russian tradition the old rows used:
  -ia -> ія (Палатія, not Палатия);  final -i -> -і (Джованні, not Джованни)
  g -> г before a/o/u/consonant (Фамагоста), not ґ: §122 keeps г for foreign g
  rule of nine is applied afterwards by tools/rule9.py

The game's north_italian / south_italian names carry dialect diacritics
(Bàssàno, Sanzëvírë, Caḍḍìpuli, Legnåg) that Ukrainian does not mark, so the
first step strips accents down to the base letter. Then the Italian reading:

  c  -> ч before e i, к otherwise;  ch -> к;  ci+vowel -> ч
  g  -> дж before e i, г otherwise;  gh -> г;  gi+vowel -> дж
  gn -> нь;  gl before i -> льї;  sc before e i -> ш
  z / zz -> ц / цц;  qu -> кв;  h is silent;  s between vowels -> з
"""
import re
import unicodedata

BASE = {'\u1e0d': 'd', '\u1e0c': 'D',   # ḍ  sicilian retroflex
        '\u0161': 'sc', '\u0160': 'Sc'}  # š  abruzzese  (lù Uàštë)


def _strip(s):
    out = []
    for ch in s:
        if ch in BASE:
            out.append(BASE[ch])
            continue
        d = unicodedata.normalize('NFD', ch)
        d = ''.join(c for c in d if unicodedata.category(c) != 'Mn')
        out.append(d or ch)
    return ''.join(out)


VOWELS = 'aeiou'
SIMPLE = {'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф', 'i': 'і', 
          'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п', 'r': 'р',
          't': 'т', 'u': 'у', 'v': 'в', 'w': 'в', 'x': 'кс', 'y': 'і'}

SOFT = {'а': 'я', 'о': 'ьо', 'у': 'ю', 'е': 'є'}
# after і the vowel is written plain: Алессіо, Адраміттіо, Фіуме
AFTER_I = {'а': 'я', 'о': 'о', 'у': 'у', 'е': 'е'}  # Палатія, Алессіо


def _word(w):
    low = w.lower()
    n = len(low)
    out = []
    i = 0
    while i < n:
        c = low[i]
        n1 = low[i + 1] if i + 1 < n else ''
        n2 = low[i + 2] if i + 2 < n else ''
        prev = low[i - 1] if i else ''
        piece, step = None, 1
        if (c == 'g' and n1 == 'g' and n2 == 'i'
                and (low[i + 3] if i + 3 < n else '') in 'aou'):
            piece, step = 'дж', 3
        elif c == 'g' and n1 == 'g' and n2 and n2 in 'ei':
            piece, step = 'дж', 2
        elif (c == 'c' and n1 == 'c' and n2 == 'i'
              and (low[i + 3] if i + 3 < n else '') in 'aou'):
            piece, step = 'чч', 3
        elif c == 'c' and n1 == 'c' and n2 and n2 in 'ei':
            piece, step = 'чч', 2
        elif c == 'g' and n1 == 'n':
            # gn + vowel palatalises it: Rovigno -> Ровіньо, Segna -> Сенья
            if n2 in VOWELS:
                v = SOFT.get(SIMPLE.get(n2, ''), '')
                piece, step = 'н' + (v if v.startswith('ь') else 'ь' + v), 3
            else:
                piece, step = 'нь', 2
        elif c == 'g' and n1 == 'l' and n2 == 'i':
            # gli + vowel -> ль + iotated;  gli final -> льї
            n3 = low[i + 3] if i + 3 < n else ''
            if n3 in VOWELS:
                v = SOFT.get(SIMPLE.get(n3, ''), '')
                piece, step = 'л' + (v if v.startswith('ь') else 'ь' + v), 4
            else:
                piece, step = 'лі', 3
        elif c == 'g' and n1 == 'h':
            piece, step = 'г', 2
        elif c == 'g' and n1 == 'i' and n2 in 'aou':
            piece, step = 'дж', 2
        elif c == 'g' and n1 == 'i' and n2 in VOWELS:
            piece, step = 'дж', 2
        elif c == 'g' and n1 and n1 in 'ei':
            piece = 'дж'
        elif c == 'g':
            piece = 'г'
        elif (c == 'c' and n1 == 'h' and n2 == 'i'
              and (low[i + 3] if i + 3 < n else '') in VOWELS):
            nv = low[i + 3]
            piece, step = 'кі' + AFTER_I.get(SIMPLE.get(nv, ''), ''), 4
        elif c == 'c' and n1 == 'h':
            piece, step = 'к', 2
        elif c == 'c' and n1 == 'i' and n2 in 'aou':
            piece, step = 'ч', 2
        elif c == 'c' and n1 == 'i' and n2 in VOWELS:
            piece, step = 'ч', 2
        elif c == 'c' and n1 and n1 in 'ei':
            piece = 'ч'
        elif c == 'c':
            piece = 'к'
        elif (c == 's' and n1 == 'c' and n2 == 'i'
              and (low[i + 3] if i + 3 < n else '') in 'aou'):
            piece, step = 'ш', 3
        elif c == 's' and n1 == 'c' and n2 and n2 in 'ei':
            piece, step = 'ш', 2
        elif c == 's':
            piece = 'з' if (prev and prev in VOWELS
                            and n1 and n1 in VOWELS) else 'с'
        elif c == 'z':
            piece = 'з' if i == 0 else 'ц'
        elif c == 'q' and n1 == 'u':
            piece, step = 'кв', 2
        elif c == 'l' and (not n1 or n1 not in VOWELS) and n1 != 'l':
            piece = 'ль'
        elif c == 'j':
            nv = SIMPLE.get(n1, '')
            if n1 in VOWELS and nv:
                piece, step = SOFT.get(nv, 'й' + nv), 2
            else:
                piece = 'й'
        elif c == 'h':
            piece, step = '', 1
        elif c == 'i' and prev and prev in VOWELS and (not n1 or n1 not in VOWELS):
            piece = 'й'
        elif c == 'i' and prev and prev in VOWELS and n1 in VOWELS:
            # Laiazzo -> Лаяццо, Croia -> Кроя: i between vowels is a glide
            piece, step = SOFT.get(SIMPLE.get(n1, ''), 'й'), 2
        elif c == 'i' and prev and prev not in VOWELS and n1 in 'aou':
            # consonant + ia/io/iu -> ія/іо/іу (Palatia -> Палатія);
            # the i itself is і and the vowel after it is iotated
            soft = AFTER_I.get(SIMPLE.get(n1, ''), '')
            if out and out[-1] and out[-1][-1].lower() in 'чшжі':
                soft = SIMPLE.get(n1, '')   # Браччіано, Аріано
            piece, step = 'і' + soft, 2
        else:
            piece = SIMPLE.get(c, c)
        if piece and w[i].isupper():
            piece = piece[0].upper() + piece[1:]
        out.append(piece)
        i += step
    return ''.join(out)


def translit(s):
    s = _strip(s)
    s = s.replace("'", '\u2019')
    s = re.sub(r"[A-Za-z]+", lambda m: _word(m.group(0)), s)
    return s.replace(' ', '-')
