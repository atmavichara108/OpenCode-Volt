---
type: project
repo: /home/rudra/dotfiles
kind: система
stack: shell / GNU Stow / конфиги Manjaro (23 пакета) / OpenCode multi-agent
---
# dotfiles

Операционная система для управления конфигами Manjaro через OpenCode. Мульти-агентная архитектура с пайплайнами, субагентами, памятью и UX-осознанностью.

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

### Subagent (4)
| Агент | Модель | Назначение |
|-------|--------|-----------|
| reviewer | deepseek-v4-flash-free | Ревьюер (PASS/FAIL, безопасность) |
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
| [[closed-loop]] | 🟡 | Пайплайны с reviewer (PASS/FAIL) — зачатки closed-loop |
| [[verifier-pattern]] | 🟡 | reviewer с PASS/FAIL вердиктом, но не глобальный |
| [[context-as-docs]] | ✅ | AGENTS.md + user-profile.md + decisions.md + docs/ |
| [[distill-pattern]] | ✅ | 8 команд-пайплайнов — образец дистилляции |
| [[memory-management]] | 🟡 | .opencode/memory/ есть, flush-протокол не формализован |
| [[model-routing]] | ➖ | все на DeepSeek (тесты), роутинг позже |

## Состояние
- [x] репо dotfiles создан (GitHub + локально)
- [x] GNU Stow — менеджер дотфайлов
- [x] OpenCode инициализирован (2026-06-30)
- [x] Мульти-агентная архитектура: 3 primary + 4 subagent
- [x] 8 пайплайнов-команд
- [x] Система памяти: user-profile + decisions + cheatsheets
- [x] UX-профиль: все агенты знают для кого работают
- [ ] первый /sysaudit
- [ ] model-routing (после тестов)
- [ ] closed-loop формализация

## Лог изменений
- 2026-06-26: карточка-план заведена
- 2026-06-29: репо создано
- 2026-06-30 (v1): OpenCode инициализирован — sysop, /sysaudit
- 2026-06-30 (v2): полная архитектура — 7 агентов, 8 пайплайнов, память, UX-профиль
