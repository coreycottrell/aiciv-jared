#!/bin/bash
# Run the complete video fix deployment
# Usage: bash tools/run_video_fix.sh

cd /home/jared/projects/AI-CIV/aether

echo "=== PureBrain Video Fix - 2026-03-01 ==="
echo ""

# Load env
set -a
source .env
set +a

echo "Step 1: Building plugin v4.7.4..."
python3 tools/build_plugin_v474.py
echo ""

echo "Step 2: Running complete fix (plugin + Elementor)..."
python3 tools/deploy_video_fix_complete.py
echo ""

echo "Done. Check output above for PASS/FAIL status."
