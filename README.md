# make-prompt-better

Research-grounded prompt, context, and harness optimization using semi-formal reasoning. Eleven papers. Four certificate modes. Any coding agent or LLM.

---

## TL;DR for Developers

**What it does:** Rewrites vague, brittle, or goal-biased prompts and context files into verifiable **reasoning certificates** (`[P1]` Premises, `[T1]` Evidence Traces or `[V1]` Verification Gates, and a Formal Conclusion with Remediation). Works universally across **Claude Code, Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, GitHub Copilot CLI, Cursor, Windsurf, AdaL, and raw LLM APIs**.

**Does it work?** Cross-architecture benchmarking across Gemini, GLM, Qwen, and Kimi:
- **+25.9%** average relative improvement (range: +20.5% on Gemini to +37.8% on Kimi)
- **96.3%** win rate over unstructured prompts on analytical tasks
- **+1.9 avg** traceability gain (the primary value driver, larger than accuracy +0.6)
- **+6.3 avg** delta on code review tasks (the strongest domain)
- **Zero** orphan claims (hallucinated conclusions without supporting trace IDs) across 40 benchmark tests

**What it costs:** ~2.2x token overhead in **Max mode**, ~1.5x in **Lite mode**, ~1.1x to 1.3x in **LRM / Harness mode**, and ~1.6x in **Creative & Divergent v2 mode**.

**New in V4 (The Context, Harness & Diversity Update):**
- **Expanded Research Foundation (6 to 11 papers):** Adds Verbalized Sampling (`[VS]`, Zhang et al., 2025), Structural Signatures of AI Writing (`[SLOPSHAPE]`, Madler, 2026), Repository Context File Evaluation (`[CONTEXT-FILES]`, Gloaguen et al., 2026), Harness & Context-as-a-File Optimization (`[HARNESS]`, Lee et al., 2026; Zhang et al., 2026; Shao et al., 2026; Nam et al., 2025), and Skill Residency & Positive Recipe Shaping (`[SKILLS-SDO]`, Yin et al., 2026).
- **Mode 3 (LRM / Harness Mode):** Dedicated optimization for reasoning models (o3, DeepSeek-R1, Claude Extended Thinking, Gemini Thinking) that uses `[V]` Verification Gates instead of forced visible step-by-step CoT (preventing the LRM Overthinking Trap), plus Minimal Viable Context pruning for `AGENTS.md` and `CLAUDE.md` files (removing directory trees that add >20% token cost and -3% task success).
- **Mode 4 (Creative & Divergent v2):** Combines `[NT0]` Verbalized Distribution Sampling (1.6x to 2.1x diversity gain against post-training mode collapse) with Narrative Traces and the 4-part Anti-SlopShape Structural Rarity Contract.
- **Universal Cross-Tool Compatibility:** Follows the `agentskills.io` standard with parser-safe frontmatter and ships with `install.sh` for one-command installation into `~/.agents/skills/`, `~/.claude/skills/`, and `~/.qwen/skills/`.

**Quick Install (All Coding Tools):**
```bash
./install.sh
```
Or copy manually to `~/.agents/skills/make-prompt-better` (universal cross-runtime alias) and `~/.claude/skills/make-prompt-better`.

---

## What This Is

This project is a synthesis of academic research into an actionable prompt optimization skill. It is not a novel research contribution. It takes six peer-reviewed papers from 2025 and 2026, extracts the constraints each one imposes on how language models should be prompted, and assembles those constraints into a single methodology anyone can apply.

The core technique is **semi-formal reasoning**: instead of asking a model for an answer, you ask it to produce a structured certificate that includes explicit premises, step-by-step traces, and a conclusion. This mirrors how mathematical proofs work at a lighter weight. The model lays out its reasoning in a predictable structure, which makes errors easier to spot and outputs easier to parse.

make-prompt-better works as a **Claude Code skill** you install for interactive use, and as a **standalone reference** you can apply to any prompt in any domain. The methodology is domain-agnostic: code review, legal analysis, medical reasoning, financial due diligence, comparative analysis, and any other task where structured reasoning beats freeform generation.

