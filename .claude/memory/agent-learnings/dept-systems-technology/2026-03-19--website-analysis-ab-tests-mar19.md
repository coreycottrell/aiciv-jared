# Memory: PureBrain.ai Website Analysis & A/B Test Plan — March 19, 2026

**Date**: 2026-03-19
**Type**: synthesis + teaching
**Tags**: purebrain, website-analysis, ab-tests, SEO, performance, CTA, mobile, conversion

---

## Context

Comprehensive website analysis for Jared — overnight task ST#. Covers homepage, /blog/, /insiders/, /awakened/, individual blog posts. Built on March 17 Playwright audit data plus live page fetches.

---

## Most Critical Findings

1. **Homepage title = "Elementor #1502 - Pure Brain"** — Critical SEO issue. Every Google SERP result, every social share card shows this broken internal draft name. Fix takes 5 minutes in Yoast SEO panel.

2. **No homepage meta description** — Confirmed by Yoast admin notice in source. Write 155-char description.

3. **/insiders/ is a full homepage duplicate** — 192 resources, 6 seconds to load, then gated behind password. User sees the same homepage after entering password. Wasted page.

4. **No mobile navigation anywhere** — 3 different nav patterns across 6 pages. Users cannot navigate on mobile without browser back button.

5. **Blog alt text missing on 8/13 images** — Direct image SEO impact.

6. **Audio player not detected on blog posts** — Audio produced via ElevenLabs but may not be deploying to CF Pages.

---

## A/B Tests Identified (7 tests)

1. Hero CTA text: "Begin Awakening" vs "Start Your Free AI Assessment" vs "Talk to Your Future AI"
2. Pricing order: low-to-high vs high-to-low (anchoring)
3. Blog CTA position: bottom-only vs mid-article + bottom
4. Social proof placement: below hero vs trust strip immediately below headline
5. Compare page CTA: generic vs "See How PureBrain Compares to Your Current AI"
6. Newsletter position: below fold vs inline after post #3
7. Audio player: secondary vs featured above-fold option

---

## SEO Quick Wins

- WebSite + Organization schema missing from homepage (1 hr to add)
- ItemList schema missing from /compare/ (16 tools = rich result opportunity)
- No internal linking between blog posts (ongoing, high cumulative impact)
- Author schema for Aether entity (novel E-E-A-T differentiator)

---

## Performance Baseline (confirmed Mar 17)

- Homepage: 7,164ms DOM / 211 resources / 17.9 MB
- Blog posts: 333ms DOM / 9 resources — CF Pages fast
- Primary fix: defer Three.js init, lazy-load testimonials, extract critical CSS

---

## Report Location

/home/jared/projects/AI-CIV/aether/exports/overnight-content-mar19/website-analysis-mar19.md
