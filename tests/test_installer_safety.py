import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.sh"


def install(project, *args, env=None):
    return subprocess.run(
        ["bash", str(INSTALLER), "--project", *args], cwd=project, env=env,
        text=True, capture_output=True, timeout=30,
    )


class InstallerSafetyTests(unittest.TestCase):
    def test_dry_run_reports_preview_without_claiming_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = install(project, "--runtime", "claude", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Would install", result.stdout)
            self.assertNotIn("Done. Synced", result.stdout)
            self.assertFalse((project / ".claude").exists())

    def test_non_cursor_install_and_uninstall_preserve_cursor_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            rule = project / ".cursor/rules/make-prompt-better.mdc"
            rule.parent.mkdir(parents=True)
            rule.write_text("user-owned rule")
            self.assertEqual(install(project, "--runtime", "claude").returncode, 0)
            self.assertEqual(rule.read_text(), "user-owned rule")
            self.assertEqual(install(project, "--runtime", "claude", "--uninstall").returncode, 0)
            self.assertEqual(rule.read_text(), "user-owned rule")

    def test_cursor_rule_symlink_does_not_modify_external_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            sentinel = project / "sentinel"
            sentinel.write_text("keep me")
            rule = project / ".cursor/rules/make-prompt-better.mdc"
            rule.parent.mkdir(parents=True)
            rule.symlink_to(sentinel)
            result = install(project, "--runtime", "cursor", "--backup")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(), "keep me")
            self.assertTrue(rule.is_symlink())

    def test_failed_copy_preserves_existing_install_without_backup_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            target = project / ".claude/skills/make-prompt-better"
            target.mkdir(parents=True)
            (target / "custom").write_text("old content")
            fakebin = project / "fakebin"
            fakebin.mkdir()
            (fakebin / "cp").write_text("#!/bin/sh\nexit 23\n")
            (fakebin / "cp").chmod(0o755)
            env = dict(os.environ, PATH=f"{fakebin}{os.pathsep}{os.environ['PATH']}")
            result = install(project, "--runtime", "claude", env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((target / "custom").exists())
            self.assertEqual((target / "custom").read_text(), "old content")

    def test_replacing_custom_skill_keeps_unique_recoverable_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            target = project / ".claude/skills/make-prompt-better"
            target.mkdir(parents=True)
            (target / "custom").write_text("first")
            self.assertEqual(install(project, "--runtime", "claude").returncode, 0)
            (target / "custom").write_text("second")
            self.assertEqual(install(project, "--runtime", "claude").returncode, 0)
            contents = sorted(p.read_text() for p in (project / ".make-prompt-better/backups").glob("*/payload/custom"))
            self.assertEqual(contents, ["first", "second"])

    def test_repeated_unchanged_copy_does_not_create_a_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            target = project / ".claude/skills/make-prompt-better"
            self.assertEqual(install(project, "--runtime", "claude").returncode, 0)
            repeated = install(project, "--runtime", "claude")
            self.assertEqual(repeated.returncode, 0)
            self.assertIn("1 already current", repeated.stdout)
            self.assertEqual(list(target.parent.glob("make-prompt-better.bak.*")), [])

    def test_repeated_cursor_install_does_not_backup_unchanged_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            rule = project / ".cursor/rules/make-prompt-better.mdc"
            self.assertEqual(install(project, "--runtime", "cursor").returncode, 0)
            self.assertEqual(install(project, "--runtime", "cursor").returncode, 0)
            self.assertEqual(list((project / ".make-prompt-better/backups").glob("make-prompt-better.mdc.*/payload")), [])

    def test_parent_symlink_does_not_redirect_project_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            outside = Path(tmp) / "outside"
            project.mkdir()
            outside.mkdir()
            (project / ".claude").symlink_to(outside, target_is_directory=True)
            result = install(project, "--runtime", "claude")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(outside.iterdir()), [])

    def test_cursor_custom_rule_is_preserved_without_explicit_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            rule = project / ".cursor/rules/make-prompt-better.mdc"
            rule.parent.mkdir(parents=True)
            rule.write_text("custom content")
            result = install(project, "--runtime", "cursor")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(rule.read_text(), "custom content")

    def test_explicit_cursor_backup_preserves_custom_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            rule = project / ".cursor/rules/make-prompt-better.mdc"
            rule.parent.mkdir(parents=True)
            rule.write_text("custom content")
            result = install(project, "--runtime", "cursor", "--backup")
            self.assertEqual(result.returncode, 0, result.stderr)
            backups = list((project / ".make-prompt-better/backups").glob("make-prompt-better.mdc.*/payload"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "custom content")
            self.assertIn("Managed by make-prompt-better installer", rule.read_text())

    def test_source_equal_to_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            parent = project / ".claude/skills"
            source = parent / "make-prompt-better"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("original skill")
            shutil.copy2(INSTALLER, parent / "install.sh")
            result = subprocess.run(["bash", str(parent / "install.sh"), "--project", "--runtime", "claude"],
                                    cwd=project, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((source / "SKILL.md").read_text(), "original skill")
            self.assertEqual(list(parent.glob("make-prompt-better.bak.*")), [])

    def test_locked_skill_target_preserves_existing_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            target = project / ".claude/skills/make-prompt-better"
            target.mkdir(parents=True)
            (target / "custom").write_text("unchanged")
            target.with_name(target.name + ".lock").mkdir()
            result = install(project, "--runtime", "claude")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((target / "custom").read_text(), "unchanged")

    def test_locked_cursor_rule_prevents_partial_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            lock = project / ".cursor/rules/make-prompt-better.mdc.lock"
            lock.mkdir(parents=True)
            result = install(project, "--runtime", "cursor")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((project / ".cursor/skills/make-prompt-better").exists())
            self.assertTrue(lock.exists())

    def test_failed_final_switch_leaves_recoverable_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            target = project / ".claude/skills/make-prompt-better"
            target.mkdir(parents=True)
            (target / "custom").write_text("before switch")
            fakebin = project / "fakebin"
            fakebin.mkdir()
            fake = fakebin / "mv"
            fake.write_text('#!/bin/sh\ncase "$1" in */.make-prompt-better.stage.*/skill) exit 23;; esac\nexec /bin/mv "$@"\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=f"{fakebin}{os.pathsep}{os.environ['PATH']}")
            result = install(project, "--runtime", "claude", env=env)
            self.assertNotEqual(result.returncode, 0)
            backups = list((project / ".make-prompt-better/backups").glob("*/payload/custom"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "before switch")


if __name__ == "__main__":
    unittest.main()
