---
type: project
repo: /home/rudra/dotfiles
kind: система
stack: shell / GNU Stow / конфиги Manjaro (23 пакета) / OpenCode multi-agent
---
# dotfiles

Операционная система для управления конфигами Manjaro через OpenCode. Мульти-агент v2 + verifier + closed-loop + flush-протокол: пайплайны, субагенты (включая verifier), память и UX-осознанность.

Канонический профиль Max Rudra: `.opencode/memory/user-profile.md`. Глобальный `profile-governor` выдаёт scoped context и проактивно сверяет профиль с Vault/dotfiles/ChaT/AndroidOS только через explicit invocation, hooks, events или scheduled checks; он предлагает diff, но не пишет тихо и не дублирует профиль. Контракт: [[user-profile-contract]].

**Окружение:** Manjaro (Arch-based). Менеджер — **GNU Stow** (23 пакета).
**CI / проверка:** нет (конфиги, не приложение).
**Провайдер:** OpenCode Go; GPT-5.6 Luna для планирования/сборки, DeepSeek Go для аудита и проверок.

## Структура (пакеты Stow)

23 пакета: zsh, nvim, tmux, git, qtile, alacritty, rofi, picom, btop, bat, dunst, htop, lazygit, neofetch, ranger, screenlayout, scripts, systemd, taskwarrior, wal, weathr, x11, xdg.

Скрипты: `stow.sh` (массовый stow), `add-package.sh` (новый пакет).

## Агенты

### Primary (3)
| Агент | Модель | Назначение |
|-------|--------|-----------|
| sysop | opencode-go/deepseek-v4-flash | Инспектор системы (read-only аудит) |
| profile-governor | opencode-go/gpt-5.6-luna | Проактивное глобальное управление профилем, scoped context, drift review и approval-gated proposals |
| planner | opencode-go/gpt-5.6-luna | Архитектор (ADR, планы, дизайн) |
| builder | opencode-go/gpt-5.6-luna | Строитель (конфиги, скрипты, модули) |

### Subagent (8)
| Агент | Модель | Назначение |
|-------|--------|-----------|
| reviewer | opencode-go/deepseek-v4-flash | Ревьюер (PASS/FAIL, безопасность) |
| verifier | opencode-go/deepseek-v4-flash | Верификатор (глобальная проверка контрактов, /loop) |
| think | opencode-go/gpt-5.6-luna | Сложные рассуждения и анализ |
| researcher | opencode-go/deepseek-v4-flash | Read-only исследование кода, истории и документации |
| stow-ops | opencode-go/deepseek-v4-flash | Операции GNU Stow и миграции |
| qtile-dev | opencode-go/gpt-5.6-luna | Qtile-специалист (WM, виджеты, Python) |
| bash-dev | opencode-go/gpt-5.6-luna | Bash-специалист (скрипты, автоматизация) |
| util-dev | opencode-go/gpt-5.6-luna | Утилиты (макросы, нотификации, rofi) |

### Local extension: dotfiles-local
| Агент | Статус | Границы |
|-------|--------|---------|
| system-ops | skeleton создан; runtime/root execution не подтверждены | High-risk host root apply только через explicit approval; `edit`/`task` deny; dangerous operations deny-safe |

`sysop` остаётся read-only инспектором системы. `system-ops` — отдельное локальное
расширение для dotfiles-local, а не замена `sysop` и не global role.

## Пайплайны (команды)

| Команда | Пайплайн | Назначение |
|---------|----------|-----------|
| `/sysaudit` | sysop | Аудит: пакеты, конфиги, дрейф, сервисы |
| `/script` | planner → bash-dev → reviewer | Bash-скрипты |
| `/qtile` | planner → qtile-dev → reviewer | Qtile: конфиги, виджеты, хуки |
| `/util` | planner → util-dev → reviewer | Утилиты: btop, wal, neofetch |
| `/prompt` | builder → docs/cheatsheets/ | Чит-шиты, подсказки |
| `/notify` | util-dev → reviewer | Уведомления (dunst) |
| `/macro` | util-dev → reviewer | Макросы: sxhkd, rofi-меню |
| `/plugin` | builder → reviewer | Плагины: nvim, rofi, btop |
| `/loop` | builder → @verifier | Closed-loop: build → verify → fix (автономная итерация) |
| `/flush` | builder | Флаш-протокол: сброс контекста в файлы перед компакцией |

## Память

- `.opencode/memory/user-profile.md` — кто Rudra, как работает, предпочтения UX
- `.opencode/memory/decisions.md` — реестр ADR
- `docs/cheatsheets/` — шпаргалки для пользователя

## Конфиг (opencode.json)
- `default_agent`: planner
- `model`: opencode-go/gpt-5.6-luna (fallback; роли переопределены в agent-конфигах)
- `lsp`: false
- `edit`: ask, `external_directory`: allow

## Состояние внедрения методов
| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ✅ | `/loop` команда (builder → @verifier), автономная итерация build → verify → fix |
| [[verifier-pattern]] | ✅ | verifier subagent (глобальный), PASS/FAIL верификация контрактов |
| [[context-as-docs]] | ✅ | AGENTS.md + user-profile.md + decisions.md + docs/ |
| [[distill-pattern]] | ✅ | 10 команд-пайплайнов — образец дистилляции (+/loop, /flush) |
| [[memory-management]] | ✅ | .opencode/memory/ + формализованный flush-протокол (`/flush` команда) |
| [[model-routing]] | 🟡 | временная статическая политика Luna для primary/dev и DeepSeek Go для дешёвых audit/review/research ролей; capability-routing позже |

## Состояние
- [x] репо dotfiles создан (GitHub + локально)
- [x] GNU Stow — менеджер дотфайлов
- [x] OpenCode инициализирован (2026-06-30)
- [x] Мульти-агентная архитектура: 3 primary + 5 subagent (+verifier)
- [x] 10 пайплайнов-команд (+/loop, /flush)
- [x] Система памяти: user-profile + decisions + cheatsheets
- [x] UX-профиль: все агенты знают для кого работают
- [x] verifier-pattern: verifier subagent (глобальный PASS/FAIL)
- [x] closed-loop формализация: /loop (builder → @verifier)
- [x] memory-management: /flush + формализованный flush-протокол
- [ ] первый /sysaudit
- [ ] model-routing (после тестов)
- [ ] system-ops: permission/root smoke-test до live evidence (T-108)

## Лог изменений
- 2026-06-26: карточка-план заведена
- 2026-06-29: репо создано
- 2026-06-30 (v1): OpenCode инициализирован — sysop, /sysaudit
- 2026-06-30 (v2): полная архитектура — 7 агентов, 8 пайплайнов, память, UX-профиль
- 2026-07-04 (v3): verifier subagent + /loop + /flush — closed-loop ✅, verifier-pattern ✅, memory-management ✅
- 2026-08-25: зафиксирован dotfiles-local `system-ops`; skeleton создан, runtime/root execution не подтверждены; root apply требует explicit approval, edit/task deny, dangerous operations deny-safe.
