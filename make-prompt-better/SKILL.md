---
name: make-prompt-better
description: "Use when optimizing, hardening, or rewriting any prompt, system instruction, AGENTS.md or CLAUDE.md context file, or agent workflow (v4.3.0) to improve accuracy, requirement preservation, auditability, structured output compliance, or creative diversity across any LLM or coding agent."
---

# Semi-Formal Prompt Optimizer (v4.3.0)

## Overview

This skill rewrites vague, brittle, or goal-biased prompts into verifiable **reasoning certificates** grounded in eleven peer-reviewed research papers. It is completely tool-agnostic and model-agnostic: the optimized prompts work across Claude Code, Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, GitHub Copilot, Cursor, Windsurf, API pipelines, and chat interfaces.

## Research Foundation (11 Papers)

Each principle in this workflow traces to an empirical finding. For full summaries and citations, read `references/research-principles.md`.

1. **[META] Semi-Formal Reasoning** (Ugare & Chandra, 2026, arXiv:2603.01896): Requiring explicit Premises, Evidence Traces, and a Formal Conclusion improves analytical accuracy by 10 to 15 percentage points on code analysis benchmarks at ~2.2x average token cost when proportional to task complexity.
2. **[GOAL-BLIND] Purpose-Conditioned Cognition** (Cao, Jiang & Xu, 2026, arXiv:2602.09504): Disclosing downstream evaluative pressure, desired verdicts, or grading rubrics biases intermediate reasoning and degrades out-of-sample generalization. Strip evaluative pressure while preserving decision-relevant operational constraints (deadlines, budgets, clinical acuity, target environment).
3. **[ACE] Agentic Context Engineering** (Zhang, Hu et al., 2026, arXiv:2510.04618): Itemized bullets with unique identifiers (`[P1]`, `[T1]`) prevent brevity bias and context collapse (+10.6% on agent benchmarks, 86.9% lower adaptation latency via incremental delta edits).
4. **[HIERARCHY] Instruction Hierarchy Failure** (Geng et al., 2025, arXiv:2502.15851): System/user message separation achieves only 9.6% to 45.8% compliance on conflicting constraints, whereas expertise and consensus framing ("The standard analytical protocol requires...") achieves 54% to 77.8% compliance.
5. **[CODE-SMELLS] LLM Integration Smells** (Mahmoudi et al., 2025, arXiv:2512.18020): 40.5% of LLM systems lack structured output schemas, causing silent downstream failures. Pair the reasoning certificate with an explicit JSON or typed schema whenever output is parsed programmatically.
6. **[PRISM] Persona Calibration** (Hu, Rostami & Thomason, 2026, arXiv:2603.18507): Expert personas improve alignment tasks (+0.4 to +0.65 MT-Bench) but damage accuracy tasks (-3.6 to -5.3 pp on MMLU). Omit personas on accuracy tasks, cap at 5 words on mixed tasks, and use full personas only on alignment tasks.
7. **[VS] Verbalized Sampling** (Zhang et al., 2025, arXiv:2510.01171): Post-training typicality bias causes mode collapse. Prompting the model to verbalize a candidate distribution with estimated typicality probabilities before committing increases creative and open-ended diversity by 1.6x to 2.1x.
8. **[SLOPSHAPE] Structural Signatures of AI Writing** (Madler, 2026, arXiv:2609.15369; Russell et al., 2026): Discourse-level structural features detect AI writing at 98.0 macro-F1 even after full rewording (10 core features reach 93.5 macro-F1). AI text clusters in a "tidy, self-announcing shape" (payoff in title, thesis before first section, formulaic legacy-vs-modern contrast, editorial-explainer voice, and restated-thesis summary endings). Creative and editorial prompts must enforce structural rarity rules.
9. **[CONTEXT-FILES] Repository Context File Evaluation** (Gloaguen et al., 2026, arXiv:2602.11988): Auto-generated `AGENTS.md` and `CLAUDE.md` files reduce coding agent task success by 3% while raising inference cost by over 20%, and directory overviews fail to speed up file localization. Persistent context files should prioritize non-inferable tooling commands and hard boundary invariants while compactly satisfying any explicit user-requested sections.
10. **[HARNESS] Harness Routing, Context-as-a-File & Plan Verification** (Lee et al., 2026, arXiv:2603.28052; Zhang et al., 2026, arXiv:2606.09498; Shao et al., 2026, arXiv:2609.37725; Nam et al., 2025, arXiv:2509.21825): Model-specific harnesses (+14.2 to +21.4 pp on Terminal-Bench-2.0), file-backed context state (+11.4% accuracy with 21.5% fewer FLOPs), and plan-sufficiency gates outperform static bloated prompts. For Large Reasoning Models (LRMs) and concurrency coding, code-first verification gates replace verbose pre-code tables to prevent overthinking and token starvation.
11. **[SKILLS-SDO] Skill Residency & Positive Recipe Shaping** (Yin et al., 2026, arXiv:2608.12610): Under competing incentives, negative prohibitions ("Do not X") backfire and increase violations compared to positive structural recipes and conditionals keyed to observable predicates ("When condition X holds, output Y").

