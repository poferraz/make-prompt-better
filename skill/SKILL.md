---
name: semi-formal-prompt-optimizer
description: >
  Optimize any prompt using semi-formal reasoning templates grounded in Meta's
  "Agentic Code Reasoning" research (Ugare & Chandra, arXiv 2603.01896, 2026)
  and five additional peer-reviewed papers on goal-blind prompting, context
  engineering, instruction hierarchy, LLM code smells, and persona effects.
  The core technique forces the LLM to state explicit premises, trace concrete
  execution/reasoning paths, and derive formal conclusions before answering,
  eliminating guesswork and hallucination. Use this skill whenever a user wants
  to: improve a prompt's accuracy or reliability, reduce hallucination in LLM
  outputs, add structured reasoning to any prompt, create reasoning certificates
  or evidence-backed templates, apply semi-formal reasoning to any domain (not
  just code), convert a vague or underperforming prompt into a rigorous one, or
  build task-specific reasoning scaffolds. Also trigger when users mention
  "structured prompting", "reasoning templates", "semi-formal", "certificate
  template", "evidence-based prompting", "prompt hardening", "reduce
  hallucination in prompts", "goal-blind prompting", or "context engineering".
  This skill applies broadly: code review, analysis, decision-making, research
  synthesis, compliance checks, medical reasoning, legal analysis, financial due
  diligence, or any domain where structured evidence gathering improves output
  quality.
---

# Semi-Formal Prompt Optimizer

## Research Foundation

This skill synthesizes findings from six research sources into a unified prompt
optimization methodology. Each source contributes a specific principle that
shapes how prompts are rewritten.

### Primary Source

**"Agentic Code Reasoning"** (Ugare & Chandra, Meta, 2026), arXiv 2603.01896

Core technique: semi-formal reasoning templates that force the LLM to state
premises, trace execution paths, and derive formal conclusions before answering.
Results: patch equivalence accuracy 78% to 88% on curated examples, 93% on
real-world patches. Code QA accuracy 78% to 87%. Fault localization Top-5
improved 5 to 12 percentage points. Pure prompt engineering, no model training
required. Uses roughly 2.8x more execution steps than standard reasoning.

### Supporting Sources

**"Seeing the Goal, Missing the Truth"** (Cao, Jiang & Xu, 2026), arXiv 2602.09504

Core finding: disclosing downstream objectives causes LLMs to reshape
intermediate outputs toward inferred goals. Goal-aware prompts inflated
in-sample performance but degraded out-of-sample generalization. Fix: keep
prompts goal-blind. Specify what to measure or build, never reveal how the
output will be evaluated or used downstream.

**Skill constraint:** When rewriting prompts, NEVER include the evaluation
criteria, downstream use case, or success metrics in the prompt itself. The
certificate template specifies what evidence to gather, not what answer is
desired.

**"ACE: Agentic Context Engineering"** (Zhang, Hu et al., 2026), arXiv 2510.04618.
Accepted at ICLR 2026.

Core finding: contexts work best as comprehensive evolving playbooks, not
compressed summaries. Two failure modes to avoid: (1) brevity bias, where
optimization collapses toward short generic instructions that omit domain
specifics, and (2) context collapse, where iterative rewriting erodes detail
over time. Structured, itemized bullets with unique identifiers preserve
knowledge better than monolithic paragraphs. Results: +10.6% on agents,
+8.6% on finance benchmarks vs. baselines. 86.9% lower adaptation latency
through incremental delta updates vs. full context rewrites.

**Skill constraint:** Certificate templates should use itemized, structured
entries (numbered traces, labeled premises) rather than prose paragraphs.
Each evidence item should be independently identifiable. Prefer comprehensive
detail over brevity. When iterating on a prompt across sessions, make
incremental delta edits rather than full rewrites.

**"Control Illusion: Failure of Instruction Hierarchies"** (Geng et al., 2025),
arXiv 2502.15851

Core finding: system/user prompt separation fails to enforce instruction
priority. Models average 9.6% to 45.8% primary obedience rate on conflicting
constraints. However, societal hierarchy framings (authority, expertise,
consensus) show stronger influence: consensus framing reached 65.8 to 77.8%
priority adherence vs. 14.4 to 47.5% for system/user separation. Models have
strong inherent biases toward certain constraint types (favoring lowercase, longer
text, keyword avoidance) regardless of priority designation.

**Skill constraint:** Do not rely on system/user message separation alone to
enforce the certificate structure. Instead, embed priority through framing:
use expertise-based authority ("As established in peer-reviewed methodology...")
or consensus-based framing ("The standard analytical protocol requires...").
Place the most critical constraints (the certificate structure itself) using
authority framing, not just positional placement. Be aware of model constraint
biases: models naturally prefer longer outputs, so length constraints in
certificates need explicit reinforcement.

**"Specification and Detection of LLM Code Smells"** (Mahmoudi et al., 2025),
arXiv 2512.18020

