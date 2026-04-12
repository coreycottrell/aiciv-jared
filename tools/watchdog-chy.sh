#!/bin/bash
# Watchdog: Aether watches Chy
# Checks every 5 minutes if Chy's portal and Claude are running
# Auto-restarts if down

CHY_HOST="37.27.237.109"
CHY_PORT="2213"
CHY_USER="aiciv"
LOG="/home/jared/projects/AI-CIV/aether/logs/watchdog-chy.log"

check_and_fix() {
    local now=$(date '+%Y-%m-%d %H:%M:%S')

    # Check 1: Can we SSH in?
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes -p $CHY_PORT $CHY_USER@$CHY_HOST "echo ok" > /dev/null 2>&1; then
        echo "$now [FAIL] Cannot SSH to Chy container — container may be down" >> $LOG
        return 1
    fi

    # Check 2: Is portal server running?
    local portal_running=$(ssh -o ConnectTimeout=5 -p $CHY_PORT $CHY_USER@$CHY_HOST "ps aux | grep portal_server | grep -v grep | wc -l" 2>/dev/null)
    if [ "$portal_running" = "0" ]; then
        echo "$now [HEAL] Chy portal server DOWN — restarting" >> $LOG
        ssh -o ConnectTimeout=10 -p $CHY_PORT $CHY_USER@$CHY_HOST "
            tmux kill-session -t portal-server 2>/dev/null
            tmux new-session -d -s portal-server 'cd /home/aiciv/purebrain_portal && python3 portal_server.py'
        " 2>/dev/null
        echo "$now [HEAL] Chy portal server restarted" >> $LOG
    fi

    # Check 3: Is Claude running?
    local claude_running=$(ssh -o ConnectTimeout=5 -p $CHY_PORT $CHY_USER@$CHY_HOST "ps aux | grep 'claude' | grep -v grep | wc -l" 2>/dev/null)
    if [ "$claude_running" = "0" ]; then
        echo "$now [HEAL] Chy Claude DOWN — restarting with bypass flag" >> $LOG
        ssh -o ConnectTimeout=10 -p $CHY_PORT $CHY_USER@$CHY_HOST "
            tmux send-keys -t aiciv-primary 'claude --dangerously-skip-permissions' Enter 2>/dev/null || \
            tmux new-session -d -s chy-primary 'claude --dangerously-skip-permissions'
        " 2>/dev/null
        echo "$now [HEAL] Chy Claude restarted" >> $LOG
    fi

    # All good
    echo "$now [OK] Chy healthy — portal: running, claude: $claude_running instances" >> $LOG
}

check_and_fix