---

## What's New in V3

V3 is grounded in cross-architecture benchmark evaluation across four model families (Gemini, GLM, Qwen, Kimi). Five updates harden the skill based on empirical findings.

### Lite vs. Max Certificate Modes

Not every task needs the full certificate. V3 introduces two modes:

| Mode | When to Use | Token Overhead | Traceability |
|------|-------------|----------------|--------------|
| **Max** | High-stakes (medical, legal, financial), low baseline competence, full auditability required | ~2.2x | Full |
| **Lite** | Routine analytical tasks (standard code reviews, basic document analysis, simple comparisons) | ~1.5x | ~80% of Max (projected target, not yet benchmarked) |

**Lite mode constraints:** max 3 premises, single-line causal arrow traces (`[T1] Input -> Processing Step -> Finding`), conclusion fields capped at 1-2 sentences.

**Selection heuristic:** If a wrong answer causes real harm, use Max. If the task is analytical but routine, use Lite. When uncertain, default to Max.

### Actionability Mandate

Cross-architecture testing revealed a consistent failure mode: models produce perfect analysis certificates but stop at the verdict without generating the fix. We call this the **Actionability Gap**.

V3 adds a mandatory `REMEDIATION / NEXT ACTION` block after every formal conclusion. The model must provide a copy-pasteable fix, a concrete next action with specific steps, or an explicit "No remediation required" statement with justification. The instruction is: *"The task is incomplete until the final, copy-pasteable artifact or specific fix is generated."*

### Creative Pivot (Narrative Tracing)

Logical evidence traces constrain and flatten creative writing. But completely bypassing the certificate for creative tasks throws away the benefits of structured reasoning.

V3 replaces the old "skip the certificate for creative tasks" advice with **Narrative Traces**: a backstage scaffold that traces Audience Empathy, Emotional Arcs, and Tone Calibration. The model still reasons before writing, but the final creative output is presented cleanly without analytical scaffolding. The narrative traces act like a director's notes: they shape the performance without appearing on stage.

### Traceability Self-Check Guard

Models occasionally generate well-structured certificates where the conclusion introduces claims not grounded in any trace. V3 appends a mandatory self-check instruction to every optimized prompt:

> *Before finalizing, verify that every claim in your conclusion references at least one T-identifier from your evidence traces. If any claim lacks a supporting trace, either add the missing trace or remove the claim.*

### Updated Token Economics

The original META paper (Ugare & Chandra, 2026) reported ~2.8x overhead. Cross-architecture benchmarking shows the actual average is **~2.2x** across model families (~1.7x on Qwen, ~2.0x on GLM, ~2.5x on Gemini, ~2.7x on Kimi). This cost reliably buys a ~26% relative improvement for analytical tasks.

---

## Benchmark Results

Cross-architecture evaluation across four model families (N=10 tests per model, 5 scoring dimensions per test). All evaluations were self-judged; deltas are more reliable than absolute scores.

### Per-Model Performance

| Model | Baseline Avg | Optimized Avg | Delta | Relative Gain | Token Overhead | Win Rate |
|-------|-------------|---------------|-------|---------------|----------------|----------|
| **GLM-5.1** | 19.5/25 | 24.3/25 | +4.8 | +24.6% | ~2.0x | 90% |
| **Gemini** | 20.5/25 | 24.6/25 | +4.2 | +20.5% | ~2.5x | 95% |
| **Qwen Code** | 20.3/25 | 24.5/25 | +4.2 | +20.7% | ~1.7x | 100% |
| **Kimi** | 17.2/25 | 24.0/25 | +6.5 | +37.8% | ~2.7x | 100% |
| **Average** | **19.4/25** | **24.4/25** | **+4.9** | **+25.9%** | **~2.2x** | **96.3%** |

### Where the Improvement Actually Lives

