#!/usr/bin/env python3
"""
Классификатор постов captures_all.json по категориям VibeOS.

Категории:
  dotfiles 👨‍💻 — CLI/terminal/file managers/system utils/media/notes/Linux UX/browser ext/file transfer/image viewers
  vibeos   🏆 — AI agents, MCP, model routing, context mgmt, agent orchestration, PDF→MD, Claude Code tools, LLM inference, token monitoring, prompt engineering
  new      🎉 — Android apps (VibeAndroid), AI видео инструменты, совершенно новые направления
  serplux  🔥 — Docker, SEO, парсинг, веб-скрапинг, API-клиенты, Google позиционирование
  error    🤔 — пустые, дубликаты, нерелевантное, сломанные

Порядок проверки (приоритет сверху вниз):
  1. error  — пустые/сломанные/курсы/дубликаты
  2. vibeos (CORE)  — MCP, Claude Code, agentic, harness, LLM-агент, AI-кодинг-агент, open interpreter, phidata/langchain/langflow/flowise, openai/anthropic
  3. new   — строгое определение Android-app или AI-видео
  4. vibeos (GENERIC) — llm/llama/chatgpt/gpt/ollama/claude/нейросет*/ии-сервис/AI-сервис/AI-агент/промпт-инжиниринг и пр.
  5. serplux — Docker/SEO/скрапинг/clone-site/DNS/SSL/торговые-терминалы
  6. dotfiles — CLI/terminal/file-manager/system/media/notes/Linux/wallpaper/browser-ext/file-transfer/image-viewer
  7. topic-default — Смарт→new, Вайб→vibeos, ИИ→vibeos, Питонизм→error
  8. final → dotfiles
"""
import json
import re
from datetime import date
from pathlib import Path

SRC = Path(__file__).resolve().parent / "captures_all.json"
OUT = Path(__file__).resolve().parent / "captures_classified.json"


# --- Утилиты -------------------------------------------------------------------

def normalize(text: str) -> str:
    """Убираем футер с разделителем ===== из текста для анализа."""
    t = text or ""
    t = re.split(r"\n={5,}", t)[0]
    return t.strip()


def extract_title(text: str) -> str:
    """Извлечь краткое название (2-5 слов)."""
    t = normalize(text)
    if not t:
        return ""
    m = re.match(r"^\*\*\s*([^*\n]{1,80}?)\s*\*\*", t)
    if m:
        name = m.group(1).strip()
    else:
        m = re.match(r"^\[([^\]\n]{1,80})\]\([^)]*\)\s*\*{0,2}\s*[—\-:]\s*\*{0,2}", t)
        if m:
            name = m.group(1).strip()
        else:
            m = re.match(r"^\[\*\*([^*\n]{1,80})\*\*\]", t)
            if m:
                name = m.group(1).strip()
            else:
                first = re.split(r"[\n,]", t, maxsplit=1)[0].strip()
                first = re.sub(r"^[\W_]+", "", first)
                name = first.strip()
    name = re.sub(r"\s+", " ", name).strip(" *[](){}#")
    if "—" in name:
        name = name[: name.find("—")].strip(" *[](){}#")
    if ":" in name:
        name = name[: name.find(":")].strip(" *[](){}#")
    words = [w for w in re.split(r"[\s/|]+", name) if w]
    words = words[:5]
    name = " ".join(words)
    return name[:80]


def extract_repo(text: str) -> str:
    t = text or ""
    m = re.search(r"https?://github\.com/[A-Za-z0-9_.\-/]+", t)
    if m:
        url = m.group(0).rstrip("/.,)")
        url = re.sub(r"[\)\]\.,]+$", "", url)
        return url
    return ""


