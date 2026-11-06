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
CHECK=false
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
  -u, --uninstall           Remove the selected installation and duplicate skill entries
  -b, --backup              Allow replacement/removal of an unmanaged Cursor rule (with backup)
                            Existing skill targets are always backed up before replacement
  -n, --dry-run             Print actions that would be taken without modifying files
      --check               Check selected installations and duplicates without changing files
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
    --check)       CHECK=true; shift ;;
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

if [[ "${CHECK}" == true && ( "${UNINSTALL}" == true || "${DRY_RUN}" == true ) ]]; then
  echo "Error: Use --check separately from --uninstall and --dry-run" >&2
  exit 1
fi

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
STATE_DIR="${BASE_DIR}/.make-prompt-better"
BACKUP_ROOT="${STATE_DIR}/backups"

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
      TARGETS+=("${BASE_DIR}/.agents/skills/make-prompt-better")
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
  for rt in codex claude qwen gemini antigravity cursor; do
    add_targets_for_runtime "${rt}"
  done
else
  add_targets_for_runtime "${RUNTIME}"
fi

# Refuse symlinked ancestors instead of following a project-controlled redirect.
check_parent_path() {
  local destination="$1" relative component current
  relative="${destination#${BASE_DIR}/}"
  current="${BASE_DIR}"
  while [[ "${relative}" == */* ]]; do
    component="${relative%%/*}"
    current="${current}/${component}"
    if [[ -L "${current}" ]]; then
      echo "Error: Refusing symlinked destination parent: ${current}" >&2
      return 1
    fi
    relative="${relative#*/}"
  done
}

backup_existing() {
  local destination="$1" receipt
  check_parent_path "${BACKUP_ROOT}/receipt"
  mkdir -p "${BACKUP_ROOT}"
  receipt="$(mktemp -d "${BACKUP_ROOT}/$(basename "${destination}").XXXXXXXX")"
  printf '%s\n' "${destination}" > "${receipt}/original-path.txt"
  mv "${destination}" "${receipt}/payload"
  echo "Recovery copy -> ${receipt}/payload (original path in original-path.txt)"
}

# Only frontmatter identity qualifies a sibling for migration. Similar folder
# names and unrelated skills are left alone. Recovery copies live outside every
# supported skill/rule discovery root, including on uninstall.
is_this_skill() {
  [[ -f "$1/SKILL.md" ]] || return 1
  awk 'NR==1 {if ($0 != "---") exit; next} /^---$/ {exit} {print}' "$1/SKILL.md" |
    grep -Eq "^name:[[:space:]]*(make-prompt-better|\"make-prompt-better\"|'make-prompt-better')[[:space:]]*$"
}

refuse_source() {
  if [[ -d "$1" && ! -L "$1" && "$(cd "$1" && pwd -P)" == "$(cd "${SKILL_SRC}" && pwd -P)" ]]; then
    echo "Error: Target is the source directory: $1" >&2
    return 1
  fi
}

DUPLICATES=()
find_duplicates() {
  local canonical="$1" root candidate
  local roots=("$(dirname "${canonical}")")
  if [[ "${canonical}" == "${BASE_DIR}/.agents/skills/make-prompt-better" ]]; then
    roots+=("${BASE_DIR}/.codex/skills")
  fi
  DUPLICATES=()
  for root in "${roots[@]}"; do
    check_parent_path "${root}/entry"
    for candidate in "${root}"/* "${root}"/.[!.]* "${root}"/..?*; do
      [[ "${candidate}" != "${canonical}" ]] || continue
      if is_this_skill "${candidate}"; then
        refuse_source "${candidate}"
        DUPLICATES+=("${candidate}")
      fi
    done
  done
}

retire_duplicates() {
  local canonical="$1" duplicate
  find_duplicates "${canonical}"
  for duplicate in ${DUPLICATES[@]+"${DUPLICATES[@]}"}; do
    backup_existing "${duplicate}"
    echo "Removed duplicate entry -> ${duplicate}"
  done
}

is_current() {
  local destination="$1"
  if [[ "${MODE}" == "copy" && -d "${destination}" && ! -L "${destination}" ]]; then
    diff -qr "${SKILL_SRC}" "${destination}" >/dev/null 2>&1
  elif [[ "${MODE}" == "symlink" && -L "${destination}" ]]; then
    [[ "$(readlink "${destination}")" == "${SKILL_SRC}" ]]
  else
    return 1
  fi
}

generate_cursor_rule() {
  echo "---"
  sed -n '2,/^---$/p' "${SKILL_SRC}/SKILL.md" | sed -n '/^description: /p'
  echo "globs:"
  echo "alwaysApply: false"
  echo "---"
  echo ""
  echo "<!-- Managed by make-prompt-better installer -->"
  awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "${SKILL_SRC}/SKILL.md"
}

CURSOR_RULE="${BASE_DIR}/.cursor/rules/make-prompt-better.mdc"
CURSOR_SELECTED=false
validate_cursor_rule() {
  check_parent_path "${CURSOR_RULE}"
  if [[ -L "${CURSOR_RULE}" ]]; then
    echo "Error: Refusing symlinked Cursor rule: ${CURSOR_RULE}" >&2
    return 1
  fi
  if [[ -e "${CURSOR_RULE}" ]] && ! grep -q '^<!-- Managed by make-prompt-better installer -->$' "${CURSOR_RULE}" && [[ "${BACKUP}" != true ]]; then
    echo "Error: Unmanaged Cursor rule; use --backup to preserve and replace it: ${CURSOR_RULE}" >&2
    return 1
  fi
}
if [[ "${RUNTIME}" == "cursor" || ( "${RUNTIME}" == "all" && ( "${SCOPE}" == "project" || "${INSTALL_ALL}" == true || -d "${BASE_DIR}/.cursor" ) ) ]]; then
  CURSOR_SELECTED=true
  validate_cursor_rule
fi

installed_count=0
skipped_count=0
unchanged_count=0
check_failures=0
stage_dir=""
lock_dir=""
cursor_lock=""
legacy_lock=""
cleanup() {
  if [[ -n "${stage_dir}" && -d "${stage_dir}" ]]; then rm -rf "${stage_dir}"; fi
  if [[ -n "${lock_dir}" && -d "${lock_dir}" ]]; then rmdir "${lock_dir}"; fi
  if [[ -n "${cursor_lock}" && -d "${cursor_lock}" ]]; then rmdir "${cursor_lock}"; fi
  if [[ -n "${legacy_lock}" && -d "${legacy_lock}" ]]; then rmdir "${legacy_lock}"; fi
}
trap cleanup EXIT

check_parent_path "${BACKUP_ROOT}/receipt"

# Coordinate migration with older installers that lock the legacy Codex target.
if [[ ( "${RUNTIME}" == "all" || "${RUNTIME}" == "codex" ) && -d "${BASE_DIR}/.codex/skills" && "${DRY_RUN}" != true && "${CHECK}" != true ]]; then
  check_parent_path "${BASE_DIR}/.codex/skills/entry"
  legacy_lock="${BASE_DIR}/.codex/skills/make-prompt-better.lock"
  if ! mkdir "${legacy_lock}"; then
    legacy_lock=""
    echo "Error: Legacy Codex installation is locked" >&2
    exit 1
  fi
fi

if [[ "${CURSOR_SELECTED}" == true && "${DRY_RUN}" != true && "${CHECK}" != true ]]; then
  mkdir -p "$(dirname "${CURSOR_RULE}")"
  validate_cursor_rule
  cursor_lock="${CURSOR_RULE}.lock"
  if ! mkdir "${cursor_lock}"; then
    cursor_lock=""
    echo "Error: Cursor rule is locked: ${CURSOR_RULE}" >&2
    exit 1
  fi
  validate_cursor_rule
fi

for target in "${TARGETS[@]}"; do
  rel_from_base="${target#${BASE_DIR}/}"
  agent_root="${BASE_DIR}/${rel_from_base%%/*}"
  parent_dir="$(dirname "${target}")"
  check_parent_path "${target}"

  if [[ "${UNINSTALL}" != true && "${SCOPE}" == "global" && "${RUNTIME}" == "all" && "${agent_root}" != "${BASE_DIR}/.agents" && "${INSTALL_ALL}" == false && ! -d "${agent_root}" ]]; then
    skipped_count=$((skipped_count + 1))
    continue
  fi
  refuse_source "${target}"
  find_duplicates "${target}"
  if [[ "${CHECK}" == true ]]; then
    if is_current "${target}"; then
      echo "Current -> ${target}"
    else
      echo "Missing or different from this checkout -> ${target}"
      check_failures=$((check_failures + 1))
    fi
    for duplicate in ${DUPLICATES[@]+"${DUPLICATES[@]}"}; do
      echo "Duplicate -> ${duplicate}"
      check_failures=$((check_failures + 1))
    done
    continue
  fi
  if [[ "${UNINSTALL}" == true && ! -e "${target}" && ! -L "${target}" && ${#DUPLICATES[@]} -eq 0 ]]; then
    skipped_count=$((skipped_count + 1))
    continue
  fi
  if [[ "${DRY_RUN}" == true ]]; then
    if [[ "${UNINSTALL}" != true && "${BACKUP}" != true ]] && is_current "${target}"; then
      echo "[DRY-RUN] Already current -> ${target}"
    else
      echo "[DRY-RUN] Would $([[ "${UNINSTALL}" == true ]] && echo uninstall || echo "install (${MODE})") -> ${target} (existing target retained as backup)"
    fi
    for duplicate in ${DUPLICATES[@]+"${DUPLICATES[@]}"}; do
      echo "[DRY-RUN] Would remove duplicate entry -> ${duplicate} (recovery under ${BACKUP_ROOT})"
    done
    installed_count=$((installed_count + 1))
    continue
  fi
  mkdir -p "${parent_dir}"
  check_parent_path "${target}"
  lock_dir="${target}.lock"
  if ! mkdir "${lock_dir}"; then
    lock_dir=""
    echo "Error: Installation target is locked: ${target}" >&2
    exit 1
  fi
  if [[ "${UNINSTALL}" != true && "${BACKUP}" != true ]] && is_current "${target}"; then
    echo "Already current -> ${target}"
    retire_duplicates "${target}"
    rmdir "${lock_dir}"
    lock_dir=""
    installed_count=$((installed_count + 1))
    unchanged_count=$((unchanged_count + 1))
    continue
  fi
  if [[ "${UNINSTALL}" != true ]]; then
    mkdir -p "${STATE_DIR}"
    stage_dir="$(mktemp -d "${STATE_DIR}/.make-prompt-better.stage.XXXXXXXX")"
    if [[ "${MODE}" == "symlink" ]]; then
      ln -s "${SKILL_SRC}" "${stage_dir}/skill"
    else
      cp -R "${SKILL_SRC}" "${stage_dir}/skill"
      [[ -f "${stage_dir}/skill/SKILL.md" ]] || { echo "Error: Staged skill is incomplete" >&2; exit 1; }
    fi
  fi
  if [[ -e "${target}" || -L "${target}" ]]; then backup_existing "${target}"; fi
  if [[ "${UNINSTALL}" != true ]]; then
    mv "${stage_dir}/skill" "${target}"
    echo "Installed make-prompt-better ${VERSION} -> ${target}"
    rmdir "${stage_dir}"
    stage_dir=""
  else
    echo "Uninstalled -> ${target}"
  fi
  retire_duplicates "${target}"
  rmdir "${lock_dir}"
  lock_dir=""
  installed_count=$((installed_count + 1))
done

if [[ "${CURSOR_SELECTED}" == true ]]; then
  if [[ "${CHECK}" == true ]]; then
    if [[ -f "${CURSOR_RULE}" ]] && generate_cursor_rule | cmp -s - "${CURSOR_RULE}"; then
      echo "Current -> ${CURSOR_RULE}"
    else
      echo "Missing or different from this checkout -> ${CURSOR_RULE}"
      check_failures=$((check_failures + 1))
    fi
  elif [[ "${DRY_RUN}" == true ]]; then
    if [[ "${UNINSTALL}" != true && "${BACKUP}" != true && -f "${CURSOR_RULE}" ]] && generate_cursor_rule | cmp -s - "${CURSOR_RULE}"; then
      echo "[DRY-RUN] Cursor rule already current -> ${CURSOR_RULE}"
    else
      echo "[DRY-RUN] Would $([[ "${UNINSTALL}" == true ]] && echo remove || echo update) Cursor rule -> ${CURSOR_RULE}"
    fi
  else
    mkdir -p "$(dirname "${CURSOR_RULE}")"
    validate_cursor_rule
    if [[ "${UNINSTALL}" != true ]]; then
      stage_dir="$(mktemp -d "$(dirname "${CURSOR_RULE}")/.make-prompt-better.stage.XXXXXXXX")"
      generate_cursor_rule > "${stage_dir}/rule"
    fi
    if [[ "${UNINSTALL}" != true && "${BACKUP}" != true && -f "${CURSOR_RULE}" ]] && cmp -s "${stage_dir}/rule" "${CURSOR_RULE}"; then
      rm "${stage_dir}/rule"
      rmdir "${stage_dir}"
      stage_dir=""
      echo "Cursor rule already current -> ${CURSOR_RULE}"
    else
      if [[ -e "${CURSOR_RULE}" ]]; then backup_existing "${CURSOR_RULE}"; fi
      if [[ "${UNINSTALL}" != true ]]; then
        mv "${stage_dir}/rule" "${CURSOR_RULE}"
        rmdir "${stage_dir}"
        stage_dir=""
        echo "Generated Cursor rule -> ${CURSOR_RULE}"
      fi
    fi
  fi
fi

if [[ "${CHECK}" == true ]]; then
  if [[ "${check_failures}" -gt 0 ]]; then
    echo "Check found ${check_failures} issue(s). Re-run the installer for the same runtime and scope to repair."
    exit 1
  fi
  echo "Check passed. Selected installations match this checkout; no duplicate entries in the checked roots."
elif [[ "${DRY_RUN}" == true ]]; then
  echo "Done. Previewed ${installed_count} target(s); no files changed."
elif [[ "${UNINSTALL}" == true ]]; then
  echo "Done. Uninstalled from ${installed_count} target(s)."
else
  echo "Done. Processed (${MODE}) ${installed_count} agent target(s) (${unchanged_count} already current; ${skipped_count} unconfigured agent roots skipped; pass --all to force all)."
fi
