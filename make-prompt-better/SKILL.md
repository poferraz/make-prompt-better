---
name: make-prompt-better
description: "Use when optimizing, hardening, or rewriting any prompt, system instruction, AGENTS.md or CLAUDE.md context file, or agent workflow to improve accuracy, auditability, structured output compliance, or creative diversity across any LLM or coding agent."
---

# Semi-Formal Prompt Optimizer (v4.0)

## Overview

This skill rewrites vague, brittle, or goal-biased prompts into verifiable **reasoning certificates** grounded in eleven peer-reviewed research papers. It is completely tool-agnostic and model-agnostic: the optimized prompts work across Claude Code, Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, GitHub Copilot, Cursor, Windsurf, API pipelines, and chat interfaces.

## Research Foundation (11 Papers)

Each principle in this workflow traces to an empirical finding. For full summaries and citations, read `references/research-principles.md`.

1. **[META] Semi-Formal Reasoning** (Ugare & Chandra, 2026, arXiv:2603.01896): Requiring explicit Premises, Evidence Traces, and a Formal Conclusion improves analytical accuracy by 10 to 15 percentage points and cross-architecture quality by +25.9% at ~2.2x average token cost.
2. **[GOAL-BLIND] Purpose-Conditioned Cognition** (Cao, Jiang & Xu, 2026, arXiv:2602.09504): Disclosing downstream goals, business stakes, or evaluation metrics biases intermediate reasoning and degrades out-of-sample generalization. Prompts must specify what to analyze or build, never why or how it will be judged.
3. **[ACE] Agentic Context Engineering** (Zhang, Hu et al., 2026, arXiv:2510.04618): Itemized bullets with unique identifiers (`[P1]`, `[T1]`) prevent brevity bias and context collapse (+10.6% on agent benchmarks, 86.9% lower adaptation latency via incremental delta edits).
4. **[HIERARCHY] Instruction Hierarchy Failure** (Geng et al., 2025, arXiv:2502.15851): System/user message separation achieves only 9.6% to 45.8% compliance on conflicting constraints, whereas expertise and consensus framing ("The standard analytical protocol requires...") achieves 54% to 77.8% compliance.
5. **[CODE-SMELLS] LLM Integration Smells** (Mahmoudi et al., 2025, arXiv:2512.18020): 40.5% of LLM systems lack structured output schemas, causing silent downstream failures. Pair the reasoning certificate with an explicit JSON or typed schema whenever output is parsed programmatically.
6. **[PRISM] Persona Calibration** (Hu, Rostami & Thomason, 2026, arXiv:2603.18507): Expert personas improve alignment tasks (+0.4 to +0.65 MT-Bench) but damage accuracy tasks (-3.6 to -5.3 pp on MMLU). Omit personas on accuracy tasks, cap at 5 words on mixed tasks, and use full personas only on alignment tasks.
7. **[VS] Verbalized Sampling** (Zhang et al., 2025, arXiv:2510.01171): Post-training typicality bias causes mode collapse. Prompting the model to verbalize a candidate distribution with estimated typicality probabilities before committing increases creative and open-ended diversity by 1.6x to 2.1x.
8. **[SLOPSHAPE] Structural Signatures of AI Writing** (Madler, 2026, arXiv:2609.15369; Russell et al., 2026): Discourse-level structural features detect AI writing at 98.0 macro-F1 even after full rewording (10 core features reach 93.5 macro-F1). AI text clusters in a "tidy, self-announcing shape" (payoff in title, thesis before first section, formulaic legacy-vs-modern contrast, editorial-explainer voice, and restated-thesis summary endings). Creative and editorial prompts must enforce structural rarity rules.
9. **[CONTEXT-FILES] Repository Context File Evaluation** (Gloaguen et al., 2026, arXiv:2602.11988): LLM-generated `AGENTS.md` and `CLAUDE.md` files reduce coding agent task success by 3% while raising inference cost by over 20%, and directory overviews fail to speed up file localization. Persistent context files must contain only non-inferable tooling commands and hard boundary invariants.
10. **[HARNESS] Harness Routing, Context-as-a-File & Plan Verification** (Lee et al., 2026, arXiv:2603.28052; Zhang et al., 2026, arXiv:2606.09498; Shao et al., 2026, arXiv:2609.37725; Nam et al., 2025, arXiv:2509.21825): Model-specific harnesses (+14.2 to +21.4 pp on Terminal-Bench-2.0), file-backed context state (+11.4% accuracy with 21.5% fewer FLOPs), and plan-sufficiency gates outperform static bloated prompts. For Large Reasoning Models (LRMs), verification gates replace verbose step-by-step output narration to prevent overthinking loops.
11. **[SKILLS-SDO] Skill Residency & Positive Recipe Shaping** (Yin et al., 2026, arXiv:2608.12610): Under competing incentives, negative prohibitions ("Do not X") backfire and increase violations compared to positive structural recipes and conditionals keyed to observable predicates ("When condition X holds, output Y").

