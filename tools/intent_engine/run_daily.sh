#!/bin/bash
# Intent Engine Daily Run Script
# Scheduled to run at 8 AM EST via cron

# Set working directory
cd /home/jared/projects/AI-CIV/aether

# Activate virtual environment
source venv/bin/activate

# Log file
LOG_DIR="/home/jared/projects/AI-CIV/aether/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/intent_engine_$(date +%Y-%m-%d).log"

# Run the full pipeline
echo "========================================" >> "$LOG_FILE"
echo "Intent Engine Daily Run" >> "$LOG_FILE"
echo "Started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

python3 -m tools.intent_engine.main full >> "$LOG_FILE" 2>&1

echo "" >> "$LOG_FILE"
echo "Completed: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Keep only last 30 days of logs
find "$LOG_DIR" -name "intent_engine_*.log" -mtime +30 -delete
