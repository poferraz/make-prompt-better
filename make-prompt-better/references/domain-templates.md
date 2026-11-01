# Domain-Specific Certificate Templates

Reference library for the `make-prompt-better` skill (v4.3.0). Each template adapts semi-formal reasoning to a specific domain and incorporates:
- **Requirement preservation** as the first invariant: every requested deliverable, sub-question, ordering rule, and operational constraint is retained (Zhang, Hu et al., 2026; Yin et al., 2026)
- **Itemized identifiers** `[P1]`, `[T1]`, `[V1]` with anti-redundancy cross-referencing so facts are stated once and cited by ID rather than repeated across sections (Ugare & Chandra, 2026; Zhang, Hu et al., 2026)
- **Dual context binding**: verbatim embedding in `[P]` for portable/isolated prompts, or exact `file:line` pointers for working-context coding agents (Ugare & Chandra, 2026; Lee et al., 2026)
- **Authority-framed preambles** using expertise or consensus language (Geng et al., 2025)
- **Goal-blind conclusion formats** that strip evaluative pressure while keeping operational constraints (Cao, Jiang & Xu, 2026)
- **Persona calibration** per task type (Hu, Rostami & Thomason, 2026)
- **Positive conditional recipes** instead of brittle prohibition lists (Yin et al., 2026)
- **Mandatory Remediation and Traceability Self-Check blocks** (Ugare & Chandra, 2026)

Pick the template closest to the user's task, select the intensity mode (Lite by default for routine/single-artifact queries; Max for complex multi-artifact audits; Mode 3 for LRM/Harness; Mode 4 for Creative v2), and customize the fields.

---

## 1. Code Review / Patch Verification

Origin: Primary domain from Ugare & Chandra (2026), arXiv:2603.01896.
Persona: OMIT (accuracy-dependent task; persona framing reduces code analysis precision per Hu, Rostami & Thomason, 2026).

```
The standard code review protocol requires completing the following analytical
certificate before issuing any verdict. Keep certificate length proportional to
the code under review (use Lite single-line traces for short functions) and cite
[P]/[T] identifiers rather than repeating code or facts across sections.

### PREMISES
- [P1] Code artifact(s): [embed exact code/diff for portable prompts, or cite file:line ranges in Working-Context mode]
- [P2] Symbols & contracts: [function signatures, expected units/types, and caller assumptions]
- [P3] Runtime & test constraints: [language version, edge boundaries, concurrency or performance invariants]

### EXECUTION TRACES
For each modified path or defect candidate (in Lite mode, use single-line causal
arrows: `[T1] Input -> Operation -> State Mutation -> Result`):
- [T1] Trace [path_or_symbol]:
  1. Entry & concrete inputs: [normal and boundary values, e.g., fractional vs. integer inputs]
  2. Execution & state flow: [exact line/branch behavior and invariant check]
  3. Observable outcome: [return value, side effect, or failure mode]

Grounding rule: Trace the actual implementation body rather than inferring from
function or variable names. State each fact once in [P] and reference it by ID.
When a symbol or caller convention is outside the provided context, record
`UNABLE TO TRACE: [symbol/convention]` and state what is assumed.

### FORMAL CONCLUSION
- Verdict: [PASS / FAIL / CONDITIONAL] citing [T] identifiers
- Verification gaps: [paths marked UNABLE TO TRACE and the inputs needed]

### REMEDIATION / NEXT ACTION
Provide one of the following matching all requested deliverables:
- A complete, copy-pasteable code patch fixing all defects identified in [T]
- Exact test cases to cover any unverified paths in Verification Gaps
- The explicit statement: "No remediation required: [reason citing T-identifiers]"

TRACEABILITY SELF-CHECK: Verify that every claim in the Formal Conclusion cites
at least one [T] identifier and that all user questions are answered.
```

---

## 2. Document Analysis / Review

Persona: MINIMAL for mixed tasks (`"You are an analyst."`), OMIT for pure fact extraction.

