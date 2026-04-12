# cc.purebrain.ai Login Page — Pixel-Perfect Hub Match

**Date**: 2026-02-28
**Type**: build / fix
**Agent**: dept-systems-technology

---

## What Was Fixed

The `cc.purebrain.ai` login page (`/auth/login`) did not match `purebrain-hub.vercel.app`.

### Problems Before
1. Wrong/simplified neural canvas animation (basic particles only, no rings/scan beam/secondary orbs)
2. Only 2 fields (Name + Password) — was missing Email field
3. Styling was minified/simplified and did not match hub exactly

### Fix Applied

Replaced the `login_page` GET handler and `login_submit` POST handler in:
`/home/jared/projects/AI-CIV/aether/tools/comms-gateway/api/auth.py`

Source of truth: `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/purebrain-hub-source.html` (187KB, 4709 lines)

---

## What the New Login Has

| Element | Status |
|---------|--------|
| Neural canvas with `drawRings`, `drawScanBeam`, `drawBgNodes`, `drawCenterGlow`, `drawDataArcs`, secondary orbs | Exact copy from hub |
| 3 form fields: Name (typeahead), Email (auto-fill), Password | Hub-matching |
| Aether orb with all animations (pulse, glow, rings, particles orbiting) | Exact copy |
| Glass-morphism card with backdrop-filter blur | Exact match |
| Font: Inter + Oswald from Google Fonts | Exact match |
| Colors: `--pb-bg: #0a0e1a`, `--pb-accent: #2a93c1`, `--pb-orange: #f1420b` | Exact match |
| Typeahead auto-fills email field on name select | Implemented |
| Login button shows spinner on submit | Implemented |
| Server-side auth: POST to `/auth/login`, session set, redirect to `/` | Works |
| Error handling: redirect to `/auth/login?error=...` | Works |

---

## POST Handler Changes

The POST handler now accepts `email` as an additional Form field.
Resolution order:
1. `username` (hidden field set by autocomplete selection) → fastest path
2. `display_name` match → exact, then first-word fuzzy
3. `email` match → fallback if name not resolved

This makes login work even if:
- User types name without selecting from dropdown
- User types only email

---

## Verification Results

All 20 checks passed on live endpoint:
- `http://localhost:8870/auth/login` returns 28,500 char HTML
- Login POST with correct creds → 303 to `/`
- Login POST with wrong creds → 303 to `/auth/login?error=...`
- Service: `aether-comms-gateway` active (running)

---

## Key Pattern: Extracting Login From Hub Source

Hub source is one monolithic HTML file at 187KB.
- CSS (login-specific): lines 82-600
- Login HTML: lines 1996-2140
- Neural canvas JS: lines 2580-2879
- handleLogin / initAutocomplete: lines 3195-3360
- TEAM_ROSTER: line 2930

For the gateway, we inject TEAM_ROSTER from `config.TEAM_ROSTER` server-side (Python f-string JSON injection).
The hub's client-side `handleLogin` is replaced by a form POST to the server.
Everything else (CSS, canvas animation, autocomplete, orb) is direct copy.
