# When to Use Semi-Formal Reasoning

## 1. Introduction

Structured reasoning is inspired by code-analysis results studied by Ugare and Chandra (2026). Effects for this skill and other tasks are not established. More structure can increase token use and latency or over-constrain a task.

Not every prompt needs a certificate. This framework helps you decide when the structure helps and when it gets in the way.

## 2. Use Semi-Formal Reasoning When

### Accuracy gains are worth the latency cost

For technical tasks, explicit inputs and verification steps can make a proposed answer easier to review. The result and the cost trade-off still need to be evaluated for the actual model and task (Ugare & Chandra, 2026).

### Mistakes are costly

In domains where a wrong answer has real consequences, request evidence and review the result with appropriate domain expertise. A generated verification section is not proof that an error was caught (Ugare & Chandra, 2026).

### Input complexity exceeds surface pattern matching

When the input contains multiple interacting constraints, conditional logic, or nested dependencies, the model needs a structured reasoning path to avoid losing track of variables. Semi-formal prompting asks the model to articulate a reasoning chain, which still requires review (Ugare & Chandra, 2026).

### Auditable reasoning is required

If you need to show how the model arrived at its answer (for regulatory review, quality assurance, or debugging), semi-formal reasoning produces an explicit chain that can be inspected. Standard prompting gives you the answer without the audit trail.

### Hallucination risk is high

Tasks involving multiple sources or fine distinctions can invite unsupported claims. Ask for source references and check them; the prompt cannot establish that the model actually verified each claim (Ugare & Chandra, 2026).

### Multiple competing interpretations exist

When the input is ambiguous and the model could reasonably reach different conclusions, semi-formal reasoning makes the interpretive choice explicit. The specification phase forces the model to state its interpretation before proceeding, and the certification phase checks whether that interpretation is consistent throughout.

## 3. Skip Semi-Formal Reasoning When

### Simple factual lookups

If the model already knows the answer from pre-training ("What is the capital of Japan?"), adding a verification chain adds latency without adding accuracy. The baseline is already at ceiling.

### Creative generation vs. unconstrained stream-of-consciousness

Standard analytical certificates (premises, logical evidence traces, formal conclusion) constrain and flatten creative output (Ugare & Chandra, 2026). However, for structured creative, editorial, or commercial writing, route the prompt to **Mode 4: Creative & Divergent v2**, which combines backstage Narrative Traces with Verbalized Sampling (Zhang et al., 2025, 1.6x to 2.1x diversity gain) and discourse-level anti-SlopShape rules (Madler, 2026). Only skip scaffolding entirely for pure stream-of-consciousness generation.

### Model already achieves very high baseline accuracy

If the model gets the answer right 95%+ of the time without structure, the 10 to 15pp improvement from semi-formal reasoning is impossible to realize. The ceiling effect means you pay the latency cost for no gain. Use Lite mode (~1.5x overhead) only if you require an audit trail.

### Speed matters more than precision

Real-time applications (chat interfaces, live recommendations, interactive tools) may not tolerate the ~2.2x latency increase from Max mode. Use Lite mode (~1.5x) or skip the structure if sub-second latency is mandatory.

### Using a reasoning-distilled model (LRM)

Per PRISM (Hu, Rostami & Thomason, 2026) and agentic harness evaluations (Lee et al., 2026), reasoning-distilled and extended-thinking models (such as o3, DeepSeek-R1, Claude Extended Thinking, and Gemini Thinking) perform path exploration internally. Forcing verbose step-by-step trace narration in the visible output triggers the overthinking trap and inflates token costs. For LRMs, route to **Mode 3: LRM / Harness Mode**, which keeps explicit `[P]` Premises and `[V]` Verification Gates while leaving path exploration to the model's native thinking tokens.

## 4. Decision Flowchart

```
START
│
├─► Is this an AGENTS.md, CLAUDE.md, or multi-turn agent harness?
│   ├─► YES → Use Mode 3 (LRM / Harness Mode: Minimal Viable Context).
│   │         Fulfill any explicitly requested overview/layout/style items
│   │         compactly in Section 0 (<=5 lines, Gloaguen et al., 2026);
│   │         devote 85%+ to non-inferable commands, invariants, and gates.
│   └─► NO → Continue below.
│
├─► Are you targeting a Large Reasoning Model (o3, R1, Extended Thinking) or async/concurrency code?
│   ├─► YES → Use Mode 3 (Code-First LRM Verification Harness, Template 12).
│   │         Omit persona (Hu et al., 2026); generate complete executable code
│   │         first, followed by post-hoc [V1] -> [V2] gates (<25% overhead).
│   └─► NO → Continue below.
│
├─► Is the task creative, editorial, or divergent ideation?
│   ├─► YES → Use Mode 4 (Creative & Divergent v2).
│   │         Apply internal [NT0] Verbalized Sampling (p <= 0.20, Zhang et al., 2025)
│   │         + Anti-SlopShape rules (Madler, 2026); output clean finished copy.
│   └─► NO → Continue below.
│
├─► Is the task accuracy-critical?
│   ├─► YES
│   │   └─► Is it a high-stakes multi-constraint audit (medical, legal, financial, security)?
│   │       ├─► YES → Use Mode 1 (Max Certificate, ~1.65x-2.2x overhead, anti-redundancy).
│   │       └─► NO  → Use Mode 2 (Lite Certificate, ~1.45x overhead, default analytical mode).
│   └─► NO → Use Persona + Constraints (or Lite Certificate with <=5-word persona).
│
└─► END
```

