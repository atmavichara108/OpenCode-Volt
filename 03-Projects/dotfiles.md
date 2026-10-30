---
type: project
repo: /home/rudra/dotfiles
spec-home: /home/rudra/dotfiles/docs/specs/
kind: система
stack: shell / GNU Stow / конфиги Manjaro (38 пакетов в stow.sh) / OpenCode multi-agent
---
# dotfiles

> **Coordination Bridge FROZEN BY USER (2026-08-30):** T-108/system-ops,
> permission experiments и bridge integration не активировать. Не выполнять root,
> MCP или runtime permission changes. Для отдельной потребности остаётся
> read-only `/sysaudit`; canonical spec: /home/rudra/dotfiles/docs/specs/coordination-bridge-freeze.md.

Операционная система для управления конфигами Manjaro через OpenCode. Мульти-агент v2 + verifier + closed-loop + flush-протокол: пайплайны, субагенты (включая verifier), память и UX-осознанность.

Канонический профиль Max Rudra: `.opencode/memory/user-profile.md`. Глобальный `profile-governor` выдаёт scoped context и проактивно сверяет профиль с Vault/dotfiles/ChaT/AndroidOS только через explicit invocation, hooks, events или scheduled checks; он предлагает diff, но не пишет тихо и не дублирует профиль. Контракт: [[user-profile-contract]].
**Статус 2026-10-29:** файла агента нет (ни локально, ни глобально) — роль жива в контракте и карточках. Слово владельца: не удалять; отправлен на доработку в УАС с обсуждением напрямую с владельцем (письмо 29.10). Не считать активным агентом до восстановления.

**Окружение:** Manjaro (Arch-based). Менеджер — **GNU Stow**: `stow.sh` ведёт **38 пакетов** (на диске 47 каталогов, включая служебные docs/tools/04-Memory). Пакеты: zsh, p10k, tmux, alacritty, nvim, qtile, picom, rofi, dunst, x11, gtk, ranger, git, lazygit, htop, btop, bat, neofetch, shell, wal, wallust, flameshot, copyq, nitrogen, thefuck, weathr, screenlayout, taskwarrior, task-tools, calcurse, xdg, environment.d, systemd, proxyctl, syncthing, scripts, helpreg, opencode-global, mcode.
**CI / проверка:** нет (конфиги, не приложение).
**Провайдер (сверка 2026-10-29):** рабочие модели — локальные: `amd-radeon/DeepSeek-V4.1-Flash`, `amd-radeon/GLM-5.3-Flash`, `nvidia/meta/muse-glimmer-30b`, primary — `opencode/muse-spark-1.3-contributor-free`; OpenCode Go — запасной слой (прежняя схема «Luna для plan/dev, DeepSeek Go для audit» больше не действует).

## Структура (пакеты Stow)

38 пакетов в `stow.sh` (полный список — выше в «Окружении»); на диске 47
каталогов — излишек служебный (docs, tools, 04-Memory и др.).
Раньше карточка числила 23 пакета — сверка 2026-10-29 обновила.

Скрипты: `stow.sh` (массовый stow), `add-package.sh` (новый пакет).
Дополнительно: `scripts/` (ai-syshelp.py, git-prune-branches.sh, tests/),
`tools/` — 19 инструментов (см. «Живые подсистемы»).

## Агенты

### Primary (dotfiles-local)
| Агент | Модель (факт, 2026-10-29) | Назначение |
|-------|--------|-----------|
| sysop | opencode/muse-spark-1.3-contributor-free | Оператор-оркестратор Manjaro: единственный primary, пишет сам, делегирует через task |

> **profile-governor** — бывший primary-роль профиля; файла агента нет,
> роль на доработке в УАС по слову владельца (см. выше). Не удалять.

### Subagent (dotfiles-local, `.opencode/agent/`) — 6
| Агент | Модель (факт) | Назначение |
|-------|--------|-----------|
| bash-dev | amd-radeon/DeepSeek-V4.1-Flash | Bash-скрипты, автоматизация |
| qtile-dev | amd-radeon/DeepSeek-V4.1-Flash | Qtile (WM, виджеты, Python) |
| util-dev | amd-radeon/DeepSeek-V4.1-Flash | Утилиты (макросы, нотификации, rofi) |
| obsidian-plugin-dev | amd-radeon/DeepSeek-V4.1-Flash | Разработка плагинов Obsidian (зона plugin-dev; ssh* = ask по слову владельца 10.29) |
| stow-ops | amd-radeon/GLM-5.3-Flash | Операции GNU Stow и миграции |
| verifier | nvidia/meta/muse-glimmer-30b | Верификатор применимости (синтаксис, stow dry-run) |

