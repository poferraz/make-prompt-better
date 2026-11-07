import contextlib
import io
import json
import sys
import unittest
from unittest import mock

import run_ollama_benchmarks as runner


class CloudModelSelectionTests(unittest.TestCase):
    def run_cli(self, *args):
        output = io.StringIO()
        with mock.patch.object(sys, 'argv', ['runner', *args]), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = runner.main()
        return status, output.getvalue()

    def test_direct_cloud_requires_explicit_models_for_every_tier(self):
        with mock.patch.object(runner, 'discover_ollama_cloud_models', return_value=['local:cloud']) as discovery:
            for tier in ('installed-cloud', 'fast', 'flagship', 'all-cloud'):
                with self.subTest(tier=tier):
                    status, output = self.run_cli('--host', 'https://ollama.com', '--tier', tier, '--dry-run')
                    self.assertEqual(status, 1)
                    self.assertIn('--models', output)
            discovery.assert_not_called()

    def test_environment_host_also_requires_explicit_models(self):
        with mock.patch.dict(runner.os.environ, {"OLLAMA_HOST": "https://ollama.com"}), \
                mock.patch.object(runner, 'discover_ollama_cloud_models') as discovery:
            status, output = self.run_cli('--dry-run')
            self.assertEqual(status, 1)
            self.assertIn('--models', output)
            discovery.assert_not_called()

    def test_cloud_listing_points_to_catalog_without_local_discovery(self):
        with mock.patch.object(runner, 'discover_ollama_cloud_models') as discovery:
            status, output = self.run_cli('--host', 'https://OLLAMA.COM/', '--list-models')
            self.assertEqual(status, 0)
            self.assertIn('https://ollama.com/search?c=cloud', output)
            discovery.assert_not_called()

    def test_explicit_catalog_identifier_is_preserved(self):
        with mock.patch.object(runner, 'discover_ollama_cloud_models') as discovery:
            status, output = self.run_cli('--host', 'https://ollama.com', '--models', 'gpt-oss:120b', '--dry-run')
            self.assertEqual(status, 0)
            self.assertIn('Target models (1): gpt-oss:120b', output)
            discovery.assert_not_called()

    def test_cloud_aliases_are_rejected_for_executor_and_judge(self):
        for model in ('glm-5.3:cloud', 'gpt-oss:20b-cloud', 'deepseek-v4.1-flash:1017-cloud'):
            for field in ('--models', '--judge-model'):
                with self.subTest(model=model, field=field):
                    status, output = self.run_cli('--host', 'https://ollama.com', '--models', 'gpt-oss:120b', field, model, '--dry-run')
                    self.assertEqual(status, 1)
                    self.assertIn('catalog', output)

    def test_shared_chat_rejects_cloud_alias_before_network(self):
        with mock.patch.object(runner, 'open_ollama_request') as request:
            with self.assertRaisesRegex(ValueError, 'catalog'):
                runner.call_ollama_chat('gpt-oss:20b-cloud', [], host='https://ollama.com')
            request.assert_not_called()

    def test_catalog_identifier_reaches_request_unchanged(self):
        response = io.BytesIO(b'{"message":{"content":"ok"},"done":true}\n')
        with mock.patch.object(runner, 'open_ollama_request', return_value=response) as request, \
                mock.patch.object(runner.time, 'sleep'):
            runner.call_ollama_chat('gpt-oss:120b', [], host='https://ollama.com')
        self.assertEqual(json.loads(request.call_args.args[0].data)['model'], 'gpt-oss:120b')

    def test_local_discovery_and_presets_remain_unchanged(self):
        with mock.patch.object(runner, 'discover_ollama_cloud_models', return_value=['local:cloud']) as discovery:
            status, output = self.run_cli('--host', 'http://localhost:11434', '--dry-run')
            self.assertEqual(status, 0)
            self.assertIn('Target models (1): local:cloud', output)
            discovery.assert_called_once()
        status, output = self.run_cli('--host', 'http://localhost:11434', '--tier', 'fast', '--dry-run')
        self.assertEqual(status, 0)
        self.assertIn(', '.join(runner.FAST_TIER_MODELS), output)
