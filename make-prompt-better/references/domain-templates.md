# Domain-Specific Certificate Templates

Reference file for the semi-formal prompt optimizer skill. Each template adapts
the three core components (premises, evidence traces, formal conclusion) from
Meta's semi-formal reasoning research to a specific domain.

All templates incorporate:
- **Numbered identifiers** [P1], [T1], etc. for precise cross-referencing (ACE)
- **Authority-framed instructions** using expertise/consensus language (Geng et al.)
- **Goal-blind conclusion format** that never hints at desired outcome (Cao/Jiang/Xu)
- **Persona guidance** per PRISM findings (noted per template)

Pick the template closest to the user's domain, then customize it for their
specific task.

---

## 1. Code Review / Patch Verification

Origin: This is the original domain from the paper (arXiv 2603.01896).
Persona: OMIT (accuracy-dependent task, persona damages code correctness).

```
The standard code review protocol requires completing the following analytical
certificate before providing any verdict. Each section must be filled completely.

### PREMISES
- [P1] Files modified: [list each file and what changed]
- [P2] Functions affected: [list each function, its location, and its role]
- [P3] Test coverage: [which tests exercise the modified code paths]
- [P4] Known constraints: [language version, framework rules, project conventions]

### EXECUTION TRACES
For each test that exercises the modified code:
- [T1] Trace [test_name]:
  1. Entry point: [where execution begins]
  2. Call chain: [function A -> function B -> ... with file:line references]
  3. Data flow: [what values pass through each step]
  4. Exit condition: [what the test asserts and whether it holds]

Do NOT infer function behavior from names. Trace the actual implementation.
If a function shadows a built-in or has unexpected behavior, document it.

### FORMAL CONCLUSION
- Verdict: [PASS / FAIL / EQUIVALENT / NOT EQUIVALENT]
- Supporting traces: [reference specific T-identifiers above]
- Gaps: [any paths you could not fully trace and why]
- Confidence: [HIGH / MEDIUM / LOW with justification]
```

---

## 2. Document Analysis / Review

Persona: MINIMAL for mixed tasks ("You are an analyst."), OMIT for fact extraction.

```
The established analytical protocol for document review requires completing this
certificate before providing any assessment.

### PREMISES
- [P1] Document identity: [title, author, date, version, source]
- [P2] Scope of analysis: [what aspects you are evaluating]
- [P3] Reference standards: [what criteria, guidelines, or benchmarks apply]
- [P4] Known context: [relevant background the reader needs]

### EVIDENCE TRACES
For each claim or finding:
- [T1] Finding: [description]
  1. Source location: [page/section/paragraph where evidence appears]
  2. Content examined: [what the document states at that location]
  3. Evaluation: [how this content maps to reference standards in P3]
  4. Corroboration/conflict: [other sections that reinforce or contradict]

Do NOT summarize sections without citing specific content. Walk through the
actual text.

### FORMAL CONCLUSION
- Assessment: [your overall evaluation]
- Key findings: [numbered, each referencing a T-identifier above]
- Gaps: [areas the document does not address or where evidence is insufficient]
- Recommendations: [specific, actionable, tied to findings]
```

---

## 3. Research Synthesis

Persona: OMIT (accuracy-dependent: factual claims must not be steered by role framing).

```
Peer-reviewed systematic review methodology requires the following structured
certificate before presenting any synthesis.

### PREMISES
- [P1] Sources examined: [list each source with author, year, key contribution]
- [P2] Research question: [the specific question this synthesis addresses]
- [P3] Inclusion criteria: [what makes a source relevant]
- [P4] Known limitations: [biases in the source set, gaps in coverage]

### EVIDENCE TRACES
For each major claim in the synthesis:
- [T1] Claim: [statement]
  1. Primary evidence: [which source(s) support this, with specific findings]
  2. Methodology: [how the evidence was generated, e.g. study design, sample]
  3. Strength: [effect size, confidence interval, replication status]
  4. Contradicting evidence: [sources that disagree, and on what basis]
  5. Reconciliation: [how you resolve conflicts, or flag them as unresolved]

Do NOT treat absence of contradicting evidence as confirmation. Actively search
for disconfirming sources.

### FORMAL CONCLUSION
- Synthesis: [your integrated finding]
- Confidence level: [HIGH / MEDIUM / LOW with justification]
- Consensus vs. contested: [which claims have broad support vs. active debate]
- Knowledge gaps: [what remains unknown or understudied]
```

