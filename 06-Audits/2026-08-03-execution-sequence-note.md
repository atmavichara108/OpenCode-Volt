---
type: Execution Sequence Note
date: 2026-08-03
status: draft
source: "[[06-Audits/2026-08-03-ecosystem-upgrade-plan-v1]]"
tags: [execution-sequence, planning, draft]
---
# Execution sequence note (2026-08-03)

> Короткая инженерная выжимка порядка исполнения ecosystem upgrade plan v1.
> Не план, не отчёт — sequencing rationale и зафиксированный gate-order.

## Executive verdict

- Не строить global layer целиком заранее — он формируется по мере
  validated need, не сверху вниз.
- Не начинать с dv-hub — recovery-case, не первая kernel-цель.
- Global layer идёт на **полшага впереди** SERPlux: ровно настолько,
  чтобы kernel contracts имели контрактную форму до live-adoption, но
  не более — никакого big-design-upfront для всего глобального контура.
- **SERPlux = first live adoption target.** Kernel contracts проходят
  первое реальное натяжение здесь.
- **dotfiles = second-stage hardening substrate.** Валидированные в
  SERPlux паттерны поднимаются в global contour через dotfiles как
  исполнительный субстрат.
- **dv-hub = final recovery-case adoption.** Только после того, как
  kernel/adoption logic доказаны на SERPlux и global hardening взят из
  dotfiles.

## Recommended execution order

- **Phase 1 — minimal kernel stabilization for live use.**
  - reviewer/verifier split (T-085).
  - plugin policy / loader contract (T-084).
  - `/done` adaptation by memory model (T-086).
  - runtime gate enforcement (T-089).
  - test-metrics normalization — только там, где влияет на SERPlux (T-087).
  - Цель: контрактная форма без big-design-upfront; ровно до live use.
- **Phase 2 — SERPlux first adoption.**
  - stabilize acceptance surface (T-088 и связанные).
  - remove plugin/runtime ambiguity — закрыть loader-вилки, проявленные
    на проекте.
  - align docs-based memory (SERPlux) с global rules (memory-model из Phase 1).
  - record what works vs not — первый live реестр adoption evidence.
- **Phase 3 — dotfiles / global hardening.**
  - extract validated patterns into global layer (sysop / researcher /
    reviewer / guardian — T-070/T-071/T-072/T-093).
  - strengthen global role kernel из Phase 1 split-контрактов.
  - refine local tooling as limbs (Manjaro-интеграция, notify/voice/
    system — T-076).
  - engineering-style-contract drafting/approval (T-094) в этой фазе,
    после того как контракты проверены живым adoption.
- **Phase 4 — dv-hub recovery adoption.**
  - только после того, как kernel/adoption logic доказаны на Phase 1–3.
  - restore minimum health и acceptance surface primero (T-090 recovery
    gate), затем overlay kernel contracts.
  - здесь же — declaration-vs-reality reconciliation (T-095) как
    applied meta-mechanic на восстановленном проекте.

## Rationale

- Business priority = SERPlux first: live коммерческий проект с
  acceptance-поверхностью даёт реальное натяжение контрактов, а не
  thought-experiment.
- Architectural validation in live project: kernel contracts
  стабилизируются в контакте с реальным кодом/тестами/plugins, а не в
  вакууме global-layer дизайна.
- Infrastructure follows proven need: global layer и dotfiles-substrate
  строятся из validated-in-SERPlux паттернов; обратный порядок
  производит мёртвую инфраструктуру.
- dv-hub не первый kernel target: recovery-case требует сначала
  восстановления acceptance-поверхности; overlay контрактов на
  неработающий проект маскирует kernel-failures под project-failures.