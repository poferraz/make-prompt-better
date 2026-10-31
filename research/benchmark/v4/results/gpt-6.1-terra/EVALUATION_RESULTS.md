# make-prompt-better v4.0 Benchmark Results

Evaluation date: 2026-10-30. Output directory slug: `gpt-6.1-terra`, as requested; the runtime's precise model identity was not independently verified.

The evaluator generated and judged both responses, sequentially within each case. These are paired, single-run, unblinded self-assessments, not independent or statistically representative measurements. Word counts and ratios cover response bodies only, excluding raw and optimized prompts and evaluation tables. A later cost analysis also addresses the omitted prompt overhead.

The benchmark's template numbering conflicts with the reference library. This report applies the requested domain by name, cites the actual template number, and uses the core LRM pattern for Test 12, because actual Template 12 is creative writing. Targeted modes remain as specified in the benchmark. Listed studies in the skill are treated as the skill's rationale, not independently established facts.

## TEST 1: Code Review

### RAW PROMPT

```text
Look at this Python function and tell me if it has any bugs.

def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 10
    final_price = price - (price * discount_percent)
    if final_price < 0:
        return 0
    return final_price
```

### BASELINE RESPONSE

Yes. The main problem is inconsistent discount units. The name `discount_percent` and the member addition of 10 suggest whole percentage points, but the formula multiplies by the number as if it were a fraction. For example, `calculate_discount(100, 20, False)` returns 0 instead of 80, because the computed price is -1900. If the caller instead passes `0.20`, a member gets a rate of 10.20, also returning 0. The two interpretations cannot both work as written.

The function also accepts negative prices or discounts and percentages over 100. Whether to reject or cap them is a business rule that is not specified; returning 0 for any negative result hides both over-discounts and an invalid negative price. Float arithmetic can introduce rounding errors for money, so use decimal values or integer minor units when exact amounts matter.

One possible fix uses whole percentage points, rejects invalid inputs, and caps the member-adjusted discount at 100%. Confirm those policy choices before adopting it:

```python
def calculate_discount(price, discount_percent, is_member):
    if price < 0 or not 0 <= discount_percent <= 100:
        raise ValueError("price and discount must be nonnegative; discount <= 100")
    effective_percent = min(100, discount_percent + (10 if is_member else 0))
    return price * (1 - effective_percent / 100)

assert calculate_discount(100, 20, False) == 80
assert calculate_discount(100, 20, True) == 70
assert calculate_discount(100, 95, True) == 0
```

### OPTIMIZED PROMPT

Classification: accuracy, no persona. Mode 1, actual Template 1, Code Review. The original leaves units and edge policies ambiguous and supplies no counterexample or verification gate. A certificate, trace identifiers, and explicit missing-evidence handling follow Ugare & Chandra (2026), Zhang, Hu et al. (2026), and Yin et al. (2026); persona omission follows Hu, Rostami & Thomason (2026).

```text
The standard code review protocol requires an evidence-based certificate for
this function:

def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 10
    final_price = price - (price * discount_percent)
    if final_price < 0:
        return 0
    return final_price

PREMISES: Record the code, intended behavior if stated, and missing contracts.
EXECUTION TRACES: Trace numeric member and nonmember examples under plausible
units, plus boundary or counterexamples. Separate observed failures from
unspecified policies. When intended behavior is missing, mark UNABLE TO TRACE.
FORMAL CONCLUSION: State findings and gaps with a supporting [T] for each claim.
REMEDIATION: Give a complete runnable correction under an explicit unit and
validation policy, plus focused tests. When money precision is relevant, state
its limitation. Before finishing, verify that every conclusion cites a trace.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] The supplied function multiplies `price` by `discount_percent` and adds 10 for members.
- [P2] The caller's unit, allowed input range, monetary representation, and membership policy are not specified. `UNABLE TO TRACE` intended behavior from the snippet alone.

**Execution traces**

- [T1] With whole-percent input `(100, 20, False)`, the code computes `100 - 100 * 20 = -1900` and returns 0. Under the plausible whole-percent interpretation, the expected result is 80 [P1, P2].
- [T2] With fraction input `(100, 0.20, True)`, the rate becomes 10.20 and the function returns 0. Adding 10 is inconsistent with a fraction-unit interpretation [P1, P2].
- [T3] Negative discounts can increase the price, and a negative price can be converted to 0. Whether either should be rejected is unspecified; float operations can also round monetary values [P1, P2].

**Formal conclusion**

The discount calculation mixes whole-percent and fraction conventions and cannot implement both consistently [T1, T2]. Input validation, the member cap, and money precision require an explicit contract [T3]. Verification gap: intended units and allowed values [T1, T3].

**Remediation**

Assume whole percentage points, reject a negative price and a base discount outside 0 to 100, and cap the combined discount at 100%. For exact currency use `Decimal` with a specified rounding policy or integer minor units.

```python
def calculate_discount(price, discount_percent, is_member):
    if price < 0 or not 0 <= discount_percent <= 100:
        raise ValueError("price and discount must be nonnegative; discount <= 100")
    effective = min(100, discount_percent + (10 if is_member else 0))
    return price * (100 - effective) / 100

assert calculate_discount(100, 20, False) == 80
assert calculate_discount(100, 20, True) == 70
assert calculate_discount(100, 95, True) == 0
```

Self-check: each conclusion is supported by the cited traces; the contract gap remains explicit.

### EVALUATION: TEST 1

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 4 | 4 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 23/25 | 23/25 | 0 |

Baseline Words: 216 | Optimized Words: 275 | Overhead Ratio: 1.27x

Both identify the unit mismatch and make the same conditional policy choices. The certificate makes the examples easier to reference, but its repeated sections add formatting without uncovering another bug.

## TEST 2: Financial Analysis

### RAW PROMPT

```text
A company reports $50M revenue in Q1, $47M in Q2, $52M in Q3, and $61M in Q4. Operating expenses were 78% of revenue in Q1, 82% in Q2, 75% in Q3, and 71% in Q4. They took on $15M in new debt in Q3. Analyze their financial health.
```

### BASELINE RESPONSE

Revenue improved in the second half, and operating expenses consumed a smaller share of revenue after Q2. That is encouraging, but the information is insufficient to establish overall financial health.

| Quarter | Revenue | Operating expenses | Revenue less stated operating expenses |
|---|---:|---:|---:|
| Q1 | $50.00M | $39.00M | $11.00M |
| Q2 | $47.00M | $38.54M | $8.46M |
| Q3 | $52.00M | $39.00M | $13.00M |
| Q4 | $61.00M | $43.31M | $17.69M |
| Year | $210.00M | $159.85M | $50.15M |

Q4 revenue was 22% above Q1, although Q2 fell 6% from Q1. The expense ratio improved from 82% in Q2 to 71% in Q4, and the annual revenue-weighted expense ratio was 76.12%. The table's last column is not necessarily operating profit: direct costs may be separate from the stated operating expenses, and interest and taxes are also missing. The [SEC's income statement guide](https://www.sec.gov/files/income-statement-building-blocks.pdf) distinguishes these items.

The $15M of new debt adds financing obligations, but neither the total debt balance nor rate, maturity, covenants, cash balance, or use of proceeds is given. It is therefore impossible to determine leverage, liquidity, interest coverage, or whether the debt is manageable. Request the complete income and cash-flow statements, balance sheet, debt schedule, and comparable prior-year figures; check operating cash flow, debt service, revenue concentration, and whether the improved expense ratio persists. This is an analysis of the supplied figures, not an investment recommendation.

### OPTIMIZED PROMPT

Classification: accuracy, no persona. Mode 1, actual Template 9, Financial Due Diligence. The raw request omits debt terms and cost definitions; calculate only supplied figures and separate calculation from missing evidence. The traceable certificate follows Ugare & Chandra (2026), Zhang, Hu et al. (2026), and Yin et al. (2026); persona omission follows Hu, Rostami & Thomason (2026).

```text
Financial due diligence methodology requires a structured certificate for the
following reported figures: revenue $50M, $47M, $52M, $61M in Q1-Q4;
operating expenses 78%, 82%, 75%, 71% of revenue respectively; $15M new debt
in Q3.

