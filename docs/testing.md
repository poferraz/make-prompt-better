# Testing and recurring runs

The `validate` job runs on pushes and pull requests to main. It includes the existing repository checks and benchmark tests, plus `python3 -m unittest discover -s tests -v` for CLI, installer and real npm archive integration. Tests use temporary directories and a temporary npm cache; no model credentials are needed.

The recurring matrix is configured to run on pull requests affecting the installer, CLI, skill, tests, or benchmark code. It also runs daily at 04:23 UTC and a deeper seeded property run on Sundays at 05:43 UTC. The matrix specifies Python 3.10 and 3.12 on Ubuntu, Python 3.12 on macOS, and Node.js 22. The v4.4.0 release passed this matrix; later changes must pass on their own commit. Manual dispatch accepts a numeric seed. Scheduled runs use the UTC date as seed, plus the next two integers; their reproduction command and Python coverage report are retained for 14 days. Each job has a 20 minute timeout. GitHub may delay or drop scheduled runs and disables schedules in inactive public repositories after 60 days.

Reproduce locally with `TEST_SEED=42 TEST_CASES=200 python3 -m unittest discover -s research/benchmark/v4 -p 'test_*.py' -v` and `python3 -m unittest discover -s tests -v`. For the weekly budget use `TEST_CASES=2000`. Failure output identifies the seed and property case; use the run artifact's reproduction command to repeat it. Inspect job logs for failures before retrying and fix flaky tests rather than suppressing them.

Python coverage uses coverage.py 7.6.12 with branches enabled and includes the benchmark summary module as well as the existing production modules. CI uses an 81% combined floor and per-module floors in `tests/check_python_coverage.py`. JavaScript coverage uses c8 10.1.3 across the two production modules, with overall floors of 85% lines and 78% branches, and per-module floors of 83% and 78%. Floors do not establish safety or prevent every regression. Shell has no numeric coverage; unlisted scenarios remain gaps.

| Installer scenario | Automated evidence |
| --- | --- |
| Copy, repeated execution, backup, symlink, uninstall | Temporary project integration test |
| Spaces in project path, dry run, invalid runtime and missing argument | Temporary project integration test |
| Permission denial, interrupted copy, recovery | Temporary project integration tests; permissions test skips when run as root |
| Global runtimes, default skip, forced install, Cursor rule removal | Isolated temporary home integration tests |
| Interrupted mkdir, backup move, copy, symlink and final switch | Injected failures; original target or recoverable backup checked |
| Cross-runtime Cursor edits, symlinked parents/rules, locked Cursor rule | Temporary sentinels and negative installer tests |
| Six discoverable copies to one, valid aliases, repeated update, and uninstall | Identity-based discovery regressions; malformed identities and unrelated skills preserved |
| Read-only check/preview, protected recovery roots, manual restore then update | Negative cases plus a filesystem recovery round trip |

Benchmark tests fake the chat service and cover streams, retry classes, manifest mismatch, staged resume, historical data protection, rejudging, seed propagation, and swapped judge mappings. `tests/test_skill_contract.py` checks selected literal details of one documented example; it does not establish live-model behavior. The mutation probe tests four targeted mutations. A loopback HTTP fixture tests a streamed response and retry without a model service. A live cloud-model smoke request on 2026-11-01 returned HTTP 429. Live model behavior, interruptions at every possible instruction, all host discovery paths, and exhaustive mutations are not verified. No live paid inference is performed in CI.

## npm workflow and package checks

`tests/test_npm_release.py` checks stable release labels, published-release metadata, exact-commit main CI, archive identity, execute permissions, file boundaries, lifecycle hooks, credential patterns, size limits, registry error handling, and integrity mismatches. An actual tarball is installed into an isolated home and project to test explicit Codex initialization, repeats, six-copy migration, edited-copy rejection, recovery payload preservation, uninstall, and independence from the npm cache. Filesystem smoke tests do not simulate Codex discovery or model execution. The module has an 80% branch-aware coverage floor.

`.github/workflows/publish-npm.yml` runs package preflight without npm credentials. Its manual `check-token` operation uses the protected environment solely to call npm's identity endpoint; it logs no token or raw response. `publish` requires a stable tag on validated main and a published GitHub release before the environment reviewer can approve publication. OIDC has not been configured or exercised yet. Package publication is not a test and must be selected explicitly. See [npm setup and verification](npm-publishing.md).