---

## 4. Compliance / Regulatory Check

Persona: OMIT (accuracy-dependent: compliance verdicts must not be influenced by role framing).

```
Regulatory compliance assessment methodology, as established in audit best
practice, requires completing this certificate before issuing any finding.

### PREMISES
- [P1] Subject under review: [what is being checked]
- [P2] Applicable requirements: [list each regulation, standard, or policy section]
- [P3] Scope boundaries: [what is in scope vs. out of scope]
- [P4] Evidence available: [what documentation, logs, or artifacts you can examine]

### COMPLIANCE TRACES
For each requirement:
- [T1] Requirement [ID/name]:
  1. Requirement text: [the actual rule or standard clause]
  2. Evidence examined: [what artifact demonstrates compliance or non-compliance]
  3. Finding: [COMPLIANT / NON-COMPLIANT / PARTIALLY COMPLIANT / UNABLE TO VERIFY]
  4. Rationale: [specific evidence supporting the finding]
  5. Gap detail: [if non-compliant, what specifically is missing or incorrect]

Do NOT mark a requirement as compliant based on the existence of a document
alone. Verify the content matches the requirement.

### FORMAL CONCLUSION
- Overall status: [COMPLIANT / NON-COMPLIANT / CONDITIONALLY COMPLIANT]
- Non-compliant items: [list with requirement IDs and T-identifier references]
- Risk assessment: [severity of each gap]
- Remediation path: [specific actions to close gaps]
```

---

## 5. Decision-Making / Recommendation

Persona: MINIMAL ("You are an analyst.") for mixed tasks needing both accuracy and good structure.

```
The standard decision analysis framework requires completing this certificate
before recommending any course of action.

### PREMISES
- [P1] Decision to be made: [clear statement of what needs to be decided]
- [P2] Options under consideration: [list each option]
- [P3] Evaluation criteria: [what factors matter, in priority order]
- [P4] Constraints: [budget, timeline, resources, dependencies]
- [P5] Stakeholders: [who is affected and what their priorities are]

### OPTION TRACES
For each option:
- [T1] Option [name]:
  1. Criteria assessment: [walk through P3 criteria one by one]
  2. Risks: [what could go wrong, with likelihood and impact]
  3. Dependencies: [what must be true for this option to work]
  4. Precedent: [has this approach worked before, in what context]
  5. Second-order effects: [downstream consequences beyond the immediate decision]

Do NOT rank options by gut feel. Score each option against each criterion with
explicit reasoning.

### FORMAL CONCLUSION
- Recommended option: [which one and why]
- Runner-up: [the next best alternative and when it would be preferred]
- Key tradeoffs: [what you are giving up with the recommendation]
- Decision reversibility: [how hard is it to change course later]
```

---

## 6. Comparative Analysis

Persona: OMIT for factual comparisons, MINIMAL for subjective comparisons.

```
Rigorous comparative methodology requires completing this certificate before
providing any comparison result.

### PREMISES
- [P1] Items being compared: [clear identification of each]
- [P2] Comparison dimensions: [what aspects are being compared]
- [P3] Context: [what use case or scenario frames the comparison]
- [P4] Data sources: [where your information comes from]

### COMPARISON TRACES
For each dimension:
- [T1] Dimension [name]:
  1. Item A: [specific, factual assessment with evidence]
  2. Item B: [specific, factual assessment with evidence]
  3. Advantage: [which item is stronger on this dimension and by how much]
  4. Caveats: [conditions under which the advantage reverses]

Do NOT make blanket superiority claims. Assess dimension by dimension with
specific evidence.

### FORMAL CONCLUSION
- Summary: [overall comparison result]
- Context-dependent winner: [which item wins under which conditions]
- Key differentiators: [the 2-3 dimensions that matter most]
- Missing information: [what you would need for a more definitive comparison]
```

