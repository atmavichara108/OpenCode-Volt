import json
import os
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[3]
DOTENV_PATH = VAULT_ROOT / ".env"
AUTH_JSON_PATH = Path.home() / ".local" / "share" / "opencode" / "auth.json"

_dotenv_cache = None
_auth_cache = None


def load_dotenv_file(path=None):
    global _dotenv_cache
    path = path or DOTENV_PATH
    if _dotenv_cache is not None and path == DOTENV_PATH:
        return _dotenv_cache
    data = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            name = name.strip()
            value = value.strip().strip("'").strip('"')
            if name:
                data[name] = value
    except OSError:
        data = {}
    if path == DOTENV_PATH:
        _dotenv_cache = data
    return data


def load_auth_json(path=None):
    global _auth_cache
    path = path or AUTH_JSON_PATH
    if _auth_cache is not None and path == AUTH_JSON_PATH:
        return _auth_cache
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except (OSError, json.JSONDecodeError):
        data = {}
    if path == AUTH_JSON_PATH:
        _auth_cache = data
    return data


def reset_cache():
    global _dotenv_cache, _auth_cache
    _dotenv_cache = None
    _auth_cache = None


def resolve_key(env_name, auth_id, env=None, dotenv=None, auth=None):
    if env is None:
        env = os.environ
    if dotenv is None:
        dotenv = load_dotenv_file()
    if auth is None:
        auth = load_auth_json()

    if env_name:
        val = env.get(env_name) or dotenv.get(env_name)
        if val:
            source = "env" if env.get(env_name) else "dotenv"
            return val, source

    if auth_id:
        entry = auth.get(auth_id)
        if isinstance(entry, dict):
            val = entry.get("key")
            if val:
                return val, "auth.json"

    return "", "none"
