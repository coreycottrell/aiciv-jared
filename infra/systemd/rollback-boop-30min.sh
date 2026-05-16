#!/bin/bash
# =============================================================================
# rollback-boop-30min.sh - Disable & remove aether-boop-30min units
#
# Use if the 45-min verification probe fails (no fresh
# inbox/engineering-flow-check-*.md after deploy).
#
# Does NOT touch boop_executor.py, runner scripts, or any other systemd unit.
# Additive-only rollback: removes ONLY the two units it installed.
# =============================================================================

set -euo pipefail

SYSTEMD_DIR="/etc/systemd/system"

echo "=============================================="
echo "Aether BOOP 30min Bridge — Rollback"
echo "=============================================="

echo "[rollback] sudo systemctl disable --now aether-boop-30min.timer"
sudo systemctl disable --now aether-boop-30min.timer || true

echo "[rollback] sudo systemctl stop aether-boop-30min.service"
sudo systemctl stop aether-boop-30min.service || true

if [[ -f "$SYSTEMD_DIR/aether-boop-30min.timer" ]]; then
    echo "[rollback] sudo rm $SYSTEMD_DIR/aether-boop-30min.timer"
    sudo rm "$SYSTEMD_DIR/aether-boop-30min.timer"
fi

if [[ -f "$SYSTEMD_DIR/aether-boop-30min.service" ]]; then
    echo "[rollback] sudo rm $SYSTEMD_DIR/aether-boop-30min.service"
    sudo rm "$SYSTEMD_DIR/aether-boop-30min.service"
fi

echo "[rollback] sudo systemctl daemon-reload"
sudo systemctl daemon-reload

echo ""
echo "[done] aether-boop-30min units removed."
echo "[done] boop_executor.py path remains untouched."
