# CLAUDE.md: make-prompt-better

## Repository Purpose

This repository is a research-grounded prompt optimization skill. It synthesizes six peer-reviewed papers into an actionable methodology called semi-formal reasoning. The repo serves as both an installable Claude Code skill and a standalone reference.

## File Organization

- `skill/SKILL.md`: Core optimization workflow (under 500 lines)
- `skill/references/domain-templates.md`: 10 domain certificate templates
- `skill/references/research-principles.md`: Quick-reference for 6 papers
- `skill/references/examples.md`: Before/after transformations
- `docs/`: Standalone methodology documentation
- `README.md`: Project overview with full attribution

## Key Constraints

- **No dashes as punctuation**: No em/en dashes as sentence punctuation anywhere. Use commas, colons, semicolons. Hyphens in compounds (goal-blind, semi-formal) are fine.
- **Attribution is paramount**: Every claim must trace to a cited paper. Never claim originality for ideas from the 6 papers or severity1's architecture.
- **Goal-blind**: Never include evaluation criteria or downstream use in prompt templates.
- **Progressive disclosure**: SKILL.md under 500 lines. Heavy content goes in references/.

## Adding a New Domain Template

1. Open `skill/references/domain-templates.md`
2. Add a new numbered section following the established pattern:
   - Authority-framed preamble (per Geng et al., 2025)
   - PREMISES with [P1], [P2] identifiers (per ACE)
   - EVIDENCE TRACES with [T1], [T2] identifiers
   - "Do NOT" instruction specific to the domain
   - FORMAL CONCLUSION with trace references
   - Persona guidance line (OMIT/MINIMAL/FULL per PRISM)
3. Update the template count in SKILL.md and README.md
4. Add a before/after example in `skill/references/examples.md` if the domain is commonly used
5. Verify: numbered identifiers present, authority framing used, goal-blind conclusion, persona guidance stated

## Adding a New Research Paper

When incorporating a new paper:

1. Add entry to `skill/references/research-principles.md` with Finding, Constraint, When to cite
2. Add the paper to the Research Foundation section in SKILL.md
3. Update the Prompt Structure Framework table in SKILL.md if the paper affects component mapping
4. Add to docs/methodology.md with full citation and arXiv link
5. Add to README.md Attribution section with full citation
6. Add to docs/tradeoffs.md if the paper has cost/benefit implications
7. Verify the paper is consistently cited across all files using the format: (Author, Year)

## Citation Format

Inline: (Ugare & Chandra, 2026) or (Cao, Jiang & Xu, 2026)
Full: Author names, title, year, venue, arXiv link

## Current Papers

1. Ugare & Chandra (2026) - META - arXiv:2603.01896
2. Cao, Jiang & Xu (2026) - GOAL-BLIND - arXiv:2602.09504
3. Zhang, Hu et al. (2026) - ACE - arXiv:2510.04618
4. Geng et al. (2025) - HIERARCHY - arXiv:2502.15851
5. Mahmoudi et al. (2025) - CODE-SMELLS - arXiv:2512.18020
6. Hu, Rostami & Thomason (2026) - PRISM - arXiv:2603.18507