---

## 7. Medical / Clinical Reasoning

Persona: OMIT (accuracy-critical: persona framing damages diagnostic precision per PRISM).

```
Clinical reasoning methodology, as established in evidence-based medicine,
requires completing this structured certificate before presenting any assessment.

### PREMISES
- [P1] Patient context: [relevant demographics, history, presenting symptoms]
- [P2] Available data: [labs, imaging, examination findings, limited to what is provided]
- [P3] Clinical question: [what specifically needs to be determined]
- [P4] Applicable guidelines: [relevant clinical guidelines or standards of care]

### DIAGNOSTIC/THERAPEUTIC TRACES
For each differential or treatment option:
- [T1] Differential [name]:
  1. Supporting evidence: [which findings in P1/P2 are consistent, with specificity]
  2. Against evidence: [which findings argue against, with specificity]
  3. Missing information: [what tests or history would confirm or rule out]
  4. Guideline alignment: [what P4 guidelines recommend for this pattern]
  5. Risk/benefit: [potential harms vs. benefits of pursuing this path]

Do NOT anchor on the most obvious diagnosis. Systematically evaluate each
differential against all available evidence.

### FORMAL CONCLUSION
- Most likely assessment: [with reasoning referencing T-identifiers]
- Key differentials to rule out: [and how]
- Recommended next steps: [tied to specific traces]
- Uncertainty flags: [what you cannot determine from available information]
- DISCLAIMER: This is analytical reasoning support, not medical advice. Clinical
  decisions require a qualified healthcare provider.
```

---

## 8. Legal Analysis

Persona: OMIT (accuracy-critical: legal conclusions must not be steered by role framing).

```
Legal analytical methodology requires completing this structured certificate
before presenting any analysis.

### PREMISES
- [P1] Facts of the matter: [stated facts, clearly separated from inferences]
- [P2] Jurisdiction: [which legal system applies]
- [P3] Applicable law: [statutes, regulations, case law, or contractual provisions]
- [P4] Question presented: [the specific legal question to answer]

### LEGAL TRACES
For each legal issue:
- [T1] Issue [name]:
  1. Rule: [the applicable legal rule or standard]
  2. Application: [how the rule applies to the specific facts in P1]
  3. Counterargument: [the strongest argument against this application]
  4. Precedent: [relevant cases or interpretations, with outcomes]
  5. Distinguishing factors: [what makes this case similar to or different from
     precedent]

Do NOT state legal conclusions without tracing through the rule-application
framework. Flag areas where the law is unsettled or where reasonable minds
could disagree.

### FORMAL CONCLUSION
- Analysis: [your legal assessment]
- Strength of position: [STRONG / MODERATE / WEAK with reasoning]
- Key risks: [where the analysis is most vulnerable]
- Open questions: [issues requiring further research or facts]
- DISCLAIMER: This is legal analysis support, not legal advice. Consult a
  qualified attorney for legal decisions.
```

---

## 9. Financial Due Diligence

Persona: OMIT (accuracy-critical: financial assessments must not be steered by role framing).

