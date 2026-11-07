import io
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import run_ollama_benchmarks as runner
from test_benchmark_provenance import SCORES, response


class RunnerProtocolTests(unittest.TestCase):
    def test_absent_usage_stays_unknown_and_output_is_bounded(self):
        body = io.BytesIO(b'{"message":{"content":"ok"},"done":true}\n')
        with mock.patch.object(runner.time, 'sleep'), \
             mock.patch.object(runner, 'open_ollama_request', return_value=body) as request:
            result = runner.call_ollama_chat('model', [], max_output_tokens=37)
        self.assertIsNone(result['eval_count'])
        self.assertIsNone(result['prompt_eval_count'])
        self.assertEqual(json.loads(request.call_args.args[0].data)['options']['num_predict'], 37)
        self.assertEqual(result['telemetry']['attempt_count'], 1)
        self.assertEqual(result['telemetry']['attempts'][0]['status'], 'success')

    def test_retry_and_exhausted_failure_retain_unknown_usage(self):
        body = io.BytesIO(b'{"message":{"content":"ok"},"done":true,"eval_count":3}\n')
        with mock.patch.object(runner.time, 'sleep'), \
             mock.patch.object(runner, 'open_ollama_request', side_effect=[TimeoutError('first'), body]):
            result = runner.call_ollama_chat('model', [], max_retries=2, initial_delay=2)
        telemetry = result['telemetry']
        self.assertEqual(telemetry['attempt_count'], 2)
        self.assertEqual(telemetry['retry_count'], 1)
        self.assertEqual(telemetry['backoff_seconds'], 2)
        self.assertEqual(telemetry['attempts'][0]['status'], 'failed')
        self.assertIsNone(telemetry['attempts'][0]['eval_count'])
        self.assertGreaterEqual(telemetry['total_elapsed_seconds'], 0)
        with mock.patch.object(runner.time, 'sleep'), \
             mock.patch.object(runner, 'open_ollama_request', side_effect=TimeoutError('no answer')):
            with self.assertRaises(TimeoutError) as caught:
                runner.call_ollama_chat('model', [], max_retries=2, initial_delay=0)
        self.assertEqual(caught.exception.telemetry['attempt_count'], 2)
        self.assertTrue(all(a['status'] == 'failed' for a in caught.exception.telemetry['attempts']))

    def test_optional_auth_header_never_enters_saved_errors(self):
        secret = 'test-secret-never-save'
        body = io.BytesIO(b'{"message":{"content":"ok"},"done":true}\n')
        with mock.patch.object(runner.time, 'sleep'), \
             mock.patch.object(runner, 'open_ollama_request', return_value=body) as request:
            result = runner.call_ollama_chat('model', [], api_key=secret)
        self.assertEqual(request.call_args.args[0].get_header('Authorization'), 'Bearer ' + secret)
        self.assertNotIn(secret, json.dumps(result))
        errors = [TimeoutError(secret), runner.urllib.error.HTTPError('url', 401, secret, {}, io.BytesIO(secret.encode()))]
        for error in errors:
            with self.subTest(error=type(error).__name__), \
                 mock.patch.object(runner, 'open_ollama_request', side_effect=error):
                with self.assertRaises(Exception) as caught:
                    runner.call_ollama_chat('model', [], api_key=secret, max_retries=1)
                self.assertNotIn(secret, str(caught.exception))
                self.assertNotIn(secret, json.dumps(caught.exception.telemetry))

    def test_authenticated_transient_http_error_is_redacted_in_retry_logs(self):
        secret = 'secret-retry-message'
        error = runner.urllib.error.HTTPError('url', 503, secret, {}, io.BytesIO(secret.encode()))
        body = io.BytesIO(b'{"message":{"content":"ok"},"done":true}\n')
        with mock.patch.object(runner.time, 'sleep'), \
             mock.patch('sys.stdout', new_callable=io.StringIO) as output, \
             mock.patch.object(runner, 'open_ollama_request', side_effect=[error, body]):
            result = runner.call_ollama_chat('model', [], api_key=secret, max_retries=2, initial_delay=0)
        self.assertNotIn(secret, output.getvalue())
        self.assertNotIn(secret, json.dumps(result))

    def test_strict_omitted_code_and_facts_are_executed_without_repair(self):
        for test_id in (1, 2):
            with self.subTest(test_id=test_id), tempfile.TemporaryDirectory() as tmp:
                calls = []
                replies = iter(map(response, ['baseline', 'Analyze carefully.', 'answer', SCORES, 'report']))
                def chat(**kw):
                    calls.append(kw)
                    return next(replies)
                with mock.patch.object(runner, 'call_ollama_chat', side_effect=chat):
                    self.assertTrue(runner.run_model_benchmark('model', 'skill', [test_id],
                        results_dir=Path(tmp), strict_preservation=True, max_output_tokens=50))
                saved = json.loads((Path(tmp) / 'model/metrics.json').read_text())
                test = saved['tests'][str(test_id)]
                self.assertEqual(test['executed_optimized_prompt'], 'Analyze carefully.')
                self.assertEqual(test['preservation']['status'], 'failed')
                self.assertTrue(test['preservation']['missing_anchors'])
                self.assertTrue(all(c['max_output_tokens'] == 50 for c in calls))
                self.assertIn('optimizer', saved['telemetry']['stages'])

    def test_legacy_default_still_repairs_missing_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            replies = iter(map(response, ['baseline', 'Review carefully.', 'answer', SCORES, 'report']))
            with mock.patch.object(runner, 'call_ollama_chat', side_effect=lambda **kw: next(replies)):
                self.assertTrue(runner.run_model_benchmark('model', 'skill', [1], results_dir=Path(tmp)))
            saved = json.loads((Path(tmp) / 'model/metrics.json').read_text())
            self.assertIn('def calculate_discount', saved['tests']['1']['executed_optimized_prompt'])

    def test_skill_directory_and_protocol_are_bound_to_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'references').mkdir()
            for name in ('SKILL.md', 'references/domain-templates.md', 'references/research-principles.md'):
                (root / name).write_text(name)
            bundle = runner.load_skill_bundle(root)
            self.assertIn('references/domain-templates.md', bundle)
            manifest = runner.build_manifest('model', bundle, [1], 'http://localhost', 10,
                'judge', True, True, False, False, 42, skill_dir=root,
                strict_preservation=True, max_output_tokens=71)
            self.assertEqual(manifest['skill_dir'], str(root.resolve()))
            self.assertEqual(manifest['strict_preservation'], True)
            self.assertEqual(manifest['max_output_tokens'], 71)
            self.assertEqual(manifest['schema'], 2)
            self.assertEqual(manifest['pricing_status'], 'unknown')

    def test_http_redirects_cannot_forward_auth_or_spend_extra_requests(self):
        received = []
        class RedirectService(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass
            def do_POST(self):
                received.append(('source', self.headers.get('Authorization')))
                self.send_response(302)
                self.send_header('Location', f'http://localhost:{self.server.server_port}/capture')
                self.end_headers()
            def do_GET(self):
                received.append(('target', self.headers.get('Authorization')))
                body = b'{"message":{"content":"redirected"},"done":true}\n'
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)
        with mock.patch('socket.getfqdn', return_value='localhost'):
            server = ThreadingHTTPServer(('127.0.0.1', 0), RedirectService)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for api_key in ('secret-redirect', None):
                with self.subTest(auth=bool(api_key)), mock.patch.object(runner.time, 'sleep'):
                    with self.assertRaisesRegex(RuntimeError, '302'):
                        runner.call_ollama_chat('model', [], host=f'http://127.0.0.1:{server.server_port}',
                            api_key=api_key, max_retries=2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
        self.assertEqual(received, [('source', 'Bearer secret-redirect'), ('source', None)])

    def test_invalid_judge_is_a_failed_call_with_retained_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            replies = list(map(response, ['baseline', 'prompt', 'answer', 'invalid judge']))
            with mock.patch.object(runner, 'call_ollama_chat', side_effect=replies):
                self.assertFalse(runner.run_model_benchmark('model', 'skill', [1], results_dir=Path(tmp)))
            saved = json.loads((Path(tmp) / 'model/metrics.json').read_text())
            judge = saved['telemetry']['stages']['judge']
            self.assertEqual(judge['failed_calls'], 1)
            self.assertEqual(judge['eval_count'], 1)
            self.assertEqual(saved['tests'], {})

    def test_resume_retains_previous_partial_run_synthesis_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            replies = [*map(response, ['baseline', 'prompt', 'answer', SCORES]),
                       RuntimeError('second task failed'), response('partial report')]
            with mock.patch.object(runner, 'call_ollama_chat', side_effect=replies):
                self.assertFalse(runner.run_model_benchmark('model', 'skill', [1, 2], results_dir=Path(tmp)))
            replies = list(map(response, ['baseline two', 'prompt two', 'answer two', SCORES, 'complete report']))
            with mock.patch.object(runner, 'call_ollama_chat', side_effect=replies):
                self.assertTrue(runner.run_model_benchmark('model', 'skill', [1, 2], results_dir=Path(tmp)))
            saved = json.loads((Path(tmp) / 'model/metrics.json').read_text())
            self.assertEqual(saved['telemetry']['stages']['synthesis']['calls'], 2)
            self.assertEqual(saved['telemetry']['stages']['synthesis']['eval_count'], 2)

    def test_failed_stage_is_saved_with_attempt_telemetry(self):
        with tempfile.TemporaryDirectory() as tmp:
            error = TimeoutError('executor failed')
            error.telemetry = {'attempt_count': 2, 'retry_count': 1,
                'total_elapsed_seconds': 4, 'backoff_seconds': 1,
                'attempts': [{'status': 'failed', 'eval_count': None, 'prompt_eval_count': None}] * 2}
            with mock.patch.object(runner, 'call_ollama_chat', side_effect=[response('base'), response('prompt'), error]):
                self.assertFalse(runner.run_model_benchmark('model', 'skill', [1], results_dir=Path(tmp)))
            saved = json.loads((Path(tmp) / 'model/metrics.json').read_text())
            failed = saved['in_progress']['1']['failed_stage_attempts']['execute'][0]
            self.assertEqual(failed['telemetry']['attempt_count'], 2)
            self.assertEqual(saved['in_progress']['1']['preservation']['status'], 'failed')
            self.assertEqual(saved['failures'][0]['test_id'], 1)
            self.assertIsNone(saved['telemetry']['stages']['execution']['eval_count'])
            self.assertEqual(saved['telemetry']['stages']['execution']['failed_attempts'], 2)


if __name__ == '__main__':
    unittest.main()
