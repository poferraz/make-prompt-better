# v4.0.0: The Context, Harness & Diversity Update

## Summary

V4 upgrades `make-prompt-better` from a 6-paper single-shot prompt optimizer into an **11-paper, 4-mode prompt, context, and harness engineering skill** built for universal compatibility across every major AI coding tool (`~/.agents/skills/`, Claude Code, Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, GitHub Copilot CLI, Cursor, Windsurf, and AdaL).

## Five Research Additions (6 to 11 Papers)

| Tag | Paper | Core Finding | v4.0 Constraint |
|---|---|---|---|
| **[VS]** | Zhang et al. (2025), arXiv:2510.01171 | Post-training alignment induces mode collapse via preference-data typicality bias; Verbalized Sampling boosts diversity by **1.6x to 2.1x** | Creative/divergent prompts include `[NT0]` Verbalized Distribution Sampling (`p <= 0.20`) |
| **[SLOPSHAPE]** | Madler (2026), arXiv:2609.15369; Russell et al. (2026) | 187 discourse features detect AI text at **98.0 macro-F1** (even after full self-rewording); 10 core features reach **93.5 macro-F1** | Enforces 4-part Structural Rarity Contract (Delayed Thesis, Direct Progression, Practitioner Voice, Actionable Close) |
| **[CONTEXT-FILES]** | Gloaguen et al. (2026), arXiv:2602.11988 | LLM-generated `AGENTS.md`/`CLAUDE.md` files reduce coding agent task success by **3%** while raising inference cost by **>20%**; directory trees do not speed up localization | Prunes directory trees and generic rules from context files; keeps only non-inferable tooling commands and hard boundary invariants |
| **[HARNESS]** | Lee et al. (2026), arXiv:2603.28052; Zhang et al. (2026), arXiv:2606.09498; Shao et al. (2026), arXiv:2609.37725; Nam et al. (2025), arXiv:2509.21825 | Meta-Harness beats static ACE by **+7.7 pts** with **4x fewer tokens**; CLM `Context-as-a-File` gains **+11.4%** accuracy with **21.5% fewer FLOPs** | Adds Mode 3 (LRM / Harness Mode) with `[V]` Verification Gates for reasoning models and scratchpad state files for multi-file agent tasks |
| **[SKILLS-SDO]** | Yin et al. (2026), arXiv:2608.12610 | Installed skills compete for `<100` system prompt attention slots; negative prohibitions backfire under competing incentives | Uses parser-safe, trigger-only YAML frontmatter (`<450` chars) and converts "Do NOT" rules into positive observable-predicate conditionals |

## Four Certificate Modes

1. **Mode 1: Max Certificate (~2.2x overhead)**: Exhaustive `[P]` Premises, multi-step `[T]` Evidence Traces, Formal Conclusion, Remediation block, and Traceability Self-Check for high-stakes analytical tasks.
2. **Mode 2: Lite Certificate (~1.5x overhead)**: Max 3 `[P]` Premises, single-line causal arrow traces (`[T1] Input -> Step -> Finding`), and 1-2 sentence conclusion fields for routine analytical tasks.
3. **Mode 3: LRM / Harness Mode (~1.1x to 1.3x overhead, NEW)**: For Large Reasoning Models (o3, DeepSeek-R1, Claude Extended Thinking, Gemini Thinking) and `AGENTS.md`/`CLAUDE.md` context files. Uses `[P]` Premises and `[V]` Verification Gates without forcing redundant step-by-step CoT output narration, preventing the LRM Overthinking Trap.
4. **Mode 4: Creative & Divergent v2 (~1.6x overhead, UPGRADED)**: Combines `[NT0]` Verbalized Distribution Sampling with Narrative Traces (`[NT1]`-`[NT3]`) and the 4-part Anti-SlopShape Structural Rarity Contract.

## Universal Cross-Tool Compatibility

- **Fixed Frontmatter Parsing**: Replaced the 215-word folded YAML description (whose unquoted colons broke cross-agent skill importers) with a clean, single-line quoted `"Use when..."` description.
- **One-Command Installer (`./install.sh`)**: Installs and updates `make-prompt-better` across `~/.agents/skills/`, `~/.claude/skills/`, and `~/.qwen/skills/`.
