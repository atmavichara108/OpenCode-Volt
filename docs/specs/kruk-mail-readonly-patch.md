---
type: Spec
kind: task
project: mail-hub
title: Патч read-only кусков окон КРУК в пульт (ночь Р-077)
status: accepted (вердикт ЦУ 2026-11-07; восстановлено из mail-hub 8e8da41 — сторона волта не была влита, запись приёмки исправлена)
timestamp: 2026-11-04
related:
  - docs/specs/mail-hub-kruk-window.md (основная спека окон, verifier PASS)
  - пульт: OpenCode-Vault/tools/ecosystem-map (ветка task/kruk-mail-readonly-20261104, worktree)
---
# Патч read-only кусков окон КРУК (ночь Р-077)

## Что сделано (пульт-сторона, ветка task/kruk-mail-readonly-20261104, не смержена)

1. **actions.py**: read-only ops `mail-inbox` (Global Inbox: непрочитанные
   ведомств — прямая шина ship-mail, Р-028) и `mail-list` (список Maildir);
   вызывают `bin/mail-hub` с ЧИСТЫМ env (без секретов владельца — барьер 3
   §3.1F ship-спеки); таймаут 30с; JSON-контракт {"ok":...}.
2. **pipboy.py**: whitelist += mail-inbox, mail-list (read-only — GET
   корректен); digest: + лёгкий файл счётчиков `~/.local/state/mail-hub/
   mail-counters.json` (НЕ весь Maildir — барьер 1).
3. **app/modules/MailHubModule.js + GlobalInboxModule.js**: два read-only
   тайла (список/счётчики/свежайшее); отправки в них НЕТ (кусок (г) — по
   Воротам, отдельным куском).
4. **app/core/App.js**: модули зарегистрированы; **Workspace.js**: профиль
   «Mail» (mailhub + globalinbox + terminal).
5. **bin/mail-hub (дом хаба)**: cmd_inbox пишет mail-counters.json после
   каждого прогона → SSE пульта видит живость почты (без демонов).

## Границы ночи (по мандату ЦУ)

- Без Ворот и без отправки: кусок (г) «ответ» — отдельным куском после
  живой приёмки (H1: kruk.mail.send зарегистрирован 0b265e1; H2: X-Actor +
  senders.jsonl — реализованы).
- Ничего в main не смержено: пульт-ветка + эта ветка — на приёмке ЦУ.
- Секреты: env чистый, в тайлах только метаданные.
