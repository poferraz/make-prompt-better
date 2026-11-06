# Discovery and first-use refinement

This follow-up audits the working tree produced by the earlier implementation and addresses the reported six-entry Codex picker. Existing repository edits, original audit reports, and historical benchmark artifacts were preserved. No release, registry package, deployment, or public post was created.

## Findings and changes

| Urgency | Evidence and impact | Implemented improvement | Verification |
| --- | --- | --- | --- |
| High | The previous `backup_existing` implementation put complete skills in `.bak.*` siblings under discovery roots. Codex's local `skills/list` returned six enabled entries: two canonical copies and four backups. Users could invoke stale instructions. | [Installer](../install.sh#L149) now uses `.agents/skills` for Codex, migrates same-name entries from the selected roots including legacy `.codex/skills`, and puts recovery files outside discovery. Staging also lives outside discovery. | [Captured before/after response](evidence/2026-11-06/codex-discovery.json): six entries became one, no discovery errors. [Regression tests](../tests/test_skill_discovery.py) cover the reported layout, repeat installs, alias names, and uninstall. |
| High | Backup placement was verified, but the earlier tests never checked what an agent could discover. File safety alone missed the user-facing failure. | Added a read-only `--check` path and an actual Codex discovery check for this machine. Recovery receipts record original paths. | `--check` passed on all six current filesystem targets. Complete file fingerprints matched for all 21 original folders moved into recovery. Full model execution remains outside this check. |
| Medium | Invoking the Node CLI with no arguments performed a global installation. A newcomer exploring the command could unexpectedly change agent folders. | [CLI](../bin/cli.mjs#L45) now shows help on bare invocation; `init` explicitly installs. | Negative test confirms no files are created in an isolated home. Existing explicit install and failure propagation tests still pass. |
| Medium | The earlier README had 336 lines, including mode names, multiple dense tables, and historical benchmark figures. It made installation and technical interpretation compete with the first useful example. | [README](../README.md) now leads with an everyday example, a chat starter, and distinct agent-assisted and terminal install routes. [Quickstart](quickstart.md) explains skill, scope, invocation, expected checks, and review. | Local Markdown preview at 1280x900 and 390x844. No page-wide horizontal overflow, missing image, or missing top-level CTA anchor; starter and evidence navigation and duplicate-help disclosure exercised. This approximates GitHub rendering. |
| Medium | Plugin metadata still described 11 papers and verifiable certificates despite the earlier claims cleanup. The picker description was long and technical. | [Plugin metadata](../.claude-plugin/plugin.json) and [marketplace metadata](../.claude-plugin/marketplace.json) now describe research-informed rewriting. [Codex UI metadata](../make-prompt-better/agents/openai.yaml) supplies a plain display name and a prompt-only default. | Release checks pass. The fresh Codex discovery response includes the new display name, description, brand color, and default prompt. |
| Medium | The visual materials mixed a technical diagram style with marketing claims, and small embedded text was hard to read on a phone. | Added a static [cover](../assets/prompt-cover.png), removed dense historical graphics from the README, and retained essential text in Markdown. [Asset notes](../assets/README.md) identify the artwork and retained legacy figures. | Visually inspected at desktop and phone widths. The cover is artwork; it does not depict live execution. No conversion or accessibility certification is claimed. |

## Installation contract

The current checkout is the installation source of truth. The installer does not query a registry or infer the newest version from timestamps. On this machine, a fresh Codex CLI 0.163.0 app-server process loaded exactly one enabled `make-prompt-better` from `$HOME/.agents/skills/make-prompt-better/SKILL.md` after migration. The [official discovery documentation](https://developers.openai.com/codex/skills/) also identifies `.agents/skills` as the user skill root and explains that same-name skills can both appear.

Other supported runtimes retain their own installation paths. Recovery storage is `$HOME/.make-prompt-better/backups` globally, or `.make-prompt-better/backups` at the selected project root. Every receipt has `original-path.txt` and `payload`. All 21 pre-migration installed folders matched their recovery payload file hashes. See [recovery instructions](installation.md#recovery).

For the captured discovery evidence, the local app-server received `initialize`, then `initialized`, then this read-only request:

```json
{"id":2,"method":"skills/list","params":{"cwds":["<repository path>"],"forceReload":true}}
```

It did not create a chat or invoke a model. The saved evidence normalizes the home directory and records hashes for the installed source bundle.

## Verification

- `npm test`: exit 0, 58 benchmark tests, four statistics tests, the then-current 48 integration tests, and the JavaScript self-test. After adding identity-parsing and manual-recovery cases, the final integration run passed all 50 tests. Loopback fixture tests used a local server; no live inference occurred.
- `npm run lint`: exit 0. The findings remain heuristics, not semantic or safety proofs.
- `python3 scripts/check-release.py`: exit 0, `[PASS] Release metadata and CLI agree on v4.3.0`.
- `python3 tests/mutation_probe.py`: exit 0; four targeted mutants killed.
- Final JavaScript coverage gates: exit 0, 94.89% lines and 90.74% branches; each module also meets its configured floor. Coverage is not a correctness guarantee.
- Bash syntax and `git diff --check`: exit 0.
- Exact AGENTS validation: exit 0, `VALIDATED OK`.
- Final `./install.sh`: exit 0, `Done. Processed (copy) 6 agent target(s) (6 already current; 1 unconfigured agent roots skipped; pass --all to force all).`
- Final Codex `--check`: exit 0, `Check passed. Selected installations match this checkout; no duplicate entries in the checked roots.`
- Installer positive and negative cases include migration from the six-entry layout, repeated installation, preserving unrelated skills, symbolic-link referents, failed copy, locked legacy installation, symlinked recovery storage, read-only preview/check, malformed frontmatter, uninstall when the canonical target is missing, and manual restoration followed by an update.

The earlier safety tests continue to cover failed final moves, unique backups, source-equals-target, Cursor rule conflicts, symlinked destination parents, and interruption recovery. Backups are manual recovery, not an all-target transaction or proof against every filesystem race.

## Remaining validation

- The desktop application's already-open picker may cache old entries. Restart Codex if needed. Fresh engine discovery is verified; the desktop picker itself was not refreshed or clicked.
- Duplicate cleanup is limited to recognized frontmatter identities among direct children of selected roots. Other scopes, nested custom directories, admin installations, plugin copies, and alternate host configuration are not automatically deleted.
- Full invocation, reference loading, and model output quality still need a recorded host test. Other hosts and native Windows remain untested end to end.
- The README was checked in a local GitHub-style renderer. Remote GitHub rendering, 200% browser zoom, assistive-technology testing, and novice-user success have not been measured.
- The cover is a generated PNG of about 1.95 MB. It is decorative and has a text alternative. A smaller publishing derivative can be evaluated if network performance becomes a concern.
- The README keeps a source-install path because registry ownership and publication are unverified. Remote CI has not run on this working tree; the version number does not identify a newly published release.
- Older SVGs and historical changelog prose remain preserved. Their old labels and numerical claims are not current evidence. Review the [claims register](claims.md) before reusing them.

## Next useful checks

Before promoting a release, the maintainer should record one clean install-to-invocation-to-recovery journey on each claimed host and run CI on the exact release commit. Then ask a novice, an occasional AI user, and a developer to find the entry point, improve a real request, and explain what they must verify. Record where they hesitate and whether any original requirements are lost. This is a proposed usability study, not evidence that every customer can already succeed.
