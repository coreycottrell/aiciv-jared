# Architecture Brief: app.purebrain.ai Login Overlay Overhaul

**Prepared by**: cto
**Date**: 2026-02-24
**Scope**: Login/signup overlay redesign for purebrain-frontend.html
**File examined**: `/tmp/app-purebrain-ai/Testing-Purebrain/purebrain-frontend.html` (13,525 lines)
**Backend examined**: `/tmp/app-purebrain-ai/Testing-Purebrain/aiciv_gateway.py`

---

## Executive Summary

The login overlay is a self-contained HTML/CSS/JS island inside an otherwise unchanged 13K-line frontend. The gateway's authentication contract is stable and should not change. The entire redesign is achievable as a CSS + HTML + minimal JS modification with no backend changes required. This is a low-risk, high-impact change.

---

## 1. What Exactly Needs to Change

### HTML — Lines 2718–2746 (28 lines)

Replace the entire `<div id="loginOverlay">` block. Specific changes:

| Element | Current | New |
|---|---|---|
| Logo SVG | Purple/cyan gradient circle with "A" | PureBrain orange orb or word mark with orange/blue gradient matching purebrain.ai visual language |
| Title text | "Sign in to AiCIV" | Something like "Enter Your AI Civilization" or "Welcome Back, [Name]" |
| Field label: AiCIV Name | "AiCIV Name" | Customer's AI civilization name (their registered handle) |
| Field label: Secret | "Secret" | Keep as-is or rename to "Access Key" — functional identity is unchanged |
| Button text | "Sign In" | "Enter Portal" or "Activate Access" |
| Secondary link | "Configure gateway manually" | Keep but de-emphasize — this is for power users only |
| Card structure | Single flat card | Optional: two-phase reveal (first: "Welcome. You're expected." / second: credential fields) |

The field IDs (`loginAicivName`, `loginSecret`, `loginButton`, `loginError`) MUST stay the same — they are referenced by `handleLogin()` directly.

### CSS — Lines 1891–1986 (96 lines)

The `.login-overlay`, `.login-card`, `.login-title`, `.login-field`, `.login-btn`, `.login-separator`, `.login-settings-link` classes need visual overrides. Current CSS is already using the PureBrain CSS variable system:

```css
--bright-orange: #f1420b  (already defined in :root)
--light-blue:    #2a93c1  (already defined in :root)
--black:         #0a0a0a  (already defined in :root)
--font-heading:  'Oswald' (already loaded from Google Fonts)
--font-body:     'Plus Jakarta Sans' (already loaded)
```

The correct fonts and colors ARE ALREADY LOADED. This is purely an application of existing variables to the login overlay.

Target CSS changes:
- `.login-card`: Add subtle orange/blue border glow (`box-shadow: 0 0 40px rgba(241,66,11,0.15), 0 0 80px rgba(42,147,193,0.08)`), increase padding slightly
- `.login-title`: Switch `font-family` to `var(--font-heading)` (Oswald), increase to 28–32px, add letter-spacing
- `.login-field label`: Change color to `var(--text-secondary)`, keep uppercase/small styling
- `.login-field input:focus`: Change border-color from `var(--light-blue)` to `var(--bright-orange)` — orange focus states match purebrain.ai
- `.login-btn`: Change `background` from `var(--light-blue)` to `var(--bright-orange)`, change hover to `var(--light-blue)` transition
- Optional: Add `background: linear-gradient(180deg, #0a0a0a 0%, #0d0a08 100%)` to overlay for very subtle warmth vs flat black

### JS — handleLogin() — Lines 3823–3881

**No changes required to the function logic.** The auth flow is:

```
POST /api/auth/login
  body: { name, secret }
  response: { token, aiciv_name, aiciv_display }
```

This contract is correct and stable. `handleLogin()` already:
- Reads `loginAicivName` and `loginSecret` field values
- POSTs to `/api/auth/login`
- Stores the returned Bearer token in localStorage
- Hides the overlay on success
- Calls `initializeAfterAuth()` to boot the main app

