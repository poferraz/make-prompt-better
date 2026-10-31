#!/usr/bin/env bash
set -euo pipefail

VERSION="v4.2.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="${SCRIPT_DIR}/make-prompt-better"

MODE="copy"
INSTALL_ALL=false
BACKUP=false
DRY_RUN=false

usage() {
  cat <<EOF
Usage: ./install.sh [OPTIONS]

Syncs make-prompt-better (${VERSION}) across local AI coding agent skill directories.

Options:
  -s, --symlink   Create symbolic links to this repo instead of copying files
                  (recommended so 'git pull' updates all agents automatically)
  -c, --copy      Copy skill files into target directories (default)
  -a, --all       Create and populate all supported agent directories even if
                  the parent agent folder (~/.claude, ~/.qwen, etc.) does not exist
  -b, --backup    Backup any existing non-symlink skill folder before replacing
  -n, --dry-run   Print actions that would be taken without modifying files
  -h, --help      Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--symlink) MODE="symlink"; shift ;;
    -c|--copy)    MODE="copy"; shift ;;
    -a|--all)     INSTALL_ALL=true; shift ;;
    -b|--backup)  BACKUP=true; shift ;;
    -n|--dry-run) DRY_RUN=true; shift ;;
    -h|--help)    usage; exit 0 ;;
    *)
      echo "Error: Unknown option '$1'" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -f "${SKILL_SRC}/SKILL.md" ]]; then
  echo "Error: Cannot find ${SKILL_SRC}/SKILL.md" >&2
  exit 1
fi

TARGETS=(
  "${HOME}/.agents/skills/make-prompt-better"
  "${HOME}/.claude/skills/make-prompt-better"
  "${HOME}/.qwen/skills/make-prompt-better"
  "${HOME}/.gemini/skills/make-prompt-better"
  "${HOME}/.gemini/config/skills/make-prompt-better"
  "${HOME}/.gemini/antigravity/skills/make-prompt-better"
)

installed_count=0
skipped_count=0

for target in "${TARGETS[@]}"; do
  # Extract agent root directory (e.g., ~/.claude, ~/.qwen, ~/.gemini)
  rel_from_home="${target#${HOME}/}"
  agent_root="${HOME}/${rel_from_home%%/*}"
  parent_dir="$(dirname "${target}")"

  # Always install into ~/.agents; for others, require agent_root to exist unless --all
  if [[ "${agent_root}" != "${HOME}/.agents" && "${INSTALL_ALL}" == false && ! -d "${agent_root}" ]]; then
    skipped_count=$((skipped_count + 1))
    continue
  fi

  if [[ "${DRY_RUN}" == true ]]; then
    echo "[DRY-RUN] Would install (${MODE}) make-prompt-better ${VERSION} -> ${target}"
    installed_count=$((installed_count + 1))
    continue
  fi

  mkdir -p "${parent_dir}"

  if [[ -e "${target}" && ! -L "${target}" && "${BACKUP}" == true ]]; then
    backup_path="${target}.bak.$(date +%Y%m%d%H%M%S)"
    mv "${target}" "${backup_path}"
    echo "Backed up existing directory -> ${backup_path}"
  else
    rm -rf "${target}"
  fi

  if [[ "${MODE}" == "symlink" ]]; then
    ln -sfn "${SKILL_SRC}" "${target}"
    echo "Linked make-prompt-better ${VERSION} -> ${target}"
  else
    cp -R "${SKILL_SRC}" "${target}"
    echo "Copied make-prompt-better ${VERSION} -> ${target}"
  fi
  installed_count=$((installed_count + 1))
done

echo "Done. Synced (${MODE}) across ${installed_count} agent directory(s) (${skipped_count} unconfigured agent roots skipped; pass --all to force all)."
