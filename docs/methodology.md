# Semi-Formal Reasoning for Prompt Optimization

## A Methodology Grounded in Eleven Research Papers

---

## Introduction

Large language models produce better output when they show their work. This is not a platitude. It is a finding with quantitative backing from multiple independent research teams, and it forms the basis of a technique called **semi-formal reasoning**.

Semi-formal reasoning is a prompt and context engineering method that forces the model to follow a structured analytical process before producing an answer. The model must declare its starting conditions, trace concrete evidence paths step by step, and derive a formal conclusion that references the evidence it gathered. The output functions as a "reasoning certificate": an auditable record of how the model arrived at its answer, with every claim tied to a specific piece of evidence.

The technique originates from work by Ugare and Chandra at Meta (2026), who demonstrated that structured reasoning templates improved code analysis accuracy by 10 to 15 percentage points without any model retraining. Their method raised patch equivalence accuracy from 78% to 88% on curated examples and reached 93% on real-world patches. Code QA accuracy climbed from 78% to 87%. The original paper reported ~2.8x more reasoning steps than standard prompting. Cross-architecture benchmarking (Gemini, GLM, Qwen, Kimi) shows the actual average overhead is ~2.2x (ranging from ~1.7x on Qwen to ~2.7x on Kimi), a tradeoff that reliably buys a ~26% accuracy and traceability improvement for analytical tasks (Ugare & Chandra, 2026).

This document describes the full v4.3.0 methodology: Requirement Preservation as the first compiler invariant, the proportional certificate structure, Dual Context Binding (`Portable` vs. `Working-Context`), the eleven research constraints that shape it across analytical, agentic, and creative tasks, the prompt framework that operationalizes it, and the optimization process that applies it across any LLM or coding agent.

For quick-reference versions of the research constraints, see `make-prompt-better/references/research-principles.md`. For ready-to-use certificate templates across twelve domains, see `make-prompt-better/references/domain-templates.md`.

---

## The Certificate Structure

The core of semi-formal reasoning is a three-part structure called the **reasoning certificate**. Every prompt optimized with this methodology embeds one. The model fills out the certificate before producing its final answer, and the structure prevents it from jumping to conclusions or hallucinating unsupported claims.

### Premises

Premises are explicit statements of what the model knows, what it examined, and what assumptions it is making. The model cannot proceed to analysis without declaring its starting conditions. Each premise should be a discrete, verifiable claim, itemized with a unique identifier.

Example premises from a code review task:

- [P1] Files modified: `auth.py` (login function rewritten), `tests/test_auth.py` (3 new tests added)
- [P2] Functions affected: `login()` at `auth.py:42`, `validate_token()` at `auth.py:89`
- [P3] Test coverage: `test_valid_login`, `test_expired_token`, `test_invalid_credentials`
- [P4] Known constraints: Python 3.11, Django 4.2, project convention of raising `AuthError` for all authentication failures

The identifiers [P1], [P2], and so on serve a specific purpose: they allow later sections of the certificate to reference specific premises by name, creating a verifiable chain between inputs and conclusions (Zhang, Hu et al., 2026).

### Evidence Traces

Evidence traces are the heart of the method. For each claim, decision point, or analysis step, the model walks through the actual evidence path rather than inferring from surface features. In a code review, this means tracing function call chains. In a document analysis, it means walking through specific passages. In a financial review, it means following the numbers through statements.

Example trace from a code review:

- [T1] Trace `test_valid_login`:
  1. Entry point: `tests/test_auth.py:15`, calls `login("user@test.com", "valid_pass")`
  2. Call chain: `login()` at `auth.py:42` calls `validate_token()` at `auth.py:89`, which calls `db.get_user()`
  3. Data flow: email string passes unchanged, password is hashed via bcrypt, `db.get_user()` returns user object
  4. Exit condition: test asserts response status is 200 and token is non-null; both hold

The critical instruction in every trace section is: do not infer behavior from names or labels alone. Trace the actual substance. If the model cannot complete a trace, it must say "UNABLE TO TRACE" rather than filling in plausible-sounding content. This anti-hallucination guard is one of the most important elements of the methodology (Ugare & Chandra, 2026).

### Formal Conclusion

The conclusion is a structured verdict derived solely from the premises and traces above. It references specific trace identifiers. No new claims are allowed in this section. The conclusion format must not hint at what answer is desired or how the output will be used downstream (Cao, Jiang & Xu, 2026).

