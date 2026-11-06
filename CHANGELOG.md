# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.5.0] - Unreleased

This is a prepared release candidate. GitHub release creation and npm publication require separate authorization. The existing `v4.4.0` tag remains unchanged.

### Added
- Add `install`, `check`, `update`, and `uninstall` CLI commands with terminal prompts for host and scope. Preserve `init` and existing installer flags, copy and symlink modes, and recovery behavior. Noninteractive checking, updating, and uninstalling require an explicit host and scope.
- Add `npm run verify` and `npm run verify:fast` for source validation, plus regression tests for failed or skipped release prerequisites and command failure propagation.
- Add isolated host checks for Codex, Gemini, Claude Code plugins, and the Qwen skill-loading library. Keep filesystem checks, host discovery, offline activation, and model invocation evidence distinct.
- Add explicit npm preflight, authentication-only checking, and publishing operations using the protected `npm-publish` environment. Bootstrap-token and OIDC publishing stay separate.
- Check archive identity, file boundaries, executable modes, sensitive-file exclusion, integrity, and installation/update/recovery/uninstall behavior using actual npm tarballs.
- Add an unauthenticated public installation smoke test that verifies the downloaded artifact against an independently supplied digest before executing it. Add disposable registry fixtures for missing versions, tampered files, bad executable links, and download failures.

### Changed
- Make the required `validate` check wait for source verification, the Linux/macOS regression and coverage matrix, mutation checks, and package preflight on every main push and PR, including documentation-only changes.
- Require successful CI for the exact tagged main commit before npm release preparation. Retrieve all workflow-run pages and reject incomplete evidence, unsuccessful latest runs, and failed or pending rerun attempts.
- Use explicit Bash pipeline failure handling so a failed test or coverage command cannot be hidden by `tee`.
- Report the source version during CLI updates and clarify that `update` uses the current checkout or package without fetching another version. Preserve edited installations in recovery storage.
- Keep onboarding source-first, document scope and recovery choices, and make packaged instructions conditional on actual release availability. Public npm installation is not presented as verified.

### Fixed
- Resolve generated Cursor reference paths relative to the rule file's directory.
- Run the JavaScript linter correctly from paths containing spaces or special characters.
- Preserve malformed judge responses as failed attempts and retry only invalid or missing judge stages when resuming a compatible benchmark or rejudge checkpoint. Restrict old-checkpoint migration to reviewed source hashes and preserve the original manifest.

### Evidence limits
- No new model-outcome evaluation was run for v4.5.0. Historical results and host transcripts retain their original source and version labels.
- A configured secret and a successful authentication check do not prove write scope, Bypass 2FA, package ownership, or a successful publication. Public npm installation and OIDC binding remain unverified until tested after separately authorized publication.
- Local tarball tests and disposable registry fixtures are not public installation evidence. The exact public version must pass the unauthenticated smoke test before installation is advertised as verified.
- Native Windows, Cursor and Antigravity host loading, and broader model-driven behavior remain outside the recorded verification scope.

## [4.4.0] - 2026-11-06

### Changed
- Keep one canonical Codex copy in `.agents/skills`; migrate duplicate identities and legacy `.bak.*` folders into recovery storage outside discovery. Add a read-only `--check` command.
- Show help when the Node CLI is run without arguments; add a beginner quickstart, a simpler README, current brand artwork, and concise skill-picker metadata.
- Correct plugin descriptions that still overstated paper counts and verification.
- Stage installer replacements, retain recoverable backups, scope Cursor rules to Cursor installations, and reject symlinked destination parents and rule files.
- Bind new benchmark and rejudge checkpoints to their inputs and protocol, save individual stages, preserve both judge passes, and keep new runs separate from historical results.
- Correct template mappings, qualify research and distribution claims, and add a first-use example and recovery instructions.
- Describe linter results as heuristic signals; reject unknown CLI options and propagate process failures.
- Include installer integration tests in `npm test` and configure Node.js 22 in CI.
- Synchronize active release metadata, check the skill receipt and documentation versions, and pin the beginner source-install commands to this release. Historical research and audit records retain their original labels.

### Evidence limits
- Codex CLI 0.163.0 discovery on macOS was checked separately from filesystem fixtures; desktop picker refresh and full prompt execution remain untested. See [host compatibility](docs/compatibility.md).
- No new model-outcome evaluation was run. npm returned 404 on 2026-11-06; a GitHub release does not publish an npm package. See the [npm rollout plan](docs/npm-publishing.md).

