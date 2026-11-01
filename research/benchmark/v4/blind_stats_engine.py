#!/usr/bin/env python3
"""Zero-dependency Blinded A/B Judge & Cluster-Robust Non-Parametric Statistical Engine for make-prompt-better.

Addresses five core benchmark validity requirements in research/benchmark/v4/:
1. Eliminates self-preference bias by decoupling --judge-model from candidate models and tracking self_judged provenance.
2. Eliminates rubric and label leakage: uses strictly anonymized 'Candidate A (1-5)' and 'Candidate B (1-5)' table headers
   with 'Delta (B - A)' and 'Winner: Candidate A / Candidate B / Tie' (zero 'Baseline' or 'Optimized' labels in the judge prompt),
   and supports stripping [P1]/[T1]/[V1]/[C1] certificate bracket tags before evaluation.
3. Cancels position/recency bias via deterministic A/B randomization and 2-pass position swapping,
   computing position-consistency rates across evaluation pairs.
4. Accounts for repeated-measures structure (M models x T tasks) by computing Model-Cluster Bootstrap 95% CIs,
   Two-Way Block Bootstrap (resampling models and tasks independently) 95% CIs, and Task-Clustered / Model-Clustered
   Paired Sign-Flip permutation p-values alongside cell-level descriptive statistics.
5. Separates measured API token counts from word-count ratios without fabricating synthetic token placeholders.
"""

from __future__ import annotations

import hashlib
import math
import random
import re
import statistics
import unittest
from typing import Any

CERT_TAG_PATTERN = re.compile(
    r"\[(?:P\d+|T\d+|V\d+|C\d+|D\d+|R\d+|L\d+|F\d+|S\d+|E\d+|O\d+|NT\d+|SC\d+|I\d+|"
    r"LITE|REASONING-CERT|CONTEXT-CERT|HARNESS-CERT|DIVERSITY-CERT|"
    r"META|GOAL-BLIND|ACE|HIERARCHY|CODE-SMELLS|PRISM|VS|SLOPSHAPE|CONTEXT-FILES|HARNESS|SKILLS-SDO)\]\s*"
)

LRM_AND_FRONTIER_TOKENS: tuple[str, ...] = (
    "deepseek-r1",
    "-r1",
    ":r1",
    "o1",
    "o3",
    "qwq",
    "gemini",
    "argon",
    "claude",
    "gpt-4",
    "gpt-5",
    "gpt-6",
    "kimi",
)

SUB_14B_TOKENS: tuple[str, ...] = (
    "1.5b",
    "3b",
    "4b",
    "7b",
    "8b",
    "9b",
    "12b",
    "flash",
    "mini",
    "nano",
)


def classify_model_tier(model_name: str) -> str:
    """Classifies a model identifier into one of three architectural capability tiers."""
    lower = model_name.lower()
    if any(tok in lower for tok in LRM_AND_FRONTIER_TOKENS) and not any(
        small in lower for small in ("1.5b", "7b", "8b", "flash")
    ):
        return "Tier 3: Frontier & Large Reasoning Models"
    if any(tok in lower for tok in SUB_14B_TOKENS):
        return "Tier 1: Sub-14B Edge & Flash"
    return "Tier 2: 14B-70B Open-Weights"


def strip_certificate_scaffolding(text: str) -> str:
    """Removes explicit certificate tags ([P1], [T1], [V1], etc.) and section headers so judges grade substance over syntax."""
    cleaned = CERT_TAG_PATTERN.sub("", text)
    cleaned = re.sub(
        r"^#{1,4}\s*(?:PREMISES|EVIDENCE TRACES|EXECUTION TRACES|COMPLIANCE TRACES|CLAIM TRACES|"
        r"FINANCIAL TRACES|LEGAL TRACES|DIAGNOSTIC\s*&\s*ACUITY TRACES|COMPARISON TRACES|OPTION TRACES|"
        r"FORMAL CONCLUSION|REMEDIATION\s*/\s*NEXT ACTION|VERIFICATION GATE|POST-HOC VERIFICATION GATE|"
        r"BACKSTAGE|BACKSTAGE SCAFFOLD|INTERNAL BACKSTAGE PREPARATION|FINAL DELIVERABLE|FINAL PRODUCT DESCRIPTION)\s*$",
        "",
        cleaned,
        flags=re.M | re.I,
    )
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def deterministic_ab_assignment(seed: int, model: str, test_id: int) -> dict[str, str]:
    """Deterministically maps ('A', 'B') to ('baseline', 'optimized') using SHA-256."""
    digest = hashlib.sha256(f"{seed}:{model}:{test_id}".encode("utf-8")).digest()
    if (digest[0] % 2) == 0:
        return {"A": "baseline", "B": "optimized"}
    return {"A": "optimized", "B": "baseline"}


