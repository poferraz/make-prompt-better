# Domain-Specific Certificate Templates

Reference library for the `make-prompt-better` skill (v4.1.0). Each template adapts semi-formal reasoning to a specific domain and incorporates:
- **Itemized identifiers** `[P1]`, `[T1]`, `[V1]` for verifiable cross-referencing (Zhang, Hu et al., 2026)
- **Self-contained data binding** embedding all input code, tables, numbers, and case facts directly inside `[P]` premises (Ugare & Chandra, 2026; Zhang, Hu et al., 2026)
- **Authority-framed preambles** using expertise or consensus language (Geng et al., 2025)
- **Goal-blind conclusion formats** that omit downstream evaluation criteria (Cao, Jiang & Xu, 2026)
- **Persona calibration** per task type (Hu, Rostami & Thomason, 2026)
- **Positive conditional recipes** instead of brittle prohibition lists (Yin et al., 2026)
- **Mandatory Remediation and Traceability Self-Check blocks** (Ugare & Chandra, 2026)

Pick the template closest to the user's task, select the intensity mode (Max, Lite, LRM/Harness, or Creative v2), and customize the fields.

---

## 1. Code Review / Patch Verification

Origin: Primary domain from Ugare & Chandra (2026), arXiv:2603.01896.
Persona: OMIT (accuracy-dependent task; persona framing reduces code analysis precision per Hu, Rostami & Thomason, 2026).

```
The standard code review protocol requires completing the following analytical
certificate before issuing any verdict. Every section must be completed using
observable code artifacts.

### PREMISES
- [P1] Files modified: [list each file and the scope of changes]
- [P2] Symbols affected: [list each function, class, or method with file:line]
- [P3] Test coverage: [which existing or new tests exercise the modified paths]
- [P4] Runtime constraints: [language version, framework invariants, type rules]

### EXECUTION TRACES
For each modified code path or test case (in Lite mode, use single-line causal
arrows: `[T1] Entry -> Call Chain -> State Mutation -> Result`):
- [T1] Trace [path_or_test_name]:
  1. Entry point: [where execution begins and with what input types/values]
  2. Call chain: [function A -> function B with exact file:line citations]
  3. Data flow & state: [how values transform and what invariants hold or break]
  4. Exit condition: [return value, side effect, or exception raised]

Grounding rule: Trace the actual implementation body of every called function
rather than inferring behavior from function or variable names. When a called
symbol is outside the provided context, record `UNABLE TO TRACE: [symbol]`
and state what behavior is assumed.

### FORMAL CONCLUSION
- Verdict: [PASS / FAIL / EQUIVALENT / NOT EQUIVALENT]
- Supporting traces: [cite specific T-identifiers for every finding]
- Verification gaps: [paths marked UNABLE TO TRACE and the files needed]
- Confidence: [HIGH / MEDIUM / LOW with justification tied to T-identifiers]

### REMEDIATION / NEXT ACTION
The task is incomplete until this section provides one of:
- A complete, copy-pasteable code patch fixing all defects identified in [T]
- Exact test cases to cover any unverified paths in Verification Gaps
- The explicit statement: "No remediation required: [reason citing T-identifiers]"

TRACEABILITY SELF-CHECK: Verify that every claim in the Formal Conclusion cites
at least one [T] identifier. Remove or trace any unreferenced claim.
```

---

## 2. Document Analysis / Review

Persona: MINIMAL for mixed tasks (`"You are an analyst."`), OMIT for pure fact extraction.

