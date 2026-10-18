---
type: research-case
title: Институт — внешний кейс: архитектура ИИ-агентов (NVIDIA-стек, Manjaro)
status: draft
timestamp: 2026-10-13
project: OpenCode-Vault / dotfiles
source: "техотчёт «Архитектура и инфраструктура ИИ-агентов конфиденциального уровня в среде Linux (Manjaro)», передан Rudra в Институт Передовых Технологий 2026-10-13 (R&D этап), basis: quoted"
related:
  - 06-Audits/2026-10-13-ship-research-registry.md
  - 06-Audits/2026-10-07-lab-queue.md
  - 01-Reference/providers.md
---

# Внешний кейс: NVIDIA-стек для ИИ-агентов (Manjaro)

Институт принял внешний кейс (первый по мандату). Провена проверка фактов живым
веб-поиском 2026-10-13; классификация — по компетенциям сети Корабля.

## Provenance

- Источник: слово Rudra 2026-10-13 — техотчёт передан «в Институт передовых
  технологий (R&D этап)»; полный текст — в сессии-носителе Института
  (ses_ecb58b307ffeqrigRxoUEWoXZs).
- Статус: принят к исследованию; вердикт — «годен частично» (см. ниже).
- Оговорка: приложения-«ссылки» в исходном отчёте — Gmail sync-артефакты
  (mail.google.com/mail/?extsrc=sync...), никуда не ведут; как evidence НЕ
  приняты и в артефакт не включены.

## Проверка фактов (веб-поиск 2026-10-13)

| Утверждение отчёта | Вердикт | Evidence |
|---|---|---|
| NVIDIA NemoClaw — платформа безопасных агентов (OpenShell, Docker, расширение OpenClaw) | ПОДТВЕРЖДЕНО | github.com/NVIDIA/NemoClaw, docs.nvidia.com/nemoclaw/user-guide/openclaw — open-source reference stack; Docker + K3s, policy-слои внутри контейнера |
| Изоляция NemoClaw небезупречна | ПОДТВЕРЖДЕНО (риск) | lasso.security: эксфильтрация данных и config poisoning из sandbox; reddit r/LocalLLaMA: обход изоляции |
| NVIDIA Build: 1000 кредитов / 40 RPM free tier | ПОДТВЕРЖДЕНО | forums.developer.nvidia.com, обзоры NIM free tier |
| Расширение до 5000 кредитов / 200 RPM «при верификации корпоративной почтой» | ЧАСТИЧНО | существует процесс запроса на developer-форумах NVIDIA (Credit & Rate-Limit Increase Request), не автоматическое расширение; ответы на форуме указывают, что free-tier RPM-апгрейд не гарантирован |
| deepseek-v4.1-flash (заявлено 552B MoE, 8B активных) | МОДЕЛЬ ДОСТУПНА у нас (opencode-go/deepseek-v4.1-flash); параметры [проверить] | каталог сессий/claims; размерность — не подтверждена |
| nemotron-3.5-lightning-30b-a3b | В Zen-каталоге есть nemotron-3.5-lightning-free; A3B-вариант [проверить] | facts.md (2026-09-25) |
| nemotron-3.5-content-safety как модель-актуатор | [проверить] — поиском в этой сессии не подтверждён | — |
| cosmos3-nano (NVIDIA Cosmos, physical AI) | Семейство NVIDIA Cosmos реально; nano-вариант [проверить] | — |
| DGX Spark (GB10 Grace Blackwell, 128 ГБ) | ПОДТВЕРЖДЕНО как продукт (CES 2025); перспектива, не текущая задача | — |
| TensorRT-LLM (локальный прирост 2–4x) | Инструмент реален; применимость на нашем железе (ThinkPad P51, Quadro старого поколения) [проверить] | — |
| Cloudflare Workers AI / Mistral La Plateforme / Together AI / GitHub Models | Провайдеры реальны; Mistral уже 4-й провайдер OpenCode (facts); остальные — новые кастом-провайдеры (паттерн LinaliAPI) | facts.md, 01-Reference/providers |

## Классификация по сети Корабля

**Уже покрыто (дубль, отброшено):** модели deepseek/nemotron в каталогах
(T-130, T-177, model-watch T-178); Mistral-провайдер; providers.md;
JustDoWork-шим (отказоустойчивость канала уже решается).

**Кандидаты в Ability Lab (изолированная проверка; решение Rudra):**
1. NemoClaw/OpenShell-песочница — сравнить с нашей permission-моделью
   (opencode.json гейты, main-protector, env-guard); известные обходы —
   обязательная часть протокола испытания.
2. Content-safety модель-актуатор на входном шлюзе (перехват prompt injection
   моделью, а не pattern-based) — A/B против input-security.ts.
3. cosmos3-nano — physical AI: проба на задачу устойчивых экосистем
   (пермакультура).

**Инженерному Центру (инфраструктура):**
- Кастом-провайдеры Cloudflare Workers AI / Together AI / GitHub Models —
  по паттерну LinaliAPI (T-130 расширяется); fallback-карта — развитие
  01-Reference/providers.md.
- Запрос квоты NVIDIA Build 5000/200 — операторская верификация домена
  (процесс на developer-форумах; free-tier не гарантирован).

**Оператору (Rudra), отдельно:** заявка NVIDIA Inception Program
(гранты DGX Cloud, скидки DGX Spark) — решение о подаче.

## Вердикт Института

Кейс признан ГОДНЫМ ЧАСТИЧНО: три позиции — кандидаты в очередь Ability Lab
(по слову Rudra), провайдерско-квотовая часть — Инженерному Центру, модельные
дубли отброшены. Сомнительные утверждения помечены [проверить] и не
переносятся дальше по пайплайну без закрытия.
