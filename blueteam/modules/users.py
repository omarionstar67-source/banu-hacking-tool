"""Аудит учётных записей: UID 0, пустые пароли, sudoers, оболочки, логины."""

from __future__ import annotations

import os
from typing import Any, Dict, List

from ..core import CheckResult, read_file, read_lines
from ..core import run as run_cmd

# Оболочки, которые считаются «нелогин» и не являются интерактивными.
NOLOGIN_SHELLS = {
    "/usr/sbin/nologin",
    "/sbin/nologin",
    "/bin/false",
    "/usr/bin/false",
    "/bin/sync",
    "/dev/null",
    "",
}


def _to_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return -1


def _parse_passwd() -> List[Dict[str, Any]]:
    users = []
    for line in read_lines("/etc/passwd"):
        parts = line.split(":")
        if len(parts) < 7:
            continue
        users.append(
            {
                "name": parts[0],
                "uid": _to_int(parts[2]),
                "gid": _to_int(parts[3]),
                "gecos": parts[4],
                "home": parts[5],
                "shell": parts[6],
            }
        )
    return users


def _parse_shadow() -> Dict[str, Dict[str, str]]:
    content = read_file("/etc/shadow")
    if content is None:
        return {}
    result: Dict[str, Dict[str, str]] = {}
    for line in content.splitlines():
        parts = line.split(":")
        if len(parts) < 9:
            continue
        result[parts[0]] = {
            "hash": parts[1],
            "last_change": parts[2],
            "min": parts[3],
            "max": parts[4],
            "warn": parts[5],
            "inactive": parts[6],
            "expire": parts[7],
        }
    return result


def _parse_sudoers() -> List[str]:
    entries: List[str] = []
    for line in read_lines("/etc/sudoers"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.append(stripped)
    try:
        for name in sorted(os.listdir("/etc/sudoers.d")):
            full = os.path.join("/etc/sudoers.d", name)
            for line in read_lines(full):
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    entries.append(f"{name}: {stripped}")
    except OSError:
        pass
    return entries


def _last_logins(limit: int = 15) -> List[str]:
    out = run_cmd(["last", "-n", str(limit), "-i"])
    if out:
        return [l for l in out.splitlines() if l.strip()][:limit]
    return []


def _sudo_group_members() -> List[str]:
    members: List[str] = []
    for line in read_lines("/etc/group"):
        parts = line.split(":")
        if len(parts) >= 4 and parts[0] in {"sudo", "wheel", "admin"} and parts[3].strip():
            members.extend(m.strip() for m in parts[3].split(",") if m.strip())
    return sorted(set(members))


def run(**_: Any) -> CheckResult:
    result = CheckResult(name="users")
    users = _parse_passwd()
    shadow = _parse_shadow()

    if not users:
        result.status = result.status.ERROR
        result.error = "не удалось прочитать /etc/passwd"
        return result

    roots = [u for u in users if u["uid"] == 0]
    result.info(
        "Учётные записи",
        f"всего {len(users)}, с UID 0: {len(roots)}",
        total=len(users),
    )

    # 1. Несколько UID 0 — классический признак бэкдор-пользователя.
    if len(roots) > 1:
        names = ", ".join(u["name"] for u in roots)
        result.critical(
            "Несколько учётных записей с UID 0",
            f"UID 0 имеют: {names}",
            recommendation="Оставьте только root. Остальные — вероятный бэкдор; удалите и проверьте доступы.",
            accounts=[u["name"] for u in roots],
        )
    else:
        result.info("UID 0", "только root — норма")

    root_shells = [u["name"] for u in users if u["uid"] == 0 and u["shell"] not in NOLOGIN_SHELLS]
    result.info("UID 0 с интерактивной оболочкой", ", ".join(root_shells) or "нет")

    # 2. Пустые пароли (только если удалось прочитать shadow).
    if not shadow:
        result.low(
            "Нет доступа к /etc/shadow",
            "Проверка пустых паролей пропущена.",
            recommendation="Запустите под root для полной проверки.",
        )
        result.meta["shadow_readable"] = False
    else:
        result.meta["shadow_readable"] = True
        truly_empty = [name for name, data in shadow.items() if data["hash"] == ""]
        if truly_empty:
            result.critical(
                "Учётные записи с пустым паролем",
                ", ".join(truly_empty),
                recommendation="Немедленно задайте пароли или заблокируйте (passwd -l) эти учётные записи.",
                accounts=truly_empty,
            )
        locked = [name for name, data in shadow.items() if data["hash"].startswith("!")]
        result.info("Заблокированные учётные записи", f"{len(locked)} шт.")

        no_expiry = [
            name for name, data in shadow.items()
            if data["hash"] and not data["hash"].startswith("!")
            and data["max"] in ("", "0", "99999")
        ]
        if no_expiry:
            result.low(
                "Пароли без срока действия",
                ", ".join(no_expiry[:20]) + (" …" if len(no_expiry) > 20 else ""),
                recommendation="Установите срок действия паролей в /etc/login.defs (PASS_MAX_DAYS).",
                count=len(no_expiry),
            )

    # 3. Члены групп sudo/wheel.
    admins = _sudo_group_members()
    if admins:
        result.medium(
            "Пользователи с полными правами sudo",
            ", ".join(admins),
            recommendation="Регулярно ревизуйте состав sudo-группы: это полный root.",
            accounts=admins,
        )

    sudoers = _parse_sudoers()
    risky = [e for e in sudoers if "NOPASSWD" in e]
    if risky:
        result.high(
            "Правила sudo с NOPASSWD",
            "; ".join(risky[:10]),
            recommendation="NOPASSWD позволяет повышение прав без пароля — уберите, если не требуется.",
            rules=risky,
        )
    result.meta["sudoers_entries"] = len(sudoers)

    # 4. Домашние каталоги, которых нет.
    missing_home = [
        u["name"] for u in users
        if u["uid"] >= 1000 and u["shell"] not in NOLOGIN_SHELLS
        and u["home"] and not os.path.isdir(u["home"])
    ]
    if missing_home:
        result.low(
            "Учётные записи без домашнего каталога",
            ", ".join(missing_home),
            recommendation="Проверьте, не удалён ли каталог злоумышленником, либо исправьте /etc/passwd.",
        )

    # 5. Последние входы.
    logins = _last_logins()
    if logins:
        result.info("Последние входы (last)", "\n".join(logins[:10]), logins=logins)

    # 6. Права на чувствительные файлы.
    for sensitive in ("/etc/passwd", "/etc/shadow", "/etc/sudoers"):
        try:
            st = os.stat(sensitive)
        except OSError:
            continue
        if st.st_mode & 0o022:
            result.high(
                f"{sensitive} доступен для записи группе/всем",
                f"права: {oct(st.st_mode & 0o777)}",
                recommendation="Верните права: chmod 644 /etc/passwd, 640 /etc/shadow, 440 /etc/sudoers.",
            )

    result.summary = f"{len(users)} учётных записей, {len(roots)} с UID 0, sudo-админов {len(admins)}"
    return result

