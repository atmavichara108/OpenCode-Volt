---
type: method
status: stable
tags: [method]
---
# Verifier Pattern

## Проблема
Агент-исполнитель сам себе судья: он «считает» задачу выполненной, потому что заинтересован закончить. Без внешней проверки качество дрейфует, баги и дыры безопасности просачиваются (DryRun 2026: Claude-агент дотащил IDOR и незащищённый destructive-endpoint до финала именно из-за отсутствия независимой проверки).

## Решение
Отдельный агент-верификатор, который НИЧЕГО не правит, только выносит вердикт PASS/FAIL против Definition of Done. Это паттерн evaluator из multi-agent архитектур Anthropic. Разделение ролей критично: тот, кто пишет, не должен оценивать сам себя.

## Реализация в OpenCode
Глобальный subagent в `~/.config/opencode/agent/verifier.md` (один на все проекты):

```
---
description: Strict acceptance verifier. Checks work against DoD. Returns PASS/FAIL, never edits.
mode: subagent
model: opencode-go/glm-5.2
temperature: 0.1
permission:
  edit: deny
  webfetch: deny
  bash:
    "*": deny
    "git diff*": allow
    "git log*": allow
    "npm run ci": allow
    "npm test*": allow
    "python -m pytest*": allow
---
You are a strict acceptance verifier. You NEVER fix or edit anything.
For each acceptance criterion: PASS/FAIL with concrete evidence (file:line, test name, output).
End with exactly one line: `VERDICT: PASS` or `VERDICT: FAIL`.
Partial completion is FAIL. Never soften the verdict.
If FAIL: numbered list of minimal fixes for the build agent.
```

## Когда применять / когда НЕ применять
- Применять: задачи с проверяемым DoD (тесты, CI, чёткие критерии). Идеально для SERPlux (бинарные критерии пайплайна) и dv-hub (npm run ci).
- НЕ применять: чисто исследовательские задачи без критериев — там вердикт PASS/FAIL бессмысленен.

## Verify-subagent acceptance — стандарт приёмки (P6 #34)

Порт семантики M Code — «verifier-pattern как машиностроимый гейт, acceptance
через независимый verify-subagent по diff/evidence» — замыкает самодекларацию:

- **Кто.** Независимый subagent-верификатор (не тот агент, что делал работу).
  Маркер «сделано» от исполнителя — не evidence.
- **Что проверяет.** Diff работавшего агента против acceptance boundary
  (задача/спека/DoD). Вердикт строится на concrete evidence
  (`file:line`, тест-нейм, вывод команды), а не на самодекларации.
- **Гейт.** `VERDICT: PASS` — приёмка; `FAIL` — нумерованный список
  минимальных правок исполнителю. Partial = FAIL, вердикт не смягчается.
- **Кэш.** Машиностроимые гейты (typecheck/lint/test) не гоняются заново на
  неизменённом дереве — см. `tools/verify-cache/verify.py` (tree-hash кэш,
  P6 #33). Оценочные вопросы остаются за verify-subagent, детерминированные
  — за кэшем.
- **Порядок.** Quality-review (`reviewer`, mutable work) предшествует
  acceptance (`verifier`). В [[vault]] это опрокидывается в orchestration
  protocol librarian (`[[.opencode/agent/librarian]]` § «Orchestration protocol»).

## Связанные
- Reference: [[agents]], [[permissions]]
- Используется в: [[closed-loop]] (verify-фаза)
- Модель: [[model-routing]] (почему именно sonnet, а не haiku)
- Кэш гейтов: `tools/verify-cache/verify.py` (P6 #33); референс семантики — [[01-Reference/mcode-desktop]] § «Детерминированная верификация»
- Внедрён в: [[SERPlux]] ✅, [[dv-hub]] ❌, [[vault]] ❌
