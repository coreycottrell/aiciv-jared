# Blog Format Verification - 90 Days Post

**Date**: 2026-02-26
**Agent**: browser-vision-tester
**Type**: operational

## Context

Verified visual formatting of "The First 90 Days of an AI Partnership" blog post on both purebrain.ai and jareddsanborn.com. Compared against reference post "Your AI Has No Memory. Mine Does." on purebrain.ai.

## Findings

### purebrain.ai post
- Dark brand theme renders correctly
- Title, date, category all display
- Hexagonal banner graphic renders full-width
- AETHER footer nav bar present
- Matches reference post format

### jareddsanborn.com post
- Standard WordPress theme (different from purebrain.ai - expected)
- Title, byline, date render correctly
- Same hexagonal banner graphic renders with credit lines below it
- "AETHER - AI PARTNER AT PURE TECHNOLOGY" and "Aether Your AI Partner at PUREBRAIN.ai" credit lines show under banner
- Right sidebar visible (WP default)
- Content body begins below banner (first H2 section visible)

## Playwright Gotcha

jareddsanborn.com times out with `wait_until="networkidle"` at 30s. Use `wait_until="domcontentloaded"` + `page.wait_for_timeout(3000)` instead. This is a recurring pattern for JDS site.

## Screenshot Paths

- `/home/jared/projects/AI-CIV/aether/exports/screenshots/blog-format-verify/purebrain-90days.png`
- `/home/jared/projects/AI-CIV/aether/exports/screenshots/blog-format-verify/jds-90days.png`
- `/home/jared/projects/AI-CIV/aether/exports/screenshots/blog-format-verify/purebrain-reference.png`

## When to Apply

Use domcontentloaded + wait for JDS screenshots going forward. Both sites' blog posts are formatting correctly.
