#!/usr/bin/env python3
"""model-router — переключение моделей агентов OpenCode (stdlib, без зависимостей).

Точки правды (что читает и пишет):
  глобальные агенты   ~/dotfiles/opencode-global/.config/opencode/agent/*.md
  проектные агенты    <project>/.opencode/agent/*.md
  встроенные агенты    блок `agent.<name>.model` в opencode.json / opencode.jsonc

Модель агента = фронтматтер `model:` (первично) либо agent-блок конфига.
Карты «агент → модель» нет: канон — сами файлы агентов (решение Rudra 2026-09-19).

Команды:
  list [--project P]                       JSON всех агентов + текущая model:
  models                                   объединённый список доступных моделей
  apply --agent X --model Y                точечная правка model: либо agent-блока
        [--scope global|project]           scope по умолчанию определяется по агенту
        [--project P] [--dry-run]

Гарантии:
  - пишется ТОЛЬКО строка `model:` (фронтматтер) или значение в agent-блоке;
    файл не переписывается целиком;
  - flock на целевом файле + бэкап перед записью (паттерн tools/peers/peer_lease.py);
  - --dry-run печатает diff и ничего не пишет;
  - запись только в разрешённые корни (global-конфиг, репозитории проектов, волт);
  - ключи провайдеров (auth.json) не читаются и не логируются.

Контракт вывода: одна строка JSON {"ok": true, ...} | {"ok": false, "error": ...}.
Exit codes: 0 ок · 1 ошибка исполнения · 2 ошибка ввода.
"""
from __future__ import annotations

import argparse
import difflib
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent.parent
SERVE_DIR = Path(__file__).resolve().parent
SNAPSHOT = SERVE_DIR / "generated" / "snapshot.json"

HOME = Path.home()
# Канон: symlink ~/.config/opencode -> ~/dotfiles/opencode-global/.config/opencode
GLOBAL_DIR = Path(os.environ.get(
    "PIPBOY_GLOBAL_OPENCODE_DIR",
    str(HOME / "dotfiles" / "opencode-global" / ".config" / "opencode"),
))
GLOBAL_AGENT_DIR = GLOBAL_DIR / "agent"
PROVIDERS_JSON = GLOBAL_DIR / "providers.json"

AGENT_FILE_RE = re.compile(r"^[A-Za-z0-9._-]+\.md$")
MODEL_RE = re.compile(r"^(?P<provider>[A-Za-z0-9._-]+)/(?P<rest>[A-Za-z0-9._:/-]+)$")
MAX_BACKUPS = 10


# --- общие утилиты ---------------------------------------------------------

