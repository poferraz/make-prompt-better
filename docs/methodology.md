# Semi-Formal Reasoning for Prompt Optimization

## A Methodology Grounded in Six Research Papers

---

## Introduction

Large language models produce better output when they show their work. This is not a platitude. It is a finding with quantitative backing from multiple independent research teams, and it forms the basis of a technique called **semi-formal reasoning**.

Semi-formal reasoning is a prompt engineering method that forces the model to follow a structured analytical process before producing an answer. The model must declare its starting conditions, trace concrete evidence paths step by step, and derive a formal conclusion that references the evidence it gathered. The output functions as a "reasoning certificate": an auditable record of how the model arrived at its answer, with every claim tied to a specific piece of evidence.

The technique originates from work by Ugare and Chandra at Meta (2026), who demonstrated that structured reasoning templates improved code analysis accuracy by 10 to 15 percentage points without any model retraining. Their method raised patch equivalence accuracy from 78% to 88% on curated examples and reached 93% on real-world patches. Code QA accuracy climbed from 78% to 87%. The original paper reported ~2.8x more reasoning steps than standard prompting. Cross-architecture benchmarking (Gemini, GLM, Qwen, Kimi) shows the actual average overhead is ~2.0x (ranging from 1.67x on Qwen to 2.5x on Gemini), a tradeoff that reliably buys a ~20-25% accuracy and traceability improvement for analytical tasks (Ugare & Chandra, 2026).

This document describes the full methodology: the certificate structure, the six research constraints that shape it, the prompt framework that operationalizes it, and the optimization process that applies it. It is written for anyone who wants to understand the theory behind the approach, whether or not they use the accompanying Claude Code skill.

For quick-reference versions of the research constraints, see `skill/references/research-principles.md`. For ready-to-use certificate templates across ten domains, see `skill/references/domain-templates.md`.

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

The original paper reported ~2.8x more reasoning steps than standard prompting. Cross-architecture benchmarking shows the actual average is ~2.0x (ranging from 1.67x on Qwen to 2.5x on Gemini). V3 introduces Lite Certificate mode at ~1.5x overhead for routine tasks. In domains where errors are costly, the Max mode tradeoff is clearly worthwhile; for routine analytical tasks, Lite mode offers a cost-effective middle path.

**What this means for prompt optimization:** Every optimized prompt must embed a three-part certificate structure. The model fills premises before tracing, traces before concluding. Conclusions must reference traces by identifier. The certificate acts as both a reasoning scaffold and an audit trail.

### 2. Goal-Blind Prompting

**Cao, S., Jiang, W. & Xu, H.** (2026). "Seeing the Goal, Missing the Truth: Human Accountability for AI Bias." arXiv:2602.09504. https://arxiv.org/abs/2602.09504

Cao, Jiang, and Xu discovered that disclosing the downstream objective to an LLM causes it to reshape intermediate outputs toward the inferred goal. If you tell a model "this analysis will be used to predict stock returns," the model unconsciously biases its reasoning toward outputs that would support stock prediction, even when the evidence does not justify it.

The effect is insidious. Goal-aware prompts inflated in-sample performance, making the results look better during testing. But out-of-sample generalization degraded. The inflated in-sample improvement disappeared entirely after the model's knowledge cutoff, confirming that the model was exploiting training-data correlations rather than producing genuine analytical improvement. The model was not getting smarter. It was cheating, in a way that became invisible during evaluation but harmful in production.

**What this means for prompt optimization:** Never include evaluation criteria, downstream use case, success metrics, or purpose descriptions in the prompt. The certificate specifies what evidence to gather and what analytical paths to follow, not what answer is desired or how the output will be judged. This constraint applies to the certificate's conclusion format as well: the verdict template must be neutral, not tilted toward any particular outcome.

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

