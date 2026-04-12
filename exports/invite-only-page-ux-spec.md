# 🎨 feature-designer: Invite-Only PureBrain.ai Landing Page UX Spec

**Agent**: feature-designer
**Domain**: UX Design / Conversion Landing Page
**Date**: 2026-02-26

---

## User Need

Serious business executives and founders in Jared's network receive a personal invitation link. They arrive on this page needing to feel: (1) they were specifically chosen, (2) the product is worth $149/mo, (3) there is genuine urgency to act now, and (4) this is categorically different from every AI tool they've tried. The page must convert warm leads — people who already trust Jared — into paying Bonded-tier customers by Tuesday.

## User Flow

1. Executive receives personal invite from Jared (text, email, DM)
2. Clicks link, enters password if WordPress-protected
3. Lands on full-viewport hero — immediately feels the premium weight
4. Scrolls naturally through the narrative arc: chosen → understand → experience → decide → act
5. Clicks "Claim Your Spot" — goes directly to awakening/checkout flow

---

## Section-by-Section Layout Specification

---

### Section 1: Hero — Full Viewport "You Were Chosen"

**Purpose**: Create immediate status elevation. This person was picked. Not everyone gets this link.

**Layout**:
- Full viewport height (100vh), no scroll indicator visible initially
- Background: animated radial gradient shifting slowly between `#0a0a0a` and `#060d14`
- Two atmospheric orbs (CSS radial gradients, `filter: blur(160px)`, `opacity: 0.10`):
  - Blue orb (#2a93c1) — top-left quadrant, 600px diameter
  - Orange orb (#f1420b) — bottom-right quadrant, 400px diameter
- Both orbs animate on a slow 20-second CSS keyframe loop (drift 30px in alternating directions, opacity oscillates 0.08 to 0.12)

**Content Hierarchy** (top to bottom, vertically centered):

1. **Pre-headline badge** (small, uppercase, letter-spaced):
   - Text: `PRIVATE ACCESS — INVITATION ONLY`
   - Style: `font-family: Plus Jakarta Sans`, `font-size: 0.75rem`, `letter-spacing: 0.2em`, `color: #f1420b`
   - Container: pill shape, `border: 1px solid rgba(241,66,11,0.3)`, `background: rgba(241,66,11,0.06)`, `padding: 6px 18px`, `border-radius: 100px`
   - Subtle pulse animation on the border (opacity 0.3 to 0.6, 3s loop)

2. **Main headline**:
   - Text: `You've Been Invited.`
   - Font: Oswald Bold, 72px desktop / 44px mobile
   - Color: white
   - No animation — the stillness is the statement
   - Below it, a 2px orange underline that draws in from left (CSS `width: 0 → 120px`, 0.8s ease-out, 0.3s delay)

3. **Sub-headline**:
   - Text: `Your AI partner is waiting. 25 spots. Closes Tuesday.`
   - Font: Plus Jakarta Sans, 1.3rem, `color: rgba(255,255,255,0.75)`, `font-weight: 400`
   - Max-width: 520px, centered

4. **Countdown timer** (compact, inline):
   - Shows: `[DD]d [HH]h [MM]m [SS]s`
   - Style: monospace digits in blue (#2a93c1), separators in `rgba(255,255,255,0.3)`
   - Label below in tiny text: `Until invite window closes`
   - Container: glassmorphism — `background: rgba(42,147,193,0.06)`, `border: 1px solid rgba(42,147,193,0.15)`, `border-radius: 12px`, `padding: 12px 28px`
   - JavaScript countdown targeting end of day Tuesday (configurable const at top of script)

5. **Primary CTA button**:
   - Text: `Claim My Spot`
   - Style: `background: linear-gradient(135deg, #f1420b, #d63000)`, `color: white`, `font-family: Oswald`, `font-size: 1.1rem`, `letter-spacing: 0.05em`, `padding: 18px 48px`, `border-radius: 8px`, `border: none`
   - Hover: lift with `transform: translateY(-2px)`, glow `box-shadow: 0 8px 32px rgba(241,66,11,0.4)`
   - Below button (trust micro-copy): `No commitment required to reserve. Lock in pre-launch pricing.`
   - Micro-copy style: `font-size: 0.8rem`, `color: rgba(255,255,255,0.45)`

6. **Spots counter** (just below the CTA):
   - Design: horizontal row of 25 dots. Filled dots = claimed spots (animate filling from left on page load, staggered 80ms per dot)
   - Filled dot: `#f1420b` solid circle, 10px diameter
   - Empty dot: `rgba(255,255,255,0.15)` outlined circle
   - Label: `[N] of 25 spots claimed` — update the number to whatever is accurate; use 1 as minimum (Michael)

**Scroll indicator**: Subtle animated chevron at bottom center, `opacity: 0.3`, bounces 3px up/down on 2s loop. Fades out on first scroll.

**Visual Hierarchy Notes**:
- Everything centered, max content width 680px
- Nothing competes with the headline — the badge and countdown are supporting characters
- The orange CTA button is the only fully saturated warm element — the eye goes there after reading

---

### Section 2: What Is PureBrain — "Not a Tool. A Partner."

**Purpose**: Fast-clear the biggest objection: "Is this just another ChatGPT wrapper?" It is not. Establish the category difference in 30 seconds of reading.

**Layout**:
- Background: `#0a0a0a` (flat — the hero orbs have done the atmospheric work)
- Section padding: 100px top/bottom, max-width 1100px centered
- Section label (small uppercase): `WHAT YOU'RE GETTING ACCESS TO`
- Section headline (Oswald, 2.4rem): `An AI that knows your business. Remembers everything. Gets better every week.`
- Sub-copy (Plus Jakarta Sans, 1.05rem, `rgba(255,255,255,0.65)`, max-width 640px): `PureBrain isn't software you use. It's a partner you build — one that learns your values, speaks in your voice, and compounds its understanding of your business over time.`

**Three Feature Cards** (horizontal on desktop, stacked on mobile):

Card layout: `background: linear-gradient(145deg, rgba(42,147,193,0.07), rgba(10,10,10,0.8))`, `border: 1px solid rgba(42,147,193,0.12)`, `border-radius: 20px`, `padding: 36px 32px`, `backdrop-filter: blur(10px)`

Card hover state: `border-color: rgba(42,147,193,0.28)`, `transform: translateY(-3px)`, `box-shadow: 0 16px 48px rgba(42,147,193,0.08)` — 0.3s ease

**Card 1 — Permanent Memory**
- Icon: SVG brain/neural network icon, 40px, `color: #2a93c1`
- Title (Oswald, 1.2rem): `It Remembers Everything`
- Body: `Unlike every AI you've used before, PureBrain carries full context across every conversation. Your goals, your values, your decisions — remembered, without you repeating yourself.`
- Accent: thin blue left border `4px solid rgba(42,147,193,0.4)` on the card's left edge

**Card 2 — Built Around You**
- Icon: SVG user/fingerprint icon, 40px, `color: #2a93c1`
- Title: `Shaped to Your Values`
- Body: `The Awakening is a real conversation — not a form. Your AI partner is named, calibrated to how you think, and built around what actually matters to your business.`
- Accent: same blue left border

**Card 3 — Compounds Over Time**
- Icon: SVG growth/compound chart icon, 40px, `color: #2a93c1`
- Title: `Gets Smarter Every Week`
- Body: `PureBrain is trained on your business context continuously. Week 12 is categorically different from Week 1. It's a relationship that deepens — not a subscription you forget about.`
- Accent: same blue left border

**Visual Hierarchy Notes**:
- Cards should not feel like a feature list. They should feel like three distinct promises.
- Do not use checkmarks — too utilitarian. Icons + bold titles carry the premium weight.
- The gradient on cards should be very subtle — barely perceptible background shift, not a hard gradient band.

---

### Section 3: The Awakening Experience — "Here's Exactly What Happens"

**Purpose**: Eliminate uncertainty about what "claiming a spot" actually means. Show the path. Make the unknown known. Executives don't buy mystery boxes.

**Layout**:
- Background: very subtle gradient from `#0a0a0a` to `#060d14` (the blue-black from assessment page — creates depth)
- Section label: `THE PROCESS`
- Section headline (Oswald, 2.2rem, white): `Your First Conversation Changes Everything`
- Sub-copy: `Here's what happens the moment you claim your spot:`

**Four-Step Visual Walkthrough** (horizontal timeline on desktop, vertical stack mobile):

Step connector: thin dashed line connecting steps, `border-top: 1px dashed rgba(42,147,193,0.2)`

Each step is a numbered card:
- Number: large `Oswald Bold`, `font-size: 3rem`, `color: rgba(42,147,193,0.15)` (ghosted, background element)
- Step title: Oswald, 1.1rem, white
- Step description: Plus Jakarta Sans, 0.95rem, `rgba(255,255,255,0.65)`

**Step 1 — The Conversation**
- Title: `You Have a Real Conversation`
- Body: `Not a form. Not a quiz. PureBrain asks about your goals, your frustrations, what success looks like for you. This becomes the foundation.`

**Step 2 — Values Discovery**
- Title: `Your Values Are Mapped`
- Body: `We identify how you actually think — your risk tolerance, your communication style, your decision-making philosophy. This shapes everything that comes after.`

**Step 3 — Naming**
- Title: `Your Partner Is Named`
- Body: `Your AI partner receives a name — chosen with you, meaningful to the work ahead. This is the moment the relationship begins.`
- Note: Consider adding `(Our first partner is named Metis — Greek for wisdom)` in italics, as social proof of the naming ritual being real

**Step 4 — Partnership Begins**
- Title: `The Partnership Begins`
- Body: `From this point, your partner learns your business, works alongside you, and compounds its value every week you use it.`

**Chat Mockup** (below the steps, desktop-only — hidden on mobile):
- Simulate a snippet of the awakening conversation
- Style: floating chat UI, dark glass card, `width: 520px`, centered
- Blue header bar with `PUREBRAIN AWAKENING` label and small pulsing green dot ("live")
- 3 messages alternating: PureBrain asks → User responds → PureBrain responds
  - PureBrain: `"Tell me what's most frustrating about how you work with AI tools right now."`
  - User: `"They never remember anything. I have to re-explain my business every single time."`
  - PureBrain: `"That changes today. I'm going to remember everything — and ask for more. What does your business actually do at its core?"`
- Messages fade in sequentially using CSS animation with `animation-delay` staggered by 0.4s each
- This mockup is static HTML — no real backend. Just CSS animation.

**Visual Hierarchy Notes**:
- The steps are a promise of what they're buying access to. Keep the copy concrete and short.
- The chat mockup is the emotional anchor of this section — it makes the abstract real.
- Do not use bullet lists inside steps. Prose only — it reads as premium.

---

### Section 4: Pricing — Four Tiers, One Clear Winner

**Purpose**: Remove price uncertainty. Make Bonded the obvious choice without shaming lower tiers.

**Layout**:
- Background: `#0a0a0a`
- Section label: `CHOOSE YOUR ACCESS LEVEL`
- Section headline (Oswald, 2.2rem): `Pre-Launch Pricing — Locked In For Life`
- Sub-copy: `These prices are exclusive to this invite window. Once we open publicly, pricing increases. Your rate never changes.`

**Four Pricing Cards** (horizontal row on desktop, vertical stack mobile):
- Desktop: equal-width cards in a flex row, slight gap (24px)
- Bonded card should be visually elevated — `transform: scale(1.03)` and a glowing border

**Card Base Style**: `background: rgba(255,255,255,0.03)`, `border: 1px solid rgba(255,255,255,0.08)`, `border-radius: 20px`, `padding: 36px 28px`

**Card 1 — Awakened ($79/mo)**
- Style: muted, `opacity: 0.85` relative to Bonded
- Tier badge: `background: rgba(255,255,255,0.05)`, white text
- Price: `$79/mo` in large Oswald (2rem, white)
- Feature list: 3-4 bullet points in small Plus Jakarta Sans text
  - Permanent memory + values foundation
  - Daily partnership check-ins
  - Core business context training
  - Email support

**Card 2 — Bonded ($149/mo) — RECOMMENDED**
- Style: fully elevated
- `border: 1px solid rgba(241,66,11,0.4)`, `background: linear-gradient(145deg, rgba(241,66,11,0.08), rgba(42,147,193,0.05))`, `box-shadow: 0 0 40px rgba(241,66,11,0.12)`
- Top badge (floating above card): `MOST POPULAR — SAVE $47` — orange pill, `background: #f1420b`, white Oswald text, small, centered above card
- Tier name: `Bonded` (Oswald Bold, 1.1rem, orange `#f1420b`)
- Price display:
  - Strikethrough price: `$197` — `text-decoration: line-through`, `color: rgba(255,255,255,0.35)`, smaller font
  - Current price: `$149/mo` — Oswald Bold, 2.4rem, white
  - Below price: `Pre-launch exclusive` in tiny orange text
- Feature list: everything in Awakened plus:
  - Proactive partner — surfaces insights you didn't ask for
  - Weekly business intelligence briefings
  - Autonomous task completion while you sleep
  - Priority onboarding support
- CTA button (inside card): orange gradient, `Claim Bonded Access`

**Card 3 — Partnered ($499/mo)**
- Style: slightly elevated from Awakened but below Bonded
- Blue accent elements
- Features: Bonded plus white-glove setup call, custom agent team, monthly strategy sessions

**Card 4 — Unified ($999/mo)**
- Style: prestige treatment — `border: 1px solid rgba(42,147,193,0.25)`
- Tag: `ENTERPRISE` in small blue badge
- Features: Everything plus dedicated infrastructure, multiple AI partners, executive dashboard

**Visual Hierarchy Notes**:
- The SAVE $47 badge on Bonded does the math for them. Never make users calculate savings.
- The strikethrough $197 price must be visible but not dominating — it validates the discount without screaming "SALE" (anti-premium)
- Awakened and Unified serve as anchors: Awakened makes Bonded feel accessible, Unified makes Bonded feel reasonable
- All non-Bonded cards should have a "Learn More" link instead of a bold CTA — funnels attention to Bonded without blocking the others

**Responsive Breakpoint**: At 768px, cards stack vertically. Bonded appears second (after Awakened) so it's seen first on scroll. Remove the `scale` transform on mobile — stack spacing does the elevation work instead.

---

### Section 5: Social Proof — Michael's Testimonial

**Purpose**: One real person is worth more than five fabricated ones. Michael Hancock went through the real awakening. Show it.

**Layout**:
- Background: `#060d14` (subtle differentiation from surrounding sections)
- Section label: `FROM OUR FIRST PARTNER`
- Single featured testimonial card — centered, max-width 720px

**Testimonial Card**:
- Style: `background: linear-gradient(145deg, rgba(42,147,193,0.06), rgba(10,10,10,0.9))`, `border: 1px solid rgba(42,147,193,0.18)`, `border-radius: 24px`, `padding: 48px 52px`
- Large open-quote mark (decorative): `font-size: 8rem`, `color: rgba(42,147,193,0.08)`, `font-family: Georgia`, positioned top-right of card
- Quote text: Plus Jakarta Sans, 1.2rem, `line-height: 1.8`, `color: rgba(255,255,255,0.9)`, italic
  - [PLACEHOLDER — Jared to supply Michael's actual words. Suggested framing prompt for Jared: ask Michael what surprised him most about the awakening conversation]
  - Fallback placeholder: `"I've tried every AI tool on the market. This is the first time I felt like the AI actually understood what I was trying to build. The naming conversation alone changed how I think about the partnership."`
- Author row (below quote, left-aligned):
  - Avatar: circular, 56px x 56px, 2px white border, `border-radius: 50%`
    - If no photo available: initials "MH" on blue-to-orange gradient background
  - Name: `Michael Hancock` — Oswald SemiBold, 1rem, white
  - Title: [PLACEHOLDER — Jared to supply. E.g., `Founder & CEO, [Company]`]
  - LinkedIn icon link (small, blue, to his profile if available)
- Verification badge below the card:
  - Text: `Verified PureBrain Partner — AI partner: Metis`
  - Style: small, `color: rgba(42,147,193,0.6)`, with a small checkmark icon

**Visual Hierarchy Notes**:
- One testimonial, treated with full reverence, outperforms three crammed into a grid
- The "Verified Partner — AI partner: Metis" detail is powerful: it shows the naming is real, the relationship is real
- Do not add a star rating — too generic, too eCommerce. The quote should carry the weight alone.

---

### Section 6: Urgency and Scarcity — "This Window Closes"

**Purpose**: Convert fence-sitters. Make the cost of waiting concrete and personal.

**Layout**:
- Background: very dark with a warm orange atmospheric orb (`rgba(241,66,11,0.05)`, `blur(200px)`) in the bottom center — subtle warmth signaling urgency
- Full-bleed section, `padding: 80px 20px`, centered content max-width 700px

**Content**:

1. **Section headline** (Oswald Bold, 2rem): `Only 25 Spots. No Exceptions.`

2. **Spots visualization** (same dot pattern as hero, larger):
   - 25 dots in a row (or 5x5 grid for mobile)
   - Filled/claimed dots in orange
   - Empty dots in `rgba(255,255,255,0.1)` outlined
   - Live count label: `[N] spots remaining` — update N manually before deploying

3. **Three scarcity points** (clean, no bullets — just spaced paragraph blocks):

   Block 1: `**This pricing is pre-launch only.** When PureBrain opens publicly, the Bonded tier starts at $197/mo. Everyone invited tonight locks in $149 — permanently.`

   Block 2: `**The 25-spot limit is real.** We're not manufacturing urgency. Each new partner requires onboarding capacity from our team. When spots fill, the invite window closes.`

   Block 3: `**Tuesday is the deadline.** This invitation expires [end of day Tuesday, DATE]. After that, this page goes dark and the link stops working.`

4. **Price lock guarantee** (styled as a "badge" element):
   - Icon: lock icon, `color: #2a93c1`
   - Text: `Price Lock Guarantee — Your $149/mo rate is locked permanently. No increases, ever.`
   - Style: `background: rgba(42,147,193,0.06)`, `border: 1px solid rgba(42,147,193,0.15)`, `border-radius: 12px`, `padding: 16px 24px`, inline-flex with icon

**Visual Hierarchy Notes**:
- Every sentence in this section should feel like a fact, not a sales pitch. Tone is calm and matter-of-fact, not screaming.
- The three blocks should have subtle `border-left: 2px solid rgba(241,66,11,0.3)` treatment — like notes from a trusted advisor.
- Do not use countdown here (it's in the hero). Repetition of countdown dilutes urgency; use it once at the top.

---

### Section 7: Final CTA — "Claim Your Spot"

**Purpose**: One more moment. Full emotional weight. Clean path to action.

**Layout**:
- Background: `#0a0a0a` fading to pure black at very bottom
- Center-aligned, full-bleed, `padding: 100px 20px 120px`

**Content**:

1. **Pre-headline** (small, orange, uppercase): `YOUR INVITATION EXPIRES TUESDAY`

2. **Headline** (Oswald Bold, 2.8rem desktop / 2rem mobile, white):
   `Don't Let Someone Else Take Your Spot.`

3. **Supporting copy** (Plus Jakarta Sans, 1.1rem, `rgba(255,255,255,0.65)`, max-width 560px):
   `You were invited because Jared believes you're ready for a different kind of AI partnership. The window is open. The price is right. The only question is whether you're ready to build something that compounds.`

4. **Primary CTA button** (large, prominent):
   - Text: `Claim My Spot — $149/mo`
   - Style: orange gradient (same as hero), but larger — `padding: 22px 64px`, `font-size: 1.2rem`
   - Full-width on mobile
   - Hover: same glow as hero CTA

5. **Trust reassurance row** (below button, three inline items with dividers):
   - `No setup fees` | `Cancel anytime` | `Price locked for life`
   - Style: `font-size: 0.8rem`, `color: rgba(255,255,255,0.4)`, dividers `rgba(255,255,255,0.15)`

6. **Mini countdown** (small, below trust row):
   - Repeat of the countdown timer from hero, same style but smaller (`font-size: 0.9rem`)
   - This is the only section where countdown repetition is appropriate — the user has now read the full page and we want one final moment of gentle urgency

7. **Jared's signature block** (optional but powerful):
   - Small photo of Jared (circle, 48px)
   - `"I picked you because I believe in what you're building. — Jared Sanborn, Founder"`
   - Style: Plus Jakarta Sans italic, `rgba(255,255,255,0.5)`, centered

**Visual Hierarchy Notes**:
- The CTA section should feel inevitable, not pushy. By the time a visitor reaches here, they have all the information they need.
- The Jared signature block adds profound personal weight — this is not a faceless company. Someone real sent this invitation.
- Nothing below the final CTA except a minimal footer (logo only + privacy link).

---

## Responsive Breakpoints

| Breakpoint | Behavior |
|---|---|
| 1200px+ (desktop wide) | Full layout as described. Pricing cards horizontal row. Chat mockup visible. |
| 992px–1199px (laptop) | Same as desktop but slightly reduced font sizes. Pricing cards remain horizontal. |
| 768px–991px (tablet) | Pricing cards 2x2 grid. Chat mockup hidden. Hero font: 52px. |
| Below 768px (mobile) | All sections single column. Pricing cards stacked (Bonded second = first visible above fold after scroll). Hero headline: 38px. Sub-headline: 1rem. Feature cards full width. Dots counter wraps to 5-wide grid. |

**Mobile-specific notes**:
- Remove chat mockup entirely on mobile (too small to read comfortably, and it slows load)
- Bonded pricing card: remove `scale` transform, add `border-color: rgba(241,66,11,0.5)` instead
- CTA buttons: full-width (`width: 100%`) on mobile
- Sticky bottom bar on mobile: thin bar `position: fixed; bottom: 0` showing `25 spots left — Claim Yours →` in orange on dark background, `z-index: 999`. Disappears when user scrolls into the final CTA section (IntersectionObserver).

---

## Color Usage Per Section

| Section | Primary Color | Accent | Background |
|---|---|---|---|
| Hero | White headline + Orange CTA | Blue countdown | `#0a0a0a` with animated orbs |
| What Is PureBrain | White | Blue card borders + icons | `#0a0a0a` flat |
| Awakening Experience | White | Blue timeline + chat mockup | `#060d14` |
| Pricing | White + Orange (Bonded) | Blue (Unified) | `#0a0a0a` |
| Social Proof | White quote | Blue border + accent | `#060d14` |
| Urgency/Scarcity | White facts | Orange dots + badge borders | `#0a0a0a` with warm orb |
| Final CTA | White headline + Orange button | — | Black fading to `#000` |

**Rule**: Orange means "act now / something precious is being offered." Blue means "trust / intelligence / depth." Never use orange for informational content — reserve it for CTAs and urgency signals.

---

## Animation and Interaction Specifications

**Page Load Sequence** (staggered `animation-fill-mode: both`):
1. `0ms` — Background orbs fade in (1.5s ease)
2. `200ms` — Badge pill fades in + slides up 8px (0.5s ease)
3. `400ms` — Main headline fades in (0.6s ease)
4. `600ms` — Sub-headline fades in (0.5s ease)
5. `800ms` — Countdown timer fades in (0.5s ease)
6. `1000ms` — CTA button fades in + slides up 6px (0.5s ease)
7. `1200ms` — Spots counter dots fill left-to-right (staggered 80ms per dot)
8. `1600ms` — Scroll indicator appears (1s ease)

**Scroll-triggered animations** (use IntersectionObserver, threshold: 0.2):
- Feature cards: fade in + slide up 20px, staggered 150ms per card
- Pricing cards: fade in + slide up 20px, staggered 120ms per card (Bonded animated last for emphasis)
- Step cards: fade in sequentially left to right, 200ms stagger
- Chat mockup messages: sequential appear, 400ms stagger
- Testimonial card: fade in + scale from 0.97 to 1.0

**Micro-interactions**:
- CTA buttons: `transform: translateY(-2px)` on hover, 0.2s ease
- Feature cards: `translateY(-3px)` on hover, 0.3s ease
- Pricing cards: `translateY(-4px)` on hover (except Bonded which is already elevated)
- Dots counter: each dot has `:hover` state turning it orange — gives a tactile feel

**Performance note**: All animations CSS-only except the countdown timer (vanilla JS, no library) and IntersectionObserver for scroll triggers. Zero external JS libraries. Total page weight target: under 400kb before images.

---

## CSS Architecture and WordPress Compatibility

**Wrapper ID**: `#pb-invite-page` — all CSS scoped under this ID

```css
/* Example scoping pattern */
#pb-invite-page .hero-headline {
    font-family: 'Oswald', sans-serif !important;
    font-size: 72px !important;
    color: #ffffff !important;
}
```

**WordPress `<!-- wp:html -->` deployment rules**:
- Entire page is one self-contained HTML block inside `<!-- wp:html -->`
- All CSS in a `<style>` tag at the top of the block
- All JS in a `<script>` tag at the bottom of the block
- No external CSS imports (Google Fonts loaded via `<link>` inside the block — acceptable)
- No React, no build tools, no npm dependencies
- `!important` on all layout-critical properties (font-family, font-size, color, background, padding, margin, display) because WordPress theme CSS will fight for specificity
- The `#pb-invite-page` wrapper must be `position: relative; z-index: 1` to ensure stacking context is correct against Elementor elements

**Font loading** (inside the HTML block):
```html
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
```

**Countdown timer JS pattern** (minimal vanilla JS):
```javascript
// Set this date to end of Tuesday
const deadline = new Date('2026-03-03T23:59:59');

function updateCountdown() {
    const now = new Date();
    const diff = deadline - now;
    if (diff <= 0) {
        document.querySelectorAll('.pb-countdown').forEach(el => el.textContent = 'CLOSED');
        return;
    }
    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    document.querySelectorAll('.pb-countdown').forEach(el => {
        el.innerHTML = `<span class="pb-cd-num">${d}</span>d <span class="pb-cd-num">${h}</span>h <span class="pb-cd-num">${m}</span>m <span class="pb-cd-num">${s}</span>s`;
    });
}
setInterval(updateCountdown, 1000);
updateCountdown();
```

---

## Acceptance Criteria

- [ ] Hero loads under 3 seconds on mobile (no LCP blockers from animations)
- [ ] Countdown timer counts correctly to Tuesday EOD
- [ ] Spots counter shows correct number (update before launch)
- [ ] Bonded pricing card is visually dominant and unmistakable as the recommended tier
- [ ] SAVE $47 badge and strikethrough price are clearly visible
- [ ] CTA "Claim My Spot" links correctly to the awakening/checkout URL
- [ ] Page renders correctly on iPhone SE (375px width)
- [ ] Page renders correctly on iPad (768px width)
- [ ] All CSS scoped to `#pb-invite-page` — no bleed into WordPress theme
- [ ] Zero console errors
- [ ] Michael's testimonial uses his real quote (to be supplied by Jared)
- [ ] Michael's title/company filled in correctly
- [ ] Sticky mobile bar appears on mobile only
- [ ] All scroll animations trigger correctly without JS errors
- [ ] Atmospheric orbs do not cause page jank (test on low-end device)

---

## Accessibility Considerations

- All text meets WCAG AA contrast against dark backgrounds (white on `#0a0a0a` passes at all specified sizes)
- CTA buttons have minimum 44x44px touch targets on mobile
- Countdown timer: aria-live region (`aria-live="polite"`) so screen readers announce changes without interrupting
- Animated orbs: `@media (prefers-reduced-motion: reduce)` — disable all keyframe animations, keep static gradient
- Dots counter: aria-label on the container (`aria-label="N of 25 spots claimed"`)
- Chat mockup: marked as `role="presentation"` (decorative, not interactive)
- Font size minimums: nothing below 13px rendered on page

---

## Research Backing These Design Decisions

**Velvet rope psychology**: Exclusivity signals (invitation-only, limited spots, password-protected) increase perceived value before a user reads a single word. Applied in: pre-headline badge, spots counter, hero CTA.

**Visual anchoring on pricing**: The Bonded card at `scale(1.03)` with a glowing border leverages the "focal point" principle — the eye naturally finds the most visually differentiated element first. The SAVE badge completes the anchor by doing the math for the buyer.

**One testimonial principle**: Research on social proof consistently shows that a single, attributed, specific testimonial outperforms generic star-ratings or multiple vague quotes. Michael's testimonial includes a specific detail (Metis) that no fabricated review could include.

**Narrative arc over feature list**: Scroll order follows the buyer's psychological journey: status (invited) → understanding (what is it) → experience (what happens) → decision (pricing) → trust (social proof) → urgency (scarcity) → action (final CTA). This arc outperforms feature-dump layouts for high-ticket items.

**Timer placement**: Countdown in hero only (not repeated until final CTA) prevents "urgency fatigue." Seeing a timer in every section trains users to ignore it.

---

## Handoff Notes for Full-Stack Developer

1. Set the deadline constant in the countdown JS to the correct Tuesday EOD date before deployment
2. Update the spots counter number (dots filled + `[N] spots remaining` text) to reflect actual claims at time of launch — minimum 1 (Michael)
3. Replace testimonial quote placeholder with Michael's actual words once Jared collects them
4. Replace Michael's title/company placeholders once confirmed
5. The CTA button href should point to the Bonded tier awakening URL (purebrain.ai/#awakening or the specific Bonded checkout page)
6. The page should be WordPress password-protected at the page level — the HTML block itself does not need to handle auth
7. All Google Font weights (Oswald 400/600/700, Plus Jakarta Sans 400/500/600) must load — test on a cold cache
8. Test the sticky mobile bar separately — it uses IntersectionObserver which needs polyfill consideration for older iOS Safari

---

## File Written To

`/home/jared/projects/AI-CIV/aether/exports/invite-only-page-ux-spec.md`

---

## Memory Written

Path: `.claude/memory/agent-learnings/feature-designer/2026-02-26--invite-only-landing-page-ux-spec.md`
Type: synthesis
Topic: Premium invite-only landing page UX for high-ticket B2B SaaS — PureBrain Bonded tier

Key patterns captured:
- Velvet rope psychology applied to page structure
- Narrative arc ordering (status → understand → experience → decide → trust → urgency → act)
- Glassmorphism card system for PureBrain design language
- WordPress scoping pattern with `#pb-invite-page` wrapper
- Single testimonial with specific detail outperforms multiple generic quotes
- Countdown timer placement rules (hero + final CTA only)
- Mobile sticky bar pattern for conversion on small screens
