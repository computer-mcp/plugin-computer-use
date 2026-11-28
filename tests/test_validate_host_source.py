"""Driver checks use disposable files and mock Swift; no build or native CUA runs."""
import argparse
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_host_source", ROOT / "scripts/validate_host_source.py")
DRIVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRIVER)


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="cua-driver-", dir=os.environ.get("COMPUTER_MCP_CUA_TEST_OUTPUT"))
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.host = self.root / "host"
        self.plugin = self.root / "plugin"
        self.output = self.root / "output"
        self.host.mkdir()
        self.plugin.mkdir()
        for name in DRIVER.INPUTS:
            path = self.plugin / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
        self.args = argparse.Namespace(host_source=self.host, plugin_source=self.plugin,
                                       host_sha="a" * 40, plugin_sha="b" * 40,
                                       output=self.output, timeout=1)

    def export(self, root, sha, destination, environment, output):
        destination.mkdir()
        if root == self.host:
            (destination / "Tests/ComputerMCPMacOSTests").mkdir(parents=True)
        else:
            for name in DRIVER.INPUTS:
                target = destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((root / name).read_bytes())

    def execute(self, command, cwd, environment, log, timeout):
        self.assertEqual(command[0], "/usr/bin/swift")
        self.assertIn("--scratch-path", command)
        self.assertEqual(command[-1], "ComputerUseSourceIntegrationTests")
        self.assertNotEqual(cwd, self.host)
        self.assertTrue((cwd / "Tests/ComputerMCPMacOSTests" / DRIVER.FIXTURE).is_file())
        Path(environment["COMPUTER_MCP_CUA_CASES"]).write_text(json.dumps({
            "kind": "deterministic", "run_id": environment["COMPUTER_MCP_CUA_RUN_ID"],
            "tests_executed": 1, "cases": sorted(DRIVER.CASES),
        }))
        log.write_text("mock Swift completed\n")

    def run_mocked(self, execute=None):
        with patch.object(DRIVER, "verify_source") as verify, \
                patch.object(DRIVER, "export_source", side_effect=self.export), \
                patch.object(DRIVER, "run_process", side_effect=execute or self.execute):
            DRIVER.run(self.args)
            self.assertEqual(verify.call_count, 4)

    def test_requires_exact_clean_checkout(self):
        values = [str(self.host), "a" * 40, ""]
        with patch.object(DRIVER, "git", side_effect=values):
            DRIVER.verify_source(self.host, "a" * 40)
        for values in ([str(self.host), "b" * 40], [str(self.host), "a" * 40, "?? untracked"]):
            with patch.object(DRIVER, "git", side_effect=values), self.assertRaises(ValueError):
                DRIVER.verify_source(self.host, "a" * 40)
        for value in ("master", "a" * 7, "A" * 40, "0" * 41):
            with self.assertRaises(argparse.ArgumentTypeError):
                DRIVER.revision(value)

    def test_output_and_sources_must_be_disjoint(self):
        for output in (self.host / "ignored", self.plugin / "ignored", self.root):
            with self.assertRaises(ValueError):
                DRIVER.validate_locations(self.host, self.plugin, output)
        with self.assertRaises(ValueError):
            DRIVER.validate_locations(self.host, self.host / "nested", self.output)
        self.output.symlink_to(self.root / "missing")
        with self.assertRaises(ValueError):
            DRIVER.validate_locations(self.host, self.plugin, self.output)

    def test_output_cannot_overlap_case_aliased_checkouts(self):
        if not self.host.with_name("HOST").is_dir():
            self.skipTest("Temporary filesystem is case-sensitive")

        for output in (self.host.with_name("HOST") / "ignored" / "result",
                       self.plugin.with_name("PLUGIN") / "ignored" / "result",
                       self.root.with_name(self.root.name.upper())):
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "outside both"):
                DRIVER.validate_locations(self.host, self.plugin, DRIVER.absolute(output))

    def test_source_checkouts_cannot_be_case_aliases_or_nested(self):
        host_alias = self.host.with_name("HOST")
        if not host_alias.is_dir():
            self.skipTest("Temporary filesystem is case-sensitive")

        (self.host / "nested").mkdir()
        for plugin in (host_alias, host_alias / "nested"):
            with self.subTest(plugin=plugin), self.assertRaisesRegex(ValueError, "separate, non-nested"):
                DRIVER.validate_locations(self.host, DRIVER.absolute(plugin), self.output)

    def test_success_exports_without_editing_inputs_and_removes_owned_trees(self):
        original = {name: (self.plugin / name).read_bytes() for name in DRIVER.INPUTS}
        self.run_mocked()
        receipt = json.loads((self.output / "receipt.json").read_text())
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["cleanup"], "confirmed")
        self.assertFalse(receipt["native_verified"])
        self.assertEqual(set(receipt["cases"]), DRIVER.CASES)
        self.assertEqual(original, {name: (self.plugin / name).read_bytes() for name in DRIVER.INPUTS})
        for name in ("host-source", "plugin-source", "build"):
            self.assertFalse((self.output / name).exists())
        self.assertFalse((self.host / "Tests").exists())

    def test_zero_case_stale_and_duplicate_evidence_cannot_pass(self):
        good = {"kind": "deterministic", "run_id": "this-run", "tests_executed": 1,
                "cases": sorted(DRIVER.CASES)}
        for changes in ({"cases": []}, {"run_id": "old-run"}, {"tests_executed": 0},
                        {"tests_executed": True}, {"cases": sorted(DRIVER.CASES) * 2}):
            with self.assertRaises(ValueError):
                DRIVER.validate_evidence(good | changes, "this-run")

    def test_no_matching_swift_test_cannot_report_success(self):
        def no_test(*arguments):
            pass
        with self.assertRaises(FileNotFoundError):
            self.run_mocked(no_test)
        receipt = json.loads((self.output / "receipt.json").read_text())
        self.assertEqual(receipt["status"], "failed")
        self.assertIn("unverified", receipt["cleanup"])
        self.assertFalse((self.output / "host-source").exists())

    def test_command_failure_retains_logs_and_removes_exports(self):
        def failure(command, cwd, environment, log, timeout):
            log.write_text("failure evidence\n")
            raise RuntimeError("injected failure")
        with self.assertRaisesRegex(RuntimeError, "injected"):
            self.run_mocked(failure)
        self.assertEqual((self.output / "swift-test.log").read_text(), "failure evidence\n")
        self.assertFalse((self.output / "plugin-source").exists())
        self.assertEqual(json.loads((self.output / "receipt.json").read_text())["status"], "failed")

    def test_source_change_during_execution_invalidates_success(self):
        def mutate(*arguments):
            self.execute(*arguments)
            (self.plugin / "computer-mcp-plugin.toml").write_text("changed")
        with self.assertRaisesRegex(ValueError, "changed"):
            self.run_mocked(mutate)
        self.assertEqual(json.loads((self.output / "receipt.json").read_text())["status"], "failed")

    def test_archive_rejects_escape_and_links(self):
        for name, kind in (("../escape", tarfile.REGTYPE), ("link", tarfile.SYMTYPE)):
            archive = self.root / "source.tar"
            with tarfile.open(archive, "w") as output:
                item = tarfile.TarInfo(name)
                item.type = kind
                item.linkname = "/outside"
                output.addfile(item, io.BytesIO())
            with self.assertRaises(ValueError):
                DRIVER.extract_source(archive, self.root / ("unpack-" + str(kind)))
        self.assertFalse((self.root / "escape").exists())

    def test_archive_preserves_executable_mode_and_bytes(self):
        archive = self.root / "source.tar"
        with tarfile.open(archive, "w") as output:
            item = tarfile.TarInfo("bin/peer")
            item.mode, item.size = 0o755, 4
            output.addfile(item, io.BytesIO(b"peer"))
        unpacked = self.root / "unpacked"
        DRIVER.extract_source(archive, unpacked)
        self.assertEqual((unpacked / "bin/peer").read_bytes(), b"peer")
        self.assertEqual((unpacked / "bin/peer").stat().st_mode & 0o777, 0o755)

    def test_bounded_process_execution_and_failure(self):
        log = self.root / "command.log"
        DRIVER.run_process([sys.executable, "-B", "-c", "print('owned child')"], self.root,
                           dict(os.environ), log, 2)
        self.assertIn("owned child", log.read_text())
        with self.assertRaisesRegex(RuntimeError, "exited 3"):
            DRIVER.run_process([sys.executable, "-B", "-c", "raise SystemExit(3)"], self.root,
                               dict(os.environ), log, 2)
        with self.assertRaises(TimeoutError):
            DRIVER.run_process([sys.executable, "-B", "-c", "import time; time.sleep(10)"],
                               self.root, dict(os.environ), log, 0.1)


if __name__ == "__main__":
    unittest.main()
