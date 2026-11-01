#!/usr/bin/env python3
"""
Aggregates all benchmark results across session-based evaluations (Antigravity, OpenAI Codex)
and isolated Ollama Cloud models in research/benchmark/v4/results/*/ into a unified dataset and Markdown matrix.

Methodological safeguards (v4.3.0):
- Separates session-based self-evaluations from isolated runner evaluations instead of pooling them without qualification.
- Records exact evaluation provenance (`protocol`, `judge_model`, `self_judged`, `completed_tests`).
- Never fabricates synthetic `100`-token placeholders when API `eval_count` telemetry is absent; uses `None` for missing token counts.
- Computes Model-Cluster and Two-Way Block Bootstrap 95% CIs alongside cell-level descriptive statistics.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    from research.benchmark.v4.blind_stats_engine import compute_stratified_benchmark_summary
except ImportError:
    from blind_stats_engine import compute_stratified_benchmark_summary

REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_ROOT = REPO_ROOT / "research" / "benchmark" / "v4" / "results"


def score_quality_issues(
    dimensions: dict[str, Any],
    baseline: float,
    optimized: float,
    text: str,
    blind_mapping: dict[str, str] | None = None,
) -> list[str]:
    issues = []
    for dimension, scores in dimensions.items():
        for label in ("baseline", "optimized"):
            value = scores.get(label)
            if value is not None and not 1 <= value <= 5:
                issues.append(f"{dimension} {label} score {value:g} is outside the 1-5 rubric")
    for label, total in (("baseline", baseline), ("optimized", optimized)):
        if not 5 <= total <= 25:
            issues.append(f"{label} total {total:g} is outside the 5-25 rubric")
    match = re.search(
        r"\|\s*\*{0,2}TOTAL(?:\s*\(/25\))?\*{0,2}\s*\|\s*\*{0,2}([0-9.]+)(?:/25)?\*{0,2}\s*\|\s*\*{0,2}([0-9.]+)(?:/25)?\*{0,2}\s*\|",
        text, re.IGNORECASE,
    )
    if match:
        swapped = bool(blind_mapping and blind_mapping.get("A") == "optimized")
        expected_col1 = ("optimized", optimized) if swapped else ("baseline", baseline)
        expected_col2 = ("baseline", baseline) if swapped else ("optimized", optimized)
        for (label, computed), written in ((expected_col1, float(match.group(1))),
                                           (expected_col2, float(match.group(2)))):
            if abs(written - computed) > 0.001:
                issues.append(f"written {label} total {written:g} differs from the saved total {computed:g}")
    rows = re.findall(
        r"\|\s*\*{0,2}(Accuracy|Completeness|Structure|Actionability|Traceability|TOTAL(?:\s*\(/25\))?)\*{0,2}"
        r"\s*\|\s*\*{0,2}([0-9.]+)(?:/25)?\*{0,2}\s*\|\s*\*{0,2}([0-9.]+)(?:/25)?\*{0,2}"
        r"\s*\|\s*\*{0,2}([+\-\u2013\u2212]?[0-9.]+)\*{0,2}\s*\|",
        text, re.IGNORECASE,
    )
    for dimension, b_score, o_score, delta in rows:
        written_delta = float(delta.replace("\u2013", "-").replace("\u2212", "-"))
        expected_delta = round(float(o_score) - float(b_score), 2)
        if abs(written_delta - expected_delta) > 0.001:
            issues.append(
                f"written {dimension.lower()} delta {written_delta:g} differs from "
                f"second-column minus first-column {expected_delta:g}"
            )
    return issues


def parse_markdown_eval_file(md_path: Path, slug: str) -> dict[str, Any]:
    text = md_path.read_text(encoding="utf-8")
    tests: dict[str, Any] = {}

    has_unblinded_note = "unblinded self-evaluation" in text.lower() or "in-session generation" in text.lower()
    protocol = "In-Session Unblinded Self-Eval" if has_unblinded_note else "In-Session Self-Eval (Markdown)"

    # Parse per-test evaluation tables if present
    pattern = re.compile(
        r"###\s+EVALUATION:\s*TEST\s*(\d+)(.*?)(?=\n##\s+TEST|\n##\s+FINAL REPORT|\n##\s+Final Synthesis|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    dims = ["Accuracy", "Completeness", "Structure", "Actionability", "Traceability"]
    for m in pattern.finditer(text):
        tid = m.group(1)
        block = m.group(2)
        dim_scores: dict[str, dict[str, float]] = {}
        for d in dims:
            dm = re.search(rf"\|\s*\*?\*?{d}\*?\*?\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|", block, re.IGNORECASE)
            if dm:
                b = float(dm.group(1))
                o = float(dm.group(2))
                dim_scores[d.lower()] = {"baseline": b, "optimized": o, "delta": round(o - b, 2)}
        if len(dim_scores) == 5:
            b_tot = sum(v["baseline"] for v in dim_scores.values())
            o_tot = sum(v["optimized"] for v in dim_scores.values())
        else:
            tm = re.search(r"\|\s*\*?\*?TOTAL(?:\s*\(/25\))?\*?\*?\s*\|\s*([0-9.]+)(?:/25)?\s*\|\s*([0-9.]+)(?:/25)?\s*\|", block, re.IGNORECASE)
            if not tm:
                continue
            b_tot = float(tm.group(1))
            o_tot = float(tm.group(2))
        delta_tot = round(o_tot - b_tot, 2)
        rm = re.search(r"Ratio[:\s]*`?([0-9.]+)x?`?", block, re.IGNORECASE)
        ratio = float(rm.group(1)) if rm else None
        tests[tid] = {
            "id": int(tid),
            "baseline_total": b_tot,
            "optimized_total": o_tot,
            "delta_total": delta_tot,
            "dimensions": dim_scores,
            "word_overhead_ratio": ratio,
            "baseline_tokens": None,
            "optimized_tokens": None,
            "winner": "Optimized" if delta_tot > 0 else ("Baseline" if delta_tot < 0 else "Tie"),
            "score_issues": score_quality_issues(dim_scores, b_tot, o_tot, block),
        }

    completed = list(tests.values())
    if completed:
        avg_b = round(sum(t["baseline_total"] for t in completed) / len(completed), 2)
        avg_o = round(sum(t["optimized_total"] for t in completed) / len(completed), 2)
        avg_d = round(sum(t["optimized_total"] - t["baseline_total"] for t in completed) / len(completed), 2)
        ratios = [t["word_overhead_ratio"] for t in completed if t["word_overhead_ratio"] is not None]
        avg_ratio = round(sum(ratios) / len(ratios), 2) if ratios else None
        wins = sum(1 for t in completed if t["winner"] == "Optimized")
        ties = sum(1 for t in completed if t["winner"] == "Tie")
        losses = sum(1 for t in completed if t["winner"] == "Baseline")
    else:
        avg_b = avg_o = avg_d = 0.0
        avg_ratio = None
        wins = ties = losses = 0

    return {
        "model": slug,
        "slug": slug,
        "protocol": protocol,
        "judge_model": slug,
        "self_judged": True,
        "completed_tests": len(completed),
        "avg_baseline": avg_b,
        "avg_optimized": avg_o,
        "avg_delta": avg_d,
        "avg_word_overhead_ratio": avg_ratio,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "tests": tests,
    }


def collect_all_models() -> list[dict[str, Any]]:
    if not RESULTS_ROOT.exists():
        return []
    records: list[dict[str, Any]] = []
    for sub in sorted(RESULTS_ROOT.iterdir()):
        if not sub.is_dir():
            continue
        metrics_file = sub / "metrics.json"
        md_file = sub / "EVALUATION_RESULTS.md"
        if metrics_file.exists():
            data = json.loads(metrics_file.read_text(encoding="utf-8"))
            summary = data.get("summary", {})
            model_name = data.get("model", sub.name)
            judge_model = data.get("judge_model") or summary.get("judge_model") or model_name
            self_judged = bool(data.get("self_judged", judge_model == model_name))
            per_test: dict[str, Any] = {}
            any_blind = False
            any_swapped = False
            for tid, t in data.get("tests", {}).items():
                p = t.get("evaluation", {}).get("parsed", {})
                if "blind_mapping" in p or "pass1" in p:
                    any_blind = True
                if p.get("position_swap_consistent") is not None:
                    any_swapped = True
                b_eval = t.get("baseline", {}).get("eval_count")
                o_eval = t.get("optimized_response", {}).get("eval_count")
                b_tok = int(b_eval) if b_eval and int(b_eval) > 0 else None
                o_tok = int(o_eval) if o_eval and int(o_eval) > 0 else None
                per_test[tid] = {
                    "id": int(tid),
                    "baseline_total": p.get("baseline_total", 0.0),
                    "optimized_total": p.get("optimized_total", 0.0),
                    "delta_total": p.get("delta_total", 0.0),
                    "dimensions": p.get("dimensions", {}),
                    "word_overhead_ratio": t.get("word_overhead_ratio"),
                    "baseline_tokens": b_tok,
                    "optimized_tokens": o_tok,
                    "compiler_tokens": t.get("optimized_prompt", {}).get("eval_count") or None,
                    "position_swap_consistent": p.get("position_swap_consistent"),
                    "winner": p.get("winner", "Tie"),
                    "score_issues": score_quality_issues(
                        p.get("dimensions", {}), p.get("baseline_total", 0.0),
                        p.get("optimized_total", 0.0), t.get("evaluation", {}).get("content", ""),
                        p.get("blind_mapping"),
                    ),
                }
            if per_test:
                c_list = list(per_test.values())
                avg_b = round(sum(t["baseline_total"] for t in c_list) / len(c_list), 2)
                avg_o = round(sum(t["optimized_total"] for t in c_list) / len(c_list), 2)
                avg_d = round(sum(t["optimized_total"] - t["baseline_total"] for t in c_list) / len(c_list), 2)
                ratios = [t["word_overhead_ratio"] for t in c_list if t["word_overhead_ratio"] is not None]
                avg_ratio = round(sum(ratios) / len(ratios), 2) if ratios else None
                wins = sum(1 for t in c_list if t["winner"] == "Optimized")
                ties = sum(1 for t in c_list if t["winner"] == "Tie")
                losses = sum(1 for t in c_list if t["winner"] == "Baseline")
                summary = {
                    "completed_tests": len(c_list),
                    "avg_baseline": avg_b,
                    "avg_optimized": avg_o,
                    "avg_delta": avg_d,
                    "avg_word_overhead_ratio": avg_ratio,
                    "wins": wins,
                    "ties": ties,
                    "losses": losses,
                }
            else:
                continue

            if not self_judged and any_swapped:
                protocol = "Isolated Independent-Judge 2-Pass Swapped"
            elif not self_judged and any_blind:
                protocol = "Isolated Independent-Judge Anonymized"
            elif any_blind:
                protocol = "Isolated Anonymized Self-Judged"
            else:
                protocol = "Isolated Unblinded Self-Judged"

            records.append({
                "model": model_name,
                "slug": sub.name,
                "protocol": protocol,
                "judge_model": judge_model,
                "self_judged": self_judged,
                "completed_tests": summary.get("completed_tests", len(per_test)),
                "avg_baseline": summary.get("avg_baseline", 0.0),
                "avg_optimized": summary.get("avg_optimized", 0.0),
                "avg_delta": summary.get("avg_delta", 0.0),
                "avg_word_overhead_ratio": summary.get("avg_word_overhead_ratio"),
                "wins": summary.get("wins", 0),
                "ties": summary.get("ties", 0),
                "losses": summary.get("losses", 0),
                "tests": per_test,
            })
        elif md_file.exists():
            parsed_md = parse_markdown_eval_file(md_file, sub.name)
            if parsed_md["completed_tests"] > 0:
                records.append(parsed_md)
    return records


def build_pair_records(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for r in models:
        for t in r["tests"].values():
            p_dict: dict[str, Any] = {
                "model": r["model"],
                "test_id": t["id"],
                "baseline_total": t["baseline_total"],
                "optimized_total": t["optimized_total"],
                "baseline_tokens": t.get("baseline_tokens"),
                "optimized_tokens": t.get("optimized_tokens"),
            }
            if t.get("position_swap_consistent") is not None:
                p_dict["position_swap_consistent"] = t["position_swap_consistent"]
            pairs.append(p_dict)
    return pairs


def main() -> int:
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    records = collect_all_models()
    out_json = RESULTS_ROOT / "AGGREGATED_METRICS.json"
    out_md = RESULTS_ROOT / "AGGREGATED_METRICS.md"

    session_models = [r for r in records if r["protocol"].startswith("In-Session")]
    isolated_models = [r for r in records if not r["protocol"].startswith("In-Session")]

    all_pairs = build_pair_records(records)
    session_pairs = build_pair_records(session_models)
    isolated_pairs = build_pair_records(isolated_models)

    stratified_summary = compute_stratified_benchmark_summary(all_pairs)
    session_summary = compute_stratified_benchmark_summary(session_pairs) if session_pairs else {}
    isolated_summary = compute_stratified_benchmark_summary(isolated_pairs) if isolated_pairs else {}

    out_json.write_text(
        json.dumps(
            {
                "models": records,
                "stratified_summary": stratified_summary,
                "by_protocol_stratum": {
                    "in_session_self_eval": session_summary,
                    "isolated_runner": isolated_summary,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# Aggregated Cross-Architecture Benchmark Data (v4.3.0 Audited Provenance)",
        "",
        "Methodological Disclosures: All runs in this directory are self-evaluated (`judge_model == generator_model`) unless otherwise noted in the `Judge` column. In-session runs (`argon-4-low`, `gemini-3.8`, `gpt-6-astra-max`) were generated and scored in session contexts (`gpt-6-astra-max` explicitly notes unblinded in-session self-scoring across 11 of 12 cases) and should not be pooled with isolated API runner calls as a single controlled experiment. Isolated Ollama Cloud runs isolate each generation call and randomize candidate order (`Candidate A` vs. `Candidate B`), though historical Oct 31 runs retained `Baseline`/`Optimized` column labels in the judge prompt and visible certificate tags. Partial runs (`gpt-oss:20b-cloud` 9/12, `kimi-k3:cloud` 11/12) cover subsets of the 12-task suite. Word Overhead is an output word-count ratio, not an end-to-end token-cost ratio (prompt compilation tokens and missing API token counts are excluded rather than synthesized).",
        "",
        "## 1. Overall Model Leaderboard (Stratified by Protocol Provenance)",
        "",
        "| Model | Protocol | Judge | Completed Tests | Baseline Avg (/25) | Optimized Avg (/25) | Delta (/25) | Gain (%) | Avg Word Overhead | Win-Tie-Loss |",
        "|-------|----------|-------|-----------------|--------------------|---------------------|-------------|----------|-------------------|--------------|",
    ]
    for r in records:
        tests = list(r["tests"].values())
        baseline_sum = sum(t["baseline_total"] for t in tests)
        delta_sum = sum(t["optimized_total"] - t["baseline_total"] for t in tests)
        if not tests:
            baseline_sum = r["avg_baseline"]
            delta_sum = r["avg_delta"]
        pct = round(delta_sum / baseline_sum * 100, 1) if baseline_sum > 0 else 0.0
        overhead = r["avg_word_overhead_ratio"]
        overhead_text = f"{overhead}x" if overhead is not None else "N/A"
        judge_label = "Self" if r.get("self_judged", True) else f"`{r.get('judge_model')}`"
        lines.append(
            f"| `{r['model']}` | {r['protocol']} | {judge_label} | {r['completed_tests']}/12 | {r['avg_baseline']} | {r['avg_optimized']} | "
            f"{r['avg_delta']:+g} | {pct:+g}% | {overhead_text} | "
            f"{r['wins']}W-{r['ties']}T-{r['losses']}L |"
        )

    lines.extend([
        "",
        "## 2. Per-Test Score Delta Matrix (Optimized minus Baseline, /25)",
        "",
        "| Model | T1 Code | T2 Fin | T3 Med | T4 Legal | T5 Res | T6 Biz | T7 NIST | T8 Doc | T9 Lite | T10 Creative | T11 Context | T12 LRM |",
        "|-------|---------|--------|--------|----------|--------|--------|---------|--------|---------|--------------|-------------|---------|",
    ])
    for r in records:
        cells = [f"`{r['model']}`"]
        for tid in range(1, 13):
            t = r["tests"].get(str(tid))
            if t:
                cells.append(f"{t['delta_total']:+g} ({t['optimized_total']})")
            else:
                cells.append("-")
        lines.append("| " + " | ".join(cells) + " |")

    flags = [
        f"- `{r['model']}`, Test {tid}: {issue}."
        for r in records for tid, test in r["tests"].items()
        for issue in test.get("score_issues", [])
    ]
    lines.extend([
        "",
        "## 3. Score Quality Flags",
        "",
        "The leaderboard retains the saved per-dimension scores and deterministically recomputes totals and deltas (`optimized minus baseline`). Flagged entries below indicate where a model's written delta or total column in raw markdown disagreed with its per-dimension scores.",
        "",
        *(flags or ["- No score-range or total inconsistencies were found in parsed evaluations."]),
        "",
        "## 4. Protocol-Stratified & Cluster-Robust Statistical Summary",
        "",
        "Because the benchmark crosses $M$ models with $T = 12$ fixed tasks (1 case per domain), cell-level i.i.d. resampling understates uncertainty. We report **Model-Cluster Bootstrap 95% CIs**, **Two-Way Block Bootstrap 95% CIs (resampling models and tasks)**, and **Cluster-Level Sign-Flip Permutation p-values** separately for each protocol stratum:",
        "",
        "| Stratum | Pairs (Models x Tasks) | Baseline Mean | Optimized Mean | Mean Delta | Cell Bootstrap 95% CI | Model-Cluster 95% CI | Two-Way Block 95% CI | Model Sign-Flip p | Task Sign-Flip p | Win-Tie-Loss (Win %) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])
    for label, summ in [
        ("In-Session Self-Eval Track", session_summary),
        ("Isolated Runner Track (Ollama Cloud)", isolated_summary),
        ("Combined Descriptive Pool (All 14)", stratified_summary),
    ]:
        if not summ or not summ.get("total_pairs"):
            continue
        rec = summ.get("record", {})
        c_ci = summ.get("delta_95_ci", [0, 0])
        m_ci = summ.get("model_cluster_95_ci", [0, 0])
        tw_ci = summ.get("two_way_block_95_ci", [0, 0])
        lines.append(
            f"| **{label}** | {summ['total_pairs']} ({summ.get('n_models', 0)}M, {summ.get('n_tasks', 0)}T) | "
            f"{summ['baseline_mean']}/25 | {summ['optimized_mean']}/25 | **{summ['mean_delta']:+g}** | "
            f"`[{c_ci[0]:+g}, {c_ci[1]:+g}]` | `[{m_ci[0]:+g}, {m_ci[1]:+g}]` | `[{tw_ci[0]:+g}, {tw_ci[1]:+g}]` | "
            f"`{summ.get('model_cluster_sign_flip_p_value', 1.0):.4f}` | `{summ.get('task_cluster_sign_flip_p_value', 1.0):.4f}` | "
            f"{rec.get('wins', 0)}W-{rec.get('ties', 0)}T-{rec.get('losses', 0)}L ({summ['win_rate_pct']}%) |"
        )

    tok_pairs = stratified_summary.get("measured_token_pairs", 0)
    tok_ratio = stratified_summary.get("mean_token_overhead_ratio")
    tok_lift = stratified_summary.get("mean_lift_per_1k_extra_tokens")
    lines.extend([
        "",
        f"- **Measured API Output Token Telemetry (`eval_count` > 0)**: Available on `{tok_pairs}/{stratified_summary.get('total_pairs', 0)}` pairs (Mean Output Token Ratio: `{f'{tok_ratio}x' if tok_ratio is not None else 'N/A'}`, Mean Lift per 1k Extra Output Tokens: `{f'{tok_lift:+g}' if tok_lift is not None else 'N/A'}`). In-session Markdown runs without API token telemetry are excluded rather than assigned synthetic placeholders.",
        "",
        "### Parameter-Tier Stratification (Descriptive Pool)",
        "",
        "| Parameter Tier | Pairs | Mean Delta (/25) | Cell 95% Bootstrap CI | Win Rate (%) |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])
    for tier, data in stratified_summary.get("by_tier", {}).items():
        ci_str = f"[{data['ci_95'][0]:+g}, {data['ci_95'][1]:+g}]"
        lines.append(f"| {tier} | {data['pairs']} | {data['mean_delta']:+g} | {ci_str} | {data['win_rate_pct']}% |")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Aggregated {len(records)} model(s) -> {out_md.relative_to(REPO_ROOT)} and {out_json.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
