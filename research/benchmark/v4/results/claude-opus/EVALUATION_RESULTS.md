# make-prompt-better v4.0 Benchmark: Evaluation Results (claude-opus)

- **Evaluator / generator model:** Claude Opus 5.5 (High reasoning effort), running inside Antigravity
- **Date:** 2026-10-30
- **Protocol:** `research/benchmark/v4/EVALUATION_PROMPT_V4.md` (12 tests, Baseline -> Optimized Prompt -> Optimized Response -> Evaluation)
- **Skill files read before starting:** `make-prompt-better/SKILL.md`, `make-prompt-better/references/domain-templates.md`, `make-prompt-better/references/research-principles.md`

## Evaluator Disclosures

> [!IMPORTANT]
> **Self-evaluation bias.** I am both the generator and the judge for every response in this file. I know which response is the optimized one while scoring it, and I wrote the optimized prompts myself. Treat every score below as a single-rater, non-blind estimate. Deltas of 1 point out of 25 are within my own noise floor.

1. **Sequential execution.** For each test I wrote the Baseline response first, then the Optimized Prompt, then the Optimized Response, then the scores. I did read all 12 raw prompts once at the start (they appear together in the protocol file), which is unavoidable.
2. **Word counts** were computed with a script (whitespace-delimited tokens, code included) over each response section only. The optimized *prompt* is excluded from the Overhead Ratio and reported separately as "Prompt Words".
3. **Executed verification.** Tests 1 and 12 involve code. As evaluator, I executed both baseline and optimized code in a local Python 3.14.2 sandbox to score Accuracy on evidence rather than inspection. Arithmetic in Tests 2, 8, and 9 was recomputed with a script. Results of those runs are cited in the evaluation blocks.
4. **Knowledge horizon.** Legal, regulatory, vendor, and research facts are stated from training knowledge and may be stale relative to the 2026-10-30 evaluation date. Both versions are subject to the same limitation; where a response flags uncertainty, that is scored as a strength.
5. **Template numbering mismatch in the protocol.** The protocol labels targets as "Template 2 `[F1]`-`[F3]`", "Template 6 `[O1]`-`[O3]`", "Template 10 `[NT0]` + `[SC0]`", and "Template 12 `[HARNESS]`". In `domain-templates.md`, Financial is Template 9, Decision-Making is Template 5, Creative is Template 12, Template 10 is the Blank template, and the LRM harness lives in `SKILL.md` Mode 3 Pattern A rather than in any numbered template. No `[F]`, `[O]`, `[R]`, `[C]`, `[D]`, `[E]`, `[L]`, `[S]`, or `[SC0]` identifier families exist in the skill. I used the skill files as the source of truth and mapped each test to the template that matches its domain. This is logged as a failure mode in Section 8 of the Final Report.

---

## TEST 1: Code Review (Accuracy | Mode 1 Max | Template 1 Code Review)

### BASELINE RESPONSE

Yes. There is one serious bug, a unit-consistency bug tied to it, and several robustness problems.

**1. The percentage is never converted to a fraction (critical).**
`price * discount_percent` only works if `discount_percent` is a fraction like `0.2`. The parameter name says it is a percent. If a caller passes `20` meaning 20%:

```
final_price = 100 - (100 * 20) = -1900  ->  clamped to 0
```

Any discount of 1 or more gives the item away for free.

**2. The member bonus uses the opposite unit convention.**
`discount_percent += 10` assumes percentage points. If callers use fractions instead (to make line 4 work), a member with `0.2` ends up with `10.2`, which again produces a negative price clamped to 0. There is no single unit convention under which both lines are correct: with percents line 4 breaks, with fractions line 2 breaks. Today every member gets everything free.

**3. The `< 0` clamp hides the bug instead of catching it.**
Returning 0 for a negative result turns an obvious error into a silent free sale. A negative final price should be impossible with valid inputs, so reaching that branch should raise an error.

**4. No input validation.**
- A negative discount raises the price (`calculate_discount(100, -0.5, False)` returns `150.0` under the fraction convention).
- A negative price passes straight through to the clamp and returns 0.
- Discounts above 100% are accepted.

**5. Stacked discount can exceed 100%.** A member with a 95% discount gets 105%. Cap the combined value at 100.

**6. Floating point for money.** `calculate_discount(19.99, 0.15, False)` returns `16.9915`. Currency should use `Decimal` and be rounded to cents.

**7. Minor: inconsistent return type.** The function returns `int` 0 on one path and `float` on the other.

**Open spec question:** is the member bonus additive (20% + 10% = 30% off) or multiplicative (20% off, then 10% off the remainder = 28% off)? The code implies additive; confirm with whoever owns pricing.

**Fixed version** (assumes `discount_percent` is a percent in 0-100 and the bonus is additive):

```python
from decimal import Decimal, ROUND_HALF_UP

MEMBER_BONUS_PERCENT = Decimal("10")


def calculate_discount(price, discount_percent, is_member):
    """Return the final price after applying a percentage discount (0-100)."""
    price = Decimal(str(price))
    pct = Decimal(str(discount_percent))
    if price < 0:
        raise ValueError("price must be non-negative")
    if not Decimal("0") <= pct <= Decimal("100"):
        raise ValueError("discount_percent must be between 0 and 100")
    if is_member:
        pct = min(pct + MEMBER_BONUS_PERCENT, Decimal("100"))
    final_price = price * (Decimal("100") - pct) / Decimal("100")
    return final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**Tests worth adding:**

```python
assert calculate_discount(100, 20, False) == Decimal("80.00")
assert calculate_discount(100, 20, True) == Decimal("70.00")
assert calculate_discount(100, 95, True) == Decimal("0.00")    # capped at 100%
assert calculate_discount(19.99, 15, False) == Decimal("16.99")
# ValueError for: price=-1, discount=101, discount=-5
```

### OPTIMIZED PROMPT

**Task classification:** Accuracy-dependent (code verification). Persona omitted per `[PRISM]`. **Mode 1 Max Certificate**, Template 1 (Code Review / Patch Verification). Expected overhead ~2.2x.
**Diagnosis of raw prompt:** guesswork gap (no stated unit convention for `discount_percent`, no spec for member stacking), no verification gate, no required remediation artifact. No goal leakage.

````
The standard code review protocol requires completing the following analytical
certificate before issuing any verdict. Every section must be completed using
observable code artifacts.

ARTIFACT UNDER REVIEW (line numbers added for citation):
L1  def calculate_discount(price, discount_percent, is_member):
L2      if is_member:
L3          discount_percent += 10
L4      final_price = price - (price * discount_percent)
L5      if final_price < 0:
L6          return 0
L7      return final_price

### PREMISES
- [P1] Files modified: the single function above (L1-L7), no surrounding module.
- [P2] Symbols affected: calculate_discount (L1); parameters price,
  discount_percent, is_member; local final_price.
- [P3] Test coverage: none provided.
- [P4] Runtime constraints: Python 3, numeric inputs of unspecified type
  (int, float, or Decimal); no docstring or spec defines the unit of
  discount_percent or the member-stacking rule.

### EXECUTION TRACES
For each code path and each plausible input convention, trace:
- [T1] Trace [path or input case]:
  1. Entry point: concrete input values
  2. Call chain / lines executed: cite L-numbers
  3. Data flow and state: show the arithmetic at each line
  4. Exit condition: exact return value
Required trace set: percent convention (e.g. 20), fraction convention
(e.g. 0.2), member and non-member for each, negative and >100% discounts,
negative price, and a non-terminating decimal price (e.g. 19.99).

Grounding rule: Derive behavior from the arithmetic on each cited line rather
than from parameter names. When intended behavior depends on a spec that is
absent from [P1]-[P4], record `UNABLE TO TRACE: [missing spec]` and state the
assumption used for remediation.

### FORMAL CONCLUSION
- Verdict: [PASS / FAIL]
- Supporting traces: cite T-identifiers for every defect
- Verification gaps: every UNABLE TO TRACE item
- Confidence: [HIGH / MEDIUM / LOW] tied to T-identifiers

### REMEDIATION / NEXT ACTION
The task is incomplete until this section provides a complete, copy-pasteable
patch fixing every defect in [T], plus exact test cases covering each trace.

TRACEABILITY SELF-CHECK: Verify that every claim in the Formal Conclusion cites
at least one [T] identifier. Remove or trace any unreferenced claim.
````

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] Artifact: `calculate_discount`, L1-L7, standalone.
- [P2] Symbols: `price`, `discount_percent`, `is_member`, local `final_price`.
- [P3] Tests: none provided.
- [P4] Constraints: Python 3; numeric type unspecified; unit of `discount_percent` and member-stacking rule unspecified.

#### EXECUTION TRACES
- [T1] Percent convention, non-member, `(100, 20, False)`:
  1. L2 false, skip L3.
  2. L4: `100 - (100 * 20) = -1900`.
  3. L5 true (`-1900 < 0`).
  4. L6 returns `0`. A 20% discount produces a free item.
- [T2] Percent convention, member, `(100, 20, True)`:
  1. L3: `discount_percent = 30`.
  2. L4: `100 - 3000 = -2900`; L5 true; L6 returns `0`.
- [T3] Fraction convention, non-member, `(100, 0.2, False)`:
  1. L4: `100 - 20.0 = 80.0`; L5 false; L7 returns `80.0`. Correct under this convention.
- [T4] Fraction convention, member, `(100, 0.2, True)`:
  1. L3: `0.2 + 10 = 10.2` (L3 adds percentage points, L4 expects a fraction).
  2. L4: `100 - 1020.0 = -920.0`; L6 returns `0`.
  3. Result: [T1]-[T4] show no input convention makes both L3 and L4 correct.
- [T5] Negative discount, fraction convention, `(100, -0.5, False)`:
  1. L4: `100 - (-50.0) = 150.0`; L7 returns `150.0`. The "discount" raises the price; nothing rejects it.
- [T6] Discount over 100%, fraction convention, `(100, 1.5, False)`:
  1. L4: `100 - 150.0 = -50.0`; L6 returns `0`. Invalid input is silently converted to a free item.
- [T7] Negative price, `(-50, 0.2, False)`:
  1. L4: `-50 - (-10.0) = -40.0`; L6 returns `0`. Invalid price is masked rather than rejected.
- [T8] Decimal precision, `(19.99, 0.15, False)`:
  1. L4: `19.99 - 2.9985 = 16.9915` (float); L7 returns an unrounded, binary-float currency value.
- [T9] Return type across paths:
  1. L6 returns `int` 0; L7 returns `float` (or whatever type `price` is). Callers receive inconsistent types.
- [T10] Member stacking semantics:
  1. L3 implements additive stacking (20 + 10 = 30). `UNABLE TO TRACE: specification of whether member bonus is additive (30%) or multiplicative (28%)`. Remediation assumes additive, matching current intent of L3.
- [T11] Clamp semantics (L5-L6):
  1. Under valid inputs and a correct formula, `final_price` can never be negative. [T1], [T2], [T4], [T6], [T7] all reach L6 only through a defect or invalid input, so L5-L6 conceals defects instead of handling a legitimate case.

#### FORMAL CONCLUSION
- **Verdict: FAIL.**
- **Defect 1 (critical):** L4 multiplies by a percentage without dividing by 100; any discount of 1 or more yields a free item ([T1], [T2]).
- **Defect 2 (critical):** L3 and L4 use incompatible units; all member purchases resolve to 0 under either convention ([T2], [T4]).
- **Defect 3:** L5-L6 masks Defects 1-2 and invalid inputs as a free sale ([T6], [T7], [T11]).
- **Defect 4:** No validation of discount range or price sign ([T5], [T6], [T7]).
- **Defect 5:** No cap on combined discount above 100% ([T2], [T6]).
- **Defect 6:** Float arithmetic and no rounding for currency ([T8]).
- **Defect 7 (minor):** Inconsistent return type ([T9]).
- **Verification gaps:** member stacking rule ([T10]); expected input unit (resolved by assumption: percent 0-100, matching the parameter name).
- **Confidence: HIGH** for Defects 1-7 (each is reproduced arithmetically in a trace); MEDIUM on the stacking assumption ([T10]).

#### REMEDIATION / NEXT ACTION

```python
from decimal import Decimal, ROUND_HALF_UP

MEMBER_BONUS_PERCENT = Decimal("10")  # additive percentage points; see [T10]


def calculate_discount(price, discount_percent, is_member):
    """Return the final price after a percentage discount.

    discount_percent: percent in [0, 100] (e.g. 20 means 20%).
    Members receive MEMBER_BONUS_PERCENT extra points, capped at 100%.
    """
    price = Decimal(str(price))
    pct = Decimal(str(discount_percent))
    if price < 0:                                            # [T7]
        raise ValueError("price must be non-negative")
    if not Decimal("0") <= pct <= Decimal("100"):            # [T5], [T6]
        raise ValueError("discount_percent must be between 0 and 100")
    if is_member:                                            # [T2], [T4]
        pct = min(pct + MEMBER_BONUS_PERCENT, Decimal("100"))
    final_price = price * (Decimal("100") - pct) / Decimal("100")   # [T1]
    return final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  # [T8], [T9]
```

The L5-L6 clamp is removed because, after validation, the result is provably in `[0, price]` ([T11]).

Test cases covering each trace:

```python
import pytest
from decimal import Decimal

@pytest.mark.parametrize("price,pct,member,expected", [
    (100, 20, False, "80.00"),    # T1
    (100, 20, True, "70.00"),     # T2
    (100, 95, True, "0.00"),      # T2/T6 cap
    (100, 0, False, "100.00"),    # boundary
    (19.99, 15, False, "16.99"),  # T8
])
def test_discount(price, pct, member, expected):
    assert calculate_discount(price, pct, member) == Decimal(expected)

@pytest.mark.parametrize("price,pct", [(-50, 20), (100, -5), (100, 101)])  # T5, T6, T7
def test_invalid_inputs_raise(price, pct):
    with pytest.raises(ValueError):
        calculate_discount(price, pct, False)
```

Next action for [T10]: confirm the stacking rule with the pricing owner; if multiplicative, replace the member line with `pct = 100 - (100 - pct) * (100 - MEMBER_BONUS_PERCENT) / 100`.

**Traceability self-check:** Defects 1-7 and both gaps each cite at least one T-identifier. No orphaned claims.

### EVALUATION: TEST 1

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 5        | 4         | -1    |
| Actionability | 5        | 5         | 0     |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 24/25    | 24/25     | 0     |

Baseline Words: 453 | Optimized Words: 785 | Overhead Ratio: 1.73x | Prompt Words: 381

Both responses found the same seven defects and shipped the same patch; I executed the patch and the original function as evaluator, and every value quoted in both responses reproduced exactly (for example, original `(100, -0.5, False)` returned `150.0` and `(19.99, 0.15, False)` returned `16.9915`; all fix assertions passed). The certificate improved traceability (line-cited traces, per-test trace tags, explicit `UNABLE TO TRACE` on the stacking rule) but cost Structure: eleven traces for a seven-line function is more ceremony than the task needs. Net result is a tie, which is the ceiling effect expected on a short, well-scoped bug hunt.

---

## TEST 2: Financial Analysis (Accuracy | Mode 1 Max | Template 9 Financial Due Diligence)

### BASELINE RESPONSE

**Short version:** the business looks healthy and improving on the numbers given: revenue recovered from a Q2 dip and accelerated, and operating margin expanded sharply because costs stayed roughly flat while revenue grew. The $15M of new debt looks modest relative to earnings, but there isn't enough information to call the company financially *healthy* overall, because there is no cash flow or balance sheet data.

**Quarterly picture ($M)**

| | Q1 | Q2 | Q3 | Q4 | FY |
|---|---|---|---|---|---|
| Revenue | 50.0 | 47.0 | 52.0 | 61.0 | 210.0 |
| QoQ growth | n/a | -6.0% | +10.6% | +17.3% | |
| Opex % of revenue | 78% | 82% | 75% | 71% | 76.1% |
| Opex | 39.0 | 38.5 | 39.0 | 43.3 | 159.9 |
| Operating income | 11.0 | 8.5 | 13.0 | 17.7 | 50.2 |
| Operating margin | 22% | 18% | 25% | 29% | 23.9% |

**What's going well**
- **Growth is accelerating.** After a 6% dip in Q2, revenue grew 10.6% and then 17.3% quarter over quarter. Q4 is 22% above Q1.
- **Operating leverage.** Opex was almost flat at about $39M for Q1 through Q3 even as revenue moved around, which suggests a largely fixed cost base. In Q4 opex rose 11% while revenue rose 17%, so most of the extra revenue fell to the bottom line. Operating income in Q4 ($17.7M) is 61% higher than Q1.
- **Margin trend.** Operating margin went from 22% to 29% across the year, with Q2 as the low point.

**What to watch**
- **The Q2 dip.** A 6% revenue drop with flat costs pushed margin down to 18%. That shows the downside of a fixed cost base: if revenue falls, margins compress quickly. Worth understanding whether Q2 was seasonal, a lost customer, or a one-off.
- **The debt.** $15M is about 30% of full-year operating income and roughly 0.2x the Q4 annualized run-rate ($17.7M x 4 = $70.8M). Even at a 10% interest rate that's about $1.5M a year of interest against ~$50M of operating income, so servicing it should not be a problem. The bigger question is *why* they borrowed when they were already profitable: growth investment, an acquisition, or a cash crunch would mean very different things. It's notable that the Q4 jump came right after the borrowing.
- **Possible seasonality.** With only one year of data, a strong Q4 could be seasonal rather than a trend.

**What's missing to properly judge financial health**
- Cash flow (operating income is not cash; receivables could be growing)
- Balance sheet: cash, existing debt, total liabilities
- Debt terms: interest rate, maturity, covenants
- What "operating expenses" includes (does it include cost of revenue? D&A?)
- Capex, taxes, and interest below the operating line
- Prior-year comparisons for seasonality

**Overall:** improving profitability and growth with manageable leverage on the information given, but the assessment is based on the income statement alone. I'd want cash flow and balance sheet data before calling it healthy with confidence.

### OPTIMIZED PROMPT

**Task classification:** Accuracy-dependent (numerical financial analysis). Persona omitted (`[PRISM]`). **Mode 1 Max Certificate**, Template 9 (Financial Due Diligence). Expected overhead ~2.2x.
**Diagnosis:** "Analyze their financial health" is an unbounded verdict request with no defined dimensions (guesswork gap, `[META]`); no instruction to separate reported vs. derived figures; no missing-data predicate; no required remediation artifact. No goal leakage.

```
Financial due diligence methodology requires completing this analytical
certificate before presenting any posture summary.

### PREMISES
- [P1] Entity and figures examined:
  Revenue: Q1 $50M, Q2 $47M, Q3 $52M, Q4 $61M.
  Operating expenses as % of revenue: Q1 78%, Q2 82%, Q3 75%, Q4 71%.
  New debt: $15M taken on in Q3. No other statements provided.
- [P2] Analytical dimensions: (a) revenue trajectory, (b) cost structure and
  operating leverage, (c) operating profitability, (d) leverage and debt
  service capacity, (e) liquidity and cash conversion, (f) earnings quality.
- [P3] Reference benchmarks: the four quarters in [P1] relative to each other.

### FINANCIAL TRACES
For each analytical dimension in [P2]:
- [T1] Dimension [name]:
  1. Reported figures: exact numbers and periods from [P1]
  2. Derived calculation: explicit formula and arithmetic
  3. Period trajectory: direction and rate of change across quarters
  4. Statement reconciliation: cross-checks possible with [P1], or the
     reconciliation that is impossible and why

Grounding rule: Compute metrics exclusively from figures present in [P1]. When
a required input is missing from [P1], record
`INSUFFICIENT DATA FOR [Tn]: [missing metric]`. When a figure supports a
scenario rather than a fact (for example an assumed interest rate), label it
SCENARIO and show the assumption.

Counterexample predicate: When any quarter moves against the overall trend,
record it as its own trace even if the overall posture is positive.

### FORMAL CONCLUSION
- Financial posture summary: factual synthesis citing T-identifiers
- Verified strengths vs. structural divergences: separated, citing T-traces
- Data completeness gaps: all items marked INSUFFICIENT DATA

### REMEDIATION / NEXT ACTION
Provide the exact diligence request list and spreadsheet verification formulas
needed to close all Data Completeness Gaps.
DISCLAIMER: This output is analytical support, not investment advice.

TRACEABILITY SELF-CHECK: Verify that every figure and claim in the conclusion
cites a specific [T] calculation trace.
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] Revenue $50M / $47M / $52M / $61M (Q1-Q4). Opex ratio 78% / 82% / 75% / 71%. $15M new debt in Q3. No balance sheet, cash flow, or debt terms.
- [P2] Dimensions (a)-(f) as listed.
- [P3] Benchmarks: intra-year quarter comparison only.