def out(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def fail(msg: str, code: int = 1) -> int:
    out({"ok": False, "error": msg})
    return code


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def project_repos() -> dict[str, Path]:
    """{project_id: repo_path} из snapshot.json (только существующие пути)."""
    snap = read_json(SNAPSHOT)
    repos: dict[str, Path] = {"vault": VAULT_ROOT}
    for p in snap.get("projects", []):
        repo = p.get("repo")
        if repo and Path(repo).is_dir():
            repos[p.get("id", "")] = Path(repo)
    return {k: v for k, v in repos.items() if k}


def allowed_roots() -> list[Path]:
    roots = [GLOBAL_DIR.resolve(), VAULT_ROOT.resolve()]
    roots += [r.resolve() for r in project_repos().values()]
    return roots


def is_allowed(path: Path) -> bool:
    try:
        rp = path.resolve()
    except OSError:
        return False
    for root in allowed_roots():
        try:
            rp.relative_to(root)
            return True
        except ValueError:
            continue
    return False


# --- парсинг агентов -------------------------------------------------------

def _frontmatter(text: str) -> tuple[str | None, int, int]:
    """Вернуть (frontmatter_text, start_line, end_line) или (None, -1, -1).

    Ведущие пустые строки и BOM пропускаются: часть агентских файлов
    начинается с пустой строки перед `---`.
    """
    lines = text.lstrip("\ufeff").splitlines()
    first = 0
    while first < len(lines) and not lines[first].strip():
        first += 1
    if first >= len(lines) or lines[first].strip() != "---":
        return None, -1, -1
    for i in range(first + 1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[first + 1:i]), first + 1, i
    return None, -1, -1


def parse_agent_file(path: Path, scope: str, project: str | None) -> dict:
    text = path.read_text(encoding="utf-8")
    fm, _, _ = _frontmatter(text)
    model = None
    mode = None
    desc = None
    if fm:
        for line in fm.splitlines():
            m = re.match(r"^model:\s*(.+?)\s*$", line)
            if m:
                model = m.group(1).strip().strip("\"'")
            m2 = re.match(r"^mode:\s*(.+?)\s*$", line)
            if m2:
                mode = m2.group(1).strip().strip("\"'")
            m3 = re.match(r"^description:\s*(.+?)\s*$", line)
            if m3:
                desc = m3.group(1).strip().strip("\"'")
    return {
        "agent": path.stem,
        "kind": "file",
        "scope": scope,
        "project": project,
        "path": str(path),
        "model": model,
        "mode": mode or "subagent",
        "description": (desc or "")[:120],
        "has_frontmatter": fm is not None,
    }


def _config_paths(project: str | None) -> list[tuple[Path, str]]:
    """[(config_path, scope)] — глобальный и проектный конфиги."""
    res: list[tuple[Path, str]] = []
    for name in ("opencode.jsonc", "opencode.json"):
        p = GLOBAL_DIR / name
        if p.is_file():
            res.append((p, "global"))
            break
    if project:
        repo = project_repos().get(project)
        if repo:
            for name in ("opencode.json", "opencode.jsonc"):
                p = repo / name
                if p.is_file():
                    res.append((p, "project"))
                    break
            p2 = repo / ".opencode" / "opencode.json"
            if p2.is_file():
                res.append((p2, "project"))
    return res


def _config_agents(cfg: Path, scope: str, project: str | None) -> list[dict]:
    """Встроенные агенты из блока `agent` конфига (модель = agent.<n>.model)."""
    data = read_json(cfg)
    agents_block = data.get("agent")
    if not isinstance(agents_block, dict):
        return []
    res = []
    for name, body in agents_block.items():
        if not isinstance(body, dict) or "model" not in body:
            continue
        res.append({
            "agent": name,
            "kind": "config",
            "scope": scope,
            "project": project,
            "path": str(cfg),
            "model": body.get("model"),
            "mode": "primary",
            "description": "built-in агент (agent-блок конфига)",
            "has_frontmatter": True,
        })
    return res


def collect_agents(project_filter: str | None = None) -> list[dict]:
    agents: list[dict] = []
    # 1. глобальные .md
    if GLOBAL_AGENT_DIR.is_dir():
        for f in sorted(GLOBAL_AGENT_DIR.iterdir()):
            if f.is_file() and AGENT_FILE_RE.match(f.name):
                try:
                    agents.append(parse_agent_file(f, "global", None))
                except OSError:
                    pass
    # 2. проектные .md
    for pid, repo in sorted(project_repos().items()):
        if project_filter and pid != project_filter:
            continue
        d = repo / ".opencode" / "agent"
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and AGENT_FILE_RE.match(f.name):
                try:
                    agents.append(parse_agent_file(f, "project", pid))
                except OSError:
                    pass
    # 3. встроенные из конфигов
    for cfg, scope in _config_paths(project_filter):
        pid = project_filter if scope == "project" else None
        agents.extend(_config_agents(cfg, scope, pid))
    return agents


# --- список моделей --------------------------------------------------------

def _live_models() -> list[str]:
    exe = shutil.which("opencode")
    if not exe:
        return []
    try:
        r = subprocess.run([exe, "models"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return []
    if r.returncode != 0:
        return []
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip() and "/" in ln]


def _config_declared_models() -> dict[str, list[str]]:
    """{provider: [model_id]} из provider.<id>.models деклараций конфигов."""
    found: dict[str, list[str]] = {}
    paths = [p for p, _ in _config_paths(None)]
    for pid, repo in project_repos().items():
        for name in ("opencode.json", "opencode.jsonc"):
            p = repo / name
            if p.is_file():
                paths.append(p)
    for p in paths:
        data = read_json(p)
        provs = data.get("provider")
        if not isinstance(provs, dict):
            continue
        for prov, body in provs.items():
            models = (body or {}).get("models")
            if isinstance(models, dict):
                found.setdefault(prov, []).extend(models.keys())
    return found


def _provider_registry() -> dict:
    """providers.json: сокращения + medium/free (источник — dotfiles)."""
    return read_json(PROVIDERS_JSON)


def collect_models() -> dict:
    live = _live_models()
    declared = _config_declared_models()
    reg = _provider_registry()
    in_use = sorted({a["model"] for a in collect_agents() if a.get("model")})
    card_status = _provider_card_status()

    entries: dict[str, dict] = {}

    def add(model: str, source: str, provider: str | None = None) -> None:
        if not model or not isinstance(model, str):
            return
        prov = provider or model.split("/", 1)[0]
        e = entries.setdefault(model, {"id": model, "provider": prov, "sources": []})
        if source not in e["sources"]:
            e["sources"].append(source)

    for m in live:
        add(m, "live")
    for prov, ids in declared.items():
        for mid in ids:
            add(f"{prov}/{mid}", "declared", prov)
    for _abbr, body in reg.items():
        if not isinstance(body, dict):
            continue
        for key in ("medium", "free"):
            val = body.get(key)
            if isinstance(val, str):
                add(val, f"registry:{key}")

    # источник правды по активным маршрутам: модели, уже стоящие у агентов
    for m in in_use:
        add(m, "in-use")

    providers: dict[str, dict] = {}
    for e in entries.values():
        p = providers.setdefault(e["provider"], {"id": e["provider"], "models": 0, "sources": []})
        p["models"] += 1
        for s in e["sources"]:
            if s not in p["sources"]:
                p["sources"].append(s)
    for prov, info in providers.items():
        st = card_status.get(prov)
        if st:
            info["status"] = st["status"]
            info["card"] = st["card"]

    models = sorted(entries.values(), key=lambda x: x["id"])
    return {
        "ok": True,
        "count": len(models),
        "providers": dict(sorted(providers.items())),
        "models": models,
        "aliases": {k: v for k, v in reg.items() if isinstance(v, dict)},
        "sources": {
            "live": len(live),
            "declared": sum(len(v) for v in declared.values()),
            "in_use": len(in_use),
        },
        "hint": "live = `opencode models`; in-use = модели, уже стоящие у агентов; "
                "declared = provider.<id>.models из конфигов; registry = providers.json",
    }


def _provider_card_status() -> dict[str, dict]:
    """Статус провайдеров из операционных карточек (01-Reference/provider-cards)."""
    res: dict[str, dict] = {}
    d = VAULT_ROOT / "01-Reference" / "provider-cards"
    if not d.is_dir():
        return res
    for f in sorted(d.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        pid = None
        status = None
        for line in text.splitlines():
            m = re.match(r"^\|\s*`provider_id`\s*\|\s*`?([A-Za-z0-9._-]+)`?", line)
            if m:
                pid = m.group(1)
            m2 = re.match(r"^\|\s*`status`\s*\|\s*(.+?)\s*\|", line)
            if m2:
                status = m2.group(1).strip()
        if pid and status:
            res[pid] = {"status": status, "card": str(f.relative_to(VAULT_ROOT))}
    return res


# --- правка модели ---------------------------------------------------------

def _set_frontmatter_model(text: str, model: str) -> tuple[str, bool]:
    """Заменить/вставить `model:` во фронтматтере. → (новый текст, изменилось)."""
    fm, start, end = _frontmatter(text)
    if fm is None:
        raise ValueError("у файла нет фронтматтера — правка невозможна")
    lines = text.splitlines()
    for i in range(start, end):
        if re.match(r"^model:\s*", lines[i]):
            if lines[i] == f"model: {model}":
                return text, False
            lines[i] = f"model: {model}"
            return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), True
    # вставка: после mode:/description: либо в конец фронтматтера
    insert_at = end
    for i in range(start, end):
        if re.match(r"^mode:\s*", lines[i]) or re.match(r"^description:\s*", lines[i]):
            insert_at = i + 1
    lines.insert(insert_at, f"model: {model}")
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), True


def _jsonc_has_comments(text: str) -> bool:
    stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
    return "//" in stripped or "/*" in stripped


def _surgical_json_model(text: str, agent: str, model: str) -> tuple[str | None, bool]:
    """Точечно заменить значение `model` в объекте агента внутри блока `agent`.

    Форматирование файла сохраняется полностью (никакой пересборки JSON).
    Возвращает (новый текст | None, изменилось).
    """
    m_block = re.search(r'"agent"\s*:\s*\{', text)
    if not m_block:
        return None, False
    m_agent = re.compile(r'"' + re.escape(agent) + r'"\s*:\s*\{').search(text, m_block.end())
    if not m_agent:
        return None, False
    m_model = re.compile(r'("model"\s*:\s*")([^"]*)(")').search(text, m_agent.end())
    if not m_model:
        return None, False
    if m_model.group(2) == model:
        return text, False
    return text[:m_model.start(2)] + model + text[m_model.end(2):], True


def _set_config_agent_model(cfg: Path, agent: str, model: str) -> tuple[str, bool]:
    """Вернуть (новый текст конфига, изменилось). Только точечная правка значения."""
    text = cfg.read_text(encoding="utf-8")
    new_text, changed = _surgical_json_model(text, agent, model)
    if new_text is None:
        raise ValueError(f"{cfg.name}: агент '{agent}' не найден в блоке agent")
    # контроль: если файл — строгий JSON, значение обязано совпасть после правки
    if not _jsonc_has_comments(text):
        try:
            data = json.loads(new_text)
            got = ((data.get("agent") or {}).get(agent) or {}).get("model")
            if got != model:
                raise ValueError(f"{cfg.name}: контроль не прошёл (получилось {got!r})")
        except json.JSONDecodeError:
            pass
    return new_text, changed


def _backup_dir(path: Path) -> Path:
    """Каталог бэкапов рядом с файлом (скрытый, вне сканирования агентов)."""
    return path.parent / ".model-router-backups"


def _make_backup(path: Path) -> Path:
    """Бэкап файла в скрытый подкаталог; держим последние MAX_BACKUPS на файл."""
    bdir = _backup_dir(path)
    bdir.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    bpath = bdir / f"{path.name}.{ts}"
    shutil.copy2(path, bpath)
    keep = sorted(bdir.glob(f"{path.name}.*"), key=lambda p: p.name, reverse=True)
    for old in keep[MAX_BACKUPS:]:
        try:
            old.unlink()
        except OSError:
            pass
    return bpath


def _atomic_write_locked(path: Path, new_text: str, backup: bool) -> dict:
    """flock на файле + бэкап + атомарная замена. Только внутри разрешённых корней."""
    if not is_allowed(path):
        raise PermissionError(f"{path} вне разрешённых корней")
    f = path.open("r+", encoding="utf-8")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        raise RuntimeError(f"{path.name} занят другим процессом (flock)")
    info: dict = {}
    try:
        old = f.read()
        if backup:
            try:
                info["backup"] = str(_make_backup(path).relative_to(VAULT_ROOT))
            except (OSError, ValueError):
                info["backup"] = str(_make_backup(path))
        tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
        tmp.write_text(new_text, encoding="utf-8")
        os.replace(tmp, path)
        info["bytes_before"] = len(old.encode("utf-8"))
        info["bytes_after"] = len(new_text.encode("utf-8"))
    finally:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        finally:
            f.close()
    return info


def cmd_apply(args) -> int:
    model = (args.model or "").strip()
    m = MODEL_RE.match(model)
    if not m:
        return fail(f"модель должна быть в формате provider/model[/vendor]: {model!r}", 2)
    agent = (args.agent or "").strip()
    if not agent:
        return fail("--agent обязателен", 2)

    agents = collect_agents(args.project)
    cands = [a for a in agents if a["agent"] == agent]
    if args.scope:
        cands = [a for a in cands if a["scope"] == args.scope]
    if not cands:
        return fail(f"агент '{agent}' не найден (scope={args.scope or 'любой'})")
    if len(cands) > 1:
        return fail("несколько кандидатов — уточните --scope/--project: "
                    + ", ".join(f"{c['scope']}:{c['agent']}@{c['path']}" for c in cands), 2)
    target = cands[0]
    path = Path(target["path"])
    old_model = target.get("model")

    try:
        if target["kind"] == "file":
            text = path.read_text(encoding="utf-8")
            new_text, changed = _set_frontmatter_model(text, model)
        else:
            new_text, changed = _set_config_agent_model(path, agent, model)
    except (OSError, ValueError, RuntimeError) as e:
        return fail(str(e))

    diff = "".join(difflib.unified_diff(
        (path.read_text(encoding="utf-8")).splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=f"a/{path.name}", tofile=f"b/{path.name}", n=2))

    if not changed:
        return out_ok({"changed": False, "agent": agent, "scope": target["scope"],
                       "project": target["project"], "path": str(path),
                       "model": model, "old_model": old_model,
                       "note": "модель уже стоит — ничего не менялось"})
    if args.dry_run:
        return out_ok({"changed": False, "dry_run": True, "agent": agent,
                       "scope": target["scope"], "project": target["project"],
                       "path": str(path), "old_model": old_model, "model": model,
                       "diff": diff})

    try:
        info = _atomic_write_locked(path, new_text, backup=not args.no_backup)
    except (OSError, PermissionError, RuntimeError) as e:
        return fail(str(e))

    return out_ok({"changed": True, "agent": agent, "scope": target["scope"],
                   "project": target["project"], "path": str(path),
                   "old_model": old_model, "model": model,
                   "restart_required": True, "diff": diff, **info})


def out_ok(obj: dict) -> int:
    obj["ok"] = True
    out(obj)
    return 0


def cmd_list(args) -> int:
    agents = collect_agents(args.project)
    for a in agents:
        a.pop("has_frontmatter", None)
    no_model = [a["agent"] for a in agents if not a.get("model")]
    return out_ok({
        "count": len(agents),
        "agents": agents,
        "no_model": no_model,
        "by_scope": {
            "global": sum(1 for a in agents if a["scope"] == "global"),
            "project": sum(1 for a in agents if a["scope"] == "project"),
        },
        "note": "модель применяется с рестарта инструмента / новой сессии (hot-reload нет)",
    })


def main() -> int:
    p = argparse.ArgumentParser(description="model-router — модели агентов OpenCode")
    sub = p.add_subparsers(dest="cmd")

    pl = sub.add_parser("list", help="все агенты + текущая модель")
    pl.add_argument("--project", default=None, help="ограничить проектным id")

    sub.add_parser("models", help="объединённый список доступных моделей")

    pa = sub.add_parser("apply", help="сменить модель агента")
    pa.add_argument("--agent", required=True)
    pa.add_argument("--model", required=True)
    pa.add_argument("--scope", choices=["global", "project"], default=None)
    pa.add_argument("--project", default=None, help="project id (для scope=project)")
    pa.add_argument("--dry-run", action="store_true")
    pa.add_argument("--no-backup", action="store_true")

    args = p.parse_args()
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "models":
        return out_ok(collect_models())
    if args.cmd == "apply":
        return cmd_apply(args)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
