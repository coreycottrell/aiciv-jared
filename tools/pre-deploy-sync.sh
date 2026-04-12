#!/bin/bash
# PRE-DEPLOY SYNC: Pull Chy's latest changes before deploying to CF Pages
# ALWAYS pulls Chy's owned directories so we deploy HER latest, not our stale copy

DEPLOY_DIR="/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy"
CHY_HOST="aiciv@37.27.237.109"
CHY_PORT="2213"

echo "[pre-deploy] Step 1: Pulling Chy's OWNED directories (investor-avatar, investor-tracking, gifts)..."

# ALWAYS pull her owned dirs to get her latest before we deploy
for dir in investor-avatar investor-tracking gifts; do
    rsync -avz --update -e "ssh -p ${CHY_PORT}" \
      "${CHY_HOST}:/home/aiciv/shared/cf-pages-deploy/${dir}/" "${DEPLOY_DIR}/${dir}/" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "[pre-deploy]   ${dir}: synced"
    else
        echo "[pre-deploy]   ${dir}: WARNING could not sync"
    fi
done

echo "[pre-deploy] Step 2: Pulling Chy's other shared changes (excluding her owned dirs)..."

# Pull any OTHER changes she made (non-owned dirs)
rsync -avz --update \
  --exclude=investor-avatar/ --exclude=investor-tracking/ --exclude=gifts/ \
  -e "ssh -p ${CHY_PORT}" \
  "${CHY_HOST}:/home/aiciv/shared/cf-pages-deploy/" "${DEPLOY_DIR}/" 2>/dev/null

echo "[pre-deploy] Ready to deploy (Chy's pages are current)"
