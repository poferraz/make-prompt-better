# npm installation and publishing plan

Status checked on 2026-11-06 for v4.4.0. GitHub source installation is supported. `npm view make-prompt-better ... --registry=https://registry.npmjs.org` returned 404. This does not establish name availability, ownership, token permissions, or a working registry installation. No npm publication, npm account change, or GitHub secret configuration was performed for this release.

## Recommendation

Add npm as an optional distribution channel after the gates below pass. It can give Node users a short, versioned installation command. Keep Git and Bash installation for people without Node. npm will distribute the existing installer; it will not replace skill discovery, synchronize an already copied skill automatically, or remove Bash as a prerequisite. Native Windows remains untested; document WSL until separately verified.

Public customers will need no token. Your npm access token authorizes a maintainer to publish, subject to its actual permissions. It does not belong in `SKILL.md`, `package.json`, `install.sh`, a prompt, a committed `.npmrc`, or a customer configuration. `.npmrc` and package tarballs are now ignored by Git; ignored files still need package-content checks.

Prefer GitHub Actions trusted publishing with OIDC for ongoing releases. npm currently requires Node 22.14.0+ and npm 11.5.1+; use Node 24 for the future publishing job and verify the installed npm version. Trusted publishing can generate provenance automatically on GitHub-hosted runners. [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/).

