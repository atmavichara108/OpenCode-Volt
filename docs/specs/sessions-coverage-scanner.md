# Spec: Sessions Coverage Scanner (B4/B16)

---
spec: sessions-coverage-scanner
kind: task
status: active
owner-session: igraphv2 (ses_ef6d9ec61ffexSWJ2nYTfQwEW2)
spec-home: OpenCode-Vault/docs/specs/
mandate: Рудра, 2026-10-06 — «Спека для coverage-сканера (B4/B16) ок»; blessed в пакете с p-0003
sustainability: pass (zero-LLM, детерминированный, запуск по требованию)
verifier: owner-local (igraphv2), затем handoff Дирижёру
---

## S1. Цель

Детерминированный инструмент, который сам считает: какая доля работы,
выполненной в сессиях, отражена в граф-памяти (idea-graph). Замена ручного
full-scan на повторяемый скан.

## S2. Артефакты

- `tools/idea-graph/sessions-coverage.mjs` — сканер (zero-LLM).
- Отчёт: `generated/sessions-coverage.json` + компактный markdown (gitignored
  generated/, как у observer.py-паттерна).

## S3. Входы (read-only)

- `~/.local/share/opencode/opencode.db` (и только read-only подключение;
  WAL-нестабильность честно учитывать: снапшот+время, без правки).
- `04-Memory/idea-graph/nodes.jsonl`, `edges.jsonl`, `protocol.jsonl`
  (текущая ревизия, hash фиксируется в отчёте).

## S4. Метод (детерминированный, без LLM)

1. Собрать сессии проекта Vault по фильтру времени (по умолчанию ≥ 2026-10-04,
   флагом задаётся окно).
2. Для каждой сессии: заголовок + текст сообщений → детерминированное
   извлечение ключевых строк (список правил в скрипте; магии и случайных
   эвристик на LLM нет).
3. Сопоставить с узлами `stream-intent-*` (label/essence) по литеральному
   иSlug-совпадению; результат per-session: covered / repeat-process / out-of-scope.
4. Правила уже канонизированы: p-0003 (повтор-процесс — отдельный класс,
   не missing), recruiting-hr/TG — отдельный memory scope (исключены из
   знаменателя PAE-метрики и показаны отдельной строкой).
5. Агрегаты: прямое покрытие; с учётом p-0003; PAE-знаменатель.

## S5. Ограничения

- Никаких записей в idea-graph (сканер read-only к графу).
- Нет LLM-вызовов; никаких сетевых обращений.
- tokens: unknown всегда (в БД токен-телеметрии нет — фиксировать как
  unknown, байтовую метрику помечать как прокси).
- Не обходить permission; недоступные таблицы → честный BLOCKED в отчёте.

## S6. Acceptance

1. Прогон на актуальной БД даёт числа, совместимые с ручным full-scan
   (68 сессий; прямое ~74%; p-0003-скорр. в границах 78–88%) — расхождения
   объясняются в отчёте, не сглаживаются.
2. Повторный прогон на том же снапшоте даёт идентичный вывод
   (детерминизм).
3. Локальный verifier PASS + handoff Дирижёру.
4. В idea-graph ничего не изменилось (hash до/после совпадает).

## S7. Provenance

Каждый запуск: timestamp, hash БД-снапшота (wc), hash граф-файлов,
версия окна/фильтра — в шапке отчёта.
