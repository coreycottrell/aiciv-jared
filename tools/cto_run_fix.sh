#!/bin/bash
set -e
source /home/jared/projects/AI-CIV/aether/.env
cd /home/jared/projects/AI-CIV/aether
echo "Running CTO pricing fix script..."
python3 tools/cto_pricing_fix_v2.py 2>&1 | tee /home/jared/projects/AI-CIV/aether/exports/cto-pricing-fix/run-log.txt
echo ""
echo "Done. Check exports/cto-pricing-fix/run-log.txt for full output."
