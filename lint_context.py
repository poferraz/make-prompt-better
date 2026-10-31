#!/usr/bin/env python3
"""Standalone [CONTEXT-CERT] Repository Context File Linter & Readiness Auditor.

Implements the empirical findings from make-prompt-better's research foundation:
- [CONTEXT-FILES] Gloaguen et al., 2026 (arXiv:2602.11988): Repository context files
  degrade agent task resolution when bloated with inferable directory trees or generic
  style guides; they improve performance only when restricted to non-inferable build/test
  commands, hard architectural invariants, non-obvious traps, and critical file anchors.
- [PRISM] Hu, Rostami & Thomason, 2026 (arXiv:2603.18507): Uncalibrated expert persona
  fluff ("You are a world-class 10x engineer") consumes attention and degrades accuracy.
- [META] Ugare & Chandra, 2026 (arXiv:2603.01896) & [SKILLS-SDO] Yin et al., 2026
  (arXiv:2608.12610): Negative-only constraints ("don't hallucinate", "never guess")
  fail under attention load unless rewritten as positive verification recipes.

Usage:
  python3 lint_context.py CLAUDE.md AGENTS.md
  python3 lint_context.py --json CLAUDE.md
  python3 lint_context.py --self-test
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import unittest
from typing import Any

# 1. Anti-pattern detectors grounded in arXiv:2602.11988, arXiv:2603.18507, arXiv:2608.12610
ASCII_TREE_RE = re.compile(r"[├└│─]{2,}|\+--\s|\|--\s")
PERSONA_BLOAT_RE = re.compile(
    r"\b(?:you are a(?:n)?\s+(?:world[- ]class|elite|10x|genius|master|top\s+1%)|"
    r"act as a\s+world[- ]class|as an? supreme expert)\b",
    re.I,
)
POLITENESS_FILLER_RE = re.compile(
    r"\b(?:please\s+make\s+sure\s+to|thank\s+you\s+in\s+advance|i\s+will\s+tip\s+you\s+\$\d+|"
    r"take\s+a\s+deep\s+breath\s+and\s+work\s+on\s+this\s+step\s+by\s+step)\b",
    re.I,
)
UNGROUNDED_NEGATIVE_RE = re.compile(
    r"\b(?:do\s+not\s+hallucinate|don't\s+hallucinate|never\s+hallucinate|"
    r"do\s+not\s+make\s+mistakes|never\s+make\s+bugs|be\s+100%\s+accurate)\b",
    re.I,
)
CONCLUSION_FIRST_RE = re.compile(
    r"\b(?:lead\s+with\s+(?:the\s+)?(?:final\s+)?(?:answer|verdict|conclusion)|"
    r"state\s+(?:the\s+)?(?:final\s+)?(?:answer|verdict)\s+first|"
    r"point\s+first\s+before\s+reasoning)\b",
    re.I,
)
GOAL_LEAKAGE_RE = re.compile(
    r"\b(?:for\s+(?:tomorrow's|our|the)\s+(?:client\s+demo|board\s+meeting|investor\s+pitch)|"
    r"so\s+we\s+can\s+prove\s+that|my\s+career\s+depends\s+on)\b",
    re.I,
)
EM_EN_DASH_RE = re.compile(r"[\u2014\u2013]")

# 2. [CONTEXT-CERT] 4-Pillar Signals (Mode 3 Pattern B)
PILLAR_SIGNALS: dict[str, re.Pattern[str]] = {
    "environment_commands": re.compile(
        r"(?:pytest|unittest|npm\s+test|pnpm|cargo\s+test|go\s+test|bash\s+-n|"
        r"\./install\.sh|make\s+\w+|python3\s+-m)",
        re.I,
    ),
    "architectural_invariants": re.compile(
        r"\b(?:invariant|must\s+remain|progressive\s+disclosure|line\s+limit|"
        r"under\s+\d+\s+lines|schema|frontmatter|contract)\b",
        re.I,
    ),
    "traps_and_antipatterns": re.compile(
        r"\b(?:trap|anti[- ]?pattern|pitfall|gotcha|avoid|never\s+use|warning|caveat)\b",
        re.I,
    ),
    "critical_file_anchors": re.compile(
        r"(?:`[a-zA-Z0-9_./-]+\.(?:py|md|sh|yml|yaml|json|ts|rs|go)`)",
    ),
}


def estimate_tokens(text: str) -> int:
    """Approximates BPE token count (~1.33 tokens per whitespace-delimited word + punctuation)."""
    words = len(text.split())
    return max(1, int(round(words * 1.35)))


def audit_context_text(text: str, filename: str = "CLAUDE.md") -> dict[str, Any]:
    """Audits a repository context file or skill markdown file on a 100-point rubric."""
    lines = text.splitlines()
    line_count = len(lines)
    est_tokens = estimate_tokens(text)

    findings: list[dict[str, str]] = []

    # Category 1: Signal-to-Noise & Token Budget (25 points)
    snr_score = 25
    tree_lines = [i + 1 for i, ln in enumerate(lines) if ASCII_TREE_RE.search(ln)]
    if len(tree_lines) >= 4:
        penalty = min(15, len(tree_lines))
        snr_score -= penalty
        findings.append({
            "severity": "HIGH",
            "paper": "[CONTEXT-FILES] arXiv:2602.11988",
            "issue": f"Detected {len(tree_lines)} lines of ASCII directory tree visualization (lines {tree_lines[:4]}...).",
            "remediation": "Remove static directory trees; agents discover file trees dynamically via glob/ls. List only 3-6 Critical File Anchors with non-obvious roles.",
        })

    if line_count > 500:
        over_penalty = min(15, ((line_count - 500) // 50) * 3 + 5)
        snr_score -= over_penalty
        findings.append({
            "severity": "HIGH",
            "paper": "[SKILLS-SDO] arXiv:2608.12610",
            "issue": f"File length ({line_count} lines, ~{est_tokens} tokens) exceeds the 500-line progressive disclosure ceiling.",
            "remediation": "Offload domain-specific templates or long examples into references/ and keep the root file under 500 lines.",
        })
    snr_score = max(0, snr_score)

    # Category 2: Anti-Pattern & Persona Bloat Eradication (25 points)
    bloat_score = 25
    persona_hits = PERSONA_BLOAT_RE.findall(text)
    if persona_hits:
        bloat_score -= 10
        findings.append({
            "severity": "MEDIUM",
            "paper": "[PRISM] arXiv:2603.18507",
            "issue": f"Found uncalibrated expert roleplay fluff: {persona_hits[:3]!r}.",
            "remediation": "Replace generic expert flattery with explicit verification boundaries and domain invariants.",
        })

    politeness_hits = POLITENESS_FILLER_RE.findall(text)
    if politeness_hits:
        bloat_score -= 8
        findings.append({
            "severity": "LOW",
            "paper": "[GOAL-BLIND] arXiv:2602.09504",
            "issue": f"Found emotional/politeness filler phrases: {politeness_hits[:3]!r}.",
            "remediation": "Strip emotional incentives and politeness tokens; state operational goals directly.",
        })

    neg_hits = UNGROUNDED_NEGATIVE_RE.findall(text)
    if neg_hits:
        bloat_score -= 10
        findings.append({
            "severity": "MEDIUM",
            "paper": "[SKILLS-SDO] arXiv:2608.12610",
            "issue": f"Found ungrounded negative constraints ({neg_hits[:3]!r}) that fail under attention load.",
            "remediation": "Replace negative prohibitions ('don't hallucinate') with positive verification recipes (e.g., 'Cite exact file:line anchors for every claim').",
        })

    order_hits = CONCLUSION_FIRST_RE.findall(text)
    if order_hits:
        bloat_score -= 10
        findings.append({
            "severity": "HIGH",
            "paper": "[META] arXiv:2603.01896",
            "issue": f"Found conclusion-first reversal directive ({order_hits[:2]!r}) that suppresses evidence tracing.",
            "remediation": "Enforce Reason-Before-Conclude ordering: complete [P] Premises and [T] Traces before emitting the Verdict.",
        })

    leakage_hits = GOAL_LEAKAGE_RE.findall(text)
    if leakage_hits:
        bloat_score -= 10
        findings.append({
            "severity": "MEDIUM",
            "paper": "[GOAL-BLIND] arXiv:2602.09504",
            "issue": f"Found downstream goal/stake leakage ({leakage_hits[:2]!r}).",
            "remediation": "Enforce Goal-Blind Isolation: specify what artifact to verify without disclosing downstream business stakes.",
        })
    bloat_score = max(0, bloat_score)

    # Category 3: [CONTEXT-CERT] 4-Pillar Coverage (35 points)
    pillar_scores: dict[str, bool] = {}
    pillar_points = 0
    for pillar_name, pattern in PILLAR_SIGNALS.items():
        matched = bool(pattern.search(text))
        pillar_scores[pillar_name] = matched
        if matched:
            pillar_points += 9
    pillar_points = min(35, pillar_points)

    missing_pillars = [k for k, v in pillar_scores.items() if not v]
    if missing_pillars:
        findings.append({
            "severity": "MEDIUM",
            "paper": "[CONTEXT-CERT] Mode 3 Pattern B",
            "issue": f"Missing explicit signals for [CONTEXT-CERT] pillars: {', '.join(missing_pillars)}.",
            "remediation": "Ensure context covers: (1) Non-inferable build/test commands, (2) Hard architectural invariants, (3) Non-obvious traps, and (4) Critical file anchors.",
        })

    # Category 4: Universal Formatting & Typography Hygiene (15 points)
    hygiene_score = 15
    dash_hits = EM_EN_DASH_RE.findall(text)
    if dash_hits:
        hygiene_score -= min(15, len(dash_hits) * 3)
        findings.append({
            "severity": "LOW",
            "paper": "Repository Invariant (AGENTS.md)",
            "issue": f"Found {len(dash_hits)} forbidden em/en dash character(s) (— or –).",
            "remediation": "Replace em/en dashes with standard ASCII hyphens (-), colons (:), or semicolons (;).",
        })
    hygiene_score = max(0, hygiene_score)

    total_score = snr_score + bloat_score + pillar_points + hygiene_score
    grade = (
        "A (Certified)"
        if total_score >= 90
        else "B (Production-Ready)"
        if total_score >= 75
        else "C (Needs Compaction)"
        if total_score >= 60
        else "D (High Context Rot Risk)"
    )

    return {
        "file": filename,
        "lines": line_count,
        "estimated_tokens": est_tokens,
        "total_score": total_score,
        "grade": grade,
        "subscores": {
            "signal_to_noise_25": snr_score,
            "anti_bloat_25": bloat_score,
            "four_pillars_35": pillar_points,
            "hygiene_15": hygiene_score,
        },
        "pillars_detected": pillar_scores,
        "findings": findings,
    }


def format_audit_report(result: dict[str, Any]) -> str:
    """Renders a clean terminal report for a single context file audit."""
    sub = result["subscores"]
    out = [
        f"=== [CONTEXT-CERT] Audit: {result['file']} ===",
        f"Score: {result['total_score']}/100 ({result['grade']}) | "
        f"Lines: {result['lines']} | Est. Tokens: ~{result['estimated_tokens']}",
        f"Breakdown: SNR={sub['signal_to_noise_25']}/25 | Anti-Bloat={sub['anti_bloat_25']}/25 | "
        f"4-Pillars={sub['four_pillars_35']}/35 | Hygiene={sub['hygiene_15']}/15",
    ]
    if not result["findings"]:
        out.append("Status: PASS - Zero context bloat or anti-patterns detected.")
    else:
        out.append("Actionable Findings:")
        for idx, f in enumerate(result["findings"], 1):
            out.append(f"  {idx}. [{f['severity']}] ({f['paper']}) {f['issue']}")
            out.append(f"     Fix: {f['remediation']}")
    return "\n".join(out)


class ContextLinterTests(unittest.TestCase):
    def test_high_signal_context_scores_grade_a(self) -> None:
        good_context = (
            "# Repository Operating Contract\n\n"
            "## 1. Environment & Non-Inferable Commands\n"
            "- Run unit tests via `python3 -m unittest discover -s research/benchmark/v4 -p \"test_*.py\" -v`.\n"
            "- Sync skills via `./install.sh --symlink`.\n\n"
            "## 2. Hard Architectural Invariants\n"
            "- Maintain progressive disclosure: `make-prompt-better/SKILL.md` must remain under 500 lines.\n\n"
            "## 3. Non-Obvious Traps & Anti-Patterns\n"
            "- Trap: Never pass `OPTIMIZED PROMPT` into the Step D evaluator in `run_ollama_benchmarks.py`.\n\n"
            "## 4. Critical File Anchors\n"
            "- `make-prompt-better/SKILL.md`: Entrypoint router.\n"
            "- `research/benchmark/v4/aggregate_results.py`: Metric aggregator.\n"
        )
        res = audit_context_text(good_context, "CLAUDE.md")
        self.assertGreaterEqual(res["total_score"], 95)
        self.assertEqual(res["findings"], [])

    def test_bloated_context_with_tree_and_fluff_is_penalized(self) -> None:
        bad_context = (
            "You are a world-class 10x genius developer! Take a deep breath and work on this step by step.\n"
            "Please make sure to never make bugs and do not hallucinate — ever!\n"
            "├── src/\n"
            "│   ├── index.ts\n"
            "│   ├── utils.ts\n"
            "│   └── helpers.ts\n"
            "└── package.json\n"
        )
        res = audit_context_text(bad_context, "BAD_CLAUDE.md")
        self.assertLess(res["total_score"], 50)
        issues = " ".join(f["issue"] for f in res["findings"])
        self.assertIn("ASCII directory tree", issues)
        self.assertIn("expert roleplay fluff", issues)
        self.assertIn("negative constraints", issues)
        self.assertIn("em/en dash", issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit CLAUDE.md, AGENTS.md, or SKILL.md against [CONTEXT-CERT] standards."
    )
    parser.add_argument("files", nargs="*", help="Markdown context files to audit.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output for CI pipelines.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in unit tests.")
    args = parser.parse_args(argv)

    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ContextLinterTests)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1

    if not args.files:
        parser.print_help()
        return 1

    results = []
    for file_path in args.files:
        p = Path(file_path)
        if not p.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            return 1
        results.append(audit_context_text(p.read_text(encoding="utf-8"), str(p)))

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(format_audit_report(r))
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())