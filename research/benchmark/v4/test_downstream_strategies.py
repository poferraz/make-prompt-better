"""Selectable experiment recipes remain bounded, versioned and explicitly labeled."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import downstream_design as design
import downstream_evaluation as evaluation


class StrategyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = evaluation.runner.REPO_ROOT / 'make-prompt-better'
        self.argv = ['--models','executor','--judge-model','judge','--seeds','42',
                     '--tasks','net-apples','--max-requests','27','--deadline-seconds','60',
                     '--candidate-skill-dir',str(self.skill),'--output-dir',str(self.root/'campaign')]

    def manifest(self, *args):
        return evaluation.build_manifest(evaluation.parser().parse_args(self.argv + list(args)))

    def fake_chat(self, **kwargs):
        text = kwargs['messages'][0]['content']
        if text.startswith('Prepare a prompt'):
            response = '{"decision":"bypass"}'
        elif text.startswith('You are an independent'):
            response = '| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence |\n' + \
                '\n'.join(f'| {d} | 4 | 4 | 0 | fine |' for d in
                          ('Accuracy','Completeness','Structure','Actionability','Traceability'))
        else:
            response = '18'
        return {'content':response, 'raw_content':response,
                'telemetry':{'attempt_count':1,'retry_count':0,'total_elapsed_seconds':0,
                             'attempts':[{'status':'success','prompt_eval_count':1,'eval_count':1}]}}

    def test_recipe_cell_counts_are_27_5_9(self):
        for name, expected_calls, expected_pairs in [('five-arm',27,10),('primary',5,1),('primary-aa',9,2)]:
            with self.subTest(recipe=name):
                manifest = self.manifest('--recipe',name)
                self.assertEqual(manifest['calls_per_cell'], expected_calls)
                self.assertEqual(manifest['required_request_allowance'], expected_calls)
                path = self.root / (name + '.json')
                with mock.patch.object(evaluation.runner, 'call_ollama_chat', side_effect=self.fake_chat):
                    record = evaluation.run_cell(manifest, next(evaluation.cells(manifest)), path, 'http://localhost:11434')
                self.assertEqual(record['status'], 'completed')
                self.assertEqual(len(record['calls']), expected_calls)
                self.assertEqual(len(record['comparisons']), expected_pairs)
                summary = evaluation.summarize(manifest, {'cells':{'0':{'status':'completed'}}}, [record])
                self.assertEqual(len(summary['pair_summaries']), expected_pairs)
                self.assertEqual(set(summary['outcomes']), set(manifest['arms']))

    def test_primary_does_not_require_an_unused_candidate_directory(self):
        argv = list(self.argv)
        index = argv.index('--candidate-skill-dir')
        del argv[index:index + 2]
        args = evaluation.parser().parse_args(argv + ['--recipe', 'primary'])
        manifest = evaluation.build_manifest(args)
        self.assertEqual(set(manifest['skills']), {'stable'})
        with self.assertRaises(ValueError):
            evaluation.build_manifest(evaluation.parser().parse_args(argv))

    def test_core_only_reads_and_hashes_only_skill_file(self):
        root = self.root/'only-skill'
        root.mkdir()
        (root/'SKILL.md').write_text('original')
        core = evaluation.load_preparation_bundle(root, 'core-only')
        self.assertEqual(set(core['source_sha256']), {'SKILL.md'})
        self.assertEqual(core['text'], '# SKILL FILE 1: make-prompt-better/SKILL.md\n\noriginal\n\n')
        with self.assertRaises(FileNotFoundError):
            evaluation.load_preparation_bundle(root, 'full')
        (root/'SKILL.md').write_text('changed')
        self.assertNotEqual(core['bundle_sha256'], evaluation.load_preparation_bundle(root,'core-only')['bundle_sha256'])
        full = evaluation.load_preparation_bundle(self.skill, 'full')
        self.assertEqual(full['text'], evaluation.runner.load_skill_bundle(self.skill))

    def test_core_only_manifest_labels_effective_treatment(self):
        manifest = self.manifest('--candidate-bundle-mode', 'core-only')
        self.assertEqual(manifest['skills']['candidate']['mode'], 'core-only')
        self.assertEqual(manifest['skills']['stable']['mode'], 'full')
        self.assertNotEqual(manifest['skills']['candidate']['bundle_sha256'],
                            manifest['skills']['stable']['bundle_sha256'])
        self.assertNotIn('full skill bundle', manifest['preparation'])

    def test_reservation_is_checked_before_allocating_the_schedule(self):
        with mock.patch.object(evaluation, 'build_cell_schedule', side_effect=AssertionError('allocated')):
            with self.assertRaisesRegex(ValueError, 'reserved HTTP attempts'):
                self.manifest('--max-requests', '1')

    def test_primary_aa_rejects_nonidentical_treatments(self):
        with self.assertRaises(ValueError):
            self.manifest('--recipe','primary-aa','--candidate-bundle-mode','core-only')
        directory = self.root/'different'
        (directory/'references').mkdir(parents=True)
        (directory/'SKILL.md').write_text('different')
        (directory/'references/domain-templates.md').write_text('different')
        (directory/'references/research-principles.md').write_text('different')
        with self.assertRaises(ValueError):
            self.manifest('--recipe','primary-aa','--candidate-skill-dir',str(directory))

    def test_strategy_change_refuses_existing_manifest_before_dispatch(self):
        args = evaluation.parser().parse_args(self.argv)
        original = evaluation.build_manifest(args)
        args.output_dir.mkdir()
        (args.output_dir/'manifest.json').write_text(json.dumps(original))
        (args.output_dir/'state.json').write_text('{}')
        before = (args.output_dir/'manifest.json').read_bytes()
        changed = self.manifest('--recipe','primary')
        with mock.patch.object(evaluation.subprocess, 'run', side_effect=AssertionError('worker')):
            with self.assertRaisesRegex(ValueError, 'Manifest mismatch'):
                evaluation.run_campaign(args, changed, self.argv)
        self.assertEqual((args.output_dir/'manifest.json').read_bytes(), before)

    def test_saved_schedule_is_reproducible_and_complete(self):
        cases = [{'id':'first'}, {'id':'second'}, {'id':'third'}]
        arms = ['strong_direct','stable']
        first = evaluation.build_cell_schedule(cases,['m1','m2'],[1,2],arms,789)
        self.assertEqual(first, evaluation.build_cell_schedule(cases,['m1','m2'],[1,2],arms,789))
        self.assertNotEqual(first, evaluation.build_cell_schedule(cases,['m1','m2'],[1,2],arms,790))
        self.assertEqual([x['index'] for x in first], list(range(12)))
        self.assertEqual(len({(x['task_id'],x['model'],x['seed']) for x in first}), 12)
        self.assertTrue(all(sorted(x['arm_order']) == sorted(arms) for x in first))
        for group_size in (2,3):
            names = ['a','b','c'][:group_size]
            orders = [evaluation.arm_order(i, names) for i in range(2*group_size)]
            self.assertTrue(all(sum(order[p] == arm for order in orders)==2
                                for arm in names for p in range(group_size)))

    def test_recipe_stop_does_not_spend_unused_allowance(self):
        manifest = self.manifest('--recipe','primary')
        def stop_on_preparation(**kwargs):
            if kwargs['messages'][0]['content'].startswith('Prepare a prompt'):
                raise evaluation.runner.OllamaStopError('unknown_usage', {'attempt_count':1,'retry_count':0,
                    'attempts':[{'status':'failed','prompt_eval_count':None,'eval_count':None}]})
            return self.fake_chat(**kwargs)
        with mock.patch.object(evaluation.runner, 'call_ollama_chat', side_effect=stop_on_preparation):
            record = evaluation.run_cell(manifest,next(evaluation.cells(manifest)),self.root/'stopped.json','http://localhost:11434')
        self.assertEqual(record['status'], 'stopped')
        self.assertEqual(record['stop_reason'], 'unknown_usage')
        self.assertLess(len(record['calls']), manifest['calls_per_cell'])


if __name__ == '__main__':
    unittest.main()
