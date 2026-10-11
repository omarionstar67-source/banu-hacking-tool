"""Аудит сети: слушающие порты, соединения, необычные состояния.

Только локальное чтение (ss / /proc/net). Никакого сканирования внешних хостов.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..core import CheckResult
from ..core import run as run_cmd

# Порты, которые чаще всего указывают на отладку/бэкдор, если открыты наружу.
RISKY_PORTS = {
    21: "FTP (открытый текст)",
    23: "Telnet (открытый текст)",
    25: "SMTP",
    111: "rpcbind",
    135: "MS RPC",
    139: "NetBIOS",
    445: "SMB",
    512: "rexec",
    513: "rlogin",
    514: "rsh",
    1433: "MSSQL",
    1521: "Oracle",
    2049: "NFS",
    2375: "Docker API (без TLS)",
    3306: "MySQL",
    3389: "RDP",
    4444: "Metasploit / reverse shell по умолчанию",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    9200: "Elasticsearch",
    11211: "Memcached",
    27017: "MongoDB",
    31337: "Back Orifice / исторический бэкдор",
    12345: "NetBus / частый бэкдор",
}


def _parse_ss() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    text = run_cmd(["ss", "-H", "-tulpn"])
    if not text:
        return rows
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        local = parts[4]
        peer = parts[5] if len(parts) > 5 else ""
        proc = parts[6] if len(parts) > 6 else ""
        rows.append(
            {
                "proto": parts[0],
                "state": parts[1],
                "local": local,
                "peer": peer,
                "process": proc,
                "port": _port(local),
                "external": not local.startswith(("127.", "::1", "[::1]", "*:*")),
            }
        )
    return rows


def _port(addr: str) -> int:
    try:
        return int(addr.rsplit(":", 1)[1])
    except (ValueError, IndexError):
        return -1


def _established() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    text = run_cmd(["ss", "-H", "-tnp", "state", "established"])
    if not text:
        return rows
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        rows.append(
            {
                "local": parts[3],
                "peer": parts[4],
                "process": parts[5] if len(parts) > 5 else "",
            }
        )
    return rows


def run(**_: Any) -> CheckResult:
    result = CheckResult(name="network")

    listeners = [r for r in _parse_ss() if r["state"] in ("LISTEN", "UNCONN")]
    if not listeners:
        result.status = result.status.SKIPPED
        result.error = "ss недоступен или нет данных"
        result.low(
            "Не удалось получить список сокетов",
            "Утилита ss недоступна или не вернула данные.",
            recommendation="Установите iproute2 либо запустите с правами, позволяющими читать сокеты.",
        )
        return result

    external = [r for r in listeners if r["external"]]
    result.meta["listeners"] = len(listeners)
    result.meta["external_listeners"] = len(external)
    result.info(
        "Слушающие сокеты",
        f"{len(listeners)} всего, {len(external)} доступны извне",
        listeners=listeners,
    )

    # 1. Опасные порты, открытые наружу.
    for row in external:
        if row["port"] in RISKY_PORTS:
            result.high(
                f"Наружу открыт потенциально опасный порт {row['port']}",
                f"{row['proto']} {row['local']} — {RISKY_PORTS[row['port']]}",
                recommendation=(
                    "Закройте порт файрволом или привяжите сервис к localhost, "
                    "если внешний доступ не требуется."
                ),
                port=row["port"],
                process=row["process"],
            )

    # 2. Слушатель на всех интерфейсах (0.0.0.0 / ::).
    wildcard = [r for r in external if r["local"].startswith(("0.0.0.0", "[::]", "*"))]
    if wildcard:
        result.medium(
            "Сервисы слушают на всех интерфейсах",
            ", ".join(sorted({f"{r['proto']}:{r['local']}" for r in wildcard})),
            recommendation="Привязывайте сервисы к конкретному адресу, если это возможно.",
            count=len(wildcard),
        )

    # 3. Установленные соединения — обратим внимание на нестандартные порты.
    conns = _established()
    result.meta["established"] = len(conns)
    odd = [
        c for c in conns
        if _port(c["peer"]) not in (80, 443, 53, 22, 25, 587, 993, 995, 123)
        and _port(c["peer"]) > 0
    ]
    if conns:
        result.info(
            "Установленные соединения",
            f"{len(conns)} активных, {len(odd)} на нестандартные порты",
            connections=conns[:200],
        )

    # 4. Проверка, включён ли файрвол.
    fw = _firewall_state()
    result.meta["firewall"] = fw
    if fw == "absent":
        result.high(
            "Не обнаружен активный файрвол",
            "nft/iptables/ufw/firewalld не найдены или неактивны.",
            recommendation="Включите файрвол: ufw enable / nftables / firewalld, и закройте лишние порты.",
        )
    elif fw:
        result.info("Файрвол", fw)

    result.summary = (
        f"{len(listeners)} слушателей ({len(external)} внешних), {len(conns)} соединений"
    )
    return result


def _firewall_state() -> str:
    if run_cmd(["nft", "list", "ruleset"]):
        return "nftables активен"
    ipt = run_cmd(["iptables", "-S"])
    if ipt and len(ipt.splitlines()) > 3:
        return "iptables с правилами"
    if run_cmd(["ufw", "status"]) and "Status: active" in (run_cmd(["ufw", "status"]) or ""):
        return "ufw активен"
    if run_cmd(["firewall-cmd", "--state"]) and "running" in (run_cmd(["firewall-cmd", "--state"]) or ""):
        return "firewalld активен"
    return "absent"
