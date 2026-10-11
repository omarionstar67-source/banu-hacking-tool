"""Детект подозрительных процессов по эвристикам.

Каждому процессу считается риск-скор. Эвристики намеренно «шумные»
(это инструмент для триажа, а не приговор) и все настраиваемы через параметры.
"""

from __future__ import annotations

import os
import pwd
from typing import Any, Dict, List, Optional, Tuple

from ..core import CheckResult, Finding, Severity, read_file, read_lines

# Каталоги, из которых обычно НЕ должны запускаться бинарники.
SUSPICIOUS_DIRS = (
    "/tmp/",
    "/var/tmp/",
    "/dev/shm/",
    "/run/shm/",
    "/tmp",
    "/var/tmp",
    "/dev/shm",
)

# Утилиты, частые «лошадки» маскировки.
LOLBINS = {
    "nc", "ncat", "netcat", "socat", "curl", "wget", "base64", "xxd",
    "python", "python3", "perl", "ruby", "php", "node", "gcc", "cc",
    "mkfifo", "telnet", "openssl", "dd",
}

# Команды-индикаторы туннелей/шеллов в аргументах.
SHELL_INDICATORS = (
    "/dev/tcp/", "bash -i", "sh -i", "mkfifo", "cmd.exe",
    "powershell -enc", "nc -e", "ncat -e", "socat exec",
)


def _cmdline(pid: int) -> str:
    raw = read_file(f"/proc/{pid}/cmdline")
    if not raw:
        return ""
    return raw.replace("\x00", " ").strip()


def _exe(pid: int) -> str:
    try:
        return os.readlink(f"/proc/{pid}/exe")
    except OSError:
        return ""


def _cwd(pid: int) -> str:
    try:
        return os.readlink(f"/proc/{pid}/cwd")
    except OSError:
        return ""


