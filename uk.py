"""Ukrainian localization for Europa Universalis V.

    python uk.py extract     pull the original English localization out of the game into work/
    python uk.py check       validate translations/ against the current English source
    python uk.py status      translation coverage per namespace
    python uk.py leftovers   English left in the mod (missing/empty/uk == en/Latin words) -> work/leftovers.tsv
    python uk.py concepts    [Concept('key','text')] whose text strays from the game_concepts name -> work/concepts.tsv
    python uk.py grep RX [--en RX] [--keys F]   rows whose uk (and en) match, as a keys file for translate.py fix
    python uk.py build       build the mod into dist/
    python uk.py package     build + zip the mod for distribution
    python uk.py install     build + copy the mod into the game's Documents mod folder
    python uk.py uninstall   remove the mod from the game's Documents mod folder

Game directory: --game <path>, or the EU5_DIR environment variable.
"""
import argparse
import collections
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK, DIST, TRANSLATIONS, OVERLAY = ROOT / 'work', ROOT / 'dist', ROOT / 'translations', ROOT / 'overlay'
DEFAULT_GAME = r'C:\Program Files\Steam\steamapps\common\Europa Universalis V'

MOD_NAME = 'Ukraina Universalis'
MOD_VERSION = '1.2.0'  # bump together with description.bbcode and the git tag
ROOTS = ['main_menu', 'loading_screen']
TARGETS = ROOTS  # translate.py imports this name

# root -> list of (english dir relative to --game, root prefix used for relpaths)
_SOURCE_DIRS = {
    'main_menu': [
        'game/main_menu/localization/english',
        'game/dlc/D000_shared/main_menu/localization/dlc/english',
    ],
    'loading_screen': [
        'game/loading_screen/localization/english',
    ],
}

# Two folders under Documents/Paradox Interactive/Europa Universalis V/mod:
#   MOD_DIR_NAME  - the pdx-workshop-manager working copy; publishing to the Workshop uploads THIS folder.
#                   Only `install --release` writes here, right before publishing a new version.
#   DEV_DIR_NAME  - the everyday build. Separate id, so the launcher lists it as its own mod.
MOD_DIR_NAME = f'{MOD_NAME} 1.0'
DEV_DIR_NAME = f'{MOD_NAME} DEV'
DEV_MOD_ID = 'ukraina.universalis.dev'


def ns_file(root, relpath):
    return TRANSLATIONS / root / f'{relpath}.json'


def ns_from_file(path, root):
    return path.relative_to(TRANSLATIONS / root).with_suffix('').as_posix()


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')


def translation_files():
    return sorted(p for p in TRANSLATIONS.glob('*/**/*.json'))


# ---------------------------------------------------------------- yml parsing

_LINE_RE = re.compile(r'^\s*(?P<key>[A-Za-z0-9_.\-]+):\d*\s*"(?P<text>.*)"\s*(?:#[^"]*)?$')


def parse_yml(text):
    """{key: text} from one l_english.yml file's content (BOM already stripped)."""
    out = {}
    for line in text.split('\n'):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = _LINE_RE.match(line)
        if not m:
            continue
        out[m.group('key')] = m.group('text').replace('\\"', '"')
    return out


def read_yml_file(path):
    data = path.read_bytes()
    text = data.decode('utf-8-sig')
    return parse_yml(text)


def write_yml_file(path, keys):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8-sig', newline='\n') as f:
        f.write('l_english:\n')
        for key, text in keys.items():
            f.write(f' {key}: "{text.replace(chr(34), chr(92) + chr(34))}"\n')


def source_strings(root, game_dir=None, baseline=None):
    """{relpath: {key: text}}"""
    out = collections.defaultdict(dict)
    root_dir = baseline if baseline is not None else (game_dir or os.environ.get('EU5_DIR', DEFAULT_GAME))
    for src_dir in _SOURCE_DIRS[root]:
        base = Path(root_dir) / src_dir
        if not base.exists():
            continue
        for path in sorted(base.rglob('*_l_english.yml')):
            relpath = path.relative_to(base).as_posix()[:-len('_l_english.yml')]
            out[relpath].update(read_yml_file(path))
    return out


