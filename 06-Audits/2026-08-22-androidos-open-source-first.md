---
type: decision / research note
project: AndroidOS
status: planning
date: 2026-08-22
---
# AndroidOS: open-source-first и research backlog

## Decision

AndroidOS сначала ищет зрелые open-source компоненты и строит тонкие adapters/contracts вокруг них. Собственная разработка допустима для glue, UX, domain model, privacy policy и отсутствующих интеграций. Ни один инструмент ниже не выбран: перед выбором нужны лицензия, Android compatibility, offline behavior, maintenance, model size/performance, security, data export and interoperability checks.

## Research dimensions

Для каждого кандидата фиксировать: license/attribution, repository health and release cadence, Android API/support floor, offline operation, data ownership/export, threat model, resource use, extension/API surface, packaging, test evidence, migration/exit path.

## Backlog

| Area | Questions to answer |
|---|---|
| STT | offline languages, streaming/chunking, punctuation, model size, transcript timestamps and correction loop |
| TTS | offline voices/languages, latency, licensing, optional post-MVP voice replies |
| Local LLM | on-device runtimes/models, quantization, privacy, battery/RAM, structured extraction reliability |
| Android widget/background/notifications | widget lifecycle, foreground/background limits, pause/resume recording, exact alarm and notification policy |
| Local DB | schema evolution, full-text search, event log, extensible entity types, encrypted storage and export |
| Encrypted phone-laptop sync | pairing, end-to-end encryption, retries, conflict resolution, delayed/offline queue, deletion/retention propagation |
| APIs/adapters | Vault/dotfiles/ChaT boundaries, auth, least privilege, audit log, Telegram post-MVP isolation |

## Guardrails

No secret, raw audio, transcript, token, or private profile fact belongs in public research notes or source control. A candidate becomes a decision only with evidence and an explicit ADR; otherwise mark `[проверить]`/`[уточнить]`.

## Snapshot

Проверено 2026-08-22 по официальным репозиториям/документации. Это candidate matrix, а не финальный стек. Даты в строках означают дату наблюдения источника, а не гарантию текущего релиза.

## Candidate matrix

### STT: Russian, offline

