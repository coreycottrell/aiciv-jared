#!/usr/bin/env bash
# List files at a path on CF Pages (from the deployment manifest)
# Usage: ./tools/cf-list.sh                  # List all files
# Usage: ./tools/cf-list.sh blog/            # List files under /blog/
# Usage: ./tools/cf-list.sh investor-avatar  # List files under /investor-avatar/

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$1" ]; then
    python3 "${SCRIPT_DIR}/cf-deploy.py" --list
else
    python3 "${SCRIPT_DIR}/cf-deploy.py" --list-path "$1"
fi
