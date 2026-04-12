# Hardcoded API Keys Security Fix

**Date**: 2026-04-04
**Type**: teaching
**Agent**: dept-systems-technology

## What Happened

Security scan found 6 hardcoded API keys in client-side deployed code under `exports/cf-pages-deploy/`. Three critical keys were in HTML visible to any browser visitor.

## Keys Found

1. **Airtable PAT** in team-dashboard (CRITICAL - full DB access)
2. **Brevo API key** in 29 files (CRITICAL - email send capability)
3. **TTS API key** in investor-avatar (MEDIUM)
4. **ACG logging key** in purebrain-3 (MEDIUM - not yet fixed)
5. **Cal.com key** in agent-calendar (MEDIUM - not yet fixed)
6. **PureSurf keys** in 5 tools files (LOW - server-side only)

## Fix Pattern

Created CF Pages Function proxies (`functions/api/airtable-proxy.js`, `functions/api/brevo-proxy.js`) following the existing pattern from `investor-chat.js` and `investor-tts.js`. Client calls proxy, proxy reads key from CF environment variable.

## Root Cause

WordPress migration carried over inline API keys from old WP pages. 28 of the Brevo exposures were legacy pages migrated verbatim.

## Prevention

Need pre-deploy scan: `grep -rn "xkeysib\|patc\|Bearer [A-Z]" exports/cf-pages-deploy/ --include="*.html"` before every deploy.

## Key Files

- Report: `/home/jared/exports/portal-files/security-fix-report-2026-04-06.md`
- New proxy: `exports/cf-pages-deploy/functions/api/airtable-proxy.js`
- New proxy: `exports/cf-pages-deploy/functions/api/brevo-proxy.js`

## Action Required

1. ROTATE Airtable PAT (compromised)
2. ROTATE Brevo API key (compromised)
3. Set both as CF Pages env vars
4. Deploy fixed files
5. Update 28 legacy pages to use proxy endpoint
