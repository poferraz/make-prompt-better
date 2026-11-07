<!-- Context Architecture Contract: Generic directory trees and standard language style guides are omitted per Gloaguen et al. (2026) to protect agent context window. -->
# make-prompt-better Agent Operating Contract (v4.5.1)

This file follows **Template 11 (`[CONTEXT-FILES]`, Gloaguen et al., 2026, arXiv:2602.11988)** from `make-prompt-better/references/domain-templates.md`.

## 1. Non-Inferable Validation & Sync Commands
- Full source verification, including CLI, installer and npm archive tests: `npm run verify`. For structural, release metadata, lint and Bash syntax checks only: `npm run verify:fast`. CI additionally requires the Linux/macOS coverage and mutation matrix before `validate` can pass. These commands do not synchronize real agent installations or publish.
- Sync skill across local coding agents (`~/.agents`, `~/.claude`, `~/.qwen`, `~/.gemini`): `./install.sh`
- Test npm packaging and release gates without publishing: `python3 -m unittest discover -s tests -p test_npm_release.py -v`. Use the explicit Actions operation for token checks; keep credentials out of local fixtures.
- Run CI validation check locally (strictly enforces `<500` line limit on `SKILL.md`, universal YAML frontmatter, 12 templates in `domain-templates.md`, and zero em/en dashes across all core Markdown files):
  `python3 scripts/validate_repo.py`

## 2. Hard Architectural & Editorial Invariants
- [I1] Punctuation rule: Never use em dashes or en dashes as sentence punctuation in any Markdown file; use commas, colons, or semicolons. Hyphens in compound words (`semi-formal`, `goal-blind`) are permitted.
- [I2] Universal `agentskills.io` frontmatter: `make-prompt-better/SKILL.md` must contain only `name: make-prompt-better` and a single-line double-quoted `description` starting with `"Use when..."` (under 450 characters, zero colons inside the description string).
- [I3] Progressive disclosure ceiling: Keep `make-prompt-better/SKILL.md` under 500 lines; place domain templates, research summaries, and before/after examples in `make-prompt-better/references/`.
- [I4] Requirement preservation, attribution & goal-blindness: Preserve every user-requested deliverable, ordering requirement, and operational constraint (`[REQ-PRESERVE]`, Invariant #1); cite at least one of the 11 research papers in `(Author, Year)` format for every methodological rule; keep prompt templates goal-blind (Cao, Jiang & Xu, 2026) and use positive observable-predicate recipes (Yin et al., 2026).

- [I5] Internal storage: Keep plans, audits, drafts, research records and generated output under the single ignored `.private/` root. Keep its inventory local; never force-add it or depend on it for public validation. Essential usage guides stay in `docs/`.

## 3. Mandatory Verification Gate
Before declaring any change complete:
1. Run the validation command and `./install.sh` from Section 1.
2. Confirm exit code 0 and cite the command output in your response.
