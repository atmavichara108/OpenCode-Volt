---
type: project
repo: /home/rudra/dotfiles
spec-home: /home/rudra/dotfiles/docs/specs/
kind: система
stack: shell / GNU Stow / конфиги Manjaro (23 пакета) / OpenCode multi-agent
---
# dotfiles

> **Coordination Bridge FROZEN BY USER (2026-08-30):** T-108/system-ops,
> permission experiments и bridge integration не активировать. Не выполнять root,
> MCP или runtime permission changes. Для отдельной потребности остаётся
> read-only `/sysaudit`; canonical spec: /home/rudra/dotfiles/docs/specs/coordination-bridge-freeze.md.

Операционная система для управления конфигами Manjaro через OpenCode. Мульти-агент v2 + verifier + closed-loop + flush-протокол: пайплайны, субагенты (включая verifier), память и UX-осознанность.

Канонический профиль Max Rudra: `.opencode/memory/user-profile.md`. Глобальный `profile-governor` выдаёт scoped context и проактивно сверяет профиль с Vault/dotfiles/ChaT/AndroidOS только через explicit invocation, hooks, events или scheduled checks; он предлагает diff, но не пишет тихо и не дублирует профиль. Контракт: [[user-profile-contract]].

**Окружение:** Manjaro (Arch-based). Менеджер — **GNU Stow** (23 пакета).
**CI / проверка:** нет (конфиги, не приложение).
**Провайдер:** OpenCode Go; GPT-5.6 Luna для планирования/сборки, DeepSeek Go для аудита и проверок.

## Структура (пакеты Stow)

23 пакета: zsh, nvim, tmux, git, qtile, alacritty, rofi, picom, btop, bat, dunst, htop, lazygit, neofetch, ranger, screenlayout, scripts, systemd, taskwarrior, wal, weathr, x11, xdg.

Скрипты: `stow.sh` (массовый stow), `add-package.sh` (новый пакет).

## Агенты

### Primary (1)
| Агент | Модель | Назначение |
|-------|--------|-----------|
| sysop | opencode-go/gpt-5.6-luna | Оператор-оркестратор Manjaro: анализирует, проектирует, пишет, делегирует субагентам через task |
| profile-governor | opencode-go/gpt-5.6-luna | Проактивное глобальное управление профилем, scoped context, drift review и approval-gated proposals |

### Subagent (dotfiles-local, `.opencode/agent/`)
| Агент | Модель | Назначение |
|-------|--------|-----------|
| planner | opencode-go/gpt-5.6-luna | Стратег/ADR: анализирует, проектирует, код не пишет (был primary) |
| builder | opencode-go/qwen3.7-plus | Строитель конфигов/скриптов/модулей по спеку (был primary) |
| verifier | opencode/deepseek-v4-flash-free | Верификатор применимости (синтаксис, stow dry-run, готовность) |
| qtile-dev | opencode-go/qwen3.7-plus | Qtile-специалист (WM, виджеты, Python) |
| bash-dev | opencode-go/qwen3.7-plus | Bash-специалист (скрипты, автоматизация) |
| util-dev | opencode-go/qwen3.7-plus | Утилиты (макросы, нотификации, rofi) |
| stow-ops | opencode-go/qwen3.7-plus | Операции GNU Stow и миграции |

### Subagent (global, `opencode-global/.config/opencode/agent/`)
| Агент | Модель | Назначение |
|-------|--------|-----------|
| reviewer | linaliapi/deepseek/deepseek-v4-pro | Read-only quality/style/domain reviewer |
| researcher | linaliapi/google/gemini-3.8-flash | Read-only исследование кода/файлов/git/документации |
| meta | opencode-go/gpt-5.6-luna | Правка агентной инфраструктуры OpenCode |
| verifier | opencode-go/glm-5.3-flash | Strict acceptance verifier (PASS/FAIL по DoD) |
| system-audit | opencode-go/glm-5.3-flash | Read-only аудит системы/экосистемы (ранее глобальный `sysop`) |
| system-ops | opencode-go/gpt-5.6-luna | High-risk host apply planner; explicit approval, dry-run/preflight, post-check, rollback |

