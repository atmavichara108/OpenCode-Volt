---
type: market-research
title: PAE market scan — «вайбкодинг как приключение», кто строит подобное
status: accepted
timestamp: 2026-10-07
source: researcher (ses_ee88a83e1…), сбор ≤55–60 уникальных источников;
  файл собран Дирижёром из полного рабочего материала исследователя
  (лимит шагов исчерпан до записи; evidence-материал передан целиком)
rule-of-silence: TradingMind не встречался в выдачах, не упоминается
---

# Ресёрч: строит ли кто-то «игру поверх агентной разработки»?

## TL;DR

**Прямых конкурентов PAE не найдено.** Ближайшие — десятки pet-проектов
2025–2026, накладывающих XP/квесты/ачивки поверх Claude Code / Codex /
OpenCode (rpgdev, Agent Dungeon, repos-and-dungeons, AGPA и др.). Но **ни в
одном нет двунаправленного переводного слоя «игровая реальность ↔ рабочая
реальность»** (git-ветки как локации, сцены как решения, объявления только о
свершившемся) — это ядро уникальности PAE.

**Ниша «Pip-Boy как операционная панель агентов» пуста**: fallout-реплики
(PIP-OS, piboy, PiBoy5) — чистая косметика для Raspberry Pi, к dev-workflow
не привязаны.

**Главный анти-урок:** Vibe Kanban (28.3k★) закрылся 10.04.2026 — «not able to
find a business model»: planning/review-интерфейсы к агентам сами по себе не
монетизируются. Massовая смертность pet-проектов геймификации (0–1★) —
норма. Вывод для PAE: ценность должна быть в рабочей функции (память,
границы, координация), игра — оболочка, а не продукт.

## Карта близости (0 — косвенно, 3 — PAE-двойник)

### Кластер 1. Геймификация агентного кодинга (ближе всех)

| Проект | Что делает | Близость | Статус |
|---|---|---|---|
| kitepon-rgb/rpgdev | JRPG-оверлей на хуки Codex/Claude Code: tool-calls=бой, TODO=quest log | 2–2.5 | жив |
| Human-Agency-Hackathon/ha-agent-rpg | Agent Dungeon: папки=комнаты, issues=квесты, MCP ClaimQuest, 209 тестов | 2–2.5 | хакатон, Feb 2026 |
| dbl8005/repos-and-dungeons | repo как пиксельное подземелье, непрочитанный код=туман (11★) | 2 | активен 10/2026 |
| Hin-Nattapat/agent-quest | пиксель-RPG поверх агентных сессий, XP за промпты/эдиты (5★) | 2 | жив |
| thousandsky2024/claude-pixel-agent-web | сессии Claude Code как пиксельные рыцари (15★) | 1.5 | жив |
| eiainano/AgentPlayerAchievements | Steam-ачивки/XP для Claude Code, OpenCode, Kilo, Hermes; MCP+хуки (476 коммитов) | 2 | активен |
| devsemih/claude-rpg-game | PostToolUse-хук: XP, классы, луут, дейлики | 1.5 | жив |
| SeanZoR/claude-quest | 90 ачивок освоения Claude Code (10★) | 1 | жив |
| subinium/claude-code-achievements | ачивки (84★, Jan 2026) | 1 | жив |
| IdoCohen560/KodamaAlpha | терминальный компаньон-питомец: 25 видов, 100 уровней, prestige | 1.5 | жив |
| ygalsk/codecritter | компаньон + данжен-кроулер, враги «Null Pointer / Race Condition» | 1.5 | жив |
| timoncool/prompt-warrior | лог агентной работы = лист персонажа, 5 харнессов (24★) | 2 | окт 2026 |
| AutumnsGrove/CodeQuest | Go-TUI: коммиты→XP→квесты + AI-ментор (1★, beta) | 1.5 | сомнителен |
| shiprpg-agent (npm) | «геймификация агентов в одну строку»: quests/XP/leaderboard | 1.5 | npm 04/2026 |
| dburks-svg/DevQuest | wrapper: XP за commit/push/test/deploy, классы | 1.5 | жив |
| AIckathon-2025-08/codex-mcp | задачи→квесты, Gandalf-персонажи, XP | 1.5 | хакатон |
| drakegriffith/agent-village; zachloh00/agent-town | Sims-style 3D/пиксельная деревня агентов | 1 | 0★, недоделки |

### Кластер 2. Обсервабельность агентов как мир

Pixel Agents (VS Code, roadmap «Actually a game»); SwarmVille (low-poly
деревня цикла plan→ship); AI Village (13–15 LLM-агентов с реальными
компьютерами, 323+ дня публичного дневника — сильнейший live-след);
AI Town a16z (10.2k★, MIT); Generative Agents/Smallville (Stanford 2023,
канон); Project Sid/Altera (1000+ агентов в Minecraft, arXiv:2411.00114);
WorldLines, WorldSeed, BOOKWORLD (ACL 2025), Caosmos. Все — story-sims
(агенты живут в игре), НЕ рабочий слой (игра поверх реальной работы).

### Кластер 3. Gamified life/PKM

