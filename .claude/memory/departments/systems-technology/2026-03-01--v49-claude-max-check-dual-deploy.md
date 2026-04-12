# ST# v4.9 Claude Max Account Check + Dual Deployment

**Date**: 2026-03-01
**Agent**: dept-systems-technology
**Type**: deployment + feature

---

## Summary

Deployed pay-test-script-chat-flow-v4.9 to both pay-test pages (688, 689).

Two tasks completed:
1. v4.8 already had 3-stage seed firing (fireSeed) — deployed to both pages for first time
2. Added Claude Max account check question to chatbox questionnaire

---

## Changes Made

### Script: v4.8 → v4.9

**File**: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js`

#### Change 1: Version header updated to v4.9

#### Change 2: payTestData new field
```js
hasClaudeMax: null,  // NEW v4.9: true if user has Claude Max, false if not
```

#### Change 3: Claude Max question inserted in runQuestionnaire()

Location: After opening welcome message, BEFORE Q1 (name collection)

Flow:
- AI asks: "Do you already have a Claude Max account?"
- Button choice: "Yes, I have Claude Max" (primary) | "No, I don't have one yet"
- YES path: AI confirms, proceeds to Q1
- NO path: Shows 3-step guide:
  - Step 1: Go to claude.ai
  - Step 2: Create account (Google or email + phone)
  - Step 3: Upgrade to Max at claude.ai/upgrade (5x $100/mo or 20x $200/mo)
  - Shows "I'm ready — I have Claude Max now" button
  - On click: sets hasClaudeMax = true, logs, continues to Q1
- Logs to logPayTestData with event 'questionnaire:claude_max_check' and 'questionnaire:claude_max_confirmed'

---

## Deployment

| Page | ID | URL | Deploy Status | Modified |
|------|----|----|---------------|----------|
| pay-test-2 | 689 | purebrain.ai/pay-test-2 | HTTP 200 | 2026-03-01T19:55:04 |
| pay-test-sandbox-2 | 688 | purebrain.ai/pay-test-sandbox-2 | HTTP 200 | 2026-03-01T19:55:12 |

Both pages deployed via: `curl -X POST https://purebrain.ai/wp-json/wp/v2/pages/{ID}` with Basic Auth.

**Important**: Python urllib was returning 403 despite correct credentials. curl worked correctly. Always use curl for large WP REST API deploys going forward.

---

## Verification Checks (Both Pages)

- v4.9 header: PASS
- Claude Max question text: PASS
- hasClaudeMax field in payTestData: PASS
- Seed Stage 1 (payment_complete): PASS
- Seed Stage 2 (oauth_authenticated): PASS
- Seed Stage 3 (portal_ready): PASS
- "I'm ready" button: PASS

---

## Seed Firing (v4.8 feature now live on both pages)

The 3-stage seed routine fires:
- Stage 1 (payment_complete): fires at flow start in initPayTestFlow()
- Stage 2 (oauth_authenticated): fires when /birth/code confirms OAuth
- Stage 3 (portal_ready): fires when portal polling detects readiness

Proxy: https://api.purebrain.ai/api/intake/seed
Fallback: http://104.248.239.98:8200/intake/seed

---

## Key Pattern: Large WP Page Deploy

1. Save full page JSON to /tmp/pageXXX.json via curl (avoids piping issues)
2. Find script boundaries: `raw.find('/* === Post-Payment Chat Flow')` → `rfind('<script>')` for open, `find('window.initPayTestFlow = initPayTestFlow;')` → next `</script>` for close
3. Build new_raw = raw[:open] + '<script>\n' + new_script + '\n</script>' + raw[close_end:]
4. Write payload JSON to /tmp/payloadXXX.json
5. Deploy via: `curl -X POST ... --data @/tmp/payloadXXX.json`
6. Verify by checking /tmp/respXXX.json for key strings
