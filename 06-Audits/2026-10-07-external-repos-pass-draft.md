---
type: audit-draft
status: draft
timestamp: 2026-10-07
source: coordinator mandate via route-log append #10
provenance: research researcher ses_eece6127cffez6zTL2sYNmr4Ka + прямой read-only pass librarian (external_directory allow)
owner: команда; поэтапный review
---

# External repos — read-only pass (draft)

## Резюме и границы

- Проверены четыре репозитория: `dv-hub`, `dotfiles`, `ChaT`, `AndroidOS`; цель — доступность, реальные объекты, текущий/исторический статус и расхождения с карточками Vault. Evidence: `/home/rudra/Projects/dv-hub`, `/home/rudra/dotfiles`, `/home/rudra/Projects/ChaT`, `/home/rudra/Projects/AndroidOS`.
- Скоуп задан координатором 2026-10-07. Evidence: `route-log append #10`.
- TradingMind в pass не включён; только memory-reference/bootstrap candidate. Evidence: `route-log append #10`.

## Кросс-мотивная находка

- В трёх репо (`dv-hub`, `ChaT`, `AndroidOS`) в worktree обнаружены массовые незакоммиченные удаления файлов `.opencode/agents` и/или `.opencode/command`. `dotfiles` чистый, единственное исключение — `?? docs/specs/bugfix-proactive-plugin.md`. Evidence: `/home/rudra/Projects/dv-hub` (`git status`), `/home/rudra/dotfiles` (`git status`), `/home/rudra/Projects/ChaT` (`git status`), `/home/rudra/Projects/AndroidOS` (`git status`).
- `dv-hub`: 25 строк status — 16 `D`, 7 `M`, 2 `??`; удалены `.opencode/agents/{build,infra,plan,researcher,reviewer}.md` и `.opencode/commands/{hygiene,morning,review,spec,sync-context,sync-context-self}.md`. Evidence: `/home/rudra/Projects/dv-hub` (`git status`).
- `ChaT`: 20 строк status — 18 `D`, 2 `??`; удалены 9 агентов, включая `chat-reviewer`, `community-architect`, `curator`, `development-manager`, `product-market`, `regeneration-designer`, `tea-master`, `tea-scientist`, `velisov-steward`, а также команды (включая `develop`, `experiment`). Evidence: `/home/rudra/Projects/ChaT` (`git status`).
- `AndroidOS`: удалены `.opencode/agents/{builder,planner,researcher,reviewer,verifier}.md` и `.opencode/command/android-*.md` (5+5 файлов). Evidence: `/home/rudra/Projects/AndroidOS` (`git status`).
- `dotfiles`: worktree чистый; единственное исключение — `?? docs/specs/bugfix-proactive-plugin.md`. Evidence: `/home/rudra/dotfiles` (`git status`).
- AndroidOS фактически использует `.mcode/agents` и `.mcode/command`; это наблюдение, а не доказательство причины удалений. Evidence: `/home/rudra/Projects/AndroidOS/.mcode/agents`, `/home/rudra/Projects/AndroidOS/.mcode/command`.
- Гипотеза о переносе проектных объектов в другой каталог — [проверить]; кто совершил удаления — [проверить]. Удаления не включены ни в один коммит на момент pass (worktree-only, git status D) — кто их совершил и когда, [проверить]. Evidence: `/home/rudra/Projects/dv-hub` (`git status`, `git log`), `/home/rudra/Projects/ChaT` (`git status`, `git log`), `/home/rudra/Projects/AndroidOS` (`git status`, `git log`).
- Чужие незакоммиченные правки не тронуты согласно правилу tree-cop. Evidence: `/home/rudra/dotfiles/opencode-global/.config/opencode/AGENTS.md` (раздел о `tree-cop` и чужих правках).

## 1. dv-hub

- Репозиторий доступен; ветка `main` синхронна с `origin/main`; последний коммит — `e803d02` от 2026-09-29, «merge: V2-TODO compaction (task/v2-todo-fixes)». Evidence: `/home/rudra/Projects/dv-hub` (`git status`, `git log`).
- `BLOCKED` при первом проходе researcher-субагентом (`Permission denied: external_directory`); снят прямым read-only проходом из сессии librarian (`external_directory: allow`, git-команды `git -C <path>`).
- Execution specs: `docs/specs/{audit-drift-backlog,data-recovery,dev-loop-upgrade-2026-09,local-development,pipboy-synergy,README}.md`. Evidence: `/home/rudra/Projects/dv-hub/docs/specs/`.
- `opencode.json` задаёт модель `opencode-go/deepseek-v4-flash`, LSP и instructions, включая `docs/product-vision.md`; permission-гейты запрещают чтение `.env*`, `auth.json`, `.ssh`, `keys-passwords`, `git push --force`, `rm -rf`, `/etc`, `/root`. Evidence: `/home/rudra/Projects/dv-hub/opencode.json`.
- `.opencode/` фактически содержит только `node_modules`, `package.json`, `package-lock.json`; agents/commands удалены в worktree. Evidence: `/home/rudra/Projects/dv-hub/.opencode/`, `/home/rudra/Projects/dv-hub` (`git status`).
- `UNKNOWN: плагины не обнаружены; история ограничена последним коммитом (e803d02, `git log -1`)`. Evidence: `/home/rudra/Projects/dv-hub/.opencode/`, `/home/rudra/Projects/dv-hub` (`git log -1`).
- Карточке Vault требуется сверка и пометка актуальности: факт содержимого карточки без повторного чтения — [проверить]. Evidence: `/home/rudra/Projects/OpenCode-Vault/03-Projects/dv-hub.md`.