```
The established analytical protocol for document review requires completing this
certificate before providing any assessment. Keep scaffolding concise and avoid
repeating quoted passages across sections.

### PREMISES
- [P1] Source text / artifact: [embed exact text for portable prompts, or cite document/section in Working-Context mode]
- [P2] Claims & review scope: [specific claims, questions, or deliverables requested]
- [P3] Reference standards & missing context: [applicable baselines, definitions, or absent supporting artifacts]

### EVIDENCE TRACES
For each claim or section in [P2]:
- [T1] Claim / Finding [topic]:
  1. Source wording: [exact quote or concise reference to P1]
  2. Verification & denominator check: [explicit calculation, baseline required, or comparison standard from P3]
  3. Credibility disposition: [SUPPORTED / UNSUPPORTED BY SUPPLIED TEXT / CONTRADICTED, distinguishing unsupported from disproven]

Grounding rule: Anchor every trace in [P1] and state each fact once. When
supporting evidence (such as pilot data, comparator sets, or cost breakdowns) is
absent from [P1], record `ABSENT FROM [P1]: [exact evidence needed to verify]`.

### FORMAL CONCLUSION
- Assessment: [concise evaluation citing T-identifiers]
- Evidence gaps: [items marked ABSENT FROM P1]

### REMEDIATION / NEXT ACTION
Provide a concrete, copy-pasteable replacement draft or verification checklist
that qualifies unvalidated claims as testable targets, or state: "No remediation
required: [reason]."

TRACEABILITY SELF-CHECK: Verify that every finding in the conclusion cites at
least one [T] identifier and fulfills all deliverables in [P2].
```

---

## 3. Research Synthesis

Persona: OMIT (accuracy-dependent; factual synthesis must remain free of role-induced bias per Hu, Rostami & Thomason, 2026).

```
Peer-reviewed systematic synthesis methodology requires completing the following
structured certificate before presenting any cross-source findings. Cite [P]/[T]
identifiers rather than repeating study details across sections.

### PREMISES
- [P1] Sources & evidence base: [list provided papers/data, or note when synthesis draws on established empirical literature]
- [P2] Research question & required deliverables: [exact question, balance requirements, and scope]
- [P3] Methodological & measurement boundaries: [definitions, task types, and known confounders]

### EVIDENCE TRACES
For each mechanism, finding cluster, or source dimension:
- [T1] Dimension / Mechanism [name]:
  1. Positive / supporting evidence: [conditions, study designs, and measured effects]
  2. Negative / contradicting evidence: [conditions where the effect reverses or degrades]
  3. Moderating variables: [task coupling, measurement differences, selection effects, or time horizon]

Grounding rule: Distinguish measured causal effects from observational
correlations. When exact study texts or effect sizes are not supplied in [P1],
qualify claims by study design and mark unverified specifics as `UNSPECIFIED IN INPUT`.

### FORMAL CONCLUSION
- Balanced synthesis: [core convergent and contested findings citing T-identifiers]
- Practical moderators: [when the effect is positive vs. negative per T-traces]

### REMEDIATION / NEXT ACTION
Provide a concise decision or evaluation protocol for applying these findings in
practice, grounded in the moderating variables from [T1]-[Tn].

TRACEABILITY SELF-CHECK: Verify that every synthesis claim cites at least one
[T] identifier and addresses all parts of [P2].
```

---

## 4. Compliance / Regulatory Check

Persona: OMIT (accuracy-dependent; compliance determinations require neutral verification).

```
Regulatory audit methodology requires completing this verification certificate
before issuing any compliance disposition. Keep clause traces concise and avoid
repeating policy text across sections.

### PREMISES
- [P1] Policy or system artifact under review: [embed exact policy items or cite config files]
- [P2] Applicable standard & revision: [pin exact standard/revision, e.g., NIST SP 800-63B-4, and distinguish conditional contexts such as single-factor vs. MFA]
- [P3] Implementation evidence scope: [what is observable in P1 vs. uninspected runtime implementation]

### COMPLIANCE TRACES
For each item in [P1] and required control in [P2]:
- [T1] Clause / Item [name]:
  1. Normative rule: [exact requirement and section in P2]
  2. Disposition: [COMPLIANT / NON-COMPLIANT / CONDITIONAL / UNABLE TO VERIFY FROM POLICY TEXT]
  3. Deficit or condition: [exact conflict or missing implementation evidence]

Grounding rule: Assign `COMPLIANT` or `NON-COMPLIANT` only where [P1] directly
satisfies or conflicts with [P2]; when a rule is context-dependent (e.g., MFA vs.
single-factor length) or requires unprovided implementation evidence (e.g.,
blocklist screening, rate-limiting across windows), mark `CONDITIONAL` or
`UNABLE TO VERIFY`.

### FORMAL CONCLUSION
- Disposition summary: [overall status citing T-identifiers]
- Unverified implementation controls: [items requiring config/runtime inspection]

### REMEDIATION / NEXT ACTION
Provide copy-pasteable replacement policy clauses for all non-compliant items
and a concrete verification checklist for conditional/unverified controls.

TRACEABILITY SELF-CHECK: Verify that every conclusion item cites a specific
[T] identifier and [P2] clause.
```

