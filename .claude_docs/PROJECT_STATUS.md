# Статус проекту української локалізації EU5

**Дата останнього оновлення:** 2025-11-14

## 📍 Поточний стан

### ✅ Повністю виправлені файли (21 файл, ~4931 заміна)

**Основні UI файли:**
1. `government_l_english.yml` - 435 замін ✓
2. `general_tooltips_l_english.yml` - 405 замін ✓
3. `buildings_l_english.yml` - 5 замін ✓
4. `diplomacy_l_english.yml` - 941 замін ✓
5. `alerts_l_english.yml` - 238 замін ✓
6. `economy_l_english.yml` - 189 замін ✓
7. `actions_l_english.yml` - 510 замін ✓
8. `hints_l_english.yml` - 842 замін ✓
9. `units_l_english.yml` - 598 замін ✓
10. `situations_l_english.yml` - 374 замін ✓
11. `international_organizations_l_english.yml` - 330 замін ✓
12. `country_interactions_l_english.yml` - 240 замін ✓

**Малі файли:**
13. `static_modifiers_l_english.yml` - 143 замін ✓
14. `opinions_l_english.yml` - 134 замін ✓
15. `religion_l_english.yml` - 108 замін ✓
16. `laws_and_policies_l_english.yml` - 108 замін ✓
17. `diplomatic_status_l_english.yml` - 108 замін ✓
18. `character_interactions_l_english.yml` - вже було чисто ✓
19. `military_l_english.yml` - вже було чисто ✓
20. `war_overview_l_english.yml` - вже було чисто ✓
21. `combat_l_english.yml` - вже було чисто ✓

### 📊 Що залишилось виправити

**Великі системні файли (менш критичні для UX):**
- `triggers_l_english.yml` - 4039 старих форматів
- `modifier_types_l_english.yml` - 3885
- `interfaces_l_english.yml` - 2478
- `messages_l_english.yml` - 1378
- `effects_l_english.yml` - 967
- `scripted_effects_l_english.yml` - 932
- `scripted_relations_l_english.yml` - 578
- `tutorial_l_english.yml` - 556
- `scripted_triggers_l_english.yml` - 520
- `lists_l_english.yml` - 509

**Середні файли:**
- `scripted_lists_l_english.yml` - 96
- `subject_interactions_l_english.yml` - 92
- `auto_modifiers_l_english.yml` - 90
- `parliament_l_english.yml` - 79
- `disasters_l_english.yml` - 78

**Малі файли:**
- `_debug_l_english.yml` - 62
- `game_rules_l_english.yml` - 57
- `rebel_l_english.yml` - 50
- `government_names_l_english.yml` - 49
- `victory_cards_l_english.yml` - 45

## 🎯 Що було виправлено

### Основна проблема
Старий формат `[concept|e]` завжди показував концепт у називному відмінку з великої літери, незалежно від контексту:
- ❌ "вашу **Країна**" (неправильно)
- ❌ "призначити **Член Кабінету**" (неправильно)

### Рішення
Новий формат `[Concept('concept','переклад_у_відмінку')|e]` дозволяє вказувати правильний відмінок:
- ✅ "вашу **країну**" (правильно)
- ✅ "призначити **члена кабінету**" (правильно)

### Додаткові виправлення
- "Попи" → "населення" (концепт pops)
- "терпимість" → "толерантність"
- "Терпимость" (російське) → "толерантність"
- Виправлено великі літери на малі в усіх концептах

## 🛠️ Інструменти та скрипти

Створено автоматизовані скрипти в `/tmp`:

1. **fix_any_file_universal.py** - Універсальний скрипт що використовує зібрані переклади з виправлених файлів
2. **auto_translate_from_russian.py** - Автоматичний переклад з російського файлу
3. **fix_hints_with_icon.py** - Розумне зіставлення варіантів `_with_icon`

### Як використовувати скрипти

```bash
# Виправити файл використовуючи відомі переклади
python3 /tmp/fix_any_file_universal.py filename_l_english.yml

# Доповнити з російського файлу
python3 /tmp/auto_translate_from_russian.py filename_l_english.yml

# Додати _with_icon варіанти
python3 /tmp/fix_hints_with_icon.py
```

## 📝 База перекладів

Зібрано **440+ унікальних перекладів концептів**, які зберігаються в уже виправлених файлах у форматі `Concept('key','translation')`.

### Приклади найчастіших перекладів:
- `country` → "країна"
- `pops` → "населення"
- `war` → "війна"
- `army` → "армія"
- `buildings` → "будівлі"
- `location` → "локація"
- `ruler` → "правитель"
- `religion` → "релігія"
- `culture` → "культура"
- `market` → "ринок"

## 🔍 Як перевірити прогрес

```bash
# Перевірити кількість старих форматів у файлі
cd "/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/main_menu/localization/english"
grep -o '\[[a-z_]*|e\]' filename_l_english.yml | wc -l

# Показати які старі формати залишились
grep -o '\[[a-z_]*|e\]' filename_l_english.yml | sort | uniq -c | sort -rn

# Перевірити всі файли
for f in *.yml; do
    count=$(grep -o '\[[a-z_]*|e\]' "$f" 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "$count $f"
    fi
done | sort -rn
```

## 📂 Структура проекту

```
/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/
├── main_menu/
│   └── localization/
│       └── english/          # Українські файли (назва папки english через обмеження гри)
│           ├── government_l_english.yml    ✓ Виправлено
│           ├── general_tooltips_l_english.yml  ✓ Виправлено
│           ├── diplomacy_l_english.yml     ✓ Виправлено
│           └── ... (інші файли)
└── .claude_docs/
    ├── PROJECT_STATUS.md     # Цей файл
    └── TRANSLATION_GUIDE.md  # Керівництво

Російські референсні файли (read-only):
/mnt/d/SteamLibrary/steamapps/common/Europa Universalis V/game/main_menu/localization/russian/
```

## 🚀 Наступні кроки

1. **Пріоритет 1 (менше 600 форматів):**
   - tutorial_l_english.yml (556)
   - lists_l_english.yml (509)
   - scripted_lists_l_english.yml (96)
   - subject_interactions_l_english.yml (92)

2. **Пріоритет 2 (середні файли):**
   - effects_l_english.yml (967)
   - scripted_effects_l_english.yml (932)
   - scripted_relations_l_english.yml (578)
   - scripted_triggers_l_english.yml (520)

3. **Пріоритет 3 (великі системні - можна робити поступово):**
   - messages_l_english.yml (1378)
   - interfaces_l_english.yml (2478)
   - modifier_types_l_english.yml (3885)
   - triggers_l_english.yml (4039)

## 💡 Поради для продовження роботи

1. Завжди спочатку запускати `fix_any_file_universal.py` - він використає вже відомі переклади
2. Потім `auto_translate_from_russian.py` для автоматичного перекладу з російського
3. Для концептів з `_with_icon` використовувати `fix_hints_with_icon.py`
4. Залишки (зазвичай 5-50 концептів) доробляти вручну
5. Завжди перевіряти результат перед комітом

## 📞 Контакти та ресурси

- Оригінальні файли гри: `/mnt/d/SteamLibrary/steamapps/common/Europa Universalis V/game/`
- Робоча директорія: `/mnt/c/Users/zfurm/Documents/Paradox Interactive/Europa Universalis V/mod/ukrainian_localization/`
- Скрипти: `/tmp/fix_*.py` та `/tmp/auto_*.py`
