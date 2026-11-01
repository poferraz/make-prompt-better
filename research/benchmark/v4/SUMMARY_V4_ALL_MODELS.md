# Master Synthesis Report: Cross-Architecture Evaluation of make-prompt-better (v4.2.0 Benchmark & v4.3.0 Upgrade)

This report presents the cross-architecture empirical synthesis of the `make-prompt-better` v4.2.0 benchmark suite (executed October 31, 2026) across 14 distinct language model architectures (`N = 164` evaluated Baseline vs. Optimized pairs across 12 standardized domain tasks). In accordance with the v4.3.0 methodological audit, this synthesis strictly separates **In-Session Frontier Self-Evaluations** from **Isolated Runner Anonymized Self-Evaluations**, reports **Model-Cluster and Two-Way Block Bootstrap 95% confidence intervals** alongside cell-level descriptives, qualifies longitudinal comparisons between the October 30 (v4.0) and October 31 (v4.2.0) runs as observational rather than purely causal, and documents the v4.3.0 compiler and harness upgrades implemented in response.

*(Methodological note: Prior October 30 v4.0 unblinded evaluations in `research/benchmark/v4/results_pre_run_backup/`, including `claude-opus`, `gpt-6.1-terra`, and `meta-muse-wonder-1.0-max`, are treated strictly as longitudinal baseline references and excluded from the 14-model v4.2.0 cohort tables.)*

---

## 1. Executive Summary, Protocol Provenance & Headline Metrics

The v4.2.0 evaluation cohort comprises 14 models (`164` evaluated pairs across `T = 12` tasks, 1 task per domain). Because the execution tracks differ in blinding, context isolation, and judge assignment, their results carry distinct evidentiary weight and **should not be interpreted as a single homogeneous controlled trial**:

- **Stratum A: In-Session Frontier Self-Evaluation Track (Tracks 1 & 2, 3 models, 36 pairs)**:
  - **Track 1 (Google Antigravity Session Track)**: `gemini-3.8` (Gemini 3.8 Flash High, 12/12) and `argon-4-low` (Gemini 4 Argon Low, 12/12). Executed as in-session evaluations recorded in Markdown without API `eval_count` telemetry; self-judged by the session model.
  - **Track 2 (OpenAI Codex Session Track)**: `gpt-6-astra-max` (GPT 6 Astra Max, 12/12). As documented in `results/gpt-6-astra-max/EVALUATION_RESULTS.md`, Tests 1 through 11 were generated and self-scored inside the same conversation without blinded candidate labels, and Test 12 was regenerated in-session. Track 2 is therefore an **exploratory in-session benchmark**, not a blinded controlled trial.
- **Stratum B: Isolated Runner Anonymized Self-Judged Track (Track 3, 11 Ollama Cloud models, 128 pairs)**:
  - Models: `gpt-oss:20b-cloud` (9/12), `gemma4:31b-cloud` (12/12), `glm-5.3-flash:cloud` (12/12), `deepseek-v4.1-flash:cloud` (12/12), `deepseek-v4.1-flash:1017-cloud` (12/12), `minimax-m3.1-flash:cloud` (12/12), `beam:cloud` (12/12), `muse-spark-open:cloud` (12/12), `glm-5.3:cloud` (12/12), `mistral-large-4:cloud` (12/12), and `kimi-k3:cloud` (11/12).
  - Provenance & Residual Confounders: Each API call (`Step A` baseline, `Step B` prompt compilation, `Step C` optimized generation, `Step D` judge) ran in an isolated stateless context with randomized `Candidate A` / `Candidate B` assignment. However, three confounders remained in the v4.2.0 run: (1) each model served as its own judge (`judge_model == model`), (2) the v4.2.0 judge table template still printed `"Baseline (1-5)"` and `"Optimized (1-5)"` as column headers for the randomized slots (repaired in v4.3.0 `blind_stats_engine.py`), and (3) visible `[P1]`/`[T1]` certificate headers remained unstripped by default.

### Protocol-Stratified & Cluster-Robust Aggregate Metrics

Because the dataset crosses $M$ models with $T = 12$ fixed tasks (1 case per domain), treating all 164 cells as independent and identically distributed (i.i.d.) observations overstates statistical precision. The table below reports **Cell-Level Bootstrap 95% CIs**, **Model-Cluster Bootstrap 95% CIs**, **Two-Way Block Bootstrap 95% CIs** (resampling both models and tasks), and **Cluster-Level Sign-Flip Permutation p-values** (`research/benchmark/v4/results/AGGREGATED_METRICS.md`):

| Cohort Stratum | Models ($M$) | Pairs ($N$) | Baseline Mean (/25) | Optimized Mean (/25) | Mean Delta (/25) | Cell 95% CI | Model-Cluster 95% CI | Two-Way Block 95% CI | Model Sign-Flip $p$ | Task Sign-Flip $p$ | Avg Word Overhead | Win-Tie-Loss (Win %) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **(a) In-Session Frontier Self-Eval Track (Tracks 1 & 2)** | 3 | 36 | 22.14 | 24.50 | **+2.36** | `[+1.90, +2.79]` | `[+0.92, +3.29]` | `[+1.00, +3.38]` | `0.2500` | `0.0005` | **1.65x** | **31W-4T-1L (86.1%)** |
| **(b) Isolated Anonymized Self-Judged Cloud Track (Track 3)** | 11 | 128 | 22.30 | 19.95 | **-2.35** | `[-3.18, -1.52]` | `[-3.13, -1.57]` | `[-4.11, -0.66]` | `0.0010` | `0.0073` | **3.57x** | **38W-5T-85L (29.7%)** |
| **Combined Descriptive Pool (All 14 Models)** | 14 | 164 | 22.27 | 20.95 | **-1.31** | `[-2.04, -0.61]` | `[-2.47, -0.08]` | `[-3.15, +0.35]` | `0.0555` | `0.0469` | **3.15x** | **69W-9T-86L (42.1%)** |

*(Statistical note: With $M = 3$ frontier models, the minimum attainable two-sided model-level sign-flip permutation p-value is $2 / 2^3 = 0.2500$, even though all 3 models had positive mean deltas and the task-level sign-flip p-value across the 12 tasks is $p = 0.0005$. When pooling all 14 models descriptively, the Two-Way Block 95% CI `[-3.15, +0.35]` crosses zero, confirming that opposite effects across the two protocol strata cannot be collapsed into a single pooled significance claim.)*