def build_blind_eval_instruction(
    tc: dict[str, Any],
    resp_a_text: str,
    resp_b_text: str,
    strip_markers: bool = False,
) -> str:
    """Builds a blinded, label-leak-free evaluation prompt for Step D using anonymous Candidate A/B columns."""
    clean_a = strip_certificate_scaffolding(resp_a_text) if strip_markers else resp_a_text
    clean_b = strip_certificate_scaffolding(resp_b_text) if strip_markers else resp_b_text
    words_a = len(clean_a.split())
    words_b = len(clean_b.split())

    return (
        "You are an independent, rigorous evaluator scoring two anonymized candidate responses "
        "(Candidate A vs. Candidate B) to the ORIGINAL TASK below.\n"
        "Judge strictly on how accurately, completely, clearly, and actionably each candidate "
        "solves the ORIGINAL TASK, including preserving all requested deliverables and constraints. "
        "Do NOT reward verbosity or bracketed headers unless they substantively improve factual accuracy, "
        "edge-case coverage, or verification rigor.\n\n"
        f"ORIGINAL TASK ({tc['domain']} - {tc['task_type']}):\n{tc['raw_prompt']}\n\n"
        f"=== CANDIDATE A ({words_a} words) ===\n{clean_a}\n\n"
        f"=== CANDIDATE B ({words_b} words) ===\n{clean_b}\n\n"
        "Score BOTH responses from 1 to 5 on each of the 5 dimensions using this exact Markdown table "
        "(where Delta is Candidate B minus Candidate A):\n\n"
        "| Dimension | Candidate A (1-5) | Candidate B (1-5) | Delta (B - A) | Evidence / Justification |\n"
        "| :--- | :---: | :---: | :---: | :--- |\n"
        "| Accuracy | X | Y | +/-Z | ... |\n"
        "| Completeness | X | Y | +/-Z | ... |\n"
        "| Structure | X | Y | +/-Z | ... |\n"
        "| Actionability | X | Y | +/-Z | ... |\n"
        "| Traceability | X | Y | +/-Z | ... |\n"
        "| **TOTAL (/25)** | **XX** | **YY** | **+/-ZZ** | **Winner: Candidate A / Candidate B / Tie** |\n\n"
        "COLUMN MAPPING RULE: Record Candidate A's score in the 'Candidate A (1-5)' column "
        "and Candidate B's score in the 'Candidate B (1-5)' column."
    )


def unblind_parsed_scores(
    parsed_ab: dict[str, Any], mapping: dict[str, str]
) -> dict[str, Any]:
    """Maps blinded (Candidate A, Candidate B) scores back to true ('baseline', 'optimized') scores.

    `parse_scores` extracts column 1 into `baseline_total` (Candidate A) and column 2 into `optimized_total` (Candidate B).
    """
    if mapping["A"] == "baseline" and mapping["B"] == "optimized":
        return {**parsed_ab, "blind_mapping": mapping}

    unblinded: dict[str, Any] = dict(parsed_ab)
    b_tot = parsed_ab.get("optimized_total", 0)
    o_tot = parsed_ab.get("baseline_total", 0)
    unblinded["baseline_total"] = b_tot
    unblinded["optimized_total"] = o_tot
    unblinded["delta_total"] = round(o_tot - b_tot, 2)

    if "dimensions" in parsed_ab and isinstance(parsed_ab["dimensions"], dict):
        swapped_dims = {}
        for dim, vals in parsed_ab["dimensions"].items():
            b_val = vals.get("optimized", 0)
            o_val = vals.get("baseline", 0)
            swapped_dims[dim] = {
                **vals,
                "baseline": b_val,
                "optimized": o_val,
                "delta": round(o_val - b_val, 2),
            }
        unblinded["dimensions"] = swapped_dims

    if o_tot > b_tot:
        unblinded["winner"] = "Optimized"
    elif b_tot > o_tot:
        unblinded["winner"] = "Baseline"
    else:
        unblinded["winner"] = "Tie"

    unblinded["blind_mapping"] = mapping
    return unblinded


