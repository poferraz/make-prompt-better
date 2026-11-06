"""Opt-in Codex host discovery test; no model requests or real-home writes."""
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get("MPB_TEST_CODEX_HOST") == "1" and shutil.which("codex"),
                     "Set MPB_TEST_CODEX_HOST=1 with Codex CLI installed")
class CodexHostTests(unittest.TestCase):
    def test_project_and_global_install_update_uninstall_and_recovery(self):
        for scope in ("project", "global"):
            with self.subTest(scope=scope), tempfile.TemporaryDirectory(prefix="mpb codex host ") as tmp:
                base = Path(tmp)
                home, project = base / "home", base / "project"
                (home / ".codex").mkdir(parents=True)
                project.mkdir()
                env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / ".codex"))
                target_root = project if scope == "project" else home
                skill = target_root / ".agents/skills/make-prompt-better/SKILL.md"

                def command(action):
                    return subprocess.run(["node", str(ROOT / "bin/cli.mjs"), action,
                                           "--runtime", "codex", "--" + scope],
                                          cwd=project, env=env, text=True,
                                          capture_output=True, timeout=30)

                def discover():
                    process = subprocess.Popen(["codex", "app-server"], cwd=project, env=env,
                                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                               stderr=subprocess.DEVNULL, text=True, bufsize=1)
                    lines = queue.Queue()
                    reader = threading.Thread(target=lambda: [lines.put(line) for line in process.stdout],
                                              daemon=True)
                    reader.start()

                    def send(item):
                        process.stdin.write(json.dumps(item) + "\n")
                        process.stdin.flush()

                    def response(request_id):
                        while True:
                            item = json.loads(lines.get(timeout=20))
                            if item.get("id") == request_id:
                                self.assertNotIn("error", item)
                                return item["result"]

                    try:
                        send({"id": 1, "method": "initialize", "params": {"clientInfo": {
                            "name": "mpb_host_test", "version": "1"}}})
                        response(1)
                        send({"method": "initialized", "params": {}})
                        send({"id": 2, "method": "skills/list", "params": {
                            "cwds": [str(project)], "forceReload": True}})
                        data = response(2)["data"][0]
                        self.assertEqual(data.get("errors", []), [])
                        return [entry for entry in data["skills"] if entry["name"] == "make-prompt-better"]
                    finally:
                        process.terminate()
                        process.wait(timeout=10)
                        process.stdin.close()
                        process.stdout.close()
                        reader.join(timeout=5)

                self.assertEqual(discover(), [])
                self.assertEqual(command("install").returncode, 0)
                matches = discover()
                self.assertEqual(len(matches), 1)
                self.assertTrue(matches[0]["enabled"])
                self.assertEqual(Path(matches[0]["path"]).resolve(), skill.resolve())
                self.assertEqual(matches[0]["scope"], "repo" if scope == "project" else "user")
                for name in ("domain-templates.md", "examples.md", "research-principles.md"):
                    self.assertTrue((skill.parent / "references" / name).is_file())
                skill.write_text(skill.read_text() + "\nlocal edit\n")
                self.assertNotEqual(command("check").returncode, 0)
                self.assertEqual(command("update").returncode, 0)
                backups = list((target_root / ".make-prompt-better/backups").glob("*/payload/SKILL.md"))
                edited = next(path for path in backups if "local edit" in path.read_text())
                self.assertEqual(len(discover()), 1)
                self.assertEqual(command("uninstall").returncode, 0)
                self.assertEqual(discover(), [])
                shutil.move(str(edited.parent), str(skill.parent))
                self.assertEqual(len(discover()), 1)
                self.assertNotEqual(command("check").returncode, 0)
                self.assertEqual(command("update").returncode, 0)
                self.assertEqual(command("check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