### Five Principal Findings

1. **Divergence Across Protocol Strata & Model Tiers**: On the 3-model In-Session Frontier Track (`gemini-3.8`, `argon-4-low`, `gpt-6-astra-max`), `make-prompt-better` v4.2.0 recorded a **+2.36 / 25 mean gain** (`Two-Way Block 95% CI: [+1.00, +3.38]`, `31W-4T-1L`, `86.1%` win rate) at **1.65x** average word overhead. On the 11-model Isolated Anonymized Self-Judged Cloud Track, forced-mode compilation yielded a **-2.35 / 25 mean regression** (`Two-Way Block 95% CI: [-4.11, -0.66]`, `38W-5T-85L`, `29.7%` win rate) accompanied by **3.57x** average word expansion (`5.22x` measured API output token expansion across the `128` pairs with `eval_count` telemetry).
2. **Observational Shift Between v4.0 Unblinded and v4.2.0 Anonymized Cloud Runs (-3.41 Points)**: Across the 11 Ollama Cloud models, the mean delta shifted from **+1.06 / 25** (`98W-4T-30L`, October 30 v4.0 unblinded run) to **-2.35 / 25** (`38W-5T-85L`, October 31 v4.2.0 anonymized run), a net shift of **-3.41 / 25** (+1.53 on Baseline and -1.88 on Optimized). Because the two runs also differed in skill version (v4.0 vs. v4.2.0), freshly generated responses, and completion counts (`132` vs. `128` pairs), this `-3.41` shift is an **observational multi-factor difference**, not a pure causal estimate of label bias alone. Section 3 details how `rejudge_saved_outputs.py` isolates pure judge effects on identical saved outputs.
3. **Traceability Improved Across Both Strata (+0.78 / 5.0 Overall)**: Even in the isolated cloud stratum where Structure (-1.40) and Actionability (-0.80) were penalized for verbosity and dropped sections, **Traceability** improved across both strata: **+0.90 / 5.0** on the Frontier Track (4.07 to 4.97) and **+0.75 / 5.0** on the Isolated Cloud Track (3.62 to 4.37), averaging **+0.78 / 5.0** across all 164 pairs (Ugare & Chandra, 2026; Zhang, Hu et al., 2026).
4. **Code-First Template 12 (`AsyncTokenBucket`) Reversed the v4.0 Concurrency Collapse (+1.83 Overall Delta)**: In v4.0, Test 12 suffered a -1.85 net delta on open models because pre-code verification tables exhausted output token budgets. The v4.2.0 code-first refactoring of Template 12 (`[HARNESS]`, Lee et al., 2026) made Test 12 the **highest-scoring task across the 14-model suite (+1.83 / 25 overall delta, +3.67 on Frontier, +1.22 on Cloud)**, delivering +7.0 point gains on `beam:cloud`, `deepseek-v4.1-flash:1017-cloud`, and `gemma4:31b-cloud`.
5. **Test 11 (`CLAUDE.md`) Exposed a Compiler Requirement-Preservation Defect (-8.91 on Cloud)**: The Test 11 prompt explicitly asks for a project overview, folder structure, and PEP8 convention explanation. Template 11 (`[CONTEXT-FILES]`, Gloaguen et al., 2026) instructed the compiler to delete those three requested sections entirely. Anonymized cloud judges evaluating `Candidate B` (`0.33x` word ratio) against the user's prompt penalized the omission of three explicit deliverables (`0W-0T-11L`, `-8.91 / 25`). As `gpt-6-astra-max` noted in its Test 11 evaluation, silently dropping explicitly requested deliverables is a **compiler scope-preservation defect**, repaired in v4.3.0 via `[REQ-PRESERVE]` and `Section 0` compact fulfillment.

---

## 2. 14-Model v4.2.0 Performance Matrix

The table below reports complete v4.2.0 metrics across all 14 evaluated architectures, including explicit evaluation protocol provenance, judge assignment, completion counts, and measured token ratios.

| Model | Protocol Provenance | Judge (`Self?`) | Completed | Baseline (/25) | Optimized (/25) | Delta (/25) | Gain (%) | Word Ratio | API Token Ratio | Win-Tie-Loss | Best Task (Delta) | Worst Task (Delta) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| `gemini-3.8` | In-Session Self-Eval (MD) | `gemini-3.8` (Yes) | 12/12 | 21.54 | 24.83 | **+3.29** | +15.3% | 1.55x | N/A | 12W-0T-0L | T11, T12 (+4.5) | T1, T3, T7 (+2.5) |
| `argon-4-low` | In-Session Self-Eval (MD) | `argon-4-low` (Yes) | 12/12 | 22.12 | 25.00 | **+2.88** | +13.0% | 1.61x | N/A | 12W-0T-0L | T11 Context (+4.5) | T3, T9 (+2.0) |
| `gpt-6-astra-max` | In-Session Unblinded Self-Eval | `gpt-6-astra-max` (Yes) | 12/12 | 22.75 | 23.67 | **+0.92** | +4.0% | 1.79x | N/A | 7W-4T-1L | T8, T12 (+3.0) | T2 Financial (-1.0) |
| `gemma4:31b-cloud` | Isolated Anonymized Self-Judged | `gemma4:31b` (Yes) | 12/12 | 22.42 | 22.08 | **-0.33** | -1.5% | 0.85x | 1.24x | 6W-0T-6L | T12 LRM (+7.0) | T9, T11 (-7.0) |
| `glm-5.3-flash:cloud` | Isolated Anonymized Self-Judged | `glm-5.3-flash` (Yes) | 12/12 | 21.54 | 21.08 | **-0.46** | -2.1% | 3.76x | 4.86x | 6W-1T-5L | T8 Document (+4.0) | T11 Context (-14.0) |
| `beam:cloud` | Isolated Anonymized Self-Judged | `beam:cloud` (Yes) | 12/12 | 21.50 | 19.92 | **-1.58** | -7.4% | 2.11x | 5.21x | 4W-0T-8L | T12 LRM (+7.0) | T11 Context (-11.0) |
| `minimax-m3.1-flash:cloud` | Isolated Anonymized Self-Judged | `minimax-m3.1` (Yes) | 12/12 | 22.50 | 20.67 | **-1.83** | -8.1% | 8.78x | 12.18x | 4W-0T-8L | T2 Financial (+4.0) | T11 Context (-8.0) |
| `glm-5.3:cloud` | Isolated Anonymized Self-Judged | `glm-5.3:cloud` (Yes) | 12/12 | 23.08 | 21.08 | **-2.00** | -8.7% | 3.98x | 5.19x | 3W-1T-8L | T3 Medical (+2.0) | T11, T12 (-6.0) |
| `mistral-large-4:cloud` | Isolated Anonymized Self-Judged | `mistral-large-4` (Yes) | 12/12 | 22.42 | 20.25 | **-2.17** | -9.7% | 2.95x | 3.49x | 4W-0T-8L | T10 Creative (+4.0) | T4 Legal (-12.0) |
| `kimi-k3:cloud` | Isolated Anonymized Self-Judged | `kimi-k3:cloud` (Yes) | 11/12 | 22.27 | 19.82 | **-2.45** | -11.0% | 4.14x | 5.86x | 3W-0T-8L | T1 Code (+5.0) | T11 Context (-10.0) |
| `deepseek-v4.1-flash:1017-cloud` | Isolated Anonymized Self-Judged | `deepseek-1017` (Yes) | 12/12 | 22.75 | 19.92 | **-2.83** | -12.5% | 4.43x | 6.01x | 3W-1T-8L | T12 LRM (+7.0) | T6 Business (-11.0) |
| `muse-spark-open:cloud` | Isolated Anonymized Self-Judged | `muse-spark` (Yes) | 12/12 | 20.92 | 16.92 | **-4.00** | -19.1% | 2.19x | 3.31x | 2W-1T-9L | T7 NIST (+5.0) | T5 Research (-14.0) |
| `deepseek-v4.1-flash:cloud` | Isolated Anonymized Self-Judged | `deepseek-flash` (Yes) | 12/12 | 23.17 | 18.83 | **-4.33** | -18.7% | 4.92x | 6.64x | 2W-0T-10L | T12 LRM (+3.0) | T8 Document (-15.0) |
| `gpt-oss:20b-cloud` | Isolated Anonymized Self-Judged | `gpt-oss:20b` (Yes) | 9/12 | 22.89 | 18.56 | **-4.33** | -18.9% | 0.43x | 2.75x | 1W-1T-7L | T3 Medical (+7.0) | T8 Document (-11.0) |

