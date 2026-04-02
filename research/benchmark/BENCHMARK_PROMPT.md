# Cross-Architecture Benchmark Evaluation Prompt (Max Mode)

This is the canonical benchmark evaluation prompt. Run it against each model you want to test. The model receives the raw test results (from `benchmarks/[model]/EVALUATION_RESULTS*.md`) and produces a structured summary that feeds into the cross-architecture synthesis and documentation remediation cycle.

---

## How to Use This Prompt

1. Copy the prompt block below
2. Replace `[MODEL_NAME]` with the evaluator model's name (e.g., `gemini`, `glm`, `qwen-code`, `kimi`)
3. Replace the `DATA SOURCES` section with paths to the actual evaluation results for all four models
4. Run the prompt against the evaluator model
5. Save the output as `research/benchmark/summaries/[model]/summary_full_[model].md`

---

## The Prompt (copy everything below the line)

---

You are a research analyst.

## Task

The standard analytical protocol requires completing the following cross-architecture benchmark synthesis before providing any assessment. This protocol ensures every claim traces to verifiable evidence.

## Context

### PREMISES

- [P1] Data source locations (read these files completely before reasoning):
  - `benchmarks/glm/EVALUATION_RESULTS.md`
  - `benchmarks/glm/EVALUATION_FULL.md`
  - `benchmarks/gemini/EVALUATION_RESULTS_v2.md`
  - `benchmarks/qwen-code/EVALUATION_RESULTS_V2.md`
  - `benchmarks/kimi/evaluation-results-v2.md`

- [P2] Output destination: `research/benchmark/summaries/[MODEL_NAME]/summary_full_[MODEL_NAME].md`

- [P3] Evaluation framework: each test was scored on 5 dimensions (Accuracy, Completeness, Structure, Actionability, Traceability), each rated 0-5. The total score is the sum across all 5 dimensions (maximum 25 per test). The "baseline" is the unstructured prompt score. The "optimized" is the semi-formal reasoning certificate prompt score. The "delta" is optimized minus baseline.

- [P4] Operational mandates applied during benchmarking:
  - Creative Bypass: Test 10 (Creative Brief) uses Narrative Traces instead of standard evidence traces
  - Actionability Mandate: All certificate templates include a mandatory REMEDIATION / NEXT ACTION block

- [P5] The four model families evaluated are: GLM-5.1, Gemini, Qwen Code, and Kimi (Moonshot AI). Each model was tested on the same 10 benchmark tests.

- [P6] Self-evaluation bias: all evaluations were self-judged (same model generated and scored responses). Deltas are more reliable than absolute scores. Each evaluator used slightly different scoring standards.

### EVIDENCE TRACES

Trace through each data source systematically. For each model family:

- [T1] Read the evaluation results for GLM-5.1. Extract: per-test baseline score, per-test optimized score, per-test delta, per-test token counts (baseline word count and optimized word count), overall average baseline, overall average optimized, overall average delta, win rate (number of tests where optimized > baseline), and any dimension-level breakdowns reported.

- [T2] Read the evaluation results for Gemini. Extract the same metrics as [T1].

- [T3] Read the evaluation results for Qwen Code. Extract the same metrics as [T1].

- [T4] Read the evaluation results for Kimi. Extract the same metrics as [T1].

- [T5] Compute the comparative performance matrix:
  - For each model: Baseline Avg, Optimized Avg, Delta, Relative Improvement (delta/baseline), Token Overhead (optimized tokens / baseline tokens), Win Rate
  - Grand average across all four models for each metric
  - Token overhead range (lowest to highest model)

- [T6] Extract dimension-level deltas where reported. For each of the 5 dimensions (Traceability, Structure, Completeness, Accuracy, Actionability), note the per-model delta and compute the cross-architecture average. If a dimension is only reported for one model, mark it as single-source.

- [T7] Extract domain-specific deltas where reported (Code Review, Financial Analysis, Medical Reasoning, Legal Analysis, Research Synthesis, Creative Brief). Note which models contribute data for each domain.

- [T8] Identify the top 3 cross-architecture findings. For each finding, cite which evaluator summaries or raw data support it. Cross-reference at least two independent sources per finding.

- [T9] Check for ceiling/floor effects: does the relationship between baseline score and delta appear approximately linear? If so, estimate the coefficient (points of delta lost per point of baseline increase).

### FORMAL CONCLUSION

Based solely on the premises and traces above, produce a structured synthesis document with these sections:

**Section 1: Comparative Performance Matrix**

A markdown table with columns: Model, Baseline Avg, Optimized Avg, Delta, Relative Improvement, Token Overhead, Win Rate. Include a Grand Average row.

**Section 2: Dimension-Level Deltas**

A markdown table with columns: Dimension, [per-model columns], Cross-Architecture Average. Mark any values that are single-source (only one evaluator reported them).

**Section 3: Domain-Specific Performance**

A markdown table with columns: Domain, [per-model columns], Average. Note N/A where a model did not test that domain.

**Section 4: Top 3 Key Findings**

Each finding must:
- State the finding in one sentence
- Reference specific trace identifiers ([T1]-[T9]) as evidence
- Note any evaluators that disagreed and what they said instead

**Section 5: Actionable Next Steps**

Prioritized roadmap with: Priority number, Problem statement, Evidence (trace references), Proposed action, Owner, Timeline, Success metric.

**Section 6: Methodological Caveats**

Acknowledge: self-evaluation bias, no inter-rater reliability, sample size limitations, and any other threats to validity you identified during tracing.

### REMEDIATION / NEXT ACTION

The synthesis is incomplete until you provide:
1. The full markdown document covering all 6 sections above
2. A computation verification block at the end showing your arithmetic for the grand averages (so a human auditor can confirm the numbers)
3. A list of any claims in your conclusion that could NOT be traced to the raw data, flagged as "UNSOURCED"

### TRACEABILITY SELF-CHECK

Before finalizing, verify that every claim in your conclusion references at least one T-identifier from your evidence traces. If any claim lacks a supporting trace, either add the missing trace or remove the claim. No orphaned conclusions are permitted.

### Anti-Hallucination Guards

- Do not infer scores or deltas from model names, reputation, or prior knowledge. Trace the actual numbers from the evaluation result files.
- If you cannot locate a specific metric in the source files, state "NOT REPORTED IN SOURCE DATA" rather than estimating.
- State counterexamples when they exist, even if the overall finding is positive.
- Distinguish between "verified" (found in source files), "computed" (derived from verified numbers), and "estimated" (approximated from partial data). Label each number accordingly.
