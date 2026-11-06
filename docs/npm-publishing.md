# npm publishing setup and runbook

## v4.5.0 release

The v4.5.0 changelog and citation use 2026-11-06 as the release date. GitHub release creation and npm publication are separate actions. The v4.4.0 tag remains unchanged, and public npm installation remains unverified.

Proceed through these steps separately:

1. Review and merge the release metadata PR, including the final changelog and citation date, then verify every required check on the exact main commit before tagging.
2. Obtain explicit authorization for the GitHub tag and release, naming v4.5.0 and that verified commit. Creating the GitHub release does not authorize npm publication.
3. Confirm package ownership and publishing access, then obtain separate authorization for npm publication. The guarded workflow must verify the final tagged source and the artifact it will publish.
4. After publication, run `python3 scripts/public_npm_smoke.py --tag v4.5.0 --integrity 'sha512-REVIEWED_BASE64_DIGEST'` using the digest from that independently verified release artifact. Record the outcome before describing npm installation as verified. A missing public version is a failed verification attempt, not a reason to bypass the gate.

## Earlier setup observations

Status recorded on 2026-11-06; this is a historical snapshot, not a live registry check. At that time, the GitHub v4.4.0 release was published and source installation was supported. The environment and secret had been configured; automation added after v4.4.0 was on main and needed a subsequent version tag before it could publish. The existing release tag was unchanged.

