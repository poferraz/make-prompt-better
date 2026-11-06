#!/usr/bin/env node
/**
 * Zero-Dependency Universal CLI for make-prompt-better
 *
 * Commands:
 *   node bin/cli.mjs                    Guided installation in a terminal
 *   node bin/cli.mjs install [options]  Install the skill
 *   node bin/cli.mjs check [options]    Check the installation
 *   node bin/cli.mjs update [options]   Update from this checkout or package
 *   node bin/cli.mjs uninstall [options] Remove the installation with recovery
 *   node bin/cli.mjs init [options]     Legacy installer alias
 *   node bin/cli.mjs lint <files...>    Run the heuristic prompt & context linter
 *   node bin/cli.mjs --version          Print version
 *   node bin/cli.mjs --help             Show usage
 */

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";
import { lintPromptText, formatReport, parseLintArgs } from "../scripts/lint-prompt.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, "..");
const { version } = JSON.parse(fs.readFileSync(path.join(ROOT_DIR, "package.json"), "utf8"));

function printHelp() {
  console.log(`make-prompt-better v${version} - Clearer prompts with requirement checks

Usage:
  npx make-prompt-better                     Guided installation and verification
  npx make-prompt-better install [options]   Install the skill in your coding agent
  npx make-prompt-better check [options]     Check the selected installation
  npx make-prompt-better update [options]    Update from this checkout or package
  npx make-prompt-better uninstall [options] Remove the installation with a recovery backup
  npx make-prompt-better init [options]      Legacy installer alias
  npx make-prompt-better lint [--json] [--fail-on-findings] [--] <file>
                                            Run heuristic checks; scores are not certification

Install Options (passed to install.sh):
  -s, --symlink                 Link installed skill to this source directory
  -c, --copy                    Copy skill files into target directories (default)
  -r, --runtime <target>        Target: all, claude, gemini, antigravity, codex, cursor, qwen
  -p, --project                 Install into current project workspace (.claude, .cursor, .agents)
  -g, --global                  Install into global user home directories (default)
  -u, --uninstall               Remove installed make-prompt-better skill files
  -b, --backup                  Allow replacement or removal of an unmanaged Cursor rule
  -a, --all                     Include unconfigured global agent directories
  -n, --dry-run                 Preview actions without modifying files
      --check                   Check installation files and duplicate entries
  -h, --help                    Show this help message

Installation notes:
  Requires Bash; use WSL on Windows.
  With no arguments in a terminal, choose an agent and scope; installation is checked afterward.
  With redirected input or output, no arguments shows help without installing.
  Installing the npm package alone does not activate the skill; run the CLI to install it.
  Copy mode keeps the skill independent of an npm installation or npx cache.
  Update uses the version of this checkout or package; it does not fetch a newer version.
  For check, update, and uninstall in scripts, specify --runtime and --project or --global.
  Install and init retain the installer's existing noninteractive defaults.
  Public package installation needs no publisher token.`);
}

const runtimes = ["codex", "claude", "cursor", "gemini", "antigravity", "qwen", "all"];
const runtimeNames = { codex: "Codex", claude: "Claude Code", cursor: "Cursor", gemini: "Gemini CLI",
  antigravity: "Antigravity", qwen: "Qwen", all: "All supported agents" };

function detectedRuntimes() {
  const roots = [process.cwd(), os.homedir()];
  const folders = { claude: ".claude", gemini: ".gemini",
                    codex: ".agents", cursor: ".cursor", qwen: ".qwen" };
  const found = Object.entries(folders)
    .filter(([, folder]) => roots.some((root) => fs.existsSync(path.join(root, folder))))
    .map(([runtime]) => runtime);
  if (fs.existsSync(path.join(process.cwd(), ".agent")) ||
      fs.existsSync(path.join(os.homedir(), ".gemini", "antigravity"))) found.push("antigravity");
  return found;
}

async function chooseMissing(passArgs, needsRuntime, needsScope) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: false });
  const lines = rl[Symbol.asyncIterator]();
  async function choose(label, allowed, names) {
    console.log(label);
    allowed.forEach((value, index) => console.log(`  ${index + 1}. ${names[value]} (${value})`));
    while (true) {
      process.stdout.write("Choose a number or name (q to cancel): ");
      const { value, done } = await lines.next();
      if (done || value.trim().toLowerCase() === "q") return null;
      const answer = value.trim().toLowerCase();
      if (allowed.includes(answer)) return answer;
      if (/^[1-9]$/.test(answer) && Number(answer) <= allowed.length) return allowed[Number(answer) - 1];
      console.error(`Choose ${allowed.join(", ")} or q to cancel.`);
    }
  }
  try {
    if (needsRuntime) {
      const found = detectedRuntimes();
      if (found.length) console.log(`Detected host directories: ${found.join(", ")}`);
      const runtime = await choose("Runtime: which coding agent do you use?", runtimes, runtimeNames);
      if (!runtime) return false;
      passArgs.push("--runtime", runtime);
    }
    if (needsScope) {
      const scope = await choose("Scope: where should the skill be available?", ["project", "global"], {
        project: `This project: ${process.cwd()}`, global: `Your user account: ${os.homedir()}`,
      });
      if (!scope) return false;
      passArgs.push(`--${scope}`);
    }
    return true;
  } finally {
    rl.close();
  }
}

