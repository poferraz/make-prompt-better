import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


class RoutingTests(unittest.TestCase):
    def setUp(self):
        path = HERE / 'evaluate_routing.py'
        self.assertTrue(path.exists(), 'Routing experiment is required')
        spec = importlib.util.spec_from_file_location('evaluate_routing', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_metrics_keep_invalid_decisions_visible_and_all_negative_defined(self):
        rows = [{'expected': 'make-prompt-better', 'selected': 'make-prompt-better'},
                {'expected': 'code-review', 'selected': 'make-prompt-better'},
                {'expected': 'none', 'selected': None}]
        metrics = self.module.summarize(rows)
        self.assertEqual(metrics['target_recall'], 1)
        self.assertEqual(metrics['false_positive_rate'], .5)
        self.assertEqual(metrics['invalid'], 1)
        self.assertAlmostEqual(metrics['accuracy'], 1/3)
        self.assertIsNone(self.module.summarize(rows[1:])['target_recall'])

    def test_current_and_candidate_share_cases_seeds_and_fixed_neighbor_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'routing.json'
            calls = []
            def fake(model, messages, **kwargs):
                calls.append((messages, kwargs['seed']))
                return {'content': '{"selected":"make-prompt-better"}', 'eval_count': 2}
            args = ['--model', 'fixture', '--seeds', '42,43', '--split', 'development',
                    '--max-requests', '24', '--output', str(output)]
            with patch.object(self.module.runner, 'call_ollama_chat', side_effect=fake):
                self.assertEqual(self.module.main(args), 0)
            report = json.loads(output.read_text())
            self.assertEqual(len(calls), 24)
            self.assertEqual(len(report['rows']), 24)
            self.assertEqual({r['variant'] for r in report['rows']}, {'current', 'candidate'})
            self.assertEqual(len(report['corpus_sha256']), 64)
            self.assertEqual(len(report['library_sha256']), 64)
            pairs = {(r['case_id'], r['seed']) for r in report['rows'] if r['variant'] == 'current'}
            self.assertEqual(len(pairs), 12)

    def test_budget_and_dry_run_send_nothing_and_write_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'output.json'
            with patch.object(self.module.runner, 'call_ollama_chat') as call:
                self.assertEqual(self.module.main(['--model', 'fixture', '--max-requests', '1', '--output', str(output)]), 1)
                self.assertEqual(self.module.main(['--model', 'fixture', '--dry-run', '--output', str(output)]), 0)
                call.assert_not_called()
                self.assertFalse(output.exists())

    def test_invalid_model_output_is_an_observation_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'output.json'
            with patch.object(self.module.runner, 'call_ollama_chat', return_value={'content': 'garbage'}):
                self.assertEqual(self.module.main(['--model', 'fixture', '--seeds', '42', '--output', str(output)]), 1)
            report = json.loads(output.read_text())
            self.assertEqual(report['summary']['candidate']['invalid'], 12)
