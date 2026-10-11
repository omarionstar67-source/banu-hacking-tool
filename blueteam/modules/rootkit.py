"""Детект признаков руткитов: LD_PRELOAD, скрытые модули, аномалии /proc.

Это защитная (blue-team) проверка: она ищет следы сокрытия, а не создаёт их.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Set

from ..core import CheckResult, read_file, read_lines
from ..core import run as run_cmd

# Легитимные модули, которые часто встречаются на обычных системах.
COMMON_MODULE_PREFIXES = (
    "xt_", "nf_", "nft_", "iptable_", "ip6table_", "arptable_", "ip_", "ip6_", "nls_", "snd_", "vfat", "fat", "loop",
    "overlay", "binfmt_", "autofs", "fuse", "dm_", "raid", "ext4", "xfs",
    "btrfs", "tcp_", "udp_", "8021q", "bridge", "bonding", "veth", "tun",
    "dummy", "efi_pstore", "kvm", "mac80211", "cfg80211", "rfkill", "bluetooth",
    "crc32", "crc32c", "aesni", "crypto_", "cryptd", "sha", "ghash", "gcm",
    "vfio", "irqbypass", "cls_", "sch_", "bfq", "mq_deadline", "inet_diag",
    "unix_diag", "packet_diag", "tcp_diag", "netlink_diag", "sctp", "dccp",
    "pci_", "i2c_", "drm", "i915", "amdgpu", "nouveau", "soundcore", "usb_",
    "hid", "input_", "evdev", "joydev", "serio", "tpm", "watchdog", "gve",
    "virtio", "hv_", "xen", "acpi", "button", "battery", "thermal", "coretemp",
)


def _ld_preload() -> Dict[str, Any]:
    content = read_file("/etc/ld.so.preload")
    entries: List[str] = []
    if content:
        for line in content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append(stripped)
    # Также переменная окружения в текущей сессии.
    env = os.environ.get("LD_PRELOAD", "")
    return {"file_entries": entries, "env": env}


def _loaded_modules() -> List[str]:
    modules: List[str] = []
    for line in read_lines("/proc/modules"):
        parts = line.split()
        if parts:
            modules.append(parts[0])
    return modules


def _hidden_pids() -> List[int]:
    """PID, которые есть в /proc, но не видны в выводе ps (признак руткита)."""
    in_proc: Set[int] = set()
    try:
        for name in os.listdir("/proc"):
            if name.isdigit():
                in_proc.add(int(name))
    except OSError:
        return []

    ps_out = run_cmd(["ps", "-eo", "pid", "--no-headers"])
    if not ps_out:
        return []
    in_ps: Set[int] = set()
    for line in ps_out.splitlines():
        line = line.strip()
        if line.isdigit():
            in_ps.add(int(line))

    # Процессы, видимые в /proc, но отсутствующие в ps.
    return sorted(in_proc - in_ps)


def _deleted_exe_processes() -> List[Dict[str, str]]:
    found: List[Dict[str, str]] = []
    try:
        pids = [int(n) for n in os.listdir("/proc") if n.isdigit()]
    except OSError:
        return found
    for pid in pids:
        try:
            exe = os.readlink(f"/proc/{pid}/exe")
        except OSError:
            continue
        if "(deleted)" in exe:
            comm = read_file(f"/proc/{pid}/comm") or "?"
            found.append({"pid": str(pid), "exe": exe, "comm": comm.strip()})
    return found


def _suspicious_module(mod: str) -> bool:
    if mod.startswith(COMMON_MODULE_PREFIXES):
        return False
    # Необычные имена (случайные строки) — потенциальный руткит.
    if re.fullmatch(r"[a-z0-9_]{3,}", mod):
        return True
    return False


def run(**_: Any) -> CheckResult:
    result = CheckResult(name="rootkit")

    preload = _ld_preload()
    if preload["file_entries"]:
        result.critical(
            "Найден /etc/ld.so.preload",
            "Записи: " + ", ".join(preload["file_entries"]),
            recommendation=(
                "LD_PRELOAD перехватывает системные вызовы — классический руткит. "
                "Проверьте каждую библиотеку; при отсутствии ваших записей удалите файл."
            ),
            entries=preload["file_entries"],
        )
    else:
        result.info("/etc/ld.so.preload", "отсутствует или пуст")

    if preload["env"]:
        result.high(
            "LD_PRELOAD установлен в окружении",
            preload["env"],
            recommendation="Проверьте, кто установил переменную; это может быть перехват вызовов.",
        )

    modules = _loaded_modules()
    result.meta["modules_count"] = len(modules)
    suspicious = [m for m in modules if _suspicious_module(m)]
    if suspicious:
        result.medium(
            "Необычные загруженные модули ядра",
            ", ".join(suspicious),
            recommendation="Проверьте происхождение модулей: modinfo <mod>, lsmod. Незнакомые — выгрузите.",
            modules=suspicious,
        )
    result.info("Загруженные модули", f"{len(modules)} шт.")

    hidden = _hidden_pids()
    if hidden:
        result.critical(
            "Процессы, скрытые от ps",
            f"PID видны в /proc, но отсутствуют в ps: {', '.join(map(str, hidden[:20]))}",
            recommendation="Сильный признак руткита. Проверьте ls -l /proc/PID/exe и сверьте с эталоном.",
            pids=hidden,
        )
    else:
        result.info("Скрытые процессы", "не обнаружены")

    deleted = _deleted_exe_processes()
    if deleted:
        result.high(
            "Процессы с удалёнными бинарниками",
            "\n".join(f"pid {d['pid']} ({d['comm']}): {d['exe']}" for d in deleted[:10]),
            recommendation="Процесс работает из удалённого файла — типично для вредоноса. Соберите /proc/PID/exe.",
            processes=deleted,
        )

    # Проверка подмены известных утилит (по размеру/владельцу).
    tampered = _check_coreutils()
    if tampered:
        result.high(
            "Возможная подмена системных утилит",
            "\n".join(tampered[:10]),
            recommendation="Сверьте пакетные хеши: dpkg -V coreutils. При расхождении — переустановите пакет.",
            entries=tampered,
        )

    result.summary = (
        f"preload: {'да' if preload['file_entries'] else 'нет'}, "
        f"модулей {len(modules)}, скрытых PID {len(hidden)}, удалённых бинарников {len(deleted)}"
    )
    return result


def _check_coreutils() -> List[str]:
    """Ищем изменённые системные утилиты по данным пакетного менеджера (dpkg -V).

    Игнорируем отсутствующие файлы документации/локалей — это норма для
    минимальных образов и не является признаком подмены бинарников.
    """
    issues: List[str] = []
    out = run_cmd(["dpkg", "-V", "coreutils"], timeout=30)
    if not out:
        return issues
    for line in out.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Формат: "??5??????  /path" или "missing     /path"
        path = stripped.split()[-1]
        if stripped.startswith("missing"):
            if path.startswith((
                "/usr/share/doc/", "/usr/share/man/", "/usr/share/locale/",
                "/usr/share/info/", "/usr/share/lintian/",
            )):
                continue
        if stripped.startswith("??") or stripped.startswith("missing"):
            issues.append(stripped)
    return issues
