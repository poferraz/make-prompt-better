"""Check branch-aware per-module floors against coverage.py JSON output."""
import json
import sys

FLOORS = {
    'lint_context.py': 68,
    'research/benchmark/v4/aggregate_results.py': 83,
    'research/benchmark/v4/blind_stats_engine.py': 87,
    'research/benchmark/v4/rejudge_saved_outputs.py': 89,
    'research/benchmark/v4/run_ollama_benchmarks.py': 70,
    'scripts/check-release.py': 98,
}
report = json.load(open(sys.argv[1], encoding='utf-8'))['files']
failed = False
for name, floor in FLOORS.items():
    if name not in report:
        print(f'MISSING coverage: {name}')
        failed = True
        continue
    actual = report[name]['summary']['percent_covered']
    print(f'{name}: {actual:.1f}% (minimum {floor}%)')
    failed |= actual < floor
raise SystemExit(1 if failed else 0)
