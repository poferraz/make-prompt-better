# Host compatibility

The installer has automated filesystem tests for the target directories below. On 2026-11-06, the unreleased working tree was also checked against locally available hosts on macOS using isolated home and project directories. Apart from the Codex invocation described below, model invocation and reference loading remain unverified. These checks do not establish compatibility with other host versions.

| Target | Filesystem tests | Host discovery evidence and limits |
| --- | --- | --- |
| Claude Code | Temporary project and isolated-home tests | Claude Code 2.1.319 validated a local plugin and confirmed its installation, skill listing, update, and uninstall in an isolated user configuration. This checks the local marketplace plugin route; model invocation is untested. |
| Gemini CLI | Isolated-home tests | Gemini CLI 0.63.0 discovered project and global copies. When both were installed, the project copy took precedence and the host reported a conflict. The opt-in suite's two tests also checked update, backup, and uninstall, and exercised the offline `ActivateSkillTool` with a stubbed host configuration: it activated the skill body and listed all three reference resources. Full authenticated invocation and model-driven reference reads remain untested. |
| Antigravity | Isolated-home tests | Host discovery and invocation untested. |
| Codex | Isolated-home and duplicate-migration tests | Codex CLI 0.163.0 discovered project and global installations in fresh app-server processes through install, update, uninstall, and recovery. A separate signed-in `codex exec --ephemeral --sandbox read-only` invocation used an isolated project skill; its tool trace accessed `references/domain-templates.md` and its answer reported the Template 1 heading. It exited 0 after an unauthenticated Neon MCP startup error. This is one invocation, not a desktop picker check. Earlier v4.4.0 candidate checks are recorded in [discovery evidence](evidence/2026-11-06/v4.4.0-candidate-discovery.json). |
| Cursor | Isolated-home, rule conflict, symlink, and rule-reference path tests | Cursor was unavailable for host testing. The tested source generates rule reference paths relative to the rule file, but actual rule loading and reference access remain unverified. |
| Qwen | Isolated-home tests | The isolated `SkillManager` library from `@qwen-code/qwen-code` 0.26.9 loaded the parsed project and user skill. Project scope took precedence; update, backup, and uninstall were checked. The test read the references directly from the filesystem, not through a model. Authenticated CLI and model invocation remain untested. The probe is pinned to package version 0.26.9 and its `chunks/chunk-HQA2UOVS.js` bundle. |

The host checks are opt-in and must be run from a source checkout containing these test files: `MPB_TEST_CODEX_HOST=1 python3 -m unittest discover -s tests -p test_codex_host.py -v`, `MPB_TEST_GEMINI_HOST=1 python3 -m unittest discover -s tests -p test_gemini_host.py -v`, `MPB_TEST_CLAUDE_BIN=/path/to/claude python3 -m unittest discover -s tests -p test_claude_host.py -v`, and `MPB_TEST_QWEN_HOST=1 MPB_QWEN_PACKAGE_DIR=/path/to/@qwen-code/qwen-code python3 -m unittest discover -s tests -p test_qwen_host.py -v`. They make no model requests. The recorded host results apply to the tested source state below; they do not automatically verify any tagged release.

Recorded source state: baseline commit `801e028f0975162c2bb23f8544fbffc1c5258a46` with uncommitted changes. SHA-256 fingerprints for the tested working-tree inputs:

| Input | SHA-256 |
| --- | --- |
| `install.sh` | `88479362d34b10edc721b2a47bba73199086adeb199fdb59609eb93eb6ac3692` |
| `make-prompt-better/SKILL.md` | `da9a1e37d8fa22932300d319a5da1168374bca12dd40f34873a486c366459b1b` |
| `make-prompt-better/references/domain-templates.md` | `901c85559a597fe8b110da28176bd8b6fcf3706eea3bc70fdcf3619e6a825ca5` |
| `bin/cli.mjs` | `e90472392b6ba57065d20513c6051c87b8a1a7fd7e67833e1ff17fb924ef4042` |

Cursor documents discovery from both `.cursor/skills/` and `.agents/skills/` in project and user scopes. Installing the same skill into both roots could create duplicate discovery or selection; that behavior has not been observed in a host test. [Cursor skills documentation](https://cursor.com/docs/skills).

For future host checks, record the operating system, host version, exact source state, installation mode, discovered skill path, invocation, reference loading, output, update, uninstall, and backup restoration. Include failure cases and the transcript or other verifiable evidence.
