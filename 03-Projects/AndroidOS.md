---
type: project
repo: /home/rudra/Projects/AndroidOS
kind: umbrella / mobile / ecosystem
status: planning
stack: Android / Kotlin (to validate) / OpenCode / offline-first data
timestamp: 2026-08-22
---

# AndroidOS — модульная персональная ОС

> **Статус:** planning. Это umbrella-проект и архитектурная граница, а не утверждение, что модули уже реализованы.
> **Связано:** [[rudra-phone]], [[rudra-ai]], [[dotfiles]], [[ChaT]], [[06-Audits/2026-08-22-androidos-open-source-first]], [[06-Audits/2026-08-22-androidos-pa-mvp-architecture-adr]], [[06-Audits/2026-08-28-androidos-coordination-bridge-spec]], [[user-profile-contract]], [[TASKS]]

> **Coordination Bridge FROZEN BY USER (2026-08-30):** bridge не является
> обязательным шагом AndroidOS и не вызывается. Historical artifacts сохраняются;
> canonical execution spec: [[06-Specs/AndroidOS/androidos-return-to-implementation]].

> **Historical T-109 bootstrap (2026-08-28):** в AndroidOS создан canonical docs-only
> surface `coordination/bridge/`. Bridge artifacts uncommitted/untracked; the
> pre-bridge AndroidOS baseline does not contain them and is not their
> provenance. Task/handoff/evidence/decision artifacts связаны между собой.
> Structural smoke partial; local named runtime dispatch не доказан: попытка
> dispatch для `reviewer` откатилась на default. Поэтому reviewer/verifier
> acceptance не подтверждена, bridge remains `BLOCKED`; не симулировать `PASS`
> и не переводить задачу в Done.

> **Current operator path:** открыть AndroidOS, прочитать `AGENTS.md`, выполнить
> `/android-plan` или свободный запрос; порядок read-only status → plan → user
> approval → implementation. Не копировать отчёты в Vault. Historical guide:
> [[07-Runbooks/coordination-bridge-operator-guide]].

> Профиль: Personal Assistant будет тесно связан с каноническим профилем через scoped adapter и approval-gated proposals. Практическая глубокая интеграция AndroidOS откладывается до завершения Personal Assistant MVP; до этого фиксируются только контракты, threat model и research.

## Граница umbrella

AndroidOS объединяет самостоятельные модули, которые могут развиваться и проверяться отдельно, а затем интегрироваться через явные контракты данных, синхронизации и прав доступа. Он не заменяет Vault, dotfiles или ChaT и не является обещанием единого backend/cloud.

## Модули

| Модуль | Роль | Статус |
|---|---|---|
| Personal Assistant | flagship: голосовой inbox → редактируемая расшифровка → структура и действия | planning |
| Personal/Social Manager | профили контактов, отношения, история взаимодействий | planned |
| Project Manager | проекты, задачи, события, встречи, promises, kanban и views | planned |
| Ecosystem Control | scoped-управление Vault, dotfiles, ChaT и другими проектами | planned |
| BlogerAI | слой повествования и контента поверх истории экосистемы | planned, after PA MVP |
| Android Development Layer / VibeAndroid | методы, шаблоны и агентная инфраструктура Android-разработки | planning; [[TASKS]] T-029 |

## Personal Assistant MVP

- Android widget controls: `start`, `pause`, `resume`, `stop`.
- Короткие и длинные монологи; после STT показывать transcript для редактирования до сохранения.
- Offline-first: телефон и laptop равноправны, синхронизация delayed; private data local by default.
- Raw audio и transcripts сохраняются временно и автоматически удаляются по настраиваемому retention policy.
- Entity model: events, tasks, contacts, projects, meetings, promises, ideas, notes, habits, goals, relations; новые типы добавляются без переделки ядра.
- Напоминания в течение дня и daily plan.
- Killer feature: inbox-to-structure с подтверждением пользователя.
- Kanban/views и базовые social/contact profiles.
- Proactive behavior вводится постепенно, только после проверяемого базового контура.
- Профильные события и предложения изменений проходят через global `profile-governor`; Personal Assistant не создаёт вторую копию канонического профиля и не пишет в него молча.
- Telegram не входит в MVP; после MVP возможны отдельные bot(s) с отдельными credentials и scope.

### Acceptance criteria MVP

MVP принимается только после демонстрации на phone и laptop: запись можно прервать и продолжить; transcript редактируется до структурирования; inbox item превращается в выбранные entities с подтверждением; сущности доступны offline; delayed sync не теряет и не дублирует изменения; retention job удаляет raw audio/transcripts согласно настройке; daily plan/reminders работают локально; новые entity types регистрируются без миграции каждой существующей сущности. Архитектурный MVP-контур и provisional defaults зафиксированы в [[06-Audits/2026-08-22-androidos-pa-mvp-architecture-adr]]; реализация и final device-specific stack не заявлены.

## Roadmap

1. **P0: boundaries and research** — контракты данных/profile/sync, threat model, OSS research.
2. **P1: Personal Assistant vertical slice** — widget → STT → edit → inbox → one or more entities → local reminders.
3. **P2: PA MVP** — полный entity set, extensibility, daily plan, views, retention and phone/laptop delayed sync.
4. **P3: ecosystem integration** — Personal/Social Manager, Project Manager, scoped Ecosystem Control; Telegram only as a post-MVP adapter.
5. **P4: VibeAndroid layer** — reusable Android methods and project tooling validated by the slice.
6. **P5: BlogerAI** — only after full PA MVP; chronicle, storytelling, posts/articles/scripts/crowdfunding/media content from cross-project history.

## Legacy relation and dependencies

- [[rudra-phone]] is the legacy remote-control/mobile surface. It remains planning; its Telegram-first and API Gateway proposals are candidates, not AndroidOS decisions.
- [[rudra-ai]] is the legacy assistant/planner concept. AndroidOS supersedes its scope as the canonical assistant umbrella; no implementation claim is carried over.
- [[VibeOS]] / T-029 ([[TASKS]]) supplies the planned development layer.
- [[ChaT]] is a separate knowledge/operations project and may receive scoped adapters; AndroidOS must not copy its facts.
- AndroidOS/Personal Assistant is a planned first-class profile consumer, but deep runtime integration is explicitly **after PA MVP**; until then only design/research work is claimed.

## Open decisions

- Android app/module/repository boundary and Kotlin/other stack.
- Canonical entity schema, event log/conflict policy, and extensibility mechanism.
- STT/TTS/local LLM choices and device capability floor.
- Encrypted phone-laptop transport, pairing, recovery, and deletion semantics.
- Background/widget/notification constraints across Android versions.
- Whether Ecosystem Control uses APIs, filesystem adapters, or both; exact permission scopes.
- BlogerAI privacy boundary and source-selection/consent model.
- Acceptance evidence for provisional PA architecture: Redmi lab, STT/LLM benchmarks, lifecycle, retention and sync fault injection ([[06-Audits/2026-08-22-androidos-pa-mvp-architecture-adr]]).

## Non-goals for this phase

No Telegram-first MVP, voice replies/voice conversation, autonomous destructive actions, cloud-first storage, or selected vendor/tool claims. Research candidates are recorded only in [[06-Audits/2026-08-22-androidos-open-source-first]].
