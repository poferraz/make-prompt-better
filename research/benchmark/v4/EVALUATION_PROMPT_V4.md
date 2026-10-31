# SKILL EVALUATION PROMPT: make-prompt-better (v4.0 Benchmark Suite)

You are conducting a controlled evaluation of the prompt optimization skill `make-prompt-better` (v4.0). The skill improves LLM output quality by routing prompts across **4 Certificate Modes** (`Max`, `Lite`, `LRM / Agentic Harness`, and `Creative & Divergent v2`) grounded in 11 peer-reviewed papers (2025-2026). Your job is to test whether these claims hold, measure the improvement (or degradation) across 12 standardized tasks, and produce an honest, quantitative report.

## YOUR ROLE

You are an independent evaluator. You have no stake in whether the skill performs well or poorly. Your job is to measure what actually happens, report it accurately, and flag anything that does not work as claimed. If the skill makes outputs worse, say so. If it makes them better, quantify by how much. If the results are mixed, explain the pattern.

## THE SKILL BEING TESTED

The skill is in your working directory (`/Users/poferraz/Documents/Development/active/make-prompt-better`). Read these files before starting:

### Required (read all three before proceeding)

1. `make-prompt-better/SKILL.md` (the core v4.0 optimization methodology, 6-step process, and 4 Certificate Modes)
2. `make-prompt-better/references/domain-templates.md` (12 domain-specific certificate templates)
3. `make-prompt-better/references/research-principles.md` (11 research papers and their empirical constraints)

### Recommended (read for deeper understanding)

4. `make-prompt-better/references/examples.md` (9 before/after transformations showing all 4 modes in action)
5. `docs/tradeoffs.md` (cost/benefit analysis with paper-backed numbers and failure modes)
6. `docs/when-to-use.md` (decision framework for Mode 1 Max, Mode 2 Lite, Mode 3 Harness, Mode 4 Creative v2, and Bypass)

Read all three required files now. Understand the methodology before proceeding.

## EVALUATION DESIGN

### The Core Test

For each test case, you will produce TWO outputs from the SAME task:

- **Baseline**: Answer the task using the original prompt exactly as written, with no optimization.
- **Optimized**: Apply the `make-prompt-better` v4.0 skill to rewrite the prompt first (selecting the optimal Certificate Mode and Domain Template), then answer using the optimized prompt.

Both outputs must be generated with equal effort. Do not sandbag the baseline or over-invest in the optimized version. The point is to test the PROMPT STRUCTURE, not your willingness to try harder.

### Test Cases (12 total: Tests 1-10 longitudinal + Tests 11-12 v4.0 Harness/LRM)

Complete ALL 12 test cases. Tests 1-10 match the v1.0 benchmark verbatim for longitudinal comparison; Tests 9-12 additionally evaluate v4.0's new Certificate Modes (Mode 2 Lite, Mode 4 Creative v2, and Mode 3 Agentic Harness / LRM Verification Gates).

---

**TEST 1: Code Review (Accuracy task | Target Mode: Mode 1 Max Certificate, Template 1 `[P1]`-`[P3]`)**

Raw prompt:
```
Look at this Python function and tell me if it has any bugs.

def calculate_discount(price, discount_percent, is_member):
    if is_member:
        discount_percent += 10
    final_price = price - (price * discount_percent)
    if final_price < 0:
        return 0
    return final_price
```

---

**TEST 2: Financial Analysis (Accuracy task | Target Mode: Mode 1 Max Certificate, Template 2 `[F1]`-`[F3]`)**

Raw prompt:
```
A company reports $50M revenue in Q1, $47M in Q2, $52M in Q3, and $61M in Q4. Operating expenses were 78% of revenue in Q1, 82% in Q2, 75% in Q3, and 71% in Q4. They took on $15M in new debt in Q3. Analyze their financial health.
```

---

**TEST 3: Medical Reasoning (Accuracy task | Target Mode: Mode 1 Max Certificate, Template 3 `[S1]`-`[S4]`)**

Raw prompt:
```
A 58-year-old male presents with sudden onset chest pain radiating to the left arm, diaphoresis, and shortness of breath. BP 90/60, HR 110, SpO2 94%. ECG shows ST elevation in leads II, III, and aVF. Troponin pending. What is the most likely diagnosis and what are the immediate priorities?
```

