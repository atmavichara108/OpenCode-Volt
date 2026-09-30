---
type: Research Snapshot
title: M Code ↔ OpenCode — bridge-исследование 2026-09-30
description: Живые проверки API обоих харнессов: есть ли peer-общение M Code→OpenCode, что открывает OpenCode v2 server, асимметрия каналов, итоговый паттерн для совместной работы.
tags: [research, bridge, mcode, opencode, api, orchestration]
timestamp: 2026-09-30
status: draft
---

# Research Snapshot — M Code ↔ OpenCode bridge

## Цель

Пользователь хочет, чтобы M Code (форк OpenCode Desktop) и OpenCode TUI v2
работали не просто параллельно, а **совместно** — как сессии одного проекта в
M Code общаются через peer-механизм, так же инициировать работу из OpenCode.

## Вердикт (коротко)

- **Peer-общение M Code — это внутренняя шина M Code**, не протокол. OpenCode
  TUI в неё не входит.
- **У OpenCode v2 есть собственный HTTP-сервер**, и он открывает почти весь
  нужный канал: создать сессию, внедрить промпт, прочитать результат, прочитать
  inbox. Всё проверено вживую.
- **Асимметрия есть**: M Code → OpenCode работает полноценно (M Code ставит
  задачу в живую OpenCode-сессию через `prompt` и читает `message`); обратно
  OpenCode → M Code через HTTP нельзя (у M Code API нет `/prompt`/`/synthetic`
  инжекта — только `question`/`permission` reply). Обратный канал — общее
  git-дерево + собственный `synthetic` на стороне OpenCode.
- **Паттерн = librarian (M Code) → build-агент (OpenCode)**, ровно как в Vault.

## Проверенное вживую (2026-09-30)

### OpenCode v2 server (поднят на 127.0.0.1:4099, версия 2.0.19)

Список путей `/openapi.json` (115 путей) — релевантные для bridge:

| Операция | Что делает | Проверено |
|----------|-----------|-----------|
| `POST /api/session` | создать сессию извне | ✅ вернул `ses_f0eac8e96ffe...` |
| `POST /api/session/{id}/prompt` | внедрить промпт → сессия выполняет | ✅ (тело — ключ `text`, не `prompt`; 400 если нет `text`) |
| `GET /api/session/{id}/message` | прочитать результат | ✅ (`type:user`/`assistant`, `finish`, `error`, пагинация `cursor`) |
| `GET /api/session/{id}/inbox` | письма-в-сессию (аналог peer inbox) | ✅ пусто `{"data":[]}`; POST на inbox — 404 (только системное) |
| `POST /api/session/{id}/synthetic` | инжект сообщения от агента | ✅ вернул `type:synthetic` |
| `GET /api/session/active` | список живых сессий | ✅ `{"data":{}}` |

Практический результат проб: сессия, созданная извне, приняла `prompt`,
запустилась, ответила — но упала на `provider.auth` (`Missing Authorization`,
`liquid/d1` через vercel) — это **отсутствие авторизации модели на голом
сервере**, а не дефект контракта. Канал рабочий.

### Постоянный OpenCode service (уже был запущен до этой сессии)

- Процесс: `opencode serve --service`, PID 1144661, uptime 12ч+, слушает
  `127.0.0.1:49374`.
- `opencode service status` говорит **"stopped"** — процесс не управляется
  штатным сервисом, это orphan (`PPID=1`), запущен вне менеджера.
- Пароль — в `~/.config/opencode/service.json` (SSOT-зона dotfiles-агента).
- Подключился с реальным токеном: `{"version":"2.0.19","pid":1144661,...}`,
  активных сессий нет.
- **Это тот сервис, к которому окно "Connect to server" M Code Desktop просило
  подключиться.** Не был убит (не я его поднял; возможно dotfiles-агент/прежний
  запуск). Рекомендация ниже.

### M Code API (openapi.json, 32 пути)

- Среди `POST /api/session/{id}/*`: только `compact`, `model`,
  `permission{/reply}`, `question{/reject,/reply}`.
- **Нет `/prompt`, `/synthetic`, `/message`-инжекта, `/inbox`-записи.**
  M Code не умеет принимать письма от внешнего HTTP-актора в живую сессию.

## Диагностические артефакты

| Файл | Что это |
|------|---------|
| `/tmp/mcode-openapi.json` | полный OpenAPI spec M Code (32 пути) |
| `/tmp/opencode-openapi.json` | полный OpenAPI spec OpenCode v2 (115 путей) |
| `/tmp/mcode-doc.txt` | embedded customize-mcode docs из asar (v1.5.0) |

## Выводы и рекомендации

1. **M Code → OpenCode — задача-мост.** Дирижёр (librarian в M Code) ставит
   задачу живому OpenCode-агенту через `opencode api --server ... POST
   /api/session/{id}/prompt` (или `opencode run --agent <name> --prompt "..."`)
   и читает результат через `GET /api/session/{id}/message`. OpenCode остаётся
   исполнителем (build-агент dotfiles и т.п.).

2. **OpenCode → M Code — только через общее дерево** (git: `TASKS.md`, claims,
   `spec-home`, ветки `task/*`) либо собственный `synthetic` на стороне
   OpenCode, если обе стороны держат общий OpenCode-сервис.

3. **Требования для стабильного bridge:**
   - OpenCode v2 service должен быть **управляемым** (`opencode service start`,
     а не orphan `serve --service`), иначе окно M Code каждый раз будет
     спрашивать пароль, а процесс может исчезнуть.
   - Пароль (token) bridge-клиенту брать из `~/.config/opencode/service.json`,
     не хардкодить.
   - На OpenCode-стороне модель должна быть авторизована (иначе
     `provider.auth` как в пробе).

4. **Орфан `opencode serve --service` (PID 1144661)** — стоит завести в
   штатный сервис или аккуратно перезапустить; пока он живой и запаролен, M Code
   Desktop будет показывать окно подключения. Вопрос к владельцу (dotfiles).

## Следующие шаги (не в этом документе)

- Первый промт для OpenCode build-агента (задача-контракт) — отдельно.
- Спека bridge-слоя (`kind: task`) при решении строить постоянный мост.