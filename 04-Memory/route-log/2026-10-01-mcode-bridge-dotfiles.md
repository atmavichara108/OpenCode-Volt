---
type: Route Log
title: M Code↔OpenCode bridge — делегация dotfiles
date: 2026-10-01
status: ROUTED (handoff pending dotfiles session)
tags: [routing, bridge, mcode, opencode, dotfiles, infra]
---
# Route — bridge-endpoint M Code↔OpenCode

- **route_id:** `mcode-bridge->dotfiles:service+wrapper:2026-10-01`
- **status:** `ROUTED` — handoff подготовлен, dispatch в dotfiles-сессии
- **task:** управляемый OpenCode v2 service + тонкая обёртка моста
- **capability:** `system-audit` + `meta-infrastructure`
- **role:** dotfiles primary (sysop → planner → builder)
- **agent:** dotfiles sysop/builder (НЕ general; librarian не task()-ит чужой primary)
- **scope:** `project:dotfiles`
- **risk:** `high` (управление системным сервисом, от которого зависит M Code)
- **mutability:** `infra-edit`
- **review:** `reviewer`
- **acceptance:** `project-verifier` (dotfiles) — PASS перед commit
- **fallback:** `UNROUTABLE` если dotfiles primary недоступен (не general)
- **override:** null
- **runtime_dispatch:** `false` в этой Vault-сессии — librarian не вызывает
  чужой primary через task; handoff передаётся оператором в dotfiles-сессию
  (переключение харнеса), либо через host apply route (sysop/system-ops) с
  явным approval.
- **inputs:**
  - `06-Audits/2026-09-30-mcode-opencode-bridge.md` (Addendum 2026-10-01)
  - `~/.config/opencode/service.json` (токен, read-only, не логировать)
- **outputs (ожидаемые):**
  - спека `kind: task` в `/home/rudra/dotfiles/docs/specs/`
  - systemd user-unit (или `opencode service start` + автозапуск)
  - тонкая обёртка (`prompt`/`read`/`handoff`), токен из `service.json`

## Порядок (контракт)

1. dotfiles пишет спеку `kind: task` в свой spec-home (контракт + DoD + rollback).
2. Перевод orphan `serve --service` (PID 3378244, :49374) в управляемый сервис;
   живой orphan без необходимости не убивать (M Code подключён), rollback-план.
3. Проверка авторизации модели на серверной стороне (`provider.auth`).
4. Тонкая обёртка: `prompt` (POST /prompt, тело `text`), `read` (GET /message),
   `handoff` (git-tree async reverse). Токен из `service.json`, без хардкода/логов.
5. Verifier PASS → commit → перенос спеки в `spec-home/done/`.

Boundary: это route decision + handoff, не доказательство выполнения. Live
dispatch, acceptance evidence и verifier PASS принадлежат dotfiles-сессии.
Жёсткий предел дизайна: unprompted live-пуш OpenCode→M Code не реализуется
(ограничение API M Code) — обратная инициатива async через git-дерево.

## Append 2026-10-05 — контракт ре-верифицирован, канал передачи выбран

- **Contract re-verified 2026-10-05** (openapi живого сервиса, 117 путей):
  `POST /api/session`, `POST .../prompt`, `GET .../message`, `POST .../synthetic`,
  `GET /api/session/active` — все в наличии и работают на **OpenCode v2.0.23**
  (аудит 30.09 делался на 2.0.19; контракт не сломан, прирост путей:
  `/interrupt`, `/fork`, `/command`, `/wait` — потенциальные бонусы моста).
  Токен `service.json` валиден (200 на живом сервисе). M Code не двигался
  (бинарь 28.09, процесс с 30.09) — асимметрия обратного канала в силе.
- **PID-уточнение к промту:** конкретный PID orphan'а передавать нельзя —
  он меняется штатно (`dotfiles/scripts/.local/bin/opencode-reload` целенаправленно
  убивает бэкенд для релоада; актуальный PID: `pgrep -f "opencode serve --service"`,
  порт стабильный :49374). В промте заменено на механизм, не PID.
