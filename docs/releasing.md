# Release checklist

1. Inspect open issues, pull requests, and the previous release comparison. Keep historical benchmark results labeled with their original version and protocol.
2. Update `package.json`, both plugin manifests, `pyproject.toml`, `CITATION.cff`, `install.sh`, the skill version, README badge, hero version, and `CHANGELOG.md`. The CLI reads its version from `package.json`; the Cursor rule reads its description from the skill.
3. Run `python3 scripts/check-release.py`, `npm test`, `npm run lint`, `bash -n install.sh`, and `./install.sh --dry-run`. Run the exact validation command in [AGENTS.md](../AGENTS.md) and `./install.sh`; the latter updates local agent installations.
4. Review `npm pack --dry-run` if distributing the Node CLI. Test the installation instructions from a fresh checkout. The npm package is currently unpublished; a GitHub release does not publish it.
5. Push the reviewed changes and wait for the Validate Skill, Links & Unit Tests workflow to pass on the exact commit being released.
6. Create the version tag and GitHub release targeting that commit, with notes derived from the changelog. State what changed, how it was checked, and what has not been remeasured. Verify the README version badge opens the new release.
7. Re-read the published release and repository About settings. Keep topics factual and link the homepage to current documentation. Share only claims supported by the cited results.

## Current distribution boundaries

Source installation is the supported path. npm publication requires confirming package ownership and completing a packaging smoke test before advertising registry commands. A custom social preview can be uploaded through repository settings; GitHub recommends 1280 by 640 pixels and a PNG, JPG, or GIF under 1 MB.

References: [GitHub release management](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository), [social preview requirements](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview).