#### FINANCIAL TRACES
- [T1] Revenue trajectory
  1. Reported: 50.0, 47.0, 52.0, 61.0. FY = 210.0.
  2. QoQ growth = R(t)/R(t-1) - 1: Q2 = 47/50 - 1 = **-6.0%**; Q3 = 52/47 - 1 = **+10.6%**; Q4 = 61/52 - 1 = **+17.3%**. Q4 vs Q1 = 61/50 - 1 = **+22.0%**.
  3. Trajectory: one contraction, then two quarters of accelerating growth.
  4. Reconciliation: `INSUFFICIENT DATA FOR [T1]: prior-year quarters` (cannot separate trend from seasonality).
- [T2] Counterexample: Q2 contraction
  1. Revenue -$3.0M QoQ while opex ratio rose 78% -> 82%.
  2. Opex Q2 = 47 x 0.82 = $38.54M vs Q1 $39.00M: opex fell only $0.46M (-1.2%) while revenue fell $3.0M (-6.0%).
  3. Decremental margin = (8.46 - 11.00) / (47 - 50) = **84.7%**: 85 cents of every lost revenue dollar came out of operating income.
  4. Cause: `INSUFFICIENT DATA FOR [T2]: customer churn, pricing, or seasonal explanation`.
- [T3] Cost structure and operating leverage
  1. Opex = R x ratio: Q1 39.00, Q2 38.54, Q3 39.00, Q4 43.31. FY = **$159.85M** (76.1% of revenue).
  2. QoQ opex change: -1.2%, +1.2%, **+11.1%**.
  3. Incremental margin = ΔOI / ΔRevenue: Q2->Q3 = 4.54 / 5.0 = **90.8%**; Q3->Q4 = 4.69 / 9.0 = **52.1%**.
  4. Interpretation: Q1-Q3 opex held within $0.46M of $39M, consistent with a largely fixed cost base. Q4 is the first quarter where opex stepped up materially. Reconciliation: `INSUFFICIENT DATA FOR [T3]: opex composition (COGS, S&M, R&D, G&A, D&A)`; whether "operating expenses" includes cost of revenue is not stated.
- [T4] Operating profitability
  1. Operating income = R - Opex: Q1 **11.00**, Q2 **8.46**, Q3 **13.00**, Q4 **17.69**. FY = **$50.15M**.
  2. Operating margin = 1 - ratio: 22%, 18%, 25%, 29%. FY margin = 50.15 / 210 = **23.9%**.
  3. Q4 operating income is 17.69 / 11.00 - 1 = **+60.8%** above Q1.
  4. Reconciliation: `INSUFFICIENT DATA FOR [T4]: interest, taxes, D&A` (cannot compute net income or EBITDA).
- [T5] Leverage and debt service capacity
  1. Reported: $15M new debt in Q3. Existing debt: `INSUFFICIENT DATA FOR [T5]: pre-Q3 debt balance, rate, maturity, covenants`.
  2. New debt / FY operating income = 15 / 50.15 = **0.30x**. New debt / Q4 annualized OI (17.69 x 4 = 70.76) = **0.21x**.
  3. SCENARIO interest coverage (assumed rates, not reported): at 6%, annual interest = $0.90M, coverage = 50.15 / 0.90 = **55.7x**; at 10%, interest = $1.50M, coverage = **33.4x**; at 15%, interest = $2.25M, coverage = **22.3x**.
  4. Timing: Q4 revenue acceleration (+17.3%) and the opex step-up (+11.1%) follow the Q3 borrowing. Causal link is `UNABLE TO TRACE: use of proceeds`.
- [T6] Liquidity and cash conversion
  1. `INSUFFICIENT DATA FOR [T6]: cash balance, operating cash flow, working capital, capex`.
  2. No derived calculation is possible. Operating income cannot be treated as cash generation without the cash flow statement.
- [T7] Earnings quality
  1. `INSUFFICIENT DATA FOR [T7]: revenue recognition policy, receivables, deferred revenue, customer concentration, one-time items`.
  2. Observable flag only: the Q4 jump (+$9M QoQ) is the largest movement in the year and is the quarter most worth decomposing.

#### FORMAL CONCLUSION
- **Financial posture summary:** On the income-statement figures provided, the company is profitable in every quarter and its profitability is improving: FY operating income $50.15M at a 23.9% margin ([T4]), with revenue +22% from Q1 to Q4 ([T1]). Debt service on the new $15M appears comfortably covered under any plausible rate ([T5] SCENARIO). Overall financial *health* cannot be fully determined because liquidity, cash conversion, and total leverage are untraceable ([T5], [T6], [T7]).
- **Verified strengths:**
  1. Accelerating growth after Q2: +10.6%, then +17.3% QoQ ([T1]).
  2. Strong operating leverage: 52% to 91% incremental margins ([T3]).
  3. Margin expansion from 22% to 29% in Q1 vs Q4 ([T4]).
  4. New debt is 0.30x FY operating income ([T5]).
- **Structural divergences:**
  1. High fixed-cost sensitivity: the Q2 contraction carried an 84.7% decremental margin ([T2]). A revenue downturn would compress profit quickly.
  2. Q4 cost step-up (+11.1% opex) coincides with new borrowing; whether this is funded expansion with durable returns is unverified ([T3], [T5]).
  3. Single-year view cannot exclude seasonality as the driver of the strong Q4 ([T1]).
- **Data completeness gaps:** prior-year quarters ([T1]); Q2 driver ([T2]); opex composition ([T3]); interest, taxes, D&A ([T4]); existing debt and terms, use of proceeds ([T5]); cash flow and balance sheet ([T6]); revenue quality ([T7]).

#### REMEDIATION / NEXT ACTION
**Diligence request list**
1. Quarterly cash flow statements for the year (closes [T6]).
2. Quarter-end balance sheets, including cash, total debt, and working capital (closes [T5], [T6]).
3. Credit agreement for the Q3 facility: rate, maturity, amortization, covenants, use of proceeds (closes [T5]).
4. Opex breakdown by function with COGS shown separately (closes [T3]).
5. Prior two years of quarterly revenue (closes [T1] seasonality).
6. Revenue by customer, top-10 concentration, and Q2 churn explanation (closes [T2], [T7]).
7. AR aging and deferred revenue by quarter (closes [T7]).

**Spreadsheet verification formulas** (revenue in B2:E2, opex ratio in B3:E3):
- Opex: `=B2*B3` (fill right)
- Operating income: `=B2-B4`
- QoQ growth: `=C2/B2-1`
- Incremental margin: `=(C5-B5)/(C2-B2)`
- Interest coverage (once rate is known in G1, debt in G2): `=SUM(B5:E5)/(G1*G2)`
- Cash conversion (once OCF is in row 7): `=SUM(B7:E7)/SUM(B5:E5)`

DISCLAIMER: This output is analytical support, not investment advice.

**Traceability self-check:** every figure in the conclusion maps to [T1]-[T7]; all scenario figures are labeled SCENARIO.

### EVALUATION: TEST 2

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 4        | 5         | +1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 22/25    | 24/25     | +2    |

Baseline Words: 512 | Optimized Words: 944 | Overhead Ratio: 1.84x | Prompt Words: 359

All figures in both responses match my scripted recomputation (FY opex 159.85, FY operating income 50.15, margin 23.88%, incremental margins 90.8% and 52.1%, debt/OI 0.299). The optimized version added two genuinely useful analyses that the baseline only gestured at (the 84.7% decremental margin in Q2 via the counterexample predicate, and labeled interest-coverage scenarios) and converted "what's missing" into a request list with formulas. The baseline's single table plus prose was easier to read, so Structure drops one point for the optimized version.

---

## TEST 3: Medical Reasoning (Accuracy | Mode 1 Max | Template 7 Medical / Clinical Reasoning)

### BASELINE RESPONSE

**Most likely diagnosis: acute inferior ST-elevation myocardial infarction (STEMI)**, most often from right coronary artery (RCA) occlusion, with hypotension and tachycardia raising concern for **right ventricular (RV) involvement** and early cardiogenic shock.

Why: classic ischemic pain (radiating to the left arm, diaphoresis, dyspnea) plus ST elevation in the contiguous inferior leads II, III, and aVF meets STEMI criteria. STEMI is an ECG diagnosis, so the pending troponin should not delay treatment. Hypotension (90/60) with an inferior STEMI is a red flag for RV infarction, which occurs in a substantial share of inferior MIs. The shock index (HR / SBP = 110 / 90 ≈ 1.2) is elevated.

**Immediate priorities**

1. **Activate the cath lab for primary PCI.** Target first-medical-contact-to-device time of 90 minutes or less (120 minutes or less if transfer is needed). If PCI cannot be achieved within 120 minutes, give fibrinolysis within 30 minutes of arrival, assuming no contraindications.
2. **Get a right-sided ECG (V4R)** to look for RV infarction (ST elevation of 1 mm or more in V4R), and consider posterior leads (V7-V9). Look for reciprocal ST depression in I and aVL and whether ST elevation in III exceeds II (favors RCA).
3. **Antiplatelet and anticoagulant therapy:** aspirin 162-325 mg chewed; a P2Y12 inhibitor (ticagrelor or clopidogrel loading, per cath lab protocol); unfractionated heparin.
4. **Manage hypotension carefully:**
   - **Avoid nitrates** (SBP at 90 and suspected RV infarct; nitrates can cause profound hypotension in preload-dependent RV infarction).
   - **Avoid beta-blockers** (hypotension, possible evolving shock).
   - Use morphine cautiously, if at all.
   - If lungs are clear and RV infarct is suspected, give cautious IV fluid boluses (for example 250-500 mL) and reassess.
   - If hypotension persists, escalate to vasopressors/inotropes (norepinephrine first line for cardiogenic shock) and consider mechanical circulatory support.
5. **Oxygen only if SpO2 falls below 90%.** At 94%, routine supplemental oxygen is not indicated.
6. **Continuous monitoring, defibrillator pads on.** RCA occlusion commonly causes bradycardia and AV block; have atropine and pacing available. Watch for VT/VF.
7. **Bedside echo** if it does not delay reperfusion: RV function, LV wall motion, mechanical complications, pericardial effusion.
8. **Exclude aortic dissection before full anticoagulation if there is any suspicion** (tearing pain to the back, pulse or BP differential between arms, neurological deficit, widened mediastinum). Dissection can extend into the RCA ostium and mimic inferior STEMI, and anticoagulation or fibrinolysis would be catastrophic.
9. **Labs:** troponin (already pending), CBC, BMP, coagulation profile, lactate, type and screen.

**Differential to keep in mind:** aortic dissection (as above), pulmonary embolism (hypotension, tachycardia, hypoxia), and pericarditis (usually diffuse ST elevation with PR depression, not regional with reciprocal changes).

*This is educational information; real patients need management by a qualified clinical team following local protocols.*

### OPTIMIZED PROMPT

**Task classification:** Accuracy-dependent (clinical reasoning). Persona omitted (`[PRISM]`: roleplay framing degrades diagnostic accuracy). **Mode 1 Max Certificate**, Template 7 (Medical / Clinical Reasoning). Expected overhead ~2.2x.
**Diagnosis:** "Most likely diagnosis" invites premature anchoring on a single label (guesswork gap); no instruction to separate probability from acuity, to trace disconfirming findings, or to list discriminating gaps. No goal leakage.

```
Clinical reasoning methodology, as established in evidence-based medicine,
requires completing this structured certificate before presenting any
differential synthesis.

### PREMISES
- [P1] Presenting context: 58-year-old male; sudden-onset chest pain radiating
  to the left arm; diaphoresis; shortness of breath.
- [P2] Objective findings: BP 90/60, HR 110, SpO2 94%. ECG: ST elevation in
  II, III, aVF. Troponin pending.
- [P3] Active regimen: not provided.
- [P4] Reference guidelines: current ACC/AHA and ESC acute coronary syndrome
  guidance for reperfusion timing, antithrombotic therapy, and hemodynamic
  management.

### DIAGNOSTIC & THERAPEUTIC TRACES
For each plausible condition in the differential:
- [T1] Condition [name]:
  1. Supporting findings: specific items from P1/P2/P3
  2. Disconfirming findings: specific items from P1/P2/P3
  3. Discriminating gaps: missing history, exam, lab, or imaging
  4. Acuity and risk: time-sensitivity per P4
Then trace each immediate management priority:
- [Tn] Priority [action]: the P1-P4 finding that triggers it, and the P2
  finding that modifies or contraindicates it.

Grounding rule: Evaluate multiple competing hypotheses across all data points
in [P1]-[P3] before ranking, separating probability from acuity. When a
management decision depends on a finding absent from [P1]-[P3], record
`DISCRIMINATING GAP: [finding]` and state the conditional action for each
possible result.

### FORMAL CONCLUSION
- Evidence-ranked differential: conditions ordered by supporting T-traces
- High-acuity exclusions required: urgent conditions citing T-identifiers
- Immediate priorities: ordered, each citing T-identifiers
- Critical information gaps: discriminating workup items from T-traces

### REMEDIATION / NEXT ACTION
List the concrete diagnostic workup questions and verification checks needed
to resolve the discriminating gaps in [T].
DISCLAIMER: This output is structured analytical support, not clinical advice.
All diagnostic and treatment decisions require a licensed healthcare clinician.

TRACEABILITY SELF-CHECK: Verify that every condition and workup item in the
conclusion cites a specific [T] trace and [P] premise.
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] 58M; sudden chest pain radiating to left arm; diaphoresis; dyspnea.
- [P2] BP 90/60; HR 110; SpO2 94%; ST elevation II, III, aVF; troponin pending.
- [P3] Medications, allergies, history: not provided.
- [P4] ACC/AHA ACS guideline (2025) and ESC ACS guideline (2023): primary PCI preferred; first-medical-contact-to-device 90 min or less (120 min or less with transfer); fibrinolysis when PCI is not achievable within 120 min; oxygen only if SpO2 below 90%.

#### DIAGNOSTIC & THERAPEUTIC TRACES
- [T1] Inferior STEMI (likely RCA)
  1. Supporting: ischemic pain pattern, diaphoresis, dyspnea ([P1]); ST elevation in three contiguous inferior leads ([P2]).
  2. Disconfirming: none in [P1]-[P2]. Troponin pending does not disconfirm; STEMI is an ECG diagnosis.
  3. Gaps: reciprocal ST depression in I/aVL; III vs II elevation magnitude (III > II favors RCA over circumflex); posterior involvement (V7-V9).
  4. Acuity: highest; time-to-reperfusion determines myocardial salvage ([P4]).
- [T2] RV infarction complicating [T1]
  1. Supporting: hypotension (SBP 90) with inferior STEMI ([P2]); shock index = 110 / 90 = **1.22**.
  2. Disconfirming: none recorded, but SpO2 94% with dyspnea could instead reflect LV failure with pulmonary congestion.
  3. `DISCRIMINATING GAP: V4R ST elevation (1 mm or more); JVP; lung auscultation.` Classic RV pattern is hypotension + elevated JVP + clear lungs. If crackles are present, LV failure dominates and fluid loading is harmful.
  4. Acuity: high; changes hemodynamic management immediately ([T6], [T7]).
- [T3] Evolving cardiogenic shock
  1. Supporting: SBP 90, HR 110, diaphoresis, dyspnea ([P1], [P2]).
  2. Disconfirming: SBP is at, not below, the 90 mmHg threshold; perfusion markers are absent from [P2].
  3. `DISCRIMINATING GAP: lactate, mental status, urine output, skin perfusion, repeat BP trend.`
  4. Acuity: high; shock changes the reperfusion and support strategy (vasopressors, mechanical support).
- [T4] Acute aortic dissection (type A) involving the RCA ostium
  1. Supporting: sudden onset, hypotension ([P1], [P2]); dissection into the RCA can produce inferior ST elevation.
  2. Disconfirming: pain described as radiating to the left arm rather than tearing pain to the back; not decisive.
  3. `DISCRIMINATING GAP: bilateral arm BPs, pulse deficits, neurological deficits, aortic regurgitation murmur, mediastinal width, bedside echo for flap or effusion.`
  4. Acuity: highest, and it inverts management: anticoagulation and fibrinolysis are contraindicated. Probability is low but the harm asymmetry requires active exclusion before or alongside antithrombotics.
- [T5] Pulmonary embolism / pericarditis
  1. Supporting (PE): hypotension, tachycardia, dyspnea, SpO2 94% ([P2]).
  2. Disconfirming: regional inferior ST elevation fits coronary occlusion better than PE (PE more often shows sinus tachycardia, right heart strain) or pericarditis (diffuse ST elevation with PR depression).
  3. Gaps: full 12-lead morphology; echo (RV dilation without inferior wall motion abnormality would favor PE).
  4. Acuity: PE high, pericarditis low; both lower probability given [P2].
- [T6] Priority: reperfusion. Triggered by [T1]. Activate cath lab; FMC-to-device 90 min or less ([P4]). If PCI is not achievable within 120 min, fibrinolysis within 30 min, conditional on [T4] exclusion and no contraindications (unknown, [P3]).
- [T7] Priority: hemodynamics. Triggered by [T2], [T3].
  - Nitrates: withhold (SBP 90 and suspected RV involvement, [P2], [T2]).
  - Beta-blockers: withhold (hypotension, compensatory tachycardia, [P2]).
  - Morphine: avoid or use minimal doses (hypotension; delays oral P2Y12 absorption).
  - If V4R positive and lungs clear: IV fluid boluses of 250-500 mL with reassessment ([T2]).
  - If lungs show congestion or hypotension persists: norepinephrine; evaluate for mechanical circulatory support ([T3]).
- [T8] Priority: antithrombotic therapy. Triggered by [T1]; modified by [T4] and [P3].
  - Aspirin 162-325 mg chewed; P2Y12 loading per cath lab protocol; unfractionated heparin.
  - Conditional: hold pending rapid exclusion of [T4] if any dissection feature is present; confirm allergy and bleeding history (`DISCRIMINATING GAP: [P3]`).
- [T9] Priority: rhythm and monitoring. Triggered by [T1] (RCA supplies the SA and AV nodes in most patients).
  - Continuous monitoring, defibrillator pads, atropine and transcutaneous pacing available for bradycardia or AV block.
- [T10] Priority: oxygen. SpO2 94% is above the 90% threshold in [P4]; no routine oxygen. Reassess if SpO2 falls.

#### FORMAL CONCLUSION
- **Evidence-ranked differential:** (1) Inferior STEMI, probable RCA occlusion ([T1]); (2) with probable RV involvement ([T2]); (3) evolving cardiogenic shock ([T3]); lower probability: aortic dissection ([T4]), PE ([T5]), pericarditis ([T5]).
- **High-acuity exclusions required:** aortic dissection before or alongside antithrombotics ([T4]); LV failure vs. RV infarct before fluid loading ([T2]).
- **Immediate priorities (ordered):** cath lab activation ([T6]); right-sided ECG, JVP, lung exam ([T2]); targeted dissection screen ([T4]); aspirin, P2Y12, heparin ([T8]); withhold nitrates and beta-blockers, guided fluids or vasopressors ([T7]); monitoring and pacing readiness ([T9]); no routine oxygen ([T10]).
- **Critical information gaps:** V4R, JVP, lung exam ([T2]); perfusion markers ([T3]); dissection features ([T4]); medications, allergies, bleeding risk ([T8]).

#### REMEDIATION / NEXT ACTION
Workup checklist, in order:
1. Right-sided ECG (V4R) and posterior leads (V7-V9) within minutes ([T1], [T2]).
2. Exam: JVP, lung bases, bilateral arm BPs, peripheral pulses, focused neuro exam, murmur ([T2], [T4]).
3. Bedside echo if it does not delay reperfusion: RV function, inferior wall motion, aortic root flap, pericardial effusion ([T2], [T4], [T5]).
4. History: medications (especially anticoagulants, PDE5 inhibitors), allergies, prior bleeding, recent surgery or stroke ([T8]).
5. Labs: CBC, BMP, coagulation profile, lactate, type and screen; troponin already sent ([T3], [T8]).
6. Repeat BP every 5 minutes; reassess after any fluid bolus ([T7]).

DISCLAIMER: This output is structured analytical support, not clinical advice. All diagnostic and treatment decisions require a licensed healthcare clinician.

**Traceability self-check:** every differential item, priority, and workup step cites a [T] and [P]. No orphaned claims.

### EVALUATION: TEST 3

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 4        | 5         | +1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 5        | 5         | 0     |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 23/25    | 24/25     | +1    |

Baseline Words: 451 | Optimized Words: 914 | Overhead Ratio: 2.03x | Prompt Words: 353

Both versions reached the same diagnosis and the same core priorities; the baseline was already strong and clinically ordered. The certificate's "disconfirming findings" and `DISCRIMINATING GAP` predicates surfaced one substantive addition: the RV-infarct vs. LV-failure split (SpO2 94% with dyspnea could mean pulmonary congestion, in which case fluids are harmful), which the baseline only covered implicitly with "if lungs are clear". For a time-critical emergency, the baseline's flat numbered list is faster to act on, so Structure favors it.

---

## TEST 4: Legal Analysis (Accuracy | Mode 1 Max | Template 8 Legal Analysis)

### BASELINE RESPONSE

**Bottom line:** As written, this non-compete is very likely overbroad in most U.S. jurisdictions, and in some states it is void outright. But "overbroad" does not automatically mean the employee is safe, because many courts will narrow (rather than throw out) an unreasonable non-compete, and a narrowed version could still cover a job at a direct competitor 150 miles away just 8 months after leaving. The single most important fact missing is **which state's law governs**.

**1. Jurisdiction decides almost everything**
- **Void or nearly void:** California (Bus. & Prof. Code §16600, and since 2024 §16600.5 also bars enforcing out-of-state non-competes against California workers), Minnesota (agreements signed on or after July 1, 2023), North Dakota, and Oklahoma.
- **Restricted by statute:** Several states limit non-competes by income threshold, duration, or notice requirements, including Washington (presumptive 18-month cap and an earnings threshold), Massachusetts (12-month cap, garden leave or other consideration required), Oregon (12-month cap and salary threshold), Illinois (income threshold), and Colorado (only highly compensated workers, with notice requirements).
- **Common-law reasonableness states:** Most other states (for example New York, Pennsylvania, Texas, Georgia, Florida) enforce non-competes that are reasonable, though they differ in how reasonableness is judged.
- **Federal:** The FTC's 2024 rule banning most non-competes was set aside by a federal court in 2024 and the FTC later abandoned its appeal, so there is no nationwide ban; the FTC still challenges specific non-competes case by case.

**2. The reasonableness test (where non-competes are allowed)**
Courts generally ask whether the restriction (a) protects a legitimate business interest such as trade secrets, confidential information, or customer relationships, (b) is reasonable in duration, geography, and scope of activity, and (c) is not unduly harsh on the employee or harmful to the public.

- **Duration (5 years):** This is the weakest term. Courts commonly uphold 6 months to 2 years for ordinary employees; 5 years is usually seen only in sale-of-business contexts.
- **Geography (200 miles):** Could be reasonable if the employer genuinely does business across that area, but it must match where the employee actually worked or had customers.
- **Scope ("any related industry"):** Likely overbroad and vague. Courts prefer restrictions tied to the employee's actual role and to direct competitors, not entire adjacent industries.

**3. Consideration and formation**
Was the agreement signed at hiring or mid-employment? Some states require new consideration (a raise, bonus, promotion) for a mid-employment non-compete; continued employment alone is not always enough.

**4. What happens if a court finds it overbroad**
- **Blue pencil / reformation states** (Texas requires reformation; many others allow it): the court rewrites the restriction to something reasonable, such as 1 year and a smaller radius in the same role.
- **All-or-nothing states** (Wisconsin by statute; Virginia courts generally refuse to rewrite): an overbroad clause fails entirely.
The risk for the employee: if the court reforms the covenant to 12 months, a job at a direct competitor at month 8 could still violate the reformed version.

**5. Facts that matter on the merits**
- Is the new role similar to the old one? Did the employee have access to trade secrets or key customers?
- Was the employee fired or did they resign? Some courts are less willing to enforce against employees terminated without cause.
- Is there a choice-of-law or forum clause?
- Did the employee take any documents or data? (Trade secret claims stand on their own regardless of the non-compete.)
- Are there separate non-solicitation or confidentiality clauses? Those are more often enforceable.

**6. Practical next steps for the employee**
- Get a copy of the full agreement and consult an employment lawyer in the relevant state.
- Do not use or retain any former-employer confidential information.
- Tell the new employer; many will provide legal support or indemnification.
- A threat letter is not a lawsuit. To stop the employee from working, the former employer usually needs a preliminary injunction showing likely success and irreparable harm, which is harder with a facially overbroad covenant.
- In some states the employee can seek a declaratory judgment that the clause is unenforceable.

*This is general information, not legal advice.*

### OPTIMIZED PROMPT

**Task classification:** Accuracy-dependent (legal rule application). Persona omitted (`[PRISM]`). **Mode 1 Max Certificate**, Template 8 (Legal Analysis). Expected overhead ~2.2x.
**Diagnosis:** Governing law is absent (the decisive variable), and the prompt does not ask for counter-interpretations or the remedy question (reformation vs. voiding), which is where the 8-month fact becomes decisive. "The former employer is threatening to sue" is context, not goal leakage, and is retained as a fact.

```
Legal analytical methodology requires completing this structured certificate
before presenting any legal assessment.

