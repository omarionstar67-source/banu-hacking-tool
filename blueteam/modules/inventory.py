"""Инвентаризация хоста: ОС, ресурсы, интерфейсы, слушающие порты.

Только чтение. Сетевые интерфейсы берутся из /sys и /proc, без сканирования.
"""

from __future__ import annotations

import os
import platform
import socket
import time
from typing import Any, Dict, List

from ..core import CheckResult, human_bytes, is_root, read_file, read_lines
from ..core import run as run_cmd


def _uptime() -> str:
    content = read_file("/proc/uptime")
    if not content:
        return "n/a"
    try:
        seconds = float(content.split()[0])
    except (ValueError, IndexError):
        return "n/a"
    days, rem = divmod(int(seconds), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    return f"{days}д {hours}ч {minutes}м"


def _loadavg() -> str:
    content = read_file("/proc/loadavg")
    if not content:
        return "n/a"
    return " ".join(content.split()[:3])


def _meminfo() -> Dict[str, int]:
    info: Dict[str, int] = {}
    for line in read_lines("/proc/meminfo"):
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        parts = value.strip().split()
        if not parts:
            continue
        try:
            info[key.strip()] = int(parts[0]) * 1024  # kB -> bytes
        except ValueError:
            continue
    return info


def _cpu_model() -> str:
    for line in read_lines("/proc/cpuinfo"):
        if line.lower().startswith("model name"):
            return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def _interfaces() -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    try:
        names = sorted(os.listdir("/sys/class/net"))
    except OSError:
        return result
    for name in names:
        entry: Dict[str, Any] = {"name": name}
        state = read_file(f"/sys/class/net/{name}/operstate")
        if state:
            entry["state"] = state.strip()
        try:
            with open(f"/sys/class/net/{name}/address") as fh:
                entry["mac"] = fh.read().strip()
        except OSError:
            pass
        addr = run_cmd(["ip", "-o", "addr", "show", "dev", name])
        if addr:
            for token in addr.split():
                if "/" in token and token.count(":") >= 2:
                    entry["addr"] = token
        result.append(entry)
    return result


def _listening_ports() -> List[Dict[str, str]]:
    """Список слушающих сокетов через ss, если он доступен."""
    out: List[Dict[str, str]] = []
    text = run_cmd(["ss", "-H", "-tulpn"])
    if text:
        for line in text.splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            out.append(
                {
                    "proto": parts[0],
                    "state": parts[1],
                    "local": parts[4],
                    "process": parts[6] if len(parts) > 6 else "",
                }
            )
        return out

    # Fallback: разбор /proc/net/{tcp,udp} (без имён процессов).
    for proto, path in (("tcp", "/proc/net/tcp"), ("udp", "/proc/net/udp")):
        for line in read_lines(path)[1:]:
            cols = line.split()
            if len(cols) < 4:
                continue
            local = cols[1]
            state = cols[3]
            try:
                ip_hex, port_hex = local.split(":")
                port = int(port_hex, 16)
                ip = ".".join(str(int(ip_hex[i : i + 2], 16)) for i in (6, 4, 2, 0))
            except (ValueError, IndexError):
                continue
            if proto == "tcp" and state != "0A":  # 0A = LISTEN
                continue
            out.append(
                {
                    "proto": proto,
                    "state": "LISTEN" if proto == "tcp" else "UNCONN",
                    "local": f"{ip}:{port}",
                    "process": "",
                }
            )
    return out


def _distro() -> str:
    for line in read_lines("/etc/os-release"):
        if line.startswith("PRETTY_NAME="):
            return line.split("=", 1)[1].strip().strip('"')
    return "unknown"


def run(**_: Any) -> CheckResult:
    result = CheckResult(name="inventory")

    uname = platform.uname()
    hostname = socket.gethostname()
    try:
        up_seconds = float((read_file("/proc/uptime") or "0 0").split()[0] or 0)
    except (ValueError, IndexError):
        up_seconds = 0.0
    boot = time.time() - up_seconds

    result.info(
        "Параметры хоста",
        f"{hostname} | {uname.system} {uname.release} | {uname.machine}",
        hostname=hostname,
        kernel=uname.release,
        arch=uname.machine,
        python=platform.python_version(),
        uptime=_uptime(),
        boot_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot)),
        loadavg=_loadavg(),
        cpu=_cpu_model(),
        cpu_count=os.cpu_count(),
    )

    mem = _meminfo()
    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", mem.get("MemFree", 0))
    swap_total = mem.get("SwapTotal", 0)
    swap_free = mem.get("SwapFree", 0)
    if total:
        used_pct = 100.0 * (total - available) / total
        msg = (
            f"RAM: {human_bytes(total - available)} / {human_bytes(total)} "
            f"({used_pct:.0f}%), swap: {human_bytes(swap_total - swap_free)} / {human_bytes(swap_total)}"
        )
        if used_pct > 95:
            result.high("Память почти исчерпана", msg,
                        recommendation="Проверьте процессы-пожиратели памяти; возможен OOM-kill.")
        elif used_pct > 85:
            result.medium("Высокое потребление памяти", msg,
                          recommendation="Найдите крупнейшие процессы (blueteam processes).")
        else:
            result.info("Использование памяти", msg)
        result.meta["memory"] = {
            "total": total,
            "available": available,
            "used_percent": round(used_pct, 1),
        }

    disks = []
    try:
        usage = os.statvfs("/")
        d_total = usage.f_blocks * usage.f_frsize
        d_free = usage.f_bavail * usage.f_frsize
        d_used = d_total - d_free
        pct = 100.0 * d_used / d_total if d_total else 0
        disks.append({"mount": "/", "total": d_total, "free": d_free, "used_percent": round(pct, 1)})
        if pct > 95:
            result.critical(
                "Корневой раздел почти заполнен",
                f"/: {pct:.0f}% ({human_bytes(d_free)} свободно)",
                recommendation="Освободите место: заполненный / ломает логирование и сервисы.",
            )
        elif pct > 85:
            result.high(
                "Мало свободного места на /",
                f"/: {pct:.0f}% занято",
                recommendation="Запланируйте очистку или расширение диска.",
            )
    except OSError as exc:
        result.error = f"statvfs: {exc}"

    ifaces = _interfaces()
    result.info(
        "Сетевые интерфейсы",
        ", ".join(f"{i['name']}({i.get('state', '?')})" for i in ifaces) or "нет данных",
        interfaces=ifaces,
    )

    ports = _listening_ports()
    exposed = [p for p in ports if not p["local"].startswith(("127.", "::1", "[::1]"))]
    result.info(
        "Слушающие сокеты",
        f"всего {len(ports)}, доступных извне {len(exposed)}",
        ports=ports,
    )
    if exposed and not is_root():
        result.meta["note"] = "Имена процессов слушателей видны только под root."

    result.meta.update(
        {
            "hostname": hostname,
            "kernel": uname.release,
            "distro": _distro(),
            "disks": disks,
            "listening_total": len(ports),
            "listening_external": len(exposed),
        }
    )
    result.summary = (
        f"{hostname}: {uname.system} {uname.release}, uptime {_uptime()}, "
        f"{len(ports)} слушающих сокетов"
    )
    return result