---

**TEST 4: Legal Analysis (Accuracy task | Target Mode: Mode 1 Max Certificate, Template 4 `[L1]`-`[L3]`)**

Raw prompt:
```
An employee signed a non-compete agreement that prevents them from working in "any related industry" within a 200-mile radius for 5 years after leaving the company. They left and took a job at a competitor 150 miles away, 8 months later. The former employer is threatening to sue. Analyze the enforceability of this non-compete.
```

---

**TEST 5: Research Synthesis (Mixed task | Target Mode: Mode 1 Max Certificate, Template 5 `[E1]`-`[E3]`)**

Raw prompt:
```
What does the research say about whether remote work improves or hurts productivity? Give me a balanced overview.
```

---

**TEST 6: Business Decision (Mixed task | Target Mode: Mode 1 Max Certificate, Template 6 `[O1]`-`[O3]`)**

Raw prompt:
```
We're a 15-person SaaS startup deciding between building our own authentication system or using Auth0/Clerk. We handle sensitive healthcare data (HIPAA). What should we do?
```

---

**TEST 7: Compliance Check (Accuracy task | Target Mode: Mode 1 Max Certificate, Template 7 `[R1]`-`[R2]`)**

Raw prompt:
```
Review this password policy for NIST 800-63B compliance:
- Minimum 8 characters
- Must include uppercase, lowercase, number, and special character
- Passwords expire every 90 days
- Cannot reuse last 5 passwords
- Account locks after 3 failed attempts for 30 minutes
```

---

**TEST 8: Document Analysis (Mixed task | Target Mode: Mode 1 Max Certificate, Template 8 `[C1]`-`[C3]`)**

Raw prompt:
```
Here is an executive summary from a project proposal: "Our AI-powered customer service solution will reduce support tickets by 60% within 6 months of deployment. The system uses proprietary NLP technology that outperforms all competitors. Implementation requires minimal IT involvement and the ROI will exceed 300% in the first year." Analyze the credibility of these claims.
```

---

**TEST 9: Comparative Analysis (Mixed task | Target Mode: Mode 2 Lite Certificate `[LITE]`, Template 9 `[D1]`-`[D3]`)**

Raw prompt:
```
Compare PostgreSQL and MongoDB for a new application that needs to handle both structured transaction data and semi-structured user activity logs. We expect 10M records per month growing 20% annually.
```
*(Note for Test 9: Use **Mode 2: Lite Certificate** (`1-3` core premises + compact decision matrix + verified recommendation, capping overhead at `<1.5x`) to test whether Lite Mode retains full analytical rigor while eliminating the token bloat observed in v1.0 benchmarks.)*

---

**TEST 10: Creative Brief with Structure (Creative/Alignment task | Target Mode: Mode 4 Creative & Divergent v2, Template 10 `[NT0]` + `[SC0]`)**

Raw prompt:
```
Write a product description for a new ergonomic office chair designed for people who work 10+ hour days. The chair has lumbar support that auto-adjusts, breathable mesh, and a 12-year warranty. Target audience is remote tech workers ages 25-45.
```
*(Note for Test 10: Use **Mode 4: Creative & Divergent v2** (`[NT0]` Verbalized Sampling of 3 distinct tonal candidates with `<0.15` typicality + `[SC0]` Anti-SlopShape Structural Rarity Contract with positive observable predicates, selecting and executing the strongest candidate) to test whether Mode 4 fixes the creative rigidity of v1.0.)*

---

**TEST 11: Repository Context File Optimization (Agentic Harness task | Target Mode: Mode 3 `[CONTEXT-FILES]`, Template 11)**

Raw prompt:
```
Write a CLAUDE.md file for our Python FastAPI + PostgreSQL repository. Explain the project overview, list the folder structure (app/api, app/models, app/services, tests/), explain standard PEP8 coding conventions, and include our non-obvious commands: running unit tests requires `pytest -m "not integration" --reuse-db`, database migrations must run via `./scripts/migrate.sh check` before committing, and Redis cache keys in `app/services/billing.py` must never be mutated without bumping `SCHEMA_EPOCH`.
```
*(Note for Test 11: Use **Mode 3: Agentic Harness (`[CONTEXT-FILES]`, Template 11, Gloaguen et al., 2026)** to test whether the optimized prompt forces stripping discoverable codebase summaries and standard PEP8 boilerplate (`<150` lines) while isolating non-inferable commands, hard invariants, and verification gates.)*