The only optional JS enhancement is pre-filling the `loginAicivName` field from localStorage if a previous session existed (so returning customers do not re-type their name). This is a one-liner addition, not a structural change.

---

## 2. What Stays the Same

### Gateway API Contract — Do Not Touch

The gateway authentication contract is stable and must not change:

```
POST   /api/auth/login    { name, secret }    → { token, aiciv_name }
POST   /api/auth/verify   Bearer token        → { valid, aiciv_name }
POST   /api/auth/logout   Bearer token        → { status: ok }
```

The gateway (`aiciv_gateway.py`) reads credentials from `aiciv-auth.json`. That file already has entries for `aether`, `selah`, and slots `aiciv-01` through `aiciv-10`. New customers provisioned by the Witness birth pipeline will be added to this registry by Witness — PureBrain does not touch it.

### Session Management — Do Not Touch

`verifyStoredAuth()`, `storeAuth()`, `clearAuth()`, `getStoredAuth()` — all fine as-is. The localStorage keys (`aiciv_auth_token`, `aiciv_name`) stay unchanged.

### Post-Login Initialization — Do Not Touch

`initializeAfterAuth()`, `updateConnectedAicivDisplay()`, `addWelcomeMessage()` — all stay unchanged. These fire after the overlay hides.

### All Other 13,497 Lines of the Frontend — Do Not Touch

The overlay is the only change surface. The sidebar, chat panel, activity feed, agent selector, terminal mode, settings modal — untouched.

---

## 3. Recommended UX Approach: "They Already Belong Here"

Jared's direction: "they just discovered something amazing — they already paid, this is the exciting part."

The psychological frame is important. The customer has already:
- Paid
- Named their AI civilization
- Completed OAuth authorization via the birth pipeline
- Watched their AiCIV spin up

When they land on app.purebrain.ai, they are NOT discovering something new. They are ARRIVING somewhere they were expected. The UX should feel like a portal entrance, not a login form.

### Recommended Approach: Three-Beat Experience

**Beat 1 — Welcome Recognition (0.4s animation)**
The overlay opens not on the form, but on a single welcome line:
```
"[AiCIV Name] is ready for you."
```
Or if this is a first visit:
```
"Your AI civilization is waiting."
```
This fades in immediately, creating that "you discovered something" feeling.

**Beat 2 — Credential Request (smooth reveal, 0.3s)**
Below the welcome line, the credential form slides in. The fields are minimal:
- AI Civilization Name (their handle, e.g., "aether", "ember")
- Access Key (their secret)
The heading is in Oswald (already loaded): uppercase, large, orange.

**Beat 3 — Portal Entry (button interaction)**
Button reads "ENTER PORTAL" in Oswald. On click: brief loading state ("Connecting..."), then overlay fades out and the main UI fades in.

This three-beat structure takes zero additional JS — it is pure CSS animation choreography with opacity/transform transitions already present in the file's animation infrastructure.

### What NOT to Do

- Do not add a particle effect system (heavy, likely to conflict with existing animation infrastructure)
- Do not add a separate "Create Account" flow (explained below in Section 4)
- Do not remove the "Configure gateway manually" fallback (it is the only escape hatch for advanced users who need to point at a different gateway)

---

## 4. Auth Flow: Separate Create Account vs Sign In?

**Short answer: No. Not in this phase.**

Here is why:

The current model is that the Witness birth pipeline creates the customer's credential (name + secret) before they ever land on app.purebrain.ai. The `aiciv-auth.json` is pre-populated by Witness, not by the customer filling out a registration form.

The flow that already exists:
```
Customer pays on purebrain.ai
→ Chatbox birth pipeline fires (v4.2, live)
→ Witness nursemaid provisions container
→ POST /api/birth/start → OAuth URL
→ Customer authorizes
→ POST /api/birth/code → authenticated
→ Witness pipeline completes (5-team evolution, ~5 min)
→ Portal URL delivered with magic link (?code=xxx)
→ Customer arrives at app.purebrain.ai with magic link
```