# ---------------------------------------------------------------- markup

_TOKEN_RE = re.compile(r'\$[^$\s]*\$|\[[^\[\]]*\]|#[\w;:.\-]+|#!|£[^£\s]+£|@[^!\s]+!|§.|\\n')


_CONCEPT_RE = re.compile(r"^\[Concept\('([^']+)'\s*,\s*'.*'\)(?:\|[eE])?\]$|^\[([A-Za-z0-9_]+)(?:\|[eE])?\]$")
_FORMAT_RE = re.compile(r'^(#[\w;:.\-]+|#!|\\n)$')
_VAR_RE = re.compile(r'^\$([^$|]+)(\|[^$]*)?\$$')
_SCOPE_RE = re.compile(r'^\[(.+?)(\.[A-Za-z_]+(\([^()]*\))?)?(\|[^\]|]*)?\]$')


def _normalize(tok):
    m = _CONCEPT_RE.match(tok)
    return f"[concept:{m.group(1) or m.group(2)}]" if m else tok


def _lenient(tok):
    """What must survive translation: the variable name without format, the scope object without
    the final getter and format ([X.GetName|U] == [X.Custom('CL_GEN')|l])."""
    m = _VAR_RE.match(tok)
    if m:
        return f'${m.group(1)}$'
    m = _SCOPE_RE.match(tok)
    if m and m.group(2):
        return f'[{m.group(1)}]'
    return tok


def markup_tokens(s, lenient=False):
    """Multiset of markup tokens. Concept links are normalised: [x|E] == [Concept('x','будь-який текст')|e].
    Formatting (#tags, #!, \\n) is a translator's freedom and is left out; see format_tokens.
    lenient=True keeps only variable names and scope objects, as a set: legacy translations pick
    their own getters and repeat objects."""
    toks = [_normalize(t) for t in _TOKEN_RE.findall(s) if not _FORMAT_RE.match(t)]
    if lenient:
        return collections.Counter(set(_lenient(t) for t in toks))
    return collections.Counter(toks)


_CALL_RE = re.compile(r"\[[^\]\[]*\]")


def call_quotes_ok(s):
    """Whether every script call's single quotes pair up.

    The engine parses ' inside [Foo('bar')] as a string delimiter, so a Ukrainian
    apostrophe there (об'єднання) or a stray " truncates the call and the whole
    loc string fails to render. Word-internal apostrophes must be U+2019.
    """
    for m in _CALL_RE.finditer(s):
        body = m.group(0)
        if body.count("'") % 2 or '"' in body:
            return False
    return True


def _syntax_flaws(s):
    """The set of syntax rules a string breaks, as short names."""
    flaws = set()
    depth = 0
    for ch in s:
        depth += (ch == '[') - (ch == ']')
        if depth < 0:
            flaws.add('brackets')
            break
    if depth:
        flaws.add('brackets')
    if s.count('$') % 2:
        flaws.add('dollars')
    if not call_quotes_ok(s):
        flaws.add('quotes')
    return flaws


def syntax_ok(s, en=None):
    """Whether the string can be shipped: balanced [], even $ count and paired
    quotes inside script calls.

    #tags are deliberately NOT counted. Measured against the game's own shipped
    russian localization, 447 of 17050 tagged strings leave a #tag unclosed
    (`#TOOLTIP:RELIGIONGROUP,muslim,X #L мусульман#!`), so the engine clearly
    does not require one #! per tag and a counting rule only blocks correct text.
    With `en` given, a flaw the source already has is not the translation's fault.
    Missing variables are a quality issue for review; broken syntax is not."""
    flaws = _syntax_flaws(s)
    if en is not None:
        flaws -= _syntax_flaws(en)
    return not flaws


