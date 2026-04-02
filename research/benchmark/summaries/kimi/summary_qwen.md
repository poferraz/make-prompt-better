# Qwen Code Benchmark Summary: Methodical Document Breakdown & Risk Assessment

**Data Source:** `benchmarks/qwen-code/EVALUATION_RESULTS_V2.md`  
**Evaluator:** Qwen Code (Qwen3.5, self-evaluated)  
**Date:** April 1, 2026

---

## Performance Snapshot

| Metric | Score |
|--------|-------|
| Average Baseline | **~20.0/25** |
| Average Optimized | **~24.3/25** |
| Average Delta | **+4.3 points (+21.5%)** |
| Token Overhead | **~1.67x (67% word increase)** — lowest overhead observed |
| Tests Won by Optimized | **10/10** |

## Peak Performance Domains

Qwen's optimized responses excelled in tasks requiring **systematic option evaluation** and **risk-aware document parsing**:

- **Business Decision (Test 6): +8 (v1), strong in v2** — The option-tracing framework forced explicit scoring matrices, quantified development time estimates (4–8 weeks vs. 3–5 days), and surfaced vendor maturity risks (Clerk's 2022 founding date vs. Auth0's 2013 track record) that the baseline omitted.
- **Research Synthesis (Test 5): +5 (v2)** — The optimized response explicitly distinguished between RCT evidence (Bloom study) and self-reported survey data, flagged NBER papers as "working paper status (not yet peer-reviewed)," and honestly acknowledged knowledge-cutoff limitations.
- **Legal Analysis (Test 4): +5 (v2)** — Detailed jurisdictional analysis named specific states and their approaches, and the counterargument section explained when enforcement might actually occur.

## Architecture-Specific Strengths

1. **Methodical Document Breakdown:** Qwen consistently decomposed documents, proposals, and contracts into discrete, traceable claims. In Document Analysis (Test 8), it provided an "evidence required to verify" checklist for each claim.
2. **Risk Assessment Rigor:** The model naturally weighted risk matrices. In Business Decision and Legal Analysis, it quantified litigation costs ($50K–$200K+), vendor lock-in, and jurisdictional variance with precision.
3. **Token Efficiency Champion:** Qwen achieved the highest win rate (10/10) with the lowest token overhead (~1.67x), proving that structured reasoning does not require extreme verbosity on this architecture.

## Failure Modes Observed

- **Redundancy in Traces:** In Tests 2, 3, and 6, some trace sections repeated information that could have been stated once and referenced by identifier. The ACE research warns about brevity bias but does not address verbosity risk.
- **Gap Overload:** The anti-hallucination guards sometimes led to excessive gap-listing without providing "best effort guidance despite uncertainty." In Business Decision analysis, the model listed numerous open questions but could have been more decisive.
- **Creative Constraint (Test 10):** +2 points in v2, but the evaluator noted the certificate structure was "essentially dead weight" for creative generation. The traces acted as brief brainstorming outlines but did not improve the final copy's voice.

## Key Quote from Evaluator

> "The certificate structure's main contribution here was making the reasoning auditable rather than making it more correct."

## Recommendation for Qwen-Specific Optimization

Qwen benefits most from an **anti-verbosity guard.** Add an instruction that reads: "If a trace section would repeat information from another section, reference it by identifier instead of restating." This will preserve Qwen's low overhead advantage while maintaining traceability.
