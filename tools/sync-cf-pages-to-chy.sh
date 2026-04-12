#!/bin/bash
# Sync cf-pages-deploy to Chy's Docker container volume on Witness VPS
# Runs every 10 minutes via cron
# The container's /home/aiciv maps to /var/lib/docker/volumes/vol-aiciv-13/_data on host
rsync -az --delete --exclude='.git' --exclude='node_modules' --exclude='.wrangler' \
  /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ \
  root@37.27.237.109:/var/lib/docker/volumes/vol-aiciv-13/_data/shared/cf-pages-deploy/ 2>/dev/null
