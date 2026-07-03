---
type: project
repo: /home/rudra/dotfiles
kind: система
stack: shell / GNU Stow / конфиги Manjaro (23 пакета) / OpenCode multi-agent
---
# dotfiles

Операционная система для управления конфигами Manjaro через OpenCode. Мульти-агент v2 + verifier + closed-loop + flush-протокол: пайплайны, субагенты (включая verifier), память и UX-осознанность.

**Окружение:** Manjaro (Arch-based). Менеджер — **GNU Stow** (23 пакета).
**CI / проверка:** нет (конфиги, не приложение).
**Провайдер:** OpenCode Zen, все агенты на `opencode/deepseek-v4-flash-free` (тесты)

## Структура (пакеты Stow)

23 пакета: zsh, nvim, tmux, git, qtile, alacritty, rofi, picom, btop, bat, dunst, htop, lazygit, neofetch, ranger, screenlayout, scripts, systemd, taskwarrior, wal, weathr, x11, xdg.

Скрипты: `stow.sh` (массовый stow), `add-package.sh` (новый пакет).

## Агенты

### Primary (3)
| Агент | Модель | Назначение |
|-------|--------|-----------|
| sysop | deepseek-v4-flash-free | Инспектор системы (read-only аудит) |
| planner | deepseek-v4-flash-free | Архитектор (ADR, планы, дизайн) |
| builder | deepseek-v4-flash-free | Строитель (конфиги, скрипты, модули) |

### Subagent (5)
| Агент | Модель | Назначение |
|-------|--------|-----------|
| reviewer | deepseek-v4-flash-free | Ревьюер (PASS/FAIL, безопасность) |
| verifier | deepseek-v4-flash-free | Верификатор (глобальная проверка контрактов, /loop) |
| qtile-dev | deepseek-v4-flash-free | Qtile-специалист (WM, виджеты, Python) |
| bash-dev | deepseek-v4-flash-free | Bash-специалист (скрипты, автоматизация) |
| util-dev | deepseek-v4-flash-free | Утилиты (макросы, нотификации, rofi) |

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
- `model`: opencode/deepseek-v4-flash-free (все агенты)
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
| [[model-routing]] | ➖ | все на DeepSeek (тесты), роутинг позже |

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

## Лог изменений
- 2026-06-26: карточка-план заведена
- 2026-06-29: репо создано
- 2026-06-30 (v1): OpenCode инициализирован — sysop, /sysaudit
- 2026-06-30 (v2): полная архитектура — 7 агентов, 8 пайплайнов, память, UX-профиль
- 2026-07-04 (v3): verifier subagent + /loop + /flush — closed-loop ✅, verifier-pattern ✅, memory-management ✅