### The Prompt Structure Framework

| Component | Certificate Mapping & Research Rule |
|---|---|
| **REQUIREMENTS** | **Invariant #1:** Preserve every requested deliverable, constraint, ordering requirement, and decision-relevant objective (`[ACE]`, `[SKILLS-SDO]`). |
| **IDENTITY** | Omit for accuracy tasks and LRMs; cap at 5 words for mixed tasks; use full persona only for alignment/style tasks (`[PRISM]`). |
| **TASK** | State what artifact or analysis to produce in goal-blind terms; strip evaluative pressure while keeping operational constraints (`[GOAL-BLIND]`). |
| **CONTEXT** | Declare as itemized `[P1]`, `[P2]` Premises (`[ACE]`). Use Portable embedding for isolated calls or `file:line` references for repo-connected agents (`[HARNESS]`). |
| **CONSTRAINTS** | Enforce proportional Certificate Mode using expertise/consensus framing (`[HIERARCHY]`) and positive observable-predicate conditionals (`[SKILLS-SDO]`). |
| **OUTPUT FORMAT** | Require a Formal Conclusion citing `[T]`/`[V]` identifiers, a `REMEDIATION / NEXT ACTION` block, and a typed JSON schema if parsed downstream (`[CODE-SMELLS]`). |

---

## The Optimization Workflow

Follow these steps in order whenever a user asks to optimize, harden, or review a prompt or context file.

### Step 0: Requirement Preservation & Anti-Overhead Guardrail (`[ACE]`, `[META]`, `[HARNESS]`)

