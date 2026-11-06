# Guided installation for v4.5.1

The user approved a bare `npx make-prompt-better` guided installer, automatic installation verification, compatibility with existing commands, repository/onboarding review, tests, and preparation of v4.5.1 without publishing.

## Approach

Reuse the current Node CLI, terminal prompts, and Bash installer. A terminal invocation with no arguments enters a two-choice flow: coding agent, then user or project scope. Accept numbered choices and existing runtime/scope names. Display friendly agent names and directory hints. Install in copy mode, then run the existing read-only check for exactly the same selection. Report readiness only after both succeed, then explain how to invoke the skill.

Silently selecting detected directories would be quicker but could install into the wrong scope. A new prompt dependency would add packaging and maintenance work for two questions. The existing zero-dependency flow fits the approved behavior.

## Boundaries

- Bare noninteractive execution continues to show help and changes no skill files. Both stdin and stdout must be terminals to enter the guide.
- Explicit help, version, install, init, check, update, uninstall, and lint keep their existing behavior and flags. Automatic verification belongs to the new bare guided path.
- No write occurs until both choices are valid. Cancellation and EOF exit without installing. Installation failure skips verification; verification failure exits nonzero and never reports readiness.
- Recovery, duplicate migration, Cursor conflicts, source installation, and symlink support remain with the existing installer. The guide uses copy mode.
- Existing version tags, npm 4.5.0, and historical evidence remain unchanged. v4.5.1 has no release date or public-installation claim until separately released and tested.

## Onboarding and repository review

Impeccable's README leads with `npx impeccable install`, followed by a short usage instruction, with advanced paths in secondary documentation. Apply that ordering and progressive disclosure to this repository's installation content, while clearly labeling the unpublished v4.5.1 guide and preserving a working 4.5.0 route.

Review active version surfaces, CLI help, README links, quickstart, installation/release/testing guides, package contents, and contributor instructions. Preserve historical research, audit records, and unrelated working files.

## Verification

Use real pseudo-terminal sessions and isolated homes/projects for names, numeric choices, invalid input, both scopes, repeat/recovery, cancellation, EOF, help, redirected I/O, install failure, and a real post-install mismatch. Exercise the same guide from an actual npm tarball. Run the full source suite, required validator and isolated installer, package checks, coverage and mutation gates, and hosted Linux/macOS checks. No publication or tag creation is authorized.

Reference: [Impeccable README](https://github.com/pbakaus/impeccable/blob/main/README.md), reviewed 2026-11-06.
