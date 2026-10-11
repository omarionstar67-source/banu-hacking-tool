"""Проверка механизмов персистентности: cron, systemd, rc.local, профили shell."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List

from ..core import CheckResult, read_file, read_lines, run

CRON_DIRS = [
    "/etc/cron.d",
    "/etc/cron.daily",
    "/etc/cron.hourly",
    "/etc/cron.weekly",
    "/etc/cron.monthly",
]
SHELL_PROFILES = [
    "/etc/profile",
    "/etc/bash.bashrc",
    "/root/.bashrc",
    "/root/.profile",
    "/root/.bash_profile",
]
# Подозрительные приёмы в строках автозапуска.
SUSPICIOUS_PATTERNS = [
    re.compile(r"(curl|wget)\s+[^\s|]+\s*\|\s*(ba)?sh", re.IGNORECASE),
    re.compile(r"base64\s+(-d|--decode)", re.IGNORECASE),
    re.compile(r"/dev/tcp/", re.IGNORECASE),
    re.compile(r"nc\s+-[a-z]*e", re.IGNORECASE),
    re.compile(r"bash\s+-i", re.IGNORECASE),
    re.compile(r"python[23]?\s+-c\s+", re.IGNORECASE),
    re.compile(r"eval\s*\(", re.IGNORECASE),
]


def _scan_cron() -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for line in read_lines("/etc/crontab"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.append({"source": "/etc/crontab", "line": stripped})

    for d in CRON_DIRS:
        try:
            names = sorted(os.listdir(d))
        except OSError:
            continue
        for name in names:
            full = os.path.join(d, name)
            if not os.path.isfile(full):
                continue
            for line in read_lines(full):
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    entries.append({"source": full, "line": stripped})

    for spool in ("/var/spool/cron/crontabs", "/var/spool/cron"):
        if not os.path.isdir(spool):
            continue
        for user in sorted(os.listdir(spool)):
            full = os.path.join(spool, user)
            if not os.path.isfile(full):
                continue
            for line in read_lines(full):
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    entries.append({"source": f"crontab[{user}]", "line": stripped})
    return entries


def _scan_profiles() -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for path in SHELL_PROFILES:
        for line in read_lines(path):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append({"source": path, "line": stripped})
    return entries


def _is_suspicious(text: str) -> bool:
    return any(p.search(text) for p in SUSPICIOUS_PATTERNS)


def _scan_authorized_keys() -> List[Dict[str, str]]:
    found: List[Dict[str, str]] = []
    targets: List[str] = ["/root/.ssh/authorized_keys"]
    try:
        import pwd

        for entry in pwd.getpwall():
            if entry.pw_uid >= 1000 and entry.pw_dir:
                targets.append(os.path.join(entry.pw_dir, ".ssh", "authorized_keys"))
    except (ImportError, KeyError):
        pass
    for path in targets:
        for line in read_lines(path):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                parts = stripped.split()
                found.append(
                    {
                        "file": path,
                        "key": (parts[0] + " " + (parts[2] if len(parts) > 2 else ""))[:80],
                    }
                )
    return found


def run(**_: Any) -> CheckResult:
    result = CheckResult(name="persistence")

    cron = _scan_cron()
    result.meta["cron_entries"] = len(cron)
    result.info("Записи cron", f"{len(cron)} активных", entries=cron)

    suspicious_cron = [e for e in cron if _is_suspicious(e["line"])]
    for entry in suspicious_cron:
        result.critical(
            "Подозрительная запись cron",
            f"{entry['source']}: {entry['line']}",
            recommendation="Скачивание и запуск кода из сети — типичный признак бэкдора. Проверьте запись.",
            data=entry,
        )

    tmp_cron = [e for e in cron if "/tmp/" in e["line"] or "/dev/shm/" in e["line"]]
    for entry in tmp_cron:
        result.high(
            "Cron-задача ссылается на временный каталог",
            f"{entry['source']}: {entry['line']}",
            recommendation="Запуск из /tmp или /dev/shm — признак персистентности вредоноса.",
            data=entry,
        )

    profiles = _scan_profiles()
    result.meta["profile_lines"] = len(profiles)
    for entry in [e for e in profiles if _is_suspicious(e["line"])]:
        result.high(
            "Подозрительная строка в профиле shell",
            f"{entry['source']}: {entry['line']}",
            recommendation="Проверьте, кто добавил эту строку; она выполняется при каждом входе.",
            data=entry,
        )

    if os.path.exists("/etc/rc.local"):
        content = read_file("/etc/rc.local") or ""
        lines = [
            l.strip() for l in content.splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        body = [l for l in lines if l != "exit 0"]
        if body:
            result.medium(
                "Активный /etc/rc.local",
                "\n".join(body[:10]),
                recommendation="Уберите лишние команды — этот файл выполняется при загрузке.",
                lines=body,
            )

    keys = _scan_authorized_keys()
    if keys:
        result.high(
            "Ключи в authorized_keys",
            "\n".join(f"{k['file']}: {k['key']}" for k in keys[:10]),
            recommendation="Проверьте каждый ключ: неизвестные удалите, доступ root — только при необходимости.",
            keys=keys,
        )

    result.summary = (
        f"cron: {len(cron)} записей ({len(suspicious_cron)} подозрительных), "
        f"профилей: {len(profiles)}, ключей: {len(keys)}"
    )
    return result

