#!/bin/bash
# check-dual-source-parity.sh
#
# Constitutional drift-hardening for the CF Pages dual-source race condition.
# Per `feedback_dual_source_cf_pages_silent_overwrite.md`: every shared file
# MUST stay byte-identical across aether `exports/cf-pages-deploy/` AND the
# external `puretechnyc/purebrain-site/` repo. Drift in either causes the
# next external push (Lumen swap, investor gift page, pitch deck, etc.) to
# atomically regress production.
#
# This script:
#   1. Walks every path under AETHER that has a counterpart under EXTERNAL
#   2. md5-compares each pair
#   3. Reports drift (paths only — never file contents)
#   4. Exits 1 on ANY mismatch (suitable for pre-deploy hooks)
#
# Wired into:
#   - `tools/cf-deploy.py` pre-deploy hook (BLOCKS deploy if drift detected)
#   - Nightly cron via `aether-drift-watch.timer` (paging on Telegram if drift)
#
# Usage:
#   tools/check-dual-source-parity.sh                # default paths
#   tools/check-dual-source-parity.sh --verbose      # show every checked file
#   tools/check-dual-source-parity.sh --skip-missing # ignore files missing on one side
#   tools/check-dual-source-parity.sh --paths foo,bar  # only check these subpaths
#
# Exit codes:
#   0 = no drift detected
#   1 = drift detected (one or more files differ)
#   2 = configuration/environment error

set -u

AETHER_ROOT="${AETHER_ROOT:-/home/jared/projects/AI-CIV/aether}"
AETHER_CF_DIR="${AETHER_ROOT}/exports/cf-pages-deploy"
EXTERNAL_DIR="${EXTERNAL_DIR:-/home/jared/purebrain-site}"

VERBOSE=0
SKIP_MISSING=0
PATH_FILTER=""

while [ $# -gt 0 ]; do
  case "$1" in
    --verbose|-v) VERBOSE=1 ; shift ;;
    --skip-missing) SKIP_MISSING=1 ; shift ;;
    --paths) PATH_FILTER="$2" ; shift 2 ;;
    --help|-h)
      grep '^#' "$0" | sed 's/^# //; s/^#//'
      exit 0
      ;;
    *) echo "unknown arg: $1" ; exit 2 ;;
  esac
done

if [ ! -d "$AETHER_CF_DIR" ]; then
  echo "ERROR: aether cf-pages-deploy not found at $AETHER_CF_DIR" >&2
  exit 2
fi
if [ ! -d "$EXTERNAL_DIR" ]; then
  echo "ERROR: external purebrain-site not found at $EXTERNAL_DIR" >&2
  exit 2
fi

# Paths under aether that we KNOW are dual-source (cross-pushed by both).
# Empty default = check every file in aether that has a counterpart in external.
# Use --paths to override with a specific subset.
DEFAULT_SHARED_PATHS=(
  "admin/referrals/index.html"
  "admin/clients/index.html"
  "our-team/index.html"
  "user-guide/index.html"
  "blog"
  "insiders"
  "investor-onboarding"
  "investment-opportunity"
)

shopt -s nullglob globstar

declare -i CHECKED=0
declare -i MATCHED=0
declare -i DRIFTED=0
declare -i MISSING_AETHER=0
declare -i MISSING_EXTERNAL=0
declare -a DRIFT_PATHS=()
declare -a MISSING_EXTERNAL_PATHS=()
declare -a MISSING_AETHER_PATHS=()

# Build the set of relative paths to check.
RELATIVE_PATHS=()

if [ -n "$PATH_FILTER" ]; then
  IFS=',' read -ra USER_PATHS <<< "$PATH_FILTER"
  RELATIVE_PATHS=("${USER_PATHS[@]}")
else
  RELATIVE_PATHS=("${DEFAULT_SHARED_PATHS[@]}")
fi