def format_tokens(s):
    return collections.Counter(t for t in _TOKEN_RE.findall(s) if _FORMAT_RE.match(t))


# ---------------------------------------------------------------- extract

def cmd_extract(args):
    total = 0
    for root in ROOTS:
        strings = source_strings(root, game_dir=args.game, baseline=args.baseline)
        dst_root = WORK / 'en' / ('baseline' if args.baseline else 'current') / root
        shutil.rmtree(dst_root, ignore_errors=True)
        for relpath, keys in strings.items():
            write_yml_file(dst_root / f'{relpath}_l_english.yml', keys)
            total += len(keys)
        print(f'{root}: {sum(len(v) for v in strings.values())} keys in {len(strings)} files')
    print(f'extracted {total} keys total to {WORK / "en"}')


# ---------------------------------------------------------------- check

def cmd_check(args, bad=None):
    """Prints problems; returns the error count. `bad` (a set) collects (root, relpath, key) of entries
    whose markup is broken, so build can ship English for them instead of a broken string."""
    errors = warnings = structural = 0
    game_source = {root: source_strings(root, game_dir=args.game) for root in ROOTS}
    for path in translation_files():
        root = path.relative_to(TRANSLATIONS).parts[0]
        relpath = ns_from_file(path, root)
        source = game_source.get(root, {}).get(relpath)
        rel = path.relative_to(ROOT)
        if source is None:
            print(f'{rel}: namespace not found in the game'); errors += 1; structural += 1
            continue
        for key, entry in load_json(path).items():
            where = f'{rel} :: {key}'
            if key not in source:
                print(f'{where}: key no longer exists in the game'); warnings += 1
                continue
            if not isinstance(entry, dict) or not isinstance(entry.get('uk'), str):
                print(f'{where}: expected {{"en": ..., "uk": ...}}'); errors += 1; structural += 1
                continue
            if entry.get('en') != source[key]:
                print(f'{where}: English source changed, review translation\n'
                      f'   was: {entry.get("en")!r}\n   now: {source[key]!r}'); warnings += 1
                continue
            if not entry['uk']:
                continue  # missing/empty translation is not an error
            a, b = markup_tokens(source[key], args.lenient), markup_tokens(entry['uk'], args.lenient)
            if a != b:
                print(f'{where}: markup mismatch, missing {dict(a - b)}, extra {dict(b - a)}'); errors += 1
            if not syntax_ok(entry['uk'], source[key]):
                print(f'{where}: broken markup syntax'); errors += 1
                if bad is not None:
                    bad.add((root, relpath, key))
            elif args.formatting and format_tokens(source[key]) != format_tokens(entry['uk']):
                a, b = format_tokens(source[key]), format_tokens(entry['uk'])
                print(f'{where}: formatting differs, missing {dict(a - b)}, extra {dict(b - a)}'); warnings += 1
    print(f'{errors} error(s), {warnings} warning(s)')
    if structural:
        sys.exit('fix the structural errors above first')
    return errors


# ---------------------------------------------------------------- status

def cmd_status(args):
    total_done = total_all = 0
    for root in ROOTS:
        for relpath, keys in sorted(source_strings(root, game_dir=args.game).items()):
            keys = {k for k, en in keys.items() if en}   # empty source strings need no translation
            path = ns_file(root, relpath)
            done = sum(1 for k, e in load_json(path).items() if k in keys and e.get('uk')) if path.exists() else 0
            total_done += done
            total_all += len(keys)
            if done or args.all:
                pct = 100 * done // len(keys) if keys else 100
                print(f'{root:15} {relpath:45} {done:5}/{len(keys):<5} {pct:3}%')
    if total_all:
        print(f'{"total":61} {total_done:5}/{total_all:<5} {100 * total_done // total_all:3}%')


# ---------------------------------------------------------------- leftovers

