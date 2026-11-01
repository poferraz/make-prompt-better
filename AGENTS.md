<!-- Context Architecture Contract: Generic directory trees and standard language style guides are omitted per Gloaguen et al. (2026) to protect agent context window. -->
# make-prompt-better Agent Operating Contract (v4.3.0)

This file follows **Template 11 (`[CONTEXT-FILES]`, Gloaguen et al., 2026, arXiv:2602.11988)** from `make-prompt-better/references/domain-templates.md`.

## 1. Non-Inferable Validation & Sync Commands
- Sync skill across local coding agents (`~/.agents`, `~/.claude`, `~/.qwen`, `~/.gemini`): `./install.sh`
- Run CI validation check locally (strictly enforces `<500` line limit on `SKILL.md`, universal YAML frontmatter, 12 templates in `domain-templates.md`, and zero em/en dashes across all core Markdown files):
  `python3 -c 'import re; files=["make-prompt-better/SKILL.md","make-prompt-better/references/domain-templates.md","make-prompt-better/references/research-principles.md","make-prompt-better/references/examples.md","docs/methodology.md","docs/tradeoffs.md","docs/when-to-use.md","docs/task-classification.md","README.md","CLAUDE.md","AGENTS.md","research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md"]; bad=[p for p in files if re.search(r"[\u2014\u2013]", open(p).read())]; assert not bad, f"Dashes in {bad}"; s=open("make-prompt-better/SKILL.md").read(); assert len(s.splitlines())<500; m=re.match(r"^---\nname: make-prompt-better\ndescription: \"(Use when [^\n:\"]+)\"\n---\n", s); assert m and len(m.group(1))<450; assert len(re.findall(r"^## \d+\.", open("make-prompt-better/references/domain-templates.md").read(), re.M))==12; print("VALIDATED OK")'`

## 2. Hard Architectural & Editorial Invariants
- [I1] Punctuation rule: Never use em dashes or en dashes as sentence punctuation in any Markdown file; use commas, colons, or semicolons. Hyphens in compound words (`semi-formal`, `goal-blind`) are permitted.
- [I2] Universal `agentskills.io` frontmatter: `make-prompt-better/SKILL.md` must contain only `name: make-prompt-better` and a single-line double-quoted `description` starting with `"Use when..."` (under 450 characters, zero colons inside the description string).
- [I3] Progressive disclosure ceiling: Keep `make-prompt-better/SKILL.md` under 500 lines; place domain templates, research summaries, and before/after examples in `make-prompt-better/references/`.
- [I4] Requirement preservation, attribution & goal-blindness: Preserve every user-requested deliverable, ordering requirement, and operational constraint (`[REQ-PRESERVE]`, Invariant #1); cite at least one of the 11 research papers in `(Author, Year)` format for every methodological rule; keep prompt templates goal-blind (Cao, Jiang & Xu, 2026) and use positive observable-predicate recipes (Yin et al., 2026).

## 3. Mandatory Verification Gate
Before declaring any change complete:
1. Run the validation one-liner and `./install.sh` from Section 1.
2. Confirm exit code 0 and cite the command output in your response.
