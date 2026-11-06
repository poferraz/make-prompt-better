"""User-visible guided installation, with real terminal and filesystem behavior."""
import os
from pathlib import Path
import pty
import signal
import subprocess
import tempfile
import unittest

from terminal_session import terminal_session


ROOT = Path(__file__).resolve().parents[1]
CLI = ['node', str(ROOT / 'bin/cli.mjs')]


class GuidedInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='guided install spaces ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home, self.project = self.root / 'home', self.root / 'project'
        self.home.mkdir()
        self.project.mkdir()

    def guide(self, runtime=b'codex\n', scope=b'project\n', **kwargs):
        return terminal_session(CLI, cwd=self.project, home=self.home,
                                answers=[(b'Runtime', runtime), (b'Scope', scope)], **kwargs)

    def assert_no_install(self):
        for base in (self.home, self.project):
            self.assertFalse((base / '.agents/skills/make-prompt-better').exists())
            self.assertFalse((base / '.make-prompt-better').exists())

    def test_bare_terminal_installs_checks_and_preserves_edits_on_repeat(self):
        result = self.guide()
        target = self.project / '.agents/skills/make-prompt-better'
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue((target / 'SKILL.md').is_file(), result.stdout)
        self.assertFalse(target.is_symlink())
        self.assertEqual((target / 'SKILL.md').read_bytes(), (ROOT / 'make-prompt-better/SKILL.md').read_bytes())
        self.assertIn('Check passed.', result.stdout)
        self.assertIn('Installation verified.', result.stdout)
        self.assertIn('$make-prompt-better', result.stdout)
        self.assertFalse((self.home / '.agents').exists())
        (target / 'SKILL.md').write_text((target / 'SKILL.md').read_text() + '\nMy local changes\n')
        repeated = self.guide()
        self.assertEqual(repeated.returncode, 0, repeated.stdout)
        self.assertIn('Check passed.', repeated.stdout)
        backups = (self.project / '.make-prompt-better/backups').glob('*/payload/SKILL.md')
        self.assertTrue(any('My local changes' in backup.read_text() for backup in backups))

    def test_numbers_select_agent_and_user_scope_without_writing_project(self):
        result = self.guide(runtime=b'1\n', scope=b'2\n')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue((self.home / '.agents/skills/make-prompt-better/SKILL.md').is_file(), result.stdout)
        self.assertFalse((self.project / '.agents').exists())
        self.assertFalse((self.home / '.claude').exists())
        self.assertIn('Check passed.', result.stdout)

    def test_invalid_choices_are_retried_before_installing_the_selected_agent(self):
        result = self.guide(runtime=b'99\nnot-an-agent\nclaude\n', scope=b'wrong\nproject\n')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue((self.project / '.claude/skills/make-prompt-better/SKILL.md').is_file(), result.stdout)
        self.assertFalse((self.project / '.agents').exists())
        self.assertIn('Check passed.', result.stdout)
        self.assertIn('Installation verified.', result.stdout)

    def test_cancel_eof_and_interrupt_do_not_install(self):
        for response in (b'q\n', b'\x04', signal.SIGINT):
            for stage in ('Runtime', 'Scope'):
                with self.subTest(response=response, stage=stage):
                    answers = [] if stage == 'Runtime' else [(b'Runtime', b'codex\n')]
                    answers.append((stage.encode(), response))
                    result = terminal_session(CLI, cwd=self.project, home=self.home, answers=answers)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertNotIn('Installation verified.', result.stdout)
                    self.assert_no_install()

    def test_redirected_streams_keep_bare_help_without_installing(self):
        env = dict(os.environ, HOME=str(self.home))
        piped = subprocess.run(CLI, input='codex\nproject\n', cwd=self.project,
                               env=env, text=True, capture_output=True, timeout=10)
        self.assertEqual(piped.returncode, 0, piped.stderr)
        self.assertIn('Usage:', piped.stdout)
        master, slave = pty.openpty()
        try:
            redirected = subprocess.run(CLI, stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        cwd=self.project, env=env, text=True, timeout=10)
            self.assertEqual(redirected.returncode, 0, redirected.stderr)
            self.assertIn('Usage:', redirected.stdout)
        finally:
            os.close(slave)
            os.close(master)
        input_pipe = terminal_session(CLI, cwd=self.project, home=self.home,
                                      input_data=b'codex\nproject\n')
        self.assertEqual(input_pipe.returncode, 0, input_pipe.stdout)
        self.assertIn('Usage:', input_pipe.stdout)
        self.assert_no_install()

    def test_explicit_help_and_dry_run_remain_nonwriting_in_a_terminal(self):
        for args in (['--help'], ['install', '--runtime', 'codex', '--project', '--dry-run']):
            result = terminal_session([*CLI, *args], cwd=self.project, home=self.home)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertNotIn('Installation verified.', result.stdout)
            self.assert_no_install()

    def test_install_failure_skips_verification_and_readiness(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.project / '.agents').symlink_to(outside)
        result = self.guide()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertNotIn('Check passed.', result.stdout)
        self.assertNotIn('Verifying installation', result.stdout)
        self.assertNotIn('Installation verified.', result.stdout)
        self.assertEqual(list(outside.iterdir()), [])

    def test_post_install_mismatch_fails_the_real_check_without_claiming_readiness(self):
        fakebin = self.root / 'fakebin'
        fakebin.mkdir()
        wrapper = fakebin / 'bash'
        wrapper.write_text('#!/bin/sh\n/bin/bash "$@"\nstatus=$?\n[ "$status" -eq 0 ] || exit "$status"\ncase " $* " in\n*" --check "*) ;;\n*) printf "\\nTampered after installation\\n" >> "$TAMPER_TARGET" ;;\nesac\n')
        wrapper.chmod(0o755)
        target = self.project / '.agents/skills/make-prompt-better/SKILL.md'
        result = self.guide(env={'PATH': str(fakebin) + os.pathsep + os.environ['PATH'],
                                 'TAMPER_TARGET': str(target)})
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertTrue(target.is_file(), result.stdout)
        self.assertIn('Tampered after installation', target.read_text())
        self.assertIn('Missing or different', result.stdout)
        self.assertNotIn('Installation verified.', result.stdout)


if __name__ == '__main__':
    unittest.main()