```
The established analytical protocol for document review requires completing this
certificate before providing any assessment.

### PREMISES
- [P1] Document identity: [title, author, date, version, source artifact]
- [P2] Analysis scope: [specific sections or dimensions under review]
- [P3] Reference standards: [applicable specifications, policies, or benchmarks]
- [P4] Contextual inputs: [supporting documents or baseline facts provided]

### EVIDENCE TRACES
For each finding or section evaluated:
- [T1] Finding [topic]:
  1. Source location: [exact page, section, heading, or paragraph]
  2. Direct evidence: [quote or exact paraphrase of what the text states]
  3. Standard mapping: [how the text aligns with or diverges from P3]
  4. Internal consistency: [other sections in P1 that corroborate or conflict]

Grounding rule: Anchor every trace in a specific passage from [P1]. When a
topic in [P2] is absent from the text, record `ABSENT FROM [P1]: [topic]`.

### FORMAL CONCLUSION
- Assessment: [overall structural and factual evaluation]
- Key findings: [numbered list, each citing at least one T-identifier]
- Verification gaps: [items marked ABSENT or requiring external documents]

### REMEDIATION / NEXT ACTION
Provide concrete, copy-pasteable redline edits for each gap or inconsistency
cited in the conclusion, or state: "No remediation required: [reason]."

TRACEABILITY SELF-CHECK: Verify that every finding in the conclusion cites at
least one [T] identifier. Remove or trace any unreferenced claim.
```

---

## 3. Research Synthesis

Persona: OMIT (accuracy-dependent; factual synthesis must remain free of role-induced bias per Hu, Rostami & Thomason, 2026).

```
Peer-reviewed systematic synthesis methodology requires completing the following
structured certificate before presenting any cross-source findings.

### PREMISES
- [P1] Sources examined: [list each paper/source with author, year, identifier]
- [P2] Research question: [the exact question this synthesis addresses]
- [P3] Methodological scope: [experimental, empirical, or theoretical boundaries]
- [P4] Corpus limitations: [known sample limits or missing coverage in P1]

### EVIDENCE TRACES
For each source and cross-source claim:
- [T1] Claim or Source [identifier]:
  1. Primary evidence: [which P1 source(s) report this, with exact metrics]
  2. Study design: [sample size, models/datasets tested, evaluation protocol]
  3. Effect magnitude: [reported deltas, confidence intervals, replication]
  4. Contradicting evidence: [sources in P1 that diverge, and on what variable]
  5. Reconciliation: [mechanistic explanation for divergence, or flag UNRESOLVED]

Grounding rule: Report findings exactly as measured in [P1]. Treat the absence
of contradicting studies in [P1] as `UNEXAMINED IN CORPUS` rather than proof
of consensus.

### FORMAL CONCLUSION
- Integrated synthesis: [core findings citing T-identifiers]
- Convergent vs. contested claims: [grouped by T-identifiers]
- Open research gaps: [questions unresolved by P1]

### REMEDIATION / NEXT ACTION
Provide a structured summary table or actionable protocol derived from the
convergent [T] traces, or specify the exact follow-up query needed to close
the open research gaps.

TRACEABILITY SELF-CHECK: Verify that every claim in the synthesis cites at
least one [T] identifier and its underlying [P] source.
```

---

## 4. Compliance / Regulatory Check

Persona: OMIT (accuracy-dependent; compliance determinations require neutral verification).

```
Regulatory audit methodology requires completing this verification certificate
before issuing any compliance disposition.

### PREMISES
- [P1] System or artifact under review: [exact scope]
- [P2] Applicable clauses: [list each regulation, standard, or policy section]
- [P3] Boundary scope: [in-scope components vs. out-of-scope dependencies]
- [P4] Audit evidence provided: [logs, configs, code, or policy documents]

### COMPLIANCE TRACES
For each clause in [P2]:
- [T1] Clause [ID/section]:
  1. Normative requirement: [exact requirement from P2]
  2. Artifact examined: [specific section or config in P4]
  3. Disposition: [COMPLIANT / NON-COMPLIANT / PARTIAL / UNABLE TO VERIFY]
  4. Substantive match: [how the artifact's actual mechanism satisfies or fails P2]
  5. Deficit specification: [exact missing control or documentation if not COMPLIANT]

Grounding rule: Assign `COMPLIANT` only when [P4] contains verifiable implementation
evidence matching the clause's mechanism, not merely a policy title.

### FORMAL CONCLUSION
- Disposition summary: [overall status across all traced clauses]
- Non-compliant & unverified items: [list with clause IDs and T-identifiers]
- Severity ranking: [ordered by operational exposure grounded in T-traces]

### REMEDIATION / NEXT ACTION
For every NON-COMPLIANT, PARTIAL, or UNABLE TO VERIFY trace, provide the exact
remediation artifact (configuration change, policy clause text, or evidence
collection command).

TRACEABILITY SELF-CHECK: Verify that every conclusion item cites a specific
[T] identifier and [P2] clause.
```