Habitica (14k★; ⚠ пауза PR с Aug 2026 + запрет LLM-контрибуций — усталость
модели); Octogriffin; Notion-шаблоны Gamified Life OS (~1.5–1.7k покупателей),
Second Brain 6.0 Game Mode, LiFE RPG; LifeForge, Eighty (MCP), Level Journey,
HERO, LifeRPG.co; LifeOS (open-source, 18★); **wahnahbe-system** —
Solo-Leveling-дашборд поверх Obsidian-vault (файлы=API, Claude-скилы) —
концептуально ближайший к «vault↔мир», близость 2, личный проект.

### Кластер 4. Pip-Boy/киберпанк

RobCo PIP-OS, SirLefti/piboy, pypboy, PiBoy5, Piboy2000 — все косметика.
Cyberpunk-темы (Neovim/tmux/Ghostty, statusline'ы, r/unixporn). К агентной
работе не привязан ни один.

### Кластер 5. Академия

GitRev (LLM-геймификация code review, 86 студентов); Stol 2021 / Indriasari
2022 (геймификация×SE: вовлечённость→удовлетворённость); AI pair-programmer
мотивация (Springer IJ STEM Ed 2025 n=234; arXiv 2505.08119; ACM
10.1145/3765964.3811664 «Fast and Forgettable»); **контраргумент:
arXiv 2410.08922 — friction-by-design, чрезмерная гладкость мешает
обучению** (важно для дизайна сцен: полезное трение оставлять).

### Кластер 6. RU-сегмент

Habr 2025–2026: вайбкодинг как термин ( Collins word of 2025), гайды
«НЕразработчикам» (971080), кейс МТС, игровые кейсы (959506, sfly.pieter.com,
AI Roguelite), Cursor-опыт (906820), LLM в геймдеве (940072, 956342).
**Прямых «игра поверх агентной разработки» нет — ниша в RU свободна.**

## Тренды

1. Взрыв микро-проектов XP-над-агентом в 2025–2026 (десятки) — спрос
   доказан, исполнение детское (счётчики, без мира и памяти).
2. Наблюдаемые миры агентов (AI Village, AI Town) живы и с аудиторией —
   формат «живой след» работает.
3. Конвергенция: хуки/скилы/MCP стали стандартом встраивания — оверлеи
   ставятся без форка харнессов (наш путь: plugins/hooks, не форк).
4. Эстетика терминального ретро-интерфейса (Pip-Boy/cyberpunk) жива как
   косметика — ниша операционной панели свободна.

## Пробелы рынка (= где уникален PAE)

- Двунаправленный переводной слой мир↔работа (ни у кого нет).
- Память, переживающая сессии (граф+валидатор) как часть мира, а не логов.
- Границы и безопасность как игровые механики (Maya-lint, Git Freed, lease).
- Объявления только о доказанном (закон Голоса) — анти-шум.
- RU-ниша пуста.

## Почему у других не взлетело

- **Vibe Kanban/bloop закрылся 10.04.2026** (28.3k★): нет бизнес-модели у
  planning/review-оболочек → PAE должен ценностью покрывать работу, не UI.
- Смертность pet-оверлеев: механики без памяти/последствий = игрушка на
  неделю.
- Habitica-стагнация: ручная модерация контента + отсутствие LLM-пути.
- Механические риски: XP-инфляция, grind-усталость (октолизис),
  gaming the system; friction-by-design предупреждает об обратной стороне
  «бесшовного приключения».

## Риски для PAE

1. Копирайт/эстетика Fallout — держать «вдохновение», не ассеты (уже так).
2. Механики без бизнес-оправдания умрут как Vibe Kanban — держать связь
   каждой механики с рабочей функцией.
3. Масштабирование внимания: десятки сцен/объявлений = шум; закон Голоса
   уже частично привит.

## Ссылки (все verified researcher'ом; GitHub — owner/repo, Habr — id статей)

github.com: kitepon-rgb/rpgdev · Human-Agency-Hackathon/ha-agent-rpg ·
dbl8005/repos-and-dungeons · Hin-Nattapat/agent-quest ·
thousandsky2024/claude-pixel-agent-web · eiainano/AgentPlayerAchievements ·
devsemih/claude-rpg-game · SeanZoR/claude-quest ·
subinium/claude-code-achievements · IdoCohen560/KodamaAlpha ·
ygalsk/codecritter · timoncool/prompt-warrior · AutumnsGrove/CodeQuest ·
dburks-svg/DevQuest · AIckathon-2025-08/codex-mcp ·
drakegriffith/agent-village · zachloh00/agent-town · a16z-infra/ai-town ·
Altera-Institute (Project Sid) · habitica/habitica · Octogriffin ·
wahnahbe-system · SirLefti/piboy · RobCo PIP-OS · PiBoy5 · Piboy2000 ·
pypboy · vibekanban.com/blog/shutdown
arXiv: 2411.00114 · 2410.08922 · 2505.08119 · BOOKWORLD (ACL 2025)
ACM: 10.1145/3765964.3811664
Habr: 971080 · 959506 · 906820 · 940072 · 956342
npm: shiprpg-agent · pypi: pypboy
Прочее: AI Village (public diary, 323+ дней), SwarmVille, Pixel Agents
(VS Code), Stanford Generative Agents/Smallville.
