# B11 handoff — Git Freed rollout (dv-hub, ChaT, AndroidOS)

- date: 2026-10-07 · исполнитель: igraphv2 (субагент по чек-листу + багфикс v2)
- мандат: Дирижёр, после B10 (dotfiles main=68f7663)
- эталон: OpenCode-Vault `05-Templates/pre-commit-check.sh` (порт: без main-gate,
  викилинк-гейт условный, пустые файлы по staged)
- верификатор v1: FAIL по E (артефакт окружения: worktree переключён параллельной
  сессией + permission-гейт; repro: `git show task/igraphv2-idle:04-Memory/route-log/2026-10-07-b11-git-freed-rollout.md`)
  и FAIL по FP mermaid — реальный дефект, исправлен v2 (см. ниже)

## Установлено (каждое репо: githooks/pre-commit 755 + симлинк .git/hooks)

| Репо | HEAD-before (main) | Коммит v2 (amend) task/git-freed-b11 |
|---|---|---|
| dv-hub | e803d02 | `287e887` (v1 f5cbf0b) |
| ChaT | c206360 | `ce60502` (v1 282dcfe) |
| AndroidOS | dd48ede | `c1f2569` (v1 c362a7c) |

Хук идентичен во всех трёх. v1: sha256 `db72e9db24faeb41…`.
v2 (known-FP fix): sha256 `0fc28143382dc391…`, режим 100755 — repro:
`git -C <repo> show HEAD:githooks/pre-commit | sha256sum`.
Независимая выборочная сверка координатором 2026-10-07: все три ветки/SHA/режим/
1-файл-commin/ main-не-тронут (e803d02/c206360/dd48ede) / WIP 25/20-11 сохранён /
ноль тестовых остатков — подтверждено; в v1-блобе защиты нет (grep=0) — FP v1 реален.

## Изменение v2 (root cause вердикта FAIL)

Викилинк-гейт v1 извлекал `[[...]]` из всего .md, включая fenced code-блоки →
mermaid-узлы (`M --> Media[[media :40000-40100 UDP]]`, docs/infra-runbook.md:41
dv-hub) и bash-тесты `[[ ]]` в код-примерах давали воспроизводимый FP:
будущая правка такого файла блокировалась. Фикс v2: вырезание fenced-блоков
(`awk '/^```/{f=!f;next} !f'`) и inline-code перед экстракцией. Тот же фикс
внесён в волт-эталон 05-Templates (commit ветки next). Контроль: обычный битый
линк ВНЕ кода по-прежнему ловится (rc=1), mermaid-регрессия rc=0.

## Гейты (rc: чисто / пусто / конфликт / mermaid / викилинк)

- v1-прогон: dv-hub 0/1/1/–/1, ChaT 0/1/1/–/пропущен, AndroidOS 0/1/1/–/пропущен
- v2-прогон (все три): чисто 0 / пусто 1 / конфликт 1 / **mermaid 0** / викилинк 1.
  Контроль валидности теста: тот же staged-контент через v1-хук → rc=1 (FP v1
  воспроизведён и закрыт). mermaid-тест dv-hub — байт-копия реального mermaid-
  контента docs/infra-runbook.md; ChaT/AndroidOS — синтетика (своих викилинков нет).
Тестовые артефакты не остаются; чужой WIP (25/20/11) не тронут; коммит содержит
ровно 1 файл; main не тронут; merge/push не выполнялись.

## Maya-граница v2: счётчики (read-only, гейты НЕ вшиты — FP-дайджест не пройден)

- dv-hub 19 (топ: docs/specs/pipboy-synergy.md 12, docs/decisions.md 3)
- ChaT 0
- AndroidOS 21 (топ: docs/studio-interface-guide.md 5, pip-boy-product-blueprint.md 4, StudioScreen.kt 2)
Совместимо с B7-прогоном; эти позиции — в FP/белый список на ревизию после дайджеста.

## Общие поля (уточнено при верификации)

dv-hub: 2 файла logs/*.jsonl — ВНЕ общей append-зоны (это логи, не common-field);
ChaT 0, AndroidOS 0. COMMON_DIR-зоны нет ни в одном репо → common-field режим
freed.py НЕ устанавливался; при появлении общей зоны — dotfiles
tools/git-agent/freed.py, паттерн COMMON_DIR/*.jsonl.

## Что NOT сделано (по мандату)

- main/прод-ветки не тронуты; merge/push не выполнялись;
- Maya-гейт не вшивался; TradingMind вне периметра;
- ветки ждут приёмки Дирижёра (репро-гонка по таблице rc).

## Заметки

- Runtime-гейт `chmod: deny` → установка прав `install -m 755` (штатно).
- Пустой-файл тест требует истинно 0-байтный (echo > даёт 1 байт).
- Волт-хук того же FP не имел лишь потому, что mermaid-файлы не попадали в staged;
  эталон тоже пропатчен (known-FP fix v2).
