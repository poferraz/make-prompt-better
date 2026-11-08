"""Historical reanalysis must remain read-only, explicit and offline."""
import hashlib
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    import downstream_reanalysis as analysis
except ModuleNotFoundError:
    analysis = None

HEADER = '| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence |\n'
DIMS = ('Accuracy', 'Completeness', 'Structure', 'Actionability', 'Traceability')


def judge_text(bold=False):
    score_a, score_b = ('**4**', '**5**') if bold else ('4', '5')
    return HEADER + '\n'.join(f'| {d} | {score_a} | {score_b} | 1 | fine |' for d in DIMS)


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class ReanalysisTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(analysis, 'offline reanalysis module is required')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.private = Path(self.temp.name) / '.private'
        self.campaign = self.private / 'input' / 'campaign'
        (self.campaign / 'cells').mkdir(parents=True)
        self.output = self.private / 'output'
        self.manifest = {'schema': 2, 'protocol': 'five-arm-downstream-v2',
                         'arms': ['original', 'minimal_clarity', 'strong_direct', 'stable', 'candidate'],
                         'cases': [{'id': 'task', 'original_request': 'answer only'}],
                         'models': ['executor'], 'seeds': [42], 'judge_model': 'judge'}
        self.identity = {'index': 0, 'task_id': 'task', 'model': 'executor', 'seed': 42,
                         'arm_order': ['original', 'minimal_clarity', 'strong_direct', 'stable', 'candidate']}
        key = 'original__candidate'
        hashed = hashlib.sha256(f'42:executor:{key}:task'.encode()).digest()[0] % 2 == 0
        mapping = {'A': 'original' if hashed else 'candidate', 'B': 'candidate' if hashed else 'original'}
        self.record = {'identity': self.identity, 'status': 'failed', 'arms': {
            'original': {'answer': 'first'}, 'candidate': {'answer': 'second'}},
            'comparisons': {}, 'calls': [], 'failures': []}
        for i, assignment in enumerate((mapping, {'A': mapping['B'], 'B': mapping['A']})):
            messages = [{'role': 'system', 'content': 'judge'}, {'role': 'user', 'content': json.dumps({
                'original_request': 'answer only', 'candidate_A': self.record['arms'][assignment['A']]['answer'],
                'candidate_B': self.record['arms'][assignment['B']]['answer']})}]
            payload = json.dumps({'model': 'judge', 'messages': messages, 'options': {'seed': 42}})
            self.record['calls'].append({'stage': 'judge', 'arm': key,
                'status': 'completed' if i == 0 else 'failed', 'error': None if i == 0 else 'ValueError',
                'request_body': payload,
                'request_body_sha256': hashlib.sha256(payload.encode()).hexdigest(),
                'request_sha256': hashlib.sha256(json.dumps(messages, ensure_ascii=False).encode()).hexdigest(),
                'response': {'content': judge_text(bold=bool(i)),
                             'telemetry': {'attempts': [{'prompt_eval_count': 9, 'eval_count': 2}]}}})
        self.state = {'cells': {'0': {'status': 'failed', 'reserved_request_allowance': 27}},
                      'reserved_request_allowance': 27}
        self.save()

    def save(self):
        write_json(self.campaign / 'manifest.json', self.manifest)
        write_json(self.campaign / 'state.json', self.state)
        write_json(self.campaign / 'cells' / '0.json', self.record)
        write_json(self.campaign / 'summary.json', {'historical': 'preserved'})

    def files(self):
        return {str(p.relative_to(self.campaign)): p.read_bytes() for p in self.campaign.rglob('*') if p.is_file()}

    def test_reanalysis_recovers_format_without_rewriting_history(self):
        before = self.files()
        result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(self.files(), before)
        self.assertEqual(result['official_completed_pairs'], 0)
        self.assertEqual(result['derived_completed_pairs'], 1)
        self.assertEqual(result['recovered_pairs'], 1)
        self.assertEqual(result['pair_summaries']['original__candidate']['completed_pairs'], 1)
        self.assertEqual(result['pair_summaries']['original__candidate']['expected_pairs'], 1)
        saved = json.loads((self.output / 'comparison-results.json').read_text())
        self.assertTrue(saved[0]['recovered_format_valid'])
        self.assertFalse(saved[0]['official_complete'])
        self.assertEqual(saved[0]['original_statuses'], ['completed', 'failed'])

    def test_reanalysis_never_calls_network_or_workers(self):
        with mock.patch.object(socket, 'create_connection', side_effect=AssertionError('network')):
            result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(result['derived_completed_pairs'], 1)

    def test_refuses_overwrite_symlinks_and_input_overlap(self):
        self.output.mkdir()
        sentinel = self.output / 'sentinel'
        sentinel.write_text('KEEP')
        with self.assertRaises(ValueError):
            analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(sentinel.read_text(), 'KEEP')
        with self.assertRaises(ValueError):
            analysis.reanalyze(self.campaign, self.campaign / 'new')
        with self.assertRaises(ValueError):
            analysis.reanalyze(self.campaign, Path(self.temp.name) / 'outside')
        link = self.private / 'link'
        link.symlink_to(self.private / 'input', target_is_directory=True)
        with self.assertRaises(ValueError):
            analysis.reanalyze(link / 'campaign', self.private / 'other')

    def test_v2_mapping_reconstruction_matches_requests(self):
        entry = self.record['calls'][1]
        payload = json.loads(entry['request_body'])
        data = json.loads(payload['messages'][1]['content'])
        data['candidate_A'] = 'fabricated'
        payload['messages'][1]['content'] = json.dumps(data)
        entry['request_body'] = json.dumps(payload)
        entry['request_body_sha256'] = hashlib.sha256(entry['request_body'].encode()).hexdigest()
        entry['request_sha256'] = hashlib.sha256(json.dumps(payload['messages'], ensure_ascii=False).encode()).hexdigest()
        self.save()
        with self.assertRaises(ValueError):
            analysis.reanalyze(self.campaign, self.output)
        self.assertFalse(self.output.exists())

    def test_failed_transport_is_not_recovered_even_with_parseable_text(self):
        self.record['calls'][1]['error'] = 'OllamaStopError'
        self.save()
        result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(result['derived_completed_pairs'], 0)
        self.assertEqual(result['orphan_valid_passes'], 1)
        self.assertEqual(result['excluded_passes']['transport_failed'], 1)

    def test_pending_judge_intent_is_excluded_without_guessing_usage(self):
        self.record['calls'][1] = {'stage': 'judge', 'arm': 'original__candidate', 'status': 'running'}
        self.save()
        result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(result['derived_completed_pairs'], 0)
        self.assertEqual(result['orphan_valid_passes'], 1)
        self.assertEqual(result['excluded_passes']['request_body_missing'], 1)
        self.assertIsNone(result['usage']['judge']['eval_count'])

    def test_reanalysis_reports_scheduled_pair_denominators(self):
        result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(result['expected_pairs'], 10)
        self.assertEqual(result['official_missing_pairs'], 10)
        self.assertEqual(result['derived_missing_pairs'], 9)

    def test_rejects_invalid_manifests_without_creating_output(self):
        variants = [dict(self.manifest, schema=9), dict(self.manifest, protocol='five-arm-downstream-v3'),
                    dict(self.manifest, seeds=[42,42]), dict(self.manifest, cell_schedule=[])]
        for manifest in variants:
            with self.subTest(manifest=manifest):
                self.manifest = manifest
                self.save()
                with self.assertRaises(ValueError):
                    analysis.reanalyze(self.campaign, self.output)
                self.assertFalse(self.output.exists())

    def test_missing_launched_record_never_reports_zero_usage(self):
        (self.campaign/'cells'/'0.json').unlink()
        result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(result['missing_cell_indexes'], [0])
        self.assertEqual(result['missing_launched_cells'], [0])
        self.assertIsNone(result['usage']['execution']['eval_count'])
        self.assertEqual(result['usage']['execution']['known_eval_count'], 0)

    def test_corrupt_hash_or_identity_is_rejected(self):
        self.record['calls'][0]['request_body_sha256'] = 'bad'
        self.save()
        with self.assertRaises(ValueError):
            analysis.reanalyze(self.campaign, self.output)
        self.assertFalse(self.output.exists())
        self.record['calls'][0]['request_body_sha256'] = hashlib.sha256(
            self.record['calls'][0]['request_body'].encode()).hexdigest()
        self.record['identity']['model'] = 'different'
        self.save()
        with self.assertRaises(ValueError):
            analysis.reanalyze(self.campaign, self.output)

    def test_invalid_format_stays_missing(self):
        self.record['calls'][1]['response']['content'] = 'not a rubric'
        self.save()
        result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual((result['derived_completed_pairs'], result['orphan_valid_passes']), (0, 1))
        self.assertEqual(result['excluded_passes']['invalid_judge_format'], 1)

    def test_atomic_output_cleanup_leaves_input_untouched(self):
        before = self.files()
        with mock.patch.object(analysis.os, 'replace', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                analysis.reanalyze(self.campaign, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.files(), before)

    def test_cli_reports_errors_without_private_response_contents(self):
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(analysis.main(['--campaign-dir', str(self.campaign),
                                            '--output-dir', str(self.output)]), 0)
            self.assertEqual(analysis.main(['--campaign-dir', str(self.campaign),
                                            '--output-dir', str(self.output)]), 1)
        self.assertIn('Error: ValueError', output.getvalue())

    def test_saved_v3_schedule_and_mapping_are_checked(self):
        self.manifest.update(schema=3, protocol='five-arm-downstream-v3', cell_schedule=[self.identity])
        for i, call in enumerate(self.record['calls'], 1):
            data = json.loads(json.loads(call['request_body'])['messages'][1]['content'])
            first = 'original' if data['candidate_A'] == 'first' else 'candidate'
            call.update(judge_pair='original__candidate', judge_pass_index=i,
                        judge_mapping={'A':first,'B':'candidate' if first=='original' else 'original'})
        self.save()
        result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(result['derived_completed_pairs'], 1)
        self.record['calls'][1]['judge_pass_index'] = 1
        self.save()
        with self.assertRaises(ValueError):
            analysis.reanalyze(self.campaign, self.private/'another-output')

    def test_v3_orphan_remains_orphan(self):
        self.manifest['schema'] = 3
        self.manifest['protocol'] = 'five-arm-downstream-v3'
        self.record['calls'] = self.record['calls'][:1]
        data = json.loads(json.loads(self.record['calls'][0]['request_body'])['messages'][1]['content'])
        left = 'original' if data['candidate_A'] == 'first' else 'candidate'
        self.record['calls'][0].update(judge_pair='original__candidate', judge_pass_index=1,
            judge_mapping={'A': left, 'B': 'candidate' if left == 'original' else 'original'})
        self.save()
        result = analysis.reanalyze(self.campaign, self.output)
        self.assertEqual(result['derived_completed_pairs'], 0)
        self.assertEqual(result['orphan_valid_passes'], 1)


if __name__ == '__main__':
    unittest.main()
