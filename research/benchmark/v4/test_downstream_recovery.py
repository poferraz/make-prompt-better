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
        response = (b'{"message":{"content":"answer"},"done":true,"eval_count":1}\n'
                    if self.mode == 'missing_usage' else b'')
        self.send_response(200 if self.mode == 'missing_usage' else 429)
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

    def test_429_stops_remaining_cells_and_resume(self):
        self.run_stop('rate_limit', 'http_429')

    def test_missing_usage_stops_remaining_cells_and_resume(self):
        self.run_stop('missing_usage', 'unknown_usage')
