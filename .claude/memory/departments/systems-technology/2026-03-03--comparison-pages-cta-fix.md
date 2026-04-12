# Comparison Pages CTA Fix — 2026-03-03

## Task
Fix "Get Started Free" → "Get Started" and `/start` → `https://purebrain.ai/#awakening` on all comparison pages.

## Audit Results
Fetched all 11 comparison pages (IDs: 1190, 1044, 752-760).

Only 2 needed fixes:
- **Page 1190** (purebrain-vs-glbgpt): `Get Started Free` text + `https://purebrain.ai/start` link (2x)
- **Page 1044** (purebrain-vs-sitegpt): `Start Free` nav CTA text (link already at #awakening)

Pages 753-760, 752: Already clean — using `#awakening` with correct text.

## Fixes Applied
- Page 1190: `Get Started Free` → `Get Started` (1x), `https://purebrain.ai/start` → `https://purebrain.ai/#awakening` (2x)
- Page 1044: `Start Free` → `Get Started` in nav CTA only (targeted replace via `class="pb-nav-cta">Start Free</a>`)

## Deployment
- REST API `POST /wp-json/wp/v2/pages/{id}` with `content` field
- Elementor cache cleared: `DELETE /elementor/v1/cache` → 200 OK
- No elementor_data involved — all fixes were in `content.raw`

## QA Verification
Both API-level and live HTTP verification passed:
- No `Get Started Free`, no `Start Free` in nav, no `/start` links
- `#awakening` present on both pages (2x on 1190, 3x on 1044)

## Security Review
- Pure string replacements, no new HTML added
- No display:none, no new scripts, no CSP changes
- CLEAN

## Pattern: Comparison Page Template Gotcha
Pages 753-760 were created with a later template that already had the correct patterns.
Pages 1190 and 1044 used an older template with different button text and broken `/start` href.
When creating new comparison pages, use the 753-760 template as the canonical reference.
