# Kimi Benchmark Summary: Massive Relative Improvement & Token-to-Value Cost

**Data Source:** `benchmarks/kimi/evaluation-results-v2.md`  
**Evaluator:** Kimi (Moonshot AI, self-evaluated)  
**Date:** 2026-04-01

---

## Performance Snapshot

| Metric | Score |
|--------|-------|
| Average Baseline | **~17.0/25** (lowest across all four architectures) |
| Average Optimized | **~23.7/25** |
| Average Delta | **+6.6 points (+38.8%)** — highest improvement observed |
| Token Overhead | **~2.3x** (down from 3.8x in v1) |
| Tests Won by Optimized | **10/10** |

## Peak Performance Domains

Kimi showed the largest relative gains because its baselines were the weakest, creating the most headroom for the certificate structure to add value. The standout domain was **universal traceability**:

- **Traceability: +3 on every single test** in v2 (from 1/5 or 2/5 baselines to 4/5 or 5/5 optimized). This is the only architecture to achieve a perfect +3 sweep across all 10 tests.
- **Legal Analysis (Test 4): +7** — The optimized response mapped each legal issue to rule-application-precedent structures, added counterarguments for each issue, and provided a jurisdictional variance table.
- **Research Synthesis (Test 5): +7** — The optimized version distinguished study designs (RCT vs. survey), noted generalizability concerns, and separated consensus claims from contested claims with explicit knowledge-gap documentation.
- **Medical Reasoning (Test 3): +7** — Systematic differential evaluation with probability assignments (HIGH/LOW/MODERATE) and explicit anatomy references (RCA occlusion) improved both structure and actionability.

## Architecture-Specific Strengths

1. **Massive Relative Improvement:** Kimi's +6.6 delta is the largest of the four models, confirming that structured prompting provides the highest ROI when baseline competence is lowest.
2. **Traceability Rigor:** Kimi is the only model to achieve a perfect +3 traceability improvement on every single test. The [T]-identifier system forced explicit connections between conclusions and evidence that were entirely absent in baselines.
3. **Gap Detection Honesty:** Kimi was the most aggressive at flagging missing information (debt terms, jurisdiction, troponin results). While this occasionally reduced actionability, it virtually eliminated hallucination of unstated facts.

## Failure Modes Observed

- **Highest Token Overhead:** Kimi's v1 reported 3.8x overhead; v2 reduced this to ~2.3x, but it remains the most verbose architecture when applying the certificate. At high volume, this cost compounds significantly.
- **Gap Overload Reducing Actionability:** The optimized responses repeatedly flagged missing information. In Business Decision and Financial Analysis, this sometimes substituted lists of unknowns for decisive guidance. The evaluator explicitly noted: "readers want guidance despite uncertainty, not just a list of what we don't know."
- **Creative Forcing (Test 10):** +2 points in v2, but the evaluator stated the certificate "forced analytical scaffolding onto a creative task." The traces (headline development, tone calibration) were artificial and described decisions that "don't benefit from formal structure."

## Key Quote from Evaluator

> "The traceability improvement (+3 on every test) is particularly robust—it's an objective structural feature that doesn't depend on subjective quality judgment."

## Recommendation for Kimi-Specific Optimization

For Kimi, the priority is **gap-handling guidance.** The certificate template should include an explicit rule: "After listing critical gaps, provide a 'best effort' recommendation based solely on the available premises. Do not stop at uncertainty." This will convert Kimi's excellent traceability into better actionability without sacrificing its honesty advantage.
