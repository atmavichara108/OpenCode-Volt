---
type: research
title: "Институт — И-35: разбор телеграм-капчуров (качество классификации, GLiClass, persist)"
status: draft
timestamp: 2026-10-14
project: OpenCode-Vault / dotfiles
source: "мандат sysop/Engineering Center (одобрен Рудрой 2026-10-14), слово Rudra: «там все сообщения в группе Архив полезная инфа, не личная переписка, приватность не уместна» (basis: quoted); полные расчёты — /tmp/opencode/institute-i35-20261014/REPORT.md"
related:
  - 06-Audits/2026-10-13-ship-research-registry.md
  - tools/telegram-capture/classify.py
---

# Институт — И-35: разбор телеграм-капчуров

Дистиллят разбора результатов `tools/telegram-capture/` (classify.py) по датасету
captures_all.json. Данные: 517 постов (2023-12-15 → 2026-09-06), классификация
`captures_classified.json` (classify.py, 2026-09-07). Полные расчёты и трассировка —
`/tmp/opencode/institute-i35-20261014/REPORT.md`.

## Цифры

- Всего постов: **517**; классифицировано **517** (100% — постов без метки нет).
- Распределение: vibeos **269** (52.0%), error **121** (23.4%), dotfiles **70** (13.5%),
  new **46** (8.9%), serplux **11** (2.1%), dv-hub **0**.
- **dv-hub = 0 — дефект**: категория объявлена в `EMOJI_MAP` (config.py), но
  classify.py её **не производит**.
- «Без категории» как значения нет: всё, что не совпало, тихо падает в
  `FINAL_FALLBACK → dotfiles`.

Состав error-бакета (121): пустой текст (медиа без подписи) 64; «прочее/дубликат» 21
(реальный dedup по repo/text — 14); платные курсы (руб/₽) 7; copyright-takedown 7;
`#Видео`/`#Плейлист` 7; «чему вы научитесь» 6; шпаргалки 3; стубы 6.

## Потерянное

`FINAL_FALLBACK` = 31 пост не совпал ни с одним правилом. Из них **16 содержат
github/CLI/LLM-признаки** и должны были попасть в dotfiles/vibeos/serplux, но ушли в
дефолтный dotfiles (или ошибочный error). Примеры: id=710 (Inertia — физическая
песочница в терминале, GH+CLI), id=42 (github-readme-terminal, GH+CLI), id=699
(Frappe Builder — low-code конструктор, GH), id=453 (shadify, GH), id=444 (Framely, GH),
id=269 (Cables — визуальное программирование, GH), id=740 (awesome-certificates, GH),
id=25 (CodinGame, LLM).

Ключевой разрыв: «Обучалки» с github = курс/ресурс не опознаётся (нет правила на
`awesome-*`, `курс`, `CodinGame`, `Exercism`, `Coding Bat`), а конструкторы сайтов
(Frappe/shadify/Framely/Cables) не матчатся ни SERPLUX (нет «scraping/SEO»), ни DOTFILES.

## Ошибочное

