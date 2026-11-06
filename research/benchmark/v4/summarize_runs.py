#!/usr/bin/env python3
"""Summarize provenance-bound runs without pooling incompatible protocols."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile


REQUIRED = {"schema", "model", "judge_model", "skill_sha256", "test_suite_sha256",
            "runner_sha256", "judge_code_sha256", "host_sha256", "test_ids", "timeout",
            "blind_eval", "swap_positions", "strip_cert_markers", "unprescribed_routing",
            "seed", "loading_strategy"}


def summarize(results_dir: Path) -> dict:
    groups = {}
    seen = set()
    files = sorted(results_dir.glob("*/metrics.json"))
    if not files:
        raise ValueError("No model metrics found in the selected run")
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        manifest = data.get("manifest")
        if not isinstance(manifest, dict) or not REQUIRED <= manifest.keys() or manifest["schema"] != 1:
            raise ValueError(f"Missing or unsupported manifest: {path}")
        model = data.get("model")
        if model != manifest["model"]:
            raise ValueError(f"Model differs from manifest: {path}")
        self_judged = manifest["judge_model"] == model
        identity = {key: value for key, value in manifest.items() if key not in {"model", "judge_model"}}
        identity["judge"] = "self" if self_judged else manifest["judge_model"]
        group_key = json.dumps(identity, sort_keys=True)
        group = groups.setdefault(group_key, {"protocol": identity, "models": set(), "deltas": []})
        for test_id, test in data.get("tests", {}).items():
            if (model, test_id) in seen:
                raise ValueError(f"Duplicate model/test pair: {model}, {test_id}")
            seen.add((model, test_id))
            if int(test_id) not in manifest["test_ids"]:
                raise ValueError(f"Test is outside the manifest: {path}, {test_id}")
            if test.get("judge_model") != manifest["judge_model"] or test.get("self_judged") != self_judged:
                raise ValueError(f"Saved judge differs from manifest: {path}, {test_id}")
            scores = test["evaluation"]["parsed"]
            baseline, optimized, delta = (scores[key] for key in ("baseline_total", "optimized_total", "delta_total"))
            if not (5 <= baseline <= 25 and 5 <= optimized <= 25 and abs(optimized - baseline - delta) < 0.001):
                raise ValueError(f"Invalid or inconsistent scores: {path}, {test_id}")
            group["models"].add(model)
            group["deltas"].append(delta)
    return {"description": "Descriptive saved judge scores; not proof of efficacy.", "groups": [
        {"protocol": group["protocol"], "models": sorted(group["models"]),
         "pairs": len(group["deltas"]),
         "mean_delta": round(sum(group["deltas"]) / len(group["deltas"]), 4) if group["deltas"] else None}
        for group in groups.values()
    ]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New summary file; existing files are never overwritten.")
    args = parser.parse_args()
    try:
        result = summarize(args.results_dir)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(prefix=".summary.", dir=args.output.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(result, stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temp, args.output)
        finally:
            os.unlink(temp)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(result['groups'])} protocol group(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
