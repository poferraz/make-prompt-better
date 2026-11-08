"""Denominators and failures in v3 summaries are not inferred successes."""
import copy
from pathlib import Path
import unittest

import downstream_evaluation as evaluation


class SummaryV3Tests(unittest.TestCase):
    def setUp(self):
        argv = ['--models', 'executor', '--judge-model', 'judge', '--seeds', '1,2,3',
                '--tasks', 'net-apples', '--max-requests', '81', '--deadline-seconds', '30',
                '--candidate-skill-dir', str(evaluation.runner.REPO_ROOT / 'make-prompt-better'),
                '--output-dir', '/tmp/.private/unused']
        self.manifest = evaluation.build_manifest(evaluation.parser().parse_args(argv))
        self.cells = list(evaluation.cells(self.manifest))

    def arm(self, decision='bypass', answer='18', literal_status='passed'):
        return {'decision': decision, 'prompt': 'prompt', 'unchanged': decision == 'bypass',
                'preservation': [{'id': 'constraint-0', 'status': literal_status}],
                'literal_audit': {'status': 'no_literal_omissions_detected'},
                'answer': answer, 'objective_checks': [{'id': 'answer', 'status': 'passed'}]}

    def record(self, index, arms=None, calls=None, comparisons=None):
        return {'identity': self.cells[index], 'status': 'failed', 'arms': arms or {},
                'calls': calls or [], 'comparisons': comparisons or {}}

    def test_summary_separates_expected_launched_available_and_correct(self):
        records = [self.record(0, {'candidate': self.arm()}),
                   self.record(1, calls=[{'stage':'preparation','arm':'candidate','status':'failed'}])]
        state = {'cells': {'0': {'status': 'completed', 'reserved_request_allowance': 27},
                           '1': {'status': 'failed', 'reserved_request_allowance': 27},
                           '2': {'status': 'not_launched', 'reserved_request_allowance': 0}}}
        outcome = evaluation.summarize(self.manifest, state, records)['outcomes']['candidate']
        self.assertEqual((outcome['expected'], outcome['launched_cells'], outcome['answered'],
                          outcome['objective_successes'], outcome['unavailable']), (3, 2, 1, 1, 2))
        self.assertEqual(outcome['objective_rate_answered'], {'numerator':1, 'denominator':1, 'value':1.0})
        self.assertEqual(outcome['delivered_success_rate_launched'],
                         {'numerator':1, 'denominator':2, 'value':0.5})

    def test_missing_reserved_cell_record_keeps_unknown_cost(self):
        state = {'reserved_request_allowance':27,
                 'cells': {'0': {'status':'failed','reserved_request_allowance':27}}}
        result = evaluation.summarize(self.manifest, state, [])
        self.assertEqual(result['outcomes']['candidate']['launched_cells'], 1)
        self.assertIsNone(result['stage_usage']['judge']['eval_count'])
        self.assertEqual(result['stage_usage']['judge']['known_eval_count'], 0)
        self.assertTrue(result['telemetry_incomplete'])

    def test_pair_missing_reason_and_orphan_counts(self):
        pair = 'original__candidate'
        original, candidate = self.arm(), self.arm()
        valid = {'stage':'judge','arm':pair,'status':'completed','parsed_scores':{'delta_total':0}}
        invalid = {'stage':'judge','arm':pair,'status':'failed','format_error':'judge_score_invalid'}
        stopped = {'stage':'judge','arm':pair,'status':'failed','error':'OllamaStopError'}
        records = [self.record(0, {'original':original,'candidate':candidate}, [valid, invalid]),
                   self.record(1, {'original':copy.deepcopy(original),'candidate':copy.deepcopy(candidate)}, [valid, stopped])]
        state = {'cells': {'0': {'status':'failed','reserved_request_allowance':27},
                           '1': {'status':'failed','reserved_request_allowance':27},
                           '2': {'status':'not_launched','reserved_request_allowance':0}}}
        result = evaluation.summarize(self.manifest, state, records)['pair_summaries'][pair]
        self.assertEqual(result['missing_by_reason'], {'judge_format_invalid':1, 'judge_transport_failed':1,
                                                        'cell_not_launched':1})
        self.assertEqual((result['expected_pairs'], result['valid_judge_passes'], result['orphan_valid_passes']),
                         (3, 2, 2))

    def test_preservation_and_routing_labels_are_not_semantic_accuracy(self):
        item = self.arm('rewrite', literal_status='failed')
        item['unchanged'] = True
        record = self.record(0, {'candidate':item})
        state = {'cells': {'0': {'status':'completed'}}}
        result = evaluation.summarize(self.manifest, state, [record])
        self.assertEqual(result['outcomes']['candidate']['preservation']['semantic_review_status'], 'not_evaluated')
        self.assertEqual(result['outcomes']['candidate']['preservation']['literal_checks']['failed'], 1)
        self.assertEqual(result['bypass']['candidate']['routing_expectation_status'], 'advisory_fixture_label')
        self.assertEqual((result['bypass']['candidate']['bypass_count'],
                          result['bypass']['candidate']['unchanged_rewrites']), (0, 1))

    def test_intervals_require_five_distinct_tasks(self):
        from downstream_corpus import load_corpus
        manifest = copy.deepcopy(self.manifest)
        manifest['cases'] = load_corpus()['cases'][:5]
        manifest['seeds'] = [1]
        manifest['cell_schedule'] = evaluation.build_cell_schedule(
            manifest['cases'], manifest['models'], manifest['seeds'], manifest['arms'], None)
        cases = list(evaluation.cells(manifest))
        comparison = {'left_total':20, 'right_total':21, 'delta':1, 'position_consistent':True,
                      'passes':[{'scores':{'delta_total':1}},{'scores':{'delta_total':1}}]}
        records = [{'identity':cell, 'status':'completed', 'arms':{}, 'calls':[],
                    'comparisons':{'original__candidate':comparison}} for cell in cases]
        state = {'cells':{str(i):{'status':'completed'} for i in range(5)}}
        four = evaluation.summarize(manifest, state, records[:4])['pair_summaries']['original__candidate']
        five = evaluation.summarize(manifest, state, records)['pair_summaries']['original__candidate']
        self.assertIsNone(four['task_cluster_95_ci'])
        self.assertIsNotNone(five['task_cluster_95_ci'])
        self.assertEqual(five['interval_method']['task_clusters'], 5)
        self.assertEqual(five['interval_method']['resamples'], 5000)
        self.assertEqual(five['interval_method']['seed'], 42)


if __name__ == '__main__':
    unittest.main()
