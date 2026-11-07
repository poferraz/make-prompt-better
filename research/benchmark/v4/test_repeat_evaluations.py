import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import run_ollama_benchmarks as runner


class CampaignTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.find_spec('repeat_evaluations')
        self.assertIsNotNone(spec, 'The repeated evaluation campaign module is missing')
        import repeat_evaluations
        self.campaign = repeat_evaluations
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for variant in ('baseline', 'candidate'):
            directory = self.root / variant
            (directory / 'references').mkdir(parents=True)
            for name in ('SKILL.md', 'references/domain-templates.md', 'references/research-principles.md'):
                (directory / name).write_text(variant + name)
        self.output = self.root / 'campaign'
        self.args = ['--baseline-skill-dir', str(self.root / 'baseline'),
                     '--candidate-skill-dir', str(self.root / 'candidate'),
                     '--models', 'model-a,model-b', '--judge-model', 'independent-judge',
                     '--seeds', '11,12', '--tests', '1,2', '--output-dir', str(self.output),
                     '--max-requests', '440', '--deadline-seconds', '60', '--max-output-tokens', '100']

    def fake_runner(self, cmd, **kwargs):
        def arg(name):
            return cmd[cmd.index(name) + 1]
        model = arg('--models')
        seed = int(arg('--seed'))
        skill_dir = Path(arg('--skill-dir'))
        test_ids = list(map(int, arg('--tests').split(',')))
        path = Path(arg('--results-dir')) / arg('--run-id') / runner.slugify_model(model) / 'metrics.json'
        path.parent.mkdir(parents=True)
        manifest = runner.build_manifest(model, runner.load_skill_bundle(skill_dir), test_ids,
            arg('--host'), int(arg('--timeout')), arg('--judge-model'), True, True, False, True, seed,
            skill_dir=skill_dir, strict_preservation=True, max_output_tokens=100)
        score = 23 if skill_dir.name == 'candidate' else 20
        tests = {str(tid): {'id': tid, 'judge_model': 'independent-judge', 'self_judged': False,
            'preservation': {'status': 'failed' if tid == 2 else 'no_literal_omissions_detected'},
            'evaluation': {'parsed': {'baseline_total': 19, 'optimized_total': score,
                                      'delta_total': score - 19}}} for tid in test_ids}
        path.write_text(json.dumps({'model': model, 'manifest': manifest, 'tests': tests,
                                    'in_progress': {}}))
        return subprocess.CompletedProcess(cmd, 0, 'fixture output', '')

    def test_multiple_seeds_use_exact_pairs_and_cluster_by_task(self):
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=self.fake_runner) as run:
            self.assertEqual(self.campaign.main(self.args), 0)
        self.assertEqual(run.call_count, 8)
        self.assertTrue(all('--strict-preservation' in c.args[0] and '--swap-positions' in c.args[0]
                            for c in run.call_args_list))
        summary = json.loads((self.output / 'summary.json').read_text())
        self.assertEqual(summary['completed_pairs'], 8)
        self.assertEqual(summary['task_clusters'], 2)
        self.assertEqual(summary['mean_candidate_minus_baseline'], 3)
        self.assertEqual(summary['preservation_failures'], {'baseline': 4, 'candidate': 4})
        self.assertEqual(summary['inference_status'], 'descriptive_only')
        self.assertIsNone(summary['task_cluster_95_ci'])
        self.assertEqual(summary['pricing_status'], 'unknown')
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=AssertionError('repeated call')):
            self.assertEqual(self.campaign.main(self.args), 0)

    def test_variants_are_paired_and_order_alternates_by_seed(self):
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=self.fake_runner) as run:
            self.assertEqual(self.campaign.main(self.args), 0)
        order = [(Path(c.args[0][c.args[0].index('--skill-dir') + 1]).name,
                  c.args[0][c.args[0].index('--models') + 1],
                  c.args[0][c.args[0].index('--seed') + 1]) for c in run.call_args_list]
        self.assertEqual(order[:4], [('baseline', 'model-a', '11'), ('candidate', 'model-a', '11'),
                                    ('candidate', 'model-a', '12'), ('baseline', 'model-a', '12')])

    def test_task_cluster_uncertainty_does_not_treat_repeat_seeds_as_cases(self):
        args = self.args.copy()
        args[args.index('--tests') + 1] = '1,2,3,4,5'
        args[args.index('--max-requests') + 1] = '1040'
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=self.fake_runner):
            self.assertEqual(self.campaign.main(args), 0)
        summary = json.loads((self.output / 'summary.json').read_text())
        self.assertEqual(summary['task_clusters'], 5)
        self.assertEqual(summary['completed_pairs'], 20)
        self.assertEqual(summary['task_cluster_95_ci'], [3, 3])

    def test_dry_run_has_no_network_subprocess_or_result_writes(self):
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=AssertionError('subprocess')), \
             mock.patch.object(runner.urllib.request, 'urlopen', side_effect=AssertionError('network')):
            self.assertEqual(self.campaign.main(self.args + ['--dry-run']), 0)
        self.assertFalse(self.output.exists())

    def test_cap_deadline_and_independent_judge_validation_precede_writes(self):
        for flag, value in (('--max-requests', '439'), ('--deadline-seconds', '0'),
                            ('--deadline-seconds', 'nan'), ('--max-output-tokens', '0'),
                            ('--judge-model', 'model-a'), ('--seeds', '11,11')):
            args = self.args.copy()
            args[args.index(flag) + 1] = value
            with self.subTest(flag=flag, value=value), \
                 mock.patch.object(self.campaign.subprocess, 'run', side_effect=AssertionError('subprocess')):
                self.assertNotEqual(self.campaign.main(args), 0)
            self.assertFalse(self.output.exists())

    def test_manifest_mismatch_from_changed_source_or_seeds_cannot_resume(self):
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=self.fake_runner):
            self.assertEqual(self.campaign.main(self.args), 0)
        original = (self.output / 'manifest.json').read_bytes()
        (self.root / 'candidate/SKILL.md').write_text('changed')
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=AssertionError('network')):
            self.assertNotEqual(self.campaign.main(self.args), 0)
        self.assertEqual((self.output / 'manifest.json').read_bytes(), original)

    def test_failure_and_timeout_are_saved_and_never_silently_retried(self):
        calls = 0
        def failing(cmd, **kw):
            nonlocal calls
            calls += 1
            if calls == 1:
                return subprocess.CompletedProcess(cmd, 1, '', 'fixture failure')
            if calls == 3:
                raise subprocess.TimeoutExpired(cmd, kw['timeout'], output='partial', stderr='timeout')
            return self.fake_runner(cmd, **kw)
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=failing):
            self.assertEqual(self.campaign.main(self.args), 1)
        state = json.loads((self.output / 'state.json').read_text())
        self.assertEqual(sum(c['status'] == 'failed' for c in state['cells'].values()), 2)
        summary = json.loads((self.output / 'summary.json').read_text())
        self.assertEqual(len(summary['failed_cells']), 2)
        self.assertEqual(len(summary['missing_pairs']), 4)
        self.assertEqual(summary['completed_pairs'], 4)
        self.assertTrue(any(p.read_text() == 'partial' for p in self.output.rglob('stdout.txt')))
        self.assertTrue(summary['telemetry_incomplete'])
        self.assertIsNone(summary['stage_totals']['baseline']['execution']['eval_count'])
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=AssertionError('retry')):
            self.assertEqual(self.campaign.main(self.args), 1)

    def test_saved_run_with_incompatible_manifest_is_a_failed_cell(self):
        def wrong_protocol(cmd, **kw):
            result = self.fake_runner(cmd, **kw)
            path = next((self.output / 'runs').rglob('metrics.json'))
            data = json.loads(path.read_text())
            data['manifest']['seed'] = 999
            path.write_text(json.dumps(data))
            return result
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=wrong_protocol):
            self.assertEqual(self.campaign.main(self.args), 1)
        summary = json.loads((self.output / 'summary.json').read_text())
        self.assertTrue(summary['failed_cells'])
        self.assertLess(summary['completed_pairs'], 8)

    def test_changing_sources_during_campaign_stops_further_calls_for_that_variant(self):
        calls = []
        def change_source(cmd, **kwargs):
            result = self.fake_runner(cmd, **kwargs)
            calls.append(cmd)
            (self.root / 'baseline/SKILL.md').write_text('changed during campaign')
            return result
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=change_source):
            self.assertEqual(self.campaign.main(self.args), 1)
        baseline_calls = [c for c in calls if str(self.root / 'baseline') in c]
        self.assertEqual(len(baseline_calls), 1)
        summary = json.loads((self.output / 'summary.json').read_text())
        self.assertEqual(summary['completed_pairs'], 0)

    def test_real_subprocess_is_killed_when_campaign_deadline_expires(self):
        args = self.args.copy()
        args[args.index('--deadline-seconds') + 1] = '0.05'
        real_run = subprocess.run
        def slow_runner(cmd, **kwargs):
            return real_run([__import__('sys').executable, '-c', 'import time; time.sleep(5)'], **kwargs)
        with mock.patch.object(self.campaign.subprocess, 'run', side_effect=slow_runner):
            self.assertEqual(self.campaign.main(args), 1)
        state = json.loads((self.output / 'state.json').read_text())
        self.assertTrue(any(c.get('error') == 'Campaign subprocess deadline exceeded' for c in state['cells'].values()))
        self.assertEqual(state['reserved_request_allowance'], 55)

    def test_expired_campaign_does_not_launch_more_work(self):
        with mock.patch.object(self.campaign.time, 'time', side_effect=[100, 161, 161, 161, 161, 161, 161, 161, 161]), \
             mock.patch.object(self.campaign.subprocess, 'run', side_effect=AssertionError('deadline exceeded')):
            self.assertEqual(self.campaign.main(self.args), 1)
        summary = json.loads((self.output / 'summary.json').read_text())
        self.assertEqual(summary['completed_pairs'], 0)
        self.assertEqual(len(summary['missing_pairs']), 8)


if __name__ == '__main__':
    unittest.main()
