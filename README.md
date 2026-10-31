<p align="center">
  <img src="assets/hero-banner.svg" width="100%" alt="make-prompt-better v4.1.0: 3D Isometric Prompt, Context, and Reasoning Certificate Compiler"/>
</p>

<p align="center">
  <a href="https://github.com/poferraz/make-prompt-better/actions/workflows/validate-skill.yml"><img src="https://img.shields.io/github/actions/workflow/status/poferraz/make-prompt-better/validate-skill.yml?branch=main&style=flat-square&label=skill%20validation&color=34D399" alt="CI Status"/></a>
  <a href="https://github.com/poferraz/make-prompt-better/releases/tag/v4.1.0"><img src="https://img.shields.io/badge/release-v4.1.0%20(Oct%2030%2C%202026)-38BDF8?style=flat-square" alt="Release v4.1.0"/></a>
  <a href="https://agentskills.io/specification"><img src="https://img.shields.io/badge/standard-agentskills.io-818CF8?style=flat-square" alt="Agent Skills Standard"/></a>
  <a href="#the-11-peer-reviewed-research-papers"><img src="https://img.shields.io/badge/arXiv%20papers-11%20synthesized-C084FC?style=flat-square" alt="11 ArXiv Papers"/></a>
  <a href="#cross-architecture-benchmark-suite-october-30-2026"><img src="https://img.shields.io/badge/benchmark-14%20LLMs%20%7C%2094.1%25%20frontier%20win%20rate-34D399?style=flat-square" alt="Benchmark 14 LLMs"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-64748B?style=flat-square" alt="MIT License"/></a>
</p>

<p align="center">
  <a href="#30-second-universal-install"><b>30-Sec Install</b></a> •
  <a href="#how-to-make-the-most-of-it-4-daily-ai-playbooks"><b>How to Use It</b></a> •
  <a href="#why-folk-prompting-fails-in-2026"><b>6 Myths vs. Science</b></a> •
  <a href="#the-4-model-aware-certificate-modes"><b>4 Modes</b></a> •
  <a href="#before--after-transformations"><b>Before / After Diffs</b></a> •
  <a href="#cross-architecture-benchmark-suite-october-30-2026"><b>14-Model Benchmark</b></a> •
  <a href="#the-11-peer-reviewed-research-papers"><b>11 ArXiv Papers</b></a>
</p>

---

## Stop Guessing With Folk Prompting. Compile Your Prompts Into Verified Certificates.

