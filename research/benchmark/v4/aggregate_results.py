#!/usr/bin/env python3
"""
Aggregates all v4.0 benchmark results across Antigravity (Gemini 3.8), OpenAI Codex (GPT 6.1 Terra),
and Ollama Cloud models in research/benchmark/v4/results/*/ into a unified dataset and Markdown matrix.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_ROOT = REPO_ROOT / "research" / "benchmark" / "v4" / "results"


def score_quality_issues(dimensions: dict[str, Any], baseline: float, optimized: float, text: str) -> list[str]:
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
        r"\|\s*\*{0,2}TOTAL\*{0,2}\s*\|\s*\*{0,2}([0-9.]+)(?:/25)?\*{0,2}\s*\|\s*\*{0,2}([0-9.]+)(?:/25)?\*{0,2}\s*\|",
        text, re.IGNORECASE,
    )
    if match:
        for label, written, computed in (("baseline", float(match.group(1)), baseline),
                                         ("optimized", float(match.group(2)), optimized)):
            if abs(written - computed) > 0.001:
                issues.append(f"written {label} total {written:g} differs from the saved total {computed:g}")
    rows = re.findall(
        r"\|\s*\*{0,2}(Accuracy|Completeness|Structure|Actionability|Traceability|TOTAL)\*{0,2}"
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
                f"optimized minus baseline {expected_delta:g}"
            )
    return issues


def parse_markdown_eval_file(md_path: Path, slug: str) -> dict[str, Any]:
    text = md_path.read_text(encoding="utf-8")
    tests: dict[str, Any] = {}

    # Parse per-test evaluation tables if present
    pattern = re.compile(
        r"###\s+EVALUATION:\s*TEST\s*(\d+)(.*?)(?=\n##\s+TEST|\n##\s+FINAL REPORT|\Z)",
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
            tm = re.search(r"\|\s*\*?\*?TOTAL\*?\*?\s*\|\s*([0-9.]+)(?:/25)?\s*\|\s*([0-9.]+)(?:/25)?\s*\|", block, re.IGNORECASE)
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
            per_test: dict[str, Any] = {}
            for tid, t in data.get("tests", {}).items():
                p = t.get("evaluation", {}).get("parsed", {})
                per_test[tid] = {
                    "id": int(tid),
                    "baseline_total": p.get("baseline_total", 0.0),
                    "optimized_total": p.get("optimized_total", 0.0),
                    "delta_total": p.get("delta_total", 0.0),
                    "dimensions": p.get("dimensions", {}),
                    "word_overhead_ratio": t.get("word_overhead_ratio"),
                    "winner": p.get("winner", "Tie"),
                    "score_issues": score_quality_issues(
                        p.get("dimensions", {}), p.get("baseline_total", 0.0),
                        p.get("optimized_total", 0.0), t.get("evaluation", {}).get("content", ""),
                    ),
                }
            # A resumed run saves each test before updating its final summary.
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
            records.append({
                "model": data.get("model", sub.name),
                "slug": sub.name,
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
            records.append(parse_markdown_eval_file(md_file, sub.name))
    return records


def main() -> int:
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    records = collect_all_models()
    out_json = RESULTS_ROOT / "AGGREGATED_METRICS.json"
    out_md = RESULTS_ROOT / "AGGREGATED_METRICS.md"

    out_json.write_text(json.dumps({"models": records}, indent=2), encoding="utf-8")

    lines = [
        "# Aggregated v4.0 Cross-Architecture Benchmark Data",
        "",
        "Scores are self-evaluations by the models that generated the responses, and evaluators see which response is optimized. The Ollama runner isolates its generation calls, while the session protocol uses a single conversation. Older Ollama records may not contain the exact prompt sent after input guardrails. Partial runs may cover different tests, so their averages are not directly comparable. Averages below come from per-test records; mean paired deltas are rounded independently, and model-written narratives may contain conflicting arithmetic. Overhead is an output word-count ratio, not a token-cost ratio; missing ratios are excluded from its average.",
        "",
        "## 1. Overall Model Leaderboard",
        "",
        "| Model | Completed Tests | Baseline Avg (/25) | Optimized Avg (/25) | Delta (/25) | Gain (%) | Avg Word Overhead | Win-Tie-Loss |",
        "|-------|-----------------|--------------------|---------------------|-------------|----------|--------------|--------------|",
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
        lines.append(
            f"| `{r['model']}` | {r['completed_tests']}/12 | {r['avg_baseline']} | {r['avg_optimized']} | "
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
        "The leaderboard retains the saved scores, including any flagged entries.",
        "",
        *(flags or ["- No score-range or total inconsistencies were found in parsed evaluations."]),
    ])

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Aggregated {len(records)} model(s) -> {out_md.relative_to(REPO_ROOT)} and {out_json.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
