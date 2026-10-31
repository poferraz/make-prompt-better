<p align="center">
  <img src="assets/hero-banner.svg" width="100%" alt="make-prompt-better v4.1.0: Research-Grounded Prompt, Context, and Harness Engineering"/>
</p>

<p align="center">
  <a href="https://github.com/poferraz/make-prompt-better/actions/workflows/validate-skill.yml"><img src="https://img.shields.io/github/actions/workflow/status/poferraz/make-prompt-better/validate-skill.yml?branch=main&style=flat-square&label=skill%20validation&color=34D399" alt="CI Status"/></a>
  <a href="https://github.com/poferraz/make-prompt-better/releases/tag/v4.1.0"><img src="https://img.shields.io/badge/release-v4.1.0-38BDF8?style=flat-square" alt="Release v4.1.0"/></a>
  <a href="https://agentskills.io/specification"><img src="https://img.shields.io/badge/standard-agentskills.io-818CF8?style=flat-square" alt="Agent Skills Standard"/></a>
  <a href="#the-11-research-papers"><img src="https://img.shields.io/badge/arXiv%20papers-11%20synthesized-C084FC?style=flat-square" alt="11 ArXiv Papers"/></a>
  <a href="#cross-architecture-benchmark-results"><img src="https://img.shields.io/badge/benchmark-14%20models%20(94.1%25%20frontier%20win%20rate)-34D399?style=flat-square" alt="Benchmark 14 Models"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-64748B?style=flat-square" alt="MIT License"/></a>
</p>

<p align="center">
  <a href="#quick-install-any-coding-agent"><b>Quick Install</b></a> •
  <a href="#why-folk-prompting-fails-in-2026"><b>6 Myths vs. Research</b></a> •
  <a href="#how-it-works-the-4-certificate-modes"><b>4 Certificate Modes</b></a> •
  <a href="#before--after-transformations"><b>Before / After Diffs</b></a> •
  <a href="#cross-architecture-benchmark-results"><b>Benchmarks</b></a> •
  <a href="#the-11-research-papers"><b>The 11 Papers</b></a> •
  <a href="#12-domain-templates"><b>12 Templates</b></a>
</p>

---

## What Is `make-prompt-better`?

Most prompt engineering advice on the internet is folk superstition that actively degrades modern LLMs.