## [4.3.0] - 2026-10-31

### Changed
- Preserve all requested deliverables and operational constraints; default routine analysis to proportional certificates (Zhang, Hu et al., 2026; Ugare & Chandra, 2026).
- Keep creative planning internal unless requested, and retain required context-file sections (Zhang et al., 2025; Gloaguen et al., 2026).
- Report benchmark results by protocol with cluster-robust uncertainty and explicit negative results. Existing benchmark scores describe earlier runs, not a fresh v4.3.0 evaluation.

### Fixed
- Synchronize CLI, plugin, citation, Python, installer, and hero version metadata.
- Restore CI test compatibility with the anonymized judge prompt and forward custom inference seeds through execution, judging, and synthesis.
- Replace unpublished npm installation instructions with the source installation path.
- Align contribution and security guidance with the current executable tools and requirement-preservation contract.

### Maintenance
- Pin CI action revisions, limit workflow permissions, add monthly action update checks, and verify release metadata in CI.
- Add support routes and a repeatable release checklist.

## [4.2.0] - 2026-10-31

### The Compiler, Blind Evaluation & Swiss Editorial Redesign

V4.2.0 completes the repository upgrade to a verified Model-Aware Prompt and Context Compiler. This release introduces a double-blind, position-swapped A/B benchmark evaluation protocol, a zero-dependency non-parametric statistical engine with bootstrap confidence intervals and paired sign-flip permutation tests, an automated `[CONTEXT-CERT]` static analyzer and CLI readiness linter (`lint_context.py`), hardened cross-agent installation tooling (`install.sh`), and the complete Swiss Compiler Blueprint visual redesign.

### Added
- **Double-Blind A/B Benchmark Evaluation Protocol (`research/benchmark/v4/`)**:
  - Eliminates self-preference judge bias with `--judge-model` to decouple the evaluator from the model under test.
  - Eliminates framing and labeling bias via deterministic SHA-256 assignment to `Candidate Response A` and `Candidate Response B`.
  - Eliminates rubric leakage by removing `=== OPTIMIZED PROMPT ===` scaffolding and template headers from judge prompts.
  - Eliminates position and recency bias via `--swap-positions` two-pass evaluation reconciling `(A, B)` and `(B, A)` order.
  - Supports `--strip-cert-markers` to strip `[P1]`, `[T1]`, `[V1]`, and certificate tags before judging substance over formatting.
  - Added deterministic `--seed` flag (default `42`) passed to Ollama inference payloads.
- **Non-Parametric Statistical Engine (`research/benchmark/v4/blind_stats_engine.py`)**:
  - Implements 10,000-resample Bootstrap 95% Confidence Intervals for mean deltas without third-party dependencies.
  - Implements exact (for n <= 14) and Monte Carlo paired sign-flip permutation p-values.
  - Computes 3-tier model stratification: Tier 1 (Sub-14B Edge and Flash), Tier 2 (14B-70B Open-Weights), Tier 3 (Frontier and Large Reasoning Models).
  - Measures token efficiency: token overhead ratio and quality lift per 1,000 extra tokens spent.
- **Standalone `[CONTEXT-CERT]` Static Analyzer & CLI Linter (`lint_context.py`)**:
  - 100-point readiness audit for `CLAUDE.md`, `AGENTS.md`, and `SKILL.md` files based on arXiv:2602.11988, arXiv:2603.18507, and arXiv:2608.12610.
  - Flags directory tree bloat, persona fluff, ungrounded negative constraints, and missing four-pillar coverage.
  - Built-in `--self-test` suite and `--json` structured output support for CI automation.
- **Swiss Compiler Blueprint Visual Redesign (`assets/*.svg`)**:
  - Replaces cyber-neon graphics with four unified editorial figures: `FIG. 01` Hero Banner, `FIG. 02` End-to-End Compilation Pipeline, `FIG. 03` Model-Aware Compilation Matrix, `FIG. 04` Empirical Benchmark Suite.
  - Color palette: Matte Carbon (`#0B0B0D`), Archival Bone (`#F3F0E6`), Signal Vermilion (`#FF3B00`), Verification Jade (`#00D67F`), with 100% ASCII-safe glyphs.
