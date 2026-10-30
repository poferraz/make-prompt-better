# make-prompt-better Agent Operating Contract

This file follows **Template 11 (`[CONTEXT-FILES]`, Gloaguen et al., 2026, arXiv:2602.11988)** from `make-prompt-better/references/domain-templates.md`.

## 1. Non-Inferable Validation & Sync Commands
- Sync skill across local coding agents (`~/.agents`, `~/.claude`, `~/.qwen`): `./install.sh`
- Run CI validation check locally (verifies `<500` line limit, universal YAML frontmatter, 12 templates, and zero em/en dashes):
  `python3 -c 'import re; [ None for p in ["make-prompt-better/SKILL.md","make-prompt-better/references/domain-templates.md","make-prompt-better/references/research-principles.md","make-prompt-better/references/examples.md","docs/methodology.md","docs/tradeoffs.md","docs/when-to-use.md","docs/task-classification.md","README.md","CLAUDE.md","AGENTS.md"] if (_:=open(p).read()) and ( _ for _ in [1] if not re.search(r"[\u2014\u2013]", _) or (_ for _ in ()).throw(AssertionError(p))) ]; print("VALIDATED OK")'`

## 2. Hard Architectural & Editorial Invariants
- [I1] Punctuation rule: Never use em dashes or en dashes as sentence punctuation in any Markdown file; use commas, colons, or semicolons. Hyphens in compound words (`semi-formal`, `goal-blind`) are permitted.
- [I2] Universal `agentskills.io` frontmatter: `make-prompt-better/SKILL.md` must contain only `name: make-prompt-better` and a single-line double-quoted `description` starting with `"Use when..."` (under 450 characters, zero colons inside the description string).
- [I3] Progressive disclosure ceiling: Keep `make-prompt-better/SKILL.md` under 500 lines; place domain templates, research summaries, and before/after examples in `make-prompt-better/references/`.
- [I4] Attribution & goal-blindness: Every methodological rule must cite at least one of the 11 research papers in `(Author, Year)` format, and all prompt templates must remain goal-blind (Cao, Jiang & Xu, 2026) and use positive observable-predicate recipes (Yin et al., 2026).

## 3. Mandatory Verification Gate
Before declaring any change complete:
1. Run the validation one-liner and `./install.sh` from Section 1.
2. Confirm exit code 0 and cite the command output in your response.
