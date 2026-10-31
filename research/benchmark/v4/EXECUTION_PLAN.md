# Multi-Model v4.0 Benchmark Execution Plan

This runbook orchestrates the **v4.0 Multi-LLM Evaluation Suite** across **Google Antigravity (Gemini 3.8)**, **OpenAI Codex (GPT 6.1 Terra)**, and **11+ Ollama Cloud Models**, culminating in an automated cross-architecture synthesis and **v4.1 skill upgrade**.

---

## How the Original (v1.0) Benchmark Worked vs. v4.0 Upgrade

1. **Original v1.0 Protocol** (recovered from `research/benchmark/BENCHMARK_PROMPT.md`, `research/benchmark/summaries/`, and the original evaluation session log):
   - Each model received a single self-contained prompt (`SKILL EVALUATION PROMPT: make-prompt-better`) with **10 test cases** across 5 domains (Code Review, Financial Analysis, Medical Reasoning, Legal Analysis, Research Synthesis, Business Decision, NIST Compliance, Document Analysis, Database Comparison, and Creative Brief).
   - For each test case, the model generated:
     - `### BASELINE RESPONSE` (answering the raw prompt with no optimization)
     - `### OPTIMIZED PROMPT` (rewriting the prompt using `make-prompt-better`)
     - `### OPTIMIZED RESPONSE` (answering the optimized prompt)
     - `### EVALUATION: TEST N` (scoring Baseline vs. Optimized on 5 dimensions: `Accuracy`, `Completeness`, `Structure`, `Actionability`, `Traceability`, each `/5` for a total `/25`, plus word/token overhead)
   - After all tests, a synthesizer model read every model's `EVALUATION_RESULTS.md` and generated comparative summaries in `research/benchmark/summaries/`.

2. **What Changed in the v4.0 Benchmark Suite (`research/benchmark/v4/`)**:
   - **Preserves Tests 1-10 Verbatim** for direct longitudinal comparison against v1.0 (`Gemini 2.5 Pro`, `Qwen 3.5 Plus`, `Claude`, `Kimi K2.5`).
   - **Adds Tests 11-12 & Explicit Mode Routing** to test all **4 Certificate Modes** and **12 Templates**:
     - **Tests 1-8**: Test **Mode 1 (`Max Certificate`)** on high-stakes analytical tasks.
     - **Test 9 (PostgreSQL vs. MongoDB)**: Explicitly tests **Mode 2 (`Lite Certificate [LITE]`)** to verify whether token overhead stays below `1.5x` without losing accuracy.
     - **Test 10 (Ergonomic Chair Product Copy)**: Explicitly tests **Mode 4 (`Creative & Divergent v2`: Verbalized Sampling `[NT0]` + Anti-SlopShape `[SC0]`)** to verify whether v4.0 fixes v1.0's creative rigidity.
     - **Test 11 (`CLAUDE.md` Context File)**: Tests **Mode 3 (`Agentic Harness [CONTEXT-FILES]`, Template 11)** on stripping discoverable repo prose (`<150` lines).
     - **Test 12 (`AsyncTokenBucket` Concurrency)**: Tests **Mode 3 (`LRM Verification Gate [HARNESS]`, Template 12)** on replacing prose CoT with executable invariants `[V1]`-`[V3]`.
   - **Standardized Auto-Save Output Path**: Every track writes automatically to `research/benchmark/v4/results/<model-slug>/EVALUATION_RESULTS.md`.

---

## Track 1: Antigravity Session (Gemini 3.8)

1. Open a **new session in Antigravity** inside `/Users/poferraz/Documents/Development/active/make-prompt-better`.
2. Select **Gemini 3.8** as the active model.
3. Paste the following prompt (starts with `*` to bypass prompt-rewriting hooks and run the evaluation directly):

```text
*Read `research/benchmark/v4/EVALUATION_PROMPT_V4.md` in full, then read the three required skill files (`make-prompt-better/SKILL.md`, `make-prompt-better/references/domain-templates.md`, and `make-prompt-better/references/research-principles.md`). Execute all 12 test cases sequentially following every rule in `EVALUATION_PROMPT_V4.md` (Baseline -> Optimized Prompt -> Optimized Response -> Evaluation Table + Word Counts), followed by the complete 9-section Final Report. Write your full results directly to `research/benchmark/v4/results/gemini-3.8/EVALUATION_RESULTS.md`. Remember AGENTS.md rule [I1]: do not use em dashes or en dashes.
```

---

## Track 2: OpenAI Codex Session (GPT 6.1 Terra)

