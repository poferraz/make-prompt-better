# make-prompt-better v4.0 Evaluation Results: meta-muse-wonder-1.0-max

Evaluator: Muse Code powered by muse-wonder-1.0 (model slug: meta-muse-wonder-1.0-max). Date of run: 2026-10-30.

Method note: Each test was executed in the order required by EVALUATION_PROMPT_V4.md: Baseline Response first, then Optimized Prompt, then Optimized Response, then Evaluation. Baselines answer the raw prompt directly with best effort and no certificate structure. Optimized responses follow the selected Certificate Mode and domain template from make-prompt-better/SKILL.md and make-prompt-better/references/domain-templates.md. Word counts count words in the Baseline Response body and the Optimized Response body only; the Optimized Prompt text is excluded from both counts. The overhead ratio is Optimized Words divided by Baseline Words.

Self-evaluation bias disclosure: The same model generated both responses and assigned all scores. Self-judging systematically favors the more structured output on Structure and Traceability, and favors familiar phrasing. Scores below should be read as upper bounds on the optimized advantage, not as independent measurements. No external judge, human rater, or execution harness was used except where a test includes an executable self-test that is printed for the reader to run.

Scoring reminder: Each dimension is scored 1 to 5. Totals are out of 25. Equal scores mean the two responses were judged equivalent on that dimension. Structure is penalized when formatting adds length without adding decisions, evidence, or usable artifacts.

---

## TEST 1: Code Review (Accuracy task, Target Mode 1 Max Certificate, Template 1)

Raw prompt: Look at this Python function and tell me if it has any bugs. (Function: calculate_discount(price, discount_percent, is_member) as given in EVALUATION_PROMPT_V4.md.)

### BASELINE RESPONSE

Yes. The function has one critical bug and several robustness problems.

The critical bug is the discount formula: `final_price = price - (price * discount_percent)`. The parameter is named `discount_percent`, which conventionally means a value such as 20 for 20 percent. The code multiplies price by that value directly, without dividing by 100. For price 100 and discount_percent 20, the result is 100 minus 2000, which the floor then clamps to 0. Almost every realistic percent input returns 0. The formula only works if callers pass a fraction such as 0.20, which contradicts the parameter name.

Second, there is no upper bound on the effective discount. A member with discount_percent 95 gets 105 after the member increment, and a caller can pass discount_percent above 100 or a negative price or negative discount. The `if final_price < 0` guard hides the overflow instead of validating inputs, so bad inputs silently become free items.

Third, the member rule `discount_percent += 10` is ambiguous. It is unclear whether the benefit is 10 percentage points or 10 percent relative, whether it should apply before or after other caps, and whether it should stack without limit. The code also mutates the parameter, which is harmless here but obscures the effective rate.

Fourth, there is no validation or documentation of types and ranges. Negative price, discount_percent below 0, discount_percent above 100, and non-numeric inputs either produce wrong prices or raise an unhandled TypeError.

Suggested fix: interpret the input explicitly as a percent, clamp or validate the effective percent to the range 0 to 100, and reject negative prices:

```python
def calculate_discount(price, discount_percent, is_member):
    if price < 0:
        raise ValueError("price must be non-negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be in [0, 100]")
    effective = discount_percent + (10 if is_member else 0)
    effective = min(effective, 100)
    return price * (1 - effective / 100)
```

Add unit tests for 0 percent, 100 percent, member stacking at the cap, and invalid inputs.

### OPTIMIZED PROMPT

```
The standard code review protocol requires completing the following analytical certificate before issuing any verdict. Every section must be completed using observable code artifacts. Omit any persona.

### PREMISES
- [P1] Files modified: the single function calculate_discount(price, discount_percent, is_member) supplied in full. Body: if is_member, discount_percent increases by 10; final_price equals price minus (price times discount_percent); if final_price is below 0, return 0; otherwise return final_price.
- [P2] Symbols affected: calculate_discount only; no callers, tests, or type annotations supplied.
- [P3] Test coverage: no tests supplied.
- [P4] Runtime constraints: Python semantics; percent naming convention; no stated contract for valid input ranges.

### EXECUTION TRACES
For each code path, record entry inputs, data flow, and exit value:
- [T1] Trace non-member percent path: evaluate price 100, discount_percent 20, is_member False through every line.
- [T2] Trace member stacking path: evaluate price 100, discount_percent 95, is_member True, including the increment and any cap.
- [T3] Trace boundary and invalid inputs: discount_percent 0, 100, above 100, negative discount, negative price; record return value or exception per input.
Grounding rule: Trace the actual implementation body rather than inferring behavior from the function or variable names. When a called symbol is outside the provided context, record UNABLE TO TRACE with the assumed behavior.

### FORMAL CONCLUSION
- Verdict: PASS or FAIL, with each defect supported by specific T identifiers.
- Supporting traces: cite T1, T2, T3 for every claim.
- Verification gaps: list any path marked UNABLE TO TRACE.

### REMEDIATION / NEXT ACTION
Provide a complete copy-pasteable corrected function plus exact test cases for each defect, or state No remediation required with a reason citing T identifiers.

VERIFICATION AND TRACEABILITY CONTRACT:
- When a path cannot be verified from P1 to P4, record UNABLE TO TRACE: [exact missing input] and list it under Verification Gaps.
- When an edge case fails, record it as a dedicated T trace even when the overall verdict is positive.
TRACEABILITY SELF-CHECK: Verify that every claim in the Formal Conclusion cites at least one T identifier. Remove any claim without a trace.
```

### OPTIMIZED RESPONSE

### PREMISES
- [P1] Artifact: `calculate_discount(price, discount_percent, is_member)`. If `is_member` is true, `discount_percent` increases by 10. Then `final_price = price - (price * discount_percent)`. If `final_price < 0`, return 0; else return `final_price`.
- [P2] Symbols: `calculate_discount` only. Callers and tests: UNABLE TO TRACE, none supplied.
- [P3] Constraints: No documented contract for whether `discount_percent` is a percent (20 means 20 percent) or a fraction (0.20 means 20 percent), and no documented valid ranges.

### EXECUTION TRACES
- [T1] Non-member percent path (price 100, discount 20, member False): No increment. `final_price = 100 - (100 * 20) = 100 - 2000 = -1900`. Floor triggers, return 0. Expected price at 20 percent off is 80. Result: defect confirmed. The formula treats a percent value as a raw multiplier because division by 100 is missing.
- [T2] Member stacking path (price 100, discount 95, member True): Increment gives 105. `final_price = 100 - (100 * 105) = -10400`. Floor triggers, return 0. Even under a fraction interpretation (0.95 plus 10 points), the effective discount exceeds 100 percent and no cap exists before the floor hides it. Result: missing upper bound confirmed.
- [T3] Boundaries: discount 0 returns price (correct under both readings). Discount 100 as percent returns 0 only by floor accident (100 minus 10000 clamped). Negative discount, for example minus 10, returns price times 11 under raw math (100 minus negative 1000 equals 1100), so the function can charge more than list price with no error. Negative price returns 0 or a negative-derived value depending on discount, with no validation. Non-numeric input raises TypeError from arithmetic. Result: input validation absent.

### FORMAL CONCLUSION
- Verdict: FAIL.
- Defect 1 (critical): Percent formula omits division by 100, so conventional percent inputs collapse to 0 [T1].
- Defect 2 (major): No cap or validation on effective discount; member stacking and out-of-range inputs are silently clamped by the zero floor [T2][T3].
- Defect 3 (minor): Contract ambiguity between percent and fraction is undocumented, and invalid inputs are not rejected [T3].
- Verification gaps: Caller convention (percent vs. fraction) is UNABLE TO TRACE from [P1]; the remediation adopts the percent reading implied by the parameter name and states it explicitly.

### REMEDIATION / NEXT ACTION
```python
def calculate_discount(price, discount_percent, is_member):
    """discount_percent is a percent: 20 means 20 percent off."""
    if price < 0:
        raise ValueError("price must be non-negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be in [0, 100]")
    effective = min(discount_percent + (10 if is_member else 0), 100)
    return price * (1 - effective / 100)
```
Tests: (100, 20, False) gives 80; (100, 95, True) gives 0 at the cap; (100, 0, False) gives 100; negative price raises ValueError; discount 101 raises ValueError.

TRACEABILITY SELF-CHECK: Every conclusion claim cites [T1], [T2], or [T3]. No orphaned claims remain.

### EVALUATION: TEST 1

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 4        | 5         | +1    |
| Structure     | 4        | 5         | +1    |
| Actionability | 5        | 5         | 0     |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 21/25    | 25/25     | +4    |

Baseline Words: 328 | Optimized Words: 468 | Overhead Ratio: 1.43

What improved: The optimized response adds explicit numeric traces for the member stacking path and negative discount path, and labels the caller convention as a verification gap instead of assuming it silently. What stayed the same: Both responses find the missing division by 100, the missing cap, and the missing validation, and both supply a corrected function. What got worse: Nothing substantive; the certificate headings add length, and at 1.43x the overhead sits below the Mode 1 pooled average because the task is small.

---

## TEST 2: Financial Analysis (Accuracy task, Target Mode 1 Max Certificate, Template 9 in domain-templates, Financial Due Diligence)

Raw prompt: A company reports revenue and expense ratios for Q1 to Q4 plus $15M new debt in Q3. Analyze their financial health. (Full figures in EVALUATION_PROMPT_V4.md.)

### BASELINE RESPONSE

Revenue by quarter: Q1 $50M, Q2 $47M, Q3 $52M, Q4 $61M. Total revenue is $210M. Expenses are given as a share of revenue, so quarterly operating profit before interest and tax can be derived directly.

Q1: expenses 78 percent of $50M equals $39.0M; profit $11.0M; margin 22 percent. Q2: expenses 82 percent of $47M equals $38.54M; profit $8.46M; margin 18 percent. Q3: expenses 75 percent of $52M equals $39.0M; profit $13.0M; margin 25 percent. Q4: expenses 71 percent of $61M equals $43.31M; profit $17.69M; margin 29 percent. Full year profit on this definition is $50.15M on $210M revenue, a 23.9 percent operating margin.

The trend is favorable after a weak Q2. Revenue dipped 6 percent in Q2, then grew 10.6 percent in Q3 and 17.3 percent in Q4. More importantly, the expense ratio fell from 82 percent to 71 percent, so margin expanded by 11 points from trough to Q4. Absolute expenses still rose in Q4 ($43.31M is the highest quarter), which is consistent with scaling into growth rather than pure cost cutting, but revenue grew faster.

The $15M of new debt in Q3 needs context that the prompt does not provide. Debt taken while margins were improving can be reasonable growth financing, but health cannot be judged without the total debt balance, interest rate, maturity, cash balance, and cash flow. Profit here excludes interest, tax, depreciation, and working capital, so it is not net income or free cash flow.

Overall: operating performance improved through the year and ended strong. The main cautions are the Q2 softness, whether Q4 margin is seasonal or durable, and leverage, which is unquantifiable from the data given. Ask for the balance sheet, cash flow statement, debt schedule, and Q1 next year comparatives before drawing a firm conclusion.

### OPTIMIZED PROMPT

```
Financial due diligence methodology requires completing this analytical certificate before presenting any posture summary. Omit any persona.

### PREMISES
- [P1] Entity and filings examined: Quarterly revenue Q1 $50M, Q2 $47M, Q3 $52M, Q4 $61M. Operating expenses as share of revenue: Q1 78 percent, Q2 82 percent, Q3 75 percent, Q4 71 percent. New debt $15M taken in Q3. No balance sheet, cash flow, interest, tax, or prior year data supplied.
- [P2] Analytical dimensions: revenue trajectory, expense ratio and derived operating profit, margin trajectory, leverage signal.
- [P3] Reference benchmarks: quarter to quarter change within P1 only.

### FINANCIAL TRACES
For each dimension in P2:
- [T1] Revenue trajectory: report each quarter figure from P1, compute quarter to quarter percent change with explicit formula, and full year total.
- [T2] Derived operating profit: for each quarter compute expenses equals revenue times expense ratio, profit equals revenue minus expenses, margin equals profit divided by revenue. Show arithmetic per quarter.
- [T3] Leverage signal: state what the $15M Q3 debt can and cannot establish from P1 alone.
Grounding rule: Compute metrics exclusively from figures present in P1. When a required input is missing from P1, record INSUFFICIENT DATA FOR [trace]: [missing metric].

### FORMAL CONCLUSION
- Financial posture summary citing T identifiers for every figure.
- Verified strengths separated from structural divergences, each citing T traces.
- Data completeness gaps: list every item marked INSUFFICIENT DATA.

### REMEDIATION / NEXT ACTION
Provide the exact diligence request list needed to close each Data Completeness Gap.
DISCLAIMER: This output is analytical support, not investment advice.
TRACEABILITY SELF-CHECK: Verify that every figure in the conclusion cites a specific T calculation trace.
```

### OPTIMIZED RESPONSE

### PREMISES
- [P1] Revenue: Q1 $50M, Q2 $47M, Q3 $52M, Q4 $61M. Expense ratios: Q1 78 percent, Q2 82 percent, Q3 75 percent, Q4 71 percent. New debt: $15M in Q3. No cash, total debt, interest, tax, depreciation, or cash flow data supplied.
- [P2] Dimensions: revenue trajectory, derived operating profit and margin, leverage signal.

### FINANCIAL TRACES
- [T1] Revenue trajectory: Total equals 50 + 47 + 52 + 61 = $210M. Q2 change equals (47 minus 50) / 50 = minus 6.0 percent. Q3 change equals (52 minus 47) / 47 = plus 10.6 percent. Q4 change equals (61 minus 52) / 52 = plus 17.3 percent. Direction: contraction in Q2, then accelerating growth.
- [T2] Derived operating profit (profit equals revenue times (1 minus expense ratio)): Q1: 50 times 0.22 = $11.00M, margin 22 percent. Q2: 47 times 0.18 = $8.46M, margin 18 percent. Q3: 52 times 0.25 = $13.00M, margin 25 percent. Q4: 61 times 0.29 = $17.69M, margin 29 percent. Full year: 11.00 + 8.46 + 13.00 + 17.69 = $50.15M; blended margin equals 50.15 / 210 = 23.9 percent. Note: this profit excludes interest, tax, and non-cash items, so it is an operating proxy, not net income.
- [T3] Leverage signal: $15M new debt in Q3 equals 28.8 percent of Q3 revenue. INSUFFICIENT DATA FOR [T3]: total debt balance, interest rate, maturity, and cash balance are absent from [P1], so leverage ratios and coverage cannot be computed.