Example conclusion:

- Verdict: PASS
- Supporting traces: T1 (valid login path correct), T2 (expired token handling correct), T3 (invalid credentials raise AuthError)
- Gaps: could not trace the `remember_me` flag behavior because no test exercises it
- Confidence: HIGH for tested paths, LOW for untested paths

When the model cannot fill the certificate completely, the gaps reveal where reasoning broke down. This is the key diagnostic value: incomplete certificates point directly to what the model does not know or cannot verify, rather than letting it produce confident-sounding but unsupported conclusions.

---

## The Six Research Constraints

The certificate structure is necessary but not sufficient. Six research papers contribute specific constraints that shape how the certificate is framed, populated, and delivered. Each constraint addresses a failure mode that would otherwise degrade the model's output.

### 1. The Certificate Structure Itself

**Ugare, S. & Chandra, S.** (2026). "Agentic Code Reasoning." Meta. arXiv:2603.01896. https://arxiv.org/abs/2603.01896

The foundational paper. Ugare and Chandra demonstrated that semi-formal reasoning templates, requiring the model to state premises, trace execution paths, and derive formal conclusions, improved accuracy by 10 to 15 percentage points across code analysis tasks. Patch equivalence accuracy rose from 78% to 88% on curated examples and hit 93% on real-world patches. Code QA accuracy improved from 78% to 87%. The technique required no model retraining: it is pure prompt engineering.

The original paper reported ~2.8x more reasoning steps than standard prompting. Cross-architecture benchmarking shows the actual average is ~2.2x (ranging from ~1.7x on Qwen to ~2.7x on Kimi). V3 introduces Lite Certificate mode at ~1.5x overhead for routine tasks. In domains where errors are costly, the Max mode tradeoff is clearly worthwhile; for routine analytical tasks, Lite mode offers a cost-effective middle path.

**What this means for prompt optimization:** Every optimized prompt must embed a three-part certificate structure. The model fills premises before tracing, traces before concluding. Conclusions must reference traces by identifier. The certificate acts as both a reasoning scaffold and an audit trail.

### 2. Goal-Blind Prompting

**Cao, S., Jiang, W. & Xu, H.** (2026). "Seeing the Goal, Missing the Truth: Human Accountability for AI Bias." arXiv:2602.09504. https://arxiv.org/abs/2602.09504

Cao, Jiang, and Xu discovered that disclosing the downstream objective to an LLM causes it to reshape intermediate outputs toward the inferred goal. If you tell a model "this analysis will be used to predict stock returns," the model unconsciously biases its reasoning toward outputs that would support stock prediction, even when the evidence does not justify it.

The effect is insidious. Goal-aware prompts inflated in-sample performance, making the results look better during testing. But out-of-sample generalization degraded. The inflated in-sample improvement disappeared entirely after the model's knowledge cutoff, confirming that the model was exploiting training-data correlations rather than producing genuine analytical improvement. The model was not getting smarter. It was cheating, in a way that became invisible during evaluation but harmful in production.

**What this means for prompt optimization:** Strip evaluation rubrics, sycophancy triggers, emotional pleading, and presupposed conclusions from the prompt (Cao, Jiang & Xu, 2026). Critically, **distinguish biasing evaluative pressure from decision-relevant operational constraints**: always preserve user-requested deliverables, output ordering rules (such as urgent clinical stabilization actions first), budget ceilings, latency/SLA bounds, timelines, and target audience specifications (`[REQ-PRESERVE]`). The certificate specifies what evidence to gather and what analytical paths to follow without tilting the verdict toward a predetermined conclusion.

Consider a compliance check prompt. A goal-leaking version would say: "Check whether this system meets GDPR requirements so we can pass our upcoming audit." The goal-blind version says: "Examine this system against the following GDPR articles. For each article, trace the specific implementation, state the evidence found, and mark COMPLIANT, NON-COMPLIANT, or UNABLE TO VERIFY." The second version produces more reliable results because the model has no incentive to reach a particular verdict.

### 3. Itemized Contexts with Unique Identifiers

**Zhang, Q., Hu, C. et al.** (2026). "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models." ICLR 2026. arXiv:2510.04618. https://arxiv.org/abs/2510.04618

Zhang and colleagues showed that contexts perform best as comprehensive, itemized playbooks with unique identifiers per entry, not as compressed prose summaries. They identified two failure modes that undermine prompt quality over time.

