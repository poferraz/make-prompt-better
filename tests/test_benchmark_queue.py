import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BenchmarkQueueTests(unittest.TestCase):
    def test_failed_models_make_queue_fail_without_running_legacy_aggregator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "research/benchmark/v4").mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/run_benchmarks_queue.sh", root / "scripts/queue.sh")
            fakebin = root / "bin"
            fakebin.mkdir()
            python = fakebin / "python3"
            python.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$QUEUE_CALLS"\nexit 17\n')
            python.chmod(0o755)
            sleep = fakebin / "sleep"
            sleep.write_text("#!/bin/sh\nexit 0\n")
            sleep.chmod(0o755)
            calls = root / "calls"
            env = dict(os.environ, PATH=f"{fakebin}{os.pathsep}{os.environ['PATH']}", QUEUE_CALLS=str(calls))
            result = subprocess.run(["bash", str(root / "scripts/queue.sh")], cwd=root, env=env,
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Successful models: 0/11", result.stdout)
            self.assertNotIn("aggregate_results.py", calls.read_text())
            self.assertNotIn("--no-resume", calls.read_text())


if __name__ == "__main__":
    unittest.main()
