# Aggregated v4.0 Cross-Architecture Benchmark Data

Scores are self-evaluations by the models that generated the responses, and evaluators see which response is optimized. The Ollama runner isolates its generation calls, while the session protocol uses a single conversation. Older Ollama records may not contain the exact prompt sent after input guardrails. Partial runs may cover different tests, so their averages are not directly comparable. Averages below come from per-test records; mean paired deltas are rounded independently, and model-written narratives may contain conflicting arithmetic. Overhead is an output word-count ratio, not a token-cost ratio; missing ratios are excluded from its average.

## 1. Overall Model Leaderboard

| Model | Completed Tests | Baseline Avg (/25) | Optimized Avg (/25) | Delta (/25) | Gain (%) | Avg Word Overhead | Win-Tie-Loss |
|-------|-----------------|--------------------|---------------------|-------------|----------|--------------|--------------|
| `beam:cloud` | 12/12 | 19.42 | 21.0 | +1.58 | +8.2% | 1.98x | 8W-1T-3L |
| `claude-opus` | 12/12 | 21.0 | 23.58 | +2.58 | +12.3% | 1.83x | 10W-2T-0L |
| `deepseek-v4.1-flash:1017-cloud` | 12/12 | 22.0 | 21.58 | -0.42 | -1.9% | 5.92x | 7W-1T-4L |
| `deepseek-v4.1-flash:cloud` | 12/12 | 21.08 | 21.38 | +0.29 | +1.4% | 2.91x | 8W-1T-3L |
| `gemini-3.8` | 12/12 | 19.38 | 24.67 | +5.29 | +27.3% | 2.04x | 12W-0T-0L |
| `gemma4:31b-cloud` | 12/12 | 20.62 | 22.12 | +1.5 | +7.3% | 0.79x | 8W-0T-4L |
| `glm-5.3:cloud` | 12/12 | 21.38 | 23.67 | +2.29 | +10.7% | 3.84x | 12W-0T-0L |
| `glm-5.3-flash:cloud` | 12/12 | 21.5 | 23.5 | +2 | +9.3% | 3.5x | 11W-0T-1L |
| `gpt-6.1-terra` | 12/12 | 23.58 | 23.67 | +0.08 | +0.4% | 1.35x | 2W-8T-2L |
| `gpt-oss:20b-cloud` | 12/12 | 20.08 | 18.29 | -1.79 | -8.9% | 0.59x | 6W-0T-6L |
| `kimi-k3:cloud` | 12/12 | 21.17 | 23.54 | +2.38 | +11.2% | 3.77x | 10W-0T-2L |
| `meta-muse-wonder-1.0-max` | 12/12 | 21.42 | 24.83 | +3.42 | +16% | 1.61x | 12W-0T-0L |
| `minimax-m3.1-flash:cloud` | 12/12 | 21.0 | 22.12 | +1.12 | +5.4% | 11.93x | 10W-0T-2L |
| `mistral-large-4:cloud` | 12/12 | 21.0 | 22.88 | +1.88 | +8.9% | 3.17x | 9W-1T-2L |
| `muse-spark-open:cloud` | 12/12 | 19.25 | 20.08 | +0.83 | +4.3% | 1.98x | 9W-0T-3L |

## 2. Per-Test Score Delta Matrix (Optimized minus Baseline, /25)