# Latin words a Ukrainian string may keep: acronyms, Roman numerals, brands, game modes.
LEFTOVER_OK = {
    'SPQR', 'Ironman', 'Paradox', 'Interactive', 'Steam', 'PDX', 'Europa', 'Universalis', 'DLC', 'OK', 'UI', 'FPS', 'HDR',
    'VSync', 'Discord', 'Twitch', 'Windows', 'Tinto', 'Caesar', 'AI', 'ID', 'URL', 'BBCode', 'Clausewitz', 'Jomini',
    'Ctrl', 'Shift', 'Alt', 'Tab', 'Esc', 'Enter', 'Space', 'VRAM', 'GPU', 'CPU', 'RAM',
}
LEFTOVER_SKIP_NS = re.compile(r'^main_menu/(_debug|qa_debug/.*|editor|issue_reporter|credits|caesar_tools|lateralviews)$')
_CONCEPT_TEXT_RE = re.compile(r"\[Concept\('[^']*'\s*,\s*'([^']*)'\)[^\]]*\]")
_LEFTOVER_MARKUP_RE = re.compile(r'\$[^$\s]*\$|#\S+|£[^£\s]+£|@[^!\s]+!|§.|\\n')
_BRACKETS_RE = re.compile(r'\[[^\[\]]*\]')
_CODE_RE = re.compile(r'\b[A-Za-z]\w*(?:[.:]\w+)+|\b[A-Za-z]+_\w+|\b[A-Z][a-z]+[A-Z]\w*')   # getters, TOOLTIP:X, Select_CString
_LATIN_WORD_RE = re.compile(r'(?<![^\W\d_])[A-Za-z][A-Za-z\'’-]{2,}(?![^\W\d_])')
_ROMAN_RE = re.compile(r'^[IVXLCDM]+$')
# Frequent in the English source only inside kept Romance/German names ("Casa della Signoria"), not as English.
_NAME_PARTICLES = {'del', 'dei', 'della', 'delle', 'degli', 'des', 'dem', 'der', 'die', 'das', 'und', 'von', 'van',
                   'san', 'santa', 'alla', 'non', 'est', 'via', 'pro', 'real', 'inter', 'corpus', 'opus'}


def prose(s):
    """Visible words only: markup out, the text of [Concept('key','text')] kept."""
    s = _CONCEPT_TEXT_RE.sub(lambda m: f' {m.group(1)} ', s)
    while True:     # [Show...([ROOT.GetCountry])] nests
        t = _BRACKETS_RE.sub(' ', s)
        if t == s:
            break
        s = t
    return _LEFTOVER_MARKUP_RE.sub(' ', s)


def latin_words(s):
    return [w for w in _LATIN_WORD_RE.findall(prose(s)) if w not in LEFTOVER_OK and not _ROMAN_RE.match(w)]


