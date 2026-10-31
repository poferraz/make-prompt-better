# EVALUATION RESULTS: make-prompt-better v4.0 (deepseek-v4.1-flash:1017-cloud)

- **Model**: `deepseek-v4.1-flash:1017-cloud`
- **Timestamp**: `2026-10-30T05:23:33Z`
- **Protocol**: 12-Test v4.0 Isolated Context Pipeline (Baseline -> Optimize Prompt -> Execute Optimized -> Rubric Evaluation)

## TEST 1: Code Review (Accuracy | Mode 1 (Max Certificate, Template 1 [P1]-[P3]))

### BASELINE RESPONSE

Yes—assuming `discount_percent` is meant to be a percentage like `20` for 20%, the main bug is that the function never divides by 100:

```python
final_price = price - (price * discount_percent)
```

So if `price=100` and `discount_percent=20`, it computes:

```python
100 - (100 * 20) == -1900
```

Then the `final_price < 0` check returns `0`, hiding the bug.

Corrected version:

```python
def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 10

    # Optional: cap the discount at 100%
    discount_percent = min(discount_percent, 100)

    final_price = price - (price * discount_percent / 100)

    if final_price < 0:
        return 0

    return final_price
```

So for `price=100`, `discount_percent=20`, `is_member=True`, this returns `70.0`.

Also, if `discount_percent` is intended to be a decimal fraction like `0.20`, then the bug is different: `discount_percent += 10` should be `discount_percent += 0.10`. But based on the name, it probably should be treated as a whole-number percentage and divided by 100.

### OPTIMIZED PROMPT

````markdown
The standard code review protocol requires completing the following analytical certificate before issuing any verdict. Complete every section from observable code artifacts in [P1]-[P3], and ground every conclusion claim in [T] identifiers. The response consists solely of the sections below, in order.

### PREMISES
- [P1] Artifact under review: the Python function `calculate_discount(price, discount_percent, is_member)`, treated as the complete artifact:
```python
def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 10
    final_price = price - (price * discount_percent)
    if final_price < 0:
        return 0
    return final_price
```
- [P2] Review scope: behavioral correctness across all reachable branches — discount arithmetic, unit consistency of `discount_percent`, boundary and sign handling for `price` and `discount_percent`, return-value contract, input-type handling, and caller-visible mutation of `discount_percent`.
- [P3] Assumptions requiring explicit labels before tracing: numeric domain of `price` (non-negative currency vs. arbitrary numeric), unit and permitted range of `discount_percent` (fraction in [0,1] vs. percentage points in [0,100] vs. unbounded), whether `is_member` is strictly `bool`, and the intended handling of `None`, non-numeric, `NaN`, and infinite inputs. Record each as `ASSUMED: [statement]`, and mark any trace that depends on one as `PARTIAL`.

### EXECUTION TRACES
Produce numbered traces covering at minimum: (a) `is_member=True` with representative numeric input; (b) `is_member=False` with the same input; (c) `discount_percent` at 0, at the value driving `final_price` exactly to 0, above that value, and negative; (d) `price` at 0, negative, and non-finite (`NaN`, `inf`) where the language permits; (e) `None` and non-numeric arguments; (f) truthy non-`bool` values for `is_member`; (g) caller-visible mutation of `discount_percent`. Use this per-trace structure:

- [T1] Case: `<case name and branch condition>`
  1. Entry: exact argument values and types.
  2. Operations: evaluate each expression in order — `discount_percent += 10` (when the branch executes), `price * discount_percent`, `price - (...)`, and `final_price < 0` — citing the specific line or expression for each step.
  3. Data flow & state: computed intermediate values, the effective discount rate applied, and whether the caller's `discount_percent` binding is observable as changed after the call.
  4. Exit: returned value or raised exception with its type.
  5. Status: `VERIFIED`, `PARTIAL (assumption from [P3]: ...)`, or `UNABLE TO TRACE: [missing artifact]`.
- [T2] ... (continue until every branch, boundary, and input class listed above has a trace)

Grounding rule: Trace the actual expressions in [P1] using exact arithmetic rather than inferring behavior from parameter names. When `[P3]` leaves the unit of `discount_percent` open, evaluate both fraction and percentage-point interpretations and record each outcome as a separate sub-trace. When a behavior depends on a symbol, library, or type outside `[P1]-[P3]`, record `UNABLE TO TRACE: [missing artifact]` in that trace and list it under Verification Gaps.

### FORMAL CONCLUSION
- Verdict: `PASS` | `FAIL` | `UNABLE TO DETERMINE`.
- Defects: numbered list; each item cites at least one [T] identifier, quotes the exact expression, states observed behavior versus expected behavior, and assigns severity `HIGH` | `MEDIUM` | `LOW` with justification grounded in the trace.
- Expected behavior: state the arithmetic contract implied by the parameter names and `[P3]`, labeled `CONTRACT ASSUMPTION: [statement]` where no external specification exists.
- Supporting traces: cite every [T] identifier that supports the verdict, including traces that passed.
- Verification gaps: list every trace marked `UNABLE TO TRACE` or `PARTIAL` and the exact missing artifact or specification required to close it.
- Confidence: `HIGH` | `MEDIUM` | `LOW` with justification tied to [T] identifiers.

### REMEDIATION / NEXT ACTION
- When one or more [T] traces confirm a defect, provide (a) a complete, copy-pasteable patched function preserving the original signature and (b) at least one executable assertion per defect, in pytest or plain `assert` form, that fails on the original function and passes on the patch.
- When all [T] traces pass, state `No remediation required: [reason citing T-identifiers]` and supply regression assertions covering the boundary cases traced in [T].
- When a Verification Gap remains, provide the exact additional artifact, type specification, or command needed to resolve it, and provide a patch conditional on each plausible resolution.

### VERIFICATION & TRACEABILITY CONTRACT
- Grounding predicate: Every step in a [T] trace cites an explicit expression from [P1].
- Missing-evidence predicate: When a path cannot be verified from `[P1]-[P3]`, record `UNABLE TO TRACE: [exact missing input]` in that trace and list it under Verification Gaps.
- Counterexample predicate: When a boundary case, exception path, or disconfirming result appears in `[P1]-[P3]`, record it as a dedicated [T] trace even when the overall verdict is `PASS`.
- Assumption predicate: When a trace depends on an `ASSUMED` item from `[P3]`, mark the trace `PARTIAL` and restate the assumption inline.
- Neutrality predicate: Derive the verdict strictly from [T] traces without reference to downstream business goals, timelines, or evaluation rubrics.
- Self-check before finalizing: Verify that every claim in the Formal Conclusion cites at least one [T] identifier. For any claim lacking a supporting identifier, either add the missing trace from `[P1]-[P3]` or remove the claim so zero orphaned conclusions remain.
````

### OPTIMIZED RESPONSE

### PREMISES
- [P1] Reviewed artifact: `calculate_discount(price, discount_percent, is_member)` exactly as supplied.
- [P2] Scope: behavioral correctness across arithmetic, units, boundaries, signs, return contract, input types, and caller-visible mutation.
- [P3] Assumptions:
  - `ASSUMED A1`: `price` is intended as non-negative finite currency for normal contract; negative/NaN/inf are outside normal use but traced.
  - `ASSUMED A2`: unit and permitted range of `discount_percent` are unspecified; I evaluate both fraction-in-`[0,1]` and percentage-points-in-`[0,100]` interpretations separately.
  - `ASSUMED A3`: `is_member` is intended to be strictly `bool`; truthy non-`bool` values are traced for observed Python behavior.
  - `ASSUMED A4`: intended handling of `None`, non-numeric, `NaN`, and infinite inputs is unspecified; observed behavior is traced and gaps are listed.

### EXECUTION TRACES
- [T1] Case: fraction interpretation, `is_member=True`, representative input.
  1. Entry: `price=100.0` float, `discount_percent=0.2` float, `is_member=True` bool.
  2. Operations: `if is_member:` → True; `discount_percent += 10` → local `10.2`; `price * discount_percent` → `100.0 * 10.2 = 1020.0`; `price - (price * discount_percent)` → `100.0 - 1020.0 = -920.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: local effective multiplier is `10.2`; caller’s float binding remains `0.2`; under fraction contract this is not a 10-percentage-point member bonus.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A2: discount_percent interpreted as fraction [0,1] for expected comparison)`.

- [T2] Case: fraction interpretation, `is_member=False`, same input as T1.
  1. Entry: `price=100.0` float, `discount_percent=0.2` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False, skip `discount_percent += 10`; `price * discount_percent` → `100.0 * 0.2 = 20.0`; `price - (price * discount_percent)` → `100.0 - 20.0 = 80.0`; `if final_price < 0:` → `80.0 < 0` False; `return final_price`.
  3. Data flow & state: effective discount multiplier `0.2`; caller’s float binding remains `0.2`.
  4. Exit: returns `80.0`.
  5. Status: `PARTIAL (assumption A2: fraction interpretation [0,1])`.

- [T3] Case: percentage-point interpretation, `is_member=True`, representative input.
  1. Entry: `price=100.0` float, `discount_percent=20.0` float, `is_member=True` bool.
  2. Operations: `if is_member:` → True; `discount_percent += 10` → local `30.0`; `price * discount_percent` → `100.0 * 30.0 = 3000.0`; `price - (price * discount_percent)` → `100.0 - 3000.0 = -2900.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: local effective discount is `30.0` percentage points under A2, but multiplication treats `30.0` as a direct multiplier; caller’s float binding remains `20.0`.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A2: percentage-point interpretation [0,100])`.

- [T4] Case: percentage-point interpretation, `is_member=False`, same input as T3.
  1. Entry: `price=100.0` float, `discount_percent=20.0` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False, skip `discount_percent += 10`; `price * discount_percent` → `100.0 * 20.0 = 2000.0`; `price - (price * discount_percent)` → `100.0 - 2000.0 = -1900.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: effective discount is `20.0` percentage points under A2, but multiplication treats `20.0` as a direct multiplier; caller’s float binding remains `20.0`.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A2: percentage-point interpretation [0,100])`.

- [T5] Case: `discount_percent=0`, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent=0.0` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * 0.0 = 0.0`; `price - (price * discount_percent)` → `100.0 - 0.0 = 100.0`; `if final_price < 0:` → False; `return final_price`.
  3. Data flow & state: effective discount `0.0`; caller’s float binding remains `0.0`.
  4. Exit: returns `100.0`.
  5. Status: `VERIFIED`.

- [T6] Case: fraction boundary where `final_price` is exactly `0`, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent=1.0` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * 1.0 = 100.0`; `price - (price * discount_percent)` → `100.0 - 100.0 = 0.0`; `if final_price < 0:` → False; `return final_price`.
  3. Data flow & state: effective multiplier `1.0`; caller’s float binding remains `1.0`.
  4. Exit: returns `0.0`.
  5. Status: `PARTIAL (assumption A2: fraction boundary [0,1])`.

- [T7] Case: fraction value above boundary, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent=1.5` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * 1.5 = 150.0`; `price - (price * discount_percent)` → `100.0 - 150.0 = -50.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: effective multiplier `1.5`; caller’s float binding remains `1.5`.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A2: fraction range above [0,1])`.

- [T8] Case: negative fraction `discount_percent`, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent=-0.2` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * -0.2 = -20.0`; `price - (price * discount_percent)` → `100.0 - (-20.0) = 120.0`; `if final_price < 0:` → False; `return final_price`.
  3. Data flow & state: effective multiplier `-0.2`; caller’s float binding remains `-0.2`.
  4. Exit: returns `120.0`.
  5. Status: `PARTIAL (assumption A2: negative fraction is outside [0,1])`.

- [T9] Case: percentage-point boundary at `100`, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent=100.0` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * 100.0 = 10000.0`; `price - (price * discount_percent)` → `100.0 - 10000.0 = -9900.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: effective percentage-point discount is `100.0` under A2, but multiplication treats it as a direct multiplier; caller’s float binding remains `100.0`.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A2: percentage-point boundary [0,100])`.

- [T10] Case: percentage-point value above boundary, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent=150.0` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * 150.0 = 15000.0`; `price - (price * discount_percent)` → `100.0 - 15000.0 = -14900.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: effective percentage-point discount is `150.0` under A2; caller’s float binding remains `150.0`.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A2: percentage-point range above [0,100])`.

- [T11] Case: negative percentage-point `discount_percent`, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent=-20.0` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * -20.0 = -2000.0`; `price - (price * discount_percent)` → `100.0 - (-2000.0) = 2100.0`; `if final_price < 0:` → False; `return final_price`.
  3. Data flow & state: effective percentage-point discount is `-20.0` under A2; caller’s float binding remains `-20.0`.
  4. Exit: returns `2100.0`.
  5. Status: `PARTIAL (assumption A2: negative percentage points outside [0,100])`.

- [T12] Case: `price=0`, `is_member=False`.
  1. Entry: `price=0.0` float, `discount_percent=0.2` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `0.0 * 0.2 = 0.0`; `price - (price * discount_percent)` → `0.0 - 0.0 = 0.0`; `if final_price < 0:` → False; `return final_price`.
  3. Data flow & state: effective multiplier `0.2`; caller’s float binding remains `0.2`.
  4. Exit: returns `0.0`.
  5. Status: `VERIFIED`.

- [T13] Case: negative `price`, `is_member=False`.
  1. Entry: `price=-100.0` float, `discount_percent=0.2` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `-100.0 * 0.2 = -20.0`; `price - (price * discount_percent)` → `-100.0 - (-20.0) = -80.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: effective multiplier `0.2`; caller’s float binding remains `0.2`.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A1: negative price is outside intended non-negative currency domain)`.

- [T14] Case: negative `price` with discount above 100%, `is_member=False`.
  1. Entry: `price=-100.0` float, `discount_percent=1.5` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `-100.0 * 1.5 = -150.0`; `price - (price * discount_percent)` → `-100.0 - (-150.0) = 50.0`; `if final_price < 0:` → False; `return final_price`.
  3. Data flow & state: effective multiplier `1.5`; caller’s float binding remains `1.5`.
  4. Exit: returns `50.0`.
  5. Status: `PARTIAL (assumption A1: negative price domain unspecified)`.

- [T15] Case: `price=NaN`, `is_member=False`.
  1. Entry: `price=float('nan')`, `discount_percent=0.2` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `nan`; `price - (price * discount_percent)` → `nan - nan = nan`; `if final_price < 0:` → `nan < 0` False; `return final_price`.
  3. Data flow & state: final value propagates `NaN`; caller’s float binding remains `0.2`.
  4. Exit: returns `nan`.
  5. Status: `PARTIAL (assumption A4: NaN handling unspecified)`.

- [T16] Case: `price=inf`, `is_member=False`.
  1. Entry: `price=float('inf')`, `discount_percent=0.2` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `inf`; `price - (price * discount_percent)` → `inf - inf = nan`; `if final_price < 0:` → `nan < 0` False; `return final_price`.
  3. Data flow & state: final value is `NaN`; caller’s float binding remains `0.2`.
  4. Exit: returns `nan`.
  5. Status: `PARTIAL (assumption A4: infinite input handling unspecified)`.

- [T17] Case: `price=None`, `is_member=False`.
  1. Entry: `price=None`, `discount_percent=0.2` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `None * 0.2` raises `TypeError`; later expressions are not reached.
  3. Data flow & state: no `final_price` assigned; caller’s float binding remains `0.2`.
  4. Exit: raises `TypeError`.
  5. Status: `PARTIAL (assumption A4: None handling unspecified)`.

- [T18] Case: `discount_percent=None`, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent=None`, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * None` raises `TypeError`; later expressions are not reached.
  3. Data flow & state: no `final_price` assigned; caller binding remains `None`.
  4. Exit: raises `TypeError`.
  5. Status: `PARTIAL (assumption A4: None handling unspecified)`.

- [T19] Case: `discount_percent=None`, `is_member=True`.
  1. Entry: `price=100.0` float, `discount_percent=None`, `is_member=True` bool.
  2. Operations: `if is_member:` → True; `discount_percent += 10` → `None + 10` raises `TypeError`; later expressions are not reached.
  3. Data flow & state: no local update completed; caller binding remains `None`.
  4. Exit: raises `TypeError`.
  5. Status: `PARTIAL (assumption A4: None handling unspecified)`.

- [T20] Case: non-numeric `price` string, `is_member=False`.
  1. Entry: `price="100"` str, `discount_percent=0.2` float, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `"100" * 0.2` raises `TypeError`; later expressions are not reached.
  3. Data flow & state: no `final_price` assigned; caller’s float binding remains `0.2`.
  4. Exit: raises `TypeError`.
  5. Status: `PARTIAL (assumption A4: non-numeric handling unspecified)`.

- [T21] Case: non-numeric `discount_percent` string, `is_member=False`.
  1. Entry: `price=100.0` float, `discount_percent="0.2"` str, `is_member=False` bool.
  2. Operations: `if is_member:` → False; `price * discount_percent` → `100.0 * "0.2"` raises `TypeError`; later expressions are not reached.
  3. Data flow & state: no `final_price` assigned; caller binding remains `"0.2"`.
  4. Exit: raises `TypeError`.
  5. Status: `PARTIAL (assumption A4: non-numeric handling unspecified)`.

- [T22] Case: non-numeric `discount_percent` string, `is_member=True`.
  1. Entry: `price=100.0` float, `discount_percent="0.2"` str, `is_member=True` bool.
  2. Operations: `if is_member:` → True; `discount_percent += 10` → `"0.2" + 10` raises `TypeError`; later expressions are not reached.
  3. Data flow & state: no local update completed; caller binding remains `"0.2"`.
  4. Exit: raises `TypeError`.
  5. Status: `PARTIAL (assumption A4: non-numeric handling unspecified)`.

- [T23] Case: truthy non-`bool` `is_member` string.
  1. Entry: `price=100.0` float, `discount_percent=0.2` float, `is_member="yes"` str.
  2. Operations: `if is_member:` → True by truthiness; `discount_percent += 10` → local `10.2`; `price * discount_percent` → `1020.0`; `price - (price * discount_percent)` → `-920.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: local effective multiplier `10.2`; caller’s float binding remains `0.2`.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A3: is_member intended strictly bool; truthy non-bool policy unspecified)`.

- [T24] Case: truthy non-`bool` `is_member` integer.
  1. Entry: `price=100.0` float, `discount_percent=0.2` float, `is_member=1` int.
  2. Operations: `if is_member:` → True by truthiness; `discount_percent += 10` → local `10.2`; `price * discount_percent` → `1020.0`; `price - (price * discount_percent)` → `-920.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: local effective multiplier `10.2`; caller’s float binding remains `0.2`.
  4. Exit: returns `0` int.
  5. Status: `PARTIAL (assumption A3: strict bool policy unspecified)`.

- [T25] Case: caller-visible mutation of `discount_percent`, float.
  1. Entry: caller variable `discount_percent=0.2` float; call `calculate_discount(100.0, discount_percent, True)`.
  2. Operations: `if is_member:` → True; `discount_percent += 10` → local parameter rebinds to `10.2`; `price * discount_percent` → `1020.0`; `price - (price * discount_percent)` → `-920.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: local parameter is `10.2`; Python `float` is immutable, so caller variable remains `0.2`.
  4. Exit: returns `0`; after call caller `discount_percent == 0.2`.
  5. Status: `VERIFIED`.

- [T26] Case: caller-visible mutation of `discount_percent`, int.
  1. Entry: caller variable `discount_percent=20` int; call `calculate_discount(100.0, discount_percent, True)`.
  2. Operations: `if is_member:` → True; `discount_percent += 10` → local parameter rebinds to `30`; `price * discount_percent` → `3000.0`; `price - (price * discount_percent)` → `-2900.0`; `if final_price < 0:` → True; `return 0`.
  3. Data flow & state: local parameter is `30`; Python `int` is immutable, so caller variable remains `20`.
  4. Exit: returns `0`; after call caller `discount_percent == 20`.
  5. Status: `VERIFIED`.

### FORMAL CONCLUSION
- Verdict: `FAIL`.
- Defects:
  1. `HIGH` — Unit inconsistency between `discount_percent += 10` and `final_price = price - (price * discount_percent)`. Under fraction reading, T1 (`price=100.0`, `discount_percent=0.2`, `is_member=True`) returns `0` but a 10-point member bonus implies `70.0`; under percentage-point reading, T4 (`price=100.0`, `discount_percent=20.0`, `is_member=False`) returns `0` but a 20% discount implies `80.0`. The increment and arithmetic do not share a consistent percent unit.
  2. `MEDIUM` — Negative `discount_percent` silently raises price through `final_price = price - (price * discount_percent)`. T8 (`discount_percent=-0.2`) returns `120.0` for `price=100.0`; T11 (`discount_percent=-20.0`) returns `2100.0`. Expected under `[0,1]` or `[0,100]` contract: reject or clamp so price is not increased.
  3. `MEDIUM` — Non-finite `price` propagates `NaN` through `final_price = price - (price * discount_percent)` and `if final_price < 0:`. T15 (`price=NaN`) returns `nan`; T16 (`price=inf`) returns `nan` because `inf - inf = nan` and `nan < 0` is false. Expected under finite-currency contract: reject or handle explicitly.
  4. `LOW` — Truthy non-`bool` `is_member` is accepted by `if is_member:`. T23 (`is_member="yes"`) and T24 (`is_member=1`) execute the member branch instead of raising or following a strict-bool policy. Expected under A3: reject non-`bool` or document truthiness.

- Expected behavior:
  - `CONTRACT ASSUMPTION`: `price` is non-negative finite currency; `discount_percent` is percentage points in `[0,100]`; `is_member` is strictly `bool`; membership adds 10 percentage points; final price is `max(0, price * (1 - (discount_percent + (10 if is_member else 0)) / 100))`; invalid types/ranges are rejected or explicitly documented. This is implied by the name `discount_percent`; no external specification exists in `[P1]-[P3]`. Current deviations are shown by T1, T3, T4, T8, T11, T15, T16, T23, and T24.

- Supporting traces: T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26.

- Verification gaps:
  - `A2` unit/range missing: T1-T4, T6-T11 are `PARTIAL`. Required artifact: external specification of `discount_percent` unit (fraction `[0,1]` vs percentage points `[0,100]` vs other), permitted range, and desired behavior for negative or >100% values.
  - `A1` price domain missing: T13-T14 are `PARTIAL`. Required artifact: intended `price` domain and expected behavior for negative price.
  - `A4` input handling missing: T15-T22 are `PARTIAL`. Required artifact: intended handling for `NaN`, `inf`, `None`, and non-numeric inputs: raise, clamp, or return sentinel.
  - `A3` `is_member` type policy missing: T23-T24 are `PARTIAL`. Required artifact: whether `is_member` must be strictly `bool` and whether truthy non-`bool` values should be accepted or rejected.
  - No `UNABLE TO TRACE` traces.

- Confidence: `MEDIUM`. T1 and T4 confirm a unit inconsistency under both plausible `discount_percent` units; T25-T26 confirm no caller-visible mutation for `float`/`int`. Confidence is not `HIGH` because T15-T24 depend on missing `[P3]` specifications for input handling and strict typing.

### REMEDIATION / NEXT ACTION
Required additional artifact: an external specification or tests defining `discount_percent` unit/range, `price` domain, `is_member` strictness, and handling of `None`/`NaN`/`inf`/non-numeric inputs. Conditional patches follow for the two plausible unit resolutions.

Percentage-point contract patch:
```python
import math

def calculate_discount(price, discount_percent, is_member):
    if not isinstance(is_member, bool):
        raise TypeError("is_member must be bool")
    if isinstance(price, bool) or isinstance(discount_percent, bool):
        raise TypeError("price and discount_percent must be numeric, not bool")
    if not isinstance(price, (int, float)) or not isinstance(discount_percent, (int, float)):
        raise TypeError("price and discount_percent must be numbers")
    if not math.isfinite(price) or not math.isfinite(discount_percent):
        raise ValueError("price and discount_percent must be finite")
    if price < 0:
        raise ValueError("price must be non-negative")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be in [0, 100]")

    effective_discount_percent = discount_percent + (10 if is_member else 0)
    final_price = price - (price * effective_discount_percent / 100.0)
    if final_price < 0:
        return 0
    return final_price
```

Assertions for percentage-point patch:
```python
import pytest

assert calculate_discount(100.0, 20, False) == 80.0  # fails original: returns 0
assert calculate_discount(100.0, 20, True) == 70.0   # fails original: returns 0

with pytest.raises(ValueError):
    calculate_discount(100.0, -20, False)  # fails original: returns 2100.0

with pytest.raises(ValueError):
    calculate_discount(float('nan'), 20, False)  # fails original: returns nan
with pytest.raises(ValueError):
    calculate_discount(float('inf'), 20, False)  # fails original: returns nan

with pytest.raises(TypeError):
    calculate_discount(100.0, 20, "yes")  # fails original: returns 0
```

Fraction contract patch:
```python
import math

def calculate_discount(price, discount_percent, is_member):
    if not isinstance(is_member, bool):
        raise TypeError("is_member must be bool")
    if isinstance(price, bool) or isinstance(discount_percent, bool):
        raise TypeError("price and discount_percent must be numeric, not bool")
    if not isinstance(price, (int, float)) or not isinstance(discount_percent, (int, float)):
        raise TypeError("price and discount_percent must be numbers")
    if not math.isfinite(price) or not math.isfinite(discount_percent):
        raise ValueError("price and discount_percent must be finite")
    if price < 0:
        raise ValueError("price must be non-negative")
    if discount_percent < 0 or discount_percent > 1:
        raise ValueError("discount_percent must be in [0, 1]")

    effective_discount = discount_percent + (0.10 if is_member else 0.0)
    final_price = price - (price * effective_discount)
    if final_price < 0:
        return 0
    return final_price
```

Assertions for fraction patch:
```python
import pytest

assert calculate_discount(100.0, 0.2, True) == 70.0  # fails original: returns 0

with pytest.raises(ValueError):
    calculate_discount(100.0, -0.2, False)  # fails original: returns 120.0

with pytest.raises(ValueError):
    calculate_discount(float('nan'), 0.2, False)  # fails original: returns nan

with pytest.raises(TypeError):
    calculate_discount(100.0, 0.2, "yes")  # fails original: returns 0
```

### EVALUATION: TEST 1

- **Word Count**: Baseline `151` words | Optimized `2909` words | Ratio `19.26x`
- **Eval Tokens**: Baseline `1019` | Optimized `30133`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | +0    |
| Completeness  | 4        | 5         | +1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 5        | 5         | +0    |
| Traceability  | 4        | 5         | +1    |
| TOTAL         | 23/25    | 24/25     | +1    |

The optimized response improved completeness and traceability by systematically tracing branches, boundary cases, type handling, and mutation, and it added conditional patches with assertions. Accuracy stayed high for both, but the optimized response’s certificate structure introduced significant bloat for a simple code review and omitted the final verification/contract section, so Structure was slightly penalized.

---

## TEST 2: Financial Analysis (Accuracy | Mode 1 (Max Certificate, Template 2 [F1]-[F3]))

### BASELINE RESPONSE

Assuming “operating expenses” are the total operating costs deducted from revenue, the company’s reported operating performance is **positive and improving**, but the analysis is incomplete without cash flow, balance sheet, existing debt, interest terms, taxes, and capex.

| Quarter | Revenue | Opex % | Opex $ | Operating Income | Operating Margin |
|---|---:|---:|---:|---:|---:|
| Q1 | $50.0M | 78% | $39.0M | $11.0M | 22.0% |
| Q2 | $47.0M | 82% | $38.54M | $8.46M | 18.0% |
| Q3 | $52.0M | 75% | $39.0M | $13.0M | 25.0% |
| Q4 | $61.0M | 71% | $43.31M | $17.69M | 29.0% |
| **FY** | **$210.0M** | **76.1%** | **$159.85M** | **$50.15M** | **23.9%** |

### Key takeaways
- **Profitable every quarter:** Operating income was positive throughout, totaling **$50.15M** for the year.
- **Q2 was the weak point:** Revenue fell 6% QoQ and opex rose to 82% of revenue, compressing operating margin to 18%.
- **Strong H2 recovery:** Q3 margin rose to 25%, and Q4 reached 29%. Q4 revenue grew **17.3% QoQ**, and operating income grew **36.1% QoQ**.
- **Cost control improved:** Opex ratio fell from 82% in Q2 to 75% in Q3 and 71% in Q4.
- **H2 profitability much stronger:** H2 operating margin was about **27.2%** vs. **20.1%** in H1.

### Debt analysis
The company added **$15M of new debt in Q3**. Relative to reported operating results:
- Debt / FY revenue ≈ **7.1%**
- Debt / FY operating income ≈ **0.30x**
- Using Q4 annualized operating income of ~$70.8M, debt / operating income ≈ **0.21x**

If this is the only debt and interest rates are normal, coverage looks very strong: at, say, 6–8% interest, annual interest would be ~$0.9–1.2M, covered many times by operating income. However, **existing debt, maturity schedule, covenants, interest rate, and cash needs are unknown**.

### Overall assessment
On the provided data, financial health looks **favorable/improving**: revenue growth finished strong, operating margins expanded materially in H2, and the company remained operating-profitable all year. The $15M debt appears manageable relative to revenue and operating income **if it is not incremental to a larger existing debt load**.

Main risks to monitor: the Q2 margin compression, whether Q4 strength is seasonal, the high absolute opex ratio, and debt-service/liquidity details not provided. Overall: **positive operating trend, moderate leverage risk based on limited data, but need full balance sheet and cash flow to confirm financial health.**

### OPTIMIZED PROMPT

The standard financial analysis protocol requires completing the following reasoning certificate before issuing any posture assessment. Complete every section using only the reported figures supplied below. Show the arithmetic for every derived figure in $M to two decimal places, and cite `[F]` and `[T]` identifiers at each step.

### PREMISES

- [F1] Reported quarterly revenue, fiscal Year N ($M): Q1 = 50.00; Q2 = 47.00; Q3 = 52.00; Q4 = 61.00.
- [F2] Reported operating expenses as a percentage of revenue, same quarters: Q1 = 78%; Q2 = 82%; Q3 = 75%; Q4 = 71%.
- [F3] Financing event: $15.00M of new debt was raised in Q3. Terms, coupon, maturity, covenants, and use of proceeds are not disclosed.
- [F4] Definitional scope of "operating expenses" in [F2] is not stated. Whether it includes depreciation, amortization, stock-based compensation, one-time items, or interest expense is unresolved.
- [F5] Absent from the supplied data and therefore treated as unverified environmental assumptions: cost of goods sold / gross margin, cash flow statement, balance sheet (cash, total debt, equity), prior-year comparatives, segment mix, customer concentration, seasonality baseline, and the company's sector or size.

### EVIDENCE TRACES

- [T1] Revenue trajectory — compute quarter-over-quarter absolute and percentage change, plus full-year total.
  1. Q1 → Q2: 47.00 − 50.00 = −3.00 → −3.00 / 50.00 = −6.00%.
  2. Q2 → Q3: 52.00 − 47.00 = +5.00 → +5.00 / 47.00 = +10.64%.
  3. Q3 → Q4: 61.00 − 52.00 = +9.00 → +9.00 / 52.00 = +17.31%.
  4. Q1 → Q4 net change: 61.00 − 50.00 = +11.00 → +22.00%.
  5. Full-year revenue: 50.00 + 47.00 + 52.00 + 61.00 = 210.00.
  6. Shape classification: [T1.1] records a single sequential decline; [T1.2]–[T1.3] record two consecutive accelerations. State whether the observed path is monotonic, V-shaped, or seasonal-pattern-indeterminate, and cite which sub-trace supports that label.

- [T2] Operating expense conversion — convert [F2] percentages into dollar amounts and reconcile against [F1].
  1. Q1: 0.78 × 50.00 = 39.00.
  2. Q2: 0.82 × 47.00 = 38.54.
  3. Q3: 0.75 × 52.00 = 39.00.
  4. Q4: 0.71 × 61.00 = 43.31.
  5. Full-year operating expenses: 39.00 + 38.54 + 39.00 + 43.31 = 159.85.
  6. Full-year blended expense ratio: 159.85 / 210.00 = 76.12%.
  7. Observe that Q1 and Q3 expense dollars are identical (39.00) despite a $2.00M revenue difference; state what this implies about fixed-versus-variable cost structure under [F5].

- [T3] Implied operating income — derive earnings before any financing or tax effects, strictly from [F1] and [F2].
  1. Q1: 50.00 − 39.00 = 11.00 → margin 11.00 / 50.00 = 22.00%.
  2. Q2: 47.00 − 38.54 = 8.46 → margin 8.46 / 47.00 = 18.00%.
  3. Q3: 52.00 − 39.00 = 13.00 → margin 13.00 / 52.00 = 25.00%.
  4. Q4: 61.00 − 43.31 = 17.69 → margin 17.69 / 61.00 = 29.00%.
  5. Full-year implied operating income: 11.00 + 8.46 + 13.00 + 17.69 = 50.15 → 50.15 / 210.00 = 23.88%.
  6. Margin range across quarters: 29.00% − 18.00% = 11.00 percentage points. Record whether the margin expansion in [T3.3]–[T3.4] is driven by expense-ratio compression alone or also by revenue growth, and cite the sub-traces that separate the two effects.

- [T4] Leverage event impact — assess the Q3 debt raise from [F3].
  1. State the $15.00M against full-year revenue (15.00 / 210.00 = 7.14%) and against Q3 revenue (15.00 / 52.00 = 28.85%).
  2. Attempt to trace interest expense, covenant headroom, and maturity profile: record `UNABLE TO TRACE: coupon, maturity, covenant terms, and opening debt balance not present in [F3]`.
  3. Attempt to determine whether any portion of the debt proceeds appears in [F1] or [F2]: record `UNABLE TO TRACE: no balance sheet or cash flow line provided in [F5]`.
  4. Determine whether [T4.1] inflows distort the Q3→Q4 revenue acceleration in [T1.3]: if not resolvable from [F1]–[F3], record `UNABLE TO TRACE: use of proceeds undisclosed` and carry it to Verification Gaps.

- [T5] Counterevidence and edge-case scan — for each finding in [T1]–[T3], record the disconfirming observation present in the premises, even where the aggregate reading is favorable.
  1. [T1] revenue growth coexists with the Q2 contraction in [T1.1].
  2. [T3] margin expansion coexists with the Q2 margin trough of 18.00% and an 11.00 pp intra-year spread.
  3. [T2.6] identical expense dollars at different revenue levels indicates a cost base whose response to volume is unspecified under [F5].
  4. [T4] a 7.14% revenue-equivalent debt inflow has no traceable servicing cost, so [T3] operating income is not a proxy for net income.

- [T6] Data completeness audit — enumerate every metric a financial posture assessment standardly requires, mark each as PRESENT or `INSUFFICIENT DATA FOR [metric]: [missing statement/field]`, and identify which specific conclusion claims in [T1]–[T4] are weakened by each absence.

Grounding rule: derive every figure from [F1]–[F3] arithmetic. When a required input is absent, record `INSUFFICIENT DATA FOR [T#]: [exact missing metric]` and exclude the dependent claim from the verdict rather than estimating it.

### FORMAL CONCLUSION

- Financial posture summary: state the objectively traceable position — revenue scale and directional path, expense-ratio trajectory, implied operating margin trajectory, and the quantified but unserviceable leverage event — citing `[T]` identifiers for every clause.
- Verified strengths versus structural divergences: two separate lists. Strengths must cite supporting `[T]` sub-traces; divergences must cite the counterevidence traces from [T5].
- Sensitivity statement: identify which single unverified input from [F3]–[F5], if obtained, would most change the posture reading, and state in one sentence the direction of that change conditional on the input's value.
- Verification gaps: every item recorded as `UNABLE TO TRACE` or `INSUFFICIENT DATA` across [T4]–[T6].
- Confidence: HIGH / MEDIUM / LOW, with justification tied to the ratio of verified to gap-listed traces.

### REMEDIATION / NEXT ACTION

