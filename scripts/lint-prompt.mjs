#!/usr/bin/env node
/**
 * Deterministic Static Prompt & Context Linter (v4.2.0)
 *
 * Audits prompts, SKILL.md files, and CLAUDE.md / AGENTS.md context files
 * against 6 research-grounded deterministic rules (0-100 score):
 * - DILUTION-01: Instruction dilution (>500 lines, ASCII directory trees, or >15 competing style directives)
 * - ORDER-02: Conclusion-first reversal ("state the final answer first" preceding reasoning blocks)
 * - PERSONA-03: Uncalibrated expert roleplay fluff ("You are a world-class 10x...") (arXiv:2603.18507)
 * - LEAKAGE-04: Goal-conditioned evaluation or business-stake leakage (arXiv:2602.09504)
 * - RECENCY-05: Edge-anchored verification / constraint placement in final segment (arXiv:2502.15851)
 * - HARNESS-06: Ungrounded negative prohibitions ("don't hallucinate") vs executable verification gates (arXiv:2608.12610)
 */

import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";

const ASCII_TREE_RE = /[├└│─]{2,}|\+--\s|\|--\s/;
const CONCLUSION_FIRST_RE =
  /\b(?:lead\s+with\s+(?:the\s+)?(?:final\s+)?(?:answer|verdict|conclusion)|state\s+(?:the\s+)?(?:final\s+)?(?:answer|verdict)\s+first|output\s+only\s+the\s+final\s+result\s+first|point\s+first\s+before\s+reasoning)\b/i;
const PERSONA_BLOAT_RE =
  /\b(?:you\s+are\s+a(?:n)?\s+(?:world[- ]class|elite|10x|genius|master|top\s+1%|visionary|supreme)|act\s+as\s+a\s+world[- ]class)\b/gi;