| Кандидат | Источник, лицензия, evidence | Android/offline и ресурсы | Интеграция | Риски и exit path |
|---|---|---|---|---|
| `whisper.cpp` | [repo](https://github.com/ggml-org/whisper.cpp), MIT; README и Android example, 2026-08-22 | Android и laptop, CPU/ARM NEON, quantization, VAD, timestamps; Whisper `tiny/base/small` memory примерно 273/388/852 MB, `medium` ~2.1 GB; русский есть у multilingual моделей | C/C++ API, JNI/Java binding, готовый Android example; batch и простой stream example | Длинные монологи дороже по CPU/батарее, decoding не полноценный streaming; качество/real-time на Redmi `[проверить]`. Exit: слой `Transcriber` с заменяемым backend и хранением аудио отдельно |
| `sherpa-onnx` | [repo](https://github.com/k2-fsa/sherpa-onnx), Apache-2.0; docs/repo, 2026-08-22 | Offline, Android/WearOS/Linux, streaming и non-streaming ASR, VAD, punctuation; опубликованы русские `zipformer`, NeMo CTC/transducer модели; размер/RTF каждой модели `[проверить]` | Kotlin/Java/C API, Android APK examples, ONNX model bundles | Много моделей имеют отдельные upstream/model licenses; русский latency/пунктуация на устройстве не подтверждены. Exit: ONNX model runner behind same transcript contract |
| `Vosk` | [repo](https://github.com/alphacep/vosk-api), Apache-2.0; README, 2026-08-22 | Offline Android, streaming zero-latency API, Russian models, small models advertised ~50 MB; вероятно самый дешёвый baseline для длинной непрерывной записи `[проверить]` | Java/Kotlin/Android binding, vocabulary adaptation, word results | Older Kaldi-era model quality and punctuation may be weaker than Whisper; exact Russian model license/quality/long-utterance behavior `[проверить]`. Exit: same audio/transcript adapter, preserve word timings only when available |

### TTS: Russian, offline

| Кандидат | Источник, лицензия, evidence | Android/offline и ресурсы | Интеграция | Риски и exit path |
|---|---|---|---|---|
| `RHVoice` | [repo](https://github.com/RHVoice/RHVoice), GPL-2.0; README, 2026-08-22 | Russian voices, Android TTS interface, small statistical voice footprint; offline | Use Android `TextToSpeech` engine/API; laptop via platform integrations | GPL boundary and each voice/data license must be audited; naturalness is below newer neural voices. Exit: Android TTS abstraction, optionally system engine |
| `Piper` / successor | [archived repo](https://github.com/rhasspy/piper), MIT code shown; archived 2025-10-06 and points to [OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl); evidence 2026-08-22 | Local neural TTS is suitable for laptop; Android packaging/runtime and Russian voice availability `[проверить]` | CLI/library or ONNX runtime adapter; no Android contract assumed | Archived upstream, successor is GPL-named, model/voice licenses vary and must be checked per voice. Exit: keep TTS provider interface and RHVoice/system fallback |
| `sherpa-onnx` TTS | [repo/docs](https://github.com/k2-fsa/sherpa-onnx), Apache-2.0 code; TTS Android APK/docs and model release links, 2026-08-22 | Offline TTS and Android APK, ONNX; official examples clearly expose some languages, Russian voice `[проверить]` | Kotlin/Java/C API, same runtime family as ASR | Russian model/voice availability and license not established by repo overview; model size/quality `[проверить]`. Exit: provider adapter, WAV/PCM boundary |

### Local LLM runtime/models

| Кандидат | Источник, лицензия, evidence | Android/offline and Redmi concerns | Интеграция | Риски and exit path |
|---|---|---|---|---|
| `llama.cpp` + GGUF | [repo](https://github.com/ggml-org/llama.cpp), MIT; Android build docs, OpenCL/Adreno backend marked available/in progress in README, 2026-08-22 | CPU/ARM, quantization, Android build, grammar/JSON and OpenAI-compatible server; 0.6B-4B models are plausible candidates, 8B may be slow/heavy. Redmi Note 15 Pro+ exact RAM/SoC/GPU driver, Vulkan/OpenCL viability and sustained thermals `[проверить]` | JNI/native library or localhost-like in-process service; structured extraction with grammar, model download/update separately | Runtime has broad moving surface; Qwen GGUF conversion/version compatibility. Exit: OpenAI-compatible `LocalModel` interface or another runtime |
| Qwen3 0.6B/1.7B/4B | [official repo](https://github.com/QwenLM/Qwen3), model weights Apache-2.0 per README, 2026-08-22 | Russian and 100+ languages; dense sizes include 0.6B, 1.7B, 4B; Qwen documents llama.cpp, ExecuTorch, MNN. Device performance/RAM and JSON extraction reliability on Redmi `[проверить]` | Use GGUF via llama.cpp, or export path via ExecuTorch/MNN; model cards and tokenizer must be pinned | “Apache-2.0” applies to listed weights but not every converted artifact/dependency; thinking mode costs latency/tokens. Exit: model-independent prompt/schema contract |
| `ExecuTorch` | [repo](https://github.com/pytorch/executorch), Apache-2.0; Qwen official README links Android example, 2026-08-22 | Designed for edge/mobile, Android; backend/delegate support and actual Redmi acceleration `[проверить]` | Export model, Java/Kotlin/C++ runtime, delegate-specific packaging | Export graph/operator gaps and model conversion maintenance; exit to llama.cpp GGUF or MNN |
| `MNN` | [repo](https://github.com/alibaba/MNN), Apache-2.0 `[проверить: current license/release]`; Qwen official repo points to MNN mobile path, 2026-08-22 | Mobile inference and Qwen3 support claimed by Qwen; Redmi NPU/GPU support and benchmark `[проверить]` | Native Android SDK/API, model conversion | Vendor-specific conversion and less generic artifact portability. Exit via model/LLM interface |

**Device caveat.** Redmi Note 15 Pro+ 5G model specifications, Android API level, available RAM, storage, thermal envelope, Adreno GPU backend and OEM battery policies were not established from a primary device specification in this pass. All model-size/performance claims for that phone are `[проверить]`; no device-specific selection is made.

### Android execution constraints

| Область | Official evidence and implication | Risk/experiment |
|---|---|---|
| Widget | [App widgets](https://developer.android.com/develop/ui/views/appwidgets), Android docs, checked 2026-08-22: widget is a small launcher surface and should dispatch actions/update state, not own recording process | `start/pause/resume/stop` should be idempotent intents into app/service; launcher behavior and update latency `[проверить]` |
| Recording/background | [Foreground services](https://developer.android.com/develop/background-work/services/fgs) and [background-start restrictions](https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start), Android docs, 2026-08-22 | Microphone capture needs foreground-service type/permission and visible notification; background-start restrictions, Android version and OEM policy can block flows. Start from user gesture/widget and test screen-off, lock, reboot, battery saver |
| Notifications | [Notifications](https://developer.android.com/develop/ui/views/notifications), Android docs, 2026-08-22 | Notification channels/runtime notification permission and user-disabled channels affect recording controls and reminders; use persistent recording notification, separate reminder channel |
| Alarms | [AlarmManager](https://developer.android.com/reference/android/app/AlarmManager), Android reference, 2026-08-22 | Exact alarms are constrained by permission/policy and are not a substitute for durable task state; reminders need persisted schedule plus rescheduling after reboot/time-zone change |

### Local database, search and event log

| Кандидат | Источник/license/evidence | Fit, integration and resources | Risks/exit path |
|---|---|---|---|
| SQLite + FTS5 | [SQLite](https://sqlite.org/), public domain; [FTS5](https://sqlite.org/fts5.html), checked 2026-08-22 | Mature Android/laptop relational store, FTS5 for transcript/entity search, easy export; event table can be append-only | Encryption absent by default; schema/event semantics are ours. Exit: SQL export/JSON event export |
| Room | [Android docs](https://developer.android.com/training/data-storage/room), AndroidX docs, 2026-08-22 | Kotlin DAO/schema migrations over SQLite, offline local DB, testable | Not itself encryption, FTS design and migrations remain application responsibility. Exit: underlying SQLite schema/API |
| SQLCipher | [repo](https://github.com/sqlcipher/sqlcipher), community BSD-3-Clause; README says 256-bit AES, HMAC/KDF, FTS5 build option; 2026-08-22 | Encrypted SQLite file, cross-platform format within major version, roughly 5-15% overhead claimed upstream; native integration cost | Key lifecycle, Android build/provider and major-version migration; no protection from unlocked-process access. Exit: SQLCipher export to SQLite/JSON after authenticated unlock |
| Automerge | [site](https://automerge.org/), MIT/Apache components `[проверить per package]`; official site, 2026-08-22 | Local-first CRDT, queued offline changes, history and byte-level transport independence; Java binding listed by site `[проверить maturity]` | CRDT document model is not query DB, deletion/retention and large audio do not fit; conflicts in reminders need domain policy. Exit: export materialized entities/events, keep DB as source |

### Phone-laptop delayed sync without own server

| Candidate/protocol | Source/license/evidence | Fit and integration | Risks/exit path |
|---|---|---|---|
| `Syncthing` transport | [repo](https://github.com/syncthing/syncthing), MPL-2.0; goals/docs/repo, 2026-08-22 | Encrypted peer-to-peer continuous file sync, Android wrappers exist, no application server required; can carry an encrypted export/change-log bundle | It syncs files, not records: concurrent DB file writes/corruption, conflict files, phone background limits and deletion propagation are serious risks. Exit: replace transport with another byte channel while keeping bundle format |
| `Automerge` over arbitrary bytes | [official site](https://automerge.org/), source/evidence 2026-08-22 | Offline changes queue and converge; transport can be Syncthing, direct LAN, USB or attachment; good fit for event/change documents | Pairing, key exchange, peer discovery, authentication, compaction and tombstone retention still need design; serverless does not mean zero coordination. Exit: export event stream to another CRDT or deterministic merge |
| CalDAV/CardDAV/WebDAV interoperability | [DAVx5 OSE](https://github.com/bitfireAT/davx5-ose), GPL-3.0; README, 2026-08-22 | Mature Android bridge for calendar/contacts/tasks; syncs with any compatible server, local providers; useful integration boundary, not private PA backend | Requires a server/provider, protocol semantics do not cover arbitrary entities or raw audio; deletion/conflict semantics differ. Exit: retain ICS/vCard/task export |

### Existing apps/protocols to integrate

| Candidate | Source/license/evidence | Worth integrating | Risks/exit path |
|---|---|---|---|
| Tasks.org | [repo](https://github.com/tasks/tasks), GPL-3.0; Android, desktop alpha, F-Droid and CalDAV-oriented project evidence, 2026-08-22 | Mature task UX, reminders, recurrence, notifications and Android codebase; possible task export/CalDAV adapter rather than rebuilding task UI | GPL integration boundary, app data model and sync assumptions; does not model all PA entities. Exit: iCalendar/VTODO/CalDAV export |
| Joplin | [repo](https://github.com/laurent22/joplin), MIT `[проверить current repo license and subcomponents]`; repository URL recorded, detailed README not retrieved in this pass | Existing cross-platform notes, search, attachments and sync concepts; candidate for note/export interoperability | Own sync/data model and plugin boundary need audit; not a contacts/calendar system and raw-audio retention must not be inherited. Exit: Markdown/JSON/export adapter |
| DAVx5 + CalDAV/CardDAV | [repo](https://github.com/bitfireAT/davx5-ose), GPL-3.0; 2026-08-22 | Use standards for events, contacts and tasks where useful; avoid proprietary server coupling | Requires compatible server and user credentials; not a general encrypted delayed-sync solution. Exit: direct ICS/vCard/VTODO files |
| iCalendar, vCard, VTODO | [RFC 5545](https://www.rfc-editor.org/rfc/rfc5545), [RFC 6350](https://www.rfc-editor.org/rfc/rfc6350), [RFC 5545 VTODO](https://www.rfc-editor.org/rfc/rfc5545); standards evidence 2026-08-22 | Portable export/import and interop with calendar/contact/task software; low integration surface | Expressiveness, time zones, recurrence and conflict semantics are narrower than PA domain. Exit already is the interchange format |

## Evaluation experiments

1. **Device envelope:** obtain exact Redmi SKU/build/RAM, install test APK, record 30/300/1800-second Russian speech with screen off, locked phone, battery saver and thermal logging. Measure real-time factor, first-load time, peak RSS, battery and dropped audio. Compare Vosk, `sherpa-onnx` Russian models and `whisper.cpp` multilingual `tiny/base/small` quantizations.
2. **Transcript quality:** fixed consented corpus of short notes and long monologues with names, dates, numbers, code-switching and silence. Score WER/CER, punctuation, timestamps, segmentation, resumability and editable-text latency. Do not upload corpus.
3. **TTS:** compare RHVoice, system offline Russian engine, `sherpa-onnx` Russian model `[проверить]` and Piper successor `[проверить]` on latency, intelligibility, size, voice license and Android API behavior.
4. **LLM extraction:** run Qwen3 0.6B/1.7B/4B quantizations through at least two runtimes where possible. Test strict entity JSON, dates/time zones, ambiguity, refusal to invent, 20-turn context, peak memory, tokens/sec and sustained thermal behavior. Human confirmation remains mandatory.
5. **Lifecycle:** widget action state machine under process death, rotation, reboot, Doze, force-stop, permission denial, headset unplug and incoming call. Verify no recording continues after stop and retention deletion removes raw audio, transcript, indexes, thumbnails and sync tombstones according to policy.
6. **Sync fault injection:** two independent device databases; create/edit/delete same entities offline, reorder delivery, duplicate bundles, crash during apply, clock skew and revoked device. Verify authenticated pairing, idempotence, no plaintext transport, deterministic conflict UI and deletion propagation. Never sync a live SQLite file.
7. **Interop:** export/import ICS, VTODO, vCard, Markdown/JSON and event log; compare Tasks.org/DAVx5/Joplin boundaries and verify that replacing every candidate backend leaves domain data readable.

## Unresolved questions

- Exact Redmi Note 15 Pro+ 5G SKU, RAM, SoC/GPU, Android version, OEM restrictions and boot/runtime capabilities `[проверить]`.
- Is laptop Linux, Windows or macOS, and is a local always-on relay explicitly disallowed, or only a self-operated application server?
- Required retention defaults for raw audio/transcripts, legal hold/export behavior, and whether encrypted backups count as retained copies.
- Canonical event ID, device ID, Lamport/HLC ordering, tombstone retention and conflict UX for entities and reminders.
- Whether GPL components are acceptable as separate processes/apps, or only permissive libraries are allowed.
- Which Russian voice/model artifacts have redistributable licenses, checksums and reproducible download sources.
- Minimum Android API and whether widget controls must work from lock screen.

## Sources and scope

Primary sources consulted: official repositories/docs linked in each matrix row; Android developer/reference pages; RFC pages for interchange formats. GitHub mirrors occasionally exposed current repository metadata more clearly than rendered raw files. No application code was inspected or changed, no model/audio/private data was stored, and no final selection is claimed.