def cmd_leftovers(args):
    """English left in the mod. Kinds: missing (no entry), empty (the game shows en), same (uk == en with words),
    code (markup leaked into visible text: a lost [ or #), english (a word the English source uses in lower case
    at least 5 times), foreign (other Latin words: kept Latin/Italian names and mottos, usually deliberate)."""
    kinds = ('missing', 'empty', 'same', 'code', 'english', 'foreign')
    sources = {root: source_strings(root, game_dir=args.game) for root in ROOTS}
    vocab = collections.Counter(w for src in sources.values() for keys in src.values() for en in keys.values()
                                for w in re.findall(r'\b[a-z]{3,}\b', prose(en)))
    per_ns = collections.defaultdict(collections.Counter)
    words = collections.defaultdict(collections.Counter)
    lines = []
    for root in ROOTS:
        for relpath, keys in sorted(sources[root].items()):
            ns = f'{root}/{relpath}'
            if LEFTOVER_SKIP_NS.match(ns):
                continue
            path = ns_file(root, relpath)
            tr = load_json(path) if path.exists() else {}
            for key, en in keys.items():
                if not en or not re.search(r'[^\W\d_]{2,}', prose(en)):
                    continue    # empty or markup-only source: nothing to translate
                e = tr.get(key)
                uk = e.get('uk') if isinstance(e, dict) else None
                if uk is None:
                    kind, extra = 'missing', ''
                elif not uk:
                    kind, extra = 'empty', ''
                elif uk == en:
                    if not latin_words(en):
                        continue
                    kind, extra = 'same', ''
                else:
                    code = collections.Counter(_CODE_RE.findall(prose(uk))) - collections.Counter(_CODE_RE.findall(prose(en)))
                    lat = latin_words(uk)
                    eng = [w for w in lat if vocab[w.lower()] >= 20 and w.lower() not in _NAME_PARTICLES]
                    if code:
                        kind, extra = 'code', ' '.join(code)
                    elif eng:
                        kind, extra = 'english', ' '.join(eng)
                    elif lat:
                        kind, extra = 'foreign', ' '.join(lat)
                    else:
                        continue
                    words[kind].update(extra.split())
                per_ns[ns][kind] += 1
                lines.append(f'{kind}\t{ns}\t{key}\t{extra}\t{en[:120]}\t{(uk or "")[:120]}')
    out = WORK / 'leftovers.tsv'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    rows = sorted(per_ns.items(), key=lambda kv: -sum(kv[1].values()))
    print(f'{"namespace":55} ' + ' '.join(f'{k:>7}' for k in kinds))
    for ns, c in rows[:args.top]:
        print(f'{ns:55} ' + ' '.join(f'{c[k]:7}' for k in kinds))
    total = sum((c for c in per_ns.values()), collections.Counter())
    print(f'{"total (" + str(len(per_ns)) + " namespaces)":55} ' + ' '.join(f'{total[k]:7}' for k in kinds))
    for kind in ('code', 'english', 'foreign'):
        print(f'top {kind}: ' + ', '.join(f'{w} {n}' for w, n in words[kind].most_common(args.top)))
    print(f'-> {out.relative_to(ROOT)}')


# ---------------------------------------------------------------- concepts

_CONCEPT_CALL_RE = re.compile(r"\[Concept\('([^']+)'\s*,\s*'([^']*)'\)")
_CYR_WORD_RE = re.compile(r"[А-Яа-яЇїІіЄєҐґ’'-]{4,}")


def concept_names():
    """{concept key: its Ukrainian name} from game_concepts ($game_concept_x$ references resolved)."""
    gc = {k: e.get('uk') or '' for k, e in load_json(ns_file('main_menu', 'game_concepts')).items()}
    resolve = lambda s: re.sub(r'\$(game_concept_\w+)\$', lambda m: gc.get(m.group(1), ''), s)
    return {k[len('game_concept_'):]: resolve(resolve(v)) for k, v in gc.items()
            if k.startswith('game_concept_') and not k.endswith('_desc')}


def stems(text):
    """Crude Ukrainian stems of the content words: the first 3 letters survive case endings (ринок/ринку, рада/раді)."""
    return {w.lower()[:3] for w in _CYR_WORD_RE.findall(prose(text))}


def cmd_concepts(args):
    """[Concept('key','text')] whose text does not share the stems of the concept's name in game_concepts."""
    names = concept_names()
    per_key = collections.defaultdict(collections.Counter)
    total = collections.Counter()
    lines = []
    for path in translation_files():
        ns = path.relative_to(TRANSLATIONS).with_suffix('').as_posix()
        for key, e in load_json(path).items():
            for ck, text in _CONCEPT_CALL_RE.findall(e.get('uk') or ''):
                name = names.get(ck) or names.get(ck.removesuffix('s')) or names.get(ck.removesuffix('_with_icon'))
                total['calls'] += 1
                if not name or not stems(name):
                    total['no canon name'] += 1
                    continue
                if stems(name) & stems(text):
                    continue    # a shortened name ("задоволення" for "задоволення групи населення") is fine
                total['off'] += 1
                variant = ' '.join(sorted(stems(text))) or '(empty)'
                per_key[ck][variant] += 1
                lines.append(f'{ck}\t{name}\t{text}\t{ns}\t{key}')
    if args.keys:
        rows = sorted({f'{l.split(chr(9))[3]} {l.split(chr(9))[4]}' for l in lines})
        Path(args.keys).write_text('\n'.join(rows) + '\n', encoding='utf-8')
        print(f'{len(rows)} rows -> {args.keys}')
    out = WORK / 'concepts.tsv'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(sorted(lines)) + '\n', encoding='utf-8')
    print(', '.join(f'{k} {v}' for k, v in total.items()) + f'; {len(per_key)} concept keys off canon')
    for ck, c in sorted(per_key.items(), key=lambda kv: -sum(kv[1].values()))[:args.top]:
        print(f'{sum(c.values()):5}  {ck:32} {names.get(ck) or names.get(ck.removesuffix("s")) or ""!s:28} '
              + ' | '.join(f'{v} ×{n}' for v, n in c.most_common(4)))
    print(f'-> {out.relative_to(ROOT)}')


