---
type: Patch Proposal
title: "Патч: глобальный obsidian-servant — доступ к ship-mail (блок письма Служителя)"
description: Точечная правка allowlist для Служителя — доставка писем ship-mail без shell
ssot: false
status: ждёт meta/sysop (dotfiles-зона)
timestamp: 2026-10-26
---

# Патч: dotfiles/opencode-global/.config/opencode/agent/obsidian-servant.md

Инцидент: 10-Deck/drafts/2026-10-25-incident-shell-tool-missing.md
Служитель не может отправлять письма: доставка ship-mail = атомарный
файл в `~/.local/share/ship-mail/inbox/<sid>/`, но глобальный агент
не имеет доступа к этому пути (вольтный слой обновлён, глобальный —
нет; агентские правила приоритетнее).

## Правка (external_directory: добавить 2 строки allow)

```yaml
    "/home/rudra/.local/share/ship-mail/**": allow
    "/home/rudra/.local/bin/**": allow
```

после строки `"/tmp/opencode/**": allow` (сохранить порядок deny
секретов ниже).

## Опционально (если нужен shell для ship-mail.sh/garbage-guard)

В `bash:` перед `"*": deny` добавить:

```yaml
    "~/.local/bin/ship-mail.sh*": allow
    "python3 ~/dotfiles/tools/garbage-guard/guard.py*": allow
    "git add*": allow
    "git commit*": allow
    "git switch*": allow
    "git mv*": allow
```

## Причина (не «хотелось бы»)

Слово владельца 2026-10-25: «всё таки найди способ отправить свои
письма». Прямая доставка письмом = файл в ящике, безопасная операция
(запись в разрешённый каталог). shell-команды — только канальные
утилиты. Опасные паттерны (rm/sudo/ssh/force-push) остаются deny.

## Проверка после патча (для meta/sysop)

1. Перезапустить сессию Служителя.
2. `write` в `~/.local/share/ship-mail/inbox/<свой-sid>/test.md` →
   ожидание: успех (был Permission denied).
3. `ship-mail.sh inbox <sid>` → видит письмо.

## Кому

meta (глобальная инфра) или dotfiles primary (sysop). Служитель сам
править агентские конфиги не может (edit: "*/AGENTS.md": ask + зона).
