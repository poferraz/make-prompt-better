# npm publishing setup and runbook

## v4.5.1 release

Version 4.5.1 was released on GitHub and npm on 2026-11-07 (UTC). The [protected publication workflow](https://github.com/poferraz/make-prompt-better/actions/runs/42317679119) used the stored bootstrap token after authorization and artifact review. The source tag and publisher both identify `6d0772b41eb458608207506e010cd2a563cbf327`, whose [main CI passed](https://github.com/poferraz/make-prompt-better/actions/runs/42317071879). All 48 public archive files matched that source. v4.4.0 and v4.5.0 remain unchanged.

The publish job succeeded. Its first public smoke returned npm command exit 1 just after the registry began serving the correct identity and digest. A fresh isolated download then passed, followed by the credential-free [verification-only workflow](https://github.com/poferraz/make-prompt-better/actions/runs/42318325467). Publication was not repeated.

Public installation, checking, update, recovery, and uninstall passed on Linux and macOS. On macOS, the exact `npx make-prompt-better` command passed in both project and user scopes, including npm's package confirmation, the installer choices, automatic verification, and repeated installation preserving local edits. An upgrade from public 4.5.0 to 4.5.1 preserved an edited copy in recovery. `npm audit signatures` verified the registry signature and provenance attestation. [Dated npm evidence](evidence/2026-11-07/v4.5.1-npm-verification.json) and [provenance transparency record](https://search.sigstore.dev/?logIndex=3726930162).

The public GitHub source archive also matched every tracked file and passed isolated installation and all five opt-in host checks without model requests. [Source verification evidence](evidence/2026-11-07/v4.5.1-source-verification.json).

The published npm tarball and its README remain the immutable source-finalization snapshot, with a link to this current runbook. These later documentation updates do not overwrite the package or move its tag. OIDC authorization, native Windows, WSL, and new model-outcome evaluation remain outside this evidence.

## v4.5.0 release

Version 4.5.0 was published on 2026-11-06 through the protected GitHub workflow using the stored bootstrap token, after separate authorization. The unauthenticated public installation test passed on macOS, including update, uninstall, and recovery. Pinned `npx` commands passed in user and project scopes. `npm audit signatures` verified the registry signature and provenance attestation. [Dated evidence](evidence/2026-11-06/v4.5.0-npm-verification.json).

The [publication run](https://github.com/poferraz/make-prompt-better/actions/runs/42306630180) accepted the package, but its immediate public lookup returned 404 while npm was processing it. The later independent public test passed against the reviewed artifact's SHA-512 digest. Do not rerun publication to recover a read-back failure; use `verify-public` below.

Source tag `v4.5.0` remains at `21e6c964e2e3bfeb511349c0c5811fc0b11b7bcf`. The publisher ran from verified main commit `c487a3505a5098e01238f6cea241fc972fa0b1a4`; its repair changed only workflows and tests, and all 47 packaged files matched the released source. Provenance identifies that publishing workflow commit. The v4.4.0 tag remains unchanged.

The npm 4.5.0 tarball and its packaged README are immutable release snapshots. No package was overwritten. At that release, an upgrade between two public npm versions was unverified; the later 4.5.1 test above records that upgrade. Public filesystem tests do not establish host discovery or model behavior.

## Earlier setup observations

The [configuration snapshot](evidence/2026-11-06/npm-setup.json) records metadata from before publication. At that point the registry returned 404, and the [authentication-only run](https://github.com/poferraz/make-prompt-better/actions/runs/42280955141) had accepted the stored token without publishing. Those observations remain historical evidence, not the current distribution status.

The environment was `npm-publish`, with reviewer `poferraz`, version-tag and main branch policies, and a secret named `NPM_TOKEN`. The secret's value was never read locally. Its presence and authentication were separate from the later successful publication. Current results are in [npm workflow runs](https://github.com/poferraz/make-prompt-better/actions/workflows/publish-npm.yml).

## Consumer installation

Run `npx make-prompt-better` in a terminal for the guided installer, use the [pinned npm commands](installation.md#install-from-npm) for automation, or follow the [source quickstart](quickstart.md). Public customers need no token. Node.js 22+ and Bash are required for the npm CLI; Git and Bash suffice for the source installer. Downloading the package alone does not activate the skill. The guide installs and checks the selected copy; explicit `install` and `check` remain separate commands.

Keep one active scope and use copy mode with npm. Selecting a new package version does not refresh an already copied skill automatically; run that version's `update` command. Recovery copies remain outside skill discovery roots.

## Protected maintainer configuration

Keep publishing credentials in the protected GitHub environment, never in the skill, package, prompt, repository, or customer configuration. Public verification and pull-request tests receive no npm credentials. The only steps receiving the stored token are the authentication-only check and the explicitly selected bootstrap publish step.

In repository **Settings > Environments**, configure `npm-publish` with a required maintainer reviewer. Allow protected `main` and version tags. Main runs the maintained workflow; publishing separately checks out and verifies the selected immutable release tag. Add or replace `NPM_TOKEN` directly in GitHub, or enter it at the hidden CLI prompt:

```bash
gh secret set NPM_TOKEN --env npm-publish --repo poferraz/make-prompt-better
gh secret list --env npm-publish --repo poferraz/make-prompt-better
```

The second command lists names, not values. A 404 from the environment public-key endpoint means the environment or access needs checking. Updating a secret does not publish. [GitHub environment secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

Prefer trusted publishing for ongoing releases. Configure the package's npm trusted publisher with these exact fields, and follow npm's current setup requirements:

| Field | Value |
| --- | --- |
| GitHub owner | `poferraz` |
| Repository | `make-prompt-better` |
| Workflow filename | `publish-npm.yml` |
| Environment | `npm-publish` |

The OIDC step receives no `NPM_TOKEN`. Verify a separately authorized OIDC release before claiming this route works or retiring the temporary bootstrap credential. Bootstrap publication with signed provenance does not prove OIDC publishing authorization. [Trusted publisher setup and migration](https://docs.npmjs.com/trusted-publishers/).

## Preflight and authentication

From a full source checkout, run:

```bash
npm run verify
python3 -m unittest discover -s tests -p test_npm_release.py -v
```

The required `validate` check calls `npm-preflight.yml` on every main push and PR, alongside source validation and the Linux/macOS regression matrix. Neither preflight path receives npm credentials. To run it manually:

```bash
gh workflow run publish-npm.yml --ref main -f operation=preflight --repo poferraz/make-prompt-better
```

To check the stored token without publishing:

```bash
gh workflow run publish-npm.yml --ref main -f operation=check-token -f auth_mode=bootstrap-token --repo poferraz/make-prompt-better
```

The environment reviewer approves before GitHub releases the secret. The check sends one request to npm's identity endpoint and reports only the account name or an error category. It never checks out package code or logs the token. Success proves authentication at that time, not future validity, package ownership, write scope, Bypass 2FA, or publishing permission.

| Result | Next action |
| --- | --- |
| Secret missing or contains whitespace | Replace it with the exact generated value using the hidden prompt |
| HTTP 401 | Check expiry, revocation, and credentials |
| HTTP 403 | Inspect token/account policy and allowed IP ranges; the status alone does not identify the cause |
| Network or unexpected response | Check npm availability and repeat only the read-only check |
| Authentication succeeds but publication requires OTP/2FA | Check direct publish permission and current package policy; use OIDC or interactive publishing when required |
| Stage-only permission | This workflow does not promote staged packages; select the intended publishing process |

[npm token configuration](https://docs.npmjs.com/creating-and-viewing-access-tokens/) and [publishing authentication requirements](https://docs.npmjs.com/requiring-2fa-for-package-publishing-and-settings-modification/) describe the current account settings. Do not send tokens to an assistant or add them to test fixtures.

## Publish a future authorized version

1. Merge the final source and release metadata through CI. Wait for every required check on the exact main commit.
2. Obtain authorization for its GitHub tag and release. Keep previous tags unchanged.
3. Obtain separate authorization for npm publication, naming the package and version.
4. Dispatch the maintained workflow from verified main, selecting the immutable source tag. Replace `vX.Y.Z` below with that new authorized version. Do not republish an existing version.

```bash
gh workflow run publish-npm.yml --ref main -f operation=publish -f release_tag=vX.Y.Z -f auth_mode=bootstrap-token --repo poferraz/make-prompt-better
```

After OIDC is configured and separately authorized, select `-f auth_mode=oidc`. A normal push or GitHub release does not automatically publish to npm.

The guard requires the intended repository, stable tag, main ancestry, published GitHub release, exact-source main CI, unused registry version, and matching package version. It reads all CI run pages and rejects incomplete evidence or a failed latest run/attempt. It verifies executable modes, archive boundaries, lifecycle hooks, credential patterns, size, and installation behavior in temporary directories. It packs once and uploads that reviewed artifact. The protected publishing job downloads the same artifact, verifies its digest, and publishes with lifecycle scripts disabled and provenance requested.

The separate credential-free public job checks registry identity and integrity, then runs the public installation smoke. It retries HTTP 404 at most 20 times with 15-second pauses while npm processes the version. Other HTTP failures and identity/integrity mismatches stop immediately. Review the actual registry attestation after publication.

## Repeat public verification without publishing

This operation retains the stable-tag, source ancestry, exact-source CI, archive, and trusted-integrity checks. It skips publication and token checking and has no npm credentials or environment approval:

```bash
gh workflow run publish-npm.yml --ref main -f operation=verify-public -f release_tag=v4.5.1 --repo poferraz/make-prompt-better
```

To run the public smoke locally from a full source checkout, supply the digest from the independently reviewed artifact, not solely from the registry being tested:

```bash
python3 scripts/public_npm_smoke.py --tag v4.5.1 --integrity 'sha512-QQkPL5XHZWWNS9EqUex/FCoGH10YYqKVhINkpQoqd+IK26veOCYfTrNOVMDGssNeUr6gjxKuftrlA3QXhxZQ8A=='
```

The test uses empty npm configurations, isolated homes, and fresh caches. It downloads the exact public package with lifecycle hooks disabled, audits its archive and trusted digest, installs the public version into a separate prefix, and compares every installed byte with the archive. It checks the executable link and exercises project installation, repeats, checking, edited-copy rejection, update, recovery, and uninstall. It does not prove host discovery or model behavior.

After this passes, follow the pinned customer commands in disposable user and project scopes. A separate temporary installation can run `npm audit signatures` to verify the registry signature and attestation. Record platform and tool versions, package integrity, source/workflow commits, and run URLs under `docs/evidence/`. Exclude credentials and private paths. Update customer docs only after public verification passes.

## Recovery and remaining limits

- After a successful publish, use `verify-public` to retry failed verification. Never retry publication merely to make a run green.
- A package correction needs a new reviewed version or an explicitly authorized deprecation. Do not overwrite a published version, move tags, or rely on unpublishing as routine rollback. Preserve the source fallback and recovery data.
- OIDC publishing needs its own successful test. Token validity at publication does not establish future expiry, permissions, or account policy.
- The recorded 4.5.0-to-4.5.1 upgrade does not establish every upgrade path. Native Windows, WSL, and broader host/model behavior need separate evidence. Filesystem tests do not expand those claims.
