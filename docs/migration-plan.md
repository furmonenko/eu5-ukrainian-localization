# План: перехід на JSON-джерело й оновлення до гри 1.3.x

Стан на 2026-09-19: мод 1.0.3 писався під гру 1.0.9; гра — 1.3.x (buildid 24187685). У грі 37 441 новий
ключ, у моді 10 236 рядків лишилися англійською, ≈3.3K ключів мод містить, а гра — вже ні.

## Цільова розкладка репозиторію

```
uk.py                       extract | check | status | build | package | install   (за зразком ../guild-europa1410-ukrainian/uk.py)
translate.py                копія з guild-europa1410 із заміненою розміткою (Paradox замість UE5)
translations/<root>/<шлях>.json     {key: {"en": ..., "uk": ...}}; <root> = main_menu | loading_screen;
                            <шлях> = шлях файлу гри відносно localization/english без суфікса _l_english.yml,
                            напр. translations/main_menu/events/DHE/flavor_fra.json
overlay/                    файли мода, яких у грі немає, копіюються в збірку побайтово:
                            customizable_localization_*, location_names_ruthenian, jomini/clausewitz-файли,
                            .metadata/, description.bbcode, thumbnail.png
work/  (ignored)            work/en/<версія>/ — знімки англійської гри; work/stale.json; work/review; work/log
dist/  (ignored)            dist/<MOD_NAME>/ — зібраний мод; dist/<MOD_NAME>-<версія>.zip
tools/localization_gui.py   лишається для контриб’юторів (редагує yml у dist — описати в CONTRIBUTING пізніше)
main_menu/, loading_screen/ ЗНИКАЮТЬ з git після міграції (їх породжує build)
```

## Формат файлів гри

`<root>/localization/english/**/<name>_l_english.yml`, UTF-8 з BOM, перший рядок `l_english:`, далі
` KEY: "text"` (ключі без номера версії; парсер має приймати й `KEY:0 "text"`). Коментарі `#`. Лапки всередині
тексту екрануються `\"`. Мод підміняє англійську: збірка кладе файли в `<root>/localization/dlc/english/<той самий шлях>`
(розкладка чинного мода, сумісна з досягненнями).

Гра: `C:\Program Files\Steam\steamapps\common\Europa Universalis V\game` (appid 3450310). Англійська лежить у
`game/main_menu/localization/english`, `game/loading_screen/localization/english`,
`game/dlc/D000_shared/main_menu/localization/dlc/english` (останню теж читати; root = main_menu).

## Розмітка (валідація побайтово)

`$VAR$`, `$VAR|fmt$`, `[Scope.Func(...)]`, `#tag … #!` (`#bold`, `#R`, `#tooltippable;tooltip:…`), `£icon£`,
`@icon!`, `§Y…§!`, `\n`. Регулярка токенів: `\$[^$\s]*\$|\[[^\[\]]*\]|#[\w;:.\-]+|#!|£[^£\s]+£|@[^!\s]+!|§.|\\n`.
Мультимножина токенів у `uk` має дорівнювати мультимножині в `en`.

## Кроки

1. **`uk.py extract`** — прочитати англійську гри у `work/en/current/` (копія yml) і в пам’ять як `{root: {relpath: {key: text}}}`.
   `--baseline <dir>` дозволяє читати інший знімок (1.0.10 із DepotDownloader) тим самим кодом.
2. **`tools/migrate.py`** (одноразово) — зібрати `translations/` з чинних yml мода:
   - для кожного ключа гри взяти `uk` з мода, де б він не лежав (ключі мігрують між файлами); `en` = текст із
     `--baseline` (1.0.10), якщо ключ там є, інакше з поточної гри;
   - `uk == en` або `uk` без кирилиці при латинських словах в `en` → вважати неперекладеним: `uk: ""`;
   - ключі мода, яких нема в грі → `work/stale.json` `{key: {uk, file}}`; файли мода, у яких жодного ключа гри → `overlay/`;
   - результат: `python uk.py status` показує частку перекладу по файлах.
3. **`uk.py check`** — як у guild: змінений `en` проти гри → warning, розмітка → error, ключ зник → warning.
4. **`uk.py build`** — `dist/<MOD_NAME>/<root>/localization/dlc/english/<шлях>_l_english.yml` з `uk` (порожній `uk` →
   рядок не пишеться, гра покаже англійську), плюс `overlay/` побайтово. **`package`** — zip. **`install`** — копія в
   `%USERPROFILE%\Documents\Paradox Interactive\Europa Universalis V\mod\Ukraina Universalis 1.0\` (та, що в playset).
5. Прибрати `main_menu/`, `loading_screen/` з git; оновити `.github/workflows/release.yml` (build перед пакуванням),
   README/CONTRIBUTING — окремим кроком.
6. Переклад: `translate.py run` за пріоритетом інтерфейс → механіка → події → імена/локації.

## Знімок 1.0.10

Гілка Steam `1.0.10` (остання 1.0.x; 1.0.9 як гілки нема). Команда виконується користувачем (потрібен логін):

```
depotdownloader -app 3450310 -branch 1.0.10 -username <login> -remember-password -filelist work/depot_filelist.txt -dir work/en/1.0.10
```
