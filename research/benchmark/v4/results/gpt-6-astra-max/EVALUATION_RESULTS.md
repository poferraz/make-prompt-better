# make-prompt-better: GPT-6-Astra Max evaluation

Requested benchmark: v4.0. Required skill files actually present: v4.2.0. Requested model configuration: `gpt-6-astra` with reasoning effort `max`, saved under `gpt-6-astra-max`.

**Execution status and limitation:** The user requested faster completion after warning of 40% remaining usage. The expensive isolated launch loop was stopped. Test 1 uses the isolated CLI outputs where available; remaining cases are generated in this conversation, baseline first, followed by prompt compilation, a fresh-perspective answer and self-evaluation. Fresh perspective is not context isolation. The current conversation's exact server-side model alias is not independently exposed; the CLI requests explicitly specify the requested model and effort. This is a complete twelve-case exploratory report, not a fully controlled or independently double-blind benchmark. Its scores must not be pooled with isolated controlled runs without this qualification.

All required source files were read in full before execution. The suite's template numbering differs from the current library: tests 1-12 map to current templates 1, 9, 7, 8, 3, 5, 4, 2, 6, 10, 11, 12. The suite's explicit three creative candidates with typicality below 0.15 and V1-V3 gates take precedence. Test 11 deliberately removes raw-request content, creating a fidelity tradeoff.

The generator is also the judge and has seen the prompts. A/B labels below are presentation labels, with A = baseline and B = optimized; they do not establish blinding. Independent reversed-order scoring was not performed, so position-swap consistency is **not measured** for every case. Scores are subjective 1-5 ordinal judgments, and trace labels alone earn no credit.

Word counts use whitespace-delimited tokens in each complete response, including code, references and creative scaffolding, excluding raw/compiled prompts and evaluations. Visible-token estimates use `ceil(UTF-8 bytes / 4)`, a rough reproducible proxy rather than a model tokenizer or billing measurement. Actual isolated CLI usage is separately retained in [run-data.json](run-data.json) and [artifacts](artifacts/). The in-session calls have no separate per-case usage telemetry. Unicode em/en dashes are normalized in this Markdown report. No numerical scores or evidence are presented as population estimates.

The research rationale follows the supplied files; their empirical paper claims were not independently replicated or systematically verified here. Source snapshots, original CLI outputs, and the excluded setup attempt are retained. The first setup attempt used an ignored CLI setting and was excluded before optimization. [fast-data.json](fast-data.json) records the final report's response texts and self-scores.

## TEST 1: Code Review

Accuracy task; Mode 1; benchmark template 1, current domain template 1.

### RAW PROMPT

````text
Look at this Python function and tell me if it has any bugs.

def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 10
    final_price = price - (price * discount_percent)
    if final_price < 0:
        return 0
    return final_price
````

### BASELINE RESPONSE

Yes. Assuming `20` means a **20% discount**, the calculation is missing division by `100`.

For example, `calculate_discount(100, 20, False)` currently returns `0` instead of `80`.

Corrected version:

```python
def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 10
    final_price = price - (price * discount_percent / 100)
    return max(0, final_price)
```

This assumes membership adds **10 percentage points**, turning a 20% discount into 30%. Negative prices and negative discount percentages remain unvalidated.

### OPTIMIZED PROMPT

````text
The standard code review protocol requires completing a full evidence-grounded certificate before issuing a verdict. Review the supplied Python function for bugs. Return PREMISES, EXECUTION TRACES, FORMAL CONCLUSION, REMEDIATION / NEXT ACTION, and TRACEABILITY SELF-CHECK in that order. Present analysis and proposed code inline.

### PREMISES

- [P1] Source artifact and original request, verbatim:

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

  This is the complete supplied artifact. A filename, repository context and modification history were not supplied. Cite locations as snippet-relative line numbers, counting the function definition as line 1; retain the original code unchanged.

- [P2] Symbol, review scope and behavioral contract: Review `calculate_discount(price, discount_percent, is_member)` for functional correctness through its control flow, arithmetic and return paths. The intended input types and ranges, discount representation, membership adjustment semantics, expected outputs, invalid-input handling, result bounds and rounding policy are unspecified. Record these as contract gaps. When exploring a possible interpretation, label it ASSUMPTION and make dependent findings conditional. Distinguish correctness defects from optional robustness improvements.

- [P3] Tests, runtime and supporting evidence: No tests, sample calls, execution results, Python version, caller implementations or runtime type specifications were supplied. Preserve these as explicit gaps. Distinguish supplied facts, sourced language facts, assumptions, proposed tests and missing evidence. When language semantics require verification, consult primary sources such as official Python documentation and record the applicable version, section and URL here. Documentation can establish language behavior; the function's intended contract requires separate evidence. Label test inputs created during review as PROPOSED, and report tests as NOT RUN unless actual execution evidence is available.

Keep the premise identifiers P1-P3, grouping any additional source evidence or explicitly labeled assumptions under the appropriate premise.

### EXECUTION TRACES

Create uniquely numbered traces [T1], [T2], and onward. Cover every feasible control-flow path, relevant arithmetic and return behavior, and pertinent boundary or type cases under explicitly stated input assumptions. Provide checkable execution evidence for each trace:

1. Grounding: Cite the relevant [P1]-[P3] premises and exact snippet lines. Identify any contract or runtime assumption used.
2. Entry: State the input conditions and types. When using concrete diagnostic inputs, identify them as proposed probes rather than supplied cases.
3. Execution: Follow the actual statements in order, showing branch decisions, value transformations and relevant state changes.
4. Exit: Record the derived return value, exception or other observable effect. Distinguish static derivation from an executed result; for executed tests, include the command and observed output.
5. Contract comparison: Identify the stated requirement or labeled assumption that determines the expected behavior. Classify the result as a verified observation, confirmed defect, conditional defect or unresolved question.

When a path or correctness claim depends on missing information, record `UNABLE TO TRACE:` followed by the exact missing input and the evidence needed to resolve it. Continue tracing whatever the supplied implementation establishes independently of that gap.

When counterexamples or evidence against a candidate finding emerge, give them a dedicated [T] trace and reconcile them with the finding. Ground behavior in implementation statements and applicable language rules rather than symbol names.

### FORMAL CONCLUSION

- Verdict: PASS, FAIL or INCONCLUSIVE for the explicitly stated scope and contract. Use FAIL when a trace establishes a contract violation; use PASS only within the verified scope. Make any assumption-dependent verdict explicitly conditional. Use INCONCLUSIVE where missing evidence prevents a determination.
- Findings: Separate confirmed defects, assumption-dependent concerns and verified behavior. Cite supporting [T] identifiers and affected snippet lines for each finding.
- Verification gaps: Carry forward every `UNABLE TO TRACE` item, citing its trace and identifying the exact missing contract, test, runtime fact or source artifact.
- Confidence: HIGH, MEDIUM or LOW, with a justification citing the supporting traces and limitations.

Every conclusion claim, including confidence and scope limitations, must cite at least one supporting [T] identifier.

### REMEDIATION / NEXT ACTION

Tie each action to the relevant [T] identifiers:

- When a traced defect has a sufficiently established contract, provide a complete, copy-pasteable corrected function and runnable regression tests addressing it. Explain any behavior changes and label test execution status accurately.
- When a correction depends on an unresolved contract, list the precise clarification questions and concrete verification steps needed. Label any proposed implementation or expected test result as conditional on its stated assumptions.
- When traces justify leaving the implementation unchanged, write `No remediation required:` followed by a trace-supported reason limited to the verified scope. Give concrete next steps for any remaining verification gaps.

### TRACEABILITY SELF-CHECK

The standard verification protocol requires completing this check before finalizing:

- Data binding: Confirm that the original request and code in [P1] remain verbatim and that supplied facts are distinguishable from assumptions, sourced facts and proposed diagnostic inputs.
- Coverage: Confirm that each feasible control-flow path has a trace or an explicit missing-evidence entry.
- Evidence predicates: When a claim lacks support, add a trace grounded in the premises, qualify it as conditional, or remove it. When evidence is missing, preserve the exact gap in both its trace and Verification Gaps.
- Execution integrity: Confirm that every claimed test execution has observed command/output evidence; retain NOT RUN for unexecuted tests.
- Neutrality: Derive findings from traced behavior and stated requirements, preserving uncertainty where intent is unspecified.
- Conclusion and action coverage: Confirm that every conclusion claim and remediation action cites supporting [T] identifiers and that all cited identifiers exist. Report whether any unresolved traceability gaps remain.
````

Method rationale: The supplied skill motivates the Max certificate, remediation and self-check (Ugare & Chandra, 2026); stable identifiers and verbatim data binding (Zhang, Hu et al., 2026); evaluation-context isolation (Cao, Jiang & Xu, 2026); persona omission (Hu, Rostami & Thomason, 2026); and protocol authority with positive evidence predicates (Geng et al., 2025; Yin et al., 2026). These citations describe the supplied methodology, not independently verified empirical results.

### OPTIMIZED RESPONSE

#### PREMISES

- [P1] The supplied seven-line function adds `10` for members, subtracts `price * discount_percent`, then floors negative results at zero.
- [P2] ASSUMPTION: inputs are ordinary finite numbers; `20` denotes 20%, and membership adds ten percentage points. The input contract and rounding policy are unspecified.
- [P3] No caller, runtime specification or tests were supplied. The following probes are statically derived; tests are provided below, not claimed executed here.

#### EXECUTION TRACES

- [T1] Nonmember, proposed `(100, 20, False)`: line 2 skips the increment; line 4 computes `100 - 100 * 20 = -1900`; lines 5-6 return `0`. Under [P2], the expected price is `80`. The percentage conversion is missing.
- [T2] Member, proposed `(100, 20, True)`: line 3 makes the discount `30`; line 4 computes `-2900`; line 6 returns `0`, versus `70` under [P2]. This also exercises the membership branch.
- [T3] Counterexample, proposed `(100, 0.2, False)`: line 4 returns `80` through line 7. Fractional representation makes the nonmember calculation work, but membership would add `10`, rather than a fractional `0.10`. Thus the two operations use inconsistent units under either conventional interpretation.
- [T4] Proposed `(100, 0, False)` returns `100`; `(0, 20, True)` returns `0`. Negative discounts can increase the charge, and sufficiently large discounts are floored at zero. These are observations; their acceptability depends on the missing policy.
- [T5] Nonfinite numbers, unsupported types, monetary rounding and whether membership is additive or sequential: `UNABLE TO TRACE: intended input and pricing contract`. Custom numeric objects could also change operation semantics.

#### FORMAL CONCLUSION

