import os
import random
import unittest

import blind_stats_engine as stats


class SeededStatisticsTests(unittest.TestCase):
    def test_bootstrap_and_assignment_invariants(self):
        seed = int(os.environ.get('TEST_SEED', '42'))
        rng = random.Random(seed)
        for case in range(int(os.environ.get('TEST_CASES', '100'))):
            with self.subTest(seed=seed, case=case):
                values = [rng.randint(-20, 20) for _ in range(rng.randint(1, 15))]
                result = stats.bootstrap_mean_ci(values, n_resamples=100, seed=seed + case)
                self.assertEqual(result, stats.bootstrap_mean_ci(values, n_resamples=100, seed=seed + case))
                self.assertAlmostEqual(result[0], sum(values) / len(values), places=3)
                self.assertLessEqual(min(values), result[1])
                self.assertLessEqual(result[1], result[2])
                self.assertLessEqual(result[2], max(values))
                mapping = stats.deterministic_ab_assignment(seed, str(case), case)
                self.assertEqual(set(mapping.values()), {'baseline', 'optimized'})
                self.assertEqual(mapping, stats.deterministic_ab_assignment(seed, str(case), case))

    def test_sign_flip_invariants(self):
        self.assertEqual(stats.paired_sign_flip_p_value([]), 1.0)
        self.assertEqual(stats.paired_sign_flip_p_value([0, 0]), 1.0)
        self.assertEqual(stats.paired_sign_flip_p_value([1, 1, 1]), 0.25)
        self.assertEqual(stats.paired_sign_flip_p_value([-1, -1, -1]), 0.25)
