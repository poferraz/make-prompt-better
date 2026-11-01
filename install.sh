#!/usr/bin/env bash
set -euo pipefail

VERSION="v4.3.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="${SCRIPT_DIR}/make-prompt-better"

MODE="copy"
INSTALL_ALL=false
BACKUP=false
DRY_RUN=false
UNINSTALL=false
SCOPE="global"
RUNTIME="all"

usage() {
  cat <<EOF
Usage: ./install.sh [OPTIONS]

Syncs make-prompt-better (${VERSION}) across local AI coding agent skill directories.

Options:
  -s, --symlink             Create symbolic links to this repo instead of copying files
                            (recommended so 'git pull' updates all agents automatically)
  -c, --copy                Copy skill files into target directories (default)
  -r, --runtime <runtime>   Filter target runtime: all, claude, gemini, antigravity,
                            codex, cursor, qwen (default: all)
  -p, --project             Install into current project directory (.claude, .cursor, etc.)
  -g, --global              Install into global user home directories (default)
  -a, --all                 Create and populate all supported agent directories even if
                            the parent agent folder (~/.claude, ~/.codex, etc.) does not exist
  -u, --uninstall           Remove installed make-prompt-better skill directories/links
  -b, --backup              Backup any existing non-symlink skill folder before replacing
  -n, --dry-run             Print actions that would be taken without modifying files
  -h, --help                Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--symlink)   MODE="symlink"; shift ;;
    -c|--copy)      MODE="copy"; shift ;;
    -r|--runtime)
      if [[ $# -lt 2 ]]; then
        echo "Error: --runtime requires an argument" >&2
        exit 1
      fi
      RUNTIME="$2"; shift 2 ;;
    -p|--project)   SCOPE="project"; shift ;;
    -g|--global)    SCOPE="global"; shift ;;
    -a|--all)       INSTALL_ALL=true; shift ;;
    -u|--uninstall) UNINSTALL=true; shift ;;
    -b|--backup)    BACKUP=true; shift ;;
    -n|--dry-run)   DRY_RUN=true; shift ;;
    -h|--help)      usage; exit 0 ;;
    *)
      echo "Error: Unknown option '$1'" >&2
      usage >&2
      exit 1
      ;;
  esac
done

case "${RUNTIME}" in
  all|claude|gemini|antigravity|codex|cursor|qwen) ;;
  *)
    echo "Error: Invalid --runtime '${RUNTIME}'. Choose from: all, claude, gemini, antigravity, codex, cursor, qwen" >&2
    exit 1
    ;;
esac

if [[ ! -f "${SKILL_SRC}/SKILL.md" ]]; then
  echo "Error: Cannot find ${SKILL_SRC}/SKILL.md" >&2
  exit 1
fi

BASE_DIR="${HOME}"
if [[ "${SCOPE}" == "project" ]]; then
  BASE_DIR="$(pwd)"
fi

TARGETS=()
add_targets_for_runtime() {
  local rt="$1"
  case "${rt}" in
    claude)
      TARGETS+=("${BASE_DIR}/.claude/skills/make-prompt-better")
      ;;
    gemini)
      TARGETS+=("${BASE_DIR}/.gemini/skills/make-prompt-better")
      if [[ "${SCOPE}" == "global" ]]; then
        TARGETS+=("${BASE_DIR}/.gemini/config/skills/make-prompt-better")
      fi
      ;;
    antigravity)
      if [[ "${SCOPE}" == "global" ]]; then
        TARGETS+=("${BASE_DIR}/.gemini/antigravity/skills/make-prompt-better")
      else
        TARGETS+=("${BASE_DIR}/.agent/skills/make-prompt-better")
      fi
      ;;
    codex)
      TARGETS+=("${BASE_DIR}/.codex/skills/make-prompt-better")
      ;;
    cursor)
      TARGETS+=("${BASE_DIR}/.cursor/skills/make-prompt-better")
      ;;
    qwen)
      TARGETS+=("${BASE_DIR}/.qwen/skills/make-prompt-better")
      ;;
  esac
}

if [[ "${RUNTIME}" == "all" ]]; then
  TARGETS+=("${BASE_DIR}/.agents/skills/make-prompt-better")
  for rt in claude qwen gemini antigravity codex cursor; do
    add_targets_for_runtime "${rt}"
  done
else
  add_targets_for_runtime "${RUNTIME}"
fi

write_cursor_mdc() {
  local mdc_dir="${BASE_DIR}/.cursor/rules"
  local mdc_file="${mdc_dir}/make-prompt-better.mdc"
  if [[ "${UNINSTALL}" == true ]]; then
    if [[ -e "${mdc_file}" || -L "${mdc_file}" ]]; then
      if [[ "${DRY_RUN}" == true ]]; then
        echo "[DRY-RUN] Would remove Cursor rule -> ${mdc_file}"
      else
        rm -f "${mdc_file}"
        echo "Removed Cursor rule -> ${mdc_file}"
      fi
    fi
    return
  fi

  if [[ "${DRY_RUN}" == true ]]; then
    echo "[DRY-RUN] Would generate Cursor .mdc rule -> ${mdc_file}"
    return
  fi

  mkdir -p "${mdc_dir}"
  {
    echo "---"
    sed -n '2,/^---$/p' "${SKILL_SRC}/SKILL.md" | sed -n '/^description: /p'
    echo "globs:"
    echo "alwaysApply: false"
    echo "---"
    echo ""
    awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "${SKILL_SRC}/SKILL.md"
  } > "${mdc_file}"
  echo "Generated Cursor YAML frontmatter rule -> ${mdc_file}"
}

installed_count=0
skipped_count=0

for target in "${TARGETS[@]}"; do
  rel_from_base="${target#${BASE_DIR}/}"
  agent_root="${BASE_DIR}/${rel_from_base%%/*}"
  parent_dir="$(dirname "${target}")"

  if [[ "${UNINSTALL}" == true ]]; then
    if [[ -e "${target}" || -L "${target}" ]]; then
      if [[ "${DRY_RUN}" == true ]]; then
        echo "[DRY-RUN] Would uninstall -> ${target}"
      else
        rm -rf "${target}"
        echo "Uninstalled -> ${target}"
      fi
      installed_count=$((installed_count + 1))
    else
      skipped_count=$((skipped_count + 1))
    fi
    continue
  fi

  # Always install into .agents or when explicitly targeting a single runtime or project scope;
  # for global 'all', require agent_root to exist unless --all is passed.
  if [[ "${SCOPE}" == "global" && "${RUNTIME}" == "all" && "${agent_root}" != "${BASE_DIR}/.agents" && "${INSTALL_ALL}" == false && ! -d "${agent_root}" ]]; then
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

# Emit .cursor/rules/make-prompt-better.mdc when targeting cursor explicitly or in project scope
if [[ "${RUNTIME}" == "cursor" || "${SCOPE}" == "project" || ( "${RUNTIME}" == "all" && ( "${INSTALL_ALL}" == true || -d "${BASE_DIR}/.cursor" ) ) ]]; then
  write_cursor_mdc
fi

if [[ "${UNINSTALL}" == true ]]; then
  echo "Done. Uninstalled from ${installed_count} target(s)."
else
  echo "Done. Synced (${MODE}) across ${installed_count} agent directory(s) (${skipped_count} unconfigured agent roots skipped; pass --all to force all)."
fi