def cmd_grep(args):
    """Rows whose uk (and optionally en) match: counts per namespace, optionally a keys file for translate.py fix."""
    uk_re, en_re = re.compile(args.uk), re.compile(args.en) if args.en else None
    rows, per_ns = [], collections.Counter()
    for path in translation_files():
        ns = path.relative_to(TRANSLATIONS).with_suffix('').as_posix()
        for key, e in load_json(path).items():
            if uk_re.search((e.get('uk') or '').lower()) and (not en_re or en_re.search(e['en'].lower())):
                rows.append(f'{ns} {key}'); per_ns[ns] += 1
    print(f'{len(rows)} rows in {len(per_ns)} namespaces; top: '
          + ', '.join(f'{n} {c}' for n, c in per_ns.most_common(5)))
    if args.keys:
        Path(args.keys).write_text('\n'.join(rows) + '\n', encoding='utf-8')


# ---------------------------------------------------------------- build

def cmd_build(args):
    bad = set()
    cmd_check(args, bad)
    if bad:
        print(f'{len(bad)} strings with broken markup syntax are left in English')
    by_root = collections.defaultdict(lambda: collections.defaultdict(dict))
    for path in translation_files():
        root = path.relative_to(TRANSLATIONS).parts[0]
        relpath = ns_from_file(path, root)
        for key, entry in load_json(path).items():
            if entry.get('uk') and (root, relpath, key) not in bad:
                by_root[root][relpath][key] = entry['uk']

    stage = DIST / MOD_NAME
    shutil.rmtree(DIST, ignore_errors=True)
    file_count = key_count = 0
    for root, files in by_root.items():
        for relpath, keys in files.items():
            if not keys:
                continue
            write_yml_file(stage / root / 'localization' / 'dlc' / 'english' / f'{relpath}_l_english.yml', keys)
            file_count += 1
            key_count += len(keys)
    print(f'built {file_count} files, {key_count} keys')

    if OVERLAY.exists():
        overlay_count = 0
        no_bom = []
        for src in OVERLAY.rglob('*'):
            if src.is_file():
                dst = stage / src.relative_to(OVERLAY)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                # the game refuses a .yml without the UTF-8 BOM: "Missing UTF8 BOM in ..."
                if src.suffix == '.yml' and src.read_bytes()[:3] != b'\xef\xbb\xbf':
                    no_bom.append(src.relative_to(OVERLAY).as_posix())
                overlay_count += 1
        print(f'copied {overlay_count} overlay files')
        for p in no_bom:
            print(f'WARNING: overlay file without UTF-8 BOM, the game will not read it: {p}')
    print(f'built {stage}')


def cmd_package(args):
    cmd_build(args)
    out = DIST / f'{MOD_NAME}-{MOD_VERSION}.zip'
    stage = DIST / MOD_NAME
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in stage.rglob('*'):
            if f.is_file():
                z.write(f, f.relative_to(stage))
    print(f'packaged {out}')


