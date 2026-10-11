"""Пакет проверок blue-team модуля."""

from __future__ import annotations

from typing import Callable, Dict, List

from ..core import CheckResult

from . import (
    integrity,
    inventory,
    logs,
    network,
    persistence,
    processes,
    rootkit,
    suid,
    users,
)

# Реестр проверок: имя -> (функция, краткое описание).
# Это тот самый «реестр команд», которого не было в banu.py.
REGISTRY: Dict[str, Callable[..., CheckResult]] = {
    "inventory": inventory.run,
    "users": users.run,
    "processes": processes.run,
    "network": network.run,
    "logs": logs.run,
    "persistence": persistence.run,
    "integrity": integrity.run,
    "suid": suid.run,
    "rootkit": rootkit.run,
}

DESCRIPTIONS: Dict[str, str] = {
    "inventory": "Инвентаризация ОС, ресурсов и слушающих портов",
    "users": "Аудит учётных записей и прав",
    "processes": "Детект подозрительных процессов",
    "network": "Слушающие порты и активные соединения",
    "logs": "Анализ системных журналов на инциденты",
    "persistence": "Механизмы автозапуска и персистентности",
    "integrity": "Контроль целостности важных файлов",
    "suid": "Поиск SUID/SGID и world-writable файлов",
    "rootkit": "Признаки руткитов: LD_PRELOAD, скрытые процессы, модули",
}

ALL_CHECKS: List[str] = list(REGISTRY.keys())

__all__ = ["REGISTRY", "DESCRIPTIONS", "ALL_CHECKS"]
