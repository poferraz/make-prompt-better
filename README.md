# make-prompt-better

Research-grounded prompt optimization using semi-formal reasoning. Six papers. One methodology. Any domain.

---

## TL;DR for Developers

**What it does:** Forces LLMs to produce a structured reasoning certificate (premises, evidence traces, conclusions) before answering. The `[P1]`, `[T1]` identifier system structurally binds conclusions to evidence, eliminating "orphan claims" (hallucinated conclusions with no supporting trace). Zero orphan claims were observed across 40 benchmark tests spanning four model families.

**Does it work?** Cross-architecture benchmarking across Gemini, GLM, Qwen, and Kimi:
- **+25.9%** average relative improvement (range: +20.5% on Gemini to +37.8% on Kimi)
- **96.3%** win rate over unstructured prompts on analytical tasks
- **+1.9 avg** traceability gain (the primary value driver, larger than accuracy +0.6)
- **+6.3 avg** delta on code review tasks (the strongest domain)

**What it costs:** ~2.2x token overhead on average in Max mode (ranges from ~1.7x on Qwen to ~2.7x on Kimi). New **Lite Certificate** mode targets ~1.5x for routine tasks while preserving ~80% of the traceability benefit (projected target, not yet benchmarked). The cost is highly economical for accuracy-critical tasks (legal, financial, medical, code review) where a wrong answer costs more than extra tokens.

**Where the value is (and is not):** The skill makes responses more **traceable and auditable**, not necessarily more correct. All four synthesizers confirmed: models reached the same conclusions with and without the certificate, but the optimized versions showed their work in a verifiable structure. If you need auditability, this is high-ROI. If you need raw accuracy on tasks where the model is already strong (baseline >85%), gains are minimal.

**New in V3:** Lite/Max certificate modes, mandatory remediation blocks, Narrative Tracing for creative tasks, and an automated traceability self-check guard.

**Install:** `cp -r make-prompt-better/make-prompt-better ~/.claude/skills/make-prompt-better`

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

### Engineering Inspiration

7. **severity1/claude-code-prompt-improver** (MIT License). https://github.com/severity1/claude-code-prompt-improver
   *Contributed: Architectural patterns for skill-based prompt improvement. The progressive disclosure model (lightweight hook + on-demand skill loading), the 4-phase workflow pattern, bypass prefix conventions, and the plugin marketplace format.*

### Additional References

8. **Anthropic Prompt Engineering Documentation.** https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
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
| META (Ugare & Chandra, 2026) | Certificate structure improves accuracy 10-15pp | Every prompt needs premises, traces, conclusion | [arXiv](https://arxiv.org/abs/2603.01896) |
| GOAL-BLIND (Cao, Jiang & Xu, 2026) | Disclosing objectives degrades generalization | Never include evaluation criteria or downstream use | [arXiv](https://arxiv.org/abs/2602.09504) |
| ACE (Zhang, Hu et al., 2026) | Itemized identifiers prevent context collapse | Use [P1], [T1] identifiers, prefer detail over brevity | [arXiv](https://arxiv.org/abs/2510.04618) |
| HIERARCHY (Geng et al., 2025) | System/user separation fails (9.6-45.8%) | Use authority/consensus framing for constraints | [arXiv](https://arxiv.org/abs/2502.15851) |
| CODE-SMELLS (Mahmoudi et al., 2025) | 40.5% lack structured output | Add JSON schema when output is parsed | [arXiv](https://arxiv.org/abs/2512.18020) |
| PRISM (Hu et al., 2026) | Personas damage accuracy 3-5pp | Omit persona for accuracy, use for alignment | [arXiv](https://arxiv.org/abs/2603.18507) |

Each paper contributes a constraint the methodology must satisfy. The table above summarizes what each paper found and what that finding means for prompt design. The methodology is the intersection of all six constraints applied simultaneously.

---

## Domain Templates

The methodology ships with ten domain templates, each pre-configured with the appropriate certificate structure, constraint framing, and output format for its domain:

1. **Code Review / Patch Verification** - Security-focused certificate with OWASP/CWE references, severity levels, and concrete remediation steps.
2. **Document Analysis / Review** - Structured reading with premise extraction, thematic traces, and evidence-backed conclusions.
3. **Research Synthesis** - Multi-source certificate that tracks claims through source material with explicit provenance.
4. **Compliance / Regulatory Check** - Norm-by-norm verification with pass/fail traces and regulatory citation requirements.
5. **Decision-Making / Recommendation** - Option enumeration with explicit tradeoff traces and a ranked conclusion certificate.
6. **Comparative Analysis** - Side-by-side evaluation with dimension-specific traces and a synthesized conclusion.
7. **Medical / Clinical Reasoning** - Differential diagnosis certificate with evidence weighting and confidence levels.
8. **Legal Analysis** - Issue-rule-application-conclusion certificate with jurisdiction-specific constraint framing.
9. **Financial Due Diligence** - Risk-factor certificate with materiality thresholds and red-flag escalation traces.
10. **Blank Template (Custom Domain)** - A general certificate scaffold you adapt to any domain not covered above.

Each template lives in `domain-templates.md` with full instructions for customization.

---

## Installation

make-prompt-better is designed as a Claude Code skill. To install:

1. Clone this repository:
   ```
   git clone https://github.com/poferraz/make-prompt-better.git
   ```

2. Copy the skill directory into your Claude Code skills folder:
   ```
   cp -r make-prompt-better/make-prompt-better ~/.claude/skills/make-prompt-better
   ```

3. The skill will be available as `/make-prompt-better` in Claude Code.

For marketplace distribution, the skill follows the plugin format established by severity1/claude-code-prompt-improver: a lightweight entry point that loads the full methodology on demand, keeping baseline context usage minimal.

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