Before selecting a template, enforce two foundational checks (Ugare & Chandra, 2026; Zhang, Hu et al., 2026; Lee et al., 2026):
1. **Requirement Preservation (Compiler Invariant #1)**: Inventory every explicit deliverable, sub-question, formatting rule, answer-ordering requirement (such as urgent clinical stabilization first), and decision-relevant constraint (budget, latency, regulatory scope, timeline) in the user's request. Every item must be preserved in the compiled prompt and mapped to an output section or verification check. When a heuristic (such as `[CONTEXT-FILES]` pruning or `[GOAL-BLIND]` framing) conflicts with an explicit user request, **retain the requested deliverable in a compact section** and identify the trade-off rather than silently deleting it.
2. **Skip / Proportional-Depth Check**:
   - **Trivial single-step requests** (single-line syntax fixes, simple factual lookups, pure formatting tweaks, or direct command translations) or **already near-ceiling structured prompts**: Skip full certificate compilation and apply only a 1-to-3 line goal-blind clarity cleanup.
   - **Proportional structure**: Default to concise evidence and a direct deliverable; use full multi-section certificates only when task complexity, fault localization, or human auditability warrants the added token cost.

### Step 1: Classify the Task Type & Target Environment (`[PRISM]`, `[HARNESS]`)

Determine the primary cognitive demand of the prompt and the execution context:
- **Accuracy-dependent** (code verification, bug hunting, math, fact extraction, legal/medical/financial analysis, compliance): **Omit persona**.
- **Mixed** (technical reports, architecture reviews, data analysis with executive presentation): **Minimal persona** (5 words or fewer, such as `"You are a systems analyst."`).
- **Alignment-dependent** (formatting, tone translation, style guides): **Full persona**.
- **Creative / Divergent** (copywriting, essays, storytelling, product messaging, ideation): **Minimal or Full persona**, routed to **Mode 4 (Creative & Divergent v2)**.
- **Persistent Context / Agent Harness** (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, system prompts, multi-turn agent loops): **Omit persona**, routed to **Mode 3 (LRM / Harness Mode)**.
- **Proportional Mode Selection**: Default to **Mode 2 (Lite Certificate)** for routine analytical queries, single-function code reviews, or flash/compact models to prevent verbosity inflation (Ugare & Chandra, 2026; Lee et al., 2026), reserving **Mode 1 (Max Certificate)** for multi-artifact audits, complex quantitative/regulatory analysis, or explicit auditability requests.

### Step 1b: Select Certificate Mode (4 Modes)

Choose the certificate mode that matches the task complexity, auditability needs, and execution environment:

| Mode | When to Use | Overhead | Structure Summary |
|---|---|---|---|
| **1. Max Certificate** | Multi-artifact or high-stakes audits (security, medical, legal, financial), complex fault localization, or when full step-by-step auditability is required | ~1.6x to 2.2x | Concise `[P]` Premises + non-repetitive `[T]` Evidence Traces + Formal Conclusion + Remediation + Self-Check |
| **2. Lite Certificate** | Default for routine analytical tasks (single-function code review, comparative analysis, everyday debugging) and flash/compact models | ~1.2x to 1.5x | Max 3 `[P]` Premises + single-line causal arrows (`[T1] Input -> Step -> Finding`) + 1-2 sentence conclusion + Remediation |
| **3. LRM / Harness Mode** | Reasoning models (o3, DeepSeek-R1, Claude Extended Thinking, Gemini Thinking), algorithmic concurrency coding, OR `AGENTS.md` / `CLAUDE.md` / agent system prompts | ~1.1x to 1.4x | For LRMs & concurrency coding: Compact `[P]` Premises + Complete Executable Implementation First + Post-Hoc Verification Gate (`[V1] Invariants -> [V2] Runnable Self-Test -> [V3] Scope & Limits`, `<25%` commentary overhead). For `AGENTS.md`: Non-inferable commands & invariants + compact fulfillment of any explicitly requested sections (`[CONTEXT-FILES]`, `[HARNESS]`) |
| **4. Creative & Divergent v2** | Copywriting, essays, blog posts, storytelling, brand messaging, open-ended ideation | ~1.1x to 1.6x | Internal `[NT0]` Verbalized Sampling distribution + `[NT1]`-`[NT3]` Narrative Traces + `[SLOPSHAPE]` structural rarity contract + clean final prose only (unless backstage notes are requested) |

### Step 2: Pre-Flight Anti-Dilution Sanitizer & Failure Diagnosis

Mechanically scan and repair the user's input against six empirical failure patterns while strictly honoring **Requirement Preservation**:
1. **Reasoning order vs. urgent action ordering (`[META]`, `[HIERARCHY]`)**: Ensure the model completes its `[P]` -> `[T]` verification before committing to an unverified verdict (Ugare & Chandra, 2026; Geng et al., 2025). However, when the user or domain requires immediate action ordering (such as emergency clinical stabilization in medical triage or an executive replacement summary), preserve that action-first priority at the top of the deliverable after the evidence check.
2. **Evaluative goal leakage vs. operational constraints (`[GOAL-BLIND]`)**: Strip biasing evaluative pressure (*"Prove our vendor failed"*, *"My boss wants to invest $500k so validate this valuation"*, *"Grade this 25/25"*) so the model acts as a neutral analytical sensor (Cao, Jiang & Xu, 2026). **Preserve** decision-relevant operational constraints (such as a 6-month migration window, HIPAA requirement, 10M record/month volume, or latency SLA) inside `[P]` premises.
3. **Guesswork & persona traps (`[META]`, `[ACE]`, `[PRISM]`)**: Strip flowery expert roleplay (*"You are a 10x world-class..."*) on accuracy/coding tasks (-5.3pp MMLU penalty per Hu, Rostami & Thomason, 2026) and require tracing concrete mechanisms rather than inferring from symbol names.
4. **Weak priority framing & mid-prompt burial (`[HIERARCHY]`)**: Replace polite requests (*"please make sure"*) with protocol authority framing (*"The standard analytical protocol requires..."*) and anchor verification rules at the end of the prompt to leverage recency bias (Geng et al., 2025).
5. **Negative prohibition traps (`[SKILLS-SDO]`)**: Convert bare *"Do not X"* or *"Don't hallucinate"* lists into positive structural recipes and observable-predicate conditionals (Yin et al., 2026).
6. **Context bloat, LRM overthinking & SlopShape risk (`[CONTEXT-FILES]`, `[HARNESS]`, `[VS]`, `[SLOPSHAPE]`)**: In `AGENTS.md`/`CLAUDE.md`, replace verbose auto-generated directory tutorials with non-inferable commands and invariants while keeping a compact summary of any explicitly requested overview/layout sections (Gloaguen et al., 2026); avoid forcing pre-code tables on reasoning/compact models (Lee et al., 2026); and keep `[NT0]` creative sampling internal unless backstage notes are requested (Zhang et al., 2025; Madler, 2026).

### Step 3: Select and Adapt the Certificate Structure

Read `references/domain-templates.md` to pick one of the 12 domain templates (or adapt the core structures below). Enforce the **Anti-Redundancy Rule** across all modes: state each fact once in `[P]` and reference it by ID (`[P1]`, `[T1]`) rather than repeating the same sentences across Premises, Traces, and Conclusion.

#### Mode 1 & Mode 2 Pattern (Max and Lite Analytical Certificates)

```markdown
The standard analytical protocol for [DOMAIN] requires completing this reasoning certificate before issuing any verdict. Keep scaffolding proportional to input complexity and cite [P]/[T] identifiers rather than repeating facts across sections.

### PREMISES
Declare all observable inputs, operational constraints, and starting assumptions (cap at 3 items in Lite mode):
- [P1] Primary artifact(s) examined: [exact embedded data/code, or file:line references in Working-Context mode]
- [P2] Applicable rules, requested deliverables, and operational constraints: [concrete specifications]
- [P3] Unverified inputs or environmental assumptions: [explicitly listed]

### EVIDENCE TRACES
Walk through the concrete path for each item (in Lite mode, use single-line arrows: `[T1] Input -> Operation -> Observable Result`):
- [T1] Trace [item 1]: [concise verification citing P1-P3 without repeating full input text]
- [T2] Trace [item 2]: [concise verification citing P1-P3]

### FORMAL CONCLUSION
Derive your verdict solely from the premises and traces above (preserve urgent/stabilization action ordering when clinically or operationally required):
- Verdict: [objective disposition]
- Supporting traces: [cite T1, T2, etc. for every claim]
- Verification gaps: [list any path marked UNABLE TO TRACE and the missing input required]

### REMEDIATION / NEXT ACTION
Provide one of the following matching all requested deliverables in [P2]:
- A complete, copy-pasteable fix (patch, revised text, corrected query, or executable command)
- A concrete sequence of verification commands to resolve any Verification Gaps
- The explicit statement: "No remediation required: [reason grounded in T-identifiers]"
```

#### Mode 3 Pattern A: Large Reasoning Model (LRM) & Algorithmic Verification Certificate (Template 12)

Use when the target model performs native extended thinking or implements complex concurrency/state algorithms so pre-code verification tables do not starve output token budgets (`[PRISM]`, `[HARNESS]`):

```markdown
The verification protocol for [TASK] requires declaring compact premises, generating the complete executable implementation first, and verifying it through a post-hoc gate. Restrict non-code commentary to <25% of the total response length.

### PREMISES (Compact: <25% total response overhead)
- [P1] Source inputs and interface contract: [exact signatures, types, numeric range/precision rules, and embedded or referenced artifacts]
- [P2] Target invariants: [concurrency safety, atomicity, cross-thread/event-loop semantics, timeout/cancellation rules, and edge boundaries]

### 1. COMPLETE EXECUTABLE IMPLEMENTATION (Generated First)
Provide the complete, copy-pasteable implementation satisfying [P1] and [P2] before emitting any verification tables or test prose.

### 2. POST-HOC VERIFICATION GATE ([V1] -> [V2] -> [V3])
- [V1] Concurrency & State Invariants: Check each invariant in [P2] (`[SATISFIED / VIOLATED] -> [exact line/mechanism in implementation]`).
- [V2] Executable Self-Test Harness: Provide a runnable test block (`assert` / `asyncio.run`) exercising normal paths, fractional/boundary precision, timeout/cancellation, and concurrent contention from [P2].
- [V3] Execution Status & Scope Limits: State whether [V2] was executed or remains unrun, and record any architectural or numerical boundaries outside scope.
```

#### Mode 3 Pattern B: Persistent Agent Context (`AGENTS.md` / `CLAUDE.md` / System Prompt, Template 11)

Use when optimizing repository context files or coding-agent harnesses (`[CONTEXT-FILES]`, `[HARNESS]`):

```markdown
<!-- Context Architecture Contract: Discoverable directory tutorials and generic style prose are compacted per Gloaguen et al. (2026) to protect agent context window while preserving all requested sections. -->
# [Project Name] Agent Operating Contract

## 0. Scope, Stack & Layout (Include when overview, directory layout, or conventions are requested)
- Stack & Overview: [1-2 line summary of architecture and core services]
- Key Directories: [compact 1-line-per-folder mapping of requested paths, e.g., `app/api`, `app/models`, `app/services`, `tests/`]
- Coding Conventions: [1-line rule, e.g., standard PEP8 enforced via linter; project-specific exceptions listed in Section 2]

## 1. Environment & Execution Commands (Non-Inferable Only)
- Setup / Environment: `[exact command, e.g., uv sync]`
- Targeted Test Runner: `[exact command, e.g., pytest -m "not integration" --reuse-db]`
- Migration / Typecheck / Lint Gate: `[exact command, e.g., ./scripts/migrate.sh check]`

## 2. Hard Architectural Invariants
- [I1] Boundary / State rule: [exact non-obvious constraint, e.g., never mutate Redis cache keys in `app/services/billing.py` without bumping `SCHEMA_EPOCH`]
- [I2] Multi-file scratchpad rule: For tasks spanning 3+ files, maintain progress and intermediate findings in a scratchpad file rather than re-running broad repository searches.

## 3. Verification Gate (Required Before Completion)
- Run the exact commands from Section 1 before declaring the task complete.
- Report each command's exit code and concise output summary; if a check fails or cannot run, report `VERIFICATION BLOCKED: [command + exact error]`.
```

#### Mode 4 Pattern: Creative & Divergent Certificate v2 (`[VS]` + `[SLOPSHAPE]`, Template 10)

Use for creative writing, essays, blog posts, marketing copy, and open-ended ideation:

```markdown
You are a [specific practitioner role, <=5 words]. Follow the editorial craft protocol below to prepare and deliver the piece.

### PREMISES
- [P1] Reader & context: [who is reading and what concrete workday or lived situation they are in]
- [P2] Supplied features & target shift: [preserve all supplied facts and translate them into grounded experiential detail; avoid unverified medical or quantitative guarantees]
- [P3] Voice & format constraints: [perspective, length, format, and domain boundaries]

### INTERNAL BACKSTAGE PREPARATION (Perform silently before drafting; emit in output ONLY if the user explicitly requested brainstorming/planning notes)
- [NT0] Verbalized Distribution Sampling: Consider 3 to 4 structurally distinct entry angles with heuristic typicality estimates (p = likelihood a default LLM prompt would pick it) and select the strongest angle with p <= 0.20 that fulfills [P1]-[P3].
- [NT1] Opening Anchor: Pick a specific moment, artifact, or lived friction to open the draft.
- [NT2] Structural Trajectory: Map the progression so the core claim emerges from concrete details rather than being pre-announced.
- [NT3] Register & Cadence: Use concrete nouns, varied paragraph lengths, and grounded practitioner voice.

### STRUCTURAL RARITY CONTRACT ([SC0] anti-SlopShape rules for the final draft)
Construct the final piece to satisfy these four discourse rules:
1. Title & Opening: Open inside the specific moment or artifact from [NT1]; reserve the thesis until after the first concrete detail.
2. Argument Flow: Build through direct feature-to-experience progression rather than a formulaic "Old Way vs. New Way" contrast.
3. Voice: Write from a grounded practitioner perspective with varied sentence cadence rather than an institutional "editorial explainer" voice.
4. Ending: Close on a concrete action or practical verification step rather than a summary paragraph that restates the thesis.

### FINAL DELIVERABLE
Output ONLY the finished piece embodying the selected [NT0] angle and [SC0] contract (do not print the [NT0]-[NT3] scaffold unless requested in the original prompt).
```

### Step 4: Apply Requirement Preservation, Context Binding & Self-Check (`[SKILLS-SDO]`, `[META]`, `[ACE]`)

Support both **Portable Prompts** and **Working-Context Prompts** (Ugare & Chandra, 2026; Zhang, Hu et al., 2026; Lee et al., 2026):
- **Portable Prompt Mode (Default for isolated chat, API calls, or self-contained snippets)**: Embed all supplied code, tables, numbers, and case facts verbatim inside `[P1]-[Pn]`; never leave empty placeholders like `[insert code here]`.
- **Working-Context Prompt Mode (For repo-connected coding agents or large local documents)**: Reference artifacts via exact `path/to/file:line_start-line_end` pointers and require reporting `UNABLE TO ACCESS: [path + reason]` if any referenced file is unreadable, avoiding stale duplicate copies of large files.

Append the **Verification & Requirement-Preservation Contract** to compiled analytical prompts:

```markdown
VERIFICATION & REQUIREMENT-PRESERVATION CONTRACT:
- Requirement-preservation check: Confirm that every deliverable, sub-question, ordering rule, and operational constraint from the original request is addressed in the output (multiple requirements may map to a single section or test).
- Context-binding predicate: Embed supplied snippets/tables verbatim in [P1]-[Pn] for portable prompts, or cite exact `file:line` anchors for repo-connected agents.
- Anti-redundancy rule: State each input fact once in [P] and cite `[P1]` / `[T1]` identifiers instead of repeating full paragraphs across sections.
- Missing-evidence predicate: When a path cannot be verified from [P1]-[Pn], record `UNABLE TO TRACE: [exact missing input]` and qualify the affected finding.
- Counterexample predicate: Record disconfirming evidence or boundary limitations as a dedicated `[T]` or `[V]` item even when the overall verdict is positive.

TRACEABILITY SELF-CHECK (mandatory before finalizing):
Verify that every conclusion claim cites a `[T]` or `[V]` identifier and that all requested deliverables from [P2] are complete.
```

### Step 5: Present the Optimized Result (Compact Receipt + Compiled Prompt)

Present the output in three clean tiers:
1. **Compact 6-Line Compiler Receipt**:
   ```text
   [COMPILER RECEIPT // make-prompt-better v4.3.0]
   [MODE]         : Mode <1|2|3|4> (<Max|Lite|LRM-Harness|Creative-v2>) | Template <#>: <Name>
   [PERSONA]      : <Omitted (Accuracy/LRM) | Minimal <=5w (Mixed) | Full (Alignment)> [PRISM]
   [PRESERVATION] : All Deliverables & Operational Constraints Retained | Goal-Bias Stripped [ACE, GOAL-BLIND]
   [BINDING]      : <Portable Verbatim in [P1..Pn] | Working-Context file:line Refs> [META, HARNESS]
   [PROPORTIONAL] : Anti-Redundancy Active | ~<1.1x-2.0x> target overhead
   ```
2. **The Optimized Prompt**: In a clean, copy-pasteable code block preserving all substantive facts and requested deliverables.
3. **Research Rationale & Trade-Off Note**: A concise bullet list mapping each change to its paper citation (`[META]`, `[GOAL-BLIND]`, `[ACE]`, `[HIERARCHY]`, `[CODE-SMELLS]`, `[PRISM]`, `[VS]`, `[SLOPSHAPE]`, `[CONTEXT-FILES]`, `[HARNESS]`, `[SKILLS-SDO]`), explicitly noting any scope/compactness trade-offs.

## Reference Materials

- `references/domain-templates.md`: 12 ready-to-use templates (Code Review, Document Analysis, Research Synthesis, Compliance, Decision-Making, Comparative Analysis, Medical Reasoning, Legal Analysis, Financial Due Diligence, Creative / Editorial Writing, Agentic System Prompt / `AGENTS.md`, and LRM & Algorithmic Implementation Verification Harness, plus Custom Domain Fallback and JSON Wrapper).
- `references/research-principles.md`: Quick-reference index of all 11 research sources and their actionable constraints.
- `references/examples.md`: 9 annotated before/after prompt transformations across analytical, agentic, and creative domains.