---

## 5. Decision-Making / Recommendation

Persona: MINIMAL (`"You are a decision analyst."`) for mixed analytical and communication demands.

```
The standard decision analysis framework requires completing this certificate
before recommending any course of action.

### PREMISES
- [P1] Decision statement: [exact choice to be made]
- [P2] Candidate options: [list each distinct option under evaluation]
- [P3] Evaluation criteria: [ordered list of technical or operational factors]
- [P4] Hard constraints: [budget, latency, compatibility, timeline ceilings]

### OPTION TRACES
For each candidate option in [P2]:
- [T1] Option [name]:
  1. Criteria evaluation: [score and evidence against each factor in P3]
  2. Constraint check: [whether P4 ceilings are satisfied or breached]
  3. Failure modes: [primary technical or operational risks and triggers]
  4. Dependencies: [preconditions required for this option to succeed]
  5. Reversibility: [cost and effort required to migrate away later]

Grounding rule: Evaluate every option against the exact same [P3] criteria list
using observable evidence rather than general preference.

### FORMAL CONCLUSION
- Primary selection: [option name citing T-identifiers and P3 criteria]
- Conditional alternative: [runner-up option and the exact condition under which it wins]
- Explicit tradeoffs accepted: [what the primary selection sacrifices per T-traces]

### REMEDIATION / NEXT ACTION
Provide a concrete, step-by-step execution checklist or architecture snippet to
implement the primary selection.

TRACEABILITY SELF-CHECK: Verify that every comparative claim in the conclusion
cites the corresponding [T] option traces.
```

---

## 6. Comparative Analysis

Persona: OMIT for technical/factual comparisons; MINIMAL (`"You are an analyst."`) for mixed evaluations.

```
Rigorous comparative methodology requires completing this certificate before
issuing any comparison summary.

### PREMISES
- [P1] Subjects compared: [exact versions, models, or systems]
- [P2] Comparison dimensions: [explicit list of evaluation axes]
- [P3] Workload context: [the operational environment framing the comparison]
- [P4] Evidence sources: [benchmarks, docs, or code artifacts provided]

### COMPARISON TRACES
For each dimension in [P2]:
- [T1] Dimension [name]:
  1. Subject A evidence: [factual measurement or capability from P4]
  2. Subject B evidence: [factual measurement or capability from P4]
  3. Differential: [which subject leads on this axis and by what margin]
  4. Crossover condition: [when the advantage reverses under P3 constraints]

Grounding rule: Assess subjects dimension by dimension using [P4] evidence. When
a metric is missing for one subject, record `UNMEASURED IN [P4]: [subject/metric]`.

### FORMAL CONCLUSION
- Dimension matrix: [summary of winners per axis citing T-identifiers]
- Workload-conditional selection: [which subject fits which P3 condition]
- Unmeasured gaps: [metrics requiring empirical testing]

### REMEDIATION / NEXT ACTION
Provide the exact benchmark command, configuration template, or migration snippet
for the selected subject.

TRACEABILITY SELF-CHECK: Verify that every claim in the conclusion references
a specific [T] dimension trace.
```

---

## 7. Medical / Clinical Reasoning

Persona: OMIT (accuracy-critical; roleplay framing degrades diagnostic accuracy per Hu, Rostami & Thomason, 2026).

