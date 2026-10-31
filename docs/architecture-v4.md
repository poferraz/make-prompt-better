# Design Spec: make-prompt-better v4.0 (Universal Cross-Agent Release)

## 1. Goal and Scope

Upgrade `make-prompt-better` from v3.0 (6 papers, Claude-centric packaging) to v4.0 (11 research sources, universal `agentskills.io` compatibility across Claude Code, Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, Copilot CLI, Cursor, Windsurf, and AdaL).

## 2. Universal Cross-Tool Compatibility Requirements

1. **YAML Frontmatter Compliance**:
   - Strict two-field frontmatter (`name` and `description`), under 450 characters total.
   - Single-line double-quoted `description` with no colons or multi-line folding markers (`>`) that break naive YAML parsers during cross-agent skill migration.
   - Starts with `"Use when..."` in third person and describes only triggering conditions and symptoms, never summarizing the internal workflow (Yin et al., 2026).
2. **Tool-Agnostic Body and Relative Paths**:
   - All reference links use clean relative paths (`references/domain-templates.md`, `references/research-principles.md`, `references/examples.md`).
   - Zero dependency on runtime-specific slash commands or proprietary tools.
3. **Multi-Runtime Installation**:
   - Document and sync to `~/.agents/skills/make-prompt-better` (universal alias for Antigravity, Gemini CLI, Codex, Copilot CLI), `~/.claude/skills/make-prompt-better`, and `~/.qwen/skills/make-prompt-better`.

## 3. New Research Foundation (6 to 11 Sources)

1. `[META]` Ugare & Chandra (2026), arXiv:2603.01896 (Semi-formal certificates)
2. `[GOAL-BLIND]` Cao, Jiang & Xu (2026), arXiv:2602.09504 (Goal-blind prompting)
3. `[ACE]` Zhang, Hu et al. (2026), arXiv:2510.04618 (Itemized identifiers, delta updates)
4. `[HIERARCHY]` Geng et al. (2025), arXiv:2502.15851 (Expertise/consensus authority framing)
5. `[CODE-SMELLS]` Mahmoudi et al. (2025), arXiv:2512.18020 (Structured output contracts)
6. `[PRISM]` Hu, Rostami & Thomason (2026), arXiv:2603.18507 (Persona calibration by task type)
7. `[VS]` Zhang, Yu, Chong, Sicilia, Tomz, Manning & Shi (2025), arXiv:2510.01171 (Verbalized Sampling to mitigate mode collapse and typicality bias, 1.6x to 2.1x diversity gain)
8. `[SLOPSHAPE]` Madler (2026), arXiv:2609.15369; extending Russell et al. (2026) (Discourse-level structural signatures of AI text; 98.0 macro-F1 detection across 187 structural features, 93.5 macro-F1 on 10 core features)
9. `[CONTEXT-FILES]` Gloaguen, Mundler, Muller, Raychev & Vechev (2026), arXiv:2602.11988 (Evaluating `AGENTS.md` and `CLAUDE.md`; LLM-generated context files reduce success by 3% and raise cost by >20%; directory overviews do not help file localization)
10. `[HARNESS]` Lee, Nair, Zhang, Lee, Khattab & Finn (2026), arXiv:2603.28052; Zhang et al. (2026), arXiv:2606.09498; Shao et al. (2026), arXiv:2609.37725; Nam et al. (2025), arXiv:2509.21825 (Meta-Harness, Self-Harness, Context Language Models, and DS-STAR iterative verification)
11. `[SKILLS-SDO]` Yin, Li, Shi, Zhang, Seong & Wang (2026), arXiv:2608.12610 (Skill attention budget residency and positive structural recipes over negative prohibitions)

## 4. Four Certificate Modes

1. **Max Certificate**: Exhaustive Premises, multi-step Evidence Traces, Formal Conclusion, Remediation block, and Traceability Self-Check (~2.2x token overhead).
2. **Lite Certificate**: Up to 3 Premises, single-line causal arrow traces (`[T1] Input -> Step -> Finding`), 1-2 sentence conclusion fields, and Remediation block (~1.5x overhead).
3. **LRM / Harness Mode**: For reasoning-distilled/extended-thinking models (o3, DeepSeek-R1, Claude Extended Thinking, Gemini Thinking) and persistent `AGENTS.md`/`CLAUDE.md` files. Replaces explicit step-by-step CoT narration with Premises, Sufficiency Verification Gates, and Traceability Citations to avoid the LRM Overthinking Trap; applies Minimal Viable Context pruning to repo context files.
4. **Creative & Divergent Mode v2**: Combines `[VS]` Verbalized Sampling (`[NT0]` candidate distribution with typicality probabilities) with Narrative Traces (`[NT1]`-`[NT3]`) and `[SLOPSHAPE]` structural rarity rules.
