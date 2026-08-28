---
type: decision / research note
project: AndroidOS
status: planning
date: 2026-08-22
decision: provisional MVP architecture
---
# AndroidOS Personal Assistant: MVP architecture ADR

> Это решение задаёт границы и порядок проверки MVP. Оно не является заявлением о готовой реализации и не превращает device-specific candidates в финальный стек.
> Связано: [[AndroidOS]], [[06-Audits/2026-08-22-androidos-open-source-first]], [[user-profile-contract]], [[ChaT]], [[TASKS]]

## Context

AndroidOS — umbrella modular/hybrid project. Первый flagship — Personal Assistant (PA): widget-driven recording, русский STT с English names/terms/projects, редактирование transcript до структурирования, inbox-to-structure, reminders/daily plan и равноправная delayed sync между phone и laptop. Private data local by default; raw audio и transcripts имеют ограниченный retention. ChaT остаётся полноценным consumer профиля, но глубокая AndroidOS integration начинается после PA MVP.

OSS-first означает: зрелый OSS используется там, где он доказан, а собственный код ограничен adapters, UX, domain/privacy policy и integration. Все provisional choices ниже должны пройти real-device acceptance.

## Decision

### Architectural shape

PA строится как native Android application на Kotlin с портами `Transcriber`, `ExtractionEngine`, `LocalStore`, `SyncTransport` и `Interchange`. Laptop — равноправный peer с теми же domain contracts, но UI/runtime может быть отдельным. Widget только dispatches idempotent commands; recording живёт в foreground service, transcript/edit/approval — в app UI.

**Provisional default:** Kotlin/Android для phone, shared contract/schema и независимый laptop adapter. Это не решение о конкретном UI toolkit, Android API floor или laptop framework.

### Native Kotlin vs Flutter/PWA

| Вариант | Плюсы | Ограничения для MVP | Решение |
|---|---|---|---|
| Native Kotlin | Прямой доступ к widget, foreground microphone service, lifecycle, notifications, Room и Android security | Два UI/runtime при отдельном laptop client | **provisional default** |
| Flutter | Общий UI и быстрый cross-platform shell | Plugin/lifecycle/background bridges всё равно Android-specific; audio/crypto bridges остаются | Не default; допустим после доказательства bridge-контрактов |
| PWA | Быстрый prototype и переносимость | Ненадёжна для screen-off recording, widget, durable notifications и media lifecycle | Только prototype, не MVP base |

Acceptance: widget action latency, screen-off recording/resume, process death/reboot recovery, notification permission behavior и retention проходят на Redmi; laptop peer читает/записывает тот же portable contract.

### STT comparison and provisional gate

| Candidate | Strength | Risk | Position |
|---|---|---|---|
| Vosk | Small offline Russian baseline, streaming API, vocabulary adaptation | Russian punctuation/quality и long-monologue behavior may be weaker | Baseline experiment |
| sherpa-onnx | Streaming/non-streaming, VAD/punctuation candidates, Android bindings, Russian models | Exact model license, size and Redmi RTF not established | Strong candidate |
| whisper.cpp | Multilingual Russian quality, timestamps/quantization, Android/laptop portability | CPU/battery cost and less direct streaming ergonomics | Strong candidate |

**Provisional default:** `Transcriber` supports all three; no model выбран до fixed corpus comparison. Нужны согласованные WER/CER target, usable timestamps/segmentation, RTF <= 1.0 для short notes, bounded thermal/battery impact и accepted licenses. English names оцениваются отдельным named-term subset.

### Storage and search

**Provisional default:** Room over SQLite on Android, SQLite-compatible schema on laptop, FTS5 для transcript/entity search, SQLCipher-backed encrypted local database после проверки packaging и key lifecycle. Domain data — materialized tables плюс append-only `Change/Event`. Never sync a live SQLite file.

Plain SQLite+FTS5 проще, но без encryption at rest; Automerge/CRDT полезен для mergeable change documents, но не является query DB, retention engine или reminder policy. Поэтому CRDT не primary store. Export: SQLite/JSON/Markdown плюс ICS/VTODO/vCard где применимо.

Acceptance: authenticated unlock, migration/export round-trip, FTS, crash-safe event apply, удаление indexed/derived copies и измеренный storage overhead. SQLCipher остаётся provisional.

### Sync

Единица sync — encrypted authenticated `SyncEnvelope` с signed/idempotent changes, а не database file или raw audio по умолчанию.

