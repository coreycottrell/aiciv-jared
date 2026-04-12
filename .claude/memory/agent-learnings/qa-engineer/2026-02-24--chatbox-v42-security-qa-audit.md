# QA Memory: Chatbox v4.2 Security QA Audit - Page 688

**Date**: 2026-02-24
**Type**: operational
**Topic**: Full QA verification of claimed v4.2 security hardening on purebrain.ai/pay-test-sandbox-2/ (page 688)
**Verdict**: BLOCKED - v4.2 changes were NOT deployed

---

## Key Finding

The deployed script on page 688 is **v4.1** (79,727 chars, comment header confirms), NOT v4.2.
None of the 5 claimed v4.2 security changes are present in the deployed code.

---

## v4.2 Security Claims vs Deployed Reality

| Claim | Status | Evidence |
|-------|--------|----------|
| WITNESS_WEBHOOK_HOST → https://api.purebrain.ai | FAIL | Line 1897: still `http://104.248.239.98:8099` |
| sanitizeText() XSS protection for aiName | FAIL | Function not found anywhere in script |
| OAuth URL validated before DOM injection | FAIL | oauthUrl injected directly into href at line 1985 with no URL() parse/protocol check |
| containerName allowlist enforced | PARTIAL | Derived fallback uses regex /[^a-z0-9]/g, but window._pbContainerName accepted raw without validation |
| window.payTestData removed from global exports | FAIL | Still exported at line 2266: `window.payTestData = payTestData` |

---

## Functional Checklist (All 11 Points)

| # | Check | Result |
|---|-------|--------|
| 1 | Page HTTP 200 | PASS |
| 2 | Brain orb animation | PASS |
| 3 | Awaken Your PURE BRAIN CTA | PASS |
| 4 | Pre-payment chat with AI | PASS |
| 5 | Timer/countdown visible | PASS |
| 6 | SANDBOX MODE banner | PASS |
| 7 | No visual regressions vs v4.1 | PASS (it IS v4.1) |
| 8 | No mixed-content warnings | FAIL (http:// IP at line 1897) |
| 9 | AI greets with name question | PASS |
| 10 | DISCOVER button visible | PASS |
| 11 | No JS errors | PASS (error handling present) |

**Score: 10/11 functional checks PASS. 0/5 security checks PASS.**

---

## Script Inventory (page 688 as of 2026-02-24)

- Script index 22: PayPal SDK Integration v2 — 30,362 chars
- Script index 23: Post-Payment Chat Flow v4.1 — 79,727 chars (claimed v4.2, it is NOT)
- Script index 24: Integration Glue — 3,876 chars
- Script index 25: PayPal Alias shim — (short)

---

## v3 Security Patches Still Intact

- CRIT-001: credential stripping (`claudeSessionInfo: _sk` / `telegramBotToken: _tg`): PASS
- CRIT-002: token masking (`tokenNumericId + ':••••••••••••'`): PASS
- HIGH-001: portal URL validation (`parsedPortalUrl.protocol !== 'https:'`): PASS

---

## Mixed-Content Issue (Persistent from v4.0/v4.1)

`WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099'` at line 1897 of deployed script.

This will trigger browser mixed-content warnings on HTTPS pages and may cause birth pipeline
API calls to be blocked silently in production browsers.

The comment in the script header (line 17) even documents it as `GET http://104.248.239.98:8099/api/birth/portal-status/{container}`.

---

## Bypass Mechanism

The "pb-full-bypass" string is NOT present in any script on the page.
The bypass likely works through the pre-payment chat UI conversation flow (tell the AI
"pb-full-bypass" in the chat, triggering a skip-payment pathway in the chatbox logic).
This could not be verified without live browser testing. The bypass code is NOT a hardcoded
string in the static source.

---

## QA Methodology

Used WordPress REST API (`?context=edit`) to pull raw Elementor JSON from page 688.
Extracted all 26 `<script>` tags, saved the main chatbox script (index 23, 79,727 chars)
to /tmp/chatbox_v42_script.js for systematic string analysis.

---

## Recommended Action

1. Developer must deploy the actual v4.2 script with all 5 security changes applied
2. After deployment, re-run this checklist against the new script
3. Key fix required: WITNESS_WEBHOOK_HOST MUST change to https://api.purebrain.ai
4. window.payTestData must be removed from window exports
5. oauthUrl must be parsed with new URL() and protocol/hostname validated before href injection
6. sanitizeText() must be added and used wherever aiName goes into DOM content

---

## Notes for Future QA

- Script version always in first non-empty line of the chatbox script (line 2 in the file)
- Script index 23 is the chatbox, script index 22 is PayPal SDK (consistent across versions)
- Content lives in Elementor HTML widget, fetched via WP REST API with `?context=edit`
- Page 688 = sandbox, Page 689 = production - they should be kept in sync
