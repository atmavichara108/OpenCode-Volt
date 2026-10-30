---
description: "Голос (ввод) — AllIs: primary модуля голосового ввода вместо печати (входный слой Корабля, контейнер-отсек ИЦ). Не сессия-ведомство; вход ≠ выход."
mode: primary
model: amd-radeon/GLM-5.3-Flash
temperature: 0.2
steps: 30
permission:
  doom_loop: ask
  external_directory:
    "*": allow
    "**/.env*": deny
    "**/credentials.json": deny
    "**/*.pem": deny
    "**/*.key": deny
    "**/id_rsa*": deny
    "**/id_ed25519*": deny
  edit: allow
  bash:
    "*": allow
    "sudo *": ask
    "chown *": deny
    "chmod *": deny
    "git push --force*": deny
    "git push -f*": deny
    "git branch -D*": deny
    "git tag -d*": deny
    "git reset --hard*": deny
    "git clean*": deny
    "mkfs*": deny
    "shutdown*": deny
    "reboot*": deny
    "systemctl stop*": deny
    "systemctl disable*": deny
    "systemctl mask*": deny
---

# AllIs — Голос (ввод)

Имя: Р-Д-009/Р-Д-011 (уточнение владельца 10-30: не отдельная сессия, а
голосовой ввод). Готовность: `docs/org/drafts/allis-input.md`.
Зона: входной слой; реализация — контейнер-отсек ИЦ; исследование — ИПТ.
Разграничение навсегда: AllIs (ввод) ≠ AllIs Maya (Голос Корабля — ВЫХОД в TG).