def _uid(pid: int) -> int:
    try:
        with open(f"/proc/{pid}/status") as fh:
            for line in fh:
                if line.startswith("Uid:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return -1


def _ppid(pid: int) -> int:
    try:
        with open(f"/proc/{pid}/stat") as fh:
            data = fh.read()
    except OSError:
        return -1
    try:
        after = data.rsplit(")", 1)[1].strip().split()
        return int(after[1])
    except (IndexError, ValueError):
        return -1


def _username(uid: int) -> str:
    try:
        return pwd.getpwuid(uid).pw_name
    except (KeyError, OverflowError):
        return str(uid)


def _name(pid: int) -> str:
    value = read_file(f"/proc/{pid}/comm")
    return (value or "").strip() or f"pid{pid}"


def _listening_pids() -> Dict[int, List[str]]:
    """PID -> список локальных адресов, которые процесс слушает (если есть ss)."""
    from ..core import run as run_cmd

    out: Dict[int, List[str]] = {}
    text = run_cmd(["ss", "-H", "-tulpn"])
    if not text:
        return out
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 6:
            continue
        local = parts[4]
        proc = parts[6] if len(parts) > 6 else ""
        for chunk in proc.split(","):
            if chunk.startswith("pid="):
                try:
                    pid = int(chunk[4:].split(",")[0])
                except ValueError:
                    continue
                out.setdefault(pid, []).append(local)
    return out


def score_process(pid: int, listening: Dict[int, List[str]]) -> Tuple[int, List[str]]:
    """Вернуть (risk_score, список причин) для процесса."""
    reasons: List[str] = []
    score = 0

    exe = _exe(pid)
    cmd = _cmdline(pid)
    cwd = _cwd(pid)
    name = _name(pid)

    # 1. Запуск из временного каталога.
    for target in (exe, cwd):
        if target and any(target.startswith(d) for d in SUSPICIOUS_DIRS):
            score += 40
            reasons.append(f"путь в подозрительном каталоге: {target}")
            break

    # 2. Удалённый бинарник (exe содержит " (deleted)").
    if "(deleted)" in exe:
        score += 45
        reasons.append(f"бинарник удалён с диска: {exe}")

    # 3. Индикаторы реверс-шелла в аргументах.
    low = cmd.lower()
    for ind in SHELL_INDICATORS:
        if ind.lower() in low:
            score += 35
            reasons.append(f"индикатор шелла в cmdline: {ind}")
            break

    # 4. LOLBin + сетевой слушатель = подозрительно.
    addrs = [a for a in listening.get(pid, []) if a and a != "*:*"]
    if name in LOLBINS and addrs:
        score += 25
        reasons.append(f"{name} слушает сеть: {', '.join(addrs)}")

    # 5. Процесс без exe, но с cmdline.
    if not exe and cmd:
        score += 20
        reasons.append("нет /proc/<pid>/exe, но есть cmdline (возможна инъекция)")

    # 6. Имя начинается с точки или пробела (маскировка).
    if name.startswith(".") or name.startswith(" "):
        score += 30
        reasons.append(f"маскировочное имя процесса: {name!r}")

    # 7. Скрипт-интерпретатор с inline-кодом (base64 -d | sh и т.п.).
    if any(x in low for x in ("base64 -d", "base64 --decode", "eval ", "exec(")):
        score += 30
        reasons.append("выполнение обфусцированного/встроенного кода")

    # 8. Слушает внешний адрес под непривилегированным пользователем.
    uid = _uid(pid)
    if pid in listening and uid not in (0, -1):
        for addr in listening[pid]:
            if not addr or addr in ("*:*",):
                continue
            if not addr.startswith(("127.", "::1", "[::1]")):
                score += 15
                reasons.append(f"внешний слушатель под uid {uid} ({_username(uid)}): {addr}")
                break

    return score, reasons


def _severity_for(score: int) -> Severity:
    if score >= 70:
        return Severity.CRITICAL
    if score >= 45:
        return Severity.HIGH
    if score >= 25:
        return Severity.MEDIUM
    if score > 0:
        return Severity.LOW
    return Severity.INFO


def collect_processes() -> List[Dict[str, Any]]:
    """Собрать базовую информацию о всех процессах."""
    listening = _listening_pids()
    procs: List[Dict[str, Any]] = []
    for pid in _iter_pids():
        uid = _uid(pid)
        cmd = _cmdline(pid)
        procs.append(
            {
                "pid": pid,
                "ppid": _ppid(pid),
                "name": _name(pid),
                "uid": uid,
                "user": _username(uid),
                "exe": _exe(pid),
                "cwd": _cwd(pid),
                "cmdline": cmd,
                "listening": listening.get(pid, []),
            }
        )
    return procs


def _iter_pids() -> List[int]:
    try:
        return sorted(int(n) for n in os.listdir("/proc") if n.isdigit())
    except OSError:
        return []


def run(min_score: int = 25, **_: Any) -> CheckResult:
    result = CheckResult(name="processes")
    procs = collect_processes()
    if not procs:
        result.status = result.status.ERROR
        result.error = "/proc недоступен"
        return result

    listening_map = {p["pid"]: p["listening"] for p in procs}
    suspicious: List[Dict[str, Any]] = []

    for proc in procs:
        score, reasons = score_process(proc["pid"], listening_map)
        if score >= min_score:
            suspicious.append(
                {
                    "pid": proc["pid"],
                    "ppid": proc["ppid"],
                    "name": proc["name"],
                    "user": proc["user"],
                    "cmdline": proc["cmdline"],
                    "exe": proc["exe"],
                    "score": score,
                    "reasons": reasons,
                }
            )

    suspicious.sort(key=lambda p: p["score"], reverse=True)

    result.meta["total_processes"] = len(procs)
    result.meta["suspicious_count"] = len(suspicious)
    result.meta["min_score"] = min_score
    result.info("Процессов просканировано", str(len(procs)))

    if not suspicious:
        result.info("Подозрительных процессов не найдено", f"порог скора: {min_score}")
    else:
        for item in suspicious:
            sev = _severity_for(item["score"])
            detail = (
                f"PID {item['pid']} (ppid {item['ppid']}) user={item['user']} "
                f"score={item['score']}\n"
                f"  cmd: {item['cmdline'][:300]}\n"
                f"  exe: {item['exe'] or 'n/a'}\n"
                f"  причины: " + "; ".join(item["reasons"])
            )
            result.add(
                Finding(
                    title=f"Подозрительный процесс: {item['name']} (pid {item['pid']})",
                    severity=sev,
                    details=detail,
                    recommendation=(
                        "Проверьте процесс: ps -fp PID, ls -l /proc/PID/exe, "
                        "сравните хеш бинарника с эталоном."
                    ),
                    data=item,
                )
            )

    # Отдельно: процессы с удалёнными бинарниками — даже при низком скоре.
    deleted = [p for p in procs if "(deleted)" in (p["exe"] or "")]
    if deleted:
        result.meta["deleted_binaries"] = len(deleted)

    result.summary = (
        f"{len(procs)} процессов, {len(suspicious)} выше порога {min_score}"
    )
    return result
