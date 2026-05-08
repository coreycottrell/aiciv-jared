# Overnight Task 3 — PureBrain Homepage CRO Analysis
**Date**: 2026-05-08
**Agent**: conversion-rate-optimizer (CRO)
**Source**: Live fetch of https://purebrain.ai/ (16,341 lines HTML, 643 KB)
**Prior**: 2026-04-16 v2 audit (`.claude/memory/agent-learnings/conversion-rate-optimizer/2026-04-16--homepage-cro-v2-pricing-mobile-competitor.md`)

---

## 1. Page Audit

### Above-the-fold (hero, lines 7904–7975)

| Element | Current | Issue |
|---|---|---|
| H1 (7933) | "PURE BRAIN" (logotype only) | No value prop in H1 |
| Subhead (7937) | "Your Brain. Your AI. Actual Intelligence." | Tagline; doesn't say what it does |
| Description (7941) | "The AI that matters most!" | Vague; no outcome |
| Secondary desc (7945) | "Not another chatbot... discovers its own identity through conversation with you. Then executes across email, social, marketing strategy, research, and beyond." | First concrete promise — buried 4 lines deep |
| Primary CTA (7951) | "Awaken Your PURE BRAIN" → `scrollToChat()` | No friction-reducer ("free", "no card", "5 min") |
| Secondary CTA (7960) | "Watch Demo" → video modal | OK |
| Trust strip / logos | **None** | Jasper has 20+, Copy.ai has 8 + "17M users" in first viewport |
| Quantified outcome | **None** | Copy.ai shows "$16M savings", "5x more meetings" |

**Verdict**: Hero is atmospheric (vortex, particles, breathing pulse) but **fails the "what + why now + why me" test**. A first-time visitor leaves the hero unsure what they're being asked to do.

### Below-the-fold flow (in render order)

1. Marquee (7980): 9 capability chips loop. Decorative.
2. About (8007): "An AI That Becomes Yours" — 3 feature cards.
3. Demo section (8068)
4. Value pyramid (8094)
5. Capabilities (8130)
6. AI Tim Cook promo (8229)
7. **Awakening Chat (8253)** with collapsible "What to expect — about 5 minutes" panel (8403). **The conversion engine.**
8. Value section (8513)
9. **Pricing (8600)**: 4 tiers + consent gate + 30-day guarantee
10. Comparison table (8876)
11. Timeline / What Happens Next (9074)
12. **Testimonials (9108)**: 22 quotes
13. Calculator CTA (9212), Referral program (9314)
14. Footer (9938)

**Critical structural gap**: Testimonials sit at section 12 of 13. By the time visitors reach social proof, they've already passed pricing. **Trust evidence arrives after the trust decision is made.**

### Mobile (CSS at 213, 1081, 1357, 1460, 1530, 1674; breakpoints 400/480/500/576/768/900/1024/1280)

- Same 643 KB HTML to mobile (no adaptive payload)
- Pricing grid stacks single-column below 768 px → ~1,800 px scroll for 4 tiers
- Hero video + particles + 6 vortex rings render on mobile (battery/data cost)
- Waitlist modal is **7 fields with a textarea** (7757–7813) — high friction
- Consent checkbox (8627) is **pre-checked** (`checked` attribute) — GDPR risk flagged in v2 still unresolved

### Trust signals present

- 30-day guarantee badge (8617)
- Privacy/Terms links in footer + consent
- Microsoft Clarity (`viy9bnc56x`) and GTM both installed
- **Missing**: SOC2/security badge, customer logo bar, press mentions, active-user count

### WordPress backend probe (Track 3)

- `/wp-json/wp/v2/pages` → 404
- `/wp-admin/` → 404
- `/wp-login.php` → 404

This is **CF Pages serving static HTML, not live WordPress**. Backend analytics MUST come from:
- **Microsoft Clarity dashboard** (ID `viy9bnc56x`) — heatmaps, scroll depth, rage clicks, dead clicks, session recordings
- **Google Tag Manager** container — GA4 events
- **Google Search Console** — impressions, CTR, top queries