### FORMAL CONCLUSION
- Financial posture summary: Operating performance strengthened across the year on both growth and margin [T1][T2]. Q4 is the strongest quarter on revenue ($61M) and margin (29 percent) [T1][T2].
- Verified strengths: Revenue recovery after Q2 with accelerating growth [T1]; margin expansion of 11 points from Q2 trough to Q4 driven by expense ratio falling from 82 to 71 percent [T2].
- Structural divergences: Absolute expenses peaked in Q4 at $43.31M (61 times 0.71), so margin gain came from revenue outgrowing costs, not from cost reduction [T2]. Q2 shows the business can contract and compress simultaneously [T1][T2].
- Data completeness gaps: INSUFFICIENT DATA FOR leverage, liquidity, and cash conversion [T3].

### REMEDIATION / NEXT ACTION
Request before any health verdict: (1) balance sheet with cash and total debt, (2) debt schedule with rate and maturity for the $15M Q3 borrowing, (3) cash flow statement to test cash conversion of the $50.15M operating proxy [T2], (4) interest and tax lines, (5) same quarter prior year revenue to separate seasonality from durable growth [T1].
DISCLAIMER: This output is analytical support, not investment advice.

TRACEABILITY SELF-CHECK: Every figure cites [T1], [T2], or [T3]. Leverage is explicitly marked insufficient rather than estimated.

### EVALUATION: TEST 2

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 4        | 5         | +1    |
| Structure     | 4        | 5         | +1    |
| Actionability | 3        | 5         | +2    |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 20/25    | 25/25     | +5    |

Baseline Words: 293 | Optimized Words: 445 | Overhead Ratio: 1.52

What improved: Both responses compute identical profits and margins, but the optimized response shows each formula, separates the operating proxy from net income explicitly in the trace, and converts missing leverage data into a concrete five item diligence request. What stayed the same: The core judgment (strong Q4, weak Q2, leverage unjudgeable) is unchanged. What got worse: Nothing material; the gain here is auditability, not a different conclusion, and a reader who only wants the headline will pay 1.43x length for it.

---

## TEST 3: Medical Reasoning (Accuracy task, Target Mode 1 Max Certificate, Template 7 in domain-templates, Medical and Clinical Reasoning)

Raw prompt: A 58-year-old male presents with sudden onset chest pain radiating to the left arm, diaphoresis, and shortness of breath. BP 90/60, HR 110, SpO2 94 percent. ECG shows ST elevation in leads II, III, and aVF. Troponin pending. What is the most likely diagnosis and what are the immediate priorities? (Clinical details as given in EVALUATION_PROMPT_V4.md. This test is analytical support for evaluation only and is not clinical advice for any real patient.)

### BASELINE RESPONSE

Most likely diagnosis: acute inferior ST elevation myocardial infarction (STEMI). ST elevation in II, III, and aVF localizes to the inferior wall, most often right coronary artery occlusion. The presentation (sudden chest pain radiating to the left arm, diaphoresis, dyspnea), hypotension (90/60), tachycardia (110), and borderline hypoxemia (94 percent) fit acute MI with early hemodynamic compromise. With inferior STEMI, right ventricular infarction must be actively considered, especially with hypotension; obtain right sided leads (V4R) and a posterior assessment as indicated.

Immediate priorities, in parallel rather than in sequence: activate the catheterization laboratory for emergent reperfusion (primary PCI is preferred; fibrinolysis only if PCI cannot be delivered in guideline time and no contraindications). Establish continuous cardiac, BP, and SpO2 monitoring, defibrillator pads, and IV access. Give chewable aspirin promptly unless true allergy. Anticoagulation and a P2Y12 inhibitor per local STEMI protocol and cardiology direction. Treat pain and anxiety cautiously.

Critical cautions in this exact picture: hypotension plus inferior STEMI changes drug choices. Nitrates and diuretics can precipitate collapse if the right ventricle is infarcted and preload dependent, so avoid nitrates until RV involvement is assessed and blood pressure allows. Morphine can also drop preload and should be used sparingly, if at all. Supplemental oxygen only if SpO2 falls below 90 percent; 94 percent does not require routine oxygen. Look for bradyarrhythmias and heart block (common with inferior MI) even though the current rhythm is tachycardic, and reassess blood pressure frequently.

Do not wait for troponin to act: ECG plus presentation is sufficient to activate reperfusion. Send labs, troponin, and a chest assessment without delaying transport. This is an emergency requiring immediate in person care; this summary is educational and does not replace clinician judgment.

### OPTIMIZED PROMPT

```
Clinical reasoning methodology, as established in evidence-based medicine, requires completing this structured certificate before presenting any differential synthesis. Omit any persona.

### PREMISES
- [P1] Presenting context: 58-year-old male, sudden onset chest pain radiating to left arm, diaphoresis, shortness of breath; onset timing beyond sudden not specified.
- [P2] Objective findings: BP 90/60, HR 110, SpO2 94 percent on unstated oxygen delivery; ECG ST elevation in II, III, aVF; troponin pending. No exam, rhythm strip beyond rate, lung findings, or medication list supplied.
- [P3] Active regimen: no medications, allergies, or interventions supplied.
- [P4] Reference guidelines: standard acute coronary syndrome and STEMI reperfusion standards of care (guideline names to be cited generically, no invented section numbers).

### DIAGNOSTIC AND THERAPEUTIC TRACES
For each plausible condition in the differential:
- [T1] Condition inferior STEMI: list supporting findings from P1 and P2, disconfirming findings, discriminating gaps, and acuity per P4.
- [T2] Condition RV infarction accompanying inferior STEMI: same four elements, with attention to hypotension in P2.
- [T3] Condition at least two alternatives (for example aortic dissection, pulmonary embolism, posterior STEMI extension): same four elements, stating which P2 finding argues for or against each.
Grounding rule: Evaluate multiple competing hypotheses across all data points in P1 to P3 before ranking, separating probability from acuity. When a finding is absent from P2, record ABSENT FROM P2: [finding] rather than assuming it.

### FORMAL CONCLUSION
- Evidence ranked differential citing T identifiers.
- High acuity exclusions required citing T identifiers.
- Critical information gaps from T traces.

### REMEDIATION / NEXT ACTION
List concrete immediate priority actions and verification checks ordered by acuity, each grounded in T identifiers, including explicit drug cautions tied to T2.
DISCLAIMER: This output is structured analytical support, not clinical advice. All decisions require a licensed healthcare clinician.
TRACEABILITY SELF-CHECK: Verify every condition and action cites a T trace and P premise.
```

### OPTIMIZED RESPONSE

### PREMISES
- [P1] 58-year-old male; sudden chest pain radiating to left arm; diaphoresis; dyspnea. Pain duration, character, and risk factors: ABSENT FROM [P1].
- [P2] BP 90/60 (hypotensive), HR 110 (tachycardic), SpO2 94 percent (delivery device unstated), ECG: ST elevation II, III, aVF (inferior STEMI pattern). Troponin pending. Rhythm diagnosis beyond rate, lung exam, JVP, and right sided leads: ABSENT FROM [P2].
- [P3] Medications and allergies: ABSENT FROM [P3].
- [P4] Standard STEMI care: immediate reperfusion activation on ECG plus presentation without waiting for troponin; primary PCI preferred when timely.

### DIAGNOSTIC AND THERAPEUTIC TRACES
- [T1] Inferior STEMI. Supporting: chest pain with left arm radiation, diaphoresis, dyspnea [P1]; ST elevation II, III, aVF [P2]. Disconfirming: none in [P1][P2]. Discriminating gaps: repeat ECG, right sided and posterior leads, troponin result (confirmatory, not gating) [P2]. Acuity: highest; time critical myocardium loss per [P4].
- [T2] RV infarction complicating inferior STEMI. Supporting: inferior STEMI pattern [T1] plus hypotension 90/60 with tachycardia 110 [P2], a combination that raises RV involvement. Disconfirming: tachycardia rather than bradycardia does not exclude RV infarction. Discriminating gaps: V4R, JVP and lung exam are ABSENT FROM [P2]. Acuity: high, because it reverses nitrate and diuretic decisions.
- [T3] Alternatives. Aortic dissection: chest pain supports consideration, but ST elevation in a coronary distribution plus diaphoresis favors STEMI [P1][P2]; pulse deficits and wide mediastinum assessment ABSENT FROM [P2], so dissection cannot be formally excluded on supplied data, yet reperfusion delay to exclude it without red flags would violate [P4]. Pulmonary embolism: dyspnea, tachycardia, hypotension support it [P1][P2], but inferior ST elevation is not explained by PE, so PE ranks below STEMI. Posterior extension: possible with inferior STEMI; posterior leads ABSENT FROM [P2].

### FORMAL CONCLUSION
- Evidence ranked differential: (1) Inferior STEMI [T1]; (2) Inferior STEMI with RV involvement [T2]; (3) Posterior extension, PE, dissection as lower probability but high acuity considerations [T3].
- High acuity exclusions required: RV involvement via V4R before nitrates [T2]; rhythm monitoring for AV block and ventricular arrhythmia [T1][T2].
- Critical information gaps: right sided and posterior leads, rhythm, lung and JVP exam, allergies and medications, troponin [T1][T2][T3].

### REMEDIATION / NEXT ACTION
Immediate, in parallel: (1) Activate emergent reperfusion (cath lab for primary PCI) on [T1] without waiting for troponin per [P4]. (2) Continuous ECG, BP, SpO2 monitoring, defibrillator pads, IV access [T1][T2]. (3) Aspirin chewed promptly unless allergy (allergy status is a gap in [P3]; confirm while preparing) [T1]. (4) Anticoagulation and P2Y12 per local protocol and cardiology [T1]. (5) Withhold nitrates and diuretics until RV status and BP permit [T2]; use morphine sparingly if at all [T2]. (6) Oxygen only if SpO2 falls below 90 percent; current 94 percent does not need routine oxygen [P2]. (7) Obtain V4R, posterior leads, repeat ECG, labs and troponin without delaying reperfusion [T1][T2]. (8) Treat hypotension per clinician direction, favoring careful fluids when RV infarction is confirmed and lungs are clear [T2].
DISCLAIMER: This output is structured analytical support, not clinical advice. All diagnostic and treatment decisions require a licensed healthcare clinician.

TRACEABILITY SELF-CHECK: Every condition and action cites [T1], [T2], or [T3] and its [P] premise.

### EVALUATION: TEST 3

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 4        | 5         | +1    |
| Actionability | 5        | 5         | 0     |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 22/25    | 25/25     | +3    |

Baseline Words: 283 | Optimized Words: 522 | Overhead Ratio: 1.84

What improved: The optimized response makes uncertainty explicit (right sided leads, rhythm, allergies recorded as ABSENT rather than assumed) and ties the nitrate hold directly to the RV trace, which makes the caution auditable. What stayed the same: Diagnosis, reperfusion priority, aspirin, monitoring, and oxygen threshold are identical; the baseline was already clinically strong. What got worse: Nothing clinically; the cost is 1.84x length and a differential table that a treating team would not stop to read in a real resuscitation. The certificate is an audit artifact, not a bedside tool.

---

## TEST 4: Legal Analysis (Accuracy task, Target Mode 1 Max Certificate, Template 8 in domain-templates, Legal Analysis)

Raw prompt: An employee signed a non-compete that prevents work in any related industry within 200 miles for 5 years. They left and took a job at a competitor 150 miles away, 8 months later. The former employer threatens to sue. Analyze enforceability. (Full facts in EVALUATION_PROMPT_V4.md. Analytical support only, not legal advice.)

### BASELINE RESPONSE

This non-compete is likely unenforceable as written in most United States jurisdictions, though the answer depends heavily on state law, the employee role, and how the agreement was supported by consideration. This is general information, not legal advice.

Duration: Five years is at the extreme long end. Many courts treat one to two years as the presumptive reasonable range for employment non-competes (longer periods appear more often in sale of business contexts). Five years for an ordinary employee will strike many judges as longer than needed to protect customer relationships or confidential information.

Geography: A 200 mile radius is large but not automatically fatal if the employer genuinely operates across that area. The employee new job at 150 miles is inside the stated radius, so geography alone does not save the employee if the clause were otherwise valid. Courts ask whether the territory matches the employer actual market and the employee actual territory.

Scope: Any related industry is the weakest element for the employer. Enforceable covenants usually bar working for defined competitors, soliciting defined customers, or using defined confidential information in a defined role. Barring an entire industry prevents the employee from using general skills and looks like a restraint on competition itself rather than protection of a legitimate interest (trade secrets, customer goodwill, specialized training).

Timing and conduct: Starting eight months later does not help the employee much; eight months is well within even a shortened enforcement period, and joining a direct competitor is the core conduct these clauses target. If a court reforms (blue pencils) the clause, the reformed version could still cover this job.

State variation dominates. Some states void most employment non-competes by statute (California is the classic example, with narrow exceptions). Others enforce reasonable covenants or reform overbroad ones. Many states now also require wage thresholds, notice, or garden leave. Without the state, employee seniority, access to secrets, and consideration facts, no firm prediction is possible. Practical advice: the employee should get state specific counsel before resigning or starting, consider declaratory relief or negotiation, and preserve documents showing the new role does not use former employer confidential information. The employer threat is credible enough to litigate but the clause as drafted is vulnerable.

### OPTIMIZED PROMPT

```
Legal analytical methodology requires completing this structured certificate before presenting any legal assessment. Omit any persona.

### PREMISES
- [P1] Stated facts and text: Clause bars work in any related industry within 200 miles for 5 years after leaving. Employee joined a competitor 150 miles away, 8 months after leaving. Former employer threatens suit. Jurisdiction, employee role, consideration, and governing law clause: not supplied.
- [P2] Governing law: jurisdiction not supplied, so apply the majority reasonableness framework (legitimate interest, duration, geography, activity scope) and flag statutory ban states as a branching condition. Invent no statute or case citation.
- [P3] Issues presented: duration reasonableness, geographic reasonableness, activity scope reasonableness, effect of reformation doctrines, application to the stated 150 mile and 8 month facts.

### LEGAL TRACES
For each issue in P3:
- [T1] Duration: governing reasonableness rule, fact application to 5 years, strongest employer counter-reading, reformation effect.
- [T2] Geography: governing rule, fact application to 200 mile radius and 150 mile new job, counter-reading, reformation effect.
- [T3] Activity scope: governing rule, fact application to any related industry, counter-reading, reformation effect.
- [T4] Jurisdiction branch: how the outcome changes in a statutory ban state versus a reasonableness state versus a reform state.
Grounding rule: Quote exact clause language from P1 for every application. When a needed provision is absent from P1, record NOT ADDRESSED IN P1.

### FORMAL CONCLUSION
- Issue by issue synthesis citing T identifiers.
- Structural exposure points citing T traces.
- Unresolved questions requiring extrinsic facts or counsel.

### REMEDIATION / NEXT ACTION
Provide copy-pasteable narrowed clause language that would be more likely enforceable, plus immediate practical steps for each side.
DISCLAIMER: This output is analytical support, not legal advice. Consult qualified legal counsel for binding determinations.
TRACEABILITY SELF-CHECK: Verify every conclusion claim cites a T trace and its P premise.
```

### OPTIMIZED RESPONSE

