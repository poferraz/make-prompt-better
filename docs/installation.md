# Install, update, and recover

For a first installation, start with the [quickstart](quickstart.md). This is the v4.5.1 release snapshot; check the [current distribution status](https://github.com/poferraz/make-prompt-better/blob/main/docs/npm-publishing.md) for publication and verification results. Both earlier release tags remain unchanged.

## Distribution status

GitHub source and public npm version 4.5.0 are available. The unauthenticated public package lifecycle passed on macOS on 2026-11-06; see the [evidence and limits](npm-publishing.md). An npm installation requires Node.js 22+ and Bash and does not activate the skill by itself. Public consumers do not need a publisher token.

## Install from npm

v4.5.1 adds the two-choice guided installer. After publication and public verification, run `npx make-prompt-better` in a terminal, choose your agent and scope, and wait for the automatic file check. From this source checkout, run `node bin/cli.mjs`. It installs a copy, accepts numbers or names, and allows `q` to cancel before installation. With redirected input or output it shows help and changes no skill files.

For the previously verified 4.5.0 package, use:

```bash
npx --yes make-prompt-better@4.5.0 install --runtime codex --global --copy
npx --yes make-prompt-better@4.5.0 check --runtime codex --global --copy
```

Choose your host and one scope. For a project, run from that project's directory and replace `--global` with `--project`. Add `--dry-run` to preview installation. Copy mode prevents the skill from depending on the npm cache. `--yes` accepts npm's execution prompt for this pinned package.

To reinstall or update the selected copy, select the desired published package version and run:

```bash
npx --yes make-prompt-better@4.5.0 update --runtime codex --global --copy
npx --yes make-prompt-better@4.5.0 check --runtime codex --global --copy
```

`update` uses that selected package's files. For a future release, replace `4.5.0` in both commands with the desired published version. `npm update` alone does not refresh a copied skill. Existing edits are preserved in [recovery storage](#recovery).

To remove the selected installation:

```bash
npx --yes make-prompt-better@4.5.0 uninstall --runtime codex --global --dry-run
npx --yes make-prompt-better@4.5.0 uninstall --runtime codex --global
```

Use the same host and scope as your installation. Uninstall preserves recovery copies and does not clear npm's cache.

## Node CLI

These commands require Node.js 22+ and Bash. The named commands remain compatible with v4.5.0. v4.5.1 adds bare interactive installation and verification. Run these examples from this checkout:

```bash
node bin/cli.mjs install --runtime codex --global --dry-run
node bin/cli.mjs install --runtime codex --global
node bin/cli.mjs check --runtime codex --global
node bin/cli.mjs update --runtime codex --global
node bin/cli.mjs uninstall --runtime codex --global --dry-run
node bin/cli.mjs uninstall --runtime codex --global
```

Replace `codex` and `--global` with your chosen host and scope. To target a project, run the CLI by its absolute path from that project's directory and use `--project`. `init` and the direct `install.sh` commands remain supported. The CLI delegates to the same installer, so the backup, conflict, and recovery rules below still apply.

In a terminal, named commands can prompt for a host and scope. Only the bare guided flow automatically checks after installation; explicit commands retain their existing behavior. For noninteractive `check`, `update`, and `uninstall`, pass both `--runtime` and either `--global` or `--project`, as shown above. Existing noninteractive `install` and `init` defaults remain available for compatibility; explicit options are recommended in scripts. `--help` and `--version` do not install anything.

`update` uses the skill files in the checkout or package running the command; it does not download a new version. Select the source version first using the [update instructions](#update), then run `update` for the same host and scope. Copy mode is the default: if you installed with `--symlink`, pass `--symlink` again to `update` and `check`. Otherwise, an update backs up the existing link and replaces it with a copy. `check` compares the selected installation against that source; it does not test host discovery or model behavior.

## Choose a scope and host

A global installation is available to your user account. A project installation writes to the current working directory. Pick one scope for a given host: Codex can show separate project and global skills with the same name. In a Gemini CLI 0.63.0 working-tree test, a project copy took precedence over a global copy and the host reported a conflict. [Host evidence and limits](compatibility.md).

```bash
# Preview, install, and check one user installation.
./install.sh --runtime codex --dry-run
./install.sh --runtime codex
./install.sh --runtime codex --check

# Or, from a project's directory, run the installer by its absolute path.
/path/to/make-prompt-better/install.sh --runtime codex --project
```

Replace `/path/to/make-prompt-better` with your actual checkout. Supported runtime selectors are `claude`, `gemini`, `antigravity`, `codex`, `cursor`, and `qwen`. The default runtime is `all`: it installs the shared `.agents` copy and skips other unconfigured global agent folders. `--all` creates those folders too. `--help` lists the options.

The installer needs Bash and standard filesystem utilities. macOS and Linux are intended shell environments; Windows users need WSL. Native PowerShell and other hosts are untested. Node.js 22+ and Python 3.10+ are required only for the corresponding optional tools.

## One active Codex copy

Codex's canonical target is `~/.agents/skills/make-prompt-better` globally, or `.agents/skills/make-prompt-better` in a project. This follows the [official skill discovery documentation](https://developers.openai.com/codex/skills/), checked on 2026-11-06. Codex can display both skills when their names match; it does not merge them.

After the current target is installed successfully, the installer removes sibling entries whose `SKILL.md` frontmatter identifies `make-prompt-better`. For Codex it also migrates copies from `.codex/skills` in the same scope. This includes the `.bak.*` folders produced by the earlier installer. Other skills and unrelated similarly named folders stay in place.

Removed entries are moved into `.make-prompt-better/backups` at the chosen home or project root. These recovery directories are outside the supported skill and rule discovery roots. The source checkout is authoritative: an install copies its current files, without contacting a registry, choosing versions by modification time, or claiming that the checkout is the newest published version.

The cleanup covers direct children of the selected discovery roots. It does not edit other projects, admin folders, plugin caches, custom host roots, or host configuration. Check those separately if duplicates remain.

## Update

Choose a published version from [GitHub releases](https://github.com/poferraz/make-prompt-better/releases). Review `git status --short` first. If it lists changes, commit or otherwise preserve them before switching versions. Once v4.5.1 is released, select it with these commands. Until then, use the published `v4.5.0` tag instead:

```bash
git status --short
git fetch --depth 1 origin tag v4.5.1
git switch --detach v4.5.1
./install.sh --runtime codex
./install.sh --runtime codex --check
```

For a different release, replace `v4.5.1` in both Git commands with its published tag. A detached checkout is expected when selecting a tag; `git pull` is not the update path for that checkout. If Git reports a conflict, preserve your local changes and resolve it before updating the installation. A copy install uses a stable snapshot until you run the installer again. `--symlink` is optional for maintainers who want local edits to take effect immediately; it requires keeping the checkout at the same location. Use the same mode when checking a symlink installation: `./install.sh --runtime codex --symlink --check`.

## Check or uninstall

`--check` is read-only. Exit 0 means the selected installation files match this checkout and no duplicate identities were found in those roots. Exit 1 reports a missing or different copy, duplicates, an invalid path, or another error. It does not certify host discovery or model behavior.

```bash
./install.sh --runtime codex --check
./install.sh --runtime codex --uninstall --dry-run
./install.sh --runtime codex --uninstall
```

Uninstall removes the selected active copy and recognized duplicate entries, preserving them in recovery storage. It does not delete the source repository, other skills, or previous recovery data.

## Recovery

Every replaced or removed target gets a uniquely named directory under `.make-prompt-better/backups`, containing:

- `payload`: the original directory, rule file, or symlink.
- `original-path.txt`: the exact location it came from.

The installer prints the recovery location. Inspect that directory and its original path before restoring. Move any current target to a separate safe location outside skill discovery, then move `payload` back to the path in `original-path.txt`. Restore only the version you intend to use, then re-open your host. A restored old copy will deliberately differ from the current source; `--check` should report that difference. Installing again replaces it with the current source.

Backups of symlinks retain the link itself, not a snapshot of its referent. Restoring a relative symlink at its original path restores its original resolution. Keep the source checkout if you rely on a symlink installation. Recovery storage is not automatically pruned because it may contain user edits.

The installer stages new skill files outside discovery before replacing an existing target. A staged copy failure leaves the previous install in place; a final move failure may leave it in recovery storage. Multi-target installation is per target, so some targets may complete before another fails. Locks reduce concurrent collisions, but hostile filesystem races and every interruption point are not proven safe.

Cursor rules are written only when Cursor is selected. An unmanaged rule needs `--backup` before replacement or removal. Symlinked rule files, destination parents, and recovery parents are refused.

In checkouts containing the Cursor rule path fix, generated rules identify reference files relative to the rule's `.cursor/rules/` directory. Tests check that those paths resolve to the installed skill in project and global scopes; actual Cursor rule loading and reference access are unverified. The v4.4.0 source release predates this fix. Cursor also documents discovery from both `.cursor/skills/` and `.agents/skills/`. Installing the same skill in both roots could lead to duplicates; this has not been confirmed in a host test. [Cursor skills documentation](https://cursor.com/docs/skills).

## Troubleshooting

| What you see | What to do |
| --- | --- |
| Bare command shows help | Check `--version`. v4.5.0 needs `install`. The v4.5.1 guide needs an interactive terminal for both input and output; in automation, use explicit commands with runtime and scope. |
| Several entries in Codex | Run the current Codex installer and `--check`. Restart Codex if its picker is stale. Check for a separate project, admin, or plugin copy if it persists. |
| No skill in the picker | Confirm the target exists, restart the host, and check its discovery instructions. Filesystem placement alone does not prove the host loaded it. |
| `Missing or different from this checkout` | Confirm you are checking the intended checkout, runtime, scope, and copy/symlink mode. Reinstall if this source is the version you want. |
| `Installation target is locked` | Check that no installer is running. A forced termination can leave an empty `.lock` directory; remove that exact stale directory only after checking. |
| `Refusing symlinked destination parent` | Inspect the path printed by the installer. Use a real supported destination directory; do not delete a link without understanding where it points. |
| `Unmanaged Cursor rule` | Review your custom rule. Use `--backup` only when you want to preserve and replace it. |
| `git`, `bash`, or `node` not found | Install the tool needed for the command. Node is optional for skill installation; use Bash to run `install.sh`. |

For help, include the host and operating system, command, expected behavior, and sanitized output in a [support request](../SUPPORT.md). Avoid posting credentials or private prompt content.
