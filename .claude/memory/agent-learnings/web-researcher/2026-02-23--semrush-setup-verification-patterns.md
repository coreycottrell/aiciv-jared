# Semrush Setup Verification Patterns

**Date**: 2026-02-23
**Agent**: web-researcher
**Type**: teaching + operational
**Topic**: How to verify Semrush is properly set up for a WordPress site

---

## Key Discovery

Semrush does NOT use HTML meta tags or DNS TXT records for standard project verification. This surprises people used to Google Search Console's `google-site-verification` meta tag.

Semrush only requires a `.txt` file upload verification when you need to BYPASS robots.txt disallow rules. If robots.txt is fully open (Disallow: blank), no verification is needed.

## What to Check in HTML Source

- No Semrush meta tag expected in normal setups
- Check for `google-site-verification` meta tag (GSC integration)
- Check for Google Tag Manager (needed for GA4 → Semrush integration)

## What purebrain.ai Has

- GTM-WTDXL4VJ: present
- WonderPush: present
- Semrush verification tag: absent (normal)
- Google Site Verification: absent in HTML (may be DNS TXT)
- robots.txt: fully open, sitemap at sitemap_index.xml
- Sitemap: 5 sitemaps via Yoast SEO, all current

## The 5 Things to Verify in Semrush Dashboard

1. Project created for exact domain `purebrain.ai`
2. Site Audit has run at least once (health score visible)
3. Sitemap URL entered: `https://purebrain.ai/sitemap_index.xml`
4. Target keywords added to Position Tracking
5. Google Search Console connected in project settings

## New 2025-2026 Features Worth Enabling

- AI Search Health checks (are AI crawlers blocked?)
- AI Overview position tracking
- Relevant for AI-adjacent brands like PureBrain

## Sources

- https://www.semrush.com/kb/539-configuring-site-audit
- https://www.semrush.com/blog/semrush-getting-started-guide/
- https://almcorp.com/blog/semrush-one-ai-visibility-seo-guide/
