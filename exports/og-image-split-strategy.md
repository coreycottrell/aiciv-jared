# OG Image Split Strategy: GIF for LinkedIn, Static for Twitter/X

**Date**: 2026-02-23
**Audit of**: purebrain.ai homepage
**Status**: Correct tags are present BUT a duplicate tag bug needs fixing

---

## How It Works Technically

Social platforms read different meta tags to decide which image to show:

| Platform | Tag It Reads | Result |
|----------|-------------|--------|
| **LinkedIn** | `og:image` | **Plays GIF animations** |
| **Twitter/X** | `twitter:image` (overrides `og:image` when present) | Shows static image |
| **Facebook** | `og:image` | Shows first frame of GIF as static image |

**Key insight**: Twitter/X introduced `twitter:image` specifically so sites could override the `og:image` for their platform. When both tags are present, Twitter reads `twitter:image` and ignores `og:image`. LinkedIn only knows about Open Graph (`og:image`) so it never looks at `twitter:image` at all.

---

## Which Tags Each Platform Reads

```
og:image      → LinkedIn (plays GIF!), Facebook (first frame of GIF)
twitter:image → Twitter/X ONLY (ignores og:image when twitter:image is present)
twitter:card  → Must be "summary_large_image" for full-width card on Twitter/X
```

---

## Current State of purebrain.ai

A live audit (`curl` of homepage) found these tags already present in the correct header location:

```html
<!-- For LinkedIn (GIF plays!) and Facebook (first frame) -->
<meta property="og:image" content="https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif" />
<meta property="og:image:width" content="480" />
<meta property="og:image:height" content="270" />
<meta property="og:image:type" content="image/gif" />

<!-- For Twitter/X (static image) -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg" />
```

Both image files confirmed live (HTTP 200):
- GIF: `Pure-Brain-Vid-3.gif` — 8.8MB, 480x270
- Static: `purebrain-homepage-og.jpg` — 54KB

**The strategy is correctly implemented in the header.**

---

## CRITICAL BUG: Duplicate twitter:image Tag

A second set of OG tags appears much later in the HTML (line ~2571), injected by Elementor:

```html
<!-- WRONG: second tag lower in the page, injected by Elementor -->
<meta name="twitter:image" content="https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif" />
```

This second `twitter:image` points to the GIF, not the static JPG. Twitter/X crawlers may read the **last** occurrence of a duplicate meta tag, meaning the wrong image gets shown on Twitter despite the correct tag being in the header.

---

## What Shahbaz / Jared Need to Add to WordPress Header

The header is already correct. The only action needed is:

### Fix: Remove Elementor's Duplicate twitter:image

1. Open WordPress admin → Pages → Homepage (ID: 11)
2. Edit with Elementor
3. Click the hamburger (top-left) → Site Settings OR click the page settings gear icon
4. Look for "Social" or "SEO" panel in page settings
5. If there is a Twitter Image field set to the GIF URL — clear it
6. Alternatively: in Yoast/RankMath settings for the homepage, check if a Twitter image is separately configured there
7. After saving, use **Twitter Card Validator** to confirm only `purebrain-homepage-og.jpg` appears

### If Starting Fresh (adding tags for a new page)

Add these to the WordPress `<head>` via your SEO plugin (Yoast or RankMath) or a custom header code field:

```html
<!-- Open Graph — for LinkedIn (GIF plays) and Facebook (first frame) -->
<meta property="og:image" content="https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif" />
<meta property="og:image:width" content="480" />
<meta property="og:image:height" content="270" />
<meta property="og:image:type" content="image/gif" />

<!-- Twitter Card — for Twitter/X (static image) -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg" />
```

**Do not add these a second time in Elementor page settings.** One set in the header is correct. Two sets causes the duplicate bug.

---

## Verification Tools

After any change, verify with:

| Tool | URL | What to Check |
|------|-----|---------------|
| LinkedIn Post Inspector | https://www.linkedin.com/post-inspector/ | Should show animated GIF |
| Twitter Card Validator | https://cards-dev.twitter.com/validator | Should show static JPG only |
| Facebook Sharing Debugger | https://developers.facebook.com/tools/debug/ | Should show first frame of GIF |

Paste `https://purebrain.ai/` into each and check the image preview. Use "Scrape Again" to bust platform-side cache.

---

## Visual Proof of Concept

See the full test page with live image previews and platform routing diagram:
`/home/jared/projects/AI-CIV/aether/exports/og-image-test-page.html`

---

## Summary

The split strategy is already working correctly in the WordPress header. LinkedIn will play the GIF, Twitter/X will show the static JPG, and Facebook will show the GIF's first frame. The only outstanding issue is that Elementor is injecting a duplicate `twitter:image` tag pointing to the GIF — this second tag must be removed from Elementor's page settings to ensure Twitter/X reads the correct static image.