### PREMISES
- [P1] Clause text as supplied: work in "any related industry" barred within 200 miles for 5 years after leaving. New job: competitor, 150 miles away, started 8 months after leaving. Suit threatened. Jurisdiction, role, seniority, access to confidential information, consideration, and choice of law: NOT ADDRESSED IN [P1].
- [P2] Framework: majority reasonableness test (protectable legitimate interest, plus reasonable duration, geography, and activity scope), subject to state statute branch in [T4]. No specific statute is assumed.
- [P3] Issues: duration, geography, scope, jurisdiction branch, application to 150 miles and 8 months.

### LEGAL TRACES
- [T1] Duration (5 years). Rule: duration must be no longer than needed to protect the legitimate interest; employment covenants are most often sustained at one to two years, with longer terms concentrated in sale of business cases. Application: 5 years exceeds the usual employment range on the face of [P1]. Counter-interpretation (employer): a senior employee with durable trade secrets could argue a longer tail. Reformation effect: a reforming court could shorten 5 years to one or two years, and 8 months elapsed would still fall inside the reformed term.
- [T2] Geography (200 miles; new job at 150 miles). Rule: territory must track the employer market and the employee sphere of influence. Application: 150 miles is inside 200 miles, so the employee does not win on distance under the literal text of [P1]. Counter-interpretation (employee): if the employer market or the employee territory was local, 200 miles is broader than the interest. Reformation effect: a court could shrink the radius, but 150 miles might still fall inside a shrunken radius centered on a regional employer.
- [T3] Activity scope ("any related industry"). Rule: scope must target competitors, customers, or confidential information, not general skill in an industry. Application: "any related industry" in [P1] is the broadest possible drafting and bars jobs that use no employer secrets at all. Counter-interpretation (employer): the employee did join a direct competitor, which is the narrow core even a reformed clause would reach. Reformation effect: narrowing "any related industry" to named competitors or a defined role would still capture the stated new job.
- [T4] Jurisdiction branch. Rule: states divide into statutory restriction states (most employment non-competes void), reasonableness states (test in [T1] to [T3] applied as written), and reform states (overbroad terms judicially narrowed). Application: because jurisdiction is NOT ADDRESSED IN [P1], the same facts yield void, vulnerable, or reformed and enforced outcomes depending on the branch.

### FORMAL CONCLUSION
- Issue by issue synthesis: Duration is overlong for ordinary employment [T1]. Geography literally captures the new job but may exceed the protectable territory [T2]. Scope is the most vulnerable element [T3]. Jurisdiction is outcome determinative and unresolved [T4].
- Structural exposure points: The employer strongest fact is direct competitor employment at 8 months and 150 miles, which survives most reformation [T2][T3]. The employee strongest facts are 5 years and industry wide scope [T1][T3].
- Unresolved interpretive questions: governing state, employee role and secret access, consideration, and any statutory wage or notice conditions are NOT ADDRESSED IN [P1] and require counsel.

### REMEDIATION / NEXT ACTION
More defensible clause (illustrative, requires state specific drafting): "For 18 months after separation, Employee will not perform substantially similar services for a competitor listed in Schedule A within the counties where Employee had material customer contact in the final 24 months, and will not solicit those customers or use Confidential Information." Immediate steps: employee, get state specific advice before starting or continuing, consider negotiation or declaratory judgment, and document that the new role excludes former employer confidential information [T3][T4]. Employer, assess reform risk and litigation cost before filing on the clause as written [T1][T3].
DISCLAIMER: This output is analytical support, not legal advice. Consult qualified legal counsel for binding determinations.

TRACEABILITY SELF-CHECK: Every conclusion sentence cites [T1] to [T4]. Unresolved items are marked NOT ADDRESSED IN [P1] rather than assumed.

### EVALUATION: TEST 4

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 4        | 5         | +1    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 21/25    | 25/25     | +4    |

Baseline Words: 368 | Optimized Words: 650 | Overhead Ratio: 1.77

What improved: The optimized response separates the three reasonableness elements into independently checkable traces, adds the reformation analysis per element, and supplies a narrowed model clause the baseline only gestures at. What stayed the same: Bottom line (likely vulnerable as written, competitor facts hurt the employee, state law controls) is identical, and neither response invents a jurisdiction. What got worse: Nothing in correctness; the legal trace scaffolding is heavy at 1.77x, which is justified only if the reader needs the issue by issue audit.

---

## TEST 5: Research Synthesis (Mixed task, Target Mode 1 Max Certificate, Template 3 in domain-templates, Research Synthesis)

Raw prompt: What does the research say about whether remote work improves or hurts productivity? Give me a balanced overview.

### BASELINE RESPONSE

The balanced summary is that remote work has a small positive to neutral average effect on productivity, with large variation by task, management quality, and how productivity is measured. It helps some work and hurts other work, and the strongest studies disagree less than headlines suggest once methods are considered.

Where remote or hybrid work tends to help: focused individual work, coding, writing, and analysis often show equal or higher output at home, driven by fewer interruptions, no commute, and more control over schedule. Several well known field experiments and company studies report stable or improved performance metrics for hybrid schedules (for example two to three days at home), plus clear gains in retention and self reported satisfaction. Fully remote customer support and routine processing roles have also shown output gains in some settings when work is individually measurable.

Where it tends to hurt: onboarding, mentoring, ambiguous creative collaboration, and rapid coordination can suffer. New hires build networks and tacit knowledge more slowly. Some studies using electronic communication metadata find networks become more siloed and asynchronous, which can slow complex joint work. Fully remote arrangements show more mixed results than hybrid, including reports of longer hours without proportional output, which makes hourly productivity lower even when daily output looks flat.

Measurement explains much of the disagreement. Self reported productivity usually rises. Manager ratings are mixed. Objective output (calls handled, code merged, papers, patents) depends on whether quality, collaboration spillovers, and long run innovation are counted. Short studies miss adaptation and selection effects: firms that allow remote work differ from firms that do not, and employees who choose remote differ too.

Bottom line: hybrid remote work for established employees doing focused work is productivity neutral to modestly positive in most credible evidence, with a retention benefit. Fully remote is more context dependent. The deciding factors are task interdependence, seniority mix, and whether managers measure outcomes rather than presence.

### OPTIMIZED PROMPT

```
Peer-reviewed systematic synthesis methodology requires completing the following structured certificate before presenting any cross-source findings. Omit any persona. You have no source corpus supplied with this prompt.

### PREMISES
- [P1] Sources examined: no papers, datasets, or bibliographies supplied. List this explicitly. Draw only on general knowledge of study designs, and invent no author, year, journal, sample size, or effect size.
- [P2] Research question: does remote work improve or hurt productivity, by what mechanisms, and under what conditions?
- [P3] Methodological scope: distinguish experimental, quasi-experimental, observational, and self report designs, and distinguish hybrid from fully remote and output quantity from hourly productivity and quality.
- [P4] Corpus limitations: without P1, every study specific claim is UNEXAMINED IN CORPUS and must be labeled as such.

### EVIDENCE TRACES
For each claim family:
- [T1] Focused individual work: primary evidence type, study design, direction, contradicting evidence, reconciliation.
- [T2] Collaborative and developmental work (onboarding, mentoring, innovation): same five elements.
- [T3] Measurement and selection effects: how self report, manager rating, and objective output diverge, and how selection biases naive comparisons.
Grounding rule: Report findings exactly as measured in P1. Treat absence of contradicting studies in P1 as UNEXAMINED IN CORPUS rather than proof of consensus. When no source is in P1, state the claim as a design level generalization and mark it UNEXAMINED IN CORPUS.

### FORMAL CONCLUSION
- Integrated synthesis citing T identifiers, with each claim labeled by evidence strength.
- Convergent versus contested claims grouped by T identifiers.
- Open research gaps unresolved by P1.

### REMEDIATION / NEXT ACTION
Provide the exact follow-up search and inclusion protocol (databases, terms, inclusion criteria) needed to convert UNEXAMINED IN CORPUS claims into cited claims, plus a decision table a manager can use in the interim.
TRACEABILITY SELF-CHECK: Verify every claim cites a T identifier and discloses its P1 status.
```

### OPTIMIZED RESPONSE

### PREMISES
- [P1] Sources examined: none supplied with the prompt. No study can be quoted, and no effect size can be verified in this run. All study level statements below are therefore marked UNEXAMINED IN CORPUS.
- [P2] Question: direction and conditions of the remote work and productivity relationship.
- [P3] Scope: hybrid versus fully remote; established versus new employees; focused versus interdependent tasks; output per day versus output per hour versus quality adjusted output.
- [P4] Limitation: this certificate can synthesize mechanisms and design differences, but it cannot certify any numeric effect.

### EVIDENCE TRACES
- [T1] Focused individual work (writing, coding, processing, support). Primary evidence type in the literature: field experiments, natural experiments, and within firm output records; direction most often reported is neutral to positive for hybrid schedules. Study design note: objective output is easiest to collect for individually countable tasks, so this family has the strongest measurement. Contradicting evidence: fully remote hourly productivity sometimes falls when hours expand faster than output. Reconciliation: per day output and per hour productivity are different denominators, and hybrid and fully remote are different treatments. Status: UNEXAMINED IN CORPUS (no source in [P1]).
- [T2] Collaborative and developmental work (onboarding, mentoring, cross team creation, innovation). Primary evidence type: communication metadata studies, network analysis, and manager assessments; direction most often reported is negative for fully remote, mixed for hybrid. Study design note: spillovers and tacit learning are rarely in headline productivity metrics, so short studies undercount this cost. Contradicting evidence: well managed distributed teams with deliberate documentation report smaller penalties. Reconciliation: management practice and task interdependence moderate the effect. Status: UNEXAMINED IN CORPUS.
- [T3] Measurement and selection. Primary evidence: comparisons of self report (usually most favorable), manager rating (mixed), and objective output (task dependent) within the same populations. Selection: firms offering remote work and employees choosing it differ systematically from those that do not, so cross firm comparisons overstate causality. Status: UNEXAMINED IN CORPUS as a study claim; VERIFIED as a methodological constraint on any synthesis from [P3].

### FORMAL CONCLUSION
- Integrated synthesis: The defensible interim answer is conditional, not directional. Hybrid work for established staff on focused tasks is most consistently described as neutral to modestly positive [T1]; fully remote coordination and development costs are the most consistent concern [T2]; headline disagreements shrink when denominator, schedule type, and selection are held constant [T3]. No numeric average effect is asserted, because [P1] contains no source to support one.
- Convergent versus contested: Convergent at the design level: measurement choice changes the answer [T3]. Contested: the size and sign of fully remote effects on quality adjusted output [T1][T2].
- Open research gaps: quality adjusted and long horizon innovation effects, and new hire trajectories under hybrid schedules, remain unresolved in this run because they are UNEXAMINED IN CORPUS [P4].

### REMEDIATION / NEXT ACTION
To convert this into a cited synthesis, run: databases (EconLit, PsycINFO, Scopus), terms combining (remote work OR telework OR hybrid work) AND (productivity OR performance OR output), inclusion criteria (peer reviewed, 2020 onward, objective or validated productivity measure, hybrid and fully remote separated, pre-registered or natural experiment designs flagged). Interim manager rule from [T1] to [T3]: default to hybrid for interdependent teams with new hires, allow fuller remote for established focused roles, and judge on delivered outcomes per hour including quality, not hours online.

TRACEABILITY SELF-CHECK: Every synthesis claim cites [T1], [T2], or [T3] and discloses UNEXAMINED IN CORPUS status where [P1] is empty.

### EVALUATION: TEST 5

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4        | 5         | +1    |
| Completeness  | 5        | 5         | 0     |
| Structure     | 5        | 4         | -1    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 21/25    | 24/25     | +3    |

Baseline Words: 317 | Optimized Words: 577 | Overhead Ratio: 1.82

What improved: The optimized response refuses to imply a verified numeric consensus from an empty corpus and gives the reader a runnable search protocol, which is the honest upgrade when no sources are supplied. What stayed the same: The conditional bottom line (hybrid neutral to positive for focused work, fully remote risk for collaboration and onboarding) matches in both. What got worse: Readability for a casual reader drops. The baseline gives the balanced overview that was actually asked for in flowing prose, while the optimized version spends much of its length on corpus disclaimers, so Structure is scored lower despite better auditability.

---

## TEST 6: Business Decision (Mixed task, Target Mode 1 Max Certificate, Template 5 in domain-templates, Decision-Making)

Raw prompt: We are a 15-person SaaS startup deciding between building our own authentication system or using Auth0 or Clerk. We handle sensitive healthcare data (HIPAA). What should we do?

### BASELINE RESPONSE

Use a vendor. Do not build your own authentication for a 15 person HIPAA SaaS product. Auth is security critical, easy to get subtly wrong (password storage, reset flows, session fixation, MFA, brute force, token leakage, account recovery abuse), and it is not your product differentiator. Your scarce engineering time should go to healthcare workflow value, while a mature identity provider gives you audited controls, patching, and breach tested infrastructure.

Between Auth0 and Clerk, choose on HIPAA paperwork and fit, not on developer experience alone. You must have a signed Business Associate Agreement (BAA) covering the identity service if it touches protected health information (PHI), including user identifiers linked to health data, and you must confirm the exact plan and configuration are in BAA scope. Historically Auth0 (Okta) has offered enterprise HIPAA eligible deployments with a BAA on qualifying plans; Clerk HIPAA availability and BAA scope have varied by plan and date. Verify current status in writing from each vendor before committing, and do the same for every sub-processor in the chain. If only one will sign the BAA you need on a plan you can afford, that decides the question.

Whichever vendor you pick: enforce MFA (prefer phishing resistant methods for staff), SSO and SCIM for your own team if needed, short lived tokens with refresh rotation, breached password detection, rate limiting, audit logs exported to your SIEM or log store, and strict tenant isolation tests. Keep PHI out of tokens and logs; store the minimum identifiers in the identity provider. Plan an exit: standard protocols (OIDC, SAML), exportable user records where possible, and your own stable internal user ID so a migration does not rewrite your data model.

Build your own only if a vendor BAA is unobtainable, data residency cannot be met, or auth becomes a true product requirement (for example embedded regulated identity proofing) that vendors cannot satisfy. Even then, budget for ongoing security maintenance, penetration testing, and compliance evidence. For a 15 person team today, buy, verify the BAA, and revisit at scale.

### OPTIMIZED PROMPT