def extract_lang(text: str) -> str:
    t = text or ""
    m = re.search(r"Lang:\s*([A-Za-z0-9+#./ ]{2,30})", t)
    if m:
        return m.group(1).strip().splitlines()[0].strip()
    lang_kw = [
        ("Python", r"написан\s+на\s+Python|на\s+языке\s+Python|разработан\s+на\s+Python|на\s+Python\b"),
        ("Rust", r"на\s+языке\s+программирования\s+Rust|на\s+языке\s+Rust|на\s+Rust\b|разработан\s+на\s+языке\s+Rust"),
        ("C++", r"написан\s+на\s+C\+\+|на\s+языке\s+C\+\+"),
        ("Ruby", r"на\s+языке\s+Ruby"),
        ("Go", r"на\s+языке\s+Go\b|переписанный\s+на\s+языке\s+Go"),
        ("Kotlin", r"использованием\s+Kotlin|на\s+Kotlin"),
        ("Dart", r"на\s+Dart\b"),
        ("TypeScript", r"написана\s+на\s+TypeScript|на\s+TypeScript"),
        ("JavaScript", r"написана\s+на\s+JavaScript|на\s+JavaScript"),
        ("C", r"написана\s+на\s+C\b"),
        ("Bash", r"написанный\s+на\s+bash|на\s+Bash\b|сценарий\s+bash"),
    ]
    for lang, pat in lang_kw:
        if re.search(pat, t):
            return lang
    return ""


# --- Маркеры ошибки ------------------------------------------------------------

STUB_TEXTS = {
    "тоже", "с", "е", "срфт", "питон", "питонизм", "обучалки", "нейробуст",
    "красота", "ии",
}


def is_error_content(norm: str, full: str) -> bool:
    if not norm:
        return True
    low = norm.lower().strip()
    if low in STUB_TEXTS:
        return True
    if len(norm) < 3:
        return True
    # только URL без описания
    if len(norm) < 60 and re.fullmatch(r"https?://\S+", low):
        return True
    # шпаргалка-стубы
    if "Шпаргалка" in norm and "github.com" not in full and len(norm) < 30:
        return True
    # платные курсы
    if re.search(r"Цена[:\s].{0,15}руб|\bруб\.\b|\bЦена\b.{0,30}\bруб\b", norm):
        if "github.com" not in full:
            return True
    if "Размер" in norm and "ГБ" in norm and ("руб" in norm or "₽" in norm):
        return True
    if ("#Видео" in norm or "#Плейлист" in norm) and "github.com" not in full:
        return True
    if ("чему вы научитесь" in low or "чему вы научитесь" in norm) and "github.com" not in full:
        return True
    if "Подробное описание" in norm and "sliwbl.com" in full:
        return True
    return False


# --- Регулярки категорий ------------------------------------------------------

# CORE vibeos — конкретная AI-инфраструктура: MCP, Claude Code, agent infra, LLM-агент, AI-кодинг
CORE_VIBEOS_RE = re.compile(
    r"\bmcp\b|model\s+context\s+protocol|claude\s+code|claude\s+usage|"
    r"claude[\s-]?desktop|"
    r"agentic|agentic[-\s]?ai|agent\s+loops|agent\s+governance|agent\s+memory|"
    r"harness|harness[-\s]?engineering|"
    r"open\s+interpreter|openinterpreter|"
    r"llm-агент\w*|llm-модел\w*|llm-фреймворк|"
    r"ai-кодинг-агент|ai-кодинг-агентов|ии-кодинг-агент|ии-кодинг-агентов|"
    r"ai-кодинг|ии-кодинг|"
    r"\bphidata\b|\blangchain\b|\blangflow\b|\bflowise\b|"
    r"\bdistillat\w*|дистил\w*|"
    r"prompt[-\s]?engineering|промпт[-\s]?инжиниринг|"
    r"pixelrag|mcp[-\s]?ssh-manager|terminal-use\b|"
    r"\bfable\b|soul\.md",
    re.IGNORECASE,
)

