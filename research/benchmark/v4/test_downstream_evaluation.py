"""Offline five-arm protocol tests, including a real loopback HTTP pipeline."""
import contextlib
import copy
import io
import json
import os
import sys
from pathlib import Path
import tempfile
import subprocess
import threading
import unittest
from unittest import mock
from http.server import ThreadingHTTPServer
from test_http_service import FakeOllama

try:
    import downstream_evaluation as evaluation
except ImportError:
    evaluation = None

import run_ollama_benchmarks as runner
if evaluation is not None:
    runner = evaluation.runner


class DownstreamTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(evaluation, 'The five-arm downstream evaluator must exist')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.argv = ['--models', 'executor', '--judge-model', 'independent-judge',
                     '--seeds', '41,42', '--tasks', 'ALL', '--max-requests', '10000',
                     '--deadline-seconds', '60', '--max-output-tokens', '128',
                     '--candidate-skill-dir', str(runner.REPO_ROOT / 'make-prompt-better'),
                     '--output-dir', str(self.root / 'run')]

    def args(self, *extra):
        return evaluation.parser().parse_args(self.argv + list(extra))

    def manifest(self, *extra):
        return evaluation.build_manifest(self.args(*extra))

    def test_manifest_has_five_arms_and_provenance_without_private_dependencies(self):
        manifest = self.manifest()
        self.assertEqual(manifest['arms'], ['original', 'minimal_clarity', 'strong_direct', 'stable', 'candidate'])
        self.assertEqual(manifest['calls_per_cell'], 27)
        self.assertEqual(manifest['required_request_allowance'], len(manifest['cases']) * 2 * 27)
        self.assertEqual(manifest['skills']['stable']['bundle_sha256'], manifest['skills']['candidate']['bundle_sha256'])
        self.assertEqual(manifest['corpus']['split'], 'development')
        self.assertIn('downstream_evaluation.py', manifest['source_sha256'])
        self.assertNotIn('api_key', json.dumps(manifest))

    def test_v3_manifest_binds_contracts_and_new_source(self):
        manifest = self.manifest()
        self.assertEqual((manifest['schema'], manifest['protocol']), (3, 'five-arm-downstream-v3'))
        self.assertEqual(manifest['contracts'], {'judge_parser': 'markdown-dimensions-v2',
            'preparation': 'json-decision-v2', 'judge_rubric': 'downstream-contract-v1',
            'response_metadata': 'terminal-v1', 'summary': 'availability-v1'})
        self.assertIn('downstream_protocol.py', manifest['source_sha256'])

    def test_v2_campaign_cannot_resume_under_v3(self):
        args = self.args()
        manifest = self.manifest()
        args.output_dir.mkdir()
        old = dict(manifest, schema=2, protocol='five-arm-downstream-v2')
        (args.output_dir / 'manifest.json').write_text(json.dumps(old))
        (args.output_dir / 'state.json').write_text('{"stop_reason":"unknown_usage"}')
        before = {p.name: p.read_bytes() for p in args.output_dir.iterdir()}
        with mock.patch.object(evaluation.subprocess, 'run', side_effect=AssertionError('worker started')):
            with self.assertRaisesRegex(ValueError, 'Manifest mismatch'):
                evaluation.run_campaign(args, manifest, self.argv)
        self.assertEqual(before, {p.name: p.read_bytes() for p in args.output_dir.iterdir()})

    def test_preparation_wrapper_preserves_language_and_avoids_solving(self):
        system = evaluation.preparation_messages('SKILL', 'A task')[0]['content'].lower()
        self.assertIn('instruction language', system)
        self.assertIn('answer language', system)
        self.assertIn('newly computed answer', system)

    def test_judge_mapping_saved_before_dispatch(self):
        manifest = self.manifest()
        cell = next(evaluation.cells(manifest))
        path = self.root / 'mapping.json'
        seen = []
        def chat(**kwargs):
            if kwargs['model'] == 'independent-judge':
                entry = json.loads(path.read_text())['calls'][-1]
                seen.append((entry['judge_pair'], entry['judge_pass_index'], entry['judge_mapping']))
            return self.fake_chat(**kwargs)
        with mock.patch.object(runner, 'call_ollama_chat', side_effect=chat):
            result = evaluation.run_cell(manifest, cell, path, 'http://localhost:11434')
        self.assertEqual(result['status'], 'completed')
        self.assertEqual([x[1] for x in seen[:2]], [1, 2])
        self.assertEqual(seen[0][2]['A'], seen[1][2]['B'])
        self.assertEqual(len(seen), 20)
        self.assertTrue(all('parsed_scores' in c for c in result['calls'] if c['stage'] == 'judge'))

    def test_default_is_a_read_only_plan(self):
        with mock.patch.object(runner, 'call_ollama_chat') as chat, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(evaluation.main(self.argv), 0)
        chat.assert_not_called()
        self.assertFalse((self.root / 'run').exists())

    def test_independent_judge_unique_models_and_seeds_required(self):
        for extra in [('--judge-model', 'executor'), ('--models', 'a,a'), ('--seeds', '1,1'),
                      ('--models', '../x'), ('--max-requests', '1'), ('--deadline-seconds', 'nan'),
                      ('--max-attempts', '0'), ('--max-input-chars', '1'), ('--tasks', 'missing')]:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.manifest(*extra)

    def test_cells_preserve_task_model_seed_and_counterbalance_every_arm(self):
        manifest = self.manifest()
        cells = list(evaluation.cells(manifest))
        self.assertEqual(len(cells), len(manifest['cases']) * 2)
        self.assertEqual(len({(c['task_id'], c['model'], c['seed']) for c in cells}), len(cells))
        orders = [evaluation.arm_order(i) for i in range(10)]
        for arm in manifest['arms']:
            for position in range(5):
                self.assertEqual(sum(order[position] == arm for order in orders), 2)

    def test_preparation_contract_makes_bypass_measurable(self):
        self.assertEqual(evaluation.parse_preparation('{"decision":"bypass"}', 'original'),
                         {'decision': 'bypass', 'prompt': 'original', 'unchanged': True})
        self.assertEqual(evaluation.parse_preparation('{"decision":"rewrite","prompt":"new"}', 'original')['prompt'], 'new')
        for text in ['answer', '{"decision":"bypass","prompt":"changed"}',
                     '{"decision":"rewrite","prompt":""}', '{"decision":"execute"}', '[]']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                evaluation.parse_preparation(text, 'original')

    def test_usage_unknown_is_not_zero_and_pending_calls_remain_unknown(self):
        data = {'calls': [
            {'stage': 'execution', 'arm': 'original', 'status': 'completed',
             'response': {'telemetry': {'attempt_count': 1, 'retry_count': 0, 'total_elapsed_seconds': .1,
                                      'attempts': [{'status': 'success', 'prompt_eval_count': 7, 'eval_count': None}]}}},
            {'stage': 'preparation', 'arm': 'stable', 'status': 'running', 'reserved_attempts': 2},
        ]}
        usage = evaluation.summarize_usage([data])
        self.assertIsNone(usage['execution']['eval_count'])
        self.assertEqual(usage['execution']['known_prompt_eval_count'], 7)
        self.assertIsNone(usage['preparation']['attempt_count'])
        self.assertIsNone(usage['preparation']['prompt_eval_count'])
        self.assertEqual(usage['judge']['attempt_count'], 0)

    def test_holdout_requires_private_location_and_matching_seal(self):
        from downstream_corpus import load_corpus
        corpus = load_corpus()
        corpus['split'] = 'holdout'
        path = self.root / 'holdout.json'
        path.write_text(json.dumps(corpus))
        with self.assertRaisesRegex(ValueError, 'private'):
            self.manifest('--corpus', str(path))
        path = self.root / '.private' / 'holdout.json'
        path.parent.mkdir()
        path.write_text(json.dumps(corpus))
        with self.assertRaisesRegex(ValueError, 'seal'):
            self.manifest('--corpus', str(path))
        digest = runner.sha256_text(path.read_text())
        manifest = self.manifest('--corpus', str(path), '--holdout-sha256', digest)
        self.assertEqual(manifest['corpus']['sha256'], digest)

    def fake_chat(self, **kwargs):
        messages = kwargs['messages']
        if messages[0]['content'].startswith('Prepare a prompt'):
            text = '{"decision":"bypass"}'
        elif messages[0]['content'].startswith('You are an independent'):
            text = '| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence |\n' + \
                '\n'.join(f'| {d} | 3 | 4 | 1 | evidence |' for d in
                          ['Accuracy', 'Completeness', 'Structure', 'Actionability', 'Traceability'])
        else:
            text = '42'
        return {'content': text, 'words': len(text.split()), 'prompt_eval_count': 10, 'eval_count': 5,
                'telemetry': {'attempt_count': 1, 'retry_count': 0, 'total_elapsed_seconds': .01,
                              'attempts': [{'status': 'success', 'prompt_eval_count': 10, 'eval_count': 5}]}}

    def run_cell(self, chat=None):
        manifest = self.manifest()
        cell = next(evaluation.cells(manifest))
        path = self.root / 'cell.json'
        with mock.patch.object(runner, 'call_ollama_chat', side_effect=chat or self.fake_chat) as calls:
            result = evaluation.run_cell(manifest, cell, path, 'http://localhost:11434')
        return manifest, cell, result, calls

    def test_full_cell_uses_clean_execution_and_blinded_swapped_judges(self):
        manifest, cell, data, calls = self.run_cell()
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(len(data['arms']), 5)
        self.assertEqual(len(data['comparisons']), 10)
        self.assertEqual(calls.call_count, 27)
        self.assertTrue(all(c.kwargs['seed'] == cell['seed'] for c in calls.call_args_list))
        self.assertEqual(data['arms']['stable']['decision'], 'bypass')
        self.assertEqual(data['arms']['stable']['prompt'], manifest['cases'][0]['original_request'])
        for call in calls.call_args_list:
            self.assertEqual(call.kwargs['max_retries'], 1)
            if call.kwargs['model'] == 'independent-judge':
                self.assertEqual(call.kwargs['messages'][0]['role'], 'system')
                self.assertNotIn('stable', call.kwargs['messages'][-1]['content'])
        for comparison in data['comparisons'].values():
            self.assertEqual(comparison['delta'], 0)
            self.assertFalse(comparison['position_consistent'])
            self.assertEqual(comparison['passes'][0]['mapping']['A'], comparison['passes'][1]['mapping']['B'])

    def test_invalid_optimizer_retains_usage_and_other_arms(self):
        def chat(**kwargs):
            result = self.fake_chat(**kwargs)
            if kwargs['messages'][0]['content'].startswith('Prepare a prompt'):
                result['content'] = 'invalid JSON'
            return result
        manifest, cell, data, calls = self.run_cell(chat)
        self.assertEqual(data['status'], 'failed')
        self.assertEqual(len(data['arms']), 3)
        self.assertEqual(len(data['comparisons']), 3)
        self.assertEqual(evaluation.summarize_usage([data])['preparation']['known_eval_count'], 10)
        self.assertEqual(len(data['failures']), 2)
        summary = evaluation.summarize(manifest, {'cells': {str(cell['index']): {'status': 'failed'}}}, [data])
        self.assertTrue(summary['missing_pairs'])
        self.assertEqual(summary['completed_cells'], 0)

    def test_invalid_judge_keeps_raw_response_and_missing_pair(self):
        def chat(**kwargs):
            result = self.fake_chat(**kwargs)
            if kwargs['model'] == 'independent-judge':
                result['content'] = '| TOTAL | 20 | 25 |'
            return result
        _, _, data, _ = self.run_cell(chat)
        self.assertEqual(data['status'], 'failed')
        self.assertFalse(data['comparisons'])
        self.assertTrue(any(c.get('response', {}).get('content', '').startswith('| TOTAL') for c in data['calls']))
        self.assertEqual(evaluation.summarize_usage([data])['judge']['known_eval_count'], 100)

    def test_network_failure_keeps_unknown_attempts(self):
        def chat(**kwargs):
            if kwargs['model'] == 'independent-judge':
                raise TimeoutError('private body must not be recorded in errors')
            return self.fake_chat(**kwargs)
        _, _, data, _ = self.run_cell(chat)
        usage = evaluation.summarize_usage([data])
        self.assertIsNone(usage['judge']['attempt_count'])
        self.assertIsNone(usage['judge']['eval_count'])
        self.assertNotIn('private body', json.dumps(data))

    def test_identical_rewrite_and_declared_bypass_are_distinct(self):
        parsed = evaluation.parse_preparation('{"decision":"rewrite","prompt":"same"}', 'same')
        self.assertEqual(parsed['decision'], 'rewrite')
        self.assertTrue(parsed['unchanged'])

    def test_summary_reports_paired_deltas_and_bypass_denominators(self):
        manifest, cell, data, _ = self.run_cell()
        summary = evaluation.summarize(manifest, {'cells': {str(cell['index']): {'status': 'completed'}}}, [data])
        self.assertEqual(summary['completed_cells'], 1)
        self.assertEqual(summary['bypass']['stable']['bypass_count'], 1)
        self.assertEqual(summary['bypass']['stable']['attempted'], 1)
        self.assertEqual(summary['pair_summaries']['original__stable']['mean_delta'], 0)
        self.assertEqual(summary['pair_summaries']['original__stable']['task_clusters'], 1)
        self.assertIsNone(summary['pair_summaries']['original__stable']['task_cluster_95_ci'])
        self.assertTrue(summary['missing_pairs'])

    def test_launched_cell_without_record_never_reports_zero_usage(self):
        manifest = self.manifest()
        state = {'cells': {'0': {'status': 'failed', 'error': 'DeadlineExceeded'}},
                 'reserved_request_allowance': 27}
        summary = evaluation.summarize(manifest, state, [])
        self.assertTrue(summary['telemetry_incomplete'])
        self.assertIsNone(summary['stage_usage']['execution']['eval_count'])
        self.assertIsNone(summary['stage_usage']['preparation']['attempt_count'])
        self.assertEqual(summary['stage_usage']['execution']['known_eval_count'], 0)

    def test_stage_input_bounds_prevent_dispatch(self):
        manifest = self.manifest()
        manifest['max_input_chars'] = 1
        cell = next(evaluation.cells(manifest))
        with mock.patch.object(runner, 'call_ollama_chat') as chat:
            result = evaluation.run_cell(manifest, cell, self.root / 'bounded.json', 'http://localhost:11434')
        chat.assert_not_called()
        self.assertEqual(result['reserved_request_allowance'], 0)
        self.assertEqual(evaluation.summarize_usage([result])['execution']['attempt_count'], 0)

    def test_objective_checks_use_raw_output_not_normalized_content(self):
        manifest = self.manifest()
        manifest['cases'][0]['checks'] = [{'id': 'literal', 'type': 'equals', 'value': '42', 'strip': False}]
        cell = next(evaluation.cells(manifest))
        def chat(**kwargs):
            result = self.fake_chat(**kwargs)
            result['raw_content'] = ' ' + result['content'] + '\n'
            return result
        with mock.patch.object(runner, 'call_ollama_chat', side_effect=chat):
            data = evaluation.run_cell(manifest, cell, self.root / 'raw.json', 'http://localhost:11434')
        self.assertEqual(data['arms']['original']['objective_checks'][0]['status'], 'failed')
        self.assertEqual(data['arms']['original']['answer'], ' 42\n')

    def test_resume_never_relaunches_failed_or_interrupted_cells(self):
        args = self.args('--tasks', 'net-apples', '--seeds', '1')
        manifest = evaluation.build_manifest(args)
        args.output_dir.mkdir()
        evaluation.save(args.output_dir / 'manifest.json', manifest)
        evaluation.save(args.output_dir / 'state.json', {'deadline_at': 9999999999,
            'reserved_request_allowance': 27, 'cells': {'0': {'status': 'running'}}})
        with mock.patch.object(evaluation.subprocess, 'run') as worker, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(evaluation.run_campaign(args, manifest, self.argv), 1)
        worker.assert_not_called()
        state = json.loads((args.output_dir / 'state.json').read_text())
        self.assertEqual(state['cells']['0']['status'], 'failed')
        self.assertEqual(state['reserved_request_allowance'], 27)

    def test_coordinator_deadline_reserves_attempts_and_kills_worker(self):
        args = self.args('--tasks', 'net-apples', '--seeds', '1')
        manifest = evaluation.build_manifest(args)
        with mock.patch.object(evaluation.subprocess, 'run', side_effect=subprocess.TimeoutExpired('worker', 1)) as worker:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(evaluation.run_campaign(args, manifest, self.argv), 1)
        self.assertLessEqual(worker.call_args.kwargs['timeout'], 60)
        summary = json.loads((args.output_dir / 'summary.json').read_text())
        self.assertEqual(summary['reserved_request_allowance'], 27)
        self.assertIn('DeadlineExceeded', summary['failed_cells']['0']['error'])
        self.assertIsNone(summary['stage_usage']['execution']['eval_count'])

    def test_expired_campaign_cannot_start_more_requests(self):
        args = self.args('--tasks', 'net-apples', '--seeds', '1')
        manifest = evaluation.build_manifest(args)
        args.output_dir.mkdir()
        evaluation.save(args.output_dir / 'manifest.json', manifest)
        evaluation.save(args.output_dir / 'state.json', {'deadline_at': 0, 'reserved_request_allowance': 0, 'cells': {}})
        with mock.patch.object(evaluation.subprocess, 'run') as worker, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(evaluation.run_campaign(args, manifest, self.argv), 1)
        worker.assert_not_called()

    def test_changed_manifest_lock_and_nonempty_output_fail_closed(self):
        args = self.args()
        manifest = self.manifest()
        args.output_dir.mkdir()
        (args.output_dir / '.campaign.lock').mkdir()
        with self.assertRaisesRegex(ValueError, 'locked'):
            evaluation.run_campaign(args, manifest, self.argv)
        (args.output_dir / '.campaign.lock').rmdir()
        (args.output_dir / 'keep.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            evaluation.run_campaign(args, manifest, self.argv)
        evaluation.save(args.output_dir / 'manifest.json', {'schema': 'legacy'})
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            evaluation.run_campaign(args, manifest, self.argv)
        self.assertEqual((args.output_dir / 'keep.txt').read_text(), 'keep')

    def test_private_output_gate_and_existing_cell_protection(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(evaluation.main(self.argv + ['--run']), 1)
        manifest, cell, _, _ = self.run_cell()
        with self.assertRaisesRegex(ValueError, 'relaunch'):
            evaluation.run_cell(manifest, cell, self.root / 'cell.json', 'http://localhost:11434')


class DownstreamFakeOllama(FakeOllama):
    """Extend the existing loopback service, never contact a provider."""
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.__class__.requests.append((self.path, body))
        system = body['messages'][0]['content']
        if system.startswith('Prepare a prompt'):
            response = '{"decision":"bypass"}'
        elif system.startswith('You are an independent'):
            response = '| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence |\n' + \
                '\n'.join(f'| {d} | 4 | 4 | 0 | Both return 18. |' for d in
                          ['Accuracy', 'Completeness', 'Structure', 'Actionability', 'Traceability'])
        else:
            response = '18'
        frames = [{'message': {'content': response[:3]}, 'done': False},
                  {'message': {'content': response[3:]}, 'done': True}]
        frames[-1].update(prompt_eval_count=12, eval_count=4)
        payload = b''.join(json.dumps(frame).encode() + b'\n' for frame in frames)
        self.send_response(200)
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class DownstreamHttpTests(unittest.TestCase):
    def test_full_campaign_over_real_streamed_http_without_private_inputs(self):
        DownstreamFakeOllama.requests = []
        with mock.patch('socket.getfqdn', return_value='localhost'):
            server = ThreadingHTTPServer(('127.0.0.1', 0), DownstreamFakeOllama)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / '.private' / 'campaign'
                argv = ['--models', 'executor', '--judge-model', 'independent-judge', '--seeds', '42',
                        '--tasks', 'net-apples', '--max-requests', '27', '--deadline-seconds', '90',
                        '--max-output-tokens', '128', '--timeout', '3', '--run',
                        '--candidate-skill-dir', str(runner.REPO_ROOT / 'make-prompt-better'),
                        '--host', f'http://127.0.0.1:{server.server_port}', '--output-dir', str(output)]
                # Keep the genuine coordinator/worker process boundary and actual HTTP adapter.
                env = {**os.environ, 'OLLAMA_API_KEY': '', 'OLLAMA_HOST': ''}
                run = subprocess.run([sys.executable, evaluation.__file__, *argv],
                                     capture_output=True, text=True, timeout=100, env=env)
                self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
                summary = json.loads((output / 'summary.json').read_text())
                self.assertEqual(summary['completed_cells'], 1)
                self.assertFalse(summary['missing_pairs'])
                self.assertEqual(summary['reserved_request_allowance'], 27)
                self.assertEqual(summary['stage_usage']['judge']['eval_count'], 80)
                self.assertEqual(summary['outcomes']['original']['objective_checks']['passed'], 1)
                self.assertEqual(summary['bypass']['stable']['bypass_count'], 1)
                self.assertEqual(len(DownstreamFakeOllama.requests), 27)
                self.assertTrue(all(b['options']['seed'] == 42 for _, b in DownstreamFakeOllama.requests))
                again = subprocess.run([sys.executable, evaluation.__file__, *argv],
                                       capture_output=True, text=True, timeout=10, env=env)
                self.assertEqual(again.returncode, 0, again.stderr)
                self.assertEqual(len(DownstreamFakeOllama.requests), 27)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == '__main__':
    unittest.main()
