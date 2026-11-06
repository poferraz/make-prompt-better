"""Exercise the public smoke job's publication gate without publishing."""
import ast
import os
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/publish-npm.yml'


class PublicSmokeWorkflowTests(unittest.TestCase):
    def test_publisher_requires_preflight_with_release_evidence_enabled(self):
        workflow = WORKFLOW.read_text()
        verify = re.search(r'(?ms)^  verify:\n(.*?)(?=^  [\w-]+:\n|\Z)', workflow).group(1)
        self.assertIn('uses: ./.github/workflows/npm-preflight.yml', verify)
        condition = re.search(r'publishing: \$\{\{ (.+) \}\}', verify)
        self.assertIsNotNone(condition)
        for event, operation, expected in [
            ('workflow_dispatch', 'publish', True), ('workflow_dispatch', 'preflight', False),
            ('workflow_dispatch', 'check-token', False), ('push', 'publish', False),
            ('pull_request', 'publish', False),
        ]:
            context = {'github.event_name': event, 'inputs.operation': operation}
            clauses = [clause.split(' == ', 1) for clause in condition.group(1).split(' && ')]
            self.assertEqual(all(context[left] == ast.literal_eval(right) for left, right in clauses), expected)
        preflight = (ROOT / '.github/workflows/npm-preflight.yml').read_text()
        guard = re.search(r'(?ms)^      - name: Require a published stable tag.*?(?=^      - |\Z)', preflight)
        self.assertIsNotNone(guard)
        self.assertIn('if: inputs.publishing', guard.group(0))
        self.assertIn('gh api --paginate --slurp', guard.group(0))
        self.assertIn('python3 scripts/npm_release.py release', guard.group(0))
        publisher = re.search(r'(?ms)^  publish:\n(.*?)(?=^  [\w-]+:\n|\Z)', workflow).group(1)
        self.assertRegex(publisher, r'(?m)^    needs: verify$')
        self.assertIn("inputs.operation == 'publish'", publisher)

    def test_recurring_coverage_runs_public_smoke_and_checks_its_floor(self):
        workflow = (ROOT / '.github/workflows/recurring-tests.yml').read_text()
        match = re.search(r'(?ms)^      - name: Python branch coverage\n.*?^        run: \|\n((?:          [^\n]*\n)+)', workflow)
        self.assertIsNotNone(match)
        script = textwrap.dedent(match.group(1))
        with tempfile.TemporaryDirectory(prefix='npm coverage workflow ') as tmp:
            root = Path(tmp)
            (root / 'test-artifacts').mkdir()
            fake = root / 'python'
            fake.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CAPTURE_COMMANDS"\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ['PATH'],
                       CAPTURE_COMMANDS=str(root / 'commands'))
            result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', script], env=env,
                                    cwd=root, text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('-m coverage run -a -m unittest discover -s tests -p test_public_npm_smoke.py -v',
                          (root / 'commands').read_text().splitlines())
        source = ast.parse((ROOT / 'tests/check_python_coverage.py').read_text())
        assignment = next(node for node in source.body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == 'FLOORS' for target in node.targets))
        self.assertGreater(ast.literal_eval(assignment.value).get('scripts/public_npm_smoke.py', 0), 0)

    def test_preflight_triggers_for_representative_package_changes(self):
        workflow = (ROOT / '.github/workflows/validate-skill.yml').read_text()
        for event in ('pull_request', 'push'):
            block = re.search(r'(?ms)^  ' + event + r':\n(.*?)(?=^  [\w-]+:|\Z)', workflow)
            self.assertIsNotNone(block)
            self.assertIn('branches: [main]', block.group(1))
            self.assertNotRegex(block.group(1), r'(?m)^    paths(?:-ignore)?:')
        job = re.search(r'(?ms)^  package:\n(.*?)(?=^  [\w-]+:\n|\Z)', workflow)
        self.assertIsNotNone(job)
        self.assertIn('uses: ./.github/workflows/npm-preflight.yml', job.group(1))
        self.assertNotRegex(job.group(1), r'(?m)^    if:')
        preflight = (ROOT / '.github/workflows/npm-preflight.yml').read_text()
        self.assertNotRegex(preflight, r'secrets\.|NODE_AUTH_TOKEN|id-token:\s*write|npm publish')

    def job(self):
        text = WORKFLOW.read_text()
        match = re.search(r'(?ms)^  public-install-smoke:\n(.*?)(?=^  [\w-]+:\n|\Z)', text)
        self.assertIsNotNone(match, 'A separate public installation verification job is required')
        return match.group(1)

    def test_job_is_gated_by_explicit_publish_and_successful_dependencies(self):
        job = self.job()
        self.assertRegex(job, r'(?m)^    needs: \[verify, publish\]$')
        condition = re.search(r'(?m)^    if: (.+)$', job)
        self.assertIsNotNone(condition)
        def eligible(event, operation, repository, successful):
            context = {'github.event_name': event, 'inputs.operation': operation,
                       'github.repository': repository}
            clauses = condition.group(1).split(' && ')
            self.assertEqual(len(clauses), 3)
            matches = []
            for clause in clauses:
                left, right = clause.split(' == ', 1)
                self.assertIn(left, context)
                matches.append(context[left] == ast.literal_eval(right))
            return successful and all(matches)
        self.assertTrue(eligible('workflow_dispatch', 'publish', 'poferraz/make-prompt-better', True))
        for event, operation, repository, successful in [
            ('push', 'publish', 'poferraz/make-prompt-better', True),
            ('workflow_dispatch', 'preflight', 'poferraz/make-prompt-better', True),
            ('workflow_dispatch', 'check-token', 'poferraz/make-prompt-better', True),
            ('workflow_dispatch', 'publish', 'fork/make-prompt-better', True),
            ('workflow_dispatch', 'publish', 'poferraz/make-prompt-better', False),
        ]:
            with self.subTest(event=event, operation=operation, repository=repository, successful=successful):
                self.assertFalse(eligible(event, operation, repository, successful))
        self.assertNotRegex(job, r'secrets\.|NODE_AUTH_TOKEN|id-token:\s*write')
        self.assertIn('persist-credentials: false', job)

    def test_step_passes_verified_tag_and_integrity_as_literal_arguments(self):
        job = self.job()
        self.assertIn('RELEASE_TAG: ${{ needs.verify.outputs.tag }}', job)
        self.assertIn('EXPECTED_INTEGRITY: ${{ needs.verify.outputs.integrity }}', job)
        match = re.search(r'(?ms)^      - name: Verify public installation\n.*?^        run: \|\n((?:          [^\n]*\n)+)', job)
        self.assertIsNotNone(match)
        script = textwrap.dedent(match.group(1))
        with tempfile.TemporaryDirectory(prefix='npm workflow smoke ') as tmp:
            root = Path(tmp)
            fake = root / 'python3'
            fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$CAPTURE_ARGS"\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ['PATH'],
                       RELEASE_TAG='v4.4.1', EXPECTED_INTEGRITY='sha512-fixture integrity',
                       CAPTURE_ARGS=str(root / 'args'))
            result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', script], env=env,
                                    cwd=root, text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / 'args').read_text().splitlines(),
                             ['scripts/public_npm_smoke.py', '--tag', 'v4.4.1',
                              '--integrity', 'sha512-fixture integrity'])


if __name__ == '__main__':
    unittest.main()