# GENERIC vibeos — общие AI-маркеры (после android/video проверок)
GENERIC_VIBEOS_RE = re.compile(
    r"\bllm\b|\bllama\b|\bchatgpt\b|\bgpt-?\d|\bgpt\b|"
    r"\bollama\b|\bwhisper\b|\bstable\s+diffusion\b|\bstable\s+cascade\b|"
    r"stability\s+ai|anythingllm|\bkhoj\b|librechat|lobe\s+chat|"
    r"llama\s+2|llama\s+v2|talk-llama|"
    r"\bretreiver\b|\bретривер\b|\brag\b|"
    r"\bclaude\b|\bopenai\b|\banthropic\b|\bai\b|"
    r"\bmagnitude\b|\bmassgen\b|\bbitnet\b|\bairllm\b|\bperplexit\w*|"
    r"нейросет\w*|нейрон\w*|ии-сервис|ии-редактор|ии-инструмент|ии-университет|"
    r"ии-ассистент|ии-агент|ии-конвейер|ии-разработк|ии-органайзер\w*|ии-помощник|"
    r"ии\s+(?:помощник|сервис|инструмент|ассистент|редактор|агент|органайзер\w*|платформ|университет|конвейер|разработк|кодинг)|"
    r"ai-сервис|ai-агент|ai-ассистент|"
    r"codellama|code\s+llama|code-llama|"
    r"dall[·\.\-]e|dalle\b|"
    r"\bsdxl\b|sd-turbo|sd\s+turbo|midjourney|controlnet|"
    r"генерация\s+изображен|генератор\s+изображен|генератор\s+видео|генерация\s+видео|"
    r"искусственн\w+\s+интеллект|с\s+использованием\s+ии\b|с\s+использованием\s+искусствен|"
    r"\btoken\b|токен-мониторинг|токен\w*\s+монитор|"
    r"\btranscrib\w*|транскриб\w*|speech\s+to\s+text|преобразован\w+\s+речи\s+в\s+текст|"
    r"unstructured\s+data|извлечени\w+\s+данных\s+из\s+документов|"
    r"open-interpreter|open\s+interpreter|"
    r"tex2\w+|text2\w+|text-to-\w+|text\s+to\s+\w+|text-2-\w+|"
    r"flexible\s+локальн\w+\s+ии|локальн\w+\s+модел\w*|"
    r"vim-gpt\b|shell\s+gpt|"
    r"deepseek|qwen|gemini\b|mistral\b",
    re.IGNORECASE,
)

# Android-app detector (строгий)
ANDROID_STRICT_RE = re.compile(
    r"android[\s-]?приложение|"
    r"приложение\s+(?:для|на)\s+android|"
    r"\bandroid\s+app\b|"
    r"нативное\s+android|"
    r"jetpack\s+compose|"
    r"react\s+native|"
    r"termux[\s-]?desktop|"
    r"\bflutter\b|"
    r"разработанное\s+с\s+использованием\s+kotlin|"
    r"клиент\s+для\s+android|"
    r"управлени\w+\s+android-устройств\w*|"
    r"\bandroid-устройств\w*\b|"
    r"эмулятор\s+android|android[\s-]?эмулятор|android\s+эмулятор|"
    r"docker-android|запускающий\s+эмулятор\s+android",
    re.IGNORECASE,
)
# Loose pattern: «для android» / «на android» — срабатывает только если НЕТ
# кросс-платформенных упоминаний (Windows/macOS/Linux/iOS).
ANDROID_LOOSE_RE = re.compile(r"для\s+android\b|на\s+android\b", re.IGNORECASE)
CROSS_PLATFORM_RE = re.compile(
    r"\bios\b|\bmac\s?os\b|\bmacos\b|\bwindows\b|\blinux\b|\bmac\b|\bgnu/linux\b",
    re.IGNORECASE,
)


def is_android_app(low: str) -> bool:
    if ANDROID_STRICT_RE.search(low):
        return True
    if ANDROID_LOOSE_RE.search(low):
        # не срабатывает, если в тексте упомянуты и другие ОС → cross-platform
        if not CROSS_PLATFORM_RE.search(low):
            return True
    return False


# AI-видео инструменты
AI_VIDEO_RE = re.compile(
    r"\b(видеоредактор|видео-редактор|генератор\s+видео|генерация\s+видео|"
    r"генератор\s+роликов|созданию\s+видео|видео\s+с\s+использованием\s+искусствен|"
    r"липсинк|kling\s+ai|videogen|videosos|dreamcut|cogvideo|cogstudio|"
    r"capcut|klap\.app|"
    r"генератор\s+мегакачественн|"
    r"нарез\w+\s+длинн\w+\s+видео|"
    r"видео\s+за\s+секунд|"
    r"видео\s+от\s+meta|"
    r"монтаж\s+креативн\w+\s+видео|"
    r"запись\s+экрана\s+и\s+видеоредактор|"
    r"редактир\w+\s+(?:ваши\s+)?видео|"
    r"видео.{0,40}модел\w*\s+искусственн|"
    r"модел\w*\s+искусственн.{0,40}видео|"
    r"генератор\s+видео|созданию\s+видео\s+с\s+использованием\s+ии|"
    r"отредактир\w+\s+видео|монтирова\w+\s+ролик\w*|"
    r"видео.{0,30}текстов\w+\s+запрос|текстов\w+\s+запрос.{0,30}видео)\b",
    re.IGNORECASE,
)

