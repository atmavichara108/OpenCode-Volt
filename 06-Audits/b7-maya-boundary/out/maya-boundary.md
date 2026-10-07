# B7: Maya-lint v2 dry-run — 8 репо (report-mode, координаты+категории)

- dict v2 sha=33a0b07c983c0a64…
- HEAD: AndroidOS@dd48ede, ChaT@c206360, OpenCode-Vault@c44fa86, TradingMind@4dff359, dv-hub@e803d02, recruiting-hr@a7b65a8, serp@d94b8a0, dotfiles@43b5258
- источник: файлы из HEAD (текстовые ≤512КБ) + git-log -200; whitelist словаря применён

## Итог по репо

| Репо | файлов | live | history | internal |
|---|---|---|---|---|
| AndroidOS | 46 | 18 | 0 | 0 |
| ChaT | 40 | 0 | 0 | 0 |
| OpenCode-Vault | 354 | 269 | 56 | 139 |
| TradingMind | 52 | 0 | 0 | 0 |
| dv-hub | 91 | 18 | 0 | 3 |
| recruiting-hr | 42 | 0 | 0 | 0 |
| serp | 114 | 1 | 0 | 0 |
| dotfiles | 181 | 27 | 0 | 34 |

Non-whitelisted hits: 565 (live=333, history=56, internal=176)
- отдельный finding: путей-носителей термина в координатах: 1 — сами имена файлов несут термин (переименование — зона проектных пайплайнов, сканер путей не чинит)

## FP-корзина (history+internal — в 2-недельный дайджест перед гейтом)

