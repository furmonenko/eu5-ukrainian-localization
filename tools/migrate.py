"""One-shot: build translations/ from the current mod's yml files.

    python tools/migrate.py [--baseline DIR] [--game PATH]

For every key in the current game English, take `uk` from the mod (wherever it currently lives - keys
migrate between files across game updates); `en` = text from --baseline (the last game version the mod
was translated against) when the key is there, else the current game text.

`uk == en`, or `uk` has no Cyrillic while `en` has a Latin word of 3+ letters, counts as untranslated and
is written as `uk: ""`. Mod keys that no longer exist in the game go to work/stale.json. Mod files with
zero surviving game keys are copied verbatim into overlay/ (customizable_localization variants, jomini/
clausewitz UI files, etc. - the mod ships more files than the base English localization has).
"""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from uk import ROOT, WORK, TRANSLATIONS, OVERLAY, ROOTS, MOD_VERSION, load_json, save_json, source_strings, \
    read_yml_file, ns_file, DEFAULT_GAME

LETTERS_RE = re.compile(r'[A-Za-z]{3,}')
CYR_RE = re.compile(r'[А-Яа-яЇїІіЄєҐґ]')

MOD_SOURCE_DIRS = {
    'main_menu': 'main_menu/localization/dlc/english',
    'loading_screen': 'loading_screen/localization/dlc/english',
}


def mod_strings(root):
    """{relpath: {key: uk_text}} from the current mod's yml files for this root."""
    out = {}
    base = ROOT / MOD_SOURCE_DIRS[root]
    if not base.exists():
        return out
    for path in sorted(base.rglob('*_l_english.yml')):
        relpath = path.relative_to(base).as_posix()[:-len('_l_english.yml')]
        out[relpath] = read_yml_file(path)
    return out


def is_untranslated(en, uk):
    if uk == en:
        return True
    if LETTERS_RE.search(en) and not CYR_RE.search(uk):
        return True
    return False


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--baseline', default=None, help='previous game version snapshot dir (same layout as --game)')
    p.add_argument('--game', default=os.environ.get('EU5_DIR', DEFAULT_GAME))
    args = p.parse_args()

    total_keys = total_uk = stale_count = overlay_files = 0
    stale = {}

    for root in ROOTS:
        game = source_strings(root, game_dir=args.game)
        baseline = source_strings(root, baseline=args.baseline) if args.baseline else {}
        baseline_by_key = {k: v for keys in baseline.values() for k, v in keys.items()}  # keys move between files
        mod_files = mod_strings(root)

        # key -> uk text, wherever it currently lives in the mod; also remember which file it came from
        mod_key_uk, mod_key_file = {}, {}
        for relpath, keys in mod_files.items():
            for key, uk in keys.items():
                mod_key_uk[key] = uk
                mod_key_file[key] = relpath

        game_keys = {k for keys in game.values() for k in keys}

        # mod keys absent from the current game -> stale
        for key, uk in mod_key_uk.items():
            if key not in game_keys:
                stale[key] = {'uk': uk, 'file': mod_key_file[key]}
                stale_count += 1

        # mod files with zero surviving game keys -> overlay, copied verbatim
        for relpath in mod_files:
            if not any(k in game_keys for k in mod_files[relpath]):
                src = ROOT / MOD_SOURCE_DIRS[root] / f'{relpath}_l_english.yml'
                dst = OVERLAY / root / 'localization' / 'dlc' / 'english' / f'{relpath}_l_english.yml'
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                overlay_files += 1

        for relpath, keys in sorted(game.items()):
            entries = {}
            for key, game_en in sorted(keys.items()):
                baseline_en = baseline_by_key.get(key)
                en = baseline_en if baseline_en is not None else game_en
                uk = mod_key_uk.get(key, '')
                untranslated = False
                if uk:
                    if is_untranslated(en, uk):
                        untranslated = True
                    if baseline_en is not None and is_untranslated(baseline_en, uk):
                        untranslated = True
                    if is_untranslated(game_en, uk):
                        untranslated = True
                if untranslated:
                    uk = ''
                # a translated string keeps the English it was made from, so `check` flags later changes
                entries[key] = {'en': en if uk else game_en, 'uk': uk}
                total_keys += 1
                if uk:
                    total_uk += 1
            save_json(ns_file(root, relpath), entries)

    save_json(WORK / 'stale.json', dict(sorted(stale.items())))

    # overlay: description.bbcode + .metadata/metadata.json
    desc_src = ROOT / 'description.bbcode'
    if desc_src.exists():
        (OVERLAY).mkdir(parents=True, exist_ok=True)
        shutil.copy2(desc_src, OVERLAY / 'description.bbcode')

    installed_meta = (Path(os.environ['USERPROFILE']) / 'Documents' / 'Paradox Interactive' / 'Europa Universalis V'
                       / 'mod' / 'Ukraina Universalis 1.0' / '.metadata' / 'metadata.json')
    if installed_meta.exists():
        meta = json.loads(installed_meta.read_text(encoding='utf-8'))
        meta['version'] = MOD_VERSION
        meta['supported_game_version'] = '1.3.*'
        dst = OVERLAY / '.metadata' / 'metadata.json'
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(f'wrote {dst}')
    else:
        print(f'WARNING: {installed_meta} not found, skipped .metadata/metadata.json', file=sys.stderr)

    print(f'{total_keys} keys, {total_uk} translated -> {TRANSLATIONS}')
    print(f'{len(stale)} stale keys -> {WORK / "stale.json"}')
    print(f'{overlay_files} mod files with no surviving game keys -> {OVERLAY}')


if __name__ == '__main__':
    main()