# serplux — СТРОГИЕ маркеры (одного достаточно): scraping/SEO/clone-site/SSL/DNS/API-client
SERPLUX_RE = re.compile(
    r"\b(seo\b|seo-оптимизирован|парсинг|скрапинг|веб-скрапing|"
    r"scraping|scraper|scraperr|site\s+downloader|website-downloader|"
    r"клонировать|клонированию|клонирование|website\s+cloner|"
    r"ui\s+replicator|replicateui|website\s+по\s+промту|"
    r"преобразования\s+веб-сайтов|извлечени\w+\s+данных\s+с\s+веб|"
    r"\bssl\b|dns-сервер|dns\s+server|certimate|certmanager|"
    r"ssh-менеджер|ssh-manager|"
    r"yapi|метапоисков|поисков\s+система|"
    r"api-клиент|api\s+клиент|REST\s+API\s+клиент|"
    r"polymarket\s+терминал|торговый\s+терминал\s+для\s+polymarket)\b",
    re.IGNORECASE,
)

# СЛАБЫЕ serplux-маркеры (только если нет сильного dotfiles-маркера)
WEAK_SERPLUX_RE = re.compile(r"docker\w*|контейнер\w*", re.IGNORECASE)

# dotfiles
DOTFILES_RE = re.compile(
    r"\b(cli|tui|gui)\b|командной\s+строки|командный\s+интерфейс|"
    r"файлов\w*\s+менеджер\w*|file\s+manager|unix|"
    r"утилит\w*|системн\w*|htop|glances|мониторинг\w*|monitoring|"
    r"плеер\w*|музык\w*|media\s+server|медиа-сервер\w*|стример\w*|стриминг\w*|"
    r"заметк\w*|note\b|notes|notion|markdown-заметк\w*|"
    r"linux|manjaro|gnome|sddm|wayland|x11|"
    r"обоев\w*|обои|wallpaper|тема\s+рабочего|тем\s+рабочего|"
    r"расширение\s+для\s+браузера|browser\s+extension|chrome|firefox|"
    r"передач\w*\s+файлов|file\s+transfer|передавать\s+файлы|передачу\s+файлов|"
    r"просмотрщик\w*|image\s+viewer|"
    r"буфер\w*\s+обмен\w*|clipboard|"
    r"скриншот\w*|screenshot|захват\s+текста|ocr|"
    r"dotfiles|dotbins|themes|палитр\w*|palette|color\s+palette|colorpalette|"
    r"почт\w*|почтов\w*|"
    r"\bqr\b|qr-код|qr\s+кода|"
    r"погод\w*|weather|"
    r"календар\w*|calendar|"
    r"раскладк\w*|keyboard|keymap|"
    r"screen\s+recorder|запись\s+экрана|скринкаст\w*|record\s+screen|"
    r"оконн\w*\s+менеджер\w*|window\s+manager|tiling\s+window|"
    r"веб-браузер\w*|браузер\w*|"
    r"\bбот\b|telegram|"
    r"торрент\w*|bittorrent|торрентов|"
    r"редактор\s+кода|code\s+editor|"
    r"\brust\b|ratatui|c\+\+|"
    r"snapdrop|pairdrop|"
    r"прокси\w*|proxy|"
    r"\bssh\b|ssh-клиент|ssh-сервер|ssh-чат|"
    r"хранилищ\w*\s+файлов|облак\w*|облачн\w*\s+хранилищ\w*|"
    r"audiobookshelf|navidrome|"
    r"password\s+manager|пароль\s+менеджер|"
    r"конвертер\w*|converter|конвертаци\w*|"
    r"ведение\s+заметок|список\s+задач|todo\s+list|task\s+manager|"
    r"проигрывател\w*|видео\s+плеер|video\s+player|"
    r"\bwebrtc\b|видеозвон\w*|видеоконференц\w*|"
    r"\bgrub\b|sddm-тема|bootloader|"
    r"заставк\w*|"
    r"десктопн\w*\s+приложение|приложение\s+для\s+управления",
    re.IGNORECASE,
)


# Дефолты по темам (применяются в самом конце, если ничего не сработало)
TOPIC_DEFAULTS = {
    "Смарт": "new",
    "Вайб": "vibeos",
    "ИИ": "vibeos",
    "Питонизм": "error",
}


