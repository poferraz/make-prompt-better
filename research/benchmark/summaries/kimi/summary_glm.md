# GLM-5.1 Benchmark Summary: Surgical Precision & Mathematical Rigor

**Data Source:** `benchmarks/glm/EVALUATION_RESULTS.md`  
**Evaluator:** GLM-5.1 (self-evaluated)  
**Date:** 2026-04-01

---

## Performance Snapshot

| Metric | Score |
|--------|-------|
| Average Baseline | **19.5/25** |
| Average Optimized | **24.3/25** |
| Average Delta | **+4.8 points (+19.2%)** |
| Token Overhead | **~2.0x** (lowest reported across all architectures) |
| Tests Won by Optimized | **9/10** |

## Peak Performance Domains

GLM exhibited the largest gains in tasks where **concrete execution traces** and **numerical verification** are paramount:

- **Code Review (Test 1): +7** — The certificate structure forced specific input values (`price=100, discount_percent=20`) into execution traces, making bugs unambiguous and ruling out false positives. This is the skill's home territory.
- **Financial Analysis (Test 2): +6** — The optimized response distinguished between claims "supported by data" and those merely "consistent with data but not confirmed," a nuance the baseline blurred.
- **Legal Analysis (Test 4): +5** — Rule-application-counterargument frameworks created auditable reasoning chains and explicit jurisdictional gap-flagging.

## Architecture-Specific Strengths

1. **Mathematical Rigor:** GLM's optimized traces systematically calculated dollar OpEx, operating margins, and debt-service coverage without hallucinating unstated figures.
2. **Surgical Precision:** The model used the certificate structure to verify *correct* regions as well as buggy ones (e.g., confirming the negative-price guard worked as intended in Code Review).
3. **Efficiency Leader:** At ~2.0x token overhead, GLM demonstrated that the certificate structure can be executed with lower verbosity than the Ugare & Chandra ~2.8x citation.

## Failure Modes Observed

- **Bureaucratic Bloat:** On straightforward tasks, the model filled out Premises and Traces for information that could have been stated in one sentence.
- **Diminishing Actionability Returns:** Structure (+1.5) and Traceability (+1.8) were the primary drivers; Accuracy (+0.5) and Actionability (+0.3) improved least. The skill made responses more verifiable, not necessarily more actionable.
- **Creative Constraint (Test 10):** The certificate added meta-commentary irrelevant to creative output. The baseline had a more distinctive voice. Improvement was marginal (+1).

## Key Quote from Evaluator

> "The skill helps most where traceability is the primary weakness of unstructured responses."

## Recommendation for GLM-Specific Optimization

Leverage GLM's naturally lower token overhead by making the **full certificate the default** for all accuracy and mixed tasks on this architecture, while aggressively applying the **Creative Bypass** for generation tasks.
