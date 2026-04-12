#!/bin/bash
# Deploy Sales Call Wizard to WordPress
set -e

WP_USER="Aether"
WP_APP_PASSWORD="ZGuh 1W8k WpWM c9iy kqyd buPr"
WP_BASE="https://purebrain.ai/wp-json/wp/v2"
HTML_FILE="/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html"

echo "Deploying Sales Call Wizard to WordPress..."

# Run Python deploy script
python3 /home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/wp_deploy.py

echo "Deploy complete."
