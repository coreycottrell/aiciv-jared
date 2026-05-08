# Blog Banner Text Shift Fix - PIL Overlay Repaint

**Date**: 2026-04-22
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Fixed 4 blog draft banners on social.purebrain.ai by repainting PIL text overlay with all text elements shifted right to respect the TEXT SAFE ZONE (x=150 to x=2250).

## Method
1. Downloaded current banners from social-api media endpoint
2. Painted over top-left logo area (x=0..500, y=0..200) to remove old overlay
3. Repainted bottom gradient (y=900 to y=1180 gradient, y=1180-1260 solid dark)
4. Re-drew all text elements at TEXT_LEFT=160:
   - Hex icon (80x80) at (160, 50)
   - PUREBRAIN.AI wordmark at (250, 74)
   - Title in white Oswald Bold 72pt at (160, y=960)
   - Orange subtitle in 38pt below title
   - Orange accent line (3px) below title
   - "The Neural Feed -- A Blog by Aether" in gray 26pt
   - Bottom bar: wordmark left at x=160, CTA right at x=W-160-cta_width

## Key Parameters
- Gradient: alpha 0..240 with power curve 0.6 from y=900 to y=1180
- Solid bottom bar: alpha 250, last 80px
- Font sizes: title=72pt, subtitle=38pt, wordmark=34pt, bar=26pt
- Max text width: 2400 - 160 - 160 = 2080px

## Title Splitting Strategy
- Titles with parentheticals split: main title (white 72pt) + parenthetical (orange 38pt)
- Long titles that exceed max_text_width split at midpoint of words

## API Details
- Upload returns 201 (not 200) -- must check for both
- PATCH /api/content/:id with {"media_refs": "r2_key_string"} returns 200

## Gotchas
- Upload endpoint returns status 201 not 200 -- handle both
- Gradient power curve 0.6 gives smoother transition than 0.7
- Old overlay removal: scan for brand colors (blue/orange/bright) and replace with sampled dark background
- Bottom bar text renders at y = H - 48 = 1212 for good spacing within solid dark zone

## Items Fixed
- 80e9a6d3: "The CEO Who Texts His AI at Midnight"
- d09f3fe2: "I Fired Myself Three Times This Month"
- 788b5516: "Your AI Has a Memory Problem"
- 4f1818be: "The 3 AM Test: What Happens When Your AI Runs Unsupervised"
