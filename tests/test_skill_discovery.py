"""Filesystem discovery regressions; these do not simulate the Codex UI cache."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "make-prompt-better"


def install(base, *args, env=None):
    return subprocess.run(
        ["bash", str(ROOT / "install.sh"), "--project", "--runtime", "codex", *args],
        cwd=base, env=env, text=True, capture_output=True, timeout=30,
    )


def old_skill(path, marker="old"):
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text('---\nname: make-prompt-better\ndescription: "Old copy"\n---\n')
    (path / "keep.txt").write_text(marker)
    return path


def discovered(base):
    return sorted(str(f.parent.relative_to(base))
                  for folder in (".agents/skills", ".codex/skills")
                  for f in (base / folder).glob("*/SKILL.md")
                  if re.search(r"^name: make-prompt-better$", f.read_text(), re.M))


class SkillDiscoveryTests(unittest.TestCase):
    def test_six_entries_become_one_current_copy_with_recovery_outside_discovery(self):
        with tempfile.TemporaryDirectory(prefix="six skill entries ") as tmp:
            base = Path(tmp)
            for folder in (".agents/skills", ".codex/skills"):
                for suffix in ("", ".bak.one", ".bak.two"):
                    old_skill(base / folder / ("make-prompt-better" + suffix), folder + suffix)
            result = install(base)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(discovered(base), [".agents/skills/make-prompt-better"])
            self.assertEqual((base / discovered(base)[0] / "SKILL.md").read_bytes(), (SOURCE / "SKILL.md").read_bytes())
            backups = list((base / ".make-prompt-better/backups").glob("*/payload/keep.txt"))
            self.assertEqual(len(backups), 6)
            self.assertEqual(len({p.read_text() for p in backups}), 6)
            self.assertEqual(install(base, "--check").returncode, 0)
            self.assertEqual(install(base).returncode, 0)
            self.assertEqual(len(list((base / ".make-prompt-better/backups").glob("*/payload"))), 6)

    def test_check_and_dry_run_report_duplicates_without_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            old = old_skill(base / ".codex/skills/make-prompt-better.bak.one")
            checked = install(base, "--check")
            self.assertNotEqual(checked.returncode, 0)
            self.assertIn("Duplicate", checked.stdout)
            preview = install(base, "--dry-run")
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertIn(str(old), preview.stdout)
            self.assertTrue(old.is_dir())
            self.assertFalse((base / ".make-prompt-better").exists())
            self.assertFalse((base / ".agents").exists())

    def test_named_alias_is_removed_but_unrelated_skill_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            alias = old_skill(base / ".agents/skills/prompt-optimizer-old")
            other = base / ".agents/skills/make-prompt-better-unrelated"
            other.mkdir()
            (other / "SKILL.md").write_text("---\nname: another-skill\n---\n")
            self.assertEqual(install(base).returncode, 0)
            self.assertFalse(alias.exists())
            self.assertTrue((other / "SKILL.md").exists())

    def test_only_valid_frontmatter_identity_qualifies_for_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / ".agents/skills"
            for name in ('"make-prompt-better"', "'make-prompt-better'"):
                alias = old_skill(root / ("quoted-" + str(len(list(root.glob('*'))))))
                (alias / "SKILL.md").write_text('---\nname: ' + name + '\n---\n')
            malformed = old_skill(root / "malformed")
            (malformed / "SKILL.md").write_text('---\nname: "make-prompt-better\'\n---\n')
            body_only = old_skill(root / "body-only")
            (body_only / "SKILL.md").write_text('---\nname: another-skill\n---\nname: make-prompt-better\n')
            self.assertEqual(install(base).returncode, 0)
            self.assertEqual(list(root.glob("quoted-*")), [])
            self.assertTrue(malformed.exists())
            self.assertTrue(body_only.exists())

    def test_manual_recovery_restores_original_content_and_can_be_updated_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = old_skill(base / ".agents/skills/make-prompt-better", "user edits")
            self.assertEqual(install(base).returncode, 0)
            receipts = list((base / ".make-prompt-better/backups").glob("*/original-path.txt"))
            self.assertEqual(len(receipts), 1)
            original = Path(receipts[0].read_text().strip())
            self.assertEqual(original.resolve(), target.resolve())
            target.rename(base / "current-saved-outside-discovery")
            (receipts[0].parent / "payload").rename(original)
            self.assertEqual((target / "keep.txt").read_text(), "user edits")
            self.assertNotEqual(install(base, "--check").returncode, 0)
            self.assertEqual(install(base).returncode, 0)
            self.assertEqual(install(base, "--check").returncode, 0)

    def test_duplicate_symlink_is_removed_without_modifying_referent(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            external = old_skill(base / "external")
            alias = base / ".codex/skills/old-alias"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(external, target_is_directory=True)
            self.assertEqual(install(base).returncode, 0)
            self.assertFalse(alias.is_symlink())
            self.assertEqual((external / "keep.txt").read_text(), "old")
            self.assertTrue(any(p.is_symlink() for p in (base / ".make-prompt-better/backups").glob("*/payload")))

    def test_uninstall_removes_discoverable_backups_even_if_canonical_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            old_skill(base / ".agents/skills/make-prompt-better.bak.only")
            old_skill(base / ".codex/skills/make-prompt-better")
            result = install(base, "--uninstall")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(discovered(base), [])
            self.assertEqual(len(list((base / ".make-prompt-better/backups").glob("*/payload/keep.txt"))), 2)

    def test_failed_replacement_keeps_legacy_copy_discoverable(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            old = old_skill(base / ".codex/skills/make-prompt-better")
            fakebin = base / "fakebin"
            fakebin.mkdir()
            (fakebin / "cp").write_text("#!/bin/sh\nexit 23\n")
            (fakebin / "cp").chmod(0o755)
            env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ["PATH"])
            self.assertNotEqual(install(base, env=env).returncode, 0)
            self.assertTrue((old / "SKILL.md").exists())

    def test_symlinked_backup_root_is_refused_before_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            old = old_skill(base / ".agents/skills/make-prompt-better")
            external = base / "external"
            external.mkdir()
            (base / ".make-prompt-better").symlink_to(external, target_is_directory=True)
            self.assertNotEqual(install(base).returncode, 0)
            self.assertTrue((old / "keep.txt").exists())
            self.assertEqual(list(external.iterdir()), [])

    def test_legacy_installer_lock_prevents_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            old = old_skill(base / ".codex/skills/make-prompt-better")
            old.with_name(old.name + ".lock").mkdir()
            self.assertNotEqual(install(base).returncode, 0)
            self.assertTrue(old.is_dir())

    def test_bare_cli_shows_help_without_installing(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp)
            result = subprocess.run(["node", str(ROOT / "bin/cli.mjs")], env=env,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Usage:", result.stdout)
            self.assertEqual(list(Path(tmp).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
