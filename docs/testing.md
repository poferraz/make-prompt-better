# Testing and recurring runs

The `validate` job runs on pushes and pull requests to main. It includes the existing repository checks and benchmark tests, plus `python3 -m unittest discover -s tests -v` for CLI, installer and real npm archive integration. Tests use temporary directories and a temporary npm cache; no model credentials are needed.

The recurring workflow runs daily at 04:23 UTC and a deeper seeded property run on Sundays at 05:43 UTC. It runs Python 3.10 and 3.12 on Ubuntu and Python 3.12 on macOS. Manual dispatch accepts a numeric seed. Scheduled runs use the UTC date as seed, plus the next two integers; their reproduction command and Python coverage report are retained for 14 days. Each job has a 20 minute timeout; ordinary local suites take seconds, but hosted setup and package installation vary. GitHub may delay or drop scheduled runs, runs schedules only on the default branch, and disables schedules in inactive public repositories after 60 days.

Reproduce locally with `TEST_SEED=42 TEST_CASES=200 python3 -m unittest discover -s research/benchmark/v4 -p 'test_*.py' -v` and `python3 -m unittest discover -s tests -v`. For the weekly budget use `TEST_CASES=2000`. Failure output identifies the seed and property case; use the run artifact's reproduction command to repeat it. Inspect job logs for failures before retrying and fix flaky tests rather than suppressing them.

Python coverage uses coverage.py 7.6.12 with branches enabled and includes all six production Python modules. The combined line and branch coverage is 79% (862 of 1,044 lines and 225 of 334 branches), with a 78% combined floor to accommodate runtime differences. The floor does not prevent every per-module regression. JavaScript coverage uses c8 10.1.3 across both production modules: the local baseline is 88.75% lines and 83.63% branches, with floors of 85% and 78%. Per-module thresholds are not yet enforced. Shell has no numeric coverage. Its scenario matrix is below; unlisted cases remain gaps.

| Installer scenario | Automated evidence |
| --- | --- |
| Copy, repeated execution, backup, symlink, uninstall | Temporary project integration test |
| Spaces in project path, dry run, invalid runtime and missing argument | Temporary project integration test |
| Global runtime combinations, permissions, interruption and recovery | Not covered |

Benchmark tests fake the chat service and cover incomplete and malformed streams, errors, resume, aggregation and blind score mapping. Live model services, network timeouts, all retry types, rejudging execution, release failure cases, mutation testing, per-module coverage enforcement, and permission failures remain work. The rejudging execution path remains largely untested. No live paid inference is performed in CI.