### Per-Test Score Delta Matrix Across All 14 Models (Optimized minus Baseline, /25)

| Model | T1 Code | T2 Fin | T3 Med | T4 Legal | T5 Res | T6 Biz | T7 NIST | T8 Doc | T9 Lite | T10 Creative | T11 Context | T12 LRM |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `gemini-3.8` | +2.5 (25) | +3.5 (24.5) | +2.5 (25) | +3.5 (25) | +3.5 (24.5) | +3.5 (25) | +2.5 (25) | +3.0 (25) | +3.0 (25) | +3.0 (24) | +4.5 (25) | +4.5 (25) |
| `argon-4-low` | +2.5 (25) | +3.0 (25) | +2.0 (25) | +3.0 (25) | +2.5 (25) | +2.5 (25) | +2.5 (25) | +3.5 (25) | +2.0 (25) | +3.0 (25) | +4.5 (25) | +3.5 (25) |
| `gpt-6-astra-max` | +0.0 (23) | -1.0 (24) | +1.0 (24) | +0.0 (23) | +1.0 (23) | +1.0 (24) | +2.0 (24) | +3.0 (25) | +1.0 (24) | +0.0 (23) | +0.0 (23) | +3.0 (24) |
| `gemma4:31b-cloud` | +1.0 (24) | -1.0 (23) | -4.0 (20) | -2.0 (21) | +4.0 (23) | +1.0 (23) | +5.0 (25) | +2.0 (24) | -7.0 (17) | -3.0 (22) | -7.0 (18) | +7.0 (25) |
| `glm-5.3-flash:cloud` | +3.0 (23) | -1.0 (22) | +1.0 (22) | -2.0 (20) | +0.0 (21) | +2.5 (24) | +3.0 (22) | +4.0 (24) | +3.0 (24) | -4.0 (19) | -14.0 (11) | -1.0 (21) |
| `beam:cloud` | +3.0 (24) | +3.0 (24) | -1.0 (21) | -5.0 (19) | -5.0 (14) | -5.0 (18) | -1.0 (20) | +4.0 (24) | -6.0 (16) | -2.0 (20) | -11.0 (14) | +7.0 (25) |
| `minimax-m3.1-flash:cloud` | -3.0 (22) | +4.0 (24) | -2.0 (22) | +1.0 (22) | +1.0 (19) | -5.0 (19) | -7.0 (16) | -2.0 (22) | +2.0 (24) | -1.0 (21) | -8.0 (17) | -2.0 (20) |
| `glm-5.3:cloud` | -3.0 (21) | +1.0 (23) | +2.0 (24) | -2.0 (21) | +0.0 (22) | +1.0 (24) | -1.0 (21) | -5.0 (19) | -4.0 (20) | -1.0 (21) | -6.0 (18) | -6.0 (19) |
| `mistral-large-4:cloud` | +1.0 (24) | +3.0 (24) | -5.0 (18) | -12.0 (12) | -1.0 (20) | -5.0 (16) | -2.0 (21) | -2.0 (21) | +2.0 (23) | +4.0 (24) | -8.0 (17) | -1.0 (23) |
| `kimi-k3:cloud` | +5.0 (24) | +4.0 (24) | -5.0 (19) | -6.0 (18) | -8.0 (16) | +3.0 (24) | -3.0 (19) | -2.0 (20) | -3.0 (21) | -2.0 (20) | -10.0 (13) | - |
| `deepseek-v4.1-flash:1017-cloud` | +0.0 (23) | +2.0 (24) | -8.0 (16) | -1.0 (23) | -5.0 (19) | -11.0 (12) | -1.0 (21) | +3.0 (24) | -5.0 (19) | -5.0 (20) | -10.0 (13) | +7.0 (25) |
| `muse-spark-open:cloud` | -6.0 (17) | +0.0 (21) | -2.0 (20) | -9.0 (13) | -14.0 (5) | -4.0 (16) | +5.0 (23) | +4.0 (23) | -10.0 (13) | -5.0 (15) | -4.0 (17) | -3.0 (20) |
| `deepseek-v4.1-flash:cloud` | -2.0 (20) | -1.0 (23) | -4.0 (19) | +2.0 (23) | -6.0 (16) | -9.0 (15) | -3.0 (20) | -15.0 (10) | -1.0 (22) | -6.0 (19) | -10.0 (15) | +3.0 (24) |
| `gpt-oss:20b-cloud` | -4.0 (21) | - | +7.0 (25) | -2.0 (20) | -6.0 (19) | +0.0 (21) | -10.0 (12) | -11.0 (14) | -3.0 (20) | - | -10.0 (15) | - |