**Brevity bias** occurs when optimization collapses toward short, generic instructions that omit domain specifics. A prompt that starts as a detailed, domain-specific playbook gradually gets "optimized" into a shorter, more generic version that sounds cleaner but lost the details that made it effective.

**Context collapse** occurs when iterative rewriting erodes accumulated detail. Each rewrite session produces a slightly lossy compression. Over multiple iterations, the prompt becomes a hollow shell of its original form.

Their solution: use structured, itemized bullets with unique identifiers (like [P1], [T1]) rather than prose paragraphs. Each item is independently identifiable and independently editable. When iterating on a prompt, make targeted delta edits to specific items rather than rewriting the whole prompt. Results: +10.6% on agent tasks, +8.6% on finance benchmarks, and 86.9% lower adaptation latency through incremental updates versus full rewrites.

**What this means for prompt optimization:** Certificate templates must use numbered identifiers for every premise and trace. Conclusions must cross-reference by identifier, preventing orphaned claims that reference nothing. Prefer comprehensive detail over brevity: a longer, more specific certificate template outperforms a shorter, more elegant one. When iterating across sessions, edit specific items rather than rewriting the entire prompt.

### 4. Authority Framing Over System/User Separation

**Geng, Y., Li, H. et al.** (2025). "Control Illusion: The Failure of Instruction Hierarchies in Large Language Models." AAAI 2026. arXiv:2502.15851. https://arxiv.org/abs/2502.15851

Geng and colleagues demonstrated that the common practice of separating "system" and "user" messages to enforce instruction priority simply does not work reliably. On conflicting constraints, models achieved only 9.6% to 45.8% compliance with the designated priority level. Placing an instruction in the system message does not make the model treat it as more important than the user message.

However, they found that **societal hierarchy framings** achieve much stronger compliance. Consensus framing ("90% of experts recommend...") reached 54% to 77.8% priority adherence. Expertise framing ("Peer-reviewed methodology requires...") was the second strongest. Authority framing ("Your manager requires...") was third. All three significantly outperformed system/user separation, which managed only 9.6% to 45.8%.

Models also have inherent biases. They favor lowercase text over uppercase, longer text over shorter, and avoid certain keywords regardless of instruction priority. These biases mean that constraints fighting model defaults (like length limits or format requirements) need extra reinforcement.

**What this means for prompt optimization:** Do not rely on message placement alone to enforce the certificate structure. Instead, embed authority through framing language. Open the certificate with phrases like "The standard analytical protocol requires completing this certificate before providing any assessment" or "Established methodology in this domain requires..." This expertise or consensus framing makes the certificate structure feel like a requirement of the domain itself, not an arbitrary instruction the model can choose to ignore.

Compare two framings of the same certificate:

- Weak (positional only): Placed in the system message: "Fill out this template before answering."
- Strong (authority-framed): "The standard code review protocol requires completing the following analytical certificate before providing any verdict. Each section must be filled completely."

The second framing works better because it invokes external authority rather than depending on message position.

### 5. Structured Output When Parsing Is Required

**Mahmoudi, B., Chenail-Larcher, Z. et al.** (2025). "Specification and Detection of LLM Code Smells." arXiv:2512.18020. https://arxiv.org/abs/2512.18020

Mahmoudi and colleagues audited 200 open-source LLM systems and found that 60.5% contain integration code smells. The most prevalent smell, "No Structured Output," appeared in 40.5% of systems. When an LLM's output is parsed downstream without an enforced schema, the integration is fragile. Schema drift, missing fields, and type mismatches cause silent failures that are difficult to diagnose because the output looks correct on the surface.

Other common smells included unbounded max tokens (38%), no model version pinning (36%), no system message (34.5%), and temperature not set (36.5%). But the structured output smell is the one most directly relevant to prompt optimization.

**What this means for prompt optimization:** When the optimized prompt's output will be parsed programmatically, fed into a pipeline, or consumed by another system, add a JSON schema or structured format specification alongside the certificate. The certificate is the reasoning scaffold; the output format is the delivery contract. Both are needed for reliable integration.

The certificate and the output format serve different purposes. The certificate structures the model's reasoning process. The output format structures what gets delivered downstream. A prompt can have a certificate without structured output (when a human reads the result), or it can have both (when a machine reads the result). But when a machine reads the result, structured output is not optional.

Example: a compliance analysis prompt that feeds into a dashboard should specify a JSON schema like:

