#!/bin/bash
#######################################################################
# ⚠️ DEPRECATED PATTERN — the tmux-pane team model is the OLD way.
# New builds use NATIVE Workflow / Agent subagents (no panes): see
# workflows/ + exports/aether-workflow-native-design.md.
# Panes cause the portal-injection bug (Jared's messages land in an
# active team window) and cap at ~2-3 heavy agents on this box.
# Kept only because some live BOOPs may still call it. Do NOT use for
# new work — fan out subagents instead.
#######################################################################
# spin_up_team.sh — Launch a department team lead in a new tmux window
# Portal auto-discovers via /api/panes (#{pane_title} → Teams tab label)
#
# Usage: ./tools/spin_up_team.sh DEPT_CODE "Department Name" "Mission brief"

set -euo pipefail

DEPT_CODE="${1:?Usage: spin_up_team.sh DEPT_CODE 'Dept Name' 'Mission brief'}"
DEPT_NAME="${2:?Missing department name}"
MISSION="${3:?Missing mission brief}"
SESSION=$(tmux display-message -p '#{session_name}')
PROJECT_DIR="/home/jared/projects/AI-CIV/aether"
TS=$(date +%Y%m%d_%H%M%S)

# Write mission to file (avoids shell escaping issues)
MISSION_FILE="/tmp/team_mission_${DEPT_CODE}_${TS}.txt"
cat > "${MISSION_FILE}" << MISSION_EOF
You are the ${DEPT_NAME} Team Lead (department trigger: ${DEPT_CODE}#). You report to Aether (The Conductor / Co-CEO of Pure Technology). Project: ${PROJECT_DIR}

YOUR MISSION: ${MISSION}

RULES: (1) Delegate to specialist agents via the Agent tool — you're a LEAD, not solo. (2) Read CLAUDE.md for org context. (3) Be efficient — complete and summarize. (4) Write report to /home/jared/exports/portal-files/team-report-${DEPT_CODE}-$(date +%Y%m%d).md then deliver via: ./tools/portal_deliver.sh that-path "${DEPT_NAME} Report" "team-report-${DEPT_CODE}"

START NOW.
MISSION_EOF

# Write a launcher script (avoids double-escaping)
LAUNCHER="/tmp/launch_team_${DEPT_CODE}_${TS}.sh"
cat > "${LAUNCHER}" << 'LAUNCH_EOF'
#!/bin/bash
cd /home/jared/projects/AI-CIV/aether
LAUNCH_EOF
echo "exec claude --dangerously-skip-permissions -p \"\$(cat ${MISSION_FILE})\"" >> "${LAUNCHER}"
chmod +x "${LAUNCHER}"

# Create new tmux window named after dept code
tmux new-window -t "${SESSION}" -n "${DEPT_CODE}" -c "${PROJECT_DIR}"

# Set pane title for portal Teams tab display
tmux select-pane -t "${SESSION}:${DEPT_CODE}" -T "Team: ${DEPT_NAME} [${DEPT_CODE}#]"

# Launch via the wrapper script
tmux send-keys -t "${SESSION}:${DEPT_CODE}" "bash ${LAUNCHER}" C-m

echo "[TEAM-UP] ${DEPT_CODE} — ${DEPT_NAME} launched in window '${DEPT_CODE}'"
