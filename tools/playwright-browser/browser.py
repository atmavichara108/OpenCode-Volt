"""browser.py — детерминированный браузерный тул (Playwright) для TUI-агентов.

Реализация [[02-Methods/tool-integration-pattern]]: LLM думает, API/браузер делает.
Порт семантики Playwright-CLI из M Code Desktop (T-134, ECO-031) в TUI-стек.

Гарантии:
  - read-only default: подкоманды open/goto/snapshot/eval/screenshot не мутируют
    страницу/файлы; write-семантика только через явные subcommands
    (click/fill/storage-state-save), каждый из них — отдельный флаг.
  - сессии изолированы: storage_state одного сессии-слота не пересекается с другими.
  - вывод — JSON на stdout (машинный анализ агентом); логи/progress — stderr.
  - no network подсказок секретов: URL задаются агентом; токены не логируются.

Использование:
  python browser.py goto --url https://example.com --snapshot           # read + ARIA snapshot (mode=ai, с ref)
  python browser.py goto --url https://example.com --screenshot out.png # read + скриншот
  python browser.py eval --url https://example.com --js "document.title"# прочитать DOM/JS-значение
  python browser.py click --url ... --ref e42                          # write: клик по element-ref из snapshot
  python browser.py fill --url ... --ref e7 --value "hello"             # write: ввод в поле
  python browser.py state-save --path profile.json                      # персистент логин-сессии
  python browser.py state-load --path profile.json --url https://...    # загрузить сохранённую сессию

Окружение:
  PYTHONPATH=.venv/lib/python3.14/site-packages python3 browser.py ...  # venv не активируется под GUI M Code (sys.executable → AppImage)
"""
import argparse
import json
import sys


def _preamble():
    """Возвращает Playwright sync API, лениво (чтобы --help не требовал установки)."""
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ModuleNotFoundError as e:
        print(
            json.dumps({
                "error": "playwright_not_installed",
                "hint": "PYTHONPATH=.venv/lib/python3.14/site-packages python3 browser.py ...",
            }),
            file=sys.stdout,
        )
        raise SystemExit(2) from e


def _launch(sync_playwright, state_path=None):
    """Запуск Chromium (headless). При state_path — поднятие с сохранённым storage state."""
    p = sync_playwright().start()
    kwargs = {"headless": True}
    if state_path:
        try:
            kwargs["storage_state"] = state_path
        except FileNotFoundError:
            pass  # нет сохранённого state — стартуем чисто
    browser = p.chromium.launch(**kwargs)
    return p, browser


def _goto(browser, url, state_path=None):
    ctx = browser.new_context(storage_state=state_path) if state_path else browser.new_context()
    page = ctx.new_page()
    page.goto(url, wait_until="load", timeout=30000)
    return ctx, page


def cmd_goto(args):
    sync_playwright = _preamble()
    p, browser = _launch(sync_playwright, getattr(args, "state_path", None))
    out = {}
    try:
        ctx, page = _goto(browser, args.url, getattr(args, "state_path", None))
        out["url"] = page.url
        out["title"] = page.title()
        if args.snapshot:
            out["snapshot"] = page.aria_snapshot(mode="ai")
        if args.eval_js:
            out["eval"] = page.evaluate(args.eval_js)
        if args.screenshot:
            page.screenshot(path=args.screenshot)
            out["screenshot"] = args.screenshot
        print(json.dumps(out, ensure_ascii=False))
    finally:
        browser.close()
        p.stop()


def cmd_eval(args):
    sync_playwright = _preamble()
    p, browser = _launch(sync_playwright, getattr(args, "state_path", None))
    try:
        ctx, page = _goto(browser, args.url, getattr(args, "state_path", None))
        value = page.evaluate(args.js)
        print(json.dumps({"eval": value}, ensure_ascii=False, default=str))
    finally:
        browser.close()
        p.stop()


def _prime_ref_map(page):
    """Засеить карту ref→element: aria-ref локатор работает только после
    aria_snapshot(mode="ai") на том же page-instance (рефы детерминированы ДОМом)."""
    page.aria_snapshot(mode="ai")