Консолидация 2026-09-17 (ADR-010, `docs/decisions.md` в dotfiles):
- Один primary `sysop` вместо трёх; planner/builder переведены в subagent.
- Субагенты перенесены из `.opencode/subagent/` → `.opencode/agent/`.
- Глобальный `sysop` переименован в `system-audit` (subagent) — имя не конфликтует.
- Атавизм `think` (grok-build-0.1) удалён; `default_agent` → `sysop`.
- Канон агента — `.md`-frontmatter, `opencode.json` не дублирует определения.

`system-ops` — отдельная global роль для approval-gated high-risk apply, не замена `sysop`. Runtime dispatch, permission merge и root/apply smoke-test не подтверждены (T-108 frozen by user).

`system-audit` — глобальный read-only аудит (изолирован от apply). `sysop` — локальный primary-оркестратор. Разные роли.

## Пайплайны (команды)

| Команда | Пайплайн | Назначение |
|---------|----------|-----------|
| `/sysaudit` | sysop → system-audit | Аудит: пакеты, конфиги, дрейф, сервисы (инспекцию делает system-audit) |
| `system-ops` (named task) | system-audit → sysop plan → system-ops apply → verifier/post-check | Только high-risk host apply после explicit user approval; отдельной slash-команды нет |
| `/script` | sysop → bash-dev → reviewer | Bash-скрипты |
| `/qtile` | sysop → qtile-dev → reviewer | Qtile: конфиги, виджеты, хуки |
| `/util` | sysop → util-dev → reviewer | Утилиты: btop, wal, neofetch |
| `/prompt` | sysop → docs/cheatsheets/ | Чит-шиты, подсказки |
| `/notify` | sysop → util-dev → reviewer | Уведомления (dunst) |
| `/macro` | sysop → util-dev → reviewer | Макросы: sxhkd, rofi-меню |
| `/plugin` | sysop → builder → reviewer | Плагины: nvim, rofi, btop |
| `/loop` | sysop → verifier | Closed-loop: build → verify → fix (автономная итерация) |
| `/flush` | sysop | Флаш-протокол: сброс контекста в файлы перед компакцией |

## Память

- `.opencode/memory/user-profile.md` — кто Rudra, как работает, предпочтения UX
- `.opencode/memory/decisions.md` — реестр ADR
- `docs/cheatsheets/` — шпаргалки для пользователя

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
| [[model-routing]] | 🟡 | временная статическая политика Luna для primary/dev и DeepSeek Go для дешёвых audit/review/research ролей; capability-routing позже |
| [[promo-provider-protocol]] | 🟡 | метод принят; hook planned, не реализован — spec /home/rudra/dotfiles/docs/specs/promo-provider-probe-balance-hook.md (T-144/T-145) |

## Состояние
- [x] репо dotfiles создан (GitHub + локально)
- [x] GNU Stow — менеджер дотфайлов
- [x] OpenCode инициализирован (2026-06-30)
- [x] Мульти-агентная архитектура: 1 primary + субагенты (локал+global)
- [x] 10 пайплайнов-команд (+/loop, /flush)
- [x] Система памяти: user-profile + decisions + cheatsheets
- [x] UX-профиль: все агенты знают для кого работают
- [x] verifier-pattern: verifier subagent (глобальный PASS/FAIL)
- [x] closed-loop формализация: /loop (builder → @verifier)
- [x] memory-management: /flush + формализованный flush-протокол
- [x] opencode-global плагины (2026-09-06, dotfiles-коммит 0e46291): replay-budget.ts (T-135),
  noop-guard.ts (T-136), input-security.ts (T-137) + helpers — порт органов M Code в TUI;
  loading через symlink ~/.config/opencode/plugins/; live hook-fire после рестарта TUI [проверить]
- [ ] первый /sysaudit
- [ ] model-routing (после тестов)
- [ ] system-ops: permission/root smoke-test (T-108) — **FROZEN BY USER; не активировать.** Existing evidence сохраняется; root, MCP и permission experiments не выполнять.

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
- 2026-09-07: P6 порты — 6 плагинов (replay-budget, noop-guard, input-security + helpers) закоммичены в opencode-global (0e46291); smoke 14/14 + 9/9 + 14/14 в волте. 