---

## 5. Decision-Making / Recommendation

Persona: MINIMAL (`"You are a decision analyst."`) for mixed analytical and communication demands.

```
The standard decision analysis framework requires completing this certificate
before recommending any course of action. Preserve all operational constraints
(team size, regulatory scope, budget, timeline) in [P] and avoid repeating facts.

### PREMISES
- [P1] Decision context & candidate options: [exact choice and options under evaluation]
- [P2] Hard operational & regulatory constraints: [e.g., team size, HIPAA/BAA requirements, timeline, budget]
- [P3] Missing commercial or architectural inputs: [unprovided pricing, workload, or vendor contract terms]

### OPTION TRACES
For each candidate option in [P1]:
- [T1] Option [name]:
  1. Constraint & compliance fit: [how the option meets or fails P2, distinguishing vendor eligibility from application-level obligations]
  2. Engineering & operational burden: [build, maintenance, and specialized security/audit effort]
  3. Failure modes & lock-in: [primary risks, dependencies, and migration cost]

Grounding rule: Evaluate every option against the exact same [P2] constraints.
Separate what a vendor or tool provides (e.g., a signed BAA) from what the team
must still configure and audit (e.g., PHI logging, session lifetimes, RBAC).

### FORMAL CONCLUSION
- Primary conditional recommendation: [selected option citing T-identifiers]
- Reversal condition: [exact threshold or requirement under which the alternative wins]
- Shared obligations: [controls required regardless of which option is chosen]

### REMEDIATION / NEXT ACTION
Provide a concrete, step-by-step implementation and verification checklist to
execute the recommended option and close the gaps in [P3].

TRACEABILITY SELF-CHECK: Verify that every comparative claim in the conclusion
cites the corresponding [T] option traces.
```

---

## 6. Comparative Analysis

Persona: OMIT for technical/factual comparisons; MINIMAL (`"You are an analyst."`) for mixed evaluations.

```
Rigorous comparative methodology requires completing this certificate before
issuing any comparison summary. In Mode 2 (Lite), cap premises at 3 items and
use a compact comparison table with single-line traces.

### PREMISES
- [P1] Subjects & workload: [exact systems compared and workload types]
- [P2] Quantitative parameters: [stated volume/growth rates, converted to explicit rates such as average writes/sec with stated assumptions]
- [P3] Unmeasured workload variables: [peak burst factor, payload size, retention window, query mix, budget]

### COMPARISON TRACES
Evaluate each comparison axis across the subjects:
- [T1] Transactional & schema model: [factual capabilities of Subject A vs. Subject B, avoiding false dichotomies]
- [T2] Semi-structured / log handling: [indexing, partitioning, and ingestion trade-offs]
- [T3] Scale & operational complexity: [impact of P2 rates and P3 unknowns on single-store vs. polyglot architectures]

Grounding rule: Base capability claims on current documented features (e.g.,
PostgreSQL JSONB and partitioning; MongoDB multi-document ACID transactions).
Treat stated monthly volumes as rates rather than stored-byte totals unless
record size and retention are provided in [P1]-[P2].

### FORMAL CONCLUSION
- Workload-conditional selection: [starting recommendation citing T1-T3]
- Crossover trigger: [measured condition that justifies switching or splitting stores]

### REMEDIATION / NEXT ACTION
Specify the exact benchmark workload (payloads, peak concurrency, p95 latency,
retention, and recovery checks) required to validate the selection before production.

TRACEABILITY SELF-CHECK: Verify that every claim in the conclusion references
a specific [T] dimension trace.
```