| Dimension | GLM | Gemini | Qwen | Kimi | **Average** |
|-----------|-----|--------|------|------|-------------|
| Traceability | +1.8 | +1.6 | +1.5 | +2.7 | **+1.9** |
| Structure | +1.5 | +1.0 | +1.0 | +2.1 | **+1.4** |
| Completeness | +0.7 | +0.6 | +0.7 | +1.5 | **+0.9** |
| Accuracy | +0.5 | +0.4 | +0.4 | +0.9 | **+0.6** |
| Actionability | +0.3 | +0.2 | +0.3 | +0.9 | **+0.4** |

Traceability improved on every test, for every model, without exception. It is the single most validated finding across all four architectures. The certificate structure makes reasoning auditable; it does not make the model fundamentally smarter.

*Note: Dimension deltas are from the Qwen Code evaluator summary only. Other evaluators partially reported dimension data but not all five dimensions for all models.*

### Strongest Domains

| Domain | Avg Delta | Notes |
|--------|-----------|-------|
| Code Review | +6.3 | Strongest domain across all models |
| Financial Analysis | +5.8 | High ceiling, strong traceability gains |
| Legal Analysis | +5.0 | Single-model data (GLM), needs wider validation |
| Research Synthesis | +5.0 | Two-model data (GLM, Gemini) |
| Medical Reasoning | +3.0 | Ceiling effect: strong baselines limit delta |
| Creative Brief | +1.0 | Structural mismatch; see Creative Pivot above |

*Note: Domain deltas are from the Qwen Code evaluator summary only. Other evaluators partially reported domain data but not all domains for all models.*

### Ceiling and Floor Effects

Models with lower baselines show larger improvements. The relationship is approximately linear:

- **Kimi** (baseline 17.2) saw the largest delta: +6.5
- **GLM** (baseline 19.5) saw +4.8
- **Gemini/Qwen** (baseline ~20.4) saw +4.2

Every 1-point increase in baseline reduces the expected delta by approximately 0.8 points. The skill is most valuable for models with moderate baseline performance on analytical tasks. For models already scoring above 22/25, the overhead may not justify the marginal gain.

### Methodological Caveats

- All evaluations were self-judged (same model generated and scored). Deltas are more reliable than absolute scores.
- N=10 tests per evaluator, N=4 evaluators. Statistical significance is limited, but directional consistency across all four architectures strengthens confidence.
- Creative test deltas (+0 to +2) are structural metrics only; aesthetic quality was not evaluated.

Full benchmark data is available in `research/benchmark/summaries/`.

---

## Attribution & Credits

This project would not exist without the research and engineering work below. Every technique in this methodology traces back to a specific finding from one of these sources.

### Academic Research

1. **Ugare, S. & Chandra, S.** (2026). "Agentic Code Reasoning." Meta. arXiv:2603.01896. https://arxiv.org/abs/2603.01896
   *Contributed: The core semi-formal reasoning methodology (premises, traces, conclusion certificate structure).*

2. **Cao, S., Jiang, W. & Xu, H.** (2026). "Seeing the Goal, Missing the Truth: Human Accountability for AI Bias." arXiv:2602.09504. https://arxiv.org/abs/2602.09504
   *Contributed: The goal-blind prompting principle. Discovery that disclosing downstream objectives degrades out-of-sample generalization.*

3. **Zhang, Q., Hu, C. et al.** (2026). "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models." ICLR 2026. arXiv:2510.04618. https://arxiv.org/abs/2510.04618
   *Contributed: Itemized context design with unique identifiers, incremental delta updates, and the grow-and-refine principle. Identified brevity bias and context collapse as failure modes.*

4. **Geng, Y., Li, H. et al.** (2025). "Control Illusion: The Failure of Instruction Hierarchies in Large Language Models." AAAI 2026. arXiv:2502.15851. https://arxiv.org/abs/2502.15851
   *Contributed: Evidence that system/user separation fails to enforce instruction priority. Discovery that societal hierarchy framings (expertise, consensus) achieve roughly 2x-4x better compliance.*

