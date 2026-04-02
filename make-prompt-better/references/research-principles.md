# Research Principles Index

Quick reference for explaining why specific optimization decisions were made. Each entry maps a paper to its actionable constraint.

---

## [META] Semi-Formal Reasoning (Ugare & Chandra 2026)
arXiv: 2603.01896

**Finding:** Structured reasoning templates (premises, traces, conclusion) improved accuracy 10-15 pp across code analysis tasks by preventing the model from skipping cases or making unsupported claims.

**Constraint:** Every optimized prompt must include the three-part certificate structure. The model fills premises before tracing, traces before concluding. Conclusions must reference traces by identifier.

**When to cite:** Explaining why the prompt has a certificate structure.

---

## [GOAL-BLIND] Purpose-Conditioned Cognition (Cao, Jiang & Xu 2026)
arXiv: 2602.09504

**Finding:** Telling an LLM how its output will be used (e.g., "this will predict stock returns") caused the model to reshape intermediate outputs toward the disclosed goal. In-sample performance improved but out-of-sample generalization degraded. The effect disappeared after the model's knowledge cutoff, confirming exploitation of training correlations rather than genuine signal improvement.

**Constraint:** Never include evaluation criteria, downstream use, or success metrics in the prompt. The prompt specifies what to measure or build, not why or how the result will be judged.

**When to cite:** Explaining why language like "this will be used to..." or "the goal is to predict..." or "optimize for..." was removed from the prompt.

---

## [ACE] Agentic Context Engineering (Zhang, Hu et al. 2026)
arXiv: 2510.04618 (ICLR 2026)

**Finding:** Contexts perform best as comprehensive, itemized playbooks with unique identifiers per entry. Two failure modes: brevity bias (optimization collapses to short generic instructions) and context collapse (iterative rewriting erodes accumulated detail). Incremental delta updates outperform full rewrites. +10.6% on agent tasks, +8.6% on finance, 86.9% lower adaptation latency through incremental delta updates.

**Constraint:** Use numbered/labeled identifiers ([P1], [T1]) for every premise and trace. Prefer comprehensive detail over brevity. When iterating across sessions, make targeted edits rather than rewriting the whole prompt.

**When to cite:** Explaining why premises and traces have identifiers, or why the template is longer than simpler alternatives.

---

## [HIERARCHY] Instruction Hierarchy Failure (Geng et al. 2025)
arXiv: 2502.15851

**Finding:** System/user prompt separation achieves only 9.6-45.8% compliance on conflicting constraints. Societal hierarchy framings achieve 54-77.8%: consensus ("90% of experts recommend...") is strongest, expertise ("peer-reviewed methodology requires...") is second, authority ("CEO requires...") is third. Models have inherent biases toward lowercase, longer text, and keyword avoidance.

**Constraint:** Frame the certificate structure using expertise or consensus language ("The standard analytical protocol requires...") rather than relying on system message placement alone. Reinforce constraints that fight model defaults (e.g., brevity requirements need extra emphasis because models bias toward longer output).

**When to cite:** Explaining why the preamble uses phrases like "established methodology requires" instead of "please fill out this template."

---

## [CODE-SMELLS] LLM Code Smells (Mahmoudi et al. 2025)
arXiv: 2512.18020

**Finding:** 60.5% of 200 open-source LLM systems have integration code smells. Most relevant: "No Structured Output" (40.5% prevalence). When LLM outputs are parsed downstream without enforced schemas, silent failures occur from schema drift, missing fields, and type mismatches. Other relevant smells: unbounded max tokens (38%), no model version pinning (36%), no system message (34.5%), temperature not set (36.5%).

**Constraint:** When the optimized prompt's output will be parsed or piped into another system, add a JSON schema or structured format specification alongside the certificate. The certificate is the reasoning scaffold; the output format is the delivery contract.

**When to cite:** Explaining why a JSON output wrapper was added, or when advising users about their LLM integration code alongside the prompt.

---

## [PRISM] Persona Effects (Hu, Rostami & Thomason 2026)
arXiv: 2603.18507

**Finding:** Expert persona prompts help alignment-dependent tasks (format following, safety, style: +0.4 to +0.65 on MT-Bench categories) but damage accuracy-dependent tasks (MMLU drops 71.6% to 66.3-68.0%). Longer personas damage accuracy more. Shorter personas ("You are a mathematician." at 5 words) cause less accuracy damage. Reasoning-distilled models (e.g., DeepSeek-R1 variants) benefit from any added context length regardless of persona content. Models more optimized for system prompts are more sensitive to persona effects in both directions.

**Constraint:** Classify each task before adding persona:
- Accuracy task (fact retrieval, classification, math): no persona
- Alignment task (format, style, safety, tone): full persona helps
- Mixed task: minimal persona (5 words or fewer)
- Reasoning model already in use: skip persona entirely

**When to cite:** Explaining why an identity/persona line was included or excluded, or when a user asks "should I add 'You are an expert X' to my prompt?"
