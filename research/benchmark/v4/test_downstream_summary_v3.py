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
        self.assertIn('objective_rate_graded', outcome)
        self.assertIn('delivered_success_rate_observed', outcome)
        self.assertEqual(outcome['objective_rate_graded'], {'numerator':1, 'denominator':1, 'value':1.0})
        self.assertEqual(outcome['delivered_success_rate_observed'],
                         {'numerator':1, 'denominator':2, 'value':0.5})

    def test_pair_includes_known_preparation_failure_as_service_failure(self):
        failure = {'stage':'preparation', 'arm':'candidate', 'status':'failed',
                   'format_error':'preparation_json_invalid'}
        record = self.record(0, {'original':self.arm()}, [failure])
        state = {'cells': {'0': {'status':'failed','reserved_request_allowance':27}}}
        result = evaluation.summarize(self.manifest, state, [record])
        outcome = result['outcomes']['candidate']
        self.assertIn('workflow_dispositions', outcome)
        self.assertIn('paired_service_outcomes', result)
        self.assertEqual(outcome['workflow_dispositions']['failure'], 1)
        self.assertEqual(outcome['delivered_success_rate_observed'],
                         {'numerator':0, 'denominator':1, 'value':0.0})
        pair = result['paired_service_outcomes']['original__candidate']
        self.assertEqual((pair['expected_pairs'], pair['observed_pairs'], pair['mean_delta']), (3, 1, -1.0))
        self.assertEqual((pair['pairs'][0]['left_success'], pair['pairs'][0]['right_success']), (True, False))

    def test_stopped_before_arm_starts_is_not_a_failed_workflow(self):
        stopped = {'stage':'preparation', 'arm':'candidate', 'status':'failed', 'error':'OllamaStopError'}
        record = self.record(0, calls=[stopped])
        state = {'cells': {'0': {'status':'failed','reserved_request_allowance':27}}}
        result = evaluation.summarize(self.manifest, state, [record])
        original = result['outcomes']['original']
        self.assertIn('workflow_dispositions', original)
        self.assertEqual(original['workflow_dispositions']['not_started'], 3)
        self.assertEqual(original['workflow_dispositions']['failure'], 0)
        self.assertEqual(original['delivered_success_rate_observed'],
                         {'numerator':0, 'denominator':0, 'value':None})
        self.assertNotIn('delivered_success_rate_launched', original)
        pair = result['paired_service_outcomes']['original__candidate']
        self.assertEqual(pair['observed_pairs'], 0)
        self.assertEqual(sum(pair['missing_by_disposition'].values()), 3)

    def test_running_and_missing_reserved_workflows_remain_unknown(self):
        running = {'stage':'preparation', 'arm':'candidate', 'status':'running'}
        record = self.record(0, calls=[running])
        state = {'cells': {'0': {'status':'failed','reserved_request_allowance':27},
                           '1': {'status':'failed','reserved_request_allowance':27},
                           '2': {'status':'not_launched','reserved_request_allowance':0}}}
        outcome = evaluation.summarize(self.manifest, state, [record])['outcomes']['candidate']
        self.assertIn('workflow_dispositions', outcome)
        self.assertEqual(outcome['workflow_dispositions'], {'success':0, 'failure':0, 'ungraded':0,
                         'incomplete':1, 'not_started':1, 'missing_record':1})
        self.assertEqual(outcome['delivered_success_rate_observed']['denominator'], 0)

    def test_ungraded_answer_is_not_imputed_as_failed(self):
        state = {'cells': {'0': {'status':'completed','reserved_request_allowance':27}}}
        for checks in ([], [{'id':'answer', 'status':'failed', 'error':'ambiguous check error'}],
                       [{'id':'answer', 'status':'unknown'}]):
            with self.subTest(checks=checks):
                candidate = self.arm()
                candidate['objective_checks'] = checks
                record = self.record(0, {'original':self.arm(), 'candidate':candidate})
                result = evaluation.summarize(self.manifest, state, [record])
                outcome = result['outcomes']['candidate']
                self.assertIn('workflow_dispositions', outcome)
                self.assertEqual((outcome['answered'], outcome['objective_failures'],
                                  outcome['ungraded_answers'], outcome['workflow_dispositions']['ungraded']), (1, 0, 1, 1))
                self.assertEqual(outcome['objective_rate_graded']['denominator'], 0)
                if checks and 'error' in checks[0]:
                    self.assertEqual(outcome['objective_checks']['failed'], 0)
                    self.assertEqual(outcome['objective_check_errors'], 1)
                self.assertEqual(result['paired_service_outcomes']['original__candidate']['observed_pairs'], 0)

    def test_explicit_pre_dispatch_rejection_is_a_workflow_rejection(self):
        rejected = {'stage':'execution', 'arm':'original', 'status':'failed',
                    'error':'InputLimitExceeded', 'dispatched':False, 'reserved_attempts':0}
        record = self.record(0, {'original':{'decision':'original', 'prompt':'x', 'unchanged':True,
                                             'preservation':[], 'literal_audit':{'status':'passed'}}}, [rejected])
        state = {'cells': {'0': {'status':'failed','reserved_request_allowance':27}}}
        result = evaluation.summarize(self.manifest, state, [record])
        outcome = result['outcomes']['original']
        self.assertIn('workflow_dispositions', outcome)
        self.assertEqual(outcome['workflow_dispositions']['failure'], 1)
        self.assertEqual(outcome['pre_dispatch_rejections'], 1)
        self.assertIn('execution_call_records', outcome)
        self.assertEqual((outcome['execution_call_records'], outcome['execution_launch_intents']), (1, 0))
        self.assertEqual(result['stage_usage']['execution']['attempt_count'], 0)
        self.assertNotIn('execution_attempts', outcome)

    def test_known_failed_check_is_not_hidden_by_another_check_error(self):
        candidate = self.arm()
        candidate['objective_checks'] = [{'id':'first', 'status':'failed'},
                                         {'id':'second', 'status':'failed', 'error':'ambiguous error'}]
        record = self.record(0, {'original':self.arm(), 'candidate':candidate})
        state = {'cells': {'0': {'status':'completed','reserved_request_allowance':27}}}
        result = evaluation.summarize(self.manifest, state, [record])
        outcome = result['outcomes']['candidate']
        self.assertEqual((outcome['objective_failures'], outcome['ungraded_answers']), (1, 0))
        self.assertEqual(outcome['workflow_dispositions']['failure'], 1)
        self.assertEqual(result['paired_service_outcomes']['original__candidate']['mean_delta'], -1.0)

    def test_answer_conflicting_with_unfinished_or_failed_call_remains_unknown(self):
        candidate = self.arm()
        candidate['objective_checks'][0]['status'] = 'failed'
        state = {'cells': {'0': {'status':'failed','reserved_request_allowance':27}}}
        for stage, status in (('execution', 'running'), ('execution', 'failed'), ('preparation', 'failed')):
            with self.subTest(stage=stage, status=status):
                call = {'stage':stage, 'arm':'candidate', 'status':status}
                record = self.record(0, {'original':self.arm(), 'candidate':candidate}, [call])
                result = evaluation.summarize(self.manifest, state, [record])
                outcome = result['outcomes']['candidate']
                self.assertEqual(outcome['workflow_dispositions']['incomplete'], 1)
                self.assertEqual((outcome['objective_failures'], outcome['ungraded_answers']), (0, 1))
                self.assertEqual(result['paired_service_outcomes']['original__candidate']['observed_pairs'], 0)
                pair = result['objective_pairs']['original__candidate']
                self.assertIn('paired_graded_answers', pair)
                self.assertEqual((pair['answer_text_pairs'], pair['paired_graded_answers']), (1, 0))

    def test_malformed_check_records_do_not_create_a_failure_or_crash(self):
        state = {'cells': {'0': {'status':'failed','reserved_request_allowance':27}}}
        for checks in ([{}], [None], None):
            with self.subTest(checks=checks):
                candidate = self.arm()
                candidate['objective_checks'] = checks
                record = self.record(0, {'original':self.arm(), 'candidate':candidate})
                try:
                    result = evaluation.summarize(self.manifest, state, [record])
                except (KeyError, TypeError) as exc:
                    self.fail(f'malformed check crashed summary: {type(exc).__name__}')
                outcome = result['outcomes']['candidate']
                self.assertEqual((outcome['objective_failures'], outcome['ungraded_answers']), (0, 1))
                self.assertEqual(outcome['workflow_dispositions']['ungraded'], 1)

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