> planner и builder удалены (были субагентами до консолидации; файлы
> отсутствуют — сверка 2026-10-29). Их функции — у sysop и глобальных
> plan/build.

### Subagent (global, `opencode-global/.config/opencode/agent/`) — 11
| Агент | Модель (факт) | Назначение |
|-------|--------|-----------|
| meta | amd-radeon/GLM-5.3-Flash | Правка агентной инфраструктуры OpenCode |
| reviewer | amd-radeon/GLM-5.3-Flash | Read-only quality/style/domain reviewer |
| researcher | opencode-go/glm-5.3-flash | Read-only исследование кода/файлов/git/документации |
| verifier | nvidia/meta/muse-glimmer-30b | Strict acceptance verifier (PASS/FAIL по DoD) |
| system-audit | amd-radeon/GLM-5.3-Flash | Read-only аудит системы/экосистемы (ранее глобальный `sysop`) |
| system-ops | amd-radeon/DeepSeek-V4.1-Flash | High-risk host apply planner; explicit approval, dry-run, rollback |
| build | (без пина) | Глобальный исполнитель-строитель |
| plan | (без пина) | Глобальный планировщик |
| emergency | (без пина) | Аварийный контур |
| obsidian-servant | amd-radeon/GLM-5.3-Flash | Служитель Обсидиан (Р-021) |
| tree-cop | anymodel/cx/gpt-5.6-sol | Коп чистоты дерева и выкладки ветки |

> **Сноска (сверка 2026-10-29):** канон пинов — `model:` во frontmatter
> `.md` каждого агента (меню `/agents` правит их же); `opencode.json`
> определений не дублирует. Значения меняются часто — источник правды
> файл агента, не карточка.

Консолидация 2026-09-17 (ADR-010, `docs/decisions.md` в dotfiles):
- Один primary `sysop` вместо трёх; planner/builder переведены в subagent.
- Субагенты перенесены из `.opencode/subagent/` → `.opencode/agent/`.
- Глобальный `sysop` переименован в `system-audit` (subagent) — имя не конфликтует.
- Атавизм `think` (grok-build-0.1) удалён; `default_agent` → `sysop`.
- Канон агента — `.md`-frontmatter, `opencode.json` не дублирует определения.

`system-ops` — отдельная global роль для approval-gated high-risk apply, не замена `sysop`. Runtime dispatch, permission merge и root/apply smoke-test не подтверждены (T-108 frozen by user).

`system-audit` — глобальный read-only аудит (изолирован от apply). `sysop` — локальный primary-оркестратор. Разные роли.

## Пайплайны (команды) — 19 в `.opencode/command/` (сверка 2026-10-29)

| Команда | Пайплайн | Назначение |
|---------|----------|-----------|
| `/sysaudit` | sysop → system-audit | Аудит: пакеты, конфиги, дрейф, сервисы (инспекцию делает system-audit) |
| `system-ops` (named task) | system-audit → sysop plan → system-ops apply → verifier/post-check | Только high-risk host apply после explicit user approval; отдельной slash-команды нет |
| `/script` | sysop → bash-dev → reviewer | Bash-скрипты |
| `/qtile` | sysop → qtile-dev → reviewer | Qtile: конфиги, виджеты, хуки |
| `/util` | sysop → util-dev → reviewer | Утилиты: btop, wal, neofetch |
| `/prompt` | sysop → docs/cheatsheets/ | Чит-шиты, подсказки. Баг 29.10 устранён УАС (коммит 376d241: каталог восстановлен с .gitkeep) |
| `/notify` | sysop → util-dev → reviewer | Уведомления (dunst) |
| `/macro` | sysop → util-dev → reviewer | Макросы: sxhkd, rofi-меню |
| `/plugin` | sysop → builder → reviewer | Плагины: nvim, rofi, btop |
| `/loop` | sysop → verifier | Closed-loop: build → verify → fix (автономная итерация) |
| `/flush` | sysop | Флаш-протокол: сброс контекста в файлы перед компакцией |
| `/bugfix` `/fix` | sysop → исполнитель → verifier | Инцидент-фикс на лету (метод incident-fix) |
| `/inbox` | sysop | Разбор входящих |
| `/someday` | sysop | Отложенное |
| `/stow` | sysop → stow-ops | Операции Stow |
| `/task` | sysop | Постановка задачи |
| `/test` | sysop | Прогон тестов (scripts/tests) |
| `/vflight` | sysop | Виртуальный прогон/проверка |
| `/vpn` | sysop → proxyctl | VPN/прокси |

Глобальные команды (`opencode-global/.config/opencode/command/`, 11):
agents · branch · bridge · done · dream · flush · loop · prov · resume ·
ship · spec (+ дубли branch/ship в `commands/` — [проверить] какой слой читает ядро V2).

