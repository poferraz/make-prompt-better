# Install, update, and recover

For a first installation, start with the [quickstart](quickstart.md). Use the current source checkout for the changes described here; they are not part of the v4.3.0 tag.

## Choose a scope and host

A global installation is available to your user account. A project installation writes to the current working directory. Pick one scope for a given host: Codex can show separate project and global skills with the same name.

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

From your checkout, review any uncommitted work before pulling an update:

```bash
git status --short
git pull --ff-only
./install.sh --runtime codex
./install.sh --runtime codex --check
```

If Git reports a conflict, preserve your local changes and resolve it before updating the installation. A copy install uses a stable snapshot until you run the installer again. `--symlink` is optional for maintainers who want local edits to take effect immediately; it requires keeping the checkout at the same location. Use the same mode when checking a symlink installation: `./install.sh --runtime codex --symlink --check`.

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

## Troubleshooting

| What you see | What to do |
| --- | --- |
| Several entries in Codex | Run the current Codex installer and `--check`. Restart Codex if its picker is stale. Check for a separate project, admin, or plugin copy if it persists. |
| No skill in the picker | Confirm the target exists, restart the host, and check its discovery instructions. Filesystem placement alone does not prove the host loaded it. |
| `Missing or different from this checkout` | Confirm you are checking the intended checkout, runtime, scope, and copy/symlink mode. Reinstall if this source is the version you want. |
| `Installation target is locked` | Check that no installer is running. A forced termination can leave an empty `.lock` directory; remove that exact stale directory only after checking. |
| `Refusing symlinked destination parent` | Inspect the path printed by the installer. Use a real supported destination directory; do not delete a link without understanding where it points. |
| `Unmanaged Cursor rule` | Review your custom rule. Use `--backup` only when you want to preserve and replace it. |
| `git`, `bash`, or `node` not found | Install the tool needed for the command. Node is optional for skill installation; use Bash to run `install.sh`. |

For help, include the host and operating system, command, expected behavior, and sanitized output in a [support request](../SUPPORT.md). Avoid posting credentials or private prompt content.
