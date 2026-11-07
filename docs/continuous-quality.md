# Continuous quality and scoped review

The feedback cycle is measure, inspect failures, propose a small change, review the PR, then remeasure on held-out cases. Scheduled jobs are finite and read-only. They do not rewrite the skill, merge changes or publish npm releases.

## What the new paper supports

*Skill++: Towards Lifelong Agents via Routing-Aware Skill Refinement* (Zhang et al., 2026), [arXiv:2611.00544v1](https://arxiv.org/abs/2611.00544), addresses selection among growing libraries of skills. Section 3.2 grounds metadata in the skill body, distinguishes neighboring capabilities, and adds scope exclusions. Section 4 reports final FC@5 of 76.3% versus 36.4% for the original metadata in the main 731-skill experiment. FC@5 measures whether all required skills appear among five selected skills; it is not a prompt-quality score.

Appendix C.3 reports task pass-rate gains of 4.0 and 0.7 percentage points in a smaller 87-skill, 150-query Codex experiment, with a workflow requesting five skill names before tool use. Effects vary by model. The authors' limitations section restricts the study to text. These results do not establish that make-prompt-better v4.5.1 improves answers, costs less, or benefits from the same metadata changes.

The adaptation here is an experiment, not a new production rule. `evaluate_routing.py` compares the current description with a body-grounded description that explicitly distinguishes rewriting instructions from executing their task. The skill name and installed description remain unchanged. The public corpus has 12 development/holdout-tagged regression cases and three synthetic neighboring descriptions. It is not a sealed holdout or a reproduction of the paper. The paper's full refinement method also uses similarity retrieval and incoming-skill history; this small experiment does not implement those components.

## Three different file boundaries

`scripts/file_scope.py` defines runtime and review allowlists. The npm archive audit checks its contents against the source-controlled runtime policy, independently of the archive's own `package.json`.

| Boundary | Included | Excluded |
| --- | --- | --- |
| Consumer package | CLI, installer, linters, plugin metadata, SKILL.md, functional references, README, license | Plans, audits, historical benchmark reports, images, verification records, development tools |
| Automated review | Runtime inputs, tests, functional benchmark code/instructions and checkpoint policy, CI, release tools and selected operating docs | Saved model outputs, research summaries, historical synthesis prompts, plans, audit narratives and working drafts |
| Git tracking | Existing source and historical records | New generated campaigns/reviews and local work directories are ignored |

Functional Markdown prompts remain in scope. Package docs link to the repository instead of bundling historical evidence. Existing tracked records are retained. `.gitignore` alone neither removes tracked files nor enforces npm/context boundaries. Symlinked review inputs fail closed; unknown archive files fail the package audit. Add new functional inputs to the scope policy and its tests deliberately.

## Repeated outcome experiments

Use a source checkout. The consumer npm package does not include development evaluation tools. Start with a dry run:

```bash
python3 research/benchmark/v4/repeat_evaluations.py \
  --baseline-skill-dir make-prompt-better \
  --candidate-skill-dir make-prompt-better \
  --models example-executor --judge-model example-independent-judge \
  --seeds 42,43,44 --tests 1,2 \
  --max-requests 400 --deadline-seconds 900 \
  --max-output-tokens 4096 --output-dir quality-artifacts/pilot --dry-run
```

The example intentionally compares identical skill directories, useful for testing variance. Replace the baseline with a pinned prior checkout and the candidate with the proposed skill directory for an improvement experiment. Supply real model identifiers and `--host` for the configured Ollama-compatible endpoint, then remove `--dry-run` to make live requests. `OLLAMA_API_KEY`, when needed, is read from the environment, never from a command-line argument or saved manifest. No dollar price or provider revision is guessed.

The campaign uses independent judging, blind A/B labels, swapped answer positions, unprescribed mode selection and strict preservation. In strict mode, the runner executes the rewrite as emitted; it does not append facts omitted by the optimizer. Literal fact checks are limited diagnostics, not semantic verification. Existing direct runner callers keep the legacy default unless they opt into strict mode.

Each campaign binds the source bytes, suite, runner/judge code, models, endpoint hash, seed set and protocol. A changed input requires a new output directory. Completed cells are retained; interrupted or failed cells stay failed and retain their reserved request allowance. A rerun does not silently buy additional attempts for failed cells. Use a new explicitly budgeted campaign to retry, and preserve the old one. The overall deadline persists across resumptions. A lock prevents concurrent writers; remove a stale lock only after confirming no worker remains.

The 2-case, 3-seed, 2-variant example reserves at most 330 adapter attempts, including the configured retries and synthesis calls, within the 400 allowance. A subprocess deadline stops active work after the campaign's 900 seconds. Output tokens are capped per generation. These are request/time/output controls, not a billing guarantee: input tokens, provider accounting, caching and cancelled requests can still cost money. Use the provider's spending controls for a monetary ceiling.

Saved data distinguishes raw task baseline, optimizer, optimized execution, judge and synthesis. It includes per-attempt failures/retries and available input/output tokens. Missing counts remain null with known subtotals; word counts are not substituted for tokens. Product usage is optimizer plus execution; judging and synthesis are measurement overhead. Review the per-stage timing and token distribution, not only averages. Incomplete experiments remain visible in summaries.

Campaign summaries pair candidate and baseline skill scores by task, model and seed. They report missing pairs, preservation diagnostics, stage usage and a task-clustered bootstrap interval when at least five task clusters exist. Repeated seeds within one task do not become independent tasks. This threshold is a reporting heuristic, not a sample-size justification. The default weekly two-task campaign is descriptive only.

Before promoting a change, freeze the protocol, primary metric and minimum meaningful effect. Use a pilot to choose the required number of distinct tasks. Keep development examples separate from a larger sealed holdout, stratified by domain, complexity, language, model family, malformed input and adversarial instructions. Inspect failures and a blinded human-rated sample to calibrate the judge. Do not tune on the holdout or stop when a repeated significance check happens to pass. Compare success, preservation, safety, tokens and latency jointly; lower verbosity alone is not improvement. Failures and missing usage must be resolved or explicitly excluded from any promotion claim with justification.

## Routing experiment

```bash
python3 research/benchmark/v4/evaluate_routing.py \
  --model example-router --seeds 42,43,44 --split all \
  --max-requests 72 --max-seconds 600 \
  --output quality-artifacts/routing.json --dry-run
```

With a real model and no dry-run flag, this makes at most 72 single-attempt calls. It pairs variants by case/seed, counterbalances variant order, hashes the catalog/corpus and saves each observation. Invalid outputs are recorded and make the experiment incomplete. Metrics are exact selection accuracy, target recall, false-positive rate and invalid count; interpret all together. Test larger and growing catalogs, genuine competing skills, multiple models and actual host loading before generalizing. Direct `$make-prompt-better` invocation already selects the skill; routing changes chiefly concern automatic selection. End-to-end answer quality needs the separate outcome study.

## Recurring review and activation

| Workflow | Cadence and behavior |
| --- | --- |
| Existing recurring tests | Daily 04:23 UTC and deeper Sunday 05:43 UTC; also called by required validation |
| Continuous code review | PRs, main pushes, manual runs and Tuesday 06:17 UTC; CodeQL, shell/workflow syntax and scoped inventory |
| Optional model review | Same workflow on main only when enabled; one rotating 120,000-character context batch, one attempt, 4,096 output tokens, 120-second deadline |
| Optional prompt evaluation | Wednesday 07:41 UTC or manual on main; 2 tasks, 3 seeds, fixed v4.5.1 baseline, 400-attempt allowance and 900-second deadline |

Schedules become active only after these workflows reach the default branch. GitHub can delay or drop scheduled runs and disables schedules in inactive public repositories. This is recurring work, not a continuously resident process. Existing `validate` remains the required release gate; configure any additional required check only after its first successful hosted run. Branch protection could not be inspected through the connected integration, which returned HTTP 403.

Static review needs no model credentials. For live work, set repository variables `OLLAMA_HOST` and either `REVIEW_MODEL` or the distinct `EVAL_MODEL` and `EVAL_JUDGE`. Configure `OLLAMA_API_KEY` as an Actions secret only when the endpoint requires it. Then opt into `MODEL_REVIEW_ENABLED=true` and/or `PROMPT_EVAL_ENABLED=true` after selecting the provider's monetary budget. A local-only Ollama endpoint needs local execution or a separately secured runner; GitHub-hosted runners cannot reach your laptop's localhost. Both enable flags default off. Keep untrusted PR code away from these credentials; live workflows accept only main.

The model reviewer sends only selected functional source, never the complete repository. Truncation and omitted files are explicit, and the starting file rotates across runs. Its output must contain bounded findings with valid source paths/lines and verbatim evidence. Stable fingerprints deduplicate identical findings; CodeQL manages its own persistent alerts. Model findings are stored in artifacts, without repeated PR comments or automatic fixes. Prompt-injection text has no shell/file tools to invoke. These checks reduce risk but do not certify safety or semantic correctness.

Review reports are retained for 30 days, evaluation summaries for 90 days and curated raw runs for 14 days. Download reviewed summaries before expiry for longer-term trend analysis, retaining protocol hashes and failure counts. The scheduled corpus contains public fixture data; do not substitute confidential user prompts in public CI artifacts. All new local reports stay under ignored `quality-artifacts/` or benchmark run directories. Pause live spend by setting either enable variable to `false`; revert a candidate through a normal PR, preserving evidence from both versions.

## Verification

Run `npm run verify` plus the mandatory isolated installer verification in the agent contract. New scope, campaign, routing and review tests use offline fixtures; they are not live model results. CodeQL and GitHub schedule activation require hosted evidence. Full-bundle loading remains the outcome runner's current strategy; testing genuine host progressive disclosure and additional semantic preservation checks is future experimental work, not an efficiency result claimed by this change.