- **Фундамент готов:** dotfiles закрыли `mcode-opencode-provider-ssot` (done) —
  шаг «авторизация модели на серверной стороне» опирается на выровненный SSOT.
- **Канал передачи (решение Rudra 2026-10-05):** оператор запускает `/spec`
  из dotfiles — тот исполняет накопившиеся спеки; далее peer-comms
  (`opencode run -s <sessionID>`) для парной работы librarian ↔ dotfiles-сессия.
  Письмо ≠ авторизация: scope T-156 уже подтверждён оператором ранее.

## Append 2026-10-06 — EVIDENCE: исполнено (peer-письмо dotfiles/sysop + git-сверка librarian)

- **Status:** DONE (Implementation) — dotfiles/sysop `ses_ef2508bbfffe…`,
  peer-письмо + независимая git-сверка librarian (коммиты/spec/unit прочитаны
  из репо, не на веру).
- **Артефакты (проверены в дереве):** `docs/specs/done/mcode-opencode-bridge-endpoint.md`
  (kind: task, lifecycle-перенос корректный); `systemd/.config/systemd/user/opencode-serve.service`
  (enabled); `scripts/.local/bin/opencode-bridge` (prompt/read/handoff, токен
  только из service.json, symlink-эскейп закрыт).
- **Коммиты:** `0bf24ca` (unit+wrapper+spec), `066a033`/`7366119` (done+память),
  `1ac4be8` (meta write: allow), `ed36cdb`/`08084f5` (leak-guard + инвалидация
  кэша секретов). Теги: `t156-bridge-endpoint`, `t156-leak-guard`.
- **Live-проверки:** живой `read` → 200 (Basic base64(`opencode:<pw>`));
  авторизация модели на сервере — прогон без `provider.auth`; openapi 117 путей.
- **Инфра-бонус:** плагин `leak-guard` (редакция секрет-литералов в выводе
  инструментов, 20/20 тестов, живая проба → [REDACTED]); meta получил write.
- **Incident 1 (их лог):** auth-схема Bearer → 401; root cause — сервер
  принимает только Basic с username `opencode`. Fix в обёртке, repro→pass.
- **Incident 2 (их лог):** пароль service.json попал в stdout диагностики;
  в репо не утёк; структурный фикс leak-guard; **ротация пароля — за оператором**
  (гасит сервис, делать в плановом окне, затем re-pair M Code).
- **Открыто (решение оператора):** юнит enabled но inactive — порт держит
  M Code-backed процесс; вариант (а) вернуть сервис под systemd сейчас
  (короткий разрыв, M Code переподключится) vs (б) до следующего логина.
  Рекомендация исполнителя — (а). Ответ librarian в их сессию — после решения
  оператора (общение ≠ авторизация).

## Append 2026-10-06 (2) — EVIDENCE: apply-gate закрыт, T-156 ЗАВЕРШЕН

- **Решение оператора:** вариант (а), сейчас. Исполнено dotfiles/sysop
  (ротация пароля detached, без вывода значения; restart юнита).
- **Независимая верификация librarian (не на веру):**
  - `systemctl --user is-active` → **active**, enabled, MainPID 346858;
  - `ss -tlnp :49374` → pid 346858; `/proc/346858/cgroup` →
    `opencode-serve.service` — порт под управляемым юнитом, orphan не остался;
  - `opencode-bridge read` → rc 0 (новый токен, Fresh service.json);
  - M Code сессии видны на новом сервисе (re-pair подтверждён косвенно).
- **Git evidence:** `6665d45` (память/ротация), `800ec1b` +
  `docs/handoffs/2026-10-06-t156-apply-rotation.md`.
- **Статус задачи:** T-156 → **Done** (implementation + apply + closure,
  весь lifecycle: аудит → дизайн → route → handoff → реализация → apply →
  независимая верификация). Ответный канал peer-comms双向 отработал штатно
  (2 письма в каждую сторону + git-дерево).