| bucket | репо | файл:строка | терм | категория |
|---|---|---|---|---|
| internal-infra | dotfiles | docs/decisions.md:417 | t09 | dashboard |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:32 | t09 | dashboard |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:32 | t09 | dashboard |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:64 | t01 | coordinating agent |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:64 | t02 | coordinating agent / senior agent |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:64 | t03 | world-simulator |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:64 | t04 | notification channel |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:64 | t09 | dashboard |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:65 | t09 | dashboard |
| internal-infra | dotfiles | docs/specs/maya-lint-v2.md:70 | t09 | dashboard |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:29 | t01 | coordinating agent |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:34 | t02 | coordinating agent / senior agent |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:39 | t03 | world-simulator |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:44 | t04 | notification channel |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:49 | t05 | feature-mining |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:54 | t06 | safe-mode migration |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:54 | t07 | safe-mode migration |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:59 | t07 | safe-mode migration |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:64 | t08 | community track |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:69 | t09 | dashboard |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:74 | t10 | M Code |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:79 | t11 | agent fleet |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:84 | t12 | agent fleet |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:89 | t13 | catalog |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:94 | t14 | changelog |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:99 | t15 | acceptance gate (raw to canon) |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:112 | t09 | dashboard |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:114 | t09 | dashboard |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:123 | t09 | dashboard |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:133 | t01 | coordinating agent |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:140 | t02 | coordinating agent / senior agent |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:147 | t03 | world-simulator |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:154 | t04 | notification channel |
| internal-infra | dotfiles | tools/maya-lint/dictionary.json:161 | t09 | dashboard |
| internal-infra | dv-hub | docs/decisions.md:43 | t09 | dashboard |
| internal-infra | dv-hub | docs/decisions.md:58 | t09 | dashboard |
| internal-infra | dv-hub | docs/decisions.md:59 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 02-Methods/git-worktree-isolation.md:64 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 02-Methods/model-routing.md:72 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 02-Methods/model-routing.md:81 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 02-Methods/model-routing.md:152 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 02-Methods/team-protocol.md:19 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 02-Methods/team-protocol.md:82 | t12 | agent fleet |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/archive/v1-2026-10-04/index.md:9 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/archive/v1-2026-10-04/index.md:10 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/archive/v1-2026-10-04/index.md:12 | t08 | community track |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/archive/v1-2026-10-04/index.md:12 | t12 | agent fleet |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/archive/v1-2026-10-04/index.md:12 | t14 | changelog |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:10 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:11 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:12 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:12 | t02 | coordinating agent / senior agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:15 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:17 | t10 | M Code |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:20 | t08 | community track |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:20 | t12 | agent fleet |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:20 | t13 | catalog |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:20 | t14 | changelog |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:23 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:28 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:33 | t06 | safe-mode migration |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:33 | t07 | safe-mode migration |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:62 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:62 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:62 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:62 | t10 | M Code |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:63 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:70 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:103 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:105 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/index.md:126 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:4 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:62 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:62 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:62 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:62 | t10 | M Code |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:63 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:64 | t06 | safe-mode migration |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:64 | t07 | safe-mode migration |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:80 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:80 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 04-Memory/idea-graph/README.md:81 | t15 | acceptance gate (raw to canon) |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-upgrade-planning-seed.md:119 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-upgrade-planning-seed.md:293 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-vibecoding-layer-audit.md:98 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-vibecoding-layer-audit.md:101 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-vibecoding-layer-audit.md:106 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-vibecoding-layer-audit.md:151 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-vibecoding-layer-audit.md:267 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-vibecoding-layer-audit.md:277 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-vibecoding-layer-audit.md:314 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-02-vibecoding-layer-audit.md:335 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:12 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:20 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:48 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:72 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:81 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:184 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:209 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:213 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:252 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-08-31-ecosystem-upgrade-plan-v2.md:268 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-01-dual-sdk-architecture.md:20 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-01-dual-sdk-architecture.md:42 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-01-dual-sdk-architecture.md:74 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:98 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:158 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:158 | t02 | coordinating agent / senior agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:159 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:161 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:163 | t11 | agent fleet |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:163 | t12 | agent fleet |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:164 | t15 | acceptance gate (raw to canon) |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:165 | t05 | feature-mining |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:166 | t06 | safe-mode migration |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:166 | t07 | safe-mode migration |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:167 | t08 | community track |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:168 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:170 | t14 | changelog |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:171 | t13 | catalog |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:189 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:189 | t05 | feature-mining |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-05-pae-phase1-readiness-audit.md:189 | t07 | safe-mode migration |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:79 | t13 | catalog |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:81 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:107 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:109 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:143 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:143 | t13 | catalog |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:144 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:150 | t13 | catalog |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:172 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:173 | t13 | catalog |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:175 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:184 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-game-mechanics-map-draft.md:193 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-memory-s8-live-test-draft.md:58 | t10 | M Code |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-memory-s8-live-test-draft.md:60 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-memory-s8-live-test-draft.md:83 | t02 | coordinating agent / senior agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-memory-s8-live-test-draft.md:84 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-pae-evolution-roadmap-draft.md:10 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-pae-evolution-roadmap-draft.md:17 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-pae-evolution-roadmap-draft.md:18 | t12 | agent fleet |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-pae-evolution-roadmap-draft.md:38 | t12 | agent fleet |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-pae-evolution-roadmap-draft.md:58 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-pae-evolution-roadmap-draft.md:83 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-pae-evolution-roadmap-draft.md:197 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-progression-xp-metatokens-draft.md:44 | t06 | safe-mode migration |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-progression-xp-metatokens-draft.md:44 | t07 | safe-mode migration |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-vibecoding-layer-object-audit-draft.md:46 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-vibecoding-layer-object-audit-draft.md:68 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-vibecoding-layer-object-audit-draft.md:206 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-06-vibecoding-layer-object-audit-draft.md:206 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-name-draft.md:49 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-name-draft.md:55 | t10 | M Code |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-name-draft.md:79 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-name-draft.md:79 | t02 | coordinating agent / senior agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-name-draft.md:109 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:5 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:10 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:21 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:35 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:36 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:36 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:36 | t10 | M Code |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:38 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:75 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:80 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-scene-world-voice-draft.md:80 | t02 | coordinating agent / senior agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-worlds-matrix-draft.md:18 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-worlds-matrix-draft.md:19 | t01 | coordinating agent |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-worlds-matrix-draft.md:20 | t03 | world-simulator |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-worlds-matrix-draft.md:21 | t04 | notification channel |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-worlds-matrix-draft.md:22 | t09 | dashboard |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-worlds-matrix-draft.md:28 | t12 | agent fleet |
| internal-infra | OpenCode-Vault | 06-Audits/2026-10-07-worlds-matrix-draft.md:42 | t09 | dashboard |
| history | OpenCode-Vault | git-log:147 | t02 | coordinating agent / senior agent |
| history | OpenCode-Vault | git-log:147 | t09 | dashboard |
| history | OpenCode-Vault | git-log:171 | t09 | dashboard |
| history | OpenCode-Vault | git-log:186 | t09 | dashboard |
| history | OpenCode-Vault | git-log:191 | t09 | dashboard |
| history | OpenCode-Vault | git-log:209 | t01 | coordinating agent |
| history | OpenCode-Vault | git-log:209 | t03 | world-simulator |
| history | OpenCode-Vault | git-log:209 | t04 | notification channel |
| history | OpenCode-Vault | git-log:230 | t01 | coordinating agent |
| history | OpenCode-Vault | git-log:298 | t09 | dashboard |
| history | OpenCode-Vault | git-log:305 | t09 | dashboard |
| history | OpenCode-Vault | git-log:347 | t09 | dashboard |
| history | OpenCode-Vault | git-log:360 | t09 | dashboard |
| history | OpenCode-Vault | git-log:380 | t09 | dashboard |
| history | OpenCode-Vault | git-log:382 | t09 | dashboard |
| history | OpenCode-Vault | git-log:397 | t09 | dashboard |
| history | OpenCode-Vault | git-log:399 | t09 | dashboard |
| history | OpenCode-Vault | git-log:401 | t09 | dashboard |
| history | OpenCode-Vault | git-log:405 | t09 | dashboard |
| history | OpenCode-Vault | git-log:407 | t09 | dashboard |
| history | OpenCode-Vault | git-log:412 | t09 | dashboard |
| history | OpenCode-Vault | git-log:609 | t09 | dashboard |
| history | OpenCode-Vault | git-log:627 | t09 | dashboard |
| history | OpenCode-Vault | git-log:640 | t09 | dashboard |
| history | OpenCode-Vault | git-log:656 | t09 | dashboard |
| history | OpenCode-Vault | git-log:674 | t09 | dashboard |
| history | OpenCode-Vault | git-log:687 | t09 | dashboard |
| history | OpenCode-Vault | git-log:699 | t09 | dashboard |
| history | OpenCode-Vault | git-log:723 | t09 | dashboard |
| history | OpenCode-Vault | git-log:726 | t09 | dashboard |
| history | OpenCode-Vault | git-log:746 | t09 | dashboard |
| history | OpenCode-Vault | git-log:746 | t09 | dashboard |
| history | OpenCode-Vault | git-log:753 | t09 | dashboard |
| history | OpenCode-Vault | git-log:777 | t09 | dashboard |
| history | OpenCode-Vault | git-log:809 | t09 | dashboard |
| history | OpenCode-Vault | git-log:813 | t09 | dashboard |
| history | OpenCode-Vault | git-log:821 | t09 | dashboard |
| history | OpenCode-Vault | git-log:831 | t09 | dashboard |
| history | OpenCode-Vault | git-log:838 | t09 | dashboard |
| history | OpenCode-Vault | git-log:845 | t09 | dashboard |
| history | OpenCode-Vault | git-log:853 | t09 | dashboard |
| history | OpenCode-Vault | git-log:868 | t09 | dashboard |
| history | OpenCode-Vault | git-log:875 | t09 | dashboard |
| history | OpenCode-Vault | git-log:881 | t09 | dashboard |
| history | OpenCode-Vault | git-log:890 | t09 | dashboard |
| history | OpenCode-Vault | git-log:895 | t09 | dashboard |
| history | OpenCode-Vault | git-log:912 | t09 | dashboard |
| history | OpenCode-Vault | git-log:928 | t09 | dashboard |
| history | OpenCode-Vault | git-log:937 | t09 | dashboard |
| history | OpenCode-Vault | git-log:953 | t09 | dashboard |
| history | OpenCode-Vault | git-log:963 | t09 | dashboard |
| history | OpenCode-Vault | git-log:968 | t09 | dashboard |
| history | OpenCode-Vault | git-log:977 | t09 | dashboard |
| history | OpenCode-Vault | git-log:986 | t09 | dashboard |
| history | OpenCode-Vault | git-log:1026 | t09 | dashboard |
| history | OpenCode-Vault | git-log:1052 | t09 | dashboard |

