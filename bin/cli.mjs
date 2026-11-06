#!/usr/bin/env node
/**
 * Zero-Dependency Universal CLI for make-prompt-better
 *
 * Commands:
 *   node bin/cli.mjs init [options]     Install skill across local coding agents
 *   node bin/cli.mjs lint <files...>    Run the heuristic prompt & context linter
 *   node bin/cli.mjs --version          Print version
 *   node bin/cli.mjs --help             Show usage
 */

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { lintPromptText, formatReport, parseLintArgs } from "../scripts/lint-prompt.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, "..");
const { version } = JSON.parse(fs.readFileSync(path.join(ROOT_DIR, "package.json"), "utf8"));

function printHelp() {
  console.log(`make-prompt-better v${version} - Clearer prompts with requirement checks

Usage:
  node bin/cli.mjs init [options]         Install or update the skill in your coding agent
  node bin/cli.mjs lint [--json] [--fail-on-findings] [--] <file>
                                             Run heuristic checks; scores are not certification

Install Options (passed to install.sh):
  -s, --symlink                 Symlink skill folders for automatic git pull updates
  -c, --copy                    Copy skill files into target directories (default)
  -r, --runtime <target>        Target: all, claude, gemini, antigravity, codex, cursor, qwen
  -p, --project                 Install into current project workspace (.claude, .cursor, .agents)
  -g, --global                  Install into global user home directories (default)
  -u, --uninstall               Remove installed make-prompt-better skill files
  -n, --dry-run                 Preview actions without modifying files
      --check                   Check installation files and duplicate entries
  -h, --help                    Show this help message`);
}

const args = process.argv.slice(2);

if (args.length === 0) {
  printHelp();
  process.exit(0);
}

if (args.length === 1 && (args[0] === "-v" || args[0] === "--version")) {
  console.log(version);
  process.exit(0);
}

if (args[0] === "init" || args[0] === "install" || args[0].startsWith("-")) {
  if (args.includes("-h") || args.includes("--help")) {
    printHelp();
    process.exit(0);
  }
  const passArgs = args[0] === "init" || args[0] === "install" ? args.slice(1) : args;
  const installScript = path.join(ROOT_DIR, "install.sh");
  const res = spawnSync("bash", [installScript, ...passArgs], { stdio: "inherit" });
  if (res.error) console.error(`Error: Could not start bash: ${res.error.message}`);
  if (res.signal) console.error(`Error: Installer terminated by signal ${res.signal}`);
  process.exit(res.status ?? 1);
}

if (args[0] === "lint") {
  const subArgs = args.slice(1);
  let parsed;
  try {
    parsed = parseLintArgs(subArgs);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
  if (parsed.selfTest) {
    const linterScript = path.join(ROOT_DIR, "scripts", "lint-prompt.mjs");
    const res = spawnSync(process.execPath, [linterScript, "--self-test"], { stdio: "inherit" });
    if (res.error) console.error(`Error: Could not start linter: ${res.error.message}`);
    process.exit(res.status ?? 1);
  }
  const { asJson, failOnFindings, files } = parsed;
  if (files.length === 0) {
    console.error("Usage: node bin/cli.mjs lint [--json] [--fail-on-findings] [--] <file...>");
    process.exit(1);
  }
  const results = files.map((file) => {
    const resolved = path.resolve(file);
    if (!fs.existsSync(resolved)) {
      console.error(`Error: File not found: ${file}`);
      process.exit(1);
    }
    try {
      return lintPromptText(fs.readFileSync(resolved, "utf8"), file);
    } catch (error) {
      console.error(`Error: Cannot read ${file}: ${error.message}`);
      process.exit(1);
    }
  });
  if (asJson) {
    console.log(JSON.stringify(results, null, 2));
  } else {
    results.forEach((r) => {
      console.log(formatReport(r));
      console.log();
    });
  }
  process.exit(failOnFindings && results.some((result) => result.findings.length > 0) ? 1 : 0);
}

printHelp();
process.exit(1);
