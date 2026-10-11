"""Контроль целостности файлов: baseline хешей и поиск изменений."""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List

from ..core import CheckResult

STATE_DIR = os.path.join(os.path.expanduser("~"), ".banu_blueteam")
BASELINE_PATH = os.path.join(STATE_DIR, "integrity_baseline.json")

# Файлы, изменение которых особенно важно заметить.
DEFAULT_TARGETS = [
    "/etc/passwd",
    "/etc/shadow",
    "/etc/group",
    "/etc/sudoers",
    "/etc/ssh/sshd_config",
    "/etc/hosts",
    "/etc/crontab",
    "/etc/ld.so.preload",
    "/root/.ssh/authorized_keys",
    "/etc/pam.d/common-auth",
    "/etc/pam.d/sshd",
    "/etc/systemd/system",
    "/usr/bin/sudo",
    "/usr/bin/ssh",
    "/bin/bash",
]


def _sha256(path: str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            data = fh.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def _collect(targets: List[str]) -> Dict[str, Dict[str, Any]]:
    """Собрать хеши файлов и каталогов (для каталогов — только верхний уровень)."""
    snapshot: Dict[str, Dict[str, Any]] = {}
    for target in targets:
        if os.path.isdir(target):
            try:
                for name in sorted(os.listdir(target)):
                    full = os.path.join(target, name)
                    if os.path.isfile(full):
                        _add(snapshot, full)
            except OSError:
                continue
        elif os.path.isfile(target):
            _add(snapshot, target)
    return snapshot


def _add(snapshot: Dict[str, Dict[str, Any]], path: str) -> None:
    try:
        st = os.stat(path)
        snapshot[path] = {
            "sha256": _sha256(path),
            "size": st.st_size,
            "mode": oct(st.st_mode & 0o777),
            "mtime": int(st.st_mtime),
        }
    except (OSError, PermissionError):
        snapshot[path] = {"error": "unreadable"}


def _load_baseline() -> Dict[str, Dict[str, Any]]:
    try:
        with open(BASELINE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_baseline(snapshot: Dict[str, Dict[str, Any]]) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = BASELINE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=1, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, BASELINE_PATH)


def run(init: bool = False, targets: List[str] | None = None, **_: Any) -> CheckResult:
    result = CheckResult(name="integrity")
    targets = targets or DEFAULT_TARGETS
    current = _collect(targets)
    result.meta["baseline_path"] = BASELINE_PATH
    result.meta["tracked_files"] = len(current)

    if init:
        _save_baseline(current)
        result.info(
            "Baseline сохранён",
            f"{len(current)} файлов → {BASELINE_PATH}",
            path=BASELINE_PATH,
        )
        result.summary = f"baseline создан: {len(current)} файлов"
        return result

    baseline = _load_baseline()
    if not baseline:
        result.low(
            "Baseline отсутствует",
            f"Файл {BASELINE_PATH} не найден.",
            recommendation="Создайте baseline: python3 -m blueteam integrity --init",
        )
        result.summary = "нет baseline — сначала выполните --init"
        return result

    added, removed, changed = [], [], []
    for path, meta in current.items():
        if path not in baseline:
            added.append(path)
        elif baseline[path].get("sha256") != meta.get("sha256"):
            changed.append((path, baseline[path], meta))
    for path in baseline:
        if path not in current:
            removed.append(path)

    result.meta.update(
        {"added": len(added), "removed": len(removed), "changed": len(changed)}
    )
    result.info(
        "Сравнение с baseline",
        f"добавлено {len(added)}, удалено {len(removed)}, изменено {len(changed)}",
    )

    for path in changed:
        p, old, new = path
        sev = "high" if _is_sensitive(p) else "medium"
        getattr(result, sev)(
            f"Файл изменён: {p}",
            f"sha256 {old.get('sha256', '?')[:16]}… → {new.get('sha256', '?')[:16]}…\n"
            f"права {old.get('mode')} → {new.get('mode')}, mtime "
            f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(new.get('mtime', 0)))}",
            recommendation="Проверьте, кто и зачем изменил файл. Для бинарников сверьте пакетный хеш (dpkg -V).",
            data={"path": p, "before": old, "after": new},
        )

    for path in added:
        result.medium(
            f"Новый файл в отслеживаемой зоне: {path}",
            "Файла не было в baseline.",
            recommendation="Убедитесь, что файл создан вами, а не злоумышленником.",
        )

    for path in removed:
        result.high(
            f"Файл удалён: {path}",
            "Файл был в baseline, но исчез.",
            recommendation="Удаление системных файлов — признак вредоносной активности.",
        )

    result.summary = (
        f"проверено {len(current)} файлов: +{len(added)} −{len(removed)} ~{len(changed)}"
    )
    return result


def _is_sensitive(path: str) -> bool:
    return any(
        path.startswith(prefix)
        for prefix in ("/etc/", "/bin/", "/usr/bin/", "/root/.ssh/")
    )
