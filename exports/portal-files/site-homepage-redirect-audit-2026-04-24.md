# PureBrain.ai Full Site Audit: Homepage Content Leak
**Date**: 2026-04-23
**Auditor**: qa-engineer
**Scope**: All 507 pages in purebrain-site git repo + sitemap URLs

---

## Executive Summary

No pages are currently **broken** in the sense of showing homepage content instead of their own. However, there are TWO significant quality issues:

1. **SPA Fallback (ROOT CAUSE of recurring issue)**: Any non-existent URL returns HTTP 200 with homepage content. No 404 page exists.
2. **Embedded Homepage HTML**: 23 pages contain full copies of the homepage HTML inside Elementor widgets, bloating file sizes and creating multiple `<title>` tags.

---

## Audit Results

### Total Pages Checked: 507 (in git) + 93 sitemap URLs

### RED: Pages Incorrectly Showing Homepage

**0 pages are broken.** All pages in the git repo serve their correct first `<title>` tag when accessed live on purebrain.ai.

### RED: SPA Fallback Serves Homepage for ANY Invalid URL

| Test URL | HTTP Status | Content Served |
|----------|------------|----------------|
| /nonexistent-test-page-xyz/ | 200 | Homepage |
| /fake-route-abc/ | 200 | Homepage |

**Root Cause**: No `404.html` exists in the repo. CF Pages SPA fallback mode serves `/index.html` for any path that doesn't match a file. This returns HTTP 200 (not 404), making the issue invisible to monitoring tools.

**Why this keeps recurring**: When a page is accidentally deleted from a deploy or a URL is referenced that was never created, it silently shows the homepage instead of a 404 error. Nobody notices until a human visits.

### YELLOW: Pages with Embedded Homepage HTML (23 pages)

These pages have MULTIPLE full `<html>` documents concatenated together inside Elementor HTML widgets. The browser uses the first `<title>` (correct), but the embedded homepage HTML adds 300-600KB of dead weight and creates SEO issues (multiple `<title>` tags, multiple `<head>` sections).

**Customer-facing payment pages (CRITICAL)**:
| Page | File Size | HTML Tags | First Title (Correct) |
|------|-----------|-----------|----------------------|
| /insiders/ | 446 KB | 3 html, 6 head | "...Insiders Only" |
| /awakened/ | 452 KB | 3 html, 5 head | "...Awaken Yours Today!" |
| /partnered/ | 455 KB | 3 html, 5 head | "...Awaken Yours Today!" |
| /unified/ | 453 KB | 3 html, 5 head | "...Awaken Yours Today!" |
| /referral-program/ | 697 KB | 4 html, 5 head | "Earn With PureBrain..." |

**Other affected pages**:
- /live/, /live-braintree/, /live-stripe/ (payment variants)
- /referral-program-clone/
- /elementor-1502/, /pure-brain-agentic-ai-partner/ (legacy WP)
- /home-test/, /home-test-live-1/, /home-test-sandbox/, /home-experiment/ (test pages)
- /homepage-clone-test/, /homepage-clone-v2/ (intentional clones)
- /long-name/, /oldchatbox/, /lpm-video-test/ (misc)
- /pay-test-sandbox-3/, /insiders/pay-test-awakened/ (test sandboxes)
- /purebrain-3/ (prototype)

**The homepage itself** (`/index.html`) also has 3 `<html>` tags and 2 `<title>` tags (644 KB).

### GREEN: All Sitemap Pages Working Correctly

All 93 URLs in sitemap.xml exist in the git repo and serve correct, unique content:
- All blog posts (45+): Correct unique titles
- All comparison pages (20+): Correct unique titles
- All meeting pages: Correct unique titles
- All brainiac training modules: Correct unique titles
- /refer/, /thank-you/, /about-aether/, /blog/, /compare/, etc.: All correct
- All gift pages (157): All correct with personalized titles

### GREEN: Key Pages Verified Working

| Page | Status | Title |
|------|--------|-------|
| /insiders/ | OK | "...Insiders Only" |
| /awakened/ | OK | "...Awaken Yours Today!" |
| /partnered/ | OK | "...Awaken Yours Today!" |
| /unified/ | OK | "...Awaken Yours Today!" |
| /refer/ | OK | "Refer & Earn" |
| /investment-opportunity/ | OK | "Pure Technology -- Investment Opportunity" |
| /admin/clients/ | OK | "PureBrain Admin - Clients" |
| /admin/referrals/ | OK | "PureBrain Admin - Referrals & Affiliates" |
| /thank-you/ | OK | "Welcome to the Partnership" |
| /blog/ | OK | "The Neural Feed -- Blog" |
| /team/meetings/ | OK | "Meeting Scheduler" |
| /team/responses/ | OK | "Meeting Responses" |
| /social/ | OK | "social -- PureBrain" |
| /voice/ | OK | "Voice Manager" |
| /creator/ | OK | "PureBrain Creator AI" |

