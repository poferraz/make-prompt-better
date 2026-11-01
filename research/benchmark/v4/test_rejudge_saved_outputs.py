import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import rejudge_saved_outputs as rejudge


class SavedPairsTests(unittest.TestCase):
    def test_missing_empty_and_filtered_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(rejudge.load_saved_pairs(root / 'missing'), [])
            model = root / 'example'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'baseline': {'content': 'base'}, 'optimized_response': {'content': 'opt'}},
                '2': {'baseline': {'content': 'base'}, 'optimized_response': {'content': ''}},
            }}))
            pairs = rejudge.load_saved_pairs(root)
            self.assertEqual([(p['test_id'], p['baseline_text'], p['optimized_text']) for p in pairs], [(1, 'base', 'opt')])
            self.assertEqual(rejudge.load_saved_pairs(root, ['other']), [])
            self.assertEqual(rejudge.load_saved_pairs(root, test_filter=[2]), [])
            self.assertEqual(len(rejudge.load_saved_pairs(root, ['example'], [1])), 1)
            with mock.patch.object(rejudge, 'call_ollama_chat', side_effect=AssertionError('network called')):
                self.assertEqual(rejudge.main(['--results-dir', str(root), '--dry-run', '--seed', '17']), 0)

    def test_malformed_json_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text('{')
            with self.assertRaises(json.JSONDecodeError):
                rejudge.load_saved_pairs(Path(tmp))

    def test_judge_seed_and_swapped_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'baseline': {'content': 'BASE_TEXT'}, 'optimized_response': {'content': 'OPT_TEXT'}}
            }}))
            calls = []
            def judge(**kwargs):
                calls.append(kwargs)
                prompt = kwargs['messages'][0]['content']
                # Score by response identity, independently of position.
                a_is_base = prompt.index('BASE_TEXT') < prompt.index('OPT_TEXT')
                left, right = (3, 5) if a_is_base else (5, 3)
                rows = '\n'.join(f'| {name} | {left} | {right} |' for name in
                                 ['Accuracy', 'Completeness', 'Structure', 'Actionability', 'Traceability'])
                return {'content': rows}
            with mock.patch.object(rejudge, 'call_ollama_chat', side_effect=judge), \
                 mock.patch.object(rejudge, 'compute_stratified_benchmark_summary', return_value={}) as summary:
                self.assertEqual(rejudge.main(['--results-dir', tmp, '--swap-positions', '--seed', '17', '--judge-model', 'fake']), 0)
            self.assertEqual(len(calls), 2)
            self.assertEqual([c['seed'] for c in calls], [17, 17])
            self.assertEqual([c['model'] for c in calls], ['fake', 'fake'])
            record = summary.call_args.args[0][0]
            self.assertEqual((record['baseline_total'], record['optimized_total'], record['delta_total']), (15, 25, 10))
            self.assertTrue(record['position_swap_consistent'])
            self.assertEqual(summary.call_args.kwargs['seed'], 17)