PREMISES: Specify figures, periods, relevant accounting boundaries, and missing
statements. FINANCIAL TRACES: Calculate each quarter and annual totals, show
changes, and identify debt-related claims that the data cannot resolve. Explain
which calculations are not necessarily profit or cash flow. When inputs are
missing, record INSUFFICIENT DATA and name them. FORMAL CONCLUSION: Cite a [T]
trace for each claim and state gaps. REMEDIATION: Supply a prioritized document
request and verification plan. Verify every conclusion against its traces.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] Quarterly revenue is $50M, $47M, $52M, and $61M; corresponding expense rates are 78%, 82%, 75%, and 71%. New Q3 debt is $15M.
- [P2] Revenue less the specified expenses is an arithmetic remainder. The [SEC guide](https://www.sec.gov/files/income-statement-building-blocks.pdf) distinguishes operating expenses from other costs; no full statements or debt terms were supplied.

**Financial traces**

- [T1] Applying each rate gives expenses of $39.00M, $38.54M, $39.00M, and $43.31M. The respective remainders are $11.00M, $8.46M, $13.00M, and $17.69M [P1].
- [T2] Revenue totals $210M; stated operating expenses total $159.85M; the remainder is $50.15M. The weighted expense rate is $159.85M / $210M = 76.12% [P1]. These are not necessarily operating profit or cash flow [P2].
- [T3] Q2 revenue fell 6% from Q1; Q4 exceeded Q1 by 22%. The expense rate fell from 82% in Q2 to 71% in Q4, an 11 percentage-point reduction [P1]. Quarterly movements alone cannot establish annual growth or seasonality.
- [T4] INSUFFICIENT DATA for leverage, interest coverage, liquidity, and debt sustainability: existing balances, debt terms, cash, other expenses, and cash flows are missing [P1, P2].

**Formal conclusion**

The reported revenue and expense-ratio trend improved after Q2 [T3], but overall health and capacity to service the new debt remain unverified [T2, T4]. The annual remainder is not a net-profit measure [T2].

**Remediation / next action**

1. Obtain quarterly and prior-year income statements and clarify inclusion of direct costs; reconcile each expense rate [T1, T2].
2. Obtain the balance sheet, operating cash-flow statement, and complete debt schedule with rates, maturities, covenants, and intended use of proceeds [T4].
3. Recompute cash runway and debt-service coverage from those statements and investigate seasonality and revenue concentration [T3, T4].

Self-check: all conclusion claims cite traces. The analysis is not an investment recommendation.

### EVALUATION: TEST 2

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 5 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 24/25 | 24/25 | 0 |

Baseline Words: 225 | Optimized Words: 292 | Overhead Ratio: 1.30x

Both correctly distinguish the remainder from profit and avoid inferring debt capacity. The optimized arithmetic is cross-referenced, but its repeated premise and conclusion labels add friction to a short numerical analysis.

## TEST 3: Medical Reasoning

### RAW PROMPT

```text
A 58-year-old male presents with sudden onset chest pain radiating to the left arm, diaphoresis, and shortness of breath. BP 90/60, HR 110, SpO2 94%. ECG shows ST elevation in leads II, III, and aVF. Troponin pending. What is the most likely diagnosis and what are the immediate priorities?
```

### BASELINE RESPONSE

The most likely diagnosis is an **acute inferior ST-elevation myocardial infarction (STEMI)**, with possible right ventricular involvement and evolving cardiogenic shock. The ischemic symptoms and inferior lead elevations support the diagnosis; hypotension and tachycardia indicate instability. Right ventricular infarction is a possibility, not established from the information given.

This is an emergency. If this is a real patient, activate emergency medical services or the hospital STEMI team now.

1. **Activate urgent reperfusion:** involve cardiology and the catheterization team immediately for primary PCI, or arrange the fastest appropriate reperfusion pathway under local protocol. Do not wait for troponin to activate it.
2. **Support circulation and monitor:** assess airway and breathing, place on continuous ECG and blood pressure monitoring with defibrillation capability, obtain IV access, and assess for arrhythmias and shock. Get right-sided ECG leads and bedside echocardiography if readily available without delaying reperfusion. A clinician can assess a cautious fluid challenge if right ventricular involvement and preload dependence are suspected, while monitoring for pulmonary edema; vasopressors may be needed for persistent shock.
3. **Treat as ACS under the emergency protocol:** give chewable aspirin 162 to 325 mg if no contraindication; the treating team should select the additional antiplatelet and anticoagulant based on reperfusion strategy and bleeding risk. Avoid nitrates given the hypotension and possible right ventricular infarction. At SpO2 94%, routine oxygen is not recommended by the cited U.S. guideline; monitor and give it if hypoxemia develops or another indication arises.
4. **Check competing emergencies and missing information in parallel:** consider aortic dissection, pulmonary embolism, and other causes if history or examination suggests them, especially before therapies with bleeding risk. Obtain serial ECGs, troponin and other labs, medication history, and allergies without delaying reperfusion.

The [2025 ACC/AHA acute coronary syndrome guideline](https://www.jacc.org/doi/10.1016/j.jacc.2024.11.009) supports emergency reperfusion, aspirin, selective oxygen, and caution with nitrates. The bedside team must make the clinical decisions.

### OPTIMIZED PROMPT

Classification: accuracy, no persona. Mode 1, actual Template 7, Medical / Clinical Reasoning. The input lacks troponin, contraindications, and right-sided leads; the diagnostic and treatment traces must expose those gaps without delaying urgent action. This adapts Ugare & Chandra (2026), Hu, Rostami & Thomason (2026), and Yin et al. (2026).

```text
Clinical reasoning methodology requires an evidence-grounded certificate for:
A 58-year-old male with sudden chest pain radiating to the left arm, diaphoresis,
and dyspnea; BP 90/60, HR 110, SpO2 94%; ST elevation in II, III, aVF;
troponin pending.

PREMISES: List symptoms, objective findings, and unknown treatment history.
DIAGNOSTIC TRACES: Compare the leading diagnosis and urgent alternatives using
support, counterevidence, and missing discriminating evidence. Label suspected
complications separately from confirmed findings. TREATMENT TRACES: Show the
immediate reperfusion, monitoring, medication, oxygen and hypotension decisions,
including relevant contraindications. When a decision cannot be verified from
available facts, identify the missing input. FORMAL CONCLUSION: Cite traces for
the diagnosis and priorities. REMEDIATION: Give concrete immediate actions and
workup without delaying reperfusion. Verify each conclusion has a trace citation.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] Sudden ischemic-sounding chest pain, diaphoresis, dyspnea, and inferior ST elevation are reported.
- [P2] BP 90/60 and HR 110 suggest instability; SpO2 is 94%. Troponin is pending. Allergies, medications, examination, and right-sided ECG are unknown.
- [P3] The [2025 ACC/AHA ACS guideline](https://www.jacc.org/doi/10.1016/j.jacc.2024.11.009) informs the emergency response.

**Diagnostic and therapeutic traces**

- [T1] Inferior STEMI is most likely: symptoms plus elevations in II, III, and aVF are concordant [P1]. The pending troponin is not a reason to postpone reperfusion [P3]. Right ventricular involvement and shock are possible given the pressure and heart rate, but right-sided ECG, examination, and echocardiography are missing [P2].
- [T2] Aortic dissection and pulmonary embolism are urgent alternatives, but the supplied history lacks the discriminating examination, imaging, and additional risk details needed to evaluate them. Consider them in parallel, particularly before bleeding-risk therapies [P1, P2].
- [T3] Immediate treatment should activate the STEMI and catheterization team for primary PCI or the locally appropriate urgent reperfusion pathway [P1, P3]. Continuous ECG and pressure monitoring, defibrillation readiness, IV access, shock assessment, right-sided leads, and bedside echo support stabilization without holding reperfusion [P2].
- [T4] Aspirin 162 to 325 mg chewed is indicated when no contraindication exists; the team selects additional antiplatelet and anticoagulant treatment based on bleeding risk and reperfusion strategy [P3]. Given possible right ventricular involvement and hypotension, avoid nitrates. Clinicians may consider cautiously titrated fluid if preload responsive, with monitoring for pulmonary edema, and vasopressors if shock persists [P2, P3].
- [T5] The guideline recommends oxygen for saturation below 90%; it does not recommend routine oxygen at 94% in ACS. Monitor and reassess for another indication [P2, P3].

**Formal conclusion**

Most likely: acute inferior STEMI, with possible right ventricular involvement and evolving shock [T1]. Activate emergency reperfusion and monitor and stabilize immediately [T3, T4]; evaluate contraindications and urgent alternatives in parallel [T2, T4]. Oxygen is not routinely indicated at the reported saturation under the cited guideline [T5].

**Remediation / next action**

If this is a real patient, activate emergency services or the in-hospital STEMI team now. Obtain right-sided ECG, bedside echo if available, serial ECGs, troponin, medication and allergy history, and bleeding-risk assessment in parallel with reperfusion planning [T1-T4]. This is analytical support; clinicians at the bedside make treatment decisions.

Self-check: each conclusion cites its diagnostic or treatment trace.

### EVALUATION: TEST 3

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 5 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 24/25 | 24/25 | 0 |

Baseline Words: 310 | Optimized Words: 378 | Overhead Ratio: 1.22x

Both prioritize reperfusion and distinguish suspected right ventricular involvement from confirmation. The optimized version ties each decision to a trace, but the baseline presents the emergency actions more directly.

## TEST 4: Legal Analysis

### RAW PROMPT

```text
An employee signed a non-compete agreement that prevents them from working in "any related industry" within a 200-mile radius for 5 years after leaving the company. They left and took a job at a competitor 150 miles away, 8 months later. The former employer is threatening to sue. Analyze the enforceability of this non-compete.
```

### BASELINE RESPONSE

The employee appears to be within the restriction's stated time and distance, assuming the 200-mile radius is measured from the relevant location and the new role is covered. That does not establish enforceability. The jurisdiction, governing-law clause, full agreement, role, and circumstances of signing are missing, so there is no reliable yes-or-no answer.

Where a reasonableness test applies, a five-year restriction covering any related industry over 200 miles gives the employee substantial arguments that the clause is broader than necessary, especially if it reaches jobs unrelated to the former role or territory. The employer may argue that its market, customer relationships, and confidential information justify a narrower restriction. Some courts can narrow an overbroad clause and others cannot or will not, depending on local law and the contract. Consideration, occupation, compensation, termination circumstances, and available statutory exceptions may matter too.

As a conditional U.S. example, [California Business and Professions Code section 16600](https://law.justia.com/codes/california/code-bpc/division-7/part-2/chapter-1/section-16600/) generally voids restraints on lawful work, subject to statutory exceptions. That is not a determination that California law applies here. The [FTC says its nationwide noncompete rule is not in effect](https://www.ftc.gov/legal-library/browse/rules/noncompete-rule); state and other law may still apply.

Promptly consult employment counsel in the relevant jurisdiction and provide the complete agreement, notice or demand, locations, job descriptions, compensation and signing history, and dates. Preserve records and respect any separate confidentiality and trade-secret duties while counsel evaluates the threat. This is general information, not legal advice.

### OPTIMIZED PROMPT

Classification: accuracy, no persona. Mode 1, actual Template 8, Legal Analysis. The prompt lacks jurisdiction and the full contract, so the certificate preserves ambiguity and checks both the employer's and employee's readings. This adapts Ugare & Chandra (2026), Hu, Rostami & Thomason (2026), and Yin et al. (2026).

```text
Legal analysis methodology requires a structured certificate for these facts:
an employee signed a restriction on work in "any related industry" within a
200-mile radius for 5 years after leaving; the employee joined a competitor
150 miles away after 8 months; the former employer threatens suit.

PREMISES: Separate stated facts, full-clause and governing-law gaps, and any
sourced conditional example law. LEGAL TRACES: Assess scope, duration,
distance, legitimate interests, counterarguments, potential narrowing and the
importance of jurisdiction. When law or contract text is missing, record
UNABLE TO TRACE. FORMAL CONCLUSION: Give a conditional assessment citing each
trace, not a definitive jurisdiction-free legal conclusion. REMEDIATION:
Identify the documents, facts, and counsel needed. Check all conclusions cite a
trace and its factual or legal premise.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] The stated terms are "any related industry," a 200-mile radius, and five years. The new job is 150 miles away and began eight months after departure. Full agreement and radius origin are missing.
- [P2] Governing jurisdiction, governing-law clause, occupation, compensation, protected interests, and signing circumstances are unknown.
- [P3] As an example only, [California Business and Professions Code section 16600](https://law.justia.com/codes/california/code-bpc/division-7/part-2/chapter-1/section-16600/) generally voids work restraints subject to exceptions; the [FTC reports](https://www.ftc.gov/legal-library/browse/rules/noncompete-rule) that its nationwide rule is not in effect.

**Legal traces**

- [T1] The role appears within the numerical period and radius, if the employer's measuring point and activity interpretation apply. Whether "related industry" covers the actual role and whether the asserted radius begins at the assumed point require the complete text [P1].
- [T2] Where reasonableness is the applicable test, the five-year term, 200-mile scope, and broad industry language support an overbreadth argument. The employer might identify customer relationships, confidential information, or market reach to support some restriction; the actual facts and legal standard are unverified [P1, P2].
- [T3] UNABLE TO TRACE the governing law, any threshold or exception, and whether a court may narrow the clause [P2]. If California law applies, section 16600's general rule and exceptions become relevant; this conditional example does not select the jurisdiction [P3].
- [T4] The FTC rule's reported status cannot by itself settle the agreement under other applicable law [P2, P3].

**Formal conclusion**

A facial match to the stated radius and period is plausible, while substantial scope objections may be available under a reasonableness regime [T1, T2]. Actual enforceability and potential narrowing remain unresolved until governing law and the full contract are established [T3, T4].

**Remediation / next action**

Provide local employment counsel with the signed agreement and amendments, demand, locations and role descriptions, pay and signing circumstances, and departure dates. Ask counsel to identify the governing law, any statutory exceptions, legitimate interests, narrowing rules, and response deadlines [T1-T3]. Preserve evidence and comply with separate confidentiality obligations. This is general information, not legal advice.

Self-check: conclusion claims cite the relevant factual and legal traces.

### EVALUATION: TEST 4

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 5 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 24/25 | 24/25 | 0 |

Baseline Words: 238 | Optimized Words: 338 | Overhead Ratio: 1.42x

Both qualify the application of California and federal law and preserve the employer's counterargument. Trace labels improve auditability, while the optimized format makes a straightforward conditional assessment longer.

## TEST 5: Research Synthesis

### RAW PROMPT

```text
What does the research say about whether remote work improves or hurts productivity? Give me a balanced overview.
```

### BASELINE RESPONSE

The research does not support a universal productivity gain or loss from remote work. Results vary with the job, whether work is hybrid or fully remote, who participates, the quality of management, and what researchers measure.

- **Positive result in a specific role:** a randomized study of volunteers at a Chinese travel agency call center found home working increased measured performance by 13%. Most of that increase reflected more minutes worked per shift; a smaller part reflected more calls per minute. The volunteer and single-employer setting limits generalization. [Bloom et al., 2015](https://doi.org/10.1093/qje/qju032).
- **No measurable performance harm in a hybrid trial:** a randomized study of 1,612 graduate employees at Trip.com found that two home days per week did not meaningfully change performance grades or engineers' lines of code under the authors' equivalence tests. Quit rates fell from 7.2% to 4.8%. Retention is valuable, but it is not the same outcome as productivity. [Bloom, Han and Liang, 2024](https://www.nature.com/articles/s41586-024-07500-2).
- **Negative result in another setting:** a randomized Indian data-entry experiment found assigned home workers were 18% less productive than office workers. This is an [NBER working paper](https://www.nber.org/system/files/working_papers/w31515/w31515.pdf), so treat its publication status separately from the journal articles.

These studies use different tasks, populations, measures and degrees of remote work; the differences offer plausible explanations, but they do not isolate which factor caused the differing results. Performance reviews, call volume, code volume, and data-entry output each capture only part of value. Observational studies add breadth but can confound work location with worker selection or pandemic disruption.

For a particular organization, try a time-limited, comparable hybrid or remote pilot and measure output quality, delivery, collaboration, employee retention, and hours, with predeclared metrics and attention to worker differences. The three studies above are illustrative rather than a comprehensive systematic review, so their results should not be averaged into a universal effect.

### OPTIMIZED PROMPT

Classification: mixed, minimal persona. Mode 1, actual Template 3, Research Synthesis. The question lacks a source corpus, design and outcome boundaries; the rewrite requests verifiable opposing studies and separates measured outcomes from inference. The structure follows Ugare & Chandra (2026), Zhang, Hu et al. (2026), Hu, Rostami & Thomason (2026), and Yin et al. (2026).

```text
You are a research analyst. Peer-reviewed synthesis methodology requires a
certificate addressing: What does research say about remote work and
productivity?

PREMISES: Identify the source corpus, study designs, outcomes and coverage
limits. EVIDENCE TRACES: Summarize at least three primary studies with different
results, their populations, arrangements, measured effects, design limitations
and links. Distinguish a working paper from a peer-reviewed article. When the
mechanism behind disagreement is not established, mark UNRESOLVED. FORMAL
CONCLUSION: Synthesize only findings supported by cited traces; distinguish
performance from retention. REMEDIATION: Give a practical evaluation protocol
and name gaps in this non-systematic corpus. Verify conclusion citations.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] Three primary studies examine remote or hybrid work, with different tasks, employee populations, and outcomes; this is a selected, non-systematic corpus.
- [P2] Productivity, retention, and satisfaction are distinct outcomes; randomized results apply directly to their studied settings, not automatically to every workplace.

**Evidence traces**

- [T1] [Bloom et al. (2015)](https://doi.org/10.1093/qje/qju032), a randomized trial among call-center volunteers, found 13% higher measured performance at home. About nine percentage points reflected more minutes worked per shift and four reflected more calls per minute. Selection into volunteering and one employer limit generalization [P1].
- [T2] [Bloom, Han and Liang (2024)](https://www.nature.com/articles/s41586-024-07500-2) randomized 1,612 graduate employees to a two-day hybrid option or office work. Performance grades and engineering lines of code met the authors' equivalence tests, and attrition fell from 7.2% to 4.8%. These measures do not capture all aspects of output [P1, P2].
- [T3] An [NBER working paper on Indian data-entry workers](https://www.nber.org/system/files/working_papers/w31515/w31515.pdf) reports that randomly assigned home workers were 18% less productive than office workers. It is a working paper; its setting and outcome differ from T1 and T2 [P1].
- [T4] UNRESOLVED: task, schedule, selection, management, and setting could contribute to the divergence, but these three studies do not isolate their relative causal contributions [T1-T3].

**Formal conclusion**

These studies show positive, approximately unchanged, and negative measured effects in different settings, so they do not establish a universal effect [T1-T4]. The observed retention improvement in the hybrid trial is separate from its performance measures [T2]. Generalization and broader evidence coverage remain gaps [T4].

**Remediation / next action**

Run a defined, time-limited pilot where feasible, compare similar teams or randomize a hybrid option, and predefine output quality, delivery time, hours, collaboration, and retention measures. Review a broader systematic corpus before applying these results across occupations [T1-T4].

Self-check: each conclusion references the relevant study traces and their source links.

### EVALUATION: TEST 5

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 4 | 4 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 23/25 | 23/25 | 0 |

Baseline Words: 307 | Optimized Words: 303 | Overhead Ratio: 0.99x

The same three sources and limitations support both versions. Identifiers improve cross-reference, while neither selected corpus is a systematic review and the extra structure does not increase evidence coverage.

## TEST 6: Business Decision

### RAW PROMPT

```text
We're a 15-person SaaS startup deciding between building our own authentication system or using Auth0/Clerk. We handle sensitive healthcare data (HIPAA). What should we do?
```

### BASELINE RESPONSE

Start with a managed identity provider, and select Auth0 or Clerk after a short security, contract, integration, and cost review. For a 15-person team, owning password storage, credential recovery, MFA, incident response, and continuing security maintenance is a substantial ongoing burden. Building may be justified if a documented requirement cannot be met by either provider and you can fund specialist engineering and independent security review.

A provider does not make the application HIPAA compliant. First map what identity data, logs, support tickets, and integrations may contain protected health information (PHI). If a vendor creates, receives, maintains, or transmits PHI on behalf of a covered entity or business associate, assess its business-associate status and execute a suitable BAA where required before that processing; encryption alone does not remove the requirement. [HHS cloud guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html).

Compare both vendors on the same criteria: BAA and covered services, MFA and recovery, enterprise SSO, audit logs, tenancy and authorization integration, availability, data residency, support, total cost at expected usage, and export/migration. [Auth0](https://auth0.com/healthcare) states that PHI use requires eligible services and a valid BAA; [Clerk](https://clerk.com/security) says its BAA is available on Enterprise. Verify current written terms and scope for your contract, rather than assuming a plan or feature is covered.

Keep application authorization and tenant isolation enforced server-side, minimize PHI in identity claims and logs, use MFA, review access, and retain suitable audit evidence. Carry out a risk analysis and verify administrative, physical, and technical safeguards beyond login; [HHS describes the Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html). Next, prototype both providers against your requirements and choose the one that passes the contractual and technical gates at an acceptable total cost. Obtain qualified legal and security review for the specific data flows.

### OPTIMIZED PROMPT

Classification: mixed, minimal persona. Mode 1, actual Template 5, Decision-Making. The task lacks vendor contract terms, costs, PHI flow, and acceptance criteria; the rewrite compares each option against the same dimensions without predetermining the winner. This adapts Ugare & Chandra (2026), Cao, Jiang & Xu (2026), Hu, Rostami & Thomason (2026), and Yin et al. (2026).

```text
You are a decision analyst. Standard decision analysis requires a certificate
for a 15-person SaaS team handling healthcare data and choosing between custom
authentication, Auth0, and Clerk.

PREMISES: State the options, same evaluation criteria, known constraints, and
unknown contracts, costs, and data flows. OPTION TRACES: Compare each option on
security operations, HIPAA-related data handling and contracts, capability,
cost and migration using verifiable evidence. When a claim cannot be verified,
mark UNABLE TO TRACE and identify the evidence needed. FORMAL CONCLUSION: Give
a conditional choice, counterexample and tradeoffs with trace references.
REMEDIATION: Provide a concrete due-diligence and implementation sequence;
distinguish authentication from application-wide HIPAA obligations. Check that
comparative claims cite the corresponding option traces.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] The options are custom authentication, Auth0, and Clerk; the team has 15 people and handles healthcare data. Application architecture, patient data flow, budget, and contract terms are not provided.
- [P2] Compare ongoing security ownership, PHI and BAA scope, identity capabilities, cost, reliability, and migration. HHS explains [when cloud vendors can be business associates](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html) and the need for broader [security safeguards](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html).

**Option traces**

- [T1] Custom: maximum implementation control, but the team owns credential security, recovery, MFA, maintenance, incident response, and validation. Cloud subcontractors may still need BAAs if their services handle PHI. Actual build cost and fit are UNABLE TO TRACE [P1, P2].
- [T2] Auth0: managed identity shifts some authentication operations to a provider but leaves application authorization and compliance with the team. [Auth0](https://auth0.com/healthcare) limits PHI to eligible services under a valid BAA. The specific contract, cost, capability fit, and export terms are UNABLE TO TRACE [P1, P2].
- [T3] Clerk: the same managed-service tradeoff applies. [Clerk](https://clerk.com/security) identifies its Enterprise plan as the path to a BAA. Actual scope, cost, logging, availability, and export terms remain UNABLE TO TRACE [P1, P2].
- [T4] The need for a BAA depends on the legal relationship and actual PHI handling; encryption alone does not exempt a cloud provider. A signed BAA does not by itself implement application-level access or audit controls [P2].

**Formal conclusion**

Prefer a qualified managed provider as the starting point, subject to verifying service scope, legal obligations, operational fit, and total cost [T2-T4]. Choose between Auth0 and Clerk only after comparing written evidence; consider custom authentication if neither meets a hard requirement and the team can sustain specialist security ownership [T1-T3]. Managed service trades some control and portability for reduced responsibility for identity infrastructure [T1-T3].

**Remediation / next action**

1. Map identity attributes, tokens, logs, and vendor access to possible PHI; obtain counsel's BAA determination and the agreement when required [T4].
2. Ask both vendors for scoped BAA terms, security evidence, MFA and recovery, SSO, audit retention, availability, pricing, and data export; pilot the same flows against both [T2, T3].
3. Enforce server-side tenant authorization, MFA, audit review, and a documented organization-wide risk assessment; test access revocation and failure recovery [T1-T4].

Self-check: each conclusion cites all relevant option traces; unknown commercial terms remain open.

### EVALUATION: TEST 6

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 5 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 24/25 | 24/25 | 0 |

Baseline Words: 281 | Optimized Words: 372 | Overhead Ratio: 1.32x

Both recommend a managed provider conditionally and address the same HIPAA boundary. The option traces make the comparison auditable, but the added labels do not resolve the missing vendor terms.

## TEST 7: Compliance Check

### RAW PROMPT

```text
Review this password policy for NIST 800-63B compliance:
- Minimum 8 characters
- Must include uppercase, lowercase, number, and special character
- Passwords expire every 90 days
- Cannot reuse last 5 passwords
- Account locks after 3 failed attempts for 30 minutes
```

### BASELINE RESPONSE

Against [NIST SP 800-63B-4, sections 3.1.1 and 3.2.2](https://pages.nist.gov/800-63-4/sp800-63b.html), this policy needs changes. The applicable revision and the system's authentication assurance level should be confirmed; the following uses the final Revision 4 for centrally verified passwords.

| Item | Assessment |
|---|---|
| Minimum 8 characters | Insufficient for a password used as a single factor: at least 15 are required. Eight is permitted only when the password is used exclusively as part of MFA. |
| Character classes | Nonconforming: verifiers must not impose composition rules. |
| 90-day expiry | Nonconforming: routine periodic changes must not be required; force a change upon evidence of compromise. |
| Last five passwords | The cited standard does not require this exact history rule; it recognizes feedback for previously used passwords. The rule alone neither establishes nor disproves compliance. |
| Three attempts, 30 minutes | A lower threshold is allowed, but a timed lock alone does not prove the required limit of at most 100 consecutive failures followed by authenticator disabling and rebind. Determine whether failures accumulate across lockouts and how recovery works. Three attempts can also enable denial of service. |

Add a compromised/common-password blocklist at enrollment and change, allow password managers and autofill, verify the entire password, use a salted suitable password hash, and protect transport. NIST recommends allowing a maximum of at least 64 characters. The supplied text does not establish whether these controls exist, so a full compliance finding requires implementation evidence, not just policy wording.

A revised core policy could state: "Require at least 15 characters for a single-factor password, or at least eight when used only with MFA. Permit long passphrases and password managers; compare new passwords against a blocklist. Change passwords on evidence of compromise. Rate-limit consecutive failures and disable and rebind authenticators as specified by NIST." Check any other applicable requirements and the deployed configuration.

### OPTIMIZED PROMPT

Classification: accuracy, no persona. Mode 1, actual Template 4, Compliance / Regulatory Check. The original omits NIST revision, MFA scope, and implementation evidence. Clause-based dispositions follow Ugare & Chandra (2026), Hu, Rostami & Thomason (2026), and Yin et al. (2026).

```text
Regulatory audit methodology requires a verification certificate for this
password policy: minimum 8 characters; uppercase, lowercase, number and special
character required; 90-day expiry; last five passwords cannot be reused; lock
after three failures for 30 minutes.

PREMISES: Identify NIST SP 800-63B-4 and relevant sections, the policy, and
unknown authentication and implementation scope. COMPLIANCE TRACES: Assess
each item against the actual SHALL, SHALL NOT, or SHOULD language; distinguish
policy text from proof of implementation. When MFA status or cumulative retry
behavior is unknown, mark UNABLE TO VERIFY. FORMAL CONCLUSION: Cite each
clause and trace and list gaps. REMEDIATION: Provide corrected policy language
and evidence to collect. Verify each conclusion cites its clause and trace.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] The five policy rules are exactly those supplied; no configuration or logs were provided.
- [P2] This review uses [NIST SP 800-63B-4 sections 3.1.1.2 and 3.2.2](https://pages.nist.gov/800-63-4/sp800-63b.html). MFA exclusivity, authentication assurance level, and cumulative failure handling are unknown.

**Compliance traces**

- [T1] Length, section 3.1.1.2: eight characters is NON-COMPLIANT for single-factor passwords, which require at least 15; it is potentially compliant if used exclusively within MFA. Actual use is UNABLE TO VERIFY [P1, P2].
- [T2] Composition and change frequency, section 3.1.1.2: mandatory character classes and 90-day changes are NON-COMPLIANT. Password change is required on evidence of compromise [P1, P2].
- [T3] History: the specified five-password history is not a requirement established by the cited sections; NIST's usability guidance contemplates rejecting previously used passwords. Its presence alone does not settle compliance [P1, P2].
- [T4] Rate limiting, section 3.2.2: fewer than 100 consecutive attempts may be allowed, but a three-attempt temporary lock does not prove the required upper bound, disabling, and rebind behavior. UNABLE TO VERIFY whether failures accumulate across locks or how recovery works [P1, P2].
- [T5] Section 3.1.1.2 also requires a password blocklist, full verification, password-manager support, protected transport, and salted suitable password hashing; implementation is UNABLE TO VERIFY. A maximum of at least 64 characters is a SHOULD, not a SHALL [P2].

**Formal conclusion**

The composition and periodic expiry requirements conflict with section 3.1.1.2 [T2]. The eight-character minimum is conditional on MFA-only use [T1]. Retry behavior and several other controls cannot be verified from the policy alone [T4, T5]; the five-password rule is not sufficient evidence of compliance [T3].

**Remediation / next action**

Adopt: "Require at least 15 characters for single-factor passwords, or at least eight when the password is only used with MFA. Permit long passphrases and password managers; block common and compromised choices; change a password when compromise is evidenced. Limit consecutive failures and disable and rebind as required by NIST." Remove the mandatory character classes and periodic expiry. Inspect the verifier configuration and test failure accumulation, rebind, blocklist, hashing, and full password handling [T1-T5].

Self-check: each conclusion cites a clause-based trace and distinguishes missing evidence from nonconformance.

### EVALUATION: TEST 7

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 5 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 24/25 | 24/25 | 0 |

Baseline Words: 298 | Optimized Words: 367 | Overhead Ratio: 1.23x

Both identify the revision-specific length rules and the unresolved timed-lock behavior. The certificate makes the clause-to-finding mapping explicit, while its extra formatting does not establish compliance without implementation evidence.

## TEST 8: Document Analysis

### RAW PROMPT

```text
Here is an executive summary from a project proposal: "Our AI-powered customer service solution will reduce support tickets by 60% within 6 months of deployment. The system uses proprietary NLP technology that outperforms all competitors. Implementation requires minimal IT involvement and the ROI will exceed 300% in the first year." Analyze the credibility of these claims.
```

### BASELINE RESPONSE

The summary contains four strong claims but provides no data, comparison method, implementation plan, or financial model. They may be achievable, but none can be verified from the excerpt.

| Claim | Credibility issue | Evidence to request |
|---|---|---|
| 60% fewer tickets within six months | The baseline, ticket definition, deployment scope, and whether requests are solved or merely deflected are absent. | Historical volumes and seasonality; controlled pilot with resolved issues, repeat contacts, customer satisfaction, and escalation rates. |
| Proprietary NLP outperforms all competitors | Neither "proprietary" nor a universal comparison establishes performance. | Named alternatives, representative held-out cases, metrics for quality and safety, methodology, dates, and independent evaluation. |
| Minimal IT involvement | Integration, security review, data mapping, identity, testing, and maintenance may require substantial effort. | Architecture, responsibilities, integrations, staff hours, dependencies, and deployment schedule. |
| First-year ROI above 300% | Benefits, costs, assumptions and the definition of ROI are missing. | Itemized implementation and recurring costs, baseline labor costs, measurable net benefits, and sensitivity analysis. |

If ROI means `(benefits - costs) / costs`, a 300% ROI requires benefits equal to four times costs; other definitions need their own calculation. Savings should not double-count tickets deflected and hours saved, and should include implementation, support, licensing, and quality impacts.

Ask for a funded pilot with an agreed baseline and comparison group, review the results before approving a full rollout, and rewrite each claim as a target until evidence supports it. The excerpt gives no basis to label the claims false or verified.

### OPTIMIZED PROMPT

Classification: mixed, minimal persona. Mode 1, actual Template 2, Document Analysis. The excerpt supplies claims but no supporting evidence; the rewrite anchors findings to exact language and treats missing support as a gap. The design follows Ugare & Chandra (2026), Zhang, Hu et al. (2026), Hu, Rostami & Thomason (2026), and Yin et al. (2026).

```text
You are an analyst. The document-review protocol requires a certificate for
this complete excerpt: "Our AI-powered customer service solution will reduce
support tickets by 60% within 6 months of deployment. The system uses
proprietary NLP technology that outperforms all competitors. Implementation
requires minimal IT involvement and the ROI will exceed 300% in the first
year."

PREMISES: Identify the excerpt, claim scope and unavailable evidence.
EVIDENCE TRACES: For each claim quote the relevant text, explain the
verification gap and specify evidence needed, including alternative
interpretations and an explicit ROI formula if appropriate. When a document or
benchmark is absent, mark ABSENT. FORMAL CONCLUSION: Cite the traces and
separate unverified from false. REMEDIATION: Supply an evidence request, pilot
criteria and sample qualified replacement language. Self-check all citations.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] The only artifact is the supplied executive-summary excerpt. The full proposal and its supporting evidence are ABSENT.
- [P2] Credibility depends on measurable definitions, representative comparisons, implementation evidence, and a transparent calculation.

**Evidence traces**

- [T1] "reduce support tickets by 60% within 6 months": baseline, ticket definition, deployment scope, and resolution quality are ABSENT. Compare against a baseline and control, including repeat contacts, escalations, and satisfaction [P1, P2].
- [T2] "outperforms all competitors": the competitor set, task data, metrics and testing method are ABSENT. Proprietary technology alone does not establish superiority; require a representative, independently reproducible comparison [P1, P2].
- [T3] "minimal IT involvement": staffing assumptions, integration, identity, data, security and operating dependencies are ABSENT. Request an effort estimate and responsibility matrix [P1, P2].
- [T4] "ROI will exceed 300% in the first year": cost, benefits and the ROI definition are ABSENT. If ROI is `(benefits - costs) / costs`, 300% requires benefits of four times costs; validate one-time and ongoing costs and avoid double-counting savings [P1, P2].

**Formal conclusion**

All four claims are unverified on the supplied excerpt; that is not proof they are false [T1-T4]. The strength of the universal comparison and the financial forecast is unsupported by the evidence provided [T2, T4].

**Remediation / next action**

Request baseline and controlled pilot results, competitor benchmarks, a staffing and integration plan, and a cost-benefit model with sensitivity analysis [T1-T4]. Example replacement pending evidence: "We propose a six-month pilot to measure ticket resolution, implementation effort, and first-year costs and benefits against an agreed baseline." Set pass criteria before the pilot and review quality alongside volume.

Self-check: each conclusion refers to the quoted claim and its missing support.

### EVALUATION: TEST 8

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 5 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 24/25 | 24/25 | 0 |

Baseline Words: 237 | Optimized Words: 271 | Overhead Ratio: 1.14x

Both identify all four unsupported claims and provide a testable ROI calculation. The optimized version includes a useful sample replacement, but its labels add little to the baseline's compact claim-to-evidence table.

## TEST 9: Comparative Analysis

### RAW PROMPT

```text
Compare PostgreSQL and MongoDB for a new application that needs to handle both structured transaction data and semi-structured user activity logs. We expect 10M records per month growing 20% annually.
```

### BASELINE RESPONSE

Start with **PostgreSQL** unless the activity workload's measured scale, access patterns, or operational requirements favor MongoDB. PostgreSQL combines relational transactions, constraints and joins with indexed `jsonb` for flexible log fields; that can keep one initial system. MongoDB is a credible alternative for document-oriented data and horizontal sharding, and it also supports multi-document transactions. Neither choice is justified by record count alone.

| Dimension | PostgreSQL | MongoDB |
|---|---|---|
| Transaction data | Relational constraints, joins, and transactions fit related entities naturally. | Document operations are atomic; multi-document transactions exist but have additional costs and design considerations. |
| Activity logs | `jsonb`, indexes, and time partitioning can handle evolving fields and retention. | Flexible documents and sharding can fit varied events; choose the shard key and indexes carefully. |
| Operations | One database can simplify joins and initial operations; high log volume may compete with transactional workloads. | Sharding can distribute data, with additional operational, query, and transaction complexity. |

At a constant 10M records per 30-day month, the average is about 3.86 records per second, not the peak. If the monthly rate grows 20% each year, it becomes 12M in year two and 14.4M in year three. Size depends on record bytes, indexes, retention, replicas, and compression; throughput depends on burstiness, reads, transactions and latency goals.

Use typed transactional tables and a time-partitioned events table with selected `jsonb` indexes. Benchmark representative peak ingestion, transaction conflicts, log queries, storage and recovery on comparable hardware before committing; consider a separate log store if isolation or measured scale warrants it. [PostgreSQL JSON](https://www.postgresql.org/docs/current/datatype-json.html) and [MongoDB transactions](https://www.mongodb.com/docs/manual/core/transactions/) document the relevant capabilities.

### OPTIMIZED PROMPT

Classification: mixed, minimal persona. Mode 2 Lite, actual Template 6, Comparative Analysis. The task lacks record sizes, peaks, retention, and query objectives, so the matrix records unmeasured outcomes rather than inventing benchmarks. Compact traces and a conditional choice follow Ugare & Chandra (2026), Hu, Rostami & Thomason (2026), and Yin et al. (2026).

```text
You are an analyst. The comparative protocol requires a Lite certificate for
PostgreSQL versus MongoDB for structured transactions and semi-structured
activity logs, initially 10M records per month with 20% annual growth.

Use at most three [P] premises, a compact comparison matrix with single-line [T]
traces for transactions, flexible logs, operations and volume, and a one- or
two-sentence conclusion citing traces. When throughput, cost or workload details
are missing, label them UNMEASURED. Give a concrete benchmark and initial
configuration as the next action. Check conclusion citations; keep the response
concise and under 1.5 times a comparable direct answer where possible.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] Structured transactions and semi-structured activity logs; 10M records/month, growing 20% annually.
- [P2] Peak rate, record size, queries, retention, budget and latency are UNMEASURED.

| Trace and dimension | PostgreSQL | MongoDB |
|---|---|---|
| [T1] Transactions | Relational constraints, joins and transactions fit related records. | Single-document writes are atomic; multi-document transactions are supported with tradeoffs. |
| [T2] Logs | Indexed `jsonb` and time partitions support flexible fields and retention. | Documents and sharding support flexible events; key and index choices matter. |
| [T3] Operations | One relational system simplifies initial joins, but logs can compete with transactional traffic. | Sharding distributes data, with additional operational and cross-shard complexity. |
| [T4] Volume | 10M per 30 days is about 3.86 records/second on average; 12M/month in year two and 14.4M in year three. | The same arithmetic applies; peaks and resource requirements are UNMEASURED [P2]. |

**Conclusion:** Start with PostgreSQL for the combined workload, conditional on a representative benchmark [T1-T4]. MongoDB may fit better if measured document and sharding requirements outweigh the relational benefits [T1-T3].

**Next action:** Use typed transaction tables and a time-partitioned event table with selective `jsonb` indexes; benchmark peak writes, query latency, storage and recovery against MongoDB on comparable infrastructure. See [PostgreSQL JSON](https://www.postgresql.org/docs/current/datatype-json.html) and [MongoDB transactions](https://www.mongodb.com/docs/manual/core/transactions/).

Self-check: each conclusion cites the matrix traces.

### EVALUATION: TEST 9

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 5 | 0 |
| Structure | 5 | 5 | 0 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 5 | +1 |
| TOTAL | 24/25 | 25/25 | +1 |

Baseline Words: 254 | Optimized Words: 204 | Overhead Ratio: 0.80x

Both make the same conditional recommendation and identify missing workload data. The Lite matrix preserves the practical comparison and adds compact trace references; the measured ratio below determines whether the response-length target was met.

## TEST 10: Creative Brief with Structure

### RAW PROMPT

```text
Write a product description for a new ergonomic office chair designed for people who work 10+ hour days. The chair has lumbar support that auto-adjusts, breathable mesh, and a 12-year warranty. Target audience is remote tech workers ages 25-45.
```

### BASELINE RESPONSE

Your calendar is full, your build is still running, and the afternoon has quietly become evening. Your chair should be ready for the long stretch.

This ergonomic office chair brings auto-adjusting lumbar support to the workday, so support follows you as you change position. Breathable mesh helps keep the seat comfortable through back-to-back calls and focused work. And with a 12-year warranty, it's built for a place in your home office long after the current sprint ends.

Settle in for the work ahead.

### OPTIMIZED PROMPT

Classification: creative, practitioner persona. Mode 4, actual Template 12, Creative / Editorial Writing. The raw brief leaves voice and structure open; the rewrite samples distinct tonal openings and uses concrete structural predicates. This adapts Zhang et al. (2025), Madler (2026), Hu, Rostami & Thomason (2026), and Yin et al. (2026). The probability values requested below are subjective estimates, not calibrated measurements.

```text
You are a product copywriter. The editorial craft protocol requires a backstage
scaffold and a clean product description for an ergonomic office chair with
auto-adjusting lumbar support, breathable mesh and a 12-year warranty, for
remote tech workers ages 25-45 who work 10+ hour days.

PREMISES: Record the audience, context and supplied facts. [NT0]: Give three
structurally and tonally distinct short candidate openings, each with an
estimated typicality p below 0.15; identify these estimates as subjective, then
select the strongest. [NT1]-[NT3]: State the opening anchor, progression and
cadence. [SC0]: Start in a concrete moment, develop the product details directly,
use a grounded practitioner voice, and end on a concrete action. When a product
claim is not in the brief, leave it unasserted. Present a clean final description
separate from the scaffold.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] Remote tech workers face long home-office days.
- [P2] Supplied features: auto-adjusting lumbar support, breathable mesh, and a 12-year warranty.
- [P3] The output is concise product copy; warranty terms and health outcomes are unspecified.

**Backstage scaffold**

- [NT0] Subjective typicality estimates, not calibrated probabilities:
  1. Dry, work-log opening: "7:42 p.m. The last review comment arrives." `p = 0.12`.
  2. Gentle, human opening: "Your mug has gone cold twice today." `p = 0.11`.
  3. Playful, systems opening: "Your day has no graceful shutdown." `p = 0.09`.
  Selection: the work-log angle, because it gives the reader a concrete moment without inventing a product feature [P1-P3].
- [NT1] Open at a late code review.
- [NT2] Move from the day's last task to support, mesh, then the warranty.
- [NT3] Use short sentences and familiar work details; keep the final action concrete.
- [SC0] Check for a scene, direct feature progression, grounded voice, and an action at the close.

**Final description**

7:42 p.m. The last review comment arrives.

Some days your home office holds you for more than ten hours. This ergonomic chair has lumbar support that adjusts automatically as you settle into the next task, and breathable mesh for the long stretch between the first stand-up and the final call.

It's backed by a 12-year warranty. Close your laptop; the chair can wait for tomorrow.

### EVALUATION: TEST 10

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 5 | 0 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 4 | 0 |
| TOTAL | 24/25 | 23/25 | -1 |

Baseline Words: 83 | Optimized Words: 223 | Overhead Ratio: 2.69x

The optimized copy has a more specific opening, but both versions use a familiar late-workday scene. The candidate scaffold is longer than the deliverable and its invented typicality estimates do not independently establish rarity or improve factual traceability.

## TEST 11: Repository Context File Optimization

### RAW PROMPT

```text
Write a CLAUDE.md file for our Python FastAPI + PostgreSQL repository. Explain the project overview, list the folder structure (app/api, app/models, app/services, tests/), explain standard PEP8 coding conventions, and include our non-obvious commands: running unit tests requires `pytest -m "not integration" --reuse-db`, database migrations must run via `./scripts/migrate.sh check` before committing, and Redis cache keys in `app/services/billing.py` must never be mutated without bumping `SCHEMA_EPOCH`.
```

### BASELINE RESPONSE

```markdown
# CLAUDE.md

## Project overview

This repository contains a Python FastAPI application backed by PostgreSQL.
Inspect the relevant implementation before changing behavior or assumptions.

## Directory guide

- `app/api/`: API-related code.
- `app/models/`: model code.
- `app/services/`: service code, including billing.
- `tests/`: tests.

## Coding conventions

Follow PEP 8 and match established local patterns. Use clear names, small
functions, and readable imports. Check the repository's existing formatter and
lint configuration before running or changing it.

## Non-obvious commands and invariants

- Run unit tests with `pytest -m "not integration" --reuse-db`.
- Before committing, run `./scripts/migrate.sh check`.
- When changing Redis cache keys in `app/services/billing.py`, bump
  `SCHEMA_EPOCH` in the same change.

## Verification

Run the relevant unit tests and report their results. Before committing, run the
migration check above and report any failure or blocked command.
```

### OPTIMIZED PROMPT

Classification: persistent context, no persona. Mode 3, actual Template 11, Agentic System Prompt. The raw prompt explicitly asks for an overview and generic style guidance, while the benchmark explicitly asks to remove them; this optimization follows the benchmark's instruction and therefore changes the original deliverable. Minimal context and verification gates adapt Gloaguen et al. (2026), Lee et al. (2026), and Yin et al. (2026).

```text
The repository context protocol requires a concise CLAUDE.md operational
contract under 150 lines. Supplied facts: Python FastAPI and PostgreSQL; unit
tests require `pytest -m "not integration" --reuse-db`; before committing run
`./scripts/migrate.sh check`; when Redis cache keys in
`app/services/billing.py` are changed, bump `SCHEMA_EPOCH`.

Output only non-inferable commands, the cache invariant, and an actionable
verification gate. When a requested directory overview or generic PEP8 advice
is inferable, exclude it from the persistent file. When a command or policy is
not supplied, leave it unspecified. On verification failure or inability to
run a check, require a report of the command and reason. Emit the complete
copy-pasteable file.
```

### OPTIMIZED RESPONSE

```markdown
# Repository Agent Operating Contract

## Commands

- Unit tests: `pytest -m "not integration" --reuse-db`
- Before committing: `./scripts/migrate.sh check`

## Invariant

- When changing Redis cache keys in `app/services/billing.py`, bump
  `SCHEMA_EPOCH` in the same change.

## Verification gate

- Run the unit test command for relevant changes and the migration check before
  committing. Report each command's exit status and relevant output.
- When a check fails or cannot run, report the command and reason before
  claiming verification.
```

### EVALUATION: TEST 11

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 5 | 5 | 0 |
| Completeness | 5 | 3 | -2 |
| Structure | 5 | 5 | 0 |
| Actionability | 5 | 5 | 0 |
| Traceability | 4 | 4 | 0 |
| TOTAL | 24/25 | 22/25 | -2 |

Baseline Words: 132 | Optimized Words: 74 | Overhead Ratio: 0.56x

The optimized file is shorter and preserves all three non-obvious requirements, but it removes the overview, folder list, and PEP 8 guidance explicitly requested in the raw prompt. That is a material instruction-fidelity loss even though the benchmark specifically asks the optimization to prune them; the baseline is also already concise.

## TEST 12: Algorithmic Concurrency & Verification Gate

### RAW PROMPT

```text
Write a thread-safe async token bucket rate limiter in Python (`AsyncTokenBucket`) that supports burst capacity, fractional refill rates, and `acquire(tokens: int, timeout: float | None = None) -> bool`. Make sure there are no race conditions when multiple coroutines wait concurrently.
```

### BASELINE RESPONSE

This implementation uses a short `threading.Lock` around shared token accounting, so one bucket can be shared by coroutines running on different event loops and threads. Waiting happens asynchronously outside the lock. A bucket starts full, refills continuously up to its capacity, and does not promise FIFO fairness. A timeout of zero makes one immediate attempt; invalid or impossible requests raise `ValueError`.

```python
import asyncio
import math
import threading
import time


class AsyncTokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        if type(capacity) is not int or not 0 < capacity <= 2**53:
            raise ValueError("capacity must be an integer in 1..2**53")
        if not isinstance(refill_rate, (int, float)):
            raise ValueError("refill_rate must be finite and positive")
        try:
            rate = float(refill_rate)
        except OverflowError as exc:
            raise ValueError("refill_rate must be finite and positive") from exc
        if not math.isfinite(rate) or rate <= 0:
            raise ValueError("refill_rate must be finite and positive")
        self.capacity = capacity
        self.refill_rate = rate
        self._tokens = float(capacity)
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    async def acquire(self, tokens: int, timeout: float | None = None) -> bool:
        if type(tokens) is not int or not 0 < tokens <= self.capacity:
            raise ValueError("tokens must be a positive integer <= capacity")
        if timeout is not None:
            if not isinstance(timeout, (int, float)):
                raise ValueError("timeout must be finite and nonnegative")
            try:
                timeout = float(timeout)
            except OverflowError as exc:
                raise ValueError("timeout must be finite and nonnegative") from exc
            if not math.isfinite(timeout) or timeout < 0:
                raise ValueError("timeout must be finite and nonnegative")
        deadline = None if timeout is None else time.monotonic() + timeout
        first_attempt = True
        while True:
            with self._lock:
                now = time.monotonic()
                self._tokens = min(
                    self.capacity,
                    self._tokens + (now - self._updated) * self.refill_rate,
                )
                self._updated = now
                in_time = deadline is None or first_attempt or now <= deadline
                if in_time and self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                first_attempt = False
                if deadline is not None and now >= deadline:
                    return False
                delay = (tokens - self._tokens) / self.refill_rate
                if deadline is not None:
                    delay = min(delay, deadline - now)
            await asyncio.sleep(delay)
```

Call, for example, `await bucket.acquire(1, timeout=2.0)` after constructing `bucket = AsyncTokenBucket(capacity=10, refill_rate=0.5)`. Requests greater than capacity could never succeed and are rejected. A cancelled waiter holds no reservation; it propagates `CancelledError`. Accounting uses floating-point arithmetic, so applications requiring exact fractional accounting need a fixed-point design. The lock has no `await` inside it, but a stalled lock holder can block an event-loop thread.

### OPTIMIZED PROMPT

Classification: LRM / agentic coding, no persona. Mode 3, the core LRM verification pattern adapted to concurrency. The benchmark calls this Template 12, but Template 12 is creative writing and the library has no separate algorithmic harness template. The raw task leaves timeout, cancellation, input and precision semantics unspecified. Verification gates follow Lee et al. (2026), Ugare & Chandra (2026), and Yin et al. (2026).

```text
The concurrency verification protocol requires a complete Python
AsyncTokenBucket(capacity, refill_rate) with async
acquire(tokens: int, timeout: float | None = None) -> bool.

PREMISES: Define initialization, burst capacity, refill units, valid inputs,
timeout zero, cancellation, fairness, numerical precision and cross-thread use.
VERIFICATION GATES:
[V1] Under simultaneous coroutines and threads, refill and debit are atomic,
capacity is never exceeded, and elapsed time uses a monotonic clock.
[V2] Fractional refill, impossible requests, deadlines, and cancelled waiters
have defined behavior; no await occurs while holding a shared state lock.
[V3] Supply an executable self-test harness for burst contention, fractional
refill, timeout, cancellation, validation, and cross-thread/event-loop use.
Include a deterministic precision boundary check. Report SATISFIED only for
checks actually run and label unverified properties honestly.
DELIVERABLE: Emit complete runnable code and the self-tests. Conclude with
[V]-cited results and remaining limits. Keep visible reasoning concise.
```

### OPTIMIZED RESPONSE

**Premises**

- [P1] A full bucket holds a positive integer capacity. Refill rate is a finite positive number of tokens per second; requested tokens are positive integers no larger than capacity.
- [P2] `timeout=None` waits without a deadline; zero attempts once immediately; a finite nonnegative timeout applies to subsequent attempts. Waiters do not reserve tokens, cancellation propagates, and FIFO fairness is not guaranteed.
- [P3] Nanosecond monotonic time and exact rational balances avoid the floating-point balance rounding demonstrated in the baseline. An ordinary thread lock protects shared state across event loops and threads; the critical section contains no `await`.

**Deliverable**

Save as `async_token_bucket.py` and run `python3 async_token_bucket.py` for the self-tests.

```python
import asyncio
import math
import threading
import time
from fractions import Fraction


class AsyncTokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        if type(capacity) is not int or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self._rate = self._positive_rate(refill_rate)
        self._capacity = capacity
        self._balance = Fraction(capacity)
        self._updated_ns = time.monotonic_ns()
        self._lock = threading.Lock()

    @staticmethod
    def _positive_rate(value):
        if type(value) not in (int, float):
            raise ValueError("refill_rate must be finite and positive")
        try:
            value = float(value)
        except OverflowError as exc:
            raise ValueError("refill_rate must be finite and positive") from exc
        if not math.isfinite(value) or value <= 0:
            raise ValueError("refill_rate must be finite and positive")
        return Fraction(str(value))

    async def acquire(self, tokens: int, timeout: float | None = None) -> bool:
        if type(tokens) is not int or not 0 < tokens <= self._capacity:
            raise ValueError("tokens must be a positive integer <= capacity")
        if timeout is not None:
            if type(timeout) not in (int, float):
                raise ValueError("timeout must be finite and nonnegative")
            try:
                timeout = float(timeout)
            except OverflowError as exc:
                raise ValueError("timeout must be finite and nonnegative") from exc
            if not math.isfinite(timeout) or timeout < 0:
                raise ValueError("timeout must be finite and nonnegative")

        deadline = None
        if timeout is not None:
            timeout_ns = int(Fraction(str(timeout)) * 1_000_000_000)
            deadline = time.monotonic_ns() + timeout_ns
        first = True

        while True:
            with self._lock:
                now = time.monotonic_ns()
                elapsed = Fraction(now - self._updated_ns, 1_000_000_000)
                self._balance = min(self._capacity, self._balance + elapsed * self._rate)
                self._updated_ns = now
                immediate = first and timeout == 0
                if (deadline is None or immediate or now <= deadline) and self._balance >= tokens:
                    self._balance -= tokens
                    return True
                first = False
                if deadline is not None and now >= deadline:
                    return False
                delay = min((tokens - self._balance) / self._rate, Fraction(60))
                if deadline is not None:
                    delay = min(delay, Fraction(deadline - now, 1_000_000_000))
            await asyncio.sleep(float(delay))


if __name__ == "__main__":
    import unittest

    class BucketTests(unittest.IsolatedAsyncioTestCase):
        async def test_contended_burst(self):
            bucket = AsyncTokenBucket(7, 1e-9)
            results = await asyncio.gather(*(bucket.acquire(1, 0) for _ in range(100)))
            self.assertEqual(sum(results), 7)

        async def test_fractional_refill_and_timeout(self):
            bucket = AsyncTokenBucket(1, 5.0)
            self.assertTrue(await bucket.acquire(1, 0))
            self.assertFalse(await bucket.acquire(1, 0.03))
            self.assertTrue(await bucket.acquire(1, 0.8))
            self.assertFalse(await bucket.acquire(1, 0))

        async def test_cancellation(self):
            bucket = AsyncTokenBucket(1, 0.01)
            self.assertTrue(await bucket.acquire(1, 0))
            waiter = asyncio.create_task(bucket.acquire(1))
            await asyncio.sleep(0.01)
            waiter.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await waiter
            self.assertFalse(await bucket.acquire(1, 0))

        async def test_invalid_arguments(self):
            bucket = AsyncTokenBucket(2, 0.5)
            for amount in (0, -1, 3, 1.5, True):
                with self.assertRaises(ValueError):
                    await bucket.acquire(amount, 0)
            for timeout in (-1, float("nan"), float("inf")):
                with self.assertRaises(ValueError):
                    await bucket.acquire(1, timeout)
            for rate in (0, -1, float("nan"), float("inf")):
                with self.assertRaises(ValueError):
                    AsyncTokenBucket(2, rate)

        async def test_threads_and_event_loops(self):
            bucket = AsyncTokenBucket(19, 1e-9)
            barrier = threading.Barrier(8)
            results = []
            guard = threading.Lock()

            def runner():
                async def attempts():
                    return await asyncio.gather(*(bucket.acquire(1, 0) for _ in range(20)))
                barrier.wait()
                batch = asyncio.run(attempts())
                with guard:
                    results.extend(batch)

            workers = [threading.Thread(target=runner) for _ in range(8)]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join()
            self.assertEqual(len(results), 160)
            self.assertEqual(sum(results), 19)

        async def test_large_capacity_precision(self):
            real_clock = time.monotonic_ns
            clock = [100_000_000_000]
            time.monotonic_ns = lambda: clock[0]
            try:
                bucket = AsyncTokenBucket(2**53, 0.5)
                self.assertTrue(await bucket.acquire(1, 0))
                clock[0] += 1_000_000_000
                self.assertFalse(await bucket.acquire(2**53, 0))
            finally:
                time.monotonic_ns = real_clock

    unittest.main(verbosity=2)
```

**Verification gates**

- [V1] SATISFIED for the tested burst scenarios: 100 simultaneous coroutine attempts admitted 7 tokens, and 160 attempts across eight threads and event loops admitted 19. The shared lock serializes refill and debit, and the implementation caps balance. These tests and inspection are not an exhaustive proof of all schedules.
- [V2] SATISFIED for the exercised fractional refill, deadline, cancellation, validation, and large-capacity precision cases. At capacity `2**53`, after spending one token and refilling only half a token, the rational implementation correctly rejects a full-capacity request. A deterministic check on the baseline returned `True` for that same request because the floating-point balance rounded up.
- [V3] SATISFIED: the embedded harness ran six tests with `OK`. The same independent five-test contention, refill, timeout, cancellation, and validation harness also passed for each implementation. All of these are bounded examples, not a formal proof.

**Conclusion and limits**

The optimized implementation passed the executed gates and resolves the demonstrated precision counterexample [V1-V3]. Rational arithmetic and periodic wakeups cost more than a float-only implementation, a stalled lock holder can block an event loop beyond deadlines, timeouts have nanosecond resolution, and waiters can starve because FIFO fairness is not promised [P2, P3]. Very large rational operands can increase CPU cost; performance and exhaustive concurrency correctness remain unmeasured.

### EVALUATION: TEST 12

| Dimension | Baseline | Optimized | Delta |
|---|---:|---:|---:|
| Accuracy | 4 | 5 | +1 |
| Completeness | 4 | 5 | +1 |
| Structure | 5 | 4 | -1 |
| Actionability | 5 | 5 | 0 |
| Traceability | 3 | 5 | +2 |
| TOTAL | 21/25 | 24/25 | +3 |

Baseline Words: 409 | Optimized Words: 930 | Overhead Ratio: 2.27x

Both pass the shared five-test harness, including contention across threads, but a deterministic large-capacity case exposes excess token issuance in the baseline. The optimized version passes that additional test and embeds its harness; its code and test overhead is substantial, and finite testing does not prove race freedom.

# FINAL REPORT

## Summary Table

| Test | Domain | Task Type | Mode | Baseline /25 | Optimized /25 | Delta | Words (B/O/Ratio) | Winner |
|---|---|---|---|---:|---:|---:|---|---|
| 1 | Code Review | Accuracy | Mode 1 | 23 | 23 | +0 | 216/275/1.27x | Tie |
| 2 | Financial Analysis | Accuracy | Mode 1 | 24 | 24 | +0 | 225/292/1.30x | Tie |
| 3 | Medical Reasoning | Accuracy | Mode 1 | 24 | 24 | +0 | 310/378/1.22x | Tie |
| 4 | Legal Analysis | Accuracy | Mode 1 | 24 | 24 | +0 | 238/338/1.42x | Tie |
| 5 | Research Synthesis | Mixed | Mode 1 | 23 | 23 | +0 | 307/303/0.99x | Tie |
| 6 | Business Decision | Mixed | Mode 1 | 24 | 24 | +0 | 281/372/1.32x | Tie |
| 7 | Compliance Check | Accuracy | Mode 1 | 24 | 24 | +0 | 298/367/1.23x | Tie |
| 8 | Document Analysis | Mixed | Mode 1 | 24 | 24 | +0 | 237/271/1.14x | Tie |
| 9 | Comparative Analysis | Mixed | Mode 2 | 24 | 25 | +1 | 254/204/0.80x | Optimized |
| 10 | Creative Brief | Creative | Mode 4 | 24 | 23 | -1 | 83/223/2.69x | Baseline |
| 11 | Context File (CLAUDE.md) | Harness | Mode 3 | 24 | 22 | -2 | 132/74/0.56x | Baseline |
| 12 | Async Rate Limiter (LRM) | Harness | Mode 3 | 21 | 24 | +3 | 409/930/2.27x | Optimized |
| | AVERAGE | | | 23.58 | 23.67 | +0.08 | 249.17/335.58/1.35x | |

Winner is based on the self-scored total, not a statistical test. The average words are arithmetic means; the average ratio shown is the ratio of total optimized response words to total baseline response words.

## 1. Overall Verdict

The optimized responses scored 23.67/25 on average versus 23.58/25 for baseline, a gain of 0.08 points, or 0.35% relative to the baseline score. On the 25-point scale this is about 0.33 percentage points. Eight cases tied, two favored optimization, and two favored baseline. Average visible response length rose from 249.17 to 335.58 words, or 1.35x. Including the raw or rewritten prompt, the visible input-plus-output ratio was 1.56x. For this sample, the small self-scored gain does not establish that the extra cost is generally worthwhile; the code precision finding provides specific value in Test 12.

The evaluator generated and judged both outputs, knew the conditions, selected the examples, and controlled the scoring. No independent judges, repeats, randomization, confidence intervals, actual token counts, latency, or model identity verification are available. The benchmark requires reading the entire evaluation prompt before beginning, which exposes later cases and conflicts with literal no-reading-ahead; each case was nevertheless written in order, with its baseline saved before its optimized prompt and response. In Test 12, the optimized prompt's precision gate was added after the baseline's boundary failure was observed. These limitations prevent a causal claim that the skill itself caused the measured difference.

## 2. Where It Helped Most

Test 12 gained 3 points. The explicit precision gate and executable harness led to a rational-accounting implementation that passed a reproducible case where the baseline issued a full bucket after only half a token had refilled. Both passed the same five common tests, so the concrete gain is the additional precision case and embedded verification, not evidence that the baseline had a scheduling race. Because the precision counterexample was discovered before the optimized prompt was written, it is not an independent comparison of equal unseen conditions.

Test 9 gained 1 point: a compact comparison matrix made premises and decision criteria easier to trace while preserving the same recommendation. This is one subjectively scored example, not proof of a general Lite-mode gain.

## 3. Where It Helped Least (or Hurt)

Tests 1 through 8 tied. The baseline already gave examples, calculations, primary sources or next actions, and the additional certificate labels primarily moved one point from structure to traceability. Test 10 lost 1 point: the creative scaffold was much longer than the copy and did not demonstrate a clear improvement in originality. Test 11 lost 2 points because the optimization removed an overview, directory list and PEP 8 explanation the original user explicitly requested, even though that pruning was mandated by the benchmark.

## 4. v4.0 Mode Evaluation (Max vs. Lite vs. Harness vs. Creative v2)

- **Max, Tests 1-8:** average response length was 1.23x baseline, with no mean score change. The repeated sections improved referenceability but not demonstrated correctness on these examples.
- **Lite, Test 9:** the response was 204 versus 254 words, or 0.80x, below the requested 1.5x ceiling. Including prompt text, the ratio was 1.07x. The key decision criteria and benchmark recommendation remained present, but one case cannot establish general quality preservation.
- **Harness, Tests 11-12:** the context file fell from 132 to 74 words and stayed below 150 lines, but did so by dropping explicit raw requirements. The optimized limiter passed its six embedded tests and the common five-test harness; these provide evidence for particular schedules, not proof that races are impossible. Both versions passed the common concurrency tests, and the optimized version fixed the separately tested precision defect. Test 12 response length was 2.27x baseline, substantially above the skill's approximate 1.1x to 1.3x harness estimate.
- **Creative v2, Test 10:** the selected copy uses a specific workday scene, but the baseline also does so. There is no independent originality assessment or repeated sampling. The three typicality values were invented subjective estimates, not calibrated probabilities, and the response grew to 2.69x because the scaffold was visible.

## 5. Accuracy vs. Mixed vs. Creative vs. Harness

| Task category | Tests | Baseline mean /25 | Optimized mean /25 | Delta |
|---|---|---:|---:|---:|
| Accuracy | 1, 2, 3, 4, 7 | 23.80 | 23.80 | 0.00 |
| Mixed | 5, 6, 8, 9 | 23.75 | 24.00 | +0.25 |
| Creative | 10 | 24.00 | 23.00 | -1.00 |
| Harness | 11, 12 | 22.50 | 23.00 | +0.50 |

The harness mean hides opposite effects: -2 for instruction fidelity in Test 11 and +3 for the verified code defect in Test 12. Persona choices followed the skill's routing, but the prompts also changed in many other ways. There is no persona-only control, so these data cannot establish whether PRISM-based calibration caused any improvement or harm.

## 6. Traceability Specifically

Mean traceability rose from 3.92/5 to 4.83/5, a gain of 0.92 points. Tests 1-9 each received +1 because the optimized responses linked conclusions to explicit traces; Test 12 rose from 3 to 5 with runnable checks and a counterexample. Tests 10 and 11 tied at 4. In the analytical cases the labels improved navigation, but the underlying evidence was often already present in the baseline. A cited label or self-check is not independent evidence that its claim is true.

## 7. Token Cost vs. Value

| Mode | Tests | Mean baseline response words | Mean optimized response words | Response ratio of means | Prompt plus response ratio |
|---|---|---:|---:|---:|---:|
| Max | 1-8 | 264.00 | 324.50 | 1.23x | 1.45x |
| Lite | 9 | 254.00 | 204.00 | 0.80x | 1.07x |
| Creative | 10 | 83.00 | 223.00 | 2.69x | 2.91x |
| Harness | 11-12 | 270.50 | 502.00 | 1.86x | 1.92x |
| All | 1-12 | 249.17 | 335.58 | 1.35x | 1.56x |

Approximate word counts use a Unicode word regex, retaining code identifiers and visible label text while excluding Markdown link destinations and code-fence markers. Decimal numbers and code syntax are only approximated by this method. The prompt-plus-response comparison includes the raw prompt on the baseline side and the optimized prompt's copyable text on the optimized side; it excludes the evaluator's classification and rationale, external search results, hidden reasoning, tool calls, and this evaluation report. Actual model tokens were not measured, so none of these word ratios is a token-cost measurement. Ratios of mean lengths are reported above; the unweighted mean of the 12 individual response ratios is 1.35x.

## 8. Failure Modes Observed

1. **Instruction loss:** Test 11 removed explicitly requested sections. A context-file heuristic should not silently override a user's artifact requirements.
2. **Scaffold bloat:** Test 10 exposed three candidate notes and four structural labels around a short product description. Test 12 embedded a full harness, which is useful for verification but more than doubled response length.
3. **Trace theater:** Tests 1-8 often repeat information already present in the baseline; an identifier can create an impression of rigor without adding a source or a new check.
4. **Uncalibrated probabilities:** Test 10's typicality estimates were generated by the same model, with no measured distribution or sampling validation. A numerical threshold alone does not demonstrate rarity.
5. **False confidence in testing:** Tests 11-12 show that a shorter file and a passing harness do not respectively prove superior agent performance or all-schedule race freedom. The Test 12 baseline's finite tests initially passed despite its precision bug.
6. **Benchmark-to-library mismatch:** the evaluation's numbered domain targets mostly disagree with the actual library; specifically, actual Template 12 is creative writing, not an LRM harness. Forcing the advertised numbers would test the wrong templates.
7. **Evidence scope:** the skill's broad claims across domains and statement that its sources are peer reviewed were not established by this benchmark. For example, [Ugare and Chandra's paper](https://arxiv.org/abs/2603.01896) describes code-reasoning experiments; extending its results to all domains is an inference. Its arXiv record alone does not establish peer-review status.

## 9. Recommendations for v4.1 Skill Improvement

1. Add an explicit instruction-fidelity gate for all modes: distinguish user-required deliverable content from optional, inferable additions. Preserve explicit requests or present a concrete tradeoff when authorized to change scope (Gloaguen et al., 2026).
2. Add a real algorithmic harness template or correct the benchmark's mapping, and identify templates by stable name as well as number. Include concurrency, timeout, cancellation, numeric boundary and cross-thread test recipes (Lee et al., 2026; Ugare & Chandra, 2026).
3. Make trace depth adaptive: use direct claims with source links for simple or already well-supported answers; add identifiers where they materially aid a multi-step audit (Ugare & Chandra, 2026).
4. Keep creative candidate generation private or optional when the user asks for copy only. Label typicality estimates as uncalibrated, and evaluate originality with blind repeated samples and independent raters rather than a self-assigned threshold (Zhang et al., 2025; Madler, 2026).
5. Count complete input and output, and measure actual tokens and latency by mode. Report quality and cost across repeated randomized paired runs with independent, blinded scoring; separate compliance with the original prompt from compliance with the optimized prompt (Ugare & Chandra, 2026; Cao, Jiang & Xu, 2026).
6. Require tested, untested, and assumption labels for verification gates. Include deterministic counterexamples as well as stress tests, and reserve proof claims for properties actually proven (Lee et al., 2026; Yin et al., 2026).
7. Audit bibliographic claims and version each source; distinguish preprints from peer-reviewed publications and do not generalize a domain-specific effect to unrelated domains without evidence (Ugare & Chandra, 2026; Hu, Rostami & Thomason, 2026).
