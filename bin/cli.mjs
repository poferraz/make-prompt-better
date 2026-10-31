#!/usr/bin/env node
/**
 * Zero-Dependency Universal CLI for make-prompt-better (v4.2.0)
 *
 * Commands:
 *   npx make-prompt-better init [options]     Install skill across local coding agents
 *   npx make-prompt-better lint <files...>    Run deterministic 6-rule prompt & context linter
 *   npx make-prompt-better --version          Print version
 *   npx make-prompt-better --help             Show usage
 */

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { lintPromptText, formatReport } from "../scripts/lint-prompt.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, "..");

function printHelp() {
  console.log(`make-prompt-better v4.2.0 - Research-Grounded Prompt, Context & Harness Compiler

Usage:
  npx make-prompt-better [init] [options]       Sync skill to local AI coding agents
  npx make-prompt-better lint [--json] <file>   Audit prompt or CLAUDE.md/AGENTS.md (0-100 score)

Install Options (passed to install.sh):
  -s, --symlink                 Symlink skill folders for automatic git pull updates
  -c, --copy                    Copy skill files into target directories (default)
  -r, --runtime <target>        Target: all, claude, gemini, antigravity, codex, cursor, qwen
  -p, --project                 Install into current project workspace (.claude, .cursor, .agents)
  -g, --global                  Install into global user home directories (default)
  -u, --uninstall               Remove installed make-prompt-better skill files
  -n, --dry-run                 Preview actions without modifying files
  -h, --help                    Show this help message`);
}

const args = process.argv.slice(2);

if (args.includes("-v") || args.includes("--version")) {
  console.log("4.2.0");
  process.exit(0);
}

if (args.length === 0 || args[0] === "init" || args[0] === "install" || args[0].startsWith("-")) {
  if (args.includes("-h") || args.includes("--help")) {
    printHelp();
    process.exit(0);
  }
  const passArgs = args[0] === "init" || args[0] === "install" ? args.slice(1) : args;
  const installScript = path.join(ROOT_DIR, "install.sh");
  const res = spawnSync("bash", [installScript, ...passArgs], { stdio: "inherit" });
  process.exit(res.status ?? 0);
}

if (args[0] === "lint") {
  const subArgs = args.slice(1);
  if (subArgs.includes("--self-test")) {
    const linterScript = path.join(ROOT_DIR, "scripts", "lint-prompt.mjs");
    const res = spawnSync(process.execPath, [linterScript, "--self-test"], { stdio: "inherit" });
    process.exit(res.status ?? 0);
  }
  const asJson = subArgs.includes("--json");
  const files = subArgs.filter((a) => !a.startsWith("-"));
  if (files.length === 0) {
    console.error("Usage: npx make-prompt-better lint [--json] <file1.md> [file2.md ...]");
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
  process.exit(0);
}

printHelp();
process.exit(1);
