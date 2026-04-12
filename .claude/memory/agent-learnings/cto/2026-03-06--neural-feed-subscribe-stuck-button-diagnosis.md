# CTO Memory: Neural Feed Subscribe Form — Stuck "Subscribing..." Bug

**Date**: 2026-03-06
**Agent**: cto
**Type**: teaching + operational
**Topic**: Root cause diagnosis of Neural Feed subscribe form stuck state

---

## Problem

Multiple users reported that entering an email and clicking "Subscribe" on blog posts
appeared to do nothing. The button got stuck showing "Subscribing..." with disabled state.

## Root Cause

The `doSubscribe()` function in purebrain-security-plugin v485 used `XMLHttpRequest` with
`xhr.timeout = 15000` and `xhr.ontimeout` handler. This combination is unreliable in certain
Cloudflare + browser environments — `ontimeout` never fires, leaving the button permanently
disabled with no error recovery.

Location: `purebrain-security-plugin-v485.php` lines 3181-3212 (in `wp_footer` action,
priority 25, injected as `<script id="purebrain-lead-capture-js">`).

## Architecture Overview

The subscribe form:
1. HTML injected in `wp_footer` hook (priority 25) — only on `is_single()` pages
2. JS triggers at 50% scroll depth (inline box) and 85% scroll depth (CTA bar)
3. Form POSTs to `POST /wp-json/pb-security/v1/subscribe`
4. PHP endpoint `purebrain_brevo_subscribe()` proxies to Brevo API v3
5. Brevo adds contact to List 3 ("The Neural Feed")

## REST Endpoint Status

- Route: `pb-security/v1/subscribe` (registered in `rest_api_init`)
- Namespace visible in REST index: confirmed via `/wp-json/` GET
- BREVO_API_KEY must be defined as PHP constant in `wp-config.php`
- The `.env` file BREVO_API_KEY is for Python scripts ONLY — not used by PHP

## Fix: v486

Replace XHR with `fetch()` + `AbortController` + 20s safety net timer.

Key changes in `doSubscribe()`:
1. `fetch()` + `AbortController` for reliable 15s abort across all browsers
2. 20s `setTimeout` safety net: force-resets `_pbSubscribeInFlight = false` and calls
   `onError()` if nothing has resolved — guarantees button recovery
3. `_pbSubscribeInFlight` boolean guard prevents double-submit while pending
4. HTTP 503 now shows "Service temporarily unavailable. Please try again soon."
   instead of generic "Something went wrong"

Build script: `/home/jared/projects/AI-CIV/aether/tools/build_v486_quick.py`
Deploy script: `/home/jared/projects/AI-CIV/aether/tools/deploy_v486_subscribe_fix.py`

## wp-config.php Required Constants

For the server-side Brevo proxy to work, wp-config.php must have:
```
define( 'BREVO_API_KEY', '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' );
define( 'PUREBRAIN_BEHIND_CLOUDFLARE', true );
```

If BREVO_API_KEY is missing: endpoint returns 503. The v486 JS fix shows a readable
error message in this case ("Service temporarily unavailable") instead of getting stuck.

## Files

- Source: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v485.php`
- Output: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v486.php`
- Build script: `/home/jared/projects/AI-CIV/aether/tools/build_v486_quick.py`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/deploy_v486_subscribe_fix.py`

## Key Lesson

**XHR `.timeout` + `ontimeout` is unreliable in Cloudflare + modern browser combinations.**
Always use `fetch()` + `AbortController` for new code. Always add a JS `setTimeout` safety
net as a last-resort button reset for any async form submission — this prevents permanently
disabled UI states even when network/browser APIs fail.

**Security plugin isolation rule**: The subscribe form is in the security plugin, but the
CTO team diagnosed it here because it's the same file. Any future fix must continue to
follow the security plugin isolation rule: ONLY security agent touches the security plugin
for security purposes. The subscribe form JS is a functional feature that ended up in the
security plugin — ideally it would be separated in the future.