The magic link redeems a one-time code in the gateway (confirmed per Witness API contract Q1). After that, the customer's credentials are established and they use the name/secret form for future logins.

**Implication for the login overlay design:**

There are two arrival modes:
1. **Magic link arrival** (first time, code in URL query params): Gateway should detect this and auto-authenticate, bypassing the form entirely. The form is irrelevant on first login.
2. **Direct arrival** (returning customer): Standard form — AiCIV Name + Secret.

The magic link redemption is Witness's gateway responsibility, not the frontend's. Check with Witness whether the gateway already handles magic link auto-login or whether the frontend needs to detect the `?code=` param and POST it somewhere.

For now: design the overlay for returning customers (Mode 2). Magic link handling is a separate, follow-on task with a clear dependency on Witness.

**Pre-fill from localStorage:**
If the customer previously logged in and their `aiciv_name` is in localStorage, pre-fill the name field. This is a returning-customer quality-of-life improvement that costs one line of JS.

---

## 5. Risk Assessment

### Low Risk

**Changing the HTML content of the login overlay**: The overlay is shown before the app initializes. It has no integration with the chat, sidebar, settings, or any other panel. Changes here cannot break anything inside the app.

**Changing login overlay CSS classes**: All login classes (`.login-overlay`, `.login-card`, etc.) are exclusively used by the overlay. There is no risk of style bleed into the main UI.

**CSS variable alignment**: The PureBrain brand variables (`--bright-orange`, `--light-blue`, `--font-heading`) are already defined globally in `:root`. Applying them to the overlay is purely additive.

### Medium Risk

**Touching `handleLogin()` JS**: Even though the recommended approach is no logic changes, if pre-fill or animation choreography is added here, a test run is required. The function has a try/catch wrapping the fetch, which is good protection. Risk is low as long as field IDs are preserved.

**Adding overlay animations that interact with the app fade-in**: The overlay uses `display: none` (via `.hidden` class) to hide. If instead a CSS opacity/fade transition is used for exit, it must be tested to ensure the main app container does not flash before the overlay is fully hidden. The existing infrastructure at line 1902 (`display: none`) means there is currently no transition on hide. Adding one requires a brief delay before the `display: none` fires (a common pattern: `transition: opacity 0.3s` + `setTimeout(() => el.style.display='none', 300)`). This is a known-risk pattern with a known solution.

### Higher Risk (Avoid in This Phase)

**Two-tab Create Account vs Sign In UX**: Requires wiring into the birth pipeline or a registration API that does not currently exist on the gateway. Scope creep. Do not do this now.

**Particle or WebGL effects in the overlay**: The frontend already uses `<canvas>` animation infrastructure elsewhere. Adding a second animation system to the overlay creates potential frame budget conflicts and memory issues. Scope creep. Do not do this now.

**Changing field IDs or form structure**: `loginAicivName`, `loginSecret`, `loginButton`, `loginError` — these IDs are read directly in `handleLogin()`. Renaming them without updating `handleLogin()` will break authentication entirely. If you rename a field, you MUST update the corresponding `getElementById()` call.

---

## 6. Recommended Phased Approach

### Phase A — Quick Win (1–2 hours, zero risk)

CSS-only changes to the login overlay. No HTML changes. No JS changes.

Changes:
- `.login-title`: Oswald font, orange color, larger size
- `.login-btn`: Orange background instead of blue, orange→blue hover transition
- `.login-field input:focus`: Orange border
- `.login-card`: Subtle orange glow box-shadow

Result: The login screen now reads as PureBrain. The AiCIV purple/cyan branding is gone. Cost: zero risk.

### Phase B — Branding Overhaul (3–5 hours, low risk)

HTML + CSS changes. No JS changes.

Changes:
- Replace the SVG logo with a PureBrain-branded mark (inline SVG using `--bright-orange` and `--light-blue` gradient — the orange neural orb pattern from the rest of the app is already used throughout the sidebar avatar)
- Update title text from "Sign in to AiCIV" to customer-facing language ("Enter Your AI Civilization" or similar, confirm with Jared)
- Update field labels to customer-facing language
- Update button text to "ENTER PORTAL" in Oswald uppercase
- Add a subtle tagline beneath the title ("Your AI civilization is waiting")
- CSS three-beat entrance animation (overlay opacity fade → title fade-in → form slide-up, all pure CSS)

