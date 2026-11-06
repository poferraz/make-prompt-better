# Guided Installer Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Prepare an unpublished v4.5.1 with a two-choice bare-command installer and automatic filesystem verification.

**Architecture:** Reuse `bin/cli.mjs`, its terminal input reader, and `install.sh`. Keep noninteractive behavior and named commands compatible. Test actual filesystem effects and failure propagation through pseudo-terminals and the packaged executable.

**Tech Stack:** Node.js 22+, Bash, Python unittest; no new runtime dependency.

**Spec:** [Guided installation design](../specs/2026-11-06-guided-install-design.md).

## Constraints and review focus

- Do not publish, tag, move existing tags, change research claims, or alter unrelated work.
- Redirected input/output, cancellation, and EOF must not cause a default installation.
- Both the install and subsequent check must use the selected runtime, scope, and copy mode.
- A failed install or failed verification must never produce a readiness claim.
- Packaged README links and version labels must remain coherent while 4.5.1 is unpublished.
- The skill contract, explicit commands, recovery, and current public 4.5.0 evidence remain intact.

## Task 1: Guided CLI and regressions

- [x] Add real PTY tests in `tests/test_guided_install.py` for project/global installation, names/numbers, invalid input, repeat/recovery, cancellation/EOF, redirected I/O/help, failed installation, and post-install mismatch.
- [x] Run the tests and confirm the new interactive paths fail before implementation.
- [x] Update `bin/cli.mjs`: terminal-only bare entry, readable choices, copy installation, same-selection check, failure propagation, and concise next step. Keep existing named commands compatible.
- [x] Exercise the packaged executable in `tests/test_integration.py` using the PTY helper; rerun focused tests and existing CLI coverage.

## Task 2: Version and onboarding preparation

- [x] Bump the active surfaces enumerated by `scripts/check-release.py` to 4.5.1. Mark the changelog unreleased and omit a premature citation release date.
- [x] Simplify README installation order, CLI help, and quickstart. Review installation, testing, release, and distribution docs and package boundaries. Label future registry commands and keep the published 4.5.0 route usable.
- [x] Preserve existing historical evidence and validate all local/packaged README links.

## Task 3: Verification and reviewable delivery

- [x] Run `npm run verify`, package/release tests, the AGENTS validator, isolated `./install.sh`, actionlint, and diff checks.
- [x] Run coverage and mutation checks; fix any failures and verify the fixes.
- [ ] Open a preparation PR, verify all hosted Linux/macOS checks, and leave the release unpublished and untagged.
- [ ] Report the implementation, test evidence, and remaining publication boundary.
