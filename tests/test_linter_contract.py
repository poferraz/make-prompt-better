import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LinterContractTests(unittest.TestCase):
    def run_command(self, *args, **kwargs):
        return subprocess.run(args, text=True, capture_output=True, timeout=30, **kwargs)

    def test_legitimate_deadline_and_answer_order_are_not_instructed_away(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "prompt.md"
            prompt.write_text("Prepare a briefing for tomorrow's client demo. State the final answer first, after checking the evidence. Preserve the deadline and budget.")
            for command in (["node", str(ROOT / "bin/cli.mjs"), "lint", "--json"],
                            ["python3", str(ROOT / "lint_context.py"), "--json"]):
                with self.subTest(command=command[0]):
                    result = self.run_command(*command, str(prompt))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    findings = json.loads(result.stdout)[0]["findings"]
                    advice = " ".join(f["remediation"] for f in findings).lower()
                    self.assertNotIn("never downstream", advice)
                    self.assertNotIn("without disclosing downstream", advice)
                    self.assertNotIn("before emitting the verdict", advice)
                    self.assertNotIn("before the formal conclusion", advice)

    def test_empty_input_and_scores_do_not_claim_certification(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "empty.md"
            prompt.write_text("")
            for command in (["node", str(ROOT / "bin/cli.mjs"), "lint", "--json"],
                            ["python3", str(ROOT / "lint_context.py"), "--json"]):
                with self.subTest(command=command[0]):
                    result = self.run_command(*command, str(prompt))
                    data = json.loads(result.stdout)[0]
                    self.assertTrue(data["findings"])
                    self.assertNotIn("certified", data["grade"].lower())
                    self.assertNotIn("production-ready", data["grade"].lower())

    def test_missing_bash_and_unknown_options_return_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, PATH=tmp)
            node = shutil.which("node")
            result = self.run_command(node, str(ROOT / "bin/cli.mjs"), "init", "--dry-run", env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("bash", result.stderr.lower())
            prompt = Path(tmp) / "prompt"
            prompt.write_text("hello")
            result = self.run_command(node, str(ROOT / "bin/cli.mjs"), "lint", "--strict", str(prompt))
            self.assertNotEqual(result.returncode, 0)

    def test_findings_are_informational_unless_policy_flag_is_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "prompt"
            prompt.write_text("You are a world-class expert. Do not hallucinate.")
            base = ["node", str(ROOT / "bin/cli.mjs"), "lint"]
            self.assertEqual(self.run_command(*base, str(prompt)).returncode, 0)
            self.assertNotEqual(self.run_command(*base, "--fail-on-findings", str(prompt)).returncode, 0)

    def test_dash_prefixed_paths_work_and_unknown_self_test_flags_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "-prompt.md").write_text("Review this.")
            cli = ["node", str(ROOT / "bin/cli.mjs"), "lint"]
            self.assertEqual(self.run_command(*cli, "--", "-prompt.md", cwd=root).returncode, 0)
            self.assertNotEqual(self.run_command(*cli, "--self-test", "--strict").returncode, 0)

    def test_directory_input_has_a_readable_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_command("node", str(ROOT / "bin/cli.mjs"), "lint", tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Cannot read", result.stderr)
            self.assertNotIn("node:internal", result.stderr)

    def test_standalone_linters_reject_unknown_flags_and_support_policy_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "prompt"
            prompt.write_text("You are a world-class expert. Do not hallucinate.")
            for command in (["node", str(ROOT / "scripts/lint-prompt.mjs")],
                            ["python3", str(ROOT / "lint_context.py")]):
                with self.subTest(command=command[0]):
                    unknown = self.run_command(*command, "--strict", str(prompt))
                    self.assertNotEqual(unknown.returncode, 0)
                    policy = self.run_command(*command, "--fail-on-findings", str(prompt))
                    self.assertEqual(policy.returncode, 1, policy.stderr)
                    self.assertIn("Score:", policy.stdout)

    def test_python_linter_reports_unreadable_directories_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_command("python3", str(ROOT / "lint_context.py"), tmp)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("Cannot read", result.stderr)


if __name__ == "__main__":
    unittest.main()
