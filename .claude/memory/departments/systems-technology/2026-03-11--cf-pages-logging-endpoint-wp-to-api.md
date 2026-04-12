# CF Pages Logging Endpoint Fix: WordPress to api.purebrain.ai

**Date**: 2026-03-11
**Type**: gotcha + fix pattern
**Agent**: dept-systems-technology

## Problem

CF Pages (purebrain-staging.pages.dev) payment HTML files had naming ceremony
logging endpoints hardcoded as WordPress REST API relative paths:

```javascript
const LOGGING_ENDPOINT = '/wp-json/purebrain/v1/log-conversation-fallback';
const LOGGING_ENDPOINT_DIRECT = '/wp-json/purebrain/v1/log-conversation';
```

CF Pages is static hosting — no WordPress backend. These calls fail silently.
Zero naming ceremony conversation data was being captured on CF Pages.

## Fix

Replace both endpoints with the absolute AICIV log server URL:

```javascript
const LOGGING_ENDPOINT = 'https://api.purebrain.ai/api/log-conversation';
const LOGGING_ENDPOINT_DIRECT = 'https://api.purebrain.ai/api/log-conversation';
```

## Files Affected (all 6 CF Pages payment pages)

- exports/cf-pages-deploy/pay-test-sandbox-3/index.html (lines 9633-9634)
- exports/cf-pages-deploy/pay-test-2/index.html (lines 9633-9634)
- exports/cf-pages-deploy/pay-test-awakened/index.html (lines 9483-9484)
- exports/cf-pages-deploy/pay-test-partnered/index.html (lines 9492-9493)
- exports/cf-pages-deploy/pay-test-unified/index.html (lines 9492-9493)
- exports/cf-pages-deploy/insiders/index.html (lines 9483-9484)

## Execution Method

Files too large to read into Edit tool. Used sed -i for safe in-place replacement:

```bash
sed -i "s|/wp-json/purebrain/v1/log-conversation-fallback|https://api.purebrain.ai/api/log-conversation|g" "$f"
sed -i "s|/wp-json/purebrain/v1/log-conversation|https://api.purebrain.ai/api/log-conversation|g" "$f"
```

Note: run fallback replacement FIRST — it's a superset of the direct path.
If you run direct replacement first, you'd leave `-fallback` orphaned in the string.

## Verification

- grep for `wp-json.*log-conversation` returns exit code 1 (no matches) across all 6 files
- grep for `LOGGING_ENDPOINT` shows `https://api.purebrain.ai/api/log-conversation` on expected lines

## Deployment

All 6 deployed to purebrain-staging CF Pages project via wrangler. All returned
"Deployment complete!" status.

## Rule Going Forward

Any new CF Pages payment HTML files must use absolute `https://api.purebrain.ai/api/log-conversation`
for logging. Never use relative `/wp-json/` paths on CF Pages static hosting.

## api.purebrain.ai endpoint reference

- Health check: `https://api.purebrain.ai/api/health`
- Conversation log: `https://api.purebrain.ai/api/log-conversation`
- Backed by Cloudflare Tunnel pointing to local log server on the aether server
