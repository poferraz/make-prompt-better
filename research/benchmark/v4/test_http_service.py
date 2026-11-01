import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import threading
import unittest
from unittest import mock

import run_ollama_benchmarks as runner


class FakeOllama(BaseHTTPRequestHandler):
    requests = []

    def log_message(self, *_):
        pass

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        self.__class__.requests.append((self.path, json.loads(self.rfile.read(length))))
        if len(self.requests) == 1:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'temporary')
            return
        frames = [{'message': {'content': 'local '}, 'done': False},
                  {'message': {'content': 'answer'}, 'done': True, 'eval_count': 2}]
        body = b''.join(json.dumps(frame).encode() + b'\n' for frame in frames)
        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class HttpServiceTests(unittest.TestCase):
    @mock.patch.object(runner.time, 'sleep')
    def test_real_http_retry_stream_and_request_payload(self, _sleep):
        FakeOllama.requests = []
        with mock.patch('socket.getfqdn', return_value='localhost'):
            server = ThreadingHTTPServer(('127.0.0.1', 0), FakeOllama)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = runner.call_ollama_chat('local-model', [{'role': 'user', 'content': 'hello'}],
                host=f'http://127.0.0.1:{server.server_port}', timeout=3, initial_delay=0, max_retries=2, seed=71)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
        self.assertEqual(result['content'], 'local answer')
        self.assertEqual(result['eval_count'], 2)
        self.assertEqual(len(FakeOllama.requests), 2)
        self.assertEqual([path for path, _ in FakeOllama.requests], ['/api/chat'] * 2)
        self.assertEqual([body['options']['seed'] for _, body in FakeOllama.requests], [71, 71])
        self.assertEqual(FakeOllama.requests[0][1], FakeOllama.requests[1][1])

    @mock.patch.object(runner.time, 'sleep')
    def test_retryable_http_statuses_and_exhaustion(self, sleep):
        for status in [429, 500, 502, 503, 504, *range(520, 528)]:
            with self.subTest(status=status):
                responses = []
                def error(*args, **kwargs):
                    response = runner.urllib.error.HTTPError('http://local', status, 'unavailable', {}, io.BytesIO(b'rejected'))
                    responses.append(response)
                    raise response
                with mock.patch.object(runner.urllib.request, 'urlopen', side_effect=error) as urlopen:
                    with self.assertRaisesRegex(RuntimeError, str(status)):
                        runner.call_ollama_chat('model', [], max_retries=2, initial_delay=0)
                    self.assertEqual(urlopen.call_count, 2)
                    self.assertTrue(all(response.closed for response in responses))

    @mock.patch.object(runner.time, 'sleep')
    def test_network_error_categories_retry_and_raise(self, sleep):
        errors = [runner.urllib.error.URLError('offline'), TimeoutError('timeout'),
                  ConnectionResetError('reset'), OSError('socket'), http.client.IncompleteRead(b'partial')]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(runner.urllib.request, 'urlopen', side_effect=error) as urlopen:
                    with self.assertRaises(type(error)):
                        runner.call_ollama_chat('model', [], max_retries=2, initial_delay=0)
                    self.assertEqual(urlopen.call_count, 2)

    @mock.patch.object(runner.time, 'sleep')
    def test_nonretryable_http_boundaries_fail_immediately(self, sleep):
        for status in (400, 401, 403, 404, 519, 528):
            with self.subTest(status=status):
                error = runner.urllib.error.HTTPError('http://local', status, 'rejected', {}, io.BytesIO(b'denied'))
                with mock.patch.object(runner.urllib.request, 'urlopen', side_effect=error) as urlopen:
                    with self.assertRaisesRegex(RuntimeError, str(status)):
                        runner.call_ollama_chat('model', [], max_retries=3)
                    self.assertEqual(urlopen.call_count, 1)
                    self.assertTrue(error.closed)
        sleep.assert_not_called()

    @mock.patch.object(runner.time, 'sleep')
    def test_backoff_is_bounded_and_zero_retries_fails(self, sleep):
        with mock.patch.object(runner.urllib.request, 'urlopen', side_effect=TimeoutError('timeout')):
            with self.assertRaises(TimeoutError):
                runner.call_ollama_chat('model', [], max_retries=4, initial_delay=40)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [40, 60, 60])
        with mock.patch.object(runner.urllib.request, 'urlopen') as urlopen:
            with self.assertRaisesRegex(RuntimeError, 'Failed after 0 attempts'):
                runner.call_ollama_chat('model', [], max_retries=0)
            urlopen.assert_not_called()