## Память

- `.opencode/memory/user-profile.md` — кто Rudra, как работает, предпочтения UX
- `.opencode/memory/decisions.md` — реестр ADR (до ADR-023, сверка 2026-10-29)
- `.opencode/memory/` — также: glossary.md · inbox.md · orchestration.md ·
  registry.md · agent-lifecycle.jsonl · session-reports/ · research/
- ~~`docs/cheatsheets/`~~ — восстановлен УАС 29.10 (коммит 376d241), снова живой
- Живые docs в `docs/`: 15 файлов (runbook, runbook-proactive, memory-contract,
  engines, external-interfaces, roadmap, techdebt, deferred, decisions,
  pipelines-phase0, incident-record-template и аудиты)

## Инструменты (`tools/` — 18, сверка 2026-10-29)

agent-perms · agent-yaml-check.py · garbage-guard · git-agent ·
homeostasis · image-read · key-rotator (незакоммичен) · maya-lint ·
model-watch · orch-guard · owner-gate · peer-comms · peers ·
provider-keys · rudrakshas · ship-mail · tg-profile-doctor.py ·
vault-frontmatter

## Живые подсистемы (окт 2026)

**TG-мосты + Maya (срез 29.10)** — ветка `task/maya-reshoe-20261029`.
Сторонние systemd-юниты: `portal-tg-guard.service` (Капитанский портал),
`tg-guard.service`, `serp-tg-guard.service`, `dv-tg-guard.service`. Скрипты
`tg-reshoe`, `tg-whoami` — переобувка профилей TG-мостов на sender
`@AllIsMaya` (слово владельца 29.10). Канон портала §6, chat-scope,
«зов только от владельца»; 586 коммитов за 30 дней — репо активен.

**Инструменты Корабля (tools/)** — 18 шт, см. выше; ключевые:
`ship-mail`, `owner-gate`, `peer-comms`, `garbage-guard`, `maya-lint`,
`orch-guard`, `homeostasis`.

**Ролевые стандарты** — канонизированы 29.10 (коммит c9c3c48): стандарт
смотрителя (Р-Д-003) и стандарт представителя (Р-Д-001..002); ИС→ИЦ
вымышленное ведомство вычищено.

## Глобальные плагины opencode-global — 16 (сверка 2026-10-29)

branch-auto · bugfix-capture · command-observer · decision-queue-hook ·
fix-tool-schema · image-read · input-security · leak-guard ·
main-protector · orch-guard · replay-budget · session-flush ·
session-restart-nudge · spec-write-routing · telemetry · tree-hygiene
(+ skill `tree-hygiene`). Loading — symlink `~/.config/opencode/plugins`
→ пакет (проверен 2026-10-29). Примечание: noop-guard упразднён 2026-09-23.

## Конфиг (opencode.json)
- `default_agent`: sysop
- `model`: opencode/deepseek-v4-flash-free (fallback)
- `lsp`: true
- `edit`: ask, `external_directory`: allow
- Канон агентов — `.md`-frontmatter; agent-блоки ядра (sysop/planner/builder/think) удалены из json

## Состояние внедрения методов
| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ✅ | `/loop` команда (builder → @verifier), автономная итерация build → verify → fix |
| [[verifier-pattern]] | ✅ | verifier subagent (глобальный), PASS/FAIL верификация контрактов |
| [[context-as-docs]] | ✅ | AGENTS.md + user-profile.md + decisions.md + docs/ |
| [[distill-pattern]] | ✅ | 10 команд-пайплайнов — образец дистилляции (+/loop, /flush) |
| [[memory-management]] | ✅ | .opencode/memory/ + формализованный flush-протокол (`/flush` команда) |
| [[model-routing]] | 🟡 | статическая политика пинов во frontmatter (локальные модели: DeepSeek-V4.1-Flash / GLM-5.3-Flash / Muse-Spark / Muse-Glimmer). Переход на capability-routing запланирован. |
| [[promo-provider-protocol]] | ✅ | hook реализован; спека `promo-provider-probe-balance-hook.md` переехала в `docs/specs/done/` (сверка 2026-10-29). |

## Состояние
- [x] репо dotfiles создан (GitHub + локально)
- [x] GNU Stow — менеджер дотфайлов
- [x] OpenCode инициализирован (2026-06-30)
- [x] Мульти-агентная архитектура: 1 primary + субагенты (локал+global)
- [x] 19 пайплайнов-команд (.opencode/command/, см. таблицу выше)
- [x] Система памяти: user-profile + decisions + glossary + inbox + orchestration + registry + agent-lifecycle.jsonl + session-reports
- [x] UX-профиль: все агенты знают для кого работают
- [x] verifier-pattern: verifier subagent (глобальный PASS/FAIL)
- [x] closed-loop формализация: /loop (builder → @verifier)
- [x] memory-management: /flush + формализованный flush-протокол
- [x] opencode-global плагины (2026-09-06, dotfiles-коммит 0e46291): replay-budget.ts (T-135),
  input-security.ts (T-137) + helpers — порт органов M Code в TUI; noop-guard.ts (T-136)
  упразднён 2026-09-23. loading через symlink ~/.config/opencode/plugins/; live hook-fire
  после рестарта TUI [проверить]