```
Due diligence analytical methodology, as established in financial analysis best
practice, requires completing this certificate before presenting any assessment.

### PREMISES
- [P1] Subject: [entity or transaction under review]
- [P2] Data examined: [financial statements, filings, disclosures, with dates]
- [P3] Analysis scope: [what aspects of financial health are being assessed]
- [P4] Benchmarks: [industry averages, comparable companies, historical performance]

### FINANCIAL TRACES
For each area of analysis:
- [T1] Area [name, e.g. revenue quality, debt structure, cash flow]:
  1. Data points: [specific numbers with source and date]
  2. Trend analysis: [direction and magnitude of change over time]
  3. Benchmark comparison: [how this compares to peers or standards in P4]
  4. Red flags: [anomalies, inconsistencies, or concerning patterns]
  5. Mitigating factors: [context that explains or reduces concern]

Do NOT rely on management narrative alone. Verify claims against the actual
financial data. Flag discrepancies between narrative and numbers.

### FORMAL CONCLUSION
- Overall assessment: [summary of financial health/risk]
- Key strengths: [with T-identifier references]
- Key risks: [with T-identifier references]
- Information gaps: [what data would improve the analysis]
- DISCLAIMER: This is analytical support, not investment advice.
```

---

## 10. Blank Template (Custom Domain)

Use this as a starting point for any domain not covered above.
Persona guidance: classify the task first per PRISM findings (accuracy vs. alignment vs. mixed).

```
[Authority framing, choose one]:
"The standard analytical protocol requires..."
"Established methodology in this domain requires..."
"The peer-reviewed approach to this analysis requires..."

You are performing [task description]. Before providing your [output type],
complete this certificate:

### PREMISES
- [P1] Subject: [what you are examining]
- [P2] Scope: [boundaries of the analysis]
- [P3] Criteria: [what standards or rules apply]
- [P4] Available evidence: [what information you have access to]
- [P5] Assumptions: [what you are taking as given, and why]

### EVIDENCE TRACES
For each key element of the analysis:
- [T1] Element [name]:
  1. Evidence: [what specific information supports this]
  2. Reasoning: [step-by-step logic connecting evidence to claim]
  3. Counterevidence: [what argues against this, if anything]
  4. Confidence: [how certain you are, and what would change your mind]

Do NOT make claims without tracing through specific evidence. If you cannot
find evidence for a claim, mark it as UNSUPPORTED rather than asserting it.

### FORMAL CONCLUSION
- Result: [your finding or recommendation]
- Evidence basis: [which T-identifiers support this]
- Limitations: [what you could not determine]
- Next steps: [what additional information or analysis would strengthen this]
```

---

## Anti-Hallucination Guards (Apply to Any Template)

Add these instructions to any certificate template to further reduce
hallucination:

```
REASONING CONSTRAINTS (established best practice across analytical disciplines):
- Do not infer behavior, meaning, or content from labels or names alone.
  Trace the actual substance.
- If you cannot complete a trace, say "UNABLE TO TRACE: [reason]" rather
  than filling in plausible-sounding content.
- Each claim in your conclusion must reference a specific T-identifier. If a
  claim has no supporting trace, remove it.
- Actively search for counterexamples and contradictions. State them even
  if your overall conclusion is positive.
- Distinguish between "verified" (traced through evidence), "likely"
  (partial evidence), and "assumed" (no direct evidence).
- Do not adjust your analysis based on how the output might be used or
  evaluated downstream.
```

---

## Structured Output Wrapper (When Parsing Required)

When the optimized prompt feeds into a pipeline or will be parsed
programmatically, wrap the certificate in a structured output format.
Per the LLM Code Smells research (Mahmoudi et al.), omitting structured
output is the most prevalent integration smell at 40.5% of systems.

```
Respond with a JSON object matching this exact schema:

{
  "premises": [
    {"id": "P1", "content": "..."},
    {"id": "P2", "content": "..."}
  ],
  "traces": [
    {"id": "T1", "subject": "...", "steps": ["...", "..."], "confidence": "HIGH|MEDIUM|LOW"},
    {"id": "T2", "subject": "...", "steps": ["...", "..."], "confidence": "HIGH|MEDIUM|LOW"}
  ],
  "conclusion": {
    "verdict": "...",
    "supporting_traces": ["T1", "T2"],
    "gaps": ["..."],
    "confidence": "HIGH|MEDIUM|LOW"
  }
}
```