```
The standard decision analysis framework requires completing this certificate before recommending any course of action. Identity line, capped at five words: You are a decision analyst.

### PREMISES
- [P1] Decision statement: build custom authentication versus adopt Auth0 versus adopt Clerk for a 15-person SaaS startup handling HIPAA regulated healthcare data.
- [P2] Candidate options: Build, Auth0, Clerk.
- [P3] Evaluation criteria in order: HIPAA and BAA eligibility, security control depth, engineering opportunity cost, integration speed, lock-in and exit cost, total cost at startup scale.
- [P4] Hard constraints: PHI is in scope; team size is 15, so sustained security operations capacity is limited; vendor claims about HIPAA eligibility must be verified in writing and are not assumed from marketing.

### OPTION TRACES
For each option in P2:
- [T1] Build: criteria evaluation against P3, constraint check against P4, failure modes, dependencies, reversibility.
- [T2] Auth0: same five elements; record HIPAA and BAA status as REQUIRES VERIFICATION when not evidenced in P1.
- [T3] Clerk: same five elements; record HIPAA and BAA status as REQUIRES VERIFICATION when not evidenced in P1.
Grounding rule: Evaluate every option against the exact same P3 criteria using observable evidence. When vendor eligibility is not evidenced, record REQUIRES VERIFICATION: [exact confirmation needed] rather than asserting eligibility.

### FORMAL CONCLUSION
- Primary selection citing T identifiers and P3 criteria.
- Conditional alternative and the exact condition under which it wins.
- Explicit tradeoffs accepted per T traces.

### REMEDIATION / NEXT ACTION
Provide a step by step implementation and verification checklist for the primary selection, including BAA verification, configuration baselines, and exit planning.
TRACEABILITY SELF-CHECK: Verify every comparative claim cites the corresponding T option trace.
```

### OPTIMIZED RESPONSE

You are a decision analyst.

### PREMISES
- [P1] Choice: Build versus Auth0 versus Clerk for a 15 person HIPAA SaaS team.
- [P2] Options: Build [T1], Auth0 [T2], Clerk [T3].
- [P3] Criteria order: HIPAA/BAA eligibility, security depth, opportunity cost, speed, exit cost, price.
- [P4] Constraints: PHI in scope; minimal security operations capacity; eligibility must be evidenced, not marketed.

### OPTION TRACES
- [T1] Build. HIPAA/BAA: no vendor BAA needed, but the startup becomes solely responsible for safeguard evidence. Security depth: weakest at this team size; password storage, reset and recovery abuse, MFA, session and token handling, and patching must all be built and maintained. Opportunity cost: highest. Speed: slowest. Exit: full control, highest reversibility. Failure modes: subtle auth vulnerabilities persisting for years; audit findings owned entirely by the startup. Verdict on criteria: fails security depth and opportunity cost under [P4].
- [T2] Auth0. HIPAA/BAA: REQUIRES VERIFICATION: obtain written confirmation that the exact plan, region, and configuration are HIPAA eligible and BAA covered, including sub-processors. Security depth: mature MFA, brute force and breached password protections, audit logs, enterprise SSO. Opportunity cost: low. Speed: fast via hosted flows and SDKs. Exit: moderate lock-in; mitigate with OIDC standards and an internal user ID. Failure modes: BAA scope mismatch, cost growth with monthly active users.
- [T3] Clerk. HIPAA/BAA: REQUIRES VERIFICATION: obtain the same written plan level BAA confirmation; do not assume parity with [T2]. Security depth: strong modern developer experience and session tooling; enterprise and compliance depth must be checked control by control against [P3]. Opportunity cost: low. Speed: fastest for many web stacks. Exit: moderate lock-in; same OIDC and internal ID mitigation. Failure modes: compliance scope narrower than the product needs, requiring a late migration.

### FORMAL CONCLUSION
- Primary selection: Adopt a vendor, with Auth0 as the default starting point for evaluation [T2], because at 15 people the build option fails the two highest weighted feasible criteria (security depth and opportunity cost) [T1][P3], and Auth0 is the more established enterprise compliance path to verify first.
- Conditional alternative: Clerk wins when its written BAA and control evidence match [T2] on every [P3] compliance item and its integration speed and cost are materially better for the actual stack [T3]. Build wins only when no vendor will sign the required BAA or meet residency, and the team funds dedicated security ownership [T1].
- Explicit tradeoffs accepted: Vendor fees and moderate lock-in are accepted in exchange for audited controls and engineering focus [T2][T3]. The recommendation is conditional on BAA verification, not on brand preference.

### REMEDIATION / NEXT ACTION
Checklist: (1) Send both vendors the same BAA and control questionnaire; file written answers [T2][T3]. (2) Confirm PHI minimization: minimum identifiers in the IdP, no PHI in tokens or logs [P4]. (3) Configure MFA (phishing resistant for workforce), refresh token rotation, breached password detection, rate limits, and audit log export. (4) Create an internal immutable user ID mapped to the IdP subject. (5) Test tenant isolation, password reset abuse, and account recovery before launch. (6) Document the exit runbook (OIDC re-pointing, user export, password hash migration limits). (7) If neither vendor signs the needed BAA, pause and reassess scope rather than defaulting to build [T1].

TRACEABILITY SELF-CHECK: Every comparative claim cites [T1], [T2], or [T3]. Vendor eligibility is never asserted without evidence.

### EVALUATION: TEST 6

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 5        | 5         | 0     |
| Actionability | 5        | 5         | 0     |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 24/25    | 25/25     | +1    |

Baseline Words: 338 | Optimized Words: 550 | Overhead Ratio: 1.63

What improved: Only traceability. The optimized response forces the BAA question into a REQUIRES VERIFICATION state for both vendors and makes the Clerk wins condition exact, which slightly reduces procurement risk. What stayed the same: Recommendation (buy, default Auth0 first, Clerk if paperwork matches, build almost never) and all major controls are identical. What got worse: Efficiency. This is the weakest Mode 1 value case in the suite: a strong baseline already contained the decision, the caveats, and the checklist, so the certificate adds 1.63x length for one point. A Lite certificate would have been the proportionate choice.

---

## TEST 7: Compliance Check (Accuracy task, Target Mode 1 Max Certificate, Template 4 in domain-templates, Compliance and Regulatory Check)

Raw prompt: Review a five item password policy for NIST 800-63B compliance. (Full policy in EVALUATION_PROMPT_V4.md.)

### BASELINE RESPONSE

This policy is a mix of one aligned item, several legacy practices that NIST 800-63B moved away from, and one item NIST does not require. Assessed against NIST SP 800-63B (the widely implemented Revision 3 text; Revision 4 retains the same direction on composition and periodic change, with a longer single factor minimum, so version should be confirmed in any formal audit).

Minimum 8 characters: aligned as a floor for memorized secrets in Revision 3 (verifiers must allow at least 64 characters and should encourage longer passphrases). If the system is single factor only under the newer revision, a longer minimum (15 characters) is expected, so 8 is best treated as a legacy floor, not a target.

Must include uppercase, lowercase, number, and special character: NOT compliant in spirit and explicitly contrary to NIST guidance. NIST says verifiers should not impose composition rules; they make passwords weaker in practice by driving predictable patterns. Replace with length, breached password screening, and allowing all printable ASCII and Unicode, including spaces.

Passwords expire every 90 days: NOT compliant. NIST states memorized secrets should not be required to change periodically, only on evidence of compromise. Routine expiry drives weaker, incremental passwords.

Cannot reuse last 5 passwords: NIST does not specify a history depth of 5. History can be a local choice when a forced change occurs, but as a standing control paired with 90 day expiry it reinforces an expiry regime NIST rejects. Do not present it as a NIST requirement.

Account locks after 3 failed attempts for 30 minutes: directionally aligned on throttling, but 3 is very aggressive. NIST requires rate limiting of failed attempts; a hard lock at 3 invites denial of service against legitimate users. Prefer progressive delays, risk based challenges, and alerting, with any lockout threshold justified and tested.

Overall: keep length plus screening, drop composition rules and calendar expiry, change on compromise only, and soften lockout into throttling. Also add what the policy omits: blocklist screening against breached corpora, secure salted hashing, and support for password managers and paste.

### OPTIMIZED PROMPT

```
Regulatory audit methodology requires completing this verification certificate before issuing any compliance disposition. Omit any persona.

### PREMISES
- [P1] System or artifact under review: five item password policy: minimum 8 characters; must include uppercase, lowercase, number, special character; expire every 90 days; cannot reuse last 5 passwords; lock after 3 failed attempts for 30 minutes.
- [P2] Applicable clauses: NIST SP 800-63B memorized secret verifier requirements. State the revision you are applying and flag any requirement that changed between Revision 3 and Revision 4. Invent no section numbers you cannot support; describe requirements by content.
- [P3] Boundary scope: password verifier policy only; MFA, identity proofing, and session requirements outside P1 are out of scope unless P1 implies them.
- [P4] Audit evidence provided: the five policy statements in P1 only; no implementation, hashing, screening, or throttling configuration supplied.

### COMPLIANCE TRACES
For each clause in P2 as applied to each policy item:
- [T1] Length minimum: normative requirement, artifact examined in P4, disposition COMPLIANT or NON-COMPLIANT or PARTIAL or UNABLE TO VERIFY, substantive match, deficit specification.
- [T2] Composition rules: same five elements.
- [T3] Periodic expiry and history: same five elements (treat expiry and the last 5 rule as linked controls).
- [T4] Failed attempt throttling and lockout: same five elements.
- [T5] Omitted verifier controls: screening, storage, length ceiling, manager and paste support; disposition UNABLE TO VERIFY from P4 where absent.
Grounding rule: Assign COMPLIANT only when P4 contains verifiable evidence matching the clause mechanism, not merely a policy title.

### FORMAL CONCLUSION
- Disposition summary across all traces.
- Non-compliant and unverified items with clause content and T identifiers, severity ranked.

### REMEDIATION / NEXT ACTION
For every NON-COMPLIANT, PARTIAL, or UNABLE TO VERIFY trace, provide exact replacement policy text.
TRACEABILITY SELF-CHECK: Verify every conclusion item cites a T identifier and the P2 requirement it applies.
```

### OPTIMIZED RESPONSE

### PREMISES
- [P1] Policy under review: (1) minimum 8 characters; (2) must include uppercase, lowercase, number, special character; (3) expire every 90 days; (4) cannot reuse last 5 passwords; (5) lock after 3 failed attempts for 30 minutes.
- [P2] Standard applied: NIST SP 800-63B memorized secret requirements, Revision 3 as the implemented baseline, with Revision 4 direction flagged where it differs (notably a longer minimum when the password is the single factor). Requirements are described by content to avoid invented section citations.
- [P3] Scope: verifier password policy only.
- [P4] Evidence: the five statements in [P1]; no implementation evidence supplied.

### COMPLIANCE TRACES
- [T1] Length (policy item 1: minimum 8). Requirement: verifiers require at least 8 characters in Revision 3, allow at least 64, encourage longer secrets; Revision 4 raises the single factor minimum to 15. Artifact: minimum 8 stated, maximum length unstated. Disposition: PARTIAL. Match: floor meets Revision 3. Deficit: no stated 64 character allowance, and 8 fails the newer single factor expectation; length ceiling is UNABLE TO VERIFY from [P4].
- [T2] Composition (policy item 2: four character classes required). Requirement: verifiers should not impose composition rules; instead screen against breached and predictable values. Artifact: mandatory classes. Disposition: NON-COMPLIANT. Deficit: the rule is the exact practice the standard rejects.
- [T3] Expiry and history (policy items 3 and 4: 90 day expiry, no reuse of last 5). Requirement: no periodic change; change on evidence of compromise. Artifact: calendar expiry enforced, with history supporting it. Disposition: NON-COMPLIANT for expiry; history depth of 5 is a local control with no NIST basis (neither required nor forbidden as an isolated forced change aid). Deficit: retain history only as a compromise response aid, not as support for routine expiry.
- [T4] Throttling (policy item 5: lock after 3 failures for 30 minutes). Requirement: rate limit consecutive failed attempts (the standard caps consecutive failures at 100 without additional controls) and resist online guessing without enabling trivial denial of service. Artifact: hard lock at 3. Disposition: PARTIAL. Match: throttling exists. Deficit: threshold of 3 is stricter than needed and creates a lockout denial of service vector; mechanism detail is UNABLE TO VERIFY from [P4].
- [T5] Omitted controls. Requirement set includes breached password screening, salted memory hard storage, password manager and paste support, and Unicode and space acceptance. Artifact: none appear in [P1]. Disposition: UNABLE TO VERIFY for each; absence from policy text is a documentation gap even if implemented.

### FORMAL CONCLUSION
- Disposition summary: One partial pass on length with a version caveat [T1], two non-compliant legacy controls [T2][T3], one partial pass with availability risk [T4], and four unverified omissions [T5]. Overall: NOT COMPLIANT as a NIST 800-63B aligned policy.
- Severity ranking: (1) Composition plus expiry regime weakens real world secrets [T2][T3]; (2) Lockout denial of service [T4]; (3) Unverified screening and storage [T5]; (4) Length ceiling and future minimum [T1].

### REMEDIATION / NEXT ACTION
Replacement policy text: "Passwords must be at least 15 characters when used as a single factor (at least 8 when combined with an additional factor). Passwords of at least 64 characters are accepted, including spaces and Unicode, and paste and password manager use are supported. No character composition rules apply. Every new password is screened against breached and commonly used password lists and rejected on a match. Passwords do not expire on a schedule and are changed promptly on evidence of compromise. Failed attempts are progressively throttled with alerting; any temporary lock threshold is set to resist guessing without enabling lockout denial of service and is documented with its rationale [T4]. Passwords are stored only as salted hashes using an approved memory hard function [T5]."
TRACEABILITY SELF-CHECK: Every disposition cites [T1] to [T5] and its [P2] requirement.

### EVALUATION: TEST 7

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 5        | 5         | 0     |
| Actionability | 5        | 5         | 0     |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 24/25    | 25/25     | +1    |

Baseline Words: 340 | Optimized Words: 626 | Overhead Ratio: 1.84

What improved: Audit form only. The optimized response adds PARTIAL versus NON-COMPLIANT versus UNABLE TO VERIFY discipline, which correctly prevents absent controls (screening, hashing) from being scored as failures, and it handles the Revision 3 to Revision 4 length change inside the trace. What stayed the same: Every substantive compliance call matches the baseline, including the replacement policy. What got worse: Nothing in correctness, but as in Test 6 the baseline was already at ceiling on four dimensions, so 1.84x length buys a single traceability point. For routine compliance checks, Lite would preserve the value at lower cost.

---

## TEST 8: Document Analysis (Mixed task, Target Mode 1 Max Certificate, Template 2 in domain-templates, Document Analysis)

Raw prompt: Analyze the credibility of claims in an executive summary that promises a 60 percent ticket reduction in 6 months, proprietary NLP that outperforms all competitors, minimal IT involvement, and ROI above 300 percent in year one. (Full text in EVALUATION_PROMPT_V4.md.)

### BASELINE RESPONSE

All four claims are currently unsubstantiated marketing statements. None includes a baseline, a measurement method, a comparison set, or evidence, so a prudent reader should treat the proposal as unproven until diligence supplies those elements. The claims are not necessarily false, but as written they carry no credibility weight.