npm has announced a January 2027 target for removing direct publication through bypass-2FA tokens. That makes a permanent token workflow a poor default. The date is a stated plan, not a completed policy change. [npm token changes](https://github.blog/changelog/2026-07-31-restricting-npm-bypass-2fa-granular-access-tokens/).

## What to do with the token you created

Keep it in your password manager while the publishing workflow is prepared. Do not send it to an assistant. Confirm its expiry, package access, and write permission in npm's token settings. Prefer narrow access and short expiry. A token's existence does not prove that it can create this package or pass the account's 2FA policy. [npm access-token configuration](https://docs.npmjs.com/creating-and-viewing-access-tokens/).

If a reviewed temporary publishing job needs that token:

1. Open this repository on GitHub, then **Settings > Environments**. Create `npm-publish` and restrict deployment to reviewed release tags. Configure a required maintainer reviewer if available for the account.
2. Under **Environment secrets**, add a secret named `NPM_TOKEN`, and enter the token directly into GitHub. Alternatively, after the environment exists, run the command below and enter it at the hidden prompt.
3. The future publishing job must declare `environment: npm-publish`. Only its publish step should receive `NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}`. `actions/setup-node` can generate the temporary registry configuration. Never print the variable or enable shell tracing around it.

```bash
gh secret set NPM_TOKEN --env npm-publish --repo poferraz/make-prompt-better
gh secret list --env npm-publish --repo poferraz/make-prompt-better
```

The second command lists secret names, not values. Adding a secret alone will not publish anything: this repo has no npm publishing workflow yet. [GitHub environment secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

For the first publication of a package that does not yet exist, prefer an interactive maintainer `npm login`, account/ownership verification, and a reviewed tarball publish with 2FA. Do not create an unnecessarily broad automation token just to claim a name. Treat the first publish as a separate, explicitly authorized registry action. The public registry can reject a name even after a lookup returns 404. [Publishing an unscoped public package](https://docs.npmjs.com/creating-and-publishing-unscoped-public-packages/).

Once the package exists, configure its trusted publisher with these exact identity fields:

| Field | Planned value |
| --- | --- |
| GitHub owner | `poferraz` |
| Repository | `make-prompt-better` |
| Workflow filename | `publish-npm.yml` |
| Environment | `npm-publish` |

Create that configuration when the workflow is ready: npm currently requires its first successful publish within two days. Select direct publish permission only if using `npm publish`; staged publishing is a different approval flow. After a successful OIDC release, restrict token publishing and revoke the unused token. No `NPM_TOKEN` is needed in the OIDC job. [Trusted publisher setup and migration](https://docs.npmjs.com/trusted-publishers/).

## Ordered implementation work

Effort estimates are hands-on engineering time, excluding account approvals and CI waits. The GitHub release does not depend on npm availability.

### 0. Complete the GitHub release first

- **Owner / effort:** repository maintainer; 1 to 2 hours including verification.
- **Files:** active version surfaces listed in [releasing.md](releasing.md), `tests/test_more_integration.py`, current install guides, `CHANGELOG.md`.
- **Steps:** synchronize versions; retain historical evidence labels; pass validation; merge the release PR; tag the exact passing main commit; publish notes; download the tagged source and run clean/repeated/legacy-upgrade discovery checks.
- **Positive tests:** `python3 scripts/check-release.py`, `npm test`, `npm run lint`, the AGENTS validation command, and `./install.sh`. A fresh Codex discovery process must find one enabled current skill after a clean install and a six-copy upgrade.
- **Negative tests:** stale version and missing-file cases must fail; `--check` before install or after a deliberate edit must fail; duplicate migration must retain recovery payloads outside discovery.
- **Acceptance:** published tag resolves to the checked commit, source install passes, discovery evidence states host/version/scope, and untested behavior is explicit.
- **Rollback:** before publication, revert the release PR. After publication, leave the tag immutable and publish a corrected version if needed. Users can restore a preserved skill or select an older source tag.

### 1. Confirm identity and harden the package

- **Owner / effort:** Paulo for account identity; maintainer for code; 1 to 2 hours. **Dependency:** stage 0 and npm account access.
- **Files:** `package.json`, `.gitignore`, `tests/test_integration.py`, `docs/releasing.md`, this plan.
- **Steps:** verify `npm whoami` interactively and recheck `npm view make-prompt-better maintainers version --json`; confirm rights to the exact name. If unavailable, decide a scoped name before changing commands. Add `publishConfig` for the intended public registry and access level, keeping the package file allowlist. Inspect all packaged README links and executable modes. No install/postinstall hooks should write skill folders; only explicit `init` may do that.
- **Commands:** `npm pack --dry-run --json`; `npm pack --pack-destination /tmp`; `python3 -m unittest discover -s tests -p test_integration.py -v`.
- **Positive tests:** install the actual tarball into a temporary prefix with `npm install --ignore-scripts --no-audit --no-fund --prefix <temp-prefix> <tarball>`; invoke `--version`, bare help, `init --project --runtime codex --copy`, and `init --project --runtime codex --check` from a temporary project. Repeat installation and migrate six old copies. Move the package/cache directory afterward and confirm the copied skill still loads.
- **Negative tests:** reject unknown flags, detect a changed skill, preserve unrelated skills, retain backups, and fail installation cleanly for symlinked/locked targets. Seed fake `.npmrc` and `.env` files only in a fixture copy and assert the tarball excludes them, recovery data, test artifacts, and benchmark run outputs. Never seed fake credentials in the actual working tree.
- **Acceptance:** no secret/config file or unexpected executable is packaged; no user-home mutation from npm installation or bare CLI execution; exactly one current skill in the chosen scope after `init`; verified registry rights. A dry run is not publication proof.
- **Rollback:** revert packaging changes before publishing. Preserve the Bash source path throughout.

### 2. Prepare the publishing workflow and bootstrap

- **Owner / effort:** maintainer for implementation, Paulo for npm/GitHub settings; 2 to 4 hours. **Dependency:** stage 1.
- **Files:** new `.github/workflows/publish-npm.yml`, existing `.github/workflows/validate-skill.yml` and `.github/workflows/recurring-tests.yml`, `scripts/check-release.py`, `docs/releasing.md`.
- **Steps:** use a published-release trigger, a GitHub-hosted runner, pinned action revisions, `contents: read`, and `id-token: write` only for the publish job. Bind `npm-publish`, disable package-manager caching in that job, and set concurrency to prevent competing publishes. Verify the tag equals `v` plus `package.json` version, targets a validated main commit, and is not a draft/prerelease unless deliberately supported. Run tests in a job without publish credentials; publish only after it succeeds. Reject an existing registry version. Pack once, inspect and hash that tarball, then publish the same tarball. This zero-runtime-dependency repo has no lockfile, so do not copy an `npm ci` step without adding and justifying one.
- **Bootstrap:** explicitly authorize the first reviewed package publication. If package settings are unavailable until that succeeds, use an interactive 2FA publish first; record that it did not use OIDC. Configure the trusted publisher above for subsequent releases. A temporary token job is optional, not the default.
- **Positive tests:** exercise workflow validation and tarball smoke tests without credentials; then authorize one real release, verify registry version/integrity and, for OIDC publication, the attestation's repository and commit.
- **Negative tests:** wrong tag/version, failed CI, fork identity, duplicate version, and absent publisher configuration must prevent publication. Simulate control-flow rejection locally; test registry auth failures only in an agreed disposable test package. Never attempt malicious or wrong-account publication against the real package.
- **Acceptance:** the exact reviewed artifact appears under the authorized package identity, with matching integrity and documented provenance. Configuration files alone do not satisfy this gate.
- **Rollback:** disable the workflow and revoke temporary credentials. A published npm version cannot be overwritten; release a correction or deprecate the bad version with a recovery message. Do not rely on unpublishing as routine rollback.

### 3. Verify the registry path before changing the landing page

- **Owner / effort:** maintainer; 1 to 2 hours. **Dependency:** successful publication.
- **Files:** `tests/test_integration.py` or a new manual registry-smoke script, `docs/compatibility.md`, `docs/claims.md`, release evidence under `docs/evidence/`.
- **Commands:** `npm view make-prompt-better@4.4.0 version dist.integrity dist.attestations --json`, followed by the proposed commands below in a temporary home and a disposable project. Substitute the actually published version if it differs.
- **Positive tests:** unauthenticated download with an empty user npm config/cache; `--version`; clean install; repeat; six-copy migration; fresh Codex discovery; update from a previously published package when one exists; uninstall and manual recovery. Record macOS and Linux separately, and WSL only when actually tested.
- **Negative tests:** nonexistent version fails without modifying skills; unavailable network fails without replacing the active skill; unknown options fail; an edited skill makes `--check` fail. Do not declare native Windows support from Linux tests.
- **Acceptance:** public customers can install without a token, installed bytes match the published artifact, and each tested scope has one current discoverable skill. Desktop picker behavior, invocation, and reference loading need their own evidence.
- **Rollback:** retain source-install instructions, stop advertising the failing registry route, and publish a correction. Reinstall a chosen known-good release or restore its recovery copy.

### 4. Update every customer and maintainer touchpoint

- **Owner / effort:** maintainer; 1 to 2 hours. **Dependency:** stage 3 passes.
- **Files:** `README.md`, `docs/quickstart.md`, `docs/installation.md`, `docs/compatibility.md`, `docs/claims.md`, `docs/releasing.md`, `docs/testing.md`, `SUPPORT.md`, `.github/CONTRIBUTING.md`, `CHANGELOG.md`, `package.json`, `bin/cli.mjs` help, and this plan.
- **Steps:** add a short npm route beside the source route, Node/Bash prerequisites, a pinned package version, explicit `init`, copy mode, expected check output, invocation, update/reinstall, uninstall, and recovery. State that `npm update` alone does not refresh a copied skill. Audit links from the packaged README. Update registry status only with dated evidence. Keep the skill's method instructions and research history independent of its distribution channel.
- **Positive tests:** follow each new command in an empty environment; check packaged links and CLI help; have a first-time user complete install, invoke, update, and recover without reading maintainer docs.
- **Negative tests:** verify prerequisite and permission errors explain the next action; verify no copy-and-paste guide requests a consumer token or creates both user and project installs.
- **Acceptance:** the documented route matches observed behavior and works without knowing internal mode names. Source installation remains available.
- **Rollback:** revert customer-facing npm instructions while preserving evidence and release history.

### 5. Optional upgrades after a working npm release

- **Owner / effort:** maintainer; 2 to 6 hours each, scoped separately. **Dependencies:** stages 1 through 4.
- **Files:** potential native-Windows installer and tests; `bin/cli.mjs` for a version-aware update command; `.github/workflows/publish-npm.yml` for staged publishing; `assets/README.md` for social materials.
- **Steps and tests:** design each separately. A future update command must show the chosen version, preserve edits, and fail safely offline; a Windows route needs native host discovery and recovery tests; social material must only advertise the verified public command. Require positive and negative tests before expanding support claims.
- **Acceptance / rollback:** independently documented host/version evidence and a working source fallback; remove an experimental route if its checks fail. No adoption, efficacy, or universal safety claim follows from publishing.

## Proposed customer commands, not yet available on npm

Do not use these until registry verification passes:

```bash
npx --yes make-prompt-better@4.4.0 --version
npx --yes make-prompt-better@4.4.0 init --runtime codex --copy
npx --yes make-prompt-better@4.4.0 init --runtime codex --check
```

`--yes` accepts npm's package-execution prompt, so use only after verifying the package identity. Explicit `--copy` avoids linking a skill into an evictable npx cache. A later update selects the desired package version and runs `init` again. Use one scope. For uninstall, run that version's `init --runtime codex --uninstall`; recovery remains in the installer's documented backup location.

## Unverified until the rollout is performed

- npm account identity, name availability/ownership, token validity/scope/expiry, and publishing permission.
- First npm publication, public download, OIDC identity binding, registry provenance, and an npm-to-npm upgrade.
- GitHub `npm-publish` environment, stored secret, publishing workflow, and npm trusted-publisher configuration.
- Native Windows, other agent invocation, desktop picker refresh, and model-quality outcomes for the current release.
