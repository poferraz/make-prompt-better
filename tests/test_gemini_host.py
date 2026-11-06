"""Opt-in Gemini CLI discovery and installer lifecycle; makes no model requests."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GEMINI = shutil.which("gemini")
ENABLED = os.environ.get("MPB_TEST_GEMINI_HOST") == "1"


@unittest.skipUnless(ENABLED and GEMINI, "Set MPB_TEST_GEMINI_HOST=1 with Gemini CLI on PATH")
class GeminiHostTests(unittest.TestCase):
    def test_offline_activation_tool_lists_reference_resources(self):
        """Exercise Gemini's tool directly; this is not a model-driven invocation."""
        with tempfile.TemporaryDirectory(prefix="mpb-gemini-activation-") as tmp:
            root = Path(tmp).resolve()
            home, project = root / "home", root / "project"
            home.mkdir()
            project.mkdir()
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith(("GEMINI_", "GOOGLE_", "OPENAI_", "ANTHROPIC_"))}
            env.update(HOME=str(home), XDG_CONFIG_HOME=str(root / "config"),
                       XDG_CACHE_HOME=str(root / "cache"), XDG_DATA_HOME=str(root / "data"))
            version = subprocess.run([GEMINI, "--version"], cwd=project, env=env,
                                     capture_output=True, text=True, timeout=30)
            self.assertEqual(version.returncode, 0, version.stdout + version.stderr)
            if version.stdout.strip() != "0.63.0":
                self.skipTest("Direct activation probe is guarded to Gemini CLI 0.63.0")
            module = Path(GEMINI).resolve().parent / "chunk-2V7FO5QV.js"
            self.assertTrue(module.is_file())
            installed = subprocess.run(["bash", str(ROOT / "install.sh"), "--project", "--runtime", "gemini"],
                                       cwd=project, env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            script = r"""
import {pathToFileURL} from 'node:url';
const [modulePath, project] = process.argv.slice(1);
const {SkillManager, Storage, ActivateSkillTool} = await import(pathToFileURL(modulePath).href);
const manager = new SkillManager();
await manager.discoverSkills(new Storage(project), [], true);
const directories = [];
const config = {getSkillManager: () => manager,
                getWorkspaceContext: () => ({addDirectory: dir => directories.push(dir)})};
const result = await new ActivateSkillTool(config).buildAndExecute(
  {name: 'make-prompt-better'}, new AbortController().signal);
const resources = result.llmContent.split('<available_resources>')[1]?.split('</available_resources>')[0];
console.log(JSON.stringify({active: manager.isSkillActive('make-prompt-better'), directories,
                            body: result.llmContent.includes('# Make Prompt Better'), resources}));
"""
            probe = subprocess.run(["node", "--input-type=module", "-e", script, str(module), str(project)],
                                   cwd=project, env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(probe.returncode, 0, probe.stdout + probe.stderr)
            activation = json.loads(probe.stdout)
            self.assertTrue(activation["active"])
            self.assertTrue(activation["body"])
            self.assertEqual(activation["directories"], [str(project / ".gemini/skills/make-prompt-better")])
            for name in ("domain-templates.md", "research-principles.md", "examples.md"):
                self.assertIn(name, activation["resources"])

    def test_project_and_global_discovery_update_recovery_and_uninstall(self):
        with tempfile.TemporaryDirectory(prefix="mpb-gemini-host-") as tmp:
            root = Path(tmp).resolve()
            home = root / "home"
            project = root / "project"
            home.mkdir()
            project.mkdir()
            (home / ".gemini").mkdir()
            (home / ".gemini/trustedFolders.json").write_text(
                json.dumps({str(project): "TRUST_FOLDER"}), encoding="utf-8"
            )
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith(("GEMINI_", "GOOGLE_"))}
            env.update(HOME=str(home), XDG_CONFIG_HOME=str(root / "config"),
                       XDG_CACHE_HOME=str(root / "cache"), XDG_DATA_HOME=str(root / "data"),
                       NO_COLOR="1", TERM="dumb")

            def run(*args, cwd=project, expected=0):
                result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                                        text=True, timeout=30)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return result

            def install(*args):
                return run("bash", str(ROOT / "install.sh"), "--runtime", "gemini", *args)

            def discovered(expected):
                result = run(GEMINI, "skills", "list")
                entries = re.findall(r"(?m)^make-prompt-better \[Enabled\]$", result.stdout)
                self.assertEqual(len(entries), 1 if expected else 0, result.stdout + result.stderr)
                if expected:
                    self.assertIn(f"Location:    {expected / 'SKILL.md'}", result.stdout)
                return result

            project_skill = project / ".gemini/skills/make-prompt-better"
            global_skill = home / ".gemini/skills/make-prompt-better"
            discovered(None)
            install("--project")
            discovered(project_skill)
            skill_file = project_skill / "SKILL.md"
            skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
            run("bash", str(ROOT / "install.sh"), "--runtime", "gemini", "--project", "--check", expected=1)
            install("--project")
            backups = (project / ".make-prompt-better/backups").glob("*/payload/SKILL.md")
            self.assertTrue(any("local edit" in path.read_text(encoding="utf-8") for path in backups))
            install("--project", "--check")
            discovered(project_skill)
            install("--global")
            conflict = discovered(project_skill)
            self.assertIn("Skill conflict detected", conflict.stderr)
            install("--project", "--uninstall")
            discovered(global_skill)
            install("--global", "--uninstall")
            discovered(None)


if __name__ == "__main__":
    unittest.main()
