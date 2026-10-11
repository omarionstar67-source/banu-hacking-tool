"""Общие примитивы blue-team модуля: результаты, серьёзность, хелперы.

Модуль намеренно не имеет внешних зависимостей и работает только на чтение.
"""

from __future__ import annotations

import enum
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


class Severity(enum.IntEnum):
    """Серьёзность находки. Значения упорядочены: чем больше, тем важнее."""

    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def label(self) -> str:
        return {
            Severity.INFO: "INFO",
            Severity.LOW: "LOW",
            Severity.MEDIUM: "MEDIUM",
            Severity.HIGH: "HIGH",
            Severity.CRITICAL: "CRITICAL",
        }[self]


@dataclass
class Finding:
    """Одна конкретная находка внутри проверки."""

    title: str
    severity: Severity = Severity.INFO
    details: str = ""
    recommendation: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity.label,
            "severity_value": int(self.severity),
            "details": self.details,
            "recommendation": self.recommendation,
            "data": self.data,
        }


class CheckStatus(enum.Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class CheckResult:
    """Результат выполнения одной проверки."""

    name: str
    status: CheckStatus = CheckStatus.OK
    summary: str = ""
    findings: List[Finding] = field(default_factory=list)
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def info(self, title: str, details: str = "", **data: Any) -> None:
        self.add(Finding(title, Severity.INFO, details, "", dict(data)))

    def low(self, title: str, details: str = "", recommendation: str = "", **data: Any) -> None:
        self.add(Finding(title, Severity.LOW, details, recommendation, dict(data)))

    def medium(self, title: str, details: str = "", recommendation: str = "", **data: Any) -> None:
        self.add(Finding(title, Severity.MEDIUM, details, recommendation, dict(data)))

    def high(self, title: str, details: str = "", recommendation: str = "", **data: Any) -> None:
        self.add(Finding(title, Severity.HIGH, details, recommendation, dict(data)))

    def critical(self, title: str, details: str = "", recommendation: str = "", **data: Any) -> None:
        self.add(Finding(title, Severity.CRITICAL, details, recommendation, dict(data)))

    @property
    def highest_severity(self) -> Severity:
        if not self.findings:
            return Severity.INFO
        return max(f.severity for f in self.findings)

    @property
    def counts(self) -> Dict[str, int]:
        result = {s.label: 0 for s in Severity}
        for f in self.findings:
            result[f.severity.label] += 1
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "summary": self.summary,
            "error": self.error,
            "meta": self.meta,
            "counts": self.counts,
            "findings": [f.to_dict() for f in self.findings],
        }


class PrivilegeError(RuntimeError):
    """Проверка требует повышенных прав."""


def is_root() -> bool:
    try:
        return os.geteuid() == 0
    except AttributeError:  # pragma: no cover - экзотические платформы
        return False


def read_file(path: str, max_bytes: int = 2_000_000) -> Optional[str]:
    """Прочитать текстовый файл, вернуть None при ошибке. Только чтение."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read(max_bytes)
    except (OSError, PermissionError):
        return None


def read_lines(path: str) -> List[str]:
    content = read_file(path)
    if content is None:
        return []
    return content.splitlines()


def run(cmd: List[str], timeout: int = 15) -> Optional[str]:
    """Безопасный запуск внешней утилиты без shell. Возвращает stdout или None."""
    if not cmd or shutil.which(cmd[0]) is None:
        return None
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0 and not proc.stdout:
        return None
    return proc.stdout


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def iter_proc_pids() -> Iterable[int]:
    """Перебрать числовые PID из /proc."""
    try:
        entries = os.listdir("/proc")
    except OSError:
        return []
    pids = []
    for name in entries:
        if name.isdigit():
            pids.append(int(name))
    return pids


def proc_field(pid: int, name: str) -> Optional[str]:
    value = read_file(f"/proc/{pid}/{name}")
    if value is None:
        return None
    return value.strip("\x00").strip()


def parse_key_values(block: str, sep: str = "=") -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or sep not in line:
            continue
        key, _, value = line.partition(sep)
        out[key.strip()] = value.strip()
    return out


def human_bytes(num: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} EiB"
