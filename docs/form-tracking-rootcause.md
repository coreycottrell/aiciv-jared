# Form Tracking Root Cause — 91 Starts / 0 Submits Bug

**Date**: 2026-04-14
**Triage**: ST# Track 2 diagnostic
**Severity**: High (silent conversion blindness — leadership cannot see waitlist conversion)
**Status**: Fix staged locally (NOT deployed)

---

## Symptom

GTM / GA4 analytics show:
- **form_start**: 91 events
- **form_submit**: 0 events

Waitlist form on homepage + `/insiders/awakened/` + `/insiders/pay-test-awakened/` appears to be collecting 91 start-intents but zero submits are ever recorded, despite the Google Forms backend actually receiving entries.

## Root Cause

GTM's built-in Form Submission trigger relies on listening for the DOM `submit` event to fire on the `<form>` element naturally. Our form handlers call:

```js
function handleWaitlistSubmit(event) {
    event.preventDefault();       // <-- blocks GTM's built-in listener
    ...
    submitToWaitlist({...});      // AJAX-style POST to Google Forms
    setTimeout(() => { ...swap to success state... }, 1000);
}
```

Because `event.preventDefault()` is called immediately, the native submit bubble is cancelled. GTM's built-in Form Submission trigger never sees a completed submit, so:
- The `gtm.formSubmit` internal event is NOT generated.
- No `form_submit` GA4 event is forwarded.
- `form_start` (listener on input focus / change) still fires correctly — hence 91 starts.

This is the classic single-page / AJAX-form blindspot in GTM.

## Evidence

- Homepage (`exports/cf-pages-deploy/index.html`) — line 11395: ALREADY HAS the fix (`window.dataLayer.push({ event: 'form_submit_success', ... })`).
- `insiders/awakened/index.html` — was MISSING this push at the success branch (~line 10515).
- `insiders/pay-test-awakened/index.html` — was also MISSING the push at the same location.

Google Forms submissions ARE being received (backend unaffected). The bug is analytics-only but high impact: leadership dashboards show 0% conversion.

## Fix (Staged)

Injected `window.dataLayer.push({ event: 'form_submit_success', ... })` inside the `setTimeout` success branch of `handleWaitlistSubmit`, matching the exact pattern already proven on the homepage.

Payload fields: `form_id`, `form_name`, `tier`, `urgency`, `rating`, `has_company`, `has_role`.

Wrapped in try/catch so a dataLayer error can never block the UX.

## GTM Configuration Required (Human Action, Post-Deploy)

- Trigger type: **Custom Event**
- Event name: `form_submit_success`
- Fires on: All matching events
- Forward to GA4 as `form_submit` (or keep as `form_submit_success` and update dashboard queries).

Leave GTM's built-in Form Submission trigger disabled for this form — it will never fire reliably due to preventDefault.

## Files Changed

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/insiders/awakened/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/insiders/pay-test-awakened/index.html`

Homepage already had the fix — unchanged.

## Not Done / Deferred

- **NOT deployed** — staged locally per ST# directive.
- Full sweep across all other `cf-pages-deploy/` pages with `waitlist-form` / `onsubmit=` handlers NOT performed yet. Recommend follow-up audit.
- Payment form (`pb-paypal-form-btn`) also calls `e.preventDefault()` + popup. If payment-success tracking has a similar gap, needs a separate dataLayer push in `showPopupClosedConfirmation()` success branch. Out of scope for this ticket.
- QA pass (GTM Preview + GA4 DebugView confirm) owed before production deploy.

## Verification Checklist (Pre-Deploy)

- [ ] QA: Load `/insiders/awakened/` in GTM Preview mode, submit test entry, confirm `form_submit_success` fires with payload.
- [ ] QA: Repeat on `/insiders/pay-test-awakened/`.
- [ ] Security: Payload contains NO email/name — only booleans + categorical (tier/urgency/rating). PII-clean. Consent gate safe.
- [ ] Payment guard: awakened page is a payment page — confirm no regression to PayPal popup flow.
- [ ] Post-deploy: GA4 `form_submit_success` count > 0 within 24h.
