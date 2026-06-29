---
type: project
repo: /home/rudra/dotfiles
kind: система
stack: shell / GNU Stow / конфиги Manjaro (zsh, nvim, tmux, qtile, alacritty, git...)
---
# dotfiles

Точка входа в систему через интерфейс OpenCode. Управление конфигами Manjaro + аудит установленного софта.

**Окружение:** Manjaro (Arch-based). Менеджер дотфайлов — **GNU Stow**.
**CI / проверка:** нет (это конфиги, не приложение).
**Провайдер:** OpenCode Zen, модель `opencode/deepseek-v4-flash-free`

## Структура (пакеты Stow)

| Пакет | Что конфигурит |
|-------|---------------|
| zsh | .zshrc, p10k, shell aliases |
| nvim | Neovim конфиги |
| tmux | .tmux.conf + TPM |
| git | .gitconfig |
| qtile | WM конфиги |
| alacritty | терминал |
| rofi | лаунчер |
| picom | композитор |
| btop | мониторинг |
| bat | cat replacement |
| dunst | уведомления |
| htop | процесс-монитор |
| lazygit | TUI git |
| neofetch | системная информация |
| ranger | файловый менеджер |
| screenlayout | раскладки экранов |
| scripts | пользовательские скрипты |
| systemd | юниты пользователя |
| taskwarrior | task manager |
| wal | цветовые схемы |
| weathr | виджет погоды |
| x11 | X-конфиги |
| xdg | mimeapps, user-dirs |

> 23 пакета конфигов. Скрипты: `stow.sh` (массовый stow), `add-package.sh` (новый пакет).

## Агенты (.opencode/agent/)

| Агент | Mode | Модель | Назначение |
|-------|------|--------|-----------|
| sysop | primary | deepseek-v4-flash-free | Системный оператор: инспекция, аудит, предложения |

### sysop — права и ограничения
- `external_directory: allow` — читает всю систему ($HOME, /etc, /var)
- `edit: deny` — **не меняет** конфиги, только предлагает текстом
- bash whitelist: ls, cat, grep, find, pacman -Q*, which, systemctl status, stow -n, uname, hostnamectl, df, free, ps, du, lsblk, ip, ss
- bash deny: rm, sudo, pacman -S/R, yay, paru, systemctl start/stop/restart, chmod, chown, mkfs, mount
- **НИКОГДА** не ставит/удаляет пакеты и не правит /etc — только предлагает команды текстом

## Команды (.opencode/command/)

`/sysaudit` — полный аудит системы: пакеты, конфиги вне репо, дрейф, сервисы

## Конфиг (opencode.json)
- `default_agent`: sysop
- `model`: opencode/deepseek-v4-flash-free
- `lsp`: false
- `edit`: ask (спросить перед изменением)
- `external_directory`: allow

## Состояние внедрения методов
| Метод | Статус | Основание |
|-------|--------|-----------|
| [[closed-loop]] | ➖ | не применимо к конфигам |
| [[verifier-pattern]] | ➖ | не применимо |
| [[context-as-docs]] | 🟡 | AGENTS.md есть, docs/ нет |
| [[distill-pattern]] | 🟡 | 1 команда (/sysaudit), можно расширить |
| [[memory-management]] | ❌ | нет плагинов компакции |
| [[model-routing]] | ➖ | один агент, роутинг не нужен |

## Состояние
- [x] репо dotfiles создан (GitHub + локально)
- [x] GNU Stow — менеджер дотфайлов
- [x] OpenCode инициализирован (2026-06-30)
- [x] sysop агент создан
- [x] команда /sysaudit создана
- [x] AGENTS.md — правила и конвенции
- [ ] первый /sysaudit
- [ ] добавить docs/ с описанием архитектуры

## Лог изменений
- 2026-06-26: карточка-план заведена
- 2026-06-29: обновлён repo path, репо создано
- 2026-06-30: OpenCode инициализирован — sysop, /sysaudit, AGENTS.md, opencode.json