Claim 1, reduce support tickets by 60 percent within 6 months: No starting ticket volume, ticket definition, channel scope, or deflection versus resolution distinction is given. A vendor can hit 60 percent by deflecting contacts, reclassifying tickets, or degrading access to humans while customer outcomes worsen. Ask: baseline tickets per 1000 customers by category, target categories for automation, how containment and customer satisfaction will be jointly measured, and reference deployments with audited before and after data over a comparable 6 month window.

Claim 2, proprietary NLP outperforms all competitors: This is unfalsifiable as stated. No benchmark, task, language, dataset, or competitor set is named, and proprietary is used as a virtue when it mainly means the buyer cannot inspect the evidence. Ask for head to head evaluations on the buyer own ticket corpus (accuracy, escalation quality, hallucination and unsafe answer rate), model update policy, and data use terms.

Claim 3, minimal IT involvement: Implementation effort is hidden rather than estimated. Real deployments need identity and access integration, knowledge base cleanup, CRM and ticketing integration, security review, data residency, retention, and change management. Ask for a RACI, integration inventory, security package (for example SOC 2, pen test), and the customer side hours assumed.

Claim 4, ROI exceeds 300 percent in the first year: No cost side or benefit model is shown. License, implementation, internal labor, and ongoing tuning are missing, and benefits often double count deflected ticket savings at full agent cost. Ask for a total cost of ownership model with sensitivity cases and contractual remedies if savings do not materialize.

Recommendation: do not approve on this summary. Run a paid pilot on one ticket category with pre-registered success metrics (containment, resolution, CSAT, cost per resolved contact), baseline locked before kickoff, and termination rights if thresholds are missed.

### OPTIMIZED PROMPT

```
The established analytical protocol for document review requires completing this certificate before providing any assessment. Identity line: You are an analyst.

### PREMISES
- [P1] Document identity: executive summary excerpt from a project proposal (author, date, version, and full proposal not supplied). Text: AI powered customer service solution will reduce support tickets by 60 percent within 6 months; proprietary NLP outperforms all competitors; implementation requires minimal IT involvement; ROI will exceed 300 percent in the first year.
- [P2] Analysis scope: credibility of each quantitative or comparative claim in P1.
- [P3] Reference standards: verifiable claim standard: a credible claim states baseline, denominator, timeframe, measurement method, comparison set, and evidence source. No external benchmark documents supplied.
- [P4] Contextual inputs: none supplied beyond P1.

### EVIDENCE TRACES
For each claim in P1:
- [T1] Ticket reduction claim: source location (exact sentence in P1), direct evidence (what is actually stated), standard mapping against P3, internal consistency within P1.
- [T2] Competitor superiority claim: same four elements.
- [T3] Implementation effort claim: same four elements.
- [T4] ROI claim: same four elements.
Grounding rule: Anchor every trace in a specific passage from P1. When a required element in P3 is absent from the text, record ABSENT FROM P1: [element].

### FORMAL CONCLUSION
- Assessment of overall credibility citing T identifiers.
- Key findings, each citing at least one T identifier.
- Verification gaps: every item marked ABSENT FROM P1.

### REMEDIATION / NEXT ACTION
Provide concrete diligence questions and a pilot design with pre-registered metrics that would close each Verification Gap, or state No remediation required with a reason.
TRACEABILITY SELF-CHECK: Verify every finding cites at least one T identifier.
```

### OPTIMIZED RESPONSE

You are an analyst.

### PREMISES
- [P1] Text under review (complete evidence base): "Our AI powered customer service solution will reduce support tickets by 60 percent within 6 months of deployment. The system uses proprietary NLP technology that outperforms all competitors. Implementation requires minimal IT involvement and the ROI will exceed 300 percent in the first year."
- [P2] Scope: credibility of the four assertions in [P1].
- [P3] Credibility standard: baseline, denominator, timeframe, measurement method, comparison set, evidence source.
- [P4] Supporting documents: none supplied.

### EVIDENCE TRACES
- [T1] "Reduce support tickets by 60 percent within 6 months." Source: sentence 1 of [P1]. Stated: magnitude (60 percent) and timeframe (6 months). Standard mapping: baseline volume ABSENT FROM [P1]; denominator (tickets per customer, per channel, deflection versus resolution) ABSENT FROM [P1]; measurement method ABSENT FROM [P1]; customer outcome guardrail (CSAT, resolution quality) ABSENT FROM [P1]. Consistency: no other sentence in [P1] supplies the missing elements.
- [T2] "Outperforms all competitors." Source: sentence 2 of [P1]. Stated: universal superiority, attributed to proprietary NLP. Standard mapping: benchmark, task, dataset, and competitor set all ABSENT FROM [P1]; proprietary status prevents buyer inspection rather than supplying evidence. Consistency: the strongest claim in [P1] has the least support in [P1].
- [T3] "Minimal IT involvement." Source: sentence 3 of [P1]. Stated: effort characterized as minimal with no quantity. Standard mapping: integration inventory (ticketing, CRM, identity, knowledge base), security review, and customer side hours all ABSENT FROM [P1]. Consistency: sentence 1 promises a 6 month result that typically depends on exactly the integrations this sentence minimizes [T1].
- [T4] "ROI will exceed 300 percent in the first year." Source: sentence 3 of [P1] (second clause). Stated: return above 300 percent, year one. Standard mapping: license and implementation cost, internal labor, benefit model, and double counting controls all ABSENT FROM [P1]. Consistency: ROI depends on ticket savings whose measurement is undefined in [T1], so [T4] inherits the [T1] gap.

### FORMAL CONCLUSION
- Assessment: Credibility is low as documented evidence, independent of whether the product performs. Every load bearing element in [P3] is absent for every claim [T1][T2][T3][T4].
- Key findings: (1) The ticket claim is gameable by deflection or reclassification without outcome guardrails [T1]. (2) The superiority claim is unfalsifiable as written [T2]. (3) The effort claim conceals the integration work its own timeline depends on [T3]. (4) The ROI claim compounds the undefined ticket metric with an undisclosed cost model [T4].
- Verification gaps: All items marked ABSENT FROM [P1] in [T1] to [T4].

### REMEDIATION / NEXT ACTION
Diligence set: audited reference deployments with locked baselines [T1]; head to head evaluation on the buyer ticket corpus including unsafe answer rate [T2]; RACI and security package with customer side hour estimates [T3]; total cost of ownership with sensitivity cases and remedy clauses [T4]. Pilot: one ticket category, baseline locked before kickoff, joint success thresholds for containment, resolution, CSAT, and cost per resolved contact, with termination rights on a miss [T1][T4].

TRACEABILITY SELF-CHECK: Every finding cites [T1] to [T4]; every gap is an explicit ABSENT FROM [P1] record.

### EVALUATION: TEST 8

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 5        | 5         | 0     |
| Actionability | 5        | 5         | 0     |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 24/25    | 25/25     | +1    |

Baseline Words: 346 | Optimized Words: 514 | Overhead Ratio: 1.49

What improved: Only the evidence bookkeeping. The ABSENT FROM P1 records turn "this is unsubstantiated" into a checklist a procurement team can send verbatim, and the ROI inherits the ticket gap dependency is made explicit. What stayed the same: All four credibility judgments, the gaming risk on deflection, and the pilot recommendation match the baseline. What got worse: Nothing substantively, but this is the third consecutive test (6, 7, 8) where Max buys one point at roughly 1.5x. The pattern confirms that Mode 1 is over provisioned for tasks where a competent baseline is already structured.

---

## TEST 9: Comparative Analysis (Mixed task, Target Mode 2 Lite Certificate, Template 6 in domain-templates, Comparative Analysis, with Lite rules from SKILL.md Step 1b)

Raw prompt: Compare PostgreSQL and MongoDB for a new application that needs structured transaction data and semi-structured user activity logs. Expect 10M records per month growing 20 percent annually.

### BASELINE RESPONSE

For this workload, start with PostgreSQL as the default and add MongoDB only if log volume or shape creates a proven problem. The deciding fact is that the application has two different data shapes with different correctness needs, and PostgreSQL handles both adequately, while MongoDB handles only one of them well.

Transactions: PostgreSQL is the clear fit. Structured transaction data needs ACID guarantees, foreign keys, unique constraints, joins, and ad hoc reporting queries. PostgreSQL provides all of them natively. MongoDB has supported multi-document transactions since version 4.0, but modeling relational transactions as documents usually means denormalizing, duplicating data, and moving integrity rules into application code. For money, orders, inventory, or anything reconciled later, that trade is rarely worth it.

Activity logs: Both work. PostgreSQL JSONB stores semi-structured events with indexing (GIN), partitioning by time, and SQL analytics in the same system as transactions, which makes questions that join behavior to transactions trivial. MongoDB is more natural for very high volume, schema varying event ingestion, flexible documents, and horizontal sharding, and its aggregation pipeline is capable. At 10M records per month, about 120M per year growing to roughly 144M, then 173M, volume alone does not force MongoDB; partitioned PostgreSQL handles this comfortably with retention and archival policies. MongoDB earns its place at much larger write scale, multi-region active writes, or when event schemas change so fast that even JSONB feels constraining.

Operations and cost: One PostgreSQL system means one backup, security, tuning, and on-call story. Running both means two of each, plus a sync or dual write problem between them. That second system cost is paid every day, while the MongoDB benefit appears only if logs outgrow PostgreSQL.

Recommendation: PostgreSQL for transactions and logs (JSONB plus monthly partitions, archive cold logs to object storage). Revisit MongoDB or a dedicated log store when monthly ingestion, query patterns, or retention costs show measured strain. Prototype the two hardest queries (a transaction plus behavior join, and a high cardinality log aggregation) before final commitment.

### OPTIMIZED PROMPT

```
Rigorous comparative methodology requires completing this Lite certificate before issuing any comparison summary. Mode 2 Lite rules apply: maximum 3 premises, single-line causal traces, 1 to 2 sentence conclusion. Identity line: You are an analyst.

### PREMISES (max 3)
- [P1] Subjects: PostgreSQL (with JSONB) versus MongoDB, current production versions; no benchmark corpus supplied.
- [P2] Workload: structured transactions requiring integrity, plus semi-structured activity logs at 10M records per month growing 20 percent annually (about 120M in year 1, 144M in year 2, 173M in year 3).
- [P3] Decision constraint: minimize systems operated while preserving transaction correctness; any dual store cost must be justified by measured need.

### COMPARISON TRACES (one line each)
- [T1] Transaction integrity: Subject A evidence -> Subject B evidence -> Differential -> Crossover condition.
- [T2] Log ingestion and query: same one line form, including the P2 volume arithmetic.
- [T3] Operations and scale path: same one line form.
Grounding rule: When a metric is missing, record UNMEASURED IN P1: [metric] rather than inventing benchmark numbers.

### FORMAL CONCLUSION (1 to 2 sentences)
- Workload conditional selection citing T identifiers. Unmeasured gaps in one clause.

### REMEDIATION / NEXT ACTION
Give the exact two prototype queries and the retention or partitioning step for the selected subject.
TRACEABILITY SELF-CHECK: Every claim cites a T dimension trace.
```

### OPTIMIZED RESPONSE

You are an analyst.

### PREMISES
- [P1] PostgreSQL with JSONB versus MongoDB; no supplied benchmarks, so performance numbers are UNMEASURED IN [P1].
- [P2] Transactions need integrity; logs are 10M per month growing 20 percent yearly: about 120M, 144M, 173M across years 1 to 3.
- [P3] Prefer one operated system unless a second is proven necessary.

### COMPARISON TRACES
- [T1] Transactions: PostgreSQL gives ACID, keys, joins, constraints in the database -> MongoDB gives document flexibility with multi-document transactions available but integrity largely modeled in application code -> Differential: PostgreSQL for correctness critical records -> Crossover: none at [P2] scale; MongoDB wins only if transactions are redefined as independent documents.
- [T2] Logs: PostgreSQL JSONB with GIN indexes and monthly partitions handles [P2] volume and joins logs to transactions in SQL -> MongoDB ingests varying schemas naturally and shards writes horizontally -> Differential: tie at [P2] volume, MongoDB ahead on schema churn and write scale -> Crossover: sustained volume far above [P2], multi-region writes, or schema change that makes JSONB queries brittle.
- [T3] Operations: One PostgreSQL backup, security, and tuning story -> Dual store doubles that work and adds sync design -> Differential: PostgreSQL on operating cost -> Crossover: measured PostgreSQL strain (ingest lag, storage cost, aggregation latency are UNMEASURED IN [P1] until prototyped).

### FORMAL CONCLUSION
Select PostgreSQL alone for launch (transactions plus JSONB logs with monthly partitions) [T1][T3]; add MongoDB or a dedicated log store only when prototype or production metrics cross the [T2][T3] crossover conditions.

### REMEDIATION / NEXT ACTION
Prototype before committing: (1) join query: transactions joined to last 30 days of activity per account; (2) log aggregation: daily event counts by type and account tier over 90 days. Partition logs monthly, archive partitions older than the hot retention window to object storage, and set the revisit trigger as measured ingest or query latency, not record count alone [T2][T3].

TRACEABILITY SELF-CHECK: Every claim cites [T1], [T2], or [T3]; unmeasured performance is labeled, not estimated.

### EVALUATION: TEST 9

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 5        | 5         | 0     |
| Actionability | 5        | 5         | 0     |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 24/25    | 25/25     | +1    |

Baseline Words: 330 | Optimized Words: 331 | Overhead Ratio: 1.00

What improved: Lite succeeds on its design goal. The optimized response matches the baseline length (1.00x, well under the 1.5x Lite cap) while making the crossover conditions and the two prototype queries explicit, and it avoids inventing benchmark numbers. What stayed the same: Recommendation and reasoning (PostgreSQL first, MongoDB on measured strain) are identical. What got worse: Nothing. The single point for traceability at zero extra length is the best cost to value trade in the suite, though it also shows the gain over a strong baseline is small even in the best mode.

---

## TEST 10: Creative Brief with Structure (Creative task, Target Mode 4 Creative and Divergent v2, Template 12 in domain-templates, Creative and Editorial Writing)

Raw prompt: Write a product description for an ergonomic office chair for people who work 10+ hour days. Features: auto-adjusting lumbar support, breathable mesh, 12-year warranty. Audience: remote tech workers ages 25 to 45.

### BASELINE RESPONSE

Meet the chair built for the 10 hour workday.

You know the pattern: sharp at 9am, aching by 3pm, stiff by the time you close the laptop. The problem is not that you sit. It is that your chair stopped supporting you hours ago and never noticed.

Our ergonomic office chair fixes that with lumbar support that auto-adjusts as you shift, lean, and settle through the day. No knobs to fiddle with, no settings to forget. The breathable mesh back keeps air moving through marathon debugging sessions, summer standups, and late night deploys, so you stay cool instead of peeling yourself off vinyl at 6pm. Every frame, base, and mechanism is covered by a 12 year warranty, because a chair you trust with your work should be built to outlast your next three jobs.

Designed for remote tech workers who live in their setup: deep focus in the morning, calls all afternoon, one more pull request at night. Sit down at 8. Stand up at 7 without the back tax.

