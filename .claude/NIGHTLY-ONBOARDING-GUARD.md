# NIGHTLY ONBOARDING GUARD

**Schedule**: Every night, 2:00 AM ET
**Agent**: dept-systems-technology (ST#)
**Authority**: CONSTITUTIONAL -- cannot be skipped
**Reference**: .claude/ONBOARDING-SPEC-DEFINITIVE.md (single source of truth)
**Updated**: 2026-04-01 -- New flow: Payment -> /thank-you/ redirect (no post-payment chatbox)

---

## Guard Prompt

Run this check against EVERY payment page listed in the spec. Report any drift.

### CHECK 1: Page Availability
For each page in the inventory, verify HTTP 200:
```
/, /live/, /awakened/, /partnered/, /unified/, /insiders/, /insiders/awakened/,
/pay-test-sandbox-3/, /pay-test-sandbox-5/,
/thank-you/
```

### CHECK 2: Consent Gate JavaScript
For each page HTML file in exports/cf-pages-deploy/:
- Checkbox element `#pb-consent-check` exists with `checked` attribute
- `onConsentChange` function exists
- Auto-fire code: `if (checkbox.checked) { onConsentChange(true); }` present
- NO extra `});` syntax errors in consent gate IIFE
- `.pb-cta-locked` and `.pb-cta-unlocked` CSS classes defined
- Buttons start with unlocked state when checkbox is pre-checked

### CHECK 3: Pricing Accuracy
Verify exact pricing on each page matches spec:
- Awakened: $149/month ($197 at launch) -- OR $74.50 for insider pages
- Partnered: $499/month ($579 at launch)
- Unified: $999/month ($1,089 at launch)
- No pricing drift from approved values

### CHECK 4: PayPal Integration
- PayPal SDK script present with correct client-id
- LIVE pages use LIVE PayPal client ID
- Sandbox pages use SANDBOX PayPal client ID
- Subscription plan IDs match approved values
- PayPal buttons render in correct containers

### CHECK 5: Seed Flow
- `/api/send-seed` endpoint reachable on api.purebrain.ai
- Seed destination: witness-aiciv@agentmail.to (NOT witness-support)
- Seed format: Rich HTML with structured table (NOT plain text)
- Full conversation included in seed payload
- Seed fires BEFORE redirect to /thank-you/

### CHECK 6: Thank-You Page Redirect
For each payment page:
- `onPaymentComplete` (or equivalent) includes redirect to `/thank-you/`
- Redirect URL includes parameters: `aiName`, `name`, `email`, `tier`
- Seed fires BEFORE the redirect (not after)
- 300ms delay between seed fire and redirect
- NO post-payment chatbox overlay code present (must be ABSENT)
- NO `launchPostPaymentFlow` function (REMOVED)
- NO `_postPaymentLaunched` variable (REMOVED)
- NO `postPaymentOverlay` references (REMOVED)

### CHECK 7: Thank-You Page Functionality
Verify `/thank-you/index.html`:
- Parses URL parameters (`URLSearchParams` for aiName, name, email, tier)
- Shows personalized status checklist:
  - "Payment confirmed" (green check)
  - "AI partner being configured" (animating)
  - "Welcome email on its way" (animating)
  - "Check your inbox at [email]"
- Polls `/api/magic-link/` every 5 seconds
- Shows "Enter [AI Name]'s Brain Stream" button when magic link is ready
- All checklist items go green when ready

### CHECK 8: Welcome Email Logic
- `agentmail_monitor.py` service running (`systemctl is-active agentmail-monitor`)
- Dual-send logic present in handle_magic_link_email()
- PayPal email lookup from `logs/payer_emails_by_uuid.json`
- Deduplication: case-insensitive comparison
- Sandbox filter: sb-*, example.com patterns excluded
- Sandbox email bypass: sb-*@example.com -> jared@puretechnology.nyc
- BCC: jared@puretechnology.nyc (NOT CC)
- Auto welcome email fires via agentmail_monitor (no manual trigger)

### CHECK 9: Magic Link Pipeline
- UUID generation: ONE UUID through entire pipeline
- Email fallback if magic link fails
- Watchdog monitor running
- `purebrain_log_server.py` service running (`systemctl is-active aether-logserver`)

### CHECK 10: Payment Page Constitutional Checks
Run: `bash tools/verify-payment-pages.sh`
- Must report all checks passed
- Canvas + video pause on pricing reveal
- No WordPress scripts/CSS
- Preconnect tags present
- Thank-you redirect present
- No post-payment chatbox code
- Thank-you page exists with polling

### CHECK 11: No Exposed Secrets
Scan all payment page HTML for:
- API keys (pattern: `xkeysib-`, `pat`, `sk-`, `key-`)
- Hardcoded passwords in HTML comments
- Airtable tokens, Brevo keys, ACG keys

### CHECK 12: Portal Alarm Integration
After all checks complete:
- Send results summary to portal chat
- If ANY check fails: trigger alarm sound + red alert in portal
- If all pass: green status update, no alarm
- Always log results to `logs/nightly-onboarding-guard/YYYY-MM-DD.json`

### CHECK 13: Witness Alignment
- Seeds must include Session UUID (non-empty)
- Seeds must include AI Name (not "not yet named")
- 5-strategy conversation lookup must be active in purebrain_log_server.py

---

## Output Format

```
NIGHTLY ONBOARDING GUARD -- [DATE]

PAGES CHECKED: [count]
CHECKS RUN: [count]
PASSED: [count]
FAILED: [count]

[For each failure:]
FAIL: [check name] -- [page] -- [description]

[If all pass:]
ALL CHECKS PASSED -- Onboarding pipeline is healthy.
```

## Drift Response

- 1 failure: Fix immediately if possible, alert Jared via portal alarm
- 3+ failures: STOP all deploys, alert Jared urgently
- Pricing drift: NEVER auto-fix -- alert only, Jared approves all pricing changes
- JS syntax errors: Auto-fix if pattern matches known consent gate bug, then redeploy + re-verify

---

## What Was REMOVED (2026-04-01)

The following checks were removed because the post-payment chatbox flow was replaced with /thank-you/ redirect:

- **Post-payment chatbox checks**: Replaced by /thank-you/ page checks. Old chatbox had black screen bug.
- **Magic link button on payment page**: Replaced by thank-you page polling + button.
- **Post-payment questionnaire flow**: No longer needed; naming happens pre-payment.
- **`_postPaymentLaunched` guard (CHECK 11 old)**: No longer needed since there is no post-payment chatbox to guard.
- **`launchPostPaymentFlow` check**: Function removed from payment pages.
- **Addendum capture check**: Seed addendum (`fireSeedAddendum` / `seed-addendum`) no longer fires from payment pages.
- **Black screen prevention guard (old CHECK 11)**: No longer applicable; the black screen was caused by the post-payment chatbox which is now removed.

All removed code is archived at `/oldchatbox/` (password: PUREBRAIN2026).

---

**Created**: 2026-03-28
**Updated**: 2026-04-01 -- New flow: Payment -> /thank-you/ redirect
**Authority**: Jared (Human CEO)
**Constitutional**: Cannot be skipped, deferred, or reduced in scope
