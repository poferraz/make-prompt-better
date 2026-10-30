# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