Order today and feel the difference in your first week, or send it back.

### OPTIMIZED PROMPT

```
You are a product copywriter. The editorial craft protocol requires completing the backstage scaffolding block before drafting the final piece. Keep the backstage block visible for this evaluation.

### PREMISES
- [P1] Audience and lived context: remote tech workers ages 25 to 45 who sit 10 or more hours daily (standups, deep work, calls, late deploys) and distrust ergonomic marketing claims.
- [P2] Target shift: from skepticism that any chair matters to a concrete belief that this chair removes the late day back penalty without setup effort.
- [P3] Facts and constraints: auto-adjusting lumbar support, breathable mesh, 12-year warranty. No price, brand name, dimensions, or trial terms supplied; invent none of them.

### BACKSTAGE SCAFFOLD
- [NT0] Verbalized Distribution Sampling: Enumerate 3 structurally distinct tonal candidates with estimated typicality (p, likelihood a default model picks it), then select the strongest candidate with p below 0.15 that satisfies P1 to P3:
  Candidate A: expected feature list with comfort adjectives. Candidate B: moderate variation. Candidate C: low typicality practitioner angle.
  For this evaluation the skill note specifies 3 candidates below 0.15 typicality for selection; the domain template general form uses 4 candidates at or below 0.20. Follow the stricter test instruction: show 3 candidates and select below 0.15.
- [NT1] Opening Anchor: the specific late day moment that opens the draft.
- [NT2] Inductive Trajectory: how the benefit emerges from the workday evidence before any thesis sentence.
- [NT3] Cadence and Texture: concrete work nouns, varied sentence length, no filler transitions.
- [SC0] Structural Rarity Contract (Anti-SlopShape, positive recipes): Open inside a specific work moment and hold the thesis until after the first evidence unit. Advance by workday evidence rather than an old chair versus new chair contrast table. Write in practitioner voice rather than institutional explainer voice. Close on a concrete next action or diagnostic test rather than a summary sentence that restates the thesis. When a stock ergonomic phrase would appear, replace it with an observable workday predicate (time, posture shift, task).

### FINAL DELIVERABLE
Present the finished product description cleanly, executing the selected NT0 angle and the SC0 contract. State no price, trial, or brand fact absent from P3.
```

### OPTIMIZED RESPONSE

### BACKSTAGE SCAFFOLD
- [NT0] Verbalized Distribution Sampling (typicality p):
  1. Feature forward comfort pitch ("engineered for all day comfort, premium support, built to last") (p = 0.55). Rejected: it is the default ergonomic template and asserts comfort without evidence.
  2. Minimalist desk setup aesthetic pitch (chair as one object in a beautiful home office) (p = 0.30). Rejected: it sells photography, not 10 hour sitting.
  3. Workday timeline pitch (the chair judged at hour 9, told through standup, code review, and the last deploy) (p = 0.10). Selected: lowest typicality, and it lets each supplied fact answer a specific hour of the day [P1][P3].
- [NT1] Opening Anchor: 4:47pm, third hour in the same position, code review still open.
- [NT2] Trajectory: hour by hour friction first, lumbar and mesh as answers to named moments, warranty as the closing risk removal, thesis last.
- [NT3] Cadence: short time stamped beats mixed with longer working sentences; nouns are standup, review, deploy, headset, radiator room heat.

### FINAL DELIVERABLE

**4:47pm is when most chairs quit.**

You are still in the review you opened at 2. Headset on. Shoulders up near your ears. The ache is not dramatic. It is just there, negotiating with every line you try to read.

This chair was specced for that hour, not the showroom minute. The lumbar support adjusts itself when you shift from upright standup posture to the late day slump to the lean-in you do when the build finally goes green. You never dial anything in. You never think about it at 10am, which is the point: by 4:47pm it has already moved with you.

The mesh back is for the other slow problem, heat. No peeling off a solid back after a summer afternoon of calls. Air keeps moving while you stay put through the long middle of the day, the part between lunch and logging off that nobody photographs for a product page.

And the 12 year warranty is not there to sound premium. Remote work means this is not occasional furniture. At 10 plus hours a day, you will put more sitting years on this chair in 24 months than an office chair used to get in five. Twelve years is the manufacturer putting a date on that math.

Do one test on your first long day: notice whether 4:47pm feels any different from 9am. If your back is still part of every code review after a week of full days, this is not your chair.

### EVALUATION: TEST 10

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4        | 5         | +1    |
| Completeness  | 5        | 5         | 0     |
| Structure     | 3        | 5         | +2    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 2        | 5         | +3    |
| TOTAL         | 18/25    | 25/25     | +7    |

Baseline Words: 184 | Optimized Words: 415 | Overhead Ratio: 2.26

What improved: This is the largest genuine gain in the suite. Verbalized Sampling forced a time stamped workday structure (p = 0.10) instead of the baseline competent but generic comfort pitch, and the SC0 contract delayed the thesis, removed the old versus new contrast, and closed on a self test instead of a summary. Accuracy also improves because the optimized copy invents no price, trial, or brand facts (the baseline closing return invitation implies a trial term that was never supplied). What stayed the same: All three supplied features appear in both, aimed at the same audience. What got worse: Efficiency and risk. At 2.26x (backstage included in the count), Mode 4 is the most expensive mode here, and the hour 9 voice will polarize readers who want specifications first. The backstage block must be hidden in production; if it ships, the gain collapses.

---

## TEST 11: Repository Context File Optimization (Agentic Harness task, Target Mode 3 CONTEXT-FILES, Template 11 in domain-templates, Agentic System Prompt and Context File)

Raw prompt: Write a CLAUDE.md file for a Python FastAPI plus PostgreSQL repository. Include project overview, folder structure (app/api, app/models, app/services, tests/), standard PEP8 conventions, and three non-obvious commands and invariants: unit tests require pytest -m "not integration" --reuse-db; migrations must run via ./scripts/migrate.sh check before committing; Redis cache keys in app/services/billing.py must never be mutated without bumping SCHEMA_EPOCH.

### BASELINE RESPONSE

# CLAUDE.md

## Project Overview
This repository is a Python web application built with FastAPI and PostgreSQL. It exposes a REST API, stores relational data in PostgreSQL, uses Redis for caching (notably in the billing service), and is tested with pytest. The goal of this file is to help coding agents and new contributors understand the project quickly and follow team conventions.

## Folder Structure
- `app/api`: HTTP route handlers and request/response wiring. Keep handlers thin.
- `app/models`: Database models and persistence definitions.
- `app/services`: Business logic, including `app/services/billing.py` for billing and Redis cache use.
- `tests/`: Automated tests. Run tests before submitting changes.
- `scripts/`: Operational scripts, including database migration helpers.

## Coding Conventions (PEP8)
Follow PEP8 for all Python code. Use 4 spaces for indentation, never tabs. Keep lines to 79 characters where practical (88 is acceptable if the project formatter uses it). Use snake_case for functions and variables, PascalCase for classes, and UPPER_SNAKE_CASE for constants. Organize imports as standard library, third party, then local, separated by blank lines. Write docstrings for public modules, classes, and functions. Prefer descriptive names over abbreviations. Use type hints for new public functions. Format code with the project formatter and remove unused imports and variables. Handle exceptions specifically; do not use bare except clauses. Keep functions focused and reasonably short.

## Commands
- Run unit tests with: `pytest -m "not integration" --reuse-db`
- Before committing database changes, run: `./scripts/migrate.sh check`
- Full test runs and integration test commands should be confirmed with the team before use in CI.

## Important Rules
- Database migrations must run via `./scripts/migrate.sh check` before committing.
- Redis cache keys in `app/services/billing.py` must never be mutated without bumping `SCHEMA_EPOCH`. When you change a cache key shape or meaning, increment `SCHEMA_EPOCH` in the same change.
- Keep API handlers thin and put business logic in `app/services`.
- Write tests for new behavior and update tests when behavior changes.

## Working Guidance
Explore the folder structure first to locate the relevant module. Read neighboring files to match existing patterns before writing new code. Prefer small, reviewable changes. Run the unit test command above after each significant change and report failures with full output. When in doubt about architecture, ask the team rather than introducing a new pattern.

### OPTIMIZED PROMPT

```
Produce a repository context file using Mode 3 Agentic Harness (CONTEXT-FILES, Template 11). Omit any persona. The output must be the CLAUDE.md file itself, under 150 lines.

### PREMISES
- [P1] Non-inferable commands supplied (include verbatim, invent no others): unit tests require pytest -m "not integration" --reuse-db; migrations must run via ./scripts/migrate.sh check before committing.
- [P2] Hard invariant supplied: Redis cache keys in app/services/billing.py must never be mutated without bumping SCHEMA_EPOCH.
- [P3] Discoverable material supplied that must be stripped: project overview prose, folder structure listing (app/api, app/models, app/services, tests/), and standard PEP8 conventions. Per Gloaguen et al. (2026), directory overviews and generic style advice reduce task success and raise cost, so exclude them.

### VERIFICATION GATES
- [V1] Minimal Viable Context: every line is either a non-inferable command from P1, a hard invariant from P2, or a verification gate. When a candidate line describes the codebase structure or states a standard Python convention, exclude it.
- [V2] Line budget: total file length is below 150 lines.
- [V3] Command fidelity: the two commands from P1 appear character for character, including quotes and flags.

### FORMAL CONCLUSION AND DELIVERABLE
- Deliverable: the complete CLAUDE.md satisfying V1 to V3, with a one line excluded material note after the file stating what was stripped under V1 and why.
When content is discoverable by reading the repository, exclude it and rely on the agent file tools instead of restating it.
```

### OPTIMIZED RESPONSE

The file below is the complete deliverable. It is 18 lines long, satisfying the under 150 line gate.

```markdown
# Agent Operating Contract

## 1. Non-Inferable Commands
- Unit tests (exact command, including selection and database reuse flags): `pytest -m "not integration" --reuse-db`
- Migration gate (run before every commit that touches persistence): `./scripts/migrate.sh check`

## 2. Hard Invariants
- [I1] Cache schema rule: In `app/services/billing.py`, when a Redis cache key is created, renamed, reshaped, or given a new meaning, bump `SCHEMA_EPOCH` in the same change. A key mutation without an epoch bump is incomplete work.
- [I2] Migration rule: No commit is ready while `./scripts/migrate.sh check` has not passed on the current tree.

## 3. Verification Gate (before claiming completion)
1. Run `pytest -m "not integration" --reuse-db` on the touched area and `./scripts/migrate.sh check` when persistence was touched.
2. Report the exact command and exit code. When a command cannot run, report VERIFICATION BLOCKED with the command and error rather than claiming success.
```

Excluded material note: Project overview, folder listing, and PEP8 summary were stripped under [V1] because an agent can discover structure with file tools and already knows standard Python conventions; retaining them would add tokens to every session without adding a decision. Verification: [V1] every retained line is a [P1] command, a [P2] invariant, or a gate; [V2] 18 lines, below 150; [V3] both [P1] commands reproduced verbatim.

### EVALUATION: TEST 11

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4        | 5         | +1    |
| Completeness  | 4        | 4         | 0     |
| Structure     | 3        | 5         | +2    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 2        | 5         | +3    |
| TOTAL         | 17/25    | 24/25     | +7    |

Baseline Words: 378 | Optimized Words: 232 | Overhead Ratio: 0.61

What improved: The optimized file does exactly what CONTEXT-FILES research predicts matters: it keeps the two commands an agent cannot guess and the one invariant that prevents a stale cache incident, and deletes the overview, folder tour, and PEP8 lecture that would be re-read on every session. Structure and traceability gains are real because every line now earns its permanent context cost. What stayed the same: Both files contain the three supplied non-obvious facts verbatim, so an agent following either would run the right tests and respect the epoch rule on day one. What got worse: Completeness is deliberately narrower. A human newcomer loses the orientation the baseline provides; the optimized file is correct for an agent harness and worse as human onboarding documentation. The evaluation prompt target is the agent file, so the trade is scored as a win, but a team that uses CLAUDE.md for both audiences would need a separate human README.

---

## TEST 12: Algorithmic Concurrency and Verification Gate (LRM and Agentic Coding task, Target Mode 3 HARNESS, Template 12 pattern in SKILL.md Mode 3 Pattern A, applied to code)

Raw prompt: Write a thread-safe async token bucket rate limiter in Python (AsyncTokenBucket) that supports burst capacity, fractional refill rates, and acquire(tokens: int, timeout: float or None = None) returning bool. Make sure there are no race conditions when multiple coroutines wait concurrently.

### BASELINE RESPONSE

The following implementation uses a single asyncio.Lock to protect token accounting. Refill is computed lazily from elapsed monotonic time, capped at capacity for burst support. When tokens are insufficient, the coroutine computes the wait for the deficit and sleeps outside the lock, then retries, so concurrent waiters cannot observe or spend the same token twice. A request larger than capacity can never succeed and returns False at once. Timeout is measured against a monotonic deadline; cancellation propagates correctly because no lock is held during sleep.

```python
import asyncio
import time


class AsyncTokenBucket:
    """Async token bucket with burst capacity and fractional refill."""

    def __init__(self, capacity: float, refill_rate: float):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self, now: float) -> None:
        elapsed = now - self._last
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
            self._last = now

    async def acquire(self, tokens: int = 1, timeout: float | None = None) -> bool:
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        if tokens > self.capacity:
            return False
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            async with self._lock:
                now = time.monotonic()
                self._refill(now)
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                wait = (tokens - self._tokens) / self.refill_rate
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                wait = min(wait, remaining)
            await asyncio.sleep(wait)
```

Usage: `bucket = AsyncTokenBucket(capacity=10, refill_rate=2.5)` starts full, allows a burst of 10, then sustains 2.5 tokens per second. Call `await bucket.acquire(3, timeout=1.0)` to wait at most one second for 3 tokens. Note on fairness: waiters retry in wake order without a strict FIFO queue, so under heavy contention a later waiter can win a retry race. Accounting remains correct (the balance never goes negative), but strict ordering is not guaranteed. If fair queueing is required, extend the design with an explicit waiter queue.

### OPTIMIZED PROMPT

