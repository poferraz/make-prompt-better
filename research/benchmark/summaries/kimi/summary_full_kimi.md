# Global Multi-Architecture Synthesis

**Principal Research Lead:** Kimi (Moonshot AI)  
**Data Sources:**
- `benchmarks/glm/EVALUATION_RESULTS.md`
- `benchmarks/gemini/EVALUATION_RESULTS_v2.md`
- `benchmarks/qwen-code/EVALUATION_RESULTS_V2.md`
- `benchmarks/kimi/evaluation-results-v2.md`

**Synthesis Date:** 2026-04-01

---

## Comparative Performance Matrix

| Architecture | Avg Baseline | Avg Optimized | Avg Delta | Token Overhead | Traceability Lift | Win Rate |
|--------------|--------------|---------------|-----------|----------------|-------------------|----------|
| **GLM** | 19.5/25 | 24.3/25 | **+4.8** | ~2.0x | +1.8 avg | 9/10 |
| **Gemini** | 20.4/25 | 24.6/25 | **+4.2** | 2x–4x | +2.0 avg | 9/10 |
| **Qwen** | ~20.0/25 | ~24.3/25 | **+4.3** | ~1.67x | +1.8 avg | 10/10 |
| **Kimi** | ~17.0/25 | ~23.7/25 | **+6.6** | ~2.3x | +3.0 avg (perfect sweep) | 10/10 |
| **Grand Average** | **~19.1** | **~24.3** | **+5.2** | **~2.0x–2.5x** | **+2.1** | **~9.5/10** |

---

## Top 3 Key Findings Across All Architectures

### Finding 1: Traceability Is the Universal, Non-Negotiable Win
Across every model and every non-creative test, the certificate structure improved traceability—often by the maximum possible margin (+2 or +3 points on a 5-point scale). Kimi achieved a **perfect +3 sweep** across all 10 tests [see `summary_kimi.md`]. GLM and Qwen both averaged +1.8 to +2.0 [see `summary_glm.md`, `summary_qwen.md`]. This confirms that the `[P1]`, `[T1]` identifier system successfully eliminates "orphan claims" and forces auditable reasoning, regardless of model family.

### Finding 2: Diminishing Returns on Strong Baselines; Massive Gains on Weaker Baselines
Gemini and Qwen, with the highest baseline scores (~20.4 and ~20.0), saw the smallest deltas (+4.2 and +4.3) [see `summary_gemini.md`, `summary_qwen.md`]. Kimi, with the lowest baseline (~17.0), saw the largest delta (+6.6) [see `summary_kimi.md`]. This validates the hypothesis that semi-formal reasoning certificates function as a **scaffold**—the lower the baseline competence, the more dramatic the lift. Conversely, on tasks where the model already structures reasoning well (e.g., Medical Reasoning for Gemini and GLM), the certificate adds bureaucratic overhead without proportional correctness gains.

### Finding 3: Token Overhead Does Not Correlate with Accuracy Gain; Efficiency Varies by Architecture
Kimi imposed the highest token overhead (~2.3x–3.8x) but also delivered the highest delta (+6.6). Qwen imposed the lowest overhead (~1.67x) yet maintained a strong delta (+4.3) and a perfect win rate [see `summary_qwen.md`]. GLM sat in the middle (~2.0x overhead, +4.8 delta) [see `summary_glm.md`]. This proves that **heavier reasoning (more tokens) does not consistently result in higher accuracy deltas**; architecture-specific verbosity and prompt compression matter significantly. The skill's ~2.8x citation from Ugare & Chandra appears to be an upper bound rather than a fixed law.

---

## Creative Bypass Audit

All four evaluators independently confirmed that **Test 10 (Creative Brief)** is the domain where the certificate structure adds the least value:
- Gemini v2: **0-point tie** (24→24), with the evaluator calling the overhead "massive and arguably unnecessary" [see `summary_gemini.md`].
- GLM: **+1** (22→23), with the evaluator noting the baseline had a "more distinctive voice" [see `summary_glm.md`].
- Qwen v2: **+2** (21→23), but the structure was described as "essentially dead weight" [see `summary_qwen.md`].
- Kimi v2: **+2**, but the traces were called "artificial" and the output "needed tone guidance, not premises/traces/conclusion" [see `summary_kimi.md`].

