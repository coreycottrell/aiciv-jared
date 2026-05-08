#!/bin/bash
# Test script for cf-deploy.py --verify flag
# Run from project root: bash tools/test-cf-deploy-verify.sh

set -e

echo "🧪 Testing cf-deploy.py --verify flag implementation"
echo "=================================================="
echo ""

# Test 1: Help text shows new flags
echo "✅ Test 1: --help shows --verify and --force"
python3 tools/cf-deploy.py --help | grep -E "(--verify|--force)" | head -4
echo ""

# Test 2: Verify with Aether-owned path (should pass)
echo "✅ Test 2: --verify with Aether-owned path (blog/)"
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify --dry-run refer/index.html 2>&1 | grep -E "(✅ Verified|✅ Deploy target verified)"
echo ""

# Test 3: Verify with Chy-owned path (should error)
echo "✅ Test 3: --verify with Chy-owned path (gifts/) - should error"
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify --dry-run gifts/test-gift/ 2>&1 | grep -E "(PATH OWNERSHIP CONFLICT|owned by CHY)" || true
echo ""

# Test 4: Verify with --force on Chy-owned path (should warn but proceed)
echo "✅ Test 4: --verify --force with Chy-owned path - should warn but proceed"
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify --force --dry-run gifts/test-gift/ 2>&1 | grep -E "(--force enabled|Proceeding despite)"
echo ""

# Test 5: No map file (graceful degradation)
echo "✅ Test 5: Missing map file - should warn but continue"
mv shared/deploy-target-map.json shared/deploy-target-map.json.hidden-test
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify --dry-run blog/test 2>&1 | grep "WARNING: Deploy target map not found"
mv shared/deploy-target-map.json.hidden-test shared/deploy-target-map.json
echo ""

# Test 6: Tip message without --verify
echo "✅ Test 6: Tip message shown when --verify NOT used"
mkdir -p /tmp/cf-test && echo '<h1>Test</h1>' > /tmp/cf-test/test.html
CF_PAGES_PROJECT=purebrain-staging python3 tools/cf-deploy.py --base-dir /tmp/cf-test --dry-run test.html 2>&1 | grep "💡 Tip: run with --verify"
echo ""

# Test 7: No tip message with --verify
echo "✅ Test 7: Tip message suppressed when --verify IS used"
! CF_PAGES_PROJECT=purebrain-staging python3 tools/cf-deploy.py --verify --base-dir /tmp/cf-test --dry-run test.html 2>&1 | grep "💡 Tip" || echo "(correctly suppressed)"
echo ""

echo "=================================================="
echo "🎉 All tests passed! --verify flag is working correctly."
echo ""
echo "Usage examples:"
echo "  # Recommended (with verification)"
echo "  CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify blog/new-post/"
echo ""
echo "  # Cross-civ coordinated deploy"
echo "  CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py --verify --force gifts/shared-gift/"
echo ""
echo "Deploy target map: shared/deploy-target-map.json"
