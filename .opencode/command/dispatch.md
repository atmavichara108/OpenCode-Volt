---
description: "Мандат ведомству: провенанс слова владельца, адрес из реестра, постановка, контроль доставки"
agent: librarian
---
Команда: /dispatch <ведомство> <задача>

## Жёсткие правила
- **Слово владельца — единственная авторизация;** `basis: quoted`, домыслы
  запрещены; неоднозначность → вопрос, не трактовка.
- **`general` не является silent fallback;** неизвестный маршрут = `UNROUTABLE`.
- Ссылки: [[02-Methods/capability-routing]], [[04-Memory/peer-registry]],
  [[01-Policies/skill-taxonomy]], [[02-Methods/ministry-calibration]],
  [[01-Policies/decisions-registry]].

## Шаги

1. **Адрес — только полный sessionID из [[04-Memory/peer-registry]].**
   Адрес, взятый из чата, запрещён (класс INC-18). Нет адреса или нет такого
   ведомства → `UNROUTABLE`, не угадывать.

2. **Route decision** по [[02-Methods/capability-routing]]: capability, scope
   (`vault` | `global` | `project:<name>`), risk, mutability, review,
   acceptance, fallback. Пропуск любого обязательного поля → `UNROUTABLE`.

3. **Постановка:** дословное слово владельца (`basis: quoted`) **или** явная
   пометка «по распоряжению ЦУ, не слово владельца»; scope; DoD; что не
   трогать; ref-id.

4. **Отправка:** `tools/peer-comms/letter.sh`
   (в dotfiles: `/home/rudra/dotfiles/tools/peer-comms/letter.sh`)
   `--to <id из реестра> --from <свой id> --scope <ref> --title ... --file ...`.
   **Модель адресата не передавать** (B15; `--model` запрещён жёстко).
   Перед отправкой — `garbage-guard check-text` на текст письма.

5. **Delivery-check по журналу**: `sent ≠ delivered`; дождись записи доставки
   или зафиксируй «в очереди». route-log — append-only, история не правится.

## Выход
ref-id, адрес (sessionID), статус доставки, что ждём в ответ.
