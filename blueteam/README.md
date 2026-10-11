# BANU Blue Team Module 🛡️

Защитный (blue-team) набор инструментов для **мониторинга и аудита собственного хоста**.
Модуль ничего не атакует: он только читает локальное состояние системы (`/proc`, `/var/log`,
аудио-подсистему) и помогает заметить подозрительную активность.

> ⚠️ **Область применения:** модуль рассчитан на хосты, которыми вы владеете или которые
> вам доверены для администрирования. Никаких сетевых атак, брутфорса или сканирования
> чужих адресов здесь нет и не будет.

---

## Возможности

| Модуль | Команда | Что делает |
|--------|---------|------------|
| Инвентаризация хоста | `inventory` | ОС, ядро, uptime, CPU/RAM/диск, сетевые интерфейсы, слушающие порты |
| Аудит пользователей | `users` | Учётные записи с UID 0, пустые пароли, sudoers, свежие логины |
| Аудит процессов | `processes` | Детект подозрительных процессов по эвристикам (пути, имена, родители) |
| Аудит сети | `network` | Слушающие порты с PID, установленные соединения, необычные состояния |
| Анализ логов | `logs` | Прогон auth/syslog через набор правил (brute-force, sudo, сегфолты) |
| Персистентность | `persistence` | Проверка cron, systemd-юнитов, rc.local, autostart, профилей shell |
| Целостность файлов | `integrity` | Хеширование важных файлов, сохранение baseline, поиск изменений |
| SUID/SGID | `suid` | Поиск SUID/SGID-бинарников и world-writable файлов |
| Признаки руткитов | `rootkit` | LD_PRELOAD, скрытые от ps процессы, необычные модули ядра, подмена coreutils |
| Отчёт | `report` | Свод всех проверок в Markdown/JSON |

Все модули работают **только на чтение** (или создают свои файлы состояния в
`~/.banu_blueteam/`).

---

## Быстрый старт

```bash
# Полный отчёт в markdown
python3 -m blueteam report --format markdown --output report.md

# Отдельные проверки
python3 -m blueteam inventory
python3 -m blueteam processes --min-score 40
python3 -m blueteam logs --since "2 hours ago"
python3 -m blueteam integrity --init          # создать baseline
python3 -m blueteam integrity                 # сравнить с baseline
python3 -m blueteam rootkit                   # признаки руткитов
```

Без зависимостей: используется только стандартная библиотека Python 3.8+.
Часть проверок требует root (чтение `/etc/shadow`, полный список сокетов) —
без root модуль честно помечает такие проверки как `SKIPPED`.

---

## Структура

```
blueteam/
├── __init__.py         # версия пакета
├── __main__.py         # точка входа `python3 -m blueteam`
├── cli.py              # парсер аргументов и диспетчеризация
├── core.py             # общие утилиты, ModelCheck, Severity, вывод
├── modules/
│   ├── inventory.py
│   ├── users.py
│   ├── processes.py
│   ├── network.py
│   ├── logs.py
│   ├── persistence.py
│   ├── integrity.py
│   ├── rootkit.py
│   └── suid.py
└── report.py           # сборка markdown/json-отчёта
```

Каждая проверка возвращает объект `CheckResult` со списком `Finding`.
`Finding` содержит серьёзность (`Severity`), заголовок, детали и рекомендацию.