7 error-постов содержат github-ссылку, но реально годятся в vibeos (часть — дубликаты,
намеренно отправленные в error dedup-ом): Upscayl, Huge AI-Catalog, MiniCPM-V, LibreChat,
agency-orchestrator (голый github-URL), Buzz (×2). Плюс системная ошибка:
copyright-takedown («This message couldn't be displayed…») — первый пост уходит в
dotfiles, остальные 7 ловятся только text-dedup-ом; детерминированного правила нет.

## Шум

- Рекламный хвост `👁 [News/Soft/Hacker]…` — **122/517** (23.6%); нормализация срезает,
  но вариантов хвоста 8 и «👁 Если у вас плохо прогружаются файлы…» вклинивается иначе.
- Пустые посты (медиа без текста) — **64/517** (12.4%), все → error корректно.
- t.me-ссылки в теле — **257** постов (реклама/партнёрки + ссылки на @канал отправителя).
- Эмодзи-разметка (228 постов с ≥1 эмодзи) не срезается в `classify_post` — маркеры-заголовки
  `🧩`, `💻`, `🏠` остаются в тексте.
- Видео-посты 235 (45%); 15 из них <40 симв — «видео-визитки», текст не несёт сигнала.
- Голый github-URL без описания (id=783): `is_error_content` пропускает, но ни одна
  категория не матчит голый URL.

## Уверенность правил

- **Уверенно** (~30%): CORE_VIBEOS (84), DOTFILES_RE (45), SERPLUX_RE (7), android_app (10),
  ai_video (11) — сильные сигнатуры.
- **GENERIC_VIBEOS (173)** — самый «мусорный» catch-all по слову `\bai\b`, переклассифицирует
  dotfiles-утилиты в vibeos («с использованием ИИ» в описании), раздувая vibeos до 52%.
- **Провал**: FINAL_FALLBACK (31) + topic-defaults (Вайб 16, ИИ 4, Питонизм 11) = **62 поста
  (12%)** получают категорию «по умолчанию», а не по содержанию.

## Вердикт по GLiClass

- Словарь `classifier-gliclass.ts` (`~/.config/opencode/lib/classifier-gliclass.ts`) ожидает
  **командные слоты** `MODULE_VOCABULARY` (git-flow, stow-deploy, …) — это классификатор
  команд→слоты субагентов (И-22), **не** категорий telegram-постов; архитектурно не
  пересекается с задачей капчура.
- Работоспособность: venv `~/.local/share/opencode/gliclass-venv` жив (gliclass 0.1.20,
  torch 2.14.1, transformers 5.19.0, модель knowledgator/gliclass-edge-v3.0 закеширована);
  холодный старт ~9.4 c, инференс ~0.1 c/текст.
- Проба на 20 постах (собственные лейблы dotfiles/vibeos/new/serplux/error, multi-label,
  threshold 0.0): совпадение **9/20 (45%)**. Дефект — GLiClass «слипает» dotfiles-посты в
  `error` с уверенностью 0.7–0.96 (лейбл error «всасывает» всё не-ИИ).
- **Вывод**: для постов сейчас не нужен — правила покрывают 517/517, zero-shot хуже (45%)
  и перекошен в error. Остаётся в нише командных слотов (И-22). Потенциальная роль — только
  **второй эшелон** для 31 FINAL_FALLBACK-поста, и то после калибровки лейблов (без
  «всасывающего» error).

## Persist для SSA

`tg-read.py` пишет только stdout + маркер `last_id` в `~/.local/state/ssa-tg/last_id`.
Персистентности сообщений нет. Рекомендация — **вариант A: append-only JSONL
`~/.local/state/ssa/messages.jsonl`**: O_APPEND + одна строка = одна запись (атомарно для
POSIX, строки ≤ PIPE_BUF); вне git-зоны (не пачкает `Projects/SSA`); кросс-сессионный;
`last_id` уже живёт в соседней `ssa-tg/` — логично положить поток рядом в XDG state.
SQLite (C) оправдан только при нужде в диапазонных запросах/агрегатах — позже как
индексация поверх JSONL. Риск A: параллельный запуск двух tg-read → интерливинг строк —
лечится `flock` на файле (как уже принято для горячих файлов Vault).

## Риски

1. **dv-hub = 0**: категория объявлена в EMOJI_MAP и в задаче И-35, но классификатор её
   не выдаёт — либо удалить из схемы, либо добавить правила.
2. **GENERIC_VIBEOS (173)** через `\bai\b` переклассифицирует dotfiles-утилиты в vibeos,
   раздувая vibeos до 52%.
3. **FINAL_FALLBACK (31)** — тихий слив в dotfiles без пометки «не уверен»: 16 реально
   классифицируемы, остальные 15 — курсы/шпаргалки/видео-визитки.
4. **Дубликаты → error (14)** стирают категорию: post-repo-duplicate теряет vibeos-метку;
   стоит различать `error:duplicate` и `error:genuine`.
5. **Copyright-takedown** без правила (8 постов): 1 утёк в dotfiles.
6. **GLiClass** не применим к постам без смены словаря; 45% на пробе хуже правил.
7. **Питонизм-topic** почти целиком → error (11) — тема по факту «курсы/книги»,
   семантически совпадает, но github-исключение (→ dotfiles) сомнительно.

## Рекомендации Института

1. Добавить правила: `awesome-*`/шпаргалки, конструкторы сайтов (Frappe/shadify/Framely/Cables),
   copyright-takedown, «чему вы научитесь».
2. dv-hub — починить правило или снять категорию (сейчас классификатор её не производит).
3. Сузить `\bai\b` в GENERIC_VIBEOS (убрать ложные vibeos).
4. FINAL_FALLBACK помечать «не уверен», не сливать в dotfiles.
5. Duplicates — хранить категорию первого вхождения (не стирать в error).
6. Persist SSA = append-only JSONL `~/.local/state/ssa/messages.jsonl`.
7. GLiClass — не подключать к постам (остаётся в нише командных слотов).
