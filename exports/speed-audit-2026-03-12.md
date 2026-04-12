# purebrain.ai Full Speed Audit
**Date**: 2026-03-12
**Conducted by**: dept-systems-technology (CTO + full-stack + devops + performance-optimizer)
**Method**: Live server diagnostics + curl TTFB measurements + HTML composition analysis + asset audits

---

## Current Performance Metrics

### TTFB and Page Weight (measured from VPS, no browser cache)

| Page | TTFB | Total Transfer | HTML Size | HTTP |
|------|------|----------------|-----------|------|
| Homepage `/` | 0.23s | 0.41s | 674 KB HTML | 200 |
| Blog `/blog/` | 0.22s | 0.24s | 73 KB HTML | 200 |
| Pay-Test-2 `/pay-test-2/` | 0.18s | 0.26s | 794 KB HTML | 200 |
| Invitation `/invitation/` | 0.15s | 0.17s | 82 KB HTML | 200 |
| Training `/brainiac-mastermind-training/` | 0.15s | 0.16s | 59 KB HTML | 200 |

**Important context**: TTFB above is measured from the VPS (low latency, ideal conditions). Real user TTFB from a browser will be higher because:
- Cloudflare cache-control: `max-age=0, must-revalidate` — HTML is NEVER cached by browser or CDN edge
- `cf-cache-status: DYNAMIC` — Cloudflare passes EVERY request through to WordPress origin (no edge caching)
- Every page load hits WordPress origin cold

### Page Composition Breakdown

| Page | Ext JS | Inline JS | Inline CSS | Videos |
|------|--------|-----------|------------|--------|
| Homepage | 110 files | 260 KB | 249 KB | 2 (86MB + 70MB) |
| Pay-Test-2 | 110 files | 384 KB | 246 KB | 2 |
| Blog index | 0 files | 4 KB | 29 KB | 0 |
| Invitation | 0 files | 32 KB | 27 KB | 0 |
| Training | 1 file | 17 KB | 25 KB | 0 |

---

## Top 10 Speed Issues Ranked by Impact

---

### Issue #1 — CRITICAL: WordPress Admin Bar Rendering for ALL Visitors
**Impact**: SEVERE — adds 78+ extra JS files, block editor, Gutenberg JS to every page load

**What is happening**: The WordPress admin bar is being rendered in the HTML for anonymous visitors. The HTML contains the full admin bar markup including menus for "Edit with Elementor", "Yoast SEO", "GoDaddy Quick Links", "Web push", and "Logout". This means WordPress is treating page requests as if they are from a logged-in admin.

**Evidence**: Admin bar HTML spans thousands of characters in the source. The block editor JS files (`block-editor.min.js`, `blocks.min.js`, `editor.min.js`, `components.min.js`) are all loading because of admin context. 78 of the 110 external JS files are `wp-includes` files that only need to load for logged-in users.

**Root cause**: The exported CF Pages HTML was captured while logged in as Jared, and the admin bar HTML was included in the export. The static export is serving admin-state HTML to the public.

**Fix**: Re-export the pages while logged OUT of WordPress, or add a plugin filter to strip `show_admin_bar( false )` for non-admin requests. For CF Pages static exports specifically — always export while in an incognito/logged-out session.

**Potential savings**: Removing 78+ JS file references from the HTML reduces initial parse time significantly. The JS files themselves may not load (they are WP-origin URLs and may 404 or redirect), but the browser still attempts to fetch them.

---

### Issue #2 — CRITICAL: Zero Cloudflare HTML Caching
**Impact**: SEVERE — every user request hits WordPress origin

**What is happening**:
```
cache-control: public, max-age=0, must-revalidate
cf-cache-status: DYNAMIC
```
Cloudflare is set to DYNAMIC for all pages, meaning every page request bypasses the CDN edge and goes to WordPress origin. There is no edge caching of HTML pages at all.

**Fix**: Enable Cloudflare Page Rules or Cache Rules to cache HTML at the edge:
- Set cache TTL for static pages to at least 1 hour (3600s)
- Exclude: `/wp-admin/`, `/wp-login.php`, any pages with `?` params
- This alone could make the site feel 3-5x faster for most users by serving cached HTML from the nearest Cloudflare edge node instead of round-tripping to the GoDaddy WordPress server

**Cloudflare Dashboard**: Caching > Cache Rules > Create rule:
- If URL path does not contain `/wp-admin` AND does not contain `/wp-login`
- Then: Cache Eligibility = Eligible for cache, Edge TTL = 1 hour

---

### Issue #3 — HIGH: Homepage and Pay-Test-2 are 674KB and 794KB HTML
**Impact**: HIGH — massive initial download before any JS/CSS loads

