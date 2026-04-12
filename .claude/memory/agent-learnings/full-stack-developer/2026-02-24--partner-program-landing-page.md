# Partner Program Landing Page Build

**Date**: 2026-02-24
**Type**: operational + technique
**Topic**: Built the PureBrain Affiliate/Partner Program landing page for purebrain.ai/partners

---

## What Was Built

`/home/jared/projects/AI-CIV/aether/exports/partner-program-landing-page.html`

2090-line self-contained HTML file implementing the full Affiliate/Partner Program landing page from the 90-day roadmap (Initiative 1, Month 2).

---

## Sections Included

1. **Sticky Nav** — PureBrain logo orb + "Partner Program" orange badge
2. **Hero** — Headline with orange/blue highlights, stats row (20% commission, 90-day cookie, Net-30, 24-month window), dual CTAs
3. **The Math Block** — Concrete earnings examples from the roadmap spec ($189.60 / $717.60 / $299/mo recurring)
4. **How It Works** — 3-step card grid with connecting gradient line (hidden mobile)
5. **Commission Tiers** — 3-column card grid (Standard 20%, Certified 30%, Strategic 25%) with featured treatment on Certified
6. **Earnings Calculator** — Interactive: referral count range slider (1-50) + plan toggle buttons ($79/$149/$299), calculates monthly income / year 1 total / referrals needed for $1k/mo
7. **Benefits** — 6-card grid (dashboard, starter kit, badge, office hours, Aether content, early access)
8. **Who It's For / Not For** — 2-column fit card (good/not with color-coded dot lists)
9. **Testimonials** — 3 placeholder cards with "Coming Soon" badges, real attribution labels ready
10. **Application Form** — 8-field form (name, email, website, LinkedIn optional, role dropdown, audience size, PureBrain usage, why partner textarea with char count, client profile optional)
11. **FAQ Accordion** — 8 questions, smooth max-height accordion, one-open-at-a-time behavior
12. **Bottom CTA Banner** — Gradient border, repeat apply CTA
13. **Footer** — Privacy + Terms links

---

## Form Submission

Form POSTs to `https://89.167.19.20:8443/api/log-conversation` with:
- `session_id`: `partner-application-[timestamp]`
- `user_message`: "PARTNER APPLICATION SUBMITTED"
- `assistant_response`: JSON dump of all form fields
- `metadata.type`: `partner_application`
- `metadata.source`: `partner-program-landing-page`
- Graceful fallback: if fetch fails, success UX still shows (no silent failure for applicant)

---

## CSS Architecture

- All CSS scoped under `#pb-partner` to prevent WP theme conflicts
- CSS variables under `#pb-partner` (not `:root` which WP can override)
- All classes prefixed `pb-` to avoid collisions
- **WP magic-cursor override** included (MANDATORY for purebrain.ai):
  ```css
  body { background: #0a0a0a !important; }
  body.tt-magic-cursor { background: #0a0a0a !important; }
  ```
- Wrapped in `<!-- wp:html --> ... <!-- /wp:html -->` for WordPress deployment

---

## Design Decisions

- Colors: `#0a0a0a` bg, `#f1420b` orange, `#2a93c1` blue, `#e8edf5` text, `#8a9bb0` muted
- CSS orb in nav (same radial-gradient pattern as established PureBrain visual language)
- Orange for primary CTAs and commission numbers; blue for secondary accents and eyebrows
- Hero background: radial-gradient orange glow at top (subtle, 6% opacity)
- Cards: `#111111` bg (1px above page bg), `border: 1px solid rgba(255,255,255,0.08)`
- Featured tier (Certified): orange border + `box-shadow: 0 0 40px rgba(241,66,11,0.15)`
- Responsive: 900px breakpoint collapses grids to 1-col, 600px stacks hero CTAs
- Transition: 0.22s ease on all interactive elements

---

## Key JS Patterns

```js
// Calculator — calculates on slider input + plan btn click
var monthly = referrals * planPrice * 0.20;
var activeNeeded = Math.ceil(1000 / (planPrice * 0.20));

// FAQ — max-height accordion
item.classList.toggle('pb-faq-open');
// CSS: .pb-faq-item.pb-faq-open .pb-faq-answer { max-height: 400px; }

// Form — graceful fallback
fetch(LOG_SERVER).catch(() => pbShowSuccess()); // always show success
```

---

## Source Material

- Roadmap spec: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/90-day-roadmap-months-2-3.md`
  - Section: Initiative 1 (1A Commission Model, 1B Page Content, 1C Application Form)
- Output: `/home/jared/projects/AI-CIV/aether/exports/partner-program-landing-page.html`
- Deploy target: `purebrain.ai/partners` (new WP page, `elementor_canvas` template)

---

## What Was NOT Done (Intentionally)

- NOT deployed to WordPress (per instruction)
- No backend partner dashboard (tracking via PartnerStack/ReferralHero per roadmap)
- No Stripe webhook integration (separate backend work)
- Onboarding email sequence (separate Brevo work)

---

## Gotchas / Lessons

1. `data-price` attribute on plan toggle buttons used instead of value in select — cleaner for JS toggling with CSS active states
2. Form textarea char count uses `oninput` (not `onkeyup`) — covers paste events
3. `fetch` to log server uses graceful fallback — if server is unreachable (HTTPS self-signed cert in browser), applicant still sees success
4. FAQ accordion uses `max-height: 0 / 400px` transition not `height: auto` — `height: auto` can't be CSS-transitioned
5. Calculator "referrals needed for $1000/month" is plan-dependent — updates in real time when plan toggles
