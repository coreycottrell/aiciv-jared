# Memory: PureBrain.ai Website Analysis & A/B Test Plan — March 20, 2026

**Date**: 2026-03-20
**Type**: synthesis + operational
**Tags**: purebrain, website-analysis, ab-tests, SEO, sitemap, schema, audio, twitter-card

---

## Context

Overnight analysis building on March 19 report. New findings confirmed against CF Pages deployed files.

---

## New Findings vs. March 19

1. **4 blog posts confirmed missing from sitemap**: prompting-is-dead, what-i-named-my-ai, why-enterprises-are-betting-on-agentic-ai, why-your-ai-should-have-a-name. Sitemap has 27, deployed has 31.

2. **Audio player confirmed absent** from all blog posts examined (the-context-tax, your-ai-has-no-idea-who-you-are). Tools/blog_audio.py needs to run against all 31 posts.

3. **Joseph Diosana testimonial photo** uses local path `/wp-content/uploads/joseph-diosana-headshot.jpg` — does not exist on CF Pages. Broken image.

4. **14 vs/compare pages** exist as SEO assets with no ItemList schema on the compare hub.

5. **Twitter card title confirmed "Elementor #1502"** on homepage (lines 364, 369) AND insiders page. Two separate fixes needed.

6. **Insiders page** also has broken og:title = "Elementor #1502 - Pure Brain".

7. **Homepage has ZERO schema markup** — no WebSite, Organization, or SoftwareApplication schemas.

8. **No Article schema** in any blog posts.

---

## A/B Tests Defined (8 total)

- AB-01: Hero CTA — "Awaken Your PURE BRAIN" vs "Meet Your AI Partner — Start Free"
- AB-02: Social proof above fold vs bottom-only
- AB-03: Pricing order high-to-low vs low-to-high
- AB-04: Demo video above vs below features
- AB-05: Mid-post CTA + bottom vs bottom-only
- AB-06: Hero description long vs short copy
- AB-07: Compare page personalized CTA via URL param
- AB-08: Waitlist form 2-field vs 5-field

---

## Report Location

/home/jared/projects/AI-CIV/aether/exports/overnight-content-mar20/website-analysis-mar20.md

Delivered: Telegram (confirmed ok), Portal (fallback mode)