---

## 3. Longitudinal Comparison: v4.0 Unblinded (Oct 30) vs. v4.2.0 Anonymized (Oct 31)

Comparing the October 30 v4.0 run (`research/benchmark/v4/results_pre_run_backup/`) against the October 31 v4.2.0 run (`research/benchmark/v4/results/`) across the 11 Ollama Cloud architectures shows a **-3.41 / 25 shift in net delta** (`-3.46 / 25` across the `n = 128` strictly matched model-task cells).

### Methodological Qualification: Observational Shift vs. Isolated Label Effect

While the October 31 runner randomized candidates into `Response A` and `Response B` slots, **this -3.41 point difference is an observational shift across two distinct benchmark runs rather than a pure experimental isolation of label bias**:
1. **Simultaneous Changes Across Runs**: Between October 30 and October 31, the prompt compiler changed from v4.0 to v4.2.0 (e.g., Template 12 was refactored to code-first), all Baseline and Optimized responses were freshly generated via stochastic LLM sampling, and 4 cells failed to complete on October 31 (`kimi-k3:cloud` Test 12; `gpt-oss:20b-cloud` Tests 2, 10, 12).
2. **Residual Blinding Leak in the v4.2.0 Judge Table**: Although `build_blind_eval_instruction` randomized candidate text into `Response A` and `Response B`, its Markdown table template still requested columns titled `| Criterion | Baseline (1-5) | Optimized (1-5) | Delta |`, and `[P1]`/`[T1]` certificate headers remained visible in the optimized text. Self-judging models could therefore still experience column-header anchoring or recognize the certificate format.
3. **Controlled Ablation Tool (`rejudge_saved_outputs.py`)**: To isolate pure judge bias (label anchoring, self-preference, position bias, and visible `[P1]`/`[T1]` marker recognition) without confounding from regenerated text or skill changes, v4.3.0 introduces `research/benchmark/v4/rejudge_saved_outputs.py`, which re-scores the **exact same saved `(baseline, optimized)` response pairs** under four controlled conditions: (1) unblinded labels, (2) neutral `Candidate A`/`B` 2-pass position-swapped labels, (3) marker-stripped (`--strip-markers`) 2-pass swapped labels, and (4) independent judge (`--judge-model`).

### Paired Model Comparison: v4.0 Unblinded (Oct 30) vs. v4.2.0 Anonymized (Oct 31)

| Model Architecture | v4.0 Unblinded Baseline (/25) | v4.0 Unblinded Optimized (/25) | v4.0 Unblinded Delta (/25) | v4.0 Record | v4.2.0 Anon Baseline (/25) | v4.2.0 Anon Optimized (/25) | v4.2.0 Anon Delta (/25) | v4.2.0 Record | Baseline Shift (dB) | Optimized Shift (dO) | Observational Net Shift (v4.2 - v4.0) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `gemma4:31b-cloud` | 20.62 | 22.12 | +1.50 | 8W-0T-4L | 22.42 | 22.08 | -0.33 | 6W-0T-6L | +1.80 | -0.04 | **-1.83** |
| `deepseek-v4.1-flash:1017-cloud` | 22.00 | 21.58 | -0.42 | 7W-1T-4L | 22.75 | 19.92 | -2.83 | 3W-1T-8L | +0.75 | -1.66 | **-2.41** |
| `glm-5.3-flash:cloud` | 21.50 | 23.50 | +2.00 | 11W-0T-1L | 21.54 | 21.08 | -0.46 | 6W-1T-5L | +0.04 | -2.42 | **-2.46** |
| `gpt-oss:20b-cloud` | 20.08 | 18.29 | -1.79 | 6W-0T-6L | 22.89 | 18.56 | -4.33 | 1W-1T-7L | +2.81 | +0.27 | **-2.54** |
| `minimax-m3.1-flash:cloud` | 21.00 | 22.12 | +1.12 | 10W-0T-2L | 22.50 | 20.67 | -1.83 | 4W-0T-8L | +1.50 | -1.45 | **-2.95** |
| `beam:cloud` | 19.42 | 21.00 | +1.58 | 8W-1T-3L | 21.50 | 19.92 | -1.58 | 4W-0T-8L | +2.08 | -1.08 | **-3.16** |
| `mistral-large-4:cloud` | 21.00 | 22.88 | +1.88 | 9W-1T-2L | 22.42 | 20.25 | -2.17 | 4W-0T-8L | +1.42 | -2.63 | **-4.05** |
| `glm-5.3:cloud` | 21.38 | 23.67 | +2.29 | 12W-0T-0L | 23.08 | 21.08 | -2.00 | 3W-1T-8L | +1.70 | -2.59 | **-4.29** |
| `deepseek-v4.1-flash:cloud` | 21.08 | 21.38 | +0.29 | 8W-1T-3L | 23.17 | 18.83 | -4.33 | 2W-0T-10L | +2.09 | -2.55 | **-4.62** |
| `kimi-k3:cloud` | 21.17 | 23.54 | +2.38 | 10W-0T-2L | 22.27 | 19.82 | -2.45 | 3W-0T-8L | +1.10 | -3.72 | **-4.83** |
| `muse-spark-open:cloud` | 19.25 | 20.08 | +0.83 | 9W-0T-3L | 20.92 | 16.92 | -4.00 | 2W-1T-9L | +1.67 | -3.16 | **-4.83** |
| **11-Model Cloud Aggregate** | **20.77** | **21.83** | **+1.06** | **98W-4T-30L (74.2%)** | **22.30** | **19.95** | **-2.35** | **38W-5T-85L (29.7%)** | **+1.53** | **-1.88** | **-3.41** |
| `gemini-3.8` *(Track 1 Reference)* | 19.38 | 24.67 | +5.29 | 12W-0T-0L | 21.54 | 24.83 | +3.29 | 12W-0T-0L | +2.16 | +0.16 | **-2.00** |