---

## 7. Medical / Clinical Reasoning

Persona: OMIT (accuracy-critical; roleplay framing degrades diagnostic accuracy per Hu, Rostami & Thomason, 2026).

```
Clinical reasoning methodology requires completing this structured certificate
while preserving acuity-first action ordering for time-critical presentations.
Keep traces concise and do not delay emergency stabilization steps.

### PREMISES
- [P1] Presenting context & symptoms: [demographics, chief complaint, radiation, associated symptoms]
- [P2] Objective findings: [vitals, hemodynamic instability markers, ECG/labs/imaging provided and pending]
- [P3] Missing history & contraindication checks: [allergies, anticoagulation, prior history, right-sided/posterior lead status]

### DIAGNOSTIC & ACUITY TRACES
- [T1] Primary high-acuity diagnosis: [condition, localizing evidence from P1-P2, and anatomical/hemodynamic implications such as inferior STEMI with hypotension/RV involvement risk]
- [T2] Competing / complicating conditions to exclude: [critical mimics or mechanical/conduction complications consistent with P1-P2]
- [T3] Time-critical stabilization & reperfusion priorities: [actions that must proceed immediately without waiting for pending biomarkers in P2, plus preload-sensitive medication cautions]

Grounding rule: Map every finding in [P1]-[P2] to its physiological significance
(e.g., leads II/III/aVF -> inferior wall; BP 90/60 -> hemodynamic compromise
requiring RV infarct check before nitrates). State each fact once.

### FORMAL CONCLUSION (Acuity-First Ordering)
- Primary diagnosis & immediate life-safety priority: [state top diagnosis and urgent reperfusion/stabilization directive first, citing T1 and T3]
- Critical exclusions & workup gaps: [items from T2 and P3]

### REMEDIATION / NEXT ACTION
Provide an ordered, time-prioritized stabilization and diagnostic checklist
(immediate bedside actions, reperfusion activation, contraindication checks,
and monitoring).
DISCLAIMER: This output is structured analytical support, not clinical care.

TRACEABILITY SELF-CHECK: Verify that every diagnostic and management item cites
a specific [T] trace and [P] premise.
```

---

## 8. Legal Analysis

Persona: OMIT (accuracy-critical; legal rule application requires neutral grounding).

```
Legal analytical methodology requires completing this structured certificate
before presenting any legal assessment. Preserve all stated case facts and
qualify conclusions where governing jurisdiction is unspecified.

### PREMISES
- [P1] Stated contract terms & case facts: [exact restrictions, duration, geographic radius, scope language, and post-employment conduct]
- [P2] Governing law & jurisdictional posture: [stated jurisdiction, or explicit note that jurisdiction is unspecified and governs enforceability]
- [P3] Missing factual & procedural inputs: [employee role, trade-secret access, consideration, choice-of-law clause, blue-pencil vs. reformation rules]

### LEGAL TRACES
For each enforceability dimension:
- [T1] Scope of activity ("any related industry"): [analysis of overbreadth against legitimate business interest standards]
- [T2] Geographic & temporal reach (radius and duration vs. actual conduct): [comparison of stated terms against typical reasonableness thresholds and the specific conduct in P1]
- [T3] Jurisdictional & remedial divergence: [how outcome shifts across statutory-ban states, reformation states, and strict blue-pencil states]

Grounding rule: Separate undisputed facts in [P1] from legal standards in [P2]
and missing context in [P3]. Do not assume a single jurisdiction when [P1] omits
it; trace how the core terms fare under common-law reasonableness and statutory regimes.

### FORMAL CONCLUSION
- Enforceability synthesis: [objective assessment citing T1-T3]
- Determinative missing facts: [items from P3 that control the outcome]

### REMEDIATION / NEXT ACTION
Provide concrete next steps (document/fact checklist for counsel and narrower
alternative covenant/NDA language) to address the exposure identified in [T1]-[T3].
DISCLAIMER: This output is analytical support, not legal advice.

TRACEABILITY SELF-CHECK: Verify that every conclusion claim cites at least one
[T] trace and accounts for all facts in [P1].
```