### The Prompt Structure Framework

| Component | Certificate Mapping & Research Rule |
|---|---|
| **IDENTITY** | Omit for accuracy tasks and LRMs; cap at 5 words for mixed tasks; use full persona only for alignment/style tasks (`[PRISM]`). |
| **TASK** | State what artifact or analysis to produce in goal-blind terms; strip downstream evaluation metrics, business stakes, and audience agendas (`[GOAL-BLIND]`). |
| **CONTEXT** | Declare as itemized `[P1]`, `[P2]` Premises (`[ACE]`). For repo `AGENTS.md`/`CLAUDE.md` files, prune directory trees and inferable rules (`[CONTEXT-FILES]`). |
| **CONSTRAINTS** | Enforce the selected Certificate Mode using expertise/consensus authority framing (`[HIERARCHY]`) and positive observable-predicate conditionals (`[SKILLS-SDO]`). |
| **OUTPUT FORMAT** | Require a Formal Conclusion citing `[T]` identifiers, a mandatory `REMEDIATION / NEXT ACTION` block, and a typed JSON schema if parsed downstream (`[CODE-SMELLS]`). |

---

## The Optimization Workflow

Follow these steps in order whenever a user asks to optimize, harden, or review a prompt or context file.

### Step 1: Classify the Task Type (`[PRISM]`)

Determine the primary cognitive demand of the prompt:
- **Accuracy-dependent** (code verification, bug hunting, math, fact extraction, legal/medical/financial analysis, compliance): **Omit persona**.
- **Mixed** (technical reports, architecture reviews, data analysis with executive presentation): **Minimal persona** (5 words or fewer, such as `"You are a systems analyst."`).
- **Alignment-dependent** (formatting, tone translation, style guides): **Full persona**.
- **Creative / Divergent** (copywriting, essays, storytelling, product messaging, ideation): **Minimal or Full persona**, routed to **Mode 4 (Creative & Divergent v2)**.
- **Persistent Context / Agent Harness** (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, system prompts, multi-turn agent loops): **Omit persona**, routed to **Mode 3 (LRM / Harness Mode)**.

### Step 1b: Select Certificate Mode (4 Modes)

Choose the certificate mode that matches the task stakes, model family, and execution environment:

| Mode | When to Use | Overhead | Structure Summary |
|---|---|---|---|
| **1. Max Certificate** | High-stakes analytical tasks (security, medical, legal, financial), low baseline competence, full auditability | ~2.2x | Exhaustive `[P]` Premises + multi-step `[T]` Evidence Traces + Formal Conclusion + Remediation + Self-Check |
| **2. Lite Certificate** | Routine analytical tasks (standard code reviews, basic comparisons, everyday debugging) | ~1.5x | Max 3 `[P]` Premises + single-line causal arrows (`[T1] Input -> Step -> Finding`) + 1-2 sentence conclusion + Remediation |
| **3. LRM / Harness Mode** | Reasoning models (o3, DeepSeek-R1, Claude Extended Thinking, Gemini Thinking) OR `AGENTS.md` / `CLAUDE.md` / agent system prompts | ~1.1x to 1.3x | For LRMs: `[P]` Premises + `[V]` Verification Gates + Conclusion citing `[P]`/`[V]` + Remediation (no forced step-by-step output narration). For `AGENTS.md`: Minimal Viable Context pruning (`[CONTEXT-FILES]`, `[HARNESS]`) |
| **4. Creative & Divergent v2** | Copywriting, essays, blog posts, storytelling, brand messaging, open-ended ideation | ~1.6x | Backstage `[NT0]` Verbalized Sampling distribution + `[NT1]`-`[NT3]` Narrative Traces + `[SLOPSHAPE]` structural rarity contract + clean final prose |

### Step 2: Diagnose the Original Prompt

Audit the user's input against six failure patterns:
1. **Goal leakage (`[GOAL-BLIND]`)**: Does it reveal why the user wants the output, business stakes, or how it will be graded?
2. **Guesswork gaps (`[META]`, `[ACE]`)**: Where can the model infer from surface names instead of tracing concrete artifacts?
3. **Weak priority framing (`[HIERARCHY]`)**: Does it rely on polite requests ("please make sure") or system/user split instead of protocol authority?
4. **Negative prohibition traps (`[SKILLS-SDO]`)**: Does it use vague "Do not X" lists instead of positive structural recipes and observable predicates?
5. **Context bloat or LRM overthinking (`[CONTEXT-FILES]`, `[HARNESS]`)**: Does an `AGENTS.md` include codebase directory overviews, or does an LRM prompt force redundant visible step-by-step CoT?
6. **Mode collapse & SlopShape risk (`[VS]`, `[SLOPSHAPE]`)**: For writing tasks, will the prompt produce the highest-typicality cliché in a tidy, self-announcing AI structure?

