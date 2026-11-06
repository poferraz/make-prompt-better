# Claims and evidence register

This register covers the consequential claims reviewed in the 2026-11-06 audit. It is not an exhaustive verification of every number in the historical documents. Treat source observations, project adaptations, and current measurements as different categories.

| Claim | Evidence and scope | Current status |
| --- | --- | --- |
| Generated repository context affects cost and task success | [Gloaguen et al. (2026), v3, sections 4.2 and 4.4](https://arxiv.org/html/2602.11988v3) reports increased cost and statistically non-significant average accuracy differences in the studied settings | Source finding; the project's exact pruning recipe is an adaptation |
| Skill metadata uses attention | [Yin et al. (2026)](https://arxiv.org/html/2608.12610v1) examines skill metadata and attention | Source finding; the previously attributed negative-versus-positive wording experiment was not located |
| Context language models report accuracy and compute changes | [Shao et al. (2026)](https://arxiv.org/abs/2609.37725) reports the cited result on BrowseComp-Plus | Source finding for that experiment, not evidence for this project's scratchpad rule |
| Earlier project evaluations contain both positive and negative results | [Historical v4.2.0 summary](../research/benchmark/v4/SUMMARY_V4_ALL_MODELS.md) and saved aggregate | Reproducible descriptive results under mixed protocols and self-judging; not a current efficacy estimate |
| The current skill improves outcomes | No new controlled outcome study has been run for v4.4.0 | Unknown |
| All listed hosts discover and run the skill correctly | Filesystem targets and isolated installer tests are available | End-to-end host behavior unknown until individually tested |
| npm publishing setup is configured | Environment/secret metadata and `.github/workflows/publish-npm.yml`; [runbook and evidence](npm-publishing.md) | Configuration is distinct from token validity, package ownership, and a successful publish |
| `npx make-prompt-better` is a working registry install | Registry lookup returned 404 on 2026-11-06 | Unpublished at that check; future publication and package ownership unknown |
| Positive observable-predicate recipes and the creative typicality threshold | Project rules, informed by the research groups | Adaptations; their exact effects and the model's probability calibration are not established |

The skill groups fourteen identified papers into eleven principle groups. Some have published venues; a blanket peer-review claim for all fourteen has not been established. Before adding a new effect size, record its paper version, benchmark, population, metric, and limitations, and separately identify whether the project actually measured the same outcome.
