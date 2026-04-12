# Security Review: Witness Birth Pipeline v4/v4.1

**Date**: 2026-02-24
**Agent**: security-engineer-tech
**Type**: operational

## What Was Reviewed
`exports/pay-test-script-chat-flow-v4.js` — the post-payment chat flow with the new Witness birth pipeline (runBirthInit, runPortalButtonWatcher).

## Key Findings

### Production Blocker Found
`WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099'` — plain HTTP from HTTPS page. Modern browsers block this (mixed-content policy). The CTO had already decided to proxy through `https://api.purebrain.ai/api/birth/*` but the developer called the raw IP directly. Fix: change the constant to `'https://api.purebrain.ai'`.

### XSS Pattern: innerHTML + template literals + unsanitized variables
The codebase uses a recurring pattern of `element.innerHTML = \`...${variable}...\`` where `variable` can contain user-controlled or server-controlled strings. This is dangerous when:
- `aiName` (passed as parameter, potentially from URL params)
- `oauthUrl` (returned from Witness server — server compromise = XSS)
- `goal`, `company`, `role`, `firstName` (user-typed input)

The correct pattern (used in `userSay()`) is `element.textContent = value`. Apply this everywhere user-controlled data touches the DOM.

### Good patterns already in the code
- Credential stripping in logPayTestData (destructuring to remove claudeSessionInfo + telegramBotToken)
- Token/key masking before display (bullet characters)
- Portal URL validation with URL() constructor + hostname check
- rel="noopener" on all _blank links
- AbortController timeouts on fetch calls

### Global namespace risk
`window.payTestData` is exported and contains sensitive fields. Remove from window exports — only `initPayTestFlow` needs to be public.

## Patterns to Apply Going Forward
1. Never interpolate server responses or user input directly into innerHTML
2. Validate all URLs from external sources (protocol + allowed hostnames) before DOM use
3. Sanitize `aiName` and similar "trusted" parameters at entry point — they may come from URL params
4. Apply strict allowlist to values used in API URL paths (container names, IDs)

## Verdict
BLOCKED (mixed-content + XSS) — 2 Critical, 2 High issues before production.