- **Hardened Universal Installer (`install.sh`)**:
  - Added `--symlink` (`-s`) support for real-time `git pull` sync without re-running copies.
  - Added `--copy` (`-c`), `--all` (`-a`), `--backup` (`-b`), `--dry-run` (`-n`), and `--help` (`-h`).
  - Added smart agent detection to avoid creating empty directories for unconfigured agents.
- **CI/CD Regression & Link Auditing (`.github/workflows/validate-skill.yml`)**:
  - Executes benchmark unit test suites in CI (`python3 -m unittest discover`).
  - Audits local relative Markdown links across core documentation files to eliminate 404s.
  - Validates `install.sh` syntax and `--dry-run`.
  - Runs `lint_context.py --self-test` and dogfoods repo context files.

### Changed
- **`README.md` Above-the-Fold Architecture**: Added 5-Second Compiler Diff table, 10-Second Universal Install, repaired Shields.io badge URLs, and fixed relative citation links to `make-prompt-better/references/research-principles.md`.
- **EVALUATION_PROMPT_V4.md**: Updated to blinded `Candidate Response A` vs. `Candidate Response B` protocol.
- **Relocated Superpowers Design Spec**: Moved `docs/superpowers/specs/2026-10-29-make-prompt-better-v4-design.md` to `docs/architecture-v4.md`.
- **Removed Deprecated Root Release Notes**: Consolidated `RELEASE_v3.md` and `RELEASE_v4.md` into `CHANGELOG.md`.

## [4.0.0] - 2026-10-29

### The Context, Harness & Diversity Update (Universal Cross-Agent Release)

V4 expands the research foundation from 6 to 11 peer-reviewed papers, introduces 4 Certificate Modes (adding LRM / Harness Mode and upgrading Creative & Divergent v2 with Verbalized Sampling and discourse-level Anti-SlopShape constraints), converts negative prohibitions into positive observable-predicate recipes, and makes the skill universally compatible with every major AI coding tool (`~/.agents/skills/`, Claude Code, Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, Copilot CLI, Cursor, Windsurf, and AdaL).

### Added
- **5 New Research Sources (6 to 11 total)**:
  - `[VS]` **Verbalized Sampling** (Zhang et al., 2025, arXiv:2510.01171): Counteracts post-training mode collapse and typicality bias by enumerating candidate angles with estimated typicality probabilities (`p`), increasing creative and open-ended diversity by 1.6x to 2.1x.
  - `[SLOPSHAPE]` **Structural Signatures of AI Writing** (Madler, 2026, arXiv:2609.15369; extending StoryScope, Russell et al., 2026): Targets the 10 core discourse-level structural features that identify AI text at 93.5 to 98.0 macro-F1 even after full rewording.
  - `[CONTEXT-FILES]` **Repository Context File Evaluation** (Gloaguen et al., 2026, arXiv:2602.11988): Establishes the Minimal Viable Context rule for `AGENTS.md` and `CLAUDE.md` after empirical findings showed LLM-generated context files reduce task resolution by 3% and raise token costs by >20%.
  - `[HARNESS]` **Harness Optimization, Context-as-a-File & Plan Verification** (Lee et al., 2026, arXiv:2603.28052; Zhang et al., 2026, arXiv:2606.09498; Shao et al., 2026, arXiv:2609.37725; Nam et al., 2025, arXiv:2509.21825): Introduces model-specific harness routing, scratchpad file state (`Context-as-a-File`), and plan-sufficiency verification gates.
  - `[SKILLS-SDO]` **Skill Residency & Positive Recipe Shaping** (Yin et al., 2026, arXiv:2608.12610): Enforces compact, trigger-only frontmatter (`<450` chars) and replaces brittle "Do NOT" prohibition lists with positive structural recipes and observable-predicate conditionals.
- **Mode 3: LRM / Harness Mode**: Dedicated optimization path for Large Reasoning Models (o3, DeepSeek-R1, Claude Extended Thinking, Gemini Thinking) that uses `[P]` Premises and `[V]` Verification Gates without forcing redundant step-by-step CoT output narration (preventing the LRM Overthinking Trap), plus Minimal Viable Context pruning for `AGENTS.md` and `CLAUDE.md`.
- **Mode 4: Creative & Divergent v2**: Upgrades V3's Narrative Traces with `[NT0]` Verbalized Distribution Sampling and the 4-part Structural Rarity Contract (Delayed Thesis, Direct Evidence Progression, Practitioner Voice, Actionable Close).
- **2 New Domain Templates (10 to 12 total)** in `references/domain-templates.md`:
  - Template 11: Agentic System Prompt / `AGENTS.md` / `CLAUDE.md` Context File
  - Template 12: Creative / Editorial Writing with Verbalized Sampling & Anti-SlopShape