| Area | Observation or requirement at the time |
| --- | --- |
| GitHub environment | `npm-publish`, reviewer `poferraz`, version tags `v*`, and protected `main` for the read-only token check |
| Secret | `NPM_TOKEN` is present; its update timestamp changed to `2026-11-06T19:25:28Z`. The value was not read. Presence is not authentication or publishing proof. |
| Authentication | [Live check passed](https://github.com/poferraz/make-prompt-better/actions/runs/42280955141) using the replacement secret. The publish job was skipped; no package was published. |
| Automation | `.github/workflows/publish-npm.yml` separates preflight, authentication-only checking, and explicit publishing |
| Registry | Public lookup returned 404. Ownership, name availability, first publication, and registry installation remain unverified. |
| Source install route | The pinned GitHub source instructions in the README |

[Configuration observation](evidence/2026-11-06/npm-setup.json) records metadata only. Current run results are in [npm workflow runs](https://github.com/poferraz/make-prompt-better/actions/workflows/publish-npm.yml).

## Recommendation

Add npm as an optional distribution channel after the gates below pass. It can give Node users a short, versioned installation command. Keep Git and Bash installation for people without Node. npm will distribute the existing installer; it will not replace skill discovery, synchronize an already copied skill automatically, or remove Bash as a prerequisite. Native Windows remains untested; document WSL until separately verified.

Public customers will need no token. Your npm access token authorizes a maintainer to publish, subject to its actual permissions. It does not belong in `SKILL.md`, `package.json`, `install.sh`, a prompt, a committed `.npmrc`, or a customer configuration. `.npmrc` and package tarballs are now ignored by Git; ignored files still need package-content checks.

Prefer GitHub Actions trusted publishing with OIDC for ongoing releases. npm currently requires Node 22.14.0+ and npm 11.5.1+; the workflow uses Node 24 and its bundled compatible npm. Trusted publishing can generate provenance automatically on GitHub-hosted runners. [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/).

npm has announced a January 2027 target for removing direct publication through bypass-2FA tokens. That makes a permanent token workflow a poor default. The date is a stated plan, not a completed policy change. [npm token changes](https://github.blog/changelog/2026-07-31-restricting-npm-bypass-2fa-granular-access-tokens/).

## What to do with the token you created

The token is stored as a GitHub environment secret. Keep any personal recovery copy in your password manager. For temporary unattended publishing, select **Read and write (publish and stage)**, enable **Bypass 2FA at creation**, and choose a short expiry. A read-only or stage-only token cannot perform the direct publish used by this workflow. Limit package access where possible; an unpublished unscoped package may need temporary access to future packages for bootstrap. Organization management access is not package publishing permission. Do not send the token to an assistant. The displayed token name is only a label, not a package reservation. [npm access-token configuration](https://docs.npmjs.com/creating-and-viewing-access-tokens/).

For rotation or a new repository setup:

1. Open this repository on GitHub, then **Settings > Environments**. Create `npm-publish` if missing. Allow version tags `v*` and protected `main`; configure a required maintainer reviewer. Main is used for authentication-only checks; the publishing job separately requires a stable release tag.
2. Under **Environment secrets**, add a secret named `NPM_TOKEN`, and enter the token directly into GitHub. Alternatively, after the environment exists, run the command below and enter it at the hidden prompt.
3. The publishing job declares `environment: npm-publish`. Only its bootstrap publish step and the separate authentication check receive `NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}`. `actions/setup-node` can generate the temporary registry configuration. Never print the variable or enable shell tracing around it.

```bash
gh secret set NPM_TOKEN --env npm-publish --repo poferraz/make-prompt-better
gh secret list --env npm-publish --repo poferraz/make-prompt-better
```

The second command lists secret names, not values. A 404 from the environment public-key endpoint means the environment or access needs checking before retrying. Confirm the environment exists with `gh api repos/poferraz/make-prompt-better/environments/npm-publish`. Updating a secret does not publish a package. [GitHub environment secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

For the first publication of a package that does not yet exist, prefer an interactive maintainer `npm login`, account/ownership verification, and a reviewed tarball publish with 2FA. Do not create an unnecessarily broad automation token just to claim a name. Treat the first publish as a separate, explicitly authorized registry action. The public registry can reject a name even after a lookup returns 404. [Publishing an unscoped public package](https://docs.npmjs.com/creating-and-publishing-unscoped-public-packages/).

Once the package exists, configure its trusted publisher with these exact identity fields:

| Field | OIDC configuration value |
| --- | --- |
| GitHub owner | `poferraz` |
| Repository | `make-prompt-better` |
| Workflow filename | `publish-npm.yml` |
| Environment | `npm-publish` |

Create that configuration when the workflow is ready: npm currently requires its first successful publish within two days. Select direct publish permission only if using `npm publish`; staged publishing is a different approval flow. After a successful OIDC release, restrict token publishing and revoke the unused token. The OIDC publish step does not receive `NPM_TOKEN`. [Trusted publisher setup and migration](https://docs.npmjs.com/trusted-publishers/).

## Run the workflow

From a full source checkout, not an installed npm package, local checks are:

```bash
npm run verify
python3 -m unittest discover -s tests -p test_npm_release.py -v
```

The required `validate` workflow calls `npm-preflight.yml` on every main push and PR, alongside source validation and the regression/coverage matrix. `publish-npm.yml` remains manual and calls the same preflight. Neither preflight path receives npm credentials. To run preflight manually on main:

```bash
gh workflow run publish-npm.yml --ref main -f operation=preflight -f auth_mode=oidc --repo poferraz/make-prompt-better
```

To test the stored token without publishing:

```bash
gh workflow run publish-npm.yml --ref main -f operation=check-token -f auth_mode=bootstrap-token --repo poferraz/make-prompt-better
```

The `npm-publish` reviewer must approve the job before GitHub releases the secret. This job sends one authenticated request to npm's identity endpoint, records only the account name or an HTTP/error category, and never checks out or runs package code. Success proves that npm accepted the stored token from that runner. It does not prove package ownership, write scope, Bypass 2FA, or permission to publish. A failed check does not publish or alter the package.

| Result | Next action |
| --- | --- |
| Secret missing or contains whitespace | Replace `NPM_TOKEN` with the exact generated value using the hidden prompt |
| HTTP 401 | Check expired/revoked/incorrect credentials and replace the secret if needed |
| HTTP 403 | Inspect token/account policy and allowed IP ranges; the status alone does not identify the cause |
| Network or unexpected response | Check npm availability and rerun the read-only check |
| Authentication succeeds, publication requires OTP/2FA | Check Bypass 2FA, direct publish permission, and package policy; use OIDC or interactive publishing when tokens are disallowed |
| Stage-only permission | Use a staged publishing process or create the intended temporary direct-publish token; this workflow does not promote staged packages |

npm documents both the creation-time Bypass 2FA setting and package policies that can disallow tokens. An authentication check cannot replace these checks. [npm publishing requirements](https://docs.npmjs.com/requiring-2fa-for-package-publishing-and-settings-modification/).

For actual publication, first create a new stable version that includes this workflow, merge it through CI, and publish its GitHub release. v4.4.0 predates the workflow and cannot be dispatched for this operation. Replace `vX.Y.Z` below with that new release tag:

```bash
gh workflow run publish-npm.yml --ref vX.Y.Z -f operation=publish -f auth_mode=bootstrap-token --repo poferraz/make-prompt-better
```

After OIDC is configured, use `-f auth_mode=oidc` instead. There is no automatic npm publish on a GitHub release or normal push. The job checks a stable tag, main ancestry, published GitHub release, exact-commit validation, unused registry version, package identity, executable modes, file boundaries, lifecycle hooks, credential patterns, and archive size. Exact-commit validation now includes source, the Linux/macOS coverage and mutation matrix, and package preflight. The guard reads all workflow-run pages and rejects incomplete evidence or a non-successful latest run/attempt. It installs and exercises the actual tarball in temporary directories, then uploads that artifact. The publishing job downloads the same run's artifact, checks its integrity, waits for environment review, and publishes with lifecycle scripts disabled. A final public lookup checks registry identity and integrity, followed by the separate unauthenticated installation smoke. OIDC and bootstrap publishing request provenance; its actual registry attestation must be inspected after publication.

The workflow's read-only metadata token is separate from `NPM_TOKEN`. npm credentials are unavailable to pull-request tests, source validation, and packaging. If publication succeeds but read-back fails, inspect the registry before retrying; the version may already be immutable. Revoke the replaced token after the new credential check succeeds, and retire the temporary publishing token after OIDC works.

## Ordered implementation work

Effort estimates are hands-on engineering time, excluding account approvals and CI waits. The GitHub release does not depend on npm availability.

### 0. GitHub release: v4.4.0 complete; next npm-capable tag still required

- **Owner / effort:** repository maintainer; 1 to 2 hours including verification.
- **Files:** active version surfaces listed in [releasing.md](releasing.md), `tests/test_more_integration.py`, current install guides, `CHANGELOG.md`.
- **Steps:** synchronize versions; retain historical evidence labels; pass validation; merge the release PR; tag the exact passing main commit; publish notes; download the tagged source and run clean/repeated/legacy-upgrade discovery checks.
- **Positive tests:** `python3 scripts/check-release.py`, `npm test`, `npm run lint`, the AGENTS validation command, and `./install.sh`. A fresh Codex discovery process must find one enabled current skill after a clean install and a six-copy upgrade.
- **Negative tests:** stale version and missing-file cases must fail; `--check` before install or after a deliberate edit must fail; duplicate migration must retain recovery payloads outside discovery.
- **Acceptance:** published tag resolves to the checked commit, source install passes, discovery evidence states host/version/scope, and untested behavior is explicit.
- **Rollback:** before publication, revert the release PR. After publication, leave the tag immutable and publish a corrected version if needed. Users can restore a preserved skill or select an older source tag.

### 1. Package checks and authentication verified; package ownership still unverified

- **Owner / effort:** Paulo for account identity; maintainer for code; 1 to 2 hours. **Dependency:** stage 0 and npm account access.
- **Files:** `package.json`, `.gitignore`, `tests/test_integration.py`, `docs/releasing.md`, this plan.
- **Steps:** verify `npm whoami` interactively and recheck `npm view make-prompt-better maintainers version --json`; confirm rights to the exact name. If unavailable, decide a scoped name before changing commands. `publishConfig`, the file allowlist, archive checks, and executable-mode checks are implemented. Review them when changing package contents. No install/postinstall hooks should write skill folders; only explicit `init` may do that.
- **Commands:** `npm pack --dry-run --json`; `npm pack --pack-destination /tmp`; `python3 -m unittest discover -s tests -p test_integration.py -v`.
- **Positive tests:** install the actual tarball into a temporary prefix with `npm install --ignore-scripts --no-audit --no-fund --prefix <temp-prefix> <tarball>`; invoke `--version`, bare help, `init --project --runtime codex --copy`, and `init --project --runtime codex --check` from a temporary project. Repeat installation and migrate six old copies. Move the package/cache directory afterward and confirm the copied skill still loads.
- **Negative tests:** reject unknown flags, detect a changed skill, preserve unrelated skills, retain backups, and fail installation cleanly for symlinked/locked targets. Seed fake `.npmrc` and `.env` files only in a fixture copy and assert the tarball excludes them, recovery data, test artifacts, and benchmark run outputs. Never seed fake credentials in the actual working tree.
- **Acceptance:** no secret/config file or unexpected executable is packaged; no user-home mutation from npm installation or bare CLI execution; exactly one current skill in the chosen scope after `init`; verified registry rights. A dry run is not publication proof.
- **Rollback:** revert packaging changes before publishing. Preserve the Bash source path throughout.

### 2. Workflow implemented; first publication and OIDC setup remain

- **Owner / effort:** maintainer for implementation, Paulo for npm/GitHub settings; 2 to 4 hours. **Dependency:** stage 1.
- **Files:** new `.github/workflows/publish-npm.yml`, existing `.github/workflows/validate-skill.yml` and `.github/workflows/recurring-tests.yml`, `scripts/check-release.py`, `docs/releasing.md`.
- **Steps:** use the implemented manual operation selector, GitHub-hosted runner, pinned action revisions, `contents: read`, and `id-token: write` only for the publish job. Automatic release-triggered publishing is deferred until the bootstrap and OIDC path are verified. Bind `npm-publish`, disable package-manager caching in that job, and set concurrency to prevent competing publishes. Verify the tag equals `v` plus `package.json` version, targets a validated main commit, and is not a draft/prerelease unless deliberately supported. Run tests in a job without publish credentials; publish only after it succeeds. Reject an existing registry version. Pack once, inspect and hash that tarball, then publish the same tarball. This zero-runtime-dependency repo has no lockfile, so do not copy an `npm ci` step without adding and justifying one.
- **Bootstrap:** explicitly authorize the first reviewed package publication. If package settings are unavailable until that succeeds, use an interactive 2FA publish first; record that it did not use OIDC. Configure the trusted publisher above for subsequent releases. A temporary token job is optional, not the default.
- **Positive tests:** exercise workflow validation and tarball smoke tests without credentials; then authorize one real release, verify registry version/integrity and, for OIDC publication, the attestation's repository and commit.
- **Negative tests:** wrong tag/version, failed CI, fork identity, duplicate version, and absent publisher configuration must prevent publication. Simulate control-flow rejection locally; test registry auth failures only in an agreed disposable test package. Never attempt malicious or wrong-account publication against the real package.
- **Acceptance:** the exact reviewed artifact appears under the authorized package identity, with matching integrity and documented provenance. Configuration files alone do not satisfy this gate.
- **Rollback:** disable the workflow and revoke temporary credentials. A published npm version cannot be overwritten; release a correction or deprecate the bad version with a recovery message. Do not rely on unpublishing as routine rollback.

### 3. Verify the registry path before changing the landing page

- **Owner / effort:** maintainer; 1 to 2 hours. **Dependency:** successful publication.
- **Files:** `tests/test_integration.py` or a new manual registry-smoke script, `docs/compatibility.md`, `docs/claims.md`, release evidence under `docs/evidence/`.
- **Read-only public smoke:** after publication, run `python3 scripts/public_npm_smoke.py --tag vX.Y.Z --integrity 'sha512-REVIEWED_BASE64_DIGEST'`, replacing both placeholders with the stable tag and the SHA-512 integrity from the previously reviewed release artifact. The digest must come from that independent artifact, not solely from the registry response being checked. The command does not publish or use a token.
- **What it checks:** from empty isolated homes, npm configs and caches, download the exact public package with lifecycle scripts disabled; inspect its archive and compare its digest with the supplied trusted value. Install the exact public registry version into a separate temporary prefix with lifecycle scripts disabled, compare every installed package file against that verified archive, check the npm executable link, and exercise project installation, checking, update, backup restoration and uninstall. It does not prove host discovery or model behavior. Failed lookups, network errors, identity mismatches and integrity mismatches stop the test before package code executes.
- **Availability:** on 2026-11-06, anonymous public registry lookups still returned 404. Until an authorized publication exists, this public smoke cannot pass; the local registry fixture and tarball checks remain separate evidence.
- **Commands:** `npm view make-prompt-better@PUBLISHED_VERSION version dist.integrity dist.attestations --json`, followed by the proposed commands below in a temporary home and a disposable project. Substitute the actually published version if it differs.
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

## Customer command template

These commands are a template for a release that has passed registry verification. Replace `PUBLISHED_VERSION` with the version actually published and tested:

```bash
npx --yes make-prompt-better@PUBLISHED_VERSION --version
npx --yes make-prompt-better@PUBLISHED_VERSION init --runtime codex --copy
npx --yes make-prompt-better@PUBLISHED_VERSION init --runtime codex --check
```

`--yes` accepts npm's package-execution prompt, so use only after verifying the package identity. Explicit `--copy` avoids linking a skill into an evictable npx cache. A later update selects the desired package version and runs `init` again. Use one scope. For uninstall, run that version's `init --runtime codex --uninstall`; recovery remains in the installer's documented backup location.

## Verification gaps recorded on 2026-11-06

At that status check, these items had not been verified. Consult later release evidence for any changes.

- Package name availability/ownership, effective token write scope/expiry, and publishing permission. Authentication succeeded in the linked run; that observation is not a guarantee of future validity.
- First npm publication, public download, OIDC identity binding, registry provenance, and an npm-to-npm upgrade.
- Actual token permissions and the npm trusted-publisher configuration. Environment/secret presence and workflow source are established separately; consult the run result for authentication evidence.
- Native Windows, other agent invocation, desktop picker refresh, and model-quality outcomes for the current release.
