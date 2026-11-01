import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=ROOT, env=None):
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, timeout=30)


class CliTests(unittest.TestCase):
    def cli(self, *args, cwd=ROOT):
        return run('node', str(ROOT / 'bin/cli.mjs'), *args, cwd=cwd)

    def test_help_version_and_unknown_command(self):
        self.assertIn('Usage:', self.cli('--help').stdout)
        self.assertEqual(self.cli('--version').stdout.strip(), json.loads((ROOT / 'package.json').read_text())['version'])
        self.assertEqual(self.cli('unknown').returncode, 1)

    def test_lint_json_multiple_files_and_missing(self):
        with tempfile.TemporaryDirectory(prefix='prompt test ') as tmp:
            path = Path(tmp) / 'prompt with spaces.md'
            path.write_text('Explain the task clearly.\n')
            result = self.cli('lint', '--json', str(path), str(path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(json.loads(result.stdout)), 2)
            self.assertEqual(self.cli('lint').returncode, 1)
            missing = self.cli('lint', str(path / 'missing'))
            self.assertEqual(missing.returncode, 1)
            self.assertIn('File not found', missing.stderr)

    def test_linter_self_tests_and_text_output(self):
        self.assertEqual(self.cli('lint', '--self-test').returncode, 0)
        self.assertEqual(run('node', str(ROOT / 'scripts/lint-prompt.mjs'), '--self-test').returncode, 0)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'empty.md'
            path.write_text('')
            result = self.cli('lint', str(path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('empty.md', result.stdout)

    def test_invalid_installer_option_propagates_exit(self):
        self.assertNotEqual(self.cli('init', '--not-an-option').returncode, 0)


class InstallerTests(unittest.TestCase):
    def test_copy_backup_symlink_uninstall_and_repeat(self):
        with tempfile.TemporaryDirectory(prefix='installer spaces ') as tmp:
            project = Path(tmp)
            target = project / '.claude/skills/make-prompt-better'
            def install(*args):
                result = run('bash', str(ROOT / 'install.sh'), '--project', '--runtime', 'claude', *args, cwd=project)
                self.assertEqual(result.returncode, 0, result.stderr)
            install('--dry-run')
            self.assertFalse(target.exists())
            install('--copy')
            self.assertEqual((target / 'SKILL.md').read_bytes(), (ROOT / 'make-prompt-better/SKILL.md').read_bytes())
            (target / 'marker').write_text('original')
            install('--backup')
            self.assertEqual(len(list(target.parent.glob('make-prompt-better.bak.*/marker'))), 1)
            install('--symlink')
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), ROOT / 'make-prompt-better')
            install('--uninstall')
            install('--uninstall')
            self.assertFalse(target.exists())

    def test_invalid_runtime_and_missing_argument(self):
        for args in [('--runtime', 'bad'), ('--runtime',)]:
            self.assertNotEqual(run('bash', str(ROOT / 'install.sh'), *args).returncode, 0)


class PackageTests(unittest.TestCase):
    def test_actual_archive_installs_and_runs(self):
        with tempfile.TemporaryDirectory(prefix='package spaces ') as tmp:
            env = dict(os.environ, npm_config_cache=str(Path(tmp) / 'npm-cache'))
            packed = run('npm', 'pack', '--json', '--pack-destination', tmp, env=env)
            self.assertEqual(packed.returncode, 0, packed.stderr)
            metadata = json.loads(packed.stdout)[0]
            names = {item['path'] for item in metadata['files']}
            for required in ['bin/cli.mjs', 'install.sh', 'lint_context.py', 'scripts/lint-prompt.mjs', 'make-prompt-better/SKILL.md']:
                self.assertIn(required, names)
            installed = run('npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund', '--prefix', tmp, str(Path(tmp) / metadata['filename']), env=env)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            cli = Path(tmp) / 'node_modules/.bin/make-prompt-better'
            self.assertEqual(run(str(cli), '--version').stdout.strip(), metadata['version'])
            self.assertEqual(run(str(cli), 'init', '--project', '--runtime', 'claude', cwd=Path(tmp)).returncode, 0)
            self.assertTrue((Path(tmp) / '.claude/skills/make-prompt-better/SKILL.md').exists())


if __name__ == '__main__':
    unittest.main()