## 5. Examples

### Scenario 1: Financial compliance audit

**Prompt:** "Review this transaction log for activities that violate anti-money-laundering regulations."

**Recommendation:** Use semi-formal reasoning.

**Reasoning:** Accuracy-critical. Mistakes are costly (regulatory penalties). Baseline accuracy on AML pattern detection is not at ceiling. The input contains multiple interacting data points that require structured reasoning. The requested verification may highlight omissions, but it does not prove violations were caught. No persona needed (accuracy task).

### Scenario 2: Blog post generation

**Prompt:** "Write a 500-word blog post about the benefits of remote work."

**Recommendation:** Skip semi-formal reasoning.

**Reasoning:** Creative generation task. The model produces fluent prose without structure. Adding a certification phase would constrain the writing and add latency for no measurable quality gain. Use a persona instead ("You are a workplace culture writer") to align tone.

### Scenario 3: Code review for security vulnerabilities

**Prompt:** "Review this authentication module for security vulnerabilities."

**Recommendation:** Use semi-formal reasoning.

**Reasoning:** Accuracy-critical with high mistake cost. The input is complex (authentication logic with multiple edge cases). Hallucination risk is moderate (the model might miss subtle vulnerabilities or invent false ones). The prompt asks the model to check each claimed vulnerability against the code; a human must verify the claims. No persona needed.

### Scenario 4: Formatting a spreadsheet as a table

**Prompt:** "Format this CSV data as a markdown table."

**Recommendation:** Skip semi-formal reasoning.

**Reasoning:** Alignment-only task. The model knows how to format tables. No accuracy risk. No ambiguity. Use a constraint if the table format is unusual, but skip the full specification-certification structure.

### Scenario 5: Medical symptom differential diagnosis

**Prompt:** "Given these symptoms (fever, joint pain, rash after tick exposure), list the most likely diagnoses."

**Recommendation:** Use semi-formal reasoning.

**Reasoning:** Accuracy-critical with life-and-death stakes. Baseline accuracy on differential diagnosis is not at ceiling. Multiple competing interpretations exist (Lyme disease, Rocky Mountain spotted fever, viral illness). The prompt asks for each symptom to be considered and for diagnoses to be checked against the reported symptoms; the result still requires clinical review. No persona (accuracy task).

### Scenario 6: Quick email draft

**Prompt:** "Draft a short email confirming tomorrow's meeting."

**Recommendation:** Skip semi-formal reasoning.

**Reasoning:** Alignment-only task with low accuracy requirements. The model produces competent meeting emails without structure. Speed matters (this is likely a real-time task). Persona optional.

### Scenario 7: Data pipeline transformation logic

**Prompt:** "Write a SQL query that joins these three tables, filters by date range, and aggregates revenue by region."

**Recommendation:** Use semi-formal reasoning.

**Reasoning:** Accuracy-critical. The input has multiple interacting constraints (join logic, date filter, aggregation). Mistakes in SQL logic can corrupt data downstream. Baseline accuracy on multi-join queries is below 95%. The prompt asks for join conditions and filter logic to be stated and checked; the resulting query still needs independent verification. No persona.

### Scenario 8: Brand voice style guide creation

**Prompt:** "Create a style guide defining our company's brand voice for marketing materials."

**Recommendation:** Skip semi-formal reasoning.

**Reasoning:** Alignment-dependent creative task. The output is a set of guidelines, not a factual answer. Structure would over-constrain the creative process of defining voice attributes. Use a persona ("You are a brand strategist") to align the output with professional marketing norms.

### Scenario 9: Legal contract clause analysis

**Prompt:** "Identify any clauses in this contract that create unusual liability exposure."

**Recommendation:** Use semi-formal reasoning.

**Reasoning:** Accuracy-critical with high mistake cost. The input is long and requires careful reading. Multiple competing interpretations exist for legal language. The prompt asks the model to justify each flagged clause; legal review is still required. No persona (accuracy task per Hu, Rostami & Thomason, 2026).

### Scenario 10: Using a reasoning-distilled model for code generation

**Prompt:** "Implement a binary search tree with insert, delete, and search operations in Python."

**Recommendation:** Skip semi-formal reasoning.

**Reasoning:** If the model is reasoning-distilled (e.g., DeepSeek-R1-Distill, QwQ), the structured scaffold is redundant. The model has internalized step-by-step reasoning during distillation (Hu, Rostami & Thomason, 2026). Provide detailed context about the requirements instead. If the model is not distilled, semi-formal reasoning would help here (accuracy-critical, multiple interacting methods).

---

**References:**

Ugare, A. & Chandra, A. (2026). "A Prompt Certification Framework for Enhanced Code Generation." arXiv:2603.01896.

Hu, Z., Rostami, M. & Thomason, J. (2026). "Expert Personas Improve LLM Alignment but Damage Accuracy." arXiv:2603.18507.
