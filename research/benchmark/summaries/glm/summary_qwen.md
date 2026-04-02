# Qwen Code Evaluation Summary

**Source:** `benchmarks/qwen-code/EVALUATION_RESULTS_V2.md`
**Evaluator:** Qwen Code (Qwen3.5, 256K context)
**Date:** 2026-04-01

---

## Performance Profile

| Test | Domain | Task Type | Baseline | Optimized | Delta | Winner |
|------|--------|-----------|----------|-----------|-------|--------|
| 1 | Code Review | Accuracy | 21 | 25 | +4 | Optimized |
| 2 | Financial Analysis | Accuracy | 20 | 24 | +4 | Optimized |
| 3 | Medical Reasoning | Accuracy | 21 | 25 | +4 | Optimized |
| 4 | Legal Analysis | Accuracy | 20 | 25 | +5 | Optimized |
| 5 | Research Synthesis | Mixed | 18 | 23 | +5 | Optimized |
| 6 | Business Decision | Mixed | 21 | 25 | +4 | Optimized |
| 7 | Compliance Check | Accuracy | 21 | 25 | +4 | Optimized |
| 8 | Document Analysis | Mixed | 19 | 25 | +6 | Optimized |
| 9 | Comparative Analysis | Mixed | 20 | 25 | +5 | Optimized |
| 10 | Creative Brief | Alignment | 21 | 23 | +2 | Optimized |
| **AVG** | | | **20.2** | **24.5** | **+4.3** | |

---

## Methodical Document Breakdown

Qwen Code's evaluation is distinguished by its systematic approach to analyzing each test's evidence structure. While other evaluators provided summary verdicts, Qwen documented specific methodological observations per test:

### Document Analysis (Test 8, +6) — Largest Improvement

The certificate structure forced systematic evaluation of each claim separately (T1-T4). The baseline listed red flags but "didn't always explain the underlying reasoning." The optimized version explained **why** each claim was problematic:
- "Absolute claim requires strong evidence"
- "Precise number without evidence suggests fabrication or cherry-picking"

This is the clearest example of the skill forcing analytical depth rather than just analytical breadth.

### Research Synthesis (Test 5, +5) — Anti-Hallucination Value

Qwen explicitly noted that the optimized response was "more explicit about evidence quality and limitations." It differentiated the Bloom study (RCT, stronger evidence) from surveys (self-reported, weaker evidence), and flagged NBER papers as "working paper status (not yet peer-reviewed)." The baseline treated all studies more uniformly. This is the anti-hallucination guard in action: the certificate structure forces explicit quality grading of evidence.

### Legal Analysis (Test 4, +5) — Quantified Precision

Qwen quantified the geographic scope as "approximately 125,600 square miles" and provided specific state-by-state enforceability analysis with a formatted table. The baseline mentioned jurisdiction matters; the optimized version named specific states and their approaches. The counterargument section (T4) was flagged as a "notable improvement" — it explained **when** enforcement might occur, not just that it probably wouldn't.

---

## Task Type Decomposition

| Task Type | Tests | Avg Baseline | Avg Optimized | Avg Delta |
|-----------|-------|-------------|---------------|-----------|
| Accuracy | 1-4, 7 | 20.6 | 24.8 | +4.2 |
| Mixed | 5, 6, 8, 9 | 19.5 | 24.5 | +5.0 |
| Alignment | 10 | 21 | 23 | +2 |

**Mixed tasks benefited most (+5.0)** — the only evaluator showing this pattern. Qwen's explanation: "These tasks require both factual accuracy AND good presentation. The certificate structure helped organize both dimensions systematically." This suggests the skill's value extends beyond pure accuracy into communication quality.

---

## Token Cost Profile

| Metric | Value |
|--------|-------|
| Average overhead | ~67% (1.67x) |
| Most efficient test | Test 1 Code Review (36%) |
| Least efficient test | Test 8 Document Analysis (119%) |
| Overhead on accuracy tasks | ~57% average |
| Overhead on mixed tasks | ~80% average |
| Overhead on creative task | 50% |

Qwen reported the **lowest token overhead** of all evaluators at ~67% (1.67x), significantly below the skill's documented ~2.8x prediction and below GLM's ~2.0x. This may reflect more concise certificate filling or more efficient prompt construction by Qwen3.5.

---

## Risk Assessment

Qwen provided the most granular risk assessment of any evaluator:

1. **Knowledge cutoff acknowledgment:** Explicitly noted in Test 5 that "cannot access studies published after knowledge cutoff; cannot verify specific citations." This is honest but highlights that the certificate structure cannot overcome missing information.

2. **No "confident but wrong" cases:** All optimized responses reached the same conclusions as baselines. The structure didn't produce false confidence.

3. **Creative task overhead:** The +2 improvement on Test 10 with 50% more tokens was deemed "not worth it for creative brief." The certificate structure added overhead without proportional value.

4. **Structure redundancy:** In Tests 2, 3, and 6, some trace sections repeated information that could have been stated once. Recommended an anti-verbosity guard.

---

## Unique Recommendations

Qwen provided the most specific, actionable recommendations for skill improvement:

1. **"Skip certificate" decision flowchart:** Not just documentation guidance, but a visual decision tree at the top of SKILL.md routing users away from certificate structure for creative/alignment tasks.

2. **Lightweight certificate option:** Premises + conclusion only, no detailed traces, for tasks where full structure is overkill.

3. **Anti-verbosity guard:** "If a trace section would repeat information from another section, reference it by identifier instead of restating."

4. **Document analysis template promotion:** Test 8 showed the largest improvement (+6). Recommend making this template more prominent in skill documentation.

5. **Traceability self-check:** "Before finalizing, verify that every claim in your conclusion references at least one T-identifier."

6. **Token cost documentation correction:** The skill claims ~2.8x but this evaluation found ~67% (1.67x). Recommend updating documentation.

---

## Key Takeaway

Qwen Code's evaluation is the most methodical document-level analysis of the four evaluators. Its primary contribution is demonstrating that the certificate structure's value extends to **evidence quality assessment** (not just evidence citation) — the skill forces models to grade their sources, not just cite them. The 67% token overhead finding, if validated by other evaluators, would significantly improve the skill's cost/benefit ratio.
