"""Release authorization and artifact checks without publishing or credentials."""
import copy
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import sys
import unittest
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('npm_release', ROOT / 'scripts/npm_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.sha = 'a' * 40
        self.published = {'tag_name': 'v4.4.0', 'draft': False, 'prerelease': False,
                          'published_at': '2026-11-06T00:00:00Z'}
        self.runs = {'workflow_runs': [{'id': 2, 'path': '.github/workflows/validate-skill.yml',
                     'head_sha': self.sha, 'head_branch': 'main', 'event': 'push',
                     'status': 'completed', 'conclusion': 'success'}]}

    def test_stable_published_release_with_successful_exact_main_ci(self):
        self.assertEqual(release.validate_release('v4.4.0', self.sha, self.published, self.runs), '4.4.0')

    def test_paginated_ci_evidence_is_checked_without_ignoring_a_later_failure(self):
        first_page = {'workflow_runs': [dict(self.runs['workflow_runs'][0], path='other.yml')]}
        pages = [first_page, self.runs]
        self.assertEqual(release.validate_release('v4.4.0', self.sha, self.published, pages), '4.4.0')
        pages.append({'workflow_runs': [dict(self.runs['workflow_runs'][0], id=3, conclusion='failure')]})
        with self.assertRaises(ValueError):
            release.validate_release('v4.4.0', self.sha, self.published, pages)

    def test_newer_rerun_attempt_and_every_non_success_conclusion_block_release(self):
        passed = dict(self.runs['workflow_runs'][0], run_attempt=1)
        for status, conclusion in [('completed', 'failure'), ('completed', 'cancelled'),
                                   ('completed', 'skipped'), ('completed', 'neutral'),
                                   ('completed', 'timed_out'), ('in_progress', None), ('queued', None)]:
            retry = dict(passed, run_attempt=2, status=status, conclusion=conclusion)
            for ordered in ([passed, retry], [retry, passed]):
                with self.subTest(status=status, conclusion=conclusion, order=ordered):
                    with self.assertRaises(ValueError):
                        release.validate_release('v4.4.0', self.sha, self.published, {'workflow_runs': ordered})

    def test_incomplete_or_malformed_ci_evidence_fails_closed(self):
        for runs in ([], {}, None, [None], {'workflow_runs': 'not a list'},
                     {'total_count': 5, **self.runs},
                     {'workflow_runs': [dict(self.runs['workflow_runs'][0], id=None)]}):
            with self.subTest(runs=runs), self.assertRaises(ValueError):
                release.validate_release('v4.4.0', self.sha, self.published, runs)

    def test_invalid_tags_and_unpublished_releases_are_rejected(self):
        for tag in ['main', 'v4.4.0-beta', 'v04.4.0', '../v4.4.0', 'v4.4.0\n', 'v4.4.0; echo nope']:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release.validate_tag(tag)
        for field, value in [('tag_name', 'v9.9.9'), ('draft', True), ('prerelease', True), ('published_at', None)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.validate_release('v4.4.0', self.sha, dict(self.published, **{field: value}), self.runs)

    def test_failed_stale_missing_or_wrong_ci_is_rejected(self):
        for field, value in [('head_sha', 'b'*40), ('head_branch', 'feature'), ('event', 'pull_request'),
                             ('path', 'other.yml'), ('status', 'in_progress'), ('conclusion', 'failure')]:
            runs = copy.deepcopy(self.runs)
            runs['workflow_runs'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.validate_release('v4.4.0', self.sha, self.published, runs)
        with self.assertRaises(ValueError):
            release.validate_release('v4.4.0', self.sha, self.published, {'workflow_runs': []})
        runs = copy.deepcopy(self.runs)
        runs['workflow_runs'].append(dict(runs['workflow_runs'][0], id=3, conclusion='failure'))
        with self.assertRaises(ValueError):
            release.validate_release('v4.4.0', self.sha, self.published, runs)

    def test_registry_only_404_means_absent(self):
        for code in (401, 403, 429, 500):
            with self.subTest(code=code), patch.object(release.urllib.request, 'urlopen', side_effect=urllib.error.HTTPError('https://registry.npmjs.org', code, 'fixture', {}, None)):
                with self.assertRaises(urllib.error.HTTPError):
                    release.registry_version('4.4.0')
        with patch.object(release.urllib.request, 'urlopen', side_effect=urllib.error.HTTPError('https://registry.npmjs.org', 404, 'fixture', {}, None)):
            self.assertIsNone(release.registry_version('4.4.0'))
        with patch.object(release, 'registry_version', return_value={'name': 'make-prompt-better'}):
            with self.assertRaises(ValueError):
                release.check_registry('v4.4.0')
        data = {'name': 'make-prompt-better', 'version': '4.4.0', 'dist': {'integrity': 'sha512-fixture'}}
        with patch.object(release, 'registry_version', return_value=data):
            release.check_registry('v4.4.0', 'sha512-fixture')
            with self.assertRaises(ValueError):
                release.check_registry('v4.4.0', 'sha512-wrong')

    def test_registry_reads_bounded_json_and_cli_reports_absence(self):
        expected = {'name': 'make-prompt-better', 'version': '4.4.0'}
        with patch.object(release.urllib.request, 'urlopen', return_value=io.BytesIO(json.dumps(expected).encode())):
            self.assertEqual(release.registry_version('4.4.0'), expected)
        with patch.object(release.urllib.request, 'urlopen', return_value=io.BytesIO(b'x' * (1024 * 1024 + 1))):
            with self.assertRaises(ValueError):
                release.registry_version('4.4.0')
        with patch.object(release, 'registry_version', return_value=None), patch.object(sys, 'argv', ['npm_release.py', 'registry', '--tag', 'v4.4.0']), redirect_stdout(io.StringIO()) as output:
            release.main()
            self.assertIn('ownership unverified', output.getvalue())

    def test_release_cli_reads_the_supplied_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'release.json').write_text(json.dumps(self.published))
            (root / 'runs.json').write_text(json.dumps(self.runs))
            args = ['npm_release.py', 'release', '--tag', 'v4.4.0', '--commit', self.sha,
                    '--release-file', str(root / 'release.json'), '--runs-file', str(root / 'runs.json')]
            with patch.object(sys, 'argv', args), redirect_stdout(io.StringIO()) as output:
                release.main()
                self.assertEqual(json.loads(output.getvalue())['commit'], self.sha)


class ArchiveGateTests(unittest.TestCase):
    def setUp(self):
        self.package = json.loads((ROOT / 'package.json').read_text())
        self.version = self.package['version']
        self.tag = 'v' + self.version
        self.files = {name: b'fixture' for name in release.REQUIRED_FILES}
        self.files['make-prompt-better/SKILL.md'] = f'# Make Prompt Better ({self.tag})'.encode()

    def inspect(self, extra=None, special=None):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'package.tgz'
            files = dict(self.files, **{'package.json': json.dumps(self.package).encode()})
            files.update(extra or {})
            with tarfile.open(archive, 'w:gz') as tar:
                for name, content in files.items():
                    info = tarfile.TarInfo('package/' + name)
                    info.mode = 0o755 if name in release.EXECUTABLES else 0o644
                    info.size = len(content)
                    tar.addfile(info, io.BytesIO(content))
                if special:
                    tar.addfile(special)
            return release.inspect_archive(archive, self.tag)

    def test_package_identity_and_integrity(self):
        result = self.inspect()
        self.assertEqual(result['version'], self.version)
        self.assertTrue(result['integrity'].startswith('sha512-'))

    def test_wrong_identity_version_registry_and_lifecycle_hooks(self):
        original = copy.deepcopy(self.package)
        changes = [('name', 'wrong-package'), ('version', '9.9.9'), ('repository', {'url': 'https://example.com'}),
                   ('publishConfig', {'registry': 'https://example.com', 'access': 'public'}),
                   ('scripts', {'postinstall': 'echo unwanted'}), ('dependencies', {'unexpected': '*'})]
        for field, value in changes:
            self.package = dict(original, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.inspect()

    def test_sensitive_paths_and_credentials_are_rejected(self):
        for name in ['.npmrc', '.env', 'assets/.env.local', 'assets/private.pem', 'assets/.git/config',
                     'assets/.make-prompt-better/backups/data', 'unlisted.txt', '../escape']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.inspect({name: b'fixture'})
        for content in [b'npm_' + b'x'*40, b'-----BEGIN PRIVATE KEY-----']:
            with self.assertRaises(ValueError):
                self.inspect({'assets/accidental.txt': content})

    def test_missing_files_links_and_size_limits_are_rejected(self):
        del self.files['install.sh']
        with self.assertRaises(ValueError):
            self.inspect()
        self.files['install.sh'] = b'fixture'
        link = tarfile.TarInfo('package/assets/link')
        link.type = tarfile.SYMTYPE
        link.linkname = '/outside'
        with self.assertRaises(ValueError):
            self.inspect(special=link)
        with patch.object(release, 'MAX_FILE_BYTES', 2), self.assertRaises(ValueError):
            self.inspect()


class ActualPackageTests(unittest.TestCase):
    def test_real_archive_install_and_sensitive_file_exclusion(self):
        import os
        import shutil
        import subprocess
        with tempfile.TemporaryDirectory(prefix='npm release package ') as tmp:
            base = Path(tmp)
            source = base / 'source'
            source.mkdir()
            # Copy tracked source only; never copy local auth configuration into fixtures.
            names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
            for name in filter(None, names):
                original = ROOT / name
                if original.is_file():
                    target = source / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(original, target)
            (source / '.npmrc').write_text('//registry.npmjs.org/:_authToken=fixture-not-a-key\n')
            (source / '.env').write_text('EXAMPLE=fixture\n')
            runs = source / 'research/benchmark/v4/runs'
            runs.mkdir(parents=True, exist_ok=True)
            (runs / 'private.json').write_text('{}')
            config = base / 'empty.npmrc'
            config.write_text('')
            env = dict(os.environ, npm_config_userconfig=str(config), npm_config_cache=str(base / 'cache'))
            for key in ('NPM_TOKEN', 'NODE_AUTH_TOKEN'):
                env.pop(key, None)
            # The fixture config tests exclusion, not authentication. npm pack performs no publish.
            packed = subprocess.run(['npm', 'pack', '--ignore-scripts', '--json', '--pack-destination', str(base)],
                                    cwd=source, env=env, capture_output=True, text=True, timeout=60)
            self.assertEqual(packed.returncode, 0, packed.stderr)
            metadata = json.loads(packed.stdout)[0]
            paths = {item['path'] for item in metadata['files']}
            self.assertFalse({'.npmrc', '.env', 'research/benchmark/v4/runs/private.json'} & paths)
            archive = base / metadata['filename']
            report = release.inspect_archive(archive, 'v' + metadata['version'])
            self.assertEqual(report['integrity'], metadata['integrity'])
            for command, key, expected in [('audit', 'integrity', metadata['integrity']), ('smoke', 'package_smoke', 'passed')]:
                with patch.object(sys, 'argv', ['npm_release.py', command, str(archive), '--tag', 'v' + metadata['version']]), redirect_stdout(io.StringIO()) as output:
                    release.main()
                    self.assertEqual(json.loads(output.getvalue())[key], expected)

            # A release smoke must actually exercise each public lifecycle command.
            # Disable one command at a time in a valid archive; each must be rejected.
            with tarfile.open(archive, 'r:gz') as src:
                entries = [(copy.copy(member), src.extractfile(member).read())
                           for member in src if member.isfile()]
            marker = b'const args = process.argv.slice(2);'
            for broken_command in ('install', 'check', 'update', 'uninstall'):
                with self.subTest(broken_command=broken_command):
                    altered = base / f'broken-{broken_command}.tgz'
                    with tarfile.open(altered, 'w:gz') as dest:
                        for info, data in entries:
                            member = copy.copy(info)
                            if member.name == 'package/bin/cli.mjs':
                                self.assertEqual(data.count(marker), 1)
                                injection = f'if (process.argv[2] === "{broken_command}") process.exit(42);\n'.encode()
                                data = data.replace(marker, injection + marker)
                                member.size = len(data)
                            dest.addfile(member, io.BytesIO(data))
                    with self.assertRaisesRegex(ValueError, r'Smoke command failed: node \(exit 42\)'):
                        release.smoke_archive(altered, 'v' + metadata['version'])


class TokenCheckOutputTests(unittest.TestCase):
    """Run the exact workflow check against a local fetch stub, never a live token."""
    def test_authentication_results_never_log_credentials_or_raw_bodies(self):
        import os
        import re
        import subprocess
        import textwrap
        workflow = (ROOT / '.github/workflows/publish-npm.yml').read_text()
        step = workflow.split('- name: Authenticate without publishing or exposing the token', 1)[1]
        script = textwrap.dedent(re.search(r"node --input-type=module <<'JS'\n(.*?)\n          JS", step, re.S).group(1))
        sentinel = 'fixture-private-token-not-for-registry'
        cases = [
            ('valid', sentinel, 200, {'username': 'test-maintainer'}, 0, 'accepted'),
            ('rejected', sentinel, 401, {'error': sentinel}, 1, 'HTTP 401'),
            ('policy', sentinel, 403, {'error': sentinel}, 1, 'HTTP 403'),
            ('unexpected', sentinel, 200, {'private': sentinel}, 1, 'Unexpected'),
            ('network', sentinel, 0, {}, 1, 'could not reach'),
            ('missing', '', 200, {}, 1, 'empty or contains whitespace'),
            ('whitespace', sentinel + '\n', 200, {}, 1, 'empty or contains whitespace'),
        ]
        for name, token, status, body, expected, message in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                check = root / 'check.mjs'
                stub = ('globalThis.fetch = async () => { throw new Error("fixture network failure"); };\n' if status == 0
                        else f'globalThis.fetch = async () => new Response({json.dumps(json.dumps(body))}, {{status: {status}}});\n')
                check.write_text(stub + script)
                env = {'PATH': os.environ['PATH'], 'NODE_AUTH_TOKEN': token,
                       'GITHUB_STEP_SUMMARY': str(root / 'summary.md')}
                result = subprocess.run(['node', str(check)], env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, expected, result.stderr)
                logged = result.stdout + result.stderr + (root / 'summary.md').read_text()
                self.assertIn(message, logged)
                self.assertNotIn(sentinel, logged)