**Action for ${HUMAN_NAME}**: open Clarity → segment "First-time" + "Mobile" + "Bounced before pricing" → look for (1) hero scroll depth, (2) rage clicks on consent checkbox, (3) dead clicks on marquee chips, (4) waitlist-form abandonment recordings.

---

## 2. Conversion-Funnel Mapping

| Stage | Sections | Status |
|---|---|---|
| **Attract** | Hero, Marquee | Weak — atmospheric, no promise |
| **Engage** | About, Capabilities, Tim Cook, **Chat** | Chat is strong; preceding sections delay it |
| **Convince** | Value, Comparison, Timeline, Testimonials | Testimonials misplaced (after pricing) |
| **Convert** | Pricing (4 tiers + guarantee), Waitlist (7 fields) | Pricing OK desktop / painful mobile; waitlist form too long |

---

## 3. TOP 7 A/B Tests (Ranked Impact × Effort)

### T1 — Trust strip in hero (HIGH × LOW)
- **Hypothesis**: A single-line proof strip below the hero CTA ("Trusted by builders at VSBLTY, Red Consulting, Pure Marketing — 22+ live partners") + 4 small headshots increases scroll-to-chat rate by 15–25%.
- **Control**: hero as-is. **Treatment**: hero + proof strip.
- **Metric**: % sessions reaching `#awakening` (Clarity scroll event)
- **Sample**: 4,000 sessions/arm (~7–10 days)
- **Lift**: +15–25%. **Effort**: LOW.

### T2 — Hero CTA friction-reducer (HIGH × LOW)
- **Hypothesis**: Adding "No credit card · ~5 minutes" sub-label under "Awaken Your PURE BRAIN" lifts CTA click-through 8–15%.
- **Control**: button alone. **Treatment**: button + sub-label.
- **Metric**: click-rate on `.btn--primary` in hero. **Sample**: 3,000/arm. **Lift**: +8–15%. **Effort**: LOW.

### T3 — Move testimonials above pricing (HIGH × LOW)
- **Hypothesis**: 6 best testimonials between Comparison and Pricing increases pricing CTA click rate 10–20%. Currently 22 testimonials sit AFTER pricing — too late.
- **Control**: current order. **Treatment**: 6-card strip before pricing; remaining 16 stay below.
- **Metric**: pricing CTA click rate. **Sample**: 5,000/arm. **Lift**: +10–20%. **Effort**: LOW.

### T4 — Pricing CTA copy: replace "Activate Keen Now" (HIGH × LOW)
- **Hypothesis**: "Keen" is internal; visitors don't understand. "Start with [Tier]" lifts click-through 12–25%.
- **Control**: "Activate Keen Now". **Treatment**: "Start with Awakened" / "Start with Partnered" / "Start with Unified" + arrow.
- **Metric**: pricing CTA click rate. **Sample**: 4,000/arm. **Lift**: +12–25%. **Effort**: LOW.

### T5 — Waitlist form: 7 → 2 fields (MED × LOW)
- **Hypothesis**: Reducing required fields from 5 (Name, Email, 1–5 rating, Use case textarea, Urgency select) to 2 (Name + Email) with qualification asked AFTER submit lifts submit rate 30–60%.
- **Control**: 7-field form. **Treatment**: 2-field, 2-step.
- **Metric**: submits / opens. **Sample**: 1,500/arm. **Lift**: +30–60%. **Effort**: LOW.

### T6 — Hero subhead: outcome-led (MED × LOW)
- **Hypothesis**: "Your AI partner that runs your email, content, and research while you focus on what only you can do" outperforms identity-led tagline on chat-start rate 8–15%.
- **Control**: current tagline. **Treatment**: outcome-led subhead; tagline becomes smaller eyebrow.
- **Metric**: `startConversation()` fired. **Sample**: 3,000/arm. **Lift**: +8–15%. **Effort**: LOW.

