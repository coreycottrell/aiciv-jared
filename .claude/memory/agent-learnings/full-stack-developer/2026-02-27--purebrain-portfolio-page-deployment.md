# PureBrain Portfolio Page Deployment

**Date**: 2026-02-27
**Type**: operational
**Topic**: Full portfolio page build + WordPress deployment at purebrain.ai/portfolio

## What Was Built

`/home/jared/projects/AI-CIV/aether/exports/purebrain-portfolio-page.html` — ~37KB complete page

Lead-generation portfolio page showing PureBrain's 12 core capabilities, deployed to WordPress page ID 1006.

## WordPress Deployment

- **URL**: https://purebrain.ai/portfolio/
- **Page ID**: 1006
- **Slug**: portfolio
- **Template**: elementor_canvas
- **Status**: publish

## Images Used

### Newly Uploaded
- `portfolio-hero.png` → WP Media ID 1004 → `https://purebrain.ai/wp-content/uploads/2026/02/portfolio-hero-scaled.jpg`
  - Title: "Not A Tool - AI Civilization Orb"
- `portfolio-proof.png` → WP Media ID 1005 → `https://purebrain.ai/wp-content/uploads/2026/02/portfolio-proof-scaled.jpg`
  - Title: "Before and After PureBrain AI"

### Already Uploaded (reused)
- `https://purebrain.ai/wp-content/uploads/2026/02/amplify-founder-scaled.jpg` (YOU ARE NOT ONE PERSON ANYMORE ring)
- `https://purebrain.ai/wp-content/uploads/2026/02/vc-fomo-scaled.jpg` (competition racing image — used in urgency strip AND closing CTA)

## Page Structure

1. Sticky nav with PUREBRAIN wordmark + CTA
2. Hero section — 2-col grid (text left, image right)
3. Stat bar — 23 depts / 30+ agents / 24/7 / 200x
4. 12 capability cards — 3-col grid, staggered scroll animation
5. amplify-founder-scaled.jpg full-width strip
6. Before/After proof section
7. 8-item vertical timeline (3AM–11PM)
8. Urgency/competition strip (2-col with vc-fomo image)
9. Scaling table (3 tiers: Starter/Professional/Enterprise)
10. Closing CTA (vc-fomo image + headline + buttons)
11. Footer with links

## CSS Architecture

- All CSS scoped under `#pb-portfolio-page`
- CSS variables: `--blue: #2a93c1`, `--orange: #f1420b`, `--dark: #080a12`
- IntersectionObserver for `.pb-fade-in`, `.pb-cap-card`, `.pb-tl-item`
- Stagger delay: cap cards delay by col position × 80ms
- Responsive: 900px (2-col caps, stacked hero) + 600px (1-col caps, stacked buttons)

## All CTA Links

Every CTA button → `https://purebrain.ai/#awakening` (verified in live curl)

## Note on Image URLs

WordPress auto-scales large PNGs on upload. The `-scaled.jpg` suffix is applied automatically.
Original source files were in `/home/jared/projects/AI-CIV/aether/exports/amplify-assets/`.
