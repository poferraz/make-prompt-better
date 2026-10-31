#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="${SCRIPT_DIR}/make-prompt-better"

TARGETS=(
  "${HOME}/.agents/skills/make-prompt-better"
  "${HOME}/.claude/skills/make-prompt-better"
  "${HOME}/.qwen/skills/make-prompt-better"
  "${HOME}/.gemini/skills/make-prompt-better"
  "${HOME}/.gemini/config/skills/make-prompt-better"
  "${HOME}/.gemini/antigravity/skills/make-prompt-better"
)

for target in "${TARGETS[@]}"; do
  parent_dir="$(dirname "${target}")"
  mkdir -p "${parent_dir}"
  rm -rf "${target}"
  cp -R "${SKILL_SRC}" "${target}"
  echo "Installed make-prompt-better v4.1.0 -> ${target}"
done

echo "Done. Universal skill synced across ~/.agents, ~/.claude, ~/.qwen, and ~/.gemini skill directories."