Core finding: 60.5% of 200 open-source LLM systems contain integration code
smells. The "No Structured Output" smell (40.5% prevalence) directly applies:
when LLM outputs are parsed downstream, requiring structured output format at
the API boundary prevents schema drift, field mismatches, and silent failures.

**Skill constraint:** When the optimized prompt will feed into a pipeline or be
parsed programmatically, enforce structured output format (JSON schema,
typed fields) alongside the certificate structure. The certificate is the
reasoning scaffold; the output format is the delivery contract. Both matter.

**"PRISM: Expert Personas Improve Alignment but Damage Accuracy"** (Hu,
Rostami & Thomason, 2026), arXiv 2603.18507

Core finding: expert persona prompts consistently improve alignment-dependent
tasks (writing, roleplay, safety, format-following) but reliably damage
pretraining-dependent knowledge retrieval (MMLU accuracy drops from 71.6% to
66.3 to 68.0%). Longer personas damage more on accuracy tasks but help more on
alignment tasks. Reasoning-distilled models benefit from ANY added context
regardless of persona identity (the gain is from context length, not expertise).

**Skill constraint:** Do NOT add expert persona/identity framing to certificate
prompts when the task depends on factual accuracy, knowledge retrieval, or
discriminative judgment (e.g., classification, fact extraction, math). DO add
domain-expert framing when the task depends on alignment qualities: format
adherence, style, safety, tone, structured output compliance. For mixed tasks
(requiring both accuracy AND good formatting), use minimal persona framing (5 words
or fewer, e.g., "You are a data analyst.") to limit accuracy damage while
preserving some alignment benefit.

### The Prompt Structure Framework

Five standard prompt components map to the certificate structure:

| Framework Component | Certificate Mapping |
|---|---|
| IDENTITY | Use sparingly per PRISM findings. Omit for accuracy tasks, use minimal for mixed tasks, use full for alignment tasks. |
| TASK | The base instruction. Keep goal-blind per Cao/Jiang/Xu: state what to produce, never how it will be evaluated. |
| CONTEXT | The PREMISES section of the certificate. All relevant background, data, source material. |
| CONSTRAINTS | The certificate structure itself IS the primary constraint. Add domain-specific constraints. Use authority framing per Geng et al. |
| OUTPUT FORMAT | The FORMAL CONCLUSION section template plus any structured output requirements (JSON, schema) per Mahmoudi et al. |

**Prompt Strategy by Complexity:**

- Simple accuracy task: Task + Certificate template only, no persona
- Complex analytical task: All five components, minimal persona, full certificate
- Alignment/format task: Identity + Task + Constraints + Format, persona helps
- Ongoing project: Identity and Context as persistent files, Task and Constraints per prompt, certificate structure embedded in system context

## How Semi-Formal Reasoning Works

The technique has three mandatory components:

1. **Premises**: Explicit statements of what is known, what was examined, and
   what assumptions are being made. The model cannot proceed without declaring
   its starting conditions. Per ACE research: use itemized, independently
   identifiable entries, not prose summaries. Each premise must be a discrete
   verifiable claim.

2. **Evidence Traces**: Concrete, step-by-step paths through the material.
   In code, this means tracing function calls. In other domains, this means
   walking through specific data points, document sections, logical steps, or
   causal chains. The model must follow the actual path rather than inferring
   from names or surface features. Per ACE: number each trace with a unique
   identifier so conclusions can reference them precisely.

3. **Formal Conclusion**: A structured verdict derived solely from the
   evidence gathered above. The conclusion must reference specific premises
   and traces by their identifiers. No new claims allowed here. Per Cao/Jiang/Xu:
   the conclusion format must not hint at what answer is desired or how the
   output will be used downstream.

This triad functions as a "reasoning certificate": if the model cannot fill
it completely, the gap reveals where reasoning broke down.

## When to Apply This Technique

Semi-formal reasoning adds the most value when:
- The task requires accuracy over speed
- Mistakes are costly (compliance, medical, legal, financial, security)
- The input is complex enough that surface-level pattern matching fails
- The model must show auditable reasoning
- Standard prompting produces hallucinations or unsupported claims
- Multiple competing interpretations exist and the model must choose correctly

It adds less value when:
- The task is simple pattern matching or formatting
- The model already achieves very high accuracy on the task
- Speed matters more than precision
- The domain has no ambiguity

**When to AVOID certificate structure entirely:**
- Simple factual lookups where the model already knows the answer
- Creative generation where structured reasoning constrains the output
- Tasks where a reasoning-distilled model is already being used (per PRISM:
  these models get gains from context length alone, not certificate structure)

## The Optimization Process

When a user brings a prompt to optimize, follow these steps:

### Step 1: Classify the Task Type

Before touching the prompt, determine:
- **Accuracy-dependent?** (fact retrieval, classification, math, coding logic)
  No persona, full certificate, goal-blind framing.
- **Alignment-dependent?** (format-following, style, safety, tone)
  Persona helps, certificate optional, constraints primary.
- **Mixed?** (analysis requiring both accuracy and good presentation)
  Minimal persona, full certificate, structured output format.

This classification drives all downstream decisions per PRISM research.

