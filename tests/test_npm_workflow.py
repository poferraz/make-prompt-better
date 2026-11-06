"""Exercise the public smoke job's publication gate without publishing."""
import ast
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/publish-npm.yml'


class PublicSmokeWorkflowTests(unittest.TestCase):
    def test_publish_arguments_resolve_to_the_local_tarball_in_real_npm(self):
        commands = re.findall(r'\bnpm publish [^\n]+', WORKFLOW.read_text())
        self.assertEqual(len(commands), 2)
        npm_cli = str(Path(shutil.which('npm')).resolve())
        script = """
const {createRequire} = require('node:module');
const resolve = createRequire(process.argv[1])('npm-package-arg');
const spec = resolve(process.argv[2]);
console.log(JSON.stringify({type: spec.type, path: spec.fetchSpec}));
"""
        with tempfile.TemporaryDirectory(prefix='npm publish argument ') as tmp:
            artifact = Path(tmp) / 'dist/package.tgz'
            artifact.parent.mkdir()
            artifact.write_bytes(b'argument resolution fixture')
            for command in commands:
                with self.subTest(command=command):
                    argument = shlex.split(command)[2]
                    result = subprocess.run(['node', '-e', script, npm_cli, argument],
                                            cwd=tmp, text=True, capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    resolved = json.loads(result.stdout)
                    self.assertEqual(resolved['type'], 'file', 'npm must not interpret the artifact as a Git dependency')
                    self.assertEqual(Path(resolved['path']).resolve(), artifact.resolve())

    def test_existing_release_input_selects_source_and_serializes_the_same_version(self):
        workflow = WORKFLOW.read_text()
        preflight = (ROOT / '.github/workflows/npm-preflight.yml').read_text()
        self.assertIn('release_tag: ${{ inputs.release_tag }}', workflow)
        self.assertIn('${{ inputs.release_tag || github.ref_name }}', workflow)
        self.assertIn('ref: ${{ inputs.release_tag || github.ref }}', preflight)
        self.assertEqual(preflight.count('RELEASE_TAG: ${{ inputs.release_tag || github.ref_name }}'), 2)

    def test_release_guard_allows_main_or_matching_tag_and_rejects_other_contexts(self):
        preflight = (ROOT / '.github/workflows/npm-preflight.yml').read_text()
        match = re.search(r'(?ms)^      - name: Require a published stable tag.*?^        run: \|\n((?:          [^\n]*\n)+)', preflight)
        self.assertIsNotNone(match)
        script = textwrap.dedent(match.group(1))
        sha = 'a' * 40
        cases = [
            ('refs/heads/main', 'v4.5.0', 'poferraz/make-prompt-better', sha, 0, True),
            ('refs/tags/v4.5.0', 'v4.5.0', 'poferraz/make-prompt-better', sha, 0, True),
            ('refs/heads/main', 'main', 'poferraz/make-prompt-better', sha, 0, False),
            ('refs/heads/main', '', 'poferraz/make-prompt-better', sha, 0, False),
            ('refs/heads/topic', 'v4.5.0', 'poferraz/make-prompt-better', sha, 0, False),
            ('refs/tags/v4.5.1', 'v4.5.0', 'poferraz/make-prompt-better', sha, 0, False),
            ('refs/heads/main', 'v4.5.0', 'fork/make-prompt-better', sha, 0, False),
            ('refs/heads/main', 'v4.5.0', 'poferraz/make-prompt-better', 'b' * 40, 0, False),
            ('refs/heads/main', 'v4.5.0', 'poferraz/make-prompt-better', sha, 1, False),
            ('refs/heads/main', 'v4.5.0; touch bad', 'poferraz/make-prompt-better', sha, 0, False),
        ]
        for ref, tag, repository, tag_commit, ancestry, expected in cases:
            with self.subTest(ref=ref, tag=tag, repository=repository, tag_commit=tag_commit, ancestry=ancestry), tempfile.TemporaryDirectory(prefix='npm release guard ') as tmp:
                root = Path(tmp)
                commands = {
                    'git': '#!/bin/sh\ncase "$*" in\n"rev-parse HEAD") printf "%s\\n" "$TEST_HEAD" ;;\nrev-parse*) printf "%s\\n" "$TEST_TAG_COMMIT" ;;\nmerge-base*) exit "$TEST_ANCESTRY_EXIT" ;;\n*) exit 2 ;;\nesac\n',
                    'gh': '#!/bin/sh\nprintf "{}\\n"\n',
                    'python3': '#!/bin/sh\nprintf "%s\\n" "$*" >> "$VERIFY_CALLS"\n',
                }
                for name, content in commands.items():
                    path = root / name
                    path.write_text(content)
                    path.chmod(0o755)
                calls = root / 'verification-calls'
                env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ['PATH'],
                           GITHUB_REF=ref, GITHUB_REF_TYPE='tag' if ref.startswith('refs/tags/') else 'branch',
                           GITHUB_REPOSITORY=repository, RELEASE_TAG=tag, RUNNER_TEMP=tmp,
                           TEST_HEAD=sha, TEST_TAG_COMMIT=tag_commit, TEST_ANCESTRY_EXIT=str(ancestry),
                           VERIFY_CALLS=str(calls))
                result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', script], env=env,
                                        cwd=root, text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode == 0, expected, result.stderr)
                if expected:
                    self.assertIn(f'scripts/npm_release.py release --tag {tag} --commit {sha}', calls.read_text())
                    self.assertIn(f'scripts/npm_release.py registry --tag {tag}', calls.read_text())
                else:
                    self.assertFalse(calls.exists(), 'Invalid context must stop before release or registry verification')

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
        self.assertIn('ref: ${{ needs.verify.outputs.tag }}', job)
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
