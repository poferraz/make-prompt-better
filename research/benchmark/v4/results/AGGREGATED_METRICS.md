# Aggregated Cross-Architecture Benchmark Data (v4.3.0 Audited Provenance)

Methodological Disclosures: All runs in this directory are self-evaluated (`judge_model == generator_model`) unless otherwise noted in the `Judge` column. In-session runs (`argon-4-low`, `gemini-3.8`, `gpt-6-astra-max`) were generated and scored in session contexts (`gpt-6-astra-max` explicitly notes unblinded in-session self-scoring across 11 of 12 cases) and should not be pooled with isolated API runner calls as a single controlled experiment. Isolated Ollama Cloud runs isolate each generation call and randomize candidate order (`Candidate A` vs. `Candidate B`), though historical Oct 31 runs retained `Baseline`/`Optimized` column labels in the judge prompt and visible certificate tags. Partial runs (`gpt-oss:20b-cloud` 9/12, `kimi-k3:cloud` 11/12) cover subsets of the 12-task suite. Word Overhead is an output word-count ratio, not an end-to-end token-cost ratio (prompt compilation tokens and missing API token counts are excluded rather than synthesized).

## 1. Overall Model Leaderboard (Stratified by Protocol Provenance)

| Model | Protocol | Judge | Completed Tests | Baseline Avg (/25) | Optimized Avg (/25) | Delta (/25) | Gain (%) | Avg Word Overhead | Win-Tie-Loss |
|-------|----------|-------|-----------------|--------------------|---------------------|-------------|----------|-------------------|--------------|
| `argon-4-low` | In-Session Self-Eval (Markdown) | Self | 12/12 | 22.12 | 25.0 | +2.88 | +13% | 1.61x | 12W-0T-0L |
| `beam:cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 21.5 | 19.92 | -1.58 | -7.4% | 2.11x | 4W-0T-8L |
| `deepseek-v4.1-flash:1017-cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 22.75 | 19.92 | -2.83 | -12.5% | 4.43x | 3W-1T-8L |
| `deepseek-v4.1-flash:cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 23.17 | 18.83 | -4.33 | -18.7% | 4.92x | 2W-0T-10L |
| `gemini-3.8` | In-Session Self-Eval (Markdown) | Self | 12/12 | 21.54 | 24.83 | +3.29 | +15.3% | 1.55x | 12W-0T-0L |
| `gemma4:31b-cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 22.42 | 22.08 | -0.33 | -1.5% | 0.85x | 6W-0T-6L |
| `glm-5.3:cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 23.08 | 21.08 | -2 | -8.7% | 3.98x | 3W-1T-8L |
| `glm-5.3-flash:cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 21.54 | 21.08 | -0.46 | -2.1% | 3.76x | 6W-1T-5L |
| `gpt-6-astra-max` | In-Session Unblinded Self-Eval | Self | 12/12 | 22.75 | 23.67 | +0.92 | +4% | 1.79x | 7W-4T-1L |
| `gpt-oss:20b-cloud` | Isolated Anonymized Self-Judged | Self | 9/12 | 22.89 | 18.56 | -4.33 | -18.9% | 0.43x | 1W-1T-7L |
| `kimi-k3:cloud` | Isolated Anonymized Self-Judged | Self | 11/12 | 22.27 | 19.82 | -2.45 | -11% | 4.14x | 3W-0T-8L |
| `minimax-m3.1-flash:cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 22.5 | 20.67 | -1.83 | -8.1% | 8.78x | 4W-0T-8L |
| `mistral-large-4:cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 22.42 | 20.25 | -2.17 | -9.7% | 2.95x | 4W-0T-8L |
| `muse-spark-open:cloud` | Isolated Anonymized Self-Judged | Self | 12/12 | 20.92 | 16.92 | -4 | -19.1% | 2.19x | 2W-1T-9L |

## 2. Per-Test Score Delta Matrix (Optimized minus Baseline, /25)