Conditional FAIL under the ordinary percentage-point interpretation: the arithmetic needs `/ 100` [T1-T2]. A fractional interpretation does not resolve the member increment [T3]. Valid-input boundary behavior is observable, while invalid-input and rounding requirements remain unverified [T4-T5]. Confidence is high in these static calculations and limited regarding business intent [T1-T5].

#### REMEDIATION / NEXT ACTION

Under [P2], this complete minimal correction fixes [T1-T2] while preserving the existing floor:

```python
def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 10
    final_price = price - price * discount_percent / 100
    return max(0, final_price)

assert calculate_discount(100, 20, False) == 80
assert calculate_discount(100, 20, True) == 70
assert calculate_discount(100, 0, False) == 100
assert calculate_discount(0, 20, True) == 0
assert calculate_discount(100, 100, False) == 0
```

Proposed regression tests, not execution evidence. Confirm accepted numeric types, discount units, additive versus sequential membership, values above 100%, negative inputs and currency rounding before adding validation [T3-T5].

#### TRACEABILITY SELF-CHECK

All seven supplied lines and both membership outcomes appear in the traces. Every conclusion and action cites evidence; missing intent remains explicitly conditional. Custom-type and nonfinite behavior are unresolved rather than certified [T5].

### EVALUATION: TEST 1

Baseline Words: 71 | Optimized Words: 440 | Overhead Ratio: 6.197x. Visible-token proxy: Baseline 144; Optimized 801; ratio 5.562x. Compiled prompt: 925 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both identify the missing conversion under the same stated percentage convention. |
| Completeness | 4 | 5 | +1 | B adds fractional-unit counterevidence, boundary probes and explicit contract gaps. |
| Structure | 5 | 3 | -2 | A answers a small question directly; B repeats scope and verification material across five sections. |
| Actionability | 5 | 5 | +0 | Both supply a usable minimal correction; B adds runnable regression assertions. |
| Traceability | 4 | 5 | +1 | A supplies a concrete numerical counterexample; B maps branches and findings to inspectable calculations. |
| **TOTAL (/25)** | **23** | **23** | **+0** | **Winner: Tie** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The main diagnosis and fix are unchanged. Extra traceability and boundary coverage are offset by substantial formality, so the totals tie. The expanded prompt is especially costly for a seven-line function.

Provenance: Baseline and prompt compiler: isolated gpt-6-astra/max CLI calls. Optimized response and scores: this conversation; the unfinished isolated optimized request was cancelled and excluded.
## TEST 2: Financial Analysis

Accuracy task; Mode 1; benchmark template 2, current domain template 9.

### RAW PROMPT

````text
A company reports $50M revenue in Q1, $47M in Q2, $52M in Q3, and $61M in Q4. Operating expenses were 78% of revenue in Q1, 82% in Q2, 75% in Q3, and 71% in Q4. They took on $15M in new debt in Q3. Analyze their financial health.
````

### BASELINE RESPONSE

The business ends the year with stronger revenue and a lower reported expense ratio, but these figures alone cannot establish liquidity or debt sustainability.

| Quarter | Revenue ($M) | Reported expenses ($M) | Revenue less those expenses ($M) | Residual margin |
| --- | ---: | ---: | ---: | ---: |
| Q1 | 50 | 39.00 | 11.00 | 22% |
| Q2 | 47 | 38.54 | 8.46 | 18% |
| Q3 | 52 | 39.00 | 13.00 | 25% |
| Q4 | 61 | 43.31 | 17.69 | 29% |
| Year | 210 | 159.85 | 50.15 | 23.88% |

Each expense figure is revenue multiplied by the given percentage. The residual is operating profit only if the expense definition includes all relevant operating costs, including cost of revenue.

Revenue grows 22% from Q1 to Q4, with sequential changes of -6%, +10.64% and +17.31%. These are within-year comparisons, not year-over-year growth. Q2 is the weak quarter; Q4's expense ratio is seven percentage points lower than Q1's, although absolute expenses rise.

The $15M borrowing could fund growth, refinance obligations or cover a cash shortfall. Its purpose and the company's total debt are unknown. Accounting earnings also differ from cash flow because of accruals and noncash items. [IAS 7 overview](https://www.ifrs.org/issued-standards/list-of-standards/ias-7-statement-of-cash-flows.html)

Request the balance sheet, cash-flow statement, cost-of-revenue classification, receivables aging, debt balances, interest rates, maturities and covenants. The operating trend is encouraging; solvency and the quality of that improvement remain unresolved.

### OPTIMIZED PROMPT

````text
The financial analytical protocol requires a Max certificate with no persona. Analyze the supplied facts neutrally.
[F1] Supplied case, verbatim:
A company reports $50M revenue in Q1, $47M in Q2, $52M in Q3, and $61M in Q4. Operating expenses were 78% of revenue in Q1, 82% in Q2, 75% in Q3, and 71% in Q4. They took on $15M in new debt in Q3. Analyze their financial health.
[F2] Compute quarterly expenses, revenue less reported expenses, annual weighted margin and sequential revenue changes using only F1. Label any accounting interpretation as an assumption.
[F3] Debt balances, repayment terms, cash flow, prior-year comparators and expense classification are unavailable.
Output premises F1-F3, calculation traces T1 onward, a formal conclusion citing those traces, a concrete diligence request list, and a traceability self-check. When a metric needs an absent input, write INSUFFICIENT DATA and identify that input. When counterevidence appears, include it in its own trace. Distinguish profitability, liquidity and solvency. Verify each conclusion against a calculation or identified gap; use primary sources for external accounting rules.
````

Method rationale: Numerical traces and explicit gaps follow (Ugare & Chandra, 2026); neutral task framing follows (Cao, Jiang & Xu, 2026); conditional evidence recipes follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

#### PREMISES

[F1] Revenues are $50M, $47M, $52M and $61M; reported expense ratios are 78%, 82%, 75% and 71%; Q3 new borrowing is $15M.
[F2] All periods are quarters of the same unspecified year. Expense classification is unverified.
[F3] Balance sheets, cash flows, prior-year figures and financing terms are absent.

#### FINANCIAL TRACES

[T1] Expenses = revenue times ratio; residual = revenue minus expenses:

| Quarter | Expenses ($M) | Residual ($M) | Residual/revenue |
| --- | ---: | ---: | ---: |
| Q1 | 50 × .78 = 39 | 11 | 22% |
| Q2 | 47 × .82 = 38.54 | 8.46 | 18% |
| Q3 | 52 × .75 = 39 | 13 | 25% |
| Q4 | 61 × .71 = 43.31 | 17.69 | 29% |

Totals: revenue = 210; expenses = 159.85; residual = 50.15, all $M. Weighted residual margin = 50.15/210 = 23.88%. Calling this operating profit requires confirming that reported expenses include all operating costs.

[T2] Sequential revenue growth = current/prior minus one: -6%, +10.64%, +17.31%. Q4/Q1 minus one = 22%; this is not annual year-over-year growth.

[T3] Counterevidence: Q2 revenue and residual margin deteriorate. Q4's lower expense ratio does not mean lower dollar expenses: $43.31M versus $39M in Q1. Seasonality and revenue quality are unexamined.

