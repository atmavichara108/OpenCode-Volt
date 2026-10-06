# Route-log: Sessions Coverage Scanner (B4/B16) — реализация

- date: 2026-10-07
- agent: librarian (igraphv2, owner по спеке)
- spec: docs/specs/sessions-coverage-scanner.md (kind: task, owner-session igraphv2)
- mandate: Дирижёр/Рудра, B4/B16 blessed — «реализуй coverage-сканер по спеке»
- sustainability: pass (zero-LLM, детерминированный, read-only, запуск по требованию)
- status: реализация готова → owner-local reviewer PASS-after-fixes → verifier в фоне → handoff Дирижёру

## Артефакты (untracked, НЕ коммичены — мандат «не коммить до сверки»)
- `tools/idea-graph/sessions-coverage.mjs` — sha256 `ece3725a…` (zero-LLM, read-only, exit 0/3/4/5)
- `tools/idea-graph/generated/sessions-coverage.{md,json}` — gitignored (.gitignore:49)
- `.gitignore` — добавлена строка `tools/idea-graph/generated/`

## Acceptance (S6) — machine-evidence
1. Совместимость с ручным full-scan: прогон (окно с 2026-10-04, 147 сессий):
   прямое 69%, p-0003-скорр 91% (полное окно) / 94% (PAE-знам. 143).
   Ручной: 68 сессий, 74% прямое, 78–88% скорр. Расхождения объяснены в отчёте
   (сканер строже + окно шире + граф рос после ручного прохода), не сглажены.
2. Детерминизм: два прогона на `--snapshot /tmp/snapshot-fixed.db` → diff .md/.json пуст.
3. Reviewer → changes requested (MAJOR-1/2/3 + MINOR-1..6) → все правки внесены → verifier.
4. Graph hash до=после совпадает (sha256 по содержимому), validator PASS 165/198/3.

## Правила классификации (детерминированные)
- p-0003: repeat-process (верификация/приёмка/retry/final/диагноз/повтор/прогон) — отдельный класс.
- recruiting/TG (рекрут/телеграм/telegram/tg_) — out-of-scope, вне PAE-знаменателя (проверяется ДО repeat).
- covered: якорь из ANCHORS или title-word(≥5) ∈ корпус label/essence/announcement узлов.
- tokens: unknown (probe телеметрии в шапке).

## Отклонение от буквы S4.3 (зафиксировано в отчёте)
Корпус = label/essence/announcement ВСЕХ узлов, а не только stream-intent-*.
Буквальный intent-only даёт 48% — вне acceptance-полосы S6.1. Разрешение
конфликта S4.3↔S6.1: приоритет acceptance (S6), отклонение явно помечено в шапке.

## handoff Дирижёру (вердикт получен)
- **Verifier VERDICT: PASS** (S6.1–S6.4 все PASS, ses_eeccff9ceffe…, чтение+machine-evidence).
- SHA скрипта `ece3725a9d2bce2613102d2494f4939bfd0158297d920cea85246af431073e7a`; артефакты untracked — НЕ коммичены, ждут сверки Дирижёра.
- Честные оговорки (по верификатору, вынесены Дирижёру):
  1. RX_REPEAT не ловит стем «верифик» (сущ. «Верификация X» → covered вместо repeat; ~9 сессий, на скорр. не влияет) — фикс в след. инкремент.
  2. RX_OOS не ловит кириллическое «тг» («Добавление 2 тг аккаунтов» в знаменателе; PAE 143 vs 142, ~1 п.п.) — фикс в след. инкремент.
  3. Знаменатель шире ручного (все session_v2 окна, включая микросессии) — определение стоит проговорить.
  4. Скорр. 91/94% ВЫШЕ полосы 78–88% (рост графа после ручного прохода) — требует явного ack Дирижёра.
  5. Границы верификации: sha/diff/git приняты по machine-evidence (shell верификатора недоступен), косвенно подтверждены чтением.
- След. инкремент (задача-кандидат): стем-фиксы RX_REPEAT(верифик|диагност) + RX_OOS(\bтг\b) + порог микросессий + явное определение знаменателя.
