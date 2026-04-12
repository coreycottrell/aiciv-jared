#!/bin/bash
# Install VPS Health Monitor as a systemd timer (every 5 minutes)
# Run as root or with sudo: sudo ./tools/install-vps-monitor.sh
#
# What this installs:
#   - aether-vps-monitor.service  (the worker unit)
#   - aether-vps-monitor.timer    (fires every 5 min)
#   - Both enabled and started immediately

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CIV_ROOT="$(dirname "$SCRIPT_DIR")"
HEALTH_SCRIPT="$SCRIPT_DIR/vps-health.sh"
LOG_FILE="$CIV_ROOT/logs/vps_health.log"

# Detect current user for the service
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" = "root" ]; then
    # If running as root, try to find the actual VPS user
    CURRENT_USER=$(stat -c '%U' "$CIV_ROOT" 2>/dev/null || echo "root")
fi

echo "Installing VPS Health Monitor..."
echo "  Script: $HEALTH_SCRIPT"
echo "  Log:    $LOG_FILE"
echo "  User:   $CURRENT_USER"
echo ""

# Ensure scripts are executable
chmod +x "$SCRIPT_DIR/vps-health.sh"
chmod +x "$SCRIPT_DIR/vps-instance-tracker.sh"
chmod +x "$SCRIPT_DIR/vps-cleanup.sh"

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# ── systemd service unit ────────────────────────────────────────────────────
cat > /etc/systemd/system/aether-vps-monitor.service <<EOF
[Unit]
Description=Aether VPS Health Monitor
After=network.target

[Service]
Type=oneshot
User=$CURRENT_USER
WorkingDirectory=$CIV_ROOT
ExecStart=$HEALTH_SCRIPT --alert --quiet
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

[Install]
WantedBy=multi-user.target
EOF

# ── systemd timer unit ──────────────────────────────────────────────────────
cat > /etc/systemd/system/aether-vps-monitor.timer <<EOF
[Unit]
Description=Run Aether VPS Health Monitor every 5 minutes
Requires=aether-vps-monitor.service

[Timer]
OnBootSec=60
OnUnitActiveSec=5min
Unit=aether-vps-monitor.service

[Install]
WantedBy=timers.target
EOF

# ── Enable and start ────────────────────────────────────────────────────────
systemctl daemon-reload
systemctl enable aether-vps-monitor.timer
systemctl start aether-vps-monitor.timer

echo "Installation complete."
echo ""
systemctl status aether-vps-monitor.timer --no-pager

echo ""
echo "Timer installed. Fires every 5 minutes."
echo "To check status: systemctl status aether-vps-monitor.timer"
echo "To view logs:    tail -f $LOG_FILE"
echo "To run now:      systemctl start aether-vps-monitor.service"

# Run immediately to confirm it works
echo ""
echo "Running health check now..."
"$HEALTH_SCRIPT"
