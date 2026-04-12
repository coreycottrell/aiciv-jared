# Investor Portal — Magnum Opus Build
**Date**: 2026-03-16
**Type**: operational + pattern
**Topic**: Full interactive investor portal build — password-gated, Three.js, Chart.js, investment calculator

## What Was Built
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors/index.html` (85KB, 2575 lines)
- `/home/jared/projects/AI-CIV/aether/exports/investor-portal-v1.html` (same file, second path)
- Live at: https://purebrain.ai/investors/
- Password: pureinvestor2026

## Architecture
Single-file, fully self-contained HTML/CSS/JS. No build tools. CDN deps only:
- Chart.js v4.4.0 (CDN)
- Three.js r128 (CDN)
- Inter font (Google Fonts)

## 9 Sections
1. **Hero** — Three.js animated neural network background, live raise progress bar, counter animations
2. **Vision** — $4T market, 225:1 LTV:CAC, $105M MAKR term sheet summary
3. **Investment Calculator** — Slider $50K-$2.5M, shows shares/Series-A return/5yr value/multiple
4. **Financial Model Explorer** — Bull/Base/Bear scenario toggle, Chart.js revenue bar + subscriber line charts
5. **Portfolio** — Four company cards: PureBrain, PureTechnology, PureInfluence, PureMarketing + pricing tiers
6. **The Raise** — Full deal terms, MAKR term sheet highlight, Uber/Airbnb/Cognition historical precedent table
7. **Team** — Jared Sanborn CEO, Aether AI Co-CEO (key differentiator), 24 senior management
8. **Market** — $4T TAM, $1T smartphone, 1% = $5.9B, 95% AI pilot failure rate, 5yr revenue table
9. **Contact/CTA** — Email Jared CTA, legal disclaimer footer

## Key Hardcoded Data
- Valuation: $55M pre-money, $3.36/share
- Raise: $2.5M, $332,500 already closed
- MAKR: $25M Series-A at $105M, term sheet signed, May 2026
- ROI: 64.9% return in ~90 days on Series-A mark-up
- Year 5 multiple: 2,418x projected (based on $133B trajectory)
- Base revenue: $733M (Yr1) → $5.4B (Yr2) → $15.3B (Yr3) → $33.5B (Yr4) → $50.7B (Yr5)

## Password Gate Pattern
- JS-based gate with sessionStorage persistence (pureinvestor2026)
- Smooth opacity + scale transition on unlock (0.6s ease)
- Three.js particle field visible behind gate
- Enter key triggers auth check

## Three.js Implementation
- Gate background: 800 static particles + line mesh between nearby nodes, rotating slowly
- Hero section: 60-node animated neural network graph — nodes drift, edges rebuild every 6 frames
- Both use alpha:true WebGL canvas for dark background transparency

## Chart.js Pattern
- Scenario toggle (Base/Bull/Bear) updates both charts via `.update('active')`
- Revenue: bar chart, color changes per scenario
- Subscribers: line chart with fill, always orange (#f1420b)
- Chart defaults: dark grid, Inter font, custom tooltip styling

## Investment Calculator Math
- Shares = amount / $3.36
- Series-A value = (amount / $55M) * $105M
- Year 5 value = (amount / $55M) * $133B
- Multiple = Year5Val / amount

## Sticky Nav Dots
- IntersectionObserver on all 9 sections, threshold 0.4
- Active dot gets blue glow + scale
- Tooltips on hover (right-aligned)
- Hidden on mobile (< 900px)

## Deployment
- CF Pages project: purebrain-staging
- Deploy: npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging
- Cache purge: global API key (X-Auth-Key header) — CF Pages token does NOT have zone permissions
- Zone ID: 49400cad1527af716705f6cb8c22bb65 (purebrain.ai)

## Verification
- https://purebrain.ai/investors/ → 200
- https://purebrain-staging.pages.dev/investors/ → 200
