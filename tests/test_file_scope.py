"""Runtime and review boundaries must retain functional inputs, not work artifacts."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FileScopeTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'scripts/file_scope.py'
        self.assertTrue(path.exists(), 'Explicit file scope policy is required')
        spec = importlib.util.spec_from_file_location('file_scope', path)
        self.scope = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.scope)

    def test_runtime_retains_functional_prompts_only(self):
        for path in ['bin/cli.mjs', 'install.sh', 'make-prompt-better/SKILL.md',
                     'make-prompt-better/references/domain-templates.md']:
            self.assertTrue(self.scope.included(path, 'runtime'), path)
        for path in ['docs/audit/report.md', 'docs/superpowers/plans/plan.md',
                     'research/benchmark/v4/results/metrics.json',
                     'make-prompt-better/references/experimental-prompt.md',
                     'bin/plan.md', '../bin/cli.mjs', '/bin/cli.mjs', 'bin/../bin/cli.mjs']:
            self.assertFalse(self.scope.included(path, 'runtime'), path)

    def test_review_retains_tests_and_ci_but_omits_generated_data(self):
        for path in ['tests/test_file_scope.py', '.github/workflows/validate-skill.yml',
                     'research/benchmark/v4/run_ollama_benchmarks.py',
                     'research/benchmark/v4/EVALUATION_PROMPT_V4.md',
                     'research/benchmark/v4/checkpoint-migration-hashes.json',
                     'make-prompt-better/references/examples.md']:
            self.assertTrue(self.scope.included(path, 'review'), path)
        for path in ['docs/clief/audits/security.md', 'research/benchmark/v4/EXECUTION_PLAN.md',
                     'research/benchmark/v4/results/model/artifacts/limiter_verified.py',
                     'tests/audits/report.py', 'PROMPT.md']:
            self.assertFalse(self.scope.included(path, 'review'), path)

    def test_tracked_symlink_is_rejected_and_untracked_file_is_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'bin').mkdir()
            (root / 'secret').write_text('SENTINEL')
            (root / 'bin/cli.mjs').symlink_to(root / 'secret')
            subprocess.run(['git', 'add', 'bin/cli.mjs'], cwd=root, check=True)
            with self.assertRaises(ValueError):
                self.scope.collect(root, 'review')
            (root / 'bin/cli.mjs').unlink()
            (root / 'bin/cli.mjs').write_text('real code')
            (root / 'scripts').mkdir()
            (root / 'scripts/untracked.py').write_text('SENTINEL')
            self.assertEqual(self.scope.collect(root, 'review'), ['bin/cli.mjs'])

    def test_actual_npm_inventory_obeys_scope(self):
        packed = subprocess.run(['npm', 'pack', '--dry-run', '--ignore-scripts', '--json'],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        files = json.loads(packed.stdout)[0]['files']
        unexpected = [f['path'] for f in files if not self.scope.included(f['path'], 'runtime')]
        self.assertEqual(unexpected, [])

    def test_codeql_walks_directories_and_excludes_unrelated_tracked_code(self):
        self.assertTrue(hasattr(self.scope, 'codeql_config'), 'CodeQL needs directory-rooted scope')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            for name in ('lint_context.py', 'tests/test_scope.py',
                         'research/benchmark/v4/results/model/example.py', 'docs/audit/code.js'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('fixture')
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            config = self.scope.codeql_config(root)
            for directory in config['paths']:
                self.assertTrue((root / directory).is_dir())
            self.assertIn('docs/audit/code.js', config['paths-ignore'])
            self.assertIn('research/benchmark/v4/results/model/example.py', config['paths-ignore'])
            self.assertNotIn('lint_context.py', config['paths-ignore'])
            self.assertNotIn('tests/test_scope.py', config['paths-ignore'])