---

**TEST 12: Algorithmic Concurrency & Verification Gate (LRM / Agentic Coding task | Target Mode: Mode 3 `[HARNESS]`, Template 12)**

Raw prompt:
```
Write a thread-safe async token bucket rate limiter in Python (`AsyncTokenBucket`) that supports burst capacity, fractional refill rates, and `acquire(tokens: int, timeout: float | None = None) -> bool`. Make sure there are no race conditions when multiple coroutines wait concurrently.
```
*(Note for Test 12: Use **Mode 3: LRM & Agentic Harness (`[HARNESS]`, Template 12, Zhang et al., 2026; Chen et al., 2026)** to test whether replacing verbose prose Chain-of-Thought with explicit pre/post-condition invariants `[V1]`-`[V3]` and an executable self-test harness produces cleaner, race-free concurrent code.)*

---

## EVALUATION PROCEDURE

For EACH of the 12 test cases, follow this exact sequence:

### Step A: Produce the Baseline Response

Copy the raw prompt exactly. Answer it directly with your best effort. Do not apply the skill. Do not use certificate structure. Just answer as you normally would with a well-crafted response.

Label this: `### BASELINE RESPONSE`

### Step B: Apply the Skill to Optimize the Prompt

Read the raw prompt. Follow the `make-prompt-better` v4.0 skill methodology:
1. Classify the task type and select the Certificate Mode (Mode 1 Max, Mode 2 Lite, Mode 3 Harness/LRM, or Mode 4 Creative v2).
2. Identify problems with the original prompt (goal leakage, missing verification gates, SlopShape vulnerability, etc.).
3. Select the appropriate domain template from `make-prompt-better/references/domain-templates.md` (Templates 1-12).
4. Rewrite the prompt with the certificate structure, authority framing, positive observable-predicate recipes (Yin et al., 2026), anti-hallucination guards, and persona calibration as specified by the skill.

Show the full optimized prompt. Label this: `### OPTIMIZED PROMPT`

### Step C: Produce the Optimized Response

Answer the optimized prompt. Follow the certificate or harness structure it specifies. Fill all required premises, traces, verification gates, and conclusion sections.

Label this: `### OPTIMIZED RESPONSE`

### Step D: Self-Evaluate Both Responses

Score BOTH responses on these 5 dimensions using a 1-5 scale:

| Dimension | What It Measures | 1 (Poor) | 5 (Excellent) |
|---|---|---|---|
| **Accuracy** | Factual/technical correctness, zero hallucinated claims or bugs | Major errors | All claims/code verifiable |
| **Completeness** | Covers all relevant aspects and edge cases, no critical gaps | Major omissions | Comprehensive |
| **Structure** | Organized, easy to follow, logical flow appropriate to task | Disorganized or bloated | Clear, high-signal structure |
| **Actionability** | Provides concrete next steps, runnable code, or usable conclusions | Vague generalities | Specific, immediately usable |
| **Traceability** | Claims/decisions are supported by cited premises, math, or tests | Unsupported assertions | Every conclusion traceable |

For each response, produce:
```
| Dimension     | Baseline | Optimized | Delta |
|---------------|----------|-----------|-------|
| Accuracy      |          |           |       |
| Completeness  |          |           |       |
| Structure     |          |           |       |
| Actionability |          |           |       |
| Traceability  |          |           |       |
| TOTAL         |    /25   |     /25   |       |
```

Also record the approximate **Word Count** (`Baseline Words: X | Optimized Words: Y | Overhead Ratio: Y/X`) and write 2-3 sentences explaining what specifically improved, what stayed the same, and what (if anything) got worse.

Label this: `### EVALUATION: TEST N`

## AFTER ALL 12 TESTS: FINAL REPORT

After completing all 12 test cases, produce a summary report:

### Summary Table

