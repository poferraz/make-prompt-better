# Five-arm downstream evaluation

This source-checkout tool compares downstream answers for the same task, executor model and seed:

1. The original request, without optimization.
2. A minimal clarity rewrite supplied by the corpus.
3. A strong direct prompt independently authored from the task, without the evaluated skill.
4. The stable skill's preparation decision and downstream answer.
5. A future candidate skill's preparation decision and downstream answer.

It is a new protocol beside `repeat_evaluations.py`, not a replacement for historical campaigns. Existing campaign manifests and migration hashes are not rewritten. No installed skill or consumer dependency changes. Evaluation code and fixtures remain outside the npm archive.

## Run an offline proof

```bash
python3 -m unittest discover -s research/benchmark/v4 -p 'test_downstream_*.py' -v
npm run verify
```

The integration test extends the existing loopback mocked Ollama service. It starts the real campaign and worker subprocesses, streams two-frame responses through the existing HTTP adapter, produces all five arms and twenty judge passes, checks the summary, and resumes with zero extra requests. Separate loopback tests exercise quota errors, incomplete usage and crash recovery. No provider credentials, model installation, private corpus or paid requests are needed. The HTTP proof takes about 42 seconds because it retains the adapter's normal pacing. An isolated npm cache can be set with `npm_config_cache="$PWD/.private/npm-cache"` when the default cache is not writable.

## Inspect a plan without calling models

```bash
python3 research/benchmark/v4/downstream_evaluation.py \
  --models example-executor --judge-model example-independent-judge \
  --candidate-skill-dir make-prompt-better \
  --seeds 42,43 --tasks net-apples,leap-day,untrusted-records \
  --max-requests 162 --deadline-seconds 900 \
  --max-output-tokens 1024 --max-input-chars 120000 \
  --output-dir .private/quality-artifacts/downstream-pilot
```

Planning is the default and writes no files. The default stable directory is `make-prompt-better`; specify `--stable-skill-dir` to use another pinned checkout. Pointing both directories at the unchanged skill is an A/A calibration, not a candidate improvement. Candidate and stable bundle/source hashes are recorded independently.

For an explicitly approved live pilot, replace the placeholders with actual catalog or local model identifiers, select `--host`, and add `--run`. This guide does not grant approval to spend money. `OLLAMA_API_KEY` is read only from the environment and is not stored. All output paths must be under `.private/`. No workflow or schedule invokes this tool automatically.

For direct Cloud, an operator may save the public `https://ollama.com/api/tags` response in `.private/` and pass it with `--catalog-snapshot`. The manifest then binds the snapshot hash and advertised digests for each selected identifier, rejecting a judge with the same advertised digest as an executor. This snapshot is operator-supplied evidence, not a guarantee that the provider will serve an immutable revision or that differently reported digests imply independent model weights.

Each complete task/model/seed cell has at most 27 logical calls: two preparation calls, five answer executions, and two position-swapped passes for each of ten arm pairs. The example contains six cells and reserves 162 attempts with the default one attempt per call. `--max-attempts` includes retries and increases the required reservation accordingly. The request count, per-call output tokens, input characters, request timeout and persistent campaign deadline are bounded. HTTP 401, 402, 403 or 429, missing provider token counts, a sensitive response, or an evidence write failure stops the campaign without retrying the affected request. A resumed campaign honors the recorded stop even if the coordinator crashed before updating its state. This is not a dollar or aggregate input-token cap: provider token-limit semantics, failed or cancelled requests and account billing remain outside these guarantees. Configure and verify provider spending controls before live use. A quota reset never extends the original campaign deadline.

## What is measured

The public development corpus has nine small tasks, balanced across unclear, ordinary and already strong prompts, with English, Spanish and German inputs, checkable answers, explicit constraints and adversarial quoted instructions. Direct prompts are assistant-authored independently of the evaluated skill, not verified human-written baselines. Their strength and minimality require independent review before substantive claims.

Stable and candidate preparations use the same full-bundle loading strategy and a JSON wrapper that requires either `rewrite` with a self-contained prompt or `bypass`. Bypass executes the original request exactly. A rewrite that happens to be identical is reported separately from a declared bypass. Bypass still consumes the preparation call; it is not a zero-cost routing decision. No omitted facts are silently appended. Preparation failures stay failures, with no automatic fallback presented as success.

