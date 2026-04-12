# PureBrain 4.0 Top-Half Landing Page

**Date**: 2026-02-18
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Built

Complete top-half HTML fragment for `/purebrain-4/` landing page.
Deployed at: `/home/jared/projects/AI-CIV/aether/exports/purebrain-4/top-half.html`
Size: 56K, 1,899 lines

## Sections Included

1. Sticky navigation (semi-transparent dark, blur, hamburger mobile menu)
2. Hero section (gradient BG, headline, CTA, awakening counter, video thumbnail)
3. Video modal (with audio controls: unmute button, volume slider)
4. Trust signals bar (3 items, dark theme)
5. How It Works (3-step process, connector line on desktop)
6. Differentiation block (4 features vs ChatGPT/Claude, CTA to #pricing)
7. Capabilities grid (6 cards, 3-column desktop, 2-col tablet, 1-col mobile)

## Brand Colors / Design Decisions

- Blue: `#2a93c1`, Dark blue: `#1a7aa3`
- Orange: `#f1420b`, Dark orange: `#d13608`
- Dark BG: `#0a0a1a`, Mid BG: `#0f0f24`
- Fonts: Oswald (headings), Plus Jakarta Sans (body) via Google Fonts import
- Logo: PUREBR (blue) + AI (orange) + N (blue) + .ai (white/muted)

## Patterns Used

- CSS custom properties (`--blue`, `--orange`, etc.) for consistent theming
- Scoped class prefix `pb4-` to avoid collisions with Elementor/WordPress CSS
- IntersectionObserver for fade-in-on-scroll animations with IE/old browser fallback
- `prefers-reduced-motion` media query disables all animations
- `scroll-behavior: smooth` on html + JS fallback anchor scroll with nav offset
- Video modal: starts muted (autoplay policy), mute/unmute toggle, volume slider
- Awakening counter: starts at 73, increments 1-3 randomly every 4-18 seconds
- Mobile: hamburger animates to X, drawer overlays below nav bar

## Deployment Notes

- This is a self-contained HTML fragment (no doctype/html/body tags)
- Will be combined with bottom-half.html and pasted into a single Elementor HTML widget
- Elementor Canvas template = blank page, no WordPress theme wrapper
- WP API creds: Aether / FlFr2VOtlHiHaJWjzW96OHUJ (see PayPal memory for full API pattern)
- After Elementor update, trigger cache clear with a second POST to the page endpoint

## Key Teaching

When building landing page fragments for Elementor:
- Prefix ALL CSS classes to avoid conflicts (existing pages use `.pb-` prefix, new pages use `.pb4-`)
- Include Google Fonts via `@import` inside the `<style>` block (Elementor strips `<link>` tags sometimes)
- Video autoplay requires `muted` attribute on first load due to browser policy
- Use CSS `aspect-ratio: 16/9` for video containers (cleaner than padding-top hack)
- The counter animation pattern (random interval + random increment) feels more alive than a fixed timer
