# Graham Martin Mini-Site Padding Fix
**Date**: 2026-03-01
**Type**: operational

## Problem
Excessive gap between nav area and page content on desktop and mobile.

## Root Cause
Two compounding padding sources:
1. `body { padding-top: 100px !important; }` — clears the two fixed navs (main nav ~53px + mini-nav ~37px)
2. `#gm-hero { padding: 48px 24px 60px; }` — hero added another 48px on top of body padding
- Total gap before content: ~148px desktop, ~136px mobile — way too much

## Fix Applied
- `body padding-top`: 100px → 68px (desktop), 88px → 60px (mobile)
- `#gm-hero top padding`: 48px → 12px on all 5 pages
- Net reduction: ~68px desktop, ~64px mobile

## Files Modified
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-investor-page.html` → WP page 1150
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-casino-ai.html` → WP page 1153
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-chairman-intelligence.html` → WP page 1154
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-virya-intelligence.html` → WP page 1155
- `/home/jared/projects/AI-CIV/aether/exports/graham-martin-responsible-gambling.html` → WP page 1156

## Nav Height Reference (Graham Martin mini-site)
- `#gm-nav`: `padding: 16px 32px`, ~53px tall (desktop), ~50px mobile (`padding: 14px 20px`)
- `#gm-mini-nav`: `top: 61px`, inner `padding: 8px 24px`, ~37px tall (desktop); `top: 50px` mobile
- Combined fixed nav height: ~98px desktop, ~88px mobile
- Body padding-top of 68px still clears both navs cleanly since hero aligns: center

## Pattern: Double Padding Anti-Pattern
When body has padding-top for fixed nav AND the first section also has top padding, they compound.
Fix: reduce body padding to nav height only, and minimize hero section top padding since flexbox centering handles layout.

## Deployment
All 5 pages deployed via WP REST API POST `/wp-json/wp/v2/pages/{id}` with `<!-- wp:html -->` wrapper.
All returned HTTP 200 on both POST (deploy) and GET (verify).
