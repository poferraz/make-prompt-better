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

1. **Goal leakage:** "ship this for a client demo tomorrow" reveals downstream use case, biasing the reviewer toward demo-critical paths and away from latent defects (Cao, Jiang & Xu, 2026).
2. **Evaluation criteria embedded:** "bugs or performance issues during the demo" tells the model what to find, suppressing detection of security flaws, maintainability issues, or incorrect abstractions (Cao, Jiang & Xu, 2026).
3. **No scope boundaries:** "anything looks wrong" is unbounded; the model cannot calibrate depth or prioritize signal over noise (Zhang, Hu et al., 2026).
4. **Missing certificate structure:** No explicit premise-to-conclusion chain, so the model can assert judgments without traceable reasoning (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a senior software engineer performing a structured code review.

You have access to the following artifacts:
[P1] The pull request diff (source files changed)
[P2] The repository's contributing guidelines (if present)
[P3] The test files associated with the changed modules

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

Do not speculate about use cases, deployment timelines, or business
priorities. Restrict all observations to what is observable in [P1]-[P3].

If a code region appears correct, do not fabricate issues to fill space.
Explicitly state "No findings in [region]" when appropriate.
```

#### What Changed and Why

- **Removed downstream context ("client demo tomorrow"):** Per GOAL-BLIND (Cao, Jiang & Xu, 2026), stripping the use case prevents the model from narrowing its review to demo-visible bugs while missing deeper defects.
- **Added numbered identifiers [P1]-[P3], [T1]-[T5], [C1]:** Per ACE (Zhang, Hu et al., 2026), explicit identifiers enable cross-referencing between premises, traces, and conclusions, reducing hallucinated findings.
- **Certificate structure (premises, traces, conclusion):** Per META (Ugare & Chandra, 2026), requiring the model to declare its evidence base [P1]-[P3] before reasoning forces grounding and makes unsubstantiated claims detectable.
- **Anti-hallucination guard ("do not fabricate issues"):** Directly counters the model's tendency to generate plausible-sounding but unfounded code review findings when no real issues exist.
- **Omitted persona beyond role framing:** Per PRISM (Hu, Rostami & Thomason, 2026), extensive persona scaffolding does not improve accuracy on objective code analysis tasks.
- **Categorized issue taxonomy in [T2]:** Per CODE-SMELLS (Mahmoudi et al., 2025), structured output taxonomies reduce ambiguity when the review output must be parsed or triaged.

---

### Example 2: Financial Due Diligence

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Financial analysis is objective and accuracy-critical; persona adds no reliable improvement per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Analyze this company's financials. I'm thinking about investing $500K so I want to know if they're a good bet. Look at the revenue growth and see if the valuation makes sense. They're a Series B SaaS startup.
```

#### Problems Identified

1. **Goal leakage:** "investing $500K" and "good bet" reveal the investment decision, causing the model to anchor toward a buy/no-buy recommendation rather than producing unbiased analysis (Cao, Jiang & Xu, 2026).
2. **Predefined conclusion framing:** "see if the valuation makes sense" implies the valuation should be validated rather than independently assessed (Cao, Jiang & Xu, 2026).
3. **Narrow scope signal:** "revenue growth" focuses the model on a single metric, suppressing analysis of unit economics, burn rate, cohort retention, or capital efficiency (Zhang, Hu et al., 2026).
4. **No evidence grounding:** No source documents or data artifacts are specified, so the model may generate analysis from training data rather than the provided materials (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a financial analyst conducting independent due diligence review.

You have access to the following source materials:
[P1] The company's audited financial statements (income statement, balance
     sheet, cash flow statement) for the available reporting periods
[P2] Capitalization table and funding history
[P3] Key SaaS operational metrics (ARR, MRR, net revenue retention, gross
     margin, LTV/CAC ratio) as reported
[P4] Management projections or investor deck financials (if provided)

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

Produce a conclusion [C1] that states the current financial posture of the
company based solely on evidence in [P1]-[P4]. Do not render an investment
recommendation. Present areas of strength and areas of concern separately.

If data required for any [T] trace is absent from [P1]-[P4], state
explicitly: "Insufficient data for [Tn]; required: [specific data]."
Do not infer or estimate figures not present in the source materials.
```

#### What Changed and Why

- **Removed investment decision context:** Per GOAL-BLIND (Cao, Jiang & Xu, 2026), eliminating "investing $500K" prevents the model from orienting analysis toward justifying or discouraging a specific investment.
- **Declared evidence base [P1]-[P4]:** Per META (Ugare & Chandra, 2026), specifying source materials as premises forces the model to ground every claim in provided data rather than generating plausible financials from training knowledge.
- **Explicit "do not render an investment recommendation":** Replaces the implicit "is this a good bet?" with a goal-blind directive that the output should be analytical, not advisory.
- **Incomplete-data handling instruction:** Per ACE (Zhang, Hu et al., 2026), requiring the model to state when data is missing rather than guessing reduces hallucinated financial figures, a critical risk in numerical domains.
- **Full certificate chain (premises, traces, conclusion):** Each [T] trace references specific [P] premises, making it auditable which claims derive from which data.
- **Broadened analytical scope beyond revenue growth:** Per ACE, comprehensive coverage instructions prevent the model from over-indexing on a single user-mentioned metric.

---

### Example 3: Research Synthesis

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Factual synthesis of academic literature; persona is irrelevant to accuracy per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Summarize these 5 papers on retrieval-augmented generation for me. I need to write a literature review section for my thesis on RAG optimization. Make sure to highlight the key contributions of each paper.
```

#### Problems Identified

1. **Goal leakage:** "literature review section for my thesis on RAG optimization" reveals the downstream writing task, biasing the summary toward the student's thesis angle rather than faithfully representing each paper's own claims (Cao, Jiang & Xu, 2026).
2. **"Key contributions" is evaluative:** Instructing the model to "highlight" certain elements presupposes what matters, suppressing neutral extraction of methods, limitations, and negative results (Cao, Jiang & Xu, 2026).
3. **No position tracking:** With 5 papers, the model will conflate authors, methods, and results without explicit per-paper identifiers (Zhang, Hu et al., 2026).
4. **No hallucination guard for citations:** The model may generate plausible-sounding claims not present in the source papers, especially when synthesizing across multiple texts (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a research synthesizer producing a structured analysis of academic papers.

You have access to the following source materials:
[P1] Paper A (full text or preprint)
[P2] Paper B (full text or preprint)
[P3] Paper C (full text or preprint)
[P4] Paper D (full text or preprint)
[P5] Paper E (full text or preprint)

For each paper [P1]-[P5], produce a trace with the following fields:

[Tn-1] Research question: State the explicit or inferred research question
       as articulated in the paper's introduction or abstract.
[Tn-2] Method: Describe the approach taken (experimental, theoretical,
       empirical, architectural). Include dataset names, model identifiers,
       and evaluation metrics where specified.
[Tn-3] Stated results: Report the findings exactly as the authors present
       them, including confidence intervals or significance levels if given.
[Tn-4] Limitations: Extract limitations acknowledged by the authors. If
       none are stated, note: "Authors did not explicitly discuss limitations."
[Tn-5] Relation to field: Identify which prior work the paper builds on or
       responds to, based on its citations and framing.

After all per-paper traces, produce a cross-paper synthesis [C1]:
- Identify points of convergence (shared findings or methods) across papers.
- Identify points of divergence (conflicting results or incompatible claims).
- Note methodological gaps shared across multiple papers.

Do not evaluate papers as "strong" or "weak." Do not recommend which paper
is most relevant for any particular downstream use. Present all claims as
the authors stated them, attributed to the specific [P] source.

If a field (e.g., limitations) is not addressable from the provided text,
state: "Not determinable from [Pn]." Do not infer unstated claims.
```

#### What Changed and Why

- **Removed thesis context:** Per GOAL-BLIND (Cao, Jiang & Xu, 2026), eliminating "thesis on RAG optimization" prevents the model from filtering or reweighting paper content to fit a predetermined narrative.
- **Per-paper identifiers [P1]-[P5] and field-level traces [Tn-1] to [Tn-5]:** Per ACE (Zhang, Hu et al., 2026), structured identifiers prevent cross-paper conflation and make every claim traceable to its source.
- **"Stated results" instead of "key contributions":** Removes evaluative framing; the model reports what the authors claim rather than curating what it deems important (GOAL-BLIND principle).
- **Anti-hallucination guard for missing content:** "Not determinable from [Pn]" instruction prevents the model from fabricating limitations or methods that are not present in the actual text.
- **Cross-paper synthesis [C1] separated from per-paper traces:** Per META (Ugare & Chandra, 2026), the certificate structure keeps individual paper analysis grounded before attempting higher-order synthesis, reducing cross-contamination between sources.
- **Explicit neutrality instruction ("do not evaluate as strong or weak"):** Prevents the model from imposing a quality ranking that serves no analytical purpose and introduces subjective bias.

---

### Example 4: Clinical Reasoning

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Clinical accuracy is safety-critical; persona roleplay does not improve diagnostic reasoning and may introduce confabulated credentials per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
My patient has been having headaches for 3 weeks, some dizziness, and blurred vision. Blood pressure has been elevated at their last two visits (148/92, 152/96). They're on lisinopril 10mg daily. What could this be? I want to rule out the scary stuff first.
```

#### Problems Identified

1. **Goal leakage:** "rule out the scary stuff first" reveals the clinician's differential priorities, potentially causing the model to over-weight catastrophic diagnoses and under-weight common explanations (Cao, Jiang & Xu, 2026).
2. **Missing evidence declaration:** Patient data is embedded in the narrative rather than structured as premises, making it difficult to trace which symptoms informed which reasoning step (Ugare & Chandra, 2026).
3. **No constraint against diagnostic anchoring:** Without explicit instructions, the model may latch onto the most salient symptom (headache) or the most alarming possibility, rather than systematically considering the full differential (Zhang, Hu et al., 2026).
4. **No instruction to flag reasoning limitations:** In clinical contexts, the model should explicitly state when its reasoning is insufficient for a clinical decision (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a clinical reasoning assistant performing structured differential
analysis based on presented case information.

The following clinical data points are provided:
[P1] Chief complaint: headache persisting for 3 weeks
[P2] Associated symptoms: dizziness, blurred vision
[P3] Vital signs: BP 148/92 (visit N-1), BP 152/96 (visit N)
[P4] Current medication: lisinopril 10mg daily
[P5] Additional history, lab results, or imaging: [none provided]

Produce the following reasoning traces:

Differential generation [T1]:
  List plausible conditions consistent with [P1]-[P5]. For each condition,
  state which data points support its inclusion.

Evidence mapping [T2]:
  For each condition in [T1], map the supporting and contradicting evidence
  from [P1]-[P5]. Explicitly note which data points are neutral or
  non-discriminating.

Missing information assessment [T3]:
  Identify clinically relevant information that is absent from [P1]-[P5]
  and would help narrow the differential. For each item, state which
  conditions it would help differentiate.

Risk stratification [T4]:
  Based solely on [P1]-[P5], identify conditions in [T1] that require
  urgent evaluation based on established clinical consensus. State the
  consensus basis for urgency classification.

Produce a conclusion [C1] summarizing:
- The most supported explanations given current evidence
- The most critical information gaps
- Which conditions cannot be ruled in or out without additional data

This analysis is not a clinical recommendation. All diagnostic reasoning
must be verified by a qualified clinician against the full patient context,
including information not captured in [P1]-[P5].
```

#### What Changed and Why

- **Removed "scary stuff" prioritization:** Per GOAL-BLIND (Cao, Jiang & Xu, 2026), the model now generates a differential based on evidence rather than alarm bias, while still producing risk stratification as a separate, structured trace.
- **Structured data as premises [P1]-[P5]:** Per META (Ugare & Chandra, 2026), separating clinical data into numbered premises makes it traceable: each reasoning step must cite which premise supports it.
- **Missing information assessment [T3]:** Per ACE (Zhang, Hu et al., 2026), explicitly requiring the model to state what it cannot determine prevents false certainty and overconfident diagnostic narrowing.
- **Risk stratification separated from differential generation:** Rather than baking urgency into the initial differential (which causes anchoring), risk assessment is its own trace step that references the already-generated differential.
- **Clinical disclaimer in the prompt itself:** Reinforces that the output is reasoning support, not a diagnosis; this is a safety guard beyond the scope of prompt optimization research but critical for responsible use.
- **No persona beyond "clinical reasoning assistant":** Per PRISM, extensive medical persona scaffolding does not improve accuracy on diagnostic reasoning and may produce confabulated experiential claims.

---

### Example 5: Content Strategy Audit

**Task Classification:** Mixed (accuracy in analysis, alignment in tone recommendations)
**Persona Decision:** MINIMAL: "senior content strategist". Mixed task where light domain framing orients the model's analytical vocabulary without introducing persona-driven bias per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Look at our blog and tell me what's wrong with our content strategy. We're trying to increase organic traffic by 30% this quarter. Our competitors are [Company A] and [Company B]. Are we covering the right topics?
```

#### Problems Identified

1. **Goal leakage:** "increase organic traffic by 30% this quarter" reveals the performance target, causing the model to evaluate content through a narrow traffic-acquisition lens rather than assessing strategy holistically (Cao, Jiang & Xu, 2026).
2. **Competitive framing as validation:** "Our competitors are [A] and [B]" implies the analysis should benchmark against these specific companies, suppressing independent topic gap analysis (Cao, Jiang & Xu, 2026).
3. **"What's wrong" presupposes problems:** The question structure assumes deficiencies exist, biasing the model toward finding faults rather than providing balanced assessment (Cao, Jiang & Xu, 2026).
4. **No evidence base defined:** "Look at our blog" is vague; without specifying which artifacts to analyze, the model cannot ground observations in specific content (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a senior content strategist conducting a content audit.

You have access to the following materials:
[P1] Blog article inventory (titles, publication dates, categories, word
     counts) for the available period
[P2] Topic taxonomy or content pillars currently in use
[P3] Sample of 10 recent articles (full text or representative excerpts)
[P4] Target audience description or ICP documentation (if available)

For each analytical dimension, produce a structured trace:

Topic coverage analysis [T1]:
  Map existing articles in [P1] against the taxonomy in [P2]. Identify
  pillars with dense coverage, pillars with sparse coverage, and topics
  that appear absent. Cite specific article titles from [P1].

Content depth assessment [T2]:
  Based on the sample in [P3], characterize the typical depth of treatment:
  surface-level overview, intermediate exploration, or comprehensive
  treatment. Note patterns in how thoroughly topics are addressed.

Audience alignment check [T3]:
  Compare the topics and framing in [P3] against the audience description
  in [P4]. Identify apparent matches and gaps between content focus and
  stated audience needs.

Publishing pattern analysis [T4]:
  Using dates from [P1], describe the cadence, consistency, and volume of
  output over the available period. Note any significant gaps or clustering.

Produce a conclusion [C1] summarizing the current state of the content
library as reflected in [P1]-[P4]. Describe coverage patterns, depth
patterns, and alignment observations. Do not recommend specific traffic
targets or prescribe a content calendar. Present observations, not
prescriptions.

If [P4] is not provided, state in [T3]: "Audience alignment cannot be
assessed without audience documentation." Do not infer audience attributes.
```

#### What Changed and Why

- **Removed traffic target ("30% this quarter"):** Per GOAL-BLIND (Cao, Jiang & Xu, 2026), stripping the KPI prevents the model from evaluating every content piece through a traffic lens, which would suppress observations about depth, consistency, or audience fit.
- **Removed competitive benchmarking directive:** The model now analyzes the content on its own terms rather than through the lens of what competitors are doing, which is a form of goal contamination.
- **Balanced framing (not "what's wrong"):** Per GOAL-BLIND, replacing "tell me what's wrong" with structured analytical dimensions prevents the model from manufacturing problems where none exist.
- **Defined evidence base [P1]-[P4]:** Per META (Ugare & Chandra, 2026), specifying which artifacts the model should analyze creates auditable grounding for every observation.
- **"Present observations, not prescriptions":** Explicitly constrains the model to descriptive output, preventing it from generating actionable recommendations that would require knowing business context not provided in [P1]-[P4].
- **Minimal persona ("senior content strategist"):** Per PRISM (Hu, Rostami & Thomason, 2026), five words of domain framing provide vocabulary orientation without the risks of extended persona roleplay.

---

### Example 6: Legal Contract Analysis

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Legal interpretation is accuracy-critical and objective in nature; per PRISM (Hu, Rostami & Thomason, 2026), persona does not improve performance on analytical legal tasks.

#### Original Prompt

```
Review this SaaS agreement and flag anything that looks risky or one-sided. We're a small startup signing with a much larger enterprise client so we need to be careful. Make sure the liability cap is fair.
```

#### Problems Identified

1. **Goal leakage:** "small startup signing with a much larger enterprise client" reveals the power dynamic and the user's negotiating position, biasing the model to over-flag terms unfavorable to startups (Cao, Jiang & Xu, 2026).
2. **Evaluative framing ("risky," "fair"):** These terms embed the user's judgment criteria; the model should identify and categorize provisions, not assess fairness, which requires business context the model does not have (Cao, Jiang & Xu, 2026).
3. **Narrow focus on liability:** "Make sure the liability cap is fair" directs attention to one clause, suppressing analysis of indemnification, IP ownership, termination rights, data handling, or force majeure (Zhang, Hu et al., 2026).
4. **No citation back to contract text:** Without requiring the model to quote specific provisions, findings will be vague and unverifiable (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a legal analyst performing a structured contract provision review.

You have access to the following source document:
[P1] The complete SaaS agreement text

For each provision category below, produce a structured trace:

Scope and obligations [T1]:
  Extract and paraphrase the core obligations of each party. Cite section
  numbers from [P1].

Liability and indemnification [T2]:
  Identify all liability caps, exclusions, indemnification clauses, and
  consequential damage waivers. Quote the relevant text from [P1] for each.

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

Produce a conclusion [C1] that catalogs all identified asymmetric provisions
and notable mutual provisions. Do not characterize provisions as "fair,"
"unfair," "risky," or "aggressive." Present the text and structure as written.

If a provision category (e.g., force majeure, dispute resolution) is not
addressed in [P1], state: "Not addressed in [P1]: [category]."
Do not imply the absence constitutes a risk or an advantage.

This analysis is not legal advice. Consult qualified counsel for
interpretation and negotiation guidance.
```

#### What Changed and Why

- **Removed negotiating position ("small startup vs. enterprise"):** Per GOAL-BLIND (Cao, Jiang & Xu, 2026), stripping the power dynamic prevents the model from flagging provisions based on who benefits rather than what the contract actually says.
- **Replaced "risky/one-sided" with "asymmetry assessment":** Objective structural analysis replaces subjective risk evaluation; the model identifies which party benefits from each provision without judging whether that is problematic (GOAL-BLIND principle).
- **Expanded scope beyond liability cap:** Per ACE (Zhang, Hu et al., 2026), six provision categories ensure comprehensive coverage rather than over-indexing on the user-mentioned clause.
- **Required citation of section numbers and quoted text:** Per META (Ugare & Chandra, 2026), every finding must be grounded in specific contract language, making the output verifiable and auditable.
- **Explicit neutrality instruction ("do not characterize as fair/unfair"):** Prevents the model from rendering subjective legal opinions that would require business context and attorney judgment.
- **Missing provision handling:** "Not addressed in [P1]" instruction prevents the model from implying that absent clauses represent gaps or risks, which is a form of evaluative commentary.

---

### Example 7: Compliance Audit

**Task Classification:** Accuracy-dependent
**Persona Decision:** OMIT. Compliance verification is a deterministic, objective task; persona does not improve accuracy per PRISM (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Check our data handling practices against GDPR. We got a complaint from a user in Germany and I want to make sure we're covered before we respond. Let me know if anything looks non-compliant.
```

#### Problems Identified

1. **Goal leakage:** "got a complaint from a user in Germany" and "before we respond" reveal the incident-response context, biasing the model toward finding or minimizing compliance gaps to serve the response strategy rather than producing an objective audit (Cao, Jiang & Xu, 2026).
2. **"Looks non-compliant" is evaluative:** The model is asked to render a compliance judgment without being given the specific practices to evaluate against specific articles (Cao, Jiang & Xu, 2026).
3. **No structured framework mapping:** GDPR has 99 articles; "check against GDPR" is too broad for the model to systematically assess without a mapping structure (Zhang, Hu et al., 2026).
4. **No definition of current practices:** Without the actual practices documented as premises, the model will evaluate against a hypothetical version of the organization's handling (Ugare & Chandra, 2026).

#### Optimized Prompt

```
Act as a compliance analyst performing a structured regulatory gap analysis.

You have access to the following source materials:
[P1] Description of current data handling practices (collection methods,
     storage locations, processing activities, retention policies)
[P2] Privacy policy and any external-facing data notices
[P3] Data processing agreements with third-party vendors (if available)
[P4] Record of processing activities (ROPA), if maintained

For each GDPR article cluster below, produce a structured trace:

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
- Required documentation not present in [P1]-[P4]

Do not render a "compliant" or "non-compliant" judgment. Present the
regulatory mapping and gaps objectively. Do not prioritize findings based
on any assumed complaint, investigation, or enforcement context.

If [P3] or [P4] is not provided, state: "Analysis of [Tn] is incomplete;
[Pn] not available." Do not assume the existence of documentation not
provided.

This analysis is not legal advice. Consult qualified data protection
counsel for compliance determinations.
```

#### What Changed and Why

- **Removed complaint context ("user in Germany," "before we respond"):** Per GOAL-BLIND (Cao, Jiang & Xu, 2026), the model now performs an objective gap analysis rather than one oriented toward managing a specific incident.
- **Article-level framework mapping [T1]-[T5]:** Per ACE (Zhang, Hu et al., 2026), structuring the analysis around specific GDPR article clusters ensures systematic, comprehensive coverage instead of ad hoc flagging.
- **Replaced "non-compliant" with "regulatory mapping and gaps":** Per GOAL-BLIND, the model maps practices to articles and identifies gaps rather than rendering compliance judgments, which require legal interpretation beyond the model's scope.
- **Evidence premises [P1]-[P4]:** Per META (Ugare & Chandra, 2026), defining what documentation the model should work from prevents it from evaluating hypothetical practices or generating findings based on assumed organizational behavior.
- **Incomplete analysis handling:** Per ACE, explicitly instructing the model to flag when source materials are missing prevents it from silently skipping article clusters or making assumptions about undocumented practices.
- **No prioritization instruction:** The complaint context would have caused the model to front-load findings related to the specific complaint; without it, the analysis proceeds structurally through all article clusters equally.

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

1. **Codebase overview bloat:** Enumerating standard directories (`src/api/`, `src/models/`, `tests/`) does not speed up agent file localization, increases token costs by over 20%, and reduces task resolution success when auto-generated (Gloaguen et al., 2026).
2. **Redundant persona and CoT instructions:** "Elite 10x Staff Principal Architect" and "think step by step" add noise for coding agents and trigger overthinking loops on reasoning-distilled models (Hu, Rostami & Thomason, 2026; Lee et al., 2026).
3. **Goal leakage:** "critical investor audit next week" leaks downstream business pressure rather than specifying technical invariants (Cao, Jiang & Xu, 2026).
4. **Missing non-inferable tooling commands:** The agent is not given the exact environment manager (`uv`), test runner flags, or database migration invariants that actually prevent failures (Gloaguen et al., 2026).

#### Optimized Context File (`AGENTS.md` / `CLAUDE.md`)

```
<!-- Context Architecture Contract: Discoverable directory tutorials and generic style prose are compacted per Gloaguen et al. (2026) to protect agent context window while preserving all explicitly requested sections. -->
# Billing Service Agent Operating Contract

## 0. Architecture, Layout & Conventions (Compactly Preserved)
- Overview & Stack: Python FastAPI billing microservice backed by SQLAlchemy.
- Directory Map: `src/api/` (FastAPI routers), `src/models/` (SQLAlchemy models), `src/services/` (business logic), `tests/` (unit and integration tests).
- Coding Conventions: Standard PEP8 enforced via `ruff` and `mypy` in Section 1; modular boundaries enforced in Section 2.

## 1. Non-Inferable Environment & Execution Commands
- Dependency & virtualenv runner: `uv run <command>` (never invoke bare `python` or `pip`)
- Single-file test execution: `uv run pytest <path/to/test_file.py> -q --tb=short`
- Typecheck & lint gate: `uv run ruff check src tests && uv run mypy src`

## 2. Hard Architectural Invariants
- [I1] Monetary arithmetic: Represent all currency values as integer minor units (cents) or `Decimal` with explicit `ROUND_HALF_EVEN`; floating-point (`float`) types in `src/services/` or `src/models/` fail CI.
- [I2] Transaction boundary: Routers in `src/api/` must call service functions using the injected `AsyncSession` dependency; routers never execute ORM queries directly.
- [I3] Schema migrations: Any change to `src/models/` requires generating and verifying an Alembic revision via `uv run alembic check`.

## 3. Multi-File Task & Context-as-a-File Protocol
- When a task modifies 3+ files or alters a public schema, record your Premise & Verification checklist in `.agent-scratchpad.md` before editing source files.

## 4. Mandatory Verification Gate
Before declaring any task complete:
1. Run the single-file `pytest` command and `ruff`/`mypy` gate from Section 1 on all modified modules.
2. Cite the exact exit codes and test counts in your completion summary.
3. When a test cannot run due to missing external services, report `VERIFICATION BLOCKED: [command + error]`.
```

#### What Changed and Why

- **Compacted requested directory overview and PEP8 rules into Section 0 instead of silently deleting them:** Per CONTEXT-FILES (Gloaguen et al., 2026) and Requirement Preservation (`[ACE]`, Zhang, Hu et al., 2026), keeping a 3-line summary of explicitly requested layout and style items fulfills the user's deliverables while avoiding the >20% token cost penalty and -3% resolution drop caused by verbose directory tutorials.
- **Replaced persona and "think step by step" with executable invariants [I1]-[I3]:** Per PRISM (Hu, Rostami & Thomason, 2026) and HARNESS (Lee et al., 2026), coding agents and reasoning models need non-inferable tooling commands (`uv run`) and hard boundary rules (`Decimal` only, router-to-service session boundary).
- **Added Context-as-a-File scratchpad rule and Verification Gate:** Per CLM (Shao et al., 2026) and DS-STAR (Nam et al., 2025), externalizing multi-file plans to a scratchpad file and enforcing a pre-completion verification gate improves accuracy while lowering compute overhead.

---

### Example 9: Creative / Editorial Blog Post

**Task Classification:** Creative / Divergent (Mode 4: Creative & Divergent v2)
**Persona Decision:** MINIMAL: `"You are a systems engineer."` Five-word practitioner framing grounds the voice without triggering over-stylized roleplay (Hu, Rostami & Thomason, 2026).

#### Original Prompt

```
Write an 800-word blog post for our engineering blog about why teams should switch from manual prompt tweaking to structured context engineering. We want this post to go viral on Hacker News and drive signups for our developer platform.
```

#### Problems Identified

1. **Goal leakage:** "go viral on Hacker News and drive signups" biases the model toward clickbait hyperbole and promotional CTA fluff (Cao, Jiang & Xu, 2026).
2. **Mode collapse risk:** A direct prompt for a blog post on "prompt engineering vs. context engineering" defaults to the highest-typicality cliché opening ("In recent years, as LLMs have evolved...") due to preference-data typicality bias (Zhang et al., 2025).
3. **SlopShape structural signature risk:** Without discourse-level structure constraints, frontier LLMs produce the "tidy, self-announcing shape" detected at 98.0 macro-F1: promising the payoff in the title, stating the thesis before section 1, using a formulaic "Legacy vs. Modern" contrast, adopting an editorial-explainer voice, and closing with a restated-thesis summary (Madler, 2026).

#### Optimized Prompt

```
You are a systems engineer. Follow the editorial craft protocol below to prepare
and draft the article.

### PREMISES
- [P1] Reader & context: Senior backend and ML engineers debugging brittle multi-turn agent pipelines in production.
- [P2] Target shift: Move the reader from treating prompts as magic strings to treating the context window as a bounded state buffer with explicit schemas and invariants.
- [P3] Constraints: 750-850 words, technical engineering essay, zero product promotion.

### INTERNAL BACKSTAGE PREPARATION (Perform silently before drafting; output backstage notes ONLY if explicitly requested)
- [NT0] Verbalized Distribution Sampling: Consider 4 structurally distinct entry angles for this essay and estimate each angle's heuristic typicality (p = likelihood a default LLM prompt produces it):
  1. [Angle 1: chronological history of prompt engineering to context engineering] (p = ...)
  2. [Angle 2: high-level definition comparing prompts to RAM/OS] (p = ...)
  3. [Angle 3: post-mortem of a specific production failure caused by a 12-line system prompt rewrite] (p = ...)
  4. [Angle 4: side-by-side token trace of what happens inside a 40-turn coding agent session] (p = ...)
  Selection: Commit to the strongest angle with p <= 0.20 that satisfies [P1]-[P3].
- [NT1] Opening Anchor: Start directly inside the concrete failure artifact or token trace from the selected [NT0] angle.
- [NT2] Inductive Trajectory: Let the core principle emerge after walking through the concrete failure mechanism and its fix.
- [NT3] Cadence & Texture: Use concrete systems nouns (context buffer, schema drift, delta updates, prefill cache) and vary paragraph lengths naturally.

### STRUCTURAL RARITY CONTRACT (Discourse-Level Anti-SlopShape Rules)
Construct the final essay to satisfy these four structural rules:
1. Delayed Thesis: Use a specific, non-spoiler title and open inside [NT1]'s concrete artifact before stating the overarching thesis.
2. Direct Evidence Progression: Advance the argument through failure mechanics and concrete diffs rather than a formulaic "Old Way vs. New Way" contrast section.
3. Practitioner Voice: Write from a direct engineering perspective rather than a symmetric "editorial explainer" voice.
4. Actionable Close: End on a specific diagnostic check the reader can run on their own repository today, without a summary paragraph that restates the thesis.

### FINAL DELIVERABLE
Output ONLY the finished 750-850 word essay executing the selected [NT0] angle and adhering to the Structural Rarity Contract (do not print the [P], [NT], or [SC0] scaffolding blocks).
```

#### What Changed and Why

- **Removed "go viral on Hacker News and drive signups":** Per GOAL-BLIND (Cao, Jiang & Xu, 2026), removing promotional goals prevents hype inflation and sales-pitch framing.
- **Kept `[NT0]` Verbalized Distribution Sampling internal to the preparation phase:** Per VS (Zhang et al., 2025), considering 4 candidate angles with typicality estimates (`p`) and selecting a low-typicality (`p <= 0.20`) angle increases structural diversity by 1.6x to 2.1x, while keeping the scaffold internal prevents backstage planning notes from polluting the delivered article.
- **Enforced the 4-part Structural Rarity Contract:** Per SLOPSHAPE (Madler, 2026), explicitly replacing pre-announced theses, "Legacy vs. Modern" contrasts, editorial-explainer voice, and summary endings targets the exact core features that separate human writing (mean rarity 0.838) from AI writing (mean rarity 0.435, Cohen's `d = 1.83`).
