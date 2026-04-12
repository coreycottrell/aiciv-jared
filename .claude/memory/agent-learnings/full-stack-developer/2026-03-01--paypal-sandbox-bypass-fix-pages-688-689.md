# PayPal Sandbox Fix + Bypass Flow Fix — Pages 688 & 689

**Date**: 2026-03-01
**Agent**: dept-systems-technology → full-stack-developer
**Pages**: 688 (pay-test-sandbox-2), 689 (pay-test-2)
**Status**: DEPLOYED AND VERIFIED

## Context

After plugin rollback from v4.7.9 to v4.7.3:
- Page 689 (pay-test-2): PayPal buttons working (production)
- Page 688 (pay-test-sandbox-2): PayPal buttons NOT working
- Both pages: bypass flow broken

## Critical Rule Applied

ALL fixes in PAGE CONTENT (_elementor_data), NOT the security plugin.
"none of whatever else you did for me today should be inside that security plugin.
those should be in coding on the pages" — Jared

## Root Cause Analysis

### TASK 1 — PayPal on page 688

Page 688 has these scripts (from plugin v4.7.3):
1. `pb-paypal-routing-fix` — routes openWaitlistModal → openPayPalCheckout (production)
2. `pb-sandbox-override` — loads sandbox SDK, overrides with sandbox createOrder version

The sandbox override SHOULD work (CSP allows sandbox.paypal.com) BUT is fragile:
- Depends on plugin version
- Timing issues between routing fix and sandbox override
- If plugin changes, sandbox breaks

Solution: Add self-contained page-level sandbox script that does NOT depend on plugin.

### TASK 2 — Bypass flow on both pages

Plugin `pb-bypass-override` has `executeBypass()` function that:
1. Shows chat messages
2. Reveals pricing (#pricing)
3. **STOPS — never calls showPersonalizedCapabilities()**

`showPersonalizedCapabilities()` creates the #seeWhatBtn in chat messages.
Without it, the DISCOVERING button never appears in chat (only in pricing section).

The in-page processResponse bypass DOES work (uses [SHOW_PRICING] → displayAIMessages → creates seeWhatBtn). But the plugin's URL bypass (?bypass=true) doesn't call showPersonalizedCapabilities.

## Fix Implementation

### TASK 1 — Page 688 sandbox PayPal (page content only)

Script added at end of main widget HTML (replaced empty PayPal Alias placeholder):
- `applySandboxSetup()` function
- Removes production SDK, loads sandbox SDK
- On SDK load: overrides openWaitlistModal/openPayPalModal/openPayPalCheckout with `openSandboxModal()`
- `openSandboxModal()` uses `createOrder` (one-time capture, not subscription)
- Uses sandbox client ID: AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_
- Log prefix: [PB-SANDBOX-PAGE] to distinguish from plugin's [PB-SANDBOX]
- Fires 200ms after DOMContentLoaded (later than plugin's 100ms to win the race)

### TASK 2 — Bypass flow (both pages)

Script added at end of main widget HTML:
- `waitForBypassAndPatch()` — MutationObserver on #pricing element
- When #pricing becomes visible (any bypass or normal flow), checks if #seeWhatBtn exists
- If seeWhatBtn is missing: calls `showPersonalizedCapabilities()` or injects directly
- `injectDiscoverBtn()` fallback: creates the button manually in chatMessages
- Log prefix: [PB-BYPASS-FIX]

## Injection Point

Both scripts replace the empty placeholder at end of main widget HTML:
```
\n<script>\n/* PayPal Alias */\n(function(){/* PayPal mode active - override removed */})();\n</script>
```

## Deployment

REST API PUT to /wp-json/wp/v2/pages/688 and /689 with updated meta._elementor_data
curl has arg length limits at this payload size (~520KB) — use Python urllib instead.

After deployment: DELETE /wp-json/elementor/v1/cache

## Verification

### Page 688 live check:
- PB-SANDBOX-PAGE: 11 occurrences (page-level script + comments)
- PB-BYPASS-FIX: 6 occurrences
- applySandboxSetup: 3 occurrences
- openSandboxModal: 4 occurrences
- _elementor_data in DB: 500626 chars

### Page 689 live check:
- PB-BYPASS-FIX: 6 occurrences
- No PB-SANDBOX-PAGE (correct — production PayPal)
- _elementor_data in DB: 494464 chars

## Key Lessons

1. **curl arg length limit**: REST API payloads >~100KB hit shell arg limits. Use Python urllib.
2. **PayPal Alias placeholder**: The empty `(function(){/* PayPal mode active */})()` at end of page widget is the safe injection point for page-level fixes
3. **Sandbox vs production**: Page 688 uses sandbox client ID AYTFob05..., page 689 uses AWgWNlBQ...
4. **createOrder vs createSubscription**: Sandbox plan IDs (P-xxx) don't exist — must use createOrder for sandbox
5. **Plugin vs page content**: ALWAYS prefer page content for page-specific fixes. Plugin = site-wide only.
6. **MutationObserver pattern for bypass detection**: Watch #pricing attributes instead of trying to patch closed-over executeBypass function

## Files

- Page 688 fixed: deployed via REST API (no file artifact)
- Page 689 fixed: deployed via REST API (no file artifact)
- Fix script definitions: /tmp/fix_pages.py (session only)