[T4] INSUFFICIENT DATA: leverage needs total debt and an appropriate denominator; debt service coverage needs cash-generation and payment information. New borrowing is a flow, not the ending debt stock. Profit and cash flow differ through accruals and noncash adjustments. [IAS 7](https://www.ifrs.org/issued-standards/list-of-standards/ias-7-statement-of-cash-flows.html)

#### FORMAL CONCLUSION

The reported operating trend improves after Q2 [T1-T3]. Liquidity, leverage and debt sustainability cannot be established [T4]. The residual's accounting classification remains conditional [T1].

#### REMEDIATION / NEXT ACTION

Obtain expense definitions and cost of revenue [T1]; prior-year quarterly figures and customer/concentration data [T2-T3]; cash flow, cash balance, working capital, debt roll-forward, use of proceeds, interest, maturity and covenant schedules [T4]. Reconcile the computed $50.15M residual to the income statement [T1].

Self-check: all conclusions reference a calculation or an explicit evidence gap.

### EVALUATION: TEST 2

Baseline Words: 248 | Optimized Words: 345 | Overhead Ratio: 1.391x. Visible-token proxy: Baseline 385; Optimized 564; ratio 1.465x. Compiled prompt: 173 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both correctly distinguish residual earnings, cash flow and the stock of debt. |
| Completeness | 5 | 5 | +0 | Both include quarterly results, annual weighted margin, growth, Q2 weakness and missing financing information. |
| Structure | 5 | 4 | -1 | A already has a useful table; B repeats the same facts across premise and trace blocks. |
| Actionability | 5 | 5 | +0 | Both supply a concrete diligence list. |
| Traceability | 5 | 5 | +0 | Both show formulas, figures and an accounting source; identifiers add navigation rather than new evidence. |
| **TOTAL (/25)** | **25** | **24** | **-1** | **Winner: Candidate A** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The certificate preserves the strong baseline analysis but adds little substantive coverage. Both avoid mislabeling revenue minus an incompletely defined expense line as proven operating profit. Repetition makes the optimized answer slightly less economical.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 3: Medical Reasoning

Accuracy task; Mode 1; benchmark template 3, current domain template 7.

### RAW PROMPT

````text
A 58-year-old male presents with sudden onset chest pain radiating to the left arm, diaphoresis, and shortness of breath. BP 90/60, HR 110, SpO2 94%. ECG shows ST elevation in leads II, III, and aVF. Troponin pending. What is the most likely diagnosis and what are the immediate priorities?
````

### BASELINE RESPONSE

This is most consistent with an **acute inferior STEMI with hemodynamic instability**, with possible right ventricular involvement. Leads II, III and aVF localize the inferior injury; the ischemic symptoms support acute coronary occlusion. The culprit is often the right coronary artery, but the ECG does not prove the vessel or establish cardiogenic shock without evidence of hypoperfusion.

Activate the emergency STEMI/catheterization pathway immediately; do not wait for troponin. Obtain cardiac monitoring, defibrillation readiness, IV access and rapid bedside assessment. Arrange urgent reperfusion, preferably primary PCI through the local emergency pathway.

Give chewed aspirin if no contraindication; select additional antiplatelet and anticoagulant treatment with the reperfusion team. Assess hypotension with right-sided ECG leads, especially V4R, and bedside echocardiography without delaying reperfusion. Avoid nitrates and other preload-lowering treatment in this hypotensive patient with possible RV infarction. Assess congestion before considering a cautious fluid challenge; persistent shock needs expert hemodynamic support.

SpO2 94% alone does not justify routine oxygen; monitor and treat hypoxemia or respiratory failure. Watch for AV block, malignant arrhythmias and mechanical complications. These are emergency clinician-led priorities. [2025 ACS guideline](https://www.jacc.org/doi/10.1016/j.jacc.2024.11.009)

### OPTIMIZED PROMPT

````text
Apply the clinical Max certificate without a persona. When findings suggest an immediate emergency, put the immediate escalation instruction first, then complete the certificate.
[S1] Case, verbatim:
A 58-year-old male presents with sudden onset chest pain radiating to the left arm, diaphoresis, and shortness of breath. BP 90/60, HR 110, SpO2 94%. ECG shows ST elevation in leads II, III, and aVF. Troponin pending. What is the most likely diagnosis and what are the immediate priorities?
[S2] Separate observed symptoms, vitals and ECG findings from diagnostic inference.
[S3] Symptom duration, medications, contraindications, perfusion findings, right-sided ECG and echo are unavailable.
[S4] Verify relevant emergency priorities against primary clinical guidelines and cite them.
Provide S1-S4 premises, concise T diagnostic/therapeutic traces, a trace-citing formal conclusion, immediate clinician-led next actions and self-check. Include competing high-acuity explanations where discriminating findings matter. When a diagnosis or intervention needs absent information, state that condition explicitly. Derive urgency from supplied observations; keep testing and certificate completion from delaying emergency care.
````

Method rationale: Traceable medical analysis follows (Ugare & Chandra, 2026), persona omission follows (Hu, Rostami & Thomason, 2026), and observable evidence conditions follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

**Activate the emergency STEMI pathway now; do not await troponin.**

#### PREMISES

[S1] Age 58, abrupt ischemic-pattern chest pain, diaphoresis and dyspnea. [S2] BP 90/60, HR 110, SpO2 94%; inferior-lead ST elevation. [S3] Duration, ECG magnitude/reciprocal changes, perfusion, lung exam and medication history are unavailable. [S4] The [2023 ESC ACS guideline](https://academic.oup.com/eurheartj/article/44/38/3720/7243210) supports urgent STEMI evaluation, right-sided leads in suspected inferior STEMI, and withholding nitrates with hypotension or RV infarction.

#### DIAGNOSTIC AND THERAPEUTIC TRACES

[T1] Ischemic symptoms plus II/III/aVF elevation strongly favor an acute inferior STEMI. Right coronary occlusion is plausible, not established. The supplied ECG description is accepted as reported; the actual tracing is unavailable.

[T2] Hypotension and tachycardia indicate instability. RV involvement, LV dysfunction or mechanical complications require assessment. Shock remains a concern rather than a proven diagnosis without perfusion findings.

[T3] Aortic dissection with coronary involvement is an important competing emergency if pulse deficits, tearing pain or neurologic findings emerge. Pericarditis and other ST-elevation mimics remain possible but less supported by the stated focal pattern. Their evaluation must be proportionate to the findings.

[T4] SpO2 94% alone does not require routine oxygen. Nitrates may worsen the current hypotension, particularly with RV involvement. [2025 ACS guideline](https://www.jacc.org/doi/10.1016/j.jacc.2024.11.009)

#### FORMAL CONCLUSION

Working diagnosis: inferior STEMI with hemodynamic instability; evaluate for RV involvement and shock [T1-T2]. The pending biomarker should not postpone the emergency pathway [T1]. Confirmatory and alternative-diagnosis gaps remain [T2-T3].

#### REMEDIATION / NEXT ACTION

Arrange immediate monitored resuscitation and reperfusion-team assessment, IV access and defibrillation readiness [T1-T2]. Give aspirin when contraindications are excluded; coordinate other antithrombotics and urgent PCI with the treating team [T1,T3]. Obtain right-sided leads and bedside echo without delaying reperfusion [T2]. Assess congestion before any cautious fluid challenge; escalate persistent hypoperfusion for specialist support [T2]. Withhold nitrates, monitor oxygenation, and watch for arrhythmias and AV block [T2,T4].

Self-check: findings and uncertainty have trace links. This is educational clinical support; immediate treatment requires the emergency team.

### EVALUATION: TEST 3

Baseline Words: 180 | Optimized Words: 320 | Overhead Ratio: 1.778x. Visible-token proxy: Baseline 359; Optimized 640; ratio 1.783x. Compiled prompt: 163 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both identify inferior STEMI, possible RV involvement and conditional shock, with appropriate oxygen and nitrate cautions. |
| Completeness | 4 | 5 | +1 | B adds a discriminating alternative-emergency check and distinguishes the unavailable actual ECG. |
| Structure | 5 | 4 | -1 | A gives immediate priorities with less navigation; B preserves an emergency-first exception but remains longer. |
| Actionability | 5 | 5 | +0 | Both prioritize urgent reperfusion and parallel hemodynamic assessment. |
| Traceability | 4 | 5 | +1 | B explicitly connects the vital signs, uncertainty and treatment cautions to traces and primary guidance. |
| **TOTAL (/25)** | **23** | **24** | **+1** | **Winner: Candidate B** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The clinical priorities remain essentially the same. The certificate makes diagnostic uncertainty easier to audit but adds reading burden in a time-critical scenario. Keeping emergency escalation before the certificate is necessary for practical usability.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 4: Legal Analysis

Accuracy task; Mode 1; benchmark template 4, current domain template 8.

### RAW PROMPT

````text
An employee signed a non-compete agreement that prevents them from working in "any related industry" within a 200-mile radius for 5 years after leaving the company. They left and took a job at a competitor 150 miles away, 8 months later. The former employer is threatening to sue. Analyze the enforceability of this non-compete.
````

### BASELINE RESPONSE

The employee appears to fall within the clause's stated time and distance limits: eight months is within five years, and 150 miles is within 200 miles. That does not establish that the restriction is legally enforceable.

The governing jurisdiction is essential. Some jurisdictions largely prohibit employee noncompetes; others permit appropriately limited restraints, sometimes with notice, compensation or employee-category requirements. The location of employment, choice-of-law clause, signing date and role all matter.

Where a reasonableness test applies, this clause raises substantial concerns:

- Five years is a severe employment restraint and requires close scrutiny under the applicable law.
- A 200-mile radius needs a connection to the employer's actual protectable market or customer interests.
- “Any related industry” could prohibit work unrelated to the employee's role, confidential knowledge or customer relationships.

The employer could argue that the actual competitor job threatens trade secrets or customer goodwill. Whether a court can narrow an overbroad clause, rather than reject it, also depends on local law. Separate confidentiality or trade-secret claims may survive even if the noncompete fails.

If this is a US matter, do not assume the FTC's nationwide noncompete rule invalidates the agreement: the FTC says that rule is not in effect or enforceable. [FTC status](https://www.ftc.gov/legal-library/browse/rules/noncompete-rule)

Preserve the signed agreement and communications, identify governing law and employment locations, and have local employment counsel assess the threat promptly, especially any injunction deadline. The clause is vulnerable to challenge; a definitive enforceability conclusion is unavailable from these facts.

### OPTIMIZED PROMPT

````text
The analytical protocol requires a Mode 1 certificate. Use no expert roleplay.
[L1] Original request and supplied evidence, verbatim:
An employee signed a non-compete agreement that prevents them from working in "any related industry" within a 200-mile radius for 5 years after leaving the company. They left and took a job at a competitor 150 miles away, 8 months later. The former employer is threatening to sue. Analyze the enforceability of this non-compete.
Use L1 stated facts, L2 governing-law evidence and gaps, and L3 issues. Trace literal coverage separately from enforceability. Use conditional jurisdiction examples with primary citations; when jurisdiction is missing, request it rather than inventing binding law or a purportedly enforceable replacement clause.
When evidence is absent, name the missing input and qualify the affected finding. Include counterevidence. Finish with a conclusion citing T identifiers, concrete next actions, and a self-check that every conclusion has support. Preserve all substantive facts; derive the answer from evidence.
````

Method rationale: Evidence certificates follow (Ugare & Chandra, 2026); goal-blind framing follows (Cao, Jiang & Xu, 2026); positive evidence predicates follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

#### PREMISES

[L1] The quoted scope is “any related industry”; limits are 200 miles and five years. The competitor job began 150 miles away after eight months. [L2] Jurisdiction, complete agreement and signing date are unknown. [L3] Literal coverage and enforceability are distinct questions.

#### LEGAL TRACES

[T1] 150 < 200 miles and eight months < five years: the reported job is within the stated limits, assuming the distance is measured from the contractual reference point.

[T2] The wide industry scope could cover unrelated duties; the employer may instead argue the actual competitor role threatens confidential information or goodwill. Job duties and protectable interests are missing.

[T3] Five years and 200 miles raise substantial proportionality questions where local law tests reasonableness. As an illustration only, Massachusetts imposes statutory duration, geography and activity restrictions; those rules cannot be imported without establishing applicable law. [Massachusetts statute](https://malegislature.gov/laws/generallaws/parti/titlexxi/chapter149/section24L)

[T4] In a US case, the FTC rule supplies no automatic nationwide defense: it is not effective. [FTC status](https://www.ftc.gov/legal-library/browse/rules/noncompete-rule)

#### FORMAL CONCLUSION

The reported facts suggest contractual coverage [T1], with credible breadth objections [T2-T3]. Enforceability remains undetermined because governing law is absent; an FTC blanket-ban argument would be misplaced [T3-T4].

#### REMEDIATION / NEXT ACTION

Give local employment counsel the signed agreement, governing-law/forum clauses, work locations, signing date, termination circumstances, job duties, consideration and demand letter. Ask about narrowing rules, injunction exposure and separate confidentiality claims [T1-T4]. Preserve records and observe response deadlines. Self-check: the conclusion is conditional and every legal inference is linked. This analysis does not replace jurisdiction-specific counsel.

### EVALUATION: TEST 4

Baseline Words: 244 | Optimized Words: 255 | Overhead Ratio: 1.045x. Visible-token proxy: Baseline 445; Optimized 503; ratio 1.130x. Compiled prompt: 157 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both distinguish breach allegations from enforceability and avoid a nonexistent blanket FTC defense. |
| Completeness | 4 | 4 | +0 | Both identify the essential jurisdiction gap; neither can resolve it. |
| Structure | 5 | 4 | -1 | A is easier to scan; B adds repeated scope labels. |
| Actionability | 5 | 5 | +0 | Both give concrete counsel-preparation steps. |
| Traceability | 4 | 5 | +1 | B makes the arithmetic and illustrative statutory anchor explicit. |
| **TOTAL (/25)** | **23** | **23** | **+0** | **Winner: Tie** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The same conditional conclusion survives optimization. Trace references improve navigation, but the missing jurisdiction remains the limiting factor. The added format does not justify a higher total.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 5: Research Synthesis

Mixed task; Mode 1; benchmark template 5, current domain template 3.

### RAW PROMPT

````text
What does the research say about whether remote work improves or hurts productivity? Give me a balanced overview.
````

### BASELINE RESPONSE

Research does not support one universal productivity effect. The job, home environment, degree of remote work and outcome measure matter.

A randomized Chinese call-center experiment found a 13% performance increase from home working; some of the gain came from more minutes worked, not just faster work. [Bloom and colleagues](https://conference.nber.org/confer/2012/CEf12/roberts.pdf) A randomized Indian data-entry study instead reported 18% lower productivity among workers assigned home work. [Atkin, Schoar and Shinde](https://sumitshi.github.io/sumitshinde.net/Worker_Sorting_JMP_SumitShinde.pdf)

For hybrid work, a six-month randomized trial of 1,612 Trip.com employees found improved retention without damaged performance. That is evidence about a specific hybrid arrangement, not proof that fully remote work increases productivity. [Bloom, Han and Liang, 2024](https://www.nature.com/articles/s41586-024-07500-2)

Remote work can support concentrated individual tasks while creating coordination or learning challenges. Those mechanisms need testing in each setting. Surveys of perceived productivity and observational pandemic comparisons are less persuasive about causation than randomized evidence.

For a practical assessment, compare quality-adjusted output, delivery time, rework and retention across comparable teams. Track collaboration and onboarding separately; logged-in hours are not a sufficient productivity measure. These studies support conditional conclusions rather than a single average effect for every occupation.

### OPTIMIZED PROMPT

````text
The analytical protocol requires a Mode 1 certificate. Use no expert roleplay.
[E1] Original request and supplied evidence, verbatim:
What does the research say about whether remote work improves or hurts productivity? Give me a balanced overview.
Use E1 source corpus, E2 study designs and outcomes, E3 coverage limitations. Give a compact evidence table, distinguish hybrid from fully remote and output from hours, and reconcile different findings without averaging incomparable effects. State when the corpus is selective rather than systematic.
When evidence is absent, name the missing input and qualify the affected finding. Include counterevidence. Finish with a conclusion citing T identifiers, concrete next actions, and a self-check that every conclusion has support. Preserve all substantive facts; derive the answer from evidence.
````

Method rationale: Evidence certificates follow (Ugare & Chandra, 2026); goal-blind framing follows (Cao, Jiang & Xu, 2026); positive evidence predicates follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

#### PREMISES

[E1] Selected primary studies are linked below. [E2] Productivity means measured work output or performance, with hours and retention distinguished. [E3] This is a selective overview, not an exhaustive systematic review.

#### EVIDENCE TRACES

| Trace | Design and setting | Finding | Limitation |
| --- | --- | --- | --- |
| [T1] | Randomized Chinese call-center home-work experiment | Performance increased 13%; increased working minutes explain part | Specific tasks and participating workforce |
| [T2] | Randomized Indian data-entry home-versus-office assignment | Home-assigned productivity was 18% lower | Specific occupation and home-work conditions |
| [T3] | Six-month randomized hybrid trial, 1,612 Trip.com employees | Retention improved without damaged measured performance | Hybrid arrangement; performance is not every possible productivity outcome |

Sources: [Bloom et al.](https://conference.nber.org/confer/2012/CEf12/roberts.pdf), [Atkin, Schoar and Shinde](https://sumitshi.github.io/sumitshinde.net/Worker_Sorting_JMP_SumitShinde.pdf), [Bloom, Han and Liang, 2024](https://www.nature.com/articles/s41586-024-07500-2).

[T4] The positive, negative and neutral findings involve different jobs, arrangements and metrics. They are not estimates of one interchangeable treatment; numerical pooling would be unjustified here. Long-term innovation, all industries and all worker populations are UNEXAMINED IN CORPUS.

#### FORMAL CONCLUSION

Remote work can improve or reduce measured productivity depending on the setting [T1-T2]. The hybrid trial supports retention gains without measured performance damage in its setting [T3]. No universal productivity claim follows [T4].

#### REMEDIATION / NEXT ACTION

Run a comparable-team pilot with predeclared quality-adjusted output, rework, delivery and retention measures; distinguish novice onboarding from established individual work. Collect baseline and follow-up measures and account for task mix [T1-T4]. Self-check: causal claims stay within the studies' randomized comparisons.

### EVALUATION: TEST 5

Baseline Words: 184 | Optimized Words: 262 | Overhead Ratio: 1.424x. Visible-token proxy: Baseline 387; Optimized 516; ratio 1.333x. Compiled prompt: 122 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both preserve opposite experimental findings and distinguish hybrid work. |
| Completeness | 4 | 4 | +0 | Both are selective and leave long-term innovation and broader occupational coverage unresolved. |
| Structure | 5 | 5 | +0 | B makes the differences between studies easier to compare in a compact table. |
| Actionability | 4 | 4 | +0 | Both propose measurable workplace evaluation, without a detailed experimental design. |
| Traceability | 4 | 5 | +1 | B binds each integrated conclusion to its study and scope limitation. |
| **TOTAL (/25)** | **22** | **23** | **+1** | **Winner: Candidate B** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The most useful addition is the evidence table and explicit refusal to pool unlike interventions. The underlying findings and recommendation remain similar. This small corpus cannot establish a universal policy.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 6: Business Decision

Mixed task; Mode 1; benchmark template 6, current domain template 5.

### RAW PROMPT

````text
We're a 15-person SaaS startup deciding between building our own authentication system or using Auth0/Clerk. We handle sensitive healthcare data (HIPAA). What should we do?
````

### BASELINE RESPONSE

Prefer managed authentication, provided the chosen service and contract cover your actual healthcare-data flows. A 15-person team would otherwise own credential security, recovery, MFA, sessions, incident response and ongoing maintenance.

Start by mapping whether the provider creates, receives, maintains or transmits ePHI on your behalf. HHS requires an appropriate BAA for that cloud-service relationship; buying authentication alone does not establish HIPAA compliance. [HHS guidance](https://www.hhs.gov/hipaa/for-professionals/faq/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html)

Clerk currently advertises a BAA on its Enterprise plan. Verify the signed terms and eligible features; get equivalent written scope confirmation from Auth0 before choosing. [Clerk security](https://clerk.com/security)

Compare total contract cost, required SSO/MFA, audit export, recovery, availability, deployment constraints and migration options. Keep clinical data out of identity metadata where feasible, use opaque subject IDs, and implement authorization and tenant isolation in your application. Test cross-tenant access, revocation and account recovery before production.

Build only if documented constraints rule out suitable providers and you can staff long-term identity security. Prefer established identity components even then. The immediate decision is to evaluate eligible managed services, not select a vendor on an unverified compliance badge.

### OPTIMIZED PROMPT

````text
The analytical protocol requires a Mode 1 certificate. Use no expert roleplay.
[O1] Original request and supplied evidence, verbatim:
We're a 15-person SaaS startup deciding between building our own authentication system or using Auth0/Clerk. We handle sensitive healthcare data (HIPAA). What should we do?
Use O1 constraints, O2 build/Auth0/Clerk options, O3 equal decision criteria. Keep the team size and HIPAA context. Compare scope of responsibility, contract eligibility, implementation, operating cost and exit path. When current plan or BAA terms are unverified, mark that option conditional. Include an executable procurement/technical verification checklist.
When evidence is absent, name the missing input and qualify the affected finding. Include counterevidence. Finish with a conclusion citing T identifiers, concrete next actions, and a self-check that every conclusion has support. Preserve all substantive facts; derive the answer from evidence.
````

Method rationale: Evidence certificates follow (Ugare & Chandra, 2026); goal-blind framing follows (Cao, Jiang & Xu, 2026); positive evidence predicates follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

#### PREMISES

[O1] Fifteen-person SaaS team; sensitive healthcare data and HIPAA context. [O2] Options: custom authentication, Auth0, Clerk. [O3] Compare compliance fit, operating burden, required features, cost and portability; budget and data flows are unspecified.

#### OPTION TRACES

| Trace / option | Evidence and consequence |
| --- | --- |
| [T1] Build | Gives implementation control but leaves credential lifecycle, recovery, abuse defense, availability and incident ownership with this team. Staffing and costs are UNMEASURED. |
| [T2] Auth0 | Managed option; exact BAA, covered products, plan, deployment and price remain UNVERIFIED in this review. Require written confirmation before selection. |
| [T3] Clerk | [Published security page](https://clerk.com/security) offers a BAA on Enterprise. Actual agreement, data flow and enabled services still require review. |
| [T4] Shared boundary | A cloud provider handling ePHI on the customer's behalf needs the appropriate BAA; the customer retains its own compliance duties. [HHS](https://www.hhs.gov/hipaa/for-professionals/faq/may-a-hipaa-covered-entity-or-business-associate-use-cloud-service-to-store-or-process-ephi/index.html) |

#### FORMAL CONCLUSION

Prefer an eligible managed service, conditional on verified contract and architecture fit [T1-T4]. The evidence does not establish whether Auth0 or Clerk wins [T2-T3]. Custom development is a fallback when a documented requirement cannot be met and sustained security staffing is available [T1].

#### REMEDIATION / NEXT ACTION

1. Inventory identity attributes, logs and ePHI flows; determine business-associate scope [T4].
2. Obtain both vendors' applicable BAA, covered-feature list, pricing, audit evidence and exit/export terms [T2-T3].
3. Prototype required SSO/MFA, recovery and revocation with synthetic data [T2-T3].
4. Test application authorization, tenant isolation and audit export; assign owners for outages and incidents [T1,T4].

Self-check: vendor selection remains conditional where evidence is missing.

### EVALUATION: TEST 6

Baseline Words: 177 | Optimized Words: 268 | Overhead Ratio: 1.514x. Visible-token proxy: Baseline 377; Optimized 511; ratio 1.355x. Compiled prompt: 133 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Neither treats vendor marketing or a BAA as complete HIPAA compliance. |
| Completeness | 4 | 5 | +1 | B separates each option and gives explicit unknowns and acceptance work. |
| Structure | 5 | 4 | -1 | A is more concise; B adds structure but repeats its conditional recommendation. |
| Actionability | 5 | 5 | +0 | Both provide practical procurement and integration checks. |
| Traceability | 4 | 5 | +1 | B connects the choice and retained responsibilities to evidence and gaps. |
| **TOTAL (/25)** | **23** | **24** | **+1** | **Winner: Candidate B** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The optimization improves the decision audit by separating vendor eligibility from application obligations. It does not identify a justified vendor winner or measured cost advantage. The comparison still depends on commercial and architectural evidence.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 7: Compliance Check

Accuracy task; Mode 1; benchmark template 7, current domain template 4.

### RAW PROMPT

````text
Review this password policy for NIST 800-63B compliance:
- Minimum 8 characters
- Must include uppercase, lowercase, number, and special character
- Passwords expire every 90 days
- Cannot reuse last 5 passwords
- Account locks after 3 failed attempts for 30 minutes
````

### BASELINE RESPONSE

Using the current NIST SP 800-63B-4, this policy needs changes:

| Item | Assessment |
| --- | --- |
| Eight-character minimum | Insufficient for single-factor passwords; may meet the MFA minimum. |
| Required character classes | Conflicts with the composition-rule prohibition. |
| Ninety-day expiry | Conflicts with the prohibition on routine periodic changes. |
| Last-five reuse restriction | Not a stated NIST requirement; not automatically a violation. |
| Three failures / 30-minute lock | Not automatically prohibited, but this sentence does not establish complete retry-limit and recovery behavior. |

Use 15 characters for single-factor passwords or at least eight within MFA; remove composition and scheduled-expiry requirements. Require change on compromise. Verify blocklist screening, support for long passwords, storage, recovery and rate-limiting implementation before claiming compliance. [NIST password and rate-limiting requirements](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver)

This is a policy-text assessment, not an implementation certification. If a contract requires an older revision, record that explicitly before auditing.

### OPTIMIZED PROMPT

````text
The analytical protocol requires a Mode 1 certificate. Use no expert roleplay.
[R1] Original request and supplied evidence, verbatim:
Review this password policy for NIST 800-63B compliance:
- Minimum 8 characters
- Must include uppercase, lowercase, number, and special character
- Passwords expire every 90 days
- Cannot reuse last 5 passwords
- Account locks after 3 failed attempts for 30 minutes
Use R1 the exact policy and R2 the applicable NIST revision/clauses. Pin the revision and distinguish single-factor from MFA. For each supplied item give disposition, clause and corrective action. Policy text alone supports only policy-level findings; when implementation is absent mark it UNABLE TO VERIFY.
When evidence is absent, name the missing input and qualify the affected finding. Include counterevidence. Finish with a conclusion citing T identifiers, concrete next actions, and a self-check that every conclusion has support. Preserve all substantive facts; derive the answer from evidence.
````

Method rationale: Evidence certificates follow (Ugare & Chandra, 2026); goal-blind framing follows (Cao, Jiang & Xu, 2026); positive evidence predicates follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

#### PREMISES

[R1] Five supplied policy clauses. [R2] Current [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html), sections 3.1.1.2 and 3.2.2. MFA context and implementation evidence are absent.

#### COMPLIANCE TRACES

| Trace | Policy disposition | Correction / evidence |
| --- | --- | --- |
| [T1] Length | Conditional | 15 for single-factor; eight is permissible within MFA. |
| [T2] Composition | Noncompliant | Remove required character mixtures. |
| [T3] Expiry | Noncompliant | Replace scheduled expiry with compromise-triggered change. |
| [T4] History | Extra local control | Last-five history is not required; it is not inherently forbidden. |
| [T5] Lockout | Unable to verify | Three attempts is not automatically invalid; inspect cumulative failure handling and recovery. |

[T6] Blocklist, maximum supported length, secure storage and other authenticator controls are not evidenced in this short policy.

#### FORMAL CONCLUSION

The text conflicts with the selected revision [T2-T3], has a context-dependent minimum [T1], and cannot establish implementation compliance [T5-T6].

#### REMEDIATION / NEXT ACTION

Apply T1-T3 edits; obtain configuration and tests for T5-T6, including behavior after repeated lockout windows. Document the rationale for T4. Self-check: conclusions reference policy evidence or explicitly missing implementation evidence.

### EVALUATION: TEST 7

Baseline Words: 157 | Optimized Words: 197 | Overhead Ratio: 1.255x. Visible-token proxy: Baseline 292; Optimized 346; ratio 1.185x. Compiled prompt: 149 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both use the current revision and avoid treating a stricter lockout as inherently noncompliant. |
| Completeness | 4 | 4 | +0 | Both correctly limit the audit to the supplied text. |
| Structure | 5 | 5 | +0 | Both use concise clause-level tables. |
| Actionability | 4 | 5 | +1 | B specifically asks to test repeated lockout windows, a concrete verification gap. |
| Traceability | 4 | 5 | +1 | B adds clause references and explicit disposition-to-action mapping. |
| **TOTAL (/25)** | **22** | **24** | **+2** | **Winner: Candidate B** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The certificate makes policy findings easier to turn into an audit checklist. It does not establish implementation compliance, and both versions correctly preserve that limitation. Revision selection is more consequential than the trace labels.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 8: Document Analysis

Mixed task; Mode 1; benchmark template 8, current domain template 2.

### RAW PROMPT

````text
Here is an executive summary from a project proposal: "Our AI-powered customer service solution will reduce support tickets by 60% within 6 months of deployment. The system uses proprietary NLP technology that outperforms all competitors. Implementation requires minimal IT involvement and the ROI will exceed 300% in the first year." Analyze the credibility of these claims.
````

### BASELINE RESPONSE

The summary contains testable promises but supplies no evidence that they will be achieved. Unsupported does not mean false.

- The 60% ticket reduction needs a baseline, ticket definition, eligible population and evaluation design. Reduced contacts could reflect successful self-service or customers abandoning support; track resolution, repeat contacts and satisfaction.
- “Outperforms all competitors” needs named comparators, dates, representative tasks and equivalent testing conditions. Proprietary technology is not itself evidence of superiority.
- “Minimal IT involvement” needs an integration and security work breakdown with estimated internal hours, dependencies and ownership.
- ROI above 300% needs a transparent model. With ROI defined as `(benefits - costs) / costs`, 300% means benefits equal four times costs, not three. Include implementation, licenses, maintenance, human escalation and risk costs.

Request the pilot results, comparison protocol, implementation estimate and cash-flow assumptions. Replace guaranteed language with measurable targets pending validation. A controlled pilot should evaluate support quality alongside ticket volume; this paragraph alone cannot establish credibility beyond the fact that the claims are specific enough to investigate.

### OPTIMIZED PROMPT

````text
The analytical protocol requires a Mode 1 certificate. Use no expert roleplay.
[C1] Original request and supplied evidence, verbatim:
Here is an executive summary from a project proposal: "Our AI-powered customer service solution will reduce support tickets by 60% within 6 months of deployment. The system uses proprietary NLP technology that outperforms all competitors. Implementation requires minimal IT involvement and the ROI will exceed 300% in the first year." Analyze the credibility of these claims.
Use C1 quoted text, C2 exact claims, C3 supporting evidence and gaps. Trace each claim to its wording and specify falsifiable verification evidence. Preserve the distinction between unsupported and disproven. Include an explicitly conditional replacement summary; calculate the meaning of ROI instead of silently choosing a definition.
When evidence is absent, name the missing input and qualify the affected finding. Include counterevidence. Finish with a conclusion citing T identifiers, concrete next actions, and a self-check that every conclusion has support. Preserve all substantive facts; derive the answer from evidence.
````

Method rationale: Evidence certificates follow (Ugare & Chandra, 2026); goal-blind framing follows (Cao, Jiang & Xu, 2026); positive evidence predicates follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

#### PREMISES

[C1] The supplied paragraph contains four claims. [C2] Scope: magnitude, comparative superiority, implementation burden and ROI. [C3] No pilot, benchmark, work plan or cost model accompanies it.

#### CLAIM TRACES

| Trace | Claim | Evidence needed |
| --- | --- | --- |
| [T1] | 60% fewer tickets in six months | Baseline and eligible-ticket denominator, comparison group, repeat-contact and resolution measures |
| [T2] | Better than all competitors | Defined comparison set, versions, representative dataset, blinded quality measurement and costs |
| [T3] | Minimal IT involvement | Integration, security, migration and operating work breakdown with internal hours |
| [T4] | ROI exceeds 300% in year one | Benefits and all costs with timing and sensitivity analysis |

[T5] If ROI = (benefits - costs)/costs, ROI > 300% implies benefits > 4 × costs. That definition is not supplied. Reduced tickets are not automatically equivalent to better service or realized savings [T1].

#### FORMAL CONCLUSION

All four promises are unsupported by the supplied paragraph, not demonstrated false [T1-T4]. Proprietary technology establishes no comparative performance result [T2]. The financial claim lacks a defined calculation and assumptions [T4-T5].

#### REMEDIATION / NEXT ACTION

Proposed replacement: “The project proposes AI-assisted customer support. A pilot will test a target of 60% fewer eligible tickets over six months while measuring resolution and repeat contacts. Comparative performance, IT effort and first-year ROI remain subject to documented evaluation.” This preserves the target as a hypothesis and removes unsupported guarantees [T1-T5].

Self-check: every credibility judgment points to an absent artifact or explicit calculation.

### EVALUATION: TEST 8

Baseline Words: 171 | Optimized Words: 263 | Overhead Ratio: 1.538x. Visible-token proxy: Baseline 323; Optimized 443; ratio 1.372x. Compiled prompt: 164 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both avoid treating unverified claims as false and calculate the ROI threshold correctly. |
| Completeness | 4 | 5 | +1 | B covers the claims and adds revised usable wording. |
| Structure | 5 | 5 | +0 | The compact evidence matrix fits the task. |
| Actionability | 4 | 5 | +1 | B supplies a copy-pasteable replacement in addition to a request list. |
| Traceability | 4 | 5 | +1 | Each B judgment has a specific claim/evidence link; A has substantial but less explicit support. |
| **TOTAL (/25)** | **22** | **25** | **+3** | **Winner: Candidate B** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The clearest gain is the concrete replacement summary. The baseline already identifies the substantive credibility problems, while the optimized answer turns them into a more usable deliverable. The redraft appropriately labels the numerical target as unvalidated.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 9: Comparative Analysis

Mixed task; Mode 2; benchmark template 9, current domain template 6.

### RAW PROMPT

````text
Compare PostgreSQL and MongoDB for a new application that needs to handle both structured transaction data and semi-structured user activity logs. We expect 10M records per month growing 20% annually.
````

### BASELINE RESPONSE

Start with PostgreSQL unless measured log workloads justify another store. Relational transactions fit its constraints and joins, while JSONB supports semi-structured activity payloads and indexing. [PostgreSQL JSON documentation](https://www.postgresql.org/docs/current/datatype-json.html)

MongoDB suits document-oriented access patterns and supports multi-document transactions; it is not inherently incapable of transactional work. Distributed transactions add costs and make schema design consequential. [MongoDB transactions](https://www.mongodb.com/docs/manual/core/transactions/)

Ten million records per 30-day month averages about 3.86 writes/second. The current annualized rate is 120M records; after one 20% annual growth step it is 144M/year. These are rates, not retained-storage estimates. Record size, indexes, retention and peak bursts matter much more than the average alone.

For PostgreSQL, keep core transaction fields relational and log payloads in JSONB; consider time-based partitioning if retention and query measurements justify it. Benchmark representative peaks, concurrent queries, ingestion latency and recovery. Choose MongoDB if document-first access and operational needs show a measured advantage. Using both immediately adds operational and consistency costs without evidence that the workload requires it.

### OPTIMIZED PROMPT

````text
The analytical protocol requires a Mode 2 certificate. Use no expert roleplay.
[D1] Original request and supplied evidence, verbatim:
Compare PostgreSQL and MongoDB for a new application that needs to handle both structured transaction data and semi-structured user activity logs. We expect 10M records per month growing 20% annually.
Use Mode 2 LITE: at most three premises D1-D3, a compact comparison matrix with single-line causal traces, a two-sentence conditional recommendation and concrete benchmark action. Keep the response under 230 words. Treat volume as a rate, state any month-length assumption, and mark unmeasured latency or scale claims as such.
When evidence is absent, name the missing input and qualify the affected finding. Include counterevidence. Finish with a conclusion citing T identifiers, concrete next actions, and a self-check that every conclusion has support. Preserve all substantive facts; derive the answer from evidence.
````

Method rationale: Compact premises follow (Zhang, Hu et al., 2026); limited certificate overhead follows (Ugare & Chandra, 2026); observable evidence predicates follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

[LITE] [D1] Structured transactions plus semi-structured logs. [D2] 10M records/month, 20% annual growth. [D3] Peaks, record sizes, retention, query patterns and deployment budget are unknown.

| Trace / dimension | PostgreSQL | MongoDB |
| --- | --- | --- |
| [T1] Transaction model | Relational constraints and joins | Multi-document transactions supported; document modeling remains important |
| [T2] Logs | Indexed JSONB alongside relational fields | Native document model |
| [T3] Operational choice | One database can cover both stated needs | Select when measured document workloads favor it |

Sources: [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html), [MongoDB transactions](https://www.mongodb.com/docs/manual/core/transactions/).

[T4] 10M/(30 × 86,400) = 3.86 average records/second. Current annualized volume is 120M; the next annual growth step gives 144M. Peaks and stored bytes are UNMEASURED.

Recommendation: start by benchmarking PostgreSQL for both workloads [T1-T3]. Reconsider MongoDB or a separate log store when representative measurements show a material benefit [T3-T4].

Next action: benchmark peak ingestion plus transaction/query concurrency using realistic payloads, indexes and retention; record p95 latency, storage, recovery time and operating cost. Self-check: this is a workload-conditional choice, not a capacity guarantee [T1-T4].

### EVALUATION: TEST 9

Baseline Words: 160 | Optimized Words: 183 | Overhead Ratio: 1.144x. Visible-token proxy: Baseline 336; Optimized 350; ratio 1.042x. Compiled prompt: 140 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both avoid the false SQL-versus-no-transactions dichotomy and compute average ingestion correctly. |
| Completeness | 4 | 4 | +0 | Both identify missing peaks, sizes and retention; neither supplies measured results. |
| Structure | 5 | 5 | +0 | B remains compact and comparable to the direct baseline. |
| Actionability | 5 | 5 | +0 | Both name a conditional starting point and measurable benchmark dimensions. |
| Traceability | 4 | 5 | +1 | B explicitly ties the recommendation to capability evidence and unmeasured scale. |
| **TOTAL (/25)** | **23** | **24** | **+1** | **Winner: Candidate B** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

Lite retains the baseline recommendation and numerical caution without a large certificate. Its trace links add modest audit value. The measured word ratio below determines whether the overhead target was met.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 10: Creative Brief

Creative task; Mode 4; benchmark template 10, current domain template 10.

### RAW PROMPT

````text
Write a product description for a new ergonomic office chair designed for people who work 10+ hour days. The chair has lumbar support that auto-adjusts, breathable mesh, and a 12-year warranty. Target audience is remote tech workers ages 25-45.
````

### BASELINE RESPONSE

Your last meeting should not require a different chair.

Built for remote tech workers whose days stretch past ten hours, this ergonomic office chair brings auto-adjusting lumbar support and breathable mesh to the desk. The lumbar support adjusts automatically, while the mesh lets air move through the chair during long stretches of focused work.

A 12-year warranty gives you a clear support horizon beyond the next project, the next role or the next home-office setup.

Make room for a chair designed around the hours you actually work. Review the fit and warranty terms before you choose.

### OPTIMIZED PROMPT

````text
You are a product copywriter. The editorial craft protocol requires a brief backstage scaffold and then clean final copy.
[P1] Original brief, verbatim:
Write a product description for a new ergonomic office chair designed for people who work 10+ hour days. The chair has lumbar support that auto-adjusts, breathable mesh, and a 12-year warranty. Target audience is remote tech workers ages 25-45.
[P2] Use only the supplied product features; when a benefit would imply medical efficacy, tested productivity or unspecified warranty coverage, keep the wording at the observable feature level.
[P3] Address the stated audience with grounded workday detail.
[NT0] Generate exactly three distinct tonal candidates, each with a heuristic typicality estimate below 0.15; label these as subjective estimates, select one and execute it. [NT1] Identify a concrete opening; [NT2] map the progression; [NT3] specify cadence.
[SC0] Open within a specific moment before the product thesis, develop through concrete features, use grounded practitioner language with varied paragraph lengths, and end with a concrete action. Present the final product description separately.
````

Method rationale: Candidate variation follows (Zhang et al., 2025); structural recipes follow (Madler, 2026); observable product-fact guards follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

#### BACKSTAGE

[NT0] Subjective, uncalibrated typicality estimates:

1. Quiet deployment diary, p = 0.10: a workday marker leads into the chair's features.
2. Dry desk-side field note, p = 0.12: a brief inventory of what stays at the desk after the work changes.
3. Warranty time capsule, p = 0.08: the chair's warranty spans successive home-office setups.

Select candidate 1 for its direct connection to long technical workdays. These are independent heuristic typicalities, not an exhaustive probability distribution.

[NT1] Opening: the deployment progress bar. [NT2] Move from waiting at the desk to lumbar support, mesh and warranty. [NT3] Short opening, longer feature paragraph, concrete closing action. [SC0] Specific scene, feature-based progression, practitioner detail, practical ending.

#### FINAL PRODUCT DESCRIPTION

The deployment is at 97%.

You have been at this desk since the first stand-up. This ergonomic office chair is designed for remote tech workers whose workdays run past ten hours, with auto-adjusting lumbar support and breathable mesh. The support adjusts automatically; the mesh allows airflow through the chair.

A 12-year warranty reaches well beyond this release cycle.

Before adding it to your setup, check the fit at your desk and read the warranty terms.

### EVALUATION: TEST 10

Baseline Words: 96 | Optimized Words: 194 | Overhead Ratio: 2.021x. Visible-token proxy: Baseline 148; Optimized 324; ratio 2.189x. Compiled prompt: 170 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both stay within the supplied features without medical or guaranteed productivity claims. |
| Completeness | 5 | 5 | +0 | Both include audience, long days, lumbar support, mesh and warranty. |
| Structure | 4 | 4 | +0 | B has a more concrete opening, but its full delivered response includes a substantial scaffold. |
| Actionability | 5 | 5 | +0 | Both yield usable copy and a practical fit/warranty action. |
| Traceability | 4 | 4 | +0 | Both ground benefits in supplied features; B typicalities are explicitly uncalibrated, not evidence. |
| **TOTAL (/25)** | **23** | **23** | **+0** | **Winner: Tie** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The optimized final copy has a more specific technical-work opening, but originality cannot be quantified from one sample. Its scaffold increases delivered length substantially. The rubric total ties because factual coverage and usability were already strong.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 11: Context File (CLAUDE.md)

Harness task; Mode 3; benchmark template 11, current domain template 11.

### RAW PROMPT

````text
Write a CLAUDE.md file for our Python FastAPI + PostgreSQL repository. Explain the project overview, list the folder structure (app/api, app/models, app/services, tests/), explain standard PEP8 coding conventions, and include our non-obvious commands: running unit tests requires `pytest -m "not integration" --reuse-db`, database migrations must run via `./scripts/migrate.sh check` before committing, and Redis cache keys in `app/services/billing.py` must never be mutated without bumping `SCHEMA_EPOCH`.
````

### BASELINE RESPONSE

```markdown
# Repository Guide

## Overview
Python FastAPI application backed by PostgreSQL.

## Layout
- `app/api`: API layer.
- `app/models`: model definitions.
- `app/services`: service logic.
- `tests/`: automated tests.

## Python conventions
Follow PEP8: four-space indentation, snake_case functions and variables, CapWords classes, and organized imports. Match established project formatting.

## Required commands
- Unit tests: `pytest -m "not integration" --reuse-db`
- Before committing, check migrations: `./scripts/migrate.sh check`

## Billing cache invariant
When changing Redis cache keys in `app/services/billing.py`, bump `SCHEMA_EPOCH` in the same change.

## Verification
Run the unit-test command and migration check. Report results and any failures; successful execution must be observed before claiming checks pass.
```

### OPTIMIZED PROMPT

````text
Produce only a CLAUDE.md artifact under 150 lines using the minimal context protocol.
Supplied request, verbatim:
Write a CLAUDE.md file for our Python FastAPI + PostgreSQL repository. Explain the project overview, list the folder structure (app/api, app/models, app/services, tests/), explain standard PEP8 coding conventions, and include our non-obvious commands: running unit tests requires `pytest -m "not integration" --reuse-db`, database migrations must run via `./scripts/migrate.sh check` before committing, and Redis cache keys in `app/services/billing.py` must never be mutated without bumping `SCHEMA_EPOCH`.
Keep only the exact non-inferable commands, the billing cache/SCHEMA_EPOCH invariant and a verification gate. The output sections are Commands, Hard invariant, and Verification. When a command fails or cannot run, require a precise blocked/failure report. Use no invented setup or lint commands. Repository overview, directory inventory and standard PEP8 exposition are replaced by this operational contract.
````

Method rationale: Minimal persistent context follows (Gloaguen et al., 2026); verification gates follow (Lee et al., 2026); conditional failure reporting follows (Yin et al., 2026).

### OPTIMIZED RESPONSE

```markdown
# Agent Operating Contract

## Commands
- Unit tests: `pytest -m "not integration" --reuse-db`
- Required before committing: `./scripts/migrate.sh check`

## Hard invariant
When changing Redis cache keys in `app/services/billing.py`, bump `SCHEMA_EPOCH` in the same change.

## Verification
Run both commands above before declaring the change verified. Report each exit code and a concise output summary.
When a check fails or cannot execute, report the command and exact failure or missing prerequisite, and state which verification remains incomplete.
```

### EVALUATION: TEST 11

Baseline Words: 109 | Optimized Words: 80 | Overhead Ratio: 0.734x. Visible-token proxy: Baseline 211; Optimized 143; ratio 0.678x. Compiled prompt: 136 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 5 | 5 | +0 | Both preserve commands and the schema-epoch condition exactly. |
| Completeness | 5 | 3 | -2 | B intentionally omits the overview, folder list and PEP8 text explicitly requested in the raw prompt. |
| Structure | 4 | 5 | +1 | B is shorter and focused on non-inferable operational information. |
| Actionability | 5 | 5 | +0 | Both provide executable commands and the required invariant. |
| Traceability | 4 | 5 | +1 | B explicitly requires exit codes and a precise failure record. |
| **TOTAL (/25)** | **23** | **23** | **+0** | **Winner: Tie** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The optimized artifact is materially more compact, but this comes partly from changing the task scope. Against the original request, the missing overview, tree and style section must lower completeness. No repository-task-success experiment was run, so reduced context size is not evidence of improved agent performance.

Provenance: In-session generation and unblinded self-evaluation.
## TEST 12: Async Rate Limiter

Harness task; Mode 3; benchmark template 12, current domain template 12.

### RAW PROMPT

````text
Write a thread-safe async token bucket rate limiter in Python (`AsyncTokenBucket`) that supports burst capacity, fractional refill rates, and `acquire(tokens: int, timeout: float | None = None) -> bool`. Make sure there are no race conditions when multiple coroutines wait concurrently.
````

### BASELINE RESPONSE

Use a `threading.Lock` for the short shared-state update, and release it before every `await`. This allows one bucket to be shared by coroutines on different event loops and OS threads.

The bucket starts full. A positive integer request above capacity raises `ValueError`; `timeout=0` makes one immediate attempt. Positive timeouts bound subsequent attempts using a monotonic clock. Cancellation during a wait consumes no tokens; completed acquisitions are not refunded. Fairness is not guaranteed, so repeated small requests may starve larger ones.

```python
import asyncio
import math
import threading
import time


class AsyncTokenBucket:
    """Thread-safe shared bucket; full initially; no FIFO fairness guarantee."""

    def __init__(self, capacity: int, refill_rate: float):
        if type(capacity) is not int or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if isinstance(refill_rate, bool) or not isinstance(refill_rate, (int, float)):
            raise TypeError("refill_rate must be numeric")
        rate = float(refill_rate)
        if not math.isfinite(rate) or rate <= 0:
            raise ValueError("refill_rate must be finite and positive")
        self._capacity = float(capacity)
        self._rate = rate
        self._tokens = float(capacity)
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    async def acquire(self, tokens: int, timeout: float | None = None) -> bool:
        if type(tokens) is not int or not 0 < tokens <= self._capacity:
            raise ValueError("tokens must be a positive integer <= capacity")
        if timeout is not None:
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
                raise TypeError("timeout must be numeric or None")
            timeout = float(timeout)
            if not math.isfinite(timeout) or timeout < 0:
                raise ValueError("timeout must be finite and nonnegative")
        deadline = None if timeout is None else time.monotonic() + timeout
        first = True
        while True:
            with self._lock:
                now = time.monotonic()
                if not first and deadline is not None and now >= deadline:
                    return False
                self._tokens = min(
                    self._capacity,
                    self._tokens + (now - self._updated) * self._rate,
                )
                self._updated = now
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                delay = (tokens - self._tokens) / self._rate
            first = False
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                delay = min(delay, remaining)
            await asyncio.sleep(delay)

```

Example:

```python
async def example():
    bucket = AsyncTokenBucket(capacity=5, refill_rate=0.5)
    assert await bucket.acquire(5, timeout=0)
    assert not await bucket.acquire(1, timeout=0)

asyncio.run(example())
```

Refill, availability checking and deduction happen in one locked section, so simultaneous waiters cannot spend the same tokens. Each awakened waiter recomputes current availability. The lock is not held while sleeping; many waiters may still cause repeated wakeups. This is process-local coordination, not a distributed limiter.

### OPTIMIZED PROMPT

````text
The verification protocol requires compact premises, a complete implementation first and post-code V1-V3 gates. Keep non-code commentary below 25% of the response.
[P1] Original task, verbatim:
Write a thread-safe async token bucket rate limiter in Python (`AsyncTokenBucket`) that supports burst capacity, fractional refill rates, and `acquire(tokens: int, timeout: float | None = None) -> bool`. Make sure there are no race conditions when multiple coroutines wait concurrently.
[P2] Define capacity/refill units, initial state, timeout-zero behavior, invalid inputs, cancellation and cross-thread/event-loop scope. Protect refill/check/debit atomically and keep suspension outside the critical section.
Output complete executable Python, then [V1] preconditions and invariants mapped to mechanisms, [V2] a runnable harness covering fractional refill, burst, simultaneous callers, timeout, cancellation and separate threads/event loops, and [V3] postconditions, execution status and remaining limits. When tests have not executed, label them unrun. Use observable tests and invariants rather than narrating hidden reasoning; claim only the tested scope.
````

Method rationale: Code-first verification gates follow (Lee et al., 2026; Zhang et al., 2026); persona omission follows (Hu, Rostami & Thomason, 2026); observable pass/fail recipes follow (Yin et al., 2026).

### OPTIMIZED RESPONSE

[P1] `AsyncTokenBucket.acquire(tokens: int, timeout: float | None = None) -> bool`. [P2] Full initially, positive capacity/rate, monotonic refill, one atomic debit, cooperative waiting, shared across threads/event loops; no FIFO guarantee.

#### COMPLETE IMPLEMENTATION

```python
import asyncio
import math
import threading
import time


class AsyncTokenBucket:
    """Thread-safe shared bucket; full initially; no FIFO fairness guarantee."""

    def __init__(self, capacity: int, refill_rate: float):
        if type(capacity) is not int or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if isinstance(refill_rate, bool) or not isinstance(refill_rate, (int, float)):
            raise TypeError("refill_rate must be numeric")
        rate = float(refill_rate)
        if not math.isfinite(rate) or rate <= 0:
            raise ValueError("refill_rate must be finite and positive")
        self._capacity = float(capacity)
        self._rate = rate
        self._tokens = float(capacity)
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    async def acquire(self, tokens: int, timeout: float | None = None) -> bool:
        if type(tokens) is not int or not 0 < tokens <= self._capacity:
            raise ValueError("tokens must be a positive integer <= capacity")
        if timeout is not None:
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
                raise TypeError("timeout must be numeric or None")
            timeout = float(timeout)
            if not math.isfinite(timeout) or timeout < 0:
                raise ValueError("timeout must be finite and nonnegative")
        deadline = None if timeout is None else time.monotonic() + timeout
        first = True
        while True:
            with self._lock:
                now = time.monotonic()
                if not first and deadline is not None and now >= deadline:
                    return False
                self._tokens = min(
                    self._capacity,
                    self._tokens + (now - self._updated) * self._rate,
                )
                self._updated = now
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                delay = (tokens - self._tokens) / self._rate
            first = False
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                delay = min(delay, remaining)
            await asyncio.sleep(delay)

```

[V1] Preconditions: positive integer capacity; finite positive numeric refill rate; positive integer requests within capacity; finite nonnegative timeout or None. `threading.Lock` encloses refill/check/debit. The sole `await` is outside that lock. `timeout=0` performs one availability check; later checks respect the deadline. Cancellation while waiting makes no reservation; completed acquisitions are not refunded.

[V2] Append this executable harness to the implementation:

```python
async def self_test():
    from concurrent.futures import ThreadPoolExecutor
    from unittest.mock import patch

    class Clock:
        value = 0.0

        @classmethod
        def monotonic(cls):
            return cls.value

    # Fractional refill, saturation and burst with a controlled clock.
    with patch(__name__ + ".time", Clock):
        b = AsyncTokenBucket(2, 0.5)
        assert await b.acquire(2, 0)
        Clock.value = 1.0
        assert not await b.acquire(1, 0)
        Clock.value = 2.0
        assert await b.acquire(1, 0)
        Clock.value = 100.0
        assert await b.acquire(2, 0)
        assert not await b.acquire(1, 0)

    b = AsyncTokenBucket(5, 1e-12)
    results = await asyncio.gather(*(b.acquire(1, 0) for _ in range(50)))
    assert sum(results) == 5
    assert not await b.acquire(1, 0.002)
    waiter = asyncio.create_task(b.acquire(1))
    await asyncio.sleep(0)
    waiter.cancel()
    try:
        await waiter
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("cancellation did not propagate")

    for tokens, timeout in [(0, None), (6, None), (True, None), (1, -1)]:
        try:
            await b.acquire(tokens, timeout)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError("invalid request accepted")

    # Separate event loops on several threads share the same state.
    shared = AsyncTokenBucket(5, 1e-12)
    def worker(_):
        return asyncio.run(shared.acquire(1, 0))
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(worker, range(40))) == 5
    print("SELF-TEST PASS: refill, burst, contention, timeout, cancellation, validation, cross-thread loops")


if __name__ == "__main__":
    asyncio.run(self_test())

```

[V3] Proposed tests are not execution evidence until run. Successful grants debit once; timeout and waiting cancellation debit nothing. Fairness and distributed coordination are outside scope. Binary floating-point capacity/accounting limits very large capacities and numerical exactness; this code does not provide arbitrary-precision token arithmetic. Every stated gate maps to code or a test, with these limits retained.

### EVALUATION: TEST 12

Baseline Words: 396 | Optimized Words: 581 | Overhead Ratio: 1.467x. Visible-token proxy: Baseline 869; Optimized 1339; ratio 1.541x. Compiled prompt: 150 words, excluded from response overhead.

| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta | Evidence / Justification |
| :--- | :---: | :---: | :---: | :--- |
| Accuracy | 4 | 4 | +0 | Both use the same correct short locked state transition for ordinary capacities; floating-point representation limits very large integer capacity. |
| Completeness | 4 | 5 | +1 | B adds explicit gates and exercises timeout, cancellation, fractional refill and separate thread event loops. |
| Structure | 5 | 5 | +0 | Code remains first and commentary is compact relative to the executable artifact. |
| Actionability | 4 | 5 | +1 | B provides a full executable harness; A gives only a small example. |
| Traceability | 4 | 5 | +1 | B links concurrency claims to lock scope plus runnable cross-thread and contention checks. |
| **TOTAL (/25)** | **21** | **24** | **+3** | **Winner: Candidate B** |

Mapping: A = Baseline; B = Optimized. Position-swap consistency: not measured.

The implementation mechanism is unchanged; the gain is executable verification and explicit boundaries. Passing finite tests supports the exercised paths, not a mathematical proof of race freedom. Very large capacity and fairness limits remain visible rather than being certified away.

Provenance: In-session generation and unblinded self-evaluation.

## Final Synthesis

### Summary Table

| Test | Domain | Task Type | Mode | Baseline /25 | Optimized /25 | Delta | Words (B/O/Ratio) | Winner |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | Code Review | Accuracy | 1 | 23 | 23 | +0 | 71/440/6.197x | Tie |
| 2 | Financial Analysis | Accuracy | 1 | 25 | 24 | -1 | 248/345/1.391x | Baseline |
| 3 | Medical Reasoning | Accuracy | 1 | 23 | 24 | +1 | 180/320/1.778x | Optimized |
| 4 | Legal Analysis | Accuracy | 1 | 23 | 23 | +0 | 244/255/1.045x | Tie |
| 5 | Research Synthesis | Mixed | 1 | 22 | 23 | +1 | 184/262/1.424x | Optimized |
| 6 | Business Decision | Mixed | 1 | 23 | 24 | +1 | 177/268/1.514x | Optimized |
| 7 | Compliance Check | Accuracy | 1 | 22 | 24 | +2 | 157/197/1.255x | Optimized |
| 8 | Document Analysis | Mixed | 1 | 22 | 25 | +3 | 171/263/1.538x | Optimized |
| 9 | Comparative Analysis | Mixed | 2 | 23 | 24 | +1 | 160/183/1.144x | Optimized |
| 10 | Creative Brief | Creative | 4 | 23 | 23 | +0 | 96/194/2.021x | Tie |
| 11 | Context File (CLAUDE.md) | Harness | 3 | 23 | 23 | +0 | 109/80/0.734x | Tie |
| 12 | Async Rate Limiter | Harness | 3 | 21 | 24 | +3 | 396/581/1.467x | Optimized |
| | AVERAGE | | | 22.75 | 23.67 | +0.92 | 182.75/282.33/1.545x pooled | |

### 1. Overall Verdict

The self-scores rise from 22.75 to 23.67 out of 25: +0.92 points, or 4.03% relative to baseline, equivalent to 3.67 percentage points of the 25-point scale. There are seven improvements, four ties and one decline. The clearest gains concern inspectable evidence and concrete artifacts, rather than corrected factual errors. Strong baselines leave little headroom.

These are descriptive judgments about these outputs. The accelerated protocol, same-context generation, unblinded self-scoring, source sharing and lack of position-swapped judging prevent a controlled causal claim about the skill or requested model. The supplied files are v4.2.0, so this is also not an isolated evaluation of historical v4.0. A universal quality or cost-effectiveness claim is unsupported.

### 2. Where It Helped Most

Document analysis and concurrency verification each gain three points. Test 8 adds a usable replacement summary instead of only criticism. Test 12 adds a runnable test harness and explicit scope to an unchanged synchronization mechanism. Compliance gains two points through clause-to-action mapping and a concrete retry-limit verification request. These are improvements visible in the artifacts, not inferred from the presence of certificate headings.

### 3. Where It Helped Least (or Hurt)

Financial analysis loses one structure point because the baseline already contains the same calculations, caveats and diligence actions. Code review ties despite 6.20x response word overhead: the small bug did not need an exhaustive contract certificate. Legal analysis remains constrained by absent jurisdiction. Creative work ties on the rubric despite a more concrete opening. The context-file case trades requested content for compactness, so its overall total also ties.

### 4. v4.0 Mode Evaluation (Mode 1 Max vs. Mode 2 Lite vs. Mode 3 Harness vs. Mode 4 Creative v2)

| Mode | Cases | Mean baseline /25 | Mean optimized /25 | Mean delta |
| --- | ---: | ---: | ---: | ---: |
| 1 | 8 | 22.88 | 23.75 | +0.88 |
| 2 | 1 | 23.00 | 24.00 | +1.00 |
| 3 | 2 | 22.00 | 23.50 | +1.50 |
| 4 | 1 | 23.00 | 23.00 | +0.00 |

Lite passes its response overhead target: Test 9 is 1.144x, below 1.5x, with a one-point self-scored gain. This does not include prompt compilation cost.

Context mode emits 12 lines, below 150, with both exact commands and the epoch invariant preserved. It omits raw-request overview, tree and style content intentionally; the completeness penalty records that conflict. No repository agent was tested with either context file.

The concurrency harness passes executed checks for fractional refill, burst limits, contention, timeout, cancellation, invalid requests and separate thread event loops. The shared lock and atomic refill/check/debit explain why ordinary callers cannot spend the same available tokens. Tests are finite, not a proof over all interleavings. Both implementations have a reproduced large-capacity defect: capacity `2**53 + 1` rounds internally and a request for that original capacity raises `ValueError`. Optimized response word overhead is 1.467x; non-code commentary is 25.6%, satisfying the template's separate 25% commentary ceiling.

Creative mode includes three distinct candidates, heuristic typicalities below 0.15, NT1-NT3 and SC0. Those estimated values are not calibrated sampling probabilities or measurements of structural rarity. The final copy has a grounded deployment scene; the entire response grows 2.021x because the scaffold is delivered. One example cannot establish diversity improvement, reader preference or marketing performance.

### 5. Accuracy vs. Mixed vs. Creative vs. Harness

| Category | Cases | Baseline /25 | Optimized /25 | Delta |
| --- | ---: | ---: | ---: | ---: |
| Accuracy | 5 | 23.20 | 23.60 | +0.40 |
| Mixed | 4 | 22.50 | 24.00 | +1.50 |
| Creative | 1 | 23.00 | 23.00 | +0.00 |
| Harness | 2 | 22.00 | 23.50 | +1.50 |

Mixed tasks benefit most consistently from explicit evidence-to-deliverable mapping. Accuracy tasks already have strong substantive answers, so certificates mainly alter auditability and length. Expert roleplay was omitted for accuracy and harness tasks; the creative task uses a short copywriter persona. Because persona was not independently randomized or ablated, this run cannot determine whether PRISM calibration caused any score difference.

### 6. Traceability Specifically

Traceability rises from 49/60 to 59/60, or 4.08 to 4.92 per case. Ten cases gain a point; financial analysis and creative work do not. The largest practical distinction is evidence that can be inspected: numerical calculations, clause references, qualified source comparisons, explicit missing inputs and executable assertions. Trace labels alone cannot verify an unsupported premise. The score increase is particularly exposed to evaluator bias because the same model generated and judged the requested format.

### 7. Token Cost vs. Value

The following tokens are the explicitly defined UTF-8-byte proxies, not measured model tokens or billed usage. Counts include delivered scaffolding and code.

| Mode | Mean words B | Mean words O | Pooled word ratio | Mean token proxy B | Mean token proxy O |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 179.00 | 293.75 | 1.641x | 339.00 | 540.50 |
| 2 | 160.00 | 183.00 | 1.144x | 336.00 | 350.00 |
| 3 | 252.50 | 330.50 | 1.309x | 540.00 | 741.00 |
| 4 | 96.00 | 194.00 | 2.021x | 148.00 | 324.00 |

Across all cases, words rise from 2193 to 3388, a pooled ratio of 1.545x. The arithmetic mean of individual ratios is 1.792x; the difference is driven by the short code-review baseline. Mean visible-token proxies are 356.33 and 540.00.

Compiled prompts add 2582 words of input, separate from response overhead. Actual CLI records for the isolated baseline and compiler include system/tool context and reasoning, so they are not directly comparable to the visible-output proxies. The cancelled generation and excluded setup attempt also consumed unmeasured or separately recorded resources. End-to-end token cost, latency superiority and monetary ROI cannot be established from this accelerated run.

### 8. Failure Modes Observed

- Over-formatting on a small code review increases response length more than sixfold without a total-score gain.
- Premise/trace/conclusion repetition makes already-complete financial analysis less economical.
- Missing jurisdiction, vendor terms and implementation evidence remain missing after certificate compilation.
- Context-file pruning changes explicit requirements; it cannot be scored as an unqualified completeness improvement.
- Creative typicality numbers are self-estimates; no empirical rarity or diversity measurement supports them.
- Executable tests miss arbitrary-precision limits unless specifically exercised; both rate limiters reject a valid full-capacity request at `2**53 + 1`.
- Version drift changes template numbering and creative/harness requirements, weakening longitudinal comparability.
- The user-requested acceleration removed isolation and blinded reversal controls. Same-context contamination and self-preference remain substantial threats to validity.

### 9. Recommendations for Future Skill Improvement

1. Route simple code reviews to Lite or bypass unless concrete complexity warrants Max; set a visible response budget before expanding the certificate (Ugare & Chandra, 2026).
2. Attach each conclusion to evidence without repeating the same facts in three sections; retain identifiers for navigation (Zhang, Hu et al., 2026).
3. Preserve urgent action ordering in clinical prompts and use explicit missing-evidence conditions, so certificate presentation does not delay the practical priority (Yin et al., 2026).
4. Make context pruning an explicit task transformation with a recorded fidelity tradeoff; evaluate compactness separately from compliance with the original request (Gloaguen et al., 2026).
5. Report creative candidate estimates as uncalibrated heuristics and measure final-copy diversity separately from backstage length (Zhang et al., 2025; Madler, 2026).
6. Add precise numeric-range and cross-thread semantics to concurrency contracts; exercise adversarial boundaries alongside the normal self-test (Lee et al., 2026; Yin et al., 2026).
7. Pin a skill commit and align benchmark template IDs before future comparisons; preserve raw prompts, source snapshots and complete artifacts (Zhang, Hu et al., 2026).
8. Use separate generation and blinded judge contexts, reversed presentation orders, multiple samples and held-out criteria in the next controlled run; preserve goal-blind generation and distinguish schema adherence from correctness (Cao, Jiang & Xu, 2026; Ugare & Chandra, 2026).

#### Verification record

- Executed rate-limiter self-test, exit 0: `SELF-TEST PASS: refill, burst, contention, timeout, cancellation, validation, cross-thread loops`.
- Reproduced the large-capacity limitation with `2**53 + 1`; this is retained in Accuracy scores rather than silently fixed after scoring.
- Repository-required validation one-liner, exit 0: `VALIDATED OK`.
- Repository-required `./install.sh`, exit 0: `Done. Synced (copy) across 7 agent directory(s) (1 unconfigured agent roots skipped; pass --all to force all).`
- Additional direct checks validate report sections, scores, source frontmatter, skill line count, twelve domain templates and absence of em/en dashes. The supplied one-liner alone does not enforce all those properties; its inner generator is not consumed, so independent checks are necessary.

