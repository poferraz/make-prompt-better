#!/usr/bin/env python3
"""Zero-dependency Blinded A/B Judge & Non-Parametric Statistical Engine for make-prompt-better.

Addresses four core benchmark validity requirements in research/benchmark/v4/:
1. Eliminates self-preference bias by decoupling --judge-model from candidate models.
2. Eliminates rubric leakage (strips OPTIMIZED PROMPT from judge instructions and optionally
   strips [P1]/[T1]/[V1]/[C1] certificate bracket tags before evaluation).
3. Cancels position/recency bias via deterministic A/B randomization and 2-pass position swapping,
   computing position-consistency rates across evaluation pairs.
4. Replaces flat unweighted averages with 10,000-resample Bootstrap 95% Confidence Intervals,
   exact two-sided Paired Sign-Flip / Wilcoxon-style permutation p-values, Parameter-Tier
   Stratification (<14B Flash/Edge, 14B-70B Mid, Frontier/LRM), and Pareto token-efficiency metrics
   using 100% Python 3.12 standard library modules.
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
    r"\[(?:P\d+|T\d+|V\d+|C\d+|REASONING-CERT|CONTEXT-CERT|HARNESS-CERT|DIVERSITY-CERT|"
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
    "claude",
    "gpt-4",
    "gpt-5",
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
    """Classifies a model identifier into one of three architectural capability tiers.

    Checks Large Reasoning Models (LRMs) and frontier API models first so reasoning-tuned
    weights (e.g. deepseek-r1:70b) are grouped with LRMs rather than standard instruct models.
    """
    lower = model_name.lower()
    if any(tok in lower for tok in LRM_AND_FRONTIER_TOKENS) and not any(
        small in lower for small in ("1.5b", "7b", "8b", "flash")
    ):
        return "Tier 3: Frontier & Large Reasoning Models"
    if any(tok in lower for tok in SUB_14B_TOKENS):
        return "Tier 1: Sub-14B Edge & Flash"
    return "Tier 2: 14B-70B Open-Weights"


def strip_certificate_scaffolding(text: str) -> str:
    """Removes explicit certificate tags ([P1], [T1], [V1], etc.) so judges grade substance over syntax."""
    cleaned = CERT_TAG_PATTERN.sub("", text)
    cleaned = re.sub(
        r"^#{1,4}\s*(?:PREMISES|EVIDENCE TRACES|FORMAL CONCLUSION|VERIFICATION GATE)\s*$",
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
    """Builds a blinded, rubric-leak-free evaluation prompt for Step D."""
    clean_a = strip_certificate_scaffolding(resp_a_text) if strip_markers else resp_a_text
    clean_b = strip_certificate_scaffolding(resp_b_text) if strip_markers else resp_b_text
    words_a = len(clean_a.split())
    words_b = len(clean_b.split())

    return (
        "You are an independent, rigorous evaluator scoring two anonymized candidate responses "
        "(Candidate Response A vs. Candidate Response B) to the ORIGINAL TASK below.\n"
        "Judge strictly on how accurately, completely, clearly, and actionably each candidate "
        "solves the ORIGINAL TASK. Do NOT reward verbosity or bracketed headers unless they "
        "substantively improve factual accuracy, edge-case coverage, or verification rigor.\n\n"
        f"ORIGINAL TASK ({tc['domain']} - {tc['task_type']}):\n{tc['raw_prompt']}\n\n"
        f"=== CANDIDATE RESPONSE A ({words_a} words) ===\n{clean_a}\n\n"
        f"=== CANDIDATE RESPONSE B ({words_b} words) ===\n{clean_b}\n\n"
        "Score BOTH responses from 1 to 5 on each of the 5 dimensions using this exact Markdown table:\n\n"
        "| Dimension | Baseline (1-5) | Optimized (1-5) | Delta | Evidence / Justification |\n"
        "| :--- | :---: | :---: | :---: | :--- |\n"
        "| Accuracy | X | Y | +/-Z | ... |\n"
        "| Completeness | X | Y | +/-Z | ... |\n"
        "| Structure | X | Y | +/-Z | ... |\n"
        "| Actionability | X | Y | +/-Z | ... |\n"
        "| Traceability | X | Y | +/-Z | ... |\n"
        "| **TOTAL (/25)** | **XX** | **YY** | **+/-ZZ** | **Winner: Baseline / Optimized / Tie** |\n\n"
        "COLUMN MAPPING RULE: Record Candidate Response A's score in the 'Baseline (1-5)' column "
        "and Candidate Response B's score in the 'Optimized (1-5)' column."
    )


def unblind_parsed_scores(
    parsed_ab: dict[str, Any], mapping: dict[str, str]
) -> dict[str, Any]:
    """Maps blinded (A, B) scores back to true ('baseline', 'optimized') scores."""
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
    """Computes (mean, ci_low, ci_high) via non-parametric bootstrap in pure Python."""
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
    """Aggregates evaluation pairs with Bootstrap CIs, p-values, and Tier Stratification."""
    if not records:
        return {"total_pairs": 0}

    deltas = [r["optimized_total"] - r["baseline_total"] for r in records]
    base_scores = [r["baseline_total"] for r in records]
    opt_scores = [r["optimized_total"] for r in records]

    mean_delta, ci_low, ci_high = bootstrap_mean_ci(deltas, seed=seed)
    p_val = paired_sign_flip_p_value(deltas, seed=seed)

    base_mean = statistics.fmean(base_scores)
    opt_mean = statistics.fmean(opt_scores)
    rel_lift_pct = round(((opt_mean - base_mean) / base_mean) * 100.0, 2) if base_mean > 0 else 0.0

    wins = sum(1 for d in deltas if d > 1e-9)
    losses = sum(1 for d in deltas if d < -1e-9)
    ties = len(deltas) - wins - losses

    token_ratios = []
    lifts_per_1k = []
    for r, d in zip(records, deltas):
        b_tok = max(int(r.get("baseline_tokens", 1)), 1)
        o_tok = max(int(r.get("optimized_tokens", 1)), 1)
        token_ratios.append(o_tok / b_tok)
        extra = o_tok - b_tok
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
        if "position_swap_consistent" in r
    ]

    return {
        "total_pairs": len(records),
        "baseline_mean": round(base_mean, 2),
        "optimized_mean": round(opt_mean, 2),
        "mean_delta": mean_delta,
        "delta_95_ci": [ci_low, ci_high],
        "paired_sign_flip_p_value": p_val,
        "relative_lift_pct": rel_lift_pct,
        "record": {"wins": wins, "ties": ties, "losses": losses},
        "win_rate_pct": round((wins / len(records)) * 100.0, 1),
        "mean_token_overhead_ratio": round(statistics.fmean(token_ratios), 2) if token_ratios else 1.0,
        "mean_lift_per_1k_extra_tokens": round(statistics.fmean(lifts_per_1k), 2) if lifts_per_1k else 0.0,
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

    def test_stratified_summary_computes_ci_and_p_value(self) -> None:
        sample_records = [
            {
                "model": "qwen2.5-coder:7b",
                "baseline_total": 15.0,
                "optimized_total": 19.5,
                "baseline_tokens": 300,
                "optimized_tokens": 450,
                "position_swap_consistent": True,
            },
            {
                "model": "llama3.3:70b",
                "baseline_total": 17.0,
                "optimized_total": 22.0,
                "baseline_tokens": 350,
                "optimized_tokens": 500,
                "position_swap_consistent": True,
            },
            {
                "model": "deepseek-r1:70b",
                "baseline_total": 18.5,
                "optimized_total": 23.5,
                "baseline_tokens": 400,
                "optimized_tokens": 520,
                "position_swap_consistent": True,
            },
        ] * 4
        summary = compute_stratified_benchmark_summary(sample_records, seed=42)
        self.assertEqual(summary["total_pairs"], 12)
        self.assertGreater(summary["mean_delta"], 4.0)
        self.assertGreater(summary["delta_95_ci"][0], 3.5)
        self.assertLess(summary["paired_sign_flip_p_value"], 0.01)
        self.assertEqual(summary["position_swap_consistency_pct"], 100.0)
        self.assertIn("Tier 1: Sub-14B Edge & Flash", summary["by_tier"])
        self.assertIn("Tier 2: 14B-70B Open-Weights", summary["by_tier"])
        self.assertIn("Tier 3: Frontier & Large Reasoning Models", summary["by_tier"])


if __name__ == "__main__":
    unittest.main()