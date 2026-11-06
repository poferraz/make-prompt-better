import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import run_ollama_benchmarks as runner


SCORES = """| Dimension | Baseline | Optimized | Delta |
| Accuracy | 4 | 5 | +1 |
| Completeness | 4 | 5 | +1 |
| Structure | 4 | 5 | +1 |
| Actionability | 4 | 5 | +1 |
| Traceability | 4 | 5 | +1 |
"""


def response(content):
    return {"content": content, "words": len(content.split()), "eval_count": 1,
            "prompt_eval_count": 1, "elapsed_seconds": 0}


class ProvenanceTests(unittest.TestCase):
    def test_dry_run_estimates_calls_without_creating_results_or_using_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "runs"
            args = ["runner", "--models", "model", "--tests", "1,2", "--swap-positions",
                    "--results-dir", str(result_root), "--run-id", "sample", "--dry-run"]
            with mock.patch.object(sys, "argv", args), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=AssertionError("network used")):
                try:
                    result = runner.main()
                except SystemExit as exc:
                    self.fail(f"Dry run options were rejected: {exc}")
                self.assertEqual(result, 0)
            self.assertFalse(result_root.exists())

    def test_request_limit_rejects_run_before_model_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_root = Path(tmp) / "runs"
            args = ["runner", "--models", "model", "--tests", "1", "--results-dir", str(result_root),
                    "--run-id", "sample", "--max-requests", "1"]
            with mock.patch.object(sys, "argv", args), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=AssertionError("network")):
                self.assertNotEqual(runner.main(), 0)
            self.assertFalse(result_root.exists())

    def test_remote_cleartext_requires_explicit_opt_in(self):
        args = ["runner", "--models", "model", "--tests", "1", "--host", "http://example.com"]
        with mock.patch.object(sys, "argv", args), \
             mock.patch.object(runner, "run_model_benchmark", return_value=False) as run_model:
            self.assertNotEqual(runner.main(), 0)
            run_model.assert_not_called()

    def test_library_entrypoint_rejects_remote_cleartext_before_requests(self):
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(runner, "RESULTS_ROOT", Path(tmp)), \
             mock.patch.object(runner, "call_ollama_chat", return_value=response("unused")) as chat:
            try:
                runner.run_model_benchmark("model", "skill", [1], "http://example.com")
            except ValueError as exc:
                self.assertIn("remote cleartext", str(exc))
            else:
                self.fail("Remote cleartext was accepted by the library entry point")
            chat.assert_not_called()

    def test_template_numbers_match_domains(self):
        expected = {1: 1, 2: 9, 3: 7, 4: 8, 5: 3, 6: 5, 7: 4, 8: 2,
                    9: 6, 10: 10, 11: 11, 12: 12}
        for case in runner.TEST_CASES:
            with self.subTest(domain=case["domain"]):
                self.assertRegex(case["target_mode"], rf"Template {expected[case['id']]}(?:\D|$)")

    def test_changed_protocol_cannot_resume_or_change_existing_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            outputs = iter(map(response, ["baseline", "prompt", "answer", SCORES, "report"]))
            with mock.patch.object(runner, "REPO_ROOT", root), \
                 mock.patch.object(runner, "RESULTS_ROOT", results), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=lambda **kw: next(outputs)):
                self.assertTrue(runner.run_model_benchmark("model", "skill A", [1], "http://localhost", False, 10))
            path = results / "model/metrics.json"
            original = path.read_bytes()
            changes = [{"skill_bundle": "skill B"}, {"seed": 999}, {"judge_model": "other"},
                       {"swap_positions": True}, {"unprescribed_routing": True}, {"host": "http://127.0.0.1"}]
            for changed in changes:
                with self.subTest(changed=changed), mock.patch.object(runner, "REPO_ROOT", root), \
                     mock.patch.object(runner, "RESULTS_ROOT", results), \
                     mock.patch.object(runner, "call_ollama_chat", side_effect=AssertionError("network used")):
                    options = dict(model="model", skill_bundle="skill A", test_ids=[1],
                                   host="http://localhost", resume=True, timeout=10)
                    options.update(changed)
                    with self.assertRaisesRegex(ValueError, "manifest"):
                        runner.run_model_benchmark(**options)
                    self.assertEqual(path.read_bytes(), original)

    def test_legacy_results_and_no_resume_cannot_overwrite_old_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "model/metrics.json"
            path.parent.mkdir()
            path.write_text('{"tests": {"1": {"legacy": true}}, "summary": {"completed_tests": 1}, "final_report_md": "old"}')
            (path.parent / "EVALUATION_RESULTS.md").write_text("old report")
            original = path.read_bytes()
            with mock.patch.object(runner, "RESULTS_ROOT", root), \
                 mock.patch.object(runner, "REPO_ROOT", root), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=RuntimeError("no network")):
                for resume in (True, False):
                    with self.subTest(resume=resume), self.assertRaises((ValueError, FileExistsError)):
                        runner.run_model_benchmark("model", "skill", [1], resume=resume)
                    self.assertEqual(path.read_bytes(), original)

    def test_locked_model_run_does_not_touch_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".model.lock").mkdir()
            with mock.patch.object(runner, "RESULTS_ROOT", root), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=AssertionError("network used")):
                with self.assertRaisesRegex(RuntimeError, "locked"):
                    runner.run_model_benchmark("model", "skill", [1])
            self.assertFalse((root / "model").exists())

    def test_invalid_model_slug_cannot_escape_result_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runs"
            with mock.patch.object(runner, "RESULTS_ROOT", root), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=AssertionError("network used")):
                try:
                    runner.run_model_benchmark("..", "skill", [1])
                except Exception as exc:
                    self.assertIsInstance(exc, ValueError)
                    self.assertIn("model", str(exc))
                else:
                    self.fail("Unsafe model slug was accepted")
            self.assertFalse((Path(tmp) / "metrics.json").exists())

    def test_completed_stages_survive_and_resume_after_executor_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            first = iter([response("baseline"), response("prompt"), RuntimeError("executor failed")])
            calls = []

            def fail_on_executor(**kwargs):
                calls.append(kwargs["messages"][0]["content"])
                item = next(first)
                if isinstance(item, Exception):
                    raise item
                return item

            with mock.patch.object(runner, "REPO_ROOT", root), \
                 mock.patch.object(runner, "RESULTS_ROOT", results), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=fail_on_executor):
                self.assertFalse(runner.run_model_benchmark("model", "skill", [1], resume=False))
            self.assertTrue((results / "model/metrics.json").exists())
            saved = json.loads((results / "model/metrics.json").read_text())
            self.assertIn("in_progress", saved)
            self.assertEqual(saved["in_progress"]["1"]["baseline"]["response"]["content"], "baseline")
            self.assertEqual(saved["in_progress"]["1"]["optimize"]["response"]["content"], "prompt")
            rest = iter(map(response, ["answer", SCORES, "report"]))
            with mock.patch.object(runner, "REPO_ROOT", root), \
                 mock.patch.object(runner, "RESULTS_ROOT", results), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=lambda **kw: next(rest)):
                self.assertTrue(runner.run_model_benchmark("model", "skill", [1], resume=True))
            saved = json.loads((results / "model/metrics.json").read_text())
            self.assertEqual(saved["tests"]["1"]["baseline"]["content"], "baseline")
            self.assertEqual(saved["tests"]["1"]["optimized_prompt"]["content"], "prompt")

    def test_swapped_judge_responses_and_assignments_are_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            replies = iter(map(response, ["baseline", "prompt", "answer", SCORES, SCORES, "report"]))
            with mock.patch.object(runner, "REPO_ROOT", root), \
                 mock.patch.object(runner, "RESULTS_ROOT", results), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=lambda **kw: next(replies)):
                self.assertTrue(runner.run_model_benchmark("model", "skill", [1], resume=False, swap_positions=True))
            saved = json.loads((results / "model/metrics.json").read_text())
            evaluation = saved["tests"]["1"]["evaluation"]
            self.assertIn("passes", evaluation)
            self.assertEqual(evaluation["passes"][0]["content"], SCORES)
            self.assertEqual(evaluation["passes"][1]["content"], SCORES)
            self.assertEqual(evaluation["passes"][0]["mapping"]["A"], evaluation["passes"][1]["mapping"]["B"])

    def test_natural_routing_is_not_reported_as_a_prescribed_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            replies = iter(map(response, ["baseline", "prompt", "answer", SCORES, "report"]))
            with mock.patch.object(runner, "RESULTS_ROOT", root), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=lambda **kw: next(replies)):
                self.assertTrue(runner.run_model_benchmark("model", "skill", [1], resume=False,
                                                           unprescribed_routing=True))
            saved = json.loads((root / "model/metrics.json").read_text())
            request = saved["in_progress"]["1"]["optimize"]["request"]["messages"][0]["content"]
            self.assertNotIn("Required Mode & Template", request)
            self.assertIn("Unprescribed", saved["tests"]["1"]["target_mode"])


if __name__ == "__main__":
    unittest.main()