| Model | T1 Code | T2 Fin | T3 Med | T4 Legal | T5 Res | T6 Biz | T7 NIST | T8 Doc | T9 Lite | T10 Creative | T11 Context | T12 LRM |
|-------|---------|--------|--------|----------|--------|--------|---------|--------|---------|--------------|-------------|---------|
| `argon-4-low` | +2.5 (25.0) | +3 (25.0) | +2 (25.0) | +3 (25.0) | +2.5 (25.0) | +2.5 (25.0) | +2.5 (25.0) | +3.5 (25.0) | +2 (25.0) | +3 (25.0) | +4.5 (25.0) | +3.5 (25.0) |
| `beam:cloud` | +3 (24.0) | +3 (24.0) | -1 (21.0) | -5 (19.0) | -5 (14.0) | -5 (18.0) | -1 (20.0) | +4 (24.0) | -6 (16.0) | -2 (20.0) | -11 (14.0) | +7 (25.0) |
| `deepseek-v4.1-flash:1017-cloud` | +0 (23.0) | +2 (24.0) | -8 (16.0) | -1 (23.0) | -5 (19.0) | -11 (12.0) | -1 (21.0) | +3 (24.0) | -5 (19.0) | -5 (20.0) | -10 (13.0) | +7 (25.0) |
| `deepseek-v4.1-flash:cloud` | -2 (20.0) | -1 (23.0) | -4 (19.0) | +2 (23.0) | -6 (16.0) | -9 (15.0) | -3 (20.0) | -15 (10.0) | -1 (22.0) | -6 (19.0) | -10 (15.0) | +3 (24.0) |
| `gemini-3.8` | +2.5 (25.0) | +3.5 (24.5) | +2.5 (25.0) | +3.5 (25.0) | +3.5 (24.5) | +3.5 (25.0) | +2.5 (25.0) | +3 (25.0) | +3 (25.0) | +3 (24.0) | +4.5 (25.0) | +4.5 (25.0) |
| `gemma4:31b-cloud` | +1 (24.0) | -1 (23.0) | -4 (20.0) | -2 (21.0) | +4 (23.0) | +1 (23.0) | +5 (25.0) | +2 (24.0) | -7 (17.0) | -3 (22.0) | -7 (18.0) | +7 (25.0) |
| `glm-5.3:cloud` | -3 (21.0) | +1 (23.0) | +2 (24.0) | -2 (21.0) | +0 (22.0) | +1 (24.0) | -1 (21.0) | -5 (19.0) | -4 (20.0) | -1 (21.0) | -6 (18.0) | -6 (19.0) |
| `glm-5.3-flash:cloud` | +3 (23.0) | -1 (22.0) | +1 (22.0) | -2 (20.0) | +0 (21.0) | +2.5 (24.0) | +3 (22.0) | +4 (24.0) | +3 (24.0) | -4 (19.0) | -14 (11.0) | -1 (21.0) |
| `gpt-6-astra-max` | +0 (23.0) | -1 (24.0) | +1 (24.0) | +0 (23.0) | +1 (23.0) | +1 (24.0) | +2 (24.0) | +3 (25.0) | +1 (24.0) | +0 (23.0) | +0 (23.0) | +3 (24.0) |
| `gpt-oss:20b-cloud` | -4 (21.0) | - | +7 (25.0) | -2 (20.0) | -6 (19.0) | +0 (21.0) | -10 (12.0) | -11 (14.0) | -3 (20.0) | - | -10 (15.0) | - |
| `kimi-k3:cloud` | +5 (24.0) | +4 (24.0) | -5 (19.0) | -6 (18.0) | -8 (16.0) | +3 (24.0) | -3 (19.0) | -2 (20.0) | -3 (21.0) | -2 (20.0) | -10 (13.0) | - |
| `minimax-m3.1-flash:cloud` | -3 (22.0) | +4 (24.0) | -2 (22.0) | +1 (22.0) | +1 (19.0) | -5 (19.0) | -7 (16.0) | -2 (22.0) | +2 (24.0) | -1 (21.0) | -8 (17.0) | -2 (20.0) |
| `mistral-large-4:cloud` | +1 (24.0) | +3 (24.0) | -5 (18.0) | -12 (12.0) | -1 (20.0) | -5 (16.0) | -2 (21.0) | -2 (21.0) | +2 (23.0) | +4 (24.0) | -8 (17.0) | -1 (23.0) |
| `muse-spark-open:cloud` | -6 (17.0) | +0 (21.0) | -2 (20.0) | -9 (13.0) | -14 (5.0) | -4 (16.0) | +5 (23.0) | +4 (23.0) | -10 (13.0) | -5 (15.0) | -4 (17.0) | -3 (20.0) |

