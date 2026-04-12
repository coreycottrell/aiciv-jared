# 2026-03-19: Homepage — Copy Testimonials + Referral Section from /live/

**Type**: operational
**Agent**: dept-systems-technology

## What Was Done

Copied two sections from `/live/index.html` to the main homepage (`/index.html`).

### Task 1: Testimonials
- Homepage was missing Joseph Ray Diosana's card (Tether, real estate)
- The /live/ version had the full set: Jared → Joseph Ray → Corey C. → Parallax → Atlas → Ember → Nova
- Inserted Joseph Ray's card between Jared's card and Corey C.'s card
- Testimonial photo CSS (`.testimonial-card__photo`, `.testimonial-card__author-wrap`, etc.) was already present in homepage — no CSS changes needed

### Task 2: Referral Section
- Homepage had no referral/partner program section at all
- Copied full section from /live/ (added 2026-03-13): `<section id="referral-program">`
- Inserted before `<div id="pb-aether-footer">` (bottom of page, before footer bar)
- Includes all CSS inline in `<style>` tag, all JS inline in `<script>` tag
- Leaderboard API: `https://app.purebrain.ai/api/referral/leaderboard`
- Referral signup: `https://purebrain.ai/refer/`

## Key Pattern: /live/ as Source of Truth

The `/live/` subdirectory is more up-to-date than the main homepage. When Jared asks to copy sections, do exact HTML/CSS/JS extraction — no recreation.

## File Modified
`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html`

## Deployment
Deployed to `purebrain-staging` via wrangler. Deployment URL: `https://fe70a6de.purebrain-staging.pages.dev`

## Gotcha
HTML in this file uses literal `&` (not `&amp;`) for display text like "PureMarketing.ai & PureTechnology.ai" — need to match exactly when doing string replacements.
