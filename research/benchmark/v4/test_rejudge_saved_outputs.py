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
