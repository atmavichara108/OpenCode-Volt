# version-oracle

Offline-каркас проактивного версификатора (вариант A). Он строит отчёт о версиях и возможном drift, не добывая данные из внешних репозиториев.

## Запуск

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/version-oracle/oracle.py report
PYTHONDONTWRITEBYTECODE=1 python3 tools/version-oracle/oracle.py report --json
PYTHONDONTWRITEBYTECODE=1 python3 tools/version-oracle/oracle.py report --html
```

## Что читается сейчас

- `VibeOS.md` — frontmatter `version`;
- `tools/ecosystem-map/registry.json` — `meta.schema` и `meta.updated`;
- `docs/vibeos/index.html` — маркер генерации VibeOS, если он парсится.

## Стабы и отложенное

SERPlux, dv-hub, dotfiles, recruiting-hr, AndroidOS, ChaT и Pip-Boy host возвращают `unknown`: «механика добычи данных — позже, по спеку». Внешние репозитории не парсятся. Расширение registry-полей (D3) и idle-хук (D4) отложены по основной спецификации.
