"""Анализ системных журналов на признаки инцидентов.

Читает auth.log / secure / syslog / kern.log (только чтение) и прогоняет
строки через набор правил: брутфорс, подозрительный sudo, сегфолты, OOM и т.п.
"""

from __future__ import annotations

import glob
import os
import re
import time
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..core import CheckResult, Finding, Severity, read_lines

LOG_CANDIDATES = [
    "/var/log/auth.log",
    "/var/log/secure",
    "/var/log/syslog",
    "/var/log/messages",
    "/var/log/kern.log",
    "/var/log/daemon.log",
]


def _log_files(explicit: Optional[str] = None) -> List[str]:
    if explicit:
        return [explicit] if os.path.exists(explicit) else []
    found = [p for p in LOG_CANDIDATES if os.path.exists(p)]
    if not found:
        found = sorted(glob.glob("/var/log/*.log"))
    return found


def _since_epoch(since: Optional[str]) -> Optional[float]:
    """Разобрать простой '--since' вида '30 minutes ago', '2 hours ago', '1 day ago'."""
    if not since:
        return None
    m = re.match(r"\s*(\d+)\s*(second|minute|hour|day)s?\s*ago\s*$", since)
    if not m:
        return None
    value = int(m.group(1))
    unit = m.group(2)
    mult = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}[unit]
    return time.time() - value * mult


# (имя правила, regex, серьёзность, рекомендация)
RULES: List[Tuple[str, "re.Pattern[str]", Severity, str]] = [
    (
        "SSH: неудачные попытки входа",
        re.compile(r"Failed password for .* from (?P<ip>\S+)"),
        Severity.LOW,
        "Проверьте IP на брутфорс; при массовости — fail2ban или блокировка.",
    ),
    (
        "SSH: неверный пользователь",
        re.compile(r"Invalid user (?P<user>\S+) from (?P<ip>\S+)"),
        Severity.MEDIUM,
        "Массовый перебор имён пользователей — признак автоматизированного брутфорса.",
    ),
    (
        "SSH: успешный вход root",
        re.compile(r"Accepted .* for root from (?P<ip>\S+)"),
        Severity.HIGH,
        "Прямой вход root по SSH нежелателен: запретите PermitRootLogin, используйте sudo.",
    ),
    (
        "Создание новой учётной записи",
        re.compile(r"useradd.*new user.*name=(?P<user>\S+)"),
        Severity.HIGH,
        "Проверьте, кто и зачем создал пользователя.",
    ),
    (
        "Изменение пароля",
        re.compile(r"passwd.*password changed for (?P<user>\S+)"),
        Severity.MEDIUM,
        "Убедитесь, что смена пароля санкционирована.",
    ),
    (
        "sudo: команда от пользователя",
        re.compile(r"sudo:.*COMMAND=(?P<cmd>.+)$"),
        Severity.LOW,
        "Просмотрите команды sudo на предмет аномалий.",
    ),
    (
        "sudo: ошибка аутентификации",
        re.compile(r"sudo:.*authentication failure.*user=(?P<user>\S+)"),
        Severity.MEDIUM,
        "Серия неудачных sudo — возможен подбор пароля локальным пользователем.",
    ),
    (
        "Сегфолт процесса",
        re.compile(r"segfault at .* in (?P<bin>\S+)"),
        Severity.MEDIUM,
        "Сегфолты могут указывать на эксплуатацию уязвимости.",
    ),
    (
        "OOM-killer сработал",
        re.compile(r"Out of memory: Killed process (?P<pid>\d+) \((?P<name>[^)]+)\)"),
        Severity.MEDIUM,
        "Процесс убит из-за нехватки памяти — проверьте утечки/атаку на исчерпание ресурсов.",
    ),
    (
        "Загрузка модуля ядра",
        re.compile(r"module (?P<mod>\S+) loaded|insmod.* (?P<mod2>\S+\.ko)"),
        Severity.LOW,
        "Неожиданные модули ядра (rootkit?) — проверьте происхождение.",
    ),
    (
        "Отключение защиты SELinux/AppArmor",
        re.compile(r"(SELinux is disabled|apparmor.*disabled)", re.IGNORECASE),
        Severity.HIGH,
        "Отключение MAC — типичный шаг после компрометации.",
    ),
    (
        "Изменение правил файрвола",
        re.compile(r"(ufw|iptables|nft).*(?:block|drop|deny|flush)", re.IGNORECASE),
        Severity.LOW,
        "Проверьте легитимность изменений в правилах файрвола.",
    ),
]