### Step 2: Analyze the Original Prompt

Read the user's prompt and identify:
- What task is the prompt trying to accomplish?
- Where could the model guess instead of reason?
- What evidence should the model gather before concluding?
- What are the failure modes (hallucination, skipped cases, surface matching)?
- **Does the prompt leak its downstream objective?** (per Cao/Jiang/Xu: remove
  any mention of how the output will be used, evaluated, or scored)
- **Does the prompt rely on system/user separation for priority?** (per Geng
  et al.: this is unreliable; reframe with authority/expertise/consensus cues)

### Step 3: Identify the Domain-Specific Certificate Structure

Map the three components (premises, traces, conclusion) to the specific domain.
See `references/domain-templates.md` for templates across common domains.

The general pattern:

```
## Certificate Template for [TASK]

### PREMISES
State all relevant facts, constraints, and context before reasoning.
- [P1] What inputs/documents/data were examined?
- [P2] What are the known constraints or rules?
- [P3] What assumptions are being made (and why)?

### EVIDENCE TRACES
For each claim or decision point, walk through the concrete path:
- [T1] Trace [specific item 1]: [step-by-step reasoning with citations]
- [T2] Trace [specific item 2]: [step-by-step reasoning with citations]
- ...continue for all relevant items

### FORMAL CONCLUSION
Based solely on the premises and traces above:
- Verdict: [state the conclusion]
- Supporting evidence: [reference T1, T2, etc. by identifier]
- Gaps: [flag any uncertainties discovered during tracing]
```

Note the identifiers [P1], [T1], etc. Per ACE research, these allow precise
cross-referencing between conclusion claims and supporting evidence, preventing
orphaned claims that reference nothing.

### Step 4: Rewrite the Prompt

Transform the user's original prompt by:

1. **Remove goal leakage**: Strip any mention of downstream use, evaluation
   criteria, or success metrics (Cao/Jiang/Xu)
2. **Add authority-framed preamble**: Use expertise or consensus framing to
   establish the certificate as the required analytical protocol, not a
   suggestion (Geng et al.)
3. **Define premise requirements** specific to the task
4. **Specify what must be traced**: the concrete paths the model must walk,
   with numbered identifiers (ACE)
5. **Structure the conclusion format** so it references evidence by identifier
6. **Add gap-detection instruction**: if the model cannot complete a trace,
   it must say so rather than guess
7. **Add structured output format** if the output will be parsed downstream
   (Mahmoudi et al.)
8. **Calibrate persona**: omit for accuracy tasks, minimal for mixed, full
   for alignment tasks (PRISM)

### Step 5: Add Anti-Hallucination Guards

From the research, these patterns consistently reduce hallucination:

- "Do not infer behavior from names alone: trace the actual path" (Meta)
- "If you cannot verify a claim through the evidence, mark it as UNVERIFIED"
- "State counterexamples when they exist, even if the overall conclusion is positive"
- "Each claim in your conclusion must reference a specific trace by identifier"
- "Do not adjust your analysis based on how the output might be used" (Cao/Jiang/Xu)

### Step 6: Present the Optimized Prompt

Show the user:
- The original prompt
- The optimized prompt with certificate structure
- A brief explanation of what changed and why, organized by which research
  principle drove each change
- Expected tradeoffs (more tokens and latency for higher accuracy)
- Task type classification and why persona was included or excluded

## Tradeoffs to Communicate

Be honest with the user about costs:

- Semi-formal reasoning uses roughly 2.8x more execution steps than standard prompting
- Latency increases proportionally
- For tasks where the model is already highly accurate, gains may be minimal
  (Sonnet-4.5 showed no gain on code QA where baseline was already approximately 85%)
- The technique can produce "confident but wrong" answers: structured does not mean correct
  (the structure makes errors easier to spot, but does not eliminate them)
- Adding expert persona framing will improve format compliance but may reduce
  factual accuracy by 3 to 5 percentage points (PRISM)
- Certificate structure adds approximately 150 to 300 tokens of overhead to each prompt

## Output Format

Always deliver the optimized prompt as a clean, copy-pasteable block. Include:
1. Authority-framed preamble (not persona unless alignment task)
2. The certificate template embedded in the prompt with numbered identifiers
3. The task-specific instructions (goal-blind: what to do, not why)
4. Anti-hallucination guards
5. Structured output format specification (if downstream parsing needed)

If the user wants it as a file, create a markdown file with the prompt and
accompanying documentation.

## Reference Materials

For domain-specific certificate templates, read:
`references/domain-templates.md`

This file contains pre-built certificate structures for: code review, document
analysis, research synthesis, compliance checking, decision-making, comparative
analysis, medical/clinical reasoning, legal analysis, financial due diligence,
and a blank template for custom domains. Each template incorporates numbered
identifiers (ACE), goal-blind framing (Cao/Jiang/Xu), and authority-framed
instructions (Geng et al.).

For the research principles index, read:
`references/research-principles.md`

This file contains a quick-reference summary of each paper's key finding and
its constraint on the optimization process, useful when explaining to users
why a specific change was made.