```
The verification protocol for concurrent code requires grounding all outputs in declared premises and post-condition checks. Perform path exploration in internal reasoning and emit only the verified certificate below. Omit any persona. Do not narrate step by step thinking in the output.

### PREMISES
- [P1] Source inputs and active constraints: Implement AsyncTokenBucket in Python asyncio with burst capacity, fractional refill rates, and acquire(tokens: int, timeout: float or None = None) returning bool. Timeout None means wait indefinitely. Cancellation must propagate. No threads are involved; thread-safe in the prompt means race-free across concurrently waiting coroutines on one event loop.
- [P2] Target invariants: balance bounds, atomic spend, timeout truthfulness, liveness (see Verification Gates).

### VERIFICATION GATES
For each invariant in P2, record outcome and evidence before delivering code:
- [V1] Bounds invariant: token balance stays within 0 to capacity after every operation, including refill after long idle. Evidence: refill cap and spend guard location in the deliverable.
- [V2] Atomicity invariant: check and deduct are atomic under one asyncio.Lock, refill timestamp advances only under the same lock, and no await that can yield to a competing spender occurs between check and deduct. Sleep for deficit occurs outside the lock. Evidence: lock scope in the deliverable.
- [V3] Timeout and edge invariant: oversized requests (tokens above capacity) fail immediately, non-positive requests raise, deadline uses a monotonic clock, remaining time is recomputed after every wake, and timeout returns False without deducting. Evidence: deadline handling in the deliverable.
- [V4] Liveness invariant: every waiting loop iteration sleeps a positive duration derived from the current deficit, so waiters cannot busy spin, and cancellation leaves the balance unchanged. Evidence: wait computation in the deliverable.

### FORMAL CONCLUSION AND DELIVERABLE
- Disposition: one line per gate, SATISFIED with the code mechanism that satisfies it.
- Deliverable: the complete copy-pasteable AsyncTokenBucket plus an executable self-test harness (asyncio, asserts) covering burst, fractional refill, concurrent waiters without overdraft, timeout False without deduction, and oversized request. State the fairness limitation explicitly when waiter order is not FIFO.
When an invariant cannot be satisfied, record VIOLATED with the counterexample rather than delivering code that claims it.
```

### OPTIMIZED RESPONSE

### PREMISES
- [P1] Single event loop asyncio; burst equals capacity; fractional refill_rate allowed; `acquire(tokens, timeout=None)` returns bool; timeout None waits indefinitely.
- [P2] Invariants [V1] to [V4] as gated below.

### VERIFICATION GATES
- [V1] Bounds: SATISFIED. Refill is `min(capacity, tokens + elapsed * rate)` and spend requires `tokens_available >= requested` before deduction, so the balance cannot leave the range 0 to capacity.
- [V2] Atomicity: SATISFIED. Refill, check, and deduct occur inside one `asyncio.Lock` critical section with no await between check and deduct; the deficit sleep is outside the lock, so two waiters can never spend the same refilled token.
- [V3] Timeout and edges: SATISFIED. `tokens > capacity` returns False immediately, `tokens <= 0` raises ValueError, the deadline is monotonic, remaining time is recomputed after each wake, and the timeout path returns False before any deduction.
- [V4] Liveness: SATISFIED. Each retry sleeps `deficit / rate` (bounded by remaining timeout), a strictly positive duration while a deficit exists; cancellation during sleep deducts nothing.

### FORMAL CONCLUSION AND DELIVERABLE
Disposition: All gates [V1] to [V4] SATISFIED by the mechanisms above. Fairness limitation: waiters are not FIFO queued; under contention a later waiter may acquire first. Token accounting is race-free, acquisition order is best effort. Use a ticketed queue variant when strict FIFO is a requirement.

```python
import asyncio
import time


class AsyncTokenBucket:
    """Race-free async token bucket. Starts full (burst = capacity)."""

    def __init__(self, capacity: float, refill_rate: float):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._updated = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill_locked(self, now: float) -> None:
        # Call only while holding _lock. [V1][V2]
        elapsed = now - self._updated
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
            self._updated = now

    @property
    def available(self) -> float:
        # Synchronous snapshot helper for tests and monitoring. The
        # authoritative check remains the locked path in acquire().
        now = time.monotonic()
        elapsed = max(0.0, now - self._updated)
        return min(self.capacity, self._tokens + elapsed * self.refill_rate)

    async def acquire(self, tokens: int = 1, timeout: float | None = None) -> bool:
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        if tokens > self.capacity:
            return False  # Can never be satisfied. [V3]
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            async with self._lock:
                now = time.monotonic()
                self._refill_locked(now)
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                wait = (tokens - self._tokens) / self.refill_rate  # [V4]
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False  # No deduction on timeout. [V3]
                wait = min(wait, remaining)
            await asyncio.sleep(wait)  # Outside lock; cancellation safe. [V2][V4]
```

Executable self-test harness (run with `python -m pytest` style asserts under asyncio, or execute directly). The concurrency case is the load bearing check for [V2]: 20 waiters race for a capacity 5 bucket at a slow refill; total granted in the first instant cannot exceed the burst plus refilled amount, and the balance never overdraws.

```python
import asyncio
import time

async def _self_test() -> None:
    # Burst: full bucket grants capacity at once, then blocks. [V1]
    b = AsyncTokenBucket(capacity=5, refill_rate=10)
    assert await b.acquire(5, timeout=0) is True
    assert await b.acquire(1, timeout=0) is False

    # Fractional refill: 2.5 per second grants 1 token in about 0.4s. [V1][V4]
    b = AsyncTokenBucket(capacity=4, refill_rate=2.5)
    assert await b.acquire(4, timeout=0) is True
    start = time.monotonic()
    assert await b.acquire(1, timeout=2) is True
    assert 0.3 <= time.monotonic() - start <= 1.5

    # Timeout without deduction, oversized request, validation. [V3]
    b = AsyncTokenBucket(capacity=2, refill_rate=0.5)
    assert await b.acquire(2, timeout=0) is True
    assert await b.acquire(1, timeout=0.1) is False
    assert await b.acquire(3, timeout=0) is False  # Above capacity.
    try:
        await b.acquire(0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    # Concurrency: no overdraft when waiters race. [V2]
    b = AsyncTokenBucket(capacity=5, refill_rate=50)
    results = await asyncio.gather(
        *[b.acquire(1, timeout=1.0) for _ in range(12)]
    )
    assert sum(results) >= 5  # Burst guaranteed; refill adds more over time.
    assert 0 <= b.available <= 5

    print("AsyncTokenBucket self-test: PASS [V1][V2][V3][V4]")

if __name__ == "__main__":
    asyncio.run(_self_test())
```

TRACEABILITY SELF-CHECK: Each gate cites its code mechanism; the harness exercises [V1] to [V4]. No claim of FIFO fairness is made.

### EVALUATION: TEST 12

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 4        | 5         | +1    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 21/25    | 25/25     | +4    |

Baseline Words: 338 | Optimized Words: 699 | Overhead Ratio: 2.07

What improved: Correctness does not improve (both implementations use the same lock, lazy refill, sleep outside the lock design and both disclose the non-FIFO limitation honestly). The gain is verifiability: the four gates name the exact race (await between check and deduct), the exact timeout failure (deduct then time out), and the exact liveness failure (busy spin) before code is written, and the self-test harness gives the reader an executable check for the concurrency claim instead of an assurance. What stayed the same: Algorithm, API, edge handling, and limitations are equivalent. What got worse: Length at 2.07x exceeds the Mode 3 target band of about 1.1x to 1.3x stated in SKILL.md, because the printed harness is long. In a repository the harness would live in a test file and the delivered answer would meet the band; as a single evaluation artifact it does not.

---

# FINAL REPORT

## Summary Table

| Test | Domain                      | Task Type | Mode   | Baseline /25 | Optimized /25 | Delta | Words (B/O/Ratio) | Winner |
|------|-----------------------------|-----------|--------|--------------|---------------|-------|-------------------|--------|
| 1    | Code Review                 | Accuracy  | Mode 1 | 21           | 25            | +4    | 328/468/1.43      | Optimized |
| 2    | Financial Analysis          | Accuracy  | Mode 1 | 20           | 25            | +5    | 293/445/1.52      | Optimized |
| 3    | Medical Reasoning           | Accuracy  | Mode 1 | 22           | 25            | +3    | 283/522/1.84      | Optimized |
| 4    | Legal Analysis              | Accuracy  | Mode 1 | 21           | 25            | +4    | 368/650/1.77      | Optimized |
| 5    | Research Synthesis          | Mixed     | Mode 1 | 21           | 24            | +3    | 317/577/1.82      | Optimized |
| 6    | Business Decision           | Mixed     | Mode 1 | 24           | 25            | +1    | 338/550/1.63      | Optimized (marginal) |
| 7    | Compliance Check            | Accuracy  | Mode 1 | 24           | 25            | +1    | 340/626/1.84      | Optimized (marginal) |
| 8    | Document Analysis           | Mixed     | Mode 1 | 24           | 25            | +1    | 346/514/1.49      | Optimized (marginal) |
| 9    | Comparative Analysis        | Mixed     | Mode 2 | 24           | 25            | +1    | 330/331/1.00      | Optimized (marginal) |
| 10   | Creative Brief              | Creative  | Mode 4 | 18           | 25            | +7    | 184/415/2.26      | Optimized |
| 11   | Context File (CLAUDE.md)    | Harness   | Mode 3 | 17           | 24            | +7    | 378/232/0.61      | Optimized |
| 12   | Async Rate Limiter (LRM)    | Harness   | Mode 3 | 21           | 25            | +4    | 338/699/2.07      | Optimized |
|------|-----------------------------|-----------|--------|--------------|---------------|-------|-------------------|--------|
|      | AVERAGE                     |           |        | 21.4         | 24.8          | +3.4  | 320/502/1.57      | Optimized 12 of 12 |

Averages are computed from the per test totals and word counts above. Baseline total across 12 tests is 257 points (mean 21.4 of 25). Optimized total is 298 points (mean 24.8 of 25). Mean delta is +3.4 points. Mean baseline length is 320 words; mean optimized length is 502 words; pooled overhead is 6029 divided by 3843, which is 1.57x. Winner means higher total score in this self-evaluation; three Mode 1 wins (Tests 6, 7, 8) and the Lite win (Test 9) are single point wins and should be read as near ties, not as clear superiority.

## 1. Overall Verdict

Yes, make-prompt-better v4.0 improves output quality in this run, by +3.4 points on a 25 point scale (from 21.4 to 24.8), a 16 percent relative gain over the baseline mean. The improvement is real but unevenly distributed and unevenly earned. Every optimized response scored at or above its baseline, and none scored lower on the total, which is itself a signal to distrust: a genuinely neutral judge would expect at least one tie or loss across 12 tasks, and the absence of any loss partly reflects self-evaluation bias favoring structured outputs (see the disclosure at the top of this file). The honest core of the gain is narrower than the headline. Accuracy, the dimension that matters most for the eight analytical tasks, improved in only 3 of 12 tests (Tests 5, 10, 11) and was unchanged in 9. Completeness improved in 3 tests. The reliable, repeatable gain is Traceability, which rose in all 12 tests, plus targeted Structure and Actionability gains where the baseline genre was weak (Tests 10 and 11).

Is the gain worth the token overhead? At the pooled 1.57x, yes for high stakes audit work and for the two genre correcting modes (Creative v2 and Context Files), and no as a universal default. For Tests 6, 7, and 8 the skill spends 1.49x to 1.84x length to buy a single traceability point over a baseline that is already decision ready. Paying a 50 to 84 percent length tax on every routine query to obtain references the requester will never click is poor economics. The verdict is therefore conditional: route deliberately (Max only where audit or stakes demand it, Lite as the analytical default, Harness for persistent files and reasoning models, Creative v2 for divergent writing), rather than applying Max everywhere. A blanket Max policy would keep the +3.4 average while wasting most of its cost on tasks that needed +0 to +1.

## 2. Where It Helped Most

Largest deltas: Test 10 Creative (+7) and Test 11 Context File (+7), followed by Test 2 Financial (+5), then Tests 1, 4, and 12 (+4 each).

Test 10 helped most because the baseline failure was structural, not factual. A competent baseline still falls into the highest typicality ergonomic pitch (comfort adjectives, feature list, order now close) because that is what product copy defaults to. Verbalized Sampling [NT0] makes the default explicit (p = 0.55), prices it, and discards it in favor of a priced low typicality alternative (p = 0.10, the hour 9 workday timeline). The SC0 contract then enforces discourse level rarity (delayed thesis, evidence progression, practitioner voice, test based close) that paragraph level editing cannot achieve. This is the one test where the skill changes what is written, not just how it is cited.

Test 11 helped most for the opposite reason: subtraction. The baseline CLAUDE.md is helpful to a human and harmful as permanent agent context (overview, folder tour, PEP8 lecture re-read every session). Mode 3 [V1] Minimal Viable Context deletes everything discoverable and keeps only the two unguessable commands and the SCHEMA_EPOCH invariant. The optimized file is shorter (0.62x), scores higher, and will keep saving tokens on every future session, so its lifetime value dwarfs the single response saving.

Tests 1, 2, 4, and 12 share a pattern: the task contains a trap that unstructured answers can step around without noticing. In Test 1 the trap is silent assumption (percent versus fraction); in Test 2 it is unshown arithmetic and invisible missing leverage data; in Test 4 it is blending duration, geography, and scope into one impression; in Test 12 it is asserting race freedom without naming the await between check and deduct. Premise plus trace structure forces each trap into a labeled cell (UNABLE TO TRACE, INSUFFICIENT DATA, NOT ADDRESSED, VIOLATED or SATISFIED), where it must be answered or explicitly carried as a gap. Where a trap exists, Max earns its overhead.

## 3. Where It Helped Least (or Hurt)

Smallest deltas: Tests 6, 7, 8, and 9, each +1. No test shows a negative total delta, but three show a negative signal dimension or a negative efficiency judgment that the totals conceal.

Tests 6 (Auth0 versus Clerk versus build), 7 (NIST 800-63B), and 8 (vendor claim credibility) are tasks where a strong baseline is already structured by professional convention: decision memos already compare options on shared criteria, compliance reviews already go clause by clause, and credibility reviews already ask for baselines and methods. Re-imposing the same structure with [P] and [T] labels adds references without adding findings. In Test 6 the optimized response even reaches the identical recommendation with the identical BAA caveat; the certificate contributes only the REQUIRES VERIFICATION label. These are not skill failures. They are routing failures in the evaluation design, which assigns Max to tasks that Lite was built for. Had Tests 6 to 8 used Lite, the same +1 would likely have arrived at roughly 1.0x instead of 1.49x to 1.84x.

Test 5 shows the one dimension level loss: Structure drops from 5 to 4. The optimized research synthesis is more honest (it refuses a numeric consensus from an empty corpus), but it answers a request for a balanced overview with corpus bookkeeping, and a general reader is worse served. The skill correctly prevents hallucinated citation, but it overcorrects toward audit language when the user asked for orientation. A better optimized behavior would lead with the conditional synthesis in plain prose and confine UNEXAMINED IN CORPUS labels to a closing evidence note.

Hurt, in the absolute sense, occurs nowhere on totals. Hurt in the cost sense occurs in Tests 6 and 10 read together: Test 10 spends 2.26x (the suite maximum) for its +7, and Test 6 spends 1.63x for +1. Any deployment that averages these two as about 1.9x for +4 will misbudget. Cost must be judged per mode and per task trap, not pooled.

## 4. v4.0 Mode Evaluation (Max vs. Lite vs. Harness vs. Creative v2)

