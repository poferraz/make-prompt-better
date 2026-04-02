# GLM-5.1 Evaluation Summary

**Source:** `benchmarks/glm/EVALUATION_RESULTS.md`
**Evaluator:** GLM-5.1 (self-evaluated)
**Date:** 2026-04-01

---

## Performance Profile

| Test | Domain | Task Type | Baseline | Optimized | Delta | Winner |
|------|--------|-----------|----------|-----------|-------|--------|
| 1 | Code Review | Accuracy | 18 | 25 | +7 | Optimized |
| 2 | Financial Analysis | Accuracy | 18 | 24 | +6 | Optimized |
| 3 | Medical Reasoning | Accuracy | 21 | 25 | +4 | Optimized |
| 4 | Legal Analysis | Accuracy | 18 | 23 | +5 | Optimized |
| 5 | Research Synthesis | Mixed | 19 | 23 | +4 | Optimized |
| 6 | Business Decision | Mixed | 20 | 25 | +5 | Optimized |
| 7 | Compliance Check | Accuracy | 20 | 25 | +5 | Optimized |
| 8 | Document Analysis | Mixed | 19 | 24 | +5 | Optimized |
| 9 | Comparative Analysis | Mixed | 20 | 25 | +5 | Optimized |
| 10 | Creative Brief | Alignment | 22 | 23 | +1 | Near-tie |
| **AVG** | | | **19.5** | **24.3** | **+4.8** | |

---

## Dimension-Level Averages

| Dimension | Avg Baseline | Avg Optimized | Avg Delta |
|-----------|-------------|---------------|-----------|
| Accuracy | 4.2 | 4.7 | +0.5 |
| Completeness | 4.3 | 5.0 | +0.7 |
| Structure | 3.5 | 5.0 | +1.5 |
| Actionability | 4.5 | 4.8 | +0.3 |
| Traceability | 3.0 | 4.8 | +1.8 |

**Primary drivers:** Structure (+1.5) and Traceability (+1.8). Accuracy (+0.5) and Actionability (+0.3) improved least. The skill makes responses more organized and verifiable, not necessarily more correct or more actionable.

---

## Surgical Precision Analysis

GLM-5.1 demonstrated the most granular per-dimension scoring of all evaluators, providing a complete 5x10 scoring matrix with specific per-test narrative justifications. This yields several mathematically rigorous observations:

### 1. Traceability is the sole universal improver

Traceability improved by exactly +2 points on every non-creative test (Tests 1-9). No other dimension showed this consistency. The variance across tests for traceability delta is **zero** (excluding Test 10), making it the only statistically stable improvement vector. Structure showed +2 on six tests and +1 on three tests (variance = 0.25), making it the second-most stable.

### 2. Actionability is structurally constrained

Actionability averaged only +0.3 improvement. In 6 of 10 tests, actionability delta was exactly 0. The certificate format's "Formal Conclusion" section delivers verdicts and gap analyses but frequently omits concrete remediation steps. This is not a model limitation but a structural gap in the certificate template itself. GLM-5.1's own recommendation: add an explicit "Remediation / Corrected Code / Next Action" field to all templates.

### 3. The creative penalty is quantified at +1 (not zero)

Unlike Gemini (0 delta) and Kimi (+5 on adjusted scale), GLM-5.1's creative test showed a marginal +1 improvement. The certificate structure added meta-commentary (e.g., "formal conclusion explaining tone strategy") that is irrelevant to creative output. The skill's own documentation correctly identifies creative generation as a skip domain. The +1 rather than 0 suggests GLM-5.1's baseline creative writing was already strong enough that the structure couldn't add value but also couldn't fully destroy it.

### 4. Mathematical overhead ratio

Token overhead averaged **2.0x** across Tests 1-9 (range: 1.8x to 2.4x), the lowest reported overhead across all evaluators. The theoretical prediction from Ugare & Chandra (2026) is ~2.8x. GLM-5.1's lower overhead may reflect more concise certificate filling or more efficient prompt construction. Value-per-token: +2.4 points improvement per doubling of tokens on accuracy tasks.

---

## Strengths of GLM-5.1 as Evaluator

1. **Most disciplined dimension separation:** Explicitly identified Structure and Traceability as the primary drivers rather than accuracy, avoiding the conflation error that would attribute all improvement to "better answers."
2. **Honest self-evaluation bias acknowledgment:** Flagged that self-evaluation inflates absolute scores but preserves directional reliability. Recommended separate judge models for proper rigor.
3. **PRISM calibration validation:** Correctly observed that Accuracy tasks (no persona) showed the largest improvements (+5.4), Mixed tasks (minimal persona) nearly as much (+4.8), and Alignment tasks (full persona) showed minimal improvement (+1.0). This is consistent with the PRISM finding that persona damages accuracy but helps alignment.

---

## Unique Failure Modes Identified

1. **No "confident but wrong" answers observed** but flagged as a risk in weaker domains where well-formatted incorrect traces could create false confidence.
2. **Diminishing returns on strong baselines:** Tests 3 (medical, baseline 21) and 10 (creative, baseline 22) showed the smallest improvements, consistent with Ugare & Chandra's ceiling-effect finding.
3. **Template verbosity for simple tasks:** Recommended a "light certificate" variant (premises + traces + conclusion, fewer mandatory fields) for 80% benefit at lower token cost.

---

## Key Takeaway

GLM-5.1's evaluation is the most methodologically disciplined of the four. Its primary contribution is the dimension-level decomposition proving that the skill's value proposition is structural (traceability +1.8, structure +1.5) rather than substantive (accuracy +0.5, actionability +0.3). The certificate format makes correct answers more provable, not necessarily more correct.
