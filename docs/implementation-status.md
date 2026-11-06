# Audit implementation status

This document tracks the unreleased work against the [2026-11-06 audit](clief/audits/icm/2026-11-06-ed95968.md). The audit reports preserve their original baseline and findings. This working tree is not the published v4.3.0 tag. The later [discovery and first-use refinement](refinement-2026-11-06.md) supersedes the earlier installer and first-use observations below.

| Workstream | Implemented | Remaining or unverified |
| --- | --- | --- |
| W01 installer | Per-target staging, recovery storage outside discovery, duplicate migration, scoped Cursor rules, conflict and symlink checks, locks, read-only installation checks, and failure tests | Restoration is manual. A multi-target run is not an all-or-nothing transaction. Forced termination can leave locks. Hostile concurrent parent-directory replacement and every interruption point are not proven safe. |
| W02 CLI and lint | Empty-input signal, non-certifying grades, safer deadline and ordering advice, unknown-option and process-error handling, and opt-in failure on findings in both linters | Regex matches can include quoted examples or code. The JavaScript prompt linter and Python context linter use different heuristics; there is no semantic or safety certification. |
| W03 benchmark | Input-bound manifests, isolated run IDs, stage checkpoints, both judge passes, resumable rejudging, homogeneous summaries, corrected mappings, bounded response reads, and queue failure status | Provider model revisions may be mutable. Request estimates are not monetary or wall-clock limits. Redirect and transport behavior require further hardening; no live inference was performed. |
| W04 claims | Corrected highlighted hero, README, skill, source-attribution, and methodology claims; added a selected [claims register](claims.md) | The register is selective. Historical material and every numerical or publication-status claim have not been exhaustively revalidated. |
| W05 skill and adapters | Short-return and output-format rules, evidence-qualified receipts, source-data boundary, adapter consistency, a literal example checker, and concise Codex picker metadata | Fixture matches are not proof of semantic preservation or injection resistance. Local Codex discovery is verified in the follow-up; full host invocation remains untested. |
| W06 verification | `npm test` includes integration tests; CI config selects Node 22 and expands the affected pull-request matrix; coverage includes the new summary module | The new workflow has not run on GitHub for this working tree. The existing mandatory local sync contract remains in force. |
| W07 first use | Source and recovery guide, manually produced [example](demo.md), new cover, beginner [quickstart](quickstart.md), and simplified README | The local rendered preview is an approximation of GitHub. Assistive-technology review, 200% zoom, and a recorded install-to-recovery host session remain unverified. |
| W08 host and outcomes | [Compatibility matrix](compatibility.md) and [follow-up evaluation protocol](evaluation-followup.md) | Actual host discovery, fresh model outcomes, provider availability, budget, and evaluation results are unknown. |
| W09 release | Package allowlist, README link checks, actual local archive installation test, and unreleased changelog | No tag, release, registry package, or marketplace listing was published. Node 22 and the final release SHA still need remote CI evidence. |
| W10 adoption | [Pilot proposal](adoption-experiments.md) | No pilot, social-preview upload, outreach, or adoption claim has been made. |

The repository's local AGENTS contract still requires its exact validation command and `./install.sh` before completion. Installation updates existing local agent copies and preserves the prior copies as named backups. See [installation and recovery](installation.md) and [benchmark runs and evidence](benchmark-runs.md) for operating details.

## Earlier local verification on 2026-11-06

- `npm test`: exit 0, including 58 benchmark tests, four statistics tests, 39 integration tests, and the JavaScript linter self-test. The loopback fixture required authorized local network access; no model service was contacted.
- `npm run lint`: exit 0. Linter scores describe configured pattern matches, not safety or correctness.
- Python coverage gates: exit 0, 86% combined coverage and every configured module floor met. JavaScript c8 gates: exit 0, 94.81% lines and 90.47% branches on the local runtime. These are coverage measurements, not quality guarantees.
- `python3 tests/mutation_probe.py`: exit 0, four targeted mutants killed. `python3 scripts/check-release.py`: exit 0, `[PASS] Release metadata and CLI agree on v4.3.0`. Bash syntax checks and `git diff --check` passed.
- Exact AGENTS validation: exit 0, `VALIDATED OK`.
- Final `./install.sh`: exit 0, `Done. Processed (copy) 7 agent target(s) (7 already current; 1 unconfigured agent roots skipped; pass --all to force all).` All seven installed trees match the working skill source. The first backup set listed below matches the pre-change audit baseline; a later sync also retained intermediate copies.

The earlier installer reported the following backup directories. The subsequent [discovery refinement](refinement-2026-11-06.md) moved these and the intermediate copies into `~/.make-prompt-better/backups`, with original-path receipts. The old locations below are historical evidence, not current recovery paths:

- `~/.agents/skills/make-prompt-better.bak.kLoF372P`
- `~/.claude/skills/make-prompt-better.bak.PPXkWcNy`
- `~/.qwen/skills/make-prompt-better.bak.7VMzXWkY`
- `~/.gemini/skills/make-prompt-better.bak.KkRziIDw`
- `~/.gemini/config/skills/make-prompt-better.bak.qyTiQP19`
- `~/.gemini/antigravity/skills/make-prompt-better.bak.XVIkutG4`
- `~/.codex/skills/make-prompt-better.bak.UIhQ5yAS`

The later sync retained these intermediate copies:

- `~/.agents/skills/make-prompt-better.bak.rrY2cVYa`
- `~/.claude/skills/make-prompt-better.bak.l4ZqL1Wv`
- `~/.qwen/skills/make-prompt-better.bak.DkBThpTF`
- `~/.gemini/skills/make-prompt-better.bak.WD9JsTFZ`
- `~/.gemini/config/skills/make-prompt-better.bak.KgLkC4Hk`
- `~/.gemini/antigravity/skills/make-prompt-better.bak.Y4qKTmwv`
- `~/.codex/skills/make-prompt-better.bak.ZU4fL09H`

The local environment was macOS arm64, Bash 3.2.57, Python 3.14.2, Node 26.12.0, and npm 11.20.0. CI's configured Node 22 and Python 3.10/3.12 combinations have not been rerun remotely for this working tree.
