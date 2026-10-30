---
type: Manifest
id: uas
name: Университет Агентских Систем (сетей)
shadow: куратор агентского контура
jurisdiction: >
  Стандарты манифестов ведомств; реестры агентов, скиллов и команд; стандарты
  онбординга новых ведомств; владение решениями по всему агентскому контуру
  (Р-004/Р-012/Р-014/Р-016). Включая агентский runtime-слой: провайдеры моделей,
  здоровье, ротация, квоты — операционно через спец-отдел «Ротатор моделей».
carrier-sessions: ses_e9884e4aeffe7okjn4f7RtavmG
mandate-source: >
  Спека docs/specs/done/university-of-agent-networks-location.md (approved Rudra
  2026-10-17, verifier PASS 10/10); Р-016 (УАС — локация сети); Р-023 (ввод в строй,
  сессия-носитель с 2026-10-23).
report-address: ses_eceb23a71ffeJO9QnFou8VngZC
peer-address: ses_e9884e4aeffe7okjn4f7RtavmG
spec-home: /home/rudra/dotfiles/docs/specs/
status: active, 2026-10-23
boundaries: >
  Не правит код приложений проектов. Правку глобального opencode.jsonc
  (provider-блок) исполняет ИЦ; УАС владеет решением и каталогом. Мандат не
  самозванный (Р-009): полномочия прослеживаются до слова Rudra или спеки.
ports: реестр манифестов (docs/org/manifest-registry.md) — курирование УАС
capabilities: [capability-routing, decision-queue]
memory-zones: [uas-rotator-telemetry, provider-catalog]
file-zones: [03-Projects/uas.md, 03-Projects/uas-special-rotator.md, docs/org/]
evidence-policy: независимый verifier PASS + commit/tag; рапорты — в ЦУ
---

# Манифест УАС

Полная карточка ведомства: [[uas]] (03-Projects/uas.md).
Первый манифест реестра (Р-014): создан по пробелу, подсвеченному ИПТ
(ref: uas-spec-actual-20261023) — манифест обязателен с момента approval спеки,
а УАС в строю с 2026-10-23.