## Live-нарушения границы (кандидаты на фикс через проектные пайплайны)

| репо | файл:строка | коммит | терм | категория |
|---|---|---|---|---|
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:22 | — | t01 | coordinating agent |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:22 | — | t02 | coordinating agent / senior agent |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:22 | — | t03 | world-simulator |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:22 | — | t04 | notification channel |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:22 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:23 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:25 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:50 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:52 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:61 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:75 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:80 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-maya-lint-8repos.md:81 | — | t09 | dashboard |
| dotfiles | docs/handoffs/2026-10-06-sysop-team-hello.md:4 | — | t02 | coordinating agent / senior agent |
| dotfiles | docs/handoffs/2026-10-06-sysop-team-hello.md:43 | — | t09 | dashboard |
| dotfiles | docs/specs/done/pipboy-hotkey.md:3 | — | t09 | dashboard |
| dotfiles | docs/specs/done/pipboy-hotkey.md:10 | — | t09 | dashboard |
| dotfiles | docs/specs/done/pipboy-hotkey.md:14 | — | t09 | dashboard |
| dotfiles | docs/specs/done/pipboy-hotkey.md:19 | — | t09 | dashboard |
| dotfiles | docs/specs/done/pipboy-hotkey.md:43 | — | t09 | dashboard |
| dotfiles | docs/specs/done/pipboy-hotkey.md:57 | — | t09 | dashboard |
| dotfiles | docs/specs/done/pipboy-hotkey.md:63 | — | t09 | dashboard |
| dotfiles | docs/specs/done/pipboy-hotkey.md:71 | — | t09 | dashboard |
| dotfiles | opencode-global/.config/opencode/command/agents.md:2 | — | t09 | dashboard |
| dotfiles | opencode-global/.config/opencode/command/agents.md:6 | — | t09 | dashboard |
| dotfiles | opencode-global/.config/opencode/command/agents.md:8 | — | t09 | dashboard |
| dotfiles | qtile/.config/qtile/keys.py:62 | — | t09 | dashboard |
| AndroidOS | docs/pip-boy-product-blueprint.md:1 | — | t09 | dashboard |
| AndroidOS | docs/pip-boy-product-blueprint.md:11 | — | t09 | dashboard |
| AndroidOS | docs/pip-boy-product-blueprint.md:88 | — | t09 | dashboard |
| AndroidOS | docs/pip-boy-product-blueprint.md:172 | — | t09 | dashboard |
| AndroidOS | docs/research/evolution-applications.md:1 | — | t09 | dashboard |
| AndroidOS | docs/research/evolution-applications.md:5 | — | t09 | dashboard |
| AndroidOS | docs/research/jev-classifier.md:36 | — | t09 | dashboard |
| AndroidOS | docs/research/liya-audit.md:41 | — | t09 | dashboard |
| AndroidOS | docs/research/voice-transcriptor-audit.md:13 | — | t09 | dashboard |
| AndroidOS | docs/research/voice-transcriptor-audit.md:38 | — | t09 | dashboard |
| AndroidOS | docs/roadmap.md:5 | — | t09 | dashboard |
| AndroidOS | docs/roadmap.md:5 | — | t09 | dashboard |
| AndroidOS | docs/studio-interface-guide.md:6 | — | t09 | dashboard |
| AndroidOS | docs/studio-interface-guide.md:15 | — | t09 | dashboard |
| AndroidOS | docs/studio-interface-guide.md:20 | — | t09 | dashboard |
| AndroidOS | docs/studio-interface-guide.md:41 | — | t09 | dashboard |
| AndroidOS | docs/studio-interface-guide.md:42 | — | t09 | dashboard |
| AndroidOS | docs/widget-interface-guide.md:15 | — | t09 | dashboard |
| dv-hub | docs/specs/audit-drift-backlog.md:13 | — | t09 | dashboard |
| dv-hub | docs/specs/dev-loop-upgrade-2026-09.md:12 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:3 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:9 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:11 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:13 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:17 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:21 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:21 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:31 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:43 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:45 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:48 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:48 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:50 | — | t09 | dashboard |
| dv-hub | docs/specs/pipboy-synergy.md:63 | — | t09 | dashboard |
| dv-hub | docs/specs/README.md:42 | — | t09 | dashboard |
| dv-hub | docs/specs/README.md:50 | — | t09 | dashboard |
| OpenCode-Vault | .opencode/tools/ecosystem-next.ts:10 | — | t09 | dashboard |
| OpenCode-Vault | 00-INDEX.md:87 | — | t09 | dashboard |
| OpenCode-Vault | 00-INDEX.md:116 | — | t09 | dashboard |
| OpenCode-Vault | 01-Reference/commands.md:59 | — | t09 | dashboard |
| OpenCode-Vault | 03-Projects/vault.md:23 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/active-context.md:4 | — | t01 | coordinating agent |
| OpenCode-Vault | 04-Memory/active-context.md:15 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/active-context.md:21 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 04-Memory/active-context.md:22 | — | t03 | world-simulator |
| OpenCode-Vault | 04-Memory/active-context.md:23 | — | t01 | coordinating agent |
| OpenCode-Vault | 04-Memory/active-context.md:23 | — | t03 | world-simulator |
| OpenCode-Vault | 04-Memory/active-context.md:23 | — | t04 | notification channel |
| OpenCode-Vault | 04-Memory/active-context.md:25 | — | t06 | safe-mode migration |
| OpenCode-Vault | 04-Memory/active-context.md:25 | — | t07 | safe-mode migration |
| OpenCode-Vault | 04-Memory/active-context.md:25 | — | t10 | M Code |
| OpenCode-Vault | 04-Memory/active-context.md:52 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/active-context.md:68 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/active-context.md:87 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/active-context.md:340 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/active-context.md:372 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/active-context.md:394 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/facts.md:110 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/facts.md:719 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 04-Memory/facts.md:720 | — | t03 | world-simulator |
| OpenCode-Vault | 04-Memory/facts.md:721 | — | t01 | coordinating agent |
| OpenCode-Vault | 04-Memory/facts.md:722 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 04-Memory/facts.md:722 | — | t04 | notification channel |
| OpenCode-Vault | 04-Memory/facts.md:723 | — | t10 | M Code |
| OpenCode-Vault | 04-Memory/facts.md:754 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 04-Memory/route-log/2026-10-06-librarian-reply-draft.md:6 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 04-Memory/route-log/2026-10-06-librarian-reply-draft.md:250 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/route-log/2026-10-07-coordinator-verdicts.md:148 | — | t04 | notification channel |
| OpenCode-Vault | 04-Memory/session-log/2026-07-08.md:67 | — | t03 | world-simulator |
| OpenCode-Vault | 04-Memory/session-log/2026-07-13-part2.md:4 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-07-13-part2.md:12 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-07-13-part2.md:16 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-07-13-part2.md:29 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:5 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:6 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:13 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:32 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:49 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:71 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:104 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:126 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:156 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:181 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-08-31.md:213 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-06.md:57 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-06.md:77 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-12.md:4 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-12.md:12 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-12.md:19 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-12.md:19 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-12.md:28 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-17.md:4 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-17.md:15 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-17.md:21 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-17.md:24 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-25.md:10 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-09-25.md:16 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:6 | — | t01 | coordinating agent |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:6 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:6 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:13 | — | t03 | world-simulator |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:15 | — | t01 | coordinating agent |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:15 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:16 | — | t04 | notification channel |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:17 | — | t01 | coordinating agent |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:17 | — | t03 | world-simulator |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:21 | — | t01 | coordinating agent |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:25 | — | t06 | safe-mode migration |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:25 | — | t07 | safe-mode migration |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:30 | — | t10 | M Code |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:32 | — | t11 | agent fleet |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:32 | — | t12 | agent fleet |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:33 | — | t08 | community track |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:33 | — | t13 | catalog |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:34 | — | t14 | changelog |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:39 | — | t03 | world-simulator |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:40 | — | t09 | dashboard |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:41 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 04-Memory/session-log/2026-10-05.md:58 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:4 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:5 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:24 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:27 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:104 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:153 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:157 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:177 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:183 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:185 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:189 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:198 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:206 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:209 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:290 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:310 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:313 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:332 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/ecosystem-kanban-runbook.md:333 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-tui-smoke-test.md:3 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-tui-smoke-test.md:10 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-tui-smoke-test.md:21 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-tui-smoke-test.md:40 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-tui-smoke-test.md:87 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-v11-user-guide.md:3 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-v11-user-guide.md:4 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-v11-user-guide.md:9 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-v11-user-guide.md:11 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-v11-user-guide.md:33 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-v11-user-guide.md:86 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/pipboy-v11-user-guide.md:104 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/README.md:20 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/README.md:22 | — | t09 | dashboard |
| OpenCode-Vault | 07-Runbooks/vibecoding-changelog.md:45 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:3 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:9 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:12 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:15 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:20 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:24 | — | t04 | notification channel |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:27 | — | t04 | notification channel |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:34 | — | t04 | notification channel |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:39 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/2026-10-06-pipboy-retrospective-vision.md:48 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | 99-Inbox/vault-upgrade-research-2026-08-02.md:1450 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/vault-upgrade-research-2026-08-02.md:1526 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/vault-upgrade-research-2026-08-02.md:1545 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/vault-upgrade-research-2026-08-02.md:1548 | — | t09 | dashboard |
| OpenCode-Vault | 99-Inbox/vault-upgrade-research-2026-08-02.md:1554 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/agent-debug-budget-guard.md:14 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/agent-debug-budget-guard.md:113 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/dotfiles-doomone-removal-handoff.md:13 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/dotfiles-doomone-removal-handoff.md:62 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/dotfiles-doomone-removal-handoff.md:80 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/ecosystem-registry.md:18 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/ecosystem-registry.md:149 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/ecosystem-registry.md:170 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/ecosystem-registry.md:200 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/ecosystem-registry.md:209 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/ecosystem-registry.md:217 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/git-freed.md:95 | — | t01 | coordinating agent |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:6 | — | t01 | coordinating agent |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:10 | — | t01 | coordinating agent |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:80 | — | t03 | world-simulator |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:83 | — | t01 | coordinating agent |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:83 | — | t02 | coordinating agent / senior agent |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:86 | — | t04 | notification channel |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:87 | — | t10 | M Code |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:91 | — | t11 | agent fleet |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:91 | — | t12 | agent fleet |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:97 | — | t01 | coordinating agent |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:106 | — | t06 | safe-mode migration |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:106 | — | t07 | safe-mode migration |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:112 | — | t07 | safe-mode migration |
| OpenCode-Vault | docs/specs/idea-graph-v2.md:145 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/model-dashboard-models-module.md:3 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/model-dashboard-models-module.md:4 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/model-dashboard-models-module.md:4 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/model-dashboard-models-module.md:13 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/model-dashboard-models-module.md:19 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/model-dashboard-models-module.md:71 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pae-phase1-readiness.md:16 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:4 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:9 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:18 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:30 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:35 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:44 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:48 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:62 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:67 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:75 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:75 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:80 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-hotkey-conflict-audit.md:85 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-tui-plugin-research.md:51 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8-rethink.md:3 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8-rethink.md:4 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8-rethink.md:5 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8-rethink.md:8 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8-rethink.md:55 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8-rethink.md:159 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:3 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:5 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:8 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:24 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:30 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:44 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:64 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:149 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/pipboy-v8bis-ux.md:181 | — | t14 | changelog |
| OpenCode-Vault | docs/specs/README.md:16 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/README.md:28 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/README.md:78 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:1 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:4 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:12 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:19 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:36 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:38 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:43 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:63 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:66 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:77 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:134 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:195 | — | t14 | changelog |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:196 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/report-tui-upgrade-2026-09-12.md:216 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/roel-manifest.md:22 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/roel-manifest.md:23 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/roel-manifest.md:34 | — | t09 | dashboard |
| OpenCode-Vault | docs/specs/roel-manifest.md:50 | — | t09 | dashboard |
| OpenCode-Vault | docs/vibeos/index.html:6 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:107 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:120 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:120 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:125 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:144 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:145 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:146 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:147 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:148 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:148 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:149 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:152 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:153 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:156 | — | t09 | dashboard |
| OpenCode-Vault | TASKS.md:181 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/actions.py:2 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/actions.py:2 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/actions.py:44 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/actions.py:243 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/actions.py:966 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/actions.py:972 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/actions.py:982 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/app/core/App.js:660 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/app/core/Module.js:2 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/app/core/Workspace.js:3 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/app/modules/BrowserModule.js:10 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/app/modules/UpgradeModule.js:37 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/data.json:361 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/index-v10.html:6 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/index.html:6 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/index.html:10 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/pipboy.py:2 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/pipboy.py:2 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/pipboy.py:4 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/pipboy.py:21 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/pipboy.py:468 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:18 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:26 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:122 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:132 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:151 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:153 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:345 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:373 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:378 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:657 | — | t09 | dashboard |
| OpenCode-Vault | tools/ecosystem-map/registry.json:671 | — | t09 | dashboard |
| OpenCode-Vault | tools/version-oracle/oracle.py:21 | — | t09 | dashboard |
| OpenCode-Vault | tools/version-oracle/README.md:21 | — | t09 | dashboard |
| OpenCode-Vault | VibeOS.md:146 | — | t09 | dashboard |
| OpenCode-Vault | VibeOS.md:255 | — | t09 | dashboard |
| OpenCode-Vault | VibeOS.md:641 | — | t09 | dashboard |
| OpenCode-Vault | VibeOS.md:685 | — | t09 | dashboard |
| serp | scripts/serpctl.py:187 | — | t09 | dashboard |
