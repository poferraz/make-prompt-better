"""Run two targeted mutants in isolated temporary directories; neither may survive."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'research/benchmark/v4/blind_stats_engine.py').read_text()
tests = (ROOT / 'research/benchmark/v4/test_properties.py').read_text()
mutants = {
    'invalid blind assignment': ('return {"A": "baseline", "B": "optimized"}', 'return {"A": "baseline", "B": "baseline"}'),
    'negated bootstrap mean': ('round(statistics.fmean(values), 4)', '-round(statistics.fmean(values), 4)'),
}
with tempfile.TemporaryDirectory(prefix='mutation probe ') as tmp:
    root = Path(tmp)
    (root / 'test_properties.py').write_text(tests)
    def execute(text):
        (root / 'blind_stats_engine.py').write_text(text)
        return subprocess.run([sys.executable, '-B', '-m', 'unittest', 'test_properties'], cwd=root,
                              capture_output=True, text=True, timeout=30)
    baseline = execute(source)
    if baseline.returncode:
        raise SystemExit('Unmodified control failed:\n' + baseline.stderr)
    for name, (before, after) in mutants.items():
        if source.count(before) != 1:
            raise SystemExit(f'Mutation target changed: {name}')
        result = execute(source.replace(before, after, 1))
        if result.returncode == 0 or 'FAIL:' not in result.stderr:
            raise SystemExit(f'Mutant survived or failed to execute: {name}\n{result.stderr}')
        print(f'Killed mutant: {name}')
