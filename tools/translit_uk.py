# -*- coding: utf-8 -*-
"""Reverse the official Ukrainian romanisation (KMU 2010) back to Cyrillic.

The game spells ruthenian_language names in that romanisation (Oleksiivka,
Bilhorod, Velyka Martynivka), so this is a mechanical inverse, not a
translation. It cannot recover a historic exonym: Reschov is Ряшів and
Ciaroshkavychi is Терешковичі by history, not by letters. Those need a human.

Beyond the letter table:
  * digraphs match longest-first (shch, zh, kh, ts, ch, sh);
  * i before another vowel is ї (Oleksiivka -> Олексіївка, Andriiv -> Андріїв);
  * word-initial y + vowel is iotated (Yalta -> Ялта), elsewhere y is и;
  * и never follows ж ч ш щ or a vowel, where it becomes и/й by Ukrainian rule;
  * the adjective endings -skyi/-tskyi/-zkyi are -ський/-цький/-зький;
  * a terminal -ets is -ець, and -sk/-shl/-sl/-zl/-mel take the soft sign.
"""
import re

PAIRS = [
    ('zgh', 'зг'), ('shch', 'щ'),
    ('zh', 'ж'), ('kh', 'х'), ('ts', 'ц'), ('ch', 'ч'), ('sh', 'ш'),
    ('ye', 'є'), ('yi', 'иї'), ('yu', 'ю'), ('ya', 'я'), ('yo', 'йо'),
    ('iu', 'ю'), ('ia', 'я'), ('ie', 'є'),
    ('a', 'а'), ('b', 'б'), ('v', 'в'), ('h', 'г'), ('g', 'ґ'), ('d', 'д'),
    ('e', 'е'), ('z', 'з'), ('y', 'и'), ('i', 'і'), ('k', 'к'), ('l', 'л'),
    ('m', 'м'), ('n', 'н'), ('o', 'о'), ('p', 'п'), ('r', 'р'), ('s', 'с'),
    ('t', 'т'), ('u', 'у'), ('f', 'ф'), ('j', 'й'), ('c', 'ц'), ('w', 'в'),
    ('q', 'к'), ('x', 'кс'),
]
VOWELS = 'aeiouy'
APOSTROPHE = '\u2019'

SUFFIX = [
    ('tskyi', 'цький'), ('zkyi', 'зький'), ('skyi', 'ський'),
    ('tska', 'цька'), ('zka', 'зька'), ('ska', 'ська'),
    ('tske', 'цьке'), ('zke', 'зьке'), ('ske', 'ське'),
    ('kyi', 'кий'), ('nyi', 'ний'), ('vyi', 'вий'), ('ryi', 'рий'),
    ('niy', 'ній'), ('liy', 'лій'), ('riy', 'рій'), ('lyi', 'лий'),
    ('shl', 'шль'), ('sl', 'сль'), ('zl', 'зль'),
    ('sk', 'ськ'), ('mel', 'мель'), ('pil', 'піль'),
    ('til', 'тіль'), ('nil', 'ніль'), ('sil', 'сіль'),
    ('pol', 'поль'), ('sol', 'соль'),
]


def _core(w):
    out = []
    i = 0
    low = w.lower()
    while i < len(w):
        # ii is і+ї (Oleksiivka -> Олексіївка); a lone i before a vowel
        # is ї only after another vowel (Buinovychi -> Буїновичі)
        if low[i] == 'i' and i > 0:
            prev, nxt = low[i - 1], low[i + 1] if i + 1 < len(low) else ''
            if prev == 'i' and nxt in 'aeiouv':
                out.append('ї')
                i += 1
                continue
            if prev in 'eou' and nxt and nxt not in 'aeiouy':
                out.append('й')
                i += 1
                continue
            if prev in 'aeiou' and (nxt in 'aeiouv' or nxt in 'ns') and prev != 'i':
                out.append('ї')
                i += 1
                continue
        for src, dst in PAIRS:
            if low.startswith(src, i):
                if src == 'y' and i == 0 and i + 1 < len(low) and low[i + 1] in 'aeiou':
                    break
                piece = dst
                if w[i].isupper():
                    piece = piece[0].upper() + piece[1:]
                out.append(piece)
                i += len(src)
                break
        else:
            out.append(w[i])
            i += 1
    return ''.join(out)


def _polish(s):
    """Spelling touch-ups the letter pass cannot see.

    Deliberately minimal: an earlier version forced и after ж ч ш щ, which broke
    -вичі endings (Pyskorovychi -> Пискоровичі, not Пискоровичи). The romanisation
    already distinguishes y (и) from i (і), so no such rule is needed.
    """
    return s


SOFT_L = re.compile(r'^([Ll])(?=[vbdfghjklmnpqrstvwxz])')


def _word(w):
    low = w.lower()
    if SOFT_L.match(w):
        head = 'Ль' if w[0].isupper() else 'ль'
        return head + _core(w[1:])
    for src, dst in SUFFIX:
        if low.endswith(src) and len(low) > len(src):
            return _polish(_core(w[:-len(src)]) + dst)
    if low.endswith('ets') and len(low) > 4:
        return _polish(_core(w[:-3]) + 'ець')
    return _polish(_core(w))


def translit(s):
    s = s.replace("'", APOSTROPHE)
    return re.sub(r"[A-Za-z]+", lambda m: _word(m.group(0)), s)
