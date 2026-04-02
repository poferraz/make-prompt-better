# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