---

## 9. Financial Due Diligence

Persona: OMIT (accuracy-critical; numerical and structural analysis must remain unanchored).

```
Financial due diligence methodology requires completing this analytical
certificate before presenting any posture summary. State each reported figure
once in [P] and show exact arithmetic in [T] without prose repetition.

### PREMISES
- [P1] Reported figures by period: [exact revenue, expense ratios, and debt/cash events from input]
- [P2] Analytical dimensions requested: [growth trajectory, operating leverage, profitability, debt & liquidity impact]
- [P3] Unprovided financial statements & terms: [absent COGS vs. OpEx split, interest rate, maturity, cash balance, working capital, taxes]

### FINANCIAL TRACES
- [T1] Revenue, expense & operating income table: [compute exact dollar operating expenses and operating income for each period in P1, plus full-year totals and margin bps changes]
- [T2] Operating leverage & seasonality/trend analysis: [dip-and-recovery trajectory and incremental operating margin across periods]
- [T3] Capital structure & debt coverage check: [compare new debt in P1 against annualized/quarterly operating income and identify missing debt-service inputs from P3]

Grounding rule: Compute every dollar and percentage figure explicitly from [P1].
When a standard metric (such as free cash flow, net income, or interest coverage)
requires inputs absent from [P1], record `INSUFFICIENT DATA IN [P1]: [missing input]`.

### FORMAL CONCLUSION
- Financial health synthesis: [verified operational trajectory vs. balance-sheet unknowns citing T1-T3]
- Diligence gaps: [all items marked INSUFFICIENT DATA]

### REMEDIATION / NEXT ACTION
Provide a prioritized due-diligence request list and sensitivity checks to
resolve the gaps in [P3] and [T3].
DISCLAIMER: This output is analytical support, not investment advice.

TRACEABILITY SELF-CHECK: Verify that every figure and claim in the conclusion
cites a specific [T] calculation trace.
```

---

## 10. Creative / Editorial Writing with Verbalized Sampling & Anti-SlopShape (Mode 4)

Origin: Grounded in `[VS]` (Zhang et al., 2025, arXiv:2510.01171) and `[SLOPSHAPE]` (Madler, 2026, arXiv:2609.15369; Russell et al., 2026).
Persona: MINIMAL or FULL domain practitioner persona (alignment and voice task per Hu, Rostami & Thomason, 2026).

```
You are a [specific practitioner role, <=5 words]. Follow the editorial craft
protocol below to prepare and write the piece.

### PREMISES
- [P1] Audience & lived context: [who is reading and what concrete workday friction they face]
- [P2] Supplied features & boundaries: [include every supplied feature and fact; translate features into grounded experiential utility while avoiding unverified medical or quantitative guarantees]
- [P3] Format & register constraints: [word count, medium, perspective, and requested deliverables]

### INTERNAL BACKSTAGE PREPARATION (Perform silently before drafting; output backstage notes ONLY if the user explicitly requested brainstorming or planning notes)
- [NT0] Verbalized Distribution Sampling: Consider 3 to 4 structurally distinct entry angles
  and estimate each angle's heuristic typicality (p = likelihood a default LLM prompt
  would produce it). Select the strongest angle with p <= 0.20 that satisfies [P1]-[P3].
- [NT1] Opening Anchor: Choose a specific workday moment, artifact, or concrete scene to open the piece.
- [NT2] Inductive Trajectory: Map the progression so the product/essay thesis emerges from concrete details rather than being pre-announced.
- [NT3] Cadence & Texture: Vary sentence and paragraph lengths and use grounded practitioner nouns.

### STRUCTURAL RARITY CONTRACT ([SC0] Discourse-Level Anti-SlopShape Rules)
Shape the final piece so it satisfies all four structural rules:
1. Delayed Thesis (anti-STR_FLW_006 / PUR_OUT_003): Open inside the concrete anchor
   from [NT1] before stating the overarching thesis.
2. Direct Evidence Progression (anti-STR_FLW_005): Advance through specific features
   and lived mechanics rather than a formulaic "Legacy Way vs. Modern Way" contrast.
3. Practitioner Voice (anti-VOC_VOX_001): Write from a grounded viewpoint with asymmetric
   paragraph lengths rather than a symmetric, institutional "editorial explainer" tone.
4. Concrete Action Close (anti-STR_STG_008 / VOC_PRT_005): End on a concrete action,
   fit check, or immediate practitioner step rather than a restated-thesis summary.

### FINAL DELIVERABLE
Output ONLY the finished piece executing the selected [NT0] angle and adhering to the
Structural Rarity Contract (omit all [P], [NT], and [SC0] headers from the output unless
planning notes were explicitly requested).
```