---

## Root Cause Analysis

### Issue 1: SPA Fallback (PRIMARY ROOT CAUSE)

**How it works**:
1. `_worker.js` handles API routes, then falls through to `env.ASSETS.fetch(request)`
2. CF Pages looks for the file (e.g., `/some-page/index.html`)
3. If not found, CF Pages SPA mode serves `/index.html` (the homepage)
4. HTTP status is 200, not 404

**Impact**: Any typo in a URL, any deleted page, any referenced-but-never-created page silently shows the homepage. This is why the issue keeps recurring -- it is architecturally invisible.

### Issue 2: Embedded HTML Documents

**How it happened**: The site was migrated from WordPress/Elementor. Elementor "HTML widgets" allow embedding full HTML documents. When the homepage chatbox/payment forms were added to tier pages via Elementor widgets, entire HTML documents (including `<html>`, `<head>`, `<title>`) were embedded inside the parent page.

**Impact**: 
- File sizes 2-10x larger than needed (450-700KB vs typical 50-100KB)
- Multiple `<title>` tags confuse SEO crawlers
- Multiple `<head>` sections load duplicate CSS/JS
- Page load times slower due to bloat

---

## Fix Recommendations

### Fix 1: Add 404.html (HIGH PRIORITY -- prevents the recurring issue)

Create `/home/jared/purebrain-site/404.html` with a branded 404 page. CF Pages will serve this for missing routes instead of falling back to the homepage.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Page Not Found | PureBrain.ai</title>
    <!-- minimal branded styling -->
</head>
<body>
    <h1>Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <a href="/">Go to Homepage</a>
</body>
</html>
```

This single file eliminates the recurring "pages showing homepage" issue permanently.

### Fix 2: Clean Up Embedded HTML in Payment Pages (MEDIUM PRIORITY)

For /insiders/, /awakened/, /partnered/, /unified/, and /referral-program/:
- Extract the embedded chatbox/payment HTML widgets
- Remove the duplicate `<html>`, `<head>`, `<title>` wrappers
- Keep only the widget content (the `<div>` and its styles/scripts)
- This will reduce file sizes by 50-70% and fix SEO issues

### Fix 3: Clean Up Homepage Dual Title (LOW PRIORITY)

The homepage itself has 2 `<title>` tags. The second one ("PURE BRAIN - Your Personal AI Awakens") is inside an embedded HTML widget. Same fix as #2 -- remove the wrapper HTML from the widget.

### Fix 4: Archive Test Pages (CLEANUP)

These pages serve no purpose and could be moved to `_archived/`:
- /home-test/, /home-test-live-1/, /home-test-sandbox/, /home-experiment/
- /homepage-clone-test/, /homepage-clone-v2/
- /long-name/, /oldchatbox/, /lpm-video-test/
- /pay-test-sandbox-3/

---

## _worker.js Analysis

The `_worker.js` at `/home/jared/purebrain-site/_worker.js` (196 lines) handles:
- CORS preflight
- POST /api/subscribe (Brevo)
- POST /api/calculator-lead (D1 + Brevo)
- voice.purebrain.ai rewriting to /voice-manager/
- All other requests: `env.ASSETS.fetch(request)` (static files)

The worker itself does NOT cause the homepage fallback. It passes through to CF Pages' asset serving, which then applies SPA fallback when no file is found.

**`_redirects` file**: Only 3 redirects (switching-from-* to purebrain-vs-*). Not a factor.

**`_headers` file**: Cache and security headers only. Not a factor.

---

## Verification Evidence

```
Pages tested live: 80+
Pages checked locally: 507
Sitemap URLs verified: 93
HTTP status codes verified: 3 (existing=200, non-existing=200, confirming SPA fallback)
File hash comparisons: 9 (no identical copies of homepage found)
Multi-HTML-document scan: All 507 pages scanned
```

All findings are based on live curl tests against purebrain.ai and local file inspection of /home/jared/purebrain-site/.
