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
carrier-sessions: ses_e9884e4aeffe7okjn4f7RtavmG
mandate-source: >
  Слово Rudra 2026-10-23 (basis: quoted): «у нас уже есть какое-то количество
  провайдеров, нам нужно настроить толково ротатор моделей. для этого в уас
  должен быть отдел который этим занимается — назовём его спец отдел». Р-023.
report-address: ses_eceb23a71ffeJO9QnFou8VngZC
peer-address: ses_e9884e4aeffe7okjn4f7RtavmG
spec-home: /home/rudra/dotfiles/docs/specs/
status: active, 2026-10-23
boundaries: >
  УАС владеет решением и каталогом; правку глобального opencode.jsonc исполняет
  ИЦ. Не трогает код приложений. Секреты не появляются в файлах каталога, логах
  и отчётах (env/vault/auth.json + redact).
ports: control-plane/model-catalog.json + control-plane/telemetry/provider-health.jsonl
capabilities: [capability-routing, report]
memory-zones: [provider-health-telemetry]
file-zones: [tools/key-rotator/, control-plane/model-catalog.json, control-plane/telemetry/]
evidence-policy: независимый verifier PASS + commit/tag; живой прогон failover (Q-005.3) как доказательство
---

# Манифест спец-отдела «Ротатор моделей»

Полная карточка отдела: [[uas-special-rotator]] (03-Projects/uas-special-rotator.md).
DoD отдела — 8 пунктов; квест — 11-Quests/quests.md → Q-005 (6 подквестов).
