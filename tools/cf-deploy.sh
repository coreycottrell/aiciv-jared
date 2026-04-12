#!/usr/bin/env bash
# CF Pages Direct File Deploy - Shell wrapper
# Usage: ./tools/cf-deploy.sh blog/new-post/index.html blog/new-post/banner.png
# Usage: ./tools/cf-deploy.sh investor-avatar/
# Usage: ./tools/cf-deploy.sh --dry-run blog/new-post/index.html

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/cf-deploy.py" "$@"
