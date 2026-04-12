# Analytics Deep Dive: GTM Confirmed, Site Scale-Up, Indexing Still Zero

**Date**: 2026-02-24
**Agent**: web-researcher
**Type**: synthesis
**Topic**: PureBrain.ai analytics audit - GTM confirmation, site growth from 19 to 34 URLs, indexing status, OG tag verification
**Confidence**: high (live site verification + sitemap crawl + search confirmation)

---

## Context

Overnight deep dive analytics audit for purebrain.ai. Built on three prior memory entries from Feb 22-23.

---

## Key Discoveries

### 1. GTM-WTDXL4VJ Confirmed as Analytics Delivery Mechanism

Google Tag Manager container GTM-WTDXL4VJ is confirmed live on ALL pages (homepage, blog, all posts checked). This is significant because:
- GA4 and Clarity are likely loaded THROUGH GTM, not as direct page scripts
- This explains why no G-XXXXXXXXXX measurement ID appears directly in page HTML
- GA4 status is unknown until GTM container is inspected at tagmanager.google.com
- WonderPush push notifications are ALSO installed (separate from GTM)
- Brevo/Mailin tracking active via plugin

**Action**: Jared needs to check GTM container to confirm whether GA4 and Clarity tags exist inside it.

### 2. Site Grew from 19 to 34 URLs Overnight

Sitemap inventory confirmed 34 total URLs (10 posts + 24 pages). New pages added Feb 23-24:
- 8 competitor comparison pages (/purebrain-vs-chatgpt/, etc.)
- /compare/ - interactive comparison tool (16 AI tools)
- /migrate/ - AI history migration portal
- /ai-website-analysis/ - $99 service page
- /website-execution/ and /ai-website-execution/
- /ai-tool-stack-calculator/ - free tool (151 tools, 31 categories)
- /about-aether/ - Aether identity page

### 3. OG Tags: Blog Posts CONFIRMED, New Pages INCOMPLETE

Blog posts have complete OG tags (title, description, image) - confirmed on 3 posts.
New pages have gaps:
- /compare/ - MISSING all OG tags
- /about-aether/ - Missing OG description and image
- /migrate/ - Missing OG description and image
- /ai-website-analysis/ - Incomplete (only icon image, no description)
- /ai-tool-stack-calculator/ - Has title and image, MISSING description

### 4. Google Indexing Still Zero

Confirmed again today: site:purebrain.ai returns zero results. "purebrain.ai AI partnership" search returns no purebrain.ai results. GSC verification remains the single most urgent action.

### 5. WonderPush is an Unexpected Analytics Source

WonderPush (push notification service) is installed and provides:
- Subscriber count
- Opt-in rate (% of visitors who accept push)
- Notification open rates
- Per-post push engagement

This is a third data source Jared can check for engagement signals beyond GA4 and Brevo.

### 6. Performance Risk: /ai-website-analysis/ Has 1000+ Lines Inline CSS

The website analysis service page has 1000+ lines of CSS inline in the HTML. This is render-blocking, non-cacheable, and a significant performance drag. Needs refactoring to external stylesheet.

---

## When to Apply

- Any future analytics audit for purebrain.ai
- When GTM status question comes up (answer: GTM-WTDXL4VJ, check inside it for GA4)
- When OG tag fixes are assigned (new pages need fixing, blog posts are done)
- When performance optimization is discussed (inline CSS on /ai-website-analysis/ is key target)
- When explaining why Google can't find purebrain.ai (indexing is zero, GSC not verified)

---

## Memory Written

Path: .claude/memory/agent-learnings/web-researcher/2026-02-24--analytics-deep-dive-gtm-confirmed.md
Type: synthesis
Topic: PureBrain.ai analytics audit Feb 24 - GTM confirmed, 34 URLs, indexing zero

Deliverable report: /home/jared/projects/AI-CIV/aether/to-jared/overnight/analytics-deep-dive-2026-02-24.md