def merge_position_swapped_scores(
    pass1_unblinded: dict[str, Any], pass2_unblinded: dict[str, Any]
) -> dict[str, Any]:
    """Combines Pass 1 (A, B) and Pass 2 (B, A) unblinded scores to cancel position bias."""
    b_avg = round(
        (pass1_unblinded["baseline_total"] + pass2_unblinded["baseline_total"]) / 2.0, 2
    )
    o_avg = round(
        (pass1_unblinded["optimized_total"] + pass2_unblinded["optimized_total"]) / 2.0, 2
    )
    delta_avg = round(o_avg - b_avg, 2)

    if o_avg > b_avg:
        winner = "Optimized"
    elif b_avg > o_avg:
        winner = "Baseline"
    else:
        winner = "Tie"

    merged_dims: dict[str, dict[str, float]] = {}
    dims1 = pass1_unblinded.get("dimensions", {})
    dims2 = pass2_unblinded.get("dimensions", {})
    for dim in dims1:
        if dim in dims2:
            b_d = round((dims1[dim]["baseline"] + dims2[dim]["baseline"]) / 2.0, 2)
            o_d = round((dims1[dim]["optimized"] + dims2[dim]["optimized"]) / 2.0, 2)
            merged_dims[dim] = {
                "baseline": b_d,
                "optimized": o_d,
                "delta": round(o_d - b_d, 2),
            }

    return {
        "baseline_total": b_avg,
        "optimized_total": o_avg,
        "delta_total": delta_avg,
        "winner": winner,
        "dimensions": merged_dims,
        "position_swap_consistent": pass1_unblinded["winner"] == pass2_unblinded["winner"],
        "pass1": pass1_unblinded,
        "pass2": pass2_unblinded,
    }


