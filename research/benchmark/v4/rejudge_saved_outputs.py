#!/usr/bin/env python3
"""Controlled Saved-Output Re-Judging & Ablation Harness for make-prompt-better (v4.3.0).

Directly addresses Audit Finding #3:
  "Rejudging the same saved responses under controlled label conditions would test that question."

Loads already-generated (`baseline`, `optimized_response`) text pairs from saved `metrics.json`
files and re-scores the EXACT SAME texts under controlled conditions using an independent judge:
  1. Labeling condition: `anonymous_ab` (Candidate A vs. Candidate B) vs. `labeled` (Baseline vs. Optimized)
  2. Presentation order: `pass1` (A=Baseline, B=Optimized) vs. `pass2` (A=Optimized, B=Baseline)
  3. Surface markers: `raw` (certificate tags preserved) vs. `stripped` (content-preserving tag removal)

Also supports offline `--dry-run` inspection to verify prompt construction and saved pair inventory
without making network calls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import unittest
from typing import Any

try:
    from research.benchmark.v4.blind_stats_engine import (
        build_blind_eval_instruction,
        compute_stratified_benchmark_summary,
        deterministic_ab_assignment,
        merge_position_swapped_scores,
        strip_certificate_scaffolding,
        unblind_parsed_scores,
    )
    from research.benchmark.v4.run_ollama_benchmarks import (
        REPO_ROOT,
        RESULTS_ROOT,
        TEST_CASES,
        DEFAULT_MAX_RETRIES,
        atomic_write,
        call_ollama_chat,
        parse_scores,
        validate_host,
    )
except ImportError:
    from blind_stats_engine import (
        build_blind_eval_instruction,
        compute_stratified_benchmark_summary,
        deterministic_ab_assignment,
        merge_position_swapped_scores,
        strip_certificate_scaffolding,
        unblind_parsed_scores,
    )
    from run_ollama_benchmarks import (
        REPO_ROOT,
        RESULTS_ROOT,
        TEST_CASES,
        DEFAULT_MAX_RETRIES,
        atomic_write,
        call_ollama_chat,
        parse_scores,
        validate_host,
    )

TEST_MAP = {tc["id"]: tc for tc in TEST_CASES}
LEGACY_RESULTS_ROOT = REPO_ROOT / "research" / "benchmark" / "v4" / "results"


def build_labeled_eval_instruction(
    tc: dict[str, Any],
    base_text: str,
    opt_text: str,
    strip_markers: bool = False,
) -> str:
    """Builds an explicitly labeled (Baseline vs. Optimized) judge prompt on the same saved texts."""
    clean_b = strip_certificate_scaffolding(base_text) if strip_markers else base_text
    clean_o = strip_certificate_scaffolding(opt_text) if strip_markers else opt_text
    words_b = len(clean_b.split())
    words_o = len(clean_o.split())

    return (
        "You are an independent, rigorous evaluator scoring two responses "
        "(Baseline vs. Optimized) to the ORIGINAL TASK below.\n"
        "Judge strictly on how accurately, completely, clearly, and actionably each response "
        "solves the ORIGINAL TASK, including preserving all requested deliverables and constraints.\n\n"
        f"ORIGINAL TASK ({tc['domain']} - {tc['task_type']}):\n{tc['raw_prompt']}\n\n"
        f"=== BASELINE RESPONSE ({words_b} words) ===\n{clean_b}\n\n"
        f"=== OPTIMIZED RESPONSE ({words_o} words) ===\n{clean_o}\n\n"
        "Score BOTH responses from 1 to 5 on each of the 5 dimensions using this exact Markdown table:\n\n"
        "| Dimension | Baseline (1-5) | Optimized (1-5) | Delta (O - B) | Evidence / Justification |\n"
        "| :--- | :---: | :---: | :---: | :--- |\n"
        "| Accuracy | X | Y | +/-Z | ... |\n"
        "| Completeness | X | Y | +/-Z | ... |\n"
        "| Structure | X | Y | +/-Z | ... |\n"
        "| Actionability | X | Y | +/-Z | ... |\n"
        "| Traceability | X | Y | +/-Z | ... |\n"
        "| **TOTAL (/25)** | **XX** | **YY** | **+/-ZZ** | **Winner: Baseline / Optimized / Tie** |\n"
    )


def load_saved_pairs(results_dir: Path, model_filter: list[str] | None = None, test_filter: list[int] | None = None) -> list[dict[str, Any]]:
    """Loads saved (baseline, optimized_response) text pairs from metrics.json files."""
    pairs: list[dict[str, Any]] = []
    if not results_dir.exists():
        return pairs

    for sub in sorted(results_dir.iterdir()):
        if not sub.is_dir():
            continue
        m_path = sub / "metrics.json"
        if not m_path.exists():
            continue
        data = json.loads(m_path.read_text(encoding="utf-8"))
        model_name = data.get("model", sub.name)
        if model_filter and model_name not in model_filter and sub.name not in model_filter:
            continue

        for tid_str, t in sorted(data.get("tests", {}).items(), key=lambda kv: int(kv[0])):
            tid = int(tid_str)
            if test_filter and tid not in test_filter:
                continue
            b_content = t.get("baseline", {}).get("content", "")
            o_content = t.get("optimized_response", {}).get("content", "")
            if not b_content or not o_content:
                continue
            tc = dict(TEST_MAP.get(tid, {"id": tid, "domain": f"Test {tid}",
                                         "task_type": "Accuracy", "raw_prompt": ""}))
            for field in ("domain", "task_type", "raw_prompt"):
                if field in t:
                    tc[field] = t[field]
            pairs.append({
                "model": model_name,
                "slug": sub.name,
                "test_id": tid,
                "tc": tc,
                "baseline_text": b_content,
                "optimized_text": o_content,
                "saved_parsed": t.get("evaluation", {}).get("parsed", {}),
                "prompt_source": "saved" if "raw_prompt" in t else "current suite fallback (unverified)",
            })
    return pairs


class RejudgeSavedOutputsTests(unittest.TestCase):
    def test_labeled_vs_anonymous_prompt_construction_on_identical_texts(self) -> None:
        tc = TEST_MAP[1]
        b_txt = "Baseline explanation of discount bug."
        o_txt = "### PREMISES\n[P1] Function signature.\n### EVIDENCE TRACES\n[T1] Trace discount_percent."
        anon_raw = build_blind_eval_instruction(tc, b_txt, o_txt, strip_markers=False)
        anon_stripped = build_blind_eval_instruction(tc, b_txt, o_txt, strip_markers=True)
        labeled_raw = build_labeled_eval_instruction(tc, b_txt, o_txt, strip_markers=False)

        self.assertIn("Candidate A (1-5)", anon_raw)
        self.assertNotIn("Baseline (1-5)", anon_raw)
        self.assertIn("[P1]", anon_raw)
        self.assertNotIn("[P1]", anon_stripped)
        self.assertIn("Baseline (1-5)", labeled_raw)
        self.assertIn("Optimized (1-5)", labeled_raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Re-judge identical saved baseline/optimized outputs under controlled label, order, and marker conditions."
    )
    parser.add_argument("--results-dir", type=str, default=str(LEGACY_RESULTS_ROOT), help="Directory containing model subdirs with metrics.json.")
    parser.add_argument("--models", type=str, default="", help="Comma-separated model names or slugs (default: all with metrics.json).")
    parser.add_argument("--tests", type=str, default="", help="Comma-separated test IDs (default: all saved).")
    parser.add_argument("--judge-model", type=str, default="glm-5.3:cloud", help="Independent judge model for re-scoring.")
    parser.add_argument("--host", type=str, default="http://localhost:11434", help="Ollama API host.")
    parser.add_argument("--strip-cert-markers", action="store_true", help="Strip [P1]/[T1] markers before judging.")
    parser.add_argument("--labeled", action="store_true", help="Use labeled (Baseline vs. Optimized) headers instead of anonymous Candidate A/B.")
    parser.add_argument("--swap-positions", action="store_true", help="Run 2-pass swapped order (A,B and B,A) in anonymous mode.")
    parser.add_argument("--dry-run", action="store_true", help="Verify saved pairs and prompt construction without calling Ollama API.")
    parser.add_argument("--self-test", action="store_true", help="Run unit tests and exit.")
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic A/B assignment.")
    parser.add_argument("--output", type=Path, help="New or matching rejudge checkpoint JSON; required for live requests.")
    parser.add_argument("--allow-remote-http", action="store_true", help="Explicitly permit unencrypted non-loopback HTTP.")
    parser.add_argument("--allow-missing-original-task", action="store_true", help="Use the current suite as an explicitly unverified fallback when saved task text is missing.")
    parser.add_argument("--max-requests", type=int, help="Reject a run whose worst-case request count exceeds this limit.")
    args = parser.parse_args(argv)

    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(RejudgeSavedOutputsTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if res.wasSuccessful() else 1

    try:
        validate_host(args.host, args.allow_remote_http)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.labeled and args.swap_positions:
        print("Error: --swap-positions requires anonymous judging", file=sys.stderr)
        return 1

    model_filter = [m.strip() for m in args.models.split(",") if m.strip()] or None
    try:
        test_filter = [int(x.strip()) for x in args.tests.split(",") if x.strip()] or None
    except ValueError:
        print("Error: --tests must contain comma-separated integers", file=sys.stderr)
        return 1
    pairs = load_saved_pairs(Path(args.results_dir), model_filter, test_filter)

    print(f"Loaded {len(pairs)} saved (baseline, optimized) response pairs from {args.results_dir}.")
    worst_requests = len(pairs) * (2 if args.swap_positions else 1) * DEFAULT_MAX_RETRIES
    print(f"Maximum HTTP requests with retries: {worst_requests}")
    if args.max_requests is not None and (args.max_requests < 0 or worst_requests > args.max_requests):
        print(f"Error: up to {worst_requests} HTTP requests exceed --max-requests", file=sys.stderr)
        return 1
    fallback_count = sum(item["prompt_source"] != "saved" for item in pairs)
    if fallback_count:
        print(f"Warning: {fallback_count} pairs lack a saved task prompt; current suite fallback is unverified.")
    if args.dry_run:
        if pairs:
            sample = pairs[0]
            prompt_preview = (
                build_labeled_eval_instruction(sample["tc"], sample["baseline_text"], sample["optimized_text"], args.strip_cert_markers)
                if args.labeled
                else build_blind_eval_instruction(sample["tc"], sample["baseline_text"], sample["optimized_text"], args.strip_cert_markers)
            )
            print(f"[DRY-RUN] Sample pair: model={sample['model']}, test={sample['test_id']}, prompt_chars={len(prompt_preview)}")
        return 0
    if not pairs:
        print("Error: no saved response pairs were found", file=sys.stderr)
        return 1
    if not args.output or args.output.name == "metrics.json":
        print("Error: provide a separate --output checkpoint before live rejudging", file=sys.stderr)
        return 1
    if fallback_count and not args.allow_missing_original_task:
        print("Error: saved task text is missing; use --allow-missing-original-task only if the fallback is acceptable", file=sys.stderr)
        return 1
    manifest = {
        "schema": 1,
        "input_sha256": hashlib.sha256(json.dumps(pairs, sort_keys=True).encode()).hexdigest(),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).with_name("run_ollama_benchmarks.py").read_bytes()).hexdigest(),
        "judge_code_sha256": hashlib.sha256(Path(__file__).with_name("blind_stats_engine.py").read_bytes()).hexdigest(),
        "judge_model": args.judge_model, "model_revision": "unknown",
        "host_sha256": hashlib.sha256(args.host.encode()).hexdigest(),
        "seed": args.seed, "labeled": args.labeled, "swap_positions": args.swap_positions,
        "strip_cert_markers": args.strip_cert_markers,
        "allow_missing_original_task": args.allow_missing_original_task,
    }
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = output.with_name(output.name + ".lock")
    try:
        lock.mkdir()
    except FileExistsError:
        print(f"Error: rejudge checkpoint is locked: {lock}", file=sys.stderr)
        return 1
    try:
        if output.exists():
            state = json.loads(output.read_text(encoding="utf-8"))
            if state.get("manifest") != manifest:
                print("Error: rejudge manifest mismatch; choose a new output", file=sys.stderr)
                return 1
        else:
            state = {"manifest": manifest, "pairs": {}}
            atomic_write(output, json.dumps(state, indent=2))

        rejudged_records: list[dict[str, Any]] = []
        for item in pairs:
            tc, model, tid = item["tc"], item["model"], item["test_id"]
            b_txt, o_txt = item["baseline_text"], item["optimized_text"]
            key = f"{model}:{tid}"
            saved = state["pairs"].setdefault(key, {"passes": []})

            def judge_pass(index: int, prompt: str, mapping: dict[str, str] | None) -> dict[str, Any]:
                if index < len(saved["passes"]):
                    result = saved["passes"][index]
                    if result["prompt"] != prompt or result["mapping"] != mapping:
                        raise ValueError(f"Saved judge request differs for {key}")
                    return result["response"]
                result = call_ollama_chat(model=args.judge_model, messages=[{"role": "user", "content": prompt}], host=args.host, seed=args.seed)
                saved["passes"].append({"prompt": prompt, "mapping": mapping, "response": result})
                atomic_write(output, json.dumps(state, indent=2))
                return result

            try:
                if args.labeled:
                    prompt = build_labeled_eval_instruction(tc, b_txt, o_txt, strip_markers=args.strip_cert_markers)
                    parsed = parse_scores(judge_pass(0, prompt, None)["content"])
                else:
                    mapping_p1 = deterministic_ab_assignment(args.seed, model, tid)
                    resp_a = b_txt if mapping_p1["A"] == "baseline" else o_txt
                    resp_b = o_txt if mapping_p1["B"] == "optimized" else b_txt
                    prompt_p1 = build_blind_eval_instruction(tc, resp_a, resp_b, strip_markers=args.strip_cert_markers)
                    parsed_p1 = unblind_parsed_scores(parse_scores(judge_pass(0, prompt_p1, mapping_p1)["content"]), mapping_p1)
                    if args.swap_positions:
                        mapping_p2 = {"A": mapping_p1["B"], "B": mapping_p1["A"]}
                        prompt_p2 = build_blind_eval_instruction(tc, resp_b, resp_a, strip_markers=args.strip_cert_markers)
                        parsed_p2 = unblind_parsed_scores(parse_scores(judge_pass(1, prompt_p2, mapping_p2)["content"]), mapping_p2)
                        parsed = merge_position_swapped_scores(parsed_p1, parsed_p2)
                    else:
                        parsed = parsed_p1
            except Exception as exc:
                print(f"Error: rejudging {key} failed; saved passes remain in {output}: {exc}", file=sys.stderr)
                return 1

            record = {"model": model, "test_id": tid, "judge_model": args.judge_model,
                      "baseline_total": parsed["baseline_total"], "optimized_total": parsed["optimized_total"],
                      "delta_total": parsed["delta_total"],
                      "position_swap_consistent": parsed.get("position_swap_consistent")}
            saved["record"] = record
            rejudged_records.append(record)
            atomic_write(output, json.dumps(state, indent=2))
            print(f"  [Rejudged] {model} T{tid:02d} (judge={args.judge_model}): B={parsed['baseline_total']} O={parsed['optimized_total']} D={parsed['delta_total']:+g}")

        summary = compute_stratified_benchmark_summary(rejudged_records, seed=args.seed)
        state["summary"] = summary
        atomic_write(output, json.dumps(state, indent=2))
        print("\n=== Re-Judged Summary ===")
        print(json.dumps(summary, indent=2))
        return 0
    finally:
        lock.rmdir()


if __name__ == "__main__":
    raise SystemExit(main())
