"""Exercise recurring workflow pipelines with failing test and coverage commands."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/recurring-tests.yml"


class RecurringWorkflowTests(unittest.TestCase):
    def test_piped_check_failure_fails_its_workflow_step(self):
        workflow = WORKFLOW.read_text()
        # GitHub's Linux/macOS default is bash -e; explicit bash adds pipefail.
        explicit_bash = bool(re.search(r"(?m)^defaults:\n  run:\n    shell: bash\s*$", workflow))
        shell_flags = ["-e", "-o", "pipefail"] if explicit_bash else ["-e"]
        scenarios = [
            ("Integration tests and JavaScript coverage", "integration"),
            ("Additional reproducible seeds", "seed"),
            ("Python branch coverage", "module"),
            ("Python branch coverage", "coverage"),
            ("Targeted mutation probe", "mutation"),
        ]
        with tempfile.TemporaryDirectory(prefix="recurring workflow ") as tmp:
            root = Path(tmp)
            fakebin = root / "bin"
            fakebin.mkdir()
            (root / "test-artifacts").mkdir()
            runner = root / "runner"
            c8 = runner / "c8/node_modules/.bin/c8"
            c8.parent.mkdir(parents=True)
            c8.write_text('#!/bin/bash\n[[ "$FAIL_KIND" != integration ]] || exit 23\n')
            c8.chmod(0o755)
            python = fakebin / "python"
            python.write_text(textwrap.dedent('''\
                #!/bin/bash
                case "$FAIL_KIND:$*" in
                  seed:*test_properties.py*|module:tests/check_python_coverage.py*|coverage:*coverage*report*|mutation:tests/mutation_probe.py*) exit 23 ;;
                esac
                exit 0
            '''))
            python.chmod(0o755)
            for name, fail_kind in scenarios:
                with self.subTest(step=name, failure=fail_kind):
                    match = re.search(
                        r"(?m)^      - name: " + re.escape(name) +
                        r"\n(?:        (?!run:)[^\n]*\n)*        run: (?:\|\n((?:          [^\n]*\n)+)|([^\n]+))",
                        workflow,
                    )
                    self.assertIsNotNone(match, name)
                    script = textwrap.dedent(match.group(1) or match.group(2))
                    env = dict(os.environ, PATH=f"{fakebin}{os.pathsep}{os.environ['PATH']}",
                               RUNNER_TEMP=str(runner), TEST_SEED="42", TEST_CASES="200",
                               FAIL_KIND=fail_kind)
                    success_env = dict(env, FAIL_KIND="none")
                    control = subprocess.run(["bash", *shell_flags, "-c", script], cwd=root,
                                             env=success_env, capture_output=True, text=True)
                    self.assertEqual(control.returncode, 0, control.stdout + control.stderr)
                    result = subprocess.run(["bash", *shell_flags, "-c", script], cwd=root,
                                            env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 23, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