def bootstrap_mean_ci(
    values: list[float],
    n_resamples: int = 10000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Computes cell-level (mean, ci_low, ci_high) via non-parametric bootstrap in pure Python."""
    if not values:
        return (0.0, 0.0, 0.0)
    if len(values) == 1:
        v = round(values[0], 4)
        return (v, v, v)

    rng = random.Random(seed)
    n = len(values)
    means = sorted(
        sum(rng.choices(values, k=n)) / n for _ in range(n_resamples)
    )
    alpha = (1.0 - confidence) / 2.0
    low_idx = max(0, int(math.floor(alpha * n_resamples)))
    high_idx = min(n_resamples - 1, int(math.ceil((1.0 - alpha) * n_resamples)) - 1)
    return (
        round(statistics.fmean(values), 4),
        round(means[low_idx], 4),
        round(means[high_idx], 4),
    )


def cluster_bootstrap_mean_ci(
    records: list[dict[str, Any]],
    cluster_key: str = "model",
    n_resamples: int = 5000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Computes cluster-robust (mean, ci_low, ci_high) by resampling entire clusters (e.g. models or tasks) with replacement."""
    if not records:
        return (0.0, 0.0, 0.0)

    clusters: dict[Any, list[float]] = {}
    all_deltas: list[float] = []
    for r in records:
        d = float(r["optimized_total"]) - float(r["baseline_total"])
        all_deltas.append(d)
        cid = r.get(cluster_key, "unknown")
        clusters.setdefault(cid, []).append(d)

    overall_mean = round(statistics.fmean(all_deltas), 4)
    cluster_keys = sorted(clusters.keys(), key=str)
    if len(cluster_keys) <= 1:
        return (overall_mean, overall_mean, overall_mean)

    rng = random.Random(seed)
    k = len(cluster_keys)
    resampled_means: list[float] = []
    for _ in range(n_resamples):
        chosen = rng.choices(cluster_keys, k=k)
        total_sum = sum(sum(clusters[c]) for c in chosen)
        total_count = sum(len(clusters[c]) for c in chosen)
        resampled_means.append(total_sum / max(total_count, 1))

    resampled_means.sort()
    alpha = (1.0 - confidence) / 2.0
    low_idx = max(0, int(math.floor(alpha * n_resamples)))
    high_idx = min(n_resamples - 1, int(math.ceil((1.0 - alpha) * n_resamples)) - 1)
    return (
        overall_mean,
        round(resampled_means[low_idx], 4),
        round(resampled_means[high_idx], 4),
    )


def two_way_block_bootstrap_ci(
    records: list[dict[str, Any]],
    n_resamples: int = 5000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Resamples both models and tasks independently with replacement to account for crossed (model x task) random effects."""
    if not records:
        return (0.0, 0.0, 0.0)

    all_deltas = [float(r["optimized_total"]) - float(r["baseline_total"]) for r in records]
    overall_mean = round(statistics.fmean(all_deltas), 4)

    models = sorted({str(r.get("model", "m")) for r in records})
    tasks = sorted({str(r.get("test_id", r.get("id", "t"))) for r in records})
    if len(models) <= 1 and len(tasks) <= 1:
        return (overall_mean, overall_mean, overall_mean)

    cell_map: dict[tuple[str, str], list[float]] = {}
    for r in records:
        m = str(r.get("model", "m"))
        t = str(r.get("test_id", r.get("id", "t")))
        d = float(r["optimized_total"]) - float(r["baseline_total"])
        cell_map.setdefault((m, t), []).append(d)

    rng = random.Random(seed)
    n_m = len(models)
    n_t = len(tasks)
    resampled_means: list[float] = []
    for _ in range(n_resamples):
        sampled_m = rng.choices(models, k=n_m) if n_m > 1 else models
        sampled_t = rng.choices(tasks, k=n_t) if n_t > 1 else tasks
        vals: list[float] = []
        for m in sampled_m:
            for t in sampled_t:
                if (m, t) in cell_map:
                    vals.extend(cell_map[(m, t)])
        if vals:
            resampled_means.append(sum(vals) / len(vals))

    if not resampled_means:
        return (overall_mean, overall_mean, overall_mean)

    resampled_means.sort()
    alpha = (1.0 - confidence) / 2.0
    low_idx = max(0, int(math.floor(alpha * len(resampled_means))))
    high_idx = min(len(resampled_means) - 1, int(math.ceil((1.0 - alpha) * len(resampled_means))) - 1)
    return (
        overall_mean,
        round(resampled_means[low_idx], 4),
        round(resampled_means[high_idx], 4),
    )


def paired_sign_flip_p_value(
    deltas: list[float],
    n_permutations: int = 10000,
    seed: int = 42,
) -> float:
    """Computes two-sided paired sign-flip permutation p-value for H0: mean(deltas) == 0."""
    non_zero = [d for d in deltas if abs(d) > 1e-9]
    n = len(non_zero)
    if n == 0:
        return 1.0

    observed = abs(statistics.fmean(non_zero))
    if n <= 14:
        total_configs = 1 << n
        extreme_count = 0
        for mask in range(total_configs):
            signed_sum = 0.0
            for i, d in enumerate(non_zero):
                signed_sum += d if ((mask >> i) & 1) else -d
            if abs(signed_sum / n) >= observed - 1e-12:
                extreme_count += 1
        return round(extreme_count / total_configs, 6)

    rng = random.Random(seed)
    extreme_count = 1
    for _ in range(n_permutations - 1):
        signed_mean = abs(
            sum(d if rng.getrandbits(1) else -d for d in non_zero) / n
        )
        if signed_mean >= observed - 1e-12:
            extreme_count += 1
    return round(extreme_count / n_permutations, 6)


def compute_stratified_benchmark_summary(
    records: list[dict[str, Any]], seed: int = 42
) -> dict[str, Any]:
    """Aggregates evaluation pairs with Cell, Model-Cluster, and Two-Way Block Bootstrap CIs and p-values."""
    if not records:
        return {"total_pairs": 0}

    deltas = [r["optimized_total"] - r["baseline_total"] for r in records]
    base_scores = [r["baseline_total"] for r in records]
    opt_scores = [r["optimized_total"] for r in records]

    mean_delta, ci_low, ci_high = bootstrap_mean_ci(deltas, seed=seed)
    _, model_ci_low, model_ci_high = cluster_bootstrap_mean_ci(records, cluster_key="model", seed=seed)
    _, twoway_ci_low, twoway_ci_high = two_way_block_bootstrap_ci(records, seed=seed)
    p_val_cell = paired_sign_flip_p_value(deltas, seed=seed)

    by_model_deltas: dict[str, list[float]] = {}
    by_task_deltas: dict[str, list[float]] = {}
    for r, d in zip(records, deltas):
        by_model_deltas.setdefault(str(r.get("model", "m")), []).append(d)
        by_task_deltas.setdefault(str(r.get("test_id", r.get("id", "t"))), []).append(d)

    model_mean_deltas = [statistics.fmean(v) for v in by_model_deltas.values()]
    task_mean_deltas = [statistics.fmean(v) for v in by_task_deltas.values()]
    p_val_model_cluster = paired_sign_flip_p_value(model_mean_deltas, seed=seed)
    p_val_task_cluster = paired_sign_flip_p_value(task_mean_deltas, seed=seed)

    base_mean = statistics.fmean(base_scores)
    opt_mean = statistics.fmean(opt_scores)
    rel_lift_pct = round(((opt_mean - base_mean) / base_mean) * 100.0, 2) if base_mean > 0 else 0.0

    wins = sum(1 for d in deltas if d > 1e-9)
    losses = sum(1 for d in deltas if d < -1e-9)
    ties = len(deltas) - wins - losses

    token_ratios = []
    lifts_per_1k = []
    for r, d in zip(records, deltas):
        b_tok = r.get("baseline_tokens")
        o_tok = r.get("optimized_tokens")
        if b_tok is not None and o_tok is not None and int(b_tok) > 0 and int(o_tok) > 0:
            b_t = int(b_tok)
            o_t = int(o_tok)
            token_ratios.append(o_t / b_t)
            extra = o_t - b_t
            if extra > 0:
                lifts_per_1k.append((d / extra) * 1000.0)

    tiers: dict[str, list[float]] = {}
    for r, d in zip(records, deltas):
        tier = classify_model_tier(r.get("model", "unknown"))
        tiers.setdefault(tier, []).append(d)

    tier_summaries = {}
    for tier, t_deltas in sorted(tiers.items()):
        t_mean, t_low, t_high = bootstrap_mean_ci(t_deltas, n_resamples=2000, seed=seed)
        tier_summaries[tier] = {
            "pairs": len(t_deltas),
            "mean_delta": t_mean,
            "ci_95": [t_low, t_high],
            "win_rate_pct": round(
                (sum(1 for d in t_deltas if d > 1e-9) / len(t_deltas)) * 100.0, 1
            ),
        }

    swap_tracked = [
        r["position_swap_consistent"]
        for r in records
        if r.get("position_swap_consistent") is not None
    ]

    return {
        "total_pairs": len(records),
        "n_models": len(by_model_deltas),
        "n_tasks": len(by_task_deltas),
        "baseline_mean": round(base_mean, 2),
        "optimized_mean": round(opt_mean, 2),
        "mean_delta": mean_delta,
        "delta_95_ci": [ci_low, ci_high],
        "model_cluster_95_ci": [model_ci_low, model_ci_high],
        "two_way_block_95_ci": [twoway_ci_low, twoway_ci_high],
        "paired_sign_flip_p_value": p_val_cell,
        "model_cluster_sign_flip_p_value": p_val_model_cluster,
        "task_cluster_sign_flip_p_value": p_val_task_cluster,
        "relative_lift_pct": rel_lift_pct,
        "record": {"wins": wins, "ties": ties, "losses": losses},
        "win_rate_pct": round((wins / len(records)) * 100.0, 1),
        "measured_token_pairs": len(token_ratios),
        "mean_token_overhead_ratio": round(statistics.fmean(token_ratios), 2) if token_ratios else None,
        "mean_lift_per_1k_extra_tokens": round(statistics.fmean(lifts_per_1k), 2) if lifts_per_1k else None,
        "position_swap_consistency_pct": (
            round((sum(1 for c in swap_tracked if c) / len(swap_tracked)) * 100.0, 1)
            if swap_tracked
            else None
        ),
        "by_tier": tier_summaries,
    }


class BlindStatsEngineTests(unittest.TestCase):
    def test_strip_certificate_scaffolding_removes_tags_and_headers(self) -> None:
        raw = "### PREMISES\n[P1] Input X is bounded.\n[T1] X -> Y\n[REASONING-CERT] Final output."
        cleaned = strip_certificate_scaffolding(raw)
        self.assertNotIn("[P1]", cleaned)
        self.assertNotIn("[T1]", cleaned)
        self.assertNotIn("[REASONING-CERT]", cleaned)
        self.assertNotIn("PREMISES", cleaned)
        self.assertIn("Input X is bounded.", cleaned)

    def test_blind_eval_instruction_has_zero_baseline_or_optimized_labels(self) -> None:
        tc = {"domain": "Code Review", "task_type": "Accuracy", "raw_prompt": "def f(x): return x"}
        prompt = build_blind_eval_instruction(tc, "Answer 1", "Answer 2", strip_markers=False)
        self.assertNotIn("Baseline", prompt)
        self.assertNotIn("Optimized", prompt)
        self.assertIn("Candidate A (1-5)", prompt)
        self.assertIn("Candidate B (1-5)", prompt)

    def test_unblind_and_position_swap_reconciliation(self) -> None:
        raw_p1 = {
            "baseline_total": 23,
            "optimized_total": 17,
            "delta_total": -6,
            "winner": "Baseline",
            "dimensions": {"Accuracy": {"baseline": 5, "optimized": 3, "delta": -2}},
        }
        p1 = unblind_parsed_scores(raw_p1, {"A": "optimized", "B": "baseline"})
        self.assertEqual(p1["winner"], "Optimized")
        self.assertEqual(p1["delta_total"], 6)

        raw_p2 = {
            "baseline_total": 15,
            "optimized_total": 21,
            "delta_total": 6,
            "winner": "Optimized",
            "dimensions": {"Accuracy": {"baseline": 3, "optimized": 5, "delta": 2}},
        }
        p2 = unblind_parsed_scores(raw_p2, {"A": "baseline", "B": "optimized"})
        merged = merge_position_swapped_scores(p1, p2)
        self.assertTrue(merged["position_swap_consistent"])
        self.assertEqual(merged["baseline_total"], 16.0)
        self.assertEqual(merged["optimized_total"], 22.0)

    def test_stratified_summary_computes_cluster_ci_and_p_value(self) -> None:
        sample_records = [
            {
                "model": "qwen2.5-coder:7b",
                "test_id": i,
                "baseline_total": 15.0,
                "optimized_total": 19.5,
                "baseline_tokens": 300,
                "optimized_tokens": 450,
                "position_swap_consistent": True,
            }
            for i in range(1, 5)
        ] + [
            {
                "model": "llama3.3:70b",
                "test_id": i,
                "baseline_total": 17.0,
                "optimized_total": 22.0,
                "baseline_tokens": 350,
                "optimized_tokens": 500,
                "position_swap_consistent": True,
            }
            for i in range(1, 5)
        ] + [
            {
                "model": "deepseek-r1:70b",
                "test_id": i,
                "baseline_total": 18.5,
                "optimized_total": 23.5,
                "baseline_tokens": None,
                "optimized_tokens": None,
                "position_swap_consistent": True,
            }
            for i in range(1, 5)
        ]
        summary = compute_stratified_benchmark_summary(sample_records, seed=42)
        self.assertEqual(summary["total_pairs"], 12)
        self.assertEqual(summary["n_models"], 3)
        self.assertEqual(summary["n_tasks"], 4)
        self.assertEqual(summary["measured_token_pairs"], 8)
        self.assertGreater(summary["mean_delta"], 4.0)
        self.assertGreater(summary["model_cluster_95_ci"][0], 4.0)
        self.assertGreater(summary["two_way_block_95_ci"][0], 4.0)
        self.assertLess(summary["paired_sign_flip_p_value"], 0.01)
        self.assertEqual(summary["position_swap_consistency_pct"], 100.0)


if __name__ == "__main__":
    unittest.main()
