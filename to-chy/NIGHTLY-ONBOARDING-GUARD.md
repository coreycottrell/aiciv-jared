# NIGHTLY ONBOARDING GUARD

**Schedule**: Every night, 2:00 AM ET
**Agent**: dept-systems-technology (ST#)
**Authority**: CONSTITUTIONAL — cannot be skipped
**Reference**: .claude/ONBOARDING-SPEC-DEFINITIVE.md (single source of truth)

---

## Guard Prompt

Run this check against EVERY payment page listed in the spec. Report any drift.

### CHECK 1: Page Availability
For each page in the inventory, verify HTTP 200:
```
/live/, /awakened/, /partnered/, /unified/, /insiders/, /insiders/awakened/,
/pay-test-sandbox-3/, /insiders/pay-test-awakened/,
/pay-test-sandbox/, /pay-test-sandbox-2/, /pay-test-sandbox-5/,
/pay-test/, /pay-test-2/, /pay-test-5/,
/pay-test-awakened/, /pay-test-partnered/, /pay-test-unified/
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
- Awakened: $149/month ($197 at launch) — OR $74.50 for insider pages
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
- `/api/seed-addendum` endpoint reachable
- Seed destination: witness-aiciv@agentmail.to (NOT witness-support)
- Seed format: Rich HTML with structured table (NOT plain text)
- Full conversation included in seed payload

### CHECK 6: Welcome Email Logic
- `agentmail_monitor.py` service running (`systemctl is-active agentmail-monitor`)
- Dual-send logic present in handle_magic_link_email()
- PayPal email lookup from `logs/payer_emails_by_uuid.json`
- Deduplication: case-insensitive comparison
- Sandbox filter: sb-*, example.com patterns excluded
- BCC: jared@puretechnology.nyc (NOT CC)

### CHECK 7: Magic Link Pipeline
- UUID generation: ONE UUID through entire pipeline
- Email fallback if magic link fails
- Watchdog monitor running
- `purebrain_log_server.py` service running (`systemctl is-active aether-logserver`)

### CHECK 8: Payment Page Constitutional Checks
Run: `bash tools/verify-payment-pages.sh`
- Must report 64/64 checks passed
- Canvas + video pause on pricing reveal
- No WordPress scripts/CSS
- Preconnect tags present
- Consent checkbox present

### CHECK 9: No Exposed Secrets
Scan all payment page HTML for:
- API keys (pattern: `xkeysib-`, `pat`, `sk-`, `key-`)
- Hardcoded passwords in HTML comments
- Airtable tokens, Brevo keys, ACG keys

### CHECK 10: Portal Alarm Integration
After all checks complete:
- Send results summary to portal chat
- If ANY check fails: trigger alarm sound + red alert in portal
- If all pass: green status update, no alarm
- Always log results to `logs/nightly-onboarding-guard/YYYY-MM-DD.json`

---

## Output Format

```
NIGHTLY ONBOARDING GUARD — [DATE]

PAGES CHECKED: [count]
CHECKS RUN: [count]
PASSED: [count]
FAILED: [count]

[For each failure:]
FAIL: [check name] — [page] — [description]

[If all pass:]
ALL CHECKS PASSED — Onboarding pipeline is healthy.
```

## Drift Response

- 1 failure: Fix immediately if possible, alert Jared via portal alarm
- 3+ failures: STOP all deploys, alert Jared urgently
- Pricing drift: NEVER auto-fix — alert only, Jared approves all pricing changes
- JS syntax errors: Auto-fix if pattern matches known consent gate bug, then redeploy + re-verify

---

**Created**: 2026-03-28
**Authority**: Jared (Human CEO)
**Constitutional**: Cannot be skipped, deferred, or reduced in scope
