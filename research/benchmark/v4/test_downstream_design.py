"""An offline design never authorizes or performs provider calls."""
import contextlib
import io
import json
import socket
import tempfile
from pathlib import Path
import unittest
from unittest import mock

try:
    import downstream_design as design
except ModuleNotFoundError:
    design = None

CONFIG = {'tasks':600, 'executors':4, 'seeds_per_executor':2, 'aa_tasks':60,
          'feasibility_tasks':40, 'effect':0.05, 'task_sd':0.40,
          'holdout_custodian':None, 'spend_cap':None,
          'protocol_frozen':False, 'independent_review_complete':False}


class DesignTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(design, 'offline downstream design module is required')

    def test_confirmatory_and_feasibility_reservations(self):
        result = design.build_design(CONFIG)
        self.assertEqual(result['primary_calls'], 24000)
        self.assertEqual(result['incremental_aa_calls'], 1920)
        self.assertEqual(result['confirmatory_calls'], 25920)
        self.assertEqual(result['feasibility_calls'], 1600)
        self.assertFalse(result['calls_enabled'])
        self.assertFalse(result['launch_ready'])
        self.assertEqual(design.required_tasks(0.05, 0.40), 502)

    def test_power_sensitivity_is_not_guaranteed(self):
        self.assertEqual(design.required_tasks(0.05, 0.50), 784)
        self.assertEqual(design.required_tasks(0.05, 1.0), 3136)
        self.assertEqual(design.required_tasks(0.05, 0), 1)
        self.assertIn('approximation', design.build_design(CONFIG)['power_method'])

    def test_unrepresentable_sample_estimate_fails_as_invalid_input(self):
        try:
            design.required_tasks(1e-160, 0.4)
        except Exception as exc:
            error_type = type(exc)
        else:
            error_type = None
        self.assertIs(error_type, ValueError)

    def test_subnormal_inputs_preserve_their_ratio_before_squaring(self):
        self.assertEqual(design.required_tasks(2e-162, 1e-162), 2)
        try:
            zero_variance = design.required_tasks(5e-324, 0)
        except Exception as exc:
            zero_variance = type(exc).__name__
        self.assertEqual(zero_variance, 1)

    def test_cli_reports_unrepresentable_estimate_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / 'config.json'
            config_path.write_text(json.dumps({**CONFIG, 'effect': 1e-160}))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                try:
                    result = design.main(['--config', str(config_path)])
                except Exception as exc:
                    result = type(exc).__name__
            self.assertEqual(result, 1)
            self.assertEqual(output.getvalue(), 'Error: ValueError\n')

    def test_invalid_design_values_fail_closed(self):
        invalid = [{'tasks':True}, {'tasks':0}, {'executors':-1}, {'seeds_per_executor':1.2},
                   {'aa_tasks':601}, {'feasibility_tasks':-1}, {'effect':float('nan')},
                   {'effect':0}, {'task_sd':-0.1}, {'task_sd':float('inf')},
                   {'holdout_custodian':' '}, {'spend_cap':{'currency':'EUR','amount':1}},
                   {'spend_cap':{'currency':'USD','amount':True}}, {'protocol_frozen':1},
                   {'unknown':'x'}]
        for change in invalid:
            with self.subTest(change=change), self.assertRaises(ValueError):
                design.build_design({**CONFIG, **change})

    def test_power_simulation_is_seeded_and_family_aware(self):
        one = design.simulate_task_power(600, .05, .4, family_size=4, n_trials=50, seed=42)
        two = design.simulate_task_power(600, .05, .4, family_size=4, n_trials=50, seed=42)
        self.assertEqual(one, two)
        self.assertEqual(one['independent_families'], 150)
        self.assertEqual(one['method'], 'normal-approximation-planning-simulation')
        self.assertAlmostEqual(one['monte_carlo_se'], (one['rejection_rate'] *
                               (1-one['rejection_rate']) / 50) ** .5)
        for kwargs in [{'n_tasks':0}, {'n_tasks':5,'family_size':2}, {'n_trials':0},
                       {'effect':1,'task_sd':1}, {'family_size':True}]:
            args = dict(n_tasks=10, effect=.05, task_sd=.4, n_trials=5)
            args.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                design.simulate_task_power(**args)

    def test_degenerate_simulation_intervals_are_reported(self):
        result = design.simulate_task_power(10, 0, 0, n_trials=2, seed=42)
        self.assertEqual(result['degenerate_intervals'], 2)
        self.assertEqual(result['degenerate_interval_policy'], 'point interval when sample variance is zero')
        self.assertEqual((result['coverage'], result['rejection_rate']), (1.0, 0.0))

    def test_missing_custody_or_spend_cap_remains_explicit(self):
        result = design.build_design(CONFIG)
        self.assertIn('independent_custody', result['unresolved_prerequisites'])
        self.assertIn('spend_cap', result['unresolved_prerequisites'])
        self.assertEqual(result['authorization_status'], 'not_requested')

    def test_planner_never_dispatches_even_when_populated(self):
        config = {**CONFIG, 'holdout_custodian':'independent custodian',
                  'spend_cap':{'currency':'USD','amount':100}, 'protocol_frozen':True,
                  'independent_review_complete':True}
        with mock.patch.object(socket, 'create_connection', side_effect=AssertionError('network')):
            result = design.build_design(config)
        self.assertFalse(result['launch_ready'])
        self.assertFalse(result['calls_enabled'])
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / 'config.json'
            config_path.write_text(json.dumps(config))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    design.main(['--config', str(config_path), '--run'])
                self.assertEqual(design.main(['--config', str(config_path)]), 0)


if __name__ == '__main__':
    unittest.main()