def cmd_click(args):
    sync_playwright = _preamble()
    p, browser = _launch(sync_playwright, getattr(args, "state_path", None))
    try:
        ctx, page = _goto(browser, args.url, getattr(args, "state_path", None))
        _prime_ref_map(page)
        page.locator(f"aria-ref={args.ref}").click()
        print(json.dumps({"clicked": args.ref, "url": page.url}, ensure_ascii=False))
    finally:
        browser.close()
        p.stop()


def cmd_fill(args):
    sync_playwright = _preamble()
    p, browser = _launch(sync_playwright, getattr(args, "state_path", None))
    try:
        ctx, page = _goto(browser, args.url, getattr(args, "state_path", None))
        _prime_ref_map(page)
        page.locator(f"aria-ref={args.ref}").fill(args.value)
        print(json.dumps({"filled": args.ref, "url": page.url}, ensure_ascii=False))
    finally:
        browser.close()
        p.stop()


def cmd_state_save(args):
    sync_playwright = _preamble()
    p, browser = _launch(sync_playwright)
    try:
        ctx = browser.new_context()
        page = ctx.new_page()
        if args.url:
            page.goto(args.url, wait_until="load", timeout=30000)
        storage = ctx.storage_state(path=args.path)
        print(json.dumps({"saved": args.path, "cookies": len(storage.get("cookies", []))}, ensure_ascii=False))
    finally:
        browser.close()
        p.stop()


def cmd_state_load(args):
    # чтение сохранённого state: отдаём лишь сводку (cookies/origins), не секреты.
    import os
    if not os.path.exists(args.path):
        print(json.dumps({"error": "no_such_state", "path": args.path}))
        raise SystemExit(1)
    with open(args.path, "r", encoding="utf-8") as f:
        storage = json.load(f)
    print(json.dumps({
        "path": args.path,
        "cookies": len(storage.get("cookies", [])),
        "origins": [o.get("origin") for o in storage.get("origins", [])],
    }, ensure_ascii=False))


def build_parser():
    p = argparse.ArgumentParser(description="Playwright browser tool (T-134)")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("goto", help="открыть URL + (optional) snapshot/screenshot/eval")
    _common(g)
    g.set_defaults(func=cmd_goto)

    e = sub.add_parser("eval", help="выполнить JS и вернуть значение (read om)")
    _common(e)
    e.add_argument("--js", required=True, help="JS-выражение, напр. document.title")
    e.set_defaults(func=cmd_eval)

    c = sub.add_parser("click", help="клик по element-ref из snapshot (write)")
    _common(c)
    c.add_argument("--ref", required=True, help="element ref из aria_snapshot mode=ai")
    c.set_defaults(func=cmd_click)

    f = sub.add_parser("fill", help="ввод значения в поле по element-ref (write)")
    _common(f)
    f.add_argument("--ref", required=True)
    f.add_argument("--value", required=True)
    f.set_defaults(func=cmd_fill)

    ss = sub.add_parser("state-save", help="сохранить storage state (cookies/login)")
    ss.add_argument("--path", required=True)
    ss.add_argument("--url", default=None, help="открыть перед сохранением (напр. страница логина)")
    ss.set_defaults(func=cmd_state_save)

    sl = sub.add_parser("state-load", help="сводка сохранённого state (без секретов)")
    sl.add_argument("--path", required=True)
    sl.set_defaults(func=cmd_state_load)

    return p


def _common(parser):
    parser.add_argument("--url", required=True)
    parser.add_argument("--snapshot", action="store_true", help="ARIA snapshot (mode=ai, с ref)")
    parser.add_argument("--screenshot", default=None, help="путь к .png")
    parser.add_argument("--eval-js", dest="eval_js", default=None, help="JS-выражение")
    parser.add_argument("--state-path", dest="state_path", default=None, help="путь к storage_state json")


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # честный JSON-ошибка агенту, не traceback
        print(
            json.dumps({"error": type(e).__name__, "message": str(e)[:300]}, ensure_ascii=False),
            file=sys.stdout,
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()