"""Check portable authority declarations without building an archive or starting a peer."""
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SourceDeclarationTests(unittest.TestCase):
    def test_requests_are_reviewable_and_have_no_grants_or_native_catalog(self):
        manifest = tomllib.loads((ROOT / "computer-mcp-plugin.toml").read_text())
        self.assertEqual(manifest["plugin_api"], 1)
        self.assertEqual({entry["id"] for entry in manifest["permissions"]},
                         {"screen", "desktop-control"})
        self.assertEqual(len(manifest["permissions"]), 2)
        for entry in manifest["permissions"]:
            self.assertEqual(set(entry), {"id", "access", "purpose"})
            self.assertEqual(entry["access"], "allow")
            self.assertTrue(entry["purpose"].strip())
        self.assertNotIn("sandbox", manifest)
        self.assertEqual(manifest["mcp"], [{
            "id": "native", "transport": "stdio",
            "executable": {"dependency": "computer-use-client"}, "args": ["mcp"],
            "prefix": "computer-use", "capabilities": ["tools"],
        }])
        self.assertEqual(manifest["skills"], [{"id": "guidance", "path": "skills"}])
        self.assertEqual(manifest["dependencies"][0]["commands"], ["SkyComputerUseClient"])

    def test_fixtures_stay_outside_the_declarative_archive_inputs(self):
        # Builder traverses docs/ and skills/; tests and scripts remain source helpers.
        builder = (ROOT / "scripts/build_package.py").read_text()
        self.assertIn('pending = [root / "skills", root / "docs"]', builder)
        for directory in (ROOT / "skills", ROOT / "docs"):
            self.assertFalse(any(path.name.endswith((".swift.txt", ".c", ".py"))
                                 for path in directory.rglob("*")))
        self.assertNotIn("fixture_", (ROOT / "computer-mcp-plugin.toml").read_text())


if __name__ == "__main__":
    unittest.main()