## 3. Score Quality Flags

The leaderboard retains the saved per-dimension scores and deterministically recomputes totals and deltas (`optimized minus baseline`). Flagged entries below indicate where a model's written delta or total column in raw markdown disagreed with its per-dimension scores.

- `beam:cloud`, Test 8: written accuracy delta 1 differs from second-column minus first-column -1.
- `beam:cloud`, Test 8: written completeness delta 1 differs from second-column minus first-column -1.
- `beam:cloud`, Test 8: written structure delta 1 differs from second-column minus first-column -1.
- `beam:cloud`, Test 8: written actionability delta -1 differs from second-column minus first-column 1.
- `beam:cloud`, Test 8: written traceability delta 2 differs from second-column minus first-column -2.
- `beam:cloud`, Test 8: written total (/25) delta 4 differs from second-column minus first-column -4.
- `beam:cloud`, Test 11: written total (/25) delta 11 differs from second-column minus first-column -11.
- `deepseek-v4.1-flash:cloud`, Test 8: written actionability delta 1 differs from second-column minus first-column 2.
- `deepseek-v4.1-flash:cloud`, Test 11: written accuracy delta 1 differs from second-column minus first-column -1.
- `deepseek-v4.1-flash:cloud`, Test 11: written completeness delta 3 differs from second-column minus first-column -3.
- `deepseek-v4.1-flash:cloud`, Test 11: written structure delta 2 differs from second-column minus first-column -2.
- `deepseek-v4.1-flash:cloud`, Test 11: written actionability delta 2 differs from second-column minus first-column -2.
- `deepseek-v4.1-flash:cloud`, Test 11: written traceability delta 2 differs from second-column minus first-column -2.
- `deepseek-v4.1-flash:cloud`, Test 11: written total (/25) delta 10 differs from second-column minus first-column -10.
- `gemma4:31b-cloud`, Test 2: written completeness delta 1 differs from second-column minus first-column -1.
- `gemma4:31b-cloud`, Test 2: written structure delta 1 differs from second-column minus first-column -1.
- `gemma4:31b-cloud`, Test 2: written actionability delta -1 differs from second-column minus first-column 1.
- `gemma4:31b-cloud`, Test 2: written total (/25) delta 1 differs from second-column minus first-column -1.
- `gemma4:31b-cloud`, Test 5: written accuracy delta 1 differs from second-column minus first-column -1.
- `gemma4:31b-cloud`, Test 5: written completeness delta -1 differs from second-column minus first-column 1.
- `gemma4:31b-cloud`, Test 5: written structure delta 1 differs from second-column minus first-column -1.
- `gemma4:31b-cloud`, Test 5: written traceability delta 3 differs from second-column minus first-column -3.
- `gemma4:31b-cloud`, Test 5: written total (/25) delta 4 differs from second-column minus first-column -4.
- `gemma4:31b-cloud`, Test 11: written completeness delta 3 differs from second-column minus first-column -3.
- `gemma4:31b-cloud`, Test 11: written structure delta 1 differs from second-column minus first-column -1.
- `gemma4:31b-cloud`, Test 11: written actionability delta 1 differs from second-column minus first-column -1.
- `gemma4:31b-cloud`, Test 11: written traceability delta 2 differs from second-column minus first-column -2.
- `gemma4:31b-cloud`, Test 11: written total (/25) delta 7 differs from second-column minus first-column -7.
- `glm-5.3:cloud`, Test 12: written accuracy delta 1 differs from second-column minus first-column -1.
- `glm-5.3:cloud`, Test 12: written completeness delta 2 differs from second-column minus first-column -2.
- `glm-5.3:cloud`, Test 12: written structure delta 2 differs from second-column minus first-column -2.
- `glm-5.3:cloud`, Test 12: written actionability delta 1 differs from second-column minus first-column -1.
- `glm-5.3:cloud`, Test 12: written total (/25) delta 6 differs from second-column minus first-column -6.
- `glm-5.3-flash:cloud`, Test 6: written accuracy delta 0.5 differs from second-column minus first-column -0.5.
- `glm-5.3-flash:cloud`, Test 6: written completeness delta 0.5 differs from second-column minus first-column -0.5.
- `glm-5.3-flash:cloud`, Test 6: written structure delta -0.5 differs from second-column minus first-column 0.5.
- `glm-5.3-flash:cloud`, Test 6: written actionability delta 0.5 differs from second-column minus first-column -0.5.
- `glm-5.3-flash:cloud`, Test 6: written traceability delta 1.5 differs from second-column minus first-column -1.5.
- `glm-5.3-flash:cloud`, Test 6: written total (/25) delta 2.5 differs from second-column minus first-column -2.5.
- `gpt-oss:20b-cloud`, Test 5: written completeness delta 2 differs from second-column minus first-column -2.
- `gpt-oss:20b-cloud`, Test 5: written structure delta 2 differs from second-column minus first-column -2.
- `gpt-oss:20b-cloud`, Test 5: written actionability delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 5: written traceability delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 5: written total (/25) delta 6 differs from second-column minus first-column -6.
- `gpt-oss:20b-cloud`, Test 6: written accuracy delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 6: written completeness delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 6: written structure delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 6: written actionability delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 6: written traceability delta -4 differs from second-column minus first-column 4.
- `gpt-oss:20b-cloud`, Test 7: written traceability delta 2 differs from second-column minus first-column -2.
- `gpt-oss:20b-cloud`, Test 9: written baseline total 24 differs from the saved total 23.
- `gpt-oss:20b-cloud`, Test 9: written accuracy delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 9: written completeness delta 2 differs from second-column minus first-column -2.
- `gpt-oss:20b-cloud`, Test 9: written structure delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 9: written actionability delta 1 differs from second-column minus first-column -1.
- `gpt-oss:20b-cloud`, Test 9: written total (/25) delta 4 differs from second-column minus first-column -4.
- `kimi-k3:cloud`, Test 1: written accuracy delta 1 differs from second-column minus first-column -1.
- `kimi-k3:cloud`, Test 1: written completeness delta 2 differs from second-column minus first-column -2.
- `kimi-k3:cloud`, Test 1: written structure delta -1 differs from second-column minus first-column 1.
- `kimi-k3:cloud`, Test 1: written actionability delta 1 differs from second-column minus first-column -1.
- `kimi-k3:cloud`, Test 1: written traceability delta -1 differs from second-column minus first-column -2.
- `kimi-k3:cloud`, Test 1: written total (/25) delta 5 differs from second-column minus first-column -5.
- `kimi-k3:cloud`, Test 7: written accuracy delta 1 differs from second-column minus first-column -1.
- `kimi-k3:cloud`, Test 7: written completeness delta 1 differs from second-column minus first-column -1.
- `kimi-k3:cloud`, Test 7: written structure delta 2 differs from second-column minus first-column -2.
- `kimi-k3:cloud`, Test 7: written traceability delta -1 differs from second-column minus first-column 1.
- `kimi-k3:cloud`, Test 7: written total (/25) delta 3 differs from second-column minus first-column -3.
- `minimax-m3.1-flash:cloud`, Test 5: written accuracy delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 5: written structure delta -2 differs from second-column minus first-column 2.
- `minimax-m3.1-flash:cloud`, Test 5: written actionability delta -1 differs from second-column minus first-column 1.
- `minimax-m3.1-flash:cloud`, Test 5: written traceability delta 3 differs from second-column minus first-column -3.
- `minimax-m3.1-flash:cloud`, Test 5: written total (/25) delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 6: written accuracy delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 6: written structure delta 2 differs from second-column minus first-column -2.
- `minimax-m3.1-flash:cloud`, Test 6: written actionability delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 6: written traceability delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 6: written total (/25) delta 5 differs from second-column minus first-column -5.
- `minimax-m3.1-flash:cloud`, Test 7: written accuracy delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 7: written completeness delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 7: written structure delta 2 differs from second-column minus first-column -2.
- `minimax-m3.1-flash:cloud`, Test 7: written actionability delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 7: written traceability delta 2 differs from second-column minus first-column -2.
- `minimax-m3.1-flash:cloud`, Test 7: written total (/25) delta 7 differs from second-column minus first-column -7.
- `minimax-m3.1-flash:cloud`, Test 9: written accuracy delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 9: written completeness delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 9: written structure delta -1 differs from second-column minus first-column 1.
- `minimax-m3.1-flash:cloud`, Test 9: written traceability delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 9: written total (/25) delta 2 differs from second-column minus first-column -2.
- `minimax-m3.1-flash:cloud`, Test 10: written accuracy delta -1 differs from second-column minus first-column 1.
- `minimax-m3.1-flash:cloud`, Test 10: written structure delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 10: written actionability delta 1 differs from second-column minus first-column -1.
- `minimax-m3.1-flash:cloud`, Test 10: written total (/25) delta 1 differs from second-column minus first-column -1.