## 2. dotfiles

- Доступен; ветка `task/maya-lint-handshake`; последний коммит — `1a8b7c1` от 2026-10-07, «docs(specs): maya-lint — append резолюции librarian (whitelist fragment-level...)». Worktree чистый, кроме `?? docs/specs/bugfix-proactive-plugin.md`. Evidence: `/home/rudra/dotfiles` (`git status`, `git log`).
- Подтверждены 7 агентов: `verifier`, `meta`, `tree-cop`, `reviewer`, `system-audit`, `researcher`, `system-ops`. Evidence: `/home/rudra/dotfiles/opencode-global/.config/opencode/agent/`.
- Подтверждены команды: `done`, `flush`, `agents`, `dream`, `loop`, `ship`, `bridge`, `prov`, `spec`, `branch`, а также дубликаты `ship` и `branch` в `commands/`. Evidence: `/home/rudra/dotfiles/opencode-global/.config/opencode/command/`, `/home/rudra/dotfiles/opencode-global/.config/opencode/commands/`.
- Подтверждены 12 plugins: `branch-auto.ts`, `telemetry.ts`, `session-restart-nudge.ts`, `decision-queue-hook.ts`, `input-security.ts`, `main-protector.ts`, `leak-guard.ts`, `replay-budget.ts`, `tree-hygiene.ts`, `session-flush.ts`, `spec-write-routing.ts`, `fix-tool-schema.ts`. Evidence: `/home/rudra/dotfiles/opencode-global/.config/opencode/plugins/`.
- `opencode.jsonc` содержит `ask` для `TASKS.md`, `00-INDEX.md`, `active-context.md`, `registry.json`, `AGENTS.md`; `deny` для sudo/chmod/chown/systemctl stop/disable/mask/force-push/branch-del/rm -rf и секретов `.env`, credentials, `.pem`, `.key`, SSH. Evidence: `/home/rudra/dotfiles/opencode-global/.config/opencode/opencode.jsonc`.
- История подтверждает внедрение telemetry, verifier/read-only permission-гейтов, meta write-grant, leak-guard, peer-comms handshake, maya-lint v2 и резолюции librarian. Evidence: `/home/rudra/dotfiles` (`git log/HEAD`).
- ADR подтверждены: ADR-016 (2026-09-29) tree-cop stash-foreign; ADR-017 и ADR-018 (2026-09-30) правила stow и `$ZSH`; ADR-019 (2026-10-01) branch ownership; ADR-020 (2026-10-06) append-only peer handshake Bash+jq. Evidence: `/home/rudra/dotfiles/docs/decisions.md`.

## 3. ChaT

- Репозиторий доступен; ветка `main` синхронна с `origin/main`; последний коммит — `c206360` от 2026-09-05, «docs: обновить состояние репозитория и настройки Obsidian»; status содержит 20 строк (18 `D`, 2 `??`). Evidence: `/home/rudra/Projects/ChaT` (`git status`, `git log`).
- `BLOCKED` при первом проходе researcher-субагентом (`Permission denied: external_directory`); снят прямым read-only проходом из сессии librarian (`external_directory: allow`, git-команды `git -C <path>`).
- В корне подтверждены `AGENTS.md`, `docs`, `index.html`, `legacy`, `logs`, `README.md`, `registers`; `.opencode/` фактически содержит только `node_modules`, `package.json`, `package-lock.json`; `opencode.json` отсутствует. Evidence: `/home/rudra/Projects/ChaT/`, `/home/rudra/Projects/ChaT/.opencode/`, `/home/rudra/Projects/ChaT/opencode.json` [проверить отсутствие].
- Карточка Vault описывает `planning`, `spec-home: docs/specs/`, 9 агентов и отсутствие команд/plugins: `chat-librarian`, `development-manager`, `tea-master`, `chat-reviewer`, `community-architect`, `product-market`, `tea-scientist`, `velisov-steward`, `regeneration-designer`. Evidence: `/home/rudra/Projects/OpenCode-Vault/03-Projects/ChaT.md:38-51`.
- Git status показывает удаление 9 агентов, включая `curator`, которого нет в карточке; `chat-librarian` среди удалённых не указан. Evidence: `/home/rudra/Projects/ChaT` (`git status`).
- Наличие перечисленных в карточке агентов на диске не подтверждено: они удалены незакоммиченно. Evidence: `/home/rudra/Projects/ChaT` (`git status`).
- `docs/specs/` фактически содержит только `README.md`; содержимое README — [проверить]. Evidence: `/home/rudra/Projects/ChaT/docs/specs/`.
- `UNKNOWN: плагины не обнаружены; история ограничена последним коммитом (c206360, `git log -1`)`. Evidence: `/home/rudra/Projects/ChaT/.opencode/`, `/home/rudra/Projects/ChaT` (`git log -1`).