Most prompt advice on the internet actively makes modern AI models worse:
- Adding *"You are a world-class expert"* **drops factual accuracy by up to 5.3 percentage points** on MMLU ([Hu et al., 2026](https://arxiv.org/abs/2603.18507)).
- Auto-generating an `AGENTS.md` or `CLAUDE.md` with repo folder trees **reduces coding agent task success by 3% while inflating token costs by over 20%** ([Gloaguen et al., 2026, ETH Zurich](https://arxiv.org/abs/2602.11988)).
- Telling the model *why* you need an answer (*"for tomorrow's client demo"*) triggers **Purpose-Conditioned Bias**, causing sycophancy and missed defects ([Cao, Jiang & Xu, 2026](https://arxiv.org/abs/2602.09504)).
- Asking AI to *"avoid buzzwords"* still leaves a **98.0 macro-F1 structural AI signature ("SlopShape")** that readers and detectors spot instantly ([Madler, 2026](https://arxiv.org/abs/2609.15369)).

**`make-prompt-better` (v4.1.0, released October 30, 2026)** is an open-source, research-grounded **Prompt, Context, and Harness Compiler** built on the universal [`agentskills.io`](https://agentskills.io/specification) standard. It synthesizes **11 peer-reviewed papers** (from Meta, Stanford, MIT, ETH Zurich, UT Austin, and ICLR/AAAI) and **186 cross-architecture benchmark evaluations** (`146` controlled pairs across **14 models** in v4.0 + `40` runs in v1.0) into a single slash command: `/make-prompt-better`.

<p align="center">
  <img src="assets/live-3d-demo.svg" width="100%" alt="Live 3D Pipeline: How /make-prompt-better Strips Folk Prompting Traps and Emits Verified Certificates"/>
</p>

### Headline Empirical Results (Validated October 30, 2026)

| Benchmark Metric | Measured Result | Source / Scope |
|---|---|---|
| **Frontier Architecture Win Rate** | **94.1% Win Rate (32W-2T-0L)** | Across **Gemini 3.8** (`+27.3%`, 12W-0T-0L), **Meta Muse Wonder 1.0 Max** (`+16.0%`, 12W-0T-0L), and **Claude Opus** (`+12.3%`, 10W-2T-0L) |
| **Overall 14-Model Win Rate** | **74.0% Win Rate (108W-8T-30L)** | 146 controlled Baseline vs. Optimized test pairs across 14 frontier, flash, and open-weights architectures |
| **Analytical Baseline Quality Lift** | **+25.9% Avg Lift (96.3% Win Rate)** | v1.0 4-model suite (Gemini, Qwen Code, GLM-5.1, Kimi; up to **+37.8%** on weaker baselines) |
| **Creative & Editorial Breakthrough** | **+4.41 / 25 Net Gain (100% Win Rate)** | Test 10 (Mode 4: Verbalized Sampling `[NT0]` + Anti-SlopShape `[SC0]`, 10W-1T-0L across 11 models) |
| **Auditability & Traceability Leap** | **+1.66 / 5.0 Avg Gain (0 Orphans)** | Every conclusion claim bound to explicit `[P1]`, `[T1]`, or `[V1]` identifiers across 146 runs |

---

## 30-Second Universal Install

`make-prompt-better` works out of the box with **Claude Code, Google Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, GitHub Copilot CLI, OpenCode, Cursor, Windsurf, and AdaL**.

```bash
git clone https://github.com/poferraz/make-prompt-better.git
cd make-prompt-better
./install.sh
```

`./install.sh` automatically syncs `make-prompt-better` **v4.1.0** across:
- `~/.agents/skills/make-prompt-better` (Universal cross-runtime directory recognized by **Antigravity**, **Gemini CLI**, **OpenAI Codex CLI**, **GitHub Copilot CLI**, and **OpenCode**)
- `~/.gemini/skills/make-prompt-better`, `~/.gemini/config/skills/make-prompt-better`, and `~/.gemini/antigravity/skills/make-prompt-better` (**Gemini CLI** and **Google Antigravity**)
- `~/.claude/skills/make-prompt-better` (**Claude Code**)
- `~/.qwen/skills/make-prompt-better` (**Qwen Code**)

<details>
<summary><b>Manual Per-Tool &amp; IDE Workspace Rule Installation (Cursor, Windsurf)</b></summary>

```bash
# Universal (Antigravity, Gemini CLI, OpenAI Codex CLI, Copilot CLI, OpenCode)
mkdir -p ~/.agents/skills && cp -r make-prompt-better ~/.agents/skills/make-prompt-better

# Gemini CLI & Antigravity
mkdir -p ~/.gemini/skills ~/.gemini/config/skills && cp -r make-prompt-better ~/.gemini/skills/make-prompt-better && cp -r make-prompt-better ~/.gemini/config/skills/make-prompt-better

# Claude Code
mkdir -p ~/.claude/skills && cp -r make-prompt-better ~/.claude/skills/make-prompt-better

# Cursor / Windsurf workspace rule
mkdir -p .cursor/rules && cp make-prompt-better/SKILL.md .cursor/rules/make-prompt-better.mdc
```
</details>

---

## How to Make the Most of It: 4 Daily AI Playbooks

You do not need to memorize prompt engineering theory. Just prefix your task with `/make-prompt-better` (or ask your agent to *"optimize this prompt using make-prompt-better"*). Here is how to get the highest return on investment across four everyday workflows:

### Playbook 1: For Vibe Coders & Software Engineers (Shipping Bug-Free Code)
- **The Problem:** When you paste code and ask *"Does this look right?"*, LLMs skim function names, miss scaling or off-by-one bugs, or burn their token limit writing verbose preambles before truncating your code.
- **How to Use It:**
  - **For deep PR reviews & bug hunts on Frontier models (Claude Opus, Gemini 3.8, GPT-6, Muse Wonder):** Let it route to **Mode 1 (Max Certificate, Template 1)**. It forces the model to trace actual function bodies (`[T1] Entry -> Call Chain -> State Mutation`) and emit a copy-pasteable patch (`+2.07 / 25` average gain, 92.3% win rate).
  - **For fast daily debugging on Flash or `<30B` models:** Use **Mode 2 (Lite Certificate)**. v4.1.0 automatically routes compact models to Mode 2 (`<=3` premises + single-line causal arrows) so you get verified answers at `~1.5x` token cost with zero bloat.
  - **For complex async, concurrency, or algorithmic code:** Use **Mode 3 (Template 12 `[HARNESS]`)**. Upgraded in v4.1.0 based on 14-model benchmark findings, it forces the model to generate the **complete executable implementation first**, followed by a compact `<25%` post-hoc verification gate (`[V1] Concurrency Invariants -> [V2] Runnable Self-Test Harness`).

### Playbook 2: For AI Agent & Repository Maintainers (`AGENTS.md` / `CLAUDE.md`)
- **The Problem:** Running `/init` in coding agents dumps directory trees and generic PEP8 advice into `CLAUDE.md` or `AGENTS.md`. ETH Zurich research ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)) proved this **lowers agent task success by 3% and inflates token costs by >20%**.
- **How to Use It:** Run `/make-prompt-better` on your existing `CLAUDE.md`, `AGENTS.md`, or `.cursorrules` (routes to **Mode 3, Template 11 `[CONTEXT-FILES]`**).
- **What You Get:** A lean `<150`-line operational contract with the v4.1.0 `<!-- Context Architecture Contract -->` header, stripping discoverable folder trees and isolating only **non-inferable CLI commands** (`uv run pytest ...`), **hard boundary invariants (`[I1]`-`[I3]`)**, and a **scratchpad Context-as-a-File rule** for 3+ file edits (`+11.4%` accuracy at `21.5%` fewer FLOPs per [Shao et al., 2026](https://arxiv.org/abs/2609.37725)).

### Playbook 3: For Founders, Technical Writers & Creators (Beating AI "SlopShape")
- **The Problem:** Default LLM writing collapses into high-typicality clichés and a predictable discourse structure (spoiler title, thesis in paragraph 1, "Old Way vs. New Way" contrast, institutional explainer tone, restated summary ending) that [Madler (2026)](https://arxiv.org/abs/2609.15369) proved is detectable at **98.0 macro-F1** even after full rewording.
- **How to Use It:** Run `/make-prompt-better` on any blog post, launch announcement, product copy, or essay prompt (routes to **Mode 4: Creative & Divergent v2, Template 10**).
- **What You Get:** Backstage **Verbalized Distribution Sampling (`[NT0]`)** that forces the model to enumerate 4 structural angles, estimate typicality probabilities (`p`), and commit to a low-typicality angle (`p <= 0.20`, unlocking **1.6x to 2.1x diversity** per [Zhang et al., 2025](https://arxiv.org/abs/2510.01171)), paired with the 4-part **Structural Rarity Contract (`[SC0]`)**. In our 14-model benchmark, this achieved the **largest quality leap of any task (+4.41 / 25, 100% win rate)**.

### Playbook 4: For High-Stakes Analysts (Finance, Legal, Clinical & Compliance)
- **The Problem:** Models hallucinate intermediate arithmetic in financial due diligence, gloss over asymmetric contract clauses, or invent unsupported conclusions.
- **How to Use It:** Use **Mode 1 (Max Certificate)** with Templates 4 (Compliance), 7 (Clinical), 8 (Legal), or 9 (Financial).
- **What You Get:** v4.1.0 enforces **Self-Contained Data Binding** (embedding all tables, numbers, and clauses directly inside `[P1]`-`[Pn]` premises without placeholders), explicit step-by-step formula or clause traces (`+3.11 / 25` lift on Financial Analysis, `+2.42 / 25` on NIST Compliance and Business Decisions), and a mandatory **Traceability Self-Check** guaranteeing zero orphan claims.

### Quick-Reference Cheat Sheet: What to Type for Maximum ROI

| What You Are Doing | What to Type in Your Agent | Mode & Template Triggered | Proven Benchmark Gain |
|---|---|---|---|
| **Writing a blog post, launch copy, or essay** | `/make-prompt-better Write a post about [topic]...` | **Mode 4** (Template 10: `[VS]` + `[SLOPSHAPE]`) | **+4.41 / 25** (`100%` win rate, `2.1x` diversity) |
| **Auditing financial numbers, unit economics, or ROI** | `/make-prompt-better Analyze these financials: [data]` | **Mode 1 Max** (Template 9: Financial Traces) | **+3.11 / 25** (`92.9%` win rate across 14 LLMs) |
| **Architecture trade-offs or compliance audits (HIPAA/NIST)** | `/make-prompt-better Evaluate [system] against [rules]` | **Mode 1 Max** (Templates 4 & 5) | **+2.42 / 25** (`91.7%` win rate) |
| **Deep PR code review or hunting subtle bugs** | `/make-prompt-better Review this code: [code]` | **Mode 1 Max** (Frontier) / **Mode 2 Lite** (Flash) | **+2.07 / 25** (`92.3%` win rate, catches scaling bugs) |
| **Creating or slimming down `CLAUDE.md` / `AGENTS.md`** | `/make-prompt-better Optimize our CLAUDE.md: [text]` | **Mode 3 Harness** (Template 11: `[CONTEXT-FILES]`) | **-20% token cost**, **+7.0 / 25** on Frontier models |
| **Implementing async concurrency or complex algorithms** | `/make-prompt-better Build a thread-safe [module]` | **Mode 3 Harness** (Template 12: Code-First `[HARNESS]`) | **+6.5 / 25** on Gemini 3.8, `<25%` gate overhead |

---

## Why Folk Prompting Fails in 2026

Every rule in `make-prompt-better` exists because a peer-reviewed study proved a popular prompting habit backfires:

| Folk Prompting Habit (Myth) | What Peer-Reviewed Research Proved | How `make-prompt-better` v4.1.0 Fixes It |
|---|---|---|
| *"Start every prompt with: You are a world-class expert in X"* | **Drops factual accuracy by 3.6 to 5.3 percentage points** on MMLU (`71.6%` down to `66.3%`) because personas prime confident fabrication ([Hu et al., 2026, PRISM](https://arxiv.org/abs/2603.18507)). | **Task-Type Persona Calibration:** Omits personas on accuracy tasks and reasoning models; caps at 5 words on mixed tasks; uses full personas only on style/alignment tasks. |
| *"Explain the business goal and how the output will be graded"* | **Causes Purpose-Conditioned Bias:** Disclosing downstream stakes (*"for our client demo"*) biases intermediate reasoning and degrades generalization ([Cao, Jiang & Xu, 2026](https://arxiv.org/abs/2602.09504)). | **Goal-Blind Prompting:** Strips evaluation rubrics, business stakes, and audience agendas; specifies *what* evidence to trace, never *what* verdict is desired. |
| *"Auto-generate an `AGENTS.md` or `CLAUDE.md` with `/init` folder trees"* | **Reduces coding agent task success by 3% and inflates token cost by >20%.** Directory trees do not speed up file localization ([Gloaguen et al., 2026, ETH Zurich](https://arxiv.org/abs/2602.11988)). | **Minimal Viable Context (Template 11):** Adds the `Context Architecture Contract` header, strips directory trees/PEP8 fluff, and retains only non-inferable CLI commands and hard invariants. |
| *"Add 'Think step by step' or huge proof tables before code on reasoning/compact models"* | **Triggers Overthinking & Token Starvation:** Redundant CoT pollutes LRM thinking tokens ([Lee et al., 2026](https://arxiv.org/abs/2603.28052)), and pre-code tables starve compact models (`-1.85` delta in v4.0 Test 12). | **Code-First Verification Gates (Template 12):** Generates the complete executable implementation **first**, followed by a compact `<25%` post-hoc verification gate (`[V1] -> [V2]`). |
| *"Ban AI words ('delve', 'tapestry') to make writing sound human"* | **Word bans fail under rewording, while 10 structural features still detect AI writing at 93.5 macro-F1 (98.0 F1 on 187 features)** ([Madler, 2026, SlopShape](https://arxiv.org/abs/2609.15369)). | **Creative & Divergent v2 (Mode 4):** Combines `[NT0]` **Verbalized Sampling** (`p <= 0.20`, **1.6x to 2.1x diversity**) with the 4-part **Structural Rarity Contract** (`+4.41 / 25` benchmark lift). |
| *"Put critical rules in the System Prompt and 'Do NOT' lists at the bottom"* | **System/user split achieves only 9.6% to 45.8% compliance** on conflicts ([Geng et al., 2025](https://arxiv.org/abs/2502.15851)), and negative `"Do NOT"` lists backfire under competing incentives ([Yin et al., 2026](https://arxiv.org/abs/2608.12610)). | **Authority Framing + Positive Recipes:** Uses protocol authority framing (**54% to 77.8% compliance**) and positive observable-predicate conditionals (`When X holds, output Y`). |

---

## The 4 Model-Aware Certificate Modes

<p align="center">
  <img src="assets/architecture-4modes.svg" width="100%" alt="make-prompt-better v4.1.0: 4 Model-Aware Certificate Modes"/>
</p>

Not every prompt or model should use the same scaffold. In **v4.1.0**, `make-prompt-better` routes by **both task cognitive demand and target model capacity**:

| Mode | Target Models & Tasks | Token Overhead | Core Structure |
|---|---|---|---|
| **1. Max Certificate** | **Frontier architectures** (`Gemini 3.8`, `Claude Opus`, `Muse Wonder`, `GLM-5.3`, `Mistral Large 4`, `Kimi K3`) or mission-critical human review (security, legal, clinical, financial) | **~2.2x** | Self-contained `[P1..Pn]` Premises + multi-step `[T1..Tn]` Evidence Traces + Formal Conclusion + Remediation + Traceability Self-Check |
| **2. Lite Certificate** | **Default for Flash & `<30B` models** (`MiniMax Flash`, `DeepSeek Flash`, `GPT-OSS 20B`), plus routine daily code/doc analysis | **~1.5x** | Up to 3 `[P]` Premises + single-line causal arrow traces (`[T1] Input -> Step -> Finding`) + 1 to 2 sentence Verdict + Remediation |
| **3. LRM / Harness Mode** *(Upgraded in v4.1.0)* | Reasoning models (`o3`, `DeepSeek-R1`, `Extended Thinking`), async concurrency coding, OR `AGENTS.md` / `CLAUDE.md` files | **~1.1x to 1.3x** | **Template 12 (`[HARNESS]`):** Complete Executable Code First + Post-Hoc `[V1] -> [V2]` Gate (`<25%` overhead). **Template 11 (`[CONTEXT-FILES]`):** Context Architecture Contract + non-inferable commands & invariants |
| **4. Creative & Divergent v2** *(Validated in v4.0)* | Technical essays, copywriting, blog posts, storytelling, product positioning, ideation | **~1.6x** | Backstage `[NT0]` Verbalized Distribution Sampling (`p <= 0.20`) + `[NT1..3]` Narrative Traces + 4-part Anti-SlopShape Structural Rarity Contract (`[SC0]`) |

---

## Before & After Transformations

### 1. Code Review (Mode 1 Max / Mode 2 Lite: Analytical Certificate)

<table>
<tr>
<th width="44%">Before (Vague &amp; Goal-Biased)</th>
<th width="56%">After (Goal-Blind, Data-Bound Certificate)</th>
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
1. **Goal leakage** (`"client demo tomorrow"`) biases the model toward surface paths and away from latent scaling or state bugs ([Cao et al., 2026](https://arxiv.org/abs/2602.09504)).
2. **No trace contract**, allowing the model to guess from function names instead of tracing execution bodies ([Ugare & Chandra, 2026](https://arxiv.org/abs/2603.01896)).
3. **Actionability gap**: stops at commentary without a copy-pasteable fix.

</td>
<td>

```markdown
The standard code review protocol requires completing this
analytical certificate before issuing any verdict.

### PREMISES (Self-Contained Data Binding)
- [P1] Source artifact: [embed exact modified code/diff verbatim]
- [P2] Symbols & types affected: [functions/classes with file:line]
- [P3] Runtime invariants: [input ranges, scaling units, type rules]

### EXECUTION TRACES
For each modified path (in Lite Mode, use single-line arrows):
- [T1] Trace [symbol_or_branch]:
  1. Entry point & concrete input values (including edge types)
  2. Call chain: [fn A -> fn B with exact line citations]
  3. State & invariant check: [how values transform; what breaks]

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

### 2. Repository `AGENTS.md` / `CLAUDE.md` Context File (Mode 3: Template 11 `[CONTEXT-FILES]`)

<table>
<tr>
<th width="44%">Before (Bloated `/init` Context File)</th>
<th width="56%">After (v4.1.0 Minimal Viable Context Contract)</th>
</tr>
<tr>
<td>

```markdown
You are an elite 10x Staff Principal Python
Architect working on our FastAPI service.
Always write clean, modular, PEP8-compliant code
and think step by step before every action.

Repository Overview:
- app/api/: FastAPI routers
- app/models/: SQLAlchemy models
- app/services/: Business logic
- tests/: Unit tests

Make sure nothing breaks for next week's audit!
```

**Why it fails:**
- Auto-generated directory trees reduce agent task success by **3%** and increase token costs by **>20%** ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)).
- Persona + `"think step by step"` triggers overthinking loops.

</td>
<td>

```markdown
<!-- Context Architecture Contract: Generic directory trees and standard language style guides are omitted per Gloaguen et al. (2026) to protect agent context window. -->
# Billing Service Agent Operating Contract

## 1. Non-Inferable Environment & Tooling Commands
- Unit tests: `pytest -m "not integration" --reuse-db -q`
- Migration gate: `./scripts/migrate.sh check` (required pre-commit)
- Lint & type gate: `uv run ruff check app tests && uv run mypy app`

## 2. Hard Architectural Invariants
- [I1] Cache epoch rule: Never mutate Redis cache keys in
  `app/services/billing.py` without incrementing `SCHEMA_EPOCH`.
- [I2] Session boundary: Routers in `app/api/` call service functions
  with injected `AsyncSession`; never run ORM queries in routers.

## 3. Multi-File Context-as-a-File Protocol
- When modifying 3+ files, record your Premise & Verification
  checklist in `.agent-scratchpad.md` before editing source files.

## 4. Mandatory Verification Gate
Run the unit test, migration, and lint commands from Section 1
on all touched modules and cite exact exit codes before finishing.
```

</td>
</tr>
</table>

### 3. Algorithmic Concurrency & LRM Coding (Mode 3: Template 12 `[HARNESS]`, Upgraded in v4.1.0)

<details>
<summary><b>Click to view v4.1.0 Code-First Verification Harness (Prevents Compact-Model Token Starvation)</b></summary>

```markdown
The verification protocol for implementing `AsyncTokenBucket` requires declaring
compact premises, generating the complete executable implementation first, and
verifying it through a post-hoc gate. Restrict non-code verification preamble and
post-hoc commentary overhead to <25% of the total response length.

### PREMISES (Compact: <25% total response overhead)
- [P1] Interface contract: `AsyncTokenBucket(rate: float, capacity: float)` with
  `async def acquire(self, tokens: float = 1.0, timeout: float | None = None) -> bool`.
- [P2] Target invariants:
  - Monotonic clock refill (`time.monotonic()`) clamped to `capacity`.
  - Race-free FIFO/condition wakeup under concurrent coroutine contention.
  - Exact deadline accounting when `timeout` expires or `tokens > capacity`.

### 1. COMPLETE EXECUTABLE IMPLEMENTATION (Generated First)
Provide the complete, production-ready, copy-pasteable Python implementation
satisfying [P1] and [P2] first, before emitting any verification tables.

### 2. POST-HOC VERIFICATION GATE ([V1] Concurrency & State Invariants -> [V2] Executable Self-Test Harness)
- [V1] Concurrency & State Invariants: Check each invariant in [P2] (`[SATISFIED] -> [exact method/line]`).
- [V2] Executable Self-Test Harness: Provide a runnable `asyncio.run(main())` test block exercising burst capacity, fractional refill, timeout expiration, and 20-coroutine contention.
```
</details>

### 4. Technical Essay / Product Copy (Mode 4: Creative & Divergent v2, `+4.41 / 25` Benchmark Lift)

<details>
<summary><b>Click to view Mode 4 Transformation (Verbalized Sampling [NT0] + Anti-SlopShape [SC0])</b></summary>

```markdown
You are a systems engineer. The editorial craft protocol requires completing
the backstage scaffolding block before drafting the final article.

### PREMISES
- [P1] Reader & context: Senior backend and ML engineers debugging brittle multi-turn agent pipelines.
- [P2] Target shift: Move the reader from treating prompts as magic strings to treating the context window as a bounded state buffer with explicit invariants.
- [P3] Constraints: 750-850 words, technical engineering essay, zero product promotion.

### BACKSTAGE SCAFFOLD
- [NT0] Verbalized Distribution Sampling: Enumerate 4 structurally distinct entry angles and estimate each angle's typicality probability (p = likelihood a default LLM prompt produces it):
  1. [Angle 1: chronological history of prompt engineering to context engineering] (p = 0.45)
  2. [Angle 2: high-level definition comparing prompts to RAM/OS] (p = 0.30)
  3. [Angle 3: post-mortem of a production bug caused by a 12-line system prompt rewrite] (p = 0.15)
  4. [Angle 4: side-by-side token trace inside a 40-turn coding agent session] (p = 0.10)
  Selection: Commit to the strongest angle with p <= 0.20 that satisfies [P1]-[P3].
- [NT1] Opening Anchor: Start directly inside the concrete failure artifact or token trace from [NT0].
- [NT2] Inductive Trajectory: Let the core thesis emerge after walking through the concrete mechanism.
- [NT3] Cadence & Texture: Use concrete systems nouns and vary paragraph lengths naturally.

### STRUCTURAL RARITY CONTRACT ([SC0] Discourse-Level Anti-SlopShape Rules)
1. Delayed Thesis: Use a specific, non-spoiler title and open inside [NT1]'s concrete artifact before stating the overarching thesis.
2. Direct Evidence Progression: Advance through failure mechanics and diffs rather than a formulaic "Old Way vs. New Way" contrast section.
3. Practitioner Voice: Write from a direct engineering viewpoint rather than an institutional "editorial explainer" voice.
4. Actionable Close: End on a specific diagnostic check the reader can run today, without a summary paragraph that restates the thesis.

### FINAL DELIVERABLE
Present the finished 750-850 word essay executing the selected [NT0] angle and adhering to the Structural Rarity Contract.
```
</details>

---

## Cross-Architecture Benchmark Suite (October 30, 2026)

<p align="center">
  <img src="assets/benchmark-results.svg" width="100%" alt="14-Model Cross-Architecture Benchmark Leaderboard and Top Domain Gains"/>
</p>

`make-prompt-better` has been validated across **two comprehensive multi-model benchmark suites** totaling **186 controlled evaluations**:
1. **The v4.0 14-Model Multi-Architecture Suite (Completed October 30, 2026):** `146` controlled Baseline vs. Optimized pairs across **14 distinct models** spanning Google Antigravity, Anthropic Claude, Meta Muse, OpenAI Codex, and Ollama Cloud across 12 domain tasks ([`research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md`](research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md) and [`AGGREGATED_METRICS.md`](research/benchmark/v4/results/AGGREGATED_METRICS.md)).
2. **The v1.0 4-Model Analytical Suite:** `40` controlled evaluations across Gemini, Qwen Code, GLM-5.1, and Kimi ([`research/benchmark/summaries/`](research/benchmark/summaries/)).

### 1. v4.0 Multi-Model Leaderboard (14 Architectures, 146 Controlled Pairs)

| Model Architecture | Capacity Tier | Baseline Avg (/25) | Optimized Avg (/25) | Net Delta (/25) | Relative Lift (%) | Word Overhead | Win-Tie-Loss |
|---|---|---|---|---|---|---|---|
| **`gemini-3.8`** | Frontier | 19.38 | **24.67** | **+5.29** | **+27.3%** | 2.04x | **12W-0T-0L (100%)** |
| **`meta-muse-wonder-1.0-max`** | Frontier | 21.42 | **24.83** | **+3.42** | **+16.0%** | **1.61x** | **12W-0T-0L (100%)** |
| **`claude-opus`** | Frontier | 21.00 | **23.58** | **+2.58** | **+12.3%** | 1.83x | **10W-2T-0L (100% non-loss)** |
| **`kimi-k3:cloud`** | Frontier | 21.17 | **23.54** | **+2.38** | **+11.2%** | 3.77x | **10W-0T-2L** |
| **`glm-5.3:cloud`** | Frontier | 21.38 | **23.67** | **+2.29** | **+10.7%** | 3.84x | **12W-0T-0L (100%)** |
| **`glm-5.3-flash:cloud`** | Flash | 21.50 | **23.50** | **+2.00** | **+9.3%** | 3.50x | **11W-0T-1L** |
| **`mistral-large-4:cloud`** | Frontier | 21.00 | **22.88** | **+1.88** | **+8.9%** | 3.17x | **9W-1T-2L** |
| **`beam:cloud`** | Flash | 19.42 | **21.00** | **+1.58** | **+8.2%** | 1.98x | **8W-1T-3L** |
| **`gemma4:31b-cloud`** | Open (31B) | 20.62 | **22.12** | **+1.50** | **+7.3%** | **0.79x** | **8W-0T-4L** |
| **`minimax-m3.1-flash:cloud`** | Flash | 21.00 | **22.12** | **+1.12** | **+5.4%** | 11.93x | **10W-0T-2L** |
| **`muse-spark-open:cloud`** | Open | 19.25 | **20.08** | **+0.83** | **+4.3%** | 1.98x | **9W-0T-3L** |
| **`deepseek-v4.1-flash:cloud`** | Flash | 21.08 | **21.38** | **+0.29** | **+1.4%** | 2.91x | **8W-1T-3L** |
| **`deepseek-v4.1-flash:1017-cloud`** | Flash | 22.00 | 21.58 | -0.42 | -1.9% | 5.92x | 7W-1T-4L |
| **`gpt-oss:20b-cloud`** | Compact (20B) | 20.08 | 18.29 | -1.79 | -8.9% | 0.59x | 6W-0T-6L |

*(Note: An additional calibration run on `gpt-6.1-terra` started near ceiling at `23.58/25` and finished at `23.67/25` (`+0.08`, 1.35x overhead, 2W-8T-2L), confirming the ceiling effect documented in [`docs/tradeoffs.md`](docs/tradeoffs.md): when baseline performance already exceeds `23/25`, Mode 2 Lite is preferred over Mode 1 Max.)*

### 2. Per-Domain Performance Across All 12 Test Cases (146 Evaluated Pairs)

| Test & Certificate Mode | Domain | Baseline Avg | Optimized Avg | Net Delta (/25) | Win-Tie-Loss | What the Certificate Unlocked |
|---|---|---|---|---|---|---|
| **T10 (Mode 4 Creative v2)** | Creative Brief | 18.82 | **23.23** | **+4.41** | **10W-1T-0L (100%)** | Verbalized Sampling (`[NT0]`) + Anti-SlopShape (`[SC0]`) eliminated v1.0 creative rigidity |
| **T2 (Mode 1 Max)** | Financial Due Diligence | 20.32 | **23.43** | **+3.11** | **13W-0T-1L (92.9%)** | Step-by-step formula traces eliminated LTV/CAC and burn-multiple arithmetic errors |
| **T6 (Mode 1 Max)** | Business Architecture | 20.38 | **22.79** | **+2.42** | **11W-0T-1L (91.7%)** | Criteria-anchored option traces clarified HIPAA and latency trade-offs |
| **T7 (Mode 1 Max)** | NIST 800-63B Compliance | 20.67 | **23.08** | **+2.42** | **10W-1T-1L (90.9%)** | Clause-by-clause mapping caught periodic password-expiration violations |
| **T1 (Mode 1 Max)** | Code Review & Bug Trace | 21.04 | **23.11** | **+2.07** | **12W-1T-1L (92.3%)** | Concrete execution traces exposed decimal vs. integer discount scaling bugs |
| **T8 (Mode 1 Max)** | Document Credibility | 21.55 | **23.50** | **+1.95** | **10W-1T-0L (100%)** | Premise extraction systematically dismantled unverified vendor ROI claims |
| **T4 (Mode 1 Max)** | Legal Contract Analysis | 20.23 | **21.35** | **+1.12** | **8W-0T-5L** | Rule-application-counterargument traces exposed asymmetric non-compete clauses |
| **T9 (Mode 2 Lite)** | Database Comparison | 20.86 | **21.95** | **+1.09** | **8W-0T-3L** | Validated Lite Certificate: strong analytical lift while capping token overhead |
| **T3 (Mode 1 Max)** | Clinical Differential | 21.36 | **22.21** | **+0.86** | **11W-2T-1L (91.7%)** | Separated probability from acuity and identified discriminating workup labs |
| **T5 (Mode 1 Max)** | Research Synthesis | 20.50 | **20.73** | **+0.23** | **9W-0T-4L** | Reconciled conflicting study designs across remote-work productivity papers |
| **T11 (Mode 3 `[CONTEXT-FILES]`)** | `CLAUDE.md` Engineering | 21.32 | 20.59 | -0.73 *(Fixed in v4.1.0)* | 6W-0T-5L | Frontier models won big (`+7.0`); smaller evaluators penalized intentional folder-tree omission |
| **T12 (Mode 3 `[HARNESS]`)** | Async Concurrency | 21.75 | 19.90 | -1.85 *(Fixed in v4.1.0)* | 3W-0T-7L | Frontier models won (`+6.5`); pre-code tables starved tokens on compact models |

### 3. How the Benchmark Directly Engineered `v4.1.0`

Unlike static prompt collections, `make-prompt-better` treats benchmark losses as engineering diagnostics. The 14-model run exposed three failure modes on compact/open-weights models, each surgically resolved in **v4.1.0**:
1. **Inverted Verification Sequence in Template 12 (`[HARNESS]`)**: In v4.0 Test 12, requiring an elaborate verification table *before* the code caused compact models (`gpt-oss:20b`, `minimax-m3.1-flash`, `deepseek-v4.1-flash`) to exhaust output tokens before finishing `AsyncTokenBucket`. **v4.1.0 Fix:** Template 12 now generates the **complete executable implementation first**, followed by a compact `<25%` post-hoc gate (`[V1] Concurrency & State Invariants -> [V2] Executable Self-Test Harness`).
2. **Context Architecture Preamble in Template 11 (`[CONTEXT-FILES]`)**: In Test 11, frontier evaluators (`gemini-3.8` `+7.0`, `meta-muse-wonder-1.0-max` `+7.0`) rewarded stripping folder trees and PEP8 fluff per [Gloaguen et al. (2026)](https://arxiv.org/abs/2602.11988), whereas smaller self-evaluators penalized the omission as "incomplete." **v4.1.0 Fix:** Template 11 now prepends an explicit contract comment: `<!-- Context Architecture Contract: Generic directory trees and standard language style guides are omitted per Gloaguen et al. (2026) to protect agent context window. -->`
3. **Model-Aware Mode Routing & Self-Contained Data Binding**: Compact models (`<30B`) suffered high word overhead when forced into Mode 1 Max Certificates (e.g., `11.93x` on MiniMax), and occasionally emitted prompt templates with `[insert code here]` placeholders. **v4.1.0 Fix:** Step 1 defaults flash-tier and sub-30B models to **Mode 2 (Lite Certificate)**, and Steps 4 and 5 mandate **verbatim data binding** inside `[P]` premises.

<details>
<summary><b>View v1.0 4-Model Analytical Baseline Benchmark Table (+25.9% Avg Gain, 96.3% Win Rate)</b></summary>

| Model Family | Baseline Avg | Certificate Avg | Delta | Relative Gain | Token Overhead | Win Rate |
|---|---|---|---|---|---|---|
| **GLM-5.1** | 19.5 / 25 | **24.3 / 25** | +4.8 | **+24.6%** | ~2.0x | 90% |
| **Gemini** | 20.5 / 25 | **24.6 / 25** | +4.2 | **+20.5%** | ~2.5x | 95% |
| **Qwen Code** | 20.3 / 25 | **24.5 / 25** | +4.2 | **+20.7%** | ~1.7x | 100% |
| **Kimi** | 17.2 / 25 | **24.0 / 25** | +6.5 | **+37.8%** | ~2.7x | 100% |
| **Cross-Model Average** | **19.4 / 25** | **24.4 / 25** | **+4.9** | **+25.9%** | **~2.2x** | **96.3%** |

Full v1.0 raw data and evaluator syntheses are preserved in [`research/benchmark/summaries/`](research/benchmark/summaries/).
</details>

---

## The 11 Peer-Reviewed Research Papers

Every single rule in `make-prompt-better` traces to one of these eleven peer-reviewed papers. Full summaries live in [`make-prompt-better/references/research-principles.md`](make-prompt-better/references/research-principles.md) and [`docs/methodology.md`](docs/methodology.md).

| Tag | Paper, Authors & Venue | Key Empirical Finding | Exact Rule in `make-prompt-better` |
|---|---|---|---|
| **`[META]`** | **Ugare & Chandra (2026)**<br>*Agentic Code Reasoning* (Meta)<br>[arXiv:2603.01896](https://arxiv.org/abs/2603.01896) | Semi-formal certificates raise patch equivalence accuracy from **78% to 88%** (**93%** on real-world repos) and code QA from **78% to 87%**. | Every analytical prompt requires explicit **Premises (`[P]`)**, **Evidence Traces (`[T]`)**, and a **Formal Conclusion**. |
| **`[GOAL-BLIND]`** | **Cao, Jiang & Xu (2026)**<br>*Seeing the Goal, Missing the Truth*<br>[arXiv:2602.09504](https://arxiv.org/abs/2602.09504) | Disclosing downstream goals, business stakes, or evaluation rubrics biases intermediate reasoning and degrades generalization. | Strip business stakes, evaluation rubrics, and downstream agendas from prompts; specify *what* to analyze, never *why*. |
| **`[ACE]`** | **Zhang, Hu et al. (2026)**<br>*Agentic Context Engineering* (ICLR 2026)<br>[arXiv:2510.04618](https://arxiv.org/abs/2510.04618) | Itemized playbooks with unique IDs beat prose summaries by **+10.6%** on agent tasks and cut adaptation latency by **86.9%**. | Tag every premise (`[P1]`), trace (`[T1]`), and invariant (`[V1]`) for cross-referencing and bind all input facts verbatim. |
| **`[HIERARCHY]`** | **Geng et al. (2025)**<br>*Control Illusion* (AAAI 2026)<br>[arXiv:2502.15851](https://arxiv.org/abs/2502.15851) | System/user split achieves only **9.6% to 45.8%** compliance on conflicts; expertise/consensus framing reaches **54% to 77.8%**. | Enforce certificate templates using protocol authority framing (*"The standard analytical protocol requires..."*). |
| **`[CODE-SMELLS]`** | **Mahmoudi et al. (2025)**<br>*Specification and Detection of LLM Code Smells*<br>[arXiv:2512.18020](https://arxiv.org/abs/2512.18020) | **60.5%** of audited LLM repos contain integration smells; **40.5%** lack structured output validation. | Pair the reasoning certificate with a typed JSON schema whenever output is parsed programmatically. |
| **`[PRISM]`** | **Hu, Rostami & Thomason (2026)**<br>*Expert Personas Improve Alignment but Damage Accuracy*<br>[arXiv:2603.18507](https://arxiv.org/abs/2603.18507) | Expert personas boost alignment (`+0.4 to +0.65` MT-Bench) but reduce MMLU accuracy from **71.6% to 66.3% (-5.3pp)**. | Omit personas on accuracy tasks and LRMs; cap at 5 words on mixed tasks; use full personas only for style/alignment. |
| **`[VS]`** | **Zhang, Yu, Chong, Sicilia, Tomz, Manning & Shi (2025)**<br>*Verbalized Sampling* (Stanford / Northeastern)<br>[arXiv:2510.01171](https://arxiv.org/abs/2510.01171) | RLHF preference-data typicality bias causes mode collapse; verbalizing candidate probabilities boosts diversity by **1.6x to 2.1x**. | Prepend `[NT0]` Verbalized Distribution Sampling (`4 angles with p estimates, commit to p <= 0.20`) in Mode 4 Creative. |
| **`[SLOPSHAPE]`** | **Madler (2026)** / **Russell et al. (2026)**<br>*SlopShape: Structural Signatures of AI Content*<br>[arXiv:2609.15369](https://arxiv.org/abs/2609.15369) | 187 discourse features detect AI writing at **98.0 macro-F1** even after full rewording; 10 core features reach **93.5 F1**. | Enforce the 4-part **Structural Rarity Contract (`[SC0]`)**: Delayed Thesis, Direct Progression, Practitioner Voice, Actionable Close. |
| **`[CONTEXT-FILES]`** | **Gloaguen, Mundler, Muller, Raychev & Vechev (2026)**<br>*Evaluating AGENTS.md* (ETH Zurich)<br>[arXiv:2602.11988](https://arxiv.org/abs/2602.11988) | Auto-generated `AGENTS.md` files reduce coding agent task success by **3%** and increase inference cost by **>20%**. | Prune directory trees and generic style rules from `AGENTS.md`/`CLAUDE.md`; retain only non-inferable tooling and invariants. |
| **`[HARNESS]`** | **Lee et al. (2026)** ([arXiv:2603.28052](https://arxiv.org/abs/2603.28052)), **Zhang et al. (2026)** ([arXiv:2606.09498](https://arxiv.org/abs/2606.09498)), **Shao et al. (2026)** ([arXiv:2609.37725](https://arxiv.org/abs/2609.37725)), **Nam et al. (2025)** ([arXiv:2509.21825](https://arxiv.org/abs/2509.21825)) | Meta-Harness beats static ACE by **+7.7 pts** at 4x fewer tokens; CLM `Context-as-a-File` improves accuracy **+11.4%** at 21.5% fewer FLOPs. | Generate executable code first, verify via post-hoc `[V1] -> [V2]` gates (`<25%` overhead), and route 3+ file agent tasks to scratchpad files. |
| **`[SKILLS-SDO]`** | **Yin, Li, Shi, Zhang, Seong & Wang (2026)**<br>*@skills: Attention Is All You Have* (UT Austin / SylphAI)<br>[arXiv:2608.12610](https://arxiv.org/abs/2608.12610) | 56,804 skills compete for `<100` system prompt attention slots; negative prohibitions backfire under competing incentives. | Keep skill frontmatter compact and parser-safe; express rules as positive observable-predicate recipes. |

---

## 12 Ready-to-Use Domain Templates

All 12 domain templates live in [`make-prompt-better/references/domain-templates.md`](make-prompt-better/references/domain-templates.md), paired with 9 annotated before/after walkthroughs in [`make-prompt-better/references/examples.md`](make-prompt-better/references/examples.md):

1. **Code Review / Patch Verification** (Call-chain tracing, invariant checks, and copy-pasteable patches; `+2.07 / 25` lift)
2. **Document Analysis / Review** (Passage-anchored evidence traces and redline edits; `+1.95 / 25` lift)
3. **Research Synthesis** (Study design, effect magnitudes, and cross-paper conflict reconciliation)
4. **Compliance / Regulatory Check** (Clause-by-clause mechanism verification and remediation controls; `+2.42 / 25` lift)
5. **Decision-Making / Recommendation** (Option traces against ordered criteria, failure modes, and reversibility; `+2.42 / 25` lift)
6. **Comparative Analysis** (Dimension-by-dimension evidence matrix and crossover conditions; `+1.09 / 25` in Lite Mode)
7. **Medical / Clinical Reasoning** (Evidence-ranked differential separating probability from acuity; `+0.86 / 25` lift)
8. **Legal Analysis** (Rule-application-counterargument traces and contract symmetry analysis; `+1.12 / 25` lift)
9. **Financial Due Diligence** (Statement reconciliation, unit economics arithmetic, and diligence gap lists; `+3.11 / 25` lift)
10. **Creative / Editorial Writing with Verbalized Sampling & Anti-SlopShape** *(Validated in v4.0: `+4.41 / 25` lift, 100% win rate)*
11. **Agentic System Prompt / `AGENTS.md` / `CLAUDE.md` Context File** *(Upgraded in v4.1.0 with Context Architecture Contract header)*
12. **LRM & Algorithmic Implementation Verification Harness** *(Upgraded in v4.1.0 with Code-First implementation + `<25%` post-hoc `[V1] -> [V2]` gate, plus Custom Domain Fallback & JSON Wrapper)*

---

## Repository Structure & Documentation

```text
make-prompt-better/
├── make-prompt-better/                  # Installable Universal Agent Skill (agentskills.io)
│   ├── SKILL.md                         # Core 4-Mode workflow (v4.1.0, <500 lines, parser-safe YAML)
│   └── references/
│       ├── domain-templates.md          # 12 domain-specific certificate templates + JSON wrapper
│       ├── research-principles.md       # Quick-reference index for all 11 peer-reviewed papers
│       └── examples.md                  # 9 annotated Before/After prompt transformations
├── docs/                                # Standalone deep-dive documentation
│   ├── methodology.md                   # Complete theoretical and empirical walkthrough
│   ├── task-classification.md           # Persona decision tree and PRISM classification guide
│   ├── when-to-use.md                   # Decision flowchart across all 4 modes
│   └── tradeoffs.md                     # Token cost, latency, ceiling/floor & 14-model failure analysis
├── research/benchmark/                  # Cross-architecture benchmark suites (186 total evaluations)
│   ├── summaries/                       # v1.0 4-model analytical benchmark (40 runs)
│   └── v4/                              # v4.0 14-model multi-architecture benchmark (146 pairs, Oct 30, 2026)
├── assets/                              # 60fps 3D isometric SMIL-animated SVG diagrams
├── AGENTS.md                            # Dogfooded Minimal Viable Context contract (Template 11)
├── CLAUDE.md                            # Repository invariants and contributor checklist
├── CITATION.cff                         # GitHub academic citation metadata (v4.1.0, 2026-10-30)
└── install.sh                           # One-command installer for ~/.agents, ~/.gemini, ~/.claude, ~/.qwen
```

---

## Complementary Tools & Credits

- **[severity1/claude-code-prompt-improver](https://github.com/severity1/claude-code-prompt-improver)** (MIT License): Contributed architectural inspiration for progressive disclosure skill loading. `claude-code-prompt-improver` acts as an interactive *prompt interviewer* (clarifying requirements before execution), while `make-prompt-better` acts as a *reasoning & context compiler* (compiling prompts and `AGENTS.md` files into verifiable certificates). Installing both is highly recommended.
- **[Anthropic Context Engineering Guide](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)**: Contributed the 5-component Prompt Structure Framework mapped in [`SKILL.md`](make-prompt-better/SKILL.md).

## Contributing & License

Contributions backed by peer-reviewed research or reproducible benchmarks are welcome! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

Released under the [MIT License](LICENSE).