const args = process.argv.slice(2);
const interactive = Boolean(process.stdin.isTTY && process.stdout.isTTY);
const guided = args.length === 0 && interactive;

if (args.length === 0) {
  if (!guided) {
    printHelp();
    process.exit(0);
  }
  console.log(`make-prompt-better v${version}\nChoose your agent and scope. We will install a copy and verify its files.\n`);
  args.push("install");
}

if (args.length === 1 && (args[0] === "-v" || args[0] === "--version")) {
  console.log(version);
  process.exit(0);
}

if (["init", "install", "check", "update", "uninstall"].includes(args[0]) || args[0].startsWith("-")) {
  if (args.includes("-h") || args.includes("--help")) {
    printHelp();
    process.exit(0);
  }
  const command = args[0];
  const named = ["init", "install", "check", "update", "uninstall"].includes(command);
  const passArgs = named ? args.slice(1) : args;
  const wrapper = ["check", "update", "uninstall"].includes(command);
  if (wrapper) {
    const conflicting = command === "check" ? ["-u", "--uninstall"] :
      command === "uninstall" ? ["--check"] : ["-u", "--uninstall", "--check"];
    if (passArgs.some((arg) => conflicting.includes(arg))) {
      console.error(`Error: Conflicting installer operation for ${command}.`);
      process.exit(1);
    }
    if (passArgs.some((arg) => ["-p", "--project"].includes(arg)) &&
        passArgs.some((arg) => ["-g", "--global"].includes(arg))) {
      console.error("Error: Choose either project or global scope.");
      process.exit(1);
    }
    if (passArgs.filter((arg) => arg === "-r" || arg === "--runtime").length > 1) {
      console.error("Error: Specify only one runtime.");
      process.exit(1);
    }
    if (passArgs.some((arg) => ["-c", "--copy"].includes(arg)) &&
        passArgs.some((arg) => ["-s", "--symlink"].includes(arg))) {
      console.error("Error: Choose either copy or symlink mode.");
      process.exit(1);
    }
  }
  const runtimeIndex = passArgs.findIndex((arg) => arg === "-r" || arg === "--runtime");
  const hasRuntime = runtimeIndex !== -1;
  const hasScope = passArgs.some((arg) => ["-p", "--project", "-g", "--global"].includes(arg));
  if (hasRuntime && (!passArgs[runtimeIndex + 1] || passArgs[runtimeIndex + 1].startsWith("-"))) {
    console.error("Error: --runtime requires an argument.");
    process.exit(1);
  }
  if ((wrapper || command === "install") && interactive) {
    if (!await chooseMissing(passArgs, !hasRuntime, !hasScope)) {
      console.error("Installation operation cancelled; no files changed.");
      process.exit(1);
    }
  } else if (wrapper && (!hasRuntime || !hasScope)) {
    console.error("Error: Specify --runtime and either --project or --global for noninteractive use.");
    process.exit(1);
  }
  if (command === "check") passArgs.push("--check");
  if (command === "uninstall") passArgs.push("--uninstall");
  if (command === "update") console.log(`Updating from this checkout or package (v${version}); no version is fetched.`);
  const installScript = path.join(ROOT_DIR, "install.sh");
  function runInstaller(options) {
    const res = spawnSync("bash", [installScript, ...options], { stdio: "inherit" });
    if (res.error) console.error(`Error: Could not start bash: ${res.error.message}`);
    if (res.signal) console.error(`Error: Installer terminated by signal ${res.signal}`);
    return res.status ?? 1;
  }
  if (guided) passArgs.push("--copy");
  const status = runInstaller(passArgs);
  if (status !== 0 || !guided) process.exit(status);
  console.log("\nVerifying installation...");
  const checkStatus = runInstaller([...passArgs, "--check"]);
  if (checkStatus !== 0) {
    console.error("Installation verification failed. Re-run the installer for the same agent and scope to repair.");
    process.exit(checkStatus);
  }
  console.log("\nInstallation verified. Reload your coding agent to load the skill.");
  const selectedRuntime = passArgs[passArgs.indexOf("--runtime") + 1];
  console.log(selectedRuntime === "codex"
    ? "In Codex, type $make-prompt-better and add the request you want to improve."
    : "Select make-prompt-better in your agent and add the request you want to improve.");
  process.exit(0);
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
