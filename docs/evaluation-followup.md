# Follow-up outcome evaluation

No new model-quality evaluation was run for the unreleased changes. Select the primary host, model versions, independent judge, compute budget, data-handling rules, and stopping conditions before making live requests.

1. Freeze a code revision and a run ID. Record model/provider revisions where available, host version, skill and suite hashes, and all protocol flags. The runner's manifest records identifiers but cannot establish a mutable provider model's actual weights.
2. Predeclare the existing twelve tasks and a separately authored held-out set. Include exact deliverables, output order, deadlines, missing data, quoted adversarial instructions, and tasks where no added structure is needed. Keep held-out prompts and expected checks versioned before observing results.
3. Compare an unoptimized baseline and the rewritten prompt in separate contexts. Record the exact input, actual rewritten prompt, downstream answer, judge prompts and responses, task failures, response length, latency, and available token counts. Do not treat estimated word counts as full cost.
4. Use anonymous position-swapped scoring and an independent judge when available, plus human checks for requirement preservation, harmful additions, and whether tests actually ran. Retain unsuccessful and incomplete cases in the report.
5. Use the no-network dry run and an explicit request limit first. Set separate monetary, time, and privacy limits outside the runner; request counts do not guarantee a cost ceiling. Publish only evidence reviewed for sensitive content.
6. Report sample sizes, missing outputs, uncertainty, protocol differences, and negative results. A positive score is not a prerequisite for honest reporting, and fixture checks do not establish live safety.

The available local fixture and [example rewrite](demo.md) test selected observable details only. Host compatibility, new efficacy, and any external pilot remain unknown until actual observations are recorded.
