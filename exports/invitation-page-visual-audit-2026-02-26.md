# Visual Audit Report: Invitation Landing Page
**URL**: https://purebrain.ai/invitation/
**Date**: 2026-02-26
**Tester**: browser-vision-tester
**Viewport**: 1440x900 desktop
**Screenshots**: exports/screenshots/invitation-audit-2026-02-26/ (37 files)

---

## Overall Status: PASS with 4 issues to address

The page is structurally complete and functionally sound. All 7 sections present, all CTA links correct, Bonded highlighted as recommended, Michael Hancock testimonial present, Jared signature present. Four issues flagged below — one critical, one medium, two low.

---

## Section-by-Section Verification

### Section 1 — Hero
**Status**: PASS

**What I see**: Dark background (rgb(10,14,26) — slightly blue-tinted dark, not pure #0a0a0a but close), centered layout. Orange badge at top reading "PRIVATE ACCESS — INVITATION ONLY". Large bold headline "You've Been Invited." with a hard orange underline beneath it. Subtext "Your AI partner is waiting. 25 spots. Closes Tuesday." below.

**Countdown timer**: Present and rendered. Shows "00 : 00 : 00 : 00" with Days / Hours / Mins / Secs labels. Timer is functional in DOM (role="timer", aria-label present). The all-zeros display is expected in headless testing (JS timer needs real clock/deadline logic).

**CTA button**: Orange rounded button "Claim My Spot" with a small orb/dot indicator. Below it: "No commitment required to reserve. Lock in pre-launch pricing."

**Spots counter**: "2 of 25 spots claimed — 23 remaining" in orange text. Present and correct.

**Animated orbs**: Dark background gradient with subtle orange warm glow behind the hero text. The animated orbs/particles are CSS/canvas based — they would appear in a real browser but show as a static glow in headless mode.

**Screenshot**: FORCED-S1-hero.png (04-hero-section.png)

---

### Section 2 — Feature Cards ("What You're Getting Access To")
**Status**: PASS

**What I see**: Section header "WHAT YOU'RE GETTING ACCESS TO" in small orange caps. Large bold headline "An AI that knows your business. Remembers everything. Gets better every week." Body copy explaining the permanent memory differentiator.

**3 glassmorphism cards** (all rendered correctly):
1. "It Remembers Everything" — Memory icon (hexagonal/snowflake), description about permanent business context
2. "Shaped to Your Values" — Umbrella/shield icon, description about naming conversation calibration
3. "Gets Smarter Every Week" — Chart icon, description about weekly intelligence briefings

Cards have a dark translucent glass-effect border and consistent layout. All 3 visible and styled correctly.

**ISSUE**: Cards only appear after force-overriding `opacity: 0` from `pb-fade-in` class. In a real browser with JavaScript running, IntersectionObserver should trigger them. This is normal scroll-animation behavior. Verified DOM shows correct content.

**Screenshot**: FORCED-S2-feature-cards.png, FORCED-S2b-feature-cards-lower.png

---

### Section 3 — Awakening Experience ("Your First Conversation Changes Everything")
**Status**: PASS

**What I see**: Left column — "THE PROCESS" label in orange caps, H2 "Your First Conversation Changes Everything", body text explaining the Awakening conversation. 4-step numbered timeline:
1. "You Have a Real Conversation"
2. "Your Values Are Mapped"
3. "Your Partner Is Named"
4. "The Partnership Begins"

Each step has a blue numbered circle, bold title, and body description.

**Right column — Chat mockup**: "PUREBRAIN AWAKENING" header with green live dot. Chat interface visible. On desktop at 1440px, the 2-column layout (timeline left, chat mockup right) is rendering correctly.

**Screenshot**: FORCED-S2b-feature-cards-lower.png (shows transition), FORCED-S3-awakening-pt1.png

---

### Section 4 — Pricing ("Pre-Launch Pricing — Locked In For Life")
**Status**: PASS

**What I see**: "CHOOSE YOUR ACCESS LEVEL" in small orange caps. H2 "Pre-Launch Pricing — Locked In For Life". Subtext "This pricing exists only for the 25 people in this room. When we open to the public, it's gone."

**4 tier cards** all present and correctly styled:

| Tier | Price | Badge | CTA |
|------|-------|-------|-----|
| AWAKENED | $79/mo | None (muted card) | "Learn More →" |
| BONDED | $197/mo struck, **$149/mo** | "MOST POPULAR — SAVE $47" (orange) | "Claim Bonded Access" (orange button) |
| PARTNERED | $499/mo | None | "Learn More →" |
| UNIFIED | $999/mo | "ENTERPRISE" (blue) | "Learn More →" |

**Bonded highlighted**: YES — `pb-featured` class, orange "MOST POPULAR — SAVE $47" badge above card, orange CTA button, strikethrough $197/mo showing savings. This is the recommended tier and it's visually dominant.

**All CTA links**: All 7 CTA links across the page point to `https://purebrain.ai/#awakening`. Correct.

**Screenshot**: FORCED-S4-pricing-pt1.png (shows all 4 cards + urgency text starting), FORCED-S4-pricing-pt2.png (card details + testimonial header)

---

### Section 5 — Michael Hancock Testimonial ("From Our First Partner")
**Status**: PASS

**What I see**: "FROM OUR FIRST PARTNER" label in orange caps. Large open-quote mark. Italic testimonial text:

> "I've tried every AI tool on the market. This is the first time I felt like the AI actually understood what I was trying to build. The naming conversation alone changed how I think about the partnership."

Attribution: Blue-grey avatar circle with "MH" initials, "Michael Hancock" in bold white, "General Counsel" in grey below.

Badge: "VERIFIED PUREBRAIN PARTNER — AI PARTNER: METIS" in a small outlined badge. Nice trust signal.

Card has rounded dark border, clean centered layout. Readable and professional.

**Screenshot**: FORCED-S4-pricing-pt2.png (testimonial starts), FORCED-S5-testimonial.png

---

### Section 6 — Urgency/Scarcity ("Only 25 Spots. No Exceptions.")
**Status**: PASS

**What I see**: "THE REALITY" label in orange caps. Large bold H2 "Only 25 Spots. No Exceptions."

"2 of 25 spots claimed — 23 remaining" in orange — live counter visible.

**3 fact blocks** with orange left border:
1. "The pricing is pre-launch only." — "$149/mo rises to $197/mo on March 4th — the day after this invitation closes. The price you lock in today follows you forever."
2. "The 25-spot limit is real." — Explanation of white-glove onboarding capacity ceiling
3. "Tuesday is the hard deadline." — "When the countdown hits zero, this page closes. We will not extend, accommodate, or make exceptions."

**Price Lock Guarantee** box at bottom: Lock icon, "Price Lock Guarantee", "Your pre-launch rate is protected for as long as you stay active."

**Note on dots visual**: The DOM shows `has25Spots: true` (text confirmed) but the CSS dot-grid element (`.pb-dots-grid`) was not found in DOM inspection. The 25-dot visual grid may be rendered differently or may be in a different section. The text "25 spots" is confirmed present throughout the page.

**Screenshot**: FORCED-S4-pricing-pt3.png (urgency section clearly visible)

---

### Section 7 — Final CTA + Jared Signature ("Don't Let Someone Else Take Your Spot.")
**Status**: PASS

**What I see**: "YOUR INVITATION EXPIRES TUESDAY" in small orange caps. H2 "Don't Let Someone Else Take Your Spot." with a large bold condensed typeface that's visually impactful.

Body copy: "You were invited because we believe in what you're building. This offer won't be re-extended. The 25 people who act are the founding partners — their pricing and access level set the standard for everyone who comes after."

**Primary CTA button**: Orange rounded button "Claim My Spot — $149/mo →" — prominent, centered.

**Trust icons below button**: "No setup fees", "Cancel anytime", "Price locked for life" in small text with checkmarks.

**Second countdown timer**: "00 : 00 : 00 : 00" — Days/Hours/Mins/Secs — functional DOM, shows zeros in headless testing.

**Jared Sanborn signature block**: Orange circle avatar "JS", quote "I picked you because I believe in what you're building.", "Jared Sanborn, Founder — PureBrain.ai" in blue link text.

**Footer**: "Privacy Policy | Terms of Service — © 2026 Pure Technology Inc."

**Aether footer bar**: "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai | Why Choose PureBrain? | Mission & Values | Migrate"

**Screenshot**: FORCED-S7-final-cta-upper.png, FORCED-S7-bottom.png

---

## Issues Found

### ISSUE 1 — CRITICAL: Countdown Timer Shows All Zeros
**Severity**: Critical
**Section**: Hero + Final CTA (both countdown instances)
**What I see**: Both countdown timers display "00 : 00 : 00 : 00" — Days, Hours, Mins, Secs all zero.

**Root cause**: The deadline date in the JavaScript countdown is either:
(a) Set to a date in the past (timer already expired), or
(b) Not correctly initialized (hardcoded date that hasn't been updated for this invitation)

**Visual impact**: A real user landing on this page RIGHT NOW would see "00 : 00 : 00 : 00" — implying the offer has already expired. This is a conversion killer. The page text says "Closes Tuesday" but the timer shows expired.

**Fix needed**: Check and update the deadline date in the countdown JavaScript. Should be set to next Tuesday (March 3 or 4, 2026 based on context — the urgency copy says "$149/mo rises to $197/mo on March 4th").

**Code to check**: Look for `const deadline = new Date(...)` or similar in the page's inline `<script>` block in the WP HTML widget.

---

### ISSUE 2 — MEDIUM: Awakening Section Chat Mockup Not Loading Content in Headless (Possible Real Issue)
**Severity**: Medium — needs real browser verification
**Section**: Section 3 (pb-awakening)
**What I see**: The chat mockup container (`pb-chat-mockup`) is in the DOM and visible, but the chat body content (chat bubbles/messages) appears empty in the headless screenshot — only the "PUREBRAIN AWAKENING" header bar is visible.

**What to verify**: Open in a real browser and scroll to this section. The chat animation (typewriter effect of sample conversation) should be triggered by IntersectionObserver. If chat messages appear in real browser, this is a headless testing artifact. If not, the chat content JS is broken.

**Screenshot reference**: FORCED-S2b-feature-cards-lower.png (chat mockup visible but body appears empty at load point)

---

### ISSUE 3 — LOW: Dots Grid Visual Not Found in DOM
**Severity**: Low
**Section**: Urgency section
**What I see**: The text "2 of 25 spots claimed — 23 remaining" is present and correct. However, the described "25-dot spots counter" visual grid (the visual representation of 25 dots with some filled) was not found as a DOM element (queried `.pb-dots-grid`, `[class*="dots-grid"]`).

**Impact**: If the 25-dot visual grid is a design intention, it may be missing from the current implementation. The text counter works fine, but the dot visualization adds social proof visually.

**Action**: Check if the dot grid is intentionally omitted from this page or if it was removed during implementation. The text counter ("2 of 25 claimed") is clear and functional without it.

---

### ISSUE 4 — LOW: Background Color Slight Deviation
**Severity**: Low — cosmetic
**What I see**: Body background computed as `rgb(10, 14, 26)` — this is a dark navy blue rather than pure `#0a0a0a` (which would be `rgb(10, 10, 10)`). The difference is very subtle visually (dark blue vs pure black) but worth noting if strict brand compliance is required.

**Impact**: Visually the page reads as dark/premium — the slight blue-navy tint actually looks intentional and high-end. Not a real problem unless the spec requires pure black.

---

## CSS / Brand Colors Audit

| Check | Result |
|-------|--------|
| Brand CSS variables defined | YES — `--blue: #2a93c1; --orange: #f1420b` confirmed in stylesheet |
| Orange (#f1420b) in use | YES — CTA buttons, badges, accent labels, spots counter, urgency fact titles, orb animation |
| Blue (#2a93c1) in use | YES — numbered step circles, testimonial badge, tier labels, Jared's name link |
| Dark background | YES — `rgb(10, 14, 26)` (near-black, blue-tinted) |
| No broken images | YES — 0 broken images found (1 total image on page) |
| No layout errors | YES — no `[class*="error"]` elements |

---

## Console Errors

8 console errors captured — all are **Content Security Policy (CSP) violations**, not application errors:

1. GTM script blocked by CSP (x2)
2. GoDaddy analytics/tracking script blocked (x2 each: `scc-c2.min.js`, `tccl-tti.min.js`)
3. Blob worker creation blocked (x2)

**Assessment**: These CSP errors are the known GoDaddy hosting/Cloudflare tunnel conflict that's been previously documented. They do not affect page functionality or user experience. Google Tag Manager (GTM) may not be firing on this page, which means analytics tracking for this specific page could be missing — worth checking in GTM/GA4 to confirm conversion events are tracked.

**No JavaScript application errors.** Zero errors relating to page functionality.

---

## CTA Link Verification

All 7 CTA links on the page:

| CTA Text | href | Status |
|----------|------|--------|
| Claim My Spot (hero) | https://purebrain.ai/#awakening | CORRECT |
| Learn More → (Awakened card) | https://purebrain.ai/#awakening | CORRECT |
| Claim Bonded Access (Bonded card) | https://purebrain.ai/#awakening | CORRECT |
| Learn More → (Partnered card) | https://purebrain.ai/#awakening | CORRECT |
| Learn More → (Unified card) | https://purebrain.ai/#awakening | CORRECT |
| Claim My Spot — $149/mo (final CTA) | https://purebrain.ai/#awakening | CORRECT |
| Claim Yours → | https://purebrain.ai/#awakening | CORRECT |

All 7 point to the correct URL. Zero broken CTA links.

---

## Page Metadata

| Metric | Value |
|--------|-------|
| Page title | "Invitation - Pure Brain" |
| URL | https://purebrain.ai/invitation/ |
| Total page height | 6219px |
| Sections | 7 |
| Total links | 15 |
| Total images | 1 |
| Broken images | 0 |
| Console errors | 8 (all CSP, no app errors) |

---

## Priority Actions

**Immediate (before sharing with invitees):**
1. FIX THE COUNTDOWN TIMER — It shows 00:00:00:00. Set deadline to correct date (Tuesday, March 4 per the page copy).

**Before wider distribution:**
2. Verify chat mockup animation fires in real browser (open incognito, scroll to Section 3)

**Nice to have:**
3. Verify if 25-dot grid was intentionally omitted or accidentally dropped
4. GTM/GA4 — confirm conversion events tracking for this page despite CSP errors

---

## Screenshot Index

| File | Section |
|------|---------|
| 01-password-form.png | Password gate |
| 02-after-password-viewport.png | Hero (first view post-auth) |
| 04-hero-section.png | Hero centered |
| FORCED-S1-hero.png | Hero (animations forced) |
| FORCED-S2-feature-cards.png | Feature cards section header |
| FORCED-S2b-feature-cards-lower.png | 3 glass cards + awakening start |
| FORCED-S3-awakening-pt1.png | Awakening section (2-col layout) |
| FORCED-S3-awakening-pt2.png | Step 4 + pricing section start |
| FORCED-S4-pricing-pt1.png | All 4 pricing cards |
| FORCED-S4-pricing-pt2.png | Card details + testimonial |
| FORCED-S4-pricing-pt3.png | Urgency/scarcity section |
| FORCED-S5-testimonial.png | Testimonial + urgency |
| FORCED-S6-urgency.png | Urgency + final CTA start |
| FORCED-S7-final-cta-upper.png | Final CTA + Jared signature |
| FORCED-S7-bottom.png | Bottom + footer |
| FORCED-full-page.png | Complete page |

---

**Report by**: browser-vision-tester
**Session completed**: 2026-02-26
