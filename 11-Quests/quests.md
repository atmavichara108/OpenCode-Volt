---
type: Registry
title: Реестр квестов
ssot: true
timestamp: 2026-10-23
owner: ЦУ
---

# Реестр квестов

| ID | Квест | Статус | Владелец | Предусловие |
|---|---|---|---|---|
| **Q-001** | путь разработчика NVIDIA | active | ЦУ + владелец | — |
| Q-001.1 | заявка в NVIDIA Inception (бесплатные cloud credits) | ready | ЦУ (текст) + владелец (подача) | аккаунт NVIDIA ✓ |
| Q-001.2 | курс «Securing Agents With OpenShell and NemoClaw» | ready | владелец (прохождение) + ЦУ (разбор) | — |
| Q-001.3 | забрать NIM-кредиты и проверить целостность на Nemotron | ready | ИЦ | Q-001.1 или free-кредиты |
| Q-001.4 | вытянуть все письма NVIDIA + разобрать анонсы | active | ЦУ | mail-hub ✓ |
| Q-001.5 | кейс Корабля для блога/форума NVIDIA | locked | ИПТ + ЦУ | Q-001.2 |
| Q-001.6 | NGC/blueprints разведка (NeMo, Dynamo, NIM) | ready | ИПТ | — |
| Q-001.7 | платный dedicated NIM — оценка целесообразности | parked | ЦУ | решение владельца о бюджете |
| **Q-002** | метахаб квот: 10 компаний (Mistral, Google, Groq, Cohere, SambaNova, OpenRouter, Cerebras, Together, Cloudflare, HF) | ready | ЦУ | письмо NVIDIA ✓ |
| Q-002.1 | рассылка писем по 10 адресатам | ready | ЦУ | шаблон ✓ |
| **Q-003** | инфраструктурный апгрейд ЦУ (снять узкое горло) | locked | ИЦ | положительный ответ NVIDIA (слово владельца) |
| **Q-004** | rudrakshas: ступени А2→А3 | locked | ИЦ + Лаба | слово владельца |
| **Q-005** | толковый ротатор моделей (УАС, спец-отдел) | active | УАС (ses_e9884e4a) + ИЦ | УАС в строю ✓ (Р-023) |
| Q-005.1 | сверка каталога: providers.json ↔ model-catalog.json ↔ opencode.jsonc (отчёт расхождений) | active | УАС | база есть (22 провайдера / 9 в каталоге) |
| Q-005.2 | живой health: probe по расписанию + provider-health.jsonl | ready | УАС | probe.py работает |
| Q-005.3 | доказать failover на живом прогоне (провайдер выключен → агент переехал → запись в журнале) | ready | УАС + ИЦ | Q-005.1 |
| Q-005.4 | лимиты и приватность по каждому провайдеру в каталоге (RPM/RPD/кредиты, обучение на данных) | ready | УАС | (Mistral: $10/мес; Google: standing free tier; Groq: 1000 req/день, 200k ток/день; Cohere: 1000 вызовов/мес; SambaNova: standing free tier; OpenRouter: 17 моделей бесплатно; Cerebras: trial, сверхскорость; Together AI: \$25-50 старт; Cloudflare: free tier; HF: ежемесячные кредиты) |
| Q-005.5 | журнал переключений append-only (кто/когда/почему) | ready | УАС | Q-005.3 |
| Q-005.6 | публичный отчёт «лучший провайдер по роли» (median/p95) → вход для Q-002 | active | УАС | Q-005.4 (лимиты/приватность заполнены) |

## Легенда статусов
active — делается сейчас · ready — можно начинать в любой момент ·
locked — ждёт предусловие · parked — отложено сознательно · done — закрыт с evidence