### PREMISES
- [P1] Stated facts and text:
  - Covenant text (paraphrased in the record): no work in "any related
    industry" within a 200-mile radius for 5 years after leaving.
  - Employee left; 8 months later took a job at a competitor 150 miles away.
  - Former employer has threatened suit.
  - Not stated: governing-law clause, state of employment, employee role,
    compensation, access to confidential information, when the agreement was
    signed, consideration given, reason for separation.
- [P2] Governing law: not provided. Analyze under (a) jurisdictions that void
  employee non-competes, (b) statutory-limit jurisdictions, and (c) common-law
  reasonableness jurisdictions, plus current federal status.
- [P3] Issues presented: (1) governing law; (2) legitimate interest;
  (3) duration; (4) geography; (5) activity scope; (6) formation and
  consideration; (7) remedy for overbreadth; (8) application to the stated
  breach; (9) obligations independent of the covenant.

### LEGAL TRACES
For each issue in [P3]:
- [T1] Issue [name]:
  1. Governing rule or clause: exact text from P1 or rule from P2
  2. Fact application: how the rule applies to P1 facts
  3. Counter-interpretation: the strongest competing reading
  4. Structural symmetry: whether obligations are mutual or one-sided

Grounding rule: Quote the covenant language from [P1]. When a fact needed to
apply a rule is absent from [P1], record `NOT ADDRESSED IN [P1]: [fact]` and
give the outcome under each possible value of that fact.

### FORMAL CONCLUSION
- Issue-by-issue synthesis: objective assessment citing T-identifiers
- Structural asymmetries and exposure points: citing specific T-traces
- Unresolved interpretive questions: areas requiring extrinsic facts or counsel

### REMEDIATION / NEXT ACTION
Provide copy-pasteable redline clause revisions that would bring the covenant
within a reasonable scope, and the fact-gathering steps that resolve every
NOT ADDRESSED item.
DISCLAIMER: This output is analytical support, not legal advice. Consult
qualified legal counsel for binding determinations.

TRACEABILITY SELF-CHECK: Verify that every conclusion claim cites at least one
[T] trace and its underlying section in [P1]/[P2].
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] Covenant: "any related industry", 200-mile radius, 5 years post-employment. Employee joined a competitor 150 miles away at month 8. Suit threatened. Unknown: governing law, role, pay, access to confidential information, signing date, consideration, separation reason.
- [P2] Three regimes analyzed: void, statutory-limit, common-law reasonableness; plus federal status.
- [P3] Issues (1)-(9) as listed.

#### LEGAL TRACES
- [T1] Governing law
  1. Rule: enforceability is state law. Void regimes: California (Bus. & Prof. Code §16600; §16600.5 extends this to contracts signed elsewhere), Minnesota (Minn. Stat. §181.988, agreements from July 1, 2023), North Dakota (N.D. Cent. Code §9-08-06), Oklahoma (15 Okla. Stat. §219A, customer non-solicits excepted). Statutory-limit regimes include Washington (RCW 49.62: earnings threshold; over 18 months presumed unreasonable), Massachusetts (G.L. c.149 §24L: 12-month cap, garden leave or agreed consideration), Oregon (ORS 653.295: 12-month cap, salary threshold), Illinois (820 ILCS 90: earnings threshold), Colorado (C.R.S. §8-2-113: highly compensated workers only, notice requirements).
  2. Application: `NOT ADDRESSED IN [P1]: governing-law clause and state of employment.` Under a void regime, the covenant fails regardless of [T3]-[T5]. Under Massachusetts or Oregon law, the 5-year term exceeds the statutory cap on its face.
  3. Counter-interpretation: a choice-of-law clause selecting an enforcing state may be applied, unless the employee's home state has a statute overriding it (California §16600.5 is the clearest example).
  4. Symmetry: N/A.
- [T2] Federal status
  1. Rule: the FTC Non-Compete Clause Rule (2024) was set aside nationwide in *Ryan LLC v. FTC* (N.D. Tex., Aug. 2024); the FTC later dropped its appeal and pursues case-by-case enforcement.
  2. Application: no federal ban protects the employee; federal law does not decide this dispute.
  3. Counter-interpretation: none material.
- [T3] Duration: "5 years after leaving"
  1. Rule (common-law regimes): restriction must be no longer than needed to protect a legitimate interest; courts most often sustain 6 to 24 months for employees; multi-year terms are typically reserved for sale-of-business covenants.
  2. Application: 5 years is 2.5x to 10x the commonly sustained range.
  3. Counter-interpretation: an employer could argue long customer cycles or long-lived trade secrets justify a longer term; this is rarely accepted for 5 years absent a business sale.
  4. Symmetry: one-sided; no stated garden-leave pay or consideration during the restricted period (`NOT ADDRESSED IN [P1]`).
- [T4] Geography: "200-mile radius"
  1. Rule: radius must correspond to the area where the employer does business and the employee worked or had customer contact.
  2. Application: `NOT ADDRESSED IN [P1]: employer's market footprint and employee's territory.` The new job at 150 miles is inside the radius.
  3. Counter-interpretation: for a regional business, 200 miles may be defensible; for a remote-capable role, radius restrictions are increasingly treated as arbitrary.
- [T5] Activity scope: "any related industry"
  1. Rule: restriction must be tied to the employee's role and actual competition, not adjacent fields.
  2. Application: "related industry" is undefined and broader than "competitor"; it is the most likely term to be found overbroad or vague.
  3. Counter-interpretation: the employee joined a *competitor*, which falls within even the narrowest reading of the clause, so vagueness at the margins may not help on these facts.
- [T6] Legitimate business interest
  1. Rule: protection of trade secrets, confidential information, or customer goodwill; restraint of ordinary competition alone is insufficient.
  2. Application: `NOT ADDRESSED IN [P1]: employee role and access.` A senior or client-facing employee with confidential information supports enforcement of some restraint; a junior employee without such access weakens it.
- [T7] Formation and consideration
  1. Rule: varies; some states require fresh consideration for mid-employment covenants (for example Pennsylvania); Texas requires the covenant be ancillary to an otherwise enforceable agreement; several statutory states impose advance-notice requirements.
  2. Application: `NOT ADDRESSED IN [P1]: signing date and consideration.` If signed mid-employment with no new benefit, formation is challengeable in several states.
- [T8] Remedy for overbreadth
  1. Rule: three approaches. Reformation (Texas Bus. & Com. Code §15.51(c) requires it; many states permit it); strict blue pencil (strike severable words only); all-or-nothing (Wisconsin Stat. §103.465 voids an unreasonable covenant entirely; Virginia courts generally decline to rewrite).
  2. Application: in all-or-nothing regimes, [T3] and [T5] likely defeat the covenant. In reformation regimes, a court would likely cut it to 1 to 2 years, a narrower radius, and direct competitors only.
  3. Counter-interpretation: some courts refuse to reform covenants drafted in bad faith or grossly overbroad, treating overreach as a reason to void.
- [T9] Application to stated breach (the decisive trace)
  1. Facts: month 8; 150 miles; competitor ([P1]).
  2. Under a reformed covenant of 12 to 24 months with a radius covering 150 miles and limited to competitors, the conduct at month 8 **still falls inside** the restriction.
  3. Under a reformed 6-month covenant, the conduct falls outside it.
  4. Result: overbreadth alone does not protect the employee in reformation regimes; the outcome turns on [T1], [T6], and the reformed duration.
- [T10] Obligations independent of the covenant
  1. Rule: trade secret law (Defend Trade Secrets Act and state UTSA statutes) and any separate confidentiality or non-solicitation clauses apply regardless of non-compete enforceability.
  2. Application: `NOT ADDRESSED IN [P1]: other restrictive clauses; whether any materials were retained.` Misappropriation exposure exists independently of [T3]-[T9].
- [T11] Litigation posture
  1. Rule: to stop the employee from working, the employer typically needs a preliminary injunction (likelihood of success, irreparable harm).
  2. Application: a facially overbroad covenant ([T3], [T5]) weakens likelihood of success; the 8-month delay since departure ([P1]) may undercut claimed urgency, depending on when the employer learned of the new job (`NOT ADDRESSED IN [P1]`).

#### FORMAL CONCLUSION
- **Issue synthesis:**
  1. In void regimes, the covenant is unenforceable ([T1]).
  2. In statutory-cap regimes, the 5-year term violates the cap on its face ([T1]).
  3. In common-law regimes, duration ([T3]) and scope ([T5]) are very likely unreasonable as written; geography ([T4]) depends on market facts.
  4. Whether the employee is exposed turns on the remedy ([T8]): all-or-nothing regimes likely void it; reformation regimes could produce a narrowed covenant the employee still breaches at month 8 ([T9]).
- **Structural asymmetries and exposure points:** one-sided restraint with no stated consideration during the restricted period ([T3], [T7]); employee exposure persists through trade secret and other clauses regardless of outcome ([T10]).
- **Unresolved questions:** governing law ([T1]); role and access ([T6]); signing date and consideration ([T7]); employer footprint ([T4]); other clauses and retained materials ([T10]); date employer learned of the new job ([T11]).

#### REMEDIATION / NEXT ACTION
**Redline: a covenant drafted within commonly sustained bounds** (useful as a settlement or narrowing proposal):

> ~~For a period of five (5) years after leaving the Company, Employee shall not work in any related industry within a 200-mile radius.~~
> For twelve (12) months following the Separation Date, Employee shall not perform services for a Competitor that are the same as or substantially similar to the services Employee performed for the Company during the final twenty-four (24) months of employment, within the geographic territory in which Employee had material responsibilities during that period. "Competitor" means [named companies or a defined product category]. During the restricted period the Company shall pay Employee [X]% of base salary. This covenant is unenforceable to the extent prohibited by the law of the state where Employee primarily resides and works.

**Fact-gathering steps (resolve every NOT ADDRESSED item):**
1. Obtain the full signed agreement; locate governing-law, forum, severability, and tolling clauses ([T1], [T8]).
2. Confirm state of residence and work location, at signing and at departure ([T1]).
3. Record signing date and what was received in exchange ([T7]).
4. Compare old and new job descriptions, customers, and products ([T5], [T6], [T9]).
5. Inventory any company materials, files, or credentials still held, and return them in writing ([T10]).
6. Identify when the former employer learned of the new role ([T11]).
7. Notify the new employer and ask whether it provides legal defense or indemnity; engage employment counsel licensed in the governing state to assess a response letter or declaratory-judgment action.

DISCLAIMER: This output is analytical support, not legal advice. Consult qualified legal counsel for binding determinations.

**Traceability self-check:** every conclusion item cites [T1]-[T11]; each trace cites [P1] facts or [P2] regimes.

### EVALUATION: TEST 4

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 4        | 5         | +1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 21/25    | 24/25     | +3    |

Baseline Words: 687 | Optimized Words: 1354 | Overhead Ratio: 1.97x | Prompt Words: 403

Both responses reached the same conclusion and both identified the key "reformation could still catch month 8" risk. The certificate added statutory citations for each regime, an explicit litigation-posture trace (injunction standard and the effect of the 8-month delay), and per-fact conditional outcomes via `NOT ADDRESSED IN [P1]`, which is the largest traceability gain so far. The template's mandatory "redline clause revisions" is a partial mismatch for an already-signed contract dispute; I reframed it as a narrowing proposal, but a less careful model would produce an irrelevant redline, which is noted in Section 8.

---

## TEST 5: Research Synthesis (Mixed | Mode 1 Max | Template 3 Research Synthesis)

### BASELINE RESPONSE

**Short answer:** the research does not support a single answer. Remote work tends to *raise* productivity for focused, individually measurable work done by people who chose it, tends to *lower* it where work depends on supervision, training, or spontaneous collaboration, and **hybrid arrangements look roughly productivity-neutral while sharply improving retention**. How productivity is measured (self-reports vs. objective output, output per day vs. per hour) explains a lot of the apparent disagreement.

**Evidence that remote work helps**
- **Ctrip call center RCT (Bloom, Liang, Roberts & Ying, 2015, *QJE*):** randomly assigned home workers were about 13% more productive (more minutes worked and more calls per minute), and attrition roughly halved. A caveat: promotion rates conditional on performance fell for home workers.
- **USPTO patent examiners (Choudhury, Foroughi & Larson, 2021, *Strategic Management Journal*):** moving from work-from-home to work-from-anywhere raised output about 4.4% without hurting quality.
- **Worker surveys (Barrero, Bloom & Davis):** remote workers save roughly an hour or more of commuting per day and report being as or more productive at home; part of the saved time goes back into work.

**Evidence that remote work hurts**
- **Indian data-entry RCT (Atkin, Schoar & Shinde, 2023):** workers randomized to home were about 18% less productive than office workers, with much of the gap appearing immediately.
- **Asian IT services firm during the pandemic (Gibbs, Mengel & Siemroth, 2023):** hours worked rose substantially, output stayed roughly flat, so productivity per hour fell (estimates in the 8-19% range). Coordination and meeting costs rose.
- **U.S. call center (Emanuel & Harrington):** going remote lowered productivity modestly, and less productive workers disproportionately selected into remote jobs.

**Evidence on collaboration, learning, and innovation**
- **Microsoft (Yang et al., 2022, *Nature Human Behaviour*):** firm-wide remote work made collaboration networks more siloed and static, with fewer cross-team ties and more asynchronous communication.
- **Software engineers (Emanuel, Harrington & Pallais, 2023):** sitting near teammates increased feedback and mentoring, especially for junior engineers, at some cost to senior engineers' own output.

**Hybrid**
- **Trip.com hybrid RCT (Bloom, Han & Liang, 2024, *Nature*):** two remote days per week produced no detectable difference in performance reviews or promotions over two years, while quit rates fell by about a third.

**Why studies disagree**
1. **Fully remote vs. hybrid:** hybrid results are consistently better than fully remote results.
2. **Task type:** routine, individually measured tasks (calls, patent reviews) versus collaborative or learning-intensive work.
3. **Selection:** volunteers who chose remote work often do better; forced or randomized remote work less so.
4. **Measurement:** self-reports tend to be more positive than objective output; output per day can rise while output per hour falls.
5. **Context:** pandemic-era studies mixed remote work with school closures and disruption.

**Bottom line:** if you're making a decision, the evidence favors hybrid for most knowledge work, fully remote for well-defined individual work with good measurement, and more in-person time for early-career staff and work that depends on mentoring or tight collaboration.

### OPTIMIZED PROMPT

**Task classification:** The protocol labels this Mixed; Template 3 specifies persona OMIT for factual synthesis (`[PRISM]`). I followed the template and omitted the persona. **Mode 1 Max Certificate**, Template 3 (Research Synthesis). Expected overhead ~2.2x.
**Diagnosis:** No corpus is provided, so the model must recall sources; the raw prompt has no rule for distinguishing recalled figures from verified ones (hallucination risk). "Balanced" is a tone request rather than a method; it is replaced with an explicit contradicting-evidence and reconciliation step. No goal leakage.

