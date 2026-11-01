import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def run(*cmd, cwd=ROOT, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=30)


class GlobalInstallerTests(unittest.TestCase):
    def test_each_runtime_copy_and_uninstall_in_isolated_home(self):
        targets = {
            'claude': ['.claude/skills'], 'gemini': ['.gemini/skills', '.gemini/config/skills'],
            'antigravity': ['.gemini/antigravity/skills'], 'codex': ['.codex/skills'],
            'cursor': ['.cursor/skills'], 'qwen': ['.qwen/skills'],
        }
        with tempfile.TemporaryDirectory(prefix='global home spaces ') as tmp:
            root = Path(tmp)
            env = dict(os.environ, HOME=tmp)
            for runtime, paths in targets.items():
                with self.subTest(runtime=runtime):
                    args = ('bash', str(ROOT / 'install.sh'), '--global', '--runtime', runtime)
                    result = run(*args, env=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    for path in paths:
                        self.assertTrue((root / path / 'make-prompt-better/SKILL.md').is_file())
                    if runtime == 'cursor':
                        self.assertTrue((root / '.cursor/rules/make-prompt-better.mdc').is_file())
                    result = run(*args, '--uninstall', env=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    for path in paths:
                        self.assertFalse((root / path / 'make-prompt-better').exists())
                    if runtime == 'cursor':
                        self.assertFalse((root / '.cursor/rules/make-prompt-better.mdc').exists())

    def test_global_all_skip_and_force(self):
        with tempfile.TemporaryDirectory(prefix='global all ') as tmp:
            root = Path(tmp)
            env = dict(os.environ, HOME=tmp)
            args = ('bash', str(ROOT / 'install.sh'), '--global')
            self.assertEqual(run(*args, env=env).returncode, 0)
            self.assertTrue((root / '.agents/skills/make-prompt-better/SKILL.md').exists())
            self.assertFalse((root / '.claude').exists())
            self.assertEqual(run(*args, '--all', env=env).returncode, 0)
            self.assertTrue((root / '.claude/skills/make-prompt-better/SKILL.md').exists())
            self.assertTrue((root / '.cursor/rules/make-prompt-better.mdc').exists())
            self.assertEqual(run(*args, '--uninstall', env=env).returncode, 0)
            self.assertFalse((root / '.agents/skills/make-prompt-better').exists())
            self.assertFalse((root / '.cursor/rules/make-prompt-better.mdc').exists())

    def test_interrupted_mutations_are_recoverable(self):
        for command, extra in [('mkdir', ()), ('rm', ()), ('mv', ('--backup',)), ('cp', ()), ('ln', ('--symlink',))]:
            with self.subTest(command=command), tempfile.TemporaryDirectory(prefix='interrupted operation ') as tmp:
                root = Path(tmp)
                target = root / '.claude/skills/make-prompt-better'
                target.mkdir(parents=True)
                (target / 'original').write_text('old')
                fakebin = root / 'fakebin'
                fakebin.mkdir()
                fake = fakebin / command
                fake.write_text('#!/bin/sh\nkill -TERM $$\n')
                fake.chmod(0o755)
                env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ['PATH'])
                args = ('bash', str(ROOT / 'install.sh'), '--project', '--runtime', 'claude', *extra)
                self.assertNotEqual(run(*args, cwd=root, env=env).returncode, 0)
                result = run('bash', str(ROOT / 'install.sh'), '--project', '--runtime', 'claude', cwd=root)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((target / 'SKILL.md').exists())

    def test_backup_preserves_original_if_copy_is_interrupted(self):
        with tempfile.TemporaryDirectory(prefix='backup interruption ') as tmp:
            root = Path(tmp)
            target = root / '.claude/skills/make-prompt-better'
            target.mkdir(parents=True)
            (target / 'original').write_text('original data')
            fakebin = root / 'fakebin'
            fakebin.mkdir()
            fake = fakebin / 'cp'
            fake.write_text('#!/bin/sh\nkill -TERM $$\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ['PATH'])
            args = ('bash', str(ROOT / 'install.sh'), '--project', '--runtime', 'claude', '--backup')
            self.assertNotEqual(run(*args, cwd=root, env=env).returncode, 0)
            backups = list(target.parent.glob('make-prompt-better.bak.*/original'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), 'original data')
            self.assertEqual(run(*args, cwd=root).returncode, 0)
            self.assertEqual(backups[0].read_text(), 'original data')


class ReleaseCheckTests(unittest.TestCase):
    def test_each_release_surface_rejects_mismatch_or_missing_file(self):
        files = ['package.json', '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json',
                 'pyproject.toml', 'CITATION.cff', 'install.sh', 'CHANGELOG.md', 'README.md',
                 'assets/hero-banner.svg', 'make-prompt-better/SKILL.md', 'bin/cli.mjs',
                 'scripts/lint-prompt.mjs', 'scripts/check-release.py']
        with tempfile.TemporaryDirectory(prefix='release checks ') as tmp:
            root = Path(tmp)
            for name in files:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, dest)
            def check():
                return run('python3', str(root / 'scripts/check-release.py'), cwd=root)
            self.assertEqual(check().returncode, 0)
            for name in files[:10]:
                with self.subTest(name=name):
                    path = root / name
                    original = path.read_text()
                    path.write_text(original.replace('4.3.0', '9.9.9'))
                    self.assertNotEqual(check().returncode, 0, name)
                    path.write_text(original)
            for name in files[:10]:
                with self.subTest(missing=name):
                    path = root / name
                    backup = path.with_name(path.name + '.fixture-backup')
                    path.rename(backup)
                    try:
                        self.assertNotEqual(check().returncode, 0)
                    finally:
                        backup.rename(path)