```
Clinical reasoning methodology, as established in evidence-based medicine,
requires completing this structured certificate before presenting any differential
synthesis.

### PREMISES
- [P1] Presenting context: [demographics, chief complaint, timeline, history]
- [P2] Objective findings: [vitals, physical exam, labs, imaging provided]
- [P3] Active regimen: [current medications, allergies, interventions]
- [P4] Reference guidelines: [relevant clinical standards of care]

### DIAGNOSTIC & THERAPEUTIC TRACES
For each plausible condition in the differential:
- [T1] Condition [name]:
  1. Supporting findings: [specific items from P1/P2/P3 that align]
  2. Disconfirming findings: [specific items from P1/P2/P3 that argue against]
  3. Discriminating gaps: [missing history, lab, or imaging needed to confirm/exclude]
  4. Acuity & risk: [time-sensitivity and consensus urgency criteria per P4]

Grounding rule: Evaluate multiple competing hypotheses across all data points in
[P1]-[P3] before ranking, separating probability from acuity.

### FORMAL CONCLUSION
- Evidence-ranked differential: [conditions ordered by supporting T-traces]
- High-acuity exclusions required: [urgent conditions citing T-identifiers]
- Critical information gaps: [discriminating workup items from T-traces]

### REMEDIATION / NEXT ACTION
List the concrete diagnostic workup questions or verification checks needed to
resolve the discriminating gaps in [T].
DISCLAIMER: This output is structured analytical support, not clinical advice.
All diagnostic and treatment decisions require a licensed healthcare clinician.

TRACEABILITY SELF-CHECK: Verify that every condition and workup item in the
conclusion cites a specific [T] trace and [P] premise.
```

---

## 8. Legal Analysis

Persona: OMIT (accuracy-critical; legal rule application requires neutral grounding).

```
Legal analytical methodology requires completing this structured certificate
before presenting any legal assessment.

### PREMISES
- [P1] Stated facts & text: [contract clauses, record facts, separated from inference]
- [P2] Governing law: [jurisdiction, statutes, regulations, or case law provided]
- [P3] Issues presented: [the specific legal or contractual questions to resolve]

### LEGAL TRACES
For each issue or provision category in [P3]:
- [T1] Issue [name]:
  1. Governing rule or clause: [exact section number and quoted text from P1/P2]
  2. Fact application: [how the text or rule applies to the facts in P1]
  3. Counter-interpretation: [the strongest competing reading of the text]
  4. Structural symmetry: [whether rights/obligations are mutual or asymmetric]

Grounding rule: Quote exact section numbers and clause language from [P1]/[P2].
When a standard provision is absent from [P1], record `NOT ADDRESSED IN [P1]`.

### FORMAL CONCLUSION
- Issue-by-issue synthesis: [objective assessment citing T-identifiers]
- Structural asymmetries & exposure points: [citing specific T-traces]
- Unresolved interpretive questions: [areas requiring extrinsic facts or counsel]

### REMEDIATION / NEXT ACTION
Provide copy-pasteable redline clause revisions to resolve identified
asymmetries or ambiguities.
DISCLAIMER: This output is analytical support, not legal advice. Consult
qualified legal counsel for binding determinations.

TRACEABILITY SELF-CHECK: Verify that every conclusion claim cites at least one
[T] trace and its underlying section in [P1]/[P2].
```

---

## 9. Financial Due Diligence

Persona: OMIT (accuracy-critical; numerical and structural analysis must remain unanchored).