1. Open **Codex** in `/Users/poferraz/Documents/Development/active/make-prompt-better`.
2. Select **GPT 6.1 Terra** as the model.
3. Paste the following prompt:

```text
*Read `research/benchmark/v4/EVALUATION_PROMPT_V4.md` in full, then read `make-prompt-better/SKILL.md`, `make-prompt-better/references/domain-templates.md`, and `make-prompt-better/references/research-principles.md`. Execute all 12 test cases sequentially following every rule in `EVALUATION_PROMPT_V4.md` (Baseline -> Optimized Prompt -> Optimized Response -> Evaluation Table + Word Counts), followed by the complete 9-section Final Report. Save the complete markdown output directly to `research/benchmark/v4/results/gpt-6.1-terra/EVALUATION_RESULTS.md`. Follow AGENTS.md rule [I1]: never use em dashes or en dashes.
```

---

## Track 3: Automated Ollama Cloud Multi-Model Runner

The script `research/benchmark/v4/run_ollama_benchmarks.py` talks directly to your local Ollama HTTP API (`http://localhost:11434/api/chat`), isolates Baseline and Optimized calls into separate clean contexts (so models cannot read ahead), tracks exact token counts and latency, and saves both `EVALUATION_RESULTS.md` and `metrics.json` after every single test (supporting automatic `--resume` if interrupted).

### Discovered Ollama Cloud Models on Your Machine
- **Flagship Cloud Tier**: `glm-5.3:cloud`, `mistral-large-4:cloud`, `kimi-k3:cloud`, `gemma4:31b-cloud`
- **Fast/Flash Cloud Tier**: `glm-5.3-flash:cloud`, `deepseek-v4.1-flash:cloud`, `minimax-m3.1-flash:cloud`, `gpt-oss:20b-cloud`
- **Specialized/Experimental Cloud Tier**: `beam:cloud`, `clef:cloud`, `muse-spark-open:cloud`, `deepseek-v4.1-flash:1017-cloud`

### Commands to Run in Your Terminal

```bash
cd /Users/poferraz/Documents/Development/active/make-prompt-better

# 1. Verify discovered Ollama Cloud models
python3 research/benchmark/v4/run_ollama_benchmarks.py --list-models

# 2A. Run the Fast Cloud Tier first (4 models x 12 tests, saves incrementally)
python3 research/benchmark/v4/run_ollama_benchmarks.py --tier fast

# 2B. Run the Flagship Cloud Tier (glm-5.3, mistral-large-4, kimi-k3, gemma4:31b)
python3 research/benchmark/v4/run_ollama_benchmarks.py --tier flagship

# 2C. Or run ALL installed :cloud models automatically overnight (resumes any completed tests)
python3 research/benchmark/v4/run_ollama_benchmarks.py --tier installed-cloud

# Optional: Run specific models or specific tests (e.g. v4.0 mode tests 9,10,11,12)
python3 research/benchmark/v4/run_ollama_benchmarks.py --models "glm-5.3:cloud,kimi-k3:cloud" --tests "9,10,11,12"
```

Every model saves its outputs automatically to:
- `research/benchmark/v4/results/<model-slug>/EVALUATION_RESULTS.md`
- `research/benchmark/v4/results/<model-slug>/metrics.json`

---

## Track 4: Anthropic Claude Frontier Track (Claude Opus & Claude Sonnet 5.5)

Run the 12-test v4.0 evaluation suite on Anthropic's flagship models to benchmark how Claude Opus and Claude Sonnet 5.5 handle the 4 Certificate Modes compared to Gemini 3.8 and GPT 6.1 Terra.

### Track 4A: Claude Opus Session

1. Open a new session in your Claude environment (Claude Code, Claude Desktop, or Claude web interface) inside `/Users/poferraz/Documents/Development/active/make-prompt-better`.
2. Select **Claude Opus** (e.g. `claude-opus-4.5` / `claude-3-opus`).
3. Paste the following prompt:

```text
*Read `research/benchmark/v4/EVALUATION_PROMPT_V4.md` in full, then read the three required skill files (`make-prompt-better/SKILL.md`, `make-prompt-better/references/domain-templates.md`, and `make-prompt-better/references/research-principles.md`). Execute all 12 test cases sequentially following every rule in `EVALUATION_PROMPT_V4.md` (Baseline -> Optimized Prompt -> Optimized Response -> Evaluation Table + Word Counts), followed by the complete 9-section Final Report. Write your full results directly to `research/benchmark/v4/results/claude-opus/EVALUATION_RESULTS.md`. Remember AGENTS.md rule [I1]: do not use em dashes or en dashes.
```

