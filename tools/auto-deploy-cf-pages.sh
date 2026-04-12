#!/bin/bash
# CF Pages Auto-Deploy Script
# Owner: PTT (PureBrain Tech Team) under dept-systems-technology
# Created: 2026-03-18
# Purpose: Automate CF Pages deploy + cache flush after every site/blog change

set -e

PROJECT_ROOT="/home/jared/projects/AI-CIV/aether"
LOG_FILE="$PROJECT_ROOT/logs/cf-deploy.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DEPLOY_SOURCE="$PROJECT_ROOT/exports/cf-pages-deploy"
PROJECT_NAME="purebrain-staging"

echo "[$TIMESTAMP] CF Pages auto-deploy triggered" | tee -a "$LOG_FILE"

# Load CF Pages token from .env
CF_TOKEN=$(grep "^CF_PAGES_TOKEN=" "$PROJECT_ROOT/.env" | cut -d= -f2)

if [ -z "$CF_TOKEN" ]; then
  echo "[$TIMESTAMP] ERROR: CF_PAGES_TOKEN not found in .env" | tee -a "$LOG_FILE"
  exit 1
fi

# Load CF Zone ID for cache flush (optional — skip if not set)
CF_ZONE_ID=$(grep "^CF_ZONE_ID=" "$PROJECT_ROOT/.env" 2>/dev/null | cut -d= -f2)

echo "[$TIMESTAMP] Deploying $DEPLOY_SOURCE to $PROJECT_NAME..." | tee -a "$LOG_FILE"

# Deploy to CF Pages
cd "$PROJECT_ROOT"
CLOUDFLARE_API_TOKEN="$CF_TOKEN" npx wrangler pages deploy "$DEPLOY_SOURCE" \
  --project-name "$PROJECT_NAME" \
  --commit-dirty=true 2>&1 | tee -a "$LOG_FILE"

DEPLOY_EXIT=${PIPESTATUS[0]}

if [ "$DEPLOY_EXIT" -ne 0 ]; then
  echo "[$TIMESTAMP] ERROR: Deploy failed with exit code $DEPLOY_EXIT" | tee -a "$LOG_FILE"
  exit "$DEPLOY_EXIT"
fi

echo "[$TIMESTAMP] Deploy succeeded." | tee -a "$LOG_FILE"

# Flush CF cache after deploy (per feedback_cf_cache_flush_after_deploy.md)
if [ -n "$CF_ZONE_ID" ]; then
  echo "[$TIMESTAMP] Flushing Cloudflare cache for zone $CF_ZONE_ID..." | tee -a "$LOG_FILE"
  FLUSH_RESULT=$(curl -s -X POST \
    "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
    -H "Authorization: Bearer $CF_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"purge_everything":true}')
  echo "[$TIMESTAMP] Cache flush result: $FLUSH_RESULT" | tee -a "$LOG_FILE"
else
  echo "[$TIMESTAMP] CF_ZONE_ID not set in .env — skipping cache flush." | tee -a "$LOG_FILE"
fi

echo "[$TIMESTAMP] CF Pages auto-deploy complete." | tee -a "$LOG_FILE"
echo ""
echo "Deploy complete. Log: $LOG_FILE"