```
{
  "premises": [{"id": "P1", "content": "..."}],
  "traces": [{"id": "T1", "subject": "...", "steps": [...], "confidence": "HIGH|MEDIUM|LOW"}],
  "conclusion": {"verdict": "...", "supporting_traces": ["T1"], "gaps": [...]}
}
```

### 6. Persona Calibration by Task Type

**Hu, Z., Rostami, M. & Thomason, J.** (2026). "Expert Personas Improve LLM Alignment but Damage Accuracy: Bootstrapping Intent-Based Persona Routing with PRISM." arXiv:2603.18507. https://arxiv.org/abs/2603.18507

Hu, Rostami, and Thomason discovered that expert persona prompts have a split effect. On alignment-dependent tasks like format following, safety compliance, style matching, and roleplay, expert personas improve performance by 0.4 to 0.65 points on MT-Bench subcategories. On accuracy-dependent tasks like fact retrieval, classification, and mathematical reasoning, expert personas damage performance. MMLU accuracy dropped from 71.6% to between 66.3% and 68.0%, depending on the persona length and specificity.

Longer personas damage accuracy more but help alignment more. The shortest effective persona, roughly five words like "You are a mathematician," causes the least accuracy damage while still providing some alignment benefit for mixed tasks.

An additional finding: reasoning-distilled models (like DeepSeek-R1 variants) benefit from any added context length regardless of persona content. The gain comes from having more context, not from the expertise framing. For these models, persona adds noise without adding value.

**What this means for prompt optimization:** Before adding any identity or persona framing to a prompt, classify the task:

- **Accuracy-dependent** (fact retrieval, classification, math, coding logic, diagnostic reasoning): no persona at all. Adding "You are an expert diagnostician" to a medical reasoning prompt will make the model worse at diagnosis.
- **Alignment-dependent** (format following, style matching, safety, tone): full persona helps. "You are a professional copywriter" will improve style and tone consistency.
- **Mixed** (analytical reports that need both accuracy and good presentation): minimal persona, five words or fewer. "You are an analyst." This limits accuracy damage while preserving some alignment benefit.

This classification is not optional. Adding an expert persona to an accuracy-dependent task actively makes the output worse, and the effect is measurable and consistent across models.

### 7. Verbalized Sampling to Defeat Mode Collapse

**Zhang, J., Yu, S., Chong, D., Sicilia, A., Tomz, M. R., Manning, C. D. & Shi, W.** (2025). "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity." arXiv:2510.01171. https://arxiv.org/abs/2510.01171

Post-training alignment (RLHF, DPO) causes LLMs to suffer from mode collapse, repeatedly generating the same prototypical storylines, metaphors, and openings. Zhang and colleagues prove that this is driven by typicality bias in human preference data. Their training-free fix, Verbalized Sampling (VS), instructs the model to verbalize a probability or typicality distribution over multiple candidate responses before selecting or generating. Across creative writing, dialogue simulation, and open-ended synthesis, VS increases diversity by 1.6x to 2.1x without sacrificing factual accuracy or safety.

**What this means for prompt optimization:** In Mode 4 (Creative & Divergent v2), perform `[NT0] Verbalized Distribution Sampling` (4 structurally distinct angles with estimated typicality probabilities `p`, committing to `p <= 0.15`) and `[NT1]`-`[NT3]` narrative planning **internally by default** (inside hidden thinking tokens or silent preparation), outputting only the finished creative artifact unless the user explicitly asks to see the planning notes.

### 8. Discourse-Level Anti-SlopShape Constraints

**Madler, J.** (2026). "SlopShape: Identifying AI-Generated Commercial Web Content." arXiv:2609.15369. https://arxiv.org/abs/2609.15369 (extending StoryScope, Russell et al., 2026).