### Dimension-Level Decomposition Across the Two Cloud Runs

1. **Higher Baseline Calibration (+1.53 points on Baseline)**: In the October 30 run where evaluators were explicitly instructed to score the `Baseline` vs. `Optimized` sections in a single file, baselines averaged **20.77/25** (Traceability 3.12/5.0, Structure 4.40/5.0). In the October 31 anonymized run, natural-language baseline responses scored **22.30/25** (+1.53 points higher), with Baseline Structure rising to **4.90/5.0** and Baseline Traceability rising to **3.62/5.0**.
2. **Penalization of Certificate Verbosity & Omitted Deliverables (-1.88 points on Optimized)**: Under anonymized `Response A` vs. `Response B` presentation, judges penalized `3.57x` word inflation (`5.22x` token inflation) and omitted user sections (Test 11), lowering Optimized scores from **21.83/25** to **19.95/25**:

| Rubric Dimension | v4.0 Cloud Delta (/5) | v4.2.0 Cloud Delta (/5) | Observational Shift | Primary Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **Traceability** | **+1.66** (3.12 to 4.78) | **+0.75** (3.62 to 4.37) | -0.91 | Explicit premise-to-conclusion references remain positive (+0.75) under anonymized scoring |
| **Accuracy** | -0.13 (4.51 to 4.38) | -0.29 (4.51 to 4.22) | -0.16 | Step B prompt compiler occasionally narrows scope or drops secondary questions on smaller models |
| **Completeness** | -0.04 (4.37 to 4.33) | -0.60 (4.61 to 4.01) | -0.56 | Severe penalties on Test 11 (`CLAUDE.md`) for deleting three explicitly requested sections |
| **Actionability** | -0.11 (4.38 to 4.27) | -0.80 (4.66 to 3.86) | -0.69 | Multi-page certificates bury immediate actions beneath meta-commentary |
| **Structure** | -0.31 (4.40 to 4.08) | **-1.40** (4.90 to 3.50) | **-1.09** | Evaluators prefer concise markdown tables/lists over repetitive `[P]`/`[T]` scaffolding |

---

## 4. 4-Mode Protocol Empirical Validation