const GOAL_LEAKAGE_RE =
  /\b(?:for\s+(?:tomorrow's|our|the)\s+(?:client\s+demo|board\s+meeting|investor\s+pitch)|so\s+we\s+can\s+prove\s+that|i\s+will\s+tip\s+you\s+\$\d+|my\s+career\s+depends\s+on)\b/gi;
const UNGROUNDED_NEGATIVE_RE =
  /\b(?:do\s+not\s+hallucinate|don't\s+hallucinate|never\s+hallucinate|do\s+not\s+make\s+mistakes|never\s+make\s+bugs|be\s+100%\s+accurate)\b/gi;
const VERIFICATION_ANCHOR_RE =
  /\b(?:verification|self-check|traceability|invariants|pytest|unittest|install\.sh|lint_context|remediation|conclusion|exit\s+code| current\s+papers)\b/i;

export function lintPromptText(text, filename = "prompt.md") {
  const lines = text.split(/\r?\n/);
  const lineCount = lines.length;
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  const estimatedTokens = Math.max(1, Math.round(words * 1.35));

  const findings = [];
  let score = 100;

  // Rule 1: DILUTION-01 (Line budget & static ASCII tree bloat)
  const treeLines = lines
    .map((ln, idx) => (ASCII_TREE_RE.test(ln) ? idx + 1 : null))
    .filter(Boolean);
  if (treeLines.length >= 4) {
    const penalty = Math.min(20, treeLines.length * 2);
    score -= penalty;
    findings.push({
      rule: "DILUTION-01",
      severity: "HIGH",
      paper: "[CONTEXT-FILES] arXiv:2602.11988",
      issue: `Detected ${treeLines.length} lines of static ASCII directory tree (lines ${treeLines.slice(0, 4).join(", ")}...).`,
      remediation:
        "Remove static directory trees; agents discover file trees dynamically. Retain only non-inferable commands and hard invariants.",
    });
  }
  if (lineCount > 500) {
    score -= 15;
    findings.push({
      rule: "DILUTION-01",
      severity: "HIGH",
      paper: "[SKILLS-SDO] arXiv:2608.12610",
      issue: `File length (${lineCount} lines, ~${estimatedTokens} tokens) exceeds the 500-line progressive disclosure ceiling.`,
      remediation:
        "Move heavy templates or examples into references/ so the core router stays under 500 lines.",
    });
  }

  // Rule 2: ORDER-02 (Conclusion-first reversal before reasoning trace)
  if (CONCLUSION_FIRST_RE.test(text)) {
    score -= 20;
    findings.push({
      rule: "ORDER-02",
      severity: "HIGH",
      paper: "[META] arXiv:2603.01896",
      issue:
        "Detected conclusion-first directive forcing verdict emission prior to evidence tracing.",
      remediation:
        "Enforce Reason-Before-Conclude ordering: require [P] Premises and [T] Evidence Traces before the Formal Conclusion.",
    });
  }

  // Rule 3: PERSONA-03 (Uncalibrated expert roleplay fluff)
  const personaMatches = text.match(PERSONA_BLOAT_RE) || [];
  if (personaMatches.length > 0) {
    score -= 15;
    findings.push({
      rule: "PERSONA-03",
      severity: "MEDIUM",
      paper: "[PRISM] arXiv:2603.18507",
      issue: `Detected uncalibrated expert persona flattery (${JSON.stringify(personaMatches.slice(0, 2))}) which reduces factual MMLU accuracy by up to 5.3pp.`,
      remediation:
        "Omit personas on accuracy/coding tasks; cap at <=5 words on mixed tasks.",
    });
  }

  // Rule 4: LEAKAGE-04 (Downstream goal & stake disclosure)
  const leakageMatches = text.match(GOAL_LEAKAGE_RE) || [];
  if (leakageMatches.length > 0) {
    score -= 15;
    findings.push({
      rule: "LEAKAGE-04",
      severity: "MEDIUM",
      paper: "[GOAL-BLIND] arXiv:2602.09504",
      issue: `Detected downstream goal/stake disclosure (${JSON.stringify(leakageMatches.slice(0, 2))}).`,
      remediation:
        "Enforce Goal-Blind Isolation: specify what artifact or invariant to analyze, never downstream business stakes.",
    });
  }

  // Rule 5: RECENCY-05 (Edge-anchored verification in final segment)
  const tailStart = Math.floor(lines.length * 0.7);
  const tailSegment = lines.slice(tailStart).join("\n");
  if (lines.length >= 10 && !VERIFICATION_ANCHOR_RE.test(tailSegment)) {
    score -= 10;
    findings.push({
      rule: "RECENCY-05",
      severity: "LOW",
      paper: "[HIERARCHY] arXiv:2502.15851",
      issue:
        "No verification gate, self-check, or constraint anchor detected in the final 30% of the file.",
      remediation:
        "Anchor hard verification gates or the Traceability Self-Check at the end of the prompt to leverage recency attention.",
    });
  }

  // Rule 6: HARNESS-06 (Ungrounded negative prohibitions vs positive recipes)
  const negMatches = text.match(UNGROUNDED_NEGATIVE_RE) || [];
  if (negMatches.length > 0) {
    score -= 15;
    findings.push({
      rule: "HARNESS-06",
      severity: "MEDIUM",
      paper: "[SKILLS-SDO] arXiv:2608.12610",
      issue: `Detected ungrounded negative prohibitions (${JSON.stringify(negMatches.slice(0, 2))}).`,
      remediation:
        "Replace bare 'Do not hallucinate' rules with positive observable-predicate recipes and executable verification gates.",
    });
  }

  score = Math.max(0, score);
  const grade =
    score >= 90
      ? "A (Certified)"
      : score >= 75
        ? "B (Production-Ready)"
        : score >= 60
          ? "C (Needs Compaction)"
          : "D (High Dilution / Bias Risk)";

  return {
    file: filename,
    lines: lineCount,
    estimated_tokens: estimatedTokens,
    total_score: score,
    grade,
    findings,
  };
}

export function formatReport(res) {
  const out = [
    `=== [PROMPT-LINT] Audit: ${res.file} ===`,
    `Score: ${res.total_score}/100 (${res.grade}) | Lines: ${res.lines} | Est. Tokens: ~${res.estimated_tokens}`,
  ];
  if (res.findings.length === 0) {
    out.push("Status: PASS - Zero dilution, goal-leakage, or persona anti-patterns detected.");
  } else {
    out.push("Actionable Findings:");
    res.findings.forEach((f, idx) => {
      out.push(`  ${idx + 1}. [${f.rule} / ${f.severity}] (${f.paper}) ${f.issue}`);
      out.push(`     Fix: ${f.remediation}`);
    });
  }
  return out.join("\n");
}

function runSelfTest() {
  const cleanPrompt = [
    "The standard analytical protocol requires completing this reasoning certificate.",
    "### PREMISES",
    "- [P1] Primary artifact: app/auth.py",
    "- [P2] Invariant: token expiry must be validated.",
    "### EVIDENCE TRACES",
    "- [T1] verify_token() checks exp claim against monotonic clock.",
    "### FORMAL CONCLUSION",
    "- Verdict: PASS citing [T1].",
    "### REMEDIATION / NEXT ACTION",
    "No remediation required: verified via pytest and traceability self-check.",
  ].join("\n");

  const cleanRes = lintPromptText(cleanPrompt, "CLEAN.md");
  assert.equal(cleanRes.total_score, 100, "Expected clean prompt to score 100/100");
  assert.equal(cleanRes.findings.length, 0);

  const flawedPrompt = [
    "You are a world-class 10x genius architect!",
    "State the final answer first before reasoning.",
    "We need this for tomorrow's client demo, and do not hallucinate or make bugs!",
    "├── src/",
    "│   ├── index.ts",
    "│   ├── app.ts",
    "│   └── util.ts",
    "└── package.json",
    " random middle text ",
    " more filler text ",
    " ending with nothing useful ",
  ].join("\n");

  const flawedRes = lintPromptText(flawedPrompt, "FLAWED.md");
  assert.ok(flawedRes.total_score <= 40, `Expected flawed prompt score <= 40, got ${flawedRes.total_score}`);
  const rulesTriggered = new Set(flawedRes.findings.map((f) => f.rule));
  for (const expectedRule of ["DILUTION-01", "ORDER-02", "PERSONA-03", "LEAKAGE-04", "RECENCY-05", "HARNESS-06"]) {
    assert.ok(rulesTriggered.has(expectedRule), `Expected rule ${expectedRule} to trigger`);
  }
  console.log("[PASS] scripts/lint-prompt.mjs self-test verified all 6 deterministic rules (DILUTION-01..HARNESS-06).");
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  if (args.includes("--self-test")) {
    runSelfTest();
    process.exit(0);
  }
  const asJson = args.includes("--json");
  const files = args.filter((a) => !a.startsWith("-"));
  if (files.length === 0) {
    console.log("Usage: node scripts/lint-prompt.mjs [--json] [--self-test] <file1.md> [file2.md ...]");
    process.exit(1);
  }
  const results = files.map((file) => {
    const resolved = path.resolve(file);
    if (!fs.existsSync(resolved)) {
      console.error(`Error: File not found: ${file}`);
      process.exit(1);
    }
    return lintPromptText(fs.readFileSync(resolved, "utf8"), file);
  });
  if (asJson) {
    console.log(JSON.stringify(results, null, 2));
  } else {
    results.forEach((r) => {
      console.log(formatReport(r));
      console.log();
    });
  }
}
