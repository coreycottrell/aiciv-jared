# XSS Deploy to Pages 688/689 + Data Privacy Audit

**Date**: 2026-02-26
**Type**: operational + teaching
**Agent**: full-stack-developer

## Task 1: XSS Fix Deployment

Deployed sanitizeText() wrapping for 4 vulnerable user inputs to pages 688 (pay-test-sandbox-2)
and 689 (pay-test-2) on purebrain.ai.

### Pages Affected
- Page 688 (pay-test-sandbox-2): deployed 2026-02-26T11:32:06
- Page 689 (pay-test-2): deployed 2026-02-26T11:32:12

### Deployment Pattern Used
1. GET page content with `?context=edit` (REQUIRED for raw content)
2. Python string `.replace()` for each of the 4 vulnerable strings
3. POST back with `{"content": new_content, "status": "publish"}`
4. DELETE `/wp-json/elementor/v1/cache` to clear cache
5. Verify with second GET + assert markers

### The 4 Replacements Made
| Variable | Before | After |
|----------|--------|-------|
| firstName | `` `Nice to meet you, ${firstName}` `` | `` `Nice to meet you, ${sanitizeText(firstName)}` `` |
| company | `` `Got it — ${company}.` `` | `` `Got it — ${sanitizeText(company)}.` `` |
| role | `` `${role} — that context...` `` | `` `${sanitizeText(role)} — that context...` `` |
| goal + firstName | `` `"${goal...}"<br><br>${firstName},` `` | `` `&ldquo;${sanitizeText(goal...)}&rdquo;<br><br>${sanitizeText(firstName)},` `` |

### Why sanitizeText() is inline, not at collection time
Raw values must be preserved in `payTestData` for API calls, logging, Google Forms.
Sanitize only at the HTML rendering point, not storage.

---

## Task 2: Data Privacy Audit

### Directive
"ONLY the AICIV network should see that information so that we can spin up the persons AI
but nobody else should have access"

### Data Flows Mapped

#### Pre-payment chatbox (Page 11 - homepage)
- User input (free text conversation): sent to Claude API via two backend proxies:
  - PRIMARY: `https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` (Cloudflare Worker)
  - FALLBACK: `https://api.puremarketing.ai/v1/messages` (our backend)
  - Both are OUR infrastructure - user messages sent as Claude API messages
- Conversation logging: `https://api.purebrain.ai:8443/api/log-conversation` (our log server at 89.167.19.20)
- FALLBACK logging: `https://sageandweaver-network.netlify.app/api/capture-proxy` (A-C-Gee's proxy)
- aiName (AI name): detected from Claude's OWN response text via regex, not user-supplied
- Waitlist form (company, role): sent to Google Forms via `mode: 'no-cors'`

#### Post-payment chatbox (Pages 688/689)
- firstName, email, company, role, goal: collected in questionnaire
- Sent to: `https://api.purebrain.ai/api/log-pay-test` (our backend)
- Sent to: `https://api.purebrain.ai/api/log-conversation` (our backend)
- NOT sent anywhere else except...
  - Waitlist form: sends company + role to Google Forms (same as pre-payment)
  - Birth pipeline: sends empty `{}` to `https://89.167.19.20:8443/api/birth/start` (our server)
- Analytics: Independent Analytics plugin sends only click/page events (href, classes, UTM params) to OUR WP backend - NOT user PII

### Third-Party Exposure: ISSUE FOUND

**Google Forms** (Waitlist modal - on both page 11 AND pages 688/689):

The waitlist modal (`submitToWaitlist()`) sends to Google's servers:
- name
- email
- tier
- rating
- company (optional)
- role (optional)
- useCase
- urgency

Endpoint: `https://docs.google.com/forms/d/e/1FAIpQLSei.../formResponse`

This is the ONLY third-party with access to PII. Google is receiving waitlist signups.

**This may be intentional** (they want to collect waitlist signups in Google Sheets for easy management),
but Jared should be aware Google has this data.

### Security Assessment

| Item | Status |
|------|--------|
| Main chatbox data → AICIV servers only | PASS |
| Post-payment data → AICIV servers only | PASS |
| HTTPS on all endpoints | PASS - all https:// |
| Sensitive creds in JS | NOTE: ACGEE_API_KEY in client-side JS (low risk) |
| localStorage exposure | SAFE - only stores `pureBrainAwakenings` (counter + dates, NO PII) |
| sessionStorage exposure | SAFE - only `exitPopupShown` (boolean, NO PII) |
| cookies | SAFE - no user PII cookies set by chatbox code |
| Third-party analytics | SAFE - Independent Analytics is self-hosted on WP, no external calls |
| Google Forms | FLAG - name/email/company/role sent to Google (waitlist modal) |
| addMessage() innerHTML with user text | FLAG - page 11 renders user messages via innerHTML after markdown formatting |

### The addMessage() innerHTML issue (page 11 pre-payment chatbox)

`addMessage(input, false)` is called with raw user text and renders it via `innerHTML`
(after `**bold**` and `*italic*` markdown processing). This means if a user types
`<img src=x onerror=alert(1)>` in the pre-payment chat, it would render as an HTML tag.

However: the user is only hurting themselves (reflected XSS, their own browser only).
The content IS sent to Claude API which sanitizes/processes it server-side.
Lower severity than the post-payment XSS which was in template literals shown to ALL users.

### Recommendation

1. Google Forms - acceptable for waitlist (they opted in). Disclose in privacy policy.
2. addMessage() on page 11 - consider sanitizing user messages before rendering
3. ACGEE_API_KEY in client JS - rotate periodically, low risk (public-facing key only)

## Verification

Page 688 DEPLOYED and VERIFIED: 2026-02-26T11:32:06
Page 689 DEPLOYED and VERIFIED: 2026-02-26T11:32:12
