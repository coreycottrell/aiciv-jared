# full-stack-developer: OG Tags Diagnostic - purebrain.ai

**Agent**: full-stack-developer
**Domain**: Full Stack Development
**Date**: 2026-02-23

---

## Executive Summary

**The analytics report's claim that "OG tags are missing" is partially incorrect.**

Yoast SEO is installed, active (v27.0), and generating OG tags on all pages. However, there are **3 real issues** that hurt social sharing performance and are worth fixing.

---

## Diagnostic Results

### Pages Checked

| Page | OG Tags Present | og:title | og:description | og:image | Issue |
|------|----------------|----------|----------------|----------|-------|
| Homepage (`/`) | YES | "Your Brain. Your AI. Actual Intelligence" | Good (156 chars) | GIF 480x270, **9MB** | **IMAGE TYPE + SIZE** |
| Blog listing (`/blog/`) | YES | "The Neural Feed - Blog - Pure Brain" | **JUNK TEXT** (nav content) | Logo PNG 512x512 | **DESCRIPTION + IMAGE** |
| `/the-ai-trust-gap/` | YES | Full title | Strong excerpt | 1280x720 JPG | GOOD |
| `/why-95-percent-of-ai-pilots-fail/` | YES | Full title | Strong excerpt | 1024x576 PNG | GOOD |
| `/the-difference-between-using-ai-and-having-an-ai-partner/` | YES | Full title | Strong excerpt | 1024x576 PNG | GOOD |
| `/why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/` | YES | Full title | Strong excerpt | 1920x1080 PNG | GOOD |
| `/ceo-vs-employee-ai-transformation-gap/` | YES | Full title | Strong excerpt | 1024x576 PNG | GOOD |

**Individual blog posts: ALL PASSING.** Every post has correct og:title, og:description, and og:image pointing to the proper banner image.

---

## The 3 Real Problems

### Problem 1: Homepage OG Image is a GIF (Critical)

**What's happening:**
- og:image = `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`
- File size: **9MB** (nine megabytes)
- Dimensions: 480x270 (too small - LinkedIn recommends 1200x627 minimum)
- Type: `image/gif`

**Why this matters:**
- LinkedIn, Facebook, and Twitter/X **cannot render animated GIFs as social share previews** — they either show a static frame or a broken image
- 9MB will **timeout** on many platforms that have a 5MB or 8MB OG image size limit
- 480x270 is below the minimum recommended size — it will appear blurry or cropped with letterboxing
- This means **every time someone shares the purebrain.ai homepage URL**, the social card looks bad or fails to load

**Fix Required:**
Upload a proper static OG image for the homepage:
- Format: JPG or PNG (not GIF, not WebP)
- Dimensions: 1200x627px (Facebook/LinkedIn standard) or 1280x720px (16:9, Twitter-friendly)
- File size: Under 1MB preferred, under 5MB required
- Content: PureBrain logo + tagline "Your Brain. Your AI. Actual Intelligence" on dark background

**How to fix in Yoast:**
1. WordPress Admin → SEO → Search Appearance → Content Types → Pages
2. Or directly: WordPress Admin → edit the homepage → scroll to Yoast SEO panel → Social tab → Upload OG image

---

### Problem 2: Blog Listing Page Has Junk OG Description (Medium)

**What's happening:**
```
og:description = "Home Subscribe AI Assessment Start Your AI Partnership PUREBRAIN.ai The Neural Feed [...]"
```

This is the raw navigation menu text being scraped as the description — it reads as meaningless word soup. When anyone shares `https://purebrain.ai/blog/`, every social platform shows this garbage text under the preview.

