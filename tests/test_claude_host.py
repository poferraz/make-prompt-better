"""Opt-in, offline Claude Code plugin lifecycle and component discovery check.

Set MPB_TEST_CLAUDE_BIN to an installed Claude Code executable. No model request
or personal Claude configuration is used; the marketplace source is local.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = "make-prompt-better@make-prompt-better-marketplace"


@unittest.skipUnless(os.environ.get("MPB_TEST_CLAUDE_BIN"), "set MPB_TEST_CLAUDE_BIN to opt into Claude Code host verification")
class ClaudePluginHostTests(unittest.TestCase):
    def test_local_marketplace_install_discover_update_and_uninstall(self):
        binary = Path(os.environ["MPB_TEST_CLAUDE_BIN"]).resolve()
        self.assertTrue(binary.is_file() and os.access(binary, os.X_OK), f"Claude CLI is not executable: {binary}")
        with tempfile.TemporaryDirectory(prefix="mpb-claude-host-") as tmp:
            root = Path(tmp)
            home = root / "home"
            project = root / "project"
            home.mkdir()
            project.mkdir()
            env = {
                "PATH": os.environ["PATH"],
                "HOME": str(home),
                "CLAUDE_CONFIG_DIR": str(home / ".claude"),
                "DISABLE_TELEMETRY": "1",
                "DISABLE_AUTOUPDATER": "1",
                "NO_COLOR": "1",
            }

            def claude(*args):
                result = subprocess.run([str(binary), *args], cwd=project, env=env,
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, f"{args}: {result.stdout}\n{result.stderr}")
                return result.stdout

            version = claude("--version")
            self.assertIn("Claude Code", version)
            validation = claude("plugin", "validate", str(ROOT))
            self.assertIn("Validation passed", validation)
            claude("plugin", "marketplace", "add", str(ROOT))
            installed = json.loads(claude("plugin", "install", PLUGIN, "--scope", "user", "--json"))
            self.assertEqual(installed["outcome"], "ok")
            entries = json.loads(claude("plugin", "list", "--json"))
            self.assertEqual([entry["id"] for entry in entries], [PLUGIN])
            self.assertTrue(entries[0]["enabled"])
            installed_root = Path(entries[0]["installPath"]).resolve()
            self.assertTrue(installed_root.is_relative_to(home.resolve()))
            for relative in ("SKILL.md", "references/domain-templates.md",
                             "references/research-principles.md", "references/examples.md"):
                with self.subTest(file=relative):
                    installed_file = installed_root / "make-prompt-better" / relative
                    self.assertTrue(installed_file.is_file(), str(installed_file))
                    self.assertEqual(installed_file.read_bytes(), (ROOT / "make-prompt-better" / relative).read_bytes())
            details = claude("plugin", "details", PLUGIN)
            self.assertRegex(details, r"Skills \(1\)\s+make-prompt-better")
            update = json.loads(claude("plugin", "update", PLUGIN, "--scope", "user", "--json"))
            self.assertEqual(update["outcome"], "ok")
            claude("plugin", "uninstall", PLUGIN, "--scope", "user")
            self.assertEqual(json.loads(claude("plugin", "list", "--json")), [])


if __name__ == "__main__":
    unittest.main()
