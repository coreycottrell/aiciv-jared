# PureBrain.ai Site Analysis - April 2026

## Summary
Deep technical + UX + conversion analysis of purebrain.ai. Overall score: 6.2/10.

## Key Findings
- Homepage 638KB HTML, 24 scripts, 15 inline styles, 244 Elementor refs
- ALL 4 payment pages share identical meta tags (duplicate content risk)
- Zero Cloudflare HTML caching (max-age=0, must-revalidate) -- STILL not fixed since March audit
- 4 separate Google Font requests loading 40+ variants (only ~6 used)
- Missing HSTS, CSP, X-Frame-Options security headers
- Blog shows only 3 of 34 posts (no pagination)
- Single testimonial from founder only -- no third-party social proof
- Referral program buried at position 10/11 on homepage
- robots.txt has conflicting rules for AI crawlers

## Architecture Confirmed
- CF Pages serving static HTML export of WordPress
- PayPal JS SDK v2 Smart Buttons on payment pages
- Clarity + GTM + WonderPush integrations active
- R2 for video hosting (2 MP4s on homepage)
- Sitemap: 100 URLs indexed

## Payment Pages
- /awakened/ $149, /partnered/ $499, /unified/ $999
- 83-84 scripts each (~447KB), /live/ is lighter (295KB, 21 scripts)
- All require separate Claude Max subscription ($100-200/mo)

## Quick Wins Identified
1. CF HTML caching (15 min, 3-5x faster)
2. Unique meta per payment page (30 min)
3. Consolidate fonts to 1 request (30 min)
4. Security headers via CF (15 min)
5. Fix robots.txt conflicts (15 min)

## Report Location
/home/jared/exports/portal-files/purebrain-site-analysis-2026-04-07.md
