# Invite-Only Landing Page UX — PureBrain.ai

**Date**: 2026-02-26
**Agent**: feature-designer
**Type**: synthesis
**Topic**: Premium invite-only landing page for high-ticket B2B SaaS — Bonded tier launch
**Confidence**: high
**Tags**: ux, purebrain, landing-page, conversion, premium, glassmorphism, invite-only, urgency

---

## Context

Designed a complete UX spec for a single-page invite-only landing page targeting 25 Bonded ($149/mo) signups by Tuesday. Page is password-protected on WordPress. Targets warm leads (executives/founders in Jared's network). Spec written to `/home/jared/projects/AI-CIV/aether/exports/invite-only-page-ux-spec.md`.

---

## Key Patterns Discovered

### 1. Narrative Arc Beats Feature List for High-Ticket B2B

Scroll order should follow the buyer's psychological journey, not the product's feature hierarchy:
1. Status (you were invited — you are chosen)
2. Understanding (what is this, why is it different)
3. Experience (exactly what happens — remove unknown)
4. Decision (pricing — clear, anchored, recommended)
5. Trust (one real person's real words)
6. Urgency (scarcity + deadline, stated as calm facts)
7. Action (final CTA — inevitable, not pushy)

This arc outperforms feature-dump layouts for anything over $99/mo.

### 2. Countdown Timer Placement Rule

Place timer in hero AND final CTA only. Do NOT repeat in middle sections. Seeing urgency in every section creates "urgency fatigue" — users learn to ignore it. Two placements (top + bottom) bookend the experience correctly.

### 3. Single Testimonial With Specific Detail > Multiple Generic Quotes

Michael Hancock's testimonial is powerful not because of star ratings but because of the specific detail: his AI partner is named Metis. No fabricated review could include that. Specificity is proof of authenticity.

Format: single large card, full reverence, no stars, verified partner badge with AI name.

### 4. Velvet Rope Psychology Applied to Page Structure

The pre-headline badge (`PRIVATE ACCESS — INVITATION ONLY`) does psychological work before the user reads anything. Being invited elevates status. The spots counter (dots filling in) makes scarcity concrete and visual rather than just claimed.

### 5. Bonded Tier Visual Anchoring

At `scale(1.03)` with glowing orange border, the Bonded card creates a visual focal point the eye finds first. The SAVE $47 badge does the math. The strikethrough price validates the discount without screaming "SALE."

Adjacent tiers (Awakened below, Unified above) serve as anchors — Awakened makes Bonded accessible, Unified makes Bonded reasonable.

### 6. Mobile Sticky Bar Pattern

`position: fixed; bottom: 0` bar showing `[N] spots left — Claim Yours →` in orange. Disappears when user scrolls into final CTA section via IntersectionObserver. High-impact conversion pattern for mobile users who don't scroll to the bottom.

### 7. Chat Mockup as Emotional Anchor

A static HTML/CSS animated chat conversation (3 messages, fade-in staggered at 400ms) makes the "Awakening" abstract concrete. Hide on mobile — too small, and it costs load time. Desktop only.

### 8. CSS Architecture for WordPress

- Wrapper: `#pb-invite-page`
- All CSS scoped to that ID
- `!important` on every layout-critical property
- Self-contained in one `<!-- wp:html -->` block
- Google Fonts loaded via `<link>` inside the block
- Zero external JS libraries
- Countdown in vanilla JS (under 20 lines)

---

## Files

- Full UX spec: `/home/jared/projects/AI-CIV/aether/exports/invite-only-page-ux-spec.md`
- Prior assessment page spec: `/home/jared/projects/AI-CIV/aether/to-jared/ai-adoption-assessment-design.md`
- Prior testimonial component: `/home/jared/projects/AI-CIV/aether/exports/purebrain-content-blocks/testimonials.html`

---

## Open Questions for Jared

1. Michael's actual testimonial quote — need his real words before launch
2. Michael's title and company — needed for the testimonial card
3. The correct Tuesday EOD datetime for the countdown (timezone?)
4. How many spots are already claimed at launch time? (sets dots counter)
5. Where does the Bonded CTA button link? (purebrain.ai/#awakening or a dedicated checkout URL?)
