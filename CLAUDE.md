# CLAUDE.md: make-prompt-better

## Repository Purpose

This repository is a research-informed prompt, context, and harness optimization skill (`v4.5.1`). It groups fourteen papers into eleven principles and project-specific adaptations; publication status and host behavior vary. The repo serves as an installable skill and standalone reference.

## File Organization

- `make-prompt-better/SKILL.md`: Core optimization workflow (under 500 lines, universal frontmatter)
- `make-prompt-better/references/domain-templates.md`: 12 domain certificate templates
- `make-prompt-better/references/research-principles.md`: Quick-reference for 11 principle groups citing 14 papers
- `make-prompt-better/references/examples.md`: 9 before/after transformations
- `docs/`: Essential installation, usage, testing and release guides
- `README.md`: Project overview with research links and cross-tool install instructions
- `install.sh`: One-command installer for all major coding agent skill directories

Internal plans, audits, drafts and generated outputs belong under `.private/`. The public checkout and all required checks must work without that directory.

## Key Constraints

- **Requirement preservation (`[REQ-PRESERVE]`)**: Preserve every user-requested deliverable, sub-question, output ordering rule, and decision-relevant operational constraint (budget, latency, timeline, target audience). When optimizing `CLAUDE.md` / `AGENTS.md`, fulfill any explicitly requested overview/layout/style items compactly (`Section 0`, `<= 5` lines) rather than silently deleting them.
- **No dashes as punctuation**: No em/en dashes as sentence punctuation anywhere. Use commas, colons, semicolons. Hyphens in compounds (goal-blind, semi-formal) are fine.
- **Universal cross-tool compatibility**: `SKILL.md` frontmatter must contain only `name` and a single-line quoted `description` starting with `"Use when..."` (no colons or multi-line YAML folding markers that break cross-runtime parsers).
- **Attribution is paramount**: Cite methodological rules and distinguish a paper's measured result from this project's adaptation. The eleven principle groups include fourteen cited papers.
- **Goal-blind**: Strip evaluative pressure, sycophancy triggers, and presupposed verdicts from prompt templates while retaining operational constraints.
- **Positive recipes over prohibitions**: Express template rules as positive structural contracts and observable-predicate conditionals rather than bare "Do NOT" anti-pattern lists (avoid the negative prohibition trap).
- **Progressive disclosure**: `SKILL.md` under 500 lines. Heavy content goes in `references/`.

## Adding a New Domain Template

1. The current contract requires exactly 12 numbered templates. Propose an expansion before changing the count; update `AGENTS.md`, the skill, README, and CI together if the contract is deliberately revised.
2. When an expansion is accepted, open `make-prompt-better/references/domain-templates.md` and follow the established pattern:
   - Authority-framed preamble (per Geng et al., 2025)
   - PREMISES with `[P1]`, `[P2]` identifiers (per Zhang, Hu et al., 2026)
   - EVIDENCE TRACES with `[T1]`, `[T2]` identifiers (or `[V1]` Verification Gates for LRM/Harness templates)
   - Positive grounding rule with observable predicates (per Yin et al., 2026)
   - FORMAL CONCLUSION with trace references
   - REMEDIATION / NEXT ACTION block and TRACEABILITY SELF-CHECK
   - Persona guidance line (OMIT/MINIMAL/FULL per Hu, Rostami & Thomason, 2026)
3. Update the template count consistently across the agreed contract and validation surfaces.
4. Add a before/after example in `make-prompt-better/references/examples.md` if the domain is commonly used

## Adding a New Research Paper

When incorporating a new paper:

1. Add entry to `make-prompt-better/references/research-principles.md` with Finding, Constraint, When to cite
2. Add the paper to the Research Foundation section in `SKILL.md`
3. Update the Prompt Structure Framework table in `SKILL.md` if the paper affects component mapping
4. Keep full citations, arXiv links and methodological limits in the functional research reference
5. Update the research overview in `README.md` when its paper count or source link changes; keep full citations in the functional research reference
6. Record relevant cost/benefit limitations beside the affected functional reference or template
7. Verify the paper is consistently cited across all files using the format: `(Author, Year)`

## Current Principle Groups (11)

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

## Mandatory Verification Gate

Before completing any modification to this repository:
- Run `npm run verify` from the source checkout for structural checks, release metadata, linters, Bash syntax, benchmark tests, and installer/package integration. CI's required `validate` check also waits for the Linux/macOS regression matrix and artifact preflight.
- Run `python3 lint_context.py --self-test && python3 lint_context.py CLAUDE.md AGENTS.md` and `node scripts/lint-prompt.mjs --self-test && node scripts/lint-prompt.mjs CLAUDE.md AGENTS.md`.
- Run `./install.sh` to synchronize `make-prompt-better/SKILL.md` across all local coding agent directories and confirm exit code 0.
