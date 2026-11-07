#!/usr/bin/env python3
"""Check the public release surfaces without network access or dependencies."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


version = json.loads(read("package.json"))["version"]
assert re.fullmatch(r"\d+\.\d+\.\d+", version), version
assert json.loads(read(".claude-plugin/plugin.json"))["version"] == version
assert json.loads(read(".claude-plugin/marketplace.json"))["plugins"][0]["version"] == version
assert f'version = "{version}"' in read("pyproject.toml")
assert f"version: {version}\n" in read("CITATION.cff")
assert f'VERSION="v{version}"' in read("install.sh")
assert f"## [{version}]" in read("CHANGELOG.md")
assert f"releases/tag/v{version}" in read("README.md")
for guide in ("README.md", "docs/quickstart.md"):
    assert f"git clone --branch v{version} --depth 1" in read(guide)
assert f"git fetch --depth 1 origin tag v{version}" in read("docs/installation.md")
assert f"git switch --detach v{version}" in read("docs/installation.md")
assert f"# Make Prompt Better (v{version})" in read("make-prompt-better/SKILL.md")
assert f"[COMPILER RECEIPT // make-prompt-better v{version}]" in read("make-prompt-better/SKILL.md")
assert f"Agent Operating Contract (v{version})" in read("AGENTS.md")
assert f"skill (`v{version}`)" in read("CLAUDE.md")
assert f"skill (v{version})" in read("make-prompt-better/references/domain-templates.md")
assert f'"version": "{version}"' in read("research/benchmark/v4/run_ollama_benchmarks.py")
cli_version = subprocess.check_output(
    ["node", "bin/cli.mjs", "--version"], cwd=ROOT, text=True
).strip()
assert cli_version == version, (cli_version, version)
print(f"[PASS] Release metadata and CLI agree on v{version}")