```
Peer-reviewed systematic synthesis methodology requires completing the
following structured certificate before presenting any cross-source findings.

### PREMISES
- [P1] Sources examined: list each study you rely on with author, year, venue,
  and design. No corpus is supplied; sources come from recall. Label every
  quantitative figure RECALLED (verify before citing) unless you can state it
  with high confidence.
- [P2] Research question: What is the measured effect of remote work (fully
  remote and hybrid) on worker productivity, and what moderates it?
- [P3] Methodological scope: randomized and quasi-experimental field studies
  first; large observational and survey studies second; productivity measured
  as output, output per hour, quality, and downstream outcomes (promotion,
  retention, innovation, collaboration).
- [P4] Corpus limitations: recall-based, English-language, weighted toward
  economics and management journals; state other gaps you identify.

### EVIDENCE TRACES
For each cross-source claim:
- [T1] Claim [statement]:
  1. Primary evidence: which P1 sources, with exact metrics
  2. Study design: sample, setting, identification strategy
  3. Effect magnitude: reported effects
  4. Contradicting evidence: P1 sources that diverge, and on what variable
  5. Reconciliation: moderator that explains divergence, or UNRESOLVED

Grounding rule: Report findings as measured in [P1]. Treat absence of
contradicting studies in [P1] as `UNEXAMINED IN CORPUS` rather than proof of
consensus.

### FORMAL CONCLUSION
- Integrated synthesis: core findings citing T-identifiers
- Convergent vs. contested claims: grouped by T-identifiers
- Open research gaps: questions unresolved by P1

### REMEDIATION / NEXT ACTION
Provide a structured summary table mapping work context to the expected
direction of effect, derived from convergent [T] traces, and the exact
follow-up queries needed to verify RECALLED figures.

TRACEABILITY SELF-CHECK: Verify that every claim in the synthesis cites at
least one [T] identifier and its underlying [P] source.
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] Sources (recall-based; figures marked RECALLED should be verified):
  - S1 Bloom, Liang, Roberts & Ying (2015), *QJE*: RCT, Ctrip call center, ~250 volunteers.
  - S2 Choudhury, Foroughi & Larson (2021), *Strategic Management Journal*: natural experiment, USPTO examiners.
  - S3 Atkin, Schoar & Shinde (2023), NBER working paper: RCT, data-entry workers, India.
  - S4 Gibbs, Mengel & Siemroth (2023), *Journal of Political Economy Microeconomics*: pandemic panel, >10,000 IT professionals, Asian IT services firm.
  - S5 Emanuel & Harrington (2023/2024), working paper / journal: Fortune 500 call center, pre/post remote shift plus hiring.
  - S6 Emanuel, Harrington & Pallais (2023), NBER working paper: software engineers, co-location natural experiment.
  - S7 Yang et al. (2022), *Nature Human Behaviour*: Microsoft, ~61,000 employees, network data.
  - S8 Bloom, Han & Liang (2024), *Nature*: RCT, Trip.com, 1,612 employees, hybrid (2 days/week home).
  - S9 Barrero, Bloom & Davis (2021 onward), Survey of Working Arrangements and Attitudes: large U.S. panel survey.
- [P2] Question: measured effect of fully remote and hybrid work on productivity, and its moderators.
- [P3] Scope: field experiments and quasi-experiments prioritized; surveys used only for perceived productivity and time use.
- [P4] Limitations: recall-based; skewed to economics; most experiments cover call centers, data entry, and software, so creative and managerial work is underrepresented; pandemic-era studies are confounded by school closures and health shocks.

#### EVIDENCE TRACES
- [T1] Claim: Fully remote work can raise output for routine, individually measured tasks.
  1. Evidence: S1 performance +13% (RECALLED: about 9 points from more minutes worked, 4 from more calls per minute); S2 output +4.4% moving from WFH to work-from-anywhere.
  2. Design: S1 RCT among volunteers; S2 natural experiment.
  3. Magnitude: +4% to +13%.
  4. Contradicting: S3 found home workers about 18% less productive (RECALLED) in a comparable routine task; S5 found a modest productivity decline (RECALLED, about 4%) after a call center went remote.
  5. Reconciliation: S1 and S2 participants opted in; S3 randomized workers who had not necessarily chosen remote work; S5 adds negative selection into remote jobs. **Selection and setting** reconcile direction, but magnitudes remain UNRESOLVED.
- [T2] Claim: Remote work can raise hours while lowering output per hour.
  1. Evidence: S4 hours up substantially (RECALLED: about 30%, including after-hours work), output roughly flat, productivity per hour down (RECALLED: 8% to 19%).
  2. Design: within-firm panel across the pandemic shift.
  3. Contradicting: S9 respondents report higher productivity at home (perceived, not measured).
  4. Reconciliation: **measurement unit**: per-day output can hold or rise while per-hour output falls; self-reports do not capture per-hour efficiency.
- [T3] Claim: Hybrid arrangements are roughly productivity-neutral and improve retention.
  1. Evidence: S8 no detectable difference in performance reviews or promotions over two years; quit rate down about one-third (RECALLED).
  2. Design: RCT, 1,612 employees, two home days per week.
  3. Contradicting: `UNEXAMINED IN CORPUS`: no other hybrid RCT of comparable size in [P1].
  4. Reconciliation: single strong study; convergent with the direction of S1 attrition results.
- [T4] Claim: Remote work reduces collaboration breadth and informal learning.
  1. Evidence: S7 networks became more siloed and static, fewer bridging ties, more asynchronous communication; S6 co-location increased feedback and mentoring for junior engineers (RECALLED: about 22% more online feedback), at some cost to senior engineers' output.
  2. Design: S7 large observational network study with pandemic shock; S6 natural experiment on seating.
  3. Contradicting: `UNEXAMINED IN CORPUS`: no study in [P1] shows remote work increasing cross-team ties.
  4. Reconciliation: convergent; effect concentrated on junior staff and cross-group innovation, which short-run output metrics miss.
- [T5] Claim: Remote work has career-progression costs.
  1. Evidence: S1 lower promotion rate conditional on performance; S6 less mentoring for juniors.
  2. Contradicting: S8 found no promotion penalty under hybrid.
  3. Reconciliation: **intensity**: penalties appear in fully remote arrangements, not in two-day hybrid.
- [T6] Claim: Remote work saves commuting time, part of which returns to work.
  1. Evidence: S9 average daily commute savings of roughly an hour (RECALLED), a substantial share reinvested in primary-job work (RECALLED: about 40%).
  2. Design: survey self-reports.
  3. Contradicting: none in [P1]; magnitude depends on self-report accuracy.

#### FORMAL CONCLUSION
- **Integrated synthesis:** The sign of the remote-work productivity effect is conditional, not universal. Fully remote work has produced gains of 4% to 13% for opt-in workers on routine individual tasks ([T1]) and losses of roughly 4% to 19% in other settings, especially when workers did not choose remote work or when productivity is measured per hour ([T1], [T2]). Two-day hybrid work shows no measurable performance cost and a large retention benefit ([T3]). Collaboration breadth and junior mentoring decline under remote work ([T4]), with career penalties in fully remote but not hybrid arrangements ([T5]).
- **Convergent claims:** hybrid neutrality with retention gains ([T3]); reduced collaboration breadth and mentoring ([T4]); commute savings ([T6]).
- **Contested claims:** direction of fully remote effects on output ([T1]); per-day vs. per-hour productivity ([T2]).
- **Moderators identified:** selection (opt-in vs. assigned) ([T1]); measurement unit ([T2]); intensity, fully remote vs. hybrid ([T3], [T5]); task interdependence and seniority ([T4]).
- **Open research gaps:** long-run innovation outcomes; managerial and creative roles; hybrid RCTs outside one firm ([T3]); post-pandemic steady-state effects ([P4]).

#### REMEDIATION / NEXT ACTION
**Evidence-derived summary table**

| Work context | Expected productivity direction | Strongest supporting traces | Confidence |
|---|---|---|---|
| Routine, individually measured, opt-in | Neutral to positive | [T1] S1, S2 | Medium |
| Routine, assigned (not chosen) | Negative | [T1] S3, S5 | Medium |
| Knowledge work, hybrid 1-2 days home | Neutral output, better retention | [T3] S8 | Medium (single RCT) |
| Collaborative or innovation-heavy, fully remote | Negative on collaboration breadth | [T4] S6, S7 | Medium |
| Early-career staff, fully remote | Negative on mentoring and progression | [T4], [T5] | Medium |
| Measured per hour vs. per day | Per-hour can fall while per-day holds | [T2] S4 | Medium |

**Verification queries for RECALLED figures:**
1. `"Does Working from Home Work? Evidence from a Chinese Experiment" Bloom Liang Roberts Ying QJE 2015` (S1 +13%, attrition).
2. `Atkin Schoar Shinde "Working from Home, Worker Sorting and Development" NBER` (S3 -18%).
3. `Gibbs Mengel Siemroth "Work from Home and Productivity: Evidence from Personnel and Analytics Data on IT Professionals"` (S4 hours and per-hour figures).
4. `Emanuel Harrington "Working Remotely? Selection, Treatment, and the Market for Remote Work"` (S5 magnitude).
5. `Bloom Han Liang "Hybrid working from home improves retention without damaging performance" Nature 2024` (S8 quit-rate figure).

**Traceability self-check:** every synthesis claim cites [T1]-[T6], and every trace cites sources in [P1].

### EVALUATION: TEST 5

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4        | 4         | 0     |
| Completeness  | 4        | 5         | +1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 3        | 4         | +1    |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 20/25    | 22/25     | +2    |

Baseline Words: 489 | Optimized Words: 1091 | Overhead Ratio: 2.23x | Prompt Words: 368

Both responses draw on the same nine studies and the same recalled figures, so Accuracy is equal; neither is independently verified here, and I hold both at 4 because a few magnitudes (S5, S6) are from memory. The optimized version's real gains are epistemic hygiene (RECALLED labels, `UNEXAMINED IN CORPUS` where only one study supports a claim) and a context-to-direction table with verification queries. The baseline's "why studies disagree" section already did most of the reconciliation work in a more readable form.

---

## TEST 6: Business Decision (Mixed | Mode 1 Max | Template 5 Decision-Making)

### BASELINE RESPONSE

**Recommendation: don't build your own authentication. Use a managed identity provider that will sign a Business Associate Agreement (BAA) with you, and keep PHI out of the identity system.**

**Why not build**
- Authentication is a security-critical, never-finished system: password hashing (Argon2id or bcrypt), MFA (TOTP, WebAuthn/passkeys), session and token management, account recovery flows that resist takeover, brute-force and credential-stuffing protection, breached-password checks, audit logging, and ongoing patching. Getting any of these wrong in a healthcare product is a breach, and a breach of PHI means HHS notification obligations, possible penalties, and lost customer trust.
- Your healthcare customers will soon ask for SAML/OIDC single sign-on, SCIM provisioning, and audit trails. That's months of work for a 15-person team, plus permanent maintenance (realistically a meaningful fraction of an engineer forever).
- You will be asked about authentication in every security questionnaire and SOC 2 / HIPAA audit. A vendor with existing SOC 2 Type II and HIPAA attestations makes that much easier.

**The HIPAA catch: you need a BAA**
- If the auth provider stores data that can identify your users *in a healthcare context* (for example, a patient's email in your patient portal), that is likely PHI, which makes the vendor your subcontractor business associate. You need a signed BAA before going live.
- **Auth0 (Okta)** offers BAAs, but typically only on enterprise plans, which can be expensive for a startup.
- **Clerk**: check its current HIPAA/BAA offering and which plan it requires; get the answer in writing.
- Other options with BAAs: **AWS Cognito** (covered under the AWS BAA if you're on AWS, and much cheaper), Google Cloud Identity Platform, Microsoft Entra External ID, and vendors such as Stytch, WorkOS, or Descope (verify each).
- A **self-hosted open-source IdP** (Keycloak, Ory, Zitadel) is a middle path: no third-party BAA needed because you host it, but you take on operating and patching it.

**How to set it up well**
1. Store the minimum in the IdP: email, name if needed, and an internal user ID. Keep all clinical data in your own HIPAA-controlled database, keyed by your own user ID.
2. Require MFA, especially for clinicians and admins. HIPAA's Security Rule requires unique user IDs, audit controls, and person or entity authentication, and expects automatic logoff and encryption to be addressed; HHS has also proposed making MFA explicitly required.
3. Configure session timeouts and automatic logoff appropriate for shared clinical workstations.
4. Stream auth logs (logins, failures, MFA changes, admin actions) to your logging system and retain them.
5. Keep your own internal user ID as the primary key so you can migrate providers later. Confirm the vendor will export password hashes on request.

**When building might make sense:** almost never at your size. Only if no vendor meets a hard requirement (for example, an air-gapped deployment) and you have dedicated security engineering capacity.

**Bottom line:** pick the vendor that (1) will sign a BAA on a plan you can afford, (2) supports the SSO features your customers will ask for, and (3) fits your cloud. If you're on AWS and price-sensitive, Cognito is the cheapest compliant option; if you want the best developer experience and enterprise SSO features, budget for Auth0 Enterprise or a comparable vendor with a BAA.

### OPTIMIZED PROMPT

**Task classification:** Mixed (technical analysis with a recommendation). Minimal persona, 5 words or fewer (`[PRISM]`). **Mode 1 Max Certificate**, Template 5 (Decision-Making / Recommendation). Expected overhead ~2.2x.
**Diagnosis:** binary framing ("build or Auth0/Clerk") hides two viable alternatives (cloud-provider identity under an existing BAA, self-hosted open-source IdP); no criteria are stated, so the answer would rest on general preference (guesswork gap); HIPAA is named but its concrete obligations are not; no execution checklist is requested. No goal leakage.

```
You are a decision analyst.

The standard decision analysis framework requires completing this certificate
before recommending any course of action.

### PREMISES
- [P1] Decision statement: how a 15-person SaaS company that processes
  HIPAA-regulated health data should implement end-user authentication.
- [P2] Candidate options: (O1) build in-house; (O2) managed identity vendor
  (Auth0, Clerk, or equivalent); (O3) cloud-provider identity service covered
  by an existing cloud BAA; (O4) self-hosted open-source identity provider.
- [P3] Evaluation criteria, in order: (C1) HIPAA obligations, including BAA
  availability and Security Rule technical safeguards; (C2) security risk
  surface; (C3) engineering effort to launch and to maintain; (C4) enterprise
  features commonly required by healthcare customers (SAML/OIDC SSO, SCIM,
  audit logs); (C5) cost trajectory; (C6) reversibility.
- [P4] Hard constraints: 15 total staff; PHI in scope; a signed BAA is
  required for any third party that creates, receives, maintains, or
  transmits PHI on the company's behalf.

### OPTION TRACES
For each option in [P2]:
- [T1] Option [name]:
  1. Criteria evaluation: evidence against C1-C6
  2. Constraint check: whether P4 is satisfied or breached
  3. Failure modes: primary risks and triggers
  4. Dependencies: preconditions for success
  5. Reversibility: cost to migrate away later

Grounding rule: Evaluate every option against the same C1-C6 list. When a
vendor fact (BAA availability, plan tier, price) cannot be stated with
confidence, record `UNABLE TO TRACE: [fact]` and list the verification step.

### FORMAL CONCLUSION
- Primary selection: option citing T-identifiers and criteria
- Conditional alternative: runner-up and the exact condition under which it wins
- Explicit tradeoffs accepted: what the primary selection sacrifices

### REMEDIATION / NEXT ACTION
Provide a concrete, step-by-step execution checklist to implement the primary
selection.

TRACEABILITY SELF-CHECK: Verify that every comparative claim in the conclusion
cites the corresponding [T] option traces.
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] Decision: authentication implementation for a 15-person SaaS with PHI.
- [P2] Options: O1 build; O2 managed vendor; O3 cloud-provider identity; O4 self-hosted open source.
- [P3] Criteria C1-C6 as ordered.
- [P4] Constraints: 15 staff; PHI in scope; BAA required for any third party handling PHI.

Supporting rule detail for C1 (45 CFR 164.312): unique user identification (required); emergency access procedure (required); automatic logoff (addressable); encryption and decryption (addressable); audit controls (required); person or entity authentication (required). HHS's January 2025 proposed Security Rule update would make MFA and encryption explicitly required (`UNABLE TO TRACE: final rule status as of evaluation date`).

PHI applicability: identity records (email, name) tied to a health service can be individually identifiable health information, so an IdP holding them should be treated as a business associate.

#### OPTION TRACES
- [T1] O1 Build in-house
  1. C1: no third-party BAA needed, but every 164.312 safeguard is the company's to implement and evidence. C2: largest attack surface (hashing, MFA, recovery, sessions, credential stuffing, token handling). C3: highest; launch plus permanent maintenance, a recurring share of a security-competent engineer. C4: SSO and SCIM must be built separately. C5: low cash, high payroll. C6: high reversibility in principle; migrating off a homegrown system later is still a project.
  2. Constraints: satisfies the BAA rule; strains the 15-person headcount ([P4]).
  3. Failure modes: account-takeover flaw in recovery flow; weak MFA; missing audit trail found in a customer security review.
  4. Dependencies: in-house security expertise and penetration testing.
- [T2] O2 Managed identity vendor (Auth0, Clerk, or equivalent)
  1. C1: compliant only if the vendor signs a BAA on the purchased plan. Auth0 (Okta) offers BAAs on enterprise-tier plans (`UNABLE TO TRACE: current plan and price`). Clerk: `UNABLE TO TRACE: current BAA availability and required plan`. C2: smallest owned surface; vendor carries hashing, MFA, anomaly detection. C3: days to weeks to launch, low maintenance. C4: strongest; SAML/OIDC SSO, SCIM, logs often built in (often gated to higher tiers). C5: enterprise tiers with BAAs can cost substantially more than self-serve plans; cost grows with monthly active users. C6: moderate; requires password-hash export and an internal user ID as primary key.
  2. Constraints: satisfies [P4] only with a signed BAA.
  3. Failure modes: BAA unavailable on affordable tier; price escalation at scale; vendor outage blocks logins.
  4. Dependencies: BAA executed before PHI-linked identities are stored.