## 4. Protocol-Stratified & Cluster-Robust Statistical Summary

Because the benchmark crosses $M$ models with $T = 12$ fixed tasks (1 case per domain), cell-level i.i.d. resampling understates uncertainty. We report **Model-Cluster Bootstrap 95% CIs**, **Two-Way Block Bootstrap 95% CIs (resampling models and tasks)**, and **Cluster-Level Sign-Flip Permutation p-values** separately for each protocol stratum:

| Stratum | Pairs (Models x Tasks) | Baseline Mean | Optimized Mean | Mean Delta | Cell Bootstrap 95% CI | Model-Cluster 95% CI | Two-Way Block 95% CI | Model Sign-Flip p | Task Sign-Flip p | Win-Tie-Loss (Win %) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **In-Session Self-Eval Track** | 36 (3M, 12T) | 22.14/25 | 24.5/25 | **+2.3611** | `[+1.9028, +2.7917]` | `[+0.9167, +3.2917]` | `[+1, +3.375]` | `0.2500` | `0.0005` | 31W-4T-1L (86.1%) |
| **Isolated Runner Track (Ollama Cloud)** | 128 (11M, 12T) | 22.3/25 | 19.95/25 | **-2.3477** | `[-3.1797, -1.5156]` | `[-3.128, -1.5731]` | `[-4.1145, -0.6562]` | `0.0010` | `0.0073` | 38W-5T-85L (29.7%) |
| **Combined Descriptive Pool (All 14)** | 164 (14M, 12T) | 22.27/25 | 20.95/25 | **-1.314** | `[-2.0427, -0.6067]` | `[-2.4715, -0.0843]` | `[-3.1463, +0.3452]` | `0.0555` | `0.0469` | 69W-9T-86L (42.1%) |

- **Measured API Output Token Telemetry (`eval_count` > 0)**: Available on `128/164` pairs (Mean Output Token Ratio: `5.22x`, Mean Lift per 1k Extra Output Tokens: `-0.14`). In-session Markdown runs without API token telemetry are excluded rather than assigned synthetic placeholders.

### Parameter-Tier Stratification (Descriptive Pool)

| Parameter Tier | Pairs | Mean Delta (/25) | Cell 95% Bootstrap CI | Win Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| Tier 1: Sub-14B Edge & Flash | 48 | -2.3646 | [-3.75, -1.0417] | 31.2% |
| Tier 2: 14B-70B Open-Weights | 69 | -2.3188 | [-3.4638, -1.2609] | 29.0% |
| Tier 3: Frontier & Large Reasoning Models | 47 | +1.234 | [+0.2553, +2.0638] | 72.3% |