---

## 11. Agentic System Prompt / `AGENTS.md` / `CLAUDE.md` Context File (Mode 3 `[CONTEXT-FILES]`)

Origin: Grounded in `[CONTEXT-FILES]` (Gloaguen et al., 2026, arXiv:2602.11988) and `[HARNESS]` (Lee et al., 2026, arXiv:2603.28052; Shao et al., 2026, arXiv:2609.37725; Nam et al., 2025, arXiv:2509.21825).
Persona: OMIT (coding agents and reasoning models perform best with direct operational contracts per Hu, Rostami & Thomason, 2026).
When to use: Optimizing `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, or multi-turn agent harness prompts. Preserves any explicitly requested overview, directory, or style sections in a compact block so zero user requirements are dropped.

```
<!-- Context Architecture Contract: Discoverable directory tutorials and generic style prose are compacted per Gloaguen et al. (2026) to protect agent context window while preserving all explicitly requested sections. -->
# [Repository / System Name] Agent Operating Contract

### 0. Architecture, Layout & Conventions (Compactly fulfill any explicitly requested overview, folder list, or style rules)
- Overview & Stack: [1-2 line summary of service architecture and backing stores]
- Directory Map: [compact 1-line-per-directory list of all user-specified folders, e.g., `app/api`, `app/models`, `app/services`, `tests/`]
- Coding Conventions: [concise statement of requested style rules, e.g., PEP8 4-space indentation, `snake_case` functions/variables, `CapWords` classes, and organized imports]

### 1. Non-Inferable Environment & Tooling Commands
- Unit Test Execution: `[exact command, e.g., pytest -m "not integration" --reuse-db]`
- Pre-Commit / Migration Gate: `[exact command, e.g., ./scripts/migrate.sh check]`
- Typecheck & Linter Gate: `[exact command if provided; do not invent unrequested commands]`

### 2. Hard Architectural & Boundary Invariants
- [I1] State / Schema Invariant: [exact non-obvious rule, e.g., never mutate Redis cache keys in `app/services/billing.py` without bumping `SCHEMA_EPOCH` in the same change]
- [I2] Context Hygiene (3+ File Edits): Store multi-file plans and intermediate test outputs in a scratchpad file rather than re-running broad repository searches.

### 3. Mandatory Verification Gate (Before Claiming Completion)
1. Execute the required verification commands from Section 1 on all touched modules.
2. Confirm exit code 0 and report concise command output in your final response.
3. If any check fails or cannot run in the current sandbox, report `VERIFICATION BLOCKED: [command + exact error]` and state which check remains incomplete.
```

---

## 12. LRM & Algorithmic Implementation Verification Harness (Mode 3 `[HARNESS]`)

Origin: Grounded in `[HARNESS]` (Lee et al., 2026, arXiv:2603.28052; Zhang et al., 2026, arXiv:2606.09498; Shao et al., 2026, arXiv:2609.37725; Nam et al., 2025, arXiv:2509.21825) and `[PRISM]` (Hu, Rostami & Thomason, 2026, arXiv:2603.18507).
Persona: OMIT (reasoning models and algorithmic implementation tasks perform best without roleplay framing per Hu, Rostami & Thomason, 2026).
When to use: Algorithmic implementation, async concurrency, state-machine coding, or Large Reasoning Model (LRM) tasks. Generates the complete executable implementation first to prevent verification preamble token starvation on compact models.

```
The verification protocol for [TASK] requires declaring compact premises,
generating the complete executable implementation first, and verifying it
through a post-hoc gate. Restrict non-code verification preamble and post-hoc
commentary overhead to <25% of the total response length so full output budget
is preserved for executable code.