| Model | T1 Code | T2 Fin | T3 Med | T4 Legal | T5 Res | T6 Biz | T7 NIST | T8 Doc | T9 Lite | T10 Creative | T11 Context | T12 LRM |
|-------|---------|--------|--------|----------|--------|--------|---------|--------|---------|--------------|-------------|---------|
| `beam:cloud` | +4.5 (21.5) | +2 (23.5) | +4.5 (23.0) | +5 (22.5) | -11.5 (10.0) | -0.5 (20.5) | +3 (23.5) | +0 (21.5) | -1.5 (18.0) | +6.5 (22.0) | +1.5 (25.0) | +5.5 (21.0) |
| `claude-opus` | +0 (24.0) | +2 (24.0) | +1 (24.0) | +3 (24.0) | +2 (22.0) | +3 (24.0) | +0 (24.0) | +3 (24.0) | +2 (24.0) | +2 (21.0) | +6 (24.0) | +7 (24.0) |
| `deepseek-v4.1-flash:1017-cloud` | +1 (24.0) | +3 (24.0) | +0 (21.5) | -6 (16.0) | +2 (24.0) | +0.5 (21.5) | +4 (23.5) | +1.5 (24.0) | -3 (21.5) | +4.5 (23.5) | -9 (14.5) | -3.5 (21.0) |
| `deepseek-v4.1-flash:cloud` | +5 (24.5) | +4.5 (24.5) | -16.5 (6.5) | -1 (19.0) | +0.5 (22.5) | +0.5 (22.0) | +6 (25.0) | +0.5 (24.5) | +1 (22.0) | +0 (22.5) | +7.5 (25.0) | -4.5 (18.5) |
| `gemini-3.8` | +5 (24.5) | +5.5 (24.5) | +5 (25.0) | +5.5 (24.5) | +5 (24.5) | +4.5 (24.5) | +5 (25.0) | +5 (24.5) | +3.5 (24.5) | +6 (24.5) | +7 (25.0) | +6.5 (25.0) |
| `gemma4:31b-cloud` | -9 (13.0) | +6 (25.0) | +4 (25.0) | -3 (17.0) | -5 (18.0) | +6 (25.0) | +6.5 (25.0) | +5 (25.0) | +3.5 (24.5) | +4 (25.0) | +5 (24.0) | -5 (19.0) |
| `glm-5.3:cloud` | +1 (24.5) | +3 (23.5) | +2.5 (24.0) | +1.5 (22.5) | +1 (22.5) | +5 (23.0) | +2 (22.5) | +3 (24.5) | +2 (24.0) | +3 (24.5) | +2.5 (24.0) | +1 (24.5) |
| `glm-5.3-flash:cloud` | +3 (24.5) | +2 (23.0) | +2 (24.0) | +1.5 (24.5) | +4.5 (23.5) | +3 (23.0) | +2.5 (24.5) | +3.5 (24.5) | +4 (24.0) | +1 (23.0) | -4 (19.5) | +1 (24.0) |
| `gpt-6.1-terra` | +0 (23.0) | +0 (24.0) | +0 (24.0) | +0 (24.0) | +0 (23.0) | +0 (24.0) | +0 (24.0) | +0 (24.0) | +1 (25.0) | -1 (23.0) | -2 (22.0) | +3 (24.0) |
| `gpt-oss:20b-cloud` | +4 (24.0) | -2.5 (17.5) | +3 (23.5) | -4.5 (14.5) | +1.5 (22.0) | +3.5 (21.5) | -6.5 (13.0) | +1 (20.5) | -6 (12.5) | +4.5 (21.0) | -17 (8.0) | -2.5 (21.5) |
| `kimi-k3:cloud` | +3.5 (24.0) | +1.5 (22.0) | +2 (24.0) | +4 (25.0) | -0.5 (22.5) | +2.5 (23.0) | +3.5 (23.5) | +4 (24.5) | +1.5 (23.0) | +4 (25.0) | +3.5 (24.0) | -1 (22.0) |
| `meta-muse-wonder-1.0-max` | +4 (25.0) | +5 (25.0) | +3 (25.0) | +4 (25.0) | +3 (24.0) | +1 (25.0) | +1 (25.0) | +1 (25.0) | +1 (25.0) | +7 (25.0) | +7 (24.0) | +4 (25.0) |
| `minimax-m3.1-flash:cloud` | +1 (24.0) | +0.5 (23.5) | +0.5 (22.5) | +3.5 (22.5) | +2.5 (21.5) | +1 (21.0) | +4 (23.5) | +1 (24.0) | +5.5 (23.5) | +5 (23.5) | -2.5 (22.0) | -8.5 (14.0) |
| `mistral-large-4:cloud` | +3 (24.0) | +8 (25.0) | +0 (22.5) | -0.5 (20.0) | +4.5 (22.5) | +3 (24.0) | +2.5 (23.5) | +1.5 (24.0) | +1.5 (23.5) | +1.5 (23.5) | +5 (25.0) | -7.5 (17.0) |
| `muse-spark-open:cloud` | +3 (22.0) | +3 (23.0) | +1 (20.5) | +3 (23.0) | -5.5 (12.5) | +3.5 (21.5) | +1 (21.5) | +1.5 (21.0) | +2.5 (22.5) | +8.5 (22.0) | -8.5 (14.5) | -3 (17.0) |

## 3. Score Quality Flags

The leaderboard retains the saved scores, including any flagged entries.