- **2 New Annotated Transformations (7 to 9 total)** in `references/examples.md` covering `AGENTS.md` optimization and anti-SlopShape engineering blog writing.
- **Universal Cross-Tool Installer (`install.sh`)**: Installs and syncs the skill across `~/.agents/skills/make-prompt-better`, `~/.claude/skills/make-prompt-better`, and `~/.qwen/skills/make-prompt-better`.

### Changed
- **Universal YAML Frontmatter in `SKILL.md`**: Replaced the 215-word folded YAML description (whose colons broke cross-agent skill migration parsers) with a single-line, parser-safe, trigger-focused `"Use when..."` description compliant with `agentskills.io` and `@skills` residency budgets.
- **All 12 Domain Templates synchronized**: Added mandatory `REMEDIATION / NEXT ACTION` and `TRACEABILITY SELF-CHECK` blocks to every analytical template and converted negative "Do NOT" instructions into positive grounding rules with observable predicates.
- **Resolved `docs/when-to-use.md` inconsistencies**: Updated the decision flowchart to route creative tasks to Mode 4 and reasoning models / context files to Mode 3.

## [3.0.0] - 2026-04-01

### The Empirical Update

V3 hardens the skill based on cross-architecture benchmark evaluation across four model families (Gemini, GLM, Qwen, Kimi). 40 benchmark tests, 5 scoring dimensions each, 97.5% win rate, +24.6% average relative improvement.

### Added
- **Lite Certificate mode**: compressed certificate variant (~1.5x overhead) for routine analytical tasks. Max 3 premises, single-line causal arrow traces, 1-2 sentence conclusion fields. Preserves ~80% of traceability at ~25% lower cost.
- **Actionability Mandate**: mandatory REMEDIATION / NEXT ACTION block appended to every certificate conclusion. Closes the Actionability Gap where models analyze correctly but stop at the verdict.
- **Creative Pivot (Narrative Tracing)**: replaces "skip the certificate for creative tasks" with Narrative Traces (Audience Empathy, Emotional Arc, Tone Calibration). Backstage scaffold that preserves structured reasoning without flattening creative output.
- **Traceability Self-Check guard**: mandatory self-check instruction appended to all optimized prompts. Catches orphaned conclusions where claims lack supporting T-identifier references.
- **Benchmark Results section** in README with per-model performance matrix, dimension-level breakdown, domain performance data, and ceiling/floor effect analysis.
- **Cross-architecture benchmark data** in `research/benchmark/summaries/` (4 full synthesis documents, 16 individual model summaries).

### Changed
- **Token economics corrected**: ~2.8x (from META paper) updated to empirical ~2.0x average (range: 1.95x Gemini/Qwen to 3.8x Kimi). Based on cross-architecture measurement, not theoretical prediction.
- **Optimization process**: expanded from 6 steps to 7 (added certificate mode selection at Step 1b).
- **Step 4 (Rewrite)**: expanded from 8 operations to 9 (added REMEDIATION mandate).
- **Step 5 (Anti-hallucination)**: added mandatory traceability self-check instruction.
- **"When to AVOID" guidance**: creative tasks no longer listed as "avoid entirely"; routed to Creative Pivot instead.
- **tradeoffs.md**: rewritten with empirical dimension-level data, ceiling/floor effect analysis, creative test results, and per-model token overhead ranges.
- **methodology.md**: all stale ~2.8x references updated, V3 features integrated throughout.

## [1.0.0] - 2026-04-01

### Added
- Semi-formal prompt optimization methodology synthesizing six peer-reviewed papers
- 10 domain-specific certificate templates (code review, document analysis, research synthesis, compliance, decision-making, comparative analysis, medical reasoning, legal analysis, financial due diligence, custom)
- Research principles quick-reference index covering all six papers
- 7 before/after example transformations across domains
- Standalone methodology documentation (docs/methodology.md)
- Task classification guide with persona decision tree (docs/task-classification.md)
- When-to-use decision framework (docs/when-to-use.md)
- Honest tradeoffs analysis with paper-backed numbers (docs/tradeoffs.md)
- Claude Code skill with progressive disclosure architecture
- Contribution guidelines
