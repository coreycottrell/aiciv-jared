# Graham Martin Mini-Site — Phone Language Removal + Mini-Nav
**Date**: 2026-03-01
**Type**: content-update + navigation-build
**Agent**: dept-systems-technology

## What Was Done

Two updates to the Graham Martin mini-site at purebrain.ai.

---

## UPDATE 1: Casino AI Page — Phone Language Removed (WP ID 1153)

### Jared's Direction
"we dont need to talk about the phone in Graham's presentation. its more for inspiration of things we can help Casinos with in general but eventually moving to phones!"

### Changes Made

| Location | Before | After |
|----------|--------|-------|
| Hero subtitle | "Branded phones generating $1,792 per device per year" | "AI-driven revenue of $1,792 per engaged user per year" |
| Hero stat label | "Revenue per device / year" | "AI revenue per user / year" |
| Section 01 title | "The Device" | "The AI Platform" |
| Section 01 h2 | "Don't give players an app. Give them a key to your world." | "Give them a complete AI experience." |
| Section 01 description | "casino-branded 5G smartphone" | "unified AI platform...across every touchpoint" |
| Phone mockup card | "Casino Branded Phone" + phone icon | "Casino AI Platform" + brain icon |
| Revenue breakdown labels | "Mobile Advertising", "App & Mobile Monetization", "Mobile Commerce" | "Digital Advertising", "App & Digital Monetization", "Digital Commerce" |
| Revenue per user labels | "$1,792/device/yr" | "$1,792/user/yr" |
| Right column card 1 | "The phone is the guest" | "AI knows who the guest is across every touchpoint" |
| Right column card 4 | "giveaways drive device adoption. Each device holder" | "referral programs drive platform adoption. Each engaged user" |
| Revenue projections desc | "Initial device investment of $700 per unit is fully recouped via the phone's earnings" | "AI generates compounding revenue per engaged user" |
| Revenue projection cards | "$179 / device / yr", "$358 / device / yr", "$537 / device / yr" | "$179 / user / yr", "$358 / user / yr", "$537 / user / yr" |
| Revenue projection sublabel | "Casino 10% revenue share" | unchanged |
| Biometric section | "eliminate the problem permanently at the device level" | "at the identity layer" |
| Personalization section | "Guests with Pure Tech phones bypass room check-in" | "Guests bypass room check-in via biometric identity" |
| VSBLTY Camera Commerce | "Point your phone camera at anything" | "AI-powered camera commerce lets guests scan anything" |
| Programmable slots | "biometrics or the gaming phone" | "biometric identity verification" |
| Future slots card | "camera in their gaming phone" | "AI enables consumers...via camera commerce" |
| Responsible gambling | "The branded phone facilitates" | "The AI platform facilitates" |

### Added: Future Vision Callout
At the end of Section 01, added a subtle orange-tinted callout box:
- Title: "The AI experience, delivered on a casino-branded device"
- Body: Positions phone as the natural evolution of the platform, not the core offering
- Framing: "The capabilities come first. The device amplifies them."

---

## UPDATE 2: Mini-Site Navigation (All 5 Pages)

### Jared's Direction
"Are these all linked together via a menu? and the front page somehow? If not make those connections. again a mini site within a site"

### Implementation
- Added `#gm-mini-nav` fixed bar that sits at `top: 61px` (below the main `#gm-nav`)
- Style: dark glass-morphism `rgba(8,10,18,0.92)`, backdrop blur, same brand language
- Pills: horizontal scrollable pill tabs on mobile, centered on desktop
- Active page highlighted in orange (`rgba(241,66,11,0.15)` bg + orange border)
- Inactive pills: subtle muted text, hover shows glass effect
- Body padding-top: 104px to account for double fixed navs

### Pages and Active States

| Page | WP ID | Active Pill |
|------|-------|-------------|
| purebrain-for-graham-martin/ | 1150 | "Overview" (orange) |
| purebrain-for-graham-martin-casino-ai/ | 1153 | "Casino AI" (orange) |
| purebrain-for-graham-martin-chairman-intelligence/ | 1154 | "Chairman" (orange) |
| purebrain-for-graham-martin-virya-intelligence/ | 1155 | "Virya VC" (orange) |
| purebrain-for-graham-martin-responsible-gambling/ | 1156 | "Responsible Gambling" (orange) |

---

## Deployment Results

All 5 pages deployed HTTP 200, all 5 pages verified live HTTP 200.

---

## Source Files

- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-casino-ai.html` (v2.0 — phone language removed)
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-investor-page.html` (mini-nav added)
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-chairman-intelligence.html` (mini-nav added)
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-virya-intelligence.html` (mini-nav added)
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-responsible-gambling.html` (mini-nav added)

## Pattern: Mini-Nav Injection
- CSS injected before last `</style>` tag
- HTML injected immediately after closing `</nav>` of `#gm-nav`
- Separate active state per page via per-file class injection
- Mobile: horizontal scroll, label hidden, smaller pills
