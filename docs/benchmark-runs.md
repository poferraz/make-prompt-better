# Benchmark runs and evidence

Existing files under `research/benchmark/v4/results/` are historical records. The runner now writes separate run directories under `research/benchmark/v4/runs/` and refuses to resume a legacy result lacking a matching manifest. It also refuses to overwrite a populated model directory with `--no-resume`.

Preview a bounded experiment without model requests or result writes:

```bash
python3 research/benchmark/v4/run_ollama_benchmarks.py \
  --models example-model --tests 1,2 --run-id example --dry-run
```

The output shows the run ID, location, number of logical generation stages, and an upper estimate of initial HTTP attempts including configured retries. `--max-requests` refuses a run whose estimate exceeds the specified count. Streaming responses are capped at 8 MiB per request and error bodies at 4 KiB. The request estimate is not a monetary, token, or wall-clock budget, and redirects may introduce additional transport requests. A real run sends prompt contents to the configured Ollama endpoint and stores the submitted prompts and model responses locally; do not include data you cannot send or store there.

To resume, pass the same `--run-id`, `--results-dir`, model, tests, host, seed, skill bytes, and other protocol flags. The manifest also hashes the test suite and runner/judge code. A mismatch produces an error and requires a new run ID. A model/provider identifier can refer to mutable weights, so its actual revision remains unknown unless recorded independently. A hard termination may leave a `.model-slug.lock` directory; remove it only after verifying that no process is using that model's run.

Completed baseline, optimization, execution, and judge stages are written atomically with their requests and responses. Both swapped judge passes and their assignments are retained. A malformed but successfully returned judge response is retained as evidence; there is currently no selective stage reset, so start a new run if that response cannot be parsed. Report generation is retried separately when incomplete.

Remote cleartext HTTP is refused unless `--allow-remote-http` is explicitly supplied. HTTPS and loopback HTTP are allowed. These checks do not validate provider privacy, model quality, redirects, or remote service security. The queue uses one run ID and returns a failure status for failed models; it does not automatically aggregate new runs or modify the historical aggregate.

For completed new-style runs, `python3 research/benchmark/v4/summarize_runs.py --results-dir <run-directory> --output <new-summary.json>` groups comparable manifests separately, rejects missing manifests and inconsistent judges, and reports descriptive saved scores. It never overwrites an existing summary. The historical aggregate script refuses to write inside the tracked historical results directory; copy those results to a disposable directory and pass that directory with `--results-dir` to regenerate the old format. That old format is not a provenance-aware summary of new runs.

The rejudge script accepts `--results-dir` for either historical model folders or one new run directory. Use `--dry-run` and, optionally, `--max-requests` to inspect and bound the estimated request count. A live rejudge requires a separate `--output` JSON file, which retains each judge prompt, response, position mapping, and manifest; repeat the same command to resume. A changed input or protocol requires a new output file. If the original task text was not saved, live rejudging refuses to substitute today's suite unless `--allow-missing-original-task` is explicitly passed; that fallback remains unverified.

No live-model efficacy, cost, availability, or safety claim follows from a dry run or fixture test. No new model evaluation was performed for v4.4.0.