## 4. AndroidOS

- Репозиторий доступен; ветка `main`; последний коммит — `dd48ede` от 2026-10-01, «feat(domain): priority extraction + clarify KIND on low confidence»; status показывает 10 удалённых `.opencode/agents|command` файлов. Evidence: `/home/rudra/Projects/AndroidOS` (`git status`, `git log`).
- Фактические проектные объекты находятся в `.mcode/`: агенты `planner`, `verifier`, `reviewer`, `builder`, `researcher`; команды `android-plan`, `android-verify`, `android-build`, `android-done`, `android-research`. Evidence: `/home/rudra/Projects/AndroidOS/.mcode/agents/`, `/home/rudra/Projects/AndroidOS/.mcode/command/`.
- `AGENTS.md:30-48` задаёт workflow `/spec`, порядок `researcher→builder→reviewer→verifier`, approval перед изменениями, запрет секретов/raw audio/silent profile writes, compile/test/lint gates и lane ownership. Evidence: `/home/rudra/Projects/AndroidOS/AGENTS.md:30-48`.
- Canonical spec — `docs/specs/androidos-return-to-implementation.md` (timestamp 2026-08-30, planned); также есть `docs/specs/README.md`. Evidence: `/home/rudra/Projects/AndroidOS/docs/specs/androidos-return-to-implementation.md`, `/home/rudra/Projects/AndroidOS/docs/specs/README.md`.
- История реализации включает PA MVP skeleton, coordination bridge, recording/STT pipeline, T-one Russian STT, local reminders, encrypted change-bundle sync, entity registry/retention/search/daily plan, rule-based intent classifier, evolution/Jev research и Laya research correction. Evidence: `/home/rudra/Projects/AndroidOS` (`git log/HEAD`).
- `docs/research/evolution-applications.md` описывает Jev как framework [проверить] и кандидатов classification, reminders, Today priorities, UI cards. Evidence: `/home/rudra/Projects/AndroidOS/docs/research/evolution-applications.md`.
- `docs/research/jev-classifier.md` — research, не production; ExtractionEngine/confidence/approval подходят; cloud/privacy/licensing отмечены как риски. Evidence: `/home/rudra/Projects/AndroidOS/docs/research/jev-classifier.md`.
- `docs/research/liya-audit.md` исправляет название на Laya (2026-09-30), подтверждает Apache-2.0, typed decisions и ONNX local path. Evidence: `/home/rudra/Projects/AndroidOS/docs/research/liya-audit.md`.
- `docs/plan-silero-laya-slice.md` описывает provisional Silero punctuation + Laya ExtractionEngine; наличие INT8 ONNX-файлов в `laya/` — [проверить]. Evidence: `/home/rudra/Projects/AndroidOS/docs/plan-silero-laya-slice.md`, `/home/rudra/Projects/AndroidOS/laya/`.
- Карточка остаётся осторожной (`planning`, umbrella/canonical spec); реализация skeleton/STT/reminders/sync/classifier подтверждена. Обновление карточки рекомендуется на следующем аудите. Evidence: `/home/rudra/Projects/OpenCode-Vault/03-Projects/AndroidOS.md:6`, `/home/rudra/Projects/OpenCode-Vault/03-Projects/AndroidOS.md:18`, `/home/rudra/Projects/AndroidOS` (`git log/HEAD`).

## Сводная таблица

