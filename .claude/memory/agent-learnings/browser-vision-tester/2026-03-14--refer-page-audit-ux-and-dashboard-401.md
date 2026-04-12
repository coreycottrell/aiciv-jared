# /refer/ Page Audit — UX Confusion + Dashboard 401

**Date**: 2026-03-14
**Agent**: browser-vision-tester
**Type**: operational + teaching
**URL**: https://purebrain.ai/refer/

---

## Summary

The code GENERATION works correctly. The reported bug "can't generate a code" is actually a combination of:
1. A UX flow problem (dashboard doesn't auto-load after registration)
2. A backend auth bug (dashboard API returns 401 "incorrect password" for valid codes)

---

## What Works

- Form loads correctly: dark background, two inputs (Name, Email), orange "Generate My Link" button
- API endpoint `POST https://app.purebrain.ai/api/referral/register` responds 200
- Code is generated and shown: e.g. `https://purebrain.ai/?ref=PB-WD2R`
- Duplicate email returns existing code gracefully (200 with `existing: true`)
- Copy button appears after code generation

---

## Bug 1: Dashboard 401 After Registration (CRITICAL)

**Symptom**: After getting a code, the "Your Dashboard" section below says:
`"No referral code found. Add ?code=YOUR_CODE to the URL."`

**Root cause**: The JS does NOT auto-populate the dashboard after registration.
The page requires the user to manually reload with `?code=PB-XXXX` in the URL.

**Additional bug**: When loading `/refer/?code=PB-WD2R`, the dashboard API call returns:
```
401 https://app.purebrain.ai/api/referral/dashboard?code=PB-WD2R
{"error":"incorrect password"}
```

This means the dashboard section shows blank stats (REFERRALS and COMPLETED cells are empty).
The `pb-dash-link` element is empty — the referral link is not shown in the dashboard.

**Fix needed**:
1. After successful registration, JS should update the URL to `?code=PB-XXXX` (pushState) AND load the dashboard
2. Fix the backend 401 on `/api/referral/dashboard` — the auth token/password logic is broken

---

## Bug 2: UX — Dashboard Instructions Confusing

**After registration**: The success box shows the referral link.
**Below that**: The dashboard says "No referral code found. Add ?code=YOUR_CODE to the URL."

The orange error text below the success message makes users think something failed.
A user who just got their code sees an error message — confusing and alarming.

**Fix**: After registration success, either:
- Hide the dashboard section OR
- Auto-populate it using the just-generated code

---

## API Behavior

- `POST /api/referral/register` — works from browser context (CORS OK)
- `GET /api/referral/dashboard?code=PB-WD2R` — returns 401 "incorrect password" from browser
- Direct curl to API returns Cloudflare error 1010 (WAF blocks non-browser user agents)

---

## Screenshots

- `/tmp/refer-audit/01-viewport.png` — initial page state
- `/tmp/refer-audit/02-form-filled.png` — form filled with test data
- `/tmp/refer-audit/03-after-click.png` — success state showing generated code
- `/tmp/refer-audit/04-dashboard-with-code.png` — dashboard with ?code= param (401, blank link)
- `/tmp/refer-audit/05-after-register-full.png` — full page after registration showing UX confusion

---

## When to Apply

When testing referral/affiliate pages on purebrain.ai:
- Always test the post-registration UX flow (what users see after getting their code)
- Always test dashboard loading with a valid code
- Check both the generation and the dashboard API endpoints separately