### Track 4B: Claude Sonnet 5.5 Session

1. Open a new session in your Claude environment inside `/Users/poferraz/Documents/Development/active/make-prompt-better`.
2. Select **Claude Sonnet 5.5** (e.g. `claude-sonnet-5.5` / `claude-3-5-sonnet`).
3. Paste the following prompt:

```text
*Read `research/benchmark/v4/EVALUATION_PROMPT_V4.md` in full, then read the three required skill files (`make-prompt-better/SKILL.md`, `make-prompt-better/references/domain-templates.md`, and `make-prompt-better/references/research-principles.md`). Execute all 12 test cases sequentially following every rule in `EVALUATION_PROMPT_V4.md` (Baseline -> Optimized Prompt -> Optimized Response -> Evaluation Table + Word Counts), followed by the complete 9-section Final Report. Write your full results directly to `research/benchmark/v4/results/claude-sonnet-5.5/EVALUATION_RESULTS.md`. Remember AGENTS.md rule [I1]: do not use em dashes or en dashes.
```

---

## Track 5: Meta Frontier Track (Muse Wonder 1.0 Max)

Run the 12-test v4.0 evaluation suite on Meta's flagship reasoning model, Muse Wonder 1.0 Max, to test how Meta's architecture handles the 4 Certificate Modes and whether semi-formal reasoning certificates improve factual accuracy and reduce hallucination without constraining its generative flexibility.

### Track 5 Session Instructions: Meta Muse Wonder 1.0 Max

1. Open a new session in your environment supporting **Meta Muse Wonder 1.0 Max** (e.g. Meta AI, Cursor, Open WebUI, or your local/cloud host) inside `/Users/poferraz/Documents/Development/active/make-prompt-better`.
2. Select **Muse Wonder 1.0 Max** as the model.
3. Paste the following prompt:

```text
*Read `research/benchmark/v4/EVALUATION_PROMPT_V4.md` in full, then read the three required skill files (`make-prompt-better/SKILL.md`, `make-prompt-better/references/domain-templates.md`, and `make-prompt-better/references/research-principles.md`). Execute all 12 test cases sequentially following every rule in `EVALUATION_PROMPT_V4.md` (Baseline -> Optimized Prompt -> Optimized Response -> Evaluation Table + Word Counts), followed by the complete 9-section Final Report. Write your full results directly to `research/benchmark/v4/results/meta-muse-wonder-1.0-max/EVALUATION_RESULTS.md`. Remember AGENTS.md rule [I1]: do not use em dashes or en dashes.
```

The output will automatically save to:
`research/benchmark/v4/results/meta-muse-wonder-1.0-max/EVALUATION_RESULTS.md`

---

## Track 6: Final Cross-Model Synthesis & v4.1 Skill Upgrade Session

Once all tracks (Track 1 `gemini-3.8`, Track 2 `gpt-6.1-terra`, Track 3 Ollama Cloud models, Track 4 `claude-opus` / `claude-sonnet-5.5`, and Track 5 `meta-muse-wonder-1.0-max`) have saved their results under `research/benchmark/v4/results/*/`:

1. Run the aggregator script (or let the synthesis agent run it):
   ```bash
   python3 research/benchmark/v4/aggregate_results.py
   ```
   This generates `research/benchmark/v4/results/AGGREGATED_METRICS.md` and `AGGREGATED_METRICS.json`.

2. Open a fresh session in your preferred frontier coding agent (Antigravity with Gemini 3.8, Claude, or Codex with GPT 6.1 Terra) and paste:

```text
*Read `research/benchmark/v4/SYNTHESIS_PROMPT_V4.md` and execute all steps:
1. Run `python3 research/benchmark/v4/aggregate_results.py` to compile all model results under `research/benchmark/v4/results/*/`.
2. Read `research/benchmark/v4/results/AGGREGATED_METRICS.md` and the Final Reports inside `research/benchmark/v4/results/*/EVALUATION_RESULTS.md`.
3. Write the comprehensive cross-architecture synthesis report to `research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md`.
4. Based on the empirical findings across Gemini 3.8, GPT 6.1 Terra, Claude Opus, Claude Sonnet 5.5, Meta Muse Wonder 1.0 Max, and the Ollama Cloud models, propose and apply surgical v4.1 upgrades to `make-prompt-better/SKILL.md` and `make-prompt-better/references/domain-templates.md`, then run the validation gate from `AGENTS.md` and `./install.sh`.
```