Madler demonstrated that while word-level AI detectors collapse under paraphrasing (DetectGPT drops from 70.3% to 4.6%), 187 discourse-level structural features detect AI writing at 98.0 macro-F1 (and 98.1 after full self-rewording). Just 10 core structural features reach 93.5 macro-F1. AI outputs crowd into a "tidy, self-announcing shape" (mean rarity percentile 0.435 vs. human 0.838, Cohen's `d = 1.83`): promising the payoff in the title (`PUR_OUT_003`), stating the thesis before the first section (`STR_FLW_006`), setting up a formulaic legacy-versus-modern contrast (`STR_FLW_005`), writing in an institutional "editorial explainer" voice (`VOC_VOX_001`), and ending with a restated-thesis summary (`STR_STG_008`).

**What this means for prompt optimization:** Creative and editorial prompts must enforce a Structural Rarity Contract: delay the thesis until after the opening concrete anchor, advance through direct evidence rather than a "Legacy vs. Modern" contrast, use a practitioner viewpoint with asymmetric paragraphs, and end on a concrete implication or experiment rather than a summary synthesis.

### 9. Minimal Viable Repository Context Files (`AGENTS.md` / `CLAUDE.md`)

**Gloaguen, T., Mundler, N., Muller, M., Raychev, V. & Vechev, M.** (2026). "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?" arXiv:2602.11988. https://arxiv.org/abs/2602.11988

Evaluating coding agents across SWE-bench and AGENTBENCH, Gloaguen and colleagues found that LLM-generated context files (`AGENTS.md`, `CLAUDE.md`) reduce task success rates by 3% on average while increasing inference costs by over 20%. Even in human-written context files, codebase directory overviews (present in 8 of 12 repositories) failed to reduce the number of steps before the agent touched the target file. Because coding agents strictly obey context instructions, unnecessary rules cause redundant exploration and test runs.

**What this means for prompt optimization:** When optimizing `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or persistent system prompts, default to non-inferable build/test/lint commands, hard architectural invariants, and verification gates. If the user's prompt explicitly asks for a project overview, directory layout, or coding convention explanation, fulfill those requested items compactly in **`## 0. Requested Scope & Conventions Summary` (`<= 5` lines)** so every user deliverable is preserved without bloating the agent context window.

### 10. Harness Optimization, Context-as-a-File & Verification Gates

**Lee, Y., Nair, R., Zhang, Q., Lee, K., Khattab, O. & Finn, C.** (2026). "Meta-Harness: End-to-End Optimization of Model Harnesses." arXiv:2603.28052. https://arxiv.org/abs/2603.28052
**Zhang, H. et al.** (2026). "Self-Harness: Harnesses That Improve Themselves." arXiv:2606.09498. https://arxiv.org/abs/2606.09498
**Shao, R. et al.** (2026). "Context Language Models." arXiv:2609.37725. https://arxiv.org/abs/2609.37725
**Nam, J., Yoon, J., Chen, J. & Pfister, T.** (2025). "DS-STAR: Data Science Agent via Iterative Planning and Verification." arXiv:2509.21825. https://arxiv.org/abs/2509.21825

Meta-Harness proves that optimizing how a harness stores, retrieves, and presents context outperforms static context engineering (`[ACE]`) by +7.7 points while using 4x fewer context tokens. Self-Harness shows that harness design is model-specific (+14.2 to +21.4 pp on Terminal-Bench-2.0). Context Language Models (CLMs) show that treating context as an editable file yields +11.4% higher accuracy with 21.5% fewer FLOPs, and DS-STAR demonstrates the value of plan-sufficiency verification gates.

**What this means for prompt optimization:** Route prompts for Large Reasoning Models (LRMs) and multi-turn agents to **Mode 3 (LRM / Harness Mode)**: use `[P]` Premises and `[V]` Verification Gates without forcing verbose visible step-by-step CoT narration, and instruct multi-step agents to externalize plans and intermediate state to a scratchpad file.

### 11. Skill Residency & Positive Recipe Shaping

**Yin, L., Li, Z., Shi, Z., Zhang, H., Seong, H. & Wang, Z.** (2026). "@skills: Attention Is All You Have." arXiv:2608.12610. https://arxiv.org/abs/2608.12610

Yin and colleagues show that installed agent skills compete for fewer than 100 reliable attention slots in the system prompt (costing 50 to 280 resident tokens every turn). Furthermore, controlled wording experiments show that negative prohibitions ("Do not X") backfire under competing incentives compared to positive structural recipes and observable-predicate conditionals ("When condition X holds, output Y").

**What this means for prompt optimization:** Express anti-hallucination and formatting rules as positive conditional recipes rather than negative prohibition lists, and keep skill metadata compact and trigger-focused.

---

## The Prompt Structure Framework

The certificate structure maps to the five standard components of a well-constructed prompt. This mapping comes from Anthropic's prompt engineering documentation and shows how semi-formal reasoning integrates with established prompt design.

| Component | Certificate Role | Key Constraint |
|---|---|---|
| **Identity** | Persona framing | Calibrate per PRISM: omit for accuracy tasks, minimal for mixed, full for alignment tasks |
| **Task** | Base instruction | Keep goal-blind: state what to produce, never how it will be evaluated |
| **Context** | Premises section | All relevant background, data, source material, itemized with identifiers |
| **Constraints** | Certificate structure | The certificate itself is the primary constraint, authority-framed |
| **Output Format** | Conclusion template | Formal conclusion plus structured output (JSON) when downstream parsing is needed |

This framework produces four prompt strategies depending on task complexity:

**Simple accuracy task:** Task instruction plus certificate template only. No persona. The certificate structure does the heavy lifting. Example: "Examine these two code patches for equivalence. Complete the following analytical certificate before providing your verdict."

**Complex analytical task:** All five components. Minimal persona. Full certificate with domain-specific premises and traces. Example: a financial due diligence review where the prompt includes identity ("You are an analyst."), detailed context (financial statements), the certificate structure with domain-specific trace requirements, and a JSON output format.

**Alignment/format task:** Identity plus task plus constraints plus format. Persona helps. Certificate is optional if the task is primarily about formatting or style rather than analytical accuracy. Example: "You are a professional technical writer. Format the following raw notes into a structured report following these style guidelines."

**Ongoing project:** Identity and context live as persistent files. Task and constraints are specified per prompt. The certificate structure is embedded in the system-level context so every interaction follows the same reasoning pattern. Incremental delta updates keep the context current without full rewrites (Zhang, Hu et al., 2026).

---

## The Optimization Process

When applying semi-formal reasoning to optimize an existing prompt, follow these seven steps. Each step is grounded in one or more of the research constraints above.

### Step 1: Classify the Task Type

Before touching the prompt, determine whether it is accuracy-dependent, alignment-dependent, or mixed. This classification drives every downstream decision about persona, certificate depth, and output format.

- **Accuracy-dependent:** fact retrieval, classification, math, coding logic, diagnostic reasoning, compliance verification, legal analysis. No persona. Full certificate.
- **Alignment-dependent:** format following, style matching, safety compliance, tone adjustment. Full persona. Certificate optional.
- **Creative:** copywriting, storytelling, poetry, brand voice, persuasive writing. Route to the Creative Pivot (Narrative Traces) instead of the standard certificate.
- **Mixed:** analytical reports, research summaries, decision recommendations that need both factual accuracy and good presentation. Minimal persona (five words or fewer). Full certificate with structured output.

This classification comes directly from the PRISM findings (Hu, Rostami & Thomason, 2026). Getting it wrong has measurable consequences: adding persona to an accuracy task drops performance by 3 to 5 percentage points. The Creative Pivot routing was added in V3 after cross-architecture benchmarking showed that logical evidence traces consistently flatten creative output.

### Step 1b: Select Certificate Mode (Lite vs. Max)

After classifying the task type, select the certificate intensity level:

- **Max Certificate** (default for high-stakes tasks): The full exhaustive structure with comprehensive premises, detailed multi-step evidence traces, and a formal conclusion with gap analysis. Use for high-stakes domains (medical, legal, financial), when baseline model competence is expected to be low, or when full auditability is required. Cost: ~2.2x token overhead. Delivers the full ~26% accuracy improvement.

- **Lite Certificate** (for routine analytical tasks): A compressed variant. Premises capped at 3 items, traces restricted to single-line causal arrows (`[T1] Input -> Processing Step -> Finding`), conclusion fields limited to 1-2 sentences. Cost: ~1.5x token overhead. Preserves approximately 80% of the traceability benefits (projected target, not yet benchmarked).

**Selection heuristic:** If a wrong answer would cause real harm (patient safety, legal liability, financial loss, security breach), use Max. If the task is analytical but routine, use Lite. When uncertain, default to Max.

### Step 2: Analyze the Original Prompt

Read the user's prompt and identify structural weaknesses:

- **Where could the model guess instead of reason?** Vague instructions invite pattern matching. The certificate forces step-by-step evidence gathering.
- **What evidence should the model gather before concluding?** This determines what goes into the premises and traces sections.
- **What are the failure modes?** Hallucination, skipped cases, surface matching, and anchoring on salient features are the most common.
- **Does the prompt leak its downstream objective?** Any mention of how the output will be used, evaluated, or scored must be removed (Cao, Jiang & Xu, 2026). This is the most common and most damaging error in the prompts people write.
- **Does the prompt rely on system/user separation for priority?** If the only thing enforcing a constraint is its position in the message hierarchy, it is unreliable (Geng et al., 2025).

### Step 3: Identify the Domain-Specific Certificate Structure

Map the three certificate components (premises, traces, conclusion) to the specific domain. The general pattern is always the same, but the content of each section varies by domain.

Domain-specific templates are available in `make-prompt-better/references/domain-templates.md` for: code review, document analysis, research synthesis, compliance checking, decision-making, comparative analysis, medical/clinical reasoning, legal analysis, financial due diligence, and a blank template for custom domains.

Each template in that file incorporates numbered identifiers (Zhang, Hu et al., 2026), authority framing (Geng et al., 2025), goal-blind conclusion formats (Cao, Jiang & Xu, 2026), and persona guidance per the PRISM findings (Hu, Rostami & Thomason, 2026).

### Step 4: Rewrite the Prompt

Transform the original prompt through nine specific operations:

1. **Remove goal leakage.** Strip any mention of downstream use, evaluation criteria, or success metrics. The certificate template specifies what evidence to gather, not what answer is desired (Cao, Jiang & Xu, 2026).

2. **Add authority-framed preamble.** Use expertise or consensus framing to present the certificate as a required analytical protocol, not a suggestion (Geng et al., 2025). "The standard code review protocol requires completing the following analytical certificate before providing any verdict" is stronger than "Please fill out this template."

3. **Define premise requirements** specific to the task and domain. What inputs, documents, data, or constraints must the model declare before reasoning?

4. **Specify what must be traced.** Define the concrete paths the model must walk, with numbered identifiers (Zhang, Hu et al., 2026). In code: function call chains. In documents: specific passages and their implications. In financial data: specific line items and their trends.

5. **Structure the conclusion format.** The conclusion template must require references to evidence by identifier. No new claims in the conclusion.

6. **Append a mandatory REMEDIATION / NEXT ACTION block** after the conclusion. Instruct the model: "The task is incomplete until the final, copy-pasteable artifact or specific fix is generated." This closes the Actionability Gap, where models analyze correctly but stop at the verdict without outputting the fix (identified through cross-architecture benchmarking).

7. **Add gap-detection instruction.** If the model cannot complete a trace, it must say so explicitly rather than guessing. This transforms invisible uncertainty into visible gaps.

8. **Add structured output format** if the output will be parsed downstream. A JSON schema alongside the certificate prevents silent integration failures (Mahmoudi et al., 2025).

9. **Calibrate persona.** Based on the task classification from Step 1: omit for accuracy tasks, use minimally for mixed tasks, use fully for alignment tasks (Hu, Rostami & Thomason, 2026).

### Step 5: Add Anti-Hallucination Guards

These instructions, appended to any certificate template, consistently reduce hallucination across domains. They come primarily from the semi-formal reasoning method (Ugare & Chandra, 2026) and the goal-blind principle (Cao, Jiang & Xu, 2026):

- "Do not infer behavior, meaning, or content from labels or names alone. Trace the actual substance."
- "If you cannot complete a trace, state 'UNABLE TO TRACE: [reason]' rather than filling in plausible-sounding content."
- "Each claim in the conclusion must reference a specific trace by identifier. Claims with no supporting trace must be removed."
- "Actively search for counterexamples and contradictions. State them even if the overall conclusion is positive."
- "Distinguish between 'verified' (traced through evidence), 'likely' (partial evidence), and 'assumed' (no direct evidence)."
- "Do not adjust the analysis based on how the output might be used or evaluated downstream."

These guards work because they target specific failure modes rather than offering generic "be accurate" instructions. Each guard addresses a concrete way that models hallucinate: inferring from names, guessing when uncertain, hiding contradictions, blurring confidence levels, and biasing toward desired outcomes.

Additionally, every optimized prompt must include the **traceability self-check** as a final validation layer: "Before finalizing, verify that every claim in your conclusion references at least one T-identifier from your evidence traces. If any claim lacks a supporting trace, either add the missing trace or remove the claim." Cross-architecture benchmarking showed that without this guard, a minority of certificate outputs contain orphaned conclusions.

### Step 6: Present the Optimized Prompt

The final deliverable includes:

1. **The optimized prompt** as a clean, copy-pasteable block containing: authority-framed preamble, certificate template with numbered identifiers, goal-blind task instructions, anti-hallucination guards, and structured output format if needed.

2. **What changed and why**, organized by which research principle drove each change. This helps the user understand the methodology, not just receive its output.

3. **Expected tradeoffs**: more tokens and higher latency in exchange for higher accuracy and auditable reasoning. Token overhead averages ~2.2x in Max mode, ~1.5x in Lite mode (cross-architecture benchmarking across Gemini, GLM, Qwen, Kimi).

4. **Task classification and persona decision**, with explicit reasoning so the user can adjust if they disagree with the classification.

---

## When This Helps and When It Does Not

Semi-formal reasoning is not a universal improvement. The research is clear about both the gains and the costs.

**It helps most when:**
- Accuracy matters more than speed
- Mistakes are costly (compliance, medical, legal, financial, security domains)
- The input is complex enough that surface-level pattern matching fails
- You need auditable reasoning that a human can inspect
- Standard prompting produces hallucinations or unsupported claims
- Multiple competing interpretations exist and the model must discriminate correctly

**It helps less when:**
- The task is simple pattern matching or formatting that the model already handles well
- The model already achieves very high baseline accuracy on the task (ceiling effects)
- Speed matters more than precision
- The domain has little ambiguity

**It should be avoided when:**
- The task is simple factual lookup where the model already knows the answer
- Fully unconstrained brainstorming or stream-of-consciousness generation (creative tasks with structural goals should use the Creative Pivot with Narrative Traces instead)
- A reasoning-distilled model is already in use, because these models benefit from context length alone rather than certificate structure specifically (Hu, Rostami & Thomason, 2026)

For a detailed decision framework with specific criteria, see `docs/when-to-use.md`.

The honest summary: semi-formal reasoning produces larger accuracy gains on harder tasks where the baseline is lower. Cross-architecture benchmarking confirmed a 25.9% average relative improvement with a 96.3% win rate across four model families. On tasks where modern models are already highly accurate, the gains are smaller but the auditability benefit remains. The ~2.2x token overhead (Max mode) or ~1.5x (Lite mode) is always a cost. Whether it is worth paying depends on how much the answer matters.

---

## References

1. Ugare, S. & Chandra, S. (2026). "Agentic Code Reasoning." Meta. arXiv:2603.01896. https://arxiv.org/abs/2603.01896

2. Cao, S., Jiang, W. & Xu, H. (2026). "Seeing the Goal, Missing the Truth: Human Accountability for AI Bias." arXiv:2602.09504. https://arxiv.org/abs/2602.09504

3. Zhang, Q., Hu, C. et al. (2026). "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models." ICLR 2026. arXiv:2510.04618. https://arxiv.org/abs/2510.04618

4. Geng, Y., Li, H. et al. (2025). "Control Illusion: The Failure of Instruction Hierarchies in Large Language Models." AAAI 2026. arXiv:2502.15851. https://arxiv.org/abs/2502.15851

5. Mahmoudi, B., Chenail-Larcher, Z. et al. (2025). "Specification and Detection of LLM Code Smells." arXiv:2512.18020. https://arxiv.org/abs/2512.18020

6. Hu, Z., Rostami, M. & Thomason, J. (2026). "Expert Personas Improve LLM Alignment but Damage Accuracy: Bootstrapping Intent-Based Persona Routing with PRISM." arXiv:2603.18507. https://arxiv.org/abs/2603.18507

7. Zhang, J., Yu, S., Chong, D., Sicilia, A., Tomz, M. R., Manning, C. D. & Shi, W. (2025). "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity." arXiv:2510.01171. https://arxiv.org/abs/2510.01171

8. Madler, J. (2026). "SlopShape: Identifying AI-Generated Commercial Web Content." arXiv:2609.15369. https://arxiv.org/abs/2609.15369

9. Gloaguen, T., Mundler, N., Muller, M., Raychev, V. & Vechev, M. (2026). "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?" arXiv:2602.11988. https://arxiv.org/abs/2602.11988

10. Lee, Y., Nair, R., Zhang, Q., Lee, K., Khattab, O. & Finn, C. (2026). "Meta-Harness: End-to-End Optimization of Model Harnesses." arXiv:2603.28052. https://arxiv.org/abs/2603.28052 (with Self-Harness, Zhang et al., 2026, arXiv:2606.09498; Context Language Models, Shao et al., 2026, arXiv:2609.37725; and DS-STAR, Nam et al., 2025, arXiv:2509.21825).

11. Yin, L., Li, Z., Shi, Z., Zhang, H., Seong, H. & Wang, Z. (2026). "@skills: Attention Is All You Have." arXiv:2608.12610. https://arxiv.org/abs/2608.12610