### PREMISES (Compact: keep total non-code overhead <25% of response)
- [P1] Interface & inputs: [exact class/function signatures, types, numeric range/precision requirements, and embedded input data]
- [P2] Target invariants: [atomic state transitions, lock release before suspension/await, cross-thread/event-loop safety, timeout=0 and deadline semantics, cancellation safety, and large-integer/float boundary behavior]

### 1. COMPLETE EXECUTABLE IMPLEMENTATION (Generated First)
Provide the complete, production-ready, copy-pasteable implementation satisfying
[P1] and [P2] first, before emitting any verification tables or test prose.

### 2. POST-HOC VERIFICATION GATE ([V1] -> [V2] -> [V3])
After the implementation above, complete this compact verification gate:
- [V1] Concurrency & State Invariants:
  Map each invariant in [P2] to the exact lock/state mechanism in the code (`[SATISFIED / VIOLATED] -> [exact method/line]`).
- [V2] Executable Self-Test Harness:
  Provide a runnable self-test block (`asyncio.run` / `pytest` assertions) that deterministically exercises fractional refill, burst capacity, simultaneous coroutine contention, timeout=0 and positive timeouts, waiter cancellation, invalid arguments, and cross-thread event-loop access.
- [V3] Postconditions & Remaining Limits:
  State whether [V2] was executed or is unrun, and explicitly note any fairness, distributed-coordination, or floating-point precision boundaries outside scope.

TRACEABILITY SELF-CHECK: Confirm every invariant in [P2] is mapped in [V1] and
tested in [V2], and verify that non-code commentary stays <25% of the response.
```

---

## Custom Domain Blank Template (Fallback)

Persona: Classify task first per PRISM (`OMIT` for accuracy, `MINIMAL`<=5 words for mixed, `FULL` for alignment).

```
The standard analytical protocol in [DOMAIN] requires completing this reasoning
certificate before providing your final deliverable. Preserve all requested
deliverables and cite [P]/[T] identifiers rather than repeating facts.

### PREMISES
- [P1] Primary inputs examined: [embedded artifacts or file:line references]
- [P2] Requested deliverables & operational constraints: [rules, deadlines, and boundaries]
- [P3] Explicit assumptions & missing inputs: [what is taken as given and why]

### EVIDENCE TRACES
For each component of the analysis:
- [T1] Component [name]:
  1. Observable evidence: [specific data point or excerpt from P1]
  2. Reasoning step: [how P2 rules apply to the evidence]
  3. Counterevidence / edge case: [what challenges this step]
  4. Verification status: [VERIFIED / PARTIAL / UNABLE TO TRACE]

Grounding rule: Base every trace on explicit content in [P1]-[P3]. When evidence
is missing, record `UNABLE TO TRACE: [missing input]`.

### FORMAL CONCLUSION
- Verdict / Synthesis: [derived strictly from T-identifiers]
- Supporting traces: [cite T1, T2, etc.]
- Verification gaps: [all items marked UNABLE TO TRACE]

### REMEDIATION / NEXT ACTION
Provide a copy-pasteable deliverable, fix, or concrete execution sequence
addressing all requirements in [P2].

TRACEABILITY SELF-CHECK: Verify that every claim in the Formal Conclusion cites
at least one [T] identifier.
```

---

## Structured Output Wrapper (When Programmatic Parsing Is Required)

When the optimized prompt feeds into an API pipeline or downstream parser, pair the certificate with a typed JSON schema (Mahmoudi et al., 2025, arXiv:2512.18020):

```json
{
  "premises": [
    {"id": "P1", "content": "..."}
  ],
  "traces": [
    {"id": "T1", "subject": "...", "steps": ["..."], "status": "VERIFIED|PARTIAL|UNABLE_TO_TRACE"}
  ],
  "conclusion": {
    "verdict": "...",
    "supporting_traces": ["T1"],
    "verification_gaps": ["..."]
  },
  "remediation": {
    "action_required": true,
    "artifact_or_steps": "..."
  }
}
```
