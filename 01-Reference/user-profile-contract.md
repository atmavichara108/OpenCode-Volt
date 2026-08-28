---
type: contract
title: Канонический профиль пользователя
status: planning
updated: 2026-08-22
---
# Канонический профиль пользователя — Max Rudra

## Source of truth

Канонический расширенный профиль находится в `/home/rudra/dotfiles/.opencode/memory/user-profile.md`. Это один источник фактов для Vault, dotfiles/global agents, ChaT, AndroidOS и BlogerAI. `docs/user-profile.md` в dotfiles, карточки проектов и адаптеры могут содержать только ссылку, scope и operational preferences, но не вторую копию фактов.

## Scoped access

| Consumer | Default access | Write policy |
|---|---|---|
| Vault/librarian | read profile and project-relevant preferences | propose changes; explicit user confirmation before canonical write |
| dotfiles/global agents | read profile for UX and operating preferences | profile-governor only, explicit confirmation, append/change review |
| ChaT | first-class consumer: read the minimum relevant context for interviews, decisions, planning and operations | may propose profile changes and, after approval, write an explicitly scoped change through `profile-governor`; ChaT facts stay in ChaT registers and never sync automatically |
| AndroidOS/Personal Assistant | local user-approved subset; private data local by default | user-controlled export/sync; no implicit profile upload |
| BlogerAI | explicit selected history/profile scope per content task | no autonomous publication or scope expansion |

## Contract rules

- Canonical identity: `Max Rudra`; aliases are references, not separate profiles.
- Secrets, tokens, raw audio and private credentials are never profile facts and never exposed by an agent.
- Consumers request the minimum fields needed and record provenance when storing a derived fact.
- Changes are proposed as a diff with reason and affected consumers; no destructive rewrite or silent merge.
- Conflicting facts are marked `[уточнить]` and resolved at the canonical source.

## ChaT consumer contract

ChaT is the user's startup and a full knowledge/operations consumer of the profile, not a passive read-only adapter. It may use profile context for:

- **Read:** interview framing, participant and relationship context, project priorities, working preferences, decision context and operational constraints relevant to the current ChaT task.
- **Write proposal:** propose a new or changed profile fact when ChaT work produces durable user-level knowledge; include the exact field, proposed value, reason, source reference, timestamp and affected consumers.
- **Approved write:** after explicit user approval, `profile-governor` applies the minimal diff to the canonical profile. ChaT records only its local fact/register and provenance; it does not maintain a second profile copy.

Every ChaT read/write uses a declared scope, minimum necessary fields, and provenance (`source`, `observed_at`, `confidence/status`, and `canonical-or-derived` distinction). Project facts, hypotheses, decisions and participant data remain in their ChaT registers unless the user explicitly promotes a fact to the canonical profile.

Approval is required for every canonical write, including profile changes proposed by ChaT or detected during drift review. No consumer may silently merge, overwrite, broaden scope, export private data, or write secrets. Rejected, ambiguous or conflicting proposals remain proposals marked `[уточнить]`.

## Proactive governance

`profile-governor` is a proactive global agent, but proactivity is operational rather than magical. It runs only when invoked explicitly or connected to a configured hook, event, or scheduled check. Its checks may:

- periodically or event-triggered reconcile the canonical profile with scoped references in Vault, dotfiles, ChaT and AndroidOS;
- detect stale, contradictory or missing-provenance facts and produce an evidence-based report;
- propose minimal profile changes, consumer adapter updates and approval requests;
- report drift between declared contracts and actual adapters/registers without silently changing any file.

It never performs a quiet canonical write, never treats a project register as authority without promotion approval, and never reads or emits secrets, tokens, credentials, raw audio or unrelated private data.
