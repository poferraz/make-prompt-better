# Host compatibility

Public npm 4.5.1 was installed without credentials on Linux and macOS on 2026-11-07. The tests verified the reviewed archive digest and installed files. macOS additionally passed the exact bare npx guide in project/user scopes, repeated installation with recovery, a 4.5.0-to-4.5.1 upgrade preserving edits, and uninstall. These are filesystem checks. See the [distribution runbook](npm-publishing.md).

The public v4.5.1 source archive at commit `6d0772b41eb458608207506e010cd2a563cbf327` also passed all five opt-in Codex, Claude, Gemini, and Qwen host checks on macOS on 2026-11-07, without model requests. The table below retains the earlier observations, including the separately recorded Codex model invocation.

The installer has automated filesystem tests for the target directories below. On 2026-11-06, the unreleased working tree was also checked against locally available hosts on macOS using isolated home and project directories. Apart from the Codex invocation described below, model invocation and reference loading remain unverified. These checks do not establish compatibility with other host versions.

| Target | Filesystem tests | Host discovery evidence and limits |
| --- | --- | --- |
| Claude Code | Temporary project and isolated-home tests | Claude Code 2.1.319 validated a local plugin and confirmed its installation, skill listing, update, and uninstall in an isolated user configuration. This checks the local marketplace plugin route; model invocation is untested. |
| Gemini CLI | Isolated-home tests | Gemini CLI 0.63.0 discovered project and global copies. When both were installed, the project copy took precedence and the host reported a conflict. The opt-in suite's two tests also checked update, backup, and uninstall, and exercised the offline `ActivateSkillTool` with a stubbed host configuration: it activated the skill body and listed all three reference resources. Full authenticated invocation and model-driven reference reads remain untested. |
| Antigravity | Isolated-home tests | Host discovery and invocation untested. |
| Codex | Isolated-home and duplicate-migration tests | Codex CLI 0.163.0 discovered project and global installations in fresh app-server processes through install, update, uninstall, and recovery. A separate signed-in `codex exec --ephemeral --sandbox read-only` invocation used an isolated project skill; its tool trace accessed `references/domain-templates.md` and its answer reported the Template 1 heading. It exited 0 after an unauthenticated Neon MCP startup error. This is one invocation, not a desktop picker check. |
| Cursor | Isolated-home, rule conflict, symlink, and rule-reference path tests | Cursor was unavailable for host testing. The tested source generates rule reference paths relative to the rule file, but actual rule loading and reference access remain unverified. |
| Qwen | Isolated-home tests | The isolated `SkillManager` library from `@qwen-code/qwen-code` 0.26.9 loaded the parsed project and user skill. Project scope took precedence; update, backup, and uninstall were checked. The test read the references directly from the filesystem, not through a model. Authenticated CLI and model invocation remain untested. The probe is pinned to package version 0.26.9 and its `chunks/chunk-HQA2UOVS.js` bundle. |

The host checks are opt-in and must be run from a source checkout containing these test files: `MPB_TEST_CODEX_HOST=1 python3 -m unittest discover -s tests -p test_codex_host.py -v`, `MPB_TEST_GEMINI_HOST=1 python3 -m unittest discover -s tests -p test_gemini_host.py -v`, `MPB_TEST_CLAUDE_BIN=/path/to/claude python3 -m unittest discover -s tests -p test_claude_host.py -v`, and `MPB_TEST_QWEN_HOST=1 MPB_QWEN_PACKAGE_DIR=/path/to/@qwen-code/qwen-code python3 -m unittest discover -s tests -p test_qwen_host.py -v`. They make no model requests. The recorded host results apply to the recorded source versions; they do not automatically verify any tagged release.


Cursor documents discovery from both `.cursor/skills/` and `.agents/skills/` in project and user scopes. Installing the same skill into both roots could create duplicate discovery or selection; that behavior has not been observed in a host test. [Cursor skills documentation](https://cursor.com/docs/skills).

For future host checks, record the operating system, host version, exact source state, installation mode, discovered skill path, invocation, reference loading, output, update, uninstall, and backup restoration. Include failure cases and the transcript or other verifiable evidence.
