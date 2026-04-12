#!/bin/bash
cd /home/jared/projects/AI-CIV/aether
python3 tools/execute_pricing_688.py 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    bash tools/tg_send.sh "CTO Team: Pricing tiers updated on pay-test-sandbox-2. 5 tiers -> 4 tiers. Awakened \$149 (MOST POPULAR), Partnered \$499, Unified \$999, Enterprise Custom. Strikethrough pricing + footnote added. PayPal sandbox buttons preserved. Please review at https://purebrain.ai/pay-test-sandbox-2"
else
    bash tools/tg_send.sh "CTO Team: Pricing deploy on page 688 completed but some checks failed. Review terminal output."
fi

exit $EXIT_CODE