```
Financial due diligence methodology requires completing this analytical
certificate before presenting any posture summary.

### PREMISES
- [P1] Entity & filings examined: [statements, cap table, metrics, dates]
- [P2] Analytical dimensions: [revenue quality, unit economics, burn, structure]
- [P3] Reference benchmarks: [historical periods or cohort baselines in P1]

### FINANCIAL TRACES
For each analytical dimension in [P2]:
- [T1] Dimension [name]:
  1. Reported figures: [exact numbers, periods, and source schedules from P1]
  2. Derived calculation: [explicit formula and step-by-step arithmetic]
  3. Period/cohort trajectory: [direction and rate of change across periods]
  4. Statement reconciliation: [cross-checks between income, cash flow, and deck]

Grounding rule: Compute metrics exclusively from figures present in [P1]. When a
required input is missing from [P1], record `INSUFFICIENT DATA FOR [T1]: [missing metric]`.

### FORMAL CONCLUSION
- Financial posture summary: [factual synthesis citing T-identifiers]
- Verified strengths vs. structural divergences: [separated, citing T-traces]
- Data completeness gaps: [all items marked INSUFFICIENT DATA]

### REMEDIATION / NEXT ACTION
Provide the exact diligence request list or spreadsheet verification formulas
needed to close all Data Completeness Gaps.
DISCLAIMER: This output is analytical support, not investment advice.

TRACEABILITY SELF-CHECK: Verify that every figure and claim in the conclusion
cites a specific [T] calculation trace.
```

---

## 10. Creative / Editorial Writing with Verbalized Sampling & Anti-SlopShape (Mode 4)

Origin: Grounded in `[VS]` (Zhang et al., 2025, arXiv:2510.01171) and `[SLOPSHAPE]` (Madler, 2026, arXiv:2609.15369; Russell et al., 2026), upgrading V3's Narrative Traces.
Persona: MINIMAL or FULL domain practitioner persona (alignment and voice task per Hu, Rostami & Thomason, 2026).

```
You are a [specific practitioner role, <=5 words]. The editorial craft protocol
requires completing the backstage scaffolding block before drafting the final piece.

### PREMISES
- [P1] Audience & lived context: [who is reading and what concrete friction they face]
- [P2] Target shift: [what specific realization or emotional shift the piece must earn]
- [P3] Format & register constraints: [word count, medium, perspective, domain facts]

### BACKSTAGE SCAFFOLD (complete before drafting; keep backstage if final-only requested)
- [NT0] Verbalized Distribution Sampling: Generate 4 structurally distinct entry angles
  for this piece and estimate each angle's typicality probability (p = likelihood a
  default LLM prompt would produce it):
  1. [Angle 1: prototypical/expected framing] (p = ...)
  2. [Angle 2: moderate variation] (p = ...)
  3. [Angle 3: concrete, low-typicality practitioner angle] (p = ...)
  4. [Angle 4: unexpected structural entry or inversion] (p = ...)
  Selection: Commit to the strongest angle with p <= 0.20 that satisfies [P1]-[P3].
- [NT1] Opening Anchor: [the specific artifact, failure, or concrete scene that opens the draft]
- [NT2] Inductive Trajectory: [how the core insight emerges from evidence rather than being pre-announced]
- [NT3] Cadence & Texture: [sentence length variation, concrete domain nouns, zero filler transitions]

### STRUCTURAL RARITY CONTRACT ([SC0] Discourse-Level Anti-SlopShape Rules)
Shape the final piece so it satisfies all four structural rules:
1. Delayed Thesis (anti-STR_FLW_006 / PUR_OUT_003): Use a specific, non-spoiler title
   and open inside the concrete anchor from [NT1] before stating the overarching thesis.
2. Direct Evidence Progression (anti-STR_FLW_005): Advance the piece through specific
   examples and mechanisms rather than a formulaic "Legacy Way vs. Modern Way" contrast.
3. Practitioner Voice (anti-VOC_VOX_001): Write from a grounded viewpoint with asymmetric
   paragraph lengths rather than a symmetric, institutional "editorial explainer" tone.
4. Open-Loop / Actionable Close (anti-STR_STG_008 / VOC_PRT_005): End on a sharp concrete
   implication, diagnostic question, or immediate practitioner experiment rather than a
   summary paragraph that restates the thesis.

### FINAL DELIVERABLE
Present the finished piece cleanly, executing the selected [NT0] low-typicality angle
and adhering to the Structural Rarity Contract.
```

---

## 11. Agentic System Prompt / `AGENTS.md` / `CLAUDE.md` Context File (Mode 3 `[CONTEXT-FILES]`)

