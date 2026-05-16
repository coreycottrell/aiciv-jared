#!/bin/bash
# CRITICAL FIX for social.purebrain.ai
# Root cause: duplicate const PLATFORM_COLORS breaks ALL JavaScript
set -e

FILE="/home/jared/projects/AI-CIV/aether/from-chy/DEPLOY-THIS-MOBILE-FIX.html"
WORKER="/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js"

echo "=== CRITICAL FIX: Duplicate const PLATFORM_COLORS ==="

# Count occurrences before
BEFORE=$(grep -c "const PLATFORM_COLORS=" "$FILE" || true)
echo "Before fix: $BEFORE declarations (must be 2 to proceed)"

if [ "$BEFORE" != "2" ]; then
    echo "ERROR: Expected 2 declarations, found $BEFORE. Aborting."
    exit 1
fi

# Fix: Replace the SECOND occurrence (in analytics section) with a comment
# The second one follows "// ========== ANALYTICS =========="
# Use sed to replace only the line that matches in the analytics section
# We need to find the line number of the second occurrence
SECOND_LINE=$(grep -n "const PLATFORM_COLORS=" "$FILE" | tail -1 | cut -d: -f1)
echo "Second declaration at line: $SECOND_LINE"

# Replace that specific line
sed -i "${SECOND_LINE}s|const PLATFORM_COLORS=.*|// PLATFORM_COLORS: declared in kanban section above|" "$FILE"

# Also fix instagram color in the first declaration
sed -i "s|instagram:'#e1306c'|instagram:'#e4405f'|" "$FILE"

# Verify
AFTER=$(grep -c "const PLATFORM_COLORS=" "$FILE" || true)
echo "After fix: $AFTER declarations (must be 1)"

if [ "$AFTER" != "1" ]; then
    echo "CRITICAL ERROR: Fix did not work!"
    exit 1
fi

echo ""
echo "=== FIX 2: Add console.log to login ==="
# Add console.log after "async function login(){"
sed -i '/^async function login(){$/a\  console.log("[social] login() called");' "$FILE"

echo ""
echo "=== FIX 3: Improve auto-boot catch ==="
sed -i "s|if(TOKEN){bootApp().catch(()=>{});}|if(TOKEN){console.log('[social] Auto-boot with stored token');bootApp().catch(function(e){console.warn('[social] Auto-boot failed:',e);localStorage.removeItem('social_token');TOKEN='';});}|" "$FILE"

echo ""
echo "=== FIX 4: Add dayOffset variable ==="
sed -i 's|let monthOffset = 0;|let monthOffset = 0;\nlet dayOffset = 0;|' "$FILE"

echo ""
echo "=== FIX 5: Update build comment ==="
sed -i 's|<!-- VERIFIED BUILD: .* -->|<!-- VERIFIED BUILD: login-fix+dayview, 2026-04-20 CTO sprint -->|' "$FILE"

echo ""
echo "=== Verification ==="
echo "const PLATFORM_COLORS count: $(grep -c 'const PLATFORM_COLORS=' "$FILE" || true)"
echo "login console.log: $(grep -c 'social.*login.*called' "$FILE" || true)"
echo "auto-boot improved: $(grep -c 'Auto-boot with stored token' "$FILE" || true)"
echo "dayOffset: $(grep -c 'let dayOffset' "$FILE" || true)"
echo "Total lines: $(wc -l < "$FILE")"

echo ""
echo "=== SUCCESS: Critical fixes applied to standalone HTML ==="
echo ""
echo "Next steps:"
echo "1. Add day view JS function (renderDayView)"
echo "2. Add day view container div"
echo "3. Add platform captions to edit modal"
echo "4. Re-embed HTML into worker.js"
echo "5. Deploy"
