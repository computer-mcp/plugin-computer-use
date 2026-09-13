import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("build_package", ROOT / "Scripts/build_package.py")
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class PackageTests(unittest.TestCase):
    def test_reproducible_owned_contents(self):
        first, manifest = BUILDER.package_bytes(ROOT)
        second, _ = BUILDER.package_bytes(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(manifest["id"], "computer-use")
        with zipfile.ZipFile(io.BytesIO(first)) as archive:
            self.assertEqual(set(archive.namelist()), {
                "README.md", "computer-mcp-plugin.toml",
                "LICENSE", "THIRD_PARTY_NOTICES.md", "ThirdPartyNotices.txt",
                "CONTRIBUTING.md", "Documentation/README.md",
                "Documentation/Architecture/README.md",
                "Documentation/Architecture/Package.md",
                "Documentation/Architecture/Documentation.md",
                "skills/observe-act-verify/SKILL.md",
                "skills/observe-act-verify/agents/openai.yaml",
            })
            for name in ("LICENSE", "THIRD_PARTY_NOTICES.md", "ThirdPartyNotices.txt"):
                self.assertEqual(archive.read(name), (ROOT / name).read_bytes())
            for item in archive.infolist():
                self.assertEqual(item.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual((item.external_attr >> 16) & 0o777, 0o644)

    def test_rejects_links_oversize_and_special_files(self):
        for kind in ("file-link", "root-link", "documentation-link", "oversize", "fifo"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "source"
                root.mkdir()
                for name in ("README.md", "CONTRIBUTING.md", "computer-mcp-plugin.toml",
                             "LICENSE", "THIRD_PARTY_NOTICES.md", "ThirdPartyNotices.txt"):
                    shutil.copyfile(ROOT / name, root / name)
                shutil.copytree(ROOT / "skills", root / "skills")
                shutil.copytree(ROOT / "Documentation", root / "Documentation")
                target = root / "skills" / "unsafe"
                if kind == "file-link":
                    target.symlink_to(root / "README.md")
                elif kind == "root-link":
                    (root / "skills").rename(root / "guidance")
                    (root / "skills").symlink_to(root / "guidance", target_is_directory=True)
                elif kind == "documentation-link":
                    (root / "Documentation" / "unsafe").symlink_to(root / "README.md")
                elif kind == "oversize":
                    target.write_bytes(b"x" * 1_048_577)
                else:
                    import os
                    os.mkfifo(target)
                with self.assertRaises(ValueError):
                    BUILDER.package_bytes(root)

    def test_requires_license_and_notices(self):
        for name in ("LICENSE", "THIRD_PARTY_NOTICES.md", "ThirdPartyNotices.txt"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "source"
                shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
                (root / name).unlink()
                with self.assertRaises(FileNotFoundError):
                    BUILDER.package_bytes(root)

    def test_command_is_idempotent_but_never_overwrites_different_output(self):
        with tempfile.TemporaryDirectory() as temp:
            command = [sys.executable, str(ROOT / "Scripts/build_package.py"), temp]
            first = subprocess.run(command, capture_output=True, timeout=10)
            second = subprocess.run(command, capture_output=True, timeout=10)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout, second.stdout)
            artifact = Path(temp) / "computer-use.zip"
            artifact.write_bytes(b"keep")
            failed = subprocess.run(command, capture_output=True, timeout=10)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(artifact.read_bytes(), b"keep")


if __name__ == "__main__":
    unittest.main()
