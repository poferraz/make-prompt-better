import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import rejudge_saved_outputs as rejudge


class RejudgeConnectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        model = self.root / 'model'
        model.mkdir()
        (model / 'metrics.json').write_text(json.dumps({'model': 'model', 'tests': {
            '1': {'raw_prompt': 'saved task', 'baseline': {'content': 'base'},
                  'optimized_response': {'content': 'opt'}}
        }}))
        self.output = self.root / 'derived' / 'rejudge.json'
        self.args = ['--results-dir', str(self.root), '--judge-model', 'fixture-judge',
                     '--output', str(self.output)]
        rows = '\n'.join(f'| {name} | 3 | 5 |' for name in
                         ['Accuracy', 'Completeness', 'Structure', 'Actionability', 'Traceability'])
        self.response = {'content': rows, 'raw_content': rows, 'words': len(rows.split()),
                         'prompt_eval_count': 10, 'eval_count': 20, 'elapsed_seconds': 0,
                         'telemetry': {'attempt_count': 1, 'retry_count': 0, 'attempts': [
                             {'status': 'success', 'prompt_eval_count': 10, 'eval_count': 20}]}}
        self.api_key = 'dummy-rejudge-api-key-for-offline-test'

    def run_main(self, environment, arguments=None, side_effect=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, environment, clear=True), \
                mock.patch.object(rejudge, 'call_ollama_chat', return_value=self.response,
                                  side_effect=side_effect) as chat, \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = rejudge.main(self.args if arguments is None else arguments)
        return result, chat, stdout.getvalue() + stderr.getvalue()

    def test_environment_host_and_key_reach_both_swapped_passes_without_serialization(self):
        host = 'https://ollama.com'
        result, chat, printed = self.run_main(
            {'OLLAMA_HOST': host, 'OLLAMA_API_KEY': self.api_key}, self.args + ['--swap-positions'])
        self.assertEqual(result, 0)
        self.assertEqual(chat.call_count, 2)
        for call in chat.call_args_list:
            self.assertEqual(call.kwargs['host'], host)
            self.assertTrue(call.kwargs.get('api_key') == self.api_key, 'API key was not forwarded')
        checkpoint = self.output.read_text()
        state = json.loads(checkpoint)
        self.assertEqual(len(state['pairs']['model:1']['passes']), 2)
        self.assertEqual(state['manifest']['host_sha256'], hashlib.sha256(host.encode()).hexdigest())
        self.assertNotIn('api_key', state['manifest'])
        self.assertNotIn(self.api_key, checkpoint + printed)

    def test_explicit_host_wins_and_rotated_key_resumes_only_missing_pass(self):
        host = 'http://127.0.0.1:11434'
        args = self.args + ['--host', host, '--swap-positions']
        environment = {'OLLAMA_HOST': 'https://ollama.com', 'OLLAMA_API_KEY': self.api_key}
        result, first, printed = self.run_main(environment, args,
                                              [self.response, RuntimeError('interrupted')])
        self.assertNotEqual(result, 0)
        self.assertEqual(first.call_count, 2)
        for call in first.call_args_list:
            self.assertEqual(call.kwargs['host'], host)
            self.assertTrue(call.kwargs.get('api_key') == self.api_key, 'Initial API key was not forwarded')
        saved = json.loads(self.output.read_text())
        self.assertEqual(len(saved['pairs']['model:1']['passes']), 1)
        rotated_key = 'dummy-rejudge-rotated-api-key-for-offline-test'
        result, resumed, resumed_printed = self.run_main(
            {'OLLAMA_HOST': 'https://different.invalid', 'OLLAMA_API_KEY': rotated_key}, args)
        self.assertEqual(result, 0)
        self.assertEqual(resumed.call_count, 1)
        self.assertEqual(resumed.call_args.kwargs['host'], host)
        self.assertTrue(resumed.call_args.kwargs.get('api_key') == rotated_key,
                        'Rotated API key was not forwarded to missing pass')
        checkpoint = self.output.read_text()
        state = json.loads(checkpoint)
        self.assertEqual(state['manifest'], saved['manifest'])
        self.assertEqual(len(state['pairs']['model:1']['passes']), 2)
        for key in (self.api_key, rotated_key):
            self.assertNotIn(key, checkpoint + printed + resumed_printed)

    def test_host_environment_is_resolved_for_each_invocation(self):
        for index, host in enumerate(('https://first.invalid', 'https://second.invalid')):
            output = self.root / f'output-{index}.json'
            args = self.args[:-2] + ['--output', str(output)]
            result, chat, _ = self.run_main({'OLLAMA_HOST': host}, args)
            self.assertEqual(result, 0)
            self.assertEqual(chat.call_args.kwargs['host'], host)
            self.assertEqual(json.loads(output.read_text())['manifest']['host_sha256'],
                             hashlib.sha256(host.encode()).hexdigest())

    def test_local_default_without_key_remains_usable(self):
        result, chat, _ = self.run_main({})
        self.assertEqual(result, 0)
        self.assertEqual(chat.call_args.kwargs['host'], 'http://localhost:11434')
        self.assertIsNone(chat.call_args.kwargs.get('api_key'))
        self.assertEqual(len(json.loads(self.output.read_text())['pairs']['model:1']['passes']), 1)

    def test_changed_environment_host_rejects_checkpoint_without_new_calls(self):
        result, _, _ = self.run_main({'OLLAMA_HOST': 'https://first.invalid'})
        self.assertEqual(result, 0)
        checkpoint = self.output.read_bytes()
        result, chat, _ = self.run_main({'OLLAMA_HOST': 'https://second.invalid'})
        self.assertNotEqual(result, 0)
        chat.assert_not_called()
        self.assertEqual(self.output.read_bytes(), checkpoint)

    def test_direct_cloud_dry_run_makes_no_calls_or_output(self):
        before = {str(p.relative_to(self.root)) for p in self.root.rglob('*')}
        for api_key in (self.api_key, None):
            with self.subTest(authenticated=api_key is not None):
                environment = {'OLLAMA_HOST': 'https://ollama.com'}
                if api_key is not None:
                    environment['OLLAMA_API_KEY'] = api_key
                result, chat, printed = self.run_main(
                    environment, self.args + ['--dry-run', '--swap-positions'])
                self.assertEqual(result, 0)
                chat.assert_not_called()
                self.assertEqual({str(p.relative_to(self.root)) for p in self.root.rglob('*')}, before)
                self.assertNotIn(self.api_key, printed)

    def test_environment_cleartext_remote_host_is_rejected_before_output_or_request(self):
        result, chat, printed = self.run_main(
            {'OLLAMA_HOST': 'http://provider.invalid:11434', 'OLLAMA_API_KEY': self.api_key})
        self.assertNotEqual(result, 0)
        chat.assert_not_called()
        self.assertFalse(self.output.parent.exists())
        self.assertNotIn(self.api_key, printed)

    def test_direct_cloud_local_model_alias_is_rejected_before_output_or_request(self):
        args = self.args + ['--host', 'https://ollama.com', '--judge-model', 'fixture-judge:cloud']
        result, chat, printed = self.run_main({'OLLAMA_API_KEY': self.api_key}, args)
        self.assertNotEqual(result, 0)
        chat.assert_not_called()
        self.assertFalse(self.output.parent.exists())
        self.assertNotIn(self.api_key, printed)


class SavedPairsTests(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop('OLLAMA_HOST', None)
        os.environ.pop('OLLAMA_API_KEY', None)

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
            # Simulate approval of this successor without modifying the historical audit hashes.
            with mock.patch.object(rejudge, 'migration_code_is_approved', return_value=True), \
                 mock.patch.object(rejudge, 'call_ollama_chat', return_value={'content': rows}) as chat:
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
