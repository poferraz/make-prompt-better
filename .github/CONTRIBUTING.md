# Contributing to make-prompt-better

Thank you for your interest in contributing. This project is built on peer-reviewed research, and we ask that all contributions meet the same standard.

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct. By participating, you agree to uphold its terms. Be respectful, constructive, and inclusive in all interactions.

## Attribution Philosophy

This project synthesizes the work of original researchers. We do not claim their ideas as our own. Every contribution must credit the original source. If a technique comes from a paper, cite the paper. If an insight comes from a blog post or community discussion, link to it. When in doubt, over-attribute.

## Quality Bar

Every contribution must cite research or provide empirical evidence. We do not accept prompt patterns based solely on anecdote or intuition. Acceptable foundations include:

- Peer-reviewed papers (preferred)
- Reproducible benchmarks with documented methodology
- Documented real-world results with sufficient sample size

## Contribution Types

### New Domain Templates

To contribute a new domain certificate template:

1. Open `make-prompt-better/references/domain-templates.md`
2. Add a new numbered section following the established pattern. Every template must include:
   - **Authority-framed preamble**: Establish domain expertise in the opening lines (per Geng et al., 2025)
   - **PREMISES**: Numbered with [P1], [P2] identifiers (per ACE framework from Zhang, Hu et al., 2026)
   - **EVIDENCE TRACES**: Numbered with [T1], [T2] identifiers
   - **"Do NOT" instruction**: A domain-specific constraint that prevents common failure modes
   - **FORMAL CONCLUSION**: Must reference traces and remain goal-blind
   - **Persona guidance line**: State whether to OMIT, use MINIMAL, or use FULL persona (per PRISM: Hu, Rostami & Thomason, 2026)
3. Update the template count in `make-prompt-better/SKILL.md` and `README.md`
4. Add a before/after example in `make-prompt-better/references/examples.md` if the domain is commonly used
5. Verify: numbered identifiers present, authority framing used, goal-blind conclusion, persona guidance stated

### New Research Papers

To incorporate a new paper into the methodology:

1. Add an entry to `make-prompt-better/references/research-principles.md` with three fields: Finding, Constraint, When to cite
2. Add the paper to the Research Foundation section in `make-prompt-better/SKILL.md`
3. Update the Prompt Structure Framework table in `make-prompt-better/SKILL.md` if the paper affects component mapping
4. Add to `docs/methodology.md` with full citation and arXiv link
5. Add to `README.md` Attribution section with full citation
6. Add to `docs/tradeoffs.md` if the paper has cost/benefit implications
7. Verify consistent citation across all files using the format: (Author, Year)

### Citation Format

- Inline: (Ugare & Chandra, 2026) or (Cao, Jiang & Xu, 2026)
- Full: Author names, title, year, venue, arXiv link

## Pull Request Process

1. Fork the repository and create a branch from `main`
2. Make your changes following the guidelines above
3. Ensure all new content follows the formatting rules below
4. Open a pull request with a clear description of what you are adding and why
5. Reference any relevant papers or evidence in the PR description
6. Respond to review feedback

## Formatting Rules

### No Dashes as Punctuation

Do not use em dashes or en dashes as sentence punctuation anywhere in this project. Use commas, colons, or semicolons instead. Hyphens in compound words are fine: goal-blind, semi-formal, peer-reviewed are all acceptable.

Incorrect: "The methodology, based on six papers, produces better prompts."
Incorrect: "The methodology - based on six papers - produces better prompts."

Correct: "The methodology, based on six papers, produces better prompts."

### Goal-Blind Rule

All prompt templates in this project must be goal-blind. This means they must not include evaluation criteria, success metrics, or downstream use instructions. The template should specify what to analyze and how to structure reasoning, but never what a "good" or "correct" output looks like. This constraint comes from (Cao, Jiang & Xu, 2026): including evaluation criteria in prompts degrades performance because it constrains the reasoning process.

If you are unsure whether a template violates this rule, ask yourself: does this instruction tell the model what answer to reach, or does it tell the model how to think? Only the latter is acceptable.

## Questions

If you are unsure whether a contribution fits the project, open an issue first and describe what you have in mind. We are happy to discuss before you put in the work.
