# CLAUDE.md: make-prompt-better

## Repository Purpose

This repository is a research-grounded prompt, context, and harness optimization skill (`v4.1.0`). It synthesizes eleven peer-reviewed papers into an actionable methodology called semi-formal reasoning. The repo serves as both a universal installable agent skill (`agentskills.io` standard for Claude Code, Antigravity, Gemini CLI, OpenAI Codex CLI, Qwen Code, Copilot CLI, Cursor, Windsurf, and AdaL) and a standalone reference.

## File Organization

- `make-prompt-better/SKILL.md`: Core optimization workflow (under 500 lines, universal frontmatter)
- `make-prompt-better/references/domain-templates.md`: 12 domain certificate templates
- `make-prompt-better/references/research-principles.md`: Quick-reference for 11 papers
- `make-prompt-better/references/examples.md`: 9 before/after transformations
- `docs/`: Standalone methodology documentation
- `README.md`: Project overview with full attribution and cross-tool install instructions
- `install.sh`: One-command installer for all major coding agent skill directories

## Key Constraints

- **No dashes as punctuation**: No em/en dashes as sentence punctuation anywhere. Use commas, colons, semicolons. Hyphens in compounds (goal-blind, semi-formal) are fine.
- **Universal cross-tool compatibility**: `SKILL.md` frontmatter must contain only `name` and a single-line quoted `description` starting with `"Use when..."` (no colons or multi-line YAML folding markers that break cross-runtime parsers).
- **Attribution is paramount**: Every claim must trace to a cited paper. Never claim originality for ideas from the 11 papers or severity1's architecture.
- **Goal-blind**: Never include evaluation criteria or downstream use in prompt templates.
- **Positive recipes over prohibitions**: Express template rules as positive structural contracts and observable-predicate conditionals rather than bare "Do NOT" lists.
- **Progressive disclosure**: `SKILL.md` under 500 lines. Heavy content goes in `references/`.

## Adding a New Domain Template

1. Open `make-prompt-better/references/domain-templates.md`
2. Add a new numbered section following the established pattern:
   - Authority-framed preamble (per Geng et al., 2025)
   - PREMISES with `[P1]`, `[P2]` identifiers (per Zhang, Hu et al., 2026)
   - EVIDENCE TRACES with `[T1]`, `[T2]` identifiers (or `[V1]` Verification Gates for LRM/Harness templates)
   - Positive grounding rule with observable predicates (per Yin et al., 2026)
   - FORMAL CONCLUSION with trace references
   - REMEDIATION / NEXT ACTION block and TRACEABILITY SELF-CHECK
   - Persona guidance line (OMIT/MINIMAL/FULL per Hu, Rostami & Thomason, 2026)
3. Update the template count in `SKILL.md` and `README.md`
4. Add a before/after example in `make-prompt-better/references/examples.md` if the domain is commonly used

## Adding a New Research Paper

When incorporating a new paper:

1. Add entry to `make-prompt-better/references/research-principles.md` with Finding, Constraint, When to cite
2. Add the paper to the Research Foundation section in `SKILL.md`
3. Update the Prompt Structure Framework table in `SKILL.md` if the paper affects component mapping
4. Add to `docs/methodology.md` with full citation and arXiv link
5. Add to `README.md` Attribution section with full citation
6. Add to `docs/tradeoffs.md` if the paper has cost/benefit implications
7. Verify the paper is consistently cited across all files using the format: `(Author, Year)`

## Current Papers (11)

1. Ugare & Chandra (2026) - META - arXiv:2603.01896
2. Cao, Jiang & Xu (2026) - GOAL-BLIND - arXiv:2602.09504
3. Zhang, Hu et al. (2026) - ACE - arXiv:2510.04618
4. Geng et al. (2025) - HIERARCHY - arXiv:2502.15851
5. Mahmoudi et al. (2025) - CODE-SMELLS - arXiv:2512.18020
6. Hu, Rostami & Thomason (2026) - PRISM - arXiv:2603.18507
7. Zhang, Yu, Chong, Sicilia, Tomz, Manning & Shi (2025) - VS - arXiv:2510.01171
8. Madler (2026) / Russell et al. (2026) - SLOPSHAPE - arXiv:2609.15369
9. Gloaguen, Mundler, Muller, Raychev & Vechev (2026) - CONTEXT-FILES - arXiv:2602.11988
10. Lee et al. (2026) / Zhang et al. (2026) / Shao et al. (2026) / Nam et al. (2025) - HARNESS - arXiv:2603.28052, arXiv:2606.09498, arXiv:2609.37725, arXiv:2509.21825
11. Yin, Li, Shi, Zhang, Seong & Wang (2026) - SKILLS-SDO - arXiv:2608.12610