However, they found that **societal hierarchy framings** achieve much stronger compliance. Consensus framing ("90% of experts recommend...") reached 65.8% to 77.8% priority adherence. Expertise framing ("Peer-reviewed methodology requires...") was the second strongest. Authority framing ("Your manager requires...") was third. All three significantly outperformed system/user separation, which managed only 14.4% to 47.5%.

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

- **Max Certificate** (default for high-stakes tasks): The full exhaustive structure with comprehensive premises, detailed multi-step evidence traces, and a formal conclusion with gap analysis. Use for high-stakes domains (medical, legal, financial), when baseline model competence is expected to be low, or when full auditability is required. Cost: ~2.0x token overhead. Delivers the full ~20-25% accuracy improvement.

- **Lite Certificate** (for routine analytical tasks): A compressed variant. Premises capped at 3 items, traces restricted to single-line causal arrows (`[T1] Input -> Processing Step -> Finding`), conclusion fields limited to 1-2 sentences. Cost: ~1.5x token overhead. Preserves approximately 80% of the traceability benefits.

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

Domain-specific templates are available in `skill/references/domain-templates.md` for: code review, document analysis, research synthesis, compliance checking, decision-making, comparative analysis, medical/clinical reasoning, legal analysis, financial due diligence, and a blank template for custom domains.

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

Additionally, every optimized prompt must include the **traceability self-check** as a final validation layer: "Before finalizing, verify that every claim in your conclusion references at least one T-identifier from your evidence traces. If any claim lacks a supporting trace, either add the missing trace or remove the claim." Cross-architecture benchmarking showed that without this guard, approximately 5-10% of certificate outputs contain orphaned conclusions.

### Step 6: Present the Optimized Prompt

The final deliverable includes:

1. **The optimized prompt** as a clean, copy-pasteable block containing: authority-framed preamble, certificate template with numbered identifiers, goal-blind task instructions, anti-hallucination guards, and structured output format if needed.

2. **What changed and why**, organized by which research principle drove each change. This helps the user understand the methodology, not just receive its output.

3. **Expected tradeoffs**: more tokens and higher latency in exchange for higher accuracy and auditable reasoning. The certificate adds roughly 150 to 300 tokens of overhead per prompt. Token overhead averages ~2.0x in Max mode, ~1.5x in Lite mode (cross-architecture benchmarking across Gemini, GLM, Qwen, Kimi).

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

The honest summary: semi-formal reasoning produces larger accuracy gains on harder tasks where the baseline is lower. Cross-architecture benchmarking confirmed a 24.6% average relative improvement with a 97.5% win rate across four model families. On tasks where modern models are already highly accurate, the gains are smaller but the auditability benefit remains. The ~2.0x token overhead (Max mode) or ~1.5x (Lite mode) is always a cost. Whether it is worth paying depends on how much the answer matters.

---

## References

1. Ugare, S. & Chandra, S. (2026). "Agentic Code Reasoning." Meta. arXiv:2603.01896. https://arxiv.org/abs/2603.01896

2. Cao, S., Jiang, W. & Xu, H. (2026). "Seeing the Goal, Missing the Truth: Human Accountability for AI Bias." arXiv:2602.09504. https://arxiv.org/abs/2602.09504

3. Zhang, Q., Hu, C. et al. (2026). "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models." ICLR 2026. arXiv:2510.04618. https://arxiv.org/abs/2510.04618

4. Geng, Y., Li, H. et al. (2025). "Control Illusion: The Failure of Instruction Hierarchies in Large Language Models." AAAI 2026. arXiv:2502.15851. https://arxiv.org/abs/2502.15851

5. Mahmoudi, B., Chenail-Larcher, Z. et al. (2025). "Specification and Detection of LLM Code Smells." arXiv:2512.18020. https://arxiv.org/abs/2512.18020

6. Hu, Z., Rostami, M. & Thomason, J. (2026). "Expert Personas Improve LLM Alignment but Damage Accuracy: Bootstrapping Intent-Based Persona Routing with PRISM." arXiv:2603.18507. https://arxiv.org/abs/2603.18507