`make-prompt-better` is an open-source, research-grounded **Prompt, Context, and Harness Optimizer** built on the [Agent Skills (`agentskills.io`)](https://agentskills.io/specification) standard. It synthesizes **11 peer-reviewed papers** (from Meta, Stanford, MIT, ETH Zurich, and ICLR/AAAI) into a single executable methodology: **Semi-Formal Reasoning Certificates**.

Instead of asking a model to "think step by step" or "act as a world-class 10x expert", `make-prompt-better` compiles your raw prompt, system instruction, or `AGENTS.md` file into a verifiable structure with explicit **Premises (`[P1]`)**, **Evidence Traces (`[T1]`)** or **Verification Gates (`[V1]`)**, a **Goal-Blind Conclusion (`[C1]`)**, and a mandatory **Remediation Block**.

Across 40 cross-architecture benchmark evaluations spanning **Gemini, GLM-5.1, Qwen Code, and Kimi**, certificate-optimized prompts achieved:
- **+25.9%** average relative quality improvement (up to **+37.8%** on weaker baselines)
- **96.3%** win rate against unstructured prompts on analytical tasks
- **Zero orphan claims** (hallucinated conclusions without supporting trace citations) across all 40 tests

---

## Quick Install (Any Coding Agent)

`make-prompt-better` works out of the box with **Claude Code, Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, GitHub Copilot CLI, OpenCode, Cursor, Windsurf, and AdaL**.

### One-Command Universal Install

```bash
git clone https://github.com/poferraz/make-prompt-better.git
cd make-prompt-better
./install.sh
```

`./install.sh` automatically installs and syncs the skill into:
- `~/.agents/skills/make-prompt-better` (Universal cross-runtime directory recognized by **Antigravity**, **Gemini CLI**, **OpenAI Codex CLI**, **GitHub Copilot CLI**, and **OpenCode**)
- `~/.gemini/skills/make-prompt-better`, `~/.gemini/config/skills/make-prompt-better`, and `~/.gemini/antigravity/skills/make-prompt-better` (**Gemini CLI** and **Google Antigravity**)
- `~/.claude/skills/make-prompt-better` (**Claude Code**)
- `~/.qwen/skills/make-prompt-better` (**Qwen Code**)

<details>
<summary><b>Manual Per-Tool &amp; IDE Rules Installation (Cursor, Windsurf, AGENTS.md)</b></summary>

```bash
# Universal (Antigravity, Gemini CLI, OpenAI Codex CLI, Copilot CLI, OpenCode)
mkdir -p ~/.agents/skills && cp -r make-prompt-better ~/.agents/skills/make-prompt-better

# Claude Code
mkdir -p ~/.claude/skills && cp -r make-prompt-better ~/.claude/skills/make-prompt-better

# Cursor / Windsurf workspace rule
mkdir -p .cursor/rules && cp make-prompt-better/SKILL.md .cursor/rules/make-prompt-better.mdc
```
</details>

---

## Why Folk Prompting Fails in 2026

Every constraint in `make-prompt-better` exists because a peer-reviewed study proved a common prompting habit backfires:

| Common "Best Practice" (Folk Myth) | What Empirical Research Actually Found | How `make-prompt-better` Fixes It |
|---|---|---|
| *"Start every prompt with: You are a world-class expert in X"* | **Drops factual accuracy by 3.6 to 5.3 percentage points** on MMLU (71.6% down to 66.3%) because personas prime confident fabrication ([Hu et al., 2026, PRISM](https://arxiv.org/abs/2603.18507)). | **Task-Type Persona Calibration:** Omits personas on accuracy tasks and reasoning models; caps at 5 words on mixed tasks; uses full personas only on style/alignment tasks. |
| *"Explain the business goal and how the output will be evaluated"* | **Causes Purpose-Conditioned Bias:** Disclosing downstream goals ("for our client demo" or "to predict stock returns") biases intermediate steps and degrades out-of-sample generalization ([Cao, Jiang & Xu, 2026](https://arxiv.org/abs/2602.09504)). | **Goal-Blind Prompting:** Strips evaluation rubrics, business stakes, and audience agendas; specifies *what* evidence to trace, never *what* verdict is desired. |
| *"Auto-generate an `AGENTS.md` or `CLAUDE.md` with `/init` codebase overviews"* | **Reduces coding agent task success by 3% and inflates token cost by >20%.** Directory overviews do not speed up file localization and trigger redundant exploration ([Gloaguen et al., 2026, ETH Zurich](https://arxiv.org/abs/2602.11988)). | **Minimal Viable Context (Mode 3):** Strips directory trees and generic PEP8/clean-code fluff; retains only non-inferable tooling commands (`uv`, test flags) and hard boundary invariants. |
| *"Add 'Think step by step' to reasoning models (o3, R1, Extended Thinking)"* | **Triggers the LRM Overthinking Trap:** Redundant CoT narration pollutes native thinking tokens and inflates latency; harness-level verification beats static context bloat by **+7.7 points at 4x fewer tokens** ([Lee et al., 2026, Meta-Harness](https://arxiv.org/abs/2603.28052)). | **LRM Verification Gates (Mode 3):** Replaces forced step-by-step output narration with `[P]` Premises and `[V]` Post-Condition Verification Gates. |
| *"Ban AI words ('delve', 'tapestry') to make creative writing sound human"* | **Word detectors fail under rewording, but 10 structural features still catch AI writing at 93.5 macro-F1 (98.0 F1 on 187 features)** because AI crowds into a "tidy, self-announcing shape" ([Madler, 2026, SlopShape](https://arxiv.org/abs/2609.15369)). Plus, RLHF typicality bias causes mode collapse ([Zhang et al., 2025, VS](https://arxiv.org/abs/2510.01171)). | **Creative & Divergent v2 (Mode 4):** Combines `[NT0]` **Verbalized Sampling** (`p <= 0.20`, **1.6x to 2.1x diversity**) with the 4-part **Structural Rarity Contract** (Delayed Thesis, Direct Progression, Practitioner Voice, Actionable Close). |
| *"Put critical rules in the System Prompt and 'Do NOT' lists at the bottom"* | **System/user split achieves only 9.6% to 45.8% compliance** on conflicting constraints ([Geng et al., 2025](https://arxiv.org/abs/2502.15851)), and negative `"Do NOT"` lists backfire under competing incentives ([Yin et al., 2026](https://arxiv.org/abs/2608.12610)). | **Authority Framing + Positive Recipes:** Uses expertise/consensus framing (**54% to 77.8% compliance**) and positive observable-predicate conditionals (`When evidence is absent, output UNABLE TO TRACE`). |

---

## How It Works: The 4 Certificate Modes

<p align="center">
  <img src="assets/architecture-4modes.svg" width="100%" alt="make-prompt-better v4.0 Architecture and 4 Certificate Modes"/>
</p>

Not every prompt needs the same scaffold. `make-prompt-better` classifies your task and routes it into one of **four research-backed Certificate Modes**:

| Mode | Best For | Token Overhead | Core Structure |
|---|---|---|---|
| **1. Max Certificate** | Frontier reasoning architectures or mission-critical human review (security audits, legal, clinical, financial due diligence), low baseline competence | **~2.2x** | Exhaustive `[P1..Pn]` Premises + multi-step `[T1..Tn]` Evidence Traces + Formal Conclusion + Remediation + Traceability Self-Check |
| **2. Lite Certificate** | Default for flash-tier or sub-30B parameter models, plus routine analytical tasks (everyday code review, basic document analysis, comparisons) | **~1.5x** | Up to 3 `[P]` Premises + single-line causal arrow traces (`[T1] Input -> Step -> Finding`) + 1 to 2 sentence Verdict + Remediation |
| **3. LRM / Harness Mode** *(Upgraded in v4.1.0)* | Reasoning models (`o3`, `DeepSeek-R1`, `Claude Extended Thinking`, `Gemini Thinking`), async concurrency coding, OR `AGENTS.md` / `CLAUDE.md` files | **~1.1x to 1.3x** | **For LRMs & concurrency:** Complete Executable Implementation First + Post-Hoc Verification Gate (`[V1] -> [V2]`, `<25%` overhead). **For `AGENTS.md`:** Context Architecture Contract preamble + Minimal Viable Context pruning |
| **4. Creative & Divergent v2** *(Validated in v4.0)* | Technical essays, copywriting, blog posts, storytelling, product positioning, ideation | **~1.6x** | Backstage `[NT0]` Verbalized Distribution Sampling (`p <= 0.20`) + `[NT1..3]` Narrative Traces + 4-part Anti-SlopShape Structural Rarity Contract |

---

## Before & After Transformations

### 1. Code Review (Mode 1 / Mode 2: Analytical Certificate)

<table>
<tr>
<th width="45%">Before (Vague &amp; Goal-Biased)</th>
<th width="55%">After (Goal-Blind Semi-Formal Certificate)</th>
</tr>
<tr>
<td>

```text
Review this pull request and let me know if
anything looks wrong. I need to ship this for
a client demo tomorrow so please be thorough.
Focus on things that might cause bugs or
performance issues during the demo.
```

**Why it fails:**
1. **Goal leakage** (`"client demo tomorrow"`) biases the model toward surface UI paths and away from latent security or concurrency bugs (Cao et al., 2026).
2. **No trace requirements**, allowing the model to guess from function names instead of tracing call chains (Ugare & Chandra, 2026).
3. **Actionability gap**: stops at commentary without a copy-pasteable patch.

</td>
<td>

```markdown
The standard code review protocol requires completing this
analytical certificate before issuing any verdict.

### PREMISES
- [P1] Files modified: [list each file and scope of changes]
- [P2] Symbols affected: [functions/classes with file:line]
- [P3] Test coverage: [tests exercising modified paths]

### EXECUTION TRACES
For each modified path:
- [T1] Trace [symbol_or_test]:
  1. Entry point & input types
  2. Call chain: [fn A -> fn B with exact file:line citations]
  3. State & invariant check: [what holds or breaks]

Grounding rule: Trace the implementation body of every called
function rather than inferring from symbol names. When a symbol
is outside [P1], record `UNABLE TO TRACE: [symbol]`.

### FORMAL CONCLUSION
- Verdict: [PASS / FAIL] citing [T] identifiers
- Verification gaps: [all items marked UNABLE TO TRACE]

### REMEDIATION / NEXT ACTION
Provide a complete, copy-pasteable patch fixing all defects in [T].
```

</td>
</tr>
</table>

### 2. Repository `AGENTS.md` / `CLAUDE.md` Context File (Mode 3: Harness Mode)

<table>
<tr>
<th width="45%">Before (Bloated `/init` Context File)</th>
<th width="55%">After (Minimal Viable Context Contract)</th>
</tr>
<tr>
<td>

```markdown
You are an elite 10x Staff Principal Python
Architect working on our FastAPI service.
Always write clean, modular, PEP8-compliant code
and think step by step before every action.

Repository Overview:
- src/api/: FastAPI routers
- src/models/: SQLAlchemy models
- src/services/: Business logic
- tests/: Unit tests

Make sure nothing breaks for next week's audit!
```

**Why it fails:**
- Auto-generated directory overviews reduce task success by **3%** and increase token costs by **>20%** (Gloaguen et al., 2026).
- Persona + `"think step by step"` triggers LRM overthinking loops.

</td>
<td>

```markdown
# Billing Service Agent Operating Contract

## 1. Non-Inferable Environment & Tooling Commands
- Runner: `uv run <cmd>` (never invoke bare `python` or `pip`)
- Single-file test: `uv run pytest <path/to/test.py> -q --tb=short`
- Lint & type gate: `uv run ruff check src tests && uv run mypy src`

## 2. Hard Architectural Invariants
- [I1] Monetary values: Use integer cents or `Decimal` with
  `ROUND_HALF_EVEN`; `float` in `src/models/` or `src/services/` fails CI.
- [I2] Session boundary: Routers in `src/api/` call service functions
  with injected `AsyncSession`; never execute ORM queries in routers.

## 3. Multi-File Context-as-a-File Protocol
- When modifying 3+ files, record your Premise & Verification
  checklist in `.agent-scratchpad.md` before editing code.

## 4. Mandatory Verification Gate
Run the single-file `pytest` and `ruff`/`mypy` commands from Section 1
on all touched modules and cite exact exit codes before finishing.
```

</td>
</tr>
</table>

### 3. Technical Essay / Blog Post (Mode 4: Creative & Divergent v2)

<details>
<summary><b>Click to view Before / After Transformation (Verbalized Sampling + Anti-SlopShape)</b></summary>

**Before:**
```text
Write an 800-word blog post for our engineering blog about why teams should switch from manual prompt tweaking to structured context engineering. We want this post to go viral on Hacker News.
```

**After (Mode 4 Certificate):**
```markdown
You are a systems engineer. The editorial craft protocol requires completing
the backstage scaffolding block before drafting the final article.

### PREMISES
- [P1] Reader & context: Senior backend and ML engineers debugging brittle multi-turn agent pipelines.
- [P2] Target shift: Move the reader from treating prompts as magic strings to treating the context window as a bounded state buffer with explicit invariants.
- [P3] Constraints: 750-850 words, technical engineering essay, zero product promotion.

### BACKSTAGE SCAFFOLD
- [NT0] Verbalized Distribution Sampling: Enumerate 4 structurally distinct entry angles and estimate each angle's typicality probability (p = likelihood a default LLM prompt produces it):
  1. [Angle 1: chronological history of prompt engineering to context engineering] (p = ...)
  2. [Angle 2: high-level definition comparing prompts to RAM/OS] (p = ...)
  3. [Angle 3: post-mortem of a production bug caused by a 12-line system prompt rewrite] (p = ...)
  4. [Angle 4: side-by-side token trace inside a 40-turn coding agent session] (p = ...)
  Selection: Commit to the strongest angle with p <= 0.20 that satisfies [P1]-[P3].
- [NT1] Opening Anchor: Start directly inside the concrete failure artifact or token trace from [NT0].
- [NT2] Inductive Trajectory: Let the core thesis emerge after walking through the concrete mechanism.
- [NT3] Cadence & Texture: Use concrete systems nouns and vary paragraph lengths naturally.

### STRUCTURAL RARITY CONTRACT (Discourse-Level Anti-SlopShape Rules)
1. Delayed Thesis: Use a specific, non-spoiler title and open inside [NT1]'s concrete artifact before stating the overarching thesis.
2. Direct Evidence Progression: Advance through failure mechanics and diffs rather than a formulaic "Old Way vs. New Way" contrast section.
3. Practitioner Voice: Write from a direct engineering viewpoint rather than an institutional "editorial explainer" voice.
4. Actionable Close: End on a specific diagnostic check the reader can run today, without a summary paragraph that restates the thesis.

### FINAL DELIVERABLE
Present the finished 750-850 word essay executing the selected [NT0] angle and adhering to the Structural Rarity Contract.
```
</details>

---

## Cross-Architecture Benchmark Results

<p align="center">
  <img src="assets/benchmark-results.svg" width="100%" alt="Cross-Architecture Benchmark Results across Gemini, Qwen Code, GLM-5.1, and Kimi"/>
</p>

Evaluated across four frontier model families (`N = 40` tests, 5 scoring dimensions per test). Full raw data and evaluator syntheses are available in [`research/benchmark/summaries/`](research/benchmark/summaries/).

### Per-Model Performance Matrix

| Model Family | Baseline Avg | Certificate Avg | Delta | Relative Gain | Token Overhead | Win Rate |
|---|---|---|---|---|---|---|
| **GLM-5.1** | 19.5 / 25 | **24.3 / 25** | +4.8 | **+24.6%** | ~2.0x | 90% |
| **Gemini** | 20.5 / 25 | **24.6 / 25** | +4.2 | **+20.5%** | ~2.5x | 95% |
| **Qwen Code** | 20.3 / 25 | **24.5 / 25** | +4.2 | **+20.7%** | ~1.7x | 100% |
| **Kimi** | 17.2 / 25 | **24.0 / 25** | +6.5 | **+37.8%** | ~2.7x | 100% |
| **Cross-Model Average** | **19.4 / 25** | **24.4 / 25** | **+4.9** | **+25.9%** | **~2.2x** | **96.3%** |

### Key Takeaways from the Benchmark Suites (v1.0 & v4.0 14-Model Suite)

1. **Multi-Architecture Validation (14 Models, 146 Test Pairs):** Across the expanded v4.0 benchmark spanning Google Antigravity (`gemini-3.8`), Anthropic Claude (`claude-opus`), Meta Muse (`meta-muse-wonder-1.0-max`), and 11 Ollama Cloud architectures (`research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md`), `make-prompt-better` achieved a **74.0% overall win rate (108W-8T-30L)** and a **94.1% frontier win rate (32W-2T-0L)**, led by **Gemini 3.8 (+5.29 delta / +27.3%, 12W-0T-0L)** and **Meta Muse Wonder 1.0 Max (+3.42 delta / +16.0%, 12W-0T-0L at 1.61x overhead)**.
2. **Traceability (+1.66 / 5.0 across 146 runs; +1.9 / 5.0 in v1.0) drives the leap:** Every model improved on traceability, linking conclusions directly to `[P]` and `[T]`/`[V]` identifiers.
3. **Mode 4 Creative Breakthrough (+4.41 / 25 delta, 100% win rate):** Introducing Verbalized Sampling (`[NT0]`) + Anti-SlopShape (`[SC0]`) turned Test 10 (Creative Brief) from the lowest-scoring task in v1.0 (+1.0) into the highest-gaining task across the 14-model v4.0 benchmark (**+4.41 net delta, 10W-1T-0L**).
4. **Empirical Refinements in v4.1.0:** The 14-model benchmark exposed three specific bottlenecks on compact/open-weights models that directly shaped v4.1.0:
   - **Code-First Verification in Template 12 (`[HARNESS]`):** Placing verification tables before code caused token starvation on compact models (-1.85 delta on Test 12); v4.1.0 generates the complete executable implementation first, followed by a post-hoc `[V1] -> [V2]` gate capped at `<25%` overhead.
   - **Context Architecture Preamble in Template 11 (`[CONTEXT-FILES]`):** Standardized HTML comment header explaining intentional omission of discoverable folder trees and PEP8 boilerplate per Gloaguen et al. (2026).
   - **Model-Aware Mode Routing & Self-Contained Data Binding:** Defaults flash/sub-30B models to Mode 2 (Lite Certificate) to prevent word bloat (e.g., 11.9x on MiniMax) and requires embedding all input artifacts verbatim inside `[P]` premises.

---

## The 11 Research Papers

Every rule in `make-prompt-better` traces to one of these eleven peer-reviewed papers. Full summaries live in [`make-prompt-better/references/research-principles.md`](make-prompt-better/references/research-principles.md) and [`docs/methodology.md`](docs/methodology.md).

| Tag | Paper & Venue | Empirical Finding | Actionable Constraint in Skill |
|---|---|---|---|
| **`[META]`** | **Ugare & Chandra (2026)**<br>*Agentic Code Reasoning* (Meta)<br>[arXiv:2603.01896](https://arxiv.org/abs/2603.01896) | Semi-formal certificates raise patch equivalence accuracy from 78% to 88% (93% real-world) and code QA from 78% to 87%. | Every analytical prompt requires explicit **Premises**, **Evidence Traces**, and a **Formal Conclusion**. |
| **`[GOAL-BLIND]`** | **Cao, Jiang & Xu (2026)**<br>*Seeing the Goal, Missing the Truth*<br>[arXiv:2602.09504](https://arxiv.org/abs/2602.09504) | Disclosing downstream goals biases intermediate reasoning and degrades out-of-sample generalization. | Strip business stakes, evaluation rubrics, and downstream use cases from prompts. |
| **`[ACE]`** | **Zhang, Hu et al. (2026)**<br>*Agentic Context Engineering* (ICLR 2026)<br>[arXiv:2510.04618](https://arxiv.org/abs/2510.04618) | Itemized playbooks with unique IDs beat prose summaries by +10.6% on agents and cut adaptation latency by 86.9%. | Tag every premise (`[P1]`) and trace (`[T1]`) for cross-referencing; update prompts via incremental deltas. |
| **`[HIERARCHY]`** | **Geng et al. (2025)**<br>*Control Illusion* (AAAI 2026)<br>[arXiv:2502.15851](https://arxiv.org/abs/2502.15851) | System/user split achieves only 9.6% to 45.8% compliance on conflicts; expertise/consensus framing reaches 54% to 77.8%. | Enforce certificate templates using protocol and expertise framing rather than message position alone. |
| **`[CODE-SMELLS]`** | **Mahmoudi et al. (2025)**<br>*Specification and Detection of LLM Code Smells*<br>[arXiv:2512.18020](https://arxiv.org/abs/2512.18020) | 60.5% of audited LLM repos contain integration smells; 40.5% lack structured output validation. | Pair the reasoning certificate with a typed JSON schema whenever output is parsed downstream. |
| **`[PRISM]`** | **Hu, Rostami & Thomason (2026)**<br>*Expert Personas Improve Alignment but Damage Accuracy*<br>[arXiv:2603.18507](https://arxiv.org/abs/2603.18507) | Expert personas boost alignment (+0.4 to +0.65 MT-Bench) but reduce MMLU accuracy from 71.6% to 66.3%. | Omit personas on accuracy tasks and LRMs; cap at 5 words on mixed tasks; use full personas only for style/alignment. |
| **`[VS]`** | **Zhang, Yu, Chong, Sicilia, Tomz, Manning & Shi (2025)**<br>*Verbalized Sampling* (Stanford / Northeastern)<br>[arXiv:2510.01171](https://arxiv.org/abs/2510.01171) | Preference-data typicality bias causes post-training mode collapse; verbalizing candidate probabilities boosts diversity by **1.6x to 2.1x**. | Prepend `[NT0]` Verbalized Distribution Sampling (`4 angles with p estimates, pick p <= 0.20`) in Creative Mode. |
| **`[SLOPSHAPE]`** | **Madler (2026)** / **Russell et al. (2026)**<br>*SlopShape: Structural Signatures of AI Content*<br>[arXiv:2609.15369](https://arxiv.org/abs/2609.15369) | 187 discourse features detect AI writing at **98.0 macro-F1** even after full rewording; 10 core features reach **93.5 F1**. | Enforce the 4-part **Structural Rarity Contract** (Delayed Thesis, Direct Progression, Practitioner Voice, Actionable Close). |
| **`[CONTEXT-FILES]`** | **Gloaguen, Mundler, Muller, Raychev & Vechev (2026)**<br>*Evaluating AGENTS.md* (ETH Zurich)<br>[arXiv:2602.11988](https://arxiv.org/abs/2602.11988) | Auto-generated `AGENTS.md` files reduce coding agent task success by **3%** and increase inference cost by **>20%**. | Prune directory trees and generic rules from `AGENTS.md`/`CLAUDE.md`; retain only non-inferable tooling and invariants. |
| **`[HARNESS]`** | **Lee et al. (2026)** ([arXiv:2603.28052](https://arxiv.org/abs/2603.28052)), **Zhang et al. (2026)** ([arXiv:2606.09498](https://arxiv.org/abs/2606.09498)), **Shao et al. (2026)** ([arXiv:2609.37725](https://arxiv.org/abs/2609.37725)), **Nam et al. (2025)** ([arXiv:2509.21825](https://arxiv.org/abs/2509.21825)) | Meta-Harness beats static ACE by **+7.7 pts** at 4x fewer tokens; CLM `Context-as-a-File` improves accuracy **+11.4%** at 21.5% fewer FLOPs. | Route reasoning models to `[V]` Verification Gates and multi-file agent tasks to scratchpad state files. |
| **`[SKILLS-SDO]`** | **Yin, Li, Shi, Zhang, Seong & Wang (2026)**<br>*@skills: Attention Is All You Have* (UT Austin / SylphAI)<br>[arXiv:2608.12610](https://arxiv.org/abs/2608.12610) | 56,804 skills compete for `<100` system prompt attention slots; negative prohibitions backfire under competing incentives. | Keep skill frontmatter compact and trigger-only; express rules as positive observable-predicate recipes. |

---

## 12 Domain Templates

Ready-to-use templates live in [`make-prompt-better/references/domain-templates.md`](make-prompt-better/references/domain-templates.md), with 9 full before/after walkthroughs in [`make-prompt-better/references/examples.md`](make-prompt-better/references/examples.md):

1. **Code Review / Patch Verification** (Call-chain tracing, invariant checks, and copy-pasteable patches)
2. **Document Analysis / Review** (Passage-anchored evidence traces and redline edits)
3. **Research Synthesis** (Study design, effect magnitudes, and cross-paper conflict reconciliation)
4. **Compliance / Regulatory Check** (Clause-by-clause mechanism verification and remediation controls)
5. **Decision-Making / Recommendation** (Option traces against ordered criteria, failure modes, and reversibility)
6. **Comparative Analysis** (Dimension-by-dimension evidence matrix and crossover conditions)
7. **Medical / Clinical Reasoning** (Evidence-ranked differential separating probability from acuity)
8. **Legal Analysis** (Rule-application-counterargument traces and contract symmetry analysis)
9. **Financial Due Diligence** (Statement reconciliation, unit economics arithmetic, and diligence gap lists)
10. **Creative / Editorial Writing with Verbalized Sampling & Anti-SlopShape** *(Validated in v4.0: +4.41 delta)* (Backstage distribution sampling + discourse-level Structural Rarity Contract)
11. **Agentic System Prompt / `AGENTS.md` / `CLAUDE.md` Context File** *(Upgraded in v4.1.0)* (Context Architecture Contract header + Minimal Viable Context operating contract for coding agents)
12. **LRM & Algorithmic Implementation Verification Harness** *(Upgraded in v4.1.0)* (Code-first executable implementation + post-hoc `[V1] -> [V2]` verification gate with `<25%` overhead ceiling, plus Custom Domain Fallback and JSON Wrapper)

---

## Repository Structure & Documentation

```text
make-prompt-better/
├── make-prompt-better/                  # Installable Universal Agent Skill (agentskills.io)
│   ├── SKILL.md                         # Core 4-Mode workflow (<500 lines, parser-safe YAML)
│   └── references/
│       ├── domain-templates.md          # 12 domain-specific certificate templates
│       ├── research-principles.md       # Quick-reference index for all 11 papers
│       └── examples.md                  # 9 annotated Before/After prompt transformations
├── docs/                                # Standalone deep-dive documentation
│   ├── methodology.md                   # Complete theoretical and empirical walkthrough
│   ├── task-classification.md           # Persona decision tree and PRISM classification guide
│   ├── when-to-use.md                   # Decision flowchart across all 4 modes
│   └── tradeoffs.md                     # Honest token cost, latency, and ceiling/floor analysis
├── research/benchmark/                  # Cross-architecture benchmark prompts & 4-model data
├── assets/                              # High-DPI SVG diagrams for documentation
├── AGENTS.md                            # Dogfooded Minimal Viable Context contract (Template 11)
├── CLAUDE.md                            # Repository invariants and contributor checklist
├── CITATION.cff                         # GitHub academic citation metadata
└── install.sh                           # One-command installer for ~/.agents, ~/.claude, ~/.qwen
```

---

## Complementary Tools & Credits

- **[severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver)** (MIT License): Contributed architectural inspiration for progressive disclosure skill loading. `claude-code-prompt-improver` acts as an interactive *prompt interviewer* (clarifying requirements before execution), while `make-prompt-better` acts as a *reasoning & context architect* (compiling prompts and `AGENTS.md` files into verifiable certificates). Installing both is highly recommended.
- **[Anthropic Context Engineering Guide](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)**: Contributed the 5-component Prompt Structure Framework mapped in [`SKILL.md`](make-prompt-better/SKILL.md).

## Contributing & License

Contributions backed by peer-reviewed research or reproducible benchmarks are welcome! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

Released under the [MIT License](LICENSE).
