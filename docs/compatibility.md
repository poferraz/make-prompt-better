# Host compatibility

The installer has automated filesystem tests for the target directories below. A fresh local Codex app-server discovery query was also run on 2026-11-06. Neither filesystem tests nor discovery prove reference loading, model behavior, or support for every host version.

| Target | Filesystem tests | End-to-end host discovery and invocation |
| --- | --- | --- |
| Claude Code | Temporary project and isolated-home tests | Unknown |
| Gemini CLI | Isolated-home tests | Unknown |
| Antigravity | Isolated-home tests | Unknown |
| Codex | Isolated-home and duplicate-migration tests | Local discovery verified on macOS with CLI 0.163.0: six entries before migration, one afterward. [Captured evidence](evidence/2026-11-06/codex-discovery.json). Desktop picker cache and full prompt execution remain untested. |
| Cursor | Isolated-home, rule conflict, and symlink tests | Unknown, including resolution of rule-relative references |
| Qwen | Isolated-home tests | Unknown |

For each host, record the operating system, host version, exact commit, installation mode, discovered skill path, invocation, reference loading, output, update, uninstall, and backup restoration. Include failure cases and the transcript or other verifiable evidence. Until then, these rows describe installer targets rather than confirmed integrations.
