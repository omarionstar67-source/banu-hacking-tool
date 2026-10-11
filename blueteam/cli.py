"""CLI blue-team модуля.

Использование:
    python3 -m blueteam <check> [опции]
    python3 -m blueteam report [--format markdown|json] [--output FILE]
    python3 -m blueteam list
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List

from . import __version__
from .core import CheckResult, CheckStatus, Severity
from .modules import ALL_CHECKS, DESCRIPTIONS, REGISTRY
from .report import build_report

SEV_COLOR = {
    Severity.CRITICAL: "\033[1;31m",
    Severity.HIGH: "\033[31m",
    Severity.MEDIUM: "\033[33m",
    Severity.LOW: "\033[36m",
    Severity.INFO: "\033[90m",
}
RESET = "\033[0m"


def _print_result(result: CheckResult, verbose: bool = False) -> None:
    color = SEV_COLOR[result.highest_severity]
    print(f"\n{color}=== {result.name} [{result.status.value}] ==={RESET}")
    if result.summary:
        print(f"  {result.summary}")
    if result.error:
        print(f"  ! {result.error}")
    for f in sorted(result.findings, key=lambda x: x.severity, reverse=True):
        if not verbose and f.severity == Severity.INFO:
            continue
        c = SEV_COLOR[f.severity]
        print(f"  {c}[{f.severity.label}]{RESET} {f.title}")
        if f.details and (verbose or f.severity >= Severity.MEDIUM):
            for line in f.details.splitlines()[:8]:
                print(f"        {line}")
        if f.recommendation and (verbose or f.severity >= Severity.MEDIUM):
            print(f"        → {f.recommendation}")


def _dispatch(name: str, args: argparse.Namespace) -> CheckResult:
    func = REGISTRY[name]
    kwargs: Dict[str, Any] = {}
    if name == "processes":
        kwargs["min_score"] = args.min_score
    if name == "logs":
        kwargs["path"] = args.log_path
        kwargs["since"] = args.since
    if name == "integrity":
        kwargs["init"] = args.init
    if name == "suid":
        kwargs["roots"] = args.roots.split(",") if args.roots else None
    return func(**kwargs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blueteam",
        description="BANU Blue Team — защитный аудит собственного хоста (только чтение).",
    )
    parser.add_argument("--version", action="version", version=f"banu-blueteam {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="показывать все находки и детали")

    sub = parser.add_subparsers(dest="command")

    for name in ALL_CHECKS:
        sp = sub.add_parser(name, help=DESCRIPTIONS[name])
        sp.add_argument("-v", "--verbose", action="store_true")
        if name == "processes":
            sp.add_argument("--min-score", type=int, default=25, help="порог риск-скора (по умолчанию 25)")
        if name == "logs":
            sp.add_argument("--log-path", default=None, help="конкретный файл журнала")
            sp.add_argument("--since", default=None, help="напр. '2 hours ago'")
        if name == "integrity":
            sp.add_argument("--init", action="store_true", help="создать baseline")
        if name == "suid":
            sp.add_argument("--roots", default=None, help="каталоги через запятую")

    rp = sub.add_parser("report", help="полный отчёт по всем проверкам")
    rp.add_argument("--format", choices=["markdown", "json"], default="markdown")
    rp.add_argument("--output", default=None, help="файл для записи (иначе stdout)")
    rp.add_argument("-v", "--verbose", action="store_true")

    sub.add_parser("list", help="список доступных проверок")
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "list":
        print("Доступные проверки:")
        for name in ALL_CHECKS:
            print(f"  {name:14s} {DESCRIPTIONS[name]}")
        print("\n  report         полный отчёт (markdown/json)")
        return 0

    if args.command == "report":
        results = []
        for name in ALL_CHECKS:
            try:
                results.append(REGISTRY[name]())
            except Exception as exc:  # noqa: BLE001 — изолируем падение одной проверки
                failed = CheckResult(name=name, status=CheckStatus.ERROR, error=str(exc))
                results.append(failed)
        content = build_report(results, args.format)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(f"[+] Отчёт записан: {args.output}")
            totals = {s.label: 0 for s in Severity}
            for r in results:
                for label, count in r.counts.items():
                    totals[label] += count
            print(f"    CRITICAL={totals['CRITICAL']} HIGH={totals['HIGH']} "
                  f"MEDIUM={totals['MEDIUM']} LOW={totals['LOW']}")
        else:
            print(content)
        return 0

    if args.command in REGISTRY:
        result = _dispatch(args.command, args)
        _print_result(result, verbose=getattr(args, "verbose", False))
        # Ненулевой код возврата при критичных находках — удобно для CI.
        if result.highest_severity >= Severity.CRITICAL:
            return 2
        if result.highest_severity >= Severity.HIGH:
            return 1
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