The executions use a fresh one-message context for each arm, with the same model and seed. Arm order rotates and reverses across cells; each arm appears in each position twice per ten-cell block. Small incomplete blocks cannot be perfectly balanced. Judges use a distinct explicit model identifier, receive only the original task and anonymous answer texts, and see both answer positions. They never see the rewrite, arm identity, skill, reference answer or objective-check result. Known `:latest` and default-library aliases are rejected, but other distinct identifiers cannot prove distinct underlying models or eliminate judge bias. Before a run, check the provider catalog and independently verify model identities where possible. Quoted output is separated as untrusted JSON data, but prompt-injection resistance is not guaranteed by formatting.

The original v4 five-dimension rubric and score mapping are reused. All five rows must parse; invalid judge responses and their available usage remain recorded. Paired deltas favor the second arm. Summaries include raw task/model/seed pairs, position consistency, missing comparisons, expected and available answers, preparation/execution failures, paired objective checks, preservation diagnostics and bypass decisions with denominators. At least five distinct tasks are required before reporting a task-cluster bootstrap interval. Intervals are descriptive and unadjusted for ten comparisons; they are not promotion gates or proof of efficacy.

Objective checks compare text or JSON, never execute generated code. JSON numeric representations compare by value while booleans stay distinct. Exact text checks can retain whitespace because the adapter now preserves raw text alongside its legacy normalized content. Literal preservation checks flag selected constraints but may reject paraphrases and miss semantic changes. The conservative legacy number/code-anchor audit is reported separately. A check failure is a measured outcome, not a transport error, and does not discard the answer or its judgment.

Usage is reported by preparation, execution and judge stage, with preparation/execution also grouped by arm. Judging is measurement overhead. Static direct-prompt authoring has no measured model calls in this run; human/author effort is not priced. Available failed-attempt usage counts toward known totals. Missing fields and interrupted telemetry remain unknown (`null`), accompanied by known subtotals. Word counts are never substituted for tokens, and no dollar cost or provider revision is invented.

## Durable evidence and holdout separation

The v2 manifest binds exact corpus content, selected task data, source hashes, full skill bundles, models, seeds, endpoint hash and bounds. Changing any bound or source requires a new output directory; v1 manifests cannot be resumed as v2. Each cell reserves its maximum attempts before launch and saves the exact JSON request body and its hash before dispatch. Authorization headers are never written. The configured API key is checked against request and response text, but this cannot detect unrelated secrets; treat every prompt and response as sensitive. Campaign and cell directories are owner-only, and cell records use owner-only files. Failed and interrupted cells are not relaunched on resume. The original deadline persists. The coordinator kills and waits for an active worker at deadline, and the worker also enforces that deadline if the coordinator disappears; an interrupted response can leave usage unknown. A one-use coordinator reservation and exclusive cell creation prevent accidental duplicate workers, not hostile processes running as the same operating-system user. Preserve failed records and use a separately approved, newly budgeted directory for retries. A lock rejects concurrent writers. Remove a stale lock only after confirming no worker remains. Raw private records must not be uploaded as public-repository Actions artifacts.

An interrupted worker or unexplained worker exit stops subsequent cells when usage is unknown. Evidence is written atomically with file synchronization, but durability across host failure or power loss has not been established.

Standard checks load only the tracked development corpus and work without `.private/`. A holdout uses the same schema with `split: "holdout"`, lives under a separate ignored `.private/` directory, and requires `--corpus` plus its exact `--holdout-sha256` before even planning it. A hash detects changed content; it does not enforce secrecy, independent authorship or access control. Have an independent custodian freeze and keep the confirmatory set away from development and tuning. Any locally prepared provisional set is not confirmatory evidence until independently reviewed and resealed.

Remaining limits include a small synthetic corpus, uncalibrated judge preferences, provider seed/model mutability, full-bundle overhead, literal-only preservation checks, and no measured live-model efficacy. Keep the primary comparison, minimum meaningful effect, sample size, safety review and monetary cap fixed before a future pilot. Never execute model-produced code on the host; code-based checks require a separately designed isolated sandbox.

Rollback: remove the new tool, public corpus/check helpers and their tests/docs, and revert the additive adapter raw-text field if no longer needed. Existing v4 campaigns and consumer skill files remain usable. Preserve private evidence separately; do not rewrite old manifests to make a new source version appear identical.
