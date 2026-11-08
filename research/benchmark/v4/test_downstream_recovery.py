"""Regression tests for campaign safety and truthful evidence; no provider calls."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock
from urllib.error import HTTPError

import downstream_evaluation as evaluation
runner = evaluation.runner


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / '.private' / 'campaign'
        self.argv = ['--models', 'executor', '--judge-model', 'judge', '--seeds', '1',
                     '--tasks', 'net-apples', '--max-requests', '27', '--deadline-seconds', '30',
                     '--candidate-skill-dir', str(runner.REPO_ROOT / 'make-prompt-better'),
                     '--output-dir', str(self.root)]

    def args(self, *extra):
        return evaluation.parser().parse_args(self.argv + list(extra))

    def test_rejects_known_aliases_and_invalid_cloud_judge_before_run(self):
        for args in [('--models', 'gemma4', '--judge-model', 'gemma4:latest'),
                     ('--models', 'gemma4:latest', '--judge-model', 'library/gemma4'),
                     ('--host', 'https://ollama.com', '--judge-model', 'judge:cloud')]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                evaluation.build_manifest(self.args(*args))

    def test_catalog_digests_are_recorded_and_known_identity_collisions_rejected(self):
        catalog = self.root.parent / 'catalog.json'
        catalog.parent.mkdir(parents=True, exist_ok=True)
        catalog.write_text(json.dumps({'models': [{'name': 'executor', 'digest': 'same'},
                                                 {'name': 'judge', 'digest': 'same'}]}))
        with self.assertRaisesRegex(ValueError, 'identity'):
            evaluation.build_manifest(self.args('--catalog-snapshot', str(catalog)))
        catalog.write_text(json.dumps({'models': [{'name': 'executor', 'digest': 'one'},
                                                 {'name': 'judge', 'digest': 'two'}]}))
        manifest = evaluation.build_manifest(self.args('--catalog-snapshot', str(catalog)))
        self.assertEqual(manifest['model_catalog']['identities'], {'executor': 'one', 'judge': 'two'})
        self.assertEqual(manifest['model_catalog']['sha256'], evaluation.digest(catalog))

    def test_worker_cannot_bypass_coordinator(self):
        self.root.mkdir(parents=True)
        evaluation.save(self.root / 'manifest.json', evaluation.build_manifest(self.args()))
        with contextlib.redirect_stderr(io.StringIO()), mock.patch.object(runner, 'call_ollama_chat') as call:
            result = evaluation.main(self.argv + ['--run', '--cell-index', '0'])
        self.assertNotEqual(result, 0)
        call.assert_not_called()
        self.assertFalse((self.root / 'cells').exists())

    def test_evidence_failure_prevents_http_dispatch(self):
        def fail(payload):
            raise OSError('disk full')
        with mock.patch.object(runner, 'open_ollama_request') as request:
            with self.assertRaises(OSError):
                runner.call_ollama_chat('executor', [{'role': 'user', 'content': 'hello'}], request_observer=fail)
        request.assert_not_called()

    def test_resume_with_interrupted_worker_cannot_dispatch_another_cell(self):
        args = self.args('--seeds', '1,2', '--max-requests', '54')
        manifest = evaluation.build_manifest(args)
        self.root.mkdir(parents=True)
        (self.root / 'cells').mkdir()
        evaluation.save(self.root / 'manifest.json', manifest)
        evaluation.save(self.root / 'state.json', {'deadline_at': time.time() + 30,
            'reserved_request_allowance': 27, 'cells': {'0': {'status': 'running', 'reserved_request_allowance': 27}}})
        evaluation.save(self.root / 'cells' / '0.json', {'identity': next(evaluation.cells(manifest)),
            'status': 'running', 'arms': {}, 'comparisons': {},
            'calls': [{'stage': 'execution', 'arm': 'original', 'status': 'running'}]})
        with mock.patch.object(evaluation.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1)) as worker, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(evaluation.run_campaign(args, manifest, self.argv), 1)
        worker.assert_not_called()
        state = json.loads((self.root / 'state.json').read_text())
        self.assertEqual(state['stop_reason'], 'interrupted_cell_unknown_usage')

    def test_abnormal_worker_exit_stops_before_next_cell(self):
        args = self.args('--seeds', '1,2', '--max-requests', '54')
        manifest = evaluation.build_manifest(args)
        first = next(evaluation.cells(manifest))
        def crash(*_args, **_kwargs):
            (self.root / 'cells').mkdir(exist_ok=True)
            evaluation.save(self.root / 'cells' / '0.json', {'identity': first, 'status': 'running',
                'arms': {}, 'comparisons': {}, 'calls': [{'stage': 'execution', 'arm': 'original', 'status': 'running'}]})
            return subprocess.CompletedProcess([], -9)
        with mock.patch.object(evaluation.subprocess, 'run', side_effect=crash) as worker, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(evaluation.run_campaign(args, manifest, self.argv), 1)
        self.assertEqual(worker.call_count, 1)
        state = json.loads((self.root / 'state.json').read_text())
        self.assertEqual(state['stop_reason'], 'interrupted_cell_unknown_usage')

    def test_rate_limit_is_not_retried_when_fail_closed_enabled(self):
        error = HTTPError('http://localhost', 429, 'limited', {}, io.BytesIO(b'limited'))
        with mock.patch.object(runner, 'open_ollama_request', side_effect=error) as request:
            with self.assertRaises(runner.OllamaStopError) as caught:
                runner.call_ollama_chat('executor', [{'role': 'user', 'content': 'hello'}],
                                        max_retries=3, initial_delay=0,
                                        stop_status_codes={429}, stop_on_unknown_usage=True)
        self.assertEqual(caught.exception.reason, 'http_429')
        self.assertEqual(request.call_count, 1)

    def test_unknown_usage_from_failed_attempt_stops_before_retry(self):
        with mock.patch.object(runner, 'open_ollama_request', side_effect=TimeoutError()) as request:
            with self.assertRaises(runner.OllamaStopError) as caught:
                runner.call_ollama_chat('executor', [{'role': 'user', 'content': 'hello'}],
                                        max_retries=3, initial_delay=0, stop_on_unknown_usage=True)
        self.assertEqual(caught.exception.reason, 'unknown_usage')
        self.assertEqual(request.call_count, 1)

    def test_empty_response_with_known_usage_stops_and_retains_stream(self):
        frames = [{'message': {'thinking': 'partial reasoning', 'content': ''}, 'done': False},
                  {'message': {'content': ''}, 'done': True, 'prompt_eval_count': 15494, 'eval_count': 1024}]
        body = io.BytesIO(b''.join(json.dumps(frame).encode() + b'\n' for frame in frames))
        with mock.patch.object(runner, 'open_ollama_request', return_value=body) as request:
            with self.assertRaises(runner.OllamaStopError) as caught:
                runner.call_ollama_chat('executor', [{'role': 'user', 'content': 'hello'}],
                                        max_retries=3, stop_on_unknown_usage=True)
        self.assertEqual(caught.exception.reason, 'empty_response')
        self.assertEqual(caught.exception.response['raw_frames'], frames)
        attempt = caught.exception.telemetry['attempts'][0]
        self.assertEqual((attempt['prompt_eval_count'], attempt['eval_count']), (15494, 1024))
        self.assertEqual(request.call_count, 1)

    def test_empty_response_with_missing_usage_retains_stream_and_stops(self):
        frames = [{'message': {'thinking': 'partial', 'content': ''}, 'done': True, 'eval_count': 1024}]
        body = io.BytesIO(json.dumps(frames[0]).encode() + b'\n')
        with mock.patch.object(runner, 'open_ollama_request', return_value=body):
            with self.assertRaises(runner.OllamaStopError) as caught:
                runner.call_ollama_chat('executor', [], stop_on_unknown_usage=True)
        self.assertEqual(caught.exception.reason, 'unknown_usage')
        self.assertEqual(caught.exception.response['raw_frames'], frames)
        self.assertIsNone(caught.exception.telemetry['attempts'][0]['prompt_eval_count'])

    def test_empty_response_never_retains_frames_containing_credential(self):
        body = io.BytesIO(b'{"message":{"thinking":"private-token","content":""},"done":true,"prompt_eval_count":5,"eval_count":2}\n')
        with mock.patch.object(runner, 'open_ollama_request', return_value=body):
            with self.assertRaises(runner.OllamaStopError) as caught:
                runner.call_ollama_chat('executor', [], api_key='private-token', stop_on_unknown_usage=True)
        self.assertEqual(caught.exception.reason, 'sensitive_response')
        self.assertFalse(hasattr(caught.exception, 'response'))
        self.assertNotIn('private-token', json.dumps(caught.exception.telemetry))

    def test_empty_response_never_retains_credential_split_across_frames(self):
        frames = [{'message': {'thinking': 'private-', 'content': ''}, 'done': False},
                  {'message': {'thinking': 'token', 'content': ''}, 'done': True,
                   'prompt_eval_count': 5, 'eval_count': 2}]
        body = io.BytesIO(b''.join(json.dumps(frame).encode() + b'\n' for frame in frames))
        with mock.patch.object(runner, 'open_ollama_request', return_value=body):
            with self.assertRaises(runner.OllamaStopError) as caught:
                runner.call_ollama_chat('executor', [], api_key='private-token', stop_on_unknown_usage=True)
        self.assertEqual(caught.exception.reason, 'sensitive_response')
        self.assertFalse(hasattr(caught.exception, 'response'))

    def test_empty_response_evidence_is_saved_before_cell_stops(self):
        manifest = evaluation.build_manifest(self.args())
        cell = next(evaluation.cells(manifest))
        frames = [{'message': {'thinking': 'partial', 'content': ''}, 'done': True,
                   'prompt_eval_count': 7, 'eval_count': 3}]
        body = io.BytesIO(json.dumps(frames[0]).encode() + b'\n')
        with mock.patch.dict(os.environ, {'OLLAMA_API_KEY': ''}), \
             mock.patch.object(runner, 'open_ollama_request', return_value=body) as request:
            result = evaluation.run_cell(manifest, cell, self.root / 'cells' / '0.json', 'http://localhost:11434')
        saved = json.loads((self.root / 'cells' / '0.json').read_text())
        self.assertEqual(result['stop_reason'], 'empty_response')
        self.assertEqual(saved['calls'][0]['response']['raw_frames'], frames)
        self.assertEqual(len(saved['calls']), 1)
        self.assertEqual(request.call_count, 1)

    def test_only_one_concurrent_worker_can_claim_the_same_cell(self):
        manifest = evaluation.build_manifest(self.args())
        cell = next(evaluation.cells(manifest))
        path = self.root / 'cells' / '0.json'
        gate = threading.Barrier(2)
        outcomes = []
        def fake_chat(**kwargs):
            time.sleep(.001)
            message = kwargs['messages'][0]['content']
            if message.startswith('Prepare a prompt'):
                text = '{"decision":"bypass"}'
            elif message.startswith('You are an independent'):
                text = '\n'.join(f'| {d} | 4 | 4 | 0 | Evidence |' for d in
                                 ('Accuracy', 'Completeness', 'Structure', 'Actionability', 'Traceability'))
            else:
                text = '18'
            return {'content': text, 'telemetry': {'attempts': [], 'attempt_count': 1,
                    'retry_count': 0, 'total_elapsed_seconds': 0}}
        def worker():
            gate.wait()
            try:
                outcomes.append(evaluation.run_cell(manifest, cell, path, 'http://localhost:11434')['status'])
            except ValueError:
                outcomes.append('duplicate_rejected')
        with mock.patch.object(runner, 'call_ollama_chat', side_effect=fake_chat) as chat:
            threads = [threading.Thread(target=worker) for _ in range(2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=10)
        self.assertCountEqual(outcomes, ['completed', 'duplicate_rejected'])
        self.assertEqual(chat.call_count, 27)

    def test_payload_is_saved_before_dispatch_and_usage_cannot_embed_a_secret(self):
        body = b'{"message":{"content":"answer"},"done":true,"prompt_eval_count":"secret-token","eval_count":4}\n'
        seen = []
        def request(req, timeout):
            self.assertEqual(seen, [req.data])
            return io.BytesIO(body)
        with mock.patch.object(runner, 'open_ollama_request', side_effect=request), mock.patch.object(runner.time, 'sleep'):
            with self.assertRaises(runner.OllamaStopError) as caught:
                runner.call_ollama_chat('executor', [{'role': 'user', 'content': 'hello'}],
                    api_key='secret-token', request_observer=seen.append, stop_on_unknown_usage=True)
        self.assertEqual(caught.exception.reason, 'unknown_usage')
        self.assertNotIn('secret-token', json.dumps(caught.exception.telemetry))
        self.assertIsNone(caught.exception.telemetry['attempts'][0]['prompt_eval_count'])

    def test_missing_usage_response_containing_key_is_not_retained(self):
        body = io.BytesIO(b'{"message":{"content":"secret-token"},"done":true}\n')
        with mock.patch.object(runner, 'open_ollama_request', return_value=body):
            with self.assertRaises(runner.OllamaStopError) as caught:
                runner.call_ollama_chat('executor', [{'role': 'user', 'content': 'hello'}],
                                        api_key='secret-token', stop_on_unknown_usage=True)
        self.assertEqual(caught.exception.reason, 'sensitive_response')
        self.assertFalse(hasattr(caught.exception, 'response'))

    def test_answer_availability_is_part_of_the_denominator(self):
        manifest = evaluation.build_manifest(self.args())
        summary = evaluation.summarize(manifest, {'cells': {}}, [])
        outcome = summary['outcomes']['original']
        self.assertEqual(outcome['expected'], 1)
        self.assertEqual(outcome['answered'], 0)
        self.assertEqual(outcome['unavailable'], 1)


class LimitedHandler(BaseHTTPRequestHandler):
    count = 0
    mode = 'rate_limit'
    def do_POST(self):
        self.__class__.count += 1
        self.rfile.read(int(self.headers['Content-Length']))
        if self.mode == 'missing_usage':
            response = b'{"message":{"content":"answer"},"done":true,"eval_count":1}\n'
        elif self.mode == 'empty_response':
            response = b'{"message":{"thinking":"partial","content":""},"done":true,"prompt_eval_count":7,"eval_count":3}\n'
        else:
            response = b''
        self.send_response(200 if self.mode in {'missing_usage', 'empty_response'} else 429)
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    def log_message(self, *args):
        pass


class CampaignStopTests(unittest.TestCase):
    def run_stop(self, mode, expected_reason):
        LimitedHandler.count = 0
        LimitedHandler.mode = mode
        server = ThreadingHTTPServer(('127.0.0.1', 0), LimitedHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / '.private' / 'run'
                argv = [sys.executable, evaluation.__file__, '--models', 'executor', '--judge-model', 'judge',
                        '--seeds', '1,2', '--tasks', 'net-apples', '--max-requests', '162',
                        '--deadline-seconds', '30', '--max-attempts', '3', '--timeout', '2', '--run',
                        '--host', f'http://127.0.0.1:{server.server_port}',
                        '--candidate-skill-dir', str(runner.REPO_ROOT / 'make-prompt-better'), '--output-dir', str(output)]
                env = {**os.environ, 'OLLAMA_API_KEY': '', 'OLLAMA_HOST': ''}
                first = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=15)
                self.assertNotEqual(first.returncode, 0, first.stdout + first.stderr)
                self.assertEqual(LimitedHandler.count, 1)
                record = json.loads((output / 'cells' / '0.json').read_text())
                self.assertEqual(record['stop_reason'], expected_reason)
                self.assertIn('request_body', record['calls'][0])
                if expected_reason == 'unknown_usage':
                    self.assertEqual(record['calls'][0]['response']['content'], 'answer')
                    self.assertIsNone(record['calls'][0]['response']['prompt_eval_count'])
                if expected_reason == 'empty_response':
                    self.assertEqual(record['calls'][0]['response']['raw_frames'][0]['message']['thinking'], 'partial')
                    self.assertEqual(record['calls'][0]['response']['prompt_eval_count'], 7)
                # Simulate a coordinator crash before its state was updated with the stop.
                state_path = output / 'state.json'
                state = json.loads(state_path.read_text())
                state.pop('stop_reason', None)
                state['cells']['0']['status'] = 'running'
                state['cells'].pop('1', None)
                state_path.write_text(json.dumps(state))
                second = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=15)
                self.assertNotEqual(second.returncode, 0)
                self.assertEqual(LimitedHandler.count, 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_empty_response_stops_remaining_cells_and_resume(self):
        self.run_stop('empty_response', 'empty_response')

    def test_429_stops_remaining_cells_and_resume(self):
        self.run_stop('rate_limit', 'http_429')

    def test_missing_usage_stops_remaining_cells_and_resume(self):
        self.run_stop('missing_usage', 'unknown_usage')