5. **Mahmoudi, B., Chenail-Larcher, Z. et al.** (2025). "Specification and Detection of LLM Code Smells." arXiv:2512.18020. https://arxiv.org/abs/2512.18020
   *Contributed: The structured output requirement. Evidence that 40.5% of LLM systems lack enforced output schemas, causing silent downstream failures.*

6. **Hu, Z., Rostami, M. & Thomason, J.** (2026). "Expert Personas Improve LLM Alignment but Damage Accuracy: Bootstrapping Intent-Based Persona Routing with PRISM." arXiv:2603.18507. https://arxiv.org/abs/2603.18507
   *Contributed: The persona calibration framework. Evidence that expert personas damage accuracy tasks by 3-5pp but improve alignment tasks.*

7. **Zhang, J., Yu, S., Chong, D., Sicilia, A., Tomz, M. R., Manning, C. D. & Shi, W.** (2025). "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity." arXiv:2510.01171. https://arxiv.org/abs/2510.01171
   *Contributed: Verbalized distribution sampling (`[NT0]`) to overcome preference-data typicality bias and mode collapse, increasing creative and open-ended diversity by 1.6x to 2.1x.*

8. **Madler, J.** (2026). "SlopShape: Identifying AI-Generated Commercial Web Content." arXiv:2609.15369. https://arxiv.org/abs/2609.15369 (extending StoryScope, Russell et al., 2026).
   *Contributed: Discourse-level structural signatures of AI text (98.0 macro-F1 across 187 structural features; 93.5 macro-F1 on 10 core features) and the 4-part Structural Rarity Contract.*

9. **Gloaguen, T., Mundler, N., Muller, M., Raychev, V. & Vechev, M.** (2026). "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?" arXiv:2602.11988. https://arxiv.org/abs/2602.11988
   *Contributed: Empirical evaluation of `AGENTS.md` and `CLAUDE.md` files on coding agents, showing that LLM-generated context files reduce task resolution by 3% while raising inference costs by >20%, and that directory overviews do not speed up file localization.*

10. **Lee, Y., Nair, R., Zhang, Q., Lee, K., Khattab, O. & Finn, C.** (2026). "Meta-Harness: End-to-End Optimization of Model Harnesses." arXiv:2603.28052. https://arxiv.org/abs/2603.28052 (alongside **Self-Harness**, Zhang et al., 2026, arXiv:2606.09498; **Context Language Models**, Shao et al., 2026, arXiv:2609.37725; and **DS-STAR**, Nam et al., 2025, arXiv:2509.21825).
    *Contributed: Model-specific harness optimization (+7.7 points over ACE with 4x fewer context tokens), file-backed context management (`Context-as-a-File`, +11.4% accuracy with 21.5% fewer FLOPs), and iterative plan-sufficiency verification gates.*

11. **Yin, L., Li, Z., Shi, Z., Zhang, H., Seong, H. & Wang, Z.** (2026). "@skills: Attention Is All You Have." arXiv:2608.12610. https://arxiv.org/abs/2608.12610
    *Contributed: Skill residency economics (`<100` reliable attention slots in the system prompt) and the shift from negative prohibitions to positive structural recipes.*

### Engineering Inspiration

12. **severity1/claude-code-prompt-improver** (MIT License). https://github.com/severity1/claude-code-prompt-improver
    *Contributed: Architectural patterns for skill-based prompt improvement. The progressive disclosure model (lightweight hook + on-demand skill loading), the 4-phase workflow pattern, bypass prefix conventions, and the plugin marketplace format.*

### Additional References

13. **Anthropic Prompt Engineering & Context Engineering Documentation.** https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
    *Contributed: The 5-component Prompt Structure Framework (Identity, Task, Context, Constraints, Output Format) used to map certificate components.*

### Assembly Statement

This project is an assembly and synthesis of others' research. It contributes the integration of these findings into a unified, actionable methodology, but the underlying discoveries belong to the researchers and engineers cited above.

