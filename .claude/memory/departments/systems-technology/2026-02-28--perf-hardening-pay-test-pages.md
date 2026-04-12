# Performance Hardening: Pay-Test Pages

**Date**: 2026-02-28
**Type**: pattern + gotcha
**Pages patched**: 688, 689, 468, 439 (page 11 had no payment JS)

---

## What Was Done

Applied 4 performance hardening fixes to prevent api.purebrain.ai downtime from causing user-facing slowness.

### Fix 1: verifyPaymentServerSide — 3-second AbortController
Added AbortController with 3s timeout to the PayPal verification fetch. If backend is slow, abort fires and payment proceeds client-side. Zero user impact on backend outage.

### Fix 2: logPayTestData — Remove async/await (fire-and-forget)
- Removed `async` keyword from function declaration
- Removed `await` from all 19 call sites (pages 688/689) or 11 (pages 468/439)
- This was the BIGGEST impact fix — was blocking the entire post-payment UI flow

### Fix 3: logPayTestData — 4-second AbortController on both fetch calls
Both `/api/log-pay-test` and `/api/log-conversation` fetches now have a shared AbortController with 4s timeout. Logging is silent on failure.

### Fix 4: onPaymentComplete setTimeout 1500ms → 500ms
The delay before `launchPostPaymentFlow` reduced from 1.5s to 0.5s. 1 second saved on every payment.

---

## Critical Gotchas Discovered

### 1. Pages 468/439 have DIFFERENT elementor_data encoding
Pages 688/689 store HTML in elementor widget `settings.html` as a parsed string.
Pages 468/439 store it as a double-escaped JSON string (newlines as `\\n`, em-dashes as `\\u2014`).

**Pattern matching must use the escaped form for 468/439 elementor_data.**
Example: search for `fetch(VERIFY_ENDPOINT, {\\n` not `fetch(VERIFY_ENDPOINT, {\n`

### 2. Page 11 has no payment JS
Page 11 does not contain `logPayTestData`, `verifyPaymentServerSide`, or any PayPal code.
It was listed in the task but is a different type of page — no changes needed, not a failure.

### 3. elementor_data vs content.raw — BOTH must be patched
Elementor renders from `_elementor_data`. WordPress stores a copy in `post_content` (content.raw).
Both need to be updated. For pages 468/439, some fixes applied only to content_raw first —
required a second pass on elementor_data with escaped patterns.

### 4. The `}, 1500)` false-positive
When checking if Fix 4 was applied, `}, 1500)` still appears in other setTimeout calls on the page.
Must use the specific pattern `}, 1500);\n  };` (with the closing function brace) to confirm absence.

---

## Verification Evidence (All Pages)

Final check confirmed 9/9 tests PASS on pages 688, 689, 468, 439:
- Fix 1: AbortController 3s present, old unprotected fetch absent
- Fix 2a: sync logPayTestData present, async version absent
- Fix 2b+3: fire-and-forget comment present, await Promise.allSettled absent
- Fix 2c: zero `await logPayTestData(` call sites remaining
- Fix 4: `}, 500);\n  };` present, `}, 1500);\n  };` absent

---

## Script Reference

Patching scripts saved at:
- `/tmp/apply_perf_hardening.py` — v1 (pages 688, 689)
- `/tmp/apply_perf_hardening_v2.py` — v2 (pages 468, 439, handles escaped patterns)
