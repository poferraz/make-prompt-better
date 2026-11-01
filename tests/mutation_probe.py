"""Test four specific mutants in isolated copies; fail if one survives."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / 'research/benchmark/v4'
mutants = [
    ('invalid blind assignment', 'blind_stats_engine.py', 'return {"A": "baseline", "B": "optimized"}', 'return {"A": "baseline", "B": "baseline"}', 'test_properties'),
    ('negated bootstrap mean', 'blind_stats_engine.py', 'round(statistics.fmean(values), 4)', '-round(statistics.fmean(values), 4)', 'test_properties'),
    ('lost request seed', 'run_ollama_benchmarks.py', 'payload_options: dict[str, Any] = {"seed": seed}', 'payload_options: dict[str, Any] = {"seed": 0}', 'test_run_ollama_benchmarks.ChatStreamingTests.test_timeout_retries_with_same_seed_and_timeout'),
    ('disabled HTTP retry', 'run_ollama_benchmarks.py', 'if retryable and attempt < max_retries:', 'if False:', 'test_run_ollama_benchmarks.ChatStreamingTests.test_http_retry_and_nonretryable_error'),
]
with tempfile.TemporaryDirectory(prefix='mutation probe ') as tmp:
    root = Path(tmp) / 'a/b/c'
    root.mkdir(parents=True)
    names = ['blind_stats_engine.py', 'run_ollama_benchmarks.py', 'test_properties.py', 'test_run_ollama_benchmarks.py']
    sources = {name: (BENCH / name).read_text() for name in names}
    for name, source in sources.items():
        (root / name).write_text(source)
    def execute(test):
        return subprocess.run([sys.executable, '-B', '-m', 'unittest', test], cwd=root,
                              capture_output=True, text=True, timeout=30)
    for label, filename, before, after, test in mutants:
        control = execute(test)
        if control.returncode:
            raise SystemExit(f'Unmodified control failed: {label}\n{control.stderr}')
        original = sources[filename]
        if original.count(before) != 1:
            raise SystemExit(f'Mutation target changed: {label}')
        (root / filename).write_text(original.replace(before, after, 1))
        result = execute(test)
        (root / filename).write_text(original)
        if result.returncode == 0 or not ('FAIL:' in result.stderr or 'ERROR:' in result.stderr):
            raise SystemExit(f'Mutant survived or failed to execute: {label}\n{result.stderr}')
        print(f'Killed mutant: {label}')