def mod_dir(release=False):
    base = (Path(os.environ['USERPROFILE']) / 'Documents' / 'Paradox Interactive'
            / 'Europa Universalis V' / 'mod')
    return base / (MOD_DIR_NAME if release else DEV_DIR_NAME)


def _mark_dev(dst):
    """Give the installed copy its own id and a visible name, so the launcher lists two mods.

    No square brackets in the name: the game substitutes it into $MOD$ rows such as
    MODS_GUI_MOD_CHECKSUM_WARNING, where [x] is parsed as a data-system function call
    ("Could not find data system function 'DEV'") and the string fails to render."""
    path = dst / '.metadata' / 'metadata.json'
    meta = load_json(path)
    meta['id'] = DEV_MOD_ID
    meta['name'] = f'DEV {meta["name"].replace("[", "(").replace("]", ")")}'
    meta['version'] = f'{MOD_VERSION}-dev'
    save_json(path, meta)


def cmd_install(args):
    cmd_build(args)
    stage = DIST / MOD_NAME
    dst = mod_dir(args.release)
    dst.mkdir(parents=True, exist_ok=True)
    for name in ('main_menu', 'loading_screen', 'in_game', '.metadata'):
        target = dst / name
        shutil.rmtree(target, ignore_errors=True)
        src = stage / name
        if src.exists():
            shutil.copytree(src, target)
    src_desc = stage / 'description.bbcode'
    if src_desc.exists():
        shutil.copy2(src_desc, dst / 'description.bbcode')
    if args.release:
        print(f'installed RELEASE build into {dst}')
        print('this is the workshop-manager folder: publishing from it uploads this build to the Workshop')
    else:
        _mark_dev(dst)
        print(f'installed DEV build ({MOD_VERSION}-dev) into {dst}')
        print('enable "[DEV] ..." in the launcher playset and disable the published mod')


def cmd_uninstall(args):
    dst = mod_dir(args.release)
    if not args.release and dst.exists():
        shutil.rmtree(dst)          # the dev folder is ours alone: remove it whole
        print(f'removed {dst}')
        return
    for name in ('main_menu', 'loading_screen', 'in_game'):
        p = dst / name
        if p.exists():
            shutil.rmtree(p)
            print(f'removed {p}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--game', default=os.environ.get('EU5_DIR', DEFAULT_GAME))
    sub = parser.add_subparsers(dest='cmd', required=True)
    for name in ('check', 'build', 'package', 'install', 'uninstall'):
        sp = sub.add_parser(name)
        sp.add_argument('--formatting', action='store_true', help='also warn when #tags or \\n differ from the original')
        sp.add_argument('--lenient', action='store_true',
                        help='compare only variable names and scope objects (legacy translations use other getters)')
        if name in ('install', 'uninstall'):
            sp.add_argument('--release', action='store_true',
                            help=f'use the workshop-manager folder "{MOD_DIR_NAME}" instead of "{DEV_DIR_NAME}"')
    sub.add_parser('extract').add_argument('--baseline', default=None, help='read from this dir instead of --game')
    sub.add_parser('status').add_argument('--all', action='store_true', help='include untranslated namespaces')
    sub.add_parser('leftovers').add_argument('--top', type=int, default=30, help='namespaces and words to print')
    sp = sub.add_parser('concepts')
    sp.add_argument('--top', type=int, default=40, help='concept keys to print')
    sp.add_argument('--keys', default=None, help='also write the rows as "<root>/<ns> <key>" lines for translate.py fix')
    sp = sub.add_parser('grep')
    sp.add_argument('uk', help='regex searched in the lower-cased uk text')
    sp.add_argument('--en', default=None, help='and this regex in the lower-cased en text')
    sp.add_argument('--keys', default=None, help='write the rows as "<root>/<ns> <key>" lines for translate.py fix')
    args = parser.parse_args()
    result = globals()[f'cmd_{args.cmd}'](args)
    sys.exit(1 if args.cmd == 'check' and result else 0)


if __name__ == '__main__':
    main()
