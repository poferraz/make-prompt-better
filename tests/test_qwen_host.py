"""Opt-in Qwen 0.26.9 host-library discovery, without an authenticated CLI session.

Set MPB_TEST_QWEN_HOST=1 and MPB_QWEN_PACKAGE_DIR to the installed
@qwen-code/qwen-code package directory. No model request is made.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ENABLED = os.environ.get("MPB_TEST_QWEN_HOST") == "1"

HOST_PROBE = r"""
import {pathToFileURL} from 'node:url';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
const [modulePath, project] = process.argv.slice(1);
const {SkillManager} = await import(pathToFileURL(modulePath).href);
const config = {getProjectRoot: () => project, getBareMode: () => false,
                getActiveExtensions: () => [], isSafeMode: () => false,
                isSkillEnabled: () => true};
const manager = new SkillManager(config);
const skill = await manager.loadSkillForRuntime('make-prompt-better');
if (!skill) { console.log(JSON.stringify(null)); process.exit(0); }
const references = {};
for (const name of ['domain-templates.md', 'research-principles.md', 'examples.md']) {
  const rel = `references/${name}`;
  references[rel] = {mentioned: skill.body.includes(rel),
                     content: await readFile(path.join(path.dirname(skill.filePath), rel), 'utf8')};
}
console.log(JSON.stringify({name: skill.name, level: skill.level, filePath: skill.filePath,
                            body: skill.body, references}));
"""


@unittest.skipUnless(ENABLED, "Set MPB_TEST_QWEN_HOST=1 and MPB_QWEN_PACKAGE_DIR")
class QwenHostLibraryTests(unittest.TestCase):
    def test_project_and_global_discovery_update_recovery_and_uninstall(self):
        package_dir = os.environ.get("MPB_QWEN_PACKAGE_DIR")
        self.assertTrue(package_dir, "Set MPB_QWEN_PACKAGE_DIR to the installed Qwen package")
        package = Path(package_dir).resolve()
        metadata = json.loads((package / "package.json").read_text(encoding="utf-8"))
        self.assertEqual((metadata["name"], metadata["version"]), ("@qwen-code/qwen-code", "0.26.9"))
        # This is the exported SkillManager bundle of the explicitly guarded version.
        module = package / "chunks/chunk-HQA2UOVS.js"
        self.assertTrue(module.is_file())
        with tempfile.TemporaryDirectory(prefix="mpb-qwen-host-") as tmp:
            root = Path(tmp).resolve()
            home, project = root / "home", root / "project"
            home.mkdir()
            project.mkdir()
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith(("QWEN_", "GEMINI_", "GOOGLE_", "OPENAI_", "ANTHROPIC_"))}
            env.update(HOME=str(home), XDG_CONFIG_HOME=str(root / "config"),
                       XDG_CACHE_HOME=str(root / "cache"), XDG_DATA_HOME=str(root / "data"))

            def run(*args, expected=0):
                result = subprocess.run(args, cwd=project, env=env, capture_output=True,
                                        text=True, timeout=30)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return result

            def install(*args, expected=0):
                return run("bash", str(ROOT / "install.sh"), "--runtime", "qwen", *args, expected=expected)

            def discovered(expected, level):
                result = run("node", "--input-type=module", "-e", HOST_PROBE, str(module), str(project))
                skill = json.loads(result.stdout)
                if expected is None:
                    self.assertIsNone(skill)
                    return
                self.assertEqual((skill["name"], skill["level"], Path(skill["filePath"])),
                                 ("make-prompt-better", level, expected / "SKILL.md"))
                self.assertIn("# Make Prompt Better", skill["body"])
                for relative, reference in skill["references"].items():
                    self.assertTrue(reference["mentioned"], relative)
                    self.assertEqual(reference["content"],
                                     (ROOT / "make-prompt-better" / relative).read_text(encoding="utf-8"))

            project_skill = project / ".qwen/skills/make-prompt-better"
            global_skill = home / ".qwen/skills/make-prompt-better"
            discovered(None, None)
            install("--global")
            discovered(global_skill, "user")
            install("--project")
            discovered(project_skill, "project")
            skill_file = project_skill / "SKILL.md"
            skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
            install("--project", "--check", expected=1)
            install("--project")
            backups = (project / ".make-prompt-better/backups").glob("*/payload/SKILL.md")
            self.assertTrue(any("local edit" in path.read_text(encoding="utf-8") for path in backups))
            discovered(project_skill, "project")
            install("--project", "--uninstall")
            discovered(global_skill, "user")
            install("--global", "--uninstall")
            discovered(None, None)


if __name__ == "__main__":
    unittest.main()