def classify_post(p: dict) -> str:
    norm = normalize(p["text"])
    full = p["text"] or ""
    topic = p["topic"]
    # Убираем markdown-разметку (* _ ` ~ |) для корректной работы \b-паттернов
    low = re.sub(r"[*_`~|]+", "", norm).lower()

    # 1. error content
    if is_error_content(norm, full):
        return "error"

    # 2. CORE vibeos
    if CORE_VIBEOS_RE.search(low):
        return "vibeos"

    # 3. topic-override для "Смарт" → new (VibeAndroid флагман), но только
    #    если пост не AI-инфра (которое уже отдало в vibeos выше)
    if topic == "Смарт":
        return "new"

    # 4. new — strict android / AI-видео
    if is_android_app(low):
        return "new"
    if AI_VIDEO_RE.search(low):
        return "new"

    # 5. GENERIC vibeos
    if GENERIC_VIBEOS_RE.search(low):
        return "vibeos"

    # 6. dotfiles (сильные маркеры бьют слабый serplux/docker)
    if DOTFILES_RE.search(low):
        return "dotfiles"

    # 7. serplux (строгие маркеры) — scraping/SEO/clone/SSL/DNS/API-client
    if SERPLUX_RE.search(low):
        return "serplux"

    # 8. serplux слабый — docker/контейнер (после dotfiles, чтобы не перебивать CLI-утилиты)
    if WEAK_SERPLUX_RE.search(low):
        return "serplux"

    # 9. topic-default
    if topic in TOPIC_DEFAULTS:
        # Исключение: «Питонизм» с github-URL — это инструмент, не курс
        if topic == "Питонизм" and "github.com" in (full or "").lower():
            return "dotfiles"
        return TOPIC_DEFAULTS[topic]

    # 10. final — лучше dotfiles чем error
    return "dotfiles"


# --- Дубликаты ----------------------------------------------------------------

def make_repo_key(repo: str) -> str:
    k = re.sub(r"^https://github\.com/", "", repo).rstrip("/")
    return k.lower()


def text_signature(text: str) -> str:
    """Ключ для поиска текстовых дубликатов: первые 200 значимых символов."""
    t = normalize(text)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:200].lower()


# --- Главный цикл -------------------------------------------------------------

def main():
    with SRC.open(encoding="utf-8") as f:
        data = json.load(f)

    topics_order = list(data["topics"].keys())
    flat = []
    for topic in topics_order:
        for p in data["topics"][topic]:
            flat.append({**p, "topic": topic})

    assert len(flat) == data["total"] == 584, f"count mismatch: {len(flat)}"

    seen_repos = set()
    seen_texts = set()
    records = []
    summary = {"dotfiles": 0, "vibeos": 0, "new": 0, "serplux": 0, "error": 0}
    topic_counts = {t: 0 for t in topics_order}

    for p in flat:
        topic = p["topic"]
        full = p["text"] or ""
        norm = normalize(full)
        title = extract_title(full)
        repo = extract_repo(full)
        lang = extract_lang(full)

        cat = classify_post(p)

        # Дубликат по репо — только если обе копии не-error
        if cat != "error":
            if repo:
                rk = make_repo_key(repo)
                if rk in seen_repos:
                    cat = "error"
                else:
                    seen_repos.add(rk)
            # Дубликат по тексту
            sig = text_signature(full)
            if len(sig) > 10 and sig in seen_texts:
                cat = "error"
            else:
                seen_texts.add(sig)

        # Краткая причина
        if cat == "error":
            reason = "пусто/дубликат/нерелевантно"
        elif cat == "new":
            if is_android_app(norm.lower()):
                reason = "Android-приложение (VibeAndroid)"
            else:
                reason = "AI-видео инструмент"
        elif cat == "vibeos":
            reason = "AI/агенты/MCP/LLM-стек"
        elif cat == "serplux":
            reason = "Docker/SEO/скрапинг/API-клиент"
        else:
            reason = "CLI/софт/системная утилита"

        records.append({
            "message_id": p["message_id"],
            "topic": topic,
            "title": title,
            "lang": lang,
            "category": cat,
            "repo": repo,
            "reason": reason,
        })
        summary[cat] += 1
        topic_counts[topic] += 1

    result = {
        "classified_date": str(date.today()),
        "total": len(records),
        "summary": summary,
        "topics": topic_counts,
        "posts": records,
    }

    with OUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUT}")
    print(f"Total posts: {len(records)}")
    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("Topics:")
    for k, v in topic_counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()