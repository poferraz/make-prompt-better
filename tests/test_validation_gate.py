"""Reject structural regressions and failed or skipped release prerequisites."""
import json
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ValidationWorkflowTests(unittest.TestCase):
    def test_source_and_package_workflows_propagate_verification_failure(self):
        with tempfile.TemporaryDirectory(prefix='workflow verification ') as tmp:
            root = Path(tmp)
            fake = root / 'npm'
            fake.write_text('#!/bin/sh\n[ "$*" = "run verify" ] || exit 98\nexit 23\n')
            fake.chmod(0o755)
            for filename, step in [('validate-skill.yml', 'Verify source and integration behavior'),
                                   ('npm-preflight.yml', 'Validate source')]:
                with self.subTest(workflow=filename):
                    workflow = (ROOT / '.github/workflows' / filename).read_text()
                    match = re.search(r'(?m)^      - name: ' + step + r'\n        run: ([^\n]+)', workflow)
                    self.assertIsNotNone(match)
                    result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', match.group(1)],
                                            env=dict(os.environ, PATH=str(root) + os.pathsep + os.environ['PATH']),
                                            text=True, capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 23, result.stdout + result.stderr)

    def test_required_validate_job_fails_for_every_unsuccessful_dependency(self):
        workflow = (ROOT / '.github/workflows/validate-skill.yml').read_text()
        match = re.search(r'(?ms)^  validate:\n(.*?)(?=^  [\w-]+:\n|\Z)', workflow)
        self.assertIsNotNone(match)
        job = match.group(1)
        dependencies = re.search(r'(?m)^    needs: \[([^\]]+)\]$', job)
        self.assertIsNotNone(dependencies, 'validate must wait for the complete release bar')
        names = [name.strip() for name in dependencies.group(1).split(',')]
        self.assertEqual(set(names), {'source', 'regression', 'package'})
        self.assertRegex(job, r'(?m)^    if: always\(\)$')
        self.assertIn('GATE_RESULTS: ${{ toJSON(needs) }}', job)
        script = re.search(r'(?m)^        run: \|\n((?:          [^\n]*\n)+)', job)
        self.assertIsNotNone(script)
        script = textwrap.dedent(script.group(1))

        def run(results):
            return subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', script],
                                  env=dict(os.environ, GATE_RESULTS=json.dumps(results)),
                                  text=True, capture_output=True, timeout=10)

        successful = {name: {'result': 'success'} for name in names}
        result = run(successful)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in names:
            for status in ('failure', 'cancelled', 'skipped', 'neutral', 'in_progress', None):
                with self.subTest(name=name, status=status):
                    result = run(dict(successful, **{name: {'result': status}}))
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            with self.subTest(missing=name):
                self.assertNotEqual(run({k: v for k, v in successful.items() if k != name}).returncode, 0)
        self.assertNotEqual(run({}).returncode, 0)

    def test_pr_and_main_gate_include_real_regression_and_package_workflows(self):
        workflow = (ROOT / '.github/workflows/validate-skill.yml').read_text()
        for event in ('push', 'pull_request'):
            block = re.search(r'(?ms)^  ' + event + r':\n(.*?)(?=^  [\w-]+:|\Z)', workflow)
            self.assertIsNotNone(block)
            self.assertIn('branches: [main]', block.group(1))
            self.assertNotIn('paths', block.group(1))
        for job_id, target in [('regression', 'recurring-tests.yml'), ('package', 'npm-preflight.yml')]:
            job = re.search(r'(?ms)^  ' + job_id + r':\n(.*?)(?=^  [\w-]+:\n|\Z)', workflow)
            self.assertIsNotNone(job, f'{job_id} must execute the real checks')
            self.assertIn('uses: ./.github/workflows/' + target, job.group(1))
            self.assertNotRegex(job.group(1), r'(?m)^    (if|continue-on-error):')
            called = (ROOT / '.github/workflows' / target).read_text()
            self.assertRegex(called, r'(?m)^  workflow_call:')
        self.assertNotRegex(workflow, r'continue-on-error:\s*true')


class StructuralGateTests(unittest.TestCase):
    def test_validator_rejects_each_broken_contract_without_modifying_source(self):
        script = ROOT / 'scripts/validate_repo.py'
        self.assertTrue(script.is_file(), 'Structural validation must also be runnable locally')
        spec = importlib.util.spec_from_file_location('validate_repo', script)
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory(prefix='structural gate ') as tmp:
            root = Path(tmp) / 'source'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
                '.private', '.git', 'node_modules', '__pycache__', '.coverage*'))
            def check():
                return subprocess.run([sys.executable, str(root / 'scripts/validate_repo.py')],
                                      cwd=root, text=True, capture_output=True, timeout=10)
            result = check()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('VALIDATED OK', validator.validate(root))
            skill = root / 'make-prompt-better/SKILL.md'
            original = skill.read_text()
            mutations = [
                original.replace('name: make-prompt-better', 'name: other-skill', 1),
                original.replace('description: "Use when ', 'description: "Other ', 1),
                original.replace('description: "Use when ', 'description: "Use when colon: ', 1),
                original.replace('description: "Use when ', 'extra: field\ndescription: "Use when ', 1),
                original.replace('description: "Use when ', 'description: "Use when ' + 'x' * 450, 1),
                original + '\n' * (500 - len(original.splitlines())),
            ]
            for index, mutated in enumerate(mutations):
                with self.subTest(mutation=index):
                    skill.write_text(mutated)
                    with self.assertRaises(ValueError):
                        validator.validate(root)
                    self.assertEqual(skill.read_text(), mutated)
            skill.write_text(original)
            templates = root / 'make-prompt-better/references/domain-templates.md'
            original_templates = templates.read_text()
            templates.write_text(original_templates + '\n## 13. Extra template\n')
            with self.assertRaises(ValueError):
                validator.validate(root)
            templates.write_text(original_templates)
            readme = root / 'README.md'
            original_readme = readme.read_text()
            private = root / '.private/notes.md'
            private.parent.mkdir(exist_ok=True)
            private.write_text('PRIVATE_SENTINEL')
            for extra in ('\nBad \u2014 punctuation\n', '\nBad \u2013 punctuation\n',
                          '\n[Missing](missing-file.md)\n',
                          '\n[Private](.private/notes.md)\n',
                          '\n[Private](%2eprivate/notes.md)\n',
                          '\n[Missing](https://github.com/poferraz/make-prompt-better/blob/main/missing.md)\n',
                          '\n[Missing](https://raw.githubusercontent.com/poferraz/make-prompt-better/main/missing.png)\n'):
                readme.write_text(original_readme + extra)
                with self.assertRaises(ValueError):
                    validator.validate(root)
            readme.write_text(original_readme)
            skill.unlink()
            self.assertNotEqual(check().returncode, 0)
            with self.assertRaises(OSError):
                validator.validate(root)

    def test_verification_command_preserves_failures_from_every_stage(self):
        scripts = json.loads((ROOT / 'package.json').read_text())['scripts']
        self.assertIn('verify', scripts)
        self.assertIn('verify:fast', scripts)
        with tempfile.TemporaryDirectory(prefix='verify commands ') as tmp:
            root = Path(tmp)
            fakebin = root / 'bin'
            fakebin.mkdir()
            # Only external commands are substituted; npm executes the real scripts.
            for name in ('python3', 'node', 'bash'):
                executable = fakebin / name
                executable.write_text('#!/bin/sh\ncase "$*" in *"$FAIL_COMMAND"*) exit 23;; esac\n')
                executable.chmod(0o755)
            # Keep node real: npm itself needs it. Test the python, bash and npm stages.
            (fakebin / 'node').unlink()
            (root / 'package.json').write_text(json.dumps({'scripts': scripts}))
            for name in ('scripts/lint-prompt.mjs', 'CLAUDE.md', 'AGENTS.md'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, target)
            for fail in ('scripts/validate_repo.py', 'scripts/check-release.py',
                         'lint_context.py', '-n install.sh', 'unittest discover'):
                env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ['PATH'], FAIL_COMMAND=fail)
                result = subprocess.run(['npm', 'run', 'verify'], cwd=root, env=env,
                                        text=True, capture_output=True, timeout=20)
                # Earlier stages must be able to run before the deliberately failed stage.
                self.assertEqual(result.returncode, 23, result.stdout + result.stderr)
            result = subprocess.run(['npm', 'run', 'verify'], cwd=root,
                                    env=dict(env, FAIL_COMMAND='no injected failure'),
                                    text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
