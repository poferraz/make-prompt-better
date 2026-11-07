import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import summarize_runs as summarizer

SCRIPT = Path(__file__).with_name("summarize_runs.py")


def record(model, skill, delta):
    return {
        "model": model,
        "manifest": {"schema": 1, "model": model, "judge_model": model, "skill_sha256": skill,
                     "test_suite_sha256": "suite", "runner_sha256": "runner", "judge_code_sha256": "judge",
                     "host_sha256": "host", "test_ids": [1], "timeout": 10, "blind_eval": True,
                     "swap_positions": False, "strip_cert_markers": False, "unprescribed_routing": False,
                     "seed": 42, "loading_strategy": "full"},
        "tests": {"1": {"judge_model": model, "self_judged": True,
                       "evaluation": {"parsed": {"baseline_total": 15, "optimized_total": 15 + delta,
                                                  "delta_total": delta}}}},
    }


class RunSummaryTests(unittest.TestCase):
    def test_schema_two_strict_protocol_is_supported_and_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for schema in (1, 2):
                folder = root / str(schema)
                folder.mkdir()
                data = record(str(schema), 'same', 1)
                if schema == 2:
                    data['manifest'].update(schema=2, protocol='outcome-v2', skill_dir='/skill',
                        strict_preservation=True, max_output_tokens=100, pricing_status='unknown')
                (folder / 'metrics.json').write_text(json.dumps(data))
            self.assertEqual(len(summarizer.summarize(root)['groups']), 2)

    def test_migrated_run_is_not_grouped_with_unmigrated_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, migrated in [('one', False), ('two', True)]:
                folder = root / name
                folder.mkdir()
                data = record(name, 'same-skill', 1)
                if migrated:
                    data['previous_manifests'] = [dict(data['manifest'], runner_sha256='old-runner')]
                (folder / 'metrics.json').write_text(json.dumps(data))
            groups = summarizer.summarize(root)['groups']
            self.assertEqual(len(groups), 2)
            self.assertTrue(any(g['protocol'].get('previous_runner_sha256') == ['old-runner'] for g in groups))

    def test_incompatible_skills_are_kept_in_separate_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, skill, delta in [("one", "a", 1), ("two", "a", 3), ("three", "b", -2)]:
                folder = root / name
                folder.mkdir()
                (folder / "metrics.json").write_text(json.dumps(record(name, skill, delta)))
            output = root / "summary.json"
            result = subprocess.run([sys.executable, str(SCRIPT), "--results-dir", str(root), "--output", str(output)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.read_text())
            self.assertEqual(data, summarizer.summarize(root))
            groups = data["groups"]
            self.assertEqual(sorted((g["pairs"], g["mean_delta"]) for g in groups), [(1, -2), (2, 2)])
            before = output.read_bytes()
            with mock.patch.object(sys, "argv", ["summary", "--results-dir", str(root), "--output", str(output)]):
                self.assertNotEqual(summarizer.main(), 0)
            self.assertEqual(output.read_bytes(), before)

    def test_legacy_or_inconsistent_judge_is_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "one"
            folder.mkdir()
            output = root / "summary.json"
            for metrics in ({"model": "legacy", "tests": {}}, record("one", "a", 1)):
                if "manifest" in metrics:
                    metrics["tests"]["1"]["judge_model"] = "different"
                (folder / "metrics.json").write_text(json.dumps(metrics))
                with self.assertRaises(ValueError):
                    summarizer.summarize(root)
                result = subprocess.run([sys.executable, str(SCRIPT), "--results-dir", str(root), "--output", str(output)],
                                        text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("manifest" if "manifest" not in metrics else "judge", result.stderr.lower())
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
