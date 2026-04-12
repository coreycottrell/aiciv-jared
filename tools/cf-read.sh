#!/usr/bin/env bash
# Read a file directly from the live CF Pages site
# Usage: ./tools/cf-read.sh investor-avatar/index.html
# Usage: ./tools/cf-read.sh blog/index.html

if [ -z "$1" ]; then
    echo "Usage: $0 <path>"
    echo "Example: $0 investor-avatar/index.html"
    exit 1
fi

PATH_CLEAN=$(echo "$1" | sed 's|^/||')
curl -s "https://purebrain.ai/${PATH_CLEAN}"
