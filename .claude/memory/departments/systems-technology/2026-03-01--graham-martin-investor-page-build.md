# Graham Martin Investor Page — Build Record

**Date**: 2026-03-01
**Agent**: dept-systems-technology
**Build type**: Custom investor pitch page — single HTML file + WordPress deployment

---

## Delivery Summary

- **HTML file**: `/home/jared/projects/AI-CIV/aether/exports/graham-martin-investor-page.html` (69KB)
- **WordPress page ID**: 1150
- **Live URL**: https://purebrain.ai/purebrain-for-graham-martin/
- **Password**: skybet47
- **Template**: elementor_canvas (full-width, no theme chrome)
- **Status**: Published and password-protected

---

## Page Architecture

Six sections + fixed nav + footer:

1. **Hero** — Animated gradient, rotating glow orbs, $4.7B stat, hero CTA
2. **Your World, Amplified** — Company-by-company mapping (Sky Bet, Virya VC, P2Earn, Aquarius AI, Cardinal House), PureBrain amplification panel
3. **The Chairman's PureBrain** — Terminal mock showing live board intelligence session, 6-card capability grid
4. **Responsible Gambling, Automated** — Compliance feature list + multi-jurisdiction status panel (UK, Malta, AU, Canada, Italy, Alderney, HK)
5. **Virya VC Intelligence** — Live deal feed mock (Matchbook, Betpawa, B90 Holdings, Trakx, inbound deal) + 5-feature list
6. **The Numbers** — 4 big stats, 6 performance bar charts, ROI spotlight
7. **CTA** — Partnership framing, 4 chip options (personal PureBrain, Virya portfolio, investment, board role)

---

## Design System Used

- Base: `#080a12` (PureBrain dark)
- Blue: `#2a93c1` — PUREBR + N
- Orange: `#f1420b` — AI
- Glass morphism: `rgba(255,255,255,0.04)` backgrounds with `blur(12px)`
- Animated gradient blobs in hero (3 radial gradients, CSS keyframes)
- Intersection Observer for scroll-triggered fade-ins
- CSS custom properties for full theme consistency
- Responsive: mobile-first, all grids collapse to 1 column at 600px

---

## WordPress Deployment Pattern

- Method: REST API POST to `/wp-json/wp/v2/pages`
- Auth: Basic auth `Aether:FlFr2VOtlHiHaJWjzW96OHUJ`
- Content wrapped in `<!-- wp:html -->` / `<!-- /wp:html -->`
- Template set to `elementor_canvas` in JSON payload
- Password protection via `"password": "skybet47"` field
- Full self-contained HTML (no external deps except Google Fonts)

---

## Research Source

Full investor research: `/home/jared/projects/AI-CIV/aether/exports/graham-martin-research.md`

Key details used:
- $4.7B Sky Bet exit (The Stars Group acquisition, 2018)
- Virya VC: 20+ portfolio companies (Matchbook, Betpawa, B90 Holdings, Trakx, Spin Bookie, etc.)
- P2Earn: CSE-listed, play-to-earn, President role
- Aquarius AI: esports betting, first AI gaming role (2020)
- 17 governments advised on gambling regulation
- World's first online gambling law: Alderney, Bailiwick of Guernsey
- Market data: $9B (2024) → $28B (2030), 21.1% CAGR

---

## Key Pitch Lines Embedded

- "From the world's first online betting law to the world's first personal AI for gaming operators"
- "Instead of reading 10 board packs, your PureBrain reads them and tells you what actually matters"
- "You helped write the world's first online gambling law. PureBrain helps operators comply with every version since"
- "Virya's deal flow is global and moving fast. Your PureBrain due diligence team doesn't sleep and doesn't miss anything"
- "Let's build your PureBrain together" — partnership framing throughout
