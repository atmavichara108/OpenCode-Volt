# mem-index

Центральный индекс памяти и спеков экосистемы. Память проектов живёт
локально (владение не трогаем), здесь — заголовки с номерами строк,
mtime/size и список спек. Формат — в духе `ecosystem-map/data.json`.

## Использование

```bash
python3 tools/mem-index/index.py build                                     # пересборка index.json
python3 tools/mem-index/index.py get --path <файл> --header <подстрока>    # секция файла
```

Пересборка — при flush/dream или вручную. Коммит `index.json` — за librarian
одним пакетом с его правками (автор не коммитит).

## Источники

См. `SOURCES` в `index.py`: dotfiles, vault, ChaT, AndroidOS, SERPlux, dv-hub.
Недостающие пути пропускаются. rudra-phone / rudra-ai / prod-monitor — TODO
(нет подтверждённых memory-точек в карточках).