- [ ] первый /sysaudit
- [ ] model-routing (после тестов)
- [ ] system-ops: permission/root smoke-test (T-108) — **FROZEN BY USER; не активировать.** Existing evidence сохраняется; root, MCP и permission experiments не выполнять.

## Наблюдение за git (сверка 2026-10-29)

- ветка: `task/maya-reshoe-20261029` (локальная рабочая); `main` синхронен с origin — 0 коммитов впереди.
- активность: 586 коммитов за последние 30 дней — репо самый горячий в экосистеме.
- untracked: `tools/key-rotator/` — чужая незакоммиченная работа, не трогать.
- последние события: TG-переобувка на @AllIsMaya (29.10), канонизация стандартов смотрителя/представителя (29.10).

## Лог изменений
- 2026-06-26: карточка-план заведена
- 2026-06-29: репо создано
- 2026-06-30 (v1): OpenCode инициализирован — sysop, /sysaudit
- 2026-06-30 (v2): полная архитектура — 7 агентов, 8 пайплайнов, память, UX-профиль
- 2026-07-04 (v3): verifier subagent + /loop + /flush — closed-loop ✅, verifier-pattern ✅, memory-management ✅
- 2026-08-29: `system-ops` зарегистрирован как global subagent; добавлен scoped evidence-write protocol без broad edit allow; runtime dispatch/effective permissions/root apply не подтверждены, T-108 остаётся BLOCKED.
- 2026-08-29: protocol report T-108 зафиксировал в named session `ses_fb0ee381fffeHfjxggBF0CXpm3/` отказ edit для evidence и отказ external_directory для task/handoff; fallback не использовался. Статический merged config правила содержит, но runtime application не доказан; T-108 остаётся BLOCKED.
- 2026-08-30: probable root cause identified: canonical scalar `edit: deny` overrode project scoped object; prompt policy is now object deny-default with evidence-only edit and scoped task/handoff/evidence external reads. Fresh-session runtime merge/live evidence pending; T-108 remains BLOCKED.
- 2026-08-30: Coordination Bridge и T-108/system-ops frozen by user; bridge integration не продолжается, root/MCP/permission experiments не выполнять. `/sysaudit` остаётся отдельным read-only workflow.
- 2026-09-07: P6 порты — плагины replay-budget, input-security + helpers закоммичены в opencode-global (0e46291); smoke 14/14 + 14/14 в волте (noop-guard упразднён 2026-09-23). 
- 2026-10-13: спеки сети в `docs/specs/`: `ship-research-network.md` (kind: contract — карта компетенций локаций Корабля, правило перенаправления, два дерева навыков, research-first; +7 правок ревью sysop) и `engineering-center-location.md` (kind: task — Инженерный Центр как локация-сессия сети, закрепление существующего). Обе в main: спека сети `76596c9`+merge `38af7ea`, центр cherry-pick `22a483a`. Реестр исследований по локациям — `06-Audits/2026-10-13-ship-research-registry.md` (в волте). 
- 2026-10-13 (вечер): Ability Lab spec — оформление локации-сессии (kind: task, L1–L6, пайплайн «Институт → Лаборатория → доказанное → решение Rudra → Инженерный Центр»); reviewer issues→исправлены, verifier PASS 9/9; в main `6b8b6f7`+`54c774c`, запушено в origin. Живой тест правила перенаправления §4 пройден (sysop → Ability Lab).
- 2026-10-13 (ночь): approval Rudra — сеть approved; Инженерный Центр и Ability Lab → docs/specs/done/. Новые локации: Институт (7fef7eb+9ac54b5) и Библиотека/NotebookLM (fe77002+9ac54b5), verifier PASS 15/15, запушены в origin.
- 2026-10-29: сверка карточки↔репо (Служитель, по поручению владельца): обновлён stack (38 пакетов), переписка агентов (sysop/6 локал/11 глобал, профиль-губернатор — на доработке в УАС, не удалять), 19 команд, память без phantom cheatsheets, tools 18, плагины 16, promo-provider ✅, стандарты смотрителя/представителя канонизированы, TG-мосты Maya; баг /prompt передан на фикс в УАС (письмо 29.10).