### T7 — Mobile pricing carousel (MED × MED)
- **Hypothesis**: Replace mobile 4-card vertical stack (~1,800 px scroll) with snap-scroll horizontal carousel; lifts mobile pricing CTA click rate 15–25%.
- **Control**: vertical stack. **Treatment**: horizontal swipe, dot pagination, Awakened first.
- **Metric**: mobile pricing CTA click rate. **Sample**: 3,000/arm. **Lift**: +15–25% mobile. **Effort**: MED (CSS scroll-snap + JS).

---

## 4. Competitive Positioning

| Element | PureBrain | Jasper | Copy.ai |
|---|---|---|---|
| Hero promise | Identity | Outcome (marketing agents) | Outcome (GTM platform) |
| Logo bar | 0 | 20+ | 8 + "17M users" |
| Quantified outcome | None | "10K hours saved" | "$16M savings" |
| Hero form fields | 0 | 0 | 0 |
| Live demo above fold | No (chat mid-page) | No | No |

**Where PureBrain wins**:
- **Live in-page chat** — Jasper/Copy.ai gate behind "Get a Demo". PureBrain lets visitors talk to the product immediately. **Surface this harder.**
- **30-day relationship guarantee** with refund — neither competitor offers anything comparable.
- **22 named testimonials with LinkedIn links** — more depth than either competitor.

**Where competitors win**: hero outcome clarity, trust strip in first viewport, quantified social proof.

**Positioning gap**: PureBrain's real differentiator — "your AI develops a unique identity through conversation with you" — is buried as the fourth line of body copy. **Lead with it.**

---

## 5. Quick Wins (Ship Before 8 AM ET)

1. **Pricing CTA fix** — replace 3 instances of "Activate Keen Now" → "Start with [Tier]" (lines 8679, 8735, 8797). 5 min. Verify "Keen" isn't a constitutional brand first.
2. **Hero CTA micro-copy** — add "No credit card · ~5 minutes" under primary CTA (7951). 10 min.
3. **Uncheck consent checkbox default** — line 8627 has `checked`. Removing it = GDPR-correct + explicit micro-commitment improves opt-in quality. 1-line fix.

All three are spec-only here; ${HUMAN_NAME} or ST# ships via git → staging → prod.

---

## 6. Strategic Plays (1–2 Week)

1. **Hero rebuild combining T1 + T6** (trust strip + outcome subhead) as one experiment via 50% CF Workers cookie split. Build 3d / test 10d.
2. **DOM reorder: testimonials before pricing** (T3). 22 testimonials are the strongest unactivated asset. Build 1d / test 7d.
3. **Waitlist 2-step rebuild** (T5). Current 7-field form is a mobile killer. Build 2d / test 7d.
4. **Mobile pricing carousel** (T7). Build 3d / test 10d.
5. **Clarity heatmap audit (data-first)** — before more A/B tests, pull 7 days of Clarity data segmented mobile/desktop and bounced/converted. ~1 hour of ${HUMAN_NAME}'s time; informs next 4 weeks of testing better than any static analysis.

---

## Memory Search Results
- Searched: `.claude/memory/agent-learnings/conversion-rate-optimizer/`
- Found: 1 prior — `2026-04-16--homepage-cro-v2-pricing-mobile-competitor.md`
- Applying: persistent unresolved issues from v2 (consent pre-checked, "Keen" CTAs, 7-field form) → these have higher priority than new theories because they've already failed to ship.

## Memory Written
Path: `.claude/memory/agent-learnings/conversion-rate-optimizer/2026-05-08--homepage-cro-v3-trust-strip-form-friction.md`
Type: operational + teaching
Topic: CRO v3 — testimonial misplacement, hero outcome-clarity gap, WP-not-public confirmation

---

**Constraints honored**: read-only, exact line numbers cited, falsifiable hypotheses with metrics + samples, no live edits, no overnight payment-page changes.
