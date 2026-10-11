"""Поиск SUID/SGID-бинарников и world-writable файлов.

Ограниченно сканирует заданные корни, чтобы не съедать диск целиком.
"""

from __future__ import annotations

import os
import stat
from typing import Any, Dict, Iterable, List, Set

from ..core import CheckResult

# Ожидаемые SUID-бинарники в типичной Debian/Ubuntu-системе.
KNOWN_SUID: Set[str] = {
    "/usr/bin/sudo", "/usr/bin/su", "/usr/bin/passwd", "/usr/bin/chsh",
    "/usr/bin/chfn", "/usr/bin/newgrp", "/usr/bin/gpasswd", "/usr/bin/mount",
    "/usr/bin/umount", "/usr/bin/pkexec", "/usr/bin/fusermount",
    "/usr/bin/fusermount3", "/usr/bin/crontab", "/usr/bin/at",
    "/usr/bin/ssh-agent", "/usr/lib/openssh/ssh-keysign",
    "/usr/lib/dbus-1.0/dbus-daemon-launch-helper",
    "/usr/lib/policykit-1/polkit-agent-helper-1",
    "/usr/lib/snapd/snap-confine", "/usr/bin/ntfs-3g", "/usr/bin/expiry",
    "/usr/bin/chage", "/usr/bin/wall", "/usr/bin/write",
}

DEFAULT_ROOTS = ["/usr", "/bin", "/sbin", "/opt", "/tmp", "/var/tmp", "/dev/shm", "/home"]

# Каталоги, которые не обходим (слишком большие или виртуальные).
SKIP_DIRS = {"/proc", "/sys", "/dev", "/run", "/snap", "/var/lib/docker"}


def _walk(roots: Iterable[str], max_entries: int = 400_000) -> Iterable[str]:
    count = 0
    for root in roots:
        if not os.path.isdir(root) or root in SKIP_DIRS:
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [
                d for d in dirnames
                if os.path.join(dirpath, d) not in SKIP_DIRS
            ]
            for name in filenames:
                count += 1
                if count > max_entries:
                    return
                yield os.path.join(dirpath, name)


def run(roots: List[str] | None = None, **_: Any) -> CheckResult:
    result = CheckResult(name="suid")
    roots = roots or DEFAULT_ROOTS
    suid: List[Dict[str, Any]] = []
    sgid: List[Dict[str, Any]] = []
    world_writable: List[Dict[str, Any]] = []

    for path in _walk(roots):
        try:
            st = os.lstat(path)
        except (OSError, PermissionError):
            continue
        if not stat.S_ISREG(st.st_mode):
            continue
        mode = st.st_mode
        if mode & stat.S_ISUID:
            suid.append({"path": path, "mode": oct(mode & 0o7777), "size": st.st_size})
        if mode & stat.S_ISGID:
            sgid.append({"path": path, "mode": oct(mode & 0o7777), "size": st.st_size})
        if (mode & stat.S_IWOTH) and not (mode & stat.S_ISLNK):
            world_writable.append({"path": path, "mode": oct(mode & 0o7777)})

    result.meta["suid_count"] = len(suid)
    result.meta["sgid_count"] = len(sgid)
    result.meta["world_writable_count"] = len(world_writable)

    unexpected = [
        s for s in suid
        if s["path"] not in KNOWN_SUID
        and os.path.realpath(s["path"]) not in KNOWN_SUID
    ]
    for entry in unexpected:
        sev = "high" if entry["path"].startswith(("/tmp/", "/var/tmp/", "/dev/shm/", "/home/")) else "medium"
        getattr(result, sev)(
            f"Нестандартный SUID-бинарник: {entry['path']}",
            f"права {entry['mode']}, размер {entry['size']} байт",
            recommendation=(
                "Проверьте происхождение файла. SUID вне стандартных путей — "
                "частый способ повышения привилегий: chmod u-s файл."
            ),
            data=entry,
        )

    result.info("SUID-бинарники", f"{len(suid)} найдено, {len(unexpected)} нестандартных", suid=suid)
    result.info("SGID-бинарники", f"{len(sgid)} найдено", sgid=sgid[:100])

    # World-writable в системных каталогах — отдельно, это опасно.
    risky_ww = [
        w for w in world_writable
        if w["path"].startswith(("/etc/", "/usr/", "/bin/", "/sbin/", "/var/spool/"))
    ]
    for entry in risky_ww[:50]:
        result.high(
            f"Файл, доступный на запись всем: {entry['path']}",
            f"права {entry['mode']}",
            recommendation="Уберите бит записи для остальных: chmod o-w файл.",
            data=entry,
        )
    result.meta["world_writable_system"] = len(risky_ww)
    if world_writable:
        result.info(
            "World-writable файлы",
            f"{len(world_writable)} всего, {len(risky_ww)} в системных каталогах",
            sample=world_writable[:100],
        )

    result.summary = (
        f"SUID: {len(suid)} ({len(unexpected)} нестандартных), SGID: {len(sgid)}, "
        f"world-writable: {len(world_writable)}"
    )
    return result