Result: The overlay feels like arriving at something extraordinary. Customers who paid for an AI civilization get an entrance experience, not a login form.

### Phase C — Smart Pre-fill and Magic Link Support (follow-on, coordinate with Witness)

JS changes + Witness coordination required.

Changes:
- Pre-fill `loginAicivName` from localStorage on repeat visits
- Detect `?code=` query parameter on page load; if present, silently exchange it with the gateway and skip the form
- Graceful state message during code exchange ("Activating your civilization...")

Dependencies:
- Confirm with Witness whether the gateway's magic link endpoint (`/api/auth/create-login-code`) produces a `?code=` param that the frontend redeems, or whether redemption is handled gateway-side before the page even loads
- If redemption is frontend-side, Witness must document the endpoint that accepts the code

Result: First-time customer experience is seamless. They never see the login form on their first visit — they walk through a portal.

---

## Dependency Map

```
Phase A: Pure CSS → No dependencies → Ship immediately
Phase B: HTML + CSS → No dependencies → Ship after Phase A verified
Phase C: JS + gateway protocol → Blocked on Witness magic link spec → Coordinate via SSH channel
```

---

## File Change Inventory

| File | Lines Changed | Type | Risk |
|---|---|---|---|
| `/tmp/app-purebrain-ai/Testing-Purebrain/purebrain-frontend.html` | 1891–1986 (CSS block) | CSS modifications | Low |
| `/tmp/app-purebrain-ai/Testing-Purebrain/purebrain-frontend.html` | 2718–2746 (HTML block) | HTML replacement | Low |
| `/tmp/app-purebrain-ai/Testing-Purebrain/purebrain-frontend.html` | 3823–3881 (handleLogin JS) | Optional pre-fill addition | Low-Medium |
| `/tmp/app-purebrain-ai/Testing-Purebrain/aiciv_gateway.py` | No changes | — | None |
| `/tmp/app-purebrain-ai/Testing-Purebrain/aiciv-auth.json` | No changes | — | None |

---

## Answers to the Five Architecture Questions

**Q1: Scope — just HTML/CSS, or also handleLogin() JS?**
HTML and CSS for Phase A and B. handleLogin() requires no logic changes. Optional pre-fill of the name field is a Phase C micro-change. The function's auth contract is correct and stable.

**Q2: Auth flow — does it change for PureBrain customers?**
No. The gateway's name/secret model is the right model. PureBrain customers receive their credentials through the Witness birth pipeline — they do not self-register. The login form IS the right UX for returning visits. First-time visits via magic link are a Phase C concern that depends on Witness gateway behavior.

**Q3: New vs returning — separate Create Account and Sign In flows?**
No, not in this phase. The birth pipeline pre-creates credentials before the customer arrives. A "Create Account" flow would duplicate infrastructure that Witness already owns. The single form, properly branded, is correct for now.

**Q4: Gateway integration — what can we change client-side vs what needs gateway changes?**
Everything in this brief is client-side only. The gateway is stable. The only follow-on item that requires gateway coordination is magic link first-visit redemption (Phase C), and that requires Witness input on how their magic link `?code=` parameter is intended to be consumed by the frontend.

**Q5: Branding scope — just CSS/HTML swap, or deeper UX?**
Phase A: CSS/HTML swap — can be done today, zero risk, meaningful improvement.
Phase B: CSS/HTML swap + entrance animation choreography — 3–5 hours, low risk, premium feel.
Phase C: Smart pre-fill + magic link — requires Witness coordination, follow-on.

Recommendation: Ship Phase A immediately. Plan Phase B for the next build session. Block Phase C on Witness until the magic link redemption spec is confirmed.

---

*Architecture brief prepared by cto. No code was written. Implementation is assigned to full-stack-developer.*
