#!/bin/bash

# Comprehensive audit: which pages are serving identical content to homepage?
# Created: 2026-04-17

HOMEPAGE_HASH="81861857d88ba389091c7e8b7da1d174"
OUTPUT_FILE="/home/jared/projects/AI-CIV/aether/exports/portal-files/FULL-PAGE-VS-HOMEPAGE-AUDIT-2026-04-17.md"

# Initialize output file
cat > "$OUTPUT_FILE" << 'EOF'
# Complete Page vs Homepage Audit
**Date**: 2026-04-17
**Homepage Hash**: 81861857d88ba389091c7e8b7da1d174

## Executive Summary
Checking ALL pages on purebrain.ai against homepage to identify broken pages serving WordPress fallback.

---

EOF

echo "Starting comprehensive audit..."
echo ""

# Arrays to store results
declare -a BROKEN_PAGES
declare -a WORKING_PAGES
declare -a NO_LOCAL_FILE

# Get all directories in cf-pages-deploy
cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/

for dir in */; do
    # Remove trailing slash
    path="${dir%/}"

    # Skip if path is empty or just a dot
    [[ "$path" == "." || -z "$path" ]] && continue

    # Construct URL
    url="https://purebrain.ai/${path}/"

    echo "Checking: $url"

    # Get live page hash
    live_hash=$(curl -s "$url" | md5sum | awk '{print $1}')

    # Get title from live page
    live_title=$(curl -s "$url" | grep -oP '<title>\K[^<]+' | head -1)

    # Check if local file exists
    local_file="${path}/index.html"

    if [ -f "$local_file" ]; then
        # Get local title
        local_title=$(grep -oP '<title>\K[^<]+' "$local_file" | head -1)

        # Compare hashes
        if [ "$live_hash" == "$HOMEPAGE_HASH" ]; then
            BROKEN_PAGES+=("$path|$local_title")
            echo "  ❌ BROKEN (serving homepage)"
        else
            WORKING_PAGES+=("$path|$live_title")
            echo "  ✅ Working"
        fi
    else
        NO_LOCAL_FILE+=("$path|$live_title")
        echo "  📝 No local file (WordPress-managed?)"
    fi

    # Rate limiting
    sleep 0.5
done

# Write BROKEN section
echo "" >> "$OUTPUT_FILE"
echo "## BROKEN PAGES (Serving Homepage)" >> "$OUTPUT_FILE"
echo "**Count**: ${#BROKEN_PAGES[@]}" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| Path | Local Title (What It Should Be) | Has Local File |" >> "$OUTPUT_FILE"
echo "|------|----------------------------------|----------------|" >> "$OUTPUT_FILE"

for entry in "${BROKEN_PAGES[@]}"; do
    IFS='|' read -r path title <<< "$entry"
    echo "| /$path/ | $title | ✅ YES |" >> "$OUTPUT_FILE"
done

# Write WORKING section
echo "" >> "$OUTPUT_FILE"
echo "## WORKING PAGES (Unique Content)" >> "$OUTPUT_FILE"
echo "**Count**: ${#WORKING_PAGES[@]}" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| Path | Live Title |" >> "$OUTPUT_FILE"
echo "|------|-----------|" >> "$OUTPUT_FILE"

for entry in "${WORKING_PAGES[@]}"; do
    IFS='|' read -r path title <<< "$entry"
    echo "| /$path/ | $title |" >> "$OUTPUT_FILE"
done

# Write NO LOCAL FILE section
echo "" >> "$OUTPUT_FILE"
echo "## NO LOCAL FILE (WordPress-Managed)" >> "$OUTPUT_FILE"
echo "**Count**: ${#NO_LOCAL_FILE[@]}" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| Path | Live Title |" >> "$OUTPUT_FILE"
echo "|------|-----------|" >> "$OUTPUT_FILE"

for entry in "${NO_LOCAL_FILE[@]}"; do
    IFS='|' read -r path title <<< "$entry"
    echo "| /$path/ | $title |" >> "$OUTPUT_FILE"
done

# Summary
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "## Summary Statistics" >> "$OUTPUT_FILE"
echo "- **Total Directories**: $(ls -d */ | wc -l)" >> "$OUTPUT_FILE"
echo "- **Broken (Homepage Fallback)**: ${#BROKEN_PAGES[@]}" >> "$OUTPUT_FILE"
echo "- **Working (Unique Content)**: ${#WORKING_PAGES[@]}" >> "$OUTPUT_FILE"
echo "- **No Local File**: ${#NO_LOCAL_FILE[@]}" >> "$OUTPUT_FILE"

echo ""
echo "Audit complete! Results written to:"
echo "$OUTPUT_FILE"
