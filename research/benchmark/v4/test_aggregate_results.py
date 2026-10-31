import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import aggregate_results as aggregator


class AggregateResultsTests(unittest.TestCase):
    def test_gain_percentage_uses_unrounded_paired_scores(self):
        metrics = {"model": "example", "tests": {}}
        for tid, optimized in [(1, 15), (2, 15), (3, 17)]:
            metrics["tests"][str(tid)] = {"evaluation": {"parsed": {
                "baseline_total": 15, "optimized_total": optimized,
                "delta_total": optimized - 15,
                "winner": "Optimized" if optimized > 15 else "Tie"}}, "word_overhead_ratio": 1}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            model_dir = results / "example"
            model_dir.mkdir(parents=True)
            (model_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
            with mock.patch.object(aggregator, "RESULTS_ROOT", results), \
                 mock.patch.object(aggregator, "REPO_ROOT", root):
                aggregator.main()
            report = (results / "AGGREGATED_METRICS.md").read_text(encoding="utf-8")

        self.assertIn("| +4.4% |", report)

    def test_average_delta_uses_unrounded_paired_scores(self):
        metrics = {"model": "example", "tests": {}}
        for tid, baseline, optimized in [(1, 20, 21), (2, 20, 21.5), (3, 20.5, 21.5)]:
            metrics["tests"][str(tid)] = {"evaluation": {"parsed": {
                "baseline_total": baseline, "optimized_total": optimized,
                "delta_total": optimized - baseline, "winner": "Optimized"}},
                "word_overhead_ratio": 1}
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp)
            model_dir = results / "example"
            model_dir.mkdir()
            (model_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
            with mock.patch.object(aggregator, "RESULTS_ROOT", results):
                result = aggregator.collect_all_models()[0]

        self.assertEqual(result["avg_baseline"], 20.17)
        self.assertEqual(result["avg_optimized"], 21.33)
        self.assertEqual(result["avg_delta"], 1.17)

    def test_invalid_dimension_and_conflicting_total_are_reported_without_rewriting_scores(self):
        metrics = {
            "model": "example:cloud",
            "tests": {
                "9": {"evaluation": {
                    "content": "| TOTAL | **18.5/25** | **9.5/25** | +9 |",
                    "parsed": {
                        "baseline_total": 18.5, "optimized_total": 12.5, "delta_total": -6,
                        "winner": "Baseline", "dimensions": {
                            "traceability": {"baseline": 0.5, "optimized": 5, "delta": 4.5}}}},
                    "word_overhead_ratio": 1},
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            model_dir = results / "example-cloud"
            model_dir.mkdir(parents=True)
            (model_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
            with mock.patch.object(aggregator, "RESULTS_ROOT", results), \
                 mock.patch.object(aggregator, "REPO_ROOT", root):
                records = aggregator.collect_all_models()
                aggregator.main()
            report = (results / "AGGREGATED_METRICS.md").read_text(encoding="utf-8")

        test = records[0]["tests"]["9"]
        self.assertEqual(test["optimized_total"], 12.5)
        self.assertTrue(any("traceability baseline" in issue for issue in test.get("score_issues", [])))
        self.assertTrue(any("written optimized total" in issue for issue in test.get("score_issues", [])))
        self.assertTrue(any("written total delta" in issue for issue in test.get("score_issues", [])))
        self.assertIn("example:cloud", report)
        self.assertIn("traceability baseline", report)
        self.assertIn("written optimized total", report)
        self.assertIn("written total delta", report)

    def test_unfinished_evaluation_table_is_not_counted_as_a_completed_test(self):
        report = """## TEST 1: Example
### EVALUATION: TEST 1
| TOTAL | 20/25 | 22/25 | +2 |
## TEST 2: Unfinished
### EVALUATION: TEST 2
The score table is not written yet.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EVALUATION_RESULTS.md"
            path.write_text(report, encoding="utf-8")
            result = aggregator.parse_markdown_eval_file(path, "example")

        self.assertEqual(result["completed_tests"], 1)
        self.assertEqual(result["avg_delta"], 2)
        self.assertNotIn("2", result["tests"])

    def test_missing_word_ratio_is_not_reported_as_zero_overhead(self):
        report = """## TEST 1: Example
### EVALUATION: TEST 1
| Dimension | Baseline | Optimized | Delta |
| Accuracy | 4 | 5 | +1 |
| Completeness | 4 | 5 | +1 |
| Structure | 4 | 5 | +1 |
| Actionability | 4 | 5 | +1 |
| Traceability | 4 | 5 | +1 |
Baseline Words: {{B1}} | Optimized Words: {{O1}} | Overhead Ratio: {{R1}}x
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EVALUATION_RESULTS.md"
            path.write_text(report, encoding="utf-8")
            result = aggregator.parse_markdown_eval_file(path, "example")

        self.assertIsNone(result["tests"]["1"]["word_overhead_ratio"])
        self.assertIsNone(result["avg_word_overhead_ratio"])

    def test_saved_tests_override_an_older_summary_after_a_resumed_run(self):
        metrics = {
            "model": "example:cloud",
            "summary": {
                "completed_tests": 1, "avg_baseline": 10, "avg_optimized": 16,
                "avg_delta": 6, "wins": 1, "ties": 0, "losses": 0,
            },
            "tests": {
                "1": {"evaluation": {"parsed": {
                    "baseline_total": 10, "optimized_total": 16,
                    "delta_total": 6, "winner": "Optimized"}}, "word_overhead_ratio": 2},
                "2": {"evaluation": {"parsed": {
                    "baseline_total": 20, "optimized_total": 22,
                    "delta_total": 2, "winner": "Optimized"}}, "word_overhead_ratio": 1},
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp)
            model_dir = results / "example-cloud"
            model_dir.mkdir()
            (model_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
            with mock.patch.object(aggregator, "RESULTS_ROOT", results):
                records = aggregator.collect_all_models()

        self.assertEqual(len(records), 1)
        result = records[0]
        self.assertEqual(result["completed_tests"], 2)
        self.assertEqual(result["avg_baseline"], 15)
        self.assertEqual(result["avg_optimized"], 19)
        self.assertEqual(result["avg_delta"], 4)
        self.assertEqual(result["avg_word_overhead_ratio"], 1.5)
        self.assertEqual((result["wins"], result["ties"], result["losses"]), (2, 0, 0))


if __name__ == "__main__":
    unittest.main()
