# Post-v4.3.0 repository and GitHub audit

Audit baseline: local and remote `main` both resolved to `cd3b8a85b8bedbdbe40a4e7bc1759aaf888b4ebd`. The prior published release was `v4.2.0`. This is a point-in-time record; release and CI links in the completion report establish publication status.

| ID | Area | Finding and evidence | Status | Priority | Action |
|---|---|---|---|---|---|
| A1 | CI | [Run 41276030776](https://github.com/poferraz/make-prompt-better/actions/runs/41276030776) failed two stale tests. A new custom-seed assertion also reproduced `[17,17,42,42,42]`. | Fixed and verified | P0 | Updated test contract, strengthened anonymized-label assertions, forwarded seed through all inference stages. `npm test` passes 20 benchmark tests, 4 statistics tests, and the JS linter self-test. |
| A2 | Installation | npm registry returned HTTP 404 for `make-prompt-better`; README advertised it as a primary install path. | Fixed and verified | P0 | Use source installation. Cursor project smoke test passed. npm publication remains optional, with ownership and packaging checks first. |
| A3 | Versions | CLI, Python metadata, plugin manifests, citation, hero and Cursor description still referred to 4.2.0. | Fixed and verified | P1 | Metadata agrees on 4.3.0. CLI and Cursor description derive from their canonical files. `scripts/check-release.py` now checks release surfaces in CI. |
| A4 | Release | README linked to nonexistent `v4.3.0`; changelog ended at 4.2.0. | Fixed and verified | P1 | Published [v4.3.0](https://github.com/poferraz/make-prompt-better/releases/tag/v4.3.0) at `cd65de6` after [CI 41276790459](https://github.com/poferraz/make-prompt-better/actions/runs/41276790459) passed; re-read tag SHA and release state. |
| A5 | Workflow maintenance | Workflow had implicit token permissions, mutable action references, no update configuration, and incomplete frontmatter enforcement. | Fixed and verified | P1 | Read-only contents permission, SHA pins verified against official action repos, monthly Dependabot, timeout, concurrency, strict frontmatter and release checks. Local workflow validation and remote CI 41276790459 passed. |
| A6 | Contributor experience | Contribution, PR and feature guidance rejected operational constraints and implied every small fix needed a research paper. | Fixed and verified | P1 | Align with requirement preservation, explain the 12-template invariant, add verification commands and first-contribution routes. |
| A7 | Security/support | SECURITY.md incorrectly claimed there was no executable code or API integration. | Fixed and verified | P1 | Describe actual code/API scope, supported version policy and volunteer response targets. Added SUPPORT.md and issue routing; kept the existing private contact. |
| A8 | Discoverability | About used “Double-Blind”, homepage was empty, and that topic overstated the mixed historical protocols. | Fixed and verified | P1 | Updated description and README homepage, removed double-blind topic, and re-read all fields via GitHub. Retained 15 relevant existing topics. |
| A9 | Claims and evidence | Package description generalized an old +25.9% result. README foregrounded broad claims rather than installation and limitations. | Fixed and verified | P1 | Removed package uplift claim, added both positive and negative protocol results near the README opening, and labeled them as earlier-version results. This audit did not remeasure v4.3.0 or revalidate every paper. |
| A10 | Existing governance | Community profile reports 100%; MIT license, code of conduct, contribution guide, templates, citation and labels exist. Open issue and PR lists were empty. | Already complete | P2 | Preserve these assets. File presence alone does not prove content accuracy, as A6-A7 show. No tracked TODO/FIXME backlog found in audited docs/configuration. |
| A11 | Branch safeguards | Protection previously had no required status check; rulesets list is empty. | Fixed and verified | P1 | Re-read protection confirms strict `validate` checks, force pushes and deletions disabled. Existing admin exemption is unchanged; administrators can still bypass checks. No required review count was added for the sole maintainer. |
| A12 | Sharing | GraphQL `usesCustomOpenGraphImage` is false; existing SVGs provide README visuals, not a custom social card. | Remaining | P2 | Upload a 1280x640 PNG/JPG/GIF under 1 MB in repository Settings. Reuse the established visual identity and make the first line legible at small size. |
| A13 | Community scale | At audit time: 1 star, 0 forks, no open issues/PRs; Discussions disabled. | Not applicable | P2 | Keep Issues as the single public support route. No extra forum, stale bot, or mandatory approval bottleneck is warranted now. |
| A14 | Compatibility and research limits | Installer targets six runtime families; this audit tested local sync and Cursor project output, not every runtime UI or all cited paper claims. | Remaining | P1 | Collect per-runtime versioned installation evidence and independently check source claims before using them in promotion. Historical benchmark failures remain visible. |

## Verification record

- Exact command from AGENTS.md: exit 0, `VALIDATED OK`.
- `./install.sh`: exit 0, `Done. Synced (copy) across 7 agent directory(s)`; 1 unconfigured root skipped.
- `npm test`: exit 0; 20 benchmark tests, 4 statistics tests, and all 6 JS lint-rule self-tests pass.
- `npm run lint`: exit 0; Python self-tests pass and both agent contracts score 100/100 in both linters.
- `python3 scripts/check-release.py`: exit 0, metadata and CLI agree on v4.3.0.
- Workflow's embedded Python checks: exit 0; 232 skill lines, valid frontmatter, 12 templates, punctuation and relative links pass.
- `bash -n install.sh`, installer dry-run, isolated Cursor project installation, and `git diff --check`: exit 0.
- `npm pack --dry-run`: exit 0; 16 packaged files. This is a package-content check, not npm publication or an end-to-end registry install.
- GitHub CLI initially could not connect within the sandbox. Approved network access succeeded; no repository settings remained inaccessible in the checks performed.

## Adoption experiments

| Audience | Artifact/channel | Effort | Observable success measure |
|---|---|---|---|
| Coding-agent users | A 45-second terminal recording: clone, install, optimize one request while preserving its constraints | 1-2 hours | Three independent users reproduce the install and submit useful feedback within two weeks |
| Prompt/tool maintainers | A short before/after example linking the exact skill version, input, output, and limitations | 1 hour | Two reproducible examples or correction PRs within a month |
| Research-minded users | A write-up comparing positive and negative v4.2.0 protocol results, with a proposed v4.3.0 rerun | 2-3 hours plus separately budgeted evaluation | One independently reproduced result or documented methodological correction |
| Prospective contributors | One narrowly scoped issue per confirmed runtime/documentation gap, labeled `good first issue` only when steps and acceptance checks are ready | 30 minutes per issue | First accepted external contribution and time to first maintainer response |

Record a baseline before each experiment. Evaluate adoption through successful use and useful contributions; stars are a secondary signal. Sending outreach is outside the authorized publication work and has not been performed.

Draft announcement, for use after release verification:

> make-prompt-better v4.3.0 helps turn rough requests into prompts with explicit deliverables and verification steps. This update preserves operational constraints, uses lighter structure for routine analysis, and keeps creative planning out of the final answer. It also fixes installation docs and release consistency. Earlier benchmarks had mixed results across protocols, which remain documented. Try one real task from the README and report what was preserved, lost, or unnecessarily expanded: https://github.com/poferraz/make-prompt-better

## Platform references

The workflow controls follow [GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use). The social-card recommendation follows [GitHub's social preview requirements](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview). The homepage and topics support navigation and classification; they do not guarantee discovery or growth.
