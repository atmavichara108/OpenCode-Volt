---
type: Reference
title: Почтовый хаб re-search.wiki — канон и фактура
timestamp: 2026-10-24
status: active
ssot: true
---
# Почтовый хаб re-search.wiki — канон (root document)

## Канон-адрес владельца (единственный, без исключений)

**`rudra108@re-search.wiki`**

— адреса `maks@re-search.wiki` НЕ СУЩЕСТВУЕТ и не существовало: он был ошибкой
в хендоффе ЦУ (v0.2/v0.3), исправленной ИЦ 2026-10-23 (баг признан ИЦ:
«Resend сам подставлял владельца аккаунта, поэтому письма доходили»).
Ссылки на maks@ в любых шаблонах/доках — удалить при касании (правило
при-касании, Р-022).

## Приём (входящие)

```
rudra108@re-search.wiki
  → Namecheap Email Forwarding
    → msivyhin@gmail.com (Gmail)
      → mbsync (IMAP: imap.gmail.com) → ~/Mail/re-search.wiki/
```

- Синхронизация: `mail-hub-sync` (mbsync, `~/.mbsyncrc`).
- Подтверждено живым кругом (ИЦ, 2026-10-23): письмо U=612 прошло полный круг,
  заголовки X-Original-To=rudra108@re-search.wiki, SPF pass, DKIM есть.

## Отправка (исходящие)

- `msmtp` → `smtp.resend.com:465`, FROM = `rudra108@re-search.wiki`
  (`~/.msmtprc`), скрипт `~/.local/bin/mail-hub-send` (stdin, RFC 822).
- «Отправлено» = код 250. `journal sent ≠ delivered` — проверять доставку.
- Outbox: `~/Mail/re-search.wiki-outbox/`, флеш: `mail-hub-outbox-flush`.

## Секреты (вне репо)

- `~/.secrets/mail-hub/` — `imap.pass` (пароль приложения Gmail) и
  `resend.apikey` (ключ Resend). В репозитории — никогда.
- Внешние инструменты (Ворота владельца, `owner-gate`): события
  `mail-hub.secret` и `mail-hub.dns` — если нужен новый ключ или DNS-запись.

## Живой статус (2026-10-23, верификация ИЦ)

- Приём: 610+ писем в локальном архиве.
- Отправка: подтверждена 250 + обратная доставка (end-to-end живой).
