import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_ollama_benchmarks as runner


def stream(*frames):
    return io.BytesIO(b"\n".join(json.dumps(frame).encode("utf-8") for frame in frames) + b"\n")


class ChatStreamingTests(unittest.TestCase):
    @mock.patch.object(runner.time, "sleep")
    def test_stream_combines_content_and_preserves_final_token_counts(self, _sleep):
        def response(request, timeout):
            payload = json.loads(request.data)
            if not payload["stream"]:
                return stream({"message": {"content": "buffered response"}, "done": True})
            return stream(
                {"message": {"role": "assistant", "thinking": "thinking", "content": "Hello"}, "done": False},
                {"message": {"role": "assistant", "content": " world"}, "done": False},
                {"message": {"role": "assistant", "content": "!"}, "done": True,
                 "prompt_eval_count": 17, "eval_count": 3},
            )

        with mock.patch.object(runner.urllib.request, "urlopen", side_effect=response):
            result = runner.call_ollama_chat("model", [{"role": "user", "content": "hi"}])

        self.assertEqual(result["content"], "Hello world!")
        self.assertEqual(result["words"], 2)
        self.assertEqual(result["prompt_eval_count"], 17)
        self.assertEqual(result["eval_count"], 3)

    @mock.patch.object(runner.time, "sleep")
    def test_incomplete_stream_retries_without_including_partial_content(self, _sleep):
        responses = [
            stream({"message": {"content": "partial"}, "done": False}),
            stream({"message": {"content": "complete"}, "done": True, "eval_count": 1}),
        ]
        with mock.patch.object(runner.urllib.request, "urlopen", side_effect=responses):
            result = runner.call_ollama_chat("model", [], max_retries=2, initial_delay=0)

        self.assertEqual(result["content"], "complete")
        self.assertEqual(result["eval_count"], 1)

    @mock.patch.object(runner.time, "sleep")
    def test_truncated_json_frame_retries_instead_of_saving_a_partial_answer(self, _sleep):
        responses = [
            io.BytesIO(b'{"message":{"content":"partial'),
            stream({"message": {"content": "complete"}, "done": True}),
        ]
        with mock.patch.object(runner.urllib.request, "urlopen", side_effect=responses):
            try:
                result = runner.call_ollama_chat("model", [], max_retries=2, initial_delay=0)
            except json.JSONDecodeError:
                self.fail("A truncated stream frame should be retried")

        self.assertEqual(result["content"], "complete")

    @mock.patch.object(runner.time, "sleep")
    def test_stream_error_does_not_return_a_successful_response(self, _sleep):
        response = stream({"error": "unexpected EOF"})
        with mock.patch.object(runner.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex((RuntimeError, OSError), "unexpected EOF"):
                runner.call_ollama_chat("model", [], max_retries=1)

    @mock.patch.object(runner.time, "sleep")
    def test_thinking_only_stream_cannot_be_saved_as_an_answer(self, _sleep):
        response = stream({"message": {"thinking": "thinking", "content": ""}, "done": True})
        with mock.patch.object(runner.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex((RuntimeError, OSError), "without response content"):
                runner.call_ollama_chat("model", [], max_retries=1)


class BenchmarkResumeTests(unittest.TestCase):
    def test_resume_refreshes_a_report_older_than_the_saved_tests(self):
        response = {"content": "original", "words": 1, "eval_count": 1}
        tests = {}
        for tid in (1, 2):
            tests[str(tid)] = {
                "id": tid, "domain": "Example", "task_type": "Accuracy", "target_mode": "Mode 1",
                "baseline": response, "optimized_prompt": response, "optimized_response": response,
                "evaluation": {"content": "", "parsed": {"baseline_total": 20,
                    "optimized_total": 21, "delta_total": 1, "winner": "Optimized"}},
                "word_overhead_ratio": 1,
            }
        metrics = {"model": "model", "tests": tests, "summary": {"completed_tests": 1},
                   "final_report_md": "Report covering only one test"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            model_dir = results / "model"
            model_dir.mkdir(parents=True)
            metrics_path = model_dir / "metrics.json"
            metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
            (model_dir / "EVALUATION_RESULTS.md").write_text("Old report", encoding="utf-8")
            with mock.patch.object(runner, "REPO_ROOT", root), \
                 mock.patch.object(runner, "RESULTS_ROOT", results), \
                 mock.patch.object(runner, "call_ollama_chat", return_value={"content": "Fresh synthesis"}):
                runner.run_model_benchmark("model", "", [1, 2], "http://localhost", True, 10)
            updated = json.loads(metrics_path.read_text(encoding="utf-8"))

        self.assertEqual(updated["summary"]["completed_tests"], 2)
        self.assertIn("Fresh synthesis", updated["final_report_md"])

    def test_guardrail_augmented_prompt_is_saved_as_the_executor_received_it(self):
        evaluation = """| Dimension | Baseline | Optimized | Delta |
| Accuracy | 4 | 5 | +1 |
| Completeness | 4 | 5 | +1 |
| Structure | 4 | 5 | +1 |
| Actionability | 4 | 5 | +1 |
| Traceability | 4 | 5 | +1 |
"""
        contents = iter(["baseline", "Review the function", "optimized answer", evaluation, "final report"])
        calls = []

        def chat(*, model, messages, host, timeout):
            calls.append(messages[0]["content"])
            content = next(contents)
            return {"content": content, "words": len(content.split()), "eval_count": 1,
                    "prompt_eval_count": 1, "elapsed_seconds": 0}

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results"
            with mock.patch.object(runner, "REPO_ROOT", root), \
                 mock.patch.object(runner, "RESULTS_ROOT", results), \
                 mock.patch.object(runner, "call_ollama_chat", side_effect=chat):
                self.assertTrue(runner.run_model_benchmark("model", "", [1], "http://localhost", False, 10))
            saved = json.loads((results / "model" / "metrics.json").read_text(encoding="utf-8"))
            report = (results / "model" / "EVALUATION_RESULTS.md").read_text(encoding="utf-8")

        test = saved["tests"]["1"]
        self.assertEqual(test["optimized_prompt"]["content"], "Review the function")
        self.assertEqual(test.get("executed_optimized_prompt"), calls[2])
        self.assertIn("def calculate_discount", calls[2])
        self.assertIn("### EXECUTED OPTIMIZED PROMPT", report)

    def test_resume_preserves_an_existing_complete_report(self):
        response = {"content": "original", "words": 1, "eval_count": 1}
        metrics = {
            "model": "model",
            "tests": {
                "1": {
                    "id": 1, "domain": "Code Review", "task_type": "Accuracy",
                    "target_mode": "Mode 1", "baseline": response, "optimized_prompt": response,
                    "optimized_response": response,
                    "evaluation": {"content": "", "parsed": {
                        "baseline_total": 1, "optimized_total": 2, "delta_total": 1,
                        "winner": "Optimized"}},
                    "word_overhead_ratio": 1,
                }
            },
            "summary": {"completed_tests": 1},
            "final_report_md": "Original final report",
        }
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp)
            model_dir = results / "model"
            model_dir.mkdir()
            metrics_path = model_dir / "metrics.json"
            report_path = model_dir / "EVALUATION_RESULTS.md"
            metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
            report_path.write_text("Original report", encoding="utf-8")
            with mock.patch.object(runner, "RESULTS_ROOT", results), \
                 mock.patch.object(runner.Path, "relative_to", return_value=Path("results/model")), \
                 mock.patch.object(runner, "call_ollama_chat", return_value={"content": "replacement"}):
                runner.run_model_benchmark("model", "", [1], "http://localhost", True, 10)

            self.assertEqual(json.loads(metrics_path.read_text(encoding="utf-8")), metrics)
            self.assertEqual(report_path.read_text(encoding="utf-8"), "Original report")

    def test_markdown_rendering_normalizes_dashes_without_mutating_raw_metrics(self):
        text = "Range 1\u20132, followed by an aside\u2014with detail."
        metrics = {"tests": {}, "final_report_md": text}
        report = runner.render_markdown_report("model", metrics, text)

        self.assertNotIn("\u2013", report)
        self.assertNotIn("\u2014", report)
        self.assertIn("Range 1-2", report)
        self.assertEqual(metrics["final_report_md"], text)


class BenchmarkValidityTests(unittest.TestCase):
    def test_unparseable_evaluation_cannot_be_counted_as_a_zero_score_tie(self):
        with self.assertRaises(ValueError):
            runner.parse_scores("The evaluation did not contain a score table.")

    def test_main_reports_failure_when_requested_tests_remain_incomplete(self):
        with mock.patch.object(sys, "argv", ["runner", "--models", "model"]), \
             mock.patch.object(runner, "load_skill_bundle", return_value=""), \
             mock.patch.object(runner, "run_model_benchmark", return_value=False):
            self.assertEqual(runner.main(), 1)


if __name__ == "__main__":
    unittest.main()
