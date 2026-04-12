# PureBrain.ai Full Site Audit — 2026-03-01

**Type**: Site audit findings — technical, SEO, security, UX
**Report**: `/home/jared/projects/AI-CIV/aether/exports/overnight-site-analysis.md`

## Critical Findings (Act First)

### CRITICAL: Three embedded HTML documents on homepage
- Elementor HTML widgets on homepage contain full `<!DOCTYPE html>` documents (not just content)
- Causes: 3 title tags, 3 viewport metas, 2 canonical tags, 7 duplicate Google Font calls
- Homepage HTML is 467 KB because of this — unusually large
- Fix: strip `<head>` sections from Elementor HTML widgets, keep only `<body>` content
- Found at approximately chars 97,231 and 172,678 in the page source
- Widget type: `data-widget_type="html.default"`

### SECURITY: wp-login.php fully exposed
- Returns HTTP 200 with no protection
- No rate limiting or CAPTCHA visible from headers
- Combined with author enumeration below — brute force ready

### SECURITY: Admin username leaked via ?author=1
- `https://purebrain.ai/?author=1` redirects to `/author/835655pwpadmin/`
- Admin username `835655pwpadmin` is now publicly known
- Fix: block `?author=` redirects in PureBrain Security plugin

### SECURITY: WP File Manager plugin installed
- WP File Manager v8.0.2 — historically high CVE plugin
- Should be evaluated for removal if not actively needed

## Performance Facts
- TTFB: ~130ms (excellent — Cloudflare CDN hitting)
- HTTP/2 + HTTP/3 (QUIC) both active
- Cache: 31-day TTL, consistently HIT
- 21 CSS link tags + 215 KB inline CSS = high render-blocking potential
- No preload hints for critical fonts or hero images
- 0/15 blog posts have FAQPage schema (missed rich results opportunity)

## SEO Issues
- Post ID 1139 (`your-ai-doesnt-work-for-you`) missing meta description
- Homepage OG image is a 480x270 GIF — should be 1200x630 PNG
- `/video-test/` is indexed by Google (test page)
- 20+ backup/test pages published without noindex
- "Origin Story" category has 0 posts — delete it
- Admin email is `JaredSanborn@yahoo.com` — should be `jared@puretechnology.nyc`

## UX Gaps
- No navigation menu on homepage (intentional but hurts cold traffic)
- No social proof / testimonials anywhere on homepage
- No pricing visible on homepage
- Pay test pages publicly accessible (security and UX risk)
- Blog posts have no related posts links or read time

## Top Quick Wins
1. Fix admin email (5 min)
2. Add meta description to post 1139 (5 min)
3. Noindex test pages (20 min)
4. Replace OG image with 1200x630 PNG (45 min)
5. Add FAQPage schema to all 15 posts (3-4 hrs)
6. Strip embedded HTML heads from Elementor widgets (2-4 hrs)
7. Block wp-login.php + fix author enum (2 hrs)