- [T3] O3 Cloud-provider identity (AWS Cognito, Google Cloud Identity Platform, Microsoft Entra External ID)
  1. C1: covered under the cloud provider's existing BAA if the service is on the provider's HIPAA-eligible list (Cognito is on AWS's list; verify the others against current lists). C2: small owned surface; configuration errors are the main risk. C3: low to moderate; developer experience and customization are weaker than O2. C4: SAML/OIDC federation available; SCIM and admin UX more limited. C5: lowest per-user cost of the managed options. C6: moderate; same export considerations as O2.
  2. Constraints: satisfies [P4] with no new vendor relationship if already on that cloud.
  3. Failure modes: misconfiguration (token lifetimes, MFA enforcement); more custom UI work.
  4. Dependencies: existing BAA with the cloud provider; same cloud as the application.
- [T4] O4 Self-hosted open source (Keycloak, Ory, Zitadel)
  1. C1: no IdP vendor BAA (hosted in the company's own HIPAA environment); safeguards are configuration plus operations. C2: moderate; mature code, but patching and hardening are owned. C3: moderate launch, ongoing operations (upgrades, HA, backups). C4: strong (SSO, federation, often SCIM via extensions). C5: infrastructure plus operations time. C6: high; data stays in company infrastructure.
  2. Constraints: satisfies the BAA rule; operational load is significant for 15 staff.
  3. Failure modes: delayed security patches; availability incidents on a self-run auth tier.
  4. Dependencies: someone owning operations and upgrades.

**Option matrix** (relative ranking, 1 = best):

| Criterion | O1 Build | O2 Vendor | O3 Cloud IdP | O4 Self-host |
|---|---|---|---|---|
| C1 HIPAA obligations | 4 | 2 (if BAA) | 1 | 3 |
| C2 Security surface | 4 | 1 | 2 | 3 |
| C3 Engineering effort | 4 | 1 | 2 | 3 |
| C4 Enterprise features | 4 | 1 | 3 | 2 |
| C5 Cost trajectory | 3 | 4 | 1 | 2 |
| C6 Reversibility | 1 | 3 | 3 | 1 |

#### FORMAL CONCLUSION
- **Primary selection: buy, specifically O2 (managed vendor) with a signed BAA**, because it ranks first on C2-C4 ([T2]) and satisfies [P4] once the BAA is executed. O1 is dominated on C1-C4 at this headcount ([T1]).
- **Conditional alternative: O3 (cloud-provider identity)** wins when either (a) no shortlisted vendor will sign a BAA on an affordable plan ([T2] failure mode), or (b) the application already runs on that cloud and C5 cost outweighs C4 developer experience ([T3]).
- **Second alternative: O4** only when data-residency or air-gap requirements rule out third-party identity and someone can own IdP operations ([T4]).
- **Tradeoffs accepted with O2:** higher and rising subscription cost (C5) and moderate lock-in (C6) ([T2]), mitigated by the reversibility steps below.

#### REMEDIATION / NEXT ACTION
1. **BAA gate (week 1):** email each shortlisted vendor (Auth0, Clerk, one cloud IdP): "Will you sign a BAA, on which plan, at what price for N MAU?" Disqualify any vendor without a written yes ([T2], [T3]).
2. **Data minimization:** store only email, display name, and the company's internal `user_id` in the IdP; all PHI lives in the application database keyed by `user_id` ([P4]).
3. **Safeguard configuration mapped to 164.312:**
   - Unique user identification: one account per human; no shared logins.
   - Person or entity authentication: enforce MFA for all users; require phishing-resistant MFA (WebAuthn) for admins and clinicians.
   - Automatic logoff: idle session timeout and short-lived access tokens with rotating refresh tokens.
   - Audit controls: stream IdP events (login, failure, MFA change, admin action) to the logging system with a defined retention period.
   - Emergency access: documented break-glass admin account, stored offline, alerting on use.
4. **Reversibility (C6):** confirm in the contract that password hashes and MFA enrollment metadata are exportable; never use the vendor's user ID as a foreign key.
5. **Evidence:** record the BAA, configuration screenshots, and log retention settings in the HIPAA risk analysis and SOC 2 evidence folder.

**Traceability self-check:** every comparative claim cites [T1]-[T4]; unverifiable vendor facts are marked UNABLE TO TRACE.

### EVALUATION: TEST 6

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 4        | 5         | +1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 21/25    | 24/25     | +3    |

Baseline Words: 541 | Optimized Words: 1062 | Overhead Ratio: 1.96x | Prompt Words: 370

Both versions recommend buying and both surface the BAA requirement and the cloud-IdP and self-host alternatives. The optimized version made the decision auditable (same six criteria applied to all four options, a ranking matrix, an explicit condition under which the runner-up wins) and mapped each configuration step to a specific 164.312 safeguard. The baseline was more readable and already contained most of the substance, so Structure favors it; the large Traceability gap is real because the baseline's comparison was implicit.

---

## TEST 7: Compliance Check (Accuracy | Mode 1 Max | Template 4 Compliance / Regulatory Check)

### BASELINE RESPONSE

**Verdict: not compliant.** Two of the five rules directly conflict with NIST SP 800-63B, one is compliant only in limited circumstances, one is permitted but discouraged in practice, and the policy omits several requirements.

Note on versions: SP 800-63B Revision 3 (2017) used "SHOULD NOT" for composition rules and forced expiration. Revision 4 (finalized in 2025) upgraded both to "SHALL NOT" and raised the minimum length for passwords used as a single factor. The assessment below covers both.

| Policy rule | NIST 800-63B | Status |
|---|---|---|
| Minimum 8 characters | Rev 3: minimum 8. Rev 4: minimum 15 when the password is the only factor; minimum 8 only when used as part of MFA | **Compliant only with MFA** (under Rev 4) |
| Uppercase + lowercase + number + special | Rev 3: SHOULD NOT impose composition rules. Rev 4: SHALL NOT | **Non-compliant** |
| Expire every 90 days | Rev 3: SHOULD NOT require periodic changes. Rev 4: SHALL NOT. Force a change only on evidence of compromise | **Non-compliant** |
| Cannot reuse last 5 | Not required or prohibited | **Permitted** (low value once expiration is removed) |
| Lock after 3 failures for 30 minutes | Must limit consecutive failures to no more than 100; recommends methods that avoid locking out legitimate users | **Technically compliant, but not recommended** |

**Why the conflicts matter**
- **Composition rules** push users toward predictable patterns (`Password1!`) without meaningfully increasing strength. NIST favors length and blocklist screening instead.
- **Forced expiration** leads to incremental changes (`Summer2024!` -> `Fall2024!`) that attackers anticipate.
- **Lockout after 3 attempts** makes it easy for an attacker (or a typo-prone user) to lock accounts out, creating a denial-of-service vector and help-desk load. NIST allows up to 100 consecutive failures and suggests throttling, CAPTCHAs, increasing delays, or risk-based checks.

**Missing requirements**
- **Blocklist check (SHALL):** compare new passwords against known-breached, dictionary, repetitive or sequential (`aaaaaa`, `1234abcd`), and context-specific words (service name, username).
- **Allow long passwords:** permit at least 64 characters, accept spaces and all printable characters (and Unicode), and do not truncate.
- **Storage (SHALL):** salt and hash with an approved, memory-hard or iterated key derivation function.
- **No hints or knowledge-based security questions.**
- **Allow paste and password managers.**
- **Force a change on evidence of compromise.**
- **MFA:** to keep an 8-character minimum under Rev 4, passwords must be part of multi-factor authentication.

**Revised policy**
- Minimum 15 characters (or 8 if the account requires MFA); allow at least 64.
- Accept all printable ASCII, spaces, and Unicode. No composition rules.
- Screen new passwords against a breached-password and dictionary blocklist; explain the rejection to the user.
- No periodic expiration; require a change when compromise is suspected.
- Rate-limit failed attempts (for example, exponential back-off and CAPTCHA after 5 failures, temporary lock after 100 at most).
- Allow paste and password managers; offer a "show password" option.
- No hints or security questions.
- Store passwords salted and hashed with Argon2id, scrypt, bcrypt, or PBKDF2 with appropriate parameters.
- Require MFA for privileged and remote access.

### OPTIMIZED PROMPT

**Task classification:** Accuracy-dependent (compliance determination). Persona omitted (`[PRISM]`). **Mode 1 Max Certificate**, Template 4 (Compliance / Regulatory Check). Expected overhead ~2.2x.
**Diagnosis:** the raw prompt does not specify the revision of 800-63B (Rev 3 and Rev 4 differ on SHOULD vs. SHALL), does not ask about requirements the policy omits (the usual source of non-compliance), and has no disposition vocabulary or remediation artifact. No goal leakage.

```
Regulatory audit methodology requires completing this verification certificate
before issuing any compliance disposition.

### PREMISES
- [P1] Artifact under review: a password policy with five rules:
  R1 minimum 8 characters; R2 must include uppercase, lowercase, number, and
  special character; R3 expires every 90 days; R4 cannot reuse last 5
  passwords; R5 account locks after 3 failed attempts for 30 minutes.
- [P2] Applicable clauses: NIST SP 800-63B memorized secret / password verifier
  requirements and authentication throttling requirements, in both Revision 3
  (2017) and Revision 4 (2025). Distinguish SHALL from SHOULD.
- [P3] Boundary scope: policy text only. Implementation (hashing, storage,
  blocklist service, MFA enforcement) is out of the provided evidence.
- [P4] Audit evidence provided: the policy text in [P1] only.

### COMPLIANCE TRACES
For each rule in [P1], and for each [P2] requirement that the policy does not
address:
- [T1] Clause [ID/section]:
  1. Normative requirement: exact requirement and its SHALL/SHOULD strength
  2. Artifact examined: the rule in P1, or "absent"
  3. Disposition: COMPLIANT / NON-COMPLIANT / PARTIAL / NOT ADDRESSED /
     UNABLE TO VERIFY
  4. Substantive match: how the rule's mechanism satisfies or fails P2
  5. Deficit specification: exact missing control if not COMPLIANT

Grounding rule: Assign COMPLIANT only when [P4] contains a rule whose mechanism
matches the clause. When a requirement concerns implementation outside [P3],
assign UNABLE TO VERIFY and name the evidence needed.

### FORMAL CONCLUSION
- Disposition summary: overall status across all traced clauses
- Non-compliant and unverified items: list with clause IDs and T-identifiers
- Severity ranking: ordered by security exposure grounded in T-traces

### REMEDIATION / NEXT ACTION
For every NON-COMPLIANT, PARTIAL, NOT ADDRESSED, or UNABLE TO VERIFY trace,
provide the exact replacement policy text or evidence-collection step.

TRACEABILITY SELF-CHECK: Verify that every conclusion item cites a specific
[T] identifier and [P2] clause.
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] R1 min 8; R2 composition (upper, lower, digit, special); R3 90-day expiry; R4 history of 5; R5 lockout after 3 failures for 30 minutes.
- [P2] SP 800-63B Rev 3 (2017) §5.1.1.2 and §5.2.2; SP 800-63B-4 (2025) password verifier and rate-limiting requirements.
- [P3] Policy text only.
- [P4] Evidence: [P1] text.

#### COMPLIANCE TRACES
- [T1] Minimum length (R1)
  1. Requirement: Rev 3 SHALL require at least 8 characters. Rev 4 SHALL require at least 15 characters when the password is a single-factor authenticator, and at least 8 when used only as part of MFA.
  2. Artifact: R1, minimum 8.
  3. Disposition: Rev 3 **COMPLIANT**; Rev 4 **PARTIAL**: compliant only for accounts where MFA is enforced. MFA enforcement is `UNABLE TO VERIFY` from [P4].
  4. Deficit: no MFA statement; no 15-character minimum for password-only accounts.
- [T2] Composition rules (R2)
  1. Requirement: Rev 3 SHOULD NOT impose composition rules; Rev 4 SHALL NOT.
  2. Artifact: R2 requires four character classes.
  3. Disposition: **NON-COMPLIANT** (Rev 4); contrary to Rev 3 guidance.
  4. Mechanism: composition rules produce predictable substitutions and do not replace blocklist screening ([T7]).
- [T3] Periodic expiration (R3)
  1. Requirement: Rev 3 SHOULD NOT require periodic change; Rev 4 SHALL NOT. Both SHALL force a change on evidence of compromise.
  2. Artifact: R3, 90-day expiry; no compromise-triggered change stated.
  3. Disposition: **NON-COMPLIANT** (Rev 4); contrary to Rev 3 guidance. Compromise-triggered change: **NOT ADDRESSED**.
- [T4] Password history (R4)
  1. Requirement: no history requirement in either revision.
  2. Artifact: R4, last 5.
  3. Disposition: **COMPLIANT (permitted, not required)**.
  4. Mechanism: once R3 is removed, history only applies to voluntary or compromise-triggered changes, where blocking reuse of a compromised password is useful.
- [T5] Failed-attempt handling (R5)
  1. Requirement: SHALL limit consecutive failed attempts on a single account to no more than 100; guidance favors techniques that reduce lockout of legitimate users (CAPTCHA, increasing delays, risk-based or IP-based controls).
  2. Artifact: R5, lock after 3 failures for 30 minutes.
  3. Disposition: **COMPLIANT** with the 100-attempt ceiling.
  4. Counterexample: a 3-attempt threshold lets any party who knows a username lock that account for 30 minutes at will (denial of service), and drives help-desk resets. Compliant but misaligned with the guidance's intent.
- [T6] Maximum length and character set
  1. Requirement: SHOULD permit at least 64 characters; SHOULD accept printing ASCII, space, and Unicode; SHALL verify the entire password (no truncation, Rev 4).
  2. Artifact: absent.
  3. Disposition: **NOT ADDRESSED**.
- [T7] Blocklist screening
  1. Requirement: SHALL compare prospective passwords against a blocklist (breached corpuses, dictionary words, repetitive or sequential characters, context-specific words).
  2. Artifact: absent.
  3. Disposition: **NOT ADDRESSED** (SHALL-level gap).
- [T8] Storage
  1. Requirement: SHALL store salted and hashed with a suitable one-way key derivation function.
  2. Artifact: absent; implementation is outside [P3].
  3. Disposition: **UNABLE TO VERIFY**. Evidence needed: hashing algorithm and parameters from the authentication service configuration.
- [T9] Hints, knowledge-based prompts, and password managers
  1. Requirement: SHALL NOT store hints accessible to unauthenticated users or prompt for knowledge-based security questions; Rev 4 SHALL allow password managers and autofill; SHOULD permit paste.
  2. Artifact: absent.
  3. Disposition: **NOT ADDRESSED**.

#### FORMAL CONCLUSION
- **Disposition summary: NON-COMPLIANT** with SP 800-63B-4; materially misaligned with Rev 3 guidance.
- **Non-compliant:** composition rules ([T2]); periodic expiration ([T3]).
- **Partial:** 8-character minimum without stated MFA ([T1]).
- **Not addressed:** blocklist ([T7], SHALL); compromise-triggered change ([T3]); length ceiling and character set ([T6]); hints, knowledge-based questions, password-manager support ([T9]).
- **Unable to verify:** storage ([T8]); MFA enforcement ([T1]).
- **Compliant:** history ([T4]); failed-attempt ceiling ([T5], with a usability and denial-of-service caveat).
- **Severity ranking:** (1) missing blocklist ([T7]); (2) password-only accounts at 8 characters ([T1]); (3) unverified storage ([T8]); (4) composition and expiration rules driving predictable passwords ([T2], [T3]); (5) 3-attempt lockout enabling account denial of service ([T5]); (6) remaining NOT ADDRESSED items ([T6], [T9]).

#### REMEDIATION / NEXT ACTION
**Replacement policy text**

> 1. Passwords must be at least 15 characters for accounts that authenticate with a password alone, and at least 8 characters for accounts that require multi-factor authentication. Passwords up to at least 64 characters are accepted and verified in full. [T1], [T6]
> 2. All printable ASCII characters, spaces, and Unicode characters are accepted. No character-class requirements apply. [T2], [T6]
> 3. New passwords are checked against a list of breached, dictionary, repetitive or sequential, and service-specific values; rejected passwords are refused with an explanation. [T7]
> 4. Passwords do not expire on a schedule. A change is required when there is evidence of compromise. [T3]
> 5. The last 5 passwords may not be reused. [T4]
> 6. After 5 consecutive failed attempts, further attempts require a CAPTCHA and are delayed with exponential back-off; the account is temporarily locked after no more than 100 consecutive failures. [T5]
> 7. Password hints and security questions are not used. Pasting and password managers are supported. [T9]
> 8. Passwords are stored salted and hashed with Argon2id, scrypt, bcrypt, or PBKDF2 using current recommended parameters. [T8]
> 9. Multi-factor authentication is required for administrative and remote access. [T1]

**Evidence collection for UNABLE TO VERIFY items**
- [T8]: export the authentication service's hashing configuration (algorithm, cost or memory parameters, salt length) and attach it to the audit record.
- [T1]: produce the MFA enforcement policy and a report of accounts without MFA enrolled.

**Traceability self-check:** each conclusion item cites a [T] identifier and an 800-63B requirement in [P2].

### EVALUATION: TEST 7

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 5         | 0     |
| Structure     | 5        | 4         | -1    |
| Actionability | 5        | 5         | 0     |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 24/25    | 24/25     | 0     |

Baseline Words: 519 | Optimized Words: 909 | Overhead Ratio: 1.75x | Prompt Words: 368

Both versions reached the same dispositions, covered both revisions, listed the same omitted requirements, and produced near-identical replacement policies. The optimized version added a severity ranking and an explicit UNABLE TO VERIFY status for storage and MFA (the baseline listed them as "missing", which conflates unstated policy with unverifiable implementation), offset by a Structure penalty because the baseline's single table was the faster read. This is a tie on a well-known standard where the baseline already performs at ceiling.

---

## TEST 8: Document Analysis (Mixed | Mode 1 Max | Template 2 Document Analysis)

### BASELINE RESPONSE

**Overall: low credibility as written.** Every claim is either unsupported, unfalsifiable, or in tension with the others. None is necessarily false, but the summary provides no evidence, baselines, or definitions, which is exactly what a credible proposal would lead with.

**1. "Reduce support tickets by 60% within 6 months"**
- No baseline: 60% of what volume, measured how? Is this ticket *deflection* (users never open a ticket), *automation* (bot resolves it), or a drop in total contacts?
- 60% is at the aggressive end for AI customer service. Deflection rates vary widely by industry and by how repetitive the ticket mix is; high-complexity or account-specific support rarely sees numbers like this.
- No source: is this from a pilot, a reference customer, or a projection? A precise number with no provenance is a red flag.

**2. "Proprietary NLP technology that outperforms all competitors"**
- Unfalsifiable as stated: outperforms on what metric, on what dataset, against which competitors, tested by whom?
- "Proprietary" may mean a fine-tuned wrapper around a commercial foundation model, which is fine but undercuts a claimed moat.
- Universal superlatives ("all competitors") are a marketing signal, not a technical one.

**3. "Minimal IT involvement"**
- Getting to a 60% reduction requires deep integration: ticketing system, CRM, knowledge base, authentication (to answer account-specific questions), data-privacy review, escalation routing, and ongoing content maintenance. That is the opposite of minimal IT involvement.
- These two claims are in tension: either the system is lightly integrated (and the 60% is unlikely) or it is deeply integrated (and IT effort is substantial).

**4. "ROI will exceed 300% in the first year"**
- No cost or benefit figures, no ROI formula, no time basis.
- It conflicts with the 6-month ramp: if the full 60% reduction is reached only at month 6, first-year savings reflect a partial year of full impact.
- Fewer tickets doesn't translate one-to-one into savings: support staff costs are partly fixed in the short term, and the remaining tickets are the harder, more expensive ones.

**What would make this credible**
- Baseline ticket volume and mix, with the definition of "reduction".
- Pilot or reference-customer results with the measurement method.
- A named benchmark comparison against named competitors.
- An integration plan with IT hours estimated.
- An ROI model with all cost lines (licenses, implementation, integration, maintenance, staff time) and benefit lines.
- A contractual performance guarantee (for example, fees tied to achieved deflection).

**Questions to ask the vendor**
1. What was the ticket reduction at your three most comparable customers, and can we talk to them?
2. How do you define and measure a "reduced" ticket?
3. What systems must be integrated, and how many IT hours did comparable deployments take?
4. Show the ROI calculation, including all costs.
5. Will you put the 60% target in the contract with remedies?

### OPTIMIZED PROMPT

**Task classification:** Mixed (critical analysis with an assessment). Minimal persona (`[PRISM]`). **Mode 1 Max Certificate**, Template 2 (Document Analysis / Review). Expected overhead ~2.2x.
**Diagnosis:** "Analyze the credibility" has no stated standard of evidence (guesswork gap); no instruction to check claims against each other (internal consistency is where this text is weakest); no remediation artifact. No goal leakage.

```
You are an analyst.

The established analytical protocol for document review requires completing
this certificate before providing any assessment.

### PREMISES
- [P1] Document: executive summary of a project proposal, full text:
  "Our AI-powered customer service solution will reduce support tickets by 60%
  within 6 months of deployment. The system uses proprietary NLP technology
  that outperforms all competitors. Implementation requires minimal IT
  involvement and the ROI will exceed 300% in the first year."
- [P2] Analysis scope: each factual or quantitative claim (C1 ticket
  reduction, C2 technology superiority, C3 IT effort, C4 ROI).
- [P3] Reference standard: a claim is credible when it states a baseline, a
  definition, a measurement method, a source of evidence, and is consistent
  with the other claims.
- [P4] Contextual inputs: none beyond [P1].

### EVIDENCE TRACES
For each claim in [P2]:
- [T1] Finding [claim]:
  1. Source location: sentence in P1
  2. Direct evidence: exact quote
  3. Standard mapping: which P3 elements are present or missing
  4. Internal consistency: other P1 claims that corroborate or conflict

Grounding rule: Anchor every trace in a quote from [P1]. When a P3 element is
absent, record `ABSENT FROM [P1]: [element]`. When a claim can be tested
arithmetically against another claim, show the arithmetic and state the
assumptions.

### FORMAL CONCLUSION
- Assessment: overall credibility evaluation
- Key findings: numbered, each citing at least one T-identifier
- Verification gaps: items marked ABSENT

### REMEDIATION / NEXT ACTION
Provide copy-pasteable redline edits that would make each claim verifiable,
and the evidence request list that closes each gap.

TRACEABILITY SELF-CHECK: Verify that every finding in the conclusion cites at
least one [T] identifier. Remove or trace any unreferenced claim.
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] Three-sentence executive summary (quoted in full in the prompt).
- [P2] Claims C1 (60% ticket reduction), C2 (outperforms all competitors), C3 (minimal IT), C4 (ROI above 300% in year one).
- [P3] Credibility elements: baseline, definition, method, evidence source, consistency.
- [P4] No supporting material.

#### EVIDENCE TRACES
- [T1] C1 ticket reduction
  1. Location: sentence 1.
  2. Quote: "will reduce support tickets by 60% within 6 months of deployment."
  3. Standard mapping: `ABSENT FROM [P1]: baseline volume`; `ABSENT FROM [P1]: definition of reduction` (deflection, bot resolution, or total contact volume); `ABSENT FROM [P1]: measurement method`; `ABSENT FROM [P1]: evidence source` (pilot, reference customer, or projection).
  4. Consistency: depends on C3 ([T3]) and drives C4 ([T4]).
- [T2] C2 technology superiority
  1. Location: sentence 2.
  2. Quote: "proprietary NLP technology that outperforms all competitors."
  3. Standard mapping: `ABSENT FROM [P1]: metric, benchmark dataset, named competitors, test conductor`. "All competitors" is a universal claim; it cannot be verified without an exhaustive comparison and is falsified by a single counterexample.
  4. Consistency: no other claim supports it.
- [T3] C3 IT effort
  1. Location: sentence 3, clause 1.
  2. Quote: "Implementation requires minimal IT involvement."
  3. Standard mapping: `ABSENT FROM [P1]: definition of minimal, integration list, hour estimate`.
  4. Consistency conflict with C1: resolving 60% of tickets requires access to the systems that answer them (ticketing, CRM, order or account data, knowledge base, identity for authenticated answers) plus privacy and security review. Either integration is deep (C3 weakens) or shallow (C1 weakens). Both cannot hold at full strength.
- [T4] C4 first-year ROI
  1. Location: sentence 3, clause 2.
  2. Quote: "the ROI will exceed 300% in the first year."
  3. Standard mapping: `ABSENT FROM [P1]: cost base, benefit model, ROI formula`.
  4. Consistency test against C1 (arithmetic, stated assumptions):
     - ROI = (Benefit - Cost) / Cost > 3, so year-one Benefit > 4 x Cost.
     - Assume reduction ramps linearly from 0% to 60% over months 1-6 and holds at 60% for months 7-12. Average first-year reduction = (30% x 6 + 60% x 6) / 12 = **45%**, not 60%.
     - If every avoided ticket saves its full handling cost, year-one benefit = 0.45 x annual ticket-handling cost. The 300% claim then requires annual ticket-handling cost > 4 / 0.45 = **8.9x the total first-year cost** of the solution.
     - If only half of handling cost is variable in year one (staff are partly fixed), the requirement doubles to **17.8x**.
     - Result: C4 is possible only for organizations whose support spend dwarfs the solution cost; it is not credible as a general claim.
- [T5] Document-level pattern
  1. All four claims are forward-looking ("will") and unconditional; none is stated as a measured past result.
  2. Zero of the 20 credibility elements (5 elements x 4 claims) in [P3] are present.

#### FORMAL CONCLUSION
- **Assessment: low credibility as written.** No claim meets any [P3] element ([T5]), and two pairs of claims are mutually constraining ([T3], [T4]).
- **Key findings:**
  1. C1 lacks baseline, definition, method, and source ([T1]).
  2. C2 is an unfalsifiable universal superlative ([T2]).
  3. C1 and C3 are in tension: high deflection requires deep integration ([T3]).
  4. The 6-month ramp lowers average first-year reduction to about 45%, so C4 requires annual support cost of roughly 9x to 18x the solution's first-year cost ([T4]).
- **Verification gaps:** baseline and definition ([T1]); benchmark evidence ([T2]); integration scope ([T3]); cost and benefit model ([T4]).

#### REMEDIATION / NEXT ACTION
**Redline of the executive summary** (bracketed values to be supplied by the vendor):

> ~~Our AI-powered customer service solution will reduce support tickets by 60% within 6 months of deployment.~~
> In a [N]-month deployment at [reference customer, industry], the solution resolved [X]% of inbound tickets without agent involvement, measured as [definition], against a baseline of [volume] tickets per month. We project [Y]% for your ticket mix, based on [analysis of a sample of your tickets]. [T1]
>
> ~~The system uses proprietary NLP technology that outperforms all competitors.~~
> On [benchmark or your sample of N tickets], the system achieved [metric] versus [named competitors], evaluated by [party]. [T2]
>
> ~~Implementation requires minimal IT involvement~~
> Implementation requires integration with [ticketing, CRM, knowledge base, SSO], estimated at [hours] of customer IT effort over [weeks]. [T3]
>
> ~~and the ROI will exceed 300% in the first year.~~
> Based on the attached model (year-one cost [amount]; benefit from [avoided tickets x variable cost per ticket]), projected first-year ROI is [Z]%, assuming a [ramp] adoption curve. [T4]

**Evidence request list**
1. Ticket-volume baseline and definition of a "reduced" ticket ([T1]).
2. Results and contacts for three comparable reference deployments ([T1], [T2]).
3. Benchmark report naming competitors and methodology, or a bake-off on a sample of our tickets ([T2]).
4. Integration architecture and IT hour estimates from comparable deployments ([T3]).
5. ROI spreadsheet with all cost and benefit lines and the adoption ramp ([T4]).
6. Contract terms tying fees to achieved resolution rate ([T1], [T4]).

**Traceability self-check:** each key finding cites [T1]-[T5]; all arithmetic shows its assumptions.

### EVALUATION: TEST 8

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 4        | 5         | +1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 21/25    | 24/25     | +3    |

Baseline Words: 474 | Optimized Words: 850 | Overhead Ratio: 1.79x | Prompt Words: 339

Both versions identified the same four weaknesses and the C1/C3 tension. The certificate's arithmetic-consistency instruction produced the most valuable addition: turning the qualitative "ROI conflicts with the ramp" into a quantified test (45% average reduction; support spend must exceed 8.9x to 17.8x the solution cost), which I recomputed and confirmed. The redline is more directly usable than the baseline's question list, while the baseline remains the more readable document.

---

## TEST 9: Comparative Analysis (Mixed | Mode 2 Lite | Template 6 Comparative Analysis)

### BASELINE RESPONSE

**Recommendation: PostgreSQL**, using regular relational tables for transactions and `JSONB` columns in time-partitioned tables for the activity logs. At your volume, you don't need MongoDB's horizontal scaling, and you do benefit from Postgres's relational integrity for transaction data.

**Sizing the workload**
- 10M records/month growing 20% per year is about 120M records in year 1, 264M cumulative by end of year 2, 437M by year 3, and roughly 890M by year 5.
- Average write rate is about 4 records per second (10M / ~2.6M seconds per month). Even with 10x to 50x peaks, that's well within a single Postgres instance.
- At roughly 1 KB per record, that's about 10 GB per month of raw data before indexes, so a few hundred GB by year 3. Large but routine.

**Transaction data: PostgreSQL wins**
- Full ACID transactions, foreign keys, constraints, and joins are native and mature.
- MongoDB has supported multi-document ACID transactions since 4.0 (replica sets) and 4.2 (sharded clusters), but they carry more overhead and are not the idiomatic access pattern; referential integrity remains application-enforced.

**Semi-structured logs: closer than people think**
- MongoDB's flexible documents are a natural fit, and it has time-series collections (5.0+) and built-in sharding.
- PostgreSQL `JSONB` handles semi-structured data well: GIN indexes for containment queries, expression indexes on frequently queried fields, and declarative partitioning by month. Partition by time, add a BRIN index on the timestamp, and drop old partitions for retention.

**Operational considerations**
- **One database vs. two:** using Postgres for both avoids running two systems, two backup strategies, and cross-database consistency problems (for example, logging an activity in the same transaction as the purchase it relates to).
- **Scaling:** Postgres scales vertically and with read replicas; if you eventually need horizontal scale, Citus or moving logs to a dedicated analytics store (ClickHouse, BigQuery) are options. MongoDB's sharding is easier out of the box.
- **Analytics:** SQL over both transactions and logs (joins, window functions) is a major advantage for reporting.

**When MongoDB would be the better choice**
- Log volume grows far beyond these projections (billions of records per month) and you want built-in sharding.
- The data is mostly document-shaped with few cross-entity relationships and few multi-record transactions.
- Your team has deep MongoDB experience and little Postgres experience.

**Suggested setup**
```sql
CREATE TABLE activity_log (
  id          bigint GENERATED ALWAYS AS IDENTITY,
  user_id     bigint NOT NULL,
  occurred_at timestamptz NOT NULL,
  event_type  text NOT NULL,
  payload     jsonb NOT NULL,
  PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE INDEX ON activity_log USING brin (occurred_at);
CREATE INDEX ON activity_log (user_id, occurred_at);
CREATE INDEX ON activity_log USING gin (payload jsonb_path_ops);
```
Create monthly partitions ahead of time (`pg_partman` automates this) and drop partitions past your retention window.

### OPTIMIZED PROMPT

**Task classification:** Mixed (technical comparison with a recommendation). Minimal persona (`[PRISM]`). **Mode 2 Lite Certificate** per protocol: at most 3 premises, single-line causal traces, compact decision matrix, 1-2 sentence conclusion, remediation. Target overhead below 1.5x.
**Diagnosis:** the split between transactional and log volume is unstated (guesswork gap); no request to size the workload numerically or to name crossover conditions. No goal leakage.

```
You are a database analyst.

The standard comparative protocol requires completing this compact certificate
before issuing a recommendation.

### PREMISES (maximum 3)
- [P1] Subjects: PostgreSQL (current major version) vs. MongoDB (current major
  version).
- [P2] Workload: structured transaction data plus semi-structured user activity
  logs; 10M records/month total, growing 20% per year. Split between the two
  record types is not stated.
- [P3] Dimensions: transactional integrity, semi-structured data handling,
  scale headroom for [P2], operational footprint, analytics.

### TRACES (one line each)
Format: [Tn] Dimension -> evidence for each subject -> leader and crossover
condition. Include one numeric sizing trace computed from [P2].

### DECISION MATRIX
One row per dimension in [P3], one column per subject, a leader column.

### CONCLUSION (1-2 sentences, citing T-identifiers)

### REMEDIATION / NEXT ACTION
Provide the schema or configuration snippet for the selected subject.

When a figure depends on an unstated input, state the assumption inline.
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] PostgreSQL vs. MongoDB, current major versions.
- [P2] 10M records/month, +20%/year; transaction-vs-log split unstated (assumed log-heavy).
- [P3] Integrity, semi-structured handling, scale headroom, operations, analytics.

#### TRACES
- [T1] Sizing -> 120M records (Y1), 437M cumulative (Y3), ~893M (Y5); ~3.9 writes/s average; ~10 GB/month at an assumed 1 KB/record -> well within single-node capacity for both.
- [T2] Integrity -> Postgres: native ACID, FKs, constraints, joins; Mongo: multi-document ACID since 4.0/4.2 with higher overhead, app-enforced references -> **Postgres**; crossover: none for transaction data.
- [T3] Semi-structured logs -> Postgres: `JSONB` + GIN/expression indexes + monthly partitions; Mongo: native documents, time-series collections -> **Mongo slightly**; crossover: Postgres matches it when queried fields are known and indexable.
- [T4] Scale headroom -> Postgres: vertical + replicas, Citus if needed; Mongo: built-in sharding -> **Mongo**; crossover: matters only far above [T1] volumes (billions/month).
- [T5] Operations -> one Postgres system for both record types vs. two systems or Mongo-for-everything -> **Postgres** (single backup, single consistency boundary for "purchase + activity" writes).
- [T6] Analytics -> SQL joins and window functions across transactions and logs vs. aggregation pipelines -> **Postgres**.

#### DECISION MATRIX

| Dimension | PostgreSQL | MongoDB | Leader |
|---|---|---|---|
| Integrity ([T2]) | Native, mature | Supported, costlier | Postgres |
| Semi-structured ([T3]) | JSONB, strong | Native | Mongo (slight) |
| Scale headroom ([T4]) | Ample for [T1] | Ample, easier sharding | Mongo (not needed at [T1]) |
| Operations ([T5]) | One system | One or two | Postgres |
| Analytics ([T6]) | SQL across both | Pipelines | Postgres |

#### CONCLUSION
Choose **PostgreSQL** for both workloads: it leads on integrity, operations, and analytics ([T2], [T5], [T6]), and Mongo's advantages ([T3], [T4]) do not bind at the projected volume ([T1]). Revisit if log volume reaches billions of records per month or the team is Mongo-native.

#### REMEDIATION / NEXT ACTION
```sql
CREATE TABLE activity_log (
  id          bigint GENERATED ALWAYS AS IDENTITY,
  user_id     bigint NOT NULL,
  occurred_at timestamptz NOT NULL,
  event_type  text NOT NULL,
  payload     jsonb NOT NULL,
  PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE TABLE activity_log_2026_11 PARTITION OF activity_log
  FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');

CREATE INDEX ON activity_log USING brin (occurred_at);
CREATE INDEX ON activity_log (user_id, occurred_at);
CREATE INDEX ON activity_log USING gin (payload jsonb_path_ops);
```
Automate monthly partitions with `pg_partman`; drop partitions beyond the retention window. Validate [T1] assumptions by measuring average row size after one week of production writes.

### EVALUATION: TEST 9

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | 0     |
| Completeness  | 5        | 4         | -1    |
| Structure     | 4        | 5         | +1    |
| Actionability | 5        | 5         | 0     |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 22/25    | 24/25     | +2    |

Baseline Words: 456 | Optimized Words: 416 | Overhead Ratio: 0.91x | Prompt Words: 215

Lite mode did what it claims here: same recommendation, same sizing (recomputed: 120M, 437M, 893M records; 3.86 writes/s), a decision matrix with per-cell trace citations, and output shorter than the baseline. Structure improved because the matrix is faster to scan than the baseline's prose sections. Completeness dropped one point because the 3-premise cap and one-line traces squeezed out some nuance the baseline kept (team-expertise discussion in depth, ClickHouse offload path, Mongo's transaction caveats explained rather than abbreviated).

---

## TEST 10: Creative Brief (Creative | Mode 4 Creative & Divergent v2 | Template 12 Creative / Editorial Writing)

### BASELINE RESPONSE

**Built for the Long Day**

Your workday doesn't end at five, and your chair shouldn't give up before you do. Designed for people who routinely put in 10+ hours at the desk, this ergonomic chair keeps you supported, cool, and focused from the first standup to the last commit.

**Lumbar support that adjusts itself.** Most chairs make you choose a lumbar setting once and live with it. Ours continuously adapts to your posture, so whether you're leaning in to debug or reclining on a long call, your lower back stays supported without a single knob to fiddle with.

**Breathable mesh that keeps you cool.** The full mesh back and seat let air circulate where padded chairs trap heat, so hour nine feels a lot more like hour one.

**A 12-year warranty.** We built it to last through laptops, job changes, and home-office upgrades, and we back it for over a decade.

**Why remote tech workers love it**
- Auto-adjusting lumbar support that follows your movement
- Breathable mesh for all-day comfort
- Designed for 10+ hour workdays
- 12-year warranty for long-term peace of mind

Invest in the chair that works as hard as you do. Your back will thank you.

### OPTIMIZED PROMPT

**Task classification:** Creative / Divergent (product copy). Minimal practitioner persona (`[PRISM]`). **Mode 4 Creative & Divergent v2**, Template 12 (the protocol's "Template 10 `[NT0]` + `[SC0]`" maps to skill Template 12; I label the Structural Rarity Contract `[SC0]` to match the protocol). Expected overhead ~1.6x.
**Diagnosis:** high mode-collapse risk: the default output is a "chair that works as hard as you do" headline, three feature paragraphs, a bullet recap, and a "your back will thank you" close, which is the tidy self-announcing SlopShape (`[VS]`, `[SLOPSHAPE]`). "Target audience is remote tech workers ages 25-45" is audience context, not goal leakage, and is converted into lived friction in [P1]. The protocol asks for 3 low-typicality candidates below p = 0.15; the skill specifies 4 angles and selection at p <= 0.20. I generate 4 angles with 3 of them below 0.15, which satisfies both.

```
You are a direct-response copywriter.

The editorial craft protocol requires completing the backstage scaffolding
block before drafting the final piece.

### PREMISES
- [P1] Audience and lived context: remote tech workers, 25-45, who routinely
  sit 10+ hours; friction includes long meetings, late debugging, posture
  drifting as the day goes on, heat buildup in padded seats.
- [P2] Target shift: the reader recognizes their own hour-ten body in the copy
  and connects each feature to a specific moment in that day.
- [P3] Format and facts: product description, 180-260 words. Use only these
  product facts: lumbar support that auto-adjusts, breathable mesh, 12-year
  warranty. When a detail (price, materials, certifications, return policy)
  is not in this list, leave it out.

### BACKSTAGE SCAFFOLD (complete before drafting)
- [NT0] Verbalized Distribution Sampling: generate 4 structurally distinct entry
  angles with typicality probabilities (p = likelihood a default model would
  produce it). Include at least 3 angles with p < 0.15. Commit to the strongest
  angle with p < 0.15 that satisfies [P1]-[P3].
- [NT1] Opening anchor: the specific moment or artifact that opens the draft.
- [NT2] Inductive trajectory: how the features emerge from the scene.
- [NT3] Cadence and texture: sentence-length variation, concrete nouns.

### [SC0] STRUCTURAL RARITY CONTRACT
Shape the final piece so it satisfies all four rules:
1. Delayed thesis: a specific, non-spoiler title; open inside the [NT1] moment
   before any claim about the chair.
2. Direct evidence progression: each feature appears through a concrete moment
   in the reader's day rather than a "most chairs vs. our chair" contrast.
3. Practitioner voice: second person, asymmetric paragraph lengths.
4. Actionable close: end on a concrete implication or action rather than a
   recap of features or a slogan.

### FINAL DELIVERABLE
Show the backstage block, then the finished piece under a FINAL COPY heading.
```

### OPTIMIZED RESPONSE

#### BACKSTAGE

- [NT0] Angles:
  1. "The chair that works as hard as you do": feature-benefit list with a hustle headline (p = 0.55)
  2. Health-statistics opener about the cost of sitting, then features (p = 0.20)
  3. Hour-by-hour: the same day at 9 a.m., 2 p.m., and 7:40 p.m., with each feature appearing at the hour it matters (p = 0.12)
  4. Warranty-first inversion: open on what twelve years contains for a remote worker (laptops, jobs, apartments) and work backward to why the chair can promise it (p = 0.08)
  - Selection: **Angle 3 as the spine, closing on Angle 4.** Angle 4 alone underplays the lumbar feature (the most differentiated fact); Angle 3 delivers all three facts at their natural moments and lets the warranty land as the close.
- [NT1] Opening anchor: 7:40 p.m., a standup that started the day, a body that has slid forward a centimeter an hour.
- [NT2] Trajectory: slump (lumbar) -> heat at hour eight (mesh) -> zoom out to years (warranty) -> date-based close.
- [NT3] Cadence: short declaratives against one long sentence per paragraph; nouns from the reader's day (standup, deploy, debugger, calendar).

#### FINAL COPY

**Hour Ten**

It's 7:40. The standup that opened your day ended eleven hours ago, and you've been sliding forward in your seat ever since. Not dramatically. A centimeter an hour. By now your lower back is holding a shape it never agreed to.

This chair notices. Its lumbar support adjusts on its own as your posture changes, so the curve that met your spine at 9 a.m. is still there when you lean into a stack trace at six and when you sink back to watch the deploy finish. There is no knob to find. You were never going to reach for it anyway.

The seat and back are open mesh. Air moves through them. That barely registers in hour one. It registers in hour eight, when a padded seat starts to feel like a car in July.

Then there's the warranty: twelve years.

Count what twelve years holds for someone who works from home. Three laptops, maybe four. A couple of job changes. Possibly a move to a city you haven't picked yet. The chair is built to make every one of those moves with you.

Look at today's date. Add twelve years. Write it on the box.

### EVALUATION: TEST 10

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4        | 5         | +1    |
| Completeness  | 5        | 4         | -1    |
| Structure     | 3        | 4         | +1    |
| Actionability | 4        | 4         | 0     |
| Traceability  | 3        | 4         | +1    |
| TOTAL         | 19/25    | 21/25     | +2    |

Baseline Words: 201 | Optimized Words: 395 | Overhead Ratio: 1.97x | Prompt Words: 445 | Final-Copy-Only Words: 199

Rubric interpretation for a creative task: Accuracy = fidelity to the given product facts; Structure = structural originality and readability; Traceability = whether creative choices follow from the stated audience and facts. The baseline is competent but exhibits nearly every SlopShape marker (payoff headline, "most chairs" contrast, bullet recap restating the three paragraphs, slogan close), and "we back it for over a decade" plus "why remote tech workers love it" imply testimonials not in the brief, costing an Accuracy point. The optimized copy has a distinct voice and uses only the three given facts, but drops the scannable feature list that e-commerce pages usually need (Completeness -1), and the visible backstage block would have to be stripped before the copy could be used.

---

## TEST 11: Repository Context File (Harness | Mode 3 `[CONTEXT-FILES]` | Template 11 Agentic System Prompt / CLAUDE.md)

### BASELINE RESPONSE

````markdown
# CLAUDE.md

## Project Overview

This repository contains a Python web API built with **FastAPI** and backed by
**PostgreSQL**. It exposes REST endpoints, uses SQLAlchemy-style models for
persistence, and keeps business logic in a dedicated services layer. Redis is
used as a cache for billing-related data.

## Folder Structure

```
app/
├── api/        # FastAPI routers and endpoint definitions (request/response handling)
├── models/     # Database models and schemas
└── services/   # Business logic (e.g., billing.py)
tests/          # Unit and integration tests
scripts/        # Project scripts (e.g., migrate.sh)
```

- Keep route handlers in `app/api/` thin; put business logic in `app/services/`.
- Database models live in `app/models/`.
- Tests mirror the `app/` structure under `tests/`.

## Coding Conventions

- Follow **PEP 8**: 4-space indentation, `snake_case` for functions and
  variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Keep lines to a reasonable length (79-100 characters).
- Use type hints on all function signatures.
- Write docstrings for public modules, classes, and functions.
- Group imports: standard library, third-party, local, separated by blank lines.
- Prefer explicit over implicit; avoid wildcard imports.

## Common Commands

### Running unit tests
Unit tests must exclude integration tests and reuse the test database:

```bash
pytest -m "not integration" --reuse-db
```

### Database migrations
Before committing any change, run the migration check:

```bash
./scripts/migrate.sh check
```

Do not commit if this check fails.

### Running the dev server
```bash
uvicorn app.main:app --reload   # adjust if the entrypoint differs
```

## Important Rules

- **Redis cache keys in `app/services/billing.py` must never be mutated
  without bumping `SCHEMA_EPOCH`.** Changing a key's format without bumping
  the epoch will cause stale or incompatible cached billing data to be read.
- Always run the unit tests and the migration check before committing.
- Never commit secrets or `.env` files.
````

### OPTIMIZED PROMPT

**Task classification:** Persistent Context / Agent Harness. Persona omitted (`[PRISM]`). **Mode 3 Pattern B**, Template 11 (`[CONTEXT-FILES]`, Gloaguen et al., 2026). Expected overhead ~1.1x to 1.3x.
**Diagnosis:** the raw request asks for three discoverable sections (project overview, folder structure, PEP 8 conventions) that `[CONTEXT-FILES]` associates with lower agent task success and over 20% higher inference cost; the three genuinely non-inferable facts are buried at the end. The SCHEMA_EPOCH rule is phrased as a prohibition ("must never be mutated without"), which `[SKILLS-SDO]` recommends converting to an observable-predicate conditional. Unknown commands (lint, typecheck, server entrypoint) must not be invented.

```
Write a CLAUDE.md agent operating contract for a Python FastAPI + PostgreSQL
repository using the Minimal Viable Context structure below. The file must be
under 150 lines.

### PREMISES
- [P1] Non-inferable commands supplied by the repository owner:
  - Unit tests: pytest -m "not integration" --reuse-db
  - Migration gate before committing: ./scripts/migrate.sh check
- [P2] Non-inferable invariant supplied by the owner: Redis cache keys in
  app/services/billing.py require a SCHEMA_EPOCH bump whenever they change.
- [P3] Discoverable information (directory layout under app/api, app/models,
  app/services, tests/; FastAPI and PostgreSQL usage; PEP 8 conventions) is
  readable from the repository and standard tooling.

### STRUCTURE (sections in this order)
1. Non-Inferable Environment & Tooling Commands: only the commands in [P1].
2. Hard Architectural & Boundary Invariants: [P2] written as an
   observable-predicate conditional ("When X changes, do Y in the same commit").
3. Multi-Step Execution & Context-as-a-File Protocol: plan gate for changes
   touching 3+ files or a public interface; scratchpad for findings.
4. Mandatory Verification Gate: exact commands, exit-code reporting, and a
   VERIFICATION BLOCKED rule.

### CONTENT RULES
- When an item in [P3] is discoverable from the repository, leave it out of the
  file.
- When a command is not supplied in [P1], leave it out of the file and list it
  under VERIFICATION GAPS in your reply (outside the file).
- After the file, record VERIFICATION GATES:
  [V1] Line count under 150 -> SATISFIED / VIOLATED
  [V2] Every command in the file appears in [P1] -> SATISFIED / VIOLATED
  [V3] Every rule is phrased as a positive conditional or recipe -> SATISFIED /
  VIOLATED
```

### OPTIMIZED RESPONSE

````markdown
# Agent Operating Contract

## 1. Non-Inferable Commands
- Unit tests (excludes integration tests, reuses the test DB):
  `pytest -m "not integration" --reuse-db`
- Migration gate (run before every commit): `./scripts/migrate.sh check`

## 2. Hard Invariants
- [I1] Billing cache schema: when a change alters any Redis cache key name,
  prefix, or the shape of a cached value in `app/services/billing.py`,
  increment `SCHEMA_EPOCH` in the same commit and state the old and new epoch
  values in the commit message.
- [I2] Migration integrity: when `./scripts/migrate.sh check` exits non-zero,
  fix the migration state before committing.

## 3. Multi-Step Changes
- When a task touches 3+ files or changes a public API route or model, first
  write a short plan (files to change, invariants affected from Section 2,
  tests to run) to `scratch/PLAN.md`, then edit.
- Record intermediate findings and test output in that file instead of
  re-running broad repository searches.

## 4. Verification Gate (before claiming completion)
1. Run the unit test command from Section 1.
2. Run `./scripts/migrate.sh check`.
3. If `app/services/billing.py` changed, confirm `SCHEMA_EPOCH` changed
   accordingly per [I1] (`git diff -- app/services/billing.py`).
4. Report each command with its exit code. When a command cannot run in the
   current environment, report `VERIFICATION BLOCKED: <command> <error>`
   instead of claiming success.
````

**VERIFICATION GATES**
- [V1] Line count: 30 lines (under 150) -> SATISFIED.
- [V2] Commands: `pytest -m "not integration" --reuse-db` and `./scripts/migrate.sh check` both appear in [P1]; `git diff` is a standard inspection command, not a project command -> SATISFIED.
- [V3] Every rule is a positive conditional or ordered recipe ("when X, do Y") -> SATISFIED.

**VERIFICATION GAPS** (left out of the file; supply if they exist):
- Lint and typecheck commands (for example, a ruff or mypy invocation): not supplied.
- Dependency sync command (pip, uv, poetry): not supplied.
- Location of `SCHEMA_EPOCH`: not stated; `grep -rn SCHEMA_EPOCH app/` would locate it. If it lives outside `billing.py`, [I1] should name that file.
- `--reuse-db` is a pytest-django flag by default; in a FastAPI repo it is presumably provided by a custom `conftest.py` option or plugin. Worth confirming it exists, since an unknown flag makes pytest exit with a usage error.
- Dev server entrypoint: discoverable from the code, so intentionally omitted.

### EVALUATION: TEST 11

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4        | 5         | +1    |
| Completeness  | 4        | 4         | 0     |
| Structure     | 3        | 5         | +2    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 3        | 5         | +2    |
| TOTAL         | 18/25    | 24/25     | +6    |

Baseline Words: 298 | Optimized Words: 373 | Overhead Ratio: 1.25x | Prompt Words: 360

The baseline followed the request literally and therefore included exactly what `[CONTEXT-FILES]` identifies as harmful (a directory tree, an overview, PEP 8 platitudes); it also invented an unverified entrypoint (`uvicorn app.main:app`) and an "Important Rules" block mixing the one real invariant with generic advice. The optimized file itself is 30 lines and 208 words versus 64 lines and 296 words for the baseline file (the 1.25x response ratio comes from the V-gates and gap list written outside the file), contains only supplied commands, rewrites the SCHEMA_EPOCH prohibition as a checkable conditional with a verification step, and surfaced a real gap (`--reuse-db` is not a standard FastAPI-stack flag). Completeness is held equal rather than raised: the optimized response deliberately did not deliver three sections the user explicitly asked for, which is the right engineering call per the research but a deviation from the literal instruction that a user may not expect.

---

## TEST 12: Async Rate Limiter (Harness / LRM | Mode 3 `[HARNESS]` | SKILL.md Mode 3 Pattern A, LRM Verification Certificate)

### BASELINE RESPONSE

Here's an `asyncio`-based token bucket. The key idea for avoiding races is that all reads and writes of the token count happen under an `asyncio.Lock`, and waiters keep holding the lock while they sleep for the tokens they need. That makes waiters queue up in FIFO order, so a large request can't be starved by a stream of small ones, and no two coroutines can ever both see "enough tokens" and both take them.

```python
import asyncio
import time


class AsyncTokenBucket:
    """Async token bucket rate limiter.

    capacity: maximum number of tokens the bucket can hold (burst size).
    refill_rate: tokens added per second (may be fractional, e.g. 0.5).
    """

    def __init__(self, capacity: float, refill_rate: float) -> None:
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("capacity and refill_rate must be positive")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self._tokens = float(capacity)          # start full so bursts work immediately
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
            self._last_refill = now

    async def acquire(self, tokens: int = 1, timeout: float | None = None) -> bool:
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        if tokens > self.capacity:
            raise ValueError("cannot acquire more tokens than the bucket capacity")

        async def _wait() -> None:
            # Holding the lock while sleeping makes waiters queue in FIFO order,
            # so a large request is never starved by a stream of small ones.
            async with self._lock:
                while True:
                    self._refill()
                    if self._tokens >= tokens:
                        self._tokens -= tokens
                        return
                    deficit = tokens - self._tokens
                    await asyncio.sleep(deficit / self.refill_rate)

        try:
            await asyncio.wait_for(_wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False
```

**How it works**
- **Burst capacity:** the bucket starts full, so up to `capacity` tokens can be taken immediately.
- **Fractional refill:** tokens are tracked as floats and refilled from elapsed `time.monotonic()` time, so rates like `0.5` tokens/second work naturally. `monotonic()` is immune to wall-clock changes.
- **No race conditions:** the check-and-deduct is done atomically under the lock. Because a waiter sleeps while holding the lock, the next waiter can't jump in and steal tokens that the first one is waiting for.
- **Timeouts:** `asyncio.wait_for` cancels the wait if it takes too long and the method returns `False`. Because tokens are only deducted at the moment they're available, a timed-out or cancelled call never consumes tokens, and `async with` releases the lock on cancellation.
- **Impossible requests:** asking for more than `capacity` raises `ValueError`, since it could never succeed and would otherwise wait forever.

**Thread safety note:** `asyncio` primitives are not thread-safe. This class is safe for any number of coroutines on a single event loop. If you need to call it from multiple threads, keep one event loop that owns the limiter and submit work to it with `asyncio.run_coroutine_threadsafe`.

**Usage**
```python
bucket = AsyncTokenBucket(capacity=10, refill_rate=2.5)  # burst 10, 2.5 tokens/s

async def call_api():
    if await bucket.acquire(1, timeout=5):
        ...  # make the request
    else:
        ...  # rate limited; back off
```

### OPTIMIZED PROMPT

**Task classification:** Agentic / LRM coding task. Persona omitted (`[PRISM]`). **Mode 3 Pattern A** (LRM Verification Certificate) from `SKILL.md`; the protocol's "Template 12 `[HARNESS]`" does not exist in `domain-templates.md` (Template 12 is Creative). Expected overhead ~1.1x to 1.3x for the certificate, plus the requested test harness.
**Diagnosis:** "thread-safe async" is ambiguous (asyncio primitives are single-loop; true cross-thread safety needs a different lock); timeout semantics at `0` and the interaction of timeouts with queueing are unspecified; behavior for `tokens > capacity` is unspecified; "make sure there are no race conditions" is an unverifiable request rather than a set of checkable invariants (`[HARNESS]`, `[SKILLS-SDO]`).

```
The verification protocol for this implementation requires grounding the
deliverable in declared premises and post-condition checks. Perform design
exploration in your internal reasoning and emit only the verified certificate
below.

### PREMISES
- [P1] Deliverable: Python class AsyncTokenBucket with constructor
  (capacity, refill_rate) and method
  async acquire(tokens: int, timeout: float | None = None) -> bool.
  Python 3.11+ standard library only.
- [P2] Target invariants:
  [I1] No over-issue: total tokens granted over any interval of length t is at
       most capacity + refill_rate * t, under any number of concurrent
       coroutines and under calls from multiple threads.
  [I2] Burst: a full bucket grants up to capacity tokens without waiting.
  [I3] Fractional refill: non-integer refill_rate values produce correct
       wait durations.
  [I4] Timeout: None waits indefinitely; timeout > 0 bounds total wait,
       including time spent queued behind other waiters; timeout <= 0 is a
       non-blocking attempt that succeeds when tokens are available.
  [I5] Failed, timed-out, or cancelled calls consume zero tokens.
  [I6] Fairness: within one event loop, waiters are served in arrival order,
       so a large request is not starved by later small ones.
  [I7] Requests that can never succeed (tokens > capacity) fail immediately
       with a clear error.

### VERIFICATION GATES
For each invariant in [P2], record:
- [Vn] Invariant [In]: SATISFIED / VIOLATED / UNTESTABLE -> Evidence: the
  exact code construct that enforces it, plus the harness test that checks it.

When an invariant can only be partially enforced, mark it SATISFIED for the
enforced scope and state the residual limitation explicitly.

### FORMAL CONCLUSION & DELIVERABLE
- Disposition: summary grounded in the V-gates.
- Deliverable 1: complete, copy-pasteable implementation.
- Deliverable 2: executable self-test harness (no third-party packages) with
  one test per invariant; exit code 0 only when every test passes.
```

### OPTIMIZED RESPONSE

#### PREMISES
- [P1] `AsyncTokenBucket(capacity, refill_rate)`, `async acquire(tokens, timeout=None) -> bool`, Python 3.11+ (uses `asyncio.timeout`), standard library only.
- [P2] Invariants [I1]-[I7] as declared.

#### VERIFICATION GATES
- [V1] [I1] No over-issue: **SATISFIED.** `_tokens` is read, refilled, compared, and decremented only inside `_try_take` under `threading.Lock`; the lock is never held across an `await`, so the check-and-deduct is atomic across coroutines, threads, and event loops. Refill is capped at `capacity`. Harness: `test_no_over_issue_under_contention` (50 coroutines, elapsed >= (50 - 3) / 100 s) and `test_cross_thread_no_over_issue` (2 threads with separate loops, elapsed >= (60 - 10) / 50 s).
- [V2] [I2] Burst: **SATISFIED.** `_tokens` initialized to `capacity`. Harness: `test_burst_then_nonblocking`.
- [V3] [I3] Fractional refill: **SATISFIED.** Float arithmetic; wait = deficit / rate; loop re-checks after each sleep to absorb early wakeups and float rounding. Harness: `test_fractional_rate` (rate 2.5 -> ~0.4 s).
- [V4] [I4] Timeout: **SATISFIED.** `asyncio.timeout(timeout)` wraps both the FIFO-lock acquisition and the sleep loop, so queue time counts against the timeout; `asyncio.timeout(None)` waits indefinitely. `timeout <= 0` takes a synchronous path: returns `False` if any waiter is queued (preserves [I6]), otherwise one atomic `_try_take`. Harness: `test_nonblocking_succeeds_when_tokens_available`, `test_timeout_returns_false_and_consumes_nothing`.
- [V5] [I5] Zero-cost failure: **SATISFIED.** The only suspension points are lock acquisition and `asyncio.sleep`, both before any deduction; deduction and `return True` are synchronous, so cancellation or timeout cannot land between them. Harness: `test_timeout_returns_false_and_consumes_nothing`, `test_cancellation_consumes_nothing`.
- [V6] [I6] Fairness: **SATISFIED within one event loop.** Waiters hold a per-loop `asyncio.Lock` (FIFO) while sleeping. Residual limitation: across *different* event loops in different threads, ordering is not FIFO (tokens remain correct per [V1]). Harness: `test_fifo_large_request_not_starved`.
- [V7] [I7] Impossible requests: **SATISFIED.** `tokens > capacity` and `tokens < 0` raise `ValueError`; `tokens == 0` returns `True`. Harness: `test_invalid_requests`.

#### FORMAL CONCLUSION & DELIVERABLE
- **Disposition:** all seven invariants satisfied ([V1]-[V7]); one documented residual limitation (cross-loop fairness, [V6]). Evaluator execution: the harness below was run on Python 3.14.2 as `python3 t12_harness.py t12_optimized` and printed `9/9 passed`, exit code 0.

**Deliverable 1: `token_bucket.py`**

```python
"""AsyncTokenBucket: token bucket rate limiter for asyncio (Python 3.11+)."""
from __future__ import annotations

import asyncio
import threading
import time
import weakref


class AsyncTokenBucket:
    """Token bucket that is safe for concurrent coroutines and for multiple threads.

    capacity:    burst size, the maximum tokens the bucket holds (> 0).
    refill_rate: tokens added per second; fractional values allowed (> 0).

    Concurrency model:
    - Token arithmetic is guarded by a threading.Lock that is never held across
      an await, so grants are atomic across threads and event loops.
    - Coroutines on the same event loop queue on a per-loop asyncio.Lock (FIFO),
      so a large request is never starved by a stream of small ones.
    """

    def __init__(self, capacity: float, refill_rate: float) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be > 0")
        self._capacity = float(capacity)
        self._rate = float(refill_rate)
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._state_lock = threading.Lock()
        self._fifo_locks: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = (
            weakref.WeakKeyDictionary()
        )

    @property
    def capacity(self) -> float:
        return self._capacity

    @property
    def refill_rate(self) -> float:
        return self._rate

    def available(self) -> float:
        """Current token count after refill (for monitoring and tests)."""
        with self._state_lock:
            self._refill_locked()
            return self._tokens

    def _refill_locked(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last
        if elapsed > 0:
            self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
            self._last = now

    def _try_take(self, tokens: int) -> float:
        """Atomically deduct tokens. Return 0.0 on success, else seconds until enough accrue."""
        with self._state_lock:
            self._refill_locked()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return 0.0
            return (tokens - self._tokens) / self._rate

    def _fifo_lock(self) -> asyncio.Lock:
        loop = asyncio.get_running_loop()
        with self._state_lock:
            lock = self._fifo_locks.get(loop)
            if lock is None:
                lock = asyncio.Lock()
                self._fifo_locks[loop] = lock
            return lock

    async def acquire(self, tokens: int = 1, timeout: float | None = None) -> bool:
        """Wait until `tokens` are available and take them.

        Returns True when the tokens were granted, False when `timeout` seconds
        elapsed first. timeout=None waits indefinitely; timeout<=0 is a
        non-blocking attempt that respects queued waiters. A failed or
        cancelled call never consumes tokens.
        """
        if tokens < 0:
            raise ValueError("tokens must be >= 0")
        if tokens > self._capacity:
            raise ValueError("tokens exceeds capacity; the request can never be satisfied")
        if tokens == 0:
            return True

        fifo = self._fifo_lock()
        if timeout is not None and timeout <= 0:
            if fifo.locked():
                return False
            return self._try_take(tokens) == 0.0

        try:
            async with asyncio.timeout(timeout):
                async with fifo:
                    while True:
                        wait = self._try_take(tokens)
                        if wait == 0.0:
                            return True
                        await asyncio.sleep(wait)
        except TimeoutError:
            return False
```

**Deliverable 2: `t12_harness.py`** (run: `python3 t12_harness.py token_bucket`)

```python
"""Self-test harness for AsyncTokenBucket. Usage: python3 t12_harness.py <module_name>"""
import asyncio
import importlib
import sys
import threading
import time

AsyncTokenBucket = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "token_bucket").AsyncTokenBucket
TOL = 0.05


async def test_burst_then_nonblocking():
    b = AsyncTokenBucket(capacity=5, refill_rate=1)
    t0 = time.monotonic()
    assert all([await b.acquire(1) for _ in range(5)])
    assert time.monotonic() - t0 < TOL, "burst should be immediate"
    assert await b.acquire(1, timeout=0) is False, "empty bucket, non-blocking must fail"


async def test_nonblocking_succeeds_when_tokens_available():
    b = AsyncTokenBucket(capacity=3, refill_rate=1)
    assert await b.acquire(1, timeout=0) is True, "timeout=0 must succeed when tokens are available"


async def test_no_over_issue_under_contention():
    cap, rate, n = 3, 100.0, 50
    b = AsyncTokenBucket(capacity=cap, refill_rate=rate)
    t0 = time.monotonic()
    results = await asyncio.gather(*(b.acquire(1) for _ in range(n)))
    elapsed = time.monotonic() - t0
    floor = (n - cap) / rate
    assert all(results)
    assert elapsed >= floor - TOL, f"over-issue: {elapsed:.3f}s < {floor:.3f}s"


async def test_fractional_rate():
    b = AsyncTokenBucket(capacity=1, refill_rate=2.5)
    await b.acquire(1)
    t0 = time.monotonic()
    assert await b.acquire(1)
    dt = time.monotonic() - t0
    assert 0.4 - TOL <= dt <= 0.4 + 2 * TOL, f"expected ~0.4s, got {dt:.3f}s"


async def test_timeout_returns_false_and_consumes_nothing():
    b = AsyncTokenBucket(capacity=2, refill_rate=1)
    await b.acquire(2)
    t0 = time.monotonic()
    assert await b.acquire(2, timeout=0.1) is False
    assert time.monotonic() - t0 < 0.1 + TOL
    await asyncio.sleep(0.5)
    assert await b.acquire(1, timeout=0.6) is True  # ~0.6 accrued tokens + wait, nothing stolen


async def test_cancellation_consumes_nothing():
    b = AsyncTokenBucket(capacity=1, refill_rate=2)
    await b.acquire(1)
    task = asyncio.create_task(b.acquire(1))
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await asyncio.sleep(0.45)  # 0.55s total since drain => ~1.0 token (capped)
    t0 = time.monotonic()
    assert await b.acquire(1, timeout=0.2) is True
    assert time.monotonic() - t0 < TOL, "cancelled waiter must not have consumed tokens"


async def test_fifo_large_request_not_starved():
    b = AsyncTokenBucket(capacity=5, refill_rate=20)
    await b.acquire(5)
    order = []

    async def req(name, n):
        await b.acquire(n)
        order.append(name)

    big = asyncio.create_task(req("big", 5))
    await asyncio.sleep(0)
    smalls = [asyncio.create_task(req(f"s{i}", 1)) for i in range(5)]
    await asyncio.gather(big, *smalls)
    assert order[0] == "big", f"large request starved: {order}"


async def test_invalid_requests():
    b = AsyncTokenBucket(capacity=2, refill_rate=1)
    try:
        await b.acquire(3)
    except ValueError:
        pass
    else:
        raise AssertionError("tokens > capacity must raise ValueError")


def test_cross_thread_no_over_issue():
    cap, rate, per_thread, threads = 10, 50.0, 30, 2
    b = AsyncTokenBucket(capacity=cap, refill_rate=rate)
    errors = []

    def worker():
        async def run():
            for _ in range(per_thread):
                assert await b.acquire(1)
        try:
            asyncio.run(run())
        except Exception as e:  # surface errors to main thread
            errors.append(repr(e))

    t0 = time.monotonic()
    ts = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout=10)
    if any(t.is_alive() for t in ts):
        raise AssertionError("cross-thread deadlock: worker still blocked after 10s")
    elapsed = time.monotonic() - t0
    floor = (per_thread * threads - cap) / rate
    assert not errors, f"thread errors: {errors}"
    assert elapsed >= floor - TOL, f"cross-thread over-issue: {elapsed:.3f}s < {floor:.3f}s"


def main():
    async_tests = [
        test_burst_then_nonblocking,
        test_nonblocking_succeeds_when_tokens_available,
        test_no_over_issue_under_contention,
        test_fractional_rate,
        test_timeout_returns_false_and_consumes_nothing,
        test_cancellation_consumes_nothing,
        test_fifo_large_request_not_starved,
        test_invalid_requests,
    ]
    failed = 0
    for t in async_tests:
        try:
            asyncio.run(t())
            print(f"PASS {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e!r}")
    try:
        test_cross_thread_no_over_issue()
        print("PASS test_cross_thread_no_over_issue")
    except Exception as e:
        failed += 1
        print(f"FAIL test_cross_thread_no_over_issue: {e!r}")
    print(f"{len(async_tests) + 1 - failed}/{len(async_tests) + 1} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Harness output (evaluator run, Python 3.14.2):**

```
PASS test_burst_then_nonblocking
PASS test_nonblocking_succeeds_when_tokens_available
PASS test_no_over_issue_under_contention
PASS test_fractional_rate
PASS test_timeout_returns_false_and_consumes_nothing
PASS test_cancellation_consumes_nothing
PASS test_fifo_large_request_not_starved
PASS test_invalid_requests
PASS test_cross_thread_no_over_issue
9/9 passed
```

### EVALUATION: TEST 12

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 3        | 5         | +2    |
| Completeness  | 3        | 5         | +2    |
| Structure     | 5        | 4         | -1    |
| Actionability | 4        | 5         | +1    |
| Traceability  | 2        | 5         | +3    |
| TOTAL         | 17/25    | 24/25     | +7    |

Baseline Words: 503 | Optimized Words: 1285 | Overhead Ratio: 2.55x | Prompt Words: 395

As evaluator I ran the same harness against the baseline code: **7/9 passed (exit 1)**. Two real defects: (1) `acquire(1, timeout=0)` returns `False` even with a full bucket, because `asyncio.wait_for` with a zero timeout cancels the inner coroutine before it ever runs; (2) calling one instance from two threads with separate event loops **deadlocked** (the harness's 10-second join guard fired), because the shared `asyncio.Lock` is bound to one loop. The baseline did disclose the threading limitation in prose, but the user asked for thread safety and the code does not provide it. The optimized version's gains are attributable to the invariant list forcing explicit decisions on `timeout <= 0` and cross-thread use; the overhead ratio is inflated mainly by the 155-line test harness, which is a deliverable rather than ceremony.

---

## FINAL REPORT

### Summary Table

| Test | Domain                      | Task Type | Mode   | Baseline /25 | Optimized /25 | Delta | Words (B/O/Ratio)  | Winner    |
|------|-----------------------------|-----------|--------|--------------|---------------|-------|--------------------|-----------|
| 1    | Code Review                 | Accuracy  | Mode 1 | 24           | 24            | 0     | 453 / 785 / 1.73x  | Tie       |
| 2    | Financial Analysis          | Accuracy  | Mode 1 | 22           | 24            | +2    | 512 / 944 / 1.84x  | Optimized |
| 3    | Medical Reasoning           | Accuracy  | Mode 1 | 23           | 24            | +1    | 451 / 914 / 2.03x  | Optimized |
| 4    | Legal Analysis              | Accuracy  | Mode 1 | 21           | 24            | +3    | 687 / 1354 / 1.97x | Optimized |
| 5    | Research Synthesis          | Mixed     | Mode 1 | 20           | 22            | +2    | 489 / 1091 / 2.23x | Optimized |
| 6    | Business Decision           | Mixed     | Mode 1 | 21           | 24            | +3    | 541 / 1062 / 1.96x | Optimized |
| 7    | Compliance Check            | Accuracy  | Mode 1 | 24           | 24            | 0     | 519 / 909 / 1.75x  | Tie       |
| 8    | Document Analysis           | Mixed     | Mode 1 | 21           | 24            | +3    | 474 / 850 / 1.79x  | Optimized |
| 9    | Comparative Analysis        | Mixed     | Mode 2 | 22           | 24            | +2    | 456 / 416 / 0.91x  | Optimized |
| 10   | Creative Brief              | Creative  | Mode 4 | 19           | 21            | +2    | 201 / 395 / 1.97x  | Optimized |
| 11   | Context File (CLAUDE.md)    | Harness   | Mode 3 | 18           | 24            | +6    | 298 / 373 / 1.25x  | Optimized |
| 12   | Async Rate Limiter (LRM)    | Harness   | Mode 3 | 17           | 24            | +7    | 503 / 1285 / 2.55x | Optimized |
|      | **AVERAGE**                 |           |        | **21.00**    | **23.58**     | **+2.58** | **465 / 865 / 1.83x** (aggregate 1.86x) | **10W-2T-0L** |

Word counts are whitespace tokens of the response sections only (script-computed). The optimized prompts themselves averaged 363 words, versus roughly 20 to 80 words for the raw prompts.

**Per-dimension averages (all 12 tests):**

| Dimension     | Baseline avg | Optimized avg | Delta |
|---------------|--------------|---------------|-------|
| Accuracy      | 4.58         | 4.92          | +0.33 |
| Completeness  | 4.25         | 4.75          | +0.50 |
| Structure     | 4.58         | 4.17          | -0.42 |
| Actionability | 4.25         | 4.83          | +0.58 |
| Traceability  | 3.33         | 4.92          | +1.58 |

### 1. Overall Verdict

Yes, with qualifications. Across 12 tests the optimized responses averaged **23.58/25 vs. 21.00/25**, a gain of **+2.58 points (+12.3%)**, with 10 wins, 2 ties, and 0 losses, at an average response overhead of **1.83x** (plus a ~360-word prompt).

The headline number overstates the substantive gain. **19 of the 31 total gain points (61%) come from Traceability**, the dimension that most directly rewards the certificate format itself. Excluding Traceability, the average gain is **+1.0 point per test (+5.7%)**. Structure, the only dimension that measures cost, *fell* by 0.42 on average.

Is it worth the overhead? It depends sharply on the mode:
- **Mode 3 (Harness/LRM): clearly worth it.** +6.5 average, including the only cases where the baseline had real correctness defects (Test 12) or followed instructions into a known anti-pattern (Test 11).
- **Mode 2 (Lite): clearly worth it.** +2 at 0.91x, cheaper than the baseline.
- **Mode 1 (Max): worth it only when auditability is the point.** +1.75 average at 1.92x; on two of eight tests (code review, NIST check) it added nothing a strong model did not already produce.
- **Mode 4 (Creative v2): modest gain.** +2, better voice, but less usable as shipped.

Self-evaluation bias applies to every number here: I generated and scored both sides, knew which was which, and wrote the optimized prompts.

### 2. Where It Helped Most

1. **Test 12, async rate limiter (+7, Mode 3 LRM).** This is the strongest evidence in the suite because it is *executed*, not judged. The baseline passed 7/9 harness tests: `timeout=0` returned `False` with a full bucket (an `asyncio.wait_for` zero-timeout pitfall), and cross-thread use deadlocked. The optimized prompt's invariant list ([I4] timeout <= 0 semantics, [I1] "under calls from multiple threads") forced explicit design decisions on exactly those two points; the result passed 9/9. Converting "make sure there are no race conditions" into checkable invariants plus a harness is the single most valuable transformation observed.
2. **Test 11, CLAUDE.md (+6, Mode 3 `[CONTEXT-FILES]`).** The baseline obediently produced a directory tree, overview, and PEP 8 boilerplate, and invented an entrypoint. The optimized file is 30 lines vs. 64, contains only supplied commands, converts the SCHEMA_EPOCH prohibition into a checkable conditional, and flagged that `--reuse-db` is a pytest-django flag that needs a custom plugin in a FastAPI repo.
3. **Tests 4, 6, 8 (+3 each, Mode 1, legal / decision / document).** These share a pattern: the raw prompt asks for an open-ended judgment. The certificate's per-option or per-issue traces made implicit comparisons explicit (Test 6's four-option matrix), and the missing-evidence predicates produced conditional outcomes rather than hedged prose (Test 4's per-jurisdiction outcomes). Test 8's arithmetic-consistency instruction produced a genuinely new finding (300% ROI requires support spend of 8.9x to 17.8x the solution cost).

### 3. Where It Helped Least (or Hurt)

1. **Tests 1 and 7 (ties at 24/24).** A well-scoped bug hunt and a check against a well-known standard. The baseline found all seven bugs and all NIST deviations; the certificate added line citations and an UNABLE TO VERIFY distinction, and lost the same point back on Structure. This is a ceiling effect: when the base model already performs at ceiling, Mode 1 is pure overhead.
2. **Test 3, medical (+1).** The certificate added one substantive point (RV infarct vs. LV failure discriminator), but its trace-first layout buries the action list below ten traces. For a time-critical clinical question, a numbered priority list first is the better structure.
3. **Structure, in 10 of 12 tests.** The optimized response lost a Structure point in every Mode 1 test plus Test 10 and Test 12. The only Structure gains were Test 9 (Lite matrix) and Test 11 (minimal file). Nowhere did the optimized version lose on substance; the cost is readability and length.

### 4. v4.0 Mode Evaluation (Max vs. Lite vs. Harness vs. Creative v2)

- **Mode 2 Lite (Test 9): yes on both counts.** Overhead was **0.91x** (416 vs. 456 words), well under the 1.5x cap, and the score rose +2 (22 -> 24). The decision matrix with per-cell trace citations scanned faster than the baseline's prose. The 3-premise cap did cost one Completeness point (team-expertise and analytics-offload nuance were compressed). Lite fixed the v1.0 token-bloat problem in this test.
- **Mode 3 Harness/LRM (Tests 11-12): yes.** Test 11 prevented context bloat (30-line file, every command sourced, verification gate included; 1.25x response ratio, within the 1.1x to 1.3x claim). Test 12 prevented the two defects the baseline shipped, confirmed by execution. Test 12's 2.55x ratio exceeds the claimed 1.1x to 1.3x, but almost all of that is the 155-line test harness the prompt requested; the certificate itself (premises, seven V-gates, and disposition) was about 320 words.
- **Mode 4 Creative v2 (Test 10): improved voice and structural originality, with usability costs.** The baseline hit nearly every SlopShape marker (payoff headline, "most chairs" contrast, bullet recap, slogan close) and implied testimonials not in the brief. The optimized copy opened inside a concrete moment, introduced each feature at the hour it matters, and closed on an action ("Add twelve years. Write it on the box."), using only the three given facts in 199 words. But it dropped the scannable spec list product pages need, and the visible backstage block would have to be stripped before publication. Net +2.

### 5. Accuracy vs. Mixed vs. Creative vs. Harness

| Category | Tests | Baseline avg | Optimized avg | Delta |
|---|---|---|---|---|
| Accuracy | 1, 2, 3, 4, 7 | 22.8 | 24.0 | +1.2 |
| Mixed | 5, 6, 8, 9 | 21.0 | 23.5 | +2.5 |
| Creative | 10 | 19.0 | 21.0 | +2.0 |
| Harness | 11, 12 | 17.5 | 24.0 | +6.5 |

The gain is inversely related to baseline strength: accuracy tasks had the highest baselines and the smallest gains. **PRISM persona calibration could not be isolated** in this design: persona was varied together with the entire certificate, so no test measures persona alone. What can be said: omitting persona on accuracy tasks did no visible harm (accuracy held at 5 on all five), and the 5-word persona on mixed tasks produced no observable tone or accuracy effect. One inconsistency surfaced: the protocol labels Test 5 "Mixed" while Template 3 specifies OMIT; I followed the template.

### 6. Traceability Specifically

Traceability rose in all 12 tests: baseline average **3.33**, optimized **4.92** (+1.58), the largest dimension gain. The structures did make claims genuinely more traceable, not just better labeled, in three identifiable ways:
1. **Missing-evidence predicates** (`UNABLE TO TRACE`, `NOT ADDRESSED IN [P1]`, `INSUFFICIENT DATA`) separated "unknown" from "absent" (Test 7: storage is unverifiable, not non-compliant; Test 4: outcome per value of each missing fact).
2. **Counterexample predicates** surfaced findings the baselines skipped (Test 2's 84.7% decremental margin in Q2).
3. **Executable traces** (Test 12's V-gates map each invariant to a code construct and a passing test) are the strongest form: verifiable by a third party.

The caveat is measurement circularity: the rubric's Traceability column rewards visible citation structure, which is exactly what the certificate imposes. A blind judge or a rubric scoring "can a reader verify this claim" (rather than "is a claim tagged") would likely shrink this delta. Baselines in this run already cited sources and showed arithmetic, so baseline Traceability was rarely below 3.

### 7. Token Cost vs. Value

| Mode | Tests | Avg baseline words | Avg optimized words | Aggregate ratio | Avg score delta | Delta per 100 extra words |
|---|---|---|---|---|---|---|
| Mode 1 Max | 1-8 | 516 | 989 | 1.92x | +1.75 | 0.37 |
| Mode 2 Lite | 9 | 456 | 416 | 0.91x | +2.00 | n/a (cheaper) |
| Mode 3 Harness | 11-12 | 401 | 829 | 2.07x (1.25x and 2.55x) | +6.50 | 1.52 |
| Mode 4 Creative v2 | 10 | 201 | 395 | 1.97x | +2.00 | 1.03 |
| **All** | 1-12 | 465 | 865 | 1.86x (mean of ratios 1.83x) | +2.58 | 0.65 |

Mode 1's observed 1.92x response overhead is close to the skill's claimed ~2.2x and delivers the least value per extra word. Mode 2 was the only mode that reduced length. Mode 3's ratio varies with the deliverable (a context file shrinks; a code task grows because a test harness is added) and delivered the most value per word. All modes also carry the cost of the optimized prompt itself (215 to 445 words, average 363).

### 8. Failure Modes Observed

1. **Ceremony on small, well-scoped tasks.** Test 1 produced eleven execution traces for a seven-line function; Test 7 produced nine compliance traces that restated a single table. Both tied.
2. **Trace-first ordering in time-critical domains.** Test 3 places the actionable priority list after ten traces.
3. **Template remediation mismatch.** Template 8 mandates "redline clause revisions", which does not fit a dispute over an already-signed contract (Test 4). I reframed it as a narrowing proposal; a literal model would produce an irrelevant redline.
4. **Literal-request conflict in Mode 3 Pattern B.** Test 11's user explicitly asked for an overview, folder structure, and PEP 8 conventions. The skill strips them silently; it has no rule for telling the user why or offering them separately.
5. **Mode 4 deliverable not shippable as-is.** The backstage block is printed with the copy, and the Structural Rarity Contract has no provision for commerce formats that need a scannable feature list.
6. **Spec inconsistencies across the skill and the benchmark protocol.**
   - Template numbering in the protocol does not match `domain-templates.md` (Financial is 9, not 2; Decision is 5, not 6; Creative is 12, not 10; there is no Template 12 `[HARNESS]`).
   - The identifier families `[F]`, `[O]`, `[R]`, `[C]`, `[D]`, `[E]`, `[L]`, `[S]`, `[SC0]` do not exist in the skill.
   - Verbalized Sampling parameters appear three ways: 3 candidates at p < 0.15 (protocol), 4 angles at p <= 0.20 (`SKILL.md`, Template 12), 3 to 5 candidates at p < 0.25 (`research-principles.md`).
   - Mode 3 Pattern A (LRM) exists only in `SKILL.md`, with no numbered template in `domain-templates.md`, although it produced the largest gain.
7. **Lite compression loses nuance.** Test 9 lost a Completeness point from the 3-premise cap.
8. **Evaluation-design artifacts.** Single non-blind rater; Traceability is format-sensitive; persona effects are confounded with certificate effects.

### 9. Recommendations for v4.1 Skill Improvement

1. **Add a ceiling-check routing predicate to Step 1b** (`SKILL.md`): "When the artifact under review is under ~30 lines of code, or the reference standard is a single well-known specification, select Mode 2 Lite." Evidence: Tests 1 and 7 tied under Max.
2. **Make Lite the default for Mixed tasks; reserve Max for high-stakes auditability.** Evidence: Test 9 gained +2 at 0.91x, while Mode 1 gained +1.75 at 1.92x.
3. **Promote Mode 3 Pattern A to a numbered Template 13 ("Agentic Coding / LRM Verification")** in `domain-templates.md`, with three required parts: an invariant list `[I1]`-`[In]` covering boundary values (zero, negative, over-capacity), concurrency, and cancellation; V-gates mapping each invariant to a code construct; an executable stdlib-only harness with one test per invariant. Evidence: Test 12 (+7, executed 9/9 vs. 7/9).
4. **Add a literal-request disclosure rule to Template 11:** "When the user explicitly requests a section that Minimal Viable Context omits, deliver the minimal file and add one line outside the file naming the omitted sections and the `[CONTEXT-FILES]` rationale." Evidence: Test 11.
5. **Add a deliverable-first ordering option to Templates 7 and 1:** "When the task is time-critical or the deliverable is a patch, place FORMAL CONCLUSION and REMEDIATION first and the traces after them as an appendix." Evidence: Test 3 Structure penalty.
6. **Branch the Template 8 remediation:** drafting or review -> redlines; dispute over a signed agreement -> fact-gathering checklist and option list. Evidence: Test 4.
7. **Add two output predicates to Template 12:** "When the deliverable is publication copy, enclose the backstage block in `<backstage>` tags or omit it" and "When the medium is a product or commerce page, append a scannable facts block after the narrative." Evidence: Test 10.
8. **Harmonize Verbalized Sampling parameters** across `SKILL.md`, `domain-templates.md`, and `research-principles.md` (recommend 4 angles, selection at p <= 0.20) and update the benchmark protocol to match.
9. **Fix the benchmark protocol (`EVALUATION_PROMPT_V4.md`)** so template numbers and identifier families match `domain-templates.md`. Split Traceability into "tagged" vs. "independently verifiable", and add a blind or cross-model judging pass so format-driven gains can be separated from substantive ones.
10. **Resolve the Research Synthesis persona conflict:** either reclassify Test 5 as Accuracy in the protocol or allow a minimal persona in Template 3 for mixed synthesis tasks.