*(Methodological caveat on forced routing: `run_ollama_benchmarks.py` in v4.2.0 prescribed a fixed mode per test via `TEST_MODE_OVERRIDES`: Tests 1 to 8 forced Mode 1 Max, Test 9 forced Mode 2 Lite, Test 10 forced Mode 4 Creative, and Tests 11 to 12 forced Mode 3 Harness. Consequently, the v4.2.0 benchmark evaluates **forced mode execution** on each task rather than the skill's automatic Step 1 router. In v4.3.0, `--unprescribed-routing` is added so future runs can evaluate natural router decisions directly.)*

### Per-Test Performance Stratified by Track (v4.2.0 Cohort)

| Test & Prescribed Mode | Domain | All 14 Models Delta (W-T-L) | Frontier 3 Models Delta (W-T-L) | Cloud 11 Models Delta (W-T-L) | Frontier Word Ratio | Cloud Word Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **T1 (Mode 1 Max)** | Code Review | **+0.00** (7W-2T-5L) | **+1.67** (2W-1T-0L) | **-0.45** (5W-1T-5L) | 3.06x | 8.92x |
| **T2 (Mode 1 Max)** | Financial Analysis | **+1.50** (8W-1T-4L) | **+1.83** (2W-0T-1L) | **+1.40** (6W-1T-3L) | 1.55x | 3.82x |
| **T3 (Mode 1 Max)** | Medical Reasoning | **-1.11** (6W-0T-8L) | **+1.83** (3W-0T-0L) | **-1.91** (3W-0T-8L) | 1.64x | 7.12x |
| **T4 (Mode 1 Max)** | Legal Analysis | **-2.25** (4W-1T-9L) | **+2.17** (2W-1T-0L) | **-3.45** (2W-0T-9L) | 1.53x | 2.38x |
| **T5 (Mode 1 Max)** | Research Synthesis | **-2.36** (5W-2T-7L) | **+2.33** (3W-0T-0L) | **-3.64** (2W-2T-7L) | 1.64x | 3.68x |
| **T6 (Mode 1 Max)** | Business Decision | **-1.75** (7W-1T-6L) | **+2.33** (3W-0T-0L) | **-2.86** (4W-1T-6L) | 1.63x | 4.70x |
| **T7 (Mode 1 Max)** | NIST Compliance | **-0.57** (6W-0T-8L) | **+2.33** (3W-0T-0L) | **-1.36** (3W-0T-8L) | 1.46x | 3.90x |
| **T8 (Mode 1 Max)** | Document Analysis | **-0.75** (8W-0T-6L) | **+3.17** (3W-0T-0L) | **-1.82** (5W-0T-6L) | 1.65x | 2.73x |
| **T9 (Mode 2 Lite)** | Comparative Analysis | **-1.86** (6W-0T-8L) | **+2.00** (3W-0T-0L) | **-2.91** (3W-0T-8L) | 1.22x | 1.51x |
| **T10 (Mode 4 Creative)** | Creative Brief | **-1.46** (3W-1T-9L) | **+2.00** (2W-1T-0L) | **-2.50** (1W-0T-9L) | 1.72x | 1.53x |
| **T11 (Mode 3 Harness)** | Context (`CLAUDE.md`) | **-6.36** (2W-1T-11L) | **+3.00** (2W-1T-0L) | **-8.91** (0W-0T-11L) | 0.79x | 0.33x |
| **T12 (Mode 3 LRM)** | Async Rate Limiter | **+1.83** (7W-0T-5L) | **+3.67** (3W-0T-0L) | **+1.22** (4W-0T-5L) | 1.88x | 1.72x |

### Mode 1: Max Certificate (Tests 1 to 8)
- **Where Max Certificates Won Across Architectures**:
  - **Test 2 (Financial Analysis, +1.50 overall, 8W-1T-4L)**: The strongest Mode 1 task across both Frontier (+1.83) and Cloud (+1.40, 6W-1T-3L). Explicit `[P]` formula premises and `[T]` period-reconciliation traces prevented LTV:CAC and gross-margin arithmetic errors on `minimax-m3.1-flash:cloud` (+4.0), `kimi-k3:cloud` (+4.0), `gemini-3.8` (+3.5), `argon-4-low` (+3.0), `beam:cloud` (+3.0), and `mistral-large-4:cloud` (+3.0).
  - **Test 8 (Document Analysis, 8W-0T-6L, +3.17 on Frontier)**: Won 8 of 14 models overall, including all 3 Frontier models (`argon-4-low` +3.5, `gemini-3.8` +3.0, `gpt-6-astra-max` +3.0) and 5 Cloud models (`beam:cloud` +4.0, `glm-5.3-flash:cloud` +4.0, `muse-spark-open:cloud` +4.0, `deepseek-v4.1-flash:1017-cloud` +3.0, `gemma4:31b-cloud` +2.0).
  - **Test 1 (Code Review, 7W-2T-5L, +0.00 overall)**: Won or tied on 9 of 14 architectures (`kimi-k3:cloud` +5.0, `beam:cloud` +3.0, `glm-5.3-flash:cloud` +3.0, `gemini-3.8` +2.5, `argon-4-low` +2.5, `gemma4:31b-cloud` +1.0, `mistral-large-4:cloud` +1.0).
- **Where Forced Mode 1 Caused Severe Verbosity Inflation on Cloud Models**:
  - Across Tests 1 to 8, Frontier models held Mode 1 word overhead to **1.77x**, winning 21 of 24 pairs (`21W-2T-1L`).
  - By contrast, forcing Mode 1 on the 11 Ollama Cloud models inflated responses by **4.66x** in words (`>6x` in tokens), peaking on **Test 1 Code Review (`8.92x` average; `24.23x` on `minimax-m3.1-flash:cloud`, `16.93x` on `deepseek-v4.1-flash:cloud`)** and **Test 3 Medical Reasoning (`7.12x` average; `22.61x` on `minimax-m3.1-flash:cloud`)**. Evaluators penalized these multi-page essays for repeating the same facts across `[P]`, `[T]`, and the conclusion, and for burying urgent clinical actions in Test 3 beneath exhaustive differential workups.

### Mode 2: Lite Certificate (Test 9)
- **Overhead Control Validated (`<1.5x` Target Achieved)**: Across all 14 models, Test 9 (PostgreSQL vs. MongoDB Comparative Analysis) achieved an average word overhead ratio of **1.45x** (**1.22x** on Frontier models and **1.51x** across the 11 Cloud models, down from 4.66x in Mode 1).
- **Quality Preservation vs. Telegraphic Over-Compression**: On Frontier models, Mode 2 achieved a **3W-0T-0L record (+2.00 mean delta)**. On Cloud models, Mode 2 won on `glm-5.3-flash:cloud` (+3.0), `minimax-m3.1-flash:cloud` (+2.0), and `mistral-large-4:cloud` (+2.0 at 0.87x words), but lost on models where the Step B compiler interpreted "Lite" as extreme truncation (`gemma4:31b-cloud` at `0.35x` words, `-7.0`; `gpt-oss:20b-cloud` at `0.31x` words, `-3.0`; `muse-spark-open:cloud` at `0.73x` words, `-10.0`), stripping concrete partitioning and indexing guidance.

### Mode 3: LRM & Agentic Harness (Tests 11 & 12)
- **Test 12 (`AsyncTokenBucket` Concurrency, +1.83 overall, 7W-0T-5L)**:
  - **Code-First Validation**: Refactoring Template 12 to emit the complete executable implementation *before* the `[V1]`->`[V2]` verification gate (`<25%` commentary ceiling) resolved the v4.0 token-starvation failure (-1.85 in v4.0 to **+1.83 in v4.2.0**, a **+3.68 point turnaround**).
  - **Frontier (+3.67, 3W-0T-0L)** and **Cloud Breakthroughs (+1.22, 4W-0T-5L)**: `beam:cloud` (+7.0), `deepseek-v4.1-flash:1017-cloud` (+7.0), `gemma4:31b-cloud` (+7.0), and `deepseek-v4.1-flash:cloud` (+3.0) generated runnable `asyncio` concurrency harnesses that caught race conditions missed by their baselines. `gpt-6-astra-max` (+3.0) also identified floating-point rounding drift at large capacities (`2**53 + 1`), motivating the v4.3.0 exact-accounting check in Template 12.
- **Test 11 (`CLAUDE.md` Context File, -6.36 overall, 2W-1T-11L)**:
  - **Product Defect in Requirement Preservation**: The raw Test 11 prompt explicitly asks the model to *"Explain the project overview, list the folder structure (app/api, app/models, app/services, tests/), explain standard PEP8 coding conventions..."*. In v4.2.0, Template 11 instructed the model to delete those three requested sections entirely per Gloaguen et al. (2026). While `gemini-3.8` (+4.5) and `argon-4-low` (+4.5) scored the pruned file against the skill's own context-engineering theory, `gpt-6-astra-max` (`0.0` tie) rightly diagnosed this as a **scope and fidelity tradeoff**, and all 11 anonymized cloud judges (`0W-0T-11L`, `-8.91` mean delta) penalized the response for failing to fulfill three explicit user deliverables. In v4.3.0, Template 11 is repaired so explicitly requested overview/layout/style items are fulfilled compactly (`Section 0`, `<= 5` lines) rather than silently omitted.

### Mode 4: Creative & Divergent v2 (Test 10)
- **In-Session Frontier (+2.00 mean delta, 2W-1T-0L, 1.72x overhead)** vs. **Isolated Cloud (-2.50 mean delta, 1W-0T-9L, 1.53x overhead)**:
  - `mistral-large-4:cloud` posted a **+4.0 win at 0.63x words**, demonstrating that `[SC0]` anti-SlopShape distillation improves persuasive copy when the output is clean.
  - However, 9 of 10 evaluated cloud models lost because Template 10 instructed the model to emit a visible `[BACKSTAGE SCAFFOLD]` (`[NT0]` candidate probability distributions and `[NT1]`-`[NT3]` planning notes) above the deliverable. Anonymized evaluators penalized the unrequested planning notes as meta-commentary polluting a finished product description. In v4.3.0, `[NT0]`-`[NT3]` preparation is strictly internal by default unless the user explicitly asks to see planning notes.

---

## 5. Architectural Sensitivity Analysis

The v4.2.0 results highlight how prompt compilation interacts with model capacity, baseline ceiling effects, and two-step self-compilation (Lee et al., 2026; Ugare & Chandra, 2026):

### Tier A: Frontier Session Architectures (`gemini-3.8`, `argon-4-low`, `gpt-6-astra-max`)
- **Quantitative Profile**: `36` pairs, Baseline Mean **22.14/25**, Optimized Mean **24.50/25**, Mean Delta **+2.36/25** (`Model-Cluster 95% CI: [+0.92, +3.29]`, `Two-Way Block 95% CI: [+1.00, +3.38]`), **31W-4T-1L (86.1% win rate)**, Average Word Overhead **1.65x**.
- **Behavioral Mechanism**: Frontier models treat `[P]` and `[T]` blocks as concise analytical indexes, keep Mode 1 expansion between **1.45x and 1.91x**, preserve embedded user data during compilation, and translate verification gates into concrete deliverables.
- **High-Ceiling Behavior (`gpt-6-astra-max`)**: When a model already scores **22.75/25** at baseline (and was evaluated in-session without blinding on 11/12 tasks), heavy scaffolding offers limited upside (+0.92 overall delta, `7W-4T-1L`), delivering its clearest value on multi-constraint audit and concurrency tasks (Test 8 Document Analysis +3.0, Test 12 Concurrency +3.0, Test 7 NIST +2.0) while losing -1.0 on Test 2 where the baseline already scored 25/25.

### Tier B: Mid-to-Large Open-Weights & MoE Cloud Architectures (`gemma4:31b-cloud`, `mistral-large-4:cloud`, `glm-5.3:cloud`, `kimi-k3:cloud`, `beam:cloud`)
- **Quantitative Profile**: Baseline Means **21.50 to 23.08/25**, Optimized Means **19.82 to 22.08/25**, Mean Deltas **-0.33 to -2.45/25**, Word Overheads **0.85x to 4.14x** (API Token Ratios **1.24x to 5.86x**).
- **Behavioral Mechanism**: These models already achieve strong zero-shot baselines (>22/25) and post substantial wins when the compiled structure is proportional to the task: `gemma4:31b-cloud` won 6 of 12 tests (including +7.0 on Test 12, +5.0 on Test 7 NIST, +4.0 on Test 5 Research) at a **0.85x** word ratio (`1.24x` token ratio); `mistral-large-4:cloud` won Test 10 Creative (+4.0 at 0.63x), Test 2 Financial (+3.0), and Test 9 Lite (+2.0 at 0.87x); `kimi-k3:cloud` won Test 1 Code Review (+5.0), Test 2 Financial (+4.0), and Test 6 Business (+3.0).
- **Vulnerability (Step B Self-Compilation Drift)**: In the isolated 2-step runner (`Raw Prompt -> Step B Optimized Prompt -> Step C Optimized Response`), smaller or mid-tier compilers frequently over-rewrote the user's prompt, either stripping secondary requirements (`mistral-large-4:cloud` -12.0 on Test 4 Legal) or demanding repetitive multi-page tables (`glm-5.3:cloud` regressing on five 24-25 point baselines).

### Tier C: Flash & Compact Open Cloud Models (`glm-5.3-flash:cloud`, `minimax-m3.1-flash:cloud`, `deepseek-v4.1-flash:1017-cloud`, `deepseek-v4.1-flash:cloud`, `muse-spark-open:cloud`, `gpt-oss:20b-cloud`)
- **Quantitative Profile**: Mean Deltas **-0.46 to -4.33/25**, with extreme variance in word overhead (**0.43x** on `gpt-oss:20b-cloud` to **8.78x** words / **12.18x** tokens on `minimax-m3.1-flash:cloud`).
- **Behavioral Mechanism**:
  - `glm-5.3-flash:cloud` posted a **6W-1T-2L record (+1.50 mean delta)** across analytical Tests 1 to 9, demonstrating that flash models benefit from proportional structure, while Test 11 (-14.0) and Test 10 (-4.0) dragged its overall mean to -0.46.
  - `minimax-m3.1-flash:cloud` (`8.78x` words, `12.18x` tokens) and both `deepseek-v4.1-flash` variants (`4.43x` and `4.92x` words) suffered runaway template amplification when forced into Mode 1 Max Certificate on simple inputs.
  - Conversely, `gpt-oss:20b-cloud` (`0.43x` words, 9/12 completed) suffered Step B prompt over-truncation, dropping context needed by Step C.

---

## 6. Systematic Failure Modes Observed

Across the 164 evaluated pairs in v4.2.0, six concrete failure modes account for the observed regressions and measurement gaps:

1. **Compiler Requirement Deletion on Test 11 (`CLAUDE.md`) and Over-Aggressive Step 2 Pruning (-8.91 on Cloud, 0W-0T-11L)**:
   - *Mechanism*: Template 11 instructed the compiler to delete explicitly requested project overview, directory structure, and PEP8 sections. More broadly, `SKILL.md` Step 2 previously directed the compiler to strip user-requested answer ordering, business context, and timeline constraints while Step 4 required preserving all constraints. Dropping user-requested deliverables or decision-relevant operational constraints (budget, latency, timeline, clinical urgency ordering) directly reduces completeness and utility.
2. **Disproportionate Mode 1 Scaffolding & Cross-Section Fact Repetition (3.57x Words / 5.22x Tokens on Cloud)**:
   - *Mechanism*: Forcing full `[P1]`-`[P4]` and `[T1]`-`[T3]` certificates onto compact tasks (such as Test 1's 12-line bug fix or Test 3's urgent clinical scenario) caused cloud models to repeat the same facts three times across Premises, Traces, and Conclusions, lowering Structure by **-1.40 / 5.0** and Actionability by **-0.80 / 5.0**.
3. **Mode 4 (`[NT0]` Verbalized Sampling) Backstage Leakage into Final Copy (Test 10: -2.50 on Cloud)**:
   - *Mechanism*: Emitting visible `[BACKSTAGE SCAFFOLD]` candidate probabilities and planning notes above a creative deliverable polluted the final artifact when the user only requested the finished product description.
4. **High-Baseline Ceiling & Step B Self-Compilation Drift (Tests 4, 5, 6, 8)**:
   - *Mechanism*: When baseline responses already scored 23-25/25, two-step self-compilation by smaller models occasionally dropped secondary questions or over-constrained the output format, turning near-ceiling baselines into losses.
5. **Evaluation Harness Confounders (Self-Judging, Column-Header Leakage, Unstripped Markers, and Pooled Strata)**:
   - *Mechanism*: Pooling in-session unblinded self-evaluations (`gpt-6-astra-max`) with isolated cloud runs, using `"Baseline"` / `"Optimized"` column headers inside the judge prompt table, leaving `[P1]`/`[T1]` markers visible to self-judges, and computing i.i.d. cell-level bootstrap CIs overstated precision and left residual evaluation bias.
6. **Evaluator Arithmetic & Sign-Inversion Formatting Errors (79 Score Quality Flags in `AGGREGATED_METRICS.md`)**:
   - *Mechanism*: Multiple open-weights judges wrote inverted signs in the Markdown `Delta` column (`Candidate A minus Candidate B` instead of `Candidate B minus Candidate A`) or miscalculated row totals (`gpt-oss:20b-cloud` Test 9). `aggregate_results.py` deterministically recomputes all totals and deltas from the parsed per-dimension scores and now accounts for `blind_mapping` swap order when auditing written `TOTAL` rows.

---

## 7. Implemented v4.3.0 Skill & Benchmark Upgrades

Based on the empirical findings above and the five methodological audit recommendations, `make-prompt-better` v4.3.0 implements the following architectural and harness upgrades:

### 7.1 Requirement Preservation & Sanitizer Repair (`make-prompt-better/SKILL.md` & `references/`)
1. **Invariant #1 (`[REQ-PRESERVE]`)**: Made **Requirement Preservation** the compiler's first core invariant in `SKILL.md`: preserve every user-requested deliverable, sub-question, operational constraint (budget, latency, timeline, target audience), and output ordering requirement. Replaced the rigid 1-to-1 trace rule with a lightweight **many-to-one Requirement-to-Output Mapping Check** in Step 4 so multiple requirements can map cleanly to a single section, table, or executable test without omitting any item.
2. **Repaired Step 2 Goal-Blind Sanitizer**: Distinguished **biasing evaluative pressure** (sycophancy triggers, emotional pleading, presupposed conclusions, artificial flattery, which are stripped per Cao, Jiang & Xu, 2026) from **decision-relevant operational constraints and user-requested ordering** (which are strictly preserved).
3. **Dual Context Binding (`Portable` vs. `Working-Context`)**: Updated Step 0 and Step 4 to support both **Portable Prompts** (self-contained prompts for chat UIs or isolated APIs that embed required data verbatim) and **Working-Context Prompts** (prompts inside a live repository or IDE session that bind exact `file:line` paths and commands without bloating the prompt with pasted files).

### 7.2 Proportional Structure & Domain Template Repairs (`make-prompt-better/references/domain-templates.md`)
1. **Proportional Certificate Depth & Anti-Redundancy (Templates 1 to 9)**: Added an explicit **Anti-Redundancy Rule** to Templates 1 through 9: state each fact once in `[P]` and reference it by ID (`[P1]`, `[T1]`) rather than repeating paragraphs across Premises, Traces, and Conclusions. Avoided arbitrary fixed word caps (450/750 words) and rigid parameter-count bans in favor of task-proportional depth (`Mode 2 Lite` as the default for standard analytical tasks; `Mode 1 Max` reserved for high-stakes multi-constraint audits).
2. **Clinical Acuity-First Ordering (Template 7 Medical Reasoning)**: Updated Template 7 so urgent/emergent clinical scenarios place immediate life-safety and stabilization actions **first** at the top of the response before structured differential and premise traces.
3. **Internal-by-Default Creative Backstage (Template 10 Mode 4)**: Updated Mode 4 and Template 10 so `[NT0]` Verbalized Sampling (`p <= 0.15`) and `[SC0]` anti-SlopShape planning are performed **internally** (in hidden thinking tokens or silent preparation) by default, outputting **only the clean finished creative deliverable** unless the user explicitly asks to see planning notes. Permitted vivid sensory/experiential translation of supplied features while forbidding only unverified factual or clinical claims.
4. **Compact `Section 0` Requirement Fulfillment (Template 11 `[CONTEXT-FILES]`)**: Repaired the Test 11 defect in Mode 3 Pattern B and Template 11: when a user explicitly asks for a project overview, directory layout, or style convention in `AGENTS.md`/`CLAUDE.md`, the compiled prompt includes a compact **`## 0. Requested Scope & Conventions Summary` (`<= 5` lines)** that fulfills those requested items directly before devoting the remainder of the file to non-inferable commands, hard invariants, and verification gates (Gloaguen et al., 2026).
5. **Exact Numeric Accounting in Concurrency Harnesses (Template 12 Mode 3)**: Retained the code-first `[V1]`->`[V2]` harness architecture (+1.83 overall delta) and added explicit integer / exact rational accounting checks to prevent floating-point capacity drift (`2**53 + 1`).

### 7.3 Benchmark Measurement & Statistical Engine Repairs (`research/benchmark/v4/`)
1. **Neutral Judge Table Headers (`blind_stats_engine.py`)**: Replaced `"Baseline (1-5)"` and `"Optimized (1-5)"` in `build_blind_eval_instruction` with neutral **`"Candidate A (1-5)"`**, **`"Candidate B (1-5)"`**, and **`"Delta (B - A)"`** headers to eliminate column-label anchoring.
2. **Cluster-Robust Confidence Intervals & Permutation Tests (`blind_stats_engine.py` & `aggregate_results.py`)**: Added `cluster_bootstrap_mean_ci` (resampling by `model_id` or `task_id`), `two_way_block_bootstrap_ci` (jointly resampling models and tasks), and `cluster_paired_permutation_p_value`, reported separately by protocol stratum in `AGGREGATED_METRICS.md`.
3. **Honest Token Telemetry (`aggregate_results.py` & `blind_stats_engine.py`)**: Removed hardcoded `100`-token synthetic fallbacks; missing `eval_count` values are stored as `None` and excluded from token-efficiency ratios.
4. **Natural Router Mode (`--unprescribed-routing` in `run_ollama_benchmarks.py`)**: Added `--unprescribed-routing` so benchmarks can test the skill's own Step 1 mode router without `TEST_MODE_OVERRIDES`.
5. **Saved-Output Re-Judging Ablation Harness (`rejudge_saved_outputs.py`)**: Created a standalone script to re-score identical saved `(baseline, optimized)` response pairs under unblinded vs. 2-pass swapped neutral `Candidate A`/`B` vs. marker-stripped (`--strip-markers`) vs. independent-judge conditions, isolating pure evaluation bias from generation variance.
