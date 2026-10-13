---
type: research-inventory
title: Инвентаризация существующей работы Института Передовых Технологий
status: draft
timestamp: 2026-10-13
project: dotfiles / OpenCode-Vault
source: "researcher-инвентаризация (ses_ecb65d4c9ffeY6W153OzIy9LX7) по слову Rudra «уже есть большая работа для Института»"
related:
  - 06-Audits/2026-10-13-ship-research-registry.md
  - 06-Audits/2026-10-07-lab-queue.md
  - 04-Memory/idea-graph/nodes.jsonl
---

# Инвентаризация работы Института

Сессия-носитель Института не создана; инвентаризация — подготовка к её запуску.
Критерий отбора: исследования передовых технологий / внешние кейсы (компетенция
Института), не инфраструктура (Инженерный Центр), не испытания (Ability Lab),
не багфикс (Мастерская), не хранение (Библиотека).

## Таблица инвентаря

| # | Артефакт (путь/узел) | Что это | Статус | Provenance | Релев. | След. шаг |
|---|---|---|---|---|---|---|
| 1 | узел `stream-intent-040` (idea-graph/nodes.jsonl:184) | Исследование всех трендов памяти/кэша/оптимизации контекста; «возможно добавит сессию — представителя Института» | candidate, resolution: accepted | rudra-directive 2026-10-07 | прямая — стержневая работа Института | в реестр как главный актив; заведение узла «представитель Института» |
| 2 | узел `world-entity-veldora-two-layers` (nodes.jsonl:204) | «После исследования 040… возможно воплощение Вельдоры станет появлением института» | accepted | rudra-directive 2026-10-09 | прямая | в реестр (отсутствует) |
| 3 | `dotfiles/.opencode/memory/research/2026-10-13-hot-memory-viability.md` | И-10: состоятельность горячей памяти → И-11 спека → И-12 реализация | И-10 done | заказ, 2026-10-13 | смежная | реестр уже содержит (строка 27) |
| 4 | `dotfiles/.opencode/memory/research/2026-10-14-mcode-lab-bridge.md` | И-33: мост mcode↔opencode, барьеры портирования | draft | 2026-10-14 | смежная (Инженерный/Lab L1) | реестр (строка 25) |
| 5 | `dotfiles/.opencode/memory/research/2026-10-14-wave3-versioning-philosophy.md` | И-30 vflight + И-34 структурализм | draft | Волна 3, 2026-10-14 | И-34 — Храм | Храм-кандидат в реестр |
| 6 | `dotfiles/.opencode/memory/research/2026-10-14-machine-tracks-analysis.md` | И-38: 7706 карточек decision-queue, 96.8% шума | draft | 2026-10-14 | смежная (Мастерская) | реестр не требует |
| 7 | `dotfiles/docs/specs/agent-lifecycle-v1.md` + И-22/И-23 | Эволюция агентов: классификатор, обкатка, правило 3/5 | proposed | — | прямая/смежная (агентский контур) | в реестр как агент-контур |
| 8 | узлы tech-jev/laya/openjev/open-alternative-jev (idea-graph:83–86) | Внешние находки: TypeSafe Jev, on-device аналоги, vLLM | candidate | research 2026-10-04 | прямая (внешний кейс → годное) | сверить с текстом (не найден); в реестр |
| 9 | узел tech-tradingmind (idea-graph:90) | TradingMind — typed-edge epistemology, «первый кейс idea-stream» | accepted | research 2026-10-05 | прямая | реестр + сквозной кейс пайплайна |
| 10 | узлы tech-gepa/obra-knowledge-graph/obsidian-stack (idea-graph:87–89) | GEPA, knowledge-graph, Obsidian-стек | candidate/accepted | research 2026-10-04 | прямая | реестр |
| 11 | узлы tech-analogs/tenensuro/comp/tardis/jarvis/hev/drone (idea-graph:171–181) | Библиотека теоретических аналогов (Pip-Boy) | candidate, часть blessed | session 2026-10-07 | прямая | Lab-queue L2–L6 назначены; связь зафиксировать |
| 12 | `06-Audits/2026-10-11-counteragent-cross-domain-research.md` + sources-index | Кросс-доменный ресёрч контрагента | draft-research | 2026-10-11 | не Институт — агентский контур (К-А в2) | в реестре (строка 29) |
| 13 | `06-Audits/2026-10-09-agency-counteragency-brainstorm.md` (стр. 242–246) | «У Института нет тени/сотрудников; представитель не заведён» | draft-working | 2026-10-09 | прямая (дефицит) | учесть при создании сессии |
| 14 | `00-WORLD.md` §VII | Канон «Институт → Лаборатория → доказанное» | канон | 2026-10-07 | прямая | — |
| 15 | `06-Audits/2026-10-07-pae-market-research.md` | PAE market scan (≤55–60 источников) | accepted | 2026-10-07 | прямая (классика институтского ландшафта) | реестр (отсутствует) |
| 16 | `06-Audits/2026-10-08-email-capture-research.md` + stream-intent-email-capture | Email-capture — вход внешних кейсов | draft/deferred | 2026-10-08 | смежная | реестр как источник кейсов |
| 17 | `tools/telegram-capture/signals.json` (517 постов, 396 сигналов: new 46) | Поток необработанных внешних сигналов — кандидатный пул кейсов | часть не разобрана | capture | прямая (вход) | пакетная разметка категории институт-external |
| 18 | `99-Inbox/vault-upgrade-research-2026-08-02.md` | Ресёрч передовых OSS: token-compression, кэш, память, retrieval | seed, часть реализована | 2026-08-02 | прямая (прототип формата Института) | реестр; сверить нереализованный хвост |
| 19 | `99-Inbox/2026-10-06-sustainability-canon.md` | Канон «Устойчивое развитие» → Рафаил | raw | Рудра 2026-10-06 | не Институт — Храм | реестр |
| 20 | `99-Inbox/2026-10-06-pipboy-retrospective-vision.md` | Pip-Boy ретроспектива | raw | Рудра 2026-10-06 | смежная (Терминал) | реестр |
| 21 | Т-130, T-178 model-watch (TASKS.md) | Ресёрч провайдеров; снапшот каталога моделей | done | 2026-09/10 | прямая (тренд-мониторинг) | реестр |