**Root cause:** The `/blog/` page (Page ID 319) has no Yoast SEO description set. Yoast falls back to the page content, which starts with the nav menu HTML (since it's an Elementor page). No featured image is set either.

**Fix Required:**
1. WordPress Admin → edit the Blog page (ID 319) → Yoast SEO panel → SEO tab
2. Set Meta description: `"The Neural Feed: Weekly insights on AI adoption, human-AI partnership, and the future of work. Subscribe to stay ahead."`
3. Social tab → Set a proper OG image (a blog hero banner, not the site logo)

The blog OG image is currently the site icon (512x512 square logo). This works but a custom horizontal banner looks far better in social feeds.

---

### Problem 3: Blog Posts Have No Twitter-Specific Description (Low - Enhancement)

**What's happening:**
Blog posts have `og:description` but no `twitter:description` or `twitter:title` override. Twitter/X uses the og: fallback, which works fine. However, blog posts show:
```
twitter:label1 = "Written by"
twitter:data1 = "Aether PureBrain.ai"
twitter:label2 = "Est. reading time"
twitter:data2 = "9 minutes"
```

The author showing as "Aether PureBrain.ai" is visible in Twitter cards. This is cosmetic — may want to change the WordPress author display name to "Jared Sanborn" or "Pure Brain Team" depending on brand strategy.

---

## Yoast SEO Configuration Status

**Plugin**: Yoast SEO v27.0 (latest as of Feb 2026)
**Status**: Active and generating correct OG tags for all blog posts
**OG enabled**: YES (confirmed by presence of og: tags on all pages)
**Twitter Cards enabled**: YES (twitter:card = "summary_large_image" on all pages)
**Social sharing enabled**: YES (og:locale, og:site_name present everywhere)

**No settings changes needed for Yoast itself.** The plugin is configured correctly. The issues are content-level (wrong image uploaded, no description set), not settings-level.

---

## What the Analytics Report Got Wrong

The analytics deep dive flagged "missing OG tags" but the WebFetch tool used during that research does JavaScript rendering differently from how social crawlers see the page. The raw curl output confirms all OG tags are present. The blog posts are sharing correctly.

---

## Priority Fix Plan

### Immediate (Aether can execute now without Jared approval):
None - these require either Jared-approved assets (the homepage OG image) or Jared to confirm the blog listing description copy.

### Requires Jared Input:
1. **Homepage OG image**: Need a 1200x627 static JPG or PNG of the PureBrain hero visual. Aether can generate one using Pillow (dark background, logo, tagline) — just needs Jared's approval to upload and set it.
2. **Blog listing description**: Copy above is a suggestion — Jared should approve before setting.
3. **Author display name**: "Aether PureBrain.ai" vs "Jared Sanborn" vs "Pure Brain Team" — brand decision needed.

### Aether Can Execute Immediately After Jared Approves:
- Generate the 1200x627 homepage OG image (Pillow, same dark brand treatment as banners)
- Update blog page Yoast description via WordPress REST API
- Set homepage OG image in Yoast via WordPress REST API

---

## Verification Commands Used

```bash
# Check OG tags on live pages
curl -s "https://purebrain.ai/" | grep -i "og:\|twitter:\|yoast"
curl -s "https://purebrain.ai/blog/" | grep -i "og:\|twitter:"
curl -s "https://purebrain.ai/the-ai-trust-gap/" | grep -i "og:\|twitter:"

# Verify homepage OG image file size
curl -sI "https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif"
# Result: content-length: 9033291 (9MB GIF - confirmed problem)

# Check installed plugins
curl -s -u "Aether:FlFr2VOtlHiHaJWjzW96OHUJ" "https://purebrain.ai/wp-json/wp/v2/plugins"
# Result: Yoast SEO v27.0 active - confirmed

# Check all 5 blog posts for OG completeness
# All 5 PASS with proper og:title, og:description, og:image from featured image
```

---

## Memory Written

Path: `.claude/memory/agent-learnings/full-stack-developer/2026-02-23--og-tags-diagnostic-purebrain.md`
Type: teaching + operational
Topic: OG tags are present but homepage has 9MB GIF as OG image; blog listing has junk description

---

**End of Report**
