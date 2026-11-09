# Prompt Transformation Examples

Before/after demonstrations of the semi-formal reasoning methodology applied across domains. Each example shows a vague original prompt, the problems identified through research-backed analysis, and the optimized certificate-structured prompt with annotated rationale.

---

### Example 1: Code Review

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Accuracy-critical task; per PRISM (Hu, Rostami & Thomason, 2026), persona adds no reliable gain on objective code analysis and risks anchoring bias.

#### Original Prompt

```
Review this pull request and let me know if anything looks wrong. I need to ship this for a client demo tomorrow so please be thorough. Focus on things that might cause bugs or performance issues during the demo.
```

#### Problems Identified

1. **Operational context must survive:** The client demo tomorrow and requested bugs/performance focus determine priority; retain them without assuming the code must pass review (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
2. **Thoroughness needs evidence:** Review demo risks thoroughly while allowing other evidenced defects; a priority is not a required finding (Cao, Jiang & Xu, 2026).
3. **No scope boundaries:** "Anything looks wrong" needs concrete artifact and behavior references (Zhang, Hu et al., 2026).
4. **Missing traceability:** Link each finding to the implementation and supplied artifacts (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Perform a thorough review of this pull request.

Use the provided artifacts and identify any that are unavailable:
[P1] The pull request diff (source files changed)
[P2] The repository's contributing guidelines (if present)
[P3] The test files associated with the changed modules (if available)
[P4] Operational context: a client demo tomorrow; prioritize bugs and
     performance issues that could affect that demo.

For each finding, trace your reasoning:

[T1] Identify the specific code location (file, line range, symbol name).
[T2] State the category of the issue (correctness, security, performance,
     maintainability, concurrency, error handling, API contract).
[T3] Describe the concrete behavior or invariant that is violated or at risk.
[T4] Cite the relevant [P] artifact that grounds this observation.
[T5] Provide a corrected version or a precise remediation step.

After enumerating findings, produce a conclusion [C1] that summarizes
the review disposition: whether the changes are structurally sound,
and which categories require action before merge.

Use [P4] to prioritize evidenced demo risks, followed by other evidenced
findings. Ground findings in [P1]-[P3]; identify missing demo coverage
instead of inventing behavior or assuming the deadline justifies approval.

If a code region appears correct, do not fabricate issues to fill space.
Explicitly state "No findings in [region]" when appropriate.
```

#### What Changed and Why

- **Preserved the client demo, tomorrow deadline, thoroughness and bugs/performance priority:** These are requested operational requirements. Neutral findings can still support or oppose shipping (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
- **Conditional evidence inputs and finding traces:** The rewrite requests artifact references, concrete behavior and remediation; unavailable guidelines or tests remain gaps, not assumed facts (Ugare & Chandra, 2026).
- **Categorized findings:** Categories help review the requested defects without requiring the model to manufacture an issue in every category (Mahmoudi et al., 2025).

---

### Example 2: Financial Due Diligence

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Financial analysis is objective and accuracy-critical; persona adds no reliable improvement per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Analyze this company's financials. I'm thinking about investing $500K so I want to know if they're a good bet. Look at the revenue growth and see if the valuation makes sense. They're a Series B SaaS startup.
```

#### Problems Identified

1. **The investment question needs neutral criteria:** Preserve the proposed $500K investment and assess the case without assuming a favorable or unfavorable recommendation (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
2. **Valuation is a requested deliverable:** "See if the valuation makes sense" calls for an assessment, not validation of a predetermined answer (Cao, Jiang & Xu, 2026).
3. **Revenue growth remains explicit:** Supporting metrics can qualify the analysis, but must not replace the requested revenue-growth assessment (Zhang, Hu et al., 2026).
4. **Missing inputs must stay missing:** Identify the supplied financials and request absent valuation or investment terms rather than inventing them (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Analyze the financials of this Series B SaaS startup and assess the
proposed $500K investment, including revenue growth and valuation.

Use only supplied materials; identify missing inputs needed for the assessment:
[P1] The company's financials for the available reporting periods; do not
     assume they are audited
[P2] Capitalization table and funding history (if provided)
[P3] Key SaaS operational metrics (ARR, MRR, net revenue retention, gross
     margin, LTV/CAC ratio), where reported
[P4] Management projections or investor deck financials (if provided)
[P5] Decision context: a proposed $500K investment in a Series B SaaS startup
[P6] Valuation and investment terms, if supplied; otherwise request them

For each analytical dimension below, produce a structured trace:

Revenue composition [T1]:
  Break down revenue by line, cohort, or customer segment as data permits.
  Identify growth rates period-over-period with explicit calculation.

Unit economics [T2]:
  Derive gross margin, CAC payback period, and LTV from available data.
  State every assumption required where data is incomplete.

Cash and burn [T3]:
  Calculate monthly net burn rate. Identify runway in months from the most
  recent balance sheet date. Flag any off-balance-sheet obligations visible
  in [P1]-[P4].

Capital structure [T4]:
  Map ownership tiers, liquidation preferences, and any option pool or
  convertible instrument overhang from [P2].

Consistency check [T5]:
  Compare management projections in [P4] against historical trends in [P1].
  Identify material divergences without attributing intent.

Valuation and investment assessment [T6]:
  Assess whether the valuation is supported by the supplied financials and
  terms. Relate strengths, risks and missing information to the proposed
  $500K investment. State the criteria and assumptions behind the assessment.

Produce a conclusion [C1] assessing whether the company appears to be a
reasonable investment and whether its valuation makes sense, based on the
traces. A positive, negative or conditional assessment is valid. If essential
inputs are absent, explain why a conclusion is not yet supported and ask
for those inputs. Present areas of strength and concern separately.

If data required for any [T] trace is absent from [P1]-[P6], state
explicitly: "Insufficient data for [Tn]; required: [specific data]."
Calculate derived figures transparently from supplied inputs and stated
formulas. Do not invent financial inputs or present unsupported estimates
as reported facts.
```

#### What Changed and Why

- **Preserved the decision and its context:** The $500K amount, Series B SaaS stage, revenue growth, valuation and investment assessment remain explicit. Goal-blindness removes pressure toward a verdict, not the requested decision (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
- **Added a valuation/investment trace:** The conclusion must answer both requested assessments or identify why evidence is insufficient (Ugare & Chandra, 2026).
- **Qualified evidence availability:** Financials are not assumed audited, and absent terms or metrics are requested rather than invented. This is the project's evidence-binding adaptation (Ugare & Chandra, 2026; Zhang, Hu et al., 2026).

---

### Example 3: Research Synthesis

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Factual synthesis of academic literature; persona is irrelevant to accuracy per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Summarize these 5 papers on retrieval-augmented generation for me. I need to write a literature review section for my thesis on RAG optimization. Make sure to highlight the key contributions of each paper.
```

#### Problems Identified

1. **The thesis context is a requirement:** Preserve the literature review on RAG optimization while representing each paper faithfully (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
2. **Key contributions must remain:** Attribute each paper's contributions to its authors and supporting text rather than removing the requested emphasis (Ugare & Chandra, 2026).
3. **Five sources need distinct identifiers:** Keep authors, methods and results associated with the right paper (Zhang, Hu et al., 2026).
4. **Missing text must be explicit:** Request unavailable papers or mark unsupported fields rather than inventing claims or citations (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Summarize these five papers on retrieval-augmented generation (RAG) for a
thesis literature review on RAG optimization. Highlight the key contributions
of each paper while faithfully representing its claims.

Use the five provided papers below; request any unavailable source text:
[P1] Paper A (full text or preprint)
[P2] Paper B (full text or preprint)
[P3] Paper C (full text or preprint)
[P4] Paper D (full text or preprint)
[P5] Paper E (full text or preprint)

For each paper [P1]-[P5], produce a trace with the following fields:

[Tn-1] Research question: State the question articulated in the paper's
       introduction or abstract, or mark it not stated.
[Tn-2] Method: Describe the approach taken (experimental, theoretical,
       empirical, architectural). Include dataset names, model identifiers,
       and evaluation metrics where specified.
[Tn-3] Key contributions and stated results: Highlight each paper's key
       contributions and report its findings as the authors present them,
       including confidence intervals or significance levels if given.
[Tn-4] Limitations: Extract limitations acknowledged by the authors. If
       none are stated, note: "Authors did not explicitly discuss limitations."
[Tn-5] Relation to field: Identify which prior work the paper builds on or
       responds to, based on its citations and framing.

After all per-paper traces, produce a cross-paper synthesis [C1]:
- Identify points of convergence (shared findings or methods) across papers.
- Identify points of divergence (conflicting results or incompatible claims).
- Note methodological gaps shared across multiple papers.

Explain how the findings relate to the RAG optimization literature review
without forcing agreement with a thesis position. Attribute contributions
and claims to the specific [P] source and distinguish claims from evidence.

If a field (e.g., limitations) is not addressable from the provided text,
state: "Not determinable from [Pn]." Do not infer unstated claims.
```

#### What Changed and Why

- **Preserved the thesis, subject and key contributions:** The five-paper summary still serves a RAG optimization literature review. Neutral attribution does not require deleting its purpose or requested emphasis (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
- **Per-paper sources and traces:** Identifiers keep contributions, methods and findings attached to their source; unstated questions or unavailable text remain explicit gaps (Ugare & Chandra, 2026; Zhang, Hu et al., 2026).
- **Separated synthesis from source claims:** Cross-paper connections can support the literature review without inventing agreement or unstated results (Ugare & Chandra, 2026).

---

### Example 4: Clinical Reasoning

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Clinical accuracy is safety-critical; persona roleplay does not improve diagnostic reasoning and may introduce confabulated credentials per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
My patient has been having headaches for 3 weeks, some dizziness, and blurred vision. Blood pressure has been elevated at their last two visits (148/92, 152/96). They're on lisinopril 10mg daily. What could this be? I want to rule out the scary stuff first.
```

#### Problems Identified

1. **Urgent-first ordering must survive:** "Rule out the scary stuff first" requests priority for serious possibilities, not a predetermined diagnosis. Preserve that order while distinguishing urgency from likelihood (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
2. **Case facts need evidence mapping:** Keep the supplied symptoms, readings, duration and medication explicit (Ugare & Chandra, 2026).
3. **Avoid diagnostic anchoring:** Consider the full differential after the urgent assessment rather than assuming that an alarming explanation is most likely (Zhang, Hu et al., 2026).
4. **State limitations:** Identify what the supplied information cannot rule out (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a clinical reasoning assistant performing structured differential
analysis based on presented case information.

The following clinical data points are provided:
[P1] Chief complaint: headache persisting for 3 weeks
[P2] Associated symptoms: some dizziness, blurred vision
[P3] Vital signs: BP 148/92 (visit N-1), BP 152/96 (visit N)
[P4] Current medication: lisinopril 10mg daily
[P5] Additional history, lab results, or imaging: [none provided]

Produce the following reasoning traces in this order:

Urgent assessment [T1]:
  Address serious possibilities requiring prompt evaluation first, using
  [P1]-[P5]. State the evidence and missing information relevant to ruling
  them out. Distinguish urgency from likelihood; do not claim that the
  supplied information excludes a condition when it cannot.

Differential generation [T2]:
  List other plausible conditions consistent with [P1]-[P5]. For each
  condition, state which data points support its inclusion.

Evidence mapping [T3]:
  For conditions in [T1]-[T2], map supporting and contradicting evidence
  from [P1]-[P5]. Note neutral or non-discriminating data points.

Missing information assessment [T4]:
  Identify absent information that would help narrow the differential or
  resolve the urgent uncertainties. State what each item would clarify.

Produce a conclusion [C1] summarizing:
- The most supported explanations given current evidence
- The most critical information gaps
- Which conditions cannot be ruled in or out without additional data

This analysis is not a clinical recommendation. All diagnostic reasoning
must be verified by a qualified clinician against the full patient context,
including information not captured in [P1]-[P5].
```

#### What Changed and Why

- **Preserved urgent-first ordering:** The first trace addresses serious possibilities without treating urgency as evidence that they are most likely. This applies requirement preservation to the user's ordering (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
- **Kept every supplied clinical fact:** The symptom duration, dizziness, vision change, both readings and lisinopril dose remain available for evidence mapping (Ugare & Chandra, 2026).
- **Made uncertainty explicit:** The prompt asks what cannot be ruled out and which information is missing; it does not promise a diagnosis from a short case description (Ugare & Chandra, 2026).

---

### Example 5: Content Strategy Audit

**Task Classification:** Mixed (accuracy in analysis, alignment in tone recommendations)
**Persona Decision:** OMIT. Direct audit instructions retain the strategy objective and evidence requirements without adding persona framing (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Look at our blog and tell me what's wrong with our content strategy. We're trying to increase organic traffic by 30% this quarter. Our competitors are [Company A] and [Company B]. Are we covering the right topics?
```

#### Problems Identified

1. **The target and period are operational requirements:** Preserve the 30% organic-traffic objective this quarter without promising that the audit can establish it is achievable (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
2. **Named competitors are relevant context:** Retain Company A and Company B for comparison without assuming their approach is better (Cao, Jiang & Xu, 2026).
3. **"What's wrong" presupposes defects:** Ask for strengths and gaps supported by evidence while still assessing topic choices (Cao, Jiang & Xu, 2026).
4. **Missing materials need identification:** Use supplied articles, analytics and competitor materials, and request essential gaps rather than inventing a sample or audience (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Conduct a content strategy audit of our blog. Assess whether we cover the
right topics for our objective of increasing organic traffic by 30% this
quarter, including comparison with Company A and Company B.

Use the supplied materials and mark missing inputs:
[P1] Our blog inventory and available article text
[P2] Our current topic taxonomy and audience information, if provided
[P3] Objective: increase organic traffic by 30% this quarter
[P4] Competitors: Company A and Company B; use their supplied or accessible
     materials, identifying the sources and any unavailable evidence
[P5] Traffic baseline and performance data, if provided

Topic coverage [T1]:
  Assess our topic coverage in [P1] against the objective in [P3] and the
  available audience evidence in [P2]. Cite the articles supporting findings.

Competitor comparison [T2]:
  Compare topics in [P1] with those supported by [P4]. Identify differences
  and gaps without assuming that copying a competitor will improve traffic.

Content and publishing patterns [T3]:
  Assess depth, audience fit and publishing patterns where [P1]-[P2]
  support them. Identify what cannot be assessed from the supplied material.

Traffic objective [T4]:
  Use [P5] to assess what the evidence says about [P3]. Distinguish observed
  performance from assumptions; request missing baseline or period data
  before claiming the 30% target is feasible.

Produce a conclusion [C1] answering whether our current topic choices
support the stated strategy. Report evidenced strengths, problems and
conditional priorities for this quarter, with sources and uncertainties.
Do not invent audience attributes, analytics or competitor behavior.
```

#### What Changed and Why

- **Preserved the goal, timing and named comparisons:** The 30% organic-traffic target this quarter and both competitors remain explicit evaluation context, not pressure to report success (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
- **Retained the requested topic judgment:** The audit can identify strengths, gaps and conditional priorities while remaining neutral about whether the strategy is effective (Cao, Jiang & Xu, 2026).
- **Kept evidence availability honest:** No arbitrary ten-article sample or invented audience is substituted for missing material (Ugare & Chandra, 2026).

---

### Example 6: Legal Contract Analysis

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Legal interpretation is accuracy-critical and objective in nature; per PRISM (Hu, Rostami & Thomason, 2026), persona does not improve performance on analytical legal tasks.

#### Original Prompt

```
Review this SaaS agreement and flag anything that looks risky or one-sided. We're a small startup signing with a much larger enterprise client so we need to be careful. Make sure the liability cap is fair.
```

#### Problems Identified

1. **Negotiating context matters:** Preserve the small startup and larger enterprise counterparty without assuming every asymmetric term is unacceptable (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
2. **Risk and fairness are requested assessments:** Make the criteria and uncertainty explicit rather than prohibiting those deliverables (Cao, Jiang & Xu, 2026).
3. **Liability remains a priority:** Assess the liability cap along with other evidenced risks; do not replace the specific question with a provision inventory (Zhang, Hu et al., 2026).
4. **Ground findings in the agreement:** Cite the actual terms and request missing context needed for conclusions (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Review this SaaS agreement for risky or one-sided terms and assess whether
the liability cap is fair for the stated parties.

Use the supplied agreement and identify missing inputs:
[P1] The SaaS agreement text
[P2] Party context: we are a small startup signing with a much larger
     enterprise client
[P3] Any supplied jurisdiction, commercial terms or risk criteria; request
     missing context needed for a qualified risk or fairness assessment

For each provision category below, produce a structured trace:

Scope and obligations [T1]:
  Extract and paraphrase the core obligations of each party. Cite section
  numbers from [P1].

Liability and indemnification [T2]:
  Identify all liability caps, exclusions, indemnification clauses, and
  consequential damage waivers. Quote the relevant text from [P1] for each.
  Assess liability-cap fairness using stated criteria and [P2]-[P3];
  identify the assumptions and missing context that limit that assessment.

Intellectual property [T3]:
  Map all IP ownership, licensing, and usage rights provisions. Note any
  grant-back clauses, work-for-hire language, or feedback IP assignments.

Termination and post-termination [T4]:
  Summarize termination rights (for cause, for convenience, notice periods),
  data return/deletion obligations, and any survival clauses.

Data and confidentiality [T5]:
  Identify data handling, storage, processing, and confidentiality provisions.
  Note any breach notification requirements and data residency constraints.

Asymmetry assessment [T6]:
  For each provision in [T1]-[T5], note whether the rights or obligations
  are mutual (apply equally to both parties) or asymmetric. State which
  party benefits from the asymmetry, citing the specific language.

Produce a conclusion [C1] flagging evidenced risky or one-sided provisions
and assessing liability-cap fairness for [P2]. Explain the criteria and
uncertainty behind each judgment, with contract citations. A favorable,
unfavorable or unresolved assessment is valid; do not presume unfairness.

If a provision category (e.g., force majeure, dispute resolution) is not
addressed in [P1], state: "Not addressed in [P1]: [category]."
Explain any supported consequence of the absence and what further context
is needed; absence alone does not establish a risk or an advantage.

This analysis is not legal advice. Consult qualified counsel for
interpretation and negotiation guidance.
```

#### What Changed and Why

- **Preserved the startup context and requested judgments:** Risk, one-sidedness and liability-cap fairness remain deliverables. Neutral criteria replace a presupposed outcome, not the assessment itself (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
- **Grounded judgments in terms and stated criteria:** Contract citations and explicit missing context make the assessment reviewable without inventing a jurisdiction or fairness threshold (Ugare & Chandra, 2026).
- **Kept liability prominent:** Other provision categories support the requested review rather than displacing the cap question (Zhang, Hu et al., 2026).

---

### Example 7: Compliance Audit

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Compliance verification is a deterministic, objective task; persona does not improve accuracy per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Check our data handling practices against GDPR. We got a complaint from a user in Germany and I want to make sure we're covered before we respond. Let me know if anything looks non-compliant.
```

#### Problems Identified

1. **Complaint context must remain:** A complaint from a user in Germany and assessment before responding are known context, not proof of compliance or noncompliance (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
2. **Noncompliance is a requested finding category:** Assess it against applicable requirements and evidence rather than forbidding the judgment (Cao, Jiang & Xu, 2026).
3. **Framework mapping needs limits:** Article clusters can organize the audit, but do not establish exhaustive coverage of GDPR (Zhang, Hu et al., 2026).
4. **Practices must be supplied:** Identify absent practices or complaint details rather than evaluating hypothetical facts (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a compliance analyst performing a structured regulatory gap analysis.

Use supplied materials and identify missing inputs needed for the review:
[P1] Description of current data handling practices (collection methods,
     storage locations, processing activities, retention policies)
[P2] Privacy policy and any external-facing data notices
[P3] Data processing agreements with third-party vendors (if available)
[P4] Record of processing activities (ROPA), if maintained
[P5] A complaint from a user in Germany; assess our data handling before we
     respond. Use the complaint text if provided; request missing details

Use the GDPR article clusters below as starting headings, adding other
applicable areas and stating the limits of coverage:

Lawful basis and consent [T1]:
  Map each data processing activity in [P1] to its lawful basis under
  Articles 6-7. Cite the specific activity and the basis claimed or implied.
  Note any activities without an identifiable lawful basis.

Data subject rights [T2]:
  Assess whether the practices in [P1] and notices in [P2] address the
  rights under Articles 15-22 (access, rectification, erasure, portability,
  objection, restriction, automated decision-making). For each right,
  state the mechanism by which it is fulfilled or note its absence.

Data protection principles [T3]:
  Evaluate practices in [P1] against Article 5 principles: lawfulness,
  purpose limitation, data minimization, accuracy, storage limitation,
  integrity and confidentiality, accountability. Map specific practices
  to each principle.

International transfers [T4]:
  Identify any cross-border data transfers described in [P1]-[P3]. Note
  the transfer mechanism cited (adequacy decision, SCCs, BCRs) or flag
  if no mechanism is documented.

Breach notification readiness [T5]:
  Based on practices in [P1], assess whether detection, documentation,
  and notification procedures exist that could satisfy Articles 33-34
  timelines. State what is documented and what is not.

Produce a conclusion [C1] that lists:
- Practices with clear regulatory mapping (article and practice aligned)
- Practices with unclear or absent regulatory mapping
- Potentially non-compliant practices, with the applicable article, evidence
  and uncertainty, including complaint-relevant issues supported by [P5]
- Missing inputs or remedial questions to resolve before we respond
- Required documentation not present in [P1]-[P4]

Assess whether the supplied evidence supports compliance, potential
noncompliance or an unresolved finding. Use [P5] for relevant prioritization
without presuming the complaint is valid or that we are covered. Avoid
claiming comprehensive compliance from incomplete evidence.

If [P3] or [P4] is not provided, state: "Analysis of [Tn] is incomplete;
[Pn] not available." Do not assume the existence of documentation not
provided.

This analysis is not legal advice. Consult qualified data protection
counsel for compliance determinations.
```

#### What Changed and Why

- **Preserved Germany, the complaint and response sequence:** The review still supports assessment before responding while allowing findings favorable or unfavorable to the organization (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
- **Retained potential noncompliance findings:** Regulatory mapping supports the requested assessment; it does not replace it with an inventory that forbids conclusions (Ugare & Chandra, 2026).
- **Qualified coverage and missing evidence:** Article clusters are starting points, and unavailable practices or complaint details remain explicit gaps (Zhang, Hu et al., 2026; Ugare & Chandra, 2026).

---

### Example 8: Repository Context File (`AGENTS.md` / `CLAUDE.md`)

**Task Classification:** Persistent Context / Agent Harness (Mode 3: LRM / Harness Mode)
**Persona Decision:** OMIT. Coding agents perform best with direct operational contracts rather than roleplay personas (Gloaguen et al., 2026; Hu, Rostami & Thomason, 2026).

#### Original Prompt / Context File

```
You are an elite 10x Staff Principal Python Architect working on our FastAPI billing microservice.
Always write clean, modular, PEP8-compliant, well-documented code and think step by step before every action.
Repository Overview:
- src/api/: FastAPI routers
- src/models/: SQLAlchemy models
- src/services/: Business logic
- tests/: Unit and integration tests
Make sure we don't break anything because we have a critical investor audit next week.
```

#### Problems Identified

1. **Requested context must survive:** Preserve the overview, four directory mappings and clean, modular, PEP8-compliant, well-documented code convention compactly (Gloaguen et al., 2026; Zhang, Hu et al., 2026).
2. **Persona is not an implementation rule:** Replace "elite 10x" and visible step-by-step narration with direct work and verification instructions (Hu, Rostami & Thomason, 2026; Lee et al., 2026).
3. **The deadline is operational context:** Retain the investor audit next week without treating it as pressure to declare unverified work safe (Cao, Jiang & Xu, 2026).
4. **Tooling and invariants are unknown:** The original supplies no commands or detailed architecture rules. Locate or request them instead of inventing a toolchain or project policy (Gloaguen et al., 2026; Ugare & Chandra, 2026).

#### Optimized Context File (`AGENTS.md` / `CLAUDE.md`)

```
<!-- Context Architecture Contract: Preserve requested context compactly; use verified project commands rather than invented tooling (Gloaguen et al., 2026). -->
# Billing Service Agent Operating Contract

## 0. Architecture, Layout & Conventions
- Overview & Stack: Python FastAPI billing microservice with SQLAlchemy models.
- Directory Map: `src/api/` (FastAPI routers), `src/models/` (SQLAlchemy models), `src/services/` (business logic), `tests/` (unit and integration tests).
- Coding Conventions: Write clean, modular, PEP8-compliant, well-documented code.
- Operational Context: A critical investor audit is next week; preserve existing behavior and report unverified risks honestly.

## 1. Project Commands & Invariants
The original context does not supply setup, test, lint or migration commands,
nor detailed architecture invariants. Locate the repository's documented
commands, configuration and existing boundaries before changing code. Record
only verified project rules; request missing information when it blocks work.

## 2. Work & Verification
Before each action, review the task requirements and relevant implementation.
Keep changes modular and document behavior and interfaces where needed.
Use the applicable documented checks to assess regressions rather than
claiming that the audit deadline guarantees correctness.

Before declaring completion, report the checks actually run and their
results. If a required check cannot run, identify the missing command,
configuration or service and the affected verification gap.
```

#### What Changed and Why

- **Preserved overview, layout, style and timeline:** The compact contract retains every supplied project fact and the next-week audit, rather than treating discoverable context or deadline information as disposable (Gloaguen et al., 2026; Zhang, Hu et al., 2026; Cao, Jiang & Xu, 2026).
- **Removed invented project rules:** No `uv`, Ruff, mypy, rounding policy, session architecture, Alembic requirement or scratchpad threshold was supplied. The rewrite asks for verified commands and boundaries instead (Ugare & Chandra, 2026; Gloaguen et al., 2026).
- **Kept verification observable:** The prompt requests checks and honest gaps without claiming that an unspecified tool enforces PEP8 or that a deadline proves safety. This is a project adaptation of harness guidance (Lee et al., 2026).

---

### Example 9: Creative / Editorial Blog Post

**Task Classification:** Creative / Divergent (Mode 4: Creative & Divergent v2)
**Persona Decision:** MINIMAL: `"You are a systems engineer."` Five-word practitioner framing grounds the voice without triggering over-stylized roleplay (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Write an 800-word blog post for our engineering blog about why teams should switch from manual prompt tweaking to structured context engineering. We want this post to go viral on Hacker News and drive signups for our developer platform.
```

#### Problems Identified

1. **Promotion and channel are requirements:** Preserve the engineering blog, Hacker News ambition and developer-platform signup intent without promising virality or inventing product claims (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
2. **The requested length is exact:** Keep the 800-word deliverable rather than substituting a range (Zhang, Hu et al., 2026).
3. **Creative scaffolding must serve the brief:** Internal angle selection and structural guidance are project adaptations, not permission to replace the topic, audience or commercial purpose (Zhang et al., 2025; Madler, 2026).

#### Optimized Prompt

```
You are a systems engineer. Follow the editorial craft protocol below to prepare
and draft the article.

### PREMISES
- [P1] Publication & channel: Our engineering blog, with the ambition of engaging Hacker News readers and going viral; do not promise that outcome.
- [P2] Topic: Why teams should switch from manual prompt tweaking to structured context engineering.
- [P3] Deliverable & purpose: An 800-word blog post that supports signups for our developer platform.
- [P4] Product facts and signup destination: Use supplied details, and request any missing information needed for a grounded platform mention.

### INTERNAL BACKSTAGE PREPARATION (Perform silently before drafting; output backstage notes ONLY if explicitly requested)
- [NT0] Verbalized Distribution Sampling: Consider 4 structurally distinct entry angles for this essay and estimate each angle's heuristic typicality (p = likelihood a default LLM prompt produces it):
  1. [Angle 1: chronological history of prompt engineering to context engineering] (p = ...)
  2. [Angle 2: high-level definition comparing prompts to RAM/OS] (p = ...)
  3. [Angle 3: a documented production incident, if supplied] (p = ...)
  4. [Angle 4: a supplied workflow or token trace] (p = ...)
  Selection: Prefer the strongest grounded angle with heuristic p <= 0.20 that satisfies [P1]-[P4]. If no available grounded angle meets that estimate, use the strongest grounded angle that satisfies the brief.
- [NT1] Opening Anchor: Use a supplied artifact or concrete conceptual example from the selected angle; identify illustrative examples rather than inventing a reported incident.
- [NT2] Inductive Trajectory: Let the core principle emerge after walking through the concrete failure mechanism and its fix.
- [NT3] Cadence & Texture: Use concrete systems nouns (context buffer, schema drift, delta updates, prefill cache) and vary paragraph lengths naturally.

### STRUCTURAL RARITY CONTRACT (Discourse-Level Anti-SlopShape Rules)
Construct the final essay to satisfy these four structural rules:
1. Delayed Thesis: Use a specific, non-spoiler title and open with the supplied artifact or concrete conceptual example from [NT1] before stating the overarching thesis.
2. Direct Evidence Progression: Advance the argument through failure mechanics and concrete diffs rather than a formulaic "Old Way vs. New Way" contrast section.
3. Practitioner Voice: Write from a direct engineering perspective rather than a symmetric "editorial explainer" voice.
4. Actionable Close: Connect a concrete next step to the developer-platform signup purpose using supplied product facts and destination, without invented promises.

### FINAL DELIVERABLE
When essential product information is missing for a grounded platform mention, ask targeted questions before drafting. Otherwise, output ONLY the finished 800-word engineering blog post about [P2], retaining the Hacker News and signup intent in [P1]-[P3] and using supplied facts in [P4]. Keep internal scaffolding out of the delivered article.
```

#### What Changed and Why

- **Preserved the full brief:** The rewrite keeps 800 words, the engineering blog, the requested topic, Hacker News ambition and developer-platform signup purpose. Neutral framing removes promises of success rather than removing commercial intent (Cao, Jiang & Xu, 2026; Zhang, Hu et al., 2026).
- **Grounded promotional content:** Product facts and the signup destination must come from the user; invented incidents, audience specifics and unsupported benefits are not substituted (Ugare & Chandra, 2026).
- **Kept creative preparation internal:** Angle sampling and structural guidance remain project heuristics informed by Zhang et al. (2025) and Madler (2026), not independently measured guarantees for this article or reasons to alter its requirements.
