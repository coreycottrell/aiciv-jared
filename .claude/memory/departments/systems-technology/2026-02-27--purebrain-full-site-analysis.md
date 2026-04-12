# Memory: PureBrain.ai Full Site Analysis — Feb 27 2026
**Date**: 2026-02-27
**Type**: synthesis + operational
**Topic**: Full website analysis — ST# overnight task

---

## Key Findings (Actionable)

### CRITICAL: Security plugin is INACTIVE
- PureBrain Security plugin v4.7.2.1 shows as INACTIVE via REST API
- This plugin handles: API key protection, user enumeration blocking, cookie flags, headers, XSS
- Deactivation drops security posture from 7.2/10 to ~5/10
- Needs immediate reactivation

### CRITICAL: Wrong background video on homepage
- Current: PureResearch.ai-1.mp4
- Expected: Neural brain animation
- Fix: Swap <source> in #bgVideo on WP page ID 11

### SEO Gap: Post ID 950 has no meta description
- Slug: your-ai-has-no-memory-mine-does
- This is one of the strongest titles on the site — missing description = Google auto-generates (worse)

### 404 Without Redirect: /ai-adoption-assessment/
- Returns 404 with no redirect
- Should 301 to /ai-partnership-assessment/

### Assessment Page Load Anomaly
- /ai-partnership-assessment/ loads in 1.13s TTFB on 155KB
- Homepage is 436KB at 0.21s TTFB
- Assessment may be bypassing Cloudflare cache

---

## Site Architecture Facts (Confirmed)

- Real homepage: WP page ID 11 (slug: pure-brain-agentic-ai-partner)
- Old homepage shell: WP page ID 383 (slug: purebrain-4) — correctly set to noindex
- Front page setting: page_on_front = 11, page_for_posts = 0
- Total pages in sitemap: 32
- Total posts in sitemap: 13
- Blog post cadence: daily
- Plugins active: Elementor 3.35.5, Yoast 27.0, Brevo 3.3.2, GTM4WP 1.22.3, Independent Analytics 2.14.4, Akismet 5.6, WP File Manager 8.0.2
- Plugin INACTIVE: PureBrain Security 4.7.2.1 (URGENT)

---

## Homepage CTA Analysis

- Primary CTA: "Join Priority Waitlist" (waitlist form)
- PayPal buttons on homepage: 0
- Waitlist form references: 143
- No direct link to /ai-partnership-assessment/ from homepage nav
- No direct purchase path visible if Awakened tier is open

---

## A/B Test Proposals Filed

- HP-01: Assessment CTA vs waitlist CTA on homepage
- HP-02: Specific tier headline vs generic
- AB-02: Pricing CTA copy variations
- AB-03: Assessment post-result personalization
- AB-04: Blog post CTA footer (assessment vs generic awakening)
- AB-05: Testimonial format (3-column grid vs text blocks)

---

## Report Location
/home/jared/projects/AI-CIV/aether/to-jared/overnight-reports/website-analysis-2026-02-27.md
26KB, 436 lines