check_file() {
  local rel="$1"
  local aether_file="${AETHER_CF_DIR}/${rel}"
  local external_file="${EXTERNAL_DIR}/${rel}"

  if [ ! -f "$aether_file" ] && [ ! -f "$external_file" ]; then
    return 0
  fi
  if [ ! -f "$aether_file" ]; then
    MISSING_AETHER=$((MISSING_AETHER + 1))
    MISSING_AETHER_PATHS+=("$rel")
    if [ "$SKIP_MISSING" -eq 0 ]; then
      [ "$VERBOSE" -eq 1 ] && echo "MISSING in aether: $rel"
    fi
    return 0
  fi
  if [ ! -f "$external_file" ]; then
    MISSING_EXTERNAL=$((MISSING_EXTERNAL + 1))
    MISSING_EXTERNAL_PATHS+=("$rel")
    if [ "$SKIP_MISSING" -eq 0 ]; then
      [ "$VERBOSE" -eq 1 ] && echo "MISSING in external: $rel"
    fi
    return 0
  fi

  local h1 h2
  h1=$(md5sum "$aether_file"   | awk '{print $1}')
  h2=$(md5sum "$external_file" | awk '{print $1}')
  CHECKED=$((CHECKED + 1))

  if [ "$h1" = "$h2" ]; then
    MATCHED=$((MATCHED + 1))
    [ "$VERBOSE" -eq 1 ] && echo "OK   ${rel}  (${h1})"
  else
    DRIFTED=$((DRIFTED + 1))
    DRIFT_PATHS+=("$rel")
    echo "DRIFT  ${rel}"
    echo "       aether   ${h1}"
    echo "       external ${h2}"
  fi
}

check_dir() {
  local rel="$1"
  local aether_dir="${AETHER_CF_DIR}/${rel}"
  local external_dir="${EXTERNAL_DIR}/${rel}"

  if [ ! -d "$aether_dir" ] && [ ! -d "$external_dir" ]; then
    return 0
  fi

  # Walk every regular file under the aether subdir.
  if [ -d "$aether_dir" ]; then
    while IFS= read -r -d '' f; do
      local sub="${f#${AETHER_CF_DIR}/}"
      check_file "$sub"
    done < <(find "$aether_dir" -type f -print0)
  fi

  # Walk files that exist in external but not in aether under this subdir.
  if [ -d "$external_dir" ]; then
    while IFS= read -r -d '' f; do
      local sub="${f#${EXTERNAL_DIR}/}"
      local aether_match="${AETHER_CF_DIR}/${sub}"
      if [ ! -f "$aether_match" ]; then
        MISSING_AETHER=$((MISSING_AETHER + 1))
        MISSING_AETHER_PATHS+=("$sub")
        [ "$VERBOSE" -eq 1 ] && [ "$SKIP_MISSING" -eq 0 ] && echo "MISSING in aether: $sub"
      fi
    done < <(find "$external_dir" -type f -print0)
  fi
}

for rel in "${RELATIVE_PATHS[@]}"; do
  if [ -d "${AETHER_CF_DIR}/${rel}" ] || [ -d "${EXTERNAL_DIR}/${rel}" ]; then
    check_dir "$rel"
  else
    check_file "$rel"
  fi
done

echo ""
echo "──────────────────────────────────────────────"
echo " Dual-source parity check"
echo " Aether:   ${AETHER_CF_DIR}"
echo " External: ${EXTERNAL_DIR}"
echo "──────────────────────────────────────────────"
echo " Checked:           ${CHECKED}"
echo " Matched:           ${MATCHED}"
echo " Drifted:           ${DRIFTED}"
echo " Missing in aether: ${MISSING_AETHER}"
echo " Missing in extern: ${MISSING_EXTERNAL}"
echo "──────────────────────────────────────────────"

if [ "$DRIFTED" -gt 0 ]; then
  echo "DRIFT DETECTED — ${DRIFTED} file(s) differ between aether and external:"
  for p in "${DRIFT_PATHS[@]}"; do echo "  - $p" ; done
  echo ""
  echo "Per feedback_dual_source_cf_pages_silent_overwrite.md, every shared path"
  echo "MUST stay byte-identical across both repos. Resolve by syncing the"
  echo "authoritative version (typically aether canonical) to the divergent side."
  exit 1
fi

if [ "$SKIP_MISSING" -eq 0 ] && [ "$MISSING_EXTERNAL" -gt 0 ]; then
  echo "WARNING: ${MISSING_EXTERNAL} file(s) exist in aether but not in external."
  echo "These will NOT be regressed by external pushes, but are not synced either."
  echo "Use --skip-missing to treat as non-blocking."
fi

echo "OK — no drift on ${CHECKED} checked file(s)."
exit 0