| Option | Fit | Decision |
|---|---|---|
| Encrypted change bundles over Syncthing/files | Serverless delayed transport, retry, USB/LAN exit path | **provisional P1 transport**, только opaque bundles |
| CRDT/Automerge | Offline convergence/history для выбранных records | Domain experiment, не universal conflict policy |
| Local laptop API | Controlled peer protocol и acknowledgements | Candidate P2 transport; pairing/reachability open |
| Standards interoperability | ICS, VTODO, vCard, Markdown/JSON portability | Required import/export boundary, не backend |

Domain owns ordering, conflicts, tombstones и retention propagation. Transport replaceable; sync delayed and user-controlled; cloud-first отсутствует.

### Local extraction engine

**Provisional experiment:** llama.cpp + pinned GGUF Qwen3 0.6B/1.7B/4B, плюс второй runtime где возможно (ExecuTorch или MNN). Выбор открыт до Redmi tests: memory, tokens/sec, thermals, strict JSON. Extraction только предлагает typed changes с provenance/confidence; source of truth и approval остаются у пользователя.

`ExtractionEngine` replaceable, потому что model quality, quantization, Android delegates, licensing и battery меняются независимо. Domain принимает schema-validated proposals, не model-specific prompts. Deterministic date/time parsing и validation отклоняют invented fields; ambiguity остаётся пользователю.

## Domain contracts (MVP)

IDs — opaque UUID/ULID-like strings, создаются один раз. `created_at`/`updated_at` — UTC; timezone берётся из runtime/profile. Mutable records имеют `version`, `origin_change_id`, `provenance[]`, `retention_class`, `deleted_at?`.

```text
InboxItem { id, kind: audio|text|import, state: captured|transcribed|edited|structured|archived,
  transcript_id?, body?, source_device_id, captured_at, created_at, updated_at, provenance[], retention_class, version, deleted_at? }
Transcript { id, inbox_item_id, text, language_hints[], segments[{start_ms,end_ms,text,confidence?}],
  engine_id, model_id, status: raw|edited|superseded, edited_at?, provenance[], retention_class, version, deleted_at? }
Entity { id, type, schema_version, attributes, provenance[], status: proposed|approved|rejected, version, deleted_at? }
Event|Task|Contact { Entity with typed attributes; Event/Task carry schedule fields, Contact carries scoped identifiers/relations }
Reminder { id, target_id, schedule, timezone, state, notification_policy, provenance[], version }
ProfileProposal { id, scope, field_path, proposed_value, reason, source_ref, confidence,
  state: proposed|approved|rejected|superseded, affected_consumers[], provenance[] }
Change/Event { id, entity_id, operation, patch, actor_device_id, base_version?, occurred_at,
  logical_clock?, idempotency_key, provenance[], retention_class }
SyncEnvelope { id, sender_device_id, recipient_scope, sequence, changes[], tombstones[],
  created_at, expires_at?, key_id, signature, encryption_algorithms, bundle_hash }
```

`Entity.type` registry-backed и namespaced; новый type требует schema/validation/UI registration, но не migration каждой сущности. `Event/Task/Contact` — named views/contracts, не вторая identity system.

### Invariants and policies

- Idempotence: `Change.id` и `idempotency_key` unique; duplicate envelope/change — no-op с audit result; apply transactional и schema-validating.
- Provenance: source, device, timestamps, engine/model или human edit, source reference, confidence/status и canonical-vs-derived distinction; generated entities link to InboxItem and Transcript.
- Editing gate: raw STT никогда не структурируется silently. Сначала edit transcript, затем field diff и explicit approve proposal/batch.
- Profile gate: PA читает только approved local scoped subset. `ProfileProposal` не canonical write; `profile-governor` применяет minimal diff только после explicit approval, согласно [[user-profile-contract]]. ChaT facts остаются в ChaT registers.
- Retention: raw audio и raw/superseded transcripts — temporary classes с configurable expiry. Deletion удаляет blobs, text, FTS/index/derived caches и emits authenticated deletion tombstone peers; legal hold/export пока unresolved.
- Conflicts: no last-writer-wins для approved edits, profile proposals, reminders и destructive deletes. Preserve versions/provenance, mark `conflict`, deterministic diff, user resolution. Non-overlapping patches merge only after validation; tombstones win over stale updates unless restore approved.
- Approval: extraction, profile changes, external exports, destructive deletes и autonomous actions требуют explicit user approval. MVP sends no autonomous external messages.

## Vertical slice