Origin: Grounded in `[CONTEXT-FILES]` (Gloaguen et al., 2026, arXiv:2602.11988) and `[HARNESS]` (Lee et al., 2026, arXiv:2603.28052; Shao et al., 2026, arXiv:2609.37725; Nam et al., 2025, arXiv:2509.21825).
Persona: OMIT (coding agents and reasoning models perform best with direct operational contracts per Hu, Rostami & Thomason, 2026).
When to use: Optimizing `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, or multi-turn agent harness prompts.

```
<!-- Context Architecture Contract: Generic directory trees and standard language style guides are omitted per Gloaguen et al. (2026) to protect agent context window. -->
# [Repository / System Name] Agent Operating Contract

### 1. Non-Inferable Environment & Tooling Commands
(Include only exact commands that cannot be guessed from standard defaults; omit
directory trees and file inventories per Gloaguen et al., 2026.)
- Environment / Dependency Sync: `[exact command, e.g., uv sync --all-extras]`
- Single-File Test Execution: `[exact command, e.g., uv run pytest <path> -q]`
- Typecheck & Linter Gate: `[exact command, e.g., uv run ruff check . && uv run mypy src]`

### 2. Hard Architectural & Boundary Invariants
- [I1] Module boundary: [state non-obvious dependency direction or forbidden imports]
- [I2] Schema / Contract rule: [state required validation or serialization boundary]
- [I3] Security / State rule: [state protected files, credentials, or migration rules]

### 3. Multi-Step Execution & Context-as-a-File Protocol
- Plan Sufficiency Gate: When a task modifies 3+ files or alters a public interface,
  write a brief Premise & Verification checklist to a scratchpad file before editing
  source files.
- Context Hygiene: Prefer targeted symbol/grep searches over reading entire directories.
  Store intermediate findings and test logs in the scratchpad file so active context
  stays compact.

### 4. Mandatory Verification Gate (Before Claiming Completion)
1. Execute the Single-File Test and Linter commands from Section 1 on all touched modules.
2. Confirm exit code 0 and cite the exact command output in your final response.
3. If any check fails or cannot run in the current sandbox, report `VERIFICATION BLOCKED: [command + error]` rather than claiming success.
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
- [P1] Interface & inputs: [exact class/function signatures, types, and embedded input data]
- [P2] Target invariants: [concurrency safety, atomicity, bounds, and timeout/cancellation rules]

### 1. COMPLETE EXECUTABLE IMPLEMENTATION (Generated First)
Provide the complete, production-ready, copy-pasteable implementation satisfying
[P1] and [P2] first, before emitting any verification tables or test prose.

### 2. POST-HOC VERIFICATION GATE ([V1] Concurrency & State Invariants -> [V2] Executable Self-Test Harness)
After the implementation above, complete this compact two-step verification gate:
- [V1] Concurrency & State Invariants:
  Verify each invariant in [P2] in a compact checklist (`[SATISFIED / VIOLATED] -> [exact method/line in implementation]`).
- [V2] Executable Self-Test Harness:
  Provide a runnable self-test block (`asyncio.run` / `pytest` assertions) that deterministically exercises normal operation, edge boundaries, and concurrent contention from [P2].

TRACEABILITY SELF-CHECK: Confirm every invariant in [P2] is mapped in [V1] and
tested in [V2], and verify that non-code verification overhead stays <25% of the response.
```

---

## Custom Domain Blank Template (Fallback)

Persona: Classify task first per PRISM (`OMIT` for accuracy, `MINIMAL`<=5 words for mixed, `FULL` for alignment).

```
The standard analytical protocol in [DOMAIN] requires completing this reasoning
certificate before providing your final deliverable.

### PREMISES
- [P1] Primary inputs examined: [what artifacts or data are provided]
- [P2] Scope & invariants: [rules, constraints, and boundaries]
- [P3] Explicit assumptions: [what is taken as given and why]

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
The task is incomplete until you provide a copy-pasteable deliverable, fix, or
concrete execution sequence addressing the conclusion.

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