### Step 3: Select and Adapt the Certificate Structure

Read `references/domain-templates.md` to pick one of the 12 domain templates (or adapt the core structures below).

#### Mode 1 & Mode 2 Pattern (Max and Lite Analytical Certificates)

```markdown
The standard analytical protocol for [DOMAIN] requires completing this reasoning certificate before issuing any verdict.

### PREMISES
Declare all observable inputs, constraints, and starting assumptions (cap at 3 items in Lite mode):
- [P1] Primary artifact(s) examined: [exact files, sections, or data]
- [P2] Applicable rules or invariants: [concrete specifications or constraints]
- [P3] Unverified inputs or environmental assumptions: [explicitly listed]

### EVIDENCE TRACES
Walk through the concrete path for each item (in Lite mode, use single-line arrows: `[T1] Input -> Operation -> Observable Result`):
- [T1] Trace [item 1]: [step-by-step verification with exact citations to P1-P3]
- [T2] Trace [item 2]: [step-by-step verification with exact citations to P1-P3]

### FORMAL CONCLUSION
Derive your verdict solely from the premises and traces above:
- Verdict: [objective disposition]
- Supporting traces: [cite T1, T2, etc. for every claim]
- Verification gaps: [list any path marked UNABLE TO TRACE and the missing input required]

### REMEDIATION / NEXT ACTION
The task is incomplete until this section contains one of the following:
- A complete, copy-pasteable fix (patch, revised text, corrected query, or executable command)
- A concrete sequence of verification commands to resolve any Verification Gaps
- The explicit statement: "No remediation required: [reason grounded in T-identifiers]"
```

#### Mode 3 Pattern A: Large Reasoning Model (LRM) Verification Certificate

Use when the target model already performs native extended thinking (o3, R1, Claude Extended Thinking, Gemini Thinking) so you do not pollute its internal search tree with redundant visible CoT instructions (`[PRISM]`, `[HARNESS]`):

```markdown
The verification protocol for [TASK] requires grounding all outputs in declared premises and post-condition checks. Perform path exploration in your internal reasoning, and emit only the verified certificate below.

### PREMISES
- [P1] Source inputs and active constraints: [exact scope]
- [P2] Target invariants (complexity, interfaces, edge cases): [exact criteria]

### VERIFICATION GATES
For each target invariant in [P2], record the verification outcome:
- [V1] Invariant [name]: [SATISFIED / VIOLATED / UNTESTABLE] -> Evidence: [exact line, counterexample, or boundary check from P1]
- [V2] Invariant [name]: [SATISFIED / VIOLATED / UNTESTABLE] -> Evidence: [exact line, counterexample, or boundary check from P1]

### FORMAL CONCLUSION & DELIVERABLE
- Disposition: [summary grounded in V1, V2]
- Deliverable: [the complete, copy-pasteable code, proof, or artifact satisfying all V-gates]
```

#### Mode 3 Pattern B: Persistent Agent Context (`AGENTS.md` / `CLAUDE.md` / System Prompt)

Use when optimizing repository context files or coding-agent harnesses (`[CONTEXT-FILES]`, `[HARNESS]`):

```markdown
# [Project Name] Agent Operating Contract

## 1. Environment & Execution Commands (Non-Inferable Only)
- Setup / Environment: `[exact command, e.g., uv sync]`
- Targeted Test Runner: `[exact command for single test file, e.g., pytest path/to/test.py -q]`
- Typecheck & Lint Gate: `[exact command]`

## 2. Hard Architectural Invariants
- [I1] Boundary rule: [non-obvious constraint that cannot be inferred from directory names]
- [I2] State / Context rule: For tasks spanning 3+ files, maintain progress and intermediate findings in a scratchpad file rather than re-running broad repository searches.

## 3. Verification Gate (Required Before Completion)
- Run the targeted test and lint commands from Section 1 on all modified files.
- Report exact command exit codes and output summaries before declaring the task complete.
```

*(Note per `[CONTEXT-FILES]`: Strip all auto-generated directory trees, file-by-file overviews, and generic style advice; these reduce task success by 3% and increase token costs by >20%.)*

#### Mode 4 Pattern: Creative & Divergent Certificate v2 (`[VS]` + `[SLOPSHAPE]`)

