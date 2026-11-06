import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import rejudge_saved_outputs as rejudge


class SavedPairsTests(unittest.TestCase):
    def test_malformed_second_pass_is_retained_and_retried_on_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = root / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'raw_prompt': 'task', 'baseline': {'content': 'base'}, 'optimized_response': {'content': 'opt'}}
            }}))
            rows = '\n'.join(f'| {name} | 3 | 5 |' for name in
                             ['Accuracy', 'Completeness', 'Structure', 'Actionability', 'Traceability'])
            output = root / 'rejudge.json'
            args = ['--results-dir', tmp, '--output', str(output), '--swap-positions']
            with mock.patch.object(rejudge, 'call_ollama_chat', side_effect=[{'content': rows}, {'content': 'bad score'}]):
                self.assertNotEqual(rejudge.main(args), 0)
            state = json.loads(output.read_text())
            before = state['pairs']['model:1']
            valid_first = before['passes'][0]
            self.assertEqual(before['failed_passes'][0]['response']['content'], 'bad score')
            old = before.pop('failed_passes')[0]
            old.pop('index')
            old.pop('error')
            before['passes'].append(old)
            old_manifest = dict(state['manifest'],
                                runner_sha256='79d5ea515b51233080ef7be05ee431c3a3ff837117682c1e80e075969018b635',
                                code_sha256='9e0ea1aa46922f92f2c85204df45c8ab81fc32e75f7e34ad01c684679275bcea')
            state['manifest'] = old_manifest
            output.write_text(json.dumps(state))
            with mock.patch.object(rejudge, 'call_ollama_chat', side_effect=AssertionError('network used')):
                self.assertNotEqual(rejudge.main(args + ['--seed', '18']), 0)
            self.assertEqual(json.loads(output.read_text())['manifest'], old_manifest)
            read_bytes = Path.read_bytes
            def altered_source(path):
                data = read_bytes(path)
                return data + b'changed' if path == Path(rejudge.__file__) else data
            with mock.patch.object(Path, 'read_bytes', altered_source), \
                 mock.patch.object(rejudge, 'call_ollama_chat', side_effect=AssertionError('network used')):
                self.assertNotEqual(rejudge.main(args), 0)
            self.assertEqual(json.loads(output.read_text())['manifest'], old_manifest)
            with mock.patch.object(rejudge, 'call_ollama_chat', return_value={'content': rows}) as chat:
                self.assertEqual(rejudge.main(args), 0)
            self.assertEqual(chat.call_count, 1)
            state = json.loads(output.read_text())
            self.assertIn(old_manifest, state['previous_manifests'])
            after = state['pairs']['model:1']
            self.assertEqual(after['passes'][0], valid_first)
            self.assertEqual(after['failed_passes'][0]['response']['content'], 'bad score')

    def test_empty_live_rejudge_is_not_reported_as_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertNotEqual(rejudge.main(['--results-dir', tmp, '--output', str(Path(tmp) / 'out.json')]), 0)

    def test_invalid_test_filter_is_reported_without_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                result = rejudge.main(['--results-dir', tmp, '--tests', 'not-a-number', '--dry-run'])
            except Exception as exc:
                self.fail(f'Invalid filter raised an exception: {exc}')
            self.assertNotEqual(result, 0)

    def test_request_limit_is_checked_during_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'raw_prompt': 'task', 'baseline': {'content': 'base'}, 'optimized_response': {'content': 'opt'}}
            }}))
            args = ['--results-dir', tmp, '--swap-positions', '--dry-run', '--max-requests', '1']
            try:
                result = rejudge.main(args)
            except SystemExit as exc:
                self.fail(f'Request limit option was rejected: {exc}')
            self.assertNotEqual(result, 0)
    def test_saved_prompt_takes_precedence_over_current_test_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'raw_prompt': 'historic task', 'domain': 'old domain',
                      'baseline': {'content': 'base'}, 'optimized_response': {'content': 'opt'}}
            }}))
            pair = rejudge.load_saved_pairs(Path(tmp))[0]
            self.assertEqual(pair['tc']['raw_prompt'], 'historic task')
            self.assertEqual(pair['tc']['domain'], 'old domain')

    def test_rejudge_requires_durable_output_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'baseline': {'content': 'base'}, 'optimized_response': {'content': 'opt'}}
            }}))
            with mock.patch.object(rejudge, 'call_ollama_chat', return_value={'content': ''}) as chat:
                try:
                    result = rejudge.main(['--results-dir', tmp])
                except Exception as exc:
                    self.fail(f'Rejudge attempted work without an output path: {exc}')
                self.assertNotEqual(result, 0)
                chat.assert_not_called()

    def test_remote_http_rejudge_is_rejected_before_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'baseline': {'content': 'base'}, 'optimized_response': {'content': 'opt'}}
            }}))
            with mock.patch.object(rejudge, 'call_ollama_chat', return_value={'content': ''}) as chat:
                try:
                    result = rejudge.main(['--results-dir', tmp, '--output', str(Path(tmp) / 'out.json'),
                                           '--host', 'http://example.com'])
                except Exception as exc:
                    self.fail(f'Remote HTTP was not rejected before judging: {exc}')
                self.assertNotEqual(result, 0)
                chat.assert_not_called()

    def test_missing_saved_task_cannot_be_silently_rejudged(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'baseline': {'content': 'base'}, 'optimized_response': {'content': 'opt'}}
            }}))
            with mock.patch.object(rejudge, 'call_ollama_chat', return_value={'content': ''}) as chat:
                self.assertNotEqual(rejudge.main(['--results-dir', tmp, '--output', str(Path(tmp) / 'out.json')]), 0)
                chat.assert_not_called()

    def test_rejudge_resumes_completed_first_pass_and_rejects_changed_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = root / 'model'
            model.mkdir()
            (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
                '1': {'raw_prompt': 'saved task', 'baseline': {'content': 'BASE_TEXT'}, 'optimized_response': {'content': 'OPT_TEXT'}}
            }}))
            output = root / 'rejudge.json'
            rows = '\n'.join(f'| {name} | 3 | 5 |' for name in
                             ['Accuracy', 'Completeness', 'Structure', 'Actionability', 'Traceability'])
            args = ['--results-dir', tmp, '--swap-positions', '--seed', '17', '--output', str(output)]
            with mock.patch.object(rejudge, 'call_ollama_chat', side_effect=[{'content': rows}, RuntimeError('interrupted')]):
                try:
                    first = rejudge.main(args)
                except SystemExit as exc:
                    self.fail(f'Rejudge output option was rejected: {exc}')
                self.assertNotEqual(first, 0)
            saved = json.loads(output.read_text())
            self.assertEqual(len(saved['pairs']['model:1']['passes']), 1)
            with mock.patch.object(rejudge, 'call_ollama_chat', return_value={'content': rows}) as chat:
                self.assertEqual(rejudge.main(args), 0)
                self.assertEqual(chat.call_count, 1)
            final = json.loads(output.read_text())
            self.assertEqual(len(final['pairs']['model:1']['passes']), 2)
            original = output.read_bytes()
            with mock.patch.object(rejudge, 'call_ollama_chat', side_effect=AssertionError('network')):
                self.assertNotEqual(rejudge.main(args + ['--seed', '18']), 0)
            self.assertEqual(output.read_bytes(), original)

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
                '1': {'raw_prompt': 'saved task', 'baseline': {'content': 'BASE_TEXT'}, 'optimized_response': {'content': 'OPT_TEXT'}}
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
                self.assertEqual(rejudge.main(['--results-dir', tmp, '--swap-positions', '--seed', '17', '--judge-model', 'fake', '--output', str(Path(tmp) / 'out.json')]), 0)
            self.assertEqual(len(calls), 2)
            self.assertEqual([c['seed'] for c in calls], [17, 17])
            self.assertEqual([c['model'] for c in calls], ['fake', 'fake'])
            record = summary.call_args.args[0][0]
            self.assertEqual((record['baseline_total'], record['optimized_total'], record['delta_total']), (15, 25, 10))
            self.assertTrue(record['position_swap_consistent'])
            self.assertEqual(summary.call_args.kwargs['seed'], 17)
