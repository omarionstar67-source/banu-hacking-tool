"""Сборка отчёта: markdown и json."""

from __future__ import annotations

import json
import platform
import socket
import time
from typing import Any, Dict, List

from .core import CheckResult, Severity

SEVERITY_ICON = {
    Severity.CRITICAL: "🔴 CRITICAL",
    Severity.HIGH: "🟠 HIGH",
    Severity.MEDIUM: "🟡 MEDIUM",
    Severity.LOW: "🔵 LOW",
    Severity.INFO: "⚪ INFO",
}


def build_report(results: List[CheckResult], fmt: str = "markdown") -> str:
    if fmt == "json":
        return json.dumps(_as_dict(results), indent=2, ensure_ascii=False)
    return _as_markdown(results)


def _as_dict(results: List[CheckResult]) -> Dict[str, Any]:
    totals = {s.label: 0 for s in Severity}
    for r in results:
        for label, count in r.counts.items():
            totals[label] += count
    return {
        "tool": "banu-blueteam",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "totals": totals,
        "checks": [r.to_dict() for r in results],
    }


def _as_markdown(results: List[CheckResult]) -> str:
    lines: List[str] = []
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    totals = {s.label: 0 for s in Severity}
    for r in results:
        for label, count in r.counts.items():
            totals[label] += count

    lines.append("# BANU Blue Team — отчёт об аудите хоста")
    lines.append("")
    lines.append(f"- **Хост:** `{socket.gethostname()}`")
    lines.append(f"- **Платформа:** {platform.platform()}")
    lines.append(f"- **Время:** {now}")
    lines.append("")
    lines.append("## Сводка")
    lines.append("")
    lines.append("| Серьёзность | Находок |")
    lines.append("|---|---|")
    for sev in reversed(list(Severity)):
        lines.append(f"| {SEVERITY_ICON[sev]} | {totals[sev.label]} |")
    lines.append("")

    lines.append("## Проверки")
    lines.append("")
    lines.append("| Проверка | Статус | Находок | Макс. серьёзность |")
    lines.append("|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r.name} | {r.status.value} | {len(r.findings)} | "
            f"{r.highest_severity.label} |"
        )
    lines.append("")

    for r in results:
        lines.append(f"## {r.name}")
        lines.append("")
        if r.summary:
            lines.append(f"_{r.summary}_")
            lines.append("")
        if r.error:
            lines.append(f"> ⚠️ Ошибка: {r.error}")
            lines.append("")
        if not r.findings:
            lines.append("Находок нет.")
            lines.append("")
            continue
        ordered = sorted(r.findings, key=lambda f: f.severity, reverse=True)
        for f in ordered:
            lines.append(f"### {SEVERITY_ICON[f.severity]} — {f.title}")
            lines.append("")
            if f.details:
                lines.append("```")
                lines.append(f.details)
                lines.append("```")
                lines.append("")
            if f.recommendation:
                lines.append(f"**Рекомендация:** {f.recommendation}")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Отчёт сформирован модулем BANU Blue Team. Только локальный аудит, без сетевых атак._")
    return "\n".join(lines)
