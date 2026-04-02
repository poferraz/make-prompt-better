# Kimi Evaluation Summary

**Source:** `benchmarks/kimi/evaluation-results-v2.md`
**Evaluator:** Kimi (Moonshot AI)
**Date:** 2026-04-01

---

## Performance Profile

| Test | Domain | Task Type | Baseline | Optimized | Delta | Winner |
|------|--------|-----------|----------|-----------|-------|--------|
| 1 | Code Review | Accuracy | 18 | 25 | +7 | Optimized |
| 2 | Financial Analysis | Accuracy | 17 | 23 | +6 | Optimized |
| 3 | Medical Reasoning | Accuracy | 18 | 25 | +7 | Optimized |
| 4 | Legal Analysis | Accuracy | 17 | 24 | +7 | Optimized |
| 5 | Research Synthesis | Mixed | 16 | 23 | +7 | Optimized |
| 6 | Business Decision | Mixed | 18 | 25 | +7 | Optimized |
| 7 | Compliance Check | Accuracy | 18 | 25 | +7 | Optimized |
| 8 | Document Analysis | Mixed | 18 | 25 | +7 | Optimized |
| 9 | Comparative Analysis | Mixed | 18 | 25 | +7 | Optimized |
| 10 | Creative Brief | Alignment | ~12/20* | ~17/20* | +5 | Optimized |
| **AVG** | | | **17.0** | **24.1** | **+6.6** | |

*Test 10 used adjusted 4-dimension scale (max 20) as Kimi determined Accuracy/Actionability don't apply to creative tasks.

---

## Massive Relative Improvement

Kimi's evaluation shows the **largest delta (+6.6 average) and largest relative improvement (39%)** of all four evaluators. This is driven by two factors:

### 1. Lowest baselines across the board

Kimi's average baseline (17.0/25) is 2.5-3.4 points lower than other evaluators:
- GLM-5.1: 19.5/25 baseline
- Gemini: 20.4/25 baseline
- Qwen: 20.2/25 baseline
- **Kimi: 17.0/25 baseline**

This lower starting point provides more room for the certificate structure to demonstrate improvement. The baselines were scored as traceability-poor (average 2.0/5 on that dimension), which the certificate structure systematically addresses.

### 2. The +7 wall

Eight of ten tests showed exactly +7 improvement. This is an unusual clustering that suggests either:
- A scoring calibration artifact where Kimi's 5-point scale maps cleanly to the structural improvements the certificate provides, OR
- The certificate structure provides a consistent ~28% quality floor improvement regardless of domain

The consistency is remarkable: Code Review +7, Medical Reasoning +7, Legal Analysis +7, Research Synthesis +7, Business Decision +7, Compliance +7, Document Analysis +7, Comparative Analysis +7.

---

## Traceability: The Most Dramatic Improvement

Kimi reported the most extreme traceability improvement of any evaluator:

| Test | Baseline | Optimized | Delta |
|------|----------|-----------|-------|
| 1-9 | 2/5 | 5/5 | +3 |
| 10 | 1/5 | 4/5 | +3 |

**Every single test showed +3 traceability improvement.** This is the maximum possible improvement on a 5-point scale. No other evaluator showed this extreme a result:
- GLM: +2 average (range 0 to +2)
- Gemini: +2 average (range +1 to +3)
- Qwen: +1.8 average (range +1 to +2)
- **Kimi: +3.0 average (uniformly +3)**

Kimi's baselines started at 1-2/5 on traceability, compared to 3-4/5 for other evaluators. This suggests either Kimi grades traceability more harshly, or the baselines genuinely lacked citation structure.

---

## Token-to-Value Cost Analysis

Kimi provided the most detailed token cost analysis, including per-test word counts and explicit cost/value judgments:

| Test | Baseline Words | Optimized Words | Ratio | Delta | Verdict |
|------|---------------|-----------------|-------|-------|---------|
| 1 | ~180 | ~380 | 2.1x | +7 | Worth it |
| 2 | ~200 | ~450 | 2.25x | +6 | Worth it |
| 3 | ~220 | ~480 | 2.2x | +7 | Worth it |
| 4 | ~240 | ~550 | 2.3x | +7 | Worth it |
| 5 | ~250 | ~600 | 2.4x | +7 | Worth it |
| 6 | ~230 | ~650 | 2.8x | +7 | Worth it |
| 7 | ~250 | ~600 | 2.4x | +7 | Worth it |
| 8 | ~280 | ~700 | 2.5x | +7 | Worth it |
| 9 | ~300 | ~750 | 2.5x | +7 | Worth it |
| 10 | ~200 | ~350 | 1.75x | +5 | Not worth it |

**Average overhead: ~2.3x** — the highest reported across evaluators.

### Value ratio calculation

For accuracy tasks: **+7 points per 2.2x tokens** = 3.18 points per doubling. This is the best value ratio across all evaluators, driven entirely by Kimi's larger deltas.

For the creative task: **+5 points per 1.75x tokens** on the adjusted 20-point scale = 2.86 points per 1.75x, but Kimi still concluded "Not worth it" because the creative output quality was nearly identical despite the structure.

---

## PRISM Calibration Analysis

Kimi's evaluation includes the most detailed PRISM persona analysis:

| Task Type | Persona Used | Avg Delta | Observation |
|-----------|-------------|-----------|-------------|
| Accuracy | None | +6.8 | Highest gains; no persona damage observed |
| Mixed | "You are an analyst." | +7.0 | Similar gains; vocabulary orientation without accuracy degradation |
| Alignment | Full copywriter persona | +5.0 (adjusted) | Smallest gain; certificate structure forced, persona helped but structure overshadowed |

Kimi concluded: "The PRISM guidance to calibrate persona by task type is sound. However, the certificate structure itself may not add value to pure alignment tasks." This decouples the persona recommendation (validated) from the structure recommendation (nuanced).

---

## Failure Modes Unique to Kimi

1. **Gap detection excess:** "The optimized responses repeatedly flagged missing information. While honest, this sometimes reduced actionability — readers want guidance despite uncertainty, not just a list of what we don't know." This is the only evaluator to flag over-honest gap listing as a problem.

2. **Token cost compounding:** "At 2.3x average overhead, using this skill for every prompt would be prohibitively expensive." Kimi is the most cost-conscious evaluator, explicitly flagging that volume deployment requires selective application.

3. **Confident structure ≠ correctness:** Flagged that "if the premises [P1]-[P4] contain errors, the formal conclusion is wrong regardless of structure." This is the structural version of the "confident but wrong" risk — well-formatted errors are harder to detect.

4. **Self-evaluation bias:** Despite the 39% improvement claim, Kimi acknowledged "the consistency of results (+6 to +7 across 9 of 10 tests) suggests the skill does provide genuine improvement, not just formatting changes." The traceability improvement (+3 on every test) was cited as the most robust finding because "it's an objective structural feature that doesn't depend on subjective quality judgment."

---

## Key Takeaway

Kimi's evaluation demonstrates the skill's potential for **maximum impact on models with lower baseline performance**. The +6.6 average delta (39% improvement) is the headline number, but the more important finding is the **2.3x token cost for ~7 points of improvement on accuracy tasks** — a favorable cost/benefit ratio for high-stakes domains. The caveat: Kimi's baselines were the lowest among all evaluators, so these results represent the best-case scenario for the skill's value proposition.