Mode 1 Max (Tests 1 to 8): Mean baseline 22.1, mean optimized 24.9, mean delta +2.8, pooled overhead 4352 divided by 2613, which is 1.67x (below the roughly 2.2x figure reported for semi-formal reasoning by Ugare and Chandra, 2026, because these baselines are already long). Max is validated as an audit instrument and refuted as a default. Its value concentrates in trap bearing tasks (Tests 1, 2, 4) and dissipates on convention structured tasks (Tests 6, 7, 8). Recommendation: keep Max, gate it on stakes, audit need, or known baseline weakness.

Mode 2 Lite on Test 9: Overhead target met decisively. Optimized length is 331 words against a 330 word baseline (1.00x, against a cap of 1.5x), with quality preserved (25 versus 24, no dimension lower). The three premise cap and single line traces retain the load bearing content (volume arithmetic for years 1 to 3, crossover conditions, two prototype queries) and discard only elaboration. Lite is the clearest success in v4.0 and the strongest argument that earlier benchmark token bloat was a Max selection problem, not a certificate problem. One test cannot prove Lite across domains, but nothing in Test 9 suggests rigor was sacrificed. Lite should become the default analytical mode.

Mode 3 Harness and LRM on Tests 11 and 12: Both design claims hold, with one qualification. On Test 11, context bloat is prevented in fact: the optimized CLAUDE.md is 18 lines (gate: under 150), contains zero directory overview and zero generic style lines, and is 0.61x the baseline length while scoring +7. On Test 12, race conditions are prevented in the verifiable sense: gates [V1] to [V4] name bounds, atomicity, timeout truthfulness, and liveness before code exists, and the self-test harness exercises concurrent acquire without overdraft. Both baseline and optimized code are race-free on accounting, so the mode prevents races at the specification level rather than fixing a baseline race that never occurred. Qualification: Test 12 overhead is 2.07x, above the SKILL.md Mode 3 band of about 1.1x to 1.3x, because the harness is printed inline. The band is achievable only when the harness lives in a test file, which the skill should state explicitly.

Mode 4 Creative v2 on Test 10: Voice and structural originality improve unambiguously over baseline. The baseline is fluent and forgettable; the optimized final copy (4:47pm opening, hour by hour evidence, self test close) could not have been produced by asking for better adjectives. Both halves of the mode contribute: Verbalized Sampling selects the divergent angle, and the SC0 contract prevents the selected angle from collapsing back into thesis first, contrast table, summary ending shape during drafting. The cost is the suite highest ratio (2.26x with backstage counted) and a new production risk: backstage leakage. Mode 4 should ship with a hard rule that [NT0] to [NT3] never appear in user facing output outside evaluations.

## 5. Accuracy vs. Mixed vs. Creative vs. Harness

Accuracy tasks (Tests 1, 2, 3, 4, 7; all Mode 1, persona omitted): Baseline mean 21.6, optimized mean 25.0, delta +3.4, pooled overhead 1.68x (ratios per test: 1.43, 1.52, 1.84, 1.77, 1.84). This is the strongest Max showing, driven by completeness and traceability rather than by corrected facts: accuracy itself is flat in four of five tests because the baseline facts and calculations were already right. The exception pattern matters: where accuracy did move elsewhere (Tests 5, 10, 11), it moved because the optimized prompt forbade a specific invention (numeric consensus without sources, trial terms without facts, guessed commands). Persona omission is consistent with PRISM (Hu, Rostami and Thomason, 2026) throughout these tests, and nothing in the results challenges it: no accuracy test suffers from a missing persona, and the two medical and legal disclaimers function without role play.

Mixed tasks (Tests 5, 6, 8, 9; Modes 1 and 2, minimal persona): Baseline mean 23.3 (21, 24, 24, 24), optimized mean 24.8 (24, 25, 25, 25), delta +1.5, the smallest category gain. Mixed tasks start nearest the ceiling because professional genres (decision memo, credibility review, comparison) already impose structure. PRISM minimal persona (at most five words: You are an analyst, You are a decision analyst) does no measurable harm and no measurable good in this run; scores with and without the line would be indistinguishable. The actionable finding is modal, not personal: mixed tasks should default to Lite. Test 9 (Lite, +1 at 1.00x) dominates Tests 6 and 8 (Max, +1 at 1.63x and 1.49x) on value.

Creative task (Test 10; Mode 4, practitioner persona): 18 to 25 (+7). Harness tasks (Tests 11, 12; Mode 3, persona omitted): baseline mean 19.0, optimized mean 24.5, delta +5.5 at pooled overhead 931 divided by 716, which is 1.30x (0.61x and 2.07x combined). Harness shows the best delta per token in the suite because its baselines commit genre errors (bloated context file, unverified concurrency assurance) that the modes directly prohibit.

Does PRISM based persona calibration work as intended? Directionally yes, evidentially weak. The design (omit on accuracy, cap on mixed, allow on creative) produces no observed penalty and matches the creative success, but with one creative test and no persona ablation, this evaluation cannot estimate a persona effect. The claim remains plausible and untested here, not confirmed.

## 6. Traceability Specifically

Traceability is the one dimension that improves in every test, from a baseline mean of 3.3 (scores: 3, 4, 3, 3, 3, 4, 4, 4, 4, 2, 2, 3) to an optimized mean of 5.0 (5 in all 12 tests), a mean gain of +1.7. The optimized ceiling is uniform by construction: the TRACEABILITY SELF-CHECK requires every conclusion claim to cite a [T] or [V] identifier, and a response that follows its own prompt will satisfy a rubric that rewards citations. Readers should therefore discount part of this gain as rubric alignment. The self-check manufactures the evidence the scorer then counts.

Discounted, a genuine residue remains, and it takes three forms that a citation count alone does not explain. First, gap honesty: UNABLE TO TRACE (Test 1 caller convention), INSUFFICIENT DATA (Test 2 leverage), ABSENT FROM P1 (Test 8 claim elements), UNEXAMINED IN CORPUS (Test 5, entire literature), REQUIRES VERIFICATION (Test 6, both vendor BAAs), and UNABLE TO VERIFY (Test 7, omitted controls) are six different ways of refusing to assert, each matched to its domain. Baselines express the same doubts in prose, where they are easy to skim past; certificates promote them to first class outputs that downstream checklists can consume. Second, dependency exposure: Test 8 shows ROI inheriting the undefined ticket metric, and Test 12 shows timeout correctness depending on recomputing remaining time after each wake. These are claim graphs, not claim lists, and only the traced versions reveal them. Third, executability: Test 12 traceability terminates in asserts that can fail. That is traceability that can be wrong in public, which is the only kind that fully deserves the name.

Verdict on traceability: genuinely more traceable, by less than +1.7. A fair external estimate, stripping rubric alignment, is roughly half the measured gain. Even halved, it is the most consistent benefit in the suite and the best justification for certificate structure where audit matters.

## 7. Token Cost vs. Value

Pooled: baseline 3843 words, optimized 6029 words, ratio 1.57x, buying +41 total points (257 to 298), or about 53 added words per point gained. By mode: Mode 1 Max (Tests 1 to 8) costs 1.67x pooled (2613 to 4352 words) for a mean +2.8 points (about 79 added words per point on a totals basis, heavily skewed by Tests 6 to 8 at 1.49x to 1.84x per single point). Mode 2 Lite (Test 9) costs 1.00x for +1 point (1 added word in total; length is unchanged). Mode 4 Creative (Test 10) costs 2.26x for +7 points (about 33 added words per point, backstage included; final copy alone is roughly 240 words, which would be about 1.3x). Mode 3 Harness (Tests 11, 12) costs 1.30x pooled for a mean +5.5 points (about 20 added words per point pooled, because Test 11 saves 146 words while gaining 7 points and Test 12 spends heavily on its printed harness).

Three cost findings follow. First, the skill v4.0 framing that Max runs about 2.2x overstates cost against a strong modern baseline: observed Max is 1.67x pooled, with a per test range of 1.43x to 1.84x. Against a weak baseline (short, unstructured answers), Max would indeed approach 2.2x, so the figure describes baseline weakness more than certificate size. Second, length and value are uncorrelated across modes: the cheapest mode (Lite) and the saving mode (Context Files) deliver clean gains, while mid cost Max delivers both the second best and the worst value in the suite depending on task selection. Mode choice, not certificate verbosity, controls economics. Third, evaluation counting flatters Mode 4 and penalizes Mode 3 in opposite ways: Mode 4 backstage is scaffolding that production would hide (true delivered cost is the final copy only), while the Test 12 harness is a durable test asset whose cost should be amortized across the repository lifetime, not charged to one answer. Reported ratios should be read with those two adjustments.

Value per token ranking, best to worst: Mode 3 Context Files, Mode 2 Lite, Mode 4 Creative (delivered copy only), Mode 3 LRM with inline harness, Mode 1 Max on trap bearing tasks, Mode 1 Max on convention structured tasks. The practical budget rule is: spend Max tokens only when a wrong answer is expensive or an audit is owed; otherwise Lite captures most of the traceability at baseline length.

## 8. Failure Modes Observed

No optimized response is worse than its baseline on total score. The failure modes below are therefore inefficiencies, distortions, and near misses observed inside winning responses, plus baseline genre failures the skill exists to correct. Each item names its test so a maintainer can reproduce it.

1. Max over provisioning on convention structured work (Tests 6, 7, 8). Certificate scaffolding restates structure the genre already supplies. Symptom: +1 at 1.49x to 1.84x. This is the most frequent failure (3 of 12 tests) and the most expensive in aggregate tokens.
2. Audit language displacing the requested artifact (Test 5). Corpus disclaimers consume the overview the user asked for; Structure falls 5 to 4 while total still rises, so total only scoring would hide the regression. Any v4.1 rubric should treat a dimension level loss as reportable even when the total wins.
3. Backstage leakage risk (Test 10). The evaluation requires visible [NT0] scaffolding; production copy that retained typicality probabilities would be unusable. The skill text permits enclosing scaffolding in backstage tags but does not mandate stripping. Observed here as a deployment hazard, not as an output defect.
4. Inline harness inflating LRM overhead (Test 12). Printing the self-test in the answer pushes Mode 3 to 2.07x against a stated 1.1x to 1.3x band. The harness is valuable exactly once; without a file placement rule, every answer re-pays it.
5. Rubric gaming by construction (all tests, strongest in Tests 1, 3, 4). The self-check guarantees citable claims, and the evaluation rubric rewards citable claims, so Traceability 5s are partly manufactured. A maintainer reading only this report would overestimate external traceability gains by up to twofold (see Section 6).
6. Deliberate completeness loss misread as a defect (Test 11). The optimized CLAUDE.md omits orientation a human wants. Scored as correct for an agent file, it would fail as onboarding documentation. The mode needs an audience guard: agent file and human README are different artifacts.
7. Baseline genre failures corrected by the skill (Tests 10, 11). For symmetry: the baseline chair copy invents a return privilege never supplied, and the baseline CLAUDE.md buries two unguessable commands inside a PEP8 lecture. These are the errors (unsupplied facts, buried invariants) that positive predicate recipes and Minimal Viable Context exist to prevent, and both optimized responses avoid them.
8. No observed hallucination introduction. In no test does the optimized response invent a citation, benchmark, statute, price, or vendor eligibility that the baseline avoids. The positive predicate design (record the gap) held under all 12 prompts, including the empty corpus Test 5 and the unverifiable vendor Test 6. This null result is the strongest safety finding in the run.

## 9. Recommendations for v4.1 Skill Improvement

Each recommendation is concrete, located in SKILL.md or domain-templates.md, and tied to the test evidence above. They are ordered by expected value.

1. Make Lite the analytical default in SKILL.md Step 1b. Change the Mode 2 row trigger from routine analytical tasks to all analytical tasks without a named audit, regulatory, safety, or high stakes condition, and change Mode 1 to require an explicit stakes or audit justification. Evidence: Tests 6, 7, 8 (+1 at 1.49x to 1.84x under Max) versus Test 9 (+1 at 1.00x under Lite).
2. Add a trap test to Step 2 diagnosis. Before selecting Max, require the optimizer to name the specific silent assumption, unshown calculation, blended issue, or unverified invariant the certificate will expose. When no trap can be named, route to Lite. Evidence: Max earns overhead exactly where a trap exists (Tests 1, 2, 4, 12) and wastes it where none does (Tests 6, 7, 8).
3. Mandate backstage stripping in Template 12 and SKILL.md Mode 4. Add a delivery rule: [NT0] to [NT3] and [SC0] are never present in user facing output; deliver final copy only, with scaffolding available on request. State that reported Mode 4 overhead counts final copy only. Evidence: Test 10 at 2.26x with scaffolding versus about 1.4x delivered.
4. Add a harness placement rule to Mode 3 Pattern A. Verification harnesses belong in a named test file path; the answer cites the path and the gate results instead of printing the harness, unless the user requests inline code. Restate the 1.1x to 1.3x band as conditional on this placement. Evidence: Test 12 at 2.07x inline.
5. Add a plain language lead option to Template 3 (Research Synthesis). When no corpus is supplied, lead with a two or three sentence conditional synthesis in prose, then place UNEXAMINED IN CORPUS bookkeeping and the search protocol after it. Evidence: Test 5 Structure regression (5 to 4) inside a winning total.
6. Add an audience guard to Template 11. State explicitly: produce the minimal agent file; when the requester also needs human onboarding, name a separate README as a follow up artifact instead of expanding the agent file. Evidence: Test 11 completeness trade (optimized file wins for agents, loses for newcomers).
7. Temper the Traceability Self-Check with an external check suggestion. In SKILL.md Step 4, note that self-citation satisfies internal traceability only, and recommend (for high stakes outputs) one externally falsifiable element per certificate: a runnable test, a recomputed figure, or a quoted source line. Evidence: Section 6 discount; Test 12 harness as the positive model, Test 2 arithmetic as the second model.
8. Report mode economics honestly in SKILL.md. Replace the single Max overhead figure with observed ranges by baseline strength (about 1.7x against structured baselines in this run, approaching 2.2x against minimal baselines) and add the Lite observed result (1.00x on Test 9). Maintainers and users currently cannot budget from one number. Evidence: Section 7 pooled and per mode ratios.
9. Add one worked Lite example to references/examples.md for a decision or compliance task (the Tests 6 to 8 shape). The current example set demonstrates Max heavily; a Lite decision example would teach the routing Recommendation 1 depends on. Also add a note to the EVALUATION_PROMPT lineage: future benchmark iterations should pre-register Lite for Tests 6 to 8 so longitudinal Max comparisons do not keep paying for a known misrouting.

Closing note: v4.0 is a routing system that is currently benchmarked as a Max system. Its two new routing ideas (Lite economy, Harness subtraction) and its creative repair (Verbalized Sampling plus Anti-SlopShape) all validate. Its legacy center (Max everywhere) does not. Version 4.1 should be a smaller change than v4.0: keep the certificates, fix the defaults.

End of evaluation. File written for model slug meta-muse-wonder-1.0-max. All scores are self-evaluated; see the bias disclosure at the top of this file before citing any delta externally.