- `beam:cloud`, Test 5: written accuracy delta 2.5 differs from optimized minus baseline -2.5.
- `beam:cloud`, Test 5: written completeness delta 3.5 differs from optimized minus baseline -3.5.
- `beam:cloud`, Test 5: written structure delta 2.5 differs from optimized minus baseline -2.5.
- `beam:cloud`, Test 5: written actionability delta 2.5 differs from optimized minus baseline -2.5.
- `beam:cloud`, Test 5: written traceability delta 0.5 differs from optimized minus baseline -0.5.
- `beam:cloud`, Test 5: written total delta 11.5 differs from optimized minus baseline -11.5.
- `deepseek-v4.1-flash:cloud`, Test 3: written accuracy delta 4 differs from optimized minus baseline -4.
- `deepseek-v4.1-flash:cloud`, Test 3: written completeness delta 4 differs from optimized minus baseline -4.
- `deepseek-v4.1-flash:cloud`, Test 3: written structure delta 1.5 differs from optimized minus baseline -1.5.
- `deepseek-v4.1-flash:cloud`, Test 3: written actionability delta 4 differs from optimized minus baseline -4.
- `deepseek-v4.1-flash:cloud`, Test 3: written traceability delta 3 differs from optimized minus baseline -3.
- `deepseek-v4.1-flash:cloud`, Test 3: written total delta 16.5 differs from optimized minus baseline -16.5.
- `gemma4:31b-cloud`, Test 11: written baseline total 24 differs from the saved total 19.
- `glm-5.3-flash:cloud`, Test 5: written baseline total 19.5 differs from the saved total 19.
- `glm-5.3-flash:cloud`, Test 11: written baseline total 24 differs from the saved total 23.5.
- `gpt-oss:20b-cloud`, Test 2: written baseline total 20.5 differs from the saved total 20.
- `gpt-oss:20b-cloud`, Test 2: written accuracy delta 1.5 differs from optimized minus baseline -1.5.
- `gpt-oss:20b-cloud`, Test 2: written completeness delta 2 differs from optimized minus baseline -2.
- `gpt-oss:20b-cloud`, Test 2: written actionability delta 3 differs from optimized minus baseline -3.
- `gpt-oss:20b-cloud`, Test 2: written total delta 3 differs from optimized minus baseline -3.
- `gpt-oss:20b-cloud`, Test 4: written baseline total 18.5 differs from the saved total 19.
- `gpt-oss:20b-cloud`, Test 4: written accuracy delta 2 differs from optimized minus baseline -2.
- `gpt-oss:20b-cloud`, Test 4: written completeness delta 2 differs from optimized minus baseline -2.
- `gpt-oss:20b-cloud`, Test 4: written actionability delta 2.5 differs from optimized minus baseline -2.5.
- `gpt-oss:20b-cloud`, Test 4: written total delta 4 differs from optimized minus baseline -4.
- `gpt-oss:20b-cloud`, Test 7: written baseline total 19 differs from the saved total 19.5.
- `gpt-oss:20b-cloud`, Test 8: written baseline total 19 differs from the saved total 19.5.
- `gpt-oss:20b-cloud`, Test 8: written accuracy delta 0.5 differs from optimized minus baseline -0.5.
- `gpt-oss:20b-cloud`, Test 8: written completeness delta 1 differs from optimized minus baseline -1.
- `gpt-oss:20b-cloud`, Test 8: written structure delta -1 differs from optimized minus baseline 1.
- `gpt-oss:20b-cloud`, Test 8: written actionability delta 0.5 differs from optimized minus baseline -0.5.
- `gpt-oss:20b-cloud`, Test 8: written traceability delta -2 differs from optimized minus baseline 2.
- `gpt-oss:20b-cloud`, Test 8: written total delta -1.5 differs from optimized minus baseline 1.5.
- `gpt-oss:20b-cloud`, Test 9: traceability baseline score 0.5 is outside the 1-5 rubric.
- `gpt-oss:20b-cloud`, Test 9: written optimized total 9.5 differs from the saved total 12.5.
- `gpt-oss:20b-cloud`, Test 9: written accuracy delta 3 differs from optimized minus baseline -3.
- `gpt-oss:20b-cloud`, Test 9: written completeness delta 3.5 differs from optimized minus baseline -3.5.
- `gpt-oss:20b-cloud`, Test 9: written structure delta 0.5 differs from optimized minus baseline -0.5.
- `gpt-oss:20b-cloud`, Test 9: written actionability delta 3.5 differs from optimized minus baseline -3.5.
- `gpt-oss:20b-cloud`, Test 9: written total delta 9 differs from optimized minus baseline -9.
- `gpt-oss:20b-cloud`, Test 11: written accuracy delta 4 differs from optimized minus baseline -4.
- `gpt-oss:20b-cloud`, Test 11: written completeness delta 4 differs from optimized minus baseline -4.
- `gpt-oss:20b-cloud`, Test 11: written structure delta 3 differs from optimized minus baseline -3.
- `gpt-oss:20b-cloud`, Test 11: written actionability delta 3 differs from optimized minus baseline -3.
- `gpt-oss:20b-cloud`, Test 11: written traceability delta 3 differs from optimized minus baseline -3.
- `gpt-oss:20b-cloud`, Test 11: written total delta 17 differs from optimized minus baseline -17.
- `gpt-oss:20b-cloud`, Test 12: written accuracy delta 0.5 differs from optimized minus baseline -0.5.
- `gpt-oss:20b-cloud`, Test 12: written completeness delta 0.5 differs from optimized minus baseline -0.5.
- `gpt-oss:20b-cloud`, Test 12: written structure delta 1 differs from optimized minus baseline -1.
- `gpt-oss:20b-cloud`, Test 12: written actionability delta 0.5 differs from optimized minus baseline -0.5.
- `gpt-oss:20b-cloud`, Test 12: written total delta 2.5 differs from optimized minus baseline -2.5.
- `kimi-k3:cloud`, Test 9: written optimized total 23.5 differs from the saved total 23.
- `minimax-m3.1-flash:cloud`, Test 12: written accuracy delta 2.5 differs from optimized minus baseline -2.5.
- `minimax-m3.1-flash:cloud`, Test 12: written completeness delta 1.5 differs from optimized minus baseline -1.5.
- `minimax-m3.1-flash:cloud`, Test 12: written structure delta 1 differs from optimized minus baseline -1.
- `minimax-m3.1-flash:cloud`, Test 12: written actionability delta 3.5 differs from optimized minus baseline -3.5.