| Репо | Доступность | Git state | Кросс-мотивная находка | Объекты подтверждены | Расхождения с карточкой | BLOCKED-пункты |
|---|---|---|---|---|---|---|
| dv-hub | доступен; прямой read-only pass компенсировал permission gate | `main`, sync origin/main, `e803d02`; незакоммиченные D/M/?? | массовые удаления `.opencode/*` | `opencode.json`, specs; `.opencode/` урезан worktree-удалениями | карточка требует актуализации [проверить] | BLOCKED-resolved; [проверить] актуальность карточки |
| dotfiles | доступен | `task/maya-lint-handshake`, `1a8b7c1`; единственный `?? docs/specs/bugfix-proactive-plugin.md` | массовых удалений нет; worktree чистый кроме единственного `??` | 7 agents, команды, 12 plugins, config, ADR | существенных расхождений не выявлено | UNKNOWN; [проверить] содержимое нового spec |
| ChaT | доступен; прямой read-only pass компенсировал permission gate | `main`, sync origin/main, `c206360`; 18 D + 2 ?? | массовые удаления `.opencode/*` | корень, `.opencode/` package-only, карточка | удалены 9 агентов; `curator` не отражён карточкой, `chat-librarian` не в удалениях | BLOCKED-resolved; [проверить] README в `docs/specs/`; отсутствие `opencode.json` |
| AndroidOS | доступен | `main`, `dd48ede`; 10 D | массовые удаления `.opencode/*` | `.mcode` agents/commands, workflow, specs, реализационные следы | карточка осторожнее фактической реализации; `.opencode` удалён, `.mcode` фактически используется | UNKNOWN; [проверить] Jev и INT8 ONNX artifacts |

## UNKNOWN / [проверить]

| Статус | Объект |
|---|---|
| BLOCKED-resolved | Первый researcher-проход dv-hub и ChaT; доступ восстановлен прямым read-only проходом librarian. |
| UNKNOWN | Причина и автор массовых удалений; актуальность карточки dv-hub; содержимое ChaT README и отсутствие `opencode.json`; Jev и INT8 ONNX-файлы AndroidOS. |

- Причина и автор массовых удалений `.opencode/*`: [проверить]. Evidence: соответствующие `git status` и `git log` в `/home/rudra/Projects/dv-hub`, `/home/rudra/Projects/ChaT`, `/home/rudra/Projects/AndroidOS`.
- Актуальность и точное содержание карточки `dv-hub`: [проверить]. Evidence: `/home/rudra/Projects/OpenCode-Vault/03-Projects/dv-hub.md`.
- Содержимое `ChaT/docs/specs/README.md` и отсутствие `ChaT/opencode.json`: [проверить]. Evidence: `/home/rudra/Projects/ChaT/docs/specs/README.md`, `/home/rudra/Projects/ChaT/opencode.json`.
- Jev как framework и наличие INT8 ONNX-файлов в AndroidOS `laya/`: [проверить]. Evidence: `/home/rudra/Projects/AndroidOS/docs/research/evolution-applications.md`, `/home/rudra/Projects/AndroidOS/laya/`.
- Ранее dv-hub/ChaT были частично недоступны researcher из-за permission gate; доступность подтверждена прямым read-only pass librarian с `external_directory: allow`. Evidence: provenance данного отчёта; `/home/rudra/Projects/dv-hub`, `/home/rudra/Projects/ChaT`.

### Scope-clean proof (доказательство read-only(scope))

Операции этой работы по четырём целевым репо были ТОЛЬКО чтением (git log/status/branch/ls/read). Никаких writes/правок/коммитов:

1. **Независимый свидетель до создания draft:** research-проход `ses_eece6127cffez6zTL2sYNmr4Ka` (researcher, 2026-10-07) открыл состояние целевых репо — грязное worktree (массовые D) — ДО создания этого draft. Экспорт сессии машинно-проверяем: `opencode session export ses_eece6127cffez6zTL2sYNmr4Ka`.
   → Изменения целевых репо предшествуют этой работе и принадлежат другим сессиям/потокам (то есть являются объектом находки, а не её продуктом).
   Дополнительно: researcher был заблокирован permission-gate на dv-hub/ChaT (`Permission denied: external_directory`) — это подтверждает read-only ход субагента.
2. **Trip-wire по офисной работе:** сессия «внедрение» (первичная) выполнила по целевым путям только read-команды: `git -C <path> rev-parse/branch/log/status`, `ls`, `grep`, `head`. Ни одна write-операция (edit/write/tag/commit) на эти пути не производилась (письменная заявка scope: route-log append #10, #11).
3. **Baseline snapshot:** состояние worktree каждого репо, зафиксированное в сводной таблице этого draft, ЕСТЬ baseline на момент pass 2026-10-07 (снимки: dv-hub 25 строк status; ChaT 20; AndroidOS D:10+; dotfiles 1 ??). Любое последующее изменение — не этот pass.
4. **Единственный артефакт работы:** `06-Audits/2026-10-07-external-repos-pass-draft.md` (untracked; 06-Audits/ в OpenCode-Vault). Ни один файл в dv-hub/dotfiles/ChaT/AndroidOS не создан/изменён этой работой.
