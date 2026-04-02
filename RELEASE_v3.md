# v3.0.0: The Empirical Update

## Summary

V3 hardens the make-prompt-better skill based on cross-architecture benchmark evaluation across **four major LLM families**: Gemini, GLM-5.1, Qwen Code, and Kimi. 40 benchmark tests. 5 scoring dimensions each. The data drives every change in this release.

### Headline Numbers

| Metric | Result |
|--------|--------|
| Average relative improvement | **+25.9%** |
| Win rate (optimized beats baseline) | **96.3%** |
| Traceability gain (primary value driver) | **+1.9 avg** (out of 5) |
| Orphan claims (hallucinated conclusions) | **Zero** across 40 tests |
| Token overhead (Max mode, average) | **~2.2x** |
| Token overhead (Lite mode, target) | **~1.5x** |

### What We Learned

**The skill's value is structural, not substantive.** All four synthesizers independently concluded: models reached the same conclusions with and without the certificate. The improvement manifests as traceable, auditable reasoning chains, not raw accuracy. Traceability (+1.9) and Structure (+1.4) drove the gains. Accuracy (+0.6) and Actionability (+0.4) improved least, prompting two of the V3 features below.

**Lower baselines benefit more.** Kimi (baseline 17.2/25) improved +6.5 points (+37.8%). Gemini (baseline 20.5/25) improved +4.2 points (+20.5%). Every 1-point baseline increase reduces the delta by ~0.7 points.

**Creative tasks are a structural mismatch.** The Creative Brief test averaged +1.0 delta across all models (vs. +6.3 for code review). Evaluators called the certificate structure "dead weight" and "meta-commentary" for creative output.

**Token cost is lower than documented.** The META paper cited ~2.8x. Empirical measurement shows ~2.2x on average (ranging from ~1.7x on Qwen to ~2.7x on Kimi).

## New Features

### Lite vs. Max Certificate Modes

| Mode | Overhead | Traceability | When to Use |
|------|----------|-------------|-------------|
| **Max** | ~2.0x | Full | High-stakes (medical, legal, financial), low baseline, full audit |
| **Lite** | ~1.5x | ~80% | Routine code reviews, basic analysis, simple comparisons |

Lite mode: max 3 premises, single-line causal arrow traces (`[T1] Input -> Step -> Finding`), conclusion capped at 1-2 sentences.

### Actionability Mandate

Every certificate now ends with a mandatory `REMEDIATION / NEXT ACTION` block. The model must provide a copy-pasteable fix, concrete next steps, or an explicit "no remediation required" justification. Instruction: *"The task is incomplete until the final, copy-pasteable artifact or specific fix is generated."*

This closes the **Actionability Gap** (dimension average: +0.4, lowest of all five dimensions) observed consistently across all four model families.

### Creative Pivot (Narrative Tracing)

For creative tasks, the standard evidence traces are replaced with **Narrative Traces**:
- **Audience Empathy**: what the reader believes, feels, or resists
- **Emotional Arc**: the intended trajectory from opening to close
- **Tone Calibration**: word choices, sentence rhythms, register decisions

These act as backstage scaffolding. The final creative output is presented cleanly without analytical structure.

### Traceability Self-Check Guard

Appended to every optimized prompt:

> *Before finalizing, verify that every claim in your conclusion references at least one T-identifier. If any claim lacks a supporting trace, either add the missing trace or remove the claim.*

## Per-Model Architecture Profiles

| Model | Best Use Case | Key Strength | Watch Out For |
|-------|-------------|--------------|---------------|
| **GLM-5.1** | Complex analytical tasks | Surgical precision, mathematical rigor, ~2.0x efficiency | N/A (most balanced) |
| **Gemini** | High-baseline tasks | Highest baseline scores, plug-and-play efficiency | Actionability Gap (most prone to stopping at verdict) |
| **Qwen Code** | Token-sensitive pipelines | Most token-efficient at ~1.7x, methodical risk analysis | N/A |
| **Kimi** | Weak-baseline recovery | Massive +37.8% relative improvement, perfect traceability sweep | ~2.7x token overhead, verbose prose style |

## Breaking Changes

None. V3 is backwards-compatible. Existing prompts optimized with V2 continue to work. V3 adds new capabilities (Lite mode, remediation block, narrative traces, self-check) without removing any existing functionality.

## What's Next

- **V3.1 (planned)**: Benchmark the Creative Pivot against pure-persona and analytical-certificate baselines. Target: +3.0 creative delta (vs. current +1.0).
- **V3.2 (planned)**: Evaluate with smaller models (Llama 3 8B, Mistral 7B, Phi-3) to validate the floor effect hypothesis.
- **V3.3 (planned)**: Add domain-specific Lite templates for the five most common use cases.

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete list of changes.

## Benchmark Data

Full synthesis documents and individual model summaries are available in `research/benchmark/summaries/`.