**Conclusion:** The current `SKILL.md` guidance to "skip the certificate for pure creative tasks" is directionally correct but under-specified. A future **Creative Pivot** (narrative-empathy traces instead of logical evidence traces) should be tested as a third option between "pure persona" and "analytical certificate."

---

## Actionability Audit

The **Actionability Gap** was the most significant failure mode observed across architectures:
- **Gemini (Test 1 — Code Review):** Actionability *dropped* by -1 in v2 because the optimized response delivered a rigorous diagnosis but omitted the corrected code snippet [see `summary_gemini.md`].
- **GLM:** Structure and Traceability were the primary drivers of improvement (+1.5 and +1.8), while Actionability improved least (+0.3) [see `summary_glm.md`].
- **Kimi:** Gap overload sometimes reduced actionability by substituting lists of unknowns for decisive guidance [see `summary_kimi.md`].

**Conclusion:** The current `FORMAL CONCLUSION` templates do not universally mandate a remediation/fix output. The `Actionability Mandate` ("must include a mandatory `PROPOSED FIX` or `CORRECTED SNIPPET`") is currently mentioned in `SKILL.md` but not hard-coded into all domain templates. It needs to be.

---

## ACTIONABLE NEXT STEPS: Prioritized Roadmap for Skill and Template Hardening

### Priority 1: Harden the Actionability Mandate (Immediate)
Update `make-prompt-better/references/domain-templates.md` to include a **mandatory action field** in the conclusion of every task type where a user expects a deliverable:
- Code Review: `PROPOSED FIX: [corrected code snippet]`
- Compliance Check: `REMEDIATION PATH: [step-by-step instructions]`
- Decision-Making: `IMPLEMENTATION PLAN: [first 3 critical steps]`
- Medical Reasoning: `IMMEDIATE CLINICAL PRIORITIES: [specific next actions]`
- Legal Analysis: `LEGAL REMEDIES/NEXT STEPS: [specific actions or research needed]`

### Priority 2: Introduce a "Lite" Certificate Mode (Short-Term)
Create a compressed template variant targeting **~50% token reduction** (~1.5x overhead) by:
- Reducing Premises from 4–5 items to 2–3.
- Reducing Traces from 4–5 nested sub-bullets to 1–2 sentences + 1 caveat.
- Removing exhaustive counterargument requirements for low-stakes tasks.
Add a `mode: lite` parameter to the skill, with auto-selection logic based on task complexity.

### Priority 3: Design and Benchmark the "Creative Pivot" Template (Medium-Term)
Develop a new **Creative Alignment Template** that replaces `Evidence Traces` with `Narrative Traces`:
- Audience Empathy
- Substance Mapping
- Tone Calibration
- Cliché/Risk Check
The traces must act as a **backstage scaffold only**; the final creative output appears cleanly in the Conclusion with no meta-commentary. Test this against both pure-persona and analytical-certificate baselines.

### Priority 4: Architecture-Specific Optimization Guidance (Medium-Term)
Add a section to `SKILL.md` noting family-specific behaviors:
- **Kimi:** Apply anti-gap-overload guidance ("provide best-effort recommendations despite uncertainty").
- **Qwen:** Apply anti-verbosity guard ("reference by identifier instead of restating").
- **Gemini:** Always append the Actionability Mandate (most prone to stopping at verdict).
- **GLM:** Default to full certificate for analytical tasks; leverage naturally low overhead.

### Priority 5: Automated "Traceability Score" Self-Check (Long-Term)
Embed a final validation instruction in all optimized prompts:  
> "Before finalizing, verify that every claim in your conclusion references at least one T-identifier. If any claim lacks a supporting trace, either add a trace or remove the claim."

This converts traceability from a post-hoc evaluation metric into an in-prompt reasoning constraint.
