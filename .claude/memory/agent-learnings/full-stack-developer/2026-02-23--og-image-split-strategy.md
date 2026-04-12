# OG Image Split Strategy: Platform-Specific Social Images

**Date**: 2026-02-23
**Type**: teaching
**Topic**: How to serve GIF to LinkedIn and static image to Twitter/X using og:image + twitter:image split

---

## What Was Built

- Test page: `exports/og-image-test-page.html` — visual proof of concept with live image previews, platform routing diagram, validator links
- Strategy doc: `exports/og-image-split-strategy.md` — concise summary for Shahbaz/Jared

## Key Pattern

```
og:image      → LinkedIn (plays GIF!), Facebook (first frame only)
twitter:image → Twitter/X ONLY — overrides og:image when present
twitter:card  → Must be "summary_large_image"
```

## Live Discovery on purebrain.ai Homepage

The correct tags ARE already present in the header:
- `og:image` = `Pure-Brain-Vid-3.gif` (8.8MB, 480x270) — confirmed 200 OK
- `twitter:image` = `purebrain-homepage-og.jpg` (54KB) — confirmed 200 OK

## CRITICAL BUG FOUND

Elementor injects a SECOND set of OG tags around line 2571 of the HTML. The second `twitter:image` points to the GIF, not the static JPG. Twitter crawlers may read the last occurrence of duplicate tags. This defeats the whole strategy.

Fix: In Elementor page settings for homepage (Page ID 11), clear the Twitter image field. One set in header is correct; Elementor must not add a second set.

## Dead End to Avoid

- Do not add twitter:image in BOTH the SEO plugin header AND Elementor page settings — the duplicate causes the wrong image to show on Twitter/X