The task is incomplete until this section contains all three of the following:
- A numbered diligence request list naming the exact statements, schedules, or fields required to close each Verification Gap from [T4]–[T6] (for example: opening and closing total debt, stated interest rate, covenant thresholds, cash flow from operations, cost of goods sold, prior-year quarterly revenue and operating expense figures, and the company's stated definition of operating expenses).
- Executable ratio and reconciliation formulas, written in spreadsheet syntax against the named fields, so each derived figure in [T1]–[T3] can be independently reproduced on receipt of the requested data.
- A quarterly trend table template with rows for revenue, QoQ %, operating expenses, expense ratio, implied operating income, and margin, pre-populated with the traceable values from [T1]–[T3] and marked `PENDING` wherever a Verification Gap applies.

TRACEABILITY SELF-CHECK (mandatory before finalizing):
Verify that every claim in the Formal Conclusion cites at least one `[T]` sub-identifier from the Evidence Traces. Where a claim lacks a supporting identifier, either add the missing trace from [F1]–[F3] or delete the claim, so that zero orphaned conclusions remain. Additionally confirm: (a) all arithmetic in [T1]–[T3] is reproduced explicitly, (b) every absent metric appears in Verification Gaps rather than in an estimated form, and (c) the verdict references only the supplied financial data and contains no valuation, pricing, credit-rating, or investment-action language.

### OPTIMIZED RESPONSE

All amounts are in $M unless noted. Percentages are rounded to two decimals. Arithmetic uses only [F1]–[F3]; absent inputs are not estimated.

### [T1] Revenue trajectory

1. Q1 → Q2: $47.00M [F1] − $50.00M [F1] = −$3.00M [T1.1]; change = −$3.00M / $50.00M = −6.00% [T1.1].
2. Q2 → Q3: $52.00M [F1] − $47.00M [F1] = +$5.00M [T1.2]; change = +$5.00M / $47.00M = +10.64% [T1.2].
3. Q3 → Q4: $61.00M [F1] − $52.00M [F1] = +$9.00M [T1.3]; change = +$9.00M / $52.00M = +17.31% [T1.3].
4. Q1 → Q4 net change: $61.00M [F1] − $50.00M [F1] = +$11.00M [T1.4]; change = +$11.00M / $50.00M = +22.00% [T1.4].
5. Full-year revenue: $50.00M + $47.00M + $52.00M + $61.00M = $210.00M [F1] [T1.5].
6. Shape classification: observed path is V-shaped, not monotonic: one sequential decline in [T1.1] followed by two consecutive accelerations in [T1.2]–[T1.3]. Seasonal-pattern classification remains indeterminate because the seasonality baseline is absent under [F5] [T1.6].

### [T2] Operating expense conversion

1. Q1: 78.00% [F2] × $50.00M [F1] = $39.00M [T2.1].
2. Q2: 82.00% [F2] × $47.00M [F1] = $38.54M [T2.2].
3. Q3: 75.00% [F2] × $52.00M [F1] = $39.00M [T2.3].
4. Q4: 71.00% [F2] × $61.00M [F1] = $43.31M [T2.4].
5. Full-year operating expenses: $39.00M + $38.54M + $39.00M + $43.31M = $159.85M [T2.5].
6. Full-year blended expense ratio: $159.85M / $210.00M = 76.12% [T2.6].
7. Q1 and Q3 expense dollars are identical at $39.00M [T2.1] [T2.3] despite Q3 revenue being $52.00M − $50.00M = $2.00M higher [F1]. Under [F5], fixed-versus-variable cost structure is unspecified; therefore this identity does not prove fixed costs, variable costs, or a stable cost base—it only shows that the response of expenses to volume cannot be classified from supplied data [T2.7].

### [T3] Implied operating income

1. Q1: $50.00M [F1] − $39.00M [T2.1] = $11.00M [T3.1]; margin = $11.00M / $50.00M = 22.00% [T3.1].
2. Q2: $47.00M [F1] − $38.54M [T2.2] = $8.46M [T3.2]; margin = $8.46M / $47.00M = 18.00% [T3.2].
3. Q3: $52.00M [F1] − $39.00M [T2.3] = $13.00M [T3.3]; margin = $13.00M / $52.00M = 25.00% [T3.3].
4. Q4: $61.00M [F1] − $43.31M [T2.4] = $17.69M [T3.4]; margin = $17.69M / $61.00M = 29.00% [T3.4].
5. Full-year implied operating income: $11.00M + $8.46M + $13.00M + $17.69M = $50.15M [T3.5]; full-year margin = $50.15M / $210.00M = 23.88% [T3.5].
6. Margin range: 29.00% − 18.00% = 11.00 percentage points [T3.6]. For Q3 → Q4, margin increased from 25.00% [T3.3] to 29.00% [T3.4], while the expense ratio fell from 75.00% [F2] [T2.3] to 71.00% [F2] [T2.4]; the percentage-margin expansion is driven by expense-ratio compression alone. Dollar implied operating income also increased by $17.69M − $13.00M = $4.69M [T3.4] [T3.3], alongside Q3 → Q4 revenue growth of +$9.00M [T1.3].

### [T4] Leverage event impact

1. Q3 debt raise versus full-year revenue: $15.00M [F3] / $210.00M [T1.5] = 7.14% [T4.1]. Q3 debt raise versus Q3 revenue: $15.00M [F3] / $52.00M [F1] = 28.85% [T4.1].
2. `UNABLE TO TRACE: coupon, maturity, covenant terms, and opening debt balance not present in [F3]` [T4.2].
3. `UNABLE TO TRACE: no balance sheet or cash flow line provided in [F5]` [T4.3].
4. Q3 → Q4 revenue acceleration distortion: `UNABLE TO TRACE: use of proceeds undisclosed`; carried to Verification Gaps [T4.4].

### [T5] Counterevidence and edge-case scan

1. [T1] revenue growth coexists with the Q2 contraction: $47.00M − $50.00M = −$3.00M, or −6.00% [T1.1] [T5.1].
2. [T3] margin expansion coexists with the Q2 margin trough of 18.00% [T3.2] and an intra-year margin spread of 29.00% − 18.00% = 11.00 percentage points [T3.4] [T3.6] [T5.2].
3. [T2.6] identical expense dollars at different revenue levels: Q1 $39.00M [T2.1] and Q3 $39.00M [T2.3] against $50.00M and $52.00M revenue [F1]; cost response to volume is unspecified under [F5] [T5.3].
4. [T4] a 7.14% full-year-revenue-equivalent debt inflow has no traceable servicing cost [T4.1] [T4.2], so [T3] implied operating income is not a proxy for net income [T5.4].

### [T6] Data completeness audit

PRESENT metrics:

| Metric | Status | Trace support |
|---|---:|---|
| Quarterly revenue | PRESENT: [F1] | Supports [T1.1]–[T1.5] |
| Full-year revenue | PRESENT: $210.00M [T1.5] | Supports [T1.5], [T4.1] |
| QoQ revenue absolute and percentage changes Q1→Q4 | PRESENT: [T1.1]–[T1.4] | Supports [T1.1]–[T1.4] |
| Operating expense ratios by quarter | PRESENT: [F2] | Supports [T2.1]–[T2.4] |
| Operating expense dollars by quarter and FY | PRESENT: [T2.1]–[T2.5] | Supports [T2.1]–[T2.5] |
| Full-year blended expense ratio | PRESENT: 76.12% [T2.6] | Supports [T2.6] |
| Implied operating income by quarter and FY | PRESENT: [T3.1]–[T3.5] | Supports [T3.1]–[T3.5] |
| Implied operating margin by quarter and FY; margin range | PRESENT: [T3.1]–[T3.6] | Supports [T3.1]–[T3.6] |
| Q3 new debt amount and revenue-equivalent ratios | PRESENT: $15.00M [F3], 7.14%, 28.85% [T4.1] | Supports [T4.1]; servicing absent in [T4.2] |

Absent / unresolved metrics:

- `INSUFFICIENT DATA FOR [cost of goods sold / gross margin]: COGS, gross profit, and gross margin fields/statements absent in [F5]`; weakens margin-quality interpretation of [T3.1]–[T3.5] and cost-behavior read [T2.7] [T5.3].
- `INSUFFICIENT DATA FOR [operating expense definition]: whether [F2] includes depreciation, amortization, stock-based compensation, one-time items, or interest expense is unresolved in [F4]`; weakens [T2.1]–[T2.6], [T3.1]–[T3.5], and [T5.3].
- `INSUFFICIENT DATA FOR [depreciation and amortization]: D&A fields absent in [F4]/[F5]`; weakens comparability of [T2.1]–[T2.6] and [T3.1]–[T3.5], and prevents EBITDA-based debt analysis relevant to [T4.2].
- `INSUFFICIENT DATA FOR [stock-based compensation]: SBC field absent in [F4]/[F5]`; weakens interpretation of [T2.1]–[T2.6] and [T3.1]–[T3.5].
- `INSUFFICIENT DATA FOR [one-time items]: one-time revenue/expense fields absent in [F4]/[F5]`; weakens recurring margin read of [T3.1]–[T3.5].
- `INSUFFICIENT DATA FOR [interest expense]: coupon/interest rate, debt schedule, and interest expense fields absent in [F3]/[F5]`; weakens [T4.2] and the net-income limitation in [T5.4].
- `INSUFFICIENT DATA FOR [tax expense]: tax expense field absent in [F5]`; weakens any net-income interpretation of [T3.1]–[T3.5] and [T5.4].
- `INSUFFICIENT DATA FOR [net income]: interest expense, tax expense, and other non-operating fields absent in [F5]`; weakens [T3.1]–[T3.5] as a profitability proxy and [T5.4].
- `INSUFFICIENT DATA FOR [cash flow statement]: cash flow from operations, capex, debt proceeds, interest paid, taxes paid, and cash-change fields absent in [F5]`; weakens [T4.2]–[T4.4], [T5.4], and any debt-service assessment.
- `INSUFFICIENT DATA FOR [cash and cash equivalents]: balance sheet cash field absent in [F5]`; weakens [T4.3] and liquidity assessment.
- `INSUFFICIENT DATA FOR [opening and closing total debt]: balance sheet and debt schedule fields absent in [F5]`; weakens [T4.2]–[T4.3] and leverage assessment.
- `INSUFFICIENT DATA FOR [equity]: balance sheet equity field absent in [F5]`; weakens [T4.3] and capital-structure assessment.
- `INSUFFICIENT DATA FOR [current assets, current liabilities, working capital, inventory, receivables, payables]: balance sheet fields absent in [F5]`; weakens [T4.3] liquidity and debt-service assessment.
- `INSUFFICIENT DATA FOR [debt coupon / stated interest rate]: field absent in [F3]`; weakens [T4.2] and [T5.4].
- `INSUFFICIENT DATA FOR [maturity profile]: field absent in [F3]`; weakens [T4.2].
- `INSUFFICIENT DATA FOR [covenant thresholds and headroom]: fields absent in [F3]`; weakens [T4.2].
- `INSUFFICIENT DATA FOR [use of proceeds]: field absent in [F3]`; weakens [T4.4] and the causal read of [T1.3].
- `INSUFFICIENT DATA FOR [prior-year quarterly revenue and operating expense comparatives]: fields absent in [F5]`; weakens [T1.6] shape/seasonality read and [T3.3]–[T3.4] trend interpretation.
- `INSUFFICIENT DATA FOR [prior-quarter revenue for Q1 QoQ]: prior Q4 field absent in [F5]`; weakens Q1 sequential trend continuity in [T1.6].
- `INSUFFICIENT DATA FOR [seasonality baseline]: field absent in [F5]`; weakens [T1.6].
- `INSUFFICIENT DATA FOR [segment mix]: segment revenue/expense fields absent in [F5]`; weakens reliability of [T1.2]–[T1.4] and [T3.1]–[T3.5].
- `INSUFFICIENT DATA FOR [customer concentration]: customer/revenue concentration schedule absent in [F5]`; weakens sustainability read of [T1.2]–[T1.4].
- `INSUFFICIENT DATA FOR [sector and size]: sector/size fields absent in [F5]`; weakens benchmarking of [T2.6] and [T3.1]–[T3.6].
- `INSUFFICIENT DATA FOR [fixed-versus-variable cost breakdown / company cost structure]: fields absent in [F5]`; weakens [T2.7] and [T5.3].
- `INSUFFICIENT DATA FOR [organic versus acquired/debt-funded revenue contribution]: use-of-proceeds and transaction detail absent in [F3]/[F5]`; weakens [T1.3] and [T4.4].
- `INSUFFICIENT DATA FOR [interest coverage ratio]: interest expense and EBITDA/operating definitions absent in [F3]–[F5]`; weakens [T4.2] and [T5.4].
- `INSUFFICIENT DATA FOR [leverage ratio]: opening/closing total debt and EBITDA fields absent in [F5]`; weakens [T4.2]–[T4.3].
- `INSUFFICIENT DATA FOR [liquidity ratios / cash runway]: cash, current assets, current liabilities, and cash flow fields absent in [F5]`; weakens [T4.3].
- `INSUFFICIENT DATA FOR [EBITDA]: D&A, interest, tax, and definitional expense scope absent in [F4]/[F5]`; weakens [T3.1]–[T3.5] and [T4.2].

## FORMAL CONCLUSION

- Financial posture summary: Revenue scale is $210.00M full-year [T1.5], with a Q2 decline of −$3.00M/−6.00% [T1.1], followed by Q2→Q3 +$5.00M/+10.64% [T1.2] and Q3→Q4 +$9.00M/+17.31% [T1.3], producing an observed V-shaped path [T1.1]–[T1.3]. Operating expenses converted to $39.00M, $38.54M, $39.00M, and $43.31M by quarter [T2.1]–[T2.4], with a 76.12% full-year blended expense ratio [T2.6]. Implied operating income is $11.00M, $8.46M, $13.00M, and $17.69M by quarter [T3.1]–[T3.4], with margins of 22.00%, 18.00%, 25.00%, and 29.00% [T3.1]–[T3.4] and a full-year implied operating margin of 23.88% [T3.5]. The Q3 $15.00M debt raise equals 7.14% of full-year revenue and 28.85% of Q3 revenue [T4.1], but servicing, maturity, covenants, opening debt, balance-sheet/cash-flow treatment, and use of proceeds are untraceable [T4.2]–[T4.4].
- Verified strengths: Q3→Q4 revenue acceleration is +$9.00M/+17.31% [T1.3]; Q3→Q4 implied operating income rises from $13.00M to $17.69M [T3.3]–[T3.4]; Q4 expense ratio falls to 71.00% [F2] from Q3 75.00% [F2] [T2.3]–[T2.4]; full-year implied operating income is $50.15M at a 23.88% margin [T3.5].
- Structural divergences: Q2 revenue contracted by −$3.00M/−6.00% [T5.1] [T1.1]; Q2 margin was an 18.00% trough [T5.2] [T3.2], with an 11.00 percentage-point intra-year margin spread [T5.2] [T3.6]; identical Q1 and Q3 expense dollars of $39.00M occurred at different revenue levels [T5.3] [T2.1] [T2.3], with cost response unspecified [F5]; the $15.00M Q3 debt inflow has no traceable servicing cost [T5.4] [T4.1]–[T4.2], so implied operating income is not net income [T5.4].
- Sensitivity statement: The single most posture-changing unverified input is the stated coupon/interest rate on the $15.00M Q3 debt [F3] [T4.2]; if that rate were high, it would create a larger untraced servicing burden against $50.15M full-year implied operating income [T3.5] and weaken the posture reading, whereas if it were low, the burden would be limited and the posture reading would strengthen relative to the high-rate case.
- Verification gaps: All items recorded as `UNABLE TO TRACE` or `INSUFFICIENT DATA` above remain open: coupon, maturity, covenant terms, and opening debt balance [T4.2]; absence of balance-sheet/cash-flow lines for debt-proceeds tracing [T4.3]; use of proceeds [T4.4]; COGS/gross margin; operating expense definition; D&A; SBC; one-time items; interest expense; tax expense; net income; cash flow statement; cash; opening/closing total debt; equity; current assets/liabilities/working capital/inventory/receivables/payables; debt coupon; maturity profile; covenant thresholds/headroom; prior-year quarterly revenue and operating expense comparatives; prior-quarter revenue for Q1 QoQ; seasonality baseline; segment mix; customer concentration; sector/size; fixed-versus-variable cost breakdown; organic versus acquired/debt-funded revenue contribution; interest coverage; leverage ratio; liquidity ratios/cash runway; EBITDA [T6].
- Confidence: LOW for a complete financial posture assessment. The T1–T3 arithmetic is fully verified and reproducible [T1.1]–[T3.6], but the gap-listed fields in [T4.2]–[T4.4] and [T6] dominate the leverage, cash-flow, tax, net-income, cost-definition, and comparative dimensions; the supported verdict is therefore limited to the traceable revenue/expense/implied-margin path, not a complete financial posture.

## REMEDIATION / NEXT ACTION

1. Numbered diligence request list to close each Verification Gap from [T4]–[T6]:

1. Provide the Q3 financing agreement and debt schedule: principal amount, opening and closing total debt, stated coupon/interest rate, interest payment dates, maturity/amortization schedule, covenant thresholds and headroom (leverage, interest coverage, liquidity), use-of-proceeds schedule, and lender terms [T4.2]–[T4.4].
2. Provide the full cash flow statement for the fiscal year and quarters: cash flow from operations, capex, debt proceeds, interest paid, taxes paid, and net change in cash [T4.3] [T6].
3. Provide the balance sheet as of each quarter-end: cash and cash equivalents, current assets, inventory, receivables, current liabilities, payables, short-term debt, long-term debt, total debt, and equity [T4.3] [T6].
4. Provide the income statement detail: COGS, gross profit, gross margin, operating expense definition and components, D&A, stock-based compensation, one-time items, interest expense, tax expense, and net income [F4] [T6].
5. Provide prior-year quarterly revenue and operating expense figures and prior-year Q4 revenue for Q1 QoQ continuity and seasonality baseline [F5] [T6].
6. Provide segment revenue, segment operating expenses, segment margin, and customer concentration/top-customer schedule [F5] [T6].
7. Provide the company’s stated sector, size classification, revenue-recognition policy, and organic-versus-acquired revenue bridge [F5] [T6].
8. Provide the company’s fixed-versus-variable cost breakdown or management cost-structure schedule [F5] [T6].
9. Provide debt-service support schedules for interest coverage, leverage, net debt, liquidity/current ratio, and cash runway calculations [T4.2] [T6].
10. Provide EBITDA reconciliation beginning with implied operating income and adjusting for D&A, SBC, one-time items, interest, and taxes as defined [F4] [T6].

2. Executable ratio and reconciliation formulas in spreadsheet syntax against named fields:

```excel
Revenue_FY = SUM(Revenue_Q1,Revenue_Q2,Revenue_Q3,Revenue_Q4)
QoQ_Abs_Q2 = Revenue_Q2 - Revenue_Q1
QoQ_Pct_Q2 = (Revenue_Q2 - Revenue_Q1) / Revenue_Q1
QoQ_Abs_Q3 = Revenue_Q3 - Revenue_Q2
QoQ_Pct_Q3 = (Revenue_Q3 - Revenue_Q2) / Revenue_Q2
QoQ_Abs_Q4 = Revenue_Q4 - Revenue_Q3
QoQ_Pct_Q4 = (Revenue_Q4 - Revenue_Q3) / Revenue_Q3
Net_Change_Q1_Q4 = Revenue_Q4 - Revenue_Q1
Net_Change_Pct_Q1_Q4 = (Revenue_Q4 - Revenue_Q1) / Revenue_Q1

Opex_Dollars_Q1 = Opex_Ratio_Q1 * Revenue_Q1
Opex_Dollars_Q2 = Opex_Ratio_Q2 * Revenue_Q2
Opex_Dollars_Q3 = Opex_Ratio_Q3 * Revenue_Q3
Opex_Dollars_Q4 = Opex_Ratio_Q4 * Revenue_Q4
Opex_FY = SUM(Opex_Dollars_Q1,Opex_Dollars_Q2,Opex_Dollars_Q3,Opex_Dollars_Q4)
Expense_Ratio_FY = Opex_FY / Revenue_FY

Operating_Income_Q1 = Revenue_Q1 - Opex_Dollars_Q1
Operating_Income_Q2 = Revenue_Q2 - Opex_Dollars_Q2
Operating_Income_Q3 = Revenue_Q3 - Opex_Dollars_Q3
Operating_Income_Q4 = Revenue_Q4 - Opex_Dollars_Q4
Operating_Income_FY = SUM(Operating_Income_Q1,Operating_Income_Q2,Operating_Income_Q3,Operating_Income_Q4)

Operating_Margin_Q1 = Operating_Income_Q1 / Revenue_Q1
Operating_Margin_Q2 = Operating_Income_Q2 / Revenue_Q2
Operating_Margin_Q3 = Operating_Income_Q3 / Revenue_Q3
Operating_Margin_Q4 = Operating_Income_Q4 / Revenue_Q4
Operating_Margin_FY = Operating_Income_FY / Revenue_FY
Margin_Range = MAX(Operating_Margin_Q1,Operating_Margin_Q2,Operating_Margin_Q3,Operating_Margin_Q4) - MIN(Operating_Margin_Q1,Operating_Margin_Q2,Operating_Margin_Q3,Operating_Margin_Q4)

Debt_to_FY_Revenue = Debt_Raised_Q3 / Revenue_FY
Debt_to_Q3_Revenue = Debt_Raised_Q3 / Revenue_Q3
Net_Debt = Total_Debt_Closing - Cash_and_Equivalents
Interest_Coverage = Operating_Income_FY / Interest_Expense_FY
Net_Income = Operating_Income_FY - Interest_Expense_FY - Tax_Expense_FY
Leverage_Ratio = Total_Debt_Closing / EBITDA_FY
Current_Ratio = Current_Assets / Current_Liabilities
CFO_to_Debt = CFO_FY / Total_Debt_Closing
```

Q1 sequential growth formula pending prior-quarter data:

```excel
Q1_QoQ_Pct = IFERROR((Revenue_Q1 - Prior_Q4_Revenue) / Prior_Q4_Revenue, "PENDING")
```

3. Quarterly trend table template — pre-populated with traceable values from [T1]–[T3]:

| Line item | Q1 | Q2 | Q3 | Q4 | FY / note |
|---|---:|---:|---:|---:|---:|
| Revenue ($M) | 50.00 [F1] | 47.00 [F1] | 52.00 [F1] | 61.00 [F1] | 210.00 [T1.5] |
| QoQ % | PENDING: prior-quarter revenue absent under [F5] [T6] | −6.00% [T1.1] | +10.64% [T1.2] | +17.31% [T1.3] | Q1→Q4 +22.00% [T1.4] |
| Operating expenses ($M) | 39.00 [T2.1] | 38.54 [T2.2] | 39.00 [T2.3] | 43.31 [T2.4] | 159.85 [T2.5] |
| Expense ratio | 78.00% [F2] [T2.1] | 82.00% [F2] [T2.2] | 75.00% [F2] [T2.3] | 71.00% [F2] [T2.4] | 76.12% [T2.6] |
| Implied operating income ($M) | 11.00 [T3.1] | 8.46 [T3.2] | 13.00 [T3.3] | 17.69 [T3.4] | 50.15 [T3.5] |
| Margin | 22.00% [T3.1] | 18.00% [T3.2] | 25.00% [T3.3] | 29.00% [T3.4] | 23.88% [T3.5] |

Additional PENDING posture fields: Q3 new debt is $15.00M [F3] [T4.1]; interest expense, coupon, maturity, covenants, opening/closing total debt, and use of proceeds are `PENDING` because they are absent under [F3]/[F5] [T4.2]–[T4.4] [T6].

## TRACEABILITY SELF-CHECK

- Every Formal Conclusion clause cites at least one [T] sub-identifier; no orphaned conclusions remain.
- All arithmetic in [T1]–[T3] is reproduced explicitly above, including revenue changes, full-year revenue, operating expense dollars, blended expense ratio, implied operating income, margins, and margin range [T1.1]–[T3.6].
- Every absent metric is recorded in Verification Gaps rather than estimated or inferred [T4.2]–[T4.4] [T6].
- The verdict references only the supplied financial data [F1]–[F3] and contains no valuation, pricing, credit-rating, or investment-action language.

### EVALUATION: TEST 2

- **Word Count**: Baseline `402` words | Optimized `2580` words | Ratio `6.42x`
- **Eval Tokens**: Baseline `2721` | Optimized `21309`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 5         | +0    |
| Completeness  | 4        | 5         | +1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 3.5      | 5         | +1.5  |
| Traceability  | 3.5      | 5         | +1.5  |
| TOTAL         | 21.0/25  | 24.0/25   | +3.0  |

The baseline is concise, accurate, and clearly organized, with all core revenue, opex, margin, and debt-ratio calculations correct. The optimized response materially improves completeness, actionability, and traceability by adding explicit arithmetic, verification gaps, diligence requests, spreadsheet formulas, and a PENDING trend template. However, its certificate format is verbose and repetitive, adding unhelpful structural bloat relative to the baseline’s cleaner presentation.

---

## TEST 3: Medical Reasoning (Accuracy | Mode 1 (Max Certificate, Template 3 [S1]-[S4]))

### BASELINE RESPONSE

**Most likely diagnosis:** **Acute inferior ST-elevation myocardial infarction (STEMI)**, likely with **right ventricular involvement** given hypotension and inferior ST elevations in II, III, aVF.

**Immediate priorities:**
1. **ABC/monitoring:** continuous cardiac monitoring, defibrillator nearby, IV access, supplemental O₂ only if SpO₂ <90% or respiratory distress.
2. **Activate STEMI pathway:** immediate cardiology/cath lab activation for **primary PCI** (goal door-to-balloon ≤90 min). If PCI unavailable timely, consider fibrinolysis if no contraindications.
3. **Antiplatelet/anticoagulant therapy:** chew **aspirin 162–325 mg** immediately; give a P2Y12 inhibitor and anticoagulation per STEMI protocol.
4. **Assess for RV infarction:** obtain **right-sided ECG (V4R)**. If hypotensive from RV infarct, give **cautious IV fluid bolus** (e.g., 250–500 mL crystalloid) and reassess.
5. **Avoid nitrates** with hypotension or suspected RV infarct; avoid beta-blockers if hypotensive/shock.
6. **Pain control** and treat complications: watch for bradyarrhythmias/heart block, cardiogenic shock, and arrhythmias.
7. **Do not wait for troponin** — reperfusion decisions are ECG-based.

In short: **inferior STEMI → activate cath lab, aspirin/antiplatelet/anticoagulation, monitor, cautious fluids if RV infarct/hypotension, avoid nitrates.**

### OPTIMIZED PROMPT

```markdown
Clinical reasoning methodology, as established in evidence-based medicine, requires completing this structured reasoning certificate before presenting any differential synthesis, disposition, or priority list. Every section must be grounded in the observable data declared in the premises.

### PREMISES
- [P1] Presenting context: 58-year-old male; sudden-onset chest pain radiating to the left arm; diaphoresis; shortness of breath. Symptom onset time, past medical history, prior cardiac history, current medications, allergies, and risk factors are NOT provided in the input.
- [P2] Objective findings: BP 90/60 mmHg; HR 110 bpm; SpO2 94%; 12-lead ECG with ST-segment elevation in leads II, III, and aVF; troponin result pending (value and assay not available).
- [P3] Active regimen and interventions: none documented in the provided input.
- [P4] Reference standards: established consensus standards of care for acute chest pain with ST-segment elevation, including reperfusion-timing thresholds, hemodynamic stabilization targets, and recommended initial pharmacologic and monitoring bundles.

### DIAGNOSTIC & THERAPEUTIC TRACES
For each trace, cite the specific [P] items that support or contradict it. Grounding rule: base every step on explicit data in [P1]-[P4]; where a discriminating data element is absent, record `UNABLE TO TRACE: [exact missing element]` inside that trace and carry the item into Verification Gaps. Where disconfirming evidence exists in [P1]-[P3], record it explicitly even when the leading hypothesis remains favored.

- [S1] Leading diagnostic hypothesis — inferior ST-elevation myocardial infarction (STEMI):
  1. Supporting findings: map each [P2] item that supports it (ST elevation in II, III, aVF representing the inferior wall territory; chest pain radiating to the left arm; diaphoresis; shortness of breath; HR 110; BP 90/60).
  2. Territory and vascular correlation: state which coronary territory the II/III/aVF distribution localizes to and which vessel(s) are implicated, per [P4].
  3. Disconfirming or complicating findings: identify any [P2] element that is atypical, ambiguous, or attributable to an alternative mechanism.
  4. Discriminating gaps: list the specific missing elements (e.g., reciprocal ST depression in I/aVL, posterior or right-sided lead findings, troponin value and delta, onset-to-presentation interval) and mark each `UNABLE TO TRACE` with the exact missing input.
  5. Verification status: VERIFIED / PARTIAL / UNABLE TO TRACE, with the reason.

- [S2] Competing and immediately dangerous alternatives:
  1. Candidate set: enumerate the alternative diagnoses that [P1]/[P2] could support or fail to exclude, and state the specific feature of [P2] that keeps each one live (e.g., the hypotension–tachycardia pattern relative to a dissection or obstructive-shock picture; pleuritic or positional features relative to pericarditis; the ECG distribution relative to pericarditis or early repolarization; the oxygenation and heart-rate pattern relative to pulmonary embolism).
  2. Supporting findings per candidate: cite the exact [P1]/[P2] items.
  3. Disconfirming findings per candidate: cite the exact [P1]/[P2] items that argue against, including features whose absence lowers but does not eliminate probability.
  4. Discriminating gaps per candidate: name the single test, image, or history element from [P4] that would confirm or exclude it, and mark unresolved items `UNABLE TO TRACE: [missing element]`.
  5. Relative ranking rationale: state the ordering logic that places the [S1] hypothesis ahead of each alternative, referencing the cited items only.

- [S3] Hemodynamic, oxygenation, and perfusion acuity assessment:
  1. Data read: state the [P2] values and the physiologic pattern they constitute (systolic pressure at the stated level, tachycardia, oxygen saturation at the stated level).
  2. Shock-spectrum evaluation: assess where this patient sits on the compensated-to-decompensated continuum per [P4], citing the specific [P2] values used.
  3. Right-ventricular involvement consideration: state how an inferior-territory infarct interacts with preload dependence and with the observed blood pressure, and identify which missing data (right-sided leads, bedside findings, response to a preload challenge, lactate, urine output) would resolve that question; mark absent items `UNABLE TO TRACE`.
  4. Immediate risk if untreated: state the time-sensitive deterioration pathway per [P4], tied to [P2].
  5. Verification status: VERIFIED / PARTIAL / UNABLE TO TRACE, with the reason.

- [S4] Immediate priority sequence:
  1. Ordered priorities: produce a numbered list of immediate priorities derived from [S1]-[S3], each annotated with the [S] identifier that justifies it and the [P4] standard it satisfies.
  2. Reperfusion pathway: state the indicated reperfusion strategy and its decision window per [P4], and identify which data elements are required to finalize that decision; mark absent items `UNABLE TO TRACE`.
  3. Initial pharmacologic and monitoring bundle: itemize the components indicated by [P4] for this presentation, noting the specific [P2] value that triggers each component.
  4. Contraindication and interaction check: for each item in the bundle, state the condition under which it would be withheld and whether the data needed to evaluate that condition is present in [P1]-[P3]; when absent, record `UNABLE TO TRACE: [missing element]`.
  5. Parallel diagnostic actions: itemize the confirmatory tests and consults required alongside stabilization, each tied to a [S2] or [S3] discriminating gap it closes.

### FORMAL CONCLUSION
- Evidence-ranked differential: rank the candidate conditions in order of evidential support, cited strictly to [S1]-[S4] identifiers, and state the single most likely diagnosis.
- Acuity statement: state the acuity tier and the physiologic basis for it, citing [S3].
- High-acuity exclusions required: list the alternatives that must be actively excluded before disposition, citing [S2].
- Immediate priorities: present the ordered priority list from [S4] as a numbered sequence, with each entry citing its supporting [S] identifier.
- Verification gaps: list every item marked `UNABLE TO TRACE` across [S1]-[S4] and name the exact input, test, or measurement required to close it.

### REMEDIATION / NEXT ACTION
Provide a concrete, executable next-action block: the specific immediate stabilization and diagnostic steps in order, the exact information or test results needed to close each Verification Gap listed above, and the reassessment checkpoints at which each [S] trace should be re-evaluated against new data. Where a priority cannot be finalized from the available data, state the decision rule that governs once the missing element is obtained.

DISCLAIMER: This output is structured analytical support, not clinical advice. All diagnostic and treatment decisions require a licensed healthcare clinician.

TRACEABILITY SELF-CHECK (mandatory before finalizing): Verify that every claim in the Formal Conclusion and every item in the priority sequence cites at least one [S] identifier and its underlying [P] premise. When a claim lacks a supporting identifier, add the missing trace from [P1]-[P4] or remove the claim so zero orphaned conclusions remain. Confirm that every [S] trace containing absent data carries an explicit `UNABLE TO TRACE` entry and that same entry appears under Verification Gaps.
```

### OPTIMIZED RESPONSE

# Structured Reasoning Certificate  
*Analytical support only. Not clinical advice. All diagnostic and treatment decisions require a licensed healthcare clinician.*

> Note: [P4] is cited as the consensus standard reference. Where [P4] summarizes thresholds/bundles without reproducing exact numeric protocol values, this certificate avoids inventing protocol-specific numbers and identifies missing elements that would finalize decisions.

## DIAGNOSTIC & THERAPEUTIC TRACES

### [S1] Leading diagnostic hypothesis — inferior ST-elevation myocardial infarction (STEMI)

1. **Supporting findings**
   - ST-segment elevation in leads **II, III, aVF** indicates contiguous inferior-wall injury [P2].
   - Sudden chest pain radiating to the left arm is consistent with myocardial ischemia [P1].
   - Diaphoresis and shortness of breath are consistent with acute coronary syndrome and physiologic stress [P1].
   - HR 110 bpm, BP 90/60 mmHg, and SpO2 94% indicate a high-risk presentation with hemodynamic/oxygenation compromise, though these are not diagnostic by themselves [P2].

2. **Territory and vascular correlation**
   - Leads II, III, and aVF localize to the inferior wall; per standard [P4] correlation, this most commonly implicates the right coronary artery, or the left circumflex in a left-dominant circulation [P2; P4].
   - The provided ECG distribution therefore supports an inferior-territory STEMI [S1; P2; P4].

3. **Disconfirming or complicating findings**
   - No explicit [P1]-[P3] finding directly disconfirms inferior STEMI.
   - However, BP 90/60 mmHg and HR 110 bpm complicate the picture by raising concern for right-ventricular involvement, cardiogenic shock, or an alternative shock mechanism [P2; S3].
   - SpO2 94% and shortness of breath are nonspecific and do not exclude pulmonary embolism, dissection, or obstructive shock [P1; P2; S2].
   - Absence of documented reciprocal depression, right-sided leads, posterior leads, and troponin means the diagnosis is strongly suspected but not fully characterized [P2; S1 gaps].

4. **Discriminating gaps**
   - `UNABLE TO TRACE: reciprocal ST depression in I/aVL`
   - `UNABLE TO TRACE: right-sided lead findings (e.g., V4R)`
   - `UNABLE TO TRACE: posterior lead findings (V7-V9)`
   - `UNABLE TO TRACE: troponin value and delta`
   - `UNABLE TO TRACE: symptom onset-to-presentation interval`
   - `UNABLE TO TRACE: prior and serial ECG data`
   - `UNABLE TO TRACE: PMH, prior cardiac history, current medications, allergies, and risk factors`

5. **Verification status**
   - **PARTIAL** — Strong support from symptoms plus inferior ST elevation [P1; P2; P4], but final confirmation, territory complications, reperfusion eligibility, and contraindication checks are incomplete because key historical, ECG, troponin, and hemodynamic data are missing [S1; P2; P4].

---

### [S2] Competing and immediately dangerous alternatives

#### Candidate set and ranking overview
1. **Aortic dissection** — must exclude before fibrinolysis/anticoagulation if suspected.
2. **Pulmonary embolism** — live because of hypoxia, tachycardia, hypotension, and dyspnea.
3. **Obstructive shock (tamponade, tension pneumothorax)** — live because of hypotension/tachycardia/hypoxia.
4. **Pericarditis/myocarditis** — live because of ST elevation and chest pain.
5. **Early repolarization** — live only as an ECG mimic; much less likely given acute severe symptoms and hemodynamic compromise.

#### Aortic dissection
- **Supporting findings:** Sudden chest pain radiating to the left arm, diaphoresis, hypotension/tachycardia; inferior ST elevation could result from RCA malperfusion/occlusion [P1; P2].
- **Disconfirming/absent findings:** No tearing/back pain, pulse/BP differential, mediastinal widening, or known aortic disease is documented in [P1]-[P3]; contiguous inferior STE is more typical of STEMI, but absence of dissection features lowers without eliminating probability [P1-P3; P2].
- **Discriminating gaps:** `UNABLE TO TRACE: CT angiography/TEE and pulse/BP differential for dissection`
- **Ranking rationale:** [S1] is ahead because contiguous inferior STE with typical ischemic symptoms is more specific for STEMI [S1; P2; P4]. However, dissection remains an exclusion priority because antithrombotic/fibrinolytic therapy could be harmful [S2; P4].

#### Pulmonary embolism
- **Supporting findings:** Shortness of breath, tachycardia HR 110, SpO2 94%, hypotension BP 90/60, and chest pain are compatible with PE [P1; P2].
- **Disconfirming/absent findings:** Inferior ST elevation in II/III/aVF is not classic for PE; no pleuritic pain, immobilization, malignancy, prior VTE, D-dimer, CTPA, or RV-strain data are provided [P1-P3; P2].
- **Discriminating gaps:** `UNABLE TO TRACE: CTPA, D-dimer, RV strain echocardiogram, and VTE risk factors for PE`
- **Ranking rationale:** [S1] is ahead because focal inferior STE with diaphoresis and left-arm radiation is more consistent with STEMI [S1; P1; P2]. PE remains important because hypoxia/tachycardia/hypotension are unexplained and dangerous [S2; S3; P2].

#### Obstructive shock — tamponade or tension pneumothorax
- **Supporting findings:** Hypotension, tachycardia, hypoxia, shortness of breath, and chest pain could reflect obstructive shock [P1; P2].
- **Disconfirming/absent findings:** Focal inferior STE suggests ACS; no JVD, pulsus paradoxus, tracheal deviation, absent breath sounds, bedside ultrasound, or CXR data are provided [P1-P3; P2].
- **Discriminating gaps:** `UNABLE TO TRACE: bedside ultrasound, CXR, and obstructive-shock physical findings (JVD, pulsus paradoxus, breath sounds, tracheal deviation)`
- **Ranking rationale:** [S1] is ahead because the ECG pattern is territorial for inferior infarction [S1; P2], but obstructive shock must be rapidly excluded because of the hypotensive/tachycardic/hypoxic pattern [S3; S2; P2].

#### Pericarditis/myocarditis
- **Supporting findings:** Chest pain and ST elevation in II, III, aVF could overlap with pericarditic ST changes [P1; P2].
- **Disconfirming/absent findings:** The provided ST elevation is localized to inferior leads rather than documented diffuse; severe diaphoresis, hypotension, and tachycardia favor ischemia; no positional/pleuritic history, PR depression, diffuse STE, or echocardiogram are provided [P1-P3; P2].
- **Discriminating gaps:** `UNABLE TO TRACE: full ECG for PR depression/diffuse ST changes, positional/pleuritic history, and echocardiogram for pericarditis`
- **Ranking rationale:** [S1] is ahead because focal contiguous inferior STE plus ischemic symptoms is more consistent with STEMI [S1; P2]. Pericarditis is not fully excluded without full ECG and history [S2; P4].

#### Early repolarization
- **Supporting findings:** ST elevation is present on ECG [P2].
- **Disconfirming/absent findings:** Acute severe chest pain, diaphoresis, hypotension, tachycardia, and localized inferior STE are atypical for benign early repolarization; no prior ECG is provided [P1-P3; P2].
- **Discriminating gaps:** `UNABLE TO TRACE: prior and serial ECG data for early repolarization`
- **Ranking rationale:** Lowest priority; [S1] strongly favored by the acute ischemic syndrome and hemodynamic compromise [S1; P1; P2].

**Relative ranking summary:** [S1] inferior STEMI ranks first because of contiguous inferior STE plus sudden radiating chest pain and diaphoresis [S1; P1; P2; P4]. Aortic dissection, PE, and obstructive shock remain high-acuity exclusions because hypotension, tachycardia, and hypoxia are present [S2; S3; P2]. Pericarditis and early repolarization are less likely but not fully excluded without complete ECG/history [S2; P2].

---

### [S3] Hemodynamic, oxygenation, and perfusion acuity assessment

1. **Data read**
   - BP 90/60 mmHg: hypotension/borderline systolic pressure [P2].
   - HR 110 bpm: tachycardia [P2].
   - SpO2 94%: mild hypoxemia [P2].
   - Physiologic pattern: acute inferior STEMI with hypotension, tachycardia, and hypoxemia — a high-risk shock spectrum [S1; S3; P2; P4].

2. **Shock-spectrum evaluation**
   - The patient sits at least in a **hypotensive, compensated-to-decompensated shock-risk state** because of SBP 90/60, HR 110, and SpO2 94% in the setting of STEMI [S3; P2; P4].
   - Full shock classification is not possible without perfusion markers.
   - `UNABLE TO TRACE: lactate, urine output, mentation, capillary refill, and serial blood pressure response`

3. **Right-ventricular involvement consideration**
   - Inferior infarction may involve the right ventricle; RV ischemia is preload-dependent, and nitrates/diuretics may worsen hypotension [S1; S3; P2; P4].
   - BP 90/60 raises concern for RV involvement or cardiogenic shock [P2; S3].
   - Missing data:
     - `UNABLE TO TRACE: right-sided lead findings`
     - `UNABLE TO TRACE: bedside RV findings (JVD, Kussmaul sign, clear lungs)`
     - `UNABLE TO TRACE: response to preload challenge`
     - `UNABLE TO TRACE: lactate and urine output`
     - `UNABLE TO TRACE: echocardiographic RV assessment`

4. **Immediate risk if untreated**
   - Per [P4], acute STEMI with hypotension/tachycardia/hypoxia is time-sensitive and can deteriorate to malignant arrhythmia, cardiogenic/obstructive shock, RV failure, or death [S1-S3; P2; P4].

5. **Verification status**
   - **PARTIAL** — Hemodynamic compromise and high acuity are verified by BP 90/60, HR 110, and SpO2 94% [P2; P4], but shock severity and RV involvement remain unresolved because perfusion markers and right-sided/echo data are missing [S3; P2; P4].

---

### [S4] Immediate priority sequence

1. **Ordered priorities**
   1. Activate the STEMI/reperfusion pathway and cardiology/catheterization team immediately [S1; P2; P4].
   2. Establish continuous ECG monitoring, defibrillator availability, IV access, and oxygen/ventilation support to [P4] target because of STEMI with BP 90/60, HR 110, SpO2 94% [S3; P2; P4].
   3. Obtain right-sided/posterior and repeat ECG, troponin, lactate, renal/coagulation labs, bedside echocardiogram, and urgent assessment for dissection/PE/obstructive shock [S1-S3; P2; P4].
   4. Perform contraindication checks and give the initial STEMI pharmacologic bundle per [P4]; withhold nitrates and beta-blockers given hypotension concern [S4; S3; P2; P4].
   5. Decide and execute reperfusion: primary PCI if achievable within [P4] window; otherwise consider fibrinolysis within [P4] window only if no contraindications and dissection is excluded [S1; S4; P2; P4].
   6. Reassess hemodynamics, RV failure, arrhythmia, and response to therapy; involve critical care and cardiothoracic/vascular consultation if dissection or obstructive shock is suspected [S3; S2; P4].

2. **Reperfusion pathway**
   - Indicated strategy: emergent reperfusion for STEMI per [P4]. Primary PCI is preferred if it can be delivered within the consensus [P4] time window; if not, fibrinolysis within the consensus [P4] door-to-needle window may be considered if no contraindications and aortic dissection is excluded [S1; S4; P2; P4].
   - Required to finalize:
     - `UNABLE TO TRACE: symptom onset-to-presentation interval`
     - `UNABLE TO TRACE: PCI availability/transport time`
     - `UNABLE TO TRACE: fibrinolysis contraindications and bleeding risk`
     - `UNABLE TO TRACE: allergies and current medications`
     - `UNABLE TO TRACE: renal function/coagulation`
     - `UNABLE TO TRACE: aortic dissection status`

3. **Initial pharmacologic and monitoring bundle**
   - **Aspirin:** indicated for suspected STEMI/ischemic chest pain [P2; P4]. Withhold for aspirin allergy or active bleeding. `UNABLE TO TRACE: aspirin allergy and active bleeding status`
   - **P2Y12 inhibitor:** indicated per STEMI/PCI protocol [P4]. Withhold for allergy, active bleeding, or severe thrombocytopenia. `UNABLE TO TRACE: allergy, bleeding risk, CBC/platelets`
   - **Anticoagulation:** indicated per STEMI/PCI protocol [P4]. Withhold for active bleeding, severe thrombocytopenia, severe renal impairment, or suspected/confirmed aortic dissection. `UNABLE TO TRACE: bleeding risk, CBC/platelets, renal function, and dissection status`
   - **Nitrates:** generally for ischemic pain, but withhold here because SBP is 90/60 and RV infarction may be present [S3; P2; P4]. `UNABLE TO TRACE: RV infarct status and PDE5 inhibitor use`
   - **Beta-blocker:** withhold until hemodynamic stability because BP 90/60 and shock risk are present [S3; P2; P4]. `UNABLE TO TRACE: heart failure status, baseline conduction/bradycardia, and cocaine use`
   - **Oxygen:** titrate to [P4] target because SpO2 94% and dyspnea are present [P2; P4]. `UNABLE TO TRACE: baseline oxygen target/COPD history`
   - **Continuous ECG monitoring/defibrillator:** indicated for STEMI with hypotension/tachycardia [S1; S3; P2; P4]. No missing data for this monitoring component.
   - **IV access and labs:** CBC, chemistry, coagulation, troponin, and lactate per [P4]. `UNABLE TO TRACE: laboratory results`

4. **Contraindication and interaction check**
   - Nitrates: withheld because BP 90/60 is present; also check PDE5 inhibitor use — `UNABLE TO TRACE: PDE5 inhibitor use`.
   - Beta-blocker: withheld because hypotension/shock risk is present; evaluate heart failure and conduction disease — `UNABLE TO TRACE: heart failure status, baseline conduction/bradycardia, cocaine use`.
   - Aspirin/P2Y12/anticoagulation: allergy, bleeding risk, CBC/platelets, renal function, and dissection status are not provided — `UNABLE TO TRACE: allergy, bleeding risk, CBC/platelets, renal function, and dissection status`.
   - Reperfusion: fibrinolysis contraindications and PCI timing cannot be finalized — `UNABLE TO TRACE: onset-to-presentation interval, PCI availability/transport time, bleeding risk, and dissection status`.

5. **Parallel diagnostic actions**
   - Right-sided and posterior ECG, repeat 12-lead — closes [S1]/[S3] right-sided/posterior/RV gaps.
   - Bedside echocardiogram — assesses RV involvement, wall-motion abnormality, tamponade, and gross aortic root pathology [S1-S3; P4].
   - Serial troponin — supports/refines [S1] diagnosis; `UNABLE TO TRACE: troponin value and delta`.
   - CTA chest/TEE if dissection or PE is suspected; CXR/bedside ultrasound for pneumothorax/tamponade — closes [S2] gaps [P4].
   - CBC, chemistry, coagulation, lactate, urine output — closes [S3]/[S4] shock and contraindication gaps.
   - Cardiology/catheterization, critical care, and cardiothoracic/vascular consults as indicated by instability or suspected dissection/obstructive shock [S2-S4; P4].

---

## FORMAL CONCLUSION

### Evidence-ranked differential
1. **Inferior STEMI** — most likely, supported by contiguous inferior ST elevation, radiating chest pain, diaphoresis, and high-risk hemodynamics [S1; P1; P2; P4].
2. **Aortic dissection** — must be excluded because of hypotensive/tachycardic presentation and potential for inferior lead changes; antithrombotic/fibrinolytic therapy could be hazardous [S2; P1; P2; P4].
3. **Pulmonary embolism** — must be considered because of hypoxia, tachycardia, hypotension, and dyspnea [S2; S3; P2; P4].
4. **Obstructive shock (tamponade/tension pneumothorax)** — must be rapidly excluded because of hypotension/tachycardia/hypoxia [S2; S3; P2; P4].
5. **Pericarditis/myocarditis / early repolarization** — less likely ECG mimics; not fully excluded without full ECG, history, and echocardiogram [S2; P2; P4].

**Single most likely diagnosis:** inferior STEMI [S1; P2; P4].

### Acuity statement
**High acuity/critical.** The physiologic basis is STEMI with SBP 90/60, HR 110, and SpO2 94%, indicating hypotension, tachycardia, and hypoxemia with risk of shock, RV failure, arrhythmia, and rapid deterioration [S3; P2; P4].

### High-acuity exclusions required
- Aortic dissection [S2; P1; P2; P4].
- Pulmonary embolism [S2; S3; P2; P4].
- Obstructive shock, including tamponade and tension pneumothorax [S2; S3; P2; P4].
- Pericarditis/myocarditis if it would change antithrombotic or reperfusion management [S2; P2; P4].

### Immediate priorities
1. Activate STEMI/reperfusion pathway and cardiology/catheterization team [S1; P2; P4].
2. Monitor, defibrillator pads, IV access, and oxygen/ventilation to target [S3; P2; P4].
3. Obtain right-sided/posterior and repeat ECG, troponin, lactate, renal/coagulation labs, bedside echo, and exclusion workup for dissection/PE/obstructive shock [S1-S3; P2; P4].
4. Check contraindications and administer initial STEMI pharmacologic bundle per [P4]; withhold nitrates/beta-blockers given hypotension [S4; S3; P2; P4].
5. Finalize and execute reperfusion: primary PCI if within [P4] window; fibrinolysis only if PCI unavailable in window, no contraindications, and dissection excluded [S1; S4; P2; P4].
6. Reassess hemodynamics, RV failure, arrhythmia, and response; escalate to critical care and appropriate consults [S3; S2; P4].

### Verification gaps
| Trace | `UNABLE TO TRACE` item | Required to close |
|---|---|---|
| S1 | reciprocal ST depression in I/aVL | Repeat/full 12-lead ECG |
| S1/S3 | right-sided lead findings | Right-sided ECG |
| S1 | posterior lead findings (V7-V9) | Posterior ECG |
| S1/S4 | troponin value and delta | Serial troponin with assay |
| S1/S4 | symptom onset-to-presentation interval | History |
| S1/S2 | prior and serial ECG data | Prior tracing and repeat ECG |
| S1/S4 | PMH, prior cardiac history, current medications, allergies, risk factors | History, medication reconciliation, allergy review |
| S2/S4 | CT angiography/TEE and pulse/BP differential for dissection | Vascular imaging and bilateral BP/pulse exam |
| S2 | CTPA, D-dimer, RV strain echo, VTE risk factors | CTPA, D-dimer, echocardiogram, VTE history |
| S2 | full ECG for PR depression/diffuse STE, positional/pleuritic history, echocardiogram | Full ECG, targeted history, echo |
| S2 | bedside ultrasound, CXR, obstructive-shock physical findings | Bedside ultrasound, CXR, focused exam |
| S3 | lactate, urine output, mentation, capillary refill, serial BP | Measure and trend |
| S3 | bedside RV findings (JVD, Kussmaul, clear lungs) | Focused exam and echo |
| S3 | response to preload challenge | Protocolized fluid challenge with monitoring |
| S3 | echocardiographic RV assessment | Bedside echocardiogram |
| S4 | PCI availability/transport time | STEMI system status |
| S4 | fibrinolysis contraindications and bleeding risk | History, neuro exam, labs |
| S4 | renal function/coagulation | Laboratory testing |
| S4 | aspirin allergy and active bleeding status | History |
| S4 | allergy, bleeding risk, CBC/platelets | History and CBC |
| S4 | RV infarct status and PDE5 inhibitor use | Right-sided ECG/echo and medication history |
| S4 | heart failure status, baseline conduction/bradycardia, cocaine use | Exam, ECG, history |
| S4 | baseline oxygen target/COPD history | History and SpO2 trend |
| S4 | laboratory results | CBC, chemistry, coagulation, troponin, lactate |

---

## REMEDIATION / NEXT ACTION

1. **Immediate stabilization sequence**
   1. Activate STEMI/catheterization pathway and place on continuous ECG monitoring with defibrillator available [S1; S3; P2; P4].
   2. Secure IV access; titrate oxygen to target; avoid hypotension-inducing agents [S3; P2; P4].
   3. Obtain right-sided/posterior ECG, repeat 12-lead, troponin, lactate, CBC, chemistry, coagulation, and bedside echocardiogram [S1-S3; P4].
   4. Check for dissection/obstructive shock/PE before fibrinolysis or full anticoagulation when clinically suspected [S2; P4].
   5. Administer STEMI bundle only after contraindication review; withhold nitrates and beta-blockers in this hypotensive presentation [S4; P2; P4].
   6. Finalize reperfusion strategy and execute per [P4] [S1; S4; P4].

2. **Closing verification gaps**
   - Reciprocal/full ECG: obtain repeat/full 12-lead to assess I/aVL reciprocal change [S1].
   - Right-sided/posterior leads: obtain V4R and V7-V9 to assess RV/posterior extension [S1; S3].
   - Troponin/onset/prior ECG/PMH/meds/allergies/risk factors: complete history, medication reconciliation, allergy review, serial troponin, and prior tracing [S1; S4].
   - Dissection/PE/obstructive shock: obtain CTA/TEE, pulse/BP differential, CTPA/D-dimer/echo, CXR, bedside ultrasound, and focused exam as indicated [S2; S3].
   - Shock/RV: obtain lactate, urine output, mentation/capillary refill, serial BP, bedside RV findings, preload challenge response, and echo RV assessment [S3].
   - Reperfusion/medication contraindications: obtain PCI availability/transport time, bleeding risk, CBC/platelets, renal/coagulation, PDE5 inhibitor use, heart failure/conduction history, and oxygen target/COPD history [S4].

3. **Reassessment checkpoints**
   - Immediately after monitoring/initial ECG: reassess [S3] shock and [S2] obstructive shock.
   - After right-sided/posterior ECG and bedside echo: reassess [S1] territory/RV extension and [S3] RV involvement.
   - After troponin/labs/coagulation: reassess [S1] diagnosis, [S3] shock, and [S4] contraindications.
   - Before reperfusion: reassess [S2] dissection/PE exclusions and [S4] bleeding/fibrinolysis contraindications.
   - After reperfusion and during serial vitals: reassess [S3] hemodynamics, arrhythmia, and response to treatment.

4. **Decision rules once missing elements are obtained**
   - **Reperfusion:** if PCI can be achieved within the [P4] consensus window, proceed with primary PCI; if not, and symptom onset is within the appropriate window, no contraindications exist, and dissection is excluded, use fibrinolysis within the [P4] door-to-needle window [S1; S4; P4].
   - **Suspected dissection:** if dissection is confirmed or highly suspected, avoid fibrinolytics/anticoagulation and pursue vascular/cardiothoracic management [S2; S4; P4].
   - **RV involvement:** if right-sided ECG/echo shows RV infarction without pulmonary edema, avoid nitrates/diuretics and use cautious preload per protocol; if pulmonary edema/cardiogenic shock is present, follow shock/failure management [S3; P2; P4].
   - **Oxygen target:** titrate to the [P4] target, accounting for COPD/CO2 retention history once obtained [S4; P2; P4].

**TRACEABILITY SELF-CHECK:** Completed. Formal Conclusion and priority sequence entries carry [S] and underlying [P] citations. Every absent-data item marked `UNABLE TO TRACE` in [S1]-[S4] appears in the Verification Gaps table.

**DISCLAIMER:** This output is structured analytical support, not clinical advice. All diagnostic and treatment decisions require a licensed healthcare clinician.

### EVALUATION: TEST 3

- **Word Count**: Baseline `165` words | Optimized `3054` words | Ratio `18.51x`
- **Eval Tokens**: Baseline `764` | Optimized `21053`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 4.5       | -0.5  |
| Completeness  | 4.5      | 5         | +0.5  |
| Structure     | 4.5      | 3.5       | -1.0  |
| Actionability | 5        | 3.5       | -1.5  |
| Traceability  | 2.5      | 5         | +2.5  |
| TOTAL         | 21.5/25  | 21.5/25   | +0.0  |

The optimized response improved traceability and completeness by explicitly citing premises, enumerating dangerous alternatives, and listing verification gaps. However, it introduced substantial bloat and indirect prioritization, burying immediate actions like aspirin and reperfusion timing under labs/imaging and omitting specific doses/windows. Accuracy was largely unchanged, with minor overcaution around oxygen use and dissection workup before antithrombotic therapy.

---

## TEST 4: Legal Analysis (Accuracy | Mode 1 (Max Certificate, Template 4 [L1]-[L3]))

### BASELINE RESPONSE

**Not legal advice; enforceability depends heavily on the governing state/country law. The employee should consult local employment counsel.**

### Bottom line
As written, this covenant is **likely vulnerable to a strong unenforceability challenge** in many U.S. jurisdictions because the combination of **5 years**, **200 miles**, and **“any related industry”** is very broad. The employee’s move—**150 miles away, 8 months later**—is a **literal breach if the covenant is enforceable**, but a literal breach does not mean a court will enforce the clause. Many courts would either refuse enforcement, narrow/reform it, or enforce only a much smaller restriction if the employer can show a protectable interest.

### Framework courts generally use
In most U.S. common-law states, a non-compete is enforceable only if it is:
1. **Ancillary to employment** and supported by consideration;
2. Necessary to protect a **legitimate business interest**—e.g., trade secrets, confidential information, customer relationships, specialized training;
3. **Reasonable in duration**;
4. **Reasonable in geographic scope**;
5. **Reasonable in the scope of prohibited activities**; and
6. Not contrary to public policy or unduly harsh to the employee.

Courts often construe ambiguities against the drafter and may “blue-pencil”/reform the covenant only if the jurisdiction allows it.

### Application to this clause
- **Duration: 5 years post-employment.** This is unusually long. Most enforceable employee noncompetes run **6–24 months**; 5 years is generally associated with sale-of-business covenants or very unusual circumstances. This is a major overbreadth problem.
- **Geography: 200-mile radius.** Courts ask whether the radius is tied to the employee’s actual territory, customer contacts, or the employer’s protectable market. A 200-mile radius can be huge and may cover areas where the employee never worked and the employer has no meaningful business. Also, “radius” from what location is ambiguous if the employer has multiple offices.
- **Scope: “any related industry.”** This is vague and extremely broad. It could bar the employee from any role—even noncompetitive, non-customer-facing, or unrelated work—at any company loosely “related” to the industry. Courts usually prefer restrictions limited to **same/similar services, customers the employee served, or confidential information the employee had**.
- **Legitimate interest.** If the employee had access to trade secrets, key customer relationships, or specialized confidential information, the employer has a stronger argument. If the employee was ordinary/non-exempt, had no customer contact, and received no special training, the covenant is much weaker.
- **Consideration.** In many states, initial employment or continued employment can be sufficient consideration; some states require more. This depends on jurisdiction.
- **Breach.** If the clause is enforceable as written, working for a competitor 150 miles away within 8 months is within the literal restrictions. But the employee’s best defense is that the clause is **overbroad and unenforceable**, or enforceable only after judicial narrowing.

### Likely outcome
In many jurisdictions, a court would find the **combined** 5-year/200-mile/any-related-industry restriction unreasonable. Some states would **void the entire covenant**; others would **reform** it to something like 12–24 months, limited to the employee’s actual territory/customers or same-type role. A few employer-friendly states may enforce broader covenants, but even there 5 years and “any related industry” are aggressive.

Also note:
- **California, Minnesota, North Dakota, Oklahoma** and some other jurisdictions severely restrict or ban most employee noncompetes.
- States like **Florida and Texas** are more employer-friendly but still require reasonableness; 5 years is likely problematic outside sale-of-business contexts.
- Choice-of-law clauses may matter, but some states refuse to apply another state’s law if it would undermine their own noncompete policy.
- The FTC’s 2024 noncompete rule was set aside in federal litigation and is **not a nationwide ban**; state law remains controlling.

### Practical conclusion
The former employer can threaten suit and may seek a temporary restraining order/injunction, but it would likely face a serious enforceability fight. The employee should **not ignore the threat**, should preserve the agreement and communications, and should get local counsel to assess the governing law, the employee’s role/access to confidential information, and whether reformation is available. Separate claims for **trade-secret misappropriation or breach of confidentiality** can survive even if the non-compete is invalid.

### OPTIMIZED PROMPT

The standard legal analytical protocol requires completing this reasoning certificate before presenting any enforceability assessment. Complete every section using the operative clause text and controlling authority supplied in the premises; where an element is not supplied, record the missing input rather than substituting a default rule.

### PREMISES

- [P1] Agreement text under review: [insert the operative restraint clauses verbatim, including (a) activity scope as written ("any related industry"), (b) geographic limit (200-mile radius and the reference point it is measured from), (c) temporal limit (5 years post-termination), and (d) any choice-of-law, severability, reformation, step-down, or tolling clause]
- [P2] Governing law: [insert jurisdiction and the controlling statute plus the leading appellate standard for restraint-of-trade enforceability in that jurisdiction]
- [P3] Factual record, stated as observable facts separate from inference: signing date and role at signing [insert]; consideration received at signing [continued employment / promotion / bonus / equity / initial hire — specify]; separation date [insert]; distance from the [origin office / employee residence / contract territory] to the new employer (150 miles); elapsed time at commencement of new employment (8 months); similarity of actual new duties to prior duties [describe]; whether the new employer competes for the same customers, products, or territory [specify]
- [P4] Analytical boundaries: assessment limited to enforceability of the covenant as written and as applied to the described move. Damages quantification, injunctive procedure, and litigation posture are outside this certificate. Facts not listed in [P3] are treated as unverified.

### LEGAL TRACES

For each issue below, quote the exact clause language and the exact statutory or case citation relied on.

- [L1] Validity of each restraint dimension as drafted
  1. Governing text: [quote P1 language for duration, geography, and activity scope]
  2. Rule application: [apply the P2 standard separately to each of the three dimensions; state whether each is within, at the outer edge of, or beyond the range courts in P2 have enforced]
  3. Counter-interpretation: [state the strongest reading favoring enforceability, including any reformation or blue-pencil doctrine available under P2]
  4. Severability consequence: [state whether P1 and P2 permit enforcement of a narrowed covenant, or whether invalidity of one dimension defeats the covenant in whole or in part]

- [L2] Protectable interest and consideration
  1. Governing rule: [list the legitimate protectable-interest categories P2 recognizes, and the consideration P2 requires]
  2. Record evidence: [map each P3 fact to a category, marking categories with no supporting P3 fact as UNABLE TO TRACE: [missing fact]]
  3. Consideration analysis: [state what the employee received and whether P2 treats it as sufficient]
  4. Counter-interpretation: [state the argument that the interest asserted is ordinary market competition or generalized skill rather than a protectable interest]

- [L3] Reasonableness as applied to the actual move
  1. Geographic application: [determine from P3 whether the new role is actually performed inside the restricted territory, and identify the reference point the 200-mile radius is measured from under P1]
  2. Temporal application: [apply the 8-month interval to the 5-year term and to any tolling clause in P1]
  3. Activity application: [compare "any related industry" as written against the actual new duties in P3]
  4. Hardship and public interest: [state the P3 facts bearing on employee hardship and any public-interest factor P2 recognizes]
  5. Choice-of-law: [state the clause in P1, or record NOT ADDRESSED IN [P1]: choice of law, and identify the conflict consequence under P2]

Grounding rule: Anchor every trace in quoted P1 language or an identified P2 citation. When P2 is absent or the jurisdiction is unstated, record `UNABLE TO TRACE: governing law` and present the outcome as a jurisdiction-conditional matrix keyed to the distinct doctrinal positions rather than a single verdict. When P3 lacks a fact an element requires, record `UNABLE TO TRACE: [element]` in the relevant trace.

### FORMAL CONCLUSION

- Dimension-by-dimension disposition: [separate dispositions for duration, geographic scope, activity scope, protectable interest, and consideration, each citing L-identifiers]
- Overall enforceability posture: [enforceable as written / enforceable only as narrowed / unenforceable as written — grounded exclusively in the L traces]
- Controlling authority: [statute and case citations from P2 relied on for each disposition]
- Verification gaps: [every item marked UNABLE TO TRACE or NOT ADDRESSED, with the specific document, jurisdiction, or fact required to close it]

### REMEDIATION / NEXT ACTION

The certificate is incomplete until this section contains:
- A prioritized information-request list naming each document and fact needed to close the Verification Gaps (executed agreement with all exhibits, choice-of-law and severability clauses, signing-date consideration evidence, job-description comparison, and the geographic reference point the radius is measured from)
- Where the record supports a narrowed covenant under P2, a copy-pasteable redline of the restraint clause to the defensible duration, radius, and activity scope, with the P2 authority for each revised term
- Otherwise, the explicit statement: "No remediation available on the supplied record: [reason citing L-identifiers]"

DISCLAIMER: This output is structured analytical support, not legal advice. Binding determinations require qualified counsel licensed in the governing jurisdiction.

### VERIFICATION & TRACEABILITY CONTRACT

- Grounding rule: Base every statement in [L1]-[L3] on quoted P1 clause language or an identified P2 citation, not on general familiarity with non-compete doctrine.
- Missing-evidence predicate: When a required element is absent from P1-P3, record `UNABLE TO TRACE: [exact missing input]` in that trace and list it under Verification Gaps.
- Jurisdiction predicate: When P2 supplies no governing law, produce the matrix of doctrinal positions with each branch labeled UNABLE TO TRACE and its own disposition, rather than selecting one jurisdiction's rule.
- Counterevidence predicate: When a P3 fact undercuts the enforceability position reached in a trace, record it as a separate numbered item inside that trace even if the overall disposition is unchanged.
- Neutrality predicate: Derive dispositions strictly from the L traces without reference to any party's litigation position, negotiation leverage, or desired outcome.

TRACEABILITY SELF-CHECK (complete before finalizing): Confirm that every claim in the Formal Conclusion cites at least one L identifier, that every quoted clause carries a P1 citation, and that every legal rule carries a P2 citation. Where a claim lacks a supporting identifier, either add the trace from P1-P3 or remove the claim so zero orphaned conclusions remain.

### OPTIMIZED RESPONSE

# CERTIFICATE — LEGAL ANALYTICAL PROTOCOL

**Status: INCOMPLETE — UNABLE TO TRACE / NOT DETERMINABLE**

## Intake Summary

| Premise | Supplied content | Missing / trace issue |
|---|---|---|
| **P1** | Only the insertion template is supplied. It references, in P1, activity scope “as written (`"any related industry"`)”; geographic limit “(`200-mile radius and the reference point it is measured from`)”; temporal limit “(`5 years post-termination`)”; and choice-of-law/severability/reformation/step-down/tolling clauses. These are not supplied as verbatim operative clauses. | `UNABLE TO TRACE: operative restraint clauses verbatim`; `UNABLE TO TRACE: geographic reference point`; `UNABLE TO TRACE: choice-of-law/severability/reformation/step-down/tolling clauses` |
| **P2** | No jurisdiction, statute, or leading appellate standard supplied. | `UNABLE TO TRACE: governing law` |
| **P3** | Supplied: distance to new employer = **150 miles**, but the reference point is unselected; elapsed time at commencement of new employment = **8 months**. All other P3 fields are placeholders. | `UNABLE TO TRACE: signing date and role`; `UNABLE TO TRACE: consideration at signing`; `UNABLE TO TRACE: separation date`; `UNABLE TO TRACE: geographic reference point`; `UNABLE TO TRACE: actual new duties`; `UNABLE TO TRACE: employer competition facts` |

---

## [L1] Validity of Each Restraint Dimension as Drafted

### 1. Governing text

- **Duration:** P1 supplies only the template phrase “(`5 years post-termination`).” `UNABLE TO TRACE: verbatim duration clause and tolling clause`.
- **Geography:** P1 supplies only the template phrase “(`200-mile radius and the reference point it is measured from`).” `UNABLE TO TRACE: verbatim geographic clause and geographic reference point`.
- **Activity scope:** P1 supplies only the template phrase “(`"any related industry"`).” `UNABLE TO TRACE: verbatim activity-scope clause and definitions`.

### 2. Rule application

`UNABLE TO TRACE: governing law`. P2 supplies no jurisdiction, statute, or appellate standard. Therefore the certificate cannot classify duration, geography, or activity scope as within, at the outer edge of, or beyond an enforceable range.

### 3. Counter-interpretation

`UNABLE TO TRACE: governing law and exact P1 clause text`. The strongest enforceability reading, including reformation or blue-pencil doctrine, cannot be identified without P2 authority and the operative P1 clauses.

### 4. Severability consequence

`UNABLE TO TRACE: severability/reformation/step-down clause in P1 and governing doctrine in P2`. It cannot be determined whether a narrowed covenant could be enforced or whether invalidity of one dimension defeats the covenant in whole or in part.

---

## [L2] Protectable Interest and Consideration

### 1. Governing rule

`UNABLE TO TRACE: governing law`. P2 supplies no protectable-interest categories and no consideration rule.

### 2. Record evidence

| Required mapping | Trace result |
|---|---|
| Map P3 facts to P2 protectable-interest categories | `UNABLE TO TRACE: governing law` and `UNABLE TO TRACE: actual new duties; same customers/products/territory; role at signing; separation facts` |
| Legitimate interest category 1 | `UNABLE TO TRACE: category not supplied by P2` |
| Legitimate interest category 2 | `UNABLE TO TRACE: category not supplied by P2` |
| Any additional category | `UNABLE TO TRACE: governing law` |

The only supplied P3 facts relevant to distance/time are 150 miles and 8 months. They do not map to any P2 protectable-interest category because P2 supplies none.

### 3. Consideration analysis

`UNABLE TO TRACE: consideration received at signing`. P3 gives only a placeholder — “continued employment / promotion / bonus / equity / initial hire — specify” — and P2 supplies no sufficiency rule.

### 4. Counter-interpretation

`UNABLE TO TRACE: governing law and P3 facts`. The argument that the interest is ordinary market competition or generalized skill cannot be evaluated without P2 doctrine and P3 facts describing actual duties and employer competition.

---

## [L3] Reasonableness as Applied to the Actual Move

### 1. Geographic application

P3 supplies **150 miles** from the `[origin office / employee residence / contract territory]` to the new employer, but the reference point is not selected. P1’s 200-mile radius reference point is also `UNABLE TO TRACE: geographic reference point`. Actual place of performance of the new role is `UNABLE TO TRACE: actual performance location`.

Thus: `UNABLE TO TRACE: whether the new role is performed inside the restricted territory`. Although 150 is numerically less than 200, the certificate cannot infer that the relevant performance occurred within the radius.

### 2. Temporal application

P3 supplies **8 months** elapsed at commencement of new employment. P1 supplies only the template phrase “(`5 years post-termination`).” On the literal arithmetic, 8 months is less than 5 years, but the exact trigger, tolling clause, and governing reasonableness rule are `UNABLE TO TRACE: verbatim temporal/tolling clause and governing law`.

### 3. Activity application

P1 supplies only the phrase “(`"any related industry"`).” P3 does not describe actual new duties. Therefore: `UNABLE TO TRACE: exact activity-scope clause` and `UNABLE TO TRACE: actual new duties`.

### 4. Hardship and public interest

`UNABLE TO TRACE: P3 hardship facts` and `UNABLE TO TRACE: P2 public-interest factors`. No P3 fact supplied bears on employee hardship, and no P2 factor is supplied.

### 5. Choice-of-law

`NOT ADDRESSED IN [P1]: choice of law`. P2 supplies no conflict-of-laws rule. Therefore: `UNABLE TO TRACE: choice-of-law clause and conflict consequence`.

---

# FORMAL CONCLUSION

## Dimension-by-Dimension Disposition

| Dimension | Disposition | Trace basis |
|---|---|---|
| Duration | `UNABLE TO TRACE: governing law; verbatim duration/tolling clause` | L1; L3.2 |
| Geographic scope | `UNABLE TO TRACE: governing law; geographic reference point; actual performance location` | L1; L3.1 |
| Activity scope | `UNABLE TO TRACE: governing law; exact activity clause; actual new duties` | L1; L3.3 |
| Protectable interest | `UNABLE TO TRACE: governing law; P2 categories; P3 facts` | L2 |
| Consideration | `UNABLE TO TRACE: governing law; consideration at signing` | L2 |

## Overall Enforceability Posture

**Not determinable on the supplied record — no single verdict.** P2 is absent, so the required jurisdiction-conditional matrix cannot be populated with any jurisdiction’s rule. The certificate cannot conclude “enforceable as written,” “enforceable only as narrowed,” or “unenforceable as written” under L1-L3.

### Jurisdiction-Conditional Matrix — Empty Due to Absence of P2

| Doctrinal position slot | Required P2 authority | P1/P3 inputs | Disposition |
|---|---|---|---|
| Unspecified per-se-invalid / no-enforcement regime | `UNABLE TO TRACE: governing law` | `UNABLE TO TRACE: P1/P2/P3` | `UNABLE TO TRACE: L1-L3` |
| Unspecified statutory-limits regime | `UNABLE TO TRACE: governing law` | `UNABLE TO TRACE: P1/P2/P3` | `UNABLE TO TRACE: L1-L3` |
| Unspecified common-law reasonableness / protectable-interest regime | `UNABLE TO TRACE: governing law` | `UNABLE TO TRACE: P1/P2/P3` | `UNABLE TO TRACE: L1-L3` |
| Unspecified consideration-specific regime | `UNABLE TO TRACE: governing law` | `UNABLE TO TRACE: P1/P2/P3` | `UNABLE TO TRACE: L1-L3` |
| Unspecified reformation / blue-pencil / severability regime | `UNABLE TO TRACE: governing law` | `UNABLE TO TRACE: P1/P2/P3` | `UNABLE TO TRACE: L1-L3` |
| Unspecified no-reformation / whole-covenant-invalid regime | `UNABLE TO TRACE: governing law` | `UNABLE TO TRACE: P1/P2/P3` | `UNABLE TO TRACE: L1-L3` |
| Unspecified choice-of-law / conflict regime | `UNABLE TO TRACE: governing law` | `UNABLE TO TRACE: P1/P2/P3` | `UNABLE TO TRACE: L1-L3` |

## Controlling Authority

`UNABLE TO TRACE: governing law`. No P2 statute or case citation was supplied for any disposition. No controlling authority is relied on because none is present in the premises. See L1-L3.

## Verification Gaps

1. `UNABLE TO TRACE: operative restraint clauses verbatim` — executed agreement with all exhibits required.
2. `UNABLE TO TRACE: geographic reference point` — P1 clause and P3 reference point required.
3. `UNABLE TO TRACE: choice-of-law/severability/reformation/step-down/tolling clauses` — full agreement text required.
4. `UNABLE TO TRACE: governing law` — jurisdiction, controlling statute, and leading appellate standard required.
5. `UNABLE TO TRACE: signing date and role at signing` — P3 facts required.
6. `UNABLE TO TRACE: consideration at signing` — P3 facts and documentary evidence required.
7. `UNABLE TO TRACE: separation date` — P3 fact required.
8. `UNABLE TO TRACE: actual new duties` — job-description comparison required.
9. `UNABLE TO TRACE: employer competition facts` — whether new employer competes for same customers, products, or territory required.
10. `UNABLE TO TRACE: actual performance location` — needed for geographic application.
11. `UNABLE TO TRACE: hardship/public-interest facts` — only if relied on by governing law.
12. `NOT ADDRESSED IN [P1]: choice of law` — choice-of-law clause and P2 conflict rule required.

---

# REMEDIATION / NEXT ACTION

## Prioritized Information-Request List

1. **Executed agreement with all exhibits and verbatim restraint clauses** — to close P1/L1 gaps.
2. **Governing-law memo with jurisdiction, controlling statute, and leading appellate standard** — to close P2/L1-L3 gaps.
3. **Choice-of-law, severability, reformation, step-down, and tolling clauses** — to close L1.3-L1.4 and L3.5.
4. **Signing-date role, consideration evidence, and separation date** — to close L2 consideration and temporal gaps.
5. **Geographic reference point and actual work location of new role** — to close L3.1.
6. **Job-description comparison and employer competition evidence** — to close L2 and L3.3.
7. **Hardship/public-interest facts, if recognized by P2** — to close L3.4.

## Narrowed Covenant / Redline

No redline can be responsibly generated because P1 does not supply the operative clause text and P2 does not supply governing authority. The record therefore does not support a narrowed covenant under P2.

**No remediation available on the supplied record: L1 (no verbatim restraint clauses or governing standard to define a defensible duration, radius, or activity scope), L2 (no P2 protectable-interest/consideration rule and no P3 consideration/interest facts), L3 (no P1 geographic reference point and no P3 actual-performance/activity facts).**

---

## TRACEABILITY SELF-CHECK

- Every Formal Conclusion disposition cites an L identifier or records `UNABLE TO TRACE`.
- Every quoted P1 fragment is identified as P1 template language; no verbatim operative clause is presented because none is supplied.
- Every legal rule is absent from P2, so no non-P2 legal rule has been applied.
- Zero orphaned conclusions: all unresolved items are recorded in Verification Gaps.

**DISCLAIMER:** This output is structured analytical support, not legal advice. Binding determinations require qualified counsel licensed in the governing jurisdiction.

### EVALUATION: TEST 4

- **Word Count**: Baseline `667` words | Optimized `1648` words | Ratio `2.47x`
- **Eval Tokens**: Baseline `3327` | Optimized `10629`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4.5      | 3.5       | -1.0  |
| Completeness  | 4.5      | 2.5       | -2.0  |
| Structure     | 4.5      | 3.0       | -1.5  |
| Actionability | 5.0      | 2.5       | -2.5  |
| Traceability  | 3.5      | 4.5       | +1.0  |
| TOTAL         | 22/25    | 16/25     | -6    |

The optimized response improved formal traceability by explicitly marking missing premises and tying conclusions to L-identifiers, but it became an extensive gap report rather than an enforceability analysis and failed to populate the required jurisdiction-conditional doctrinal matrix. The baseline response was far more complete and actionable, accurately identifying the overbreadth problems and practical next steps, while being less formally traceable because it relied on general non-compete doctrine rather than a supplied P2 authority. The certificate structure in the optimized response added repetitive bloat without delivering the substantive legal assessment the task called for.

---

## TEST 5: Research Synthesis (Mixed | Mode 1 (Max Certificate, Template 5 [E1]-[E3]))

### BASELINE RESPONSE

**Bottom line:** The research does **not** support a blanket claim that remote work uniformly “improves” or “hurts” productivity. The best-supported summary is: **remote work is roughly neutral to modestly positive for many individual, focused tasks; mixed-to-negative for coordination-heavy, creative, mentoring, and onboarding tasks; and hybrid arrangements have the strongest evidence for preserving performance while improving retention.** Effects depend heavily on task, worker experience, management, measurement, and whether the arrangement is fully remote or hybrid.

### Key evidence

- **Routine, individual work can improve.** The classic randomized field experiment at a Chinese call center (Bloom et al., 2015) found that working from home raised performance by about **13%**, mainly through more minutes worked and slightly higher call rates, and reduced attrition. But this was a repetitive, easily measured job—so it generalizes poorly to complex collaborative work.

- **Hybrid can be performance-neutral with retention gains.** A large randomized hybrid trial at Trip.com (Bloom, Han & Liang, 2024, *Nature*) found that **three days in office / two days home** did **not** damage performance or promotions, while **quit rates fell by about one-third**, especially for women, non-managers, and long commuters. This is among the strongest causal evidence for hybrid work.

- **Fully remote can lower productivity in some settings.** Firm data from IT/professional-service settings have found lower output under full WFH, especially where tasks require coordination; one large IT-firm study estimated roughly **10–20% lower productivity** in that context. Pandemic-era estimates are confounded by school closures, stress, and ad hoc setups, so they are not clean tests of voluntary remote work.

- **Collaboration and innovation are the weak spot.** A Microsoft study (Yang et al., 2022, *Nature Human Behaviour*) found firmwide remote work made collaboration networks more **siloed**, with fewer cross-group ties and more asynchronous communication. Individual output may hold up while cross-team idea flow, mentoring, and onboarding suffer. Evidence on innovation is thinner and more uncertain than evidence on short-run output.

- **Measurement matters.** Self-reported productivity often looks positive; objective output measures are more mixed. Remote workers may work longer hours, which can mask lower hourly productivity or create burnout. “Productivity” also includes quality, innovation, retention, and learning—not just calls or tickets per hour.

### What moderates the effect

Remote work tends to work better for **experienced workers**, **independent and well-defined tasks**, **good home setups**, and **managers who set clear goals and communicate asynchronously**. It tends to be riskier for **early-career workers**, **complex interdependent work**, **creative brainstorming**, **mentoring**, and **rapid onboarding**. Commute length and retention effects also matter: remote/hybrid can be a major retention benefit even when output effects are neutral.

### Practical reading

- **Fully remote:** viable and often productive for independent, measurable roles, but average effects may be slightly negative in coordination-heavy settings and risks are higher for junior staff and innovation.
- **Hybrid:** best-supported compromise; performance often stays flat while retention improves—but in-office time should be intentional for collaboration, mentoring, and onboarding.
- **Don’t use attendance as a productivity proxy.** The evidence favors piloting arrangements, measuring outputs and quality, and watching collaboration, burnout, and early-career development.

### OPTIMIZED PROMPT

You are a research analyst. The standard systematic research synthesis protocol requires completing the following Max Certificate before presenting any synthesis. Every section must be completed using observable source artifacts.

### PREMISES
- [P1] Source corpus: Peer-reviewed empirical studies, meta-analyses, field experiments, and large-scale organizational evidence on remote work and productivity that you can identify with sufficient bibliographic detail from your internal knowledge or retrievable sources.
- [P2] Research question: Under what conditions, for which occupations and task types, and through which mechanisms does remote work improve or reduce productivity?
- [P3] Analytical scope: Distinguish productivity metrics (output, quality, efficiency, innovation, collaboration, absenteeism, hours), work arrangements (fully remote, hybrid, remote-only days), worker and occupation types, and time horizon (short-term versus long-term).
- [P4] Assumptions and limitations: No external database or full-text corpus is supplied. When a source, sample, effect size, or condition cannot be verified from available knowledge or retrievable sources, record `UNABLE TO TRACE: [exact missing input]` and list it under Verification Gaps.

### EVIDENCE TRACES
For each of the three evidence streams, trace the concrete source findings and boundary conditions:
- [E1] Evidence stream: Productivity improvements associated with remote work.
  1. Source(s) and design: [author/year, meta-analysis / field experiment / observational study, sample and context]
  2. Productivity metric and measured effect: [exact metric, direction, magnitude if reported]
  3. Mechanism: [focus time, commuting reduction, autonomy, reduced interruptions, etc.]
  4. Boundary conditions: [occupation/task, tenure, managerial support, home-office quality, etc.]
  5. Counterevidence within this stream: [any null or conflicting findings from cited sources]

- [E2] Evidence stream: Productivity reductions or harms associated with remote work.
  1. Source(s) and design: [author/year, meta-analysis / field experiment / observational study, sample and context]
  2. Productivity metric and measured effect: [exact metric, direction, magnitude if reported]
  3. Mechanism: [collaboration friction, onboarding or mentoring loss, communication overhead, isolation, etc.]
  4. Boundary conditions: [task interdependence, team distribution, experience level, etc.]
  5. Counterevidence within this stream: [any exceptions or conflicting findings from cited sources]

- [E3] Evidence stream: Moderators, mechanisms, and conditional synthesis.
  1. Moderator(s): [hybrid versus fully remote, task type, worker experience, manager practices, etc.]
  2. Comparative evidence: [which studies support or contradict each moderator]
  3. Causal versus correlational status: [field experiment versus observational evidence]
  4. Net direction under stated conditions: [where evidence converges or diverges]
  5. Verification gaps: [unresolved questions or missing source details]

Grounding rule: Base every trace on named empirical work, measured outcomes, and cited conditions rather than generic opinion. When a source, sample, effect size, or condition cannot be verified, record `UNABLE TO TRACE: [exact missing input]` in the trace and list it under Verification Gaps. When disconfirming evidence appears, record it as a dedicated item even if the overall pattern is positive. When sources disagree, record both findings under [E3] and label the claim `CONTESTED`.

### FORMAL CONCLUSION
- Overall synthesis: [derived solely from E1-E3, not from general preference]
- Conditions where remote work is associated with higher productivity: [cite E identifiers]
- Conditions where remote work is associated with lower productivity: [cite E identifiers]
- Evidence quality and contested claims: [group by E identifiers and note causal strength]
- Verification gaps: [all UNABLE TO TRACE items and unresolved moderators]

### REMEDIATION / NEXT ACTION
The task is incomplete until this section provides one of:
- A concrete research protocol listing the exact databases, search terms, and inclusion criteria needed to close the Verification Gaps
- A structured evidence table template with columns for source, design, sample/context, productivity metric, effect direction, moderators, and verification status
- The explicit statement: "No remediation required: [reason grounded in E-identifiers]" if all claims are traceable

VERIFICATION & TRACEABILITY CONTRACT:
- Grounding rule: Base every step in [E] traces on explicit study details, measured outcomes, and cited conditions rather than author names or generic claims.
- Missing-evidence predicate: When a path cannot be verified from available knowledge or a named source, record `UNABLE TO TRACE: [exact missing input]` in the trace and list it under Verification Gaps.
- Counterexample predicate: When disconfirming evidence or edge-case failures appear, record them as a dedicated [E] trace even if the overall verdict is positive.
- Neutrality predicate: Derive the synthesis strictly from [E] traces without referencing downstream business goals, timelines, or evaluation rubrics.
- Citation predicate: When a citation includes a specific source, include author/year, study design, sample/context, and the measured productivity outcome; when any of these is missing, mark the citation `INCOMPLETE CITATION` and exclude it from the Formal Conclusion.

TRACEABILITY SELF-CHECK (mandatory before finalizing):
Verify that every claim in the Formal Conclusion cites at least one [E] identifier from above. If any claim lacks a supporting identifier, either add the missing trace from [P1]-[P4] or remove the claim so zero orphaned conclusions remain.

### OPTIMIZED RESPONSE

# MAX CERTIFICATE

## PREMISES

- **[P1] Source corpus:** Named peer-reviewed empirical studies, field experiments, natural experiments, observational organizational studies, and meta-analytic material on remote work and productivity, identified from internal bibliographic knowledge. Exact unverifiable details are marked `UNABLE TO TRACE`.
- **[P2] Research question:** Under what conditions, for which occupations/task types, and through which mechanisms does remote work improve or reduce productivity?
- **[P3] Analytical scope:** Distinguishes productivity metrics (output, quality, efficiency, innovation, collaboration, absenteeism, hours), work arrangements (fully remote, hybrid, remote-only days), worker/occupation types, and time horizon.
- **[P4] Assumptions and limitations:** No external database or full-text corpus is supplied for this certificate. When sample size, effect size, source quality, or condition cannot be verified from available knowledge, it is recorded as `UNABLE TO TRACE` and listed under Verification Gaps.

---

## EVIDENCE TRACES

### [E1] Evidence stream: Productivity improvements associated with remote work

| Element | Trace |
|---|---|
| **1. Source(s) and design** | **Bloom, Liang, Roberts, & Ying (2015)**, randomized field experiment at Ctrip, a Chinese call-center company; call-center employees working from home four days/week for nine months. **Choudhury, Foroughi, & Larson (2021)**, natural experiment/difference-in-differences at the U.S. Patent and Trademark Office work-from-anywhere program; patent examiners. |
| **2. Productivity metric and measured effect** | Bloom et al. (2015): call-center performance increased by **13.5%**; about **9%** from more minutes per shift and **4%** from more calls per minute. Choudhury et al. (2021): patent-examiner output increased by **4.4%**. |
| **3. Mechanism** | Bloom et al.: fewer interruptions, quieter home environment, fewer breaks/sick time, greater effective work time. Choudhury et al.: geographic flexibility, reduced commuting/relocation constraints, increased focus for individual measurable work. |
| **4. Boundary conditions** | Bloom et al.: repetitive, individual, low-interdependence call-center task; experienced workers; remote four days/week, not necessarily fully remote. Choudhury et al.: individual expert task with measurable output; experienced patent examiners; work-from-anywhere arrangement. |
| **5. Counterevidence within this stream** | The positive effects are context-specific. **Bloom, Han, & Liang (2024)** hybrid RCT found no performance gain, only retention improvement. **Gibbs, Mengel, & Siemroth (2021)** found negative productivity association for interdependent IT work. Thus E1 does not support a general “remote work raises productivity” claim. |

---

### [E2] Evidence stream: Productivity reductions or harms associated with remote work

| Element | Trace |
|---|---|
| **1. Source(s) and design** | **Gibbs, Mengel, & Siemroth (2021/2023)**, observational study using personnel and analytics data from approximately 10,000 IT professionals at a large Asian IT services company during COVID-19 remote work. **Yang et al. (2022)**, observational analytics study of collaboration networks among approximately 61,000 U.S. Microsoft information workers during firm-wide remote work. |
| **2. Productivity metric and measured effect** | Gibbs et al.: work-from-home was associated with **8% lower productivity**; the negative association was larger for employees with children, approximately **12% lower productivity**. Yang et al.: remote work made collaboration networks more **siloed/static**, reduced cross-team weak ties, decreased synchronous communication, and increased asynchronous communication. Yang et al. did not directly measure individual output. |
| **3. Mechanism** | Gibbs et al.: home distractions, communication overhead, reduced collaboration, and coordination costs in interdependent IT work. Yang et al.: collaboration friction, weaker cross-boundary ties, and shift from synchronous to asynchronous communication. |
| **4. Boundary conditions** | Gibbs et al.: interdependent IT/code work, full remote work during COVID-19, workers with children. Yang et al.: large technology firm, information workers, team-interdependent collaboration networks. |
| **5. Counterevidence within this stream** | Harms are not universal. **Bloom et al. (2015)** found positive call-center output effects, and **Choudhury et al. (2021)** found positive patent-examiner output effects. **Bloom et al. (2024)** found hybrid work did not damage performance. Thus E2 supports conditional harms, especially for interdependent/collaborative work under full remote conditions. |

---

### [E3] Evidence stream: Moderators, mechanisms, and conditional synthesis

| Element | Trace |
|---|---|
| **1. Moderator(s)** | Work arrangement: hybrid vs fully remote/work-from-anywhere. Task type: repetitive individual vs expert individual vs interdependent/collaborative. Worker experience/tenure and children/home conditions. Time horizon: short-term RCT windows vs long-term effects. Managerial support and home-office quality are theoretically relevant but not directly verified in the cited studies. |
| **2. Comparative evidence** | **Hybrid:** Bloom, Han, & Liang (2024), randomized controlled trial at Trip.com with approximately 1,600 employees over six months, found hybrid work two days/week at home had **no impact on performance grades or promotions** and reduced quit rates by **35%**. **Mostly remote call center:** Bloom et al. (2015) found **+13.5%** output. **Work-from-anywhere expert task:** Choudhury et al. (2021) found **+4.4%** output. **Full remote interdependent IT work:** Gibbs et al. (2021) found **−8%** productivity, with **−12%** for employees with children. **Information-worker collaboration:** Yang et al. (2022) found increased siloing and asynchronous communication. |
| **3. Causal versus correlational status** | Causal: Bloom et al. (2015) RCT; Bloom et al. (2024) RCT. Quasi-causal/natural experiment: Choudhury et al. (2021). Observational: Gibbs et al. (2021); Yang et al. (2022). Meta-analytic evidence is incomplete in this certificate: **Gajendran & Harrison (2007)** meta-analysis of 46 telecommuting studies, n≈12,883, reported small positive psychological outcomes and mixed co-worker effects, but exact pooled productivity effect size is `UNABLE TO TRACE`; therefore it is marked **INCOMPLETE CITATION** and excluded from the Formal Conclusion. |
| **4. Net direction under stated conditions** | Evidence converges on a conditional pattern: remote work is more likely to improve productivity for individual, measurable, low-interdependence tasks under structured remote/hybrid arrangements; it is more likely to reduce productivity or collaboration quality for interdependent, information-intensive, team-based work under full remote conditions. Hybrid arrangements appear to preserve performance while improving retention. Exact experience and home-environment moderation remains `CONTESTED`/`UNABLE TO TRACE`. |
| **5. Verification gaps** | `UNABLE TO TRACE: exact pooled productivity effect size from Gajendran & Harrison (2007) meta-analysis`; `UNABLE TO TRACE: exact sample sizes and attrition for Bloom et al. (2015) and Bloom et al. (2024) from available internal knowledge`; `UNABLE TO TRACE: exact quality/innovation coefficients for Choudhury et al. (2021)`; `UNABLE TO TRACE: exact heterogeneity coefficients by tenure/experience/children/home-office quality in Choudhury et al. (2021) and Gibbs et al. (2021)`; `UNABLE TO TRACE: direct productivity effect size in Yang et al. (2022), which measures collaboration/communication rather than output`; `UNABLE TO TRACE: long-term >1-year productivity effects`; `UNABLE TO TRACE: causal estimates comparing fully remote vs hybrid within identical occupations/tasks`; `UNABLE TO TRACE: managerial support and home-office quality moderators in the cited studies`. |

---

## FORMAL CONCLUSION

- **Overall synthesis:** Remote work is not uniformly productivity-enhancing or productivity-reducing. The evidence supports a conditional conclusion: effects depend on task interdependence, occupation, work arrangement, and worker/home context. Positive output effects appear in individual, measurable, low-interdependence tasks under structured remote/hybrid arrangements [E1]; negative productivity and collaboration effects appear in interdependent IT and information-work settings under firm-wide remote work [E2]; hybrid arrangements can preserve performance while improving retention [E3].
- **Conditions where remote work is associated with higher productivity:** Individual, repetitive, measurable tasks with low interdependence, such as call-center work, showed +13.5% output in a field experiment [E1]. Individual expert tasks with measurable output and geographic flexibility, such as patent examination, showed +4.4% output in a natural experiment [E1]. Hybrid arrangements showed no performance damage and improved retention [E3].
- **Conditions where remote work is associated with lower productivity:** Interdependent IT/code work under full remote work was associated with approximately 8% lower productivity, and approximately 12% lower for employees with children [E2]. Information-worker collaboration networks became more siloed and asynchronous under firm-wide remote work [E2]. These harms are conditional, not universal, because positive counterexamples exist in call-center and patent-examiner work [E1].
- **Evidence quality and contested claims:** Causal evidence is strongest for the call-center RCT [E1] and the hybrid-work RCT [E3]; quasi-causal evidence exists for the USPTO work-from-anywhere natural experiment [E1]; observational evidence supports negative associations in IT productivity and collaboration networks [E2]. Contested or unresolved moderators include experience/tenure, home-office quality, managerial support, and long-term innovation effects [E3]. The claim that remote work broadly raises or lowers productivity is **CONTESTED** and not supported as a general conclusion [E1–E3].
- **Verification gaps:** All `UNABLE TO TRACE` items listed in [E3] remain unresolved, including exact pooled meta-analytic effects, exact sample sizes/attrition, exact quality/innovation coefficients, tenure/home-environment moderation, long-term effects, and direct causal comparisons of fully remote vs hybrid in identical task sets.

---

## REMEDIATION / NEXT ACTION

**Concrete research protocol to close Verification Gaps:**

- **Databases:** Web of Science Core Collection; Scopus; PsycINFO; EconLit; Business Source Complete; SSRN; NBER Working Papers; Google Scholar for citation chasing.
- **Search terms:**  
  `("remote work" OR telework OR telecommuting OR "work from home" OR WFH OR "hybrid work" OR "work-from-anywhere") AND (productivity OR performance OR output OR efficiency OR innovation OR collaboration OR absenteeism OR "hours worked") AND (randomized OR "natural experiment" OR "field experiment" OR "difference-in-differences" OR meta-analysis OR longitudinal OR panel)`
- **Inclusion criteria:** Empirical peer-reviewed studies, meta-analyses, field experiments, natural experiments, or large-scale organizational evidence; 2000–2025; measures a productivity-related outcome; reports work arrangement, occupation/task type, and time horizon; English language. Include lab experiments only for task-type moderation and label them as lower external validity.
- **Exclusion criteria:** Opinion pieces, purely descriptive reports, simulation-only studies, non-empirical commentaries, and studies without identifiable productivity/collaboration outcome.
- **Extraction fields:** Source; design; sample/context; arrangement; occupation/task; productivity metric; effect direction and magnitude; moderators; verification status.
- **Gap-closing tasks:** Re-verify exact effect sizes and sample sizes; retrieve current meta-analyses; locate studies measuring managerial support and home-office quality; identify long-term panel or longitudinal evidence; locate direct hybrid-vs-fully-remote comparisons within the same occupation.

**Structured evidence table template:**

| Source | Design | Sample/context | Arrangement | Occupation/task | Productivity metric | Effect direction/magnitude | Moderators | Verification status |
|---|---|---|---|---|---|---|---|---|
| Author/year | RCT / natural experiment / observational / meta-analysis | Population, setting, n if verified | Hybrid / fully remote / remote days | Task type | Output, quality, efficiency, collaboration, retention, etc. | Direction and magnitude | Task interdependence, tenure, children, manager support, home office, time horizon | Verified / `UNABLE TO TRACE` / `INCOMPLETE CITATION` |

---

## VERIFICATION & TRACEABILITY SELF-CHECK

- Overall synthesis cites [E1], [E2], and [E3].
- Higher-productivity conditions cite [E1] and [E3].
- Lower-productivity conditions cite [E2].
- Evidence-quality statement cites [E1], [E2], and [E3].
- Verification gaps are explicitly listed from [E3].
- **No orphaned conclusions:** every Formal Conclusion claim carries at least one [E] identifier. The one incomplete meta-analytic trace is marked **INCOMPLETE CITATION** and excluded from the Formal Conclusion.

### EVALUATION: TEST 5

- **Word Count**: Baseline `505` words | Optimized `1732` words | Ratio `3.43x`
- **Eval Tokens**: Baseline `3747` | Optimized `14861`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4.5      | 5.0       | +0.5  |
| Completeness  | 4.0      | 5.0       | +1.0  |
| Structure     | 5.0      | 4.5       | -0.5  |
| Actionability | 5.0      | 4.5       | -0.5  |
| Traceability  | 3.5      | 5.0       | +1.5  |
| TOTAL         | 22.0/25  | 24.0/25   | +2.0  |

The optimized response substantially improved traceability and completeness by naming studies, designs, effect sizes, boundary conditions, counterevidence, and verification gaps, and by tying conclusions to [E1]-[E3]. Its accuracy was slightly stronger because it handled missing information with explicit `UNABLE TO TRACE` labels, though the certificate format made it longer and less directly actionable than the baseline’s concise practical reading. The baseline remained clearer and more user-friendly for the original overview request, so Structure and Actionability were slightly better in the baseline, while Traceability and Completeness clearly favored the optimized version.

---

## TEST 6: Business Decision (Mixed | Mode 1 (Max Certificate, Template 6 [O1]-[O3]))

### BASELINE RESPONSE

**Short answer: don’t build your own authentication system at 15 people. Buy a mature identity provider that will sign a HIPAA BAA and let you keep PHI out of the auth layer. Auth0/Okta CIC is the more likely fit than Clerk for HIPAA, but only if they will execute a BAA and meet your audit/control requirements. Clerk should be eliminated unless they confirm HIPAA support in writing—BAA, subprocessors, audit logs, retention, admin controls—and your counsel signs off.**

### Why not build
Auth is security-critical infrastructure: MFA/WebAuthn, session revocation, password reset/recovery, OIDC/SAML, SSO/SCIM, rate limiting, bot defense, audit logs, admin tooling, patching, incident response, and compliance evidence. A 15-person SaaS team almost always underestimates this. Build only if auth is your core differentiator and you have a senior security engineer—not because it seems cheaper.

### What “HIPAA-compatible auth” actually means
- HIPAA doesn’t “certify” vendors. You need a **signed BAA** with any vendor that creates/receives/maintains/transmits PHI on your behalf, plus a risk analysis and safeguards.
- Auth identifiers can become PHI when linked to health data. Keep the identity provider’s data minimal: email/phone/MFA factors, opaque user IDs, no clinical data, no PHI in JWT claims, no PHI in SMS/email.
- Your app must enforce authorization and audit access to PHI. Auth logs alone are not enough.
- You also need BAAs with hosting, logging, email/SMS, support, and any subprocessor that can touch PHI.

### Vendor recommendation
1. **Run a short RFP between Auth0/Okta CIC and Clerk.** Require written answers:
   - Will you sign a BAA covering the auth service, logs, support, and all subprocessors?
   - Can we configure US data residency and disable storage of unnecessary profile fields?
   - Audit log export/retention, admin MFA, RBAC, SSO/SCIM, session revocation, brute-force protection?
   - Incident notification, encryption/key management, SOC 2/ISO/pen tests, support-access controls?
   - Can we keep PHI out of the IdP and use opaque subject IDs?
2. **Choose Auth0 if** it signs the BAA on a plan you can afford and meets the controls. It is generally more enterprise/HIPAA-oriented than startup-DX-first providers.
3. **Use Clerk only if** they provide a BAA and demonstrably support your HIPAA controls. If they can’t, don’t use them for this product.
4. **If neither works**, evaluate AWS Cognito under your AWS BAA if eligible for your configuration, or self-host Keycloak/Ory in a BAA-covered cloud. Self-hosting shifts the operational burden back to you, so only do it with security ownership.

### Implementation guardrails
- Use OIDC/SAML; app validates short-lived tokens; don’t put PHI in claims.
- MFA for all workforce users; phishing-resistant MFA for admins; break-glass admin with hardware keys.
- Automatic logoff/session timeouts; re-auth for sensitive actions.
- App-side audit logging of PHI access; redact tokens and PHI from logs.
- Tenant isolation and RBAC tested; no PHI in auth emails/SMS.
- BAAs before production with any ePHI.

**Bottom line:** Buy, don’t build. Prefer Auth0/Okta CIC if the BAA and controls check out. Treat Clerk as guilty-until-proven-HIPAA-eligible. If no vendor will sign a BAA, use a BAA-covered self-hosted option—but budget for the security work. This is not legal advice; have counsel review BAAs and your HIPAA risk analysis.

### OPTIMIZED PROMPT

```
You are a decision analyst. The standard decision analysis protocol requires completing this reasoning certificate before recommending any course of action.

### PREMISES

- [P1] Decision statement: Select one authentication approach for a software product that stores and processes protected health information (PHI) subject to HIPAA.
- [P2] Candidate options under comparison:
  - [O1] Build and operate an in-house authentication system.
  - [O2] Integrate Auth0.
  - [O3] Integrate Clerk.
- [P3] Comparison dimensions (evaluate every option against this identical ordered list):
  1. HIPAA compliance surface (Business Associate Agreement availability, PHI-adjacent data handling, audit logging, encryption at rest and in transit, access controls).
  2. Engineering implementation burden (initial integration effort, required in-house security expertise, maintenance and on-call load).
  3. Total cost of ownership (direct licensing plus engineering hours, at current and 5x current user volume).
  4. Time to first production deployment.
  5. Exit cost and lock-in (data portability, migration path, credential export, password hash compatibility).
  6. Feature coverage against product requirements (MFA, SSO/SAML, passkeys, session management, organization/tenant modeling, rate limiting, bot defense).
  7. Failure modes and blast radius (vendor outage, breach liability allocation, key compromise recovery).
- [P4] Hard constraints and operating facts:
  - Regulated data class: PHI under HIPAA; any vendor touching PHI-adjacent identifiers requires a signed BAA.
  - Team size available for this work: 15 people total; record the assumed number of engineers dedicated to this effort as an explicit assumption if it is not supplied.
  - Any option that cannot be covered by a BAA is disqualified as a primary selection.
- [P5] Evidence provenance rule: For each factual claim, attribute its source as one of `[P4]`, `VENDOR-DOC` (public vendor documentation or pricing pages), or `DOMAIN-KNOWLEDGE` (general engineering practice). When a claim about a specific vendor's current pricing, BAA terms, or feature availability cannot be grounded in [P4] or reliable vendor documentation, record `UNVERIFIED: [exact fact] — requires vendor documentation confirmation` and carry it to Verification Gaps. Treat vendor pricing and BAA terms as time-sensitive.

### COMPARISON TRACES

Produce one trace per dimension in [P3]. Each trace must evaluate all three options on the same evidence basis.

- [T1] Dimension 1 — HIPAA compliance surface:
  1. [O1] evidence: [what compliance obligations the build option creates, including which controls the team must implement and evidence itself]
  2. [O2] evidence: [BAA availability, PHI handling posture, audit log coverage — with provenance tag]
  3. [O3] evidence: [BAA availability, PHI handling posture, audit log coverage — with provenance tag]
  4. Disqualification check: [state explicitly whether each option clears the [P4] BAA gate: CLEARS / FAILS / UNVERIFIED]
  5. Differential: [which option leads on this axis and on what specific mechanism]

- [T2] Dimension 2 — Engineering implementation burden:
  1. [O1] evidence: [components the team must build: credential storage and hashing, session issuance, MFA enrollment, recovery flows, rate limiting, key rotation]
  2. [O2] evidence: [integration surface, SDK footprint, configuration required]
  3. [O3] evidence: [integration surface, SDK footprint, configuration required]
  4. Crossover condition: [the team-capacity threshold at which the ranking on this dimension reverses]

- [T3] Dimension 3 — Total cost of ownership:
  1. [O1] evidence: [engineering hours at a stated rate plus ongoing maintenance, expressed as an explicit formula]
  2. [O2] evidence: [pricing tier structure and the user-volume points where tiers change — provenance tagged]
  3. [O3] evidence: [pricing tier structure and the user-volume points where tiers change — provenance tagged]
  4. Period trajectory: [how each cost curve behaves from current volume to 5x volume]
  5. Differential: [cost ranking at current volume and at 5x volume, stated separately]

- [T4] Dimension 4 — Time to first production deployment:
  1. [O1] evidence: [critical-path items required before any production login is served]
  2. [O2] evidence: [critical-path items]
  3. [O3] evidence: [critical-path items]
  4. Differential: [ordering with the specific blocking dependency named]

- [T5] Dimension 5 — Exit cost and lock-in:
  1. [O1] evidence: [portability characteristics of a self-owned credential store]
  2. [O2] evidence: [credential export capability and hash compatibility — provenance tagged]
  3. [O3] evidence: [credential export capability and hash compatibility — provenance tagged]
  4. Differential: [migration effort ranking and the concrete artifact each migration requires]

- [T6] Dimension 6 — Feature coverage:
  1. [O1] evidence: [which of the [P3] features must be built, and build cost for each]
  2. [O2] evidence: [feature coverage against the [P3] list — provenance tagged]
  3. [O3] evidence: [feature coverage against the [P3] list — provenance tagged]
  4. Gap list: [any [P3] feature that no option covers without additional engineering]

- [T7] Dimension 7 — Failure modes and blast radius:
  1. [O1] evidence: [primary failure modes owned internally, detection mechanism, recovery path]
  2. [O2] evidence: [vendor outage behavior, breach liability allocation, recovery path]
  3. [O3] evidence: [vendor outage behavior, breach liability allocation, recovery path]
  4. Differential: [which option concentrates versus distributes operational risk]

### FORMAL CONCLUSION

- Primary selection: [one option, citing the specific T-identifiers and the [P3] dimensions that drive the result]
- Disqualification record: [any option removed by the [P4] BAA gate, citing the trace that established it]
- Conditional alternative: [runner-up option and the exact observable condition under which it becomes the better selection]
- Accepted tradeoffs: [what the primary selection sacrifices, each citing a T-identifier]
- Verification gaps: [every item marked UNVERIFIED, plus the exact document, pricing page, or BAA clause needed to close it]

### REMEDIATION / NEXT ACTION

The task is incomplete until this section provides one of the following:
- A concrete execution checklist for the primary selection: ordered steps, the specific integration or build artifacts required, and the compliance evidence each step must produce.
- A short list of verification actions that closes every Verification Gap (named vendor document, BAA request, or benchmark spike), each with the exact question it must answer.

### TRACEABILITY SELF-CHECK

Before finalizing, verify that every claim in the Formal Conclusion cites at least one [T] or [P] identifier, and that every dimension in [P3] has a corresponding trace. When a conclusion claim has no supporting identifier, either add the missing trace from [P1]-[P5] or remove the claim so that zero orphaned conclusions remain. When a dimension's evidence supports no clear leader, state `INCONCLUSIVE ON [dimension]` rather than defaulting to a preference.
```

### OPTIMIZED RESPONSE

## Decision Analysis Certificate

### Assumptions and Evidence Basis
- [P4] PHI under HIPAA requires a signed BAA for any vendor touching PHI-adjacent identifiers; an option not coverable by BAA is disqualified as primary.
- Assumption A1: Of the 15-person team, **4 engineers are dedicated to this authentication effort**. This is an explicit assumption because [P4] does not supply the dedicated count.
- Assumption A2: Blended fully loaded engineering rate is **$150/hour**.
- Assumption A3: Current user volume is **U** and 5x volume is **5U**. Numeric current/5x volume is not supplied; TCO is therefore formulaic, and exact ranking is marked inconclusive where pricing is unverified.
- Evidence tags used: `[P4]`, `VENDOR-DOC`, `DOMAIN-KNOWLEDGE`, `UNVERIFIED`.

---

## Comparison Traces

### [T1] Dimension 1 — HIPAA compliance surface

1. **[O1] Build in-house evidence:** The team must implement and evidence HIPAA Security Rule controls for authentication: risk analysis, access control, audit logging, encryption at rest/in transit, key management, incident response, workforce access review, and monitoring. Any cloud database, storage, KMS, or logging subprocessor that touches PHI-adjacent identifiers requires its own BAA. Provenance: [P4] and DOMAIN-KNOWLEDGE.  
2. **[O2] Auth0 evidence:** Auth0 is a third-party identity processor. If it receives PHI-adjacent identifiers, a BAA is required [P4]. BAA availability, plan eligibility, subprocessor coverage, PHI handling, breach liability allocation, and audit-log/encryption/access-control specifics are **UNVERIFIED: Auth0 current BAA terms and plan-specific HIPAA control coverage — requires Auth0 BAA/MSA and documentation confirmation.** A safer architecture sends only opaque identifiers and no clinical PHI, but PHI-adjacent identifiers still trigger BAA review [P4].  
3. **[O3] Clerk evidence:** Clerk is also a third-party identity processor. A BAA is required if it receives PHI-adjacent identifiers [P4]. BAA availability, plan eligibility, subprocessor coverage, PHI handling, audit-log/encryption/access-control coverage, and liability allocation are **UNVERIFIED: Clerk current BAA terms and plan-specific HIPAA control coverage — requires Clerk BAA/MSA and documentation confirmation.**  
4. **Disqualification check:**  
   - O1: **CLEARS** the third-party auth BAA gate, contingent on BAAs with any infrastructure/logging subprocessors that touch PHI-adjacent data [P4].  
   - O2: **UNVERIFIED** — not eligible as primary until a signed BAA and control evidence are confirmed [P4].  
   - O3: **UNVERIFIED** — not eligible as primary until a signed BAA and control evidence are confirmed [P4].  
5. **Differential:** Under verified evidence, **O1 leads** because it avoids the third-party BAA gate and gives the team direct control of audit evidence and access policy. O2 or O3 would lead only after a signed BAA, documented audit-log coverage, and plan-specific control evidence are confirmed.

---

### [T2] Dimension 2 — Engineering implementation burden

1. **[O1] evidence:** The team must build credential storage and password hashing, session issuance/rotation, MFA enrollment and recovery, account recovery, rate limiting, key rotation, audit logging, tenant/organization modeling, and on-call monitoring. Provenance: DOMAIN-KNOWLEDGE. This is a high initial burden.  
2. **[O2] evidence:** Integration surface includes SDK or OIDC/SAML integration, tenant configuration, callback handling, MFA/SSO configuration, log export, and BAA/security review. SDK details and plan-specific feature configuration are **UNVERIFIED: Auth0 SDK and plan-specific integration surface — requires Auth0 documentation confirmation.** Burden is moderate compared with O1, but still requires security review and BAA execution. Provenance: DOMAIN-KNOWLEDGE and UNVERIFIED.  
3. **[O3] evidence:** Integration surface is similar: SDK/OIDC integration, callback handling, MFA/passkey configuration, session configuration, organization modeling, and log/export review. Exact SDK footprint and enterprise-feature configuration are **UNVERIFIED: Clerk SDK and plan-specific integration surface — requires Clerk documentation confirmation.** Provenance: DOMAIN-KNOWLEDGE and UNVERIFIED.  
4. **Crossover condition:** If dedicated engineering capacity is **≤3 FTE** or launch deadline is **≤8 weeks**, O2/O3 have materially lower implementation burden. If the team can dedicate **≥5 FTE for ≥6–9 months** and requirements require substantial custom tenancy/security controls, O1 can become competitive after the initial build. Provenance: DOMAIN-KNOWLEDGE.

---

### [T3] Dimension 3 — Total cost of ownership

Let `R = $150/hour`, `T` = years, `U` = current volume, and `H_*` = estimated engineering hours.

1. **[O1] formula:**  
   `TCO_O1(T,U) = R × (H_build + H_maint_annual × T) + C_infra(U,T) + C_compliance(T) + C_oncall(T) + C_security_tooling(T)`  
   With assumption A1, illustrative build effort is about `4 FTE × 6–9 months ≈ 4,000–6,000 hours`, i.e. roughly `$600k–$900k` initial engineering at `$150/hour`, plus ongoing maintenance/on-call. Provenance: DOMAIN-KNOWLEDGE.  
2. **[O2] formula:**  
   `TCO_O2(T,U) = R × H_integration + V_Auth0(U,T) + R × H_ops × T + C_addons(T)`  
   Auth0 publishes tiered identity pricing in general, but exact current MAU boundaries, BAA inclusion, enterprise plan thresholds, and 5x-volume pricing are **UNVERIFIED: Auth0 current pricing tiers and BAA/enterprise thresholds — requires Auth0 pricing page and quote confirmation.** Provenance: VENDOR-DOC generally; exact numbers UNVERIFIED.  
3. **[O3] formula:**  
   `TCO_O3(T,U) = R × H_integration + V_Clerk(U,T) + R × H_ops × T + C_addons(T)`  
   Clerk publishes tiered pricing in general, but exact current MAU boundaries, BAA inclusion, enterprise plan thresholds, and 5x-volume pricing are **UNVERIFIED: Clerk current pricing tiers and BAA/enterprise thresholds — requires Clerk pricing page and quote confirmation.** Provenance: VENDOR-DOC generally; exact numbers UNVERIFIED.  
4. **Period trajectory:** O1 has high fixed engineering cost and low marginal per-user cost; at 5x volume its average cost falls if the build is amortized. O2/O3 have lower initial integration cost but licensing is usage-tiered and may step upward at MAU or feature thresholds; at 5x volume they may cross into higher/enterprise plans. Provenance: DOMAIN-KNOWLEDGE and UNVERIFIED vendor pricing.  
5. **Differential:**  
   - At current volume: **provisional O2/O3 lead** if U is low and standard features suffice, because O1 carries high NRE [T2]. Exact O2-vs-O3 ranking is **INCONCLUSIVE ON T3** without verified pricing.  
   - At 5x volume: O1 may become cheaper if vendor pricing enters enterprise tiers and O1 engineering is amortized; otherwise O2/O3 may remain cheaper. Exact ranking is **INCONCLUSIVE ON T3** until U, 5U, and vendor quotes are supplied.

---

### [T4] Dimension 4 — Time to first production deployment

1. **[O1] evidence:** Critical path includes HIPAA risk analysis/control mapping, BAAs for infrastructure/logging, credential/session implementation, MFA/recovery, audit logging, security testing/pen test, monitoring/on-call, backup/DR, and production readiness review. Provenance: DOMAIN-KNOWLEDGE and [P4]. This is slower than integrating a mature vendor.  
2. **[O2] evidence:** Critical path includes signed BAA before PHI-adjacent data flows, tenant configuration, SDK/OIDC integration, MFA/SSO configuration, log export, security review, and cutover. The **signed BAA is a blocking dependency** for compliant production use [P4]. Exact setup time is **UNVERIFIED: Auth0 implementation timeline — requires vendor/implementation confirmation.**  
3. **[O3] evidence:** Critical path is similar: signed BAA, SDK/OIDC integration, MFA/passkey/session configuration, organization modeling review, log export, security review, and cutover. The **signed BAA is a blocking dependency** [P4]. Exact setup time is **UNVERIFIED: Clerk implementation timeline — requires vendor/implementation confirmation.**  
4. **Differential:** Conditional on BAA clearance, **O2/O3 are faster than O1** because they avoid building core auth primitives [T2]. Under current verified evidence, O2/O3 production paths are blocked at the BAA gate, so O1 is the only demonstrably deployable path for PHI-adjacent authentication without an unverified vendor BAA.

---

### [T5] Dimension 5 — Exit cost and lock-in

1. **[O1] evidence:** The team owns the credential database, password hash parameters, MFA secrets, session records, audit logs, and schema. Migration to another system requires exporting these artifacts or forcing credential resets, but no vendor controls the source of truth. Provenance: DOMAIN-KNOWLEDGE.  
2. **[O2] evidence:** Auth0 credential export capability and password-hash compatibility are **UNVERIFIED: Auth0 bulk user export including password hashes, supported hash formats, and migration/import compatibility — requires Auth0 documentation confirmation.** Without hash export, migration likely requires forced password resets or a parallel credential strategy. Provenance: UNVERIFIED and DOMAIN-KNOWLEDGE.  
3. **[O3] evidence:** Clerk credential export capability and password-hash compatibility are **UNVERIFIED: Clerk bulk user export including password hashes, supported hash formats, and migration/import compatibility — requires Clerk documentation confirmation.** Same forced-reset risk applies. Provenance: UNVERIFIED and DOMAIN-KNOWLEDGE.  
4. **Differential:** **O1 leads** on exit cost because it owns the concrete artifacts: database dump, hash algorithm/parameters, MFA secret export or reset process, session/log schema. O2/O3 require a vendor export artifact containing hashes and metadata; if unavailable, migration cost rises to forced reset. O2-vs-O3 ranking is **INCONCLUSIVE ON T5** until export/hash compatibility is verified.

---

### [T6] Dimension 6 — Feature coverage

1. **[O1] evidence:** The team must build all [P3] features: MFA, SSO/SAML, passkeys, session management, organization/tenant modeling, rate limiting, and bot defense. Approximate build cost: MFA medium, SSO/SAML high, passkeys medium, session management medium, org/tenant modeling high, rate limiting low-to-medium, bot defense high. Provenance: DOMAIN-KNOWLEDGE.  
2. **[O2] evidence:** Auth0 feature coverage against the [P3] list is **UNVERIFIED: Auth0 plan-specific coverage for MFA, SSO/SAML, passkeys, session management, organization/tenant modeling, rate limiting, bot defense, audit-log export, and retention — requires Auth0 documentation confirmation.**  
3. **[O3] evidence:** Clerk feature coverage against the [P3] list is **UNVERIFIED: Clerk plan-specific coverage for MFA, SSO/SAML, passkeys, session management, organization/tenant modeling, rate limiting, bot defense, audit-log export, and retention — requires Clerk documentation confirmation.**  
4. **Gap list:** Under verified evidence, O1 has a build gap for every [P3] feature. O2/O3 have a documentation-verification gap for every plan-specific feature. A common additional-engineering gap is bot defense and advanced rate limiting, which often require an edge/WAF/CDN layer even when an auth vendor is used [DOMAIN-KNOWLEDGE]. **INCONCLUSIVE ON T6 for O2 vs O3** until vendor feature matrices are provided.

---

### [T7] Dimension 7 — Failure modes and blast radius

1. **[O1] evidence:** Primary failure modes include credential database compromise, session-signing key compromise, auth code defects, outage of the auth service, and on-call response failure. Detection is via audit logs, SIEM/alerts, anomaly detection, and access reviews. Recovery includes key rotation, global session revocation, backup restore, forced resets, incident response, and breach notification. Risk is concentrated inside the organization, but recovery ownership is direct. Provenance: DOMAIN-KNOWLEDGE.  
2. **[O2] evidence:** Primary failure mode is vendor outage or vendor-side incident blocking logins. Breach liability allocation is **UNVERIFIED: Auth0 BAA/MSA breach liability and recovery obligations — requires executed BAA/MSA confirmation.** Recovery depends on vendor incident response and customer configuration; self-hosted failover is generally not available. Provenance: UNVERIFIED and DOMAIN-KNOWLEDGE.  
3. **[O3] evidence:** Primary failure mode is vendor outage or vendor-side incident blocking logins. Breach liability allocation is **UNVERIFIED: Clerk BAA/MSA breach liability and recovery obligations — requires executed BAA/MSA confirmation.** Recovery depends on vendor incident response and customer configuration. Provenance: UNVERIFIED and DOMAIN-KNOWLEDGE.  
4. **Differential:** O1 **concentrates operational risk internally** but gives direct control and clear recovery ownership. O2/O3 **distribute availability responsibility to the vendor** but create third-party dependency, contractual liability dependency, and vendor outage blast radius. Under current evidence, O1 provides the clearest recovery path because no vendor BAA/liability terms are verified.

---

## Formal Conclusion

- **Primary selection: O1 — Build and operate an in-house authentication system.**  
  Driven by: O1 is the only option that clears the BAA gate on current evidence [T1][P4]; O1 gives the strongest credential portability and exit control [T5]; O1 keeps recovery ownership and incident response directly controllable [T7]. It is selected despite slower deployment [T4], high implementation burden [T2], feature-build cost [T6], and unresolved TCO ranking [T3].

- **Disqualification record:** No option is proven to **FAIL** the BAA gate. O2 and O3 are **UNVERIFIED** on BAA availability/terms [T1] and therefore are not eligible as primary selections under [P4]/[P5] until a signed BAA and control evidence are confirmed. O1 clears the third-party auth BAA gate, contingent on BAAs with any infrastructure/logging subprocessor that touches PHI-adjacent data [T1].

- **Conditional alternative: O2 — Auth0.**  
  Auth0 becomes the better selection if: Auth0 signs a BAA covering all PHI-adjacent identifiers and relevant subprocessors; vendor documentation confirms required audit logging, encryption, access controls, and [P3] feature coverage [T1][T6]; credential export/hash compatibility is acceptable [T5]; and its TCO/time-to-production advantage over O1 is verified [T3][T4]. If Auth0 cannot provide BAA coverage, O3 becomes the only vendor alternative, but only under the same verified BAA/control/export conditions.

- **Accepted tradeoffs:**  
  - Slower initial production deployment than a viable vendor integration [T4].  
  - High in-house engineering and security burden [T2].  
  - Must build MFA, SSO/SAML, passkeys, session management, tenant modeling, rate limiting, and bot defense [T6].  
  - TCO may be higher at low current volume and remains unresolved without U/5U and vendor quotes [T3].  
  - Operational risk is concentrated internally, including on-call and incident response [T7].  
  - The organization must produce and maintain its own HIPAA control evidence [T1].

- **Verification gaps:**  
  1. **Auth0 BAA:** exact availability, plan eligibility, covered PHI-adjacent data, subprocessors, breach liability, and recovery obligations — requires Auth0 BAA/MSA review [T1][T7].  
  2. **Auth0 pricing:** current and 5x-volume tier boundaries, BAA inclusion, enterprise thresholds — requires Auth0 pricing page and quote [T3].  
  3. **Auth0 features:** MFA, SSO/SAML, passkeys, session management, org/tenant modeling, rate limiting, bot defense, audit-log retention/export, encryption, access controls — requires Auth0 documentation [T1][T6].  
  4. **Auth0 export/hash compatibility:** bulk export including password hashes, supported algorithms/formats — requires Auth0 migration/export documentation [T5].  
  5. **Clerk BAA:** exact availability, plan eligibility, covered PHI-adjacent data, subprocessors, breach liability, and recovery obligations — requires Clerk BAA/MSA review [T1][T7].  
  6. **Clerk pricing:** current and 5x-volume tier boundaries, BAA inclusion, enterprise thresholds — requires Clerk pricing page and quote [T3].  
  7. **Clerk features:** same [P3] feature matrix and audit/encryption/access-control coverage — requires Clerk documentation [T1][T6].  
  8. **Clerk export/hash compatibility:** bulk export including password hashes, supported algorithms/formats — requires Clerk migration/export documentation [T5].  
  9. **Current and 5x user volume U and 5U:** not supplied; needed for exact TCO ranking [T3].  
  10. **Engineering estimates:** build/maintenance hours at 4 dedicated engineers and $150/hour need a benchmark spike or work breakdown [T3].

---

## Remediation / Next Action

### Execution checklist for primary selection O1 — Build in-house

1. **Define PHI and auth scope.** Produce data-flow diagram, PHI-adjacent identifier inventory, and updated HIPAA risk analysis. Evidence: approved risk analysis and control mapping.  
2. **Establish subprocessor BAAs.** Sign BAAs with cloud database, storage, KMS, logging, monitoring, and any vendor touching PHI-adjacent data. Evidence: BAA register and subprocessor list.  
3. **Architect credential and session model.** Define Argon2id/bcrypt parameters, session token design, cookie settings, CSRF defenses, and KMS key hierarchy. Evidence: security design review and threat model.  
4. **Implement core authentication.** Build registration, login, password hashing, session issuance/rotation, account recovery, and secure error handling. Evidence: code review, unit/integration tests, and configuration baseline.  
5. **Implement MFA and recovery.** Build TOTP/WebAuthn, recovery codes, admin reset workflows, and MFA audit events. Evidence: test plan/results and audit log samples.  
6. **Implement SSO/tenant/RBAC if required.** Build SAML/OIDC connectors, organization/tenant model, RBAC, and tenant isolation tests. Evidence: integration tests, isolation test report, access review.  
7. **Implement rate limiting and bot defense.** Configure WAF, rate-limit policies, lockout, anomaly alerts, and bot defense rules. Evidence: security test results, WAF configuration, load/abuse test.  
8. **Implement audit logging and monitoring.** Define immutable auth audit schema, retention policy, SIEM forwarding, and alerts. Evidence: log schema, retention config, sample audit report, alert test.  
9. **Implement key rotation, session revocation, and incident response.** Create runbooks for key compromise, session revocation, backup restore, breach notification, and on-call escalation. Evidence: rotation drill, revocation drill, tabletop exercise.  
10. **Validate security and production readiness.** Run SAST/DAST, dependency scanning, penetration test, backup/restore test, DR test, and load test. Evidence: pen test report, remediation tracker, DR/backup results.  
11. **Launch and maintain compliance.** Execute cutover/rollback plan, on-call schedule, access review cadence, vulnerability management, and annual risk analysis refresh. Evidence: launch approval, on-call rota, access reviews, risk-analysis schedule.

### Verification actions to close remaining gaps

| Gap | Action | Exact question it must answer |
|---|---|---|
| Auth0 BAA | Request Auth0 BAA/MSA | Will Auth0 sign a BAA covering all PHI-adjacent identifiers for this use case, which plans include it, which subprocessors are covered, and what are breach liability/recovery terms? [T1][T7] |
| Auth0 pricing | Obtain quote at U and 5U | What are current tier boundaries, BAA/enterprise inclusions, and total cost at current and 5x volume? [T3] |
| Auth0 features | Obtain feature matrix/docs | Which [P3] features are included in the applicable plan, including audit-log retention/export, encryption, and access controls? [T1][T6] |
| Auth0 export | Obtain migration/export docs | Can Auth0 bulk-export password hashes and metadata, and which hash algorithms/formats are compatible? [T5] |
| Clerk BAA | Request Clerk BAA/MSA | Will Clerk sign a BAA covering all PHI-adjacent identifiers, which plans include it, which subprocessors are covered, and what are breach liability/recovery terms? [T1][T7] |
| Clerk pricing | Obtain quote at U and 5U | What are current tier boundaries, BAA/enterprise inclusions, and total cost at current and 5x volume? [T3] |
| Clerk features | Obtain feature matrix/docs | Which [P3] features are included in the applicable plan, including audit-log retention/export, encryption, and access controls? [T1][T6] |
| Clerk export | Obtain migration/export docs | Can Clerk bulk-export password hashes and metadata, and which hash algorithms/formats are compatible? [T5] |
| Volume and TCO | Supply U and 5U plus benchmark spike | What are current and 5x active-user counts, and what are estimated O1 build/maintenance hours at 4 FTE and $150/hour? [T3] |

---

## Traceability Self-Check

| [P3] dimension | Trace | Result |
|---|---|---|
| 1 HIPAA compliance surface | T1 | O1 leads under verified BAA evidence; O2/O3 UNVERIFIED on BAA gate |
| 2 Engineering implementation burden | T2 | O2/O3 lower burden at low capacity/short deadline; O1 competitive only with sufficient dedicated engineering |
| 3 Total cost of ownership | T3 | **INCONCLUSIVE ON T3** exact ranking; provisional O2/O3 at current low volume, O1 possible at 5x if vendor tiers rise |
| 4 Time to first production deployment | T4 | O2/O3 faster if BAA cleared; O1 only currently verified deployable path under BAA gate |
| 5 Exit cost and lock-in | T5 | O1 leads; O2/O3 require verified hash/export artifacts |
| 6 Feature coverage | T6 | **INCONCLUSIVE ON T6** for O2 vs O3; O1 requires building all features |
| 7 Failure modes and blast radius | T7 | O1 concentrates internal risk but gives direct recovery ownership; O2/O3 add vendor dependency and unverified liability terms |

Every Formal Conclusion claim above cites at least one T or P identifier. All [P3] dimensions have corresponding traces. No orphaned conclusion remains; unresolved vendor facts are carried to Verification Gaps.

### EVALUATION: TEST 6

- **Word Count**: Baseline `520` words | Optimized `2984` words | Ratio `5.74x`
- **Eval Tokens**: Baseline `2791` | Optimized `13977`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4.5      | 3.0       | -1.5  |
| Completeness  | 4.5      | 5.0       | +0.5  |
| Structure     | 5.0      | 4.0       | -1.0  |
| Actionability | 5.0      | 4.5       | -0.5  |
| Traceability  | 2.0      | 5.0       | +3.0  |
| TOTAL         | 21.0/25  | 21.5/25   | +0.5  |

The optimized response substantially improved traceability and formal coverage of every requested comparison dimension, with explicit assumptions, verification gaps, and a self-check. However, it became bloated for a 15-person startup decision and, more importantly, selected building in-house as the primary recommendation because vendor BAA facts were “UNVERIFIED,” which is less practical and less accurate than the baseline’s buy-first, prefer-Auth0-with-BAA guidance. The baseline stayed much more concise and actionable, while the optimized certificate traded some real-world decision quality for formal rigor.

---

## TEST 7: Compliance Check (Accuracy | Mode 1 (Max Certificate, Template 7 [R1]-[R2]))

### BASELINE RESPONSE

**Overall: Not NIST SP 800-63B compliant as written.** It reflects older “complexity + rotation” guidance that 800-63B explicitly discourages or prohibits.

| Policy element | NIST 800-63B assessment | Why |
|---|---|---|
| **Minimum 8 characters** | ⚠️ **Partially compliant** | 8 is the NIST minimum for memorized secrets. But the policy should also allow at least **64 characters**, accept spaces and Unicode, and not truncate. If the system maxes out below 64 or blocks spaces/Unicode, it conflicts with 800-63B guidance. |
| **Must include uppercase, lowercase, number, special character** | ❌ **Non-compliant** | 800-63B says verifiers **SHALL NOT impose composition rules** such as requiring mixtures of character types. Replace this with screening against breached/common/context-specific password lists. |
| **Passwords expire every 90 days** | ❌ **Non-compliant** | 800-63B says verifiers **SHALL NOT require arbitrary periodic password changes**. Force a change only when there is evidence of compromise or at the user’s request. |
| **Cannot reuse last 5 passwords** | ❌/⚠️ **Likely non-compliant / too weak** | 800-63B requires maintaining a history of previously used memorized secrets and ensuring new ones are not the same as previous ones. A “last 5” limit is narrower than the literal NIST requirement and is not a NIST safe harbor. |
| **Account locks after 3 failed attempts for 30 minutes** | ⚠️ **Potentially acceptable, but incomplete** | 800-63B requires an effective **rate-limiting** mechanism. A 3-attempt/30-minute lockout can be one implementation, but NIST does not prescribe those exact thresholds. The policy should also address account-enumeration protection, user notification/recovery, and DoS risk from hard lockouts. |

**Key missing NIST 800-63B requirements:**  
- Screen passwords against **breached/common/context-specific** password lists.  
- Do **not** use password hints or knowledge-based authentication.  
- Allow paste/password managers.  
- Use secure salted hashing and protect account existence.  
- Implement effective rate limiting and consider MFA.

**Compliant-style replacement policy:**  
- Minimum **8** characters; allow at least **64** characters, including spaces and Unicode.  
- **No composition rules.**  
- Reject passwords found in breach/common/context lists.  
- **No periodic expiration**; force reset only on compromise.  
- Maintain password history and reject reuse of previous passwords.  
- Rate-limit failed attempts with throttling/backoff or lockout, notify users, provide recovery, and avoid revealing whether an account exists.

**Bottom line:** The 8-character minimum is the only clearly acceptable element. The composition rules and 90-day expiration are clearly non-compliant; the 5-password history and lockout policy need revision or additional controls.

### OPTIMIZED PROMPT

The standard compliance audit protocol for NIST SP 800-63B requires completing this verification certificate before issuing any compliance disposition. Every section is filled from observable text in the artifact under review, not from policy titles or intent statements.

### PREMISES

- [P1] Artifact under review — password policy statement, quoted verbatim as the sole implementation evidence:
  1. "Minimum 8 characters"
  2. "Must include uppercase, lowercase, number, and special character"
  3. "Passwords expire every 90 days"
  4. "Cannot reuse last 5 passwords"
  5. "Account locks after 3 failed attempts for 30 minutes"

- [P2] Applicable normative clause set — [R1] below (NIST SP 800-63B, Digital Identity Guidelines, Authenticator Assurance Level / password verifier requirements, §5.1.1.2 and §5.2.2 rate-limiting provisions).

- [P3] Evidence class and limits: only the written policy text in [P1] is provided. No verifier configuration, source code, password blocklist export, logs, or test results are supplied. Dispositions therefore describe what the written policy mandates; where a requirement concerns enforced runtime behavior rather than documented policy, record `UNABLE TO VERIFY: [missing artifact]` and state the artifact required.

- [P4] Scope boundaries: in scope are the five clauses of [P1] and their alignment with [R1]. Out of scope are authenticator binding, federation, identity proofing, and any control not stated in [R1].

### NORMATIVE REQUIREMENTS [R1] AND DISPOSITION TAXONOMY [R2]

- [R1] Requirement set under which [P1] is assessed:
  - [R1.1] Verifier SHALL require passwords of at least 8 characters in length.
  - [R1.2] Verifier SHALL permit a maximum password length of at least 64 characters, and SHALL accept all printable ASCII characters and space.
  - [R1.3] Verifier SHALL NOT impose composition rules that require mixtures of character types (uppercase, lowercase, digits, special characters).
  - [R1.4] Verifier SHALL NOT require periodic password expiration; a forced change occurs only on evidence of authenticator compromise.
  - [R1.5] Verifier SHALL compare prospective passwords against a blocklist containing commonly used, expected, and compromised passwords, and reject matches or near-matches.
  - [R1.6] Verifier SHALL limit consecutive failed authentication attempts, with no more than 100 consecutive failures permitted per account.
  - [R1.7] Verifier SHOULD offer guidance to users and SHALL NOT impose composition or rotation rules as a substitute for blocklist screening (composite rule linking [R1.3] and [R1.5]).

- [R2] Disposition taxonomy applied to every trace: `COMPLIANT` (policy text mandates a mechanism satisfying the requirement), `NON-COMPLIANT` (policy text mandates a mechanism that contradicts or violates the requirement), `PARTIAL` (policy text addresses part of the requirement while leaving a stated sub-element unaddressed), `UNABLE TO VERIFY` (requirement concerns behavior the written policy neither states nor implies, or needed evidence is absent from [P3]).

### COMPLIANCE TRACES

Produce one trace per requirement in [R1], in order, using this field structure:

- [T1] Clause [R1.x] — [requirement name]:
  1. Normative requirement: exact text of [R1.x].
  2. Artifact examined: verbatim quotation of the [P1] clause (numbered 1–5) that bears on this requirement; if no [P1] clause bears on it, record `ABSENT FROM [P1]`.
  3. Substantive mechanism match: how the quoted [P1] clause's actual mechanism satisfies, contradicts, or fails to address the requirement — reasoned from the clause's operative verbs ("must", "expire", "cannot") rather than its topic label.
  4. Disposition: one label from [R2].
  5. Deficit specification: for `NON-COMPLIANT` or `PARTIAL`, the exact contradictory or missing mechanism; for `UNABLE TO VERIFY`, the specific artifact needed.
  6. Severity: HIGH / MEDIUM / LOW with the reason grounded in the effect of the mechanism on the requirement in [R1.x].

Grounding rule: Assign `COMPLIANT` only when the quoted [P1] clause mandates a mechanism that demonstrably satisfies the full text of [R1.x]. Base every disposition on the clause's operative language, not on the plausibility of what an implementer might do. When a requirement is a prohibition and the policy is silent, record `ABSENT FROM [P1]` and classify by whether silence leaves the prohibited behavior permitted or unaddressed. When the clause exists but the corresponding runtime enforcement is undocumented in [P3], record `UNABLE TO VERIFY: [named artifact]` in field 5 while keeping field 4 anchored to the policy text.

Also produce, after the requirement traces, one trace per [P1] clause:

- [T6]–[T10] Policy clause 1–5 — cross-clause effect: state which [R1] requirement the clause serves or undermines, and whether it duplicates, neutralizes, or is neutral to another clause's mandated mechanism. Cite the paired trace identifiers.

### FORMAL CONCLUSION

- Disposition summary: one sentence per requirement [R1.1]–[R1.7], each citing its [T] identifier and [R2] label.
- Non-compliant items: enumerated list, each with the [R1.x] identifier, the [T] identifier, and the verbatim [P1] text that produces the non-compliance.
- Partial and unverified items: enumerated list separated from non-compliant items, each with the named missing element or missing artifact from [P3].
- Severity ranking: requirements ordered by severity as assigned in the trace field 6, with the ranking reason tied to [T] identifiers.
- Structural finding: state whether the policy's overall design pattern (composition rules, rotation, history, lockout) aligns with or diverges from the [R1] framework, citing the [T6]–[T10] cross-clause traces.
- Verification gaps: every trace marked `UNABLE TO VERIFY` and the exact artifact required to close it.

### REMEDIATION / NEXT ACTION

The task is incomplete until this section contains all of the following:

- A copy-pasteable redline of [P1]: the complete revised five-clause policy text, with each revised clause annotated by the [R1.x] identifier it satisfies. Clauses that [R1] requires to be removed appear as explicit deletions with a one-line justification citing the [T] identifier.
- A copy-pasteable replacement clause for each requirement currently marked `NON-COMPLIANT`, `PARTIAL`, or `ABSENT FROM [P1]`, written in the same policy-statement register as [P1].
- For each `UNABLE TO VERIFY` trace, the specific evidence-collection step that would close it (named configuration export, log query, or test case) expressed as an executable instruction.
- The explicit statement "No remediation required: [reason grounded in [T] identifiers]" only if every requirement is `COMPLIANT`.

TRACEABILITY SELF-CHECK (mandatory before finalizing): Verify that every claim in the Formal Conclusion and every redline in Remediation cites at least one [T] or [R1.x] identifier. When a claim lacks a supporting identifier, either add the missing trace from [P1]/[P2] or remove the claim so zero orphaned conclusions remain. Derive the disposition set strictly from [T] traces without reference to downstream review timelines, audit deadlines, certification outcomes, or any stated business consequence.

### OPTIMIZED RESPONSE

Identifier note: Requirement traces use [T1]–[T7] for [R1.1]–[R1.7]. Policy-clause cross-effect traces use [T8]–[T12] for [P1] clauses 1–5 to avoid duplicate identifiers; these are the cross-clause traces requested as [T6]–[T10], renumbered for unambiguous citation.

## COMPLIANCE TRACES

### Requirement traces [R1.1]–[R1.7]

- [T1] Clause [R1.1] — Minimum password length:
  1. Normative requirement: “Verifier SHALL require passwords of at least 8 characters in length.”
  2. Artifact examined: [P1] clause 1: “Minimum 8 characters”.
  3. Substantive mechanism match: The operative term “Minimum” mandates a password floor of 8 characters, which satisfies the “at least 8 characters” requirement. It does not address maximum length or accepted character set; those are assessed under [R1.2]/[T2].
  4. Disposition: `COMPLIANT`.
  5. Deficit specification: No written-policy deficit for [R1.1]/[T1]. Runtime enforcement evidence is absent from [P3]: `UNABLE TO VERIFY: verifier minimum-length configuration/export`; field 4 remains anchored to [P1] under [P3].
  6. Severity: LOW — the written policy mechanism meets [R1.1]/[T1]; the only gap is proof of runtime enforcement.

- [T2] Clause [R1.2] — Maximum length and printable-character acceptance:
  1. Normative requirement: “Verifier SHALL permit a maximum password length of at least 64 characters, and SHALL accept all printable ASCII characters and space.”
  2. Artifact examined: `ABSENT FROM [P1]` for maximum length and printable-ASCII/space acceptance. Adjacent text: [P1] clause 1 “Minimum 8 characters”; [P1] clause 2 “Must include uppercase, lowercase, number, and special character”.
  3. Substantive mechanism match: Clause 1 states only a minimum length and does not state that passwords up to at least 64 characters are permitted. Clause 2 imposes character-class inclusion but does not state that all printable ASCII characters and space are accepted. The required maximum-length and character-acceptance mechanisms are not mandated by [P1].
  4. Disposition: `UNABLE TO VERIFY`.
  5. Deficit specification: `UNABLE TO VERIFY: verifier password-length and character-acceptance configuration/export plus acceptance-test results`; required because [P3] provides no verifier configuration or test results.
  6. Severity: MEDIUM — missing evidence for long passphrases and printable-character/space acceptance can materially restrict password strength, but no written contradiction to [R1.2]/[T2] is proven.

- [T3] Clause [R1.3] — No composition rules:
  1. Normative requirement: “Verifier SHALL NOT impose composition rules that require mixtures of character types (uppercase, lowercase, digits, special characters).”
  2. Artifact examined: [P1] clause 2: “Must include uppercase, lowercase, number, and special character”.
  3. Substantive mechanism match: The operative term “Must include” mandates a mixture of four character classes. That is a prohibited composition rule requiring mixtures of character types.
  4. Disposition: `NON-COMPLIANT`.
  5. Deficit specification: Exact contradictory mechanism: mandatory inclusion of uppercase, lowercase, number, and special character. The policy must remove that composition requirement.
  6. Severity: HIGH — [P1] directly mandates a mechanism that [R1.3]/[T3] expressly prohibits.

- [T4] Clause [R1.4] — No periodic expiration:
  1. Normative requirement: “Verifier SHALL NOT require periodic password expiration; a forced change occurs only on evidence of authenticator compromise.”
  2. Artifact examined: [P1] clause 3: “Passwords expire every 90 days”.
  3. Substantive mechanism match: The operative term “expire every 90 days” mandates periodic password rotation independent of compromise. That contradicts the prohibition on periodic expiration.
  4. Disposition: `NON-COMPLIANT`.
  5. Deficit specification: Exact contradictory mechanism: mandatory 90-day password expiration. The policy must remove periodic expiration and permit forced change only on evidence of authenticator compromise.
  6. Severity: HIGH — [P1] directly mandates a mechanism that [R1.4]/[T4] expressly prohibits.

- [T5] Clause [R1.5] — Blocklist screening:
  1. Normative requirement: “Verifier SHALL compare prospective passwords against a blocklist containing commonly used, expected, and compromised passwords, and reject matches or near-matches.”
  2. Artifact examined: `ABSENT FROM [P1]` for blocklist screening. Adjacent text: [P1] clause 4 “Cannot reuse last 5 passwords”.
  3. Substantive mechanism match: Clause 4 imposes password history against the last 5 passwords, not a blocklist of commonly used, expected, and compromised passwords. [P1] does not mandate blocklist comparison or near-match rejection.
  4. Disposition: `UNABLE TO VERIFY`.
  5. Deficit specification: `UNABLE TO VERIFY: password blocklist export/version and verifier blocklist configuration/integration artifact or test results showing match/near-match rejection`.
  6. Severity: HIGH — blocklist screening is a central required control under [R1.5]/[T5], and [P1] provides no policy mandate or evidence for it.

- [T6] Clause [R1.6] — Failed-attempt limiting:
  1. Normative requirement: “Verifier SHALL limit consecutive failed authentication attempts, with no more than 100 consecutive failures permitted per account.”
  2. Artifact examined: [P1] clause 5: “Account locks after 3 failed attempts for 30 minutes”.
  3. Substantive mechanism match: The operative term “locks after 3 failed attempts” mandates a failed-attempt limiter stricter than the 100-failure ceiling. The 30-minute lockout period is not prohibited by [R1.6]/[T6].
  4. Disposition: `COMPLIANT`.
  5. Deficit specification: No written-policy deficit for [R1.6]/[T6]. Runtime enforcement evidence is absent from [P3]: `UNABLE TO VERIFY: authentication lockout configuration/export and failed-attempt log query`; field 4 remains anchored to [P1] under [P3].
  6. Severity: LOW — the written policy mandates a lockout threshold below the maximum permitted by [R1.6]/[T6]; the remaining issue is runtime verification only.

- [T7] Clause [R1.7] — Guidance and no composition/rotation substitute:
  1. Normative requirement: “Verifier SHOULD offer guidance to users and SHALL NOT impose composition or rotation rules as a substitute for blocklist screening (composite rule linking [R1.3] and [R1.5]).”
  2. Artifact examined: [P1] clause 2: “Must include uppercase, lowercase, number, and special character”; [P1] clause 3: “Passwords expire every 90 days”; no [P1] clause offers user guidance or blocklist screening.
  3. Substantive mechanism match: The policy imposes both composition rules and periodic rotation while containing no blocklist screening mandate. It also contains no user-guidance statement. Because the policy mandates composition and rotation without the required blocklist screening, it violates the SHALL NOT portion of [R1.7].
  4. Disposition: `NON-COMPLIANT`.
  5. Deficit specification: Exact deficiencies: mandatory composition rule from clause 2; mandatory 90-day expiration from clause 3; absent blocklist screening; absent user guidance. The policy must not use composition or rotation as a substitute for blocklist screening and should provide user guidance.
  6. Severity: HIGH — [P1] combines prohibited composition/rotation mechanisms with no blocklist screening mandate, matching the composite control failure prohibited by [R1.7]/[T7].

### Policy-clause cross-effect traces [T8]–[T12]

- [T8] Policy clause 1 — “Minimum 8 characters”:
  - Serves [R1.1]/[T1] by mandating the minimum length floor.
  - Does not satisfy [R1.2]/[T2] because it does not state maximum length of at least 64 characters or acceptance of all printable ASCII characters and space.
  - Neutral to [R1.3]/[T3], [R1.4]/[T4], [R1.5]/[T5], [R1.6]/[T6], and [R1.7]/[T7] as written.

- [T9] Policy clause 2 — “Must include uppercase, lowercase, number, and special character”:
  - Undermines [R1.3]/[T3] by mandating a prohibited composition rule.
  - Contributes to [R1.7]/[T7] non-compliance because it imposes composition rules without blocklist screening.
  - Neutral to [R1.1]/[T1], [R1.4]/[T4], [R1.5]/[T5], and [R1.6]/[T6] as written.

- [T10] Policy clause 3 — “Passwords expire every 90 days”:
  - Undermines [R1.4]/[T4] by mandating periodic password expiration.
  - Contributes to [R1.7]/[T7] non-compliance because it imposes rotation without blocklist screening.
  - Neutral to [R1.1]/[T1], [R1.2]/[T2], [R1.3]/[T3], [R1.5]/[T5], and [R1.6]/[T6] as written.

- [T11] Policy clause 4 — “Cannot reuse last 5 passwords”:
  - Is neutral to [R1.5]/[T5]: password history against the last 5 passwords is not the required common/expected/compromised-password blocklist and does not establish near-match rejection.
  - Is neutral to [R1.3]/[T3] and [R1.4]/[T4] because reuse history is neither the composition rule nor periodic expiration assessed there.
  - Does not neutralize the missing blocklist requirement under [R1.5]/[T5].

- [T12] Policy clause 5 — “Account locks after 3 failed attempts for 30 minutes”:
  - Serves [R1.6]/[T6] by mandating a failed-attempt lockout threshold below 100 consecutive failures.
  - Is neutral to [R1.1]/[T1], [R1.2]/[T2], [R1.3]/[T3], [R1.4]/[T4], [R1.5]/[T5], and [R1.7]/[T7].
  - Does not compensate for the missing blocklist required by [R1.5]/[T5] or the composition/rotation violations in [T3]/[T4]/[T7].

## FORMAL CONCLUSION

- Disposition summary:
  - [R1.1] is `COMPLIANT` per [T1].
  - [R1.2] is `UNABLE TO VERIFY` per [T2].
  - [R1.3] is `NON-COMPLIANT` per [T3].
  - [R1.4] is `NON-COMPLIANT` per [T4].
  - [R1.5] is `UNABLE TO VERIFY` per [T5].
  - [R1.6] is `COMPLIANT` per [T6].
  - [R1.7] is `NON-COMPLIANT` per [T7].

- Non-compliant items:
  1. [R1.3] / [T3] — Verbatim [P1] clause: “Must include uppercase, lowercase, number, and special character”.
  2. [R1.4] / [T4] — Verbatim [P1] clause: “Passwords expire every 90 days”.
  3. [R1.7] / [T7] — Verbatim [P1] clauses producing non-compliance: “Must include uppercase, lowercase, number, and special character” and “Passwords expire every 90 days”, coupled with the absence of any blocklist-screening or guidance clause in [P1].

- Partial and unverified items:
  - No `PARTIAL` dispositions were assigned.
  - [R1.2] / [T2] — `UNABLE TO VERIFY`: missing maximum-length ≥64 and printable-ASCII/space acceptance policy mandate plus verifier configuration/export and acceptance-test results.
  - [R1.5] / [T5] — `UNABLE TO VERIFY`: missing password-blocklist export/version and verifier blocklist configuration/integration artifact or test results showing match/near-match rejection.

- Severity ranking:
  1. HIGH — [R1.5] / [T5]: absence of documented blocklist screening is a central control gap.
  2. HIGH — [R1.3] / [T3]: [P1] directly mandates prohibited composition rules.
  3. HIGH — [R1.4] / [T4]: [P1] directly mandates prohibited periodic expiration.
  4. HIGH — [R1.7] / [T7]: composite prohibition is violated by composition/rotation without blocklist screening.
  5. MEDIUM — [R1.2] / [T2]: missing evidence for maximum length and printable-character/space acceptance.
  6. LOW — [R1.1] / [T1]: written policy meets minimum length; runtime enforcement gap remains.
  7. LOW — [R1.6] / [T6]: written policy mandates lockout below the 100-failure ceiling; runtime enforcement gap remains.

- Structural finding: The overall [P1] design pattern diverges from [R1]. [T8] shows clause 1 supports [R1.1]/[T1], and [T12] shows clause 5 supports [R1.6]/[T6]. However, [T9] clause 2 undermines [R1.3]/[T3] and contributes to [R1.7]/[T7]; [T10] clause 3 undermines [R1.4]/[T4] and contributes to [R1.7]/[T7]; and [T11] clause 4 is password history that does not substitute for the blocklist required by [R1.5]/[T5]. The policy therefore follows a legacy composition/rotation/history/lockout pattern rather than the [R1] blocklist-centered pattern.

- Verification gaps:
  - [T1] / [R1.1] runtime enforcement: `UNABLE TO VERIFY: verifier minimum-length configuration/export`; close by exporting password-policy configuration showing minimum length ≥8 and running a 7-character rejection / 8-character acceptance test.
  - [T2] / [R1.2]: `UNABLE TO VERIFY: verifier password-length and character-acceptance configuration/export plus acceptance-test results`; close by exporting max-length and allowed-character settings and testing a 64-character printable-ASCII-plus-space password.
  - [T5] / [R1.5]: `UNABLE TO VERIFY: password blocklist export/version and verifier blocklist configuration/integration artifact or test results showing match/near-match rejection`; close by exporting the blocklist and testing known common/compromised and near-match passwords.
  - [T6] / [R1.6] runtime enforcement: `UNABLE TO VERIFY: authentication lockout configuration/export and failed-attempt log query`; close by exporting lockout settings and querying failed-login logs or running a lockout test showing 3 failures cause a 30-minute lock and no more than 100 consecutive failures per account.

## REMEDIATION / NEXT ACTION

### Copy-pasteable redline of [P1]

```text
1. [REVISE] "Minimum 8 characters"
   -> "Minimum 8 characters; maximum password length must be at least 64 characters; all printable ASCII characters and space must be accepted." [R1.1, R1.2; T1, T2]

2. [DELETE] "Must include uppercase, lowercase, number, and special character"
   Deletion justification: this mandatory composition rule contradicts R1.3 [T3].
   [ADD] "Must not require mixtures of uppercase, lowercase, number, or special character; must offer user guidance on choosing passwords." [R1.3, R1.7; T3, T7]

3. [DELETE] "Passwords expire every 90 days"
   Deletion justification: this periodic expiration contradicts R1.4 [T4].
   [ADD] "Passwords must not expire periodically; change is forced only on evidence of authenticator compromise." [R1.4, R1.7; T4, T7]

4. [REVISE] "Cannot reuse last 5 passwords"
   -> "Cannot reuse last 5 passwords; prospective passwords must be compared against a blocklist of commonly used, expected, and compromised passwords, and matches or near-matches must be rejected." [R1.5; T5]

5. [REVISE] "Account locks after 3 failed attempts for 30 minutes"
   -> "Account locks after 3 failed attempts for 30 minutes; no more than 100 consecutive failed authentication attempts are permitted per account." [R1.6; T6]
```

### Final revised five-clause policy text, annotated

```text
1. Minimum 8 characters; maximum password length must be at least 64 characters; all printable ASCII characters and space must be accepted. [R1.1, R1.2; T1, T2]
2. Must not require mixtures of uppercase, lowercase, number, or special character; must offer user guidance on choosing passwords. [R1.3, R1.7; T3, T7]
3. Passwords must not expire periodically; change is forced only on evidence of authenticator compromise. [R1.4, R1.7; T4, T7]
4. Cannot reuse last 5 passwords; prospective passwords must be compared against a blocklist of commonly used, expected, and compromised passwords, and matches or near-matches must be rejected. [R1.5; T5]
5. Account locks after 3 failed attempts for 30 minutes; no more than 100 consecutive failed authentication attempts are permitted per account. [R1.6; T6]
```

### Replacement clauses for requirements marked NON-COMPLIANT, PARTIAL, or with ABSENT policy elements

- [R1.2; T2] “Maximum password length must be at least 64 characters; all printable ASCII characters and space must be accepted.”
- [R1.3; T3] “Must not require mixtures of uppercase, lowercase, number, or special character.”
- [R1.4; T4] “Passwords must not expire periodically; change is forced only on evidence of authenticator compromise.”
- [R1.5; T5] “Prospective passwords must be compared against a blocklist of commonly used, expected, and compromised passwords; matches or near-matches must be rejected.”
- [R1.7; T7] “Must offer user guidance and must not use composition or rotation rules as a substitute for blocklist screening.”

### Evidence-collection steps for UNABLE TO VERIFY items

- [T1]/[R1.1] runtime enforcement: Execute: export the verifier password-policy configuration showing minimum length, and run a test where a 7-character password is rejected and an 8-character password is accepted; retain the configuration export and test results. [R1.1; T1]
- [T2]/[R1.2]: Execute: export the verifier password-policy configuration showing maximum length and allowed-character rules, then submit a 64-character password containing printable ASCII characters and a space; verify it is accepted and retain the export and test results. [R1.2; T2]
- [T5]/[R1.5]: Execute: export the password blocklist source/version and blocklist rejection configuration; submit known common/compromised passwords and a near-match of a blocked value; verify rejection, query authentication logs for blocklist rejection events, and retain export, test results, and log query output. [R1.5; T5]
- [T6]/[R1.6] runtime enforcement: Execute: export the authentication lockout/rate-limit configuration; run a failed-login test or query failed-authentication logs demonstrating that 3 failures cause a 30-minute lock and that no more than 100 consecutive failed authentication attempts per account are permitted; retain export, test results, and log query output. [R1.6; T6]

Traceability self-check: Requirement dispositions cite [T1]–[T7]; policy-clause cross-effects cite [T8]–[T12]; the redline, replacement clauses, and evidence steps cite [R1.x] and [T] identifiers. No formal-conclusion or remediation claim is left without a [T] or [R1.x] identifier.

### EVALUATION: TEST 7

- **Word Count**: Baseline `400` words | Optimized `2397` words | Ratio `5.99x`
- **Eval Tokens**: Baseline `5843` | Optimized `29911`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 3.5      | 4.5       | +1.0  |
| Completeness  | 4.0      | 5.0       | +1.0  |
| Structure     | 4.5      | 4.0       | -0.5  |
| Actionability | 4.0      | 5.0       | +1.0  |
| Traceability  | 3.5      | 5.0       | +1.5  |
| TOTAL         | 19.5/25  | 23.5/25  | +4.0  |

The optimized response improved accuracy by avoiding the baseline’s material error that NIST 800-63B requires password history, and it better handled missing blocklist/max-length requirements through explicit gaps and remediation. It also improved completeness, actionability, and traceability with clear [R1]/[T] mappings and concrete evidence-collection steps. The main regression was structure: the certificate format became verbose and repetitive, adding unhelpful bloat for a five-clause policy review, while the baseline remained more concise and readable.

---

## TEST 8: Document Analysis (Mixed | Mode 1 (Max Certificate, Template 8 [C1]-[C3]))

### BASELINE RESPONSE

**Overall credibility: low to moderate as written.** The claims are not impossible, but they are presented as certain outcomes without methodology, baselines, evidence, or risk disclosures. This reads like marketing/pitch language rather than an evidentiary executive summary. Each claim needs substantiation before being relied on.

| Claim | Credibility | Why |
|---|---:|---|
| “Reduce support tickets by 60% within 6 months of deployment” | **Low–moderate** | 60% deflection/reduction is aggressive. It can happen in narrow, high-volume, repetitive-ticket scenarios, but depends heavily on baseline ticket mix, channel, product complexity, escalation rules, customer tolerance, and adoption. “Support tickets” is ambiguous: deflection, true resolution, reclassification, or channel shift? No baseline or pilot data given. |
| “Proprietary NLP technology outperforms all competitors” | **Low** | Absolute superlative is unverifiable and likely overstated. “Proprietary” does not mean superior; NLP/LLM capabilities are increasingly commoditized. Needs independent benchmarks, head-to-head tests, accuracy/escalation metrics, and defined “outperform” criteria. |
| “Implementation requires minimal IT involvement” | **Low** | Unrealistic for most customer-service AI: CRM/helpdesk integration, data access, SSO, security review, privacy/compliance, monitoring, model updates, and user provisioning all require IT/security involvement. “Minimal” is undefined. |
| “ROI will exceed 300% in the first year” | **Low** | ROI depends on total cost assumptions, ticket volume, labor cost, deflection rate, resolution quality, license fees, integration costs, and benefit-realization timing. A >300% first-year ROI is extremely aggressive, especially if deployment/ramp-up consumes part of year one. No calculation is shown. |

**Key red flags**
- Specific numeric outcomes without a stated methodology, baseline, pilot, or source.
- Absolute competitive claim (“all competitors”) with no benchmark.
- Understated implementation complexity.
- No mention of customer satisfaction, escalation rates, hallucination/error risk, data privacy, compliance, or change management.
- No total-cost or ROI model.
- Possible timeline tension: a 6-month deployment/ramp-up plus first-year >300% ROI requires very large benefits in a short window.

**What would raise credibility**
- Pilot results with pre-agreed metrics: ticket deflection, true resolution, escalation, CSAT, handling time, containment.
- Baseline ticket mix and assumptions.
- Independent benchmark or customer references.
- Detailed implementation plan and IT/security requirements.
- Transparent ROI model with all costs and benefit-realization assumptions.
- Clear definitions, limitations, and risk mitigations.

**Bottom line:** Treat these as **hypotheses to validate in a controlled pilot**, not established facts. As stated, the claims are plausible only under favorable, narrowly defined conditions and are not credible without supporting evidence.

### OPTIMIZED PROMPT

The standard document-credibility protocol for evaluating proposal claims requires completing this reasoning certificate before issuing any assessment.

### PREMISES
- [P1] Source artifact (sole evidence in scope, quoted verbatim in the CLAIM LEDGER): the executive summary of a project proposal, reproduced at [C1]-[C3] below.
- [P2] Claims under review: the three assertions itemized as [C1], [C2], [C3]. Each is evaluated independently before any aggregate judgment.
- [P3] Evaluation criteria applied uniformly to every claim: (a) quantitative specificity — is a baseline, denominator, timeframe, and measurement unit stated; (b) mechanism disclosure — is a method, dataset, or causal pathway described; (c) testability — can the claim be confirmed or refuted by an observable measurement; (d) internal consistency with the other claims in [P1]; (e) comparative basis — what benchmark or dataset grounds any superiority assertion.
- [P4] Explicit boundary assumptions: [P1] contains no appendices, financial model, benchmark results, customer references, pilot data, or competitive test set. That absence is itself a traceable fact about [P1], not an assumption about the underlying project.

### CLAIM LEDGER
- [C1] "Our AI-powered customer service solution will reduce support tickets by 60% within 6 months of deployment."
- [C2] "The system uses proprietary NLP technology that outperforms all competitors."
- [C3] "Implementation requires minimal IT involvement and the ROI will exceed 300% in the first year."

### EVIDENCE TRACES
For each claim in [C1]-[C3], complete all four steps in order:
1. Verbatim restatement and location within [P1].
2. Quantity audit: list every number, percentage, timeframe, and superlative asserted; for each, record whether [P1] states the corresponding baseline, denominator, comparison set, or measurement method.
3. Support audit: record any mechanism, methodology, dataset, benchmark, reference, or measurement that [P1] itself supplies for this claim.
4. Falsifiability audit: state the concrete measurement or artifact that would confirm or refute the claim, and record whether [P1] supplies it.

Then complete one cross-claim trace.

- [T1] Trace [C1] — ticket-reduction claim: [four steps above, each anchored to the literal wording of [P1]]
- [T2] Trace [C2] — competitive-superiority claim: [four steps above, each anchored to the literal wording of [P1]]
- [T3] Trace [C3] — implementation-effort and ROI claim: [four steps above, each anchored to the literal wording of [P1]]
- [T4] Cross-claim consistency: compare [C1], [C2], [C3] against one another; record any quantitative dependency (e.g., whether a 300% first-year ROI is reconcilable with a 6-month deployment window) and whether [P1] supplies the figures that would reconcile them.

GROUNDING RULE: Anchor every trace step in the literal wording of [P1]. When the baseline, method, benchmark, or measurement behind a claim is not printed in [P1], record `UNSUPPORTED IN [P1]: [exact missing artifact]` at that step and carry that status into the conclusion. When a claim asserts a comparison against competitors, record the named comparison set if present and `UNSPECIFIED COMPARISON SET` if the text names none.

### FORMAL CONCLUSION
- Per-claim rating: for each of [C1], [C2], [C3], state SUPPORTED / PARTIALLY SUPPORTED / UNSUPPORTED, with the specific [T] identifiers that carry the rating and the exact criterion from [P3] that drove it.
- Aggregate credibility assessment: a single paragraph synthesizing the three ratings, grounded strictly in [T1]-[T4].
- Verification gaps: every item recorded as `UNSUPPORTED IN [P1]` or `UNSPECIFIED COMPARISON SET`, listed with the artifact that would close it.
- Falsification summary: the one measurement per claim that would most efficiently test it, drawn from the step-4 audits.

### REMEDIATION / NEXT ACTION
The task is incomplete until this section delivers one of the following:
- A specific evidence-request list: for each Verification Gap, the exact artifact type (e.g., pilot ticket-volume data with pre/post baselines, benchmark methodology and competitor set, implementation staffing estimate, ROI model with cost inputs) that would allow the claim to be re-evaluated.
- A rewritten, defensible version of each [C1]-[C3] claim that states only what [P1] currently supports, preserving the original intent at a supportable strength.
- The explicit statement: "No remediation required: [reason citing T-identifiers]."

VERIFICATION & TRACEABILITY CONTRACT:
- Grounding predicate: every step in [T1]-[T4] cites the literal text of [P1] rather than the claim's topic or title.
- Missing-evidence predicate: when support for a claim is absent from [P1], record `UNSUPPORTED IN [P1]: [exact missing artifact]` at that step and list it under Verification Gaps.
- Counterevidence predicate: when [P1] contains wording that weakens a claim (unstated baseline, undefined comparison set, unquantified "minimal," unsourced projection), record it as an explicit step inside that claim's trace even when the headline number appears impressive.
- Neutrality predicate: derive every rating from [T1]-[T4] and the [P3] criteria alone, independent of the proposal's stated ambitions, market context, or any downstream use of this assessment.

TRACEABILITY SELF-CHECK (complete before finalizing): confirm that every rating and every sentence in the Formal Conclusion cites at least one [T] identifier and one [P3] criterion. Where a sentence lacks a supporting identifier, add the trace from [P1] or remove the sentence so zero orphaned conclusions remain.

### OPTIMIZED RESPONSE

# Document-Credibility Reasoning Certificate

**Scope note:** Per [P1], the sole evidence in scope is the executive summary reproduced literally at [C1]-[C3]. Per [P4], [P1] contains no appendices, financial model, benchmark results, customer references, pilot data, or competitive test set. No external evidence is used below.

---

## [T1] Trace [C1] — ticket-reduction claim

1. **Verbatim restatement and location in [P1]:**  
   [C1]: “Our AI-powered customer service solution will reduce support tickets by 60% within 6 months of deployment.”  
   Location: [P1], reproduced at CLAIM LEDGER [C1] as the first sentence of the executive summary.

2. **Quantity audit:**  
   - **“60%”**: percentage reduction asserted. Baseline pre-deployment ticket volume/rate: not stated. Denominator/scope: not stated. Measurement method: not stated.  
     `UNSUPPORTED IN [P1]: pre-deployment baseline ticket volume, ticket scope/denominator, and 60% calculation method.`  
   - **“6 months”**: timeframe after deployment. Deployment start definition and measurement window method: not stated.  
     `UNSUPPORTED IN [P1]: deployment start definition and six-month measurement plan.`  
   - **“support tickets”**: unit named, but no ticket definition, channel scope, or segmentation.  
     `UNSUPPORTED IN [P1]: ticket definition and channel/segment scope.`  
   - **Superlatives:** none asserted.  
   - **Counterevidence note:** the headline “60%” is numerically specific but not auditable from [P1] because the baseline and denominator are unstated.

3. **Support audit:**  
   [P1] supplies only the phrase “AI-powered customer service solution.” It supplies no method, dataset, benchmark, reference, pilot result, or causal pathway.  
   `UNSUPPORTED IN [P1]: method/dataset/causal pathway for the AI solution’s claimed ticket reduction.`

4. **Falsifiability audit:**  
   A concrete test would measure pre-deployment support-ticket volume for a defined scope and six-month post-deployment ticket volume, then compute the percentage change. [P1] does not supply the needed measurement artifact.  
   `UNSUPPORTED IN [P1]: pre/post ticket-volume data and measurement protocol.`

---

## [T2] Trace [C2] — competitive-superiority claim

1. **Verbatim restatement and location in [P1]:**  
   [C2]: “The system uses proprietary NLP technology that outperforms all competitors.”  
   Location: [P1], reproduced at CLAIM LEDGER [C2] as the second sentence of the executive summary.

2. **Quantity audit:**  
   - **“outperforms”**: superlative/comparative assertion. Performance metric, magnitude, baseline, denominator, and measurement unit: not stated.  
     `UNSUPPORTED IN [P1]: performance metric and baseline for “outperforms.”`  
   - **“all competitors”**: comparison set asserted in generic, unbounded form. No named competitor, benchmark, dataset, or competitive test set is printed.  
     `UNSPECIFIED COMPARISON SET: no named competitor set, benchmark, or competitive test set is printed in [P1].`  
   - **“proprietary NLP technology”**: no number or timeframe, but a mechanism-category phrase. Technical method/dataset/performance measurement: not stated.  
     `UNSUPPORTED IN [P1]: technical method, dataset, and performance measurement for proprietary NLP.`  
   - **Counterevidence note:** “all competitors” is unbounded, so the superiority assertion cannot be bounded or audited from the literal text.

3. **Support audit:**  
   [P1] supplies only the phrase “proprietary NLP technology.” It supplies no methodology, benchmark, dataset, competitor result, reference, or measurement.  
   `UNSUPPORTED IN [P1]: benchmark methodology, named comparison set, and competitor results.`

4. **Falsifiability audit:**  
   A concrete test would run a controlled benchmark against a named competitor set on a defined NLP task and metric. [P1] does not supply the benchmark design or comparison set.  
   `UNSUPPORTED IN [P1]: benchmark design, named competitor set, test dataset, and metric.`  
   `UNSPECIFIED COMPARISON SET`.

---

## [T3] Trace [C3] — implementation-effort and ROI claim

1. **Verbatim restatement and location in [P1]:**  
   [C3]: “Implementation requires minimal IT involvement and the ROI will exceed 300% in the first year.”  
   Location: [P1], reproduced at CLAIM LEDGER [C3] as the third sentence of the executive summary.

2. **Quantity audit:**  
   - **“minimal IT involvement”**: unquantified term. No IT hours, roles, cost, dependencies, or threshold for “minimal” are stated.  
     `UNSUPPORTED IN [P1]: definition/threshold and staffing estimate for “minimal IT involvement.”`  
   - **“300%” ROI**: percentage threshold asserted. ROI formula, baseline/cost denominator, benefit/cost inputs, and measurement method: not stated.  
     `UNSUPPORTED IN [P1]: ROI formula, cost inputs, benefit calculations, and baseline/denominator for the 300% ROI.`  
   - **“first year”**: timeframe asserted. Start date, deployment-to-first-year mapping, and benefit-realization schedule: not stated.  
     `UNSUPPORTED IN [P1]: first-year period definition and cost/benefit schedule.`  
   - **“exceed”**: threshold comparison to 300%, but no financial model or projection basis is supplied.  
     `UNSUPPORTED IN [P1]: financial model or projection basis for exceeding 300%.`  
   - **Counterevidence note:** “minimal” is unquantified, and “300%” is an unsourced projection absent a financial model.

3. **Support audit:**  
   [P1] supplies no implementation methodology, staffing estimate, financial model, ROI calculation, benchmark, reference, or measurement.  
   `UNSUPPORTED IN [P1]: implementation staffing estimate and first-year ROI model.`

4. **Falsifiability audit:**  
   A concrete test would measure IT staff hours/roles required for implementation and calculate first-year ROI from documented costs and benefits. [P1] does not supply the staffing records or financial model.  
   `UNSUPPORTED IN [P1]: implementation staffing records and first-year ROI financial model.`

---

## [T4] Cross-claim consistency

- **[T4]/[P3](d):** A 60% ticket reduction within 6 months could in principle contribute to first-year ROI, but only if ticket volume, cost per ticket, implementation cost, and benefit timing are known; [P1] supplies no such figures to reconcile [C1] and [C3].  
  `UNSUPPORTED IN [P1]: integrated first-year cost-benefit model linking 60% ticket reduction to >300% ROI.`

- **[T4]/[P3](d):** The six-month deployment window falls literally within “the first year,” so [P1] contains no explicit timeline contradiction; reconciliation still requires a deployment schedule and a benefit-realization schedule.  
  `UNSUPPORTED IN [P1]: deployment schedule and benefit-realization schedule.`

- **[T4]/[P3](d,e):** [C2]’s “outperforms all competitors” supplies no benchmark result that can ground [C1] or [C3]; the comparison remains `UNSPECIFIED COMPARISON SET`, and no linkage between NLP superiority and ticket/ROI outcomes is printed.  
  `UNSUPPORTED IN [P1]: benchmark-to-business-outcome linkage between C2 superiority and C1/C3 outcomes.`

---

# FORMAL CONCLUSION

## Per-claim ratings

- **[C1] — UNSUPPORTED:** [T1] records that “60%” and “6 months” lack baseline ticket volume/scope and a supplied measurement method under [P3](a), and that no method/dataset/causal pathway is supplied under [P3](b), with no pre/post data supplied for the falsifiability audit under [P3](c).

- **[C2] — UNSUPPORTED:** [T2] records no metric, baseline, method/dataset, benchmark, or named comparison set, failing [P3](a), [P3](b), [P3](c) supplied support, and [P3](e), with `UNSPECIFIED COMPARISON SET` recorded in [T2].

- **[C3] — UNSUPPORTED:** [T3] records that “minimal” is unquantified and the >300% first-year ROI lacks formula, cost inputs, benefits, and measurement under [P3](a), with no implementation/ROI mechanism under [P3](b) and no supplied ROI evidence under [P3](c).

## Aggregate credibility assessment

Aggregate credibility is UNSUPPORTED: [T1] and [T3] show the quantitative claims lack baselines, denominators, methods, and financial inputs required by [P3](a), [T2] lacks a metric and [T2]/[T4] record an `UNSPECIFIED COMPARISON SET` under [P3](e), all three traces lack mechanism or benchmark support under [P3](b), and [T4] finds no [P1] figures to reconcile the 60% ticket-reduction and >300% first-year-ROI assertions under [P3](d).

## Verification gaps

- **[T1]/[P3](a):** `UNSUPPORTED IN [P1]: pre-deployment baseline ticket volume and ticket scope/denominator.` Closing artifact: pre/post ticket-volume dataset with the same ticket definition and channel scope, including pre-deployment baseline.

- **[T1]/[P3](a,c):** `UNSUPPORTED IN [P1]: 60% calculation method and six-month measurement plan/deployment start definition.` Closing artifact: measurement protocol, deployment start/end dates, and percentage-change calculation formula.

- **[T1]/[P3](b):** `UNSUPPORTED IN [P1]: method/dataset/causal pathway for the AI solution’s claimed ticket reduction.` Closing artifact: technical method documentation and pilot or controlled pre/post study/data linking the AI solution to ticket reduction.

- **[T2]/[P3](a):** `UNSUPPORTED IN [P1]: performance metric and baseline for “outperforms.”` Closing artifact: defined performance metric and baseline measurement.

- **[T2]/[P3](e):** `UNSPECIFIED COMPARISON SET`: no named competitor set, benchmark, or competitive test set is printed in [P1]. Closing artifact: named competitor list and benchmark methodology/results.

- **[T2]/[P3](b,c):** `UNSUPPORTED IN [P1]: benchmark methodology, test dataset, and competitor performance measurement.` Closing artifact: benchmark protocol, test dataset, and competitor performance results.

- **[T2]/[P3](b):** `UNSUPPORTED IN [P1]: technical method/dataset documentation for “proprietary NLP technology.”` Closing artifact: technical architecture/method documentation and dataset documentation.

- **[T3]/[P3](a):** `UNSUPPORTED IN [P1]: definition/threshold and staffing estimate for “minimal IT involvement.”` Closing artifact: implementation staffing estimate with IT hours, roles, dependencies, and a stated threshold for “minimal.”

- **[T3]/[P3](a):** `UNSUPPORTED IN [P1]: ROI formula, cost inputs, benefit calculations, and baseline/denominator for the 300% ROI.` Closing artifact: first-year ROI financial model with costs, savings, assumptions, and formula.

- **[T3]/[P3](a,c):** `UNSUPPORTED IN [P1]: first-year period definition and cost/benefit schedule.` Closing artifact: deployment and benefit-realization timeline.

- **[T4]/[P3](d):** `UNSUPPORTED IN [P1]: integrated first-year cost-benefit model linking 60% ticket reduction to >300% ROI.` Closing artifact: model combining pre/post ticket volume, cost per ticket, implementation costs, and benefit timing.

- **[T4]/[P3](d,e):** `UNSUPPORTED IN [P1]: benchmark-to-business-outcome linkage between C2 superiority and C1/C3 outcomes.` Closing artifact: evidence connecting NLP benchmark results to ticket reduction or ROI, using a named competitor benchmark.

- **[T4]/[P3](d):** `UNSUPPORTED IN [P1]: deployment schedule and benefit-realization schedule reconciling six-month deployment with first-year ROI.` Closing artifact: deployment timeline and benefit realization schedule.

## Falsification summary

- **[C1]/[T1]/[P3](c):** The most efficient test is a pre/post support-ticket measurement for a defined ticket scope from a pre-deployment baseline to six months after deployment, computing the percentage reduction.

- **[C2]/[T2]/[P3](e,c):** The most efficient test is a controlled benchmark against a named competitor set on a defined NLP task/dataset using a stated performance metric.

- **[C3]/[T3]/[P3](a,c):** The most efficient test is an audited implementation IT-staffing calculation plus a first-year ROI calculation from documented costs and benefits, tested against a stated threshold for “minimal.”

---

# REMEDIATION / NEXT ACTION

**Selected action: specific evidence-request list.**

1. For [C1]: pre/post ticket-volume dataset with a pre-deployment baseline, ticket definition, channel scope, deployment dates, and six-month measurement protocol.
2. For [C1]: technical method/dataset documentation and pilot or controlled pre/post evidence linking the AI solution to ticket reduction.
3. For [C2]: named competitor set, metric definition, benchmark methodology, test dataset, and competitor performance results.
4. For [C2]: technical method/dataset documentation for the “proprietary NLP technology.”
5. For [C3]: implementation staffing estimate with IT hours, roles, dependencies, and a defined threshold for “minimal IT involvement.”
6. For [C3]: first-year ROI financial model with cost inputs, benefit calculations, formula, assumptions, deployment schedule, and benefit-realization schedule.
7. For [T4]: an integrated cost-benefit model linking the claimed 60% ticket reduction to first-year ROI, plus benchmark-to-business-outcome linkage if [C2] is intended to support business outcomes.

**Traceability self-check:** Per-claim ratings cite [T1]-[T3] and [P3] criteria; the aggregate paragraph cites [T1]-[T4] and [P3](a,b,d,e); Verification Gaps and Falsification Summary items cite their relevant [T] and [P3] criteria; no orphaned conclusions remain.

### EVALUATION: TEST 8

- **Word Count**: Baseline `399` words | Optimized `1677` words | Ratio `4.2x`
- **Eval Tokens**: Baseline `1542` | Optimized `14334`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5.0      | 5.0       | 0.0   |
| Completeness  | 4.5      | 5.0       | +0.5  |
| Structure     | 5.0      | 4.0       | -1.0  |
| Actionability | 4.5      | 5.0       | +0.5  |
| Traceability  | 3.5      | 5.0       | +1.5  |
| TOTAL         | 22.5/25  | 24.0/25   | +1.5  |

The optimized response improved completeness, actionability, and traceability by adding explicit claim-by-claim evidence audits, verification gaps, falsification tests, and a specific evidence-request list. Accuracy remained comparable because both correctly identified the claims as unsupported and low credibility as written. The optimized response’s structure got worse due to substantial redundancy and bloat from repeating the same unsupported findings across traces, gaps, and remediation.

---

## TEST 9: Comparative Analysis (Mixed | Mode 2 (Lite Certificate [LITE], Template 9 [D1]-[D3], target <1.5x overhead))

### BASELINE RESPONSE

**Bottom line:** For a new app with structured transactions **and** semi-structured activity logs, **PostgreSQL is the safer default**—use relational tables for transactions and `JSONB` for logs, with time-based partitioning and retention. MongoDB is viable, especially for the log side, but at **10M records/month growing 20%/year**, native sharding is probably premature, and MongoDB’s advantages in schema flexibility usually do not outweigh PostgreSQL’s advantages in transactions, joins, constraints, and SQL analytics.

## Sizing the workload

10M records/month initially:

- **Year 1:** 120M records
- **Year 5:** ~20.7M/month, ~249M/year
- **5-year total:** ~893M records  
  Formula: `10M × 12 × (1 + 1.2 + 1.44 + 1.728 + 2.0736) ≈ 893M`

Average write rate is only **~4 records/sec initially**, **~8/sec by year 5**—before bursts. If 10M/month is transactions **plus** logs, this is modest. If logs are additional and much larger, adjust the numbers, but the conclusion is similar: the hard parts are **query patterns, retention, indexing, and schema evolution**, not raw write throughput.

At ~2KB/record, 5 years is ~1.8TB raw; at ~5KB/record, ~4.5TB. With indexes, plan for 2–3×. Both systems can handle this with partitioning/sharding and retention.

## Comparison

| Dimension | PostgreSQL | MongoDB | Practical winner |
|---|---|---|---|
| Structured transaction data | Strong relational model, FKs, constraints, ACID | Document model; transactions possible but relational integrity is manual | **PostgreSQL** |
| Semi-structured logs | `JSONB`, GIN indexes, generated columns, SQL | Native document model, flexible schema, TTL | **MongoDB slightly**, but PostgreSQL `JSONB` is usually enough |
| ACID / multi-row transactions | Mature, full ACID, multi-table transactions | Multi-document transactions supported, but overhead and modeling constraints | **PostgreSQL** |
| Joins between transactions and logs | Native SQL joins | `$lookup` is limited/expensive at scale | **PostgreSQL** |
| Query/analytics | SQL, window functions, CTEs, mature BI ecosystem | Aggregation pipeline; good but less expressive for relational analytics | **PostgreSQL** |
| Flexible schema | `JSONB` flexible, but relational migrations for core fields | Schema-less by default; optional JSON Schema validation | **MongoDB** |
| Indexing semi-structured data | B-tree, GIN on `JSONB`, expression/partial/BRIN indexes | Compound, multikey, wildcard, text, TTL indexes | Tie, with tradeoffs |
| Horizontal scaling | Vertical + replicas + partitioning; sharding via Citus/other | Native sharding | **MongoDB** for native sharding, but likely unnecessary here |
| Retention | Drop/detach partitions—fast and cheap | TTL indexes—easy, but deletion is background/asynchronous | Tie; PostgreSQL partitions often cleaner for compliance |
| Operational complexity | Mature single-primary model; partitioning is straightforward | Replica sets simple; sharded clusters add shard-key and ops complexity | **PostgreSQL** for this scale |
| Consistency | Strong consistency by default | Tunable read/write concerns | **PostgreSQL** |
| Document limits | TOAST handles large values; avoid huge JSON | 16MB document limit; avoid unbounded arrays | Tie—model event-per-row/document |

## Recommended PostgreSQL design

Use PostgreSQL as the system of record:

1. **Transactions:** normalized relational tables with primary keys, foreign keys, check constraints, and proper isolation. This is where PostgreSQL clearly wins.

2. **Activity logs:** one row per event, not nested arrays:
   ```sql
   CREATE TABLE activity_logs (
     id bigserial,
     occurred_at timestamptz NOT NULL,
     user_id bigint NOT NULL,
     event_type text NOT NULL,
     entity_type text,
     entity_id bigint,
     payload jsonb NOT NULL,
     PRIMARY KEY (id, occurred_at)
   ) PARTITION BY RANGE (occurred_at);
   ```

3. **Partition by month** on `occurred_at`. Drop or archive old partitions for retention. This is usually better than deleting individual rows.

4. **Indexes:**
   - `BRIN` on `occurred_at` for time-range scans.
   - B-tree on `(user_id, occurred_at)` and `(event_type, occurred_at)`.
   - `GIN` on `payload` only if you truly query arbitrary JSON fields; otherwise extract hot fields into columns/generated columns and index those.
   - Avoid indexing the entire payload blindly—GIN indexes can be large and slow writes.

5. **Write path:** batch inserts, async logging queue, multi-row inserts/`COPY` where possible. Do not wrap every log write in a long transaction.

6. **Read path:** use read replicas for dashboards/analytics; consider materialized views. If logs become time-series-heavy, evaluate TimescaleDB as an extension rather than switching databases.

## When MongoDB makes sense

Choose MongoDB—or a hybrid—only if you have concrete requirements such as:

- Activity event schemas vary wildly per event and change frequently.
- You need native horizontal sharding and multi-region deployment sooner than expected.
- Your team is already MongoDB-centric and can model transactions carefully.
- Logs are document-centric and queried mostly by document key/time, not joined heavily to transactions.

If you go hybrid, use **PostgreSQL for transactions** and **MongoDB for logs**, but avoid dual writes. Use an outbox/CDC pattern, and accept that cross-store joins will need application-level composition or a warehouse. That operational complexity is usually not justified at 10M records/month.

## Final recommendation

**Start with PostgreSQL.** It handles the structured transaction data natively, handles semi-structured logs well with `JSONB`, gives you strong ACID guarantees, SQL joins/analytics, and simple retention via partitioning. At this volume, you likely will not need sharding for years. Revisit the architecture if active log volume exceeds several TB, write throughput reaches thousands of events/sec sustained, or you need native multi-region sharding—then consider Citus, a dedicated log/OLAP store, or MongoDB for the log side only.

### OPTIMIZED PROMPT

```
You are a systems analyst. The standard comparative analysis protocol requires completing this certificate before issuing any comparison summary.

### PREMISES (cap: 3)
- [P1] Subjects compared: PostgreSQL (relational engine with ACID transactions and native JSONB) and MongoDB (document store with multi-document transactions and schema-flexible collections). Pinned versions under evaluation: [state exact versions, e.g., PostgreSQL 16.x vs. MongoDB 7.x].
- [P2] Workload profile: one application persisting both (a) structured transaction records with multi-row consistency requirements and (b) semi-structured user activity logs with evolving fields; sustained ingest of 10M records per month compounded at 20% annual growth.
- [P3] Evaluation axes, applied identically to both subjects:
  - [D1] Transaction integrity and multi-record consistency guarantees
  - [D2] Semi-structured log ingest and query flexibility under schema drift
  - [D3] Operational scaling and storage/index behavior at the projected volume curve

### COMPARISON TRACES (Lite: one causal arrow per axis)
- [T1] [D1] Transaction integrity: PostgreSQL -> [mechanism from P1: multi-statement ACID scope, isolation levels, constraint enforcement] -> [observable consequence for P2 transaction records]; MongoDB -> [mechanism from P1: multi-document transaction scope, write concern, validation rules] -> [observable consequence]; Differential -> [subject leading on D1 and by what margin]; Crossover -> [condition under which the D1 advantage reverses].
- [T2] [D2] Semi-structured flexibility: PostgreSQL -> [JSONB indexing/query mechanism and its schema-governance cost from P1] -> [observable consequence for P2 activity logs]; MongoDB -> [document model and index mechanism from P1] -> [observable consequence]; Differential -> [subject leading on D2 and why]; Crossover -> [condition under which the D2 advantage reverses].
- [T3] [D3] Scaling at projected volume: PostgreSQL -> [partitioning/index/write-path behavior from P1 applied to the P2 growth curve] -> [projected pressure point]; MongoDB -> [sharding/index/write-path behavior from P1 applied to the same curve] -> [projected pressure point]; Differential -> [subject leading on D3 at 10M/month and at the 20%-growth horizon]; Crossover -> [volume or read/write ratio at which the lead changes].

Grounding rule: derive each [D] assessment from the mechanisms and versions stated in [P1]-[P3] rather than from general product reputation. When a required metric is absent from [P1]-[P3], record `UNMEASURED IN [P1]-[P3]: [subject/metric]` and exclude that metric from the conclusion.

### FORMAL CONCLUSION
- Verdict: [one to two sentences naming the fit for the P2 workload, citing [T1], [T2], [T3] for every claim].
- Workload-conditional selection: [which subject fits which condition of [D1]-[D3], citing traces].
- Verification gaps: [every axis or metric recorded as UNMEASURED, plus the input needed to close it].

### REMEDIATION / NEXT ACTION
The task is incomplete until this section contains one of the following:
- A concrete implementation path (single-engine choice with configuration specifics, or a polyglot split assigning transaction records and activity logs to named stores) plus the exact benchmark commands to validate it against the P2 volume curve (e.g., `pgbench` and `mongoperf`/YCSB invocations with stated parameters).
- A concrete sequence of measurements that resolves each Verification Gap.
- The explicit statement: "No remediation required: [reason grounded in T-identifiers]".

TRACEABILITY SELF-CHECK: Confirm that every claim in the Formal Conclusion cites at least one [T] identifier and maps to a [D] axis in [P3]. When a claim has no supporting identifier, either add the missing trace from [P1]-[P3] or remove the claim so zero orphaned conclusions remain.
```

### OPTIMIZED RESPONSE

### COMPLETED CERTIFICATE

#### PREMISES
- **[P1]** Subjects compared: PostgreSQL (relational engine with ACID transactions and native JSONB) and MongoDB (document store with multi-document transactions and schema-flexible collections). **UNMEASURED IN [P1]-[P3]: PostgreSQL exact pinned version; MongoDB exact pinned version.** Therefore no version-specific feature claims are made.
- **[P2]** Workload profile: one application persisting both (a) structured transaction records with multi-row consistency requirements and (b) semi-structured user activity logs with evolving fields; sustained ingest of **10M records/month**, compounded at **20% annual growth** → **12M/month at year 1, 14.4M/month at year 2, 17.28M/month at year 3**. **UNMEASURED IN [P1]-[P3]: record/document sizes, read/write ratio, retention period, index definitions, hardware, latency/throughput SLOs.**
- **[P3]** Evaluation axes applied identically: **[D1]** transaction integrity and multi-record consistency; **[D2]** semi-structured log ingest/query flexibility under schema drift; **[D3]** operational scaling and storage/index behavior at the projected volume curve.

#### COMPARISON TRACES
- **[T1] [D1] Transaction integrity:** PostgreSQL -> [P1 mechanism: relational ACID transactions] multi-statement ACID scope; **UNMEASURED IN [P1]-[P3]: PostgreSQL isolation levels; PostgreSQL constraint enforcement** -> [P2 consequence] direct mechanism-level alignment with multi-row consistency for structured transaction records; exact abort/latency/consistency margin **UNMEASURED IN [P1]-[P3]: D1 PostgreSQL margin**. MongoDB -> [P1 mechanism: multi-document transactions + schema-flexible collections] multi-document transaction scope; **UNMEASURED IN [P1]-[P3]: MongoDB write concern; MongoDB validation rules** -> [P2 consequence] can commit multi-document changes, but schema enforcement depends on configuration not stated; exact consistency margin **UNMEASURED IN [P1]-[P3]: D1 MongoDB margin**. **Differential:** PostgreSQL leads at the stated mechanism level for ACID multi-row consistency; measured margin **UNMEASURED IN [P1]-[P3]: D1 differential**. **Crossover:** PostgreSQL’s D1 advantage narrows or reverses when transaction records fit in a single MongoDB document and majority write concern/validation meet the required consistency test; exact crossover **UNMEASURED IN [P1]-[P3]: D1 crossover condition**.

- **[T2] [D2] Semi-structured flexibility:** PostgreSQL -> [P1 mechanism: native JSONB] stores semi-structured activity fields in relational rows; **UNMEASURED IN [P1]-[P3]: PostgreSQL JSONB indexing/query mechanisms; PostgreSQL schema-governance cost** -> [P2 consequence] can persist evolving log fields, but ingest/query performance under schema drift is **UNMEASURED IN [P1]-[P3]: D2 PostgreSQL consequence**. MongoDB -> [P1 mechanism: schema-flexible document collections] document model avoids fixed-column migration for evolving fields; **UNMEASURED IN [P1]-[P3]: MongoDB index mechanism; MongoDB query latency** -> [P2 consequence] qualitative fit for schema-drifting activity logs, with exact performance **UNMEASURED IN [P1]-[P3]: D2 MongoDB consequence**. **Differential:** MongoDB leads on stated schema flexibility; PostgreSQL native JSONB narrows the gap, but the measured D2 margin is **UNMEASURED IN [P1]-[P3]: D2 differential**. **Crossover:** the D2 lead narrows or reverses when activity logs require relational joins/constraints or when PostgreSQL JSONB indexes satisfy all top queries; exact crossover **UNMEASURED IN [P1]-[P3]: D2 crossover condition**.

- **[T3] [D3] Scaling at projected volume:** PostgreSQL -> [P1 mechanism: relational engine] applied to P2’s 10M/month curve and 20% annual growth; **UNMEASURED IN [P1]-[P3]: PostgreSQL partitioning/index/write-path behavior** -> projected pressure point **UNMEASURED IN [P1]-[P3]: PostgreSQL D3 pressure point**. MongoDB -> [P1 mechanism: document store] applied to the same curve; **UNMEASURED IN [P1]-[P3]: MongoDB sharding/index/write-path behavior** -> projected pressure point **UNMEASURED IN [P1]-[P3]: MongoDB D3 pressure point**. **Differential:** no subject has a measured D3 lead at 10M/month or at the 20%-growth horizon (12M, 14.4M, 17.28M/month); **UNMEASURED IN [P1]-[P3]: D3 differential at projected volume**. **Crossover:** the volume or read/write ratio at which the D3 lead changes is **UNMEASURED IN [P1]-[P3]: D3 crossover point**.

#### FORMAL CONCLUSION
- **Verdict:** Provisional polyglot fit: PostgreSQL for structured transaction records because [P1] states ACID transactions aligning with multi-row consistency **[T1/D1]**; MongoDB for activity logs because [P1] states schema-flexible collections aligning with schema drift **[T2/D2]**; D3 engine choice is undecided because storage/index/write-path behavior at the P2 volume curve is **UNMEASURED IN [P1]-[P3]** **[T3/D3]**.
- **Workload-conditional selection:** Select PostgreSQL where D1 multi-row consistency/ACID is mandatory **[T1/D1]**; select MongoDB where D2 schema drift and ingest flexibility dominate **[T2/D2]**; select or split for D3 only after measurement because no measured D3 lead exists at 10M/month or the 20%-growth horizon **[T3/D3]**.
- **Verification gaps:**  
  - **[T1/D1] UNMEASURED IN [P1]-[P3]:** exact versions, PostgreSQL isolation levels/constraint enforcement, MongoDB write concern/validation rules, D1 abort/latency/consistency margin. Input needed: pin versions, define transaction schema/contention, run multi-row transaction tests.  
  - **[T2/D2] UNMEASURED IN [P1]-[P3]:** PostgreSQL JSONB indexing/query/schema-governance cost, MongoDB index/query behavior, D2 ingest/query margin, schema-drift rate, field distribution, query patterns. Input needed: define log evolution and top queries/indexes, run ingest/query benchmarks.  
  - **[T3/D3] UNMEASURED IN [P1]-[P3]:** PostgreSQL partitioning/index/write-path behavior, MongoDB sharding/index/write-path behavior, storage/index size, hardware, record/document sizes, retention, read/write ratio, SLOs, crossover point. Input needed: specify hardware/retention/workload mix/SLOs and run volume-curve tests.

#### REMEDIATION / NEXT ACTION
**Recommended path:** Polyglot split — assign transaction records to **PostgreSQL** with explicit multi-statement ACID transactions and constraints; assign activity logs to **MongoDB** with schema-flexible collections, majority write concern, and indexes on frequent log query fields. Validate against the P2 volume curve with the following sequence.

1. **Pin versions and environment:**  
   ```bash
   psql -Atc 'select version()'
   mongosh --quiet --eval 'db.version()'
   ```  
   Record hardware, storage, OS, network, record/document size distribution, retention, read/write mix, and SLOs.

2. **D1 transaction-integrity measurement:** Create transaction schema with PK/FK/unique/check constraints and a custom `txn.sql` multi-row transaction script; then run:  
   ```bash
   pgbench -i -s 100
   pgbench -c 64 -j 8 -T 600 -f txn.sql -P 30
   ```  
   Run the equivalent multi-document transaction workload via `mongosh`/YCSB transaction binding with `writeConcern=majority`, same concurrency, duration, and record shape. Capture TPS, abort/serialization rate, p95, and consistency-check failures.

3. **D2 activity-log ingest/query measurement:** Load 10M evolving-field documents/rows and run identical queries. Example commands:  
   ```bash
   mongosh --eval 'db.activity.createIndex({userId:1, ts:-1})'
   ycsb load mongodb -s -P workloads/workloada -p recordcount=10000000 -p mongodb.url=mongodb://localhost:27017/ycsb
   ycsb run mongodb -s -P workloads/workloada -p recordcount=10000000 -p operationcount=10000000 -p mongodb.url=mongodb://localhost:27017/ycsb
   ```  
   ```bash
   ycsb load jdbc -s -P workloads/workloada \
     -p db.driver=org.postgresql.Driver \
     -p db.url=jdbc:postgresql://localhost:5432/ycsb \
     -p db.user=postgres -p db.passwd=postgres \
     -p recordcount=10000000
   ycsb run jdbc -s -P workloads/workloada \
     -p db.driver=org.postgresql.Driver \
     -p db.url=jdbc:postgresql://localhost:5432/ycsb \
     -p db.user=postgres -p db.passwd=postgres \
     -p recordcount=10000000 -p operationcount=10000000
   ```  
   Also run a JSONB-specific `pgbench` script for evolving activity fields.

4. **D3 volume-curve measurement:** Repeat step 3 at monthly ingest points **10M, 12M, 14.4M, 17.28M** with retention scenarios, e.g. 1/3/5 years and indefinite. Capture PostgreSQL `pg_stat_user_tables`, `\di+`, `EXPLAIN (ANALYZE, BUFFERS)`, vacuum behavior; MongoDB `db.stats()`, `db.coll.stats()`, compaction, and replication lag. Sweep read/write ratios **95/5, 50/50, 5/95** to locate the D3 crossover.

**TRACEABILITY SELF-CHECK:** All Formal Conclusion claims cite **[T1]**, **[T2]**, or **[T3]**, mapping respectively to **[D1]**, **[D2]**, and **[D3]**. Unmeasured metrics are explicitly excluded from the verdict and workload-conditional selection; no orphaned conclusions remain.

### EVALUATION: TEST 9

- **Word Count**: Baseline `853` words | Optimized `1056` words | Ratio `1.24x`
- **Eval Tokens**: Baseline `6057` | Optimized `12919`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5        | 4         | -1    |
| Completeness  | 5        | 4         | -1    |
| Structure     | 5        | 4         | -1    |
| Actionability | 5        | 4.5       | -0.5  |
| Traceability  | 4.5      | 5         | +0.5  |
| TOTAL         | 24.5/25  | 21.5/25   | -3.0  |

The optimized response clearly improved formal traceability by mapping claims to [T1]-[T3]/[D1]-[D3] and by adding an explicit remediation/benchmark sequence. However, it became overly conservative and repetitive with `UNMEASURED` labels, which reduced practical completeness and decisiveness compared with the baseline’s clear PostgreSQL-first recommendation and concrete design guidance. The certificate structure was followed but added some unhelpful bloat, so Structure was penalized relative to the baseline.

---

## TEST 10: Creative Brief (Creative | Mode 4 (Creative & Divergent v2, Template 10 [NT0] Verbalized Sampling + [SC0] Anti-SlopShape))

### BASELINE RESPONSE

**Meet the Chair That Keeps Up With Your Marathon Workdays**

You don’t clock out at 5. You debug at midnight, ship features before breakfast, and take calls from the same seat for hours. Your chair shouldn’t tap out after two.

Built for remote tech workers who live in the 10+ hour zone, this ergonomic office chair is a quiet workhorse—no gimmicks, just relentless support where it counts.

**Auto-Adjusting Lumbar Support**  
Stop fiddling with knobs mid-standup. The lumbar system senses your posture and micro-adjusts continuously, so your lower back stays supported whether you’re leaning into a code review or sitting back for a design sync. It’s like having a ergonomist on retainer—minus the appointment.

**Breathable Mesh That Breathes With You**  
Ten hours in a chair means heat builds up. The high-tensile mesh back and seat keep air moving, so you stay cool through back-to-back sprints—no sticky, sweaty reset required. Durable enough for daily 12-hour grinds, soft enough for the occasional catnap between deploys.

**12-Year Warranty. Because We Mean It.**  
We build chairs for the long haul. A 12-year warranty covers the frame, mechanism, and mesh—so you can invest once and forget about it. No planned obsolescence. No “good enough for a year.” Just reliable support for your entire career chapter.

Your back does the heavy lifting. Let the chair do its part.

### OPTIMIZED PROMPT

```markdown
You are a product copywriter. The editorial craft protocol for product description writing requires completing the backstage scaffolding block before drafting the final piece.

### PREMISES
- [P1] Product facts (the only facts you may assert): ergonomic office chair; lumbar support that auto-adjusts to the sitter; breathable mesh; 12-year warranty; engineered for people who work 10+ hour days.
- [P2] Reader & lived context: remote tech workers, ages 25-45, working long desk sessions in a home office; they sit through back-to-back calls, shift posture unconsciously, and notice heat and pressure before they notice "support."
- [P3] Format & register: a product description of 120-180 words, plus a short headline; second person or first-person plural; concrete physical nouns; professional retail register.

### BACKSTAGE SCAFFOLD (complete first; keep it above the final piece)
- [NT0] Verbalized Distribution Sampling: enumerate 4 structurally distinct entry angles for this description and assign each an estimated typicality probability (p = how likely a default product-description prompt would produce it):
  1. Category announcement ("Introducing the ultimate ergonomic chair for remote workers") (p = 0.42)
  2. Benefit-stack listing (comfort, then breathability, then warranty, in sequence) (p = 0.31)
  3. Concrete long-session moment, with features entering as the reason that moment changes (p = 0.17)
  4. Inversion: open on the chair's least glamorous part (the 12-year warranty, or the mesh weave) and let the comfort case build backward from it (p = 0.10)
  Selection: commit to the strongest angle with p <= 0.20 that satisfies [P1]-[P3], and name the chosen angle.
- [NT1] Opening Anchor: the specific moment, body sensation, or component the description opens inside.
- [NT2] Inductive Trajectory: the order in which the three [P1] features surface, and which observation earns each one.
- [NT3] Cadence & Texture: sentence-length variation plan, the concrete nouns you will use (mesh weave, lumbar plate, seat pan, duty cycle), and the words you will avoid as filler.

### STRUCTURAL RARITY CONTRACT (SC0 — discourse rules for the final draft)
1. Delayed Category: use a specific, non-spoiler headline, and open inside the concrete anchor from [NT1] before naming the product category or its main claim.
2. Evidence Progression: advance the description through physical detail and mechanism (what the lumbar support actually does across a ten-hour day, how the mesh behaves at hour nine) rather than a "cheap chairs vs. this chair" contrast.
3. Practitioner Voice: write as someone who has sat in the chair and inspected it — asymmetric paragraph lengths, specific texture, no institutional "editorial explainer" tone.
4. Open-Loop Close: end on a concrete implication, a diagnostic question about the reader's current chair, or a physical detail that keeps the warranty or the mesh in the reader's mind; the final sentence carries new information rather than restating the opening claim.

### VERIFICATION & TRACEABILITY CONTRACT
- Grounding rule: map every product claim to a [P1] feature and cite the feature identifier in the scaffold; durability, comfort, and health-adjacent statements stay within the literal wording of [P1].
- Feature coverage predicate: all three [P1] features (auto-adjusting lumbar support, breathable mesh, 12-year warranty) appear in the final description, each attached to an observable behavior or component.
- Missing-evidence predicate: when an appealing claim has no [P1] basis, record `UNABLE TO TRACE: [claim]` in the scaffold and leave it out of the draft.
- Specificity predicate: when a phrase is an abstract benefit adjective, rewrite it as a physical noun or a measurable behavior before it enters the draft.

TRACEABILITY SELF-CHECK (before finalizing): confirm that each feature sentence in the description resolves to a [P1] identifier, and that the [NT0] selection, [NT1]-[NT3], and all four SC0 rules are visibly executed in the draft.

### FINAL DELIVERABLE
Present the backstage scaffold (NT0 through NT3, compact), then the finished headline and product description as clean prose, executing the selected low-typicality angle and the SC0 Structural Rarity Contract.
```

### OPTIMIZED RESPONSE

### BACKSTAGE SCAFFOLD

**[NT0] Verbalized Distribution Sampling**
1. Category announcement (“Introducing the ultimate ergonomic chair…”) — p = 0.42  
2. Benefit-stack listing (comfort, breathability, warranty in sequence) — p = 0.31  
3. Concrete long-session moment, with features entering as the reason that moment changes — p = 0.17  
4. Inversion: open on the least glamorous part (warranty or mesh weave) and build backward — p = 0.10  

**Selection:** Angle 3, the concrete long-session moment (p = 0.17). It is the strongest angle at or below 0.20 and lets the features enter as physical explanations rather than a stack of claims.

**[NT1] Opening Anchor:** 2:47 p.m. on a back-to-back call; hips slide forward in the seat pan; the back finds a hard edge behind you; warmth gathers behind the shoulder blades. The product category is withheld until sentence two.

**[NT2] Inductive Trajectory:** posture shift/heat → ergonomic office chair named → auto-adjusting lumbar support as the reason the lower-back gap changes when you lean → hour-nine shirt/back heat → breathable mesh and air moving through its weave → 12-year warranty as the long-service backstop → palm-on-current-seat-pan diagnostic. Feature order: lumbar [P1], mesh [P1], warranty [P1]; category [P1] and 10+ hour days [P1] enter after the opening.

**[NT3] Cadence & Texture:** Long opening with colon/list; short category sentence; mid-length mechanism sentences; blunt warranty sentence; action/diagnostic close. Concrete nouns: seat pan, hard edge, shoulder blades, lumbar support, lower back, mesh, weave, shirt, palm, duty cycle. Avoid filler: ultimate, comfort, cooling, pain relief, durable, premium, solution, vague “support.” Omit “lumbar plate” because it is not in [P1].

**Traceability / self-check:**
- ergonomic office chair → [P1]
- lumbar support auto-adjusts to sitter → [P1]
- breathable mesh → [P1]
- 12-year warranty → [P1]
- engineered for people who work 10+ hour days → [P1]
- `UNABLE TO TRACE: lumbar plate; prevents back pain; keeps you cool all day; frame materials; adjustable armrests; warranty coverage details beyond length.`
- SC0 check: delayed category (yes); evidence progression through physical detail/mechanism (yes); practitioner voice and asymmetric paragraphs (yes); open-loop diagnostic close (yes).

### FINISHED HEADLINE & PRODUCT DESCRIPTION

**When the Call Runs Long**

At 2:47 on a back-to-back Tuesday, you notice it in the seat pan: your hips have slid forward, your back has found the hard edge behind you, and the space behind your shoulder blades has gone warm. This ergonomic office chair is built for that hour.

The lumbar support auto-adjusts to the sitter, so when you lean into a call, it tracks the shift instead of leaving a gap behind your lower back. The back is breathable mesh; at hour nine, air still moves through its weave and across your shirt. The chair carries a 12-year warranty. It is engineered for people who work 10+ hour days—the home-office duty cycle, not the occasional meeting. Before your next call, press your palm to your current chair’s seat pan. If it comes away warm, you know what the mesh is for.

### EVALUATION: TEST 10

- **Word Count**: Baseline `221` words | Optimized `495` words | Ratio `2.24x`
- **Eval Tokens**: Baseline `525` | Optimized `13607`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 3.5      | 5.0       | +1.5  |
| Completeness  | 5.0      | 5.0       | 0     |
| Structure     | 4.5      | 4.0       | -0.5  |
| Actionability | 3.0      | 4.5       | +1.5  |
| Traceability  | 3.0      | 5.0       | +2.0  |
| TOTAL         | 19.0/25  | 23.5/25   | +4.5  |

The optimized response improved accuracy and traceability by grounding every product claim in the provided facts and explicitly marking unsupported embellishments as untraceable. It also gained actionability through a concrete diagnostic close, while the baseline remained more conventional and less specific. The optimized response was penalized on Structure because the large backstage scaffold adds unhelpful bloat to what should be a clean product-description deliverable.

---

## TEST 11: Context File (CLAUDE.md) (Harness | Mode 3 (Agentic Harness [CONTEXT-FILES], Template 11, <150 lines non-inferable only))

### BASELINE RESPONSE

# CLAUDE.md

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Python FastAPI + PostgreSQL** backend service. It exposes a REST API
built on FastAPI, persists data to PostgreSQL, and uses Redis for caching in
performance-sensitive paths (notably billing). The codebase favors a layered
architecture: HTTP concerns live in the API layer, ORM models are isolated, and
business logic is kept in services so it can be tested independently of the web
framework.

## Folder Structure

```
app/
  api/        # FastAPI routers, request/response schemas, dependency wiring
  models/     # SQLAlchemy ORM models and DB-facing types
  services/   # Business logic (e.g., billing.py); framework-agnostic
tests/        # pytest suite; unit tests marked, integration tests separated
scripts/      # Operational helpers (migrate.sh, etc.)
```

Notes:
- **`app/api/`** — Keep handlers thin. Validate input, call a service, return a
  response. Do not put business logic or raw SQL here.
- **`app/models/`** — One module per domain model. Migrations are derived from
  these; changes here require a migration (see below).
- **`app/services/`** — Pure-ish business logic. `app/services/billing.py` is
  the most sensitive module in the repo (see caching rule below).
- **`tests/`** — Mirrors the `app/` layout. Integration tests are tagged with
  the `integration` marker and require a live DB; unit tests must not.

## Coding Conventions

Follow **PEP 8**:

- 4-space indentation, no tabs.
- `snake_case` for functions, methods, and variables; `PascalCase` for classes;
  `UPPER_SNAKE_CASE` for module-level constants.
- Max line length **88** characters (Ruff/Black default). Let the formatter
  settle this — don't hand-wrap.
- Two blank lines between top-level definitions; one blank line between methods.
- Imports grouped stdlib → third-party → first-party, alphabetized within each
  group.
- Prefer explicit typed signatures (this codebase uses type hints throughout);
  avoid `Any` when a real type exists.
- Docstrings for public functions in `app/services/`; they are the contract
  other layers depend on.

Run the formatter/linter before committing:
```bash
ruff format .
ruff check .
```

## Non-Obvious Commands

These are the commands that aren't guessable from `pyproject.toml` and are
required by the workflow:

### Unit tests (the only tests CI runs by default)
```bash
pytest -m "not integration" --reuse-db
```
- `-m "not integration"` — excludes tests that need a live PostgreSQL/Redis.
- `--reuse-db` — reuses the existing test database; without it the suite is
  dramatically slower. If you change model/schema definitions, run once without
  `--reuse-db` (or run the migrations) to rebuild the schema.

### Database migrations — MUST run before committing
```bash
./scripts/migrate.sh check
```
This verifies migration state and detects drift between the models and the
migration history. **Every commit that touches `app/models/` must be preceded by
this command passing.** Do not commit a model change without a corresponding
migration.

### Billing cache keys — DO NOT mutate without bumping `SCHEMA_EPOCH`
`app/services/billing.py` defines `SCHEMA_EPOCH`, which namespaces all Redis
cache keys written by the billing service. **Redis cache keys must never be
mutated without bumping `SCHEMA_EPOCH`.** If you change the shape, key format,
TTL semantics, or serialized payload of anything cached in billing, increment
`SCHEMA_EPOCH` in the same change. Bumping the epoch is what guarantees stale
entries from the previous format are unreachable; skipping it causes silent
wrong-value bugs in production that are painful to trace.

## Definition of Done

Before opening a PR / committing:

1. `ruff format . && ruff check .` pass.
2. `pytest -m "not integration" --reuse-db` passes.
3. If `app/models/` changed: `./scripts/migrate.sh check` passes and a migration
   is included.
4. If billing caching changed: `SCHEMA_EPOCH` bumped and noted in the PR
   description.
```

A few things worth calling out about the choices above:

- The `SCHEMA_EPOCH` rule is stated twice (once in "Non-Obvious Commands" and once in the "Definition of Done") because it's a **silent-corruption** class of bug — emphasis is justified.
- I tied `--reuse-db` to a caveat about schema changes, since that's the trap people hit when they first use that flag.
- I kept the folder-structure notes short but directional ("handlers thin," "services framework-agnostic") so they actually steer code placement rather than just describing it. Adjust the line-length (88) and linter name if you're on a different formatter.

### OPTIMIZED PROMPT

```markdown
# Billing API Agent Operating Contract

Python FastAPI + PostgreSQL service. This file contains only commands and invariants that cannot be inferred by reading the repository. Everything else is discoverable from the source.

## 1. Non-Inferable Execution Commands

- **Unit test run:** `pytest -m "not integration" --reuse-db`
  The marker selector excludes integration tests; `--reuse-db` reuses the existing test database between runs.
- **Migration gate:** `./scripts/migrate.sh check`
  Required before every commit. A non-zero exit blocks the commit.

## 2. Hard Architectural Invariants

- **[I1] Billing cache epoch.** Redis cache keys written by `app/services/billing.py` are versioned by `SCHEMA_EPOCH`. When a change alters the shape, derivation inputs, or TTL semantics of any key emitted from that module, bump `SCHEMA_EPOCH` in the same commit. A reshaped key set emitted under an unchanged epoch is the mechanism that produces mixed-schema reads across deploy windows.
- **[I2] Schema-change coupling.** When a change adds or alters a table, column, or index, the same commit carries its migration and passes `./scripts/migrate.sh check`. A commit that changes models without a corresponding migration is incomplete, regardless of test status.
- **[I3] Test marker boundary.** Tests that require a live PostgreSQL or Redis instance carry `@pytest.mark.integration`. Tests runnable against the reused test database under `--reuse-db` carry no marker, so they execute in the default unit run. When adding a test, choose the marker from the actual dependency it needs.

## 3. Multi-Step Execution & Context-as-a-File

- **Plan sufficiency gate.** When a task touches 3+ files, or changes a route signature, model field, or migration, first write the premises and a verification checklist to `.claude/scratchpad.md`, then edit source files against that checklist.
- **Context hygiene.** Locate code with targeted symbol and grep searches. Persist intermediate findings, failing test output, and the commands already run into `.claude/scratchpad.md` so the active context stays compact across turns.
- **Delta updates.** When revising your own plan or the scratchpad, append corrected entries rather than rewriting the file wholesale, so earlier findings survive.

## 4. Verification Gate (Required Before Claiming Completion)

1. Run `pytest -m "not integration" --reuse-db` against the test files covering every touched module.
2. Run `./scripts/migrate.sh check` whenever the change touches models, migrations, or `app/services/billing.py`.
3. Report each command verbatim with its exit code and a one-line output summary in the final response. Completion claims carry the commands that produced them.
4. When a check cannot run in the current sandbox, or fails for environmental reasons, emit `VERIFICATION BLOCKED: [exact command] -> [error text]` plus the specific unblock step, in place of a success claim.
5. When `[I1]` applies, state the previous and new `SCHEMA_EPOCH` values in the final response so the bump is auditable from the transcript alone.
```

### OPTIMIZED RESPONSE

I've read the operating contract. I understand the binding constraints and will operate within them. Quick confirmation of how I'll apply each section:

**Execution commands (I'll use verbatim):**
- Unit tests: `pytest -m "not integration" --reuse-db`
- Migration gate: `./scripts/migrate.sh check`

**Invariants I'll enforce:**
- **[I1]** If I touch shape/derivation-inputs/TTL of any Redis key emitted from `app/services/billing.py`, I'll bump `SCHEMA_EPOCH` in the same commit and report old→new values.
- **[I2]** Any model change ships with its migration and passes `./scripts/migrate.sh check` in the same commit.
- **[I3]** I'll pick test markers by actual dependency (live PG/Redis → `@pytest.mark.integration`; reusable-DB-only → no marker).

**Multi-step gating:**
- 3+ files, or a route signature / model field / migration change → I'll first write premises + verification checklist to `.claude/scratchpad.md`, then edit against it.
- I'll use targeted symbol/grep searches, persist findings and failing output to the scratchpad, and **append** corrections rather than rewriting.

**Verification before I claim completion:**
1. Run the targeted unit tests.
2. Run `./scripts/migrate.sh check` if models/migrations/`billing.py` were touched.
3. Report each command verbatim with exit code + one-line output summary.
4. If a check can't run or fails environmentally, emit `VERIFICATION BLOCKED: [exact command] -> [error text]` plus the unblock step instead of a success claim.
5. Report `SCHEMA_EPOCH` before/after when `[I1]` applies.

**I have not run anything yet** — no task has been specified, so there is no completion to claim.

What task would you like me to perform? If it touches 3+ files, a route signature, a model field, or a migration, I'll begin by writing the premises and verification checklist to `.claude/scratchpad.md` before editing source.

### EVALUATION: TEST 11

- **Word Count**: Baseline `693` words | Optimized `270` words | Ratio `0.39x`
- **Eval Tokens**: Baseline `1449` | Optimized `582`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 4.5      | 3.5       | -1.0  |
| Completeness  | 5        | 1.5       | -3.5  |
| Structure     | 4.5      | 3         | -1.5  |
| Actionability | 5        | 2.5       | -2.5  |
| Traceability  | 4.5      | 4         | -0.5  |
| TOTAL         | 23.5/25  | 14.5/25   | -9.0  |

The optimized response is more concise and uses explicit invariant IDs and verification gates, but it does not perform the requested task: it only acknowledges an operating contract and never writes the `CLAUDE.md` file, omitting the project overview, folder structure, PEP8 conventions, and the file itself. The baseline is more complete and directly usable, though it includes some inferable bloat and minor invented specifics. The optimized prompt itself is a stronger context file, but the scored optimized response is not the deliverable.

---

## TEST 12: Async Rate Limiter (LRM) (Harness | Mode 3 (LRM & Agentic Harness [HARNESS], Template 12 [V1]-[V3] verification gates))

### BASELINE RESPONSE

# AsyncTokenBucket — FIFO-fair, coroutine-safe rate limiter

```python
from __future__ import annotations

import asyncio
import time
from collections import deque


class AsyncTokenBucket:
    """
    Async token-bucket rate limiter with FIFO fairness.

    Parameters
    ----------
    rate:
        Refill rate in tokens/second. May be fractional (e.g. 0.5 = one
        token every two seconds).
    capacity:
        Maximum tokens the bucket can hold (i.e. maximum burst size).
    initial_tokens:
        Starting balance; defaults to ``capacity`` (bucket starts full).

    Concurrency model
    -----------------
    * All state mutation happens under ``self._lock`` (an ``asyncio.Lock``).
    * Blocked callers are enqueued in **FIFO order**; only the head of the
      queue actively sleeps on a refill timer, everyone else sleeps on a
      per-waiter ``asyncio.Event`` until they bubble to the front.
    * When the head is granted or times out, the next waiter is woken
      explicitly — no thundering herd, no starvation, and no two callers
      can ever observe/modify the bucket concurrently.

    The limiter is safe for any number of concurrent **coroutines within a
    single event loop**.  It is *not* safe to share one instance across
    multiple event loops/threads — create one bucket per loop instead.
    """

    __slots__ = (
        "_rate", "_capacity", "_tokens",
        "_last_refill", "_lock", "_waiters",
    )

    def __init__(
        self,
        rate: float,
        capacity: int,
        *,
        initial_tokens: float | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be > 0")
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        init = float(capacity) if initial_tokens is None else float(initial_tokens)
        if not 0.0 <= init <= capacity:
            raise ValueError("initial_tokens must be in [0, capacity]")

        self._rate: float = float(rate)
        self._capacity: float = float(capacity)
        self._tokens: float = init
        self._last_refill: float = time.monotonic()
        self._lock: asyncio.Lock = asyncio.Lock()
        self._waiters: deque[asyncio.Event] = deque()

    # ------------------------------------------------------------------ #
    # Internal helpers (all require the lock to be held)
    # ------------------------------------------------------------------ #

    def _refill(self, now: float) -> None:
        elapsed = now - self._last_refill
        self._last_refill = now
        if elapsed > 0 and self._tokens < self._capacity:
            self._tokens = min(self._capacity,
                               self._tokens + elapsed * self._rate)

    def _wake_head(self) -> None:
        """Wake the current head-of-queue (if any). Must hold the lock."""
        if self._waiters:
            self._waiters[0].set()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    async def acquire(self, tokens: int, timeout: float | None = None) -> bool:
        """
        Try to consume ``tokens`` tokens.

        Blocks until either the request can be granted or ``timeout``
        seconds elapse (``None`` = wait forever).

        Returns ``True`` if granted, ``False`` on timeout — or immediately
        ``False`` if the request can *never* be satisfied because
        ``tokens > capacity``.
        """
        if tokens <= 0:
            raise ValueError("tokens must be > 0")
        if tokens > self._capacity:
            return False
        if timeout is not None and timeout < 0:
            return False

        deadline = None if timeout is None else time.monotonic() + timeout

        # --- Fast path: no queue, enough tokens -> no waiting at all. ---
        async with self._lock:
            now = time.monotonic()
            self._refill(now)
            if not self._waiters and self._tokens >= tokens:
                self._tokens -= tokens
                return True
            if deadline is not None and now >= deadline:
                return False
            event = asyncio.Event()
            self._waiters.append(event)

        try:
            while True:
                async with self._lock:
                    now = time.monotonic()
                    self._refill(now)

                    if self._waiters and self._waiters[0] is event:
                        # We are the head — we get first crack at tokens.
                        if self._tokens >= tokens:
                            self._tokens -= tokens
                            self._waiters.popleft()
                            self._wake_head()
                            return True
                        if deadline is not None and now >= deadline:
                            self._waiters.popleft()
                            self._wake_head()
                            return False
                        wait: float | None = (tokens - self._tokens) / self._rate
                        if deadline is not None:
                            wait = min(wait, deadline - now)
                    else:
                        # Not the head — sleep until we're woken.
                        if deadline is not None and now >= deadline:
                            try:
                                self._waiters.remove(event)
                            except ValueError:
                                pass
                            return False
                        wait = None

                try:
                    if wait is not None:
                        await asyncio.wait_for(event.wait(), wait)
                    elif deadline is not None:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            continue
                        await asyncio.wait_for(event.wait(), remaining)
                    else:
                        await event.wait()
                except asyncio.TimeoutError:
                    pass
                finally:
                    event.clear()

        except BaseException:
            # Cancellation / unexpected error: leave the queue in a
            # consistent state so downstream waiters are not stranded.
            async with self._lock:
                was_head = bool(self._waiters) and self._waiters[0] is event
                try:
                    self._waiters.remove(event)
                except ValueError:
                    pass
                if was_head:
                    self._wake_head()
            raise

    async def try_acquire(self, tokens: int) -> bool:
        """Non-blocking variant: one attempt, no waiting."""
        return await self.acquire(tokens, timeout=0)
```

## Why this is race-free with concurrent waiters

| Concern | How it's handled |
|---|---|
| **State mutation** | Every read/write of `_tokens`, `_last_refill`, `_waiters` is done under `self._lock`. Refill is computed **lazily** from `time.monotonic()` deltas, so no background task is required. |
| **Thundering herd** | Only the **head** of the queue ever sleeps on the refill timer. Non-heads sleep on their own `asyncio.Event`, woken exactly once by `_wake_head()` when they reach the front. |
| **Lost wake-ups** | The `finally: event.clear()` runs *after* the locked re-check, and any spurious wake-up simply re-enters the loop and re-validates under the lock — no signal is required to be observed. |
| **Starvation** | Strict FIFO ordering; a later acquirer cannot jump ahead of an earlier one. |
| **Timeouts** | Head recomputes `min(refill_wait, time_to_deadline)`; non-heads use `asyncio.wait_for` and re-confirm under the lock before returning `False`, so a caller that is about to be granted isn't spuriously rejected. |
| **Cancellation** | A `BaseException` handler removes the waiter and re-wakes the new head, so cancelling a blocked `acquire()` cannot deadlock the queue. |
| **Fractional rates** | `_tokens` is a `float`; refill does `elapsed * rate`, so `rate=0.5` correctly yields one token every 2 s. |
| **Bursts** | `_refill` caps at `_capacity`, so bursts up to `capacity` are permitted after idle periods. |

## Quick example

```python
async def main():
    bucket = AsyncTokenBucket(rate=2.0, capacity=5)   # 2 tok/s, burst 5

    assert await bucket.acquire(3)                    # instant (bucket full)
    assert not await bucket.try_acquire(5)            # only 2 left

    t0 = time.monotonic()
    ok = await bucket.acquire(4, timeout=5)           # waits ~1 s
    assert ok and 0.9 <= time.monotonic() - t0 <= 1.2

    # Many concurrent waiters are served in FIFO order:
    results = await asyncio.gather(
        *(bucket.acquire(1, timeout=10) for _ in range(10))
    )
    assert all(results)
```

### OPTIMIZED PROMPT

```markdown
The verification protocol for a concurrency-safe asyncio resource limiter requires grounding every deliverable in declared premises and post-condition gates. Perform all path exploration, interleaving analysis, and edge-case search in your internal reasoning, and emit only the verified certificate and deliverable below.

### PREMISES
- [P1] Public interface (exact, must match):
  - `class AsyncTokenBucket`
  - `__init__(self, rate: float, capacity: float, *, time_func=...)` — `rate` = tokens added per second (fractional allowed), `capacity` = maximum stored tokens, `time_func` = injectable monotonic clock defaulting to `time.monotonic`.
  - `async def acquire(self, tokens: int = 1, timeout: float | None = None) -> bool`
  - Argument domain: `rate > 0`, `capacity > 0`, `0 < tokens <= capacity`. Values outside the domain raise `ValueError` at call time.
- [P2] Behavioral invariants to establish:
  - Refill is computed lazily from elapsed `time_func()` time, never by a background task: `stored = min(capacity, stored + elapsed * rate)`.
  - `acquire` returns `True` only when the requested tokens are deducted from storage within the same atomic state transition that observed them.
  - `timeout=None` waits until the request can be satisfied; `timeout >= 0` returns `False` when capacity is unavailable at or after that deadline; `timeout <= 0` performs exactly one non-blocking attempt.
  - Requests are granted in arrival order among currently-unresolvable waiters (no barging ahead of an already-queued larger request that would starve).
  - Refund path: a request that is cancelled or times out releases every reservation it holds before control returns.
- [P3] Environment and execution contract:
  - Python 3.11+, standard library `asyncio` only, no third-party dependencies, no threads, no `time.sleep`, no busy-wait polling loops.
  - All mutations of bucket state occur in synchronous, non-`await` sections so the event loop cannot interleave them.
  - Verification commands to run and report verbatim:
    - `python -m pytest tests/test_async_token_bucket.py -q`
    - `python -m ruff check async_token_bucket.py tests/test_async_token_bucket.py`
    - `python -m mypy async_token_bucket.py`
- [P4] Unverified inputs: event-loop implementation details beyond CPython 3.11 `asyncio`, multi-process or multi-threaded deployment, and cross-loop usage are outside this contract; mark such concerns `OUT OF SCOPE` rather than speculating.

### VERIFICATION GATES
Emit one line per gate, in this exact form: `[Vn] <invariant>: <SATISFIED | VIOLATED | UNTESTABLE> -> Evidence: <exact function/line reference from your deliverable, or the specific failing interleaving>`.

- [V1] Mutual exclusion of state transitions: Between the read of stored tokens, the refill computation, and the deduction, the code contains no `await`; every concurrent `acquire` either observes a fully committed state or re-evaluates after a wakeup inside a loop.
- [V2] Accounting conservation: Across arbitrary interleavings and boundary inputs (`tokens == capacity`, `tokens` just above remaining capacity, zero elapsed time, very large elapsed time), stored tokens stay within `[0, capacity]`, total granted tokens never exceed `capacity + rate * elapsed`, and no grant occurs without a matching deduction.
- [V3] Waiter lifecycle safety: Every queued waiter is resolved by exactly one of three terminal states — granted, timed out, or cancelled — and each path releases its reservation and hands off to the next eligible waiter, so no wakeup is lost and no waiter blocks past its deadline.

Gate evidence rules:
- When a gate depends on behavior you cannot demonstrate from the delivered code plus an executable test, record `UNTESTABLE` and name the exact missing test or artifact.
- When a boundary input contradicts an invariant in [P2], add a dedicated gate line recording the counterexample, even if the overall deliverable passes.

### FORMAL CONCLUSION & DELIVERABLE
- Disposition: one sentence per gate, citing `[V1]`, `[V2]`, `[V3]` and the `[P1]`/`[P2]` clauses they satisfy.
- Deliverable, complete and copy-pasteable:
  1. `async_token_bucket.py` — full implementation with docstrings, type annotations, and a module-level comment naming the single synchronization primitive used and why it preserves [V1].
  2. `tests/test_async_token_bucket.py` — pytest-asyncio-free tests built on `asyncio.run`, including: burst exhaustion and recovery, fractional refill over an injected fake clock, N concurrent waiters resolving without over-grant, timeout returning `False` at the deadline, cancellation of a queued waiter leaving state consistent, and an assertion that stored tokens never leave `[0, capacity]` after each scenario. Each test names the gate it exercises.
  3. The three verification commands from [P3] with their observed exit codes and output summaries; when a command cannot run in this environment, report `VERIFICATION BLOCKED: <command + error>`.

TRACEABILITY SELF-CHECK (complete before emitting): confirm that every claim in the Disposition cites at least one `[V]` identifier backed by a named function or test in the Deliverable. When a claim has no supporting identifier, either add the corresponding test or remove the claim so zero orphaned assertions remain.
```

### OPTIMIZED RESPONSE

[V1] Mutual exclusion of state transitions: SATISFIED -> Evidence: `async_token_bucket.py::AsyncTokenBucket.acquire` and `::AsyncTokenBucket._drain_locked`; all refill/read/deduct/queue mutations occur while holding `asyncio.Condition`, and the check `self._stored >= waiter.tokens` through `self._stored -= waiter.tokens` contains no `await`. Tests: `tests/test_async_token_bucket.py::test_burst_exhaustion_and_recovery`, `::test_concurrent_waiters_fifo_no_overgrant`.
[V2] Accounting conservation: SATISFIED -> Evidence: `async_token_bucket.py::AsyncTokenBucket._refill_locked` clamps with `min(self.capacity, ...)`, `::AsyncTokenBucket._drain_locked` deducts only after the availability check, and `::AsyncTokenBucket.acquire` refunds a granted cancellation in the `CancelledError` handler. Tests: `::test_burst_exhaustion_and_recovery`, `::test_fractional_refill_with_fake_clock`, `::test_concurrent_waiters_fifo_no_overgrant`.
[V3] Waiter lifecycle safety: SATISFIED -> Evidence: `async_token_bucket.py::AsyncTokenBucket._drain_locked` assigns terminal `GRANTED`/`TIMEOUT` states while popping FIFO waiters, and `::AsyncTokenBucket.acquire` removes PENDING or refunds GRANTED waiters on cancellation and returns `False` on elapsed deadline. Tests: `::test_concurrent_waiters_fifo_no_overgrant`, `::test_timeout_returns_false_at_deadline`, `::test_cancellation_of_queued_waiter_leaves_consistent_state`.

## FORMAL CONCLUSION & DELIVERABLE

Disposition: [V1] SATISFIED, satisfying [P2] atomic deduction and [P3] synchronous state mutation via `AsyncTokenBucket._drain_locked` under `asyncio.Condition`. [V2] SATISFIED, satisfying [P2] lazy refill/accounting via `AsyncTokenBucket._refill_locked` and the burst/fractional/concurrent tests. [V3] SATISFIED, satisfying [P2] FIFO/timeout/cancellation via `AsyncTokenBucket.acquire` and the concurrent/timeout/cancellation tests.

### 1. `async_token_bucket.py`

```python
"""Async token bucket with FIFO waiters and injectable monotonic clock."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto

# Synchronization primitive: asyncio.Condition. It guards all bucket state.
# Every state read/refill/deduction/queue mutation is performed while holding
# the Condition lock and contains no await between observation and commit,
# which preserves [V1].
class _WaiterState(Enum):
    PENDING = auto()
    GRANTED = auto()
    TIMEOUT = auto()
    CANCELLED = auto()


@dataclass
class _Waiter:
    tokens: int
    deadline: float | None
    state: _WaiterState = _WaiterState.PENDING


class AsyncTokenBucket:
    """A concurrency-safe asyncio token bucket.

    The bucket starts full. Tokens refill lazily from ``time_func`` whenever
    bucket state is touched. Waiters are served strictly FIFO.
    """

    def __init__(
        self,
        rate: float,
        capacity: float,
        *,
        time_func: Callable[[], float] = time.monotonic,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be > 0")
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self.rate = float(rate)
        self.capacity = float(capacity)
        self._time_func = time_func
        self._stored = self.capacity
        self._last = self._time_func()
        self._waiters: deque[_Waiter] = deque()
        self._condition: asyncio.Condition = asyncio.Condition()

    def _refill_locked(self) -> None:
        now = self._time_func()
        elapsed = now - self._last
        if elapsed < 0.0:
            elapsed = 0.0
        if elapsed > 0.0:
            self._stored = min(
                self.capacity, self._stored + elapsed * self.rate
            )
        self._last = now

    def _remove_waiter_locked(self, waiter: _Waiter) -> None:
        try:
            self._waiters.remove(waiter)
        except ValueError:
            pass

    def _drain_locked(self) -> int:
        """Grant or time out waiters from the head while possible.

        Returns the number of waiter state changes. Must be called with the
        condition lock held.
        """
        self._refill_locked()
        now = asyncio.get_running_loop().time()
        changed = 0
        while self._waiters:
            waiter = self._waiters[0]
            if waiter.state is not _WaiterState.PENDING:
                self._waiters.popleft()
                changed += 1
                continue
            if waiter.deadline is not None and now > waiter.deadline:
                self._waiters.popleft()
                waiter.state = _WaiterState.TIMEOUT
                changed += 1
                continue
            if self._stored >= waiter.tokens:
                self._stored -= waiter.tokens
                waiter.state = _WaiterState.GRANTED
                self._waiters.popleft()
                changed += 1
            else:
                break
        return changed

    def _compute_wait_delay_locked(self) -> float | None:
        if not self._waiters:
            return None
        head = self._waiters[0]
        if head.state is not _WaiterState.PENDING:
            return 0.0
        needed = head.tokens - self._stored
        if needed <= 0:
            return 0.0
        return needed / self.rate

    async def acquire(
        self, tokens: int = 1, timeout: float | None = None
    ) -> bool:
        """Acquire ``tokens`` from the bucket.

        Raises ValueError if ``tokens`` is outside ``(0, capacity]``.
        """
        if not isinstance(tokens, int) or isinstance(tokens, bool):
            raise ValueError("tokens must be an int")
        if tokens <= 0:
            raise ValueError("tokens must be > 0")
        if tokens > self.capacity:
            raise ValueError("tokens must be <= capacity")

        loop = asyncio.get_running_loop()
        if timeout is not None and timeout <= 0:
            async with self._condition:
                self._refill_locked()
                if not self._waiters and self._stored >= tokens:
                    self._stored -= tokens
                    return True
                return False

        deadline = None if timeout is None else loop.time() + timeout
        waiter = _Waiter(tokens, deadline)
        try:
            async with self._condition:
                self._refill_locked()
                if not self._waiters and self._stored >= tokens:
                    self._stored -= tokens
                    return True
                self._waiters.append(waiter)
                changed = self._drain_locked()
                if changed:
                    self._condition.notify_all()
                if waiter.state is _WaiterState.GRANTED:
                    return True
                if waiter.state is _WaiterState.TIMEOUT:
                    return False

            while True:
                async with self._condition:
                    self._refill_locked()
                    changed = self._drain_locked()
                    if changed:
                        self._condition.notify_all()
                    if waiter.state is _WaiterState.GRANTED:
                        return True
                    if waiter.state in (
                        _WaiterState.TIMEOUT,
                        _WaiterState.CANCELLED,
                    ):
                        return False
                    now = loop.time()
                    remaining = (
                        None if deadline is None else deadline - now
                    )
                    if remaining is not None and remaining <= 0.0:
                        self._remove_waiter_locked(waiter)
                        waiter.state = _WaiterState.TIMEOUT
                        self._drain_locked()
                        self._condition.notify_all()
                        return False
                    delay = self._compute_wait_delay_locked()
                    wait_timeout = remaining
                    if delay is not None:
                        wait_timeout = (
                            delay
                            if wait_timeout is None
                            else min(wait_timeout, delay)
                        )
                    if wait_timeout is not None and wait_timeout <= 0.0:
                        await asyncio.sleep(0)
                        continue
                    try:
                        if wait_timeout is None:
                            await self._condition.wait()
                        else:
                            await asyncio.wait_for(
                                self._condition.wait(),
                                timeout=wait_timeout,
                            )
                    except TimeoutError:
                        pass
        except asyncio.CancelledError:
            async with self._condition:
                self._refill_locked()
                if waiter.state is _WaiterState.GRANTED:
                    self._stored = min(
                        self.capacity, self._stored + waiter.tokens
                    )
                    waiter.state = _WaiterState.CANCELLED
                elif waiter.state is _WaiterState.PENDING:
                    self._remove_waiter_locked(waiter)
                    waiter.state = _WaiterState.CANCELLED
                self._drain_locked()
                self._condition.notify_all()
            raise
```

### 2. `tests/test_async_token_bucket.py`

```python
"""Tests for async_token_bucket. Gate exercised is named per test."""

from __future__ import annotations

import asyncio
import time

from async_token_bucket import AsyncTokenBucket


class FakeClock:
    def __init__(self) -> None:
        self._now = 0.0

    def time(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


def _assert_bounds(bucket: AsyncTokenBucket) -> None:
    assert 0.0 <= bucket._stored <= bucket.capacity


def test_burst_exhaustion_and_recovery() -> None:
    """[V1], [V2]: burst exhaustion, nonblocking failure, recovery."""
    clock = FakeClock()
    bucket = AsyncTokenBucket(
        rate=2.0, capacity=5.0, time_func=clock.time
    )

    async def scenario() -> None:
        assert await bucket.acquire(5) is True
        assert await bucket.acquire(1, timeout=0) is False
        clock.advance(0.5)
        assert await bucket.acquire(1, timeout=0) is True
        assert await bucket.acquire(1, timeout=0) is False
        _assert_bounds(bucket)

    asyncio.run(scenario())


def test_fractional_refill_with_fake_clock() -> None:
    """[V2]: fractional lazy refill over an injected fake clock."""
    clock = FakeClock()
    bucket = AsyncTokenBucket(
        rate=0.5, capacity=2.0, time_func=clock.time
    )

    async def scenario() -> None:
        assert await bucket.acquire(2) is True
        clock.advance(1.0)
        assert await bucket.acquire(1, timeout=0) is False
        clock.advance(1.0)
        assert await bucket.acquire(1, timeout=0) is True
        _assert_bounds(bucket)

    asyncio.run(scenario())


def test_concurrent_waiters_fifo_no_overgrant() -> None:
    """[V1], [V2], [V3]: concurrent waiters resolve without over-grant."""
    async def scenario() -> None:
        bucket = AsyncTokenBucket(rate=1000.0, capacity=5.0)
        assert await bucket.acquire(5) is True
        results = await asyncio.wait_for(
            asyncio.gather(*(bucket.acquire(1) for _ in range(5))),
            timeout=1.0,
        )
        assert results == [True] * 5
        _assert_bounds(bucket)

    asyncio.run(scenario())


def test_timeout_returns_false_at_deadline() -> None:
    """[V3]: timeout returns False when capacity is unavailable."""
    async def scenario() -> None:
        bucket = AsyncTokenBucket(rate=0.001, capacity=1.0)
        assert await bucket.acquire(1) is True
        started = time.monotonic()
        result = await bucket.acquire(1, timeout=0.02)
        elapsed = time.monotonic() - started
        assert result is False
        assert elapsed >= 0.01
        _assert_bounds(bucket)

    asyncio.run(scenario())


def test_cancellation_of_queued_waiter_leaves_consistent_state() -> None:
    """[V3]: cancelling a queued waiter removes it and preserves bounds."""
    async def scenario() -> None:
        bucket = AsyncTokenBucket(rate=0.001, capacity=1.0)
        assert await bucket.acquire(1) is True
        waiter = asyncio.create_task(bucket.acquire(1))
        await asyncio.sleep(0.01)
        assert len(bucket._waiters) == 1
        waiter.cancel()
        try:
            await waiter
        except asyncio.CancelledError:
            pass
        assert len(bucket._waiters) == 0
        assert await bucket.acquire(1, timeout=0) is False
        _assert_bounds(bucket)

    asyncio.run(scenario())
```

### 3. Verification commands

```text
VERIFICATION BLOCKED: python -m pytest tests/test_async_token_bucket.py -q (no execution environment available in this chat)
VERIFICATION BLOCKED: python -m ruff check async_token_bucket.py tests/test_async_token_bucket.py (no execution environment available in this chat)
VERIFICATION BLOCKED: python -m mypy async_token_bucket.py (no execution environment available in this chat)
```

### EVALUATION: TEST 12

- **Word Count**: Baseline `984` words | Optimized `1152` words | Ratio `1.17x`
- **Eval Tokens**: Baseline `22485` | Optimized `40247`

| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      | 5.0      | 4.0       | -1.0  |
| Completeness  | 5.0      | 4.5       | -0.5  |
| Structure     | 5.0      | 5.0       | 0.0   |
| Actionability | 5.0      | 4.5       | -0.5  |
| Traceability  | 4.5      | 3.0       | -1.5  |
| TOTAL         | 24.5/25  | 21.0/25   | -3.5  |

The optimized response improves the formal structure and adds the requested exact interface, tests, and verification gates, but it overclaims gate satisfaction because the cited tests do not cover refund-after-grant cancellation, actual FIFO order, or timeout-to-next-waiter handoff. It also introduces minor inconsistencies around the injected clock versus event-loop deadlines and a nonblocking path that does not drain already-queued waiters. The baseline remains a concise, correct implementation for the original task with strong traceability to its concurrency concerns.

---

## FINAL REPORT

### Summary Table

| Test | Domain | Task Type | Mode | Baseline /25 | Optimized /25 | Delta | Words (B/O/Ratio) | Winner |
|------|--------|-----------|------|--------------|---------------|-------|-------------------|--------|
| 1 | Code Review | Accuracy | Mode 1 | 23.0/25 | 24.0/25 | +1 | 151/2909 (19.26x) | Optimized |
| 2 | Financial Analysis | Accuracy | Mode 1 | 21.0/25 | 24.0/25 | +3 | 402/2580 (6.42x) | Optimized |
| 3 | Medical Reasoning | Accuracy | Mode 1 | 21.5/25 | 21.5/25 | +0 | 165/3054 (18.51x) | Tie |
| 4 | Legal Analysis | Accuracy | Mode 1 | 22.0/25 | 16.0/25 | -6 | 667/1648 (2.47x) | Baseline |
| 5 | Research Synthesis | Mixed | Mode 1 | 22.0/25 | 24.0/25 | +2 | 505/1732 (3.43x) | Optimized |
| 6 | Business Decision | Mixed | Mode 1 | 21.0/25 | 21.5/25 | +0.5 | 520/2984 (5.74x) | Optimized |
| 7 | Compliance Check | Accuracy | Mode 1 | 19.5/25 | 23.5/25 | +4 | 400/2397 (5.99x) | Optimized |
| 8 | Document Analysis | Mixed | Mode 1 | 22.5/25 | 24.0/25 | +1.5 | 399/1677 (4.2x) | Optimized |
| 9 | Comparative Analysis | Mixed | Mode 2 | 24.5/25 | 21.5/25 | -3 | 853/1056 (1.24x) | Baseline |
| 10 | Creative Brief | Creative | Mode 4 | 19.0/25 | 23.5/25 | +4.5 | 221/495 (2.24x) | Optimized |
| 11 | Context File (CLAUDE.md) | Harness | Mode 3 | 23.5/25 | 14.5/25 | -9 | 693/270 (0.39x) | Baseline |
| 12 | Async Rate Limiter (LRM) | Harness | Mode 3 | 24.5/25 | 21.0/25 | -3.5 | 984/1152 (1.17x) | Baseline |
| **AVG** | **ALL (12 tests)** | - | - | **22.0/25** | **21.58/25** | **-0.42** | **Avg 5.92x** | **7W-1T-4L** |

### Analysis Sections

## 1. Overall Verdict

v4.0 is a conditional, non-net-positive release. It wins 7 tests, ties 1, and loses 4, but the average score falls from 22.00 to 21.58, a delta of -0.42. The distribution is highly polarized: the seven wins plus one tie produce +16.5 total points, while the four losses produce -21.5 total points, for a net of -5.0. The typical case is mildly positive, but the tail risk is too large for default deployment. v4.0 is useful as a selective enhancement for compliance, creative briefs, financial analysis, research synthesis, and document analysis; it is harmful for harness and context-file work, legal analysis, comparative analysis on a strong baseline, and async code harness tasks. Verdict: keep v4.0 as an opt-in mode family, not as a universal replacement for the baseline prompt.

## 2. Where It Helped Most

The largest raw gains were Test 7 Compliance, +4.0, and Test 10 Creative Brief, +4.5. Test 10 is also the best value case in the entire suite: 19.0 to 23.5 at only 2.24x words. Test 2 Financial Analysis gained +3.0, Test 5 Research Synthesis gained +2.0, and Test 8 Document Analysis gained +1.5. Test 1 Code Review gained +1.0, and Test 6 Business Decision gained +0.5. The common pattern is a low-to-mid baseline task where richer structure, broader coverage, or explicit checklists helped. The best value wins are Test 10 at 2.24x, Test 5 at 3.43x, and Test 8 at 4.20x. Test 7 and Test 2 produced solid gains but at roughly 6x word expansion.

## 3. Where It Helped Least or Hurt

The worst regression is Test 11 Context File, 23.5 to 14.5, a loss of 9.0, with optimized output only 270 words versus 693 baseline words, a ratio of 0.39x. This is a severe overcompression and content-loss failure. Test 4 Legal Analysis lost 6.0 points, 22.0 to 16.0, despite using 2.47x words. Test 12 Async Rate Limiter lost 3.5 points, 24.5 to 21.0, at 1.17x words. Test 9 Comparative Analysis lost 3.0 points, 24.5 to 21.5, at 1.24x words. Test 3 Medical Reasoning tied at 21.5 but consumed 18.51x words, so it provided zero score gain at extreme cost. Test 1 gained only +1.0 at 19.26x words, and Test 6 gained only +0.5 at 5.74x. The four actual losses account for essentially all of the negative average.

## 4. v4.0 Mode Evaluation

Test 9, Mode 2, is the only Max versus Lite proxy in the table. The optimized run lost 3.0 points at 1.24x words. Since there is no separate Max and Lite score, this is evidence against an expansive Max-style pass for comparative analysis, not a clean Max versus Lite measurement. A Lite or baseline behavior wins on this case.

Harness Mode 3 on Tests 11 and 12 is clearly negative. Test 11 lost 9.0 points with extreme compression at 0.39x, and Test 12 lost 3.5 points at 1.17x. Across the two harness tests, Mode 3 produced -12.5 total points. This mode should not be enabled as written for context files or harness artifacts.

Creative v2, Mode 4, is the strongest mode-specific result. Test 10 improved from 19.0 to 23.5, a gain of +4.5, at 2.24x words. This is the best value result in the suite. Keep Creative v2, but isolate it to creative briefs and do not let its expansion behavior leak into exact-content or harness tasks.

## 5. Accuracy vs. Mixed vs. Creative vs. Harness

Accuracy tests 1, 2, 3, 4, and 7 produce a net +2.0, an average delta of +0.4, with 3 wins, 1 tie, and 1 loss. This category is positive overall but is not uniformly safe because Legal Analysis lost 6.0 points.

Mixed tests 5, 6, 8, and 9 produce a net +1.0, an average delta of +0.25, with 3 wins and 1 loss. This category is also positive overall but is undermined by the Comparative Analysis loss.

Creative Test 10 produces +4.5, the strongest per-test category result. Harness Tests 11 and 12 produce -12.5 total, an average delta of -6.25, with 0 wins and 2 losses. Outside harness, the suite produces +7.5 across 10 tests, an average of +0.75, but harness alone reverses the overall verdict. The category ranking by robustness is Creative first, Accuracy second, Mixed third, Harness last.

## 6. Traceability Specifically

The summary table does not include a separate traceability score, so traceability must be inferred from task type and score behavior. The indirect evidence is mixed. Compliance and document analysis improved, which suggests that structured checklists and broader coverage may have improved auditability. Legal Analysis lost 6.0 points despite expanding to 2.47x words, which suggests that added length did not preserve the right authorities, constraints, or reasoning chain. Test 11 lost 9.0 points at 0.39x words, a strong signal that required context was deleted or compressed away. Test 3 tied while expanding to 18.51x words, which shows that massive expansion alone did not improve medical traceability or accuracy. v4.0 therefore improves traceability in some checklist-friendly tasks but fails to guarantee it in exact-content and high-stakes tasks. v4.1 should measure traceability directly instead of inferring it from score or length.

## 7. Token Cost vs. Value

The average word ratio is 5.92x, and the overall score delta is -0.42. That is poor aggregate value. Outside harness, the average ratio rises to about 6.95x for a +0.75 average gain. Harness averages only 0.78x, but it loses heavily, so low token count is not automatically good. The best value case is Test 10, +4.5 at 2.24x. Good value cases are Test 5, +2.0 at 3.43x, and Test 8, +1.5 at 4.20x. Test 7, +4.0 at 5.99x, is a real gain but costly. Test 2, +3.0 at 6.42x, is acceptable but expensive. The worst value cases are Test 1, +1.0 at 19.26x, and Test 3, 0.0 at 18.51x. Test 11 is also a cost-value failure in the opposite direction: aggressive compression saved words but destroyed 9.0 points.

## 8. Failure Modes Observed

The main failure modes are:

1. Overcompression and content deletion in exact-content tasks. Test 11 is the clearest case: shorter output, much lower score.
2. Overexpansion without proportional accuracy gain. Test 3 and Test 1 show extreme ratios with tie or marginal gain.
3. Constraint and artifact fidelity loss. Test 4 and Test 12 lost points despite moderate expansion, suggesting missed legal requirements or harness constraints.
4. Mode and task mismatch. Mode 3 failed on harness tasks, and Mode 2 failed on comparative analysis.
5. High-baseline regression. Tests 9, 11, and 12 started at 23.5 to 24.5 and regressed, which indicates that v4.0 can damage already strong baseline prompts.
6. No cost-aware stopping rule. v4.0 expanded heavily in several cases without checking whether the added words improved the score.
7. Traceability not guaranteed by length. Legal Analysis added words but lost accuracy, while Context File removed words and lost accuracy.

## 9. Recommendations for v4.1 Skill Improvement

1. Add a hard mode router. Detect harness, context-file, legal, and exact-artifact tasks and default to conservative preservation or baseline behavior.
2. Add preservation gates for exact-content tasks. For CLAUDE.md and similar files, require no deletion of original instructions, no summarization of constraints, and no replacement of exact wording unless explicitly requested.
3. Add artifact-fidelity checks for code and harness tasks. For the async rate limiter, require preservation of API contracts, concurrency invariants, test behavior, and error handling.
4. Add token budgets by mode. Creative can target 2x to 3x, accuracy and mixed can target 3x to 6x, harness should stay near 1.2x with content preservation, and any ratio above 8x should require a verified score gain.
5. Add traceability blocks for legal, compliance, financial, research, and document tasks. Require source anchors, constraint mapping, and a checklist that separates facts, assumptions, and conclusions.
6. Keep Creative v2 isolated. Test 10 shows strong value, but the mode should not be applied to legal, harness, or exact-content work.
7. Redesign Mode 2 for comparative analysis. Use explicit comparison dimensions, evidence mapping, and a balance check instead of general expansion.
8. Redesign Mode 3 for harness tasks. Treat it as a preservation mode, not a rewriting mode.
9. Add regression tests for high-baseline prompts. Any prompt already scoring 23.5 or higher should require a no-regression check before v4.1 output is accepted.
10. Add evaluation metrics for traceability, constraint coverage, artifact fidelity, and token efficiency. The current aggregate score hides the exact failure modes that caused the largest losses.
