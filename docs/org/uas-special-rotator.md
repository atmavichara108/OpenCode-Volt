---
type: Manifest
id: uas-special-rotator
name: Спец-отдел «Ротатор моделей»
shadow: садовник провайдеров (хозяйство, не склад)
jurisdiction: >
  Каталог провайдеров как единый SSOT; живой health (probe по расписанию);
  failover по ролям агентов; учёт лимитов/квот и приватности (обучение на
  данных); журнал переключений append-only; публичный отчёт «лучший провайдер
  по роли» (median/p95). Рамка «толково» — Р-024 (5 тезисов ХПФ).
carrier-sessions: >
  ses_e5455a2f2ffe6b9EqBT1aziN2A — РМПП, примари Keymaster (спец-отдел
  перешёл в ведомство этой сессии; полномочия расширены на ротацию и
  подключение провайдеров). Координация и канон — УАС,
  ses_e9884e4aeffe7okjn4f7RtavmG.
operational-model: >
  Носитель — линия РМПП (сессия выше, примари Keymaster); каталог провайдеров
  как SSOT — tools/key-rotator/providers.json + control-plane/model-catalog.json,
  health — control-plane/telemetry/provider-health.jsonl, живой каталог проб —
  control-plane/live-model-catalog.json. Слово владельца 2026-11-12: линия РМПП
  вне заморозки ЧП, работает по своим мандатам;
  2026-11-18: протокол выпила провайдеров по истечении бесплатного периода
  (tools/key-rotator/trial_expiry.py, метод promo-provider-protocol) — anymodel
  выкинут. ХПФ — стратегический слой (критерии/рамка), не исполнитель.
  Прежняя запись («исполняет ИЦ в будущей лаб-сессии», Р-026) устарела.
  **2026-11-20 (слово владельца, Р-Д-031):** отдел стал шлюзом по умолчанию для
  всего флота — универсальный ротатор-модель-шлюз (new-api), схема «дефолт +
  явные исключения»: coding → `newapi/free-code`, general → `newapi/free-general`
  (Р-Д-032: vision+general слиты в `free-general`, `attachment: true`).
  **Исключения сняты 21.11 по слову владельца (Р-Д-033):** reviewer и verifier
  тоже работают через шлюз — `newapi/free-general` и `newapi/free-code`;
  прямые пины `nvidia/poolside/laguna-xs-2.1` / `vercel/recursive/flint-v1.0`
  остались только константами Р-109 (fallback) в гейте `pin-check`.
  Факт на диске 21.11: шлюз — 25 каналов;
  `free-code` — nvidia 60/55 → openrouter 50 → amd-radeon 45/44 → vercel 35;
  `free-general` — nvidia 90 (vision super-vl) → 60/55 → openrouter 50 →
  amd-radeon 45/44. AMD-first отменён по живому факту (зависание 320 с на
  `amd-radeon|Qwen3.8-27B`), возврат — только со словом владельца. Сторож
  `watch.timer` — 30 мин; живой каталог (`ts`, `source`, провайдеры) — второй
  источник живости пинов для гейта `pin-check` (dotfiles, спека
  `docs/specs/pin-guard.md` §4.1).
mandate-source: >
  Слово Rudra 2026-10-23 (basis: quoted): «у нас уже есть какое-то количество
  провайдеров, нам нужно настроить толково ротатор моделей. для этого в уас
  должен быть отдел который этим занимается — назовём его спец отдел». Р-023.
report-address: ses_eceb23a71ffeJO9QnFou8VngZC
peer-address: ses_e9884e4aeffe7okjn4f7RtavmG
spec-home: /home/rudra/dotfiles/docs/specs/
status: "active, 2026-10-23 (обновлён 2026-11-21: шлюз по умолчанию для флота — Р-Д-031/Р-Д-032; носитель — РМПП/Keymaster; запись об исполнителе через ИЦ устарела)"
boundaries: >
  УАС владеет решением и каталогом; правку глобального opencode.jsonc исполняет
  ИЦ. Не трогает код приложений. Секреты не появляются в файлах каталога, логах
  и отчётах (env/vault/auth.json + redact).
ports: control-plane/model-catalog.json + control-plane/telemetry/provider-health.jsonl + control-plane/live-model-catalog.json
capabilities: [capability-routing, report]
memory-zones: [provider-health-telemetry]
file-zones: [tools/key-rotator/, control-plane/model-catalog.json, control-plane/telemetry/, control-plane/live-model-catalog.json]
evidence-policy: независимый verifier PASS + commit/tag; живой прогон failover (Q-005.3) как доказательство
---

# Манифест спец-отдела «Ротатор моделей»

Полная карточка отдела: [[uas-special-rotator]] (03-Projects/uas-special-rotator.md).
DoD отдела — 8 пунктов; квест — 11-Quests/quests.md → Q-005 (6 подквестов).
