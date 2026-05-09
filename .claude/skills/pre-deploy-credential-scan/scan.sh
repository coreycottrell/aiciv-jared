#!/usr/bin/env bash
# Pre-deploy credential scanner — blocks deploys with hardcoded creds in HTML/JS/TS.
# Usage: bash scan.sh [path-to-scan]  (defaults to exports/cf-pages-deploy and workers)
# Exit 0 = clean. Exit 1 = blocked (HIGH/CRITICAL hits found).

set -euo pipefail

SCAN_PATHS="${@:-exports/cf-pages-deploy workers}"
HIGH_HITS=0
CRITICAL_HITS=0

echo "Pre-deploy credential scan starting on: $SCAN_PATHS"

scan_pattern() {
  local pattern="$1"
  local label="$2"
  local severity="$3"
  local hits
  hits=$(grep -rEn --include="*.html" --include="*.js" --include="*.ts" \
    --exclude-dir=node_modules --exclude-dir=.git \
    "$pattern" $SCAN_PATHS 2>/dev/null || true)
  if [ -n "$hits" ]; then
    echo ""
    echo "🔴 [$severity] $label"
    echo "$hits"
    if [ "$severity" = "CRITICAL" ]; then
      CRITICAL_HITS=$((CRITICAL_HITS + 1))
    else
      HIGH_HITS=$((HIGH_HITS + 1))
    fi
  fi
}

# 1. Hardcoded password constants
# 2026-05-09: added '-' and '_' to char class so 'purebrain-admin-2026' style
# tokens (the literal that leaked in admin-clients 2026-05-08) are caught.
scan_pattern "(PASS|PASSWORD|SECRET|TOKEN|KEY)[A-Z_]*\s*=\s*['\"][A-Za-z0-9!@#\$%^&*_-]{6,}['\"]" \
  "Hardcoded password/secret constant" "HIGH"

# 2. Test-account credential literals
scan_pattern "(test|demo|admin|setup|phil|chy|aether)[A-Z_]*_PASS\s*=\s*['\"][^'\"]{4,}['\"]" \
  "Test-account password literal" "HIGH"

# 3. URL query-string auto-setup flows
scan_pattern "\?(setup|admin|debug|test)=[a-zA-Z]" \
  "URL query-string auto-setup flow (move server-side)" "HIGH"

# 4. Raw API keys
scan_pattern "(sk-[A-Za-z0-9]{20,}|sk_live_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{35})" \
  "Hardcoded API key (Stripe/AWS/Google)" "CRITICAL"

# 5. JWT-shaped literals
scan_pattern "eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}" \
  "Hardcoded JWT-shaped token" "CRITICAL"

# 6. Bearer/Basic auth literals
scan_pattern "(Bearer|Basic)\s+[A-Za-z0-9._=/+-]{20,}" \
  "Hardcoded Authorization header literal" "CRITICAL"

echo ""
echo "─────────────────────────────────────────"
echo "Scan complete: $CRITICAL_HITS CRITICAL, $HIGH_HITS HIGH"
echo "─────────────────────────────────────────"

if [ "$CRITICAL_HITS" -gt 0 ] || [ "$HIGH_HITS" -gt 0 ]; then
  echo "🔴 BLOCKED: deploy halted by pre-deploy credential scan"
  exit 1
fi

echo "✅ Pre-deploy credential scan clean"
exit 0
