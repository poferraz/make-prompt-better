import json
import os
from pathlib import Path
import pty
import re
import select
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

    def test_named_commands_preserve_edited_copy_and_uninstall_backup(self):
        with tempfile.TemporaryDirectory(prefix='cli lifecycle ') as tmp:
            root = Path(tmp)
            opts = ('--project', '--runtime', 'codex')
            target = root / '.agents/skills/make-prompt-better/SKILL.md'
            self.assertNotEqual(self.cli('check', *opts, cwd=root).returncode, 0)
            self.assertEqual(self.cli('install', *opts, cwd=root).returncode, 0)
            self.assertEqual(self.cli('check', *opts, cwd=root).returncode, 0)
            target.write_text(target.read_text() + '\nlocal edit\n')
            self.assertNotEqual(self.cli('check', *opts, cwd=root).returncode, 0)
            self.assertEqual(self.cli('update', *opts, cwd=root).returncode, 0)
            backups = list((root / '.make-prompt-better/backups').glob('*/payload/SKILL.md'))
            self.assertTrue(any('local edit' in p.read_text() for p in backups))
            self.assertEqual(self.cli('check', *opts, cwd=root).returncode, 0)
            self.assertEqual(self.cli('uninstall', *opts, cwd=root).returncode, 0)
            self.assertFalse(target.exists())
            self.assertGreaterEqual(len(list((root / '.make-prompt-better/backups').glob('*/payload/SKILL.md'))), 2)

    def test_named_commands_reject_contradictory_operations_before_mutation(self):
        with tempfile.TemporaryDirectory(prefix='cli conflicts ') as tmp:
            root = Path(tmp)
            for command, flag in [('update', '--uninstall'), ('update', '--check'), ('check', '--uninstall'),
                                  ('uninstall', '--check')]:
                with self.subTest(command=command, flag=flag):
                    result = self.cli(command, '--project', '--runtime', 'codex', flag, cwd=root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse((root / '.agents').exists())

    def test_noninteractive_new_commands_require_runtime_and_scope(self):
        with tempfile.TemporaryDirectory(prefix='cli explicit ') as tmp:
            root = Path(tmp)
            env = dict(os.environ, HOME=tmp)
            for command in ('check', 'update', 'uninstall'):
                for opts in ((), ('--runtime', 'codex'), ('--project',)):
                    with self.subTest(command=command, opts=opts):
                        result = run('node', str(ROOT / 'bin/cli.mjs'), command, *opts, cwd=root, env=env)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn('runtime', result.stderr.lower())
                        self.assertFalse((root / '.agents').exists())

    def test_new_commands_reject_duplicate_runtime_before_mutation(self):
        with tempfile.TemporaryDirectory(prefix='cli duplicate runtime ') as tmp:
            root = Path(tmp)
            for command in ('check', 'update', 'uninstall'):
                result = self.cli(command, '--project', '--runtime', 'claude', '-r', 'codex', cwd=root)
                self.assertNotEqual(result.returncode, 0, command)
                self.assertIn('runtime', result.stderr.lower())
                self.assertFalse((root / '.agents').exists())
                self.assertFalse((root / '.claude').exists())

    def test_new_commands_reject_conflicting_modes_before_mutation(self):
        with tempfile.TemporaryDirectory(prefix='cli duplicate mode ') as tmp:
            root = Path(tmp)
            for command in ('check', 'update', 'uninstall'):
                result = self.cli(command, '--project', '--runtime', 'codex', '--copy', '--symlink', cwd=root)
                self.assertNotEqual(result.returncode, 0, command)
                self.assertIn('copy', result.stderr.lower())
                self.assertFalse((root / '.agents').exists())

    def test_noninteractive_install_preserves_legacy_defaults_and_flags(self):
        with tempfile.TemporaryDirectory(prefix='cli legacy ') as tmp:
            root = Path(tmp)
            env = dict(os.environ, HOME=tmp)
            cli = ('node', str(ROOT / 'bin/cli.mjs'), 'install')
            self.assertEqual(run(*cli, cwd=root, env=env).returncode, 0)
            target = root / '.agents/skills/make-prompt-better/SKILL.md'
            self.assertTrue(target.exists())
            self.assertEqual(run(*cli, '--check', cwd=root, env=env).returncode, 0)
            self.assertEqual(run(*cli, '--uninstall', cwd=root, env=env).returncode, 0)
            self.assertFalse(target.exists())

    def test_named_commands_honor_symlink_mode_and_legacy_init(self):
        with tempfile.TemporaryDirectory(prefix='cli mode ') as tmp:
            root = Path(tmp)
            opts = ('--project', '--runtime', 'codex', '--symlink')
            self.assertEqual(self.cli('init', *opts, cwd=root).returncode, 0)
            self.assertEqual(self.cli('install', *opts, '--check', cwd=root).returncode, 0)
            self.assertEqual(self.cli('check', *opts, cwd=root).returncode, 0)
            self.assertEqual(self.cli('update', *opts, cwd=root).returncode, 0)
            self.assertTrue((root / '.agents/skills/make-prompt-better').is_symlink())

    def test_interactive_install_scope_selection_and_cancellation(self):
        with tempfile.TemporaryDirectory(prefix='cli tty ') as tmp:
            root = Path(tmp)
            def session(response):
                master, slave = pty.openpty()
                process = subprocess.Popen(['node', str(ROOT / 'bin/cli.mjs'), 'install',
                                            '--runtime', 'codex'], cwd=root,
                                           stdin=slave, stdout=slave, stderr=slave)
                os.close(slave)
                output = b''
                try:
                    while b'Scope' not in output and process.poll() is None:
                        ready, _, _ = select.select([master], [], [], 5)
                        self.assertTrue(ready, output.decode(errors='replace'))
                        try:
                            output += os.read(master, 4096)
                        except OSError:
                            break
                    self.assertIn(b'Scope', output)
                    os.write(master, response)
                    process.wait(timeout=10)
                    return process.returncode
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait()
                    os.close(master)
            self.assertNotEqual(session(b'q\n'), 0)
            self.assertFalse((root / '.agents').exists())
            self.assertNotEqual(session(b'\x04'), 0)
            self.assertFalse((root / '.agents').exists())
            self.assertEqual(session(b'invalid\nproject\n'), 0)
            self.assertTrue((root / '.agents/skills/make-prompt-better/SKILL.md').is_file())

    def test_interactive_runtime_detects_global_antigravity_and_installs_choice(self):
        with tempfile.TemporaryDirectory(prefix='cli tty runtime ') as tmp:
            root = Path(tmp)
            home = root / 'home'
            project = root / 'project'
            (home / '.gemini/antigravity').mkdir(parents=True)
            project.mkdir()
            master, slave = pty.openpty()
            process = subprocess.Popen(['node', str(ROOT / 'bin/cli.mjs'), 'install', '--project'],
                                       cwd=project, env=dict(os.environ, HOME=str(home)),
                                       stdin=slave, stdout=slave, stderr=slave)
            os.close(slave)
            output = b''
            try:
                while b'Runtime' not in output and process.poll() is None:
                    ready, _, _ = select.select([master], [], [], 5)
                    self.assertTrue(ready, output.decode(errors='replace'))
                    try:
                        output += os.read(master, 4096)
                    except OSError:
                        break
                self.assertIn(b'Detected host directories:', output)
                self.assertIn(b'antigravity', output)
                self.assertIn(b'Runtime', output)
                os.write(master, b'not-a-host\ncodex\n')
                self.assertEqual(process.wait(timeout=10), 0)
                self.assertTrue((project / '.agents/skills/make-prompt-better/SKILL.md').is_file())
                self.assertFalse((home / '.agents').exists())
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                os.close(master)


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
            self.assertEqual(len(list((project / '.make-prompt-better/backups').glob('*/payload/marker'))), 1)
            install('--symlink')
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), ROOT / 'make-prompt-better')
            install('--uninstall')
            install('--uninstall')
            self.assertFalse(target.exists())

    def test_invalid_runtime_and_missing_argument(self):
        for args in [('--runtime', 'bad'), ('--runtime',)]:
            self.assertNotEqual(run('bash', str(ROOT / 'install.sh'), *args).returncode, 0)

    def test_interrupted_copy_can_be_retried(self):
        with tempfile.TemporaryDirectory(prefix='interrupted install ') as tmp:
            root = Path(tmp)
            fakebin = root / 'fakebin'
            fakebin.mkdir()
            fakecp = fakebin / 'cp'
            fakecp.write_text('#!/bin/sh\nkill -TERM $$\n')
            fakecp.chmod(0o755)
            env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ['PATH'])
            args = ('bash', str(ROOT / 'install.sh'), '--project', '--runtime', 'claude')
            interrupted = run(*args, cwd=root, env=env)
            self.assertNotEqual(interrupted.returncode, 0)
            recovered = run(*args, cwd=root)
            self.assertEqual(recovered.returncode, 0, recovered.stderr)
            self.assertTrue((root / '.claude/skills/make-prompt-better/SKILL.md').exists())

    @unittest.skipIf(hasattr(os, 'geteuid') and os.geteuid() == 0, 'root bypasses directory permissions')
    def test_permission_error_is_reported_and_recoverable(self):
        with tempfile.TemporaryDirectory(prefix='permission install ') as tmp:
            root = Path(tmp)
            agent = root / '.claude'
            agent.mkdir(mode=0o500)
            args = ('bash', str(ROOT / 'install.sh'), '--project', '--runtime', 'claude')
            try:
                denied = run(*args, cwd=root)
                self.assertNotEqual(denied.returncode, 0)
                self.assertFalse((agent / 'skills/make-prompt-better/SKILL.md').exists())
            finally:
                agent.chmod(0o700)
            recovered = run(*args, cwd=root)
            self.assertEqual(recovered.returncode, 0, recovered.stderr)
            self.assertTrue((agent / 'skills/make-prompt-better/SKILL.md').exists())


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
            readme = (ROOT / 'README.md').read_text()
            links = re.findall(r'\]\(([^)]+)\)', readme) + re.findall(r'<img\s+src="([^"]+)"', readme)
            for link in links:
                if link.startswith(('http://', 'https://', '#', 'mailto:')):
                    continue
                target = link.split('#', 1)[0]
                if target:
                    self.assertIn(target, names, f'Packaged README target missing: {target}')
            self.assertNotIn('scripts/run_benchmarks_queue.sh', names)
            installed = run('npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund', '--prefix', tmp, str(Path(tmp) / metadata['filename']), env=env)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            cli = Path(tmp) / 'node_modules/.bin/make-prompt-better'
            self.assertEqual(run(str(cli), '--version').stdout.strip(), metadata['version'])
            self.assertEqual(run(str(cli), 'init', '--project', '--runtime', 'claude', cwd=Path(tmp)).returncode, 0)
            target = Path(tmp) / '.claude/skills/make-prompt-better/SKILL.md'
            self.assertTrue(target.exists())
            opts = ('--project', '--runtime', 'claude')
            self.assertEqual(run(str(cli), 'install', *opts, cwd=Path(tmp)).returncode, 0)
            self.assertEqual(run(str(cli), 'check', *opts, cwd=Path(tmp)).returncode, 0)
            target.write_text(target.read_text() + '\npackaged local edit\n')
            updated = run(str(cli), 'update', *opts, cwd=Path(tmp))
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertIn(metadata['version'], updated.stdout)
            self.assertIn('no version is fetched', updated.stdout)
            backups = list((Path(tmp) / '.make-prompt-better/backups').glob('*/payload/SKILL.md'))
            self.assertTrue(any('packaged local edit' in backup.read_text() for backup in backups))
            self.assertEqual(run(str(cli), 'check', *opts, cwd=Path(tmp)).returncode, 0)
            self.assertEqual(run(str(cli), 'uninstall', *opts, cwd=Path(tmp)).returncode, 0)
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