---

## Quick Start

**Before:**

```
Review this code change and tell me if it looks good:

def get_user(id):
  user = db.query("SELECT * FROM users WHERE id = " + id)
  return user
```

**After:**

```
You are a senior security engineer conducting a code review.

## Task
Analyze the following code change for correctness, security, and edge cases.

## Context
[P1] This is a database query function in a web application.
[P2] The `id` parameter originates from an HTTP request path parameter.
[P3] The application uses PostgreSQL with the psycopg2 driver.

## Code Under Review
def get_user(id):
  user = db.query("SELECT * FROM users WHERE id = " + id)
  return user

## Certificate Structure
For each finding, provide:
- [PREMISE]: What assumption or rule applies
- [TRACE]: Step-by-step reasoning from premise to finding
- [SEVERITY]: Critical / High / Medium / Low
- [FIX]: Concrete remediation

## Constraints
- Cite specific OWASP or CWE references where applicable.
- If the code has no issues, state that explicitly with supporting reasoning.
- Do not suggest stylistic changes; focus on functional correctness and security.

## Output Format
JSON array of findings:
```json
{
  "findings": [
    {
      "premise": "...",
      "trace": "...",
      "severity": "...",
      "fix": "..."
    }
  ]
}
```

---

The optimized version produces structured, traceable output. Each finding comes with explicit reasoning you can verify. The model cannot skip steps because the certificate format forces it to show its work.

---

## How It Works

The optimization process follows seven steps:

1. **Classify the task type.** Determine whether the prompt targets accuracy (getting the right answer), alignment (following instructions and norms), or a mix of both. This classification drives persona usage and constraint framing, based on findings from PRISM (Hu et al., 2026). For creative tasks, this step routes to the Creative Pivot path instead of the standard certificate.

2. **Select certificate mode (Lite vs. Max).** Choose the appropriate intensity based on task stakes and model baseline competence. Max for high-stakes or low-competence tasks; Lite for routine analytical work.

3. **Analyze the original prompt.** Identify problems: missing context, ambiguous instructions, goal leakage (Cao et al., 2026), unstructured output (Mahmoudi et al., 2025), or weak constraint enforcement (Geng et al., 2025).

4. **Identify the domain-specific certificate structure.** Select or adapt a template from the domain library. Each template defines the premises, traces, conclusion format, and mandatory remediation block appropriate for that domain.

5. **Rewrite the prompt with certificate structure.** Apply the semi-formal reasoning format from Ugare & Chandra (2026). Add itemized identifiers like [P1], [T1] to prevent context collapse (Zhang et al., 2026). Append the mandatory REMEDIATION / NEXT ACTION block after the conclusion.

6. **Add anti-hallucination guards and self-check.** Enforce structured output with a JSON schema when the output will be parsed downstream (Mahmoudi et al., 2025). Use authority or consensus framing for constraints instead of relying on system/user separation (Geng et al., 2025). Append the traceability self-check instruction.

7. **Present the optimized prompt with explanation.** Show the before and after, explain which research findings drove each change, and note any tradeoffs the user should be aware of.

---

## Research Foundation

| Paper | Key Finding | Constraint on Methodology | Link |
|-------|-------------|---------------------------|------|
| META (Ugare & Chandra, 2026) | Certificate structure improves accuracy 10-15pp | Analytical prompts require premises, traces, conclusion | [arXiv](https://arxiv.org/abs/2603.01896) |
| GOAL-BLIND (Cao, Jiang & Xu, 2026) | Disclosing objectives degrades generalization | Omit evaluation criteria, stakes, or downstream use | [arXiv](https://arxiv.org/abs/2602.09504) |
| ACE (Zhang, Hu et al., 2026) | Itemized identifiers prevent context collapse | Use `[P1]`, `[T1]` identifiers and incremental delta edits | [arXiv](https://arxiv.org/abs/2510.04618) |
| HIERARCHY (Geng et al., 2025) | System/user separation fails (9.6-45.8%) | Use expertise/consensus authority framing for rules | [arXiv](https://arxiv.org/abs/2502.15851) |
| CODE-SMELLS (Mahmoudi et al., 2025) | 40.5% lack structured output | Add JSON schema when output is parsed downstream | [arXiv](https://arxiv.org/abs/2512.18020) |
| PRISM (Hu et al., 2026) | Personas damage accuracy 3-5pp | Omit persona for accuracy and LRMs; use for alignment | [arXiv](https://arxiv.org/abs/2603.18507) |
| VS (Zhang et al., 2025) | Typicality bias drives post-training mode collapse | Verbalize candidate distribution (`p <= 0.20`) in creative mode | [arXiv](https://arxiv.org/abs/2510.01171) |
| SLOPSHAPE (Madler, 2026) | 10 structural features detect AI text at 93.5 F1 | Enforce Delayed Thesis, Direct Progression, Actionable Close | [arXiv](https://arxiv.org/abs/2609.15369) |
| CONTEXT-FILES (Gloaguen et al., 2026) | Auto `AGENTS.md` files cut success 3%, raise cost >20% | Strip directory trees; keep only non-inferable commands & invariants | [arXiv](https://arxiv.org/abs/2602.11988) |
| HARNESS (Lee et al., 2026) | Harness optimization beats static ACE by +7.7 pts | Use `[V]` Verification Gates for LRMs & scratchpad files for agents | [arXiv](https://arxiv.org/abs/2603.28052) |
| SKILLS-SDO (Yin et al., 2026) | Skills compete for `<100` prompt attention slots | Use trigger-only frontmatter & positive observable-predicate recipes | [arXiv](https://arxiv.org/abs/2608.12610) |

Each paper contributes an empirical constraint the methodology satisfies.

---

## Domain Templates (12)

The methodology ships with twelve domain templates in `make-prompt-better/references/domain-templates.md`:

1. **Code Review / Patch Verification** (Security, correctness, call-chain tracing, and patch remediation)
2. **Document Analysis / Review** (Premise extraction, passage-grounded traces, and redline edits)
3. **Research Synthesis** (Multi-source synthesis with study design, effect size, and contradiction tracking)
4. **Compliance / Regulatory Check** (Clause-by-clause verification with substantive match dispositions)
5. **Decision-Making / Recommendation** (Option traces against ordered criteria, failure modes, and reversibility)
6. **Comparative Analysis** (Dimension-by-dimension evidence matrix and workload crossover conditions)
7. **Medical / Clinical Reasoning** (Evidence-ranked differential separating probability from acuity)
8. **Legal Analysis** (Rule-application-counterargument traces and contract symmetry analysis)
9. **Financial Due Diligence** (Statement reconciliation, unit economics arithmetic, and diligence gap lists)
10. **Blank Template (Custom Domain)** (Adaptable certificate scaffold for any analytical domain)
11. **Agentic System Prompt / `AGENTS.md` / `CLAUDE.md` Context File (NEW in v4.0)** (Minimal Viable Context contract with non-inferable tooling commands, hard boundary invariants, and verification gates)
12. **Creative / Editorial Writing with Verbalized Sampling & Anti-SlopShape (NEW in v4.0)** (Backstage `[NT0]` candidate distribution sampling plus discourse-level Structural Rarity Contract)

---

## Universal Installation (Any Coding Tool)

`make-prompt-better` follows the open [Agent Skills specification](https://agentskills.io/specification) and works out of the box across every major coding agent.

### Option 1: One-Command Installer (Recommended)

```bash
git clone https://github.com/poferraz/make-prompt-better.git
cd make-prompt-better
./install.sh
```

`./install.sh` installs the skill into:
- `~/.agents/skills/make-prompt-better` (Universal cross-runtime directory recognized by **Antigravity**, **Gemini CLI**, **OpenAI Codex CLI**, **GitHub Copilot CLI**, and **OpenCode**)
- `~/.claude/skills/make-prompt-better` (**Claude Code**)
- `~/.qwen/skills/make-prompt-better` (**Qwen Code**)

### Option 2: Manual / Per-Tool Installation

```bash
# Universal (Antigravity, Gemini CLI, Codex CLI, Copilot CLI, OpenCode)
mkdir -p ~/.agents/skills && cp -r make-prompt-better ~/.agents/skills/make-prompt-better

