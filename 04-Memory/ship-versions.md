---
type: Registry
title: Реестр слепков /ship — версии экосистемы
ssot: true
timestamp: 2026-10-23
---
# Реестр версий экосистемы (timeshift markers)

Каждый слепок = git-тег + запись здесь. Формат тега: `ship-YYYY-MM-DD[-suffix]`.
Слепок — машиночитаемое положение: vault main SHA + dotfiles main SHA + список
репозиториев с SHA + фокус дня.

## Как снять слепок
```bash
# 1) Зафиксировать SHA обоих репозиториев
VAULT=$(git -C /home/rudra/Projects/OpenCode-Vault rev-parse HEAD)
DOTFILES=$(git -C /home/rudra/dotfiles rev-parse HEAD)
# 2) Обновить эту таблицу (append-only)
# 3) Тег репозитория-основы (vault)
git -C /home/rudra/Projects/OpenCode-Vault tag -a ship-YYYY-MM-DD -m "..."
```

## Версии
| `ship-2026-10-30` | 2026-10-30 | `4cb238ff` | — | само-аудит 5/5 | Р-035 канон+инжект; могильники 6708→2049; сессионный коп вылечен; корень графов = нет цикла регенерации; 11 личных сессий — решение владельца (не регистрируем) |
| Версия | Дата | Vault SHA | Dotfiles SHA | Фокус | Ключевые события |
|--------|------|-----------|--------------|-------|------------------|
| `ship-2026-10-23` | 2026-10-23 | `f0d54235` | `8087455` | UAS в строю, гомеостаз v1, /ship механизация | Р-023 УАС, Р-024 рамка ротатора, Р-025 гомеостаз, docs/org манифесты (3), git-freed activated proactive, tech-debt, ship-versions, Deck v4, Inception заявка, Q-005 отчёт |
