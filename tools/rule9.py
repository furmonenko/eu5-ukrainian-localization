# -*- coding: utf-8 -*-
"""Apply the Ukrainian 'rule of nine' to transliterated names.

After д т з с ц ж ч ш р, before a consonant (and not before another vowel or
the word end), foreign i is written и: Партіскум -> Партискум, Лондініум ->
Лондиніум. Before a vowel and at the end of a word і stays і (Регія, Торі).
"""
import json, io, re, sys, collections
NINE = 'дтзсцжчшр'
VOW = 'аеєиіїоуюя'
PAT = re.compile(r'([%s])і(?=[^%s\W])' % (NINE, VOW), re.UNICODE)


def rule9(s):
    return PAT.sub(lambda m: m.group(1) + 'и', s)


if __name__ == '__main__':
    dry = '--apply' not in sys.argv
    p = sys.argv[1]
    d = json.load(io.open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    n = 0
    show = []
    for k, v in d.items():
        u = v.get('uk') or ''
        new = rule9(u)
        if new != u:
            if len(show) < 15:
                show.append((v.get('en'), u, new))
            v['uk'] = new
            n += 1
    if not dry:
        io.open(p, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(d, ensure_ascii=False, indent=1) + '\n')
    print(('DRY: ' if dry else 'APPLIED: ') + 'rows changed', n)
    for en, a, b in show:
        print('   %-24s %-22s -> %s' % (en, a, b))