# Claude Code
mkdir -p ~/.claude/skills && cp -r make-prompt-better ~/.claude/skills/make-prompt-better

# Qwen Code
mkdir -p ~/.qwen/skills && cp -r make-prompt-better ~/.qwen/skills/make-prompt-better

# Cursor / Windsurf / Repository-Level Agent Usage
cp make-prompt-better/SKILL.md .cursor/rules/make-prompt-better.mdc
```

---

## Standalone Usage

You do not need Claude Code to use this methodology. The entire approach is documented in `docs/methodology.md`, which serves as the standalone reference.

To use without Claude Code:

1. Read `docs/methodology.md` for the full methodology.
2. Read `docs/tradeoffs.md` for limitations and when NOT to use this approach.
3. Pick the appropriate domain template from `domain-templates.md`.
4. Apply the seven-step process manually to your prompt.
5. Use the certificate structure in your final prompt, regardless of which model or interface you use.

The methodology is model-agnostic. The research findings were validated across multiple frontier models, and the constraints apply broadly.

---

## Complementary Tools

**severity1/claude-code-prompt-improver** (https://github.com/severity1/claude-code-prompt-improver) is a complementary tool, not a competitor. The two solve different problems:

- **severity1/claude-code-prompt-improver** performs real-time prompt clarification. It asks you questions to surface ambiguities and missing context *before* execution. Think of it as a prompt interviewer.

- **make-prompt-better** performs structured reasoning optimization. It restructures how the model reasons *during* execution using certificate-based semi-formal methods. Think of it as a reasoning architect.

**Recommended: install both.** Use severity1's tool first to clarify what you want, then use make-prompt-better to structure how the model should reason about it. The two tools address orthogonal problems and compose cleanly.

---

## Tradeoffs

This methodology is not universally superior to unstructured prompting. Full details are in `docs/tradeoffs.md`. Key limitations:

- **Token cost.** Certificate-structured prompts produce roughly ~2.2x more tokens than unstructured equivalents on average (ranging from ~1.7x on Qwen to ~2.7x on Kimi, per cross-architecture benchmarking). The original META paper reported ~2.8x; empirical measurement across four model families shows the real overhead is lower. Lite Certificate mode reduces this further to ~1.5x. For high-volume, low-stakes tasks, Lite mode or unstructured prompting may be more appropriate.

- **Persona can hurt accuracy.** PRISM (Hu et al., 2026) found that expert personas reduce accuracy on factual tasks by 3-5 percentage points while improving alignment on normative tasks. The methodology compensates by classifying task type and omitting persona for accuracy-dominant tasks, but misclassification will degrade results.

- **Not always better.** For simple lookup tasks or open-ended brainstorming, the overhead of certificate structure adds no value and may constrain useful exploration. Creative writing now uses the Creative Pivot (Narrative Traces) instead of the standard certificate, but simple creative tasks may still work better unstructured.

- **Goal-blind discipline is hard.** The constraint from Cao et al. (2026) to omit evaluation criteria is counterintuitive. Most prompt engineering advice encourages specifying what "good" looks like. This methodology deliberately avoids it, which means you must trust the certificate structure to produce quality without goal hints.

- **Structured output rigidity.** Adding JSON schemas (from Mahmoudi et al., 2025) ensures parseability but can cause the model to force-fit nuanced findings into rigid fields. Some domains benefit from more flexible output formats.

Read `docs/tradeoffs.md` for the full analysis, including when to use unstructured prompting instead.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

---

## License

MIT