1. Widget `start` creates InboxItem and recording session through foreground service.
2. `pause`/`resume`/`stop` idempotent and recoverable after UI/process recreation; audio encrypted locally with retention metadata.
3. On stop, STT produces Transcript; app shows editable text and creates no entities directly.
4. User edits and requests structure; extraction returns schema-validated proposals with provenance.
5. User approves Event or Task; local Reminder persists and schedules.
6. Change log emits encrypted bundle; second peer imports twice and gets one identical result.
7. Retention job expires audio and transcript/index copies and syncs deletion tombstones.

## Milestones and DoD

### P0: contracts and threat model

DoD: ADR reviewed; schemas, state machine, approval/retention/conflict rules and export boundary are test fixtures; threat model covers unlocked/lost device, malicious peer, replay, revoked device and plaintext logs; no secrets/audio enter Vault.

### P1: vertical slice

DoD: real APK demonstrates widget start/pause/resume/stop, screen-off recording, editable transcript, one approved Task/Event, local reminder and encrypted change-bundle round-trip on phone plus laptop test peer. Backend behind ports; versions/checksums recorded.

### P2: PA MVP

DoD: fixed STT/LLM evidence, short/long corpus acceptance, initial entity registry, daily plan, FTS, configurable retention, conflict UI, pairing/revocation/retry and delayed sync; no data loss/duplication under fault injection; exports round-trip.

### P3: ecosystem adapters

DoD: scoped profile adapter and approval workflow after PA MVP; standards adapters and optional ChaT/Project Manager/Ecosystem Control boundaries reviewed; Telegram remains post-MVP with separate credentials/scope.

## Redmi Note 15 Pro+ 5G experiment protocol

Тестировать на real consented device; recordings/corpus остаются вне Vault и source control.

- Record exact SKU/region, RAM/storage, SoC/GPU, Android/API/build, security patch, battery health и OEM battery/autostart restrictions; private lab evidence не копировать в public ADR.
- Fixed local Russian corpus: 30 s, 300 s, 1800 s; notes/monologues с English names, terms, projects, dates, numbers, code-switching, silence, corrections. Measure WER/CER, named-term accuracy, punctuation, timestamps, segmentation, edit latency.
- Compare Vosk, Russian sherpa-onnx и whisper.cpp tiny/base/small quantizations. Record checksum/license, first-load, RTF, peak RSS, storage, dropped audio, battery delta, temperature, throttling.
- Test Qwen3 0.6B/1.7B/4B quantizations through >=2 runtimes. Measure strict JSON validity, field accuracy, ambiguity/refusal, tokens/sec, RSS, battery, thermals; approval mandatory.
- Test screen-off, lock, Doze, battery saver, headset unplug, incoming call, process death, rotation, reboot, force-stop and denied/revoked microphone/notification permissions. Verify widget lifecycle and no recording after stop.
- Test notification channels, runtime permission, reminder delivery, exact/inexact alarms, reboot/time-zone rescheduling and disabled channels.
- Test short lab retention: audio, raw/superseded transcript, FTS rows, caches, thumbnails, sync tombstones; account for encrypted backups/copies.
- Inject sync faults: reordered/duplicated bundles, crash during apply, same-field offline edits, clock skew, revoked peer, corrupted bundle, retry. Verify auth, idempotence, conflict UI, deletion propagation, no plaintext/live-DB sync.

Acceptance is a lab report with measurements, reproducible versions/checksums, gaps and a decision per candidate. Until then defaults remain provisional.

## Non-goals

- Telegram integration or Telegram-first MVP.
- Autonomous sends, destructive actions or silent profile writes.
- Voice conversation and TTS/voice replies; post-MVP adapters only.
- BlogerAI implementation.
- Deep profile runtime integration before PA MVP.
- Cloud-first storage, mandatory central server, or live database-file sync.
- Final Redmi-specific model/runtime, Android API floor, laptop OS or licensing claim before experiments.

## Unresolved questions

- Exact Redmi SKU/RAM/SoC/Android build and minimum Android API acceptance floor?
- Retention defaults, legal hold and encrypted-backup semantics?
- Laptop OS and acceptability of a local always-on relay?
- Conflict UX and Lamport/HLC scheme sufficient without CRDT everywhere?
- Are GPL components acceptable only as separate process/app boundaries?
- Corpus targets and battery/thermal limits for STT/LLM acceptance?
- Must widget controls work from lock screen, and what reboot recovery UX is required?