```
| Test | Domain                      | Task Type | Mode   | Baseline /25 | Optimized /25 | Delta | Words (B/O/Ratio) | Winner |
|------|-----------------------------|-----------|--------|--------------|---------------|-------|-------------------|--------|
| 1    | Code Review                 | Accuracy  | Mode 1 |              |               |       |                   |        |
| 2    | Financial Analysis          | Accuracy  | Mode 1 |              |               |       |                   |        |
| 3    | Medical Reasoning           | Accuracy  | Mode 1 |              |               |       |                   |        |
| 4    | Legal Analysis              | Accuracy  | Mode 1 |              |               |       |                   |        |
| 5    | Research Synthesis          | Mixed     | Mode 1 |              |               |       |                   |        |
| 6    | Business Decision           | Mixed     | Mode 1 |              |               |       |                   |        |
| 7    | Compliance Check            | Accuracy  | Mode 1 |              |               |       |                   |        |
| 8    | Document Analysis           | Mixed     | Mode 1 |              |               |       |                   |        |
| 9    | Comparative Analysis        | Mixed     | Mode 2 |              |               |       |                   |        |
| 10   | Creative Brief              | Creative  | Mode 4 |              |               |       |                   |        |
| 11   | Context File (CLAUDE.md)    | Harness   | Mode 3 |              |               |       |                   |        |
| 12   | Async Rate Limiter (LRM)    | Harness   | Mode 3 |              |               |       |                   |        |
|------|-----------------------------|-----------|--------|--------------|---------------|-------|-------------------|--------|
|      | AVERAGE                     |           |        |              |               |       |                   |        |
```

### Analysis Sections

Write each of these 9 sections:

1. **Overall Verdict**: Does `make-prompt-better` v4.0 improve output quality? By how much on average (`/25` and `%`)? Is it worth the token overhead?
2. **Where It Helped Most**: Which domains and modes saw the largest improvement? Why?
3. **Where It Helped Least (or Hurt)**: Which domains or modes showed minimal improvement or degradation? What went wrong?
4. **v4.0 Mode Evaluation (Max vs. Lite vs. Harness vs. Creative v2)**:
   - Did **Mode 2 (Lite)** on Test 9 keep overhead under `1.5x` while preserving quality?
   - Did **Mode 3 (Harness / LRM)** on Tests 11-12 prevent context bloat and race conditions?
   - Did **Mode 4 (Creative v2: Verbalized Sampling + Anti-SlopShape)** on Test 10 improve voice and structural originality over baseline?
5. **Accuracy vs. Mixed vs. Creative vs. Harness**: Break down average scores by task category. Does PRISM-based persona calibration work as intended?
6. **Traceability Specifically**: Compare traceability scores across all 12 tests. Did the certificate/harness structures genuinely make claims more traceable?
7. **Token Cost vs. Value**: Report average word/token counts for Baseline vs. Optimized across modes. Compare Mode 1 (Max) overhead against Mode 2 (Lite) and Mode 3 (Harness).
8. **Failure Modes Observed**: List specific cases where the skill produced over-formatted answers, unnecessary complexity, or worse outputs.
9. **Recommendations for v4.1 Skill Improvement**: Based on your evaluation, what concrete refinements should be made to `SKILL.md` or `domain-templates.md`?

## CRITICAL RULES FOR THE EVALUATOR

1. **Equal effort on both versions.** Do not write a lazy baseline to make the optimized version look better. Both get your best work.
2. **Honest scoring.** If both responses are essentially equal, score them equal. Do not inflate optimized scores or deflate baseline scores.
3. **Flag self-evaluation bias.** Acknowledge explicitly that you are both generator and judge.
4. **Note when structure adds overhead without value.** If a certificate structure forces unnecessary formality, penalize `Structure` accordingly.
5. **Track word/token counts.** Report word counts and ratio (`Optimized / Baseline`) for every test.
6. **Sequential execution (no reading ahead).** Produce each baseline response BEFORE writing or answering the optimized prompt for that test case.

## AUTOMATIC SAVING INSTRUCTIONS

Save your complete output (containing all 12 test cases and the Final Report) to:
`research/benchmark/v4/results/<MODEL_SLUG>/EVALUATION_RESULTS.md`

Where `<MODEL_SLUG>` identifies your model (for example, `gemini-3.8`, `gpt-6.1-terra`, `claude-opus`, `claude-sonnet-5.5`, `meta-muse-wonder-1.0-max`, or the Ollama model slug). Create the directory if it does not exist.
