# -*- coding: utf-8 -*-
"""Transliterate Latin place names into Ukrainian Cyrillic.

Follows the traditional (not classical) reading used for Latin in Ukrainian,
the same convention as Львів for Leopolis and Луцьк for Luceoria:

  c  -> ц before e i y ae oe, otherwise к   (Cannetum -> Каннетум, Cicero -> Цицеро)
  ti -> ці before a vowel unless after s t x (Palatiolum -> Палаціолум)
  ae oe -> е        (Caesar -> Цезар)
  qu -> кв, ngu+vowel -> нгв, su+vowel -> св in a few words
  h  -> г,  ph -> ф,  th -> т,  ch -> х,  rh -> р
  s between vowels -> з   (Rosa -> Роза)
  j / consonantal i -> й,  y -> і,  v -> в,  x -> кс, z -> з
  doubled consonants are kept (Cannetum -> Каннетум)
"""
import re

SOFT_C = set('eiyæœ')
VOWELS = 'aeiouy'


def _word(w):
    low = w.lower()
    out = []
    i = 0
    n = len(low)
    while i < n:
        ch = low[i]
        nxt = low[i + 1] if i + 1 < n else ''
        nxt2 = low[i + 2] if i + 2 < n else ''
        piece = None
        step = 1
        # digraphs first
        if ch == 'c' and nxt == 'a' and nxt2 == 'e':
            piece, step = 'це', 3
        elif ch == 'a' and nxt == 'e':
            piece, step = 'е', 2
        elif ch == 'o' and nxt == 'e':
            piece, step = 'е', 2
        elif ch == 'p' and nxt == 'h':
            piece, step = 'ф', 2
        elif ch == 't' and nxt == 'h':
            piece, step = 'т', 2
        elif ch == 'c' and nxt == 'h':
            piece, step = 'х', 2
        elif ch == 'r' and nxt == 'h':
            piece, step = 'р', 2
        elif ch == 'q' and nxt == 'u':
            piece, step = 'кв', 2
        elif ch == 'a' and nxt == 'u' and nxt2 and nxt2 not in VOWELS:
            piece, step = 'ав', 2
        elif ch == 'e' and nxt == 'u' and nxt2 and nxt2 not in VOWELS:
            piece, step = 'ев', 2
        elif ch == 't' and nxt == 'i' and nxt2 in VOWELS and (i == 0 or low[i - 1] not in 'stx'):
            piece, step = 'ці', 2
        elif ch == 'c':
            piece = 'ц' if nxt in SOFT_C else 'к'
        elif ch == 's':
            # voiced only strictly between vowels inside the word: Caesar -> Цезар,
            # but a word-final s stays с (Vetus -> Ветус, Sanctus -> Санктус)
            prev = low[i - 1] if i else ''
            piece = 'з' if (i and prev and prev in VOWELS and nxt and nxt in VOWELS) else 'с'
        elif ch == 'i' and i == 0 and nxt in VOWELS:
            piece, step = {'u': 'ю', 'a': 'я', 'e': 'є',
                           'o': 'йо'}.get(nxt, 'й'), (2 if nxt in 'uaeo' else 1)
        elif ch == 'i' and 0 < i and nxt and nxt in VOWELS and low[i - 1] in VOWELS:
            piece = 'й'
        elif ch == 'i' and 0 < i and nxt and nxt in 'aou' and low[i - 1] not in VOWELS:
            piece, step = {'a': 'ія', 'o': 'іо', 'u': 'іу'}[nxt], 2
        elif ch == 'j':
            piece = 'й'
        elif ch == 'y':
            piece = 'і'
        elif ch == 'x':
            piece = 'кс'
        elif ch == 'h':
            piece = 'г'
        elif ch == 'v':
            piece = 'в'
        elif ch == 'l' and (not nxt or nxt not in VOWELS):
            piece = 'ль'
        elif ch == 'u':
            piece = 'у'
        else:
            piece = {'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г',
                     'i': 'і', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о',
                     'p': 'п', 'r': 'р', 't': 'т', 'w': 'в', 'z': 'з'}.get(ch, ch)
        if w[i].isupper():
            piece = piece[0].upper() + piece[1:]
        out.append(piece)
        i += step
    return ''.join(out)


def translit(s):
    return re.sub(r"[A-Za-z]+", lambda m: _word(m.group(0)), s)
