---
type: Incident
title: "Сбой: инструмент shell/bash недоступен после рестарта сессии Служителя"
description: symptom/repro/root cause/fix/evidence — инцидент инфраструктуры инструментов
ssot: false
status: закрыт 2026-10-26 00:58 (фикс policies 5a13804/c9e49f2; shell работает, подтверждено эксплуатацией)
timestamp: 2026-10-25
---

# Инцидент: shell/bash tool недоступен (Служитель Обсидиан)

## Symptom
После рестарта сессии (конфиги обновились: ship-mail canon Р-028,
obsidian-servant.md) инструмент `shell`/`bash` **не экспонируется** в
каталоге инструментов Служителя. Раньше (до рестарта) shell работал
и использовался для peer-comms letter.sh, garbage-guard, git, ship-mail.sh.

## Repro
Любой вызов shell/bash в текущей сессии →
`No tool named "shell" is currently available` /
`Unknown tool 'bash'`. Попытка через `execute` (Code Mode) → tools
`shell`/`bash` отсутствуют в каталоге. `fetch` к `file://` не работает
(«fetch cannot be used for filesystem access»).

## Root cause (найден 2026-10-26, подтверждён чтением обоих файлов)
Сессия Служителя работает под **глобальным** слоем агента
(`dotfiles/opencode-global/.config/opencode/agent/obsidian-servant.md`),
а правки с доступом к почте зашли в **вольтный** файл
(`OpenCode-Vault/.opencode/agent/obsidian-servant.md`):
- вольтный файл содержит `~/.local/bin/**` и `~/.local/share/ship-mail/**`
  (allow) и `bash: "*": allow` — обновлён correctly;
- глобальный файл этих строк **не содержит**: external_directory
  `*`: deny без ship-mail/local/bin, bash — только read-only allowlist;
- агентские правила имеют приоритет (AGENTS.md: «agent rules take
  precedence») → доставка писем физически закрыта, shell-инструмент
  с рабочими командами недоступен.

Это и есть «не те инструкции» из слова владельца: рестарт подхватил
глобальный слой, а почвенный апдейт уехал не в тот файл.

## Fix (точный, минимальный)
В глобальный obsidian-servant.md добавить в external_directory.allow:
`/home/rudra/.local/share/ship-mail/**` и `/home/rudra/.local/bin/**`;
в bash.allow — `~/.local/bin/ship-mail.sh*`, `git add*`, `git commit*`,
`git switch*`, `git rm*` (rm — ask по runtime-гейту).
Готовый патч-файл: 10-Deck/drafts/2026-10-26-patch-global-servant.md.
Зона исполнения — meta/sysop (dotfiles), не Служитель.

## Fix (что нужно)
Проверить opencode.jsonc (глобальный, dotfiles) и agent file
obsidian-servant.md — разрешить инструмент bash/shell для Служителя,
либо добавить allowlist-паттерн, который OpenCode воспринимает как
«инструмент разрешён». Или переключить на ship-mail.sh, который требует
bash anyway (тот же блокер).

## Workaround (применён)
Владелец отправляет письмо ЦУ (roadmap A/B/C + 6 протоколов) вручную
одной командой:
```
~/.local/bin/ship-mail.sh send --to ses_eceb23a71ffeJO9QnFou8VngZC \
  --from ses_ea02cc0d8ffeFXUsAX9UeQWs2D \
  --title "Рубка управления — roadmap A/B/C и протоколы перед апрувом" \
  --file ~/Projects/OpenCode-Vault/10-Deck/drafts/2026-10-25-protocols-before-approval.md
```
Файл письма на диске готов, чистый.

## Evidence
- Файл письма: 10-Deck/drafts/2026-10-25-protocols-before-approval.md
- Receipts: ~/.local/state/opencode/mail/receipts-out.jsonl
  (c91be0e9 delivered to ЦУ — концепты рубки)
- Инцидент канала (79 писем из 379 легли как "sent" при отказе) —
  УАС, fix-peer-mail-20261024 в работе.

## Маршрут
Инфраструктура инструментов → **dotfiles primary (sysop)**. Служитель
не может сам чинить (task: deny, bash: deny). Инцидент записан здесь
для передачи sysop'у.

## Статус
Открыт. Workaround применён (письмо не отправлен, файл на диске).
