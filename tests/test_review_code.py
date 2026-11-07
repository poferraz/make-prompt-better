"""Review reports consume scoped source as data, never instructions or commands."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class ReviewTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'scripts/review_code.py'
        self.assertTrue(path.exists(), 'Scoped reviewer is required')
        spec = importlib.util.spec_from_file_location('review_code', path)
        self.review = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.review)

    def test_scope_budget_rotation_and_untrusted_sentinel(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            for path, content in {'bin/cli.mjs': 'x\n' * 1000,
                                  'install.sh': 'echo hello\n',
                                  'docs/audit/report.md': 'SECRET_SENTINEL'}.items():
                p = root / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            first = self.review.build_context(root, 512, 0)
            self.assertNotIn('SECRET_SENTINEL', first['context'])
            self.assertLessEqual(len(first['context']), 512)
            self.assertTrue(first['truncated_files'])
            second = self.review.build_context(root, 512, 1)
            self.assertEqual(second['files'][0]['path'], 'install.sh')

    def test_findings_are_grounded_deduplicated_and_never_executed(self):
        files = [{'path': 'install.sh', 'shown': ['echo hello'], 'sha256': 'a'*64}]
        item = {'path': 'install.sh', 'line': 1, 'severity': 'medium',
                'title': 'Unquoted input', 'evidence': 'echo hello',
                'verification': 'Inspect argument behavior; $(touch /tmp/should-not-run)'}
        report = self.review.validate_findings(json.dumps({'findings': [item, item]}), files)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]['fingerprint'],
                         self.review.validate_findings(json.dumps({'findings': [item]}), files)[0]['fingerprint'])
        for change in [{'path': 'docs/audit/report.md'}, {'line': 2}, {'line': True},
                       {'evidence': 'invented code'}, {'severity': 'critical'},
                       {'title': ''}, {'command': 'rm -rf /'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.review.validate_findings(json.dumps({'findings': [dict(item, **change)]}), files)

    def test_malformed_response_and_empty_findings(self):
        self.assertEqual(self.review.validate_findings('{"findings": []}', []), [])
        for raw in ['not json', '[]', '{"findings": "none"}', '{"findings": [], "execute": "echo x"}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.review.validate_findings(raw, [])

    def test_cli_inventory_is_explicitly_not_model_review(self):
        result = subprocess.run(['python3', str(ROOT / 'scripts/review_code.py'), '--dry-run'],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'model-review-skipped')
        self.assertIn('source_sha', data)
        self.assertNotIn('context', data)

    def test_model_call_is_bounded_and_produces_only_validated_advice(self):
        sys.path.insert(0, str(ROOT / 'research/benchmark/v4'))
        import run_ollama_benchmarks as runner
        response = {'content': '{"findings": []}', 'eval_count': 4}
        with patch.object(runner, 'call_ollama_chat', return_value=response) as call:
            findings, usage = self.review.model_review({'context': 'untrusted text', 'files': []},
                                                       'reviewer', 'http://localhost:11434', 2)
        self.assertEqual(findings, [])
        self.assertIsNone(usage['prompt_eval_count'])
        self.assertEqual(call.call_args.kwargs['max_retries'], 1)
        self.assertEqual(call.call_args.kwargs['options'], {'num_predict': 4096})
        with self.assertRaises(ValueError):
            self.review.model_review({'context': '', 'files': []}, 'reviewer', 'http://remote.invalid', 2)

    def test_failed_review_retains_status_without_provider_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'report.json'
            args = ['review_code.py', '--model', 'reviewer', '--output', str(output)]
            with patch.object(sys, 'argv', args), patch.object(self.review, 'model_review',
                     side_effect=RuntimeError('secret-provider-response')):
                self.assertEqual(self.review.main(), 1)
            report = json.loads(output.read_text())
            self.assertEqual(report['status'], 'model-review-failed')
            self.assertNotIn('secret-provider-response', output.read_text())

    def test_existing_output_is_rejected_before_spending_a_model_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'report.json'
            output.write_text('KEEP ORIGINAL')
            args = ['review_code.py', '--model', 'reviewer', '--output', str(output)]
            with patch.object(sys, 'argv', args), patch.object(self.review, 'model_review',
                     return_value=([], {})) as call:
                with self.assertRaises(FileExistsError):
                    self.review.main()
                self.assertEqual(call.call_count, 0)
            self.assertEqual(output.read_text(), 'KEEP ORIGINAL')

    def test_workflow_never_exposes_inference_key_on_pull_requests(self):
        text = (ROOT / '.github/workflows/continuous-review.yml').read_text()
        self.assertNotIn('pull_request_target', text)
        static, model = text.split('  model-review:', 1)
        self.assertNotIn('secrets.', static)
        self.assertIn("github.event_name != 'pull_request'", model)
        self.assertIn("github.ref == 'refs/heads/main'", model)
        self.assertIn("vars.MODEL_REVIEW_ENABLED == 'true'", model)
        self.assertNotIn('contents: write', text)
        self.assertNotIn('pull-requests: write', text)