Use for creative writing, essays, blog posts, marketing copy, and open-ended ideation:

```markdown
The editorial craft protocol requires completing the backstage scaffolding block before drafting the final piece.

### PREMISES
- [P1] Reader & context: [who is reading, what concrete problem or situation they are in]
- [P2] Target shift: [what specific realization or emotional shift the piece must produce]
- [P3] Voice & constraints: [perspective, length, format, and domain boundaries]

### BACKSTAGE SCAFFOLD (complete first, or enclose in <backstage> tags)
- [NT0] Verbalized Distribution Sampling: Enumerate 4 structurally distinct angles for this piece, assigning each an estimated typicality probability (p) reflecting how often a default AI would pick it:
  1. [Angle 1: prototypical/safe] (p = ...)
  2. [Angle 2: moderate variation] (p = ...)
  3. [Angle 3: low-typicality, concrete angle] (p = ...)
  4. [Angle 4: contrarian or unexpected structural entry] (p = ...)
  Selection: Commit to the strongest angle with p <= 0.20 that fulfills [P1]-[P3].
- [NT1] Audience Friction: [what specific skepticism or lived detail opens the piece?]
- [NT2] Structural Trajectory: [map the progression so the thesis emerges from evidence rather than being pre-announced]
- [NT3] Register & Cadence: [concrete nouns, varied paragraph lengths, and practitioner voice choices]

### STRUCTURAL RARITY CONTRACT (anti-SlopShape rules for the final draft)
Construct the final piece to satisfy these four discourse rules:
1. Title & Opening: Open inside a specific moment, artifact, or tension; reserve the core thesis until after the first concrete evidence unit.
2. Argument Flow: Build the argument through direct evidence and causal progression rather than a formulaic "Old Way vs. New Way" contrast.
3. Voice: Write from a grounded practitioner perspective with specific domain texture rather than an institutional "editorial explainer" voice.
4. Ending: Close on a concrete implication, sharp edge case, or external action pathway rather than a summary synthesis paragraph that restates the thesis.

### FINAL OUTPUT
Present the finished piece cleanly, embodying the selected [NT0] angle and the Structural Rarity Contract.
```

### Step 4: Apply Positive Recipe Guards & Self-Check (`[SKILLS-SDO]`, `[META]`)

Replace negative "Do NOT" lists with **observable-predicate conditionals** and append the mandatory **Traceability Self-Check** to every analytical prompt:

```markdown
VERIFICATION & TRACEABILITY CONTRACT:
- Grounding rule: Base every step in [T] traces on explicit implementation details, data points, or text in [P1]-[Pn] rather than symbol names or titles.
- Missing-evidence predicate: When a path cannot be verified from [P1]-[Pn], record `UNABLE TO TRACE: [exact missing input]` in the trace and list it under Verification Gaps.
- Counterexample predicate: When disconfirming evidence or edge-case failures appear in [P1]-[Pn], record them as a dedicated `[T]` trace even if the overall verdict is positive.
- Neutrality predicate: Derive the Verdict strictly from `[T]` traces without referencing downstream business goals, timelines, or evaluation rubrics.

TRACEABILITY SELF-CHECK (mandatory before finalizing):
Verify that every claim in your Formal Conclusion cites at least one `[T]` or `[V]` identifier from above. If any claim lacks a supporting identifier, either add the missing trace from [P1]-[Pn] or remove the claim so zero orphaned conclusions remain.
```

### Step 5: Present the Optimized Result

Deliver:
1. **Task Classification & Mode Selection**: State the task type (`[PRISM]`), target persona rule, and chosen Certificate Mode (Max, Lite, LRM/Harness, or Creative v2) with expected token tradeoff.
2. **The Optimized Prompt**: In a clean, copy-pasteable code block.
3. **Research Rationale**: A concise bullet list mapping each change to its paper citation (`[META]`, `[GOAL-BLIND]`, `[ACE]`, `[HIERARCHY]`, `[CODE-SMELLS]`, `[PRISM]`, `[VS]`, `[SLOPSHAPE]`, `[CONTEXT-FILES]`, `[HARNESS]`, `[SKILLS-SDO]`).

## Reference Materials

- `references/domain-templates.md`: 12 ready-to-use templates (Code Review, Document Analysis, Research Synthesis, Compliance, Decision-Making, Comparative Analysis, Medical Reasoning, Legal Analysis, Financial Due Diligence, Blank Custom, Agentic System Prompt / `AGENTS.md`, and Creative / Editorial Writing).
- `references/research-principles.md`: Quick-reference index of all 11 research sources and their actionable constraints.
- `references/examples.md`: 9 annotated before/after prompt transformations across analytical, agentic, and creative domains.