def _iter_lines(files: Iterable[str], since_epoch: Optional[float]) -> Iterable[Tuple[str, int, str]]:
    """Отдавать (файл, номер строки, текст), опционально отфильтровав по времени."""
    for path in files:
        for i, line in enumerate(read_lines(path), 1):
            if since_epoch is not None:
                ts = _parse_syslog_ts(line)
                if ts is not None and ts < since_epoch:
                    continue
            yield path, i, line


def _parse_syslog_ts(line: str) -> Optional[float]:
    """Попытаться разобрать метку времени syslog 'Mmm dd HH:MM:SS'."""
    m = re.match(r"([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})", line)
    if not m:
        return None
    months = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }
    month = months.get(m.group(1))
    if not month:
        return None
    now = time.localtime()
    try:
        tm = time.struct_time(
            (now.tm_year, month, int(m.group(2)), int(m.group(3)),
             int(m.group(4)), int(m.group(5)), 0, 0, -1)
        )
        return time.mktime(tm)
    except (ValueError, OverflowError):
        return None


def run(path: Optional[str] = None, since: Optional[str] = None, **_: Any) -> CheckResult:
    result = CheckResult(name="logs")
    files = _log_files(path)
    if not files:
        result.status = result.status.SKIPPED
        result.error = "журналы не найдены или недоступны"
        result.low(
            "Журналы недоступны",
            "Не найдено ни одного файла журнала (нужен root?).",
            recommendation="Запустите с правами root для чтения /var/log.",
        )
        return result

    since_epoch = _since_epoch(since)
    result.meta["files"] = files
    result.meta["since"] = since or "всё время"
    result.info("Анализируемые журналы", ", ".join(files), count=len(files))

    matches: Dict[str, List[Dict[str, Any]]] = {name: [] for name, *_ in RULES}
    failed_ips: Counter = Counter()
    invalid_users: Counter = Counter()
    lines_scanned = 0

    for fpath, lineno, line in _iter_lines(files, since_epoch):
        lines_scanned += 1
        for name, pattern, _sev, _rec in RULES:
            m = pattern.search(line)
            if not m:
                continue
            groups = m.groupdict()
            matches[name].append(
                {
                    "file": fpath,
                    "line": lineno,
                    "text": line.strip()[:400],
                    "groups": {k: v for k, v in groups.items() if v},
                }
            )
            if name == "SSH: неудачные попытки входа" and groups.get("ip"):
                failed_ips[groups["ip"]] += 1
            if name == "SSH: неверный пользователь" and groups.get("user"):
                invalid_users[groups["user"]] += 1

    result.meta["lines_scanned"] = lines_scanned

    for name, _pattern, sev, rec in RULES:
        hits = matches[name]
        if not hits:
            continue
        result.add(
            Finding(
                title=f"{name} ({len(hits)})",
                severity=sev,
                details="\n".join(h["text"] for h in hits[:5]) + ("\n…" if len(hits) > 5 else ""),
                recommendation=rec,
                data={"count": len(hits), "samples": hits[:20]},
            )
        )

    for ip, count in failed_ips.most_common(10):
        if count >= 10:
            result.high(
                f"Возможный брутфорс SSH с {ip}",
                f"{count} неудачных попыток входа",
                recommendation="Заблокируйте IP файрволом и включите fail2ban.",
                ip=ip,
                count=count,
            )
        elif count >= 3:
            result.medium(
                f"Множественные неудачные входы с {ip}",
                f"{count} попыток",
                recommendation="Проверьте IP; при повторе — блокировка.",
                ip=ip,
                count=count,
            )

    if invalid_users:
        top = ", ".join(f"{u}({c})" for u, c in invalid_users.most_common(5))
        result.info("Перебираемые имена пользователей", top, users=dict(invalid_users))

    result.summary = (
        f"{lines_scanned} строк из {len(files)} журналов, "
        f"{sum(len(v) for v in matches.values())} совпадений правил"
    )
    return result

