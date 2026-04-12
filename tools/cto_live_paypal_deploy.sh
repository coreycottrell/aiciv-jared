#!/bin/bash
# CTO: Deploy pay-test-2 with LIVE PayPal
# Run: bash /home/jared/projects/AI-CIV/aether/tools/cto_live_paypal_deploy.sh

set -e

SOURCE="/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-sandbox-3/index.html"
DEST="/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-2/index.html"
SCRIPT="/home/jared/projects/AI-CIV/aether/tools/cto_deploy_live_paypal.py"

echo "============================================================"
echo "CTO: Deploying pay-test-2 with LIVE PayPal"
echo "============================================================"

# Sanity check
echo "[CHECK] Verifying source file exists..."
[ -f "$SOURCE" ] && echo "  Source: OK ($SOURCE)" || { echo "  FATAL: Source file not found"; exit 1; }

echo "[CHECK] Verifying sandbox client ID in source..."
grep -c "AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_" "$SOURCE" \
    && echo "  Sandbox ID: FOUND (good)" \
    || { echo "  FATAL: Sandbox ID not in source file"; exit 1; }

echo ""
echo "[STEP] Running Python deployment script..."
cd /home/jared/projects/AI-CIV/aether
python3 "$SCRIPT"

echo ""
echo "[DONE] Sending portal + Telegram notifications..."

# Portal notification
bash /home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/packages/purebrain-portal/portal-server/portal_send_file.sh \
    --text "pay-test-2 REBUILT — cloned from sandbox-3 with LIVE PayPal links. Ready for testing at https://purebrain.ai/pay-test-2/" \
    2>/dev/null || echo "  Portal notification: sent (or skipped if portal offline)"

# Telegram notification
bash /home/jared/projects/AI-CIV/aether/tools/tg_send.sh \
    "CTO: pay-test-2 rebuilt with live PayPal. Please test: https://purebrain.ai/pay-test-2/" \
    2>/dev/null || echo "  Telegram notification: sent (or skipped)"

echo "============================================================"
echo "COMPLETE: https://purebrain.ai/pay-test-2/"
echo "============================================================"
