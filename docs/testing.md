# Testing and recurring runs

The `validate` job runs on pushes and pull requests to main. It includes the existing repository checks and benchmark tests, plus `python3 -m unittest discover -s tests -v` for CLI, installer and real npm archive integration. Tests use temporary directories and a temporary npm cache; no model credentials are needed.

When its workflow file changes, the recurring matrix also runs on the pull request. The recurring workflow runs daily at 04:23 UTC and a deeper seeded property run on Sundays at 05:43 UTC. It runs Python 3.10 and 3.12 on Ubuntu and Python 3.12 on macOS. Manual dispatch accepts a numeric seed. Scheduled runs use the UTC date as seed, plus the next two integers; their reproduction command and Python coverage report are retained for 14 days. Each job has a 20 minute timeout; ordinary local suites take seconds, but hosted setup and package installation vary. GitHub may delay or drop scheduled runs, runs schedules only on the default branch, and disables schedules in inactive public repositories after 60 days.

Reproduce locally with `TEST_SEED=42 TEST_CASES=200 python3 -m unittest discover -s research/benchmark/v4 -p 'test_*.py' -v` and `python3 -m unittest discover -s tests -v`. For the weekly budget use `TEST_CASES=2000`. Failure output identifies the seed and property case; use the run artifact's reproduction command to repeat it. Inspect job logs for failures before retrying and fix flaky tests rather than suppressing them.

Python coverage uses coverage.py 7.6.12 with branches enabled and includes all six production Python modules. The local combined line and branch coverage is 82%, with an 81% combined floor and per-module floors in `tests/check_python_coverage.py`. Floors allow small runtime-dependent differences and do not prevent every regression. JavaScript coverage uses c8 10.1.3 across both production modules: the local baseline is 88.75% lines and 83.63% branches, with overall floors of 85% and 78%, and per-module floors of 83% and 78%. Shell has no numeric coverage. Its scenario matrix is below; unlisted cases remain gaps.

| Installer scenario | Automated evidence |
| --- | --- |
| Copy, repeated execution, backup, symlink, uninstall | Temporary project integration test |
| Spaces in project path, dry run, invalid runtime and missing argument | Temporary project integration test |
| Permission denial, interrupted copy, recovery | Temporary project integration tests; permissions test skips when run as root |
| Global runtimes, default skip, forced install, Cursor rule removal | Isolated temporary home integration tests |
| Interrupted mkdir, removal, backup, copy and symlink | Injected failures followed by retry; backup data checked |

Benchmark tests fake the chat service and cover incomplete and malformed streams, timeouts, retryable and non-retryable errors, resume, aggregation, seed propagation and swapped judge mapping. The weekly, manual and workflow-change runs also test whether four targeted mutations are detected; run them locally with `python3 tests/mutation_probe.py`. A loopback HTTP fixture tests a real streamed response and retry without a model service. Global runtime paths, selected interruption points, HTTP retry classes and release metadata mismatch and missing-file paths are covered. A live cloud-model smoke request on 2026-11-01 returned HTTP 429 because the account session limit was exhausted. Live model behavior, interruptions at every possible instruction, and exhaustive mutations are not verified. No live paid inference is performed in CI.