**What is happening**: The homepage HTML alone is 674 KB. Pay-test-2 is 794 KB. This is the raw HTML document. For comparison, blog posts (optimized CF Pages export) are 59-82 KB.

**Breakdown of homepage 674 KB**:
- 259 KB inline JavaScript (79 blocks)
- 249 KB inline CSS (25 blocks)
- Admin bar HTML: ~80 KB
- GoDaddy stock photos JS template: ~61 KB inline script (one of the largest single blocks)
- PayPal + chatflow JS: ~122 KB inline

**Fix**:
1. Move large inline scripts to external `.js` files served from Cloudflare R2 with long-lived cache headers
2. Remove admin bar from exports (Issue #1)
3. Remove GoDaddy stock photos template script (only needed in WP admin)
4. Consolidate inline CSS into a single external stylesheet

---

### Issue #4 — HIGH: Two Background Videos Autoloading (86MB + 70MB)
**Impact**: HIGH — on mobile/slow connections, video preload can consume all bandwidth before the page is interactive

**What is happening**:
- `Pure-Brain-Demo-Video-real-compression-and-sizing.mp4` — **86 MB** (89,907,843 bytes)
- `PureResearch.ai-1.mp4` — **70 MB** (73,932,678 bytes)

Both are R2-hosted videos. Both appear in the homepage source.

**Fix**:
1. Verify both videos use `preload="none"` or `preload="metadata"` in their `<video>` tags — never `preload="auto"`
2. For background videos: use `poster` attribute with a static image, only play on user action or when element enters viewport
3. Consider further compressing videos — 86 MB is extremely large for a background video. Target: under 5 MB for a 30-second loop at 720p with good compression

---

### Issue #5 — HIGH: Static Asset Cache Headers are Weak (14400s = 4 hours)
**Impact**: HIGH — browser cache expiry every 4 hours means repeat visitors re-download everything

**What is happening**:
```
cache-control: public, max-age=14400, must-revalidate
cf-cache-status: EXPIRED / REVALIDATED
```
Static assets (CSS, JS, images) use 4-hour max-age. For versioned files (with `?ver=3.35.4`) this is wasteful — the version query string ensures cache-busting on updates, so these files could be cached for months.

**Fix**: Increase static asset cache to 1 year for versioned files:
```
cache-control: public, max-age=31536000, immutable
```
In Cloudflare: Create a Cache Rule for `/wp-content/*` and `/wp-includes/*` with Edge TTL = 1 year.

---

### Issue #6 — HIGH: Four Separate Google Fonts Requests
**Impact**: HIGH — each Google Fonts request is a render-blocking round trip to fonts.googleapis.com

**What is happening**: The homepage makes 4 separate Google Fonts requests:
1. Roboto (all 18 weights + italic variants)
2. Roboto Slab (all 18 weights)
3. Plus Jakarta Sans (variable font, 200-800 weights)
4. Oswald (400, 500, 600, 700 weights)

Loading 4 font families with dozens of weight variants = heavy font download + render blocking.

**Fixes**:
1. Consolidate into ONE Google Fonts request with only the weights actually used
2. Add `&display=swap` to all font requests (already partially done)
3. Self-host fonts in R2/Cloudflare for zero external DNS lookup
4. Drop Roboto and Roboto Slab if not visually evident — Plus Jakarta Sans + Oswald are the intentional brand fonts
5. For Roboto: limit to weights 400 and 700 only (not all 18 variants)

**Estimated savings**: 200-500ms on first load by reducing from 4 requests to 1, and limiting weights

---

### Issue #7 — MEDIUM: GoDaddy Stock Photos Script Loading on Frontend
**Impact**: MEDIUM — 61 KB inline JS template that is only relevant inside WP admin

**What is happening**: Script 64 in pay-test-2 is 60,626 characters of GoDaddy Stock Photos data (`wpaas_stock_photos`). This is a WP admin feature for browsing stock photos in the media library. It has no function on the public-facing site.

**Fix**: GoDaddy hosting's mu-plugin injects this on all pages. Cannot be removed without a custom plugin that uses `wp_dequeue_script('wpaas-stock-photos')`. Add this to the custom purebrain plugin:
```php
add_action('wp_enqueue_scripts', function() {
    wp_dequeue_script('wpaas-stock-photos');
    wp_dequeue_style('wpaas-stock-photos-css');
}, 100);
```

---

### Issue #8 — MEDIUM: Zero Image Optimization (No WebP)
**Impact**: MEDIUM — PNG images are 2-5x larger than equivalent WebP

**What is happening**: Every image on the site is PNG or JPG — zero WebP. Key offenders:
- `cropped-MA1.BI-1.2.4-002-211107-Icon-PT.png` — loaded 3x on homepage (same file repeated)
- `jared-sanborn-headshot-official.png` — headshot as PNG instead of WebP/JPG
- `MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png` — scaled PNG
- `purebrain-spirograph-transparent.png` — loaded 7x on pay-test-2

**Fix**:
1. Install WP plugin: Imagify or ShortPixel — auto-convert uploads to WebP
2. Use `<picture>` tags with WebP fallback for key images
3. Fix duplicate image loads — the spirograph PNG loading 7 times is likely a code bug (same asset in a loop)

---

### Issue #9 — MEDIUM: WordPress Mailin (Brevo) Plugin JS on All Pages
**Impact**: MEDIUM — unnecessary external script load

**What is happening**: `mailin-front.js` (Brevo/SendinBlue plugin) loads on every page. This plugin is for web push notifications and contact forms. It shouldn't load on payment pages or pages where it is not used.

**Fix**: Conditionally enqueue — only load on pages where the form or push feature is active:
```php
add_action('wp_enqueue_scripts', function() {
    if (!is_page(['contact', 'blog'])) {
        wp_dequeue_script('mailin-front');
    }
}, 100);
```

---

### Issue #10 — MEDIUM: VPS Disk at 77% (28GB used of 38GB)
**Impact**: MEDIUM — approaching the threshold where performance degrades

**What is happening**: VPS root filesystem is 77% full with only 8.6 GB remaining. At 90%+ disk usage, write performance degrades and some services may fail.

**What to clean**:
```bash
# Check log sizes
du -sh /var/log/* 2>/dev/null | sort -h | tail -20
# Check old Docker images if present
docker system prune 2>/dev/null
# Check large files in /tmp
du -sh /tmp/* 2>/dev/null | sort -h | tail -10
# Check Aether project logs
du -sh /home/jared/projects/AI-CIV/aether/logs/*
```

---

## Quick Wins (can implement today, high ROI)

| Fix | Effort | Impact | Expected Improvement |
|-----|--------|--------|---------------------|
| Enable Cloudflare HTML caching (Cache Rules) | 15 min | SEVERE | 3-5x TTFB reduction for repeat visitors |
| Re-export CF Pages HTML logged out | 30 min | SEVERE | Removes 78+ admin JS references |
| Consolidate Google Fonts to 1 request, 2 weights only | 30 min | HIGH | 200-500ms faster first render |
| Set video `preload="none"` + poster image | 1 hour | HIGH | Prevents 156MB background download |
| Add wp_dequeue for admin-only scripts | 1 hour | HIGH | Removes GoDaddy stock photos + mailin from frontend |
| Increase static asset cache to 1 year | 15 min | HIGH | Repeat visitor JS/CSS load = instant |

---

## Longer-Term Optimizations (this week)

| Fix | Effort | Impact |
|-----|--------|--------|
| Convert all images to WebP (install Imagify/ShortPixel) | 1 hour setup | 30-60% image size reduction |
| Move inline JS to external files with long-lived cache | 2-4 hours | 300-500 KB savings on homepage HTML |
| Fix duplicate image loads (spirograph x7 on pay-test-2) | 1 hour | Eliminates unnecessary repeat requests |
| Compress background videos under 5MB each | Video work | Eliminates 150MB+ background video |
| Self-host Google Fonts in R2 | 2 hours | Removes external DNS round trips |
| Install WP Rocket or LiteSpeed Cache | 2 hours setup | Page caching, CSS/JS minification, lazy load |
| Disk cleanup — logs and temp files | 1 hour | Prevent future degradation |

---

## Architecture Summary

**How purebrain.ai is currently served**:
1. Users hit `purebrain.ai` → Cloudflare (DNS + proxy)
2. Cloudflare passes through to **GoDaddy WordPress hosting** (no edge caching — `DYNAMIC`)
3. WordPress serves page HTML dynamically every request
4. Homepage/pay-test-2 pages appear to be CF Pages static exports embedded in WordPress (based on HTML comment structure)
5. Blog posts and some pages are clean CF Pages exports (fast, lean)
6. The portal (`portal.purebrain.ai` / `app.purebrain.ai`) routes through this VPS nginx → portal_server.py on port 8097

**This VPS hosts**:
- nginx proxy for portal subdomains (port 8099)
- portal_server.py (port 8097, Python Flask/async)
- telegram_bridge.py
- Aether AI system
- Does NOT host the main WordPress site

---

## Verification Evidence

All data collected via live curl requests 2026-03-12 20:56-21:15 UTC.

Files collected:
- `/tmp/purebrain-homepage.html` — full homepage HTML (690,403 bytes)
- TTFB measurements via `curl -w` timing format
- Asset counts via Python regex analysis of live HTML
- Cache headers via `curl -sI` on all key URLs

---

*Report generated by dept-systems-technology | 2026-03-12*
*BUILD -> SECURITY REVIEW -> QA -> SHIP*