## Топ-5 по весу

1. **stream-intent-040** — единственное крупное исследование с прямым указанием на «представителя Института»; единого документа-роллапа нет.
2. **world-entity-veldora-two-layers** — исход 040 связан словом Rudra с появлением Института.
3. **Кластер аналогов + вердикт 043** — готовый прецедент «внешние находки → вердикт Рудры → Lab (L2–L6)».
4. **vault-upgrade-research-2026-08-02** — прототипный образец институтского формата (проверяемые факты, [проверить]); есть нереализованный хвост (semantic-retrieval, observability).
5. **tech-tradingmind** — единственный внешний кейс, доведённый до accepted-метода; образец поставки Института.

## Пробелы (слово есть — артефакта нет)

- Исследование 040 не имеет отдельного артефакта — только узел и упоминания (facts.md:871, lab-queue:22).
- Узел «представитель Института» не заведён (brainstorm:246); сессия-носитель не создана (institute-location spec).
- У Института нет тени/сотрудников (нарушение закона тени, brainstorm:202/246).
- Журналы `research:2026-10-04:jev-classifier-audit / evolution-applications / graph-technologies / tradingmind-audit` — пути к первоисточникам не найдены в волте/dotfiles (возможная потеря, требуют probe).
- NotebookLM — research-артефакта в волте нет (кроме строки реестра и спеки library-location).
- G-Star+/маскированная диффузия (ICML 2026, arxiv 2510.08369) — сырье в `tools/telegram-capture/captures_all.json:3451`, не классифицировано как внешний кейс.
