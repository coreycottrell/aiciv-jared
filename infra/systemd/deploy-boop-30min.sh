#!/bin/bash
# =============================================================================
# deploy-boop-30min.sh - Install aether-boop-30min systemd timer+service
#
# Workstream A bridge: bypasses the boop_executor.py 2/2 concurrency cap by
# giving the 30min BOOP group (engineering-flow-check, delegation-enforcer,
# telegram-health-boop) its own systemd timer.
#
# Pre-flight gates:
#   1. git status --porcelain infra/systemd/ must be EMPTY
#      (per feedback_wrangler_deploy_must_be_preceded_by_git_commit.md)
#   2. Backup directory creation must succeed
#      (per feedback_execute_authority_greenlit_tasks.md)
#
# Usage: bash infra/systemd/deploy-boop-30min.sh
# =============================================================================

set -euo pipefail

REPO_ROOT="/home/jared/projects/AI-CIV/aether"
UNIT_DIR="$REPO_ROOT/infra/systemd"
SYSTEMD_DIR="/etc/systemd/system"
BACKUP_DIR="$HOME/backups/systemd-pre-bridge-fix-2026-05-16"

echo "=============================================="
echo "Aether BOOP 30min Bridge — Deploy"
echo "=============================================="

cd "$REPO_ROOT"

# -----------------------------------------------------------------------------
# Gate 1: clean working tree in infra/systemd/
# -----------------------------------------------------------------------------
echo "[gate-1] Checking git working tree for infra/systemd/ ..."
DIRTY=$(git status --porcelain infra/systemd/ || true)
if [[ -n "$DIRTY" ]]; then
    echo "[FAIL] Working tree dirty in infra/systemd/:"
    echo "$DIRTY"
    echo "Commit or stash these changes before deploying."
    exit 2
fi
echo "[gate-1] OK — working tree clean for infra/systemd/"

# -----------------------------------------------------------------------------
# Gate 2: backup current aether-* systemd state
# -----------------------------------------------------------------------------
echo "[gate-2] Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR" || { echo "[FAIL] Could not create backup dir"; exit 3; }

BACKUP_FILE="$BACKUP_DIR/state-pre.txt"
{
    echo "# Aether systemd state — pre bridge-fix"
    echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# Operator: $(whoami)@$(hostname)"
    echo ""
    echo "## ls /etc/systemd/system/aether-*"
    ls -la /etc/systemd/system/aether-* 2>/dev/null || echo "(none)"
    echo ""
    echo "## systemctl list-timers aether-* (active)"
    systemctl list-timers 'aether-*' --all 2>/dev/null || true
    echo ""
    echo "## systemctl status aether-boop-executor.service (head)"
    systemctl status aether-boop-executor.service --no-pager 2>/dev/null | head -20 || true
} > "$BACKUP_FILE"
echo "[gate-2] OK — backup written: $BACKUP_FILE"

# -----------------------------------------------------------------------------
# Sanity: source unit files exist & are valid
# -----------------------------------------------------------------------------
SERVICE_SRC="$UNIT_DIR/aether-boop-30min.service"
TIMER_SRC="$UNIT_DIR/aether-boop-30min.timer"

for f in "$SERVICE_SRC" "$TIMER_SRC"; do
    if [[ ! -f "$f" ]]; then
        echo "[FAIL] Missing unit file: $f"
        exit 4
    fi
done
echo "[sanity] Unit files found."

# -----------------------------------------------------------------------------
# Sanity: ensure runner script + log dir are present
# -----------------------------------------------------------------------------
RUNNER="$REPO_ROOT/tools/boop_group_runner.sh"
if [[ ! -x "$RUNNER" ]]; then
    echo "[FAIL] Runner not executable: $RUNNER"
    exit 5
fi
mkdir -p "$REPO_ROOT/logs/boops"
echo "[sanity] Runner executable & log dir ready."

# -----------------------------------------------------------------------------
# Install (additive only — never modifies existing units)
# -----------------------------------------------------------------------------
echo "[install] sudo cp $SERVICE_SRC $SYSTEMD_DIR/"
sudo cp "$SERVICE_SRC" "$SYSTEMD_DIR/aether-boop-30min.service"

echo "[install] sudo cp $TIMER_SRC $SYSTEMD_DIR/"
sudo cp "$TIMER_SRC" "$SYSTEMD_DIR/aether-boop-30min.timer"

echo "[install] sudo systemctl daemon-reload"
sudo systemctl daemon-reload

echo "[install] sudo systemctl enable --now aether-boop-30min.timer"
sudo systemctl enable --now aether-boop-30min.timer

# -----------------------------------------------------------------------------
# Verification print
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "systemctl status aether-boop-30min.timer"
echo "=============================================="
sudo systemctl status aether-boop-30min.timer --no-pager || true

echo ""
echo "=============================================="
echo "systemctl list-timers aether-boop-30min.timer"
echo "=============================================="
systemctl list-timers aether-boop-30min.timer --all --no-pager || true

echo ""
echo "[done] aether-boop-30min.timer installed & enabled."
echo "[done] Backup at: $BACKUP_FILE"
echo "[done] Rollback script: $UNIT_DIR/rollback-boop-30min.sh"
