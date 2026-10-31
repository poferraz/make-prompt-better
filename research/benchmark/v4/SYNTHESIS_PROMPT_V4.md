# CROSS-ARCHITECTURE SYNTHESIS & SKILL UPGRADE PROMPT (v4.0 -> v4.1)

## Context & Objective

You are the **Lead AI Evaluation Researcher & Skill Architect** for `make-prompt-better`. Multiple frontier and open-weights models across three tracks have completed the 12-test v4.0 evaluation suite:
- **Track 1 (Google Antigravity)**: `gemini-3.8`
- **Track 2 (OpenAI Codex)**: `gpt-6.1-terra`
- **Track 3 (Ollama Cloud Multi-Model Suite)**: Installed `:cloud` models (`glm-5.3:cloud`, `glm-5.3-flash:cloud`, `deepseek-v4.1-flash:cloud`, `minimax-m3.1-flash:cloud`, `mistral-large-4:cloud`, `kimi-k3:cloud`, `gemma4:31b-cloud`, `gpt-oss:20b-cloud`, `beam:cloud`, `muse-spark-open:cloud`)
- **Track 4 (Anthropic Claude Frontier Track)**: `claude-opus` and `claude-sonnet-5.5`
- **Track 5 (Meta Frontier Track)**: `meta-muse-wonder-1.0-max`

Your goal is to:
1. Run `python3 research/benchmark/v4/aggregate_results.py` to generate the unified quantitative dataset (`research/benchmark/v4/results/AGGREGATED_METRICS.md` and `AGGREGATED_METRICS.json`).
2. Read `research/benchmark/v4/results/AGGREGATED_METRICS.md` and every `research/benchmark/v4/results/*/EVALUATION_RESULTS.md` file (plus compare longitudinally against the v1.0 summaries in `research/benchmark/summaries/`).
3. Produce the comprehensive cross-model research report at `research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md`.
4. Extract concrete, evidence-backed upgrades and apply or propose **v4.1 refinements** to `make-prompt-better/SKILL.md` and `make-prompt-better/references/domain-templates.md`.

## Step 1: Data Extraction & Verification

Run:
```bash
python3 research/benchmark/v4/aggregate_results.py
```

Inspect `research/benchmark/v4/results/AGGREGATED_METRICS.md` and read the qualitative `## FINAL REPORT` sections from each `research/benchmark/v4/results/<model-slug>/EVALUATION_RESULTS.md`.

For each evaluated model, verify:
- **Average Baseline Score** (`/25`) vs. **Average Optimized Score** (`/25`), absolute delta, and percentage lift.
- **Dimension-by-Dimension Deltas**: `Accuracy`, `Completeness`, `Structure`, `Actionability`, and `Traceability`.
- **Token/Word Overhead Ratio**: Overall overhead and mode-specific overhead (`Mode 1 Max` on Tests 1-8 vs. `Mode 2 Lite` on Test 9 vs. `Mode 3 Harness` on Tests 11-12 vs. `Mode 4 Creative v2` on Test 10).
- **Longitudinal Shift (v1.0 -> v4.0)**: Did v4.0 resolve the three v1.0 weaknesses identified in `research/benchmark/summaries/` (token bloat on routine queries, creative rigidity on Test 10, and reasoning model over-thinking)?

## Step 2: Write `research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md`

Create `research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md` with the following sections:

1. **Executive Summary & Headline Metrics**:
   - Aggregate quality lift across all evaluated models (mean baseline `/25`, mean optimized `/25`, mean `%` improvement, total win-tie-loss record across `N x 12` test runs).
2. **Cross-Architecture Comparative Performance Matrix**:
   - Full markdown table comparing `gemini-3.8`, `gpt-6.1-terra`, `claude-opus`, `claude-sonnet-5.5`, `meta-muse-wonder-1.0-max`, and every Ollama Cloud model across Baseline, Optimized, Delta, Overhead Ratio, and Best/Worst Task.
3. **v4.0 Certificate Mode Validation**:
   - **Mode 1 (Max Certificate, Tests 1-8)**: Traceability and factual accuracy gains on high-stakes tasks.
   - **Mode 2 (Lite Certificate, Test 9)**: Did Lite Mode keep word/token overhead below `1.5x` while preserving analytical rigor?
   - **Mode 3 (LRM & Agentic Harness, Tests 11-12)**: Did `[CONTEXT-FILES]` (Template 11) strip discoverable repo bloat below 150 lines? Did `[HARNESS]` (Template 12) eliminate concurrency bugs via `[V1]`-`[V3]` invariants without verbose CoT bloat?
   - **Mode 4 (Creative & Divergent v2, Test 10)**: Did Verbalized Sampling (`[NT0]`) + Anti-SlopShape (`[SC0]`) outperform v1.0 on Test 10?
4. **Architectural Sensitivity Analysis (Frontier vs. Flash vs. Open-Weights Cloud)**:
   - How do frontier reasoning models (`gemini-3.8`, `gpt-6.1-terra`, `glm-5.3:cloud`, `mistral-large-4:cloud`, `kimi-k3:cloud`) respond to certificates compared to high-speed flash/compact models (`glm-5.3-flash:cloud`, `deepseek-v4.1-flash:cloud`, `minimax-m3.1-flash:cloud`, `gpt-oss:20b-cloud`)?
5. **Failure Modes & Remaining Bottlenecks**:
   - Honest accounting of any tests or models where optimization tied, degraded output quality, or exceeded token budgets.
6. **Actionable v4.1 Skill Upgrade Specification**:
   - Exact, surgical edits recommended for `make-prompt-better/SKILL.md`, `make-prompt-better/references/domain-templates.md`, and `docs/tradeoffs.md` based on empirical evidence from the v4.0 run.

## Editorial & Validation Constraints

- Follow `AGENTS.md` Invariant `[I1]`: Never use em dashes or en dashes in any Markdown file; use commas, colons, or semicolons.
- If applying v4.1 upgrades to `make-prompt-better/`, run the mandatory validation one-liner and `./install.sh` from `AGENTS.md` before finishing.
