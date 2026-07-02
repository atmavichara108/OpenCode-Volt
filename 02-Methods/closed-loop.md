---
type: method
status: stable
tags: [method]
---
# Closed Loop

## Проблема
Ведёшь агента вручную через каждый шаг: сделай → проверь → исправь → снова проверь. Тратишь время на оркестрацию того, что агент может делать сам. Альтернатива (open loop, полная свобода) жжёт токены и на задачах с размытыми критериями генерит мусор.

## Решение
Замкнутый цикл, спроектированный человеком заранее: фиксированные шаги, проверка на каждой итерации, жёсткая точка остановки. Агент сам крутит build→verify→fix, пока не PASS или пока не упрётся в лимит. Это «системный инженер строит петлю, а не промптит» (Steinberger, Addy Osmani 2026).

Ключевое отличие от open loop: путь задан заранее → укладывается в бюджет, не уходит в разнос.

## Реализация в OpenCode
Глобальная команда `~/.config/opencode/command/loop.md`:

```
---
description: Closed-loop implementation until acceptance passes (arg1=goal, arg2=ci command)
agent: build
---
Goal: $1
Verification command: $2

1. Implement the next increment toward the goal.
2. Invoke @verifier with goal, diff, and command `$2`.
3. If FAIL: apply ONLY the listed fixes, return to step 2.
4. If PASS: run `$2` once more, summarize, STOP.

HARD STOP after 5 verify cycles. If still FAIL, report blockers and STOP.
```

Использование:
- dv-hub: `/loop "DV-021 rate limit на magic-link" "npm run ci"`
- SERPlux: `/loop "labeler кэширует повторные URL" "python -m pytest -q"`

## Когда применять / когда НЕ применять
- Применять: задача с чётким DoD и быстрой проверкой (CI/тесты секунды-минуты).
- НЕ применять: проверка дорогая/долгая (петля множит её стоимость), или критерии размыты.
- `HARD STOP after 5` — не опционально. Это и бюджетный предохранитель, и защита от doom-loop.

## Связанные
- Reference: [[commands]], [[agents]]
- Зависит от: [[verifier-pattern]]
- Рамка задачи: [[context-as-docs]] (DoD берётся из спеки)
- Внедрён в: [[SERPlux]] ✅, [[dv-hub]] ❌, [[vault]] ❌
