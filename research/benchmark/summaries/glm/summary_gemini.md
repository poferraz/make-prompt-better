# Gemini Evaluation Summary

**Source:** `benchmarks/gemini/EVALUATION_RESULTS_v2.md`
**Evaluator:** Gemini (Google)
**Date:** 2026-04-01

---

## Performance Profile

| Test | Domain | Task Type | Baseline | Optimized | Delta | Winner |
|------|--------|-----------|----------|-----------|-------|--------|
| 1 | Code Review | Accuracy | 19 | 24 | +5 | Optimized |
| 2 | Financial Analysis | Accuracy | 17 | 24 | +7 | Optimized |
| 3 | Medical Reasoning | Accuracy | 23 | 25 | +2 | Optimized |
| 4 | Legal Analysis | Accuracy | 19 | 25 | +6 | Optimized |
| 5 | Research Synthesis | Mixed | 18 | 24 | +6 | Optimized |
| 6 | Business Decision | Mixed | 20 | 25 | +5 | Optimized |
| 7 | Compliance Check | Accuracy | 22 | 25 | +3 | Optimized |
| 8 | Document Analysis | Mixed | 21 | 25 | +4 | Optimized |
| 9 | Comparative Analysis | Mixed | 21 | 25 | +4 | Optimized |
| 10 | Creative Brief | Alignment | 24 | 24 | 0 | Tie |
| **AVG** | | | **20.4** | **24.6** | **+4.2** | |

---

## Highest Baseline Among All Evaluators

Gemini started with the highest average baseline score (20.4/25) of all four evaluators. This creates a ceiling effect that mechanically limits the delta the skill can demonstrate. Despite this ceiling:

- **7 of 10 optimized responses hit 24-25/25**, suggesting near-perfect performance at the top of the scoring range.
- **The creative test produced a perfect tie (24/24 both ways)**, making Gemini the only evaluator to show zero improvement on Test 10. This is actually a more honest result than showing marginal improvement; the certificate structure genuinely added nothing to creative output.
- **Test 3 (Medical Reasoning) showed only +2** because the baseline was already 23/25, leaving minimal room for improvement.

### Ceiling-adjusted analysis

If we exclude tests where the baseline exceeded 21/25 (Tests 3, 7, 8, 9, 10) and focus only on tests with room to improve (Tests 1, 2, 4, 5, 6), the average delta rises to **+5.8** — the highest ceiling-adjusted improvement across all evaluators.

---

## Plug-and-Play Efficiency

Gemini's evaluation uniquely highlights the skill's "plug-and-play" nature: the certificate template was applied uniformly across all domains with minimal per-domain customization, yet produced consistent improvements. Key evidence:

1. **Financial Analysis (+7):** The optimized prompt forced calculation of actual dollar OpEx ($39M, $38.54M, $39M, $43.31M), revealing that OpEx was sticky/flat Q1-Q3 while revenue dipped then recovered. The baseline completely missed this nuance. This is a pure structure-driven insight — no domain expertise was added, only systematic enumeration.

2. **Compliance Check (+3):** Both versions correctly identified the same NIST violations. The optimized version cited specific NIST section numbers and quoted requirement text verbatim, making it read "like a professional audit report rather than a casual helpful assistant." The improvement is entirely formatting/traceability, not accuracy.

3. **Code Review (+5) with Actionability Drop:** Gemini uniquely observed a -1 actionability score on Test 1 because the strict certificate format "prevented the model from simply offering the corrected code at the end." The baseline helpfully provided a rewritten function; the optimized version stopped at the verdict. This is the strongest evidence that the certificate template's "Formal Conclusion" section needs an explicit remediation/output field.

---

## Token Efficiency Profile

| Metric | Value |
|--------|-------|
| Average token overhead | ~2.0-3.0x |
| Most efficient test | Test 10 Creative Brief (1.3x) |
| Least efficient test | Test 6 Business Decision (~2.8x) |
| Overhead on accuracy tasks | ~2.0x |
| Overhead on mixed tasks | ~2.0x |
| Overhead on creative task | ~1.3x |

Gemini's overhead estimate is the widest range among evaluators (2.0-3.0x vs. GLM's consistent ~2.0x). This may reflect more verbose certificate filling on complex tests.

---

## Unique Strengths Identified

1. **Highest absolute optimized scores (24.6/25 average):** Even starting from the highest baseline, Gemini's optimized responses scored highest overall. This suggests the skill works well with already-capable models, not just weaker ones.

2. **Most explicit about what didn't improve:** Gemini clearly identified that "Accuracy (+0.5) and Actionability (+0.3) improved least" and concluded "the skill makes responses more organized and verifiable, not necessarily more correct or more actionable." This is the most intellectually honest assessment of what the skill actually does.

3. **Surprising finding on certificate vs. persona:** Mixed tasks showed nearly as much improvement as accuracy tasks (+4.8 vs +5.4), despite using minimal persona. Gemini concluded "the certificate structure itself — not just persona management — is the primary driver of improvement." This decouples the value of the skill from PRISM persona theory.

---

## Actionability Gap (Per T3 Audit)

Gemini is the only evaluator that observed a **negative actionability delta** (Test 1: -1). The certificate format's "Formal Conclusion" section provides verdict, supporting traces, gaps, and confidence — but no corrected code. This is a direct instance of the Actionability Mandate violation: reasoning leads to a verdict but not to remediation.

**Recommendation from Gemini's evaluation:** "Add an 'Action/Output' section to the conclusion. The certificate currently ends with a verdict or gap analysis. Adding a required `Remediation / Corrected Code / Next Action` field to all templates would fix the actionability drop observed in Test 1."

---

## Key Takeaway

Gemini's evaluation is the best case study for the skill's "plug-and-play" efficiency. Starting from the strongest baselines, the certificate template still extracted consistent +4.2 average improvement with zero domain-specific customization. The unique actionability drop in Test 1 is the most actionable finding across all four evaluations — it identifies a specific, fixable gap in the template structure.
