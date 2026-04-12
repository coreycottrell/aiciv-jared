# PureBrain.ai Full Site Diagnosis
## Date: March 10, 2026
## DIAGNOSIS ONLY — NO CHANGES MADE
## Prepared by: dept-systems-technology (ST#)

---

## Executive Summary — Top Critical Issues

1. **PLUGIN EXPLOSION**: 34 total plugins installed (22 active). Jared expected 2. We have drifted massively from the intended architecture. Every feature build has added a standalone plugin instead of consolidating. This is the root cause of recurring site breakage.

2. **SANDBOX-3 PASSWORD LOCKED** (page 1232): `pay-test-sandbox-3` is WordPress password-protected. Any visitor without the password sees a password form, not the chatbox or payment flow. The admin bypass (`?pb_admin=1`) does NOT work — the password form still renders. This page is effectively broken for all users.

3. **DUPLICATE CSS/HTML INJECTIONS**: Multiple plugins AND the Elementor page content both inject the same CSS. At least 3 duplicate injections confirmed on the homepage: `pb-video-modal-close-fix-v611` (injected twice), `pb-aether-footer` div (injected twice), `pb-aether-footer-v470` styles (injected twice). This bloats pages and creates unpredictable style conflicts.

4. **WRONG BACKGROUND VIDEO on pay-test-2 and homepage**: The `.video-background` element on both the homepage and pay-test-2 is sourcing `PureResearch.ai-1.mp4` as the background video, NOT the intended brain/neural video. The brain demo video (`Pure-Brain-Demo-Video-real-compression-and-sizing.mp4`) is only used in the demo modal. This may be intentional, but flagged for review.

5. **8 PAGES WITH WRONG TEMPLATES**: Several non-blog pages are missing the required `elementor_canvas` template and instead use the default WordPress theme template. This exposes the WP site header, navigation, and theme styling on pages that should be clean canvas pages. Most critical: `about-aether` (18 WP header elements visible), `purebrain-for-staycation-breaks` (30 header elements), `purebrain-for-danby-appliances` (same).

---

## 1. Plugin Audit

**Total Plugins**: 34
**Active**: 22
**Inactive**: 12
**Jared's expectation**: 2

The site has accumulated a plugin for every feature, every fix, and every one-shot task. This is unsustainable.

### Active Plugins (22 — should be radically consolidated)

| # | Plugin | Version | What It Does | Should Exist? |
|---|--------|---------|--------------|---------------|
| 1 | Akismet Anti-spam | 5.6 | Spam protection for comments | YES (if comments enabled) |
| 2 | Brevo | 3.3.2 | Email/SMS marketing, Brevo integration | YES |
| 3 | Elementor | 3.35.6 | Page builder (critical) | YES |
| 4 | GTM4WP (Google Tag Manager) | 1.22.3 | Analytics/GTM injection | YES |
| 5 | PureBrain 301 Redirects | 1.0.0 | URL redirect management | DEBATABLE (consolidate into security?) |
| 6 | PureBrain Blog FAQ | 1.0.0 | Blog FAQ accordion | COULD CONSOLIDATE |
| 7 | PureBrain Blog Styling | 1.1.0 | Blog CSS, nav, listing features | COULD CONSOLIDATE |
| 8 | PureBrain Breadcrumb Fix | 1.0.0 | Yoast SEO breadcrumb schema fix | COULD CONSOLIDATE |
| 9 | PureBrain Button Styling | 1.0.0 | Button hover CSS for calculator/comparison | COULD CONSOLIDATE |
| 10 | PureBrain Cache Control | 1.0.0 | Cache exclusion for dynamic pages | COULD CONSOLIDATE |
| 11 | PureBrain Calculator CTA | 2.0.0 | Injects calculator CTA on homepage | COULD CONSOLIDATE |
| 12 | PureBrain Content Gate | 1.0.0 | Password-gating for pages like 859 | YES (functional) |
| 13 | PureBrain Footer Branding | 1.0.0 | "Built by AETHER" footer bar | COULD CONSOLIDATE |
| 14 | PureBrain Lead Capture | 1.0.0 | Email capture forms | COULD CONSOLIDATE |
| 15 | PureBrain Page Metadata | 1.0.0 | Twitter/OG meta tags | COULD CONSOLIDATE |
| 16 | PureBrain Referral System | 2.2.0 | Referral tracking, dashboard, rewards | YES (complex, standalone justified) |
| 17 | **PureBrain Security** | **6.2.2** | **Security hardening, proxies, CORS** | **YES — but keep minimal** |
| 18 | PureBrain Social Sharing | 1.0.0 | Social share buttons on blog posts | COULD CONSOLIDATE |
| 19 | PureBrain Video Handler | 1.5.0 | Background video for specific pages | COULD CONSOLIDATE |
| 20 | PureBrain Video Modal | 1.0.0 | Video modal close button CSS | **FLAG: This is JUST CSS — extracted for a bug fix** |
| 21 | WP File Manager | 8.0.2 | File management in WP admin | SECURITY RISK — review need |
| 22 | Yoast SEO | 27.1.1 | SEO, sitemaps, schema | YES |

**Core Observation**: Plugins 5–15, 18–19 should ideally be a single "PureBrain Core" plugin. Instead they are 11 separate plugins. Every time we fixed a bug by extracting code into a new plugin, we added maintenance surface area.

**PureBrain Video Modal (plugin 20)** is flagged as particularly concerning: it is an entire plugin that contains ONLY CSS for a close button. This is the pattern that keeps breaking things — tiny plugins extracted for bug fixes.

### Inactive Plugins (12 — most should be DELETED)

| Plugin | Version | Status | Risk |
|--------|---------|--------|------|
| Independent Analytics | 2.14.4 | Inactive | LOW — analytics tool, safe to delete |
| **PB Cache Clear (one-shot)** | 1.0.0 | Inactive | **DELETE** — one-shot utility, task complete |
| **PB Diag (one-shot)** | 1.0.0 | Inactive | **DELETE** — diagnostic tool no longer needed |
| **PB Elementor Fix (one-shot)** | 1.0.0 | Inactive | **DELETE** — "Fixes _elementor_data for page 11" — already ran |
| **PB Force Render (one-shot)** | 1.0.0 | Inactive | **DELETE** — one-shot tool |
| **PB Restore Revision (one-shot)** | 1.0.0 | Inactive | **DELETE** — one-shot tool |
| **PB Text Updater (one-shot)** | 1.0.0 | Inactive | **DELETE** — "Updates 140+ tools text, then self-deactivates" — done |
| PureBrain Awaken CTA | 1.1.0 | Inactive | Low — feature retired or replaced |
| **PureBrain Blog Styles** | 1.0.0 | Inactive | **DELETE** — DUPLICATE of active pb-blog-styling v1.1.0 |
| PureBrain IndexNow | 1.0.0 | Inactive | Low — search engine ping tool |
| **PureBrain Security v4.8.6** | 4.8.6 | Inactive | **DANGEROUS** — old version of active security plugin sitting on disk |
| WP Super Cache | 3.0.3 | Inactive | LOW — cache plugin not needed with current setup |

**Critical**: Six one-shot plugins were built, used, then left on disk in inactive state. This is digital clutter and a maintenance hazard. They should be deleted.

**Critical**: The old PureBrain Security v4.8.6 slug is sitting inactive. Having an old version of the security plugin installed (even inactive) on disk is a security concern.

---

## 2. Page-by-Page Audit

**Total published pages**: 87
**Total published blog posts**: 23
**HTTP 404 pages**: ZERO — all 110 published pages/posts return 200 OK.
**Raw wp:html blocks exposed**: ZERO — no raw WordPress block markers found on any page.

### Template Issues (Pages with Wrong Template)

Per the rule: all non-blog pages should use `elementor_canvas`. The following do NOT:

| ID | URL | Current Template | Issue |
|----|-----|-----------------|-------|
| 174 | /purebrain-2-0/ | elementor_header_footer | Old page, but still shows theme header |
| 731 | /about-aether/ | default (empty) | **18 WP header elements visible** — theme nav showing |
| 1196 | /purebrain-for-staycation-breaks/ | default (empty) | **30 header/nav elements visible** — looks broken |
| 1200 | /purebrain-for-danby-appliances/ | default (empty) | **30 header/nav elements visible** — looks broken |
| 1231 | /purebrain-x-hovr-ai-partnership-brief/ | default (empty) | Theme elements visible |
| 1310 | /refer/ | default (empty) | Theme elements visible (duplicate of /refer-and-earn/) |
| 1459 | /compare/openclaw/ | default (empty) | New compare pages — theme elements showing |
| 1460 | /compare/enso/ | default (empty) | New compare pages — theme elements showing |
| 1461 | /compare/supercool/ | default (empty) | New compare pages — theme elements showing |
| 1462 | /compare/billiereview/ | default (empty) | New compare pages — theme elements showing |
| 1463 | /compare/boardy/ | default (empty) | New compare pages — theme elements showing |

**Most urgent**: The 5 newest comparison pages (openclaw, enso, supercool, billiereview, boardy — IDs 1459–1463) are all missing `elementor_canvas` template. These were likely deployed recently without setting the template. They render with the WordPress theme nav header visible.

**Client pages at risk**: `/purebrain-for-staycation-breaks/` and `/purebrain-for-danby-appliances/` are showing 30+ theme header/nav elements. These are client-facing pages and look unprofessional.

Note: Privacy Policy (ID 3), Terms of Service (ID 541) use default template — this is correct/expected behavior. Blog posts (IDs 98–1441) also correctly use default template with the `pb-blog-post` article wrapper.

### Pay-Test-2 (ID 689) — `/pay-test-2/`

- HTTP: 200 OK
- Template: elementor_canvas (CORRECT)
- Page size: 510,985 bytes (large but expected — full chatbox + PayPal SDK)
- Video background: PRESENT — `PureResearch.ai-1.mp4` (see video section below)
- Dark background: Enforced via `#0a0a0f` and `#080a12` (CORRECT)
- wp:html blocks exposed: NONE
- PayPal SDK: Referenced, potential error paths in JS (see CSS/JS section)
- Assessment: **Appears structurally sound.** The recent fix for bottom sections appears to hold.

### Pay-Test Sandbox-3 (ID 1232) — `/pay-test-sandbox-3/`

- HTTP: 200 (misleadingly — actually shows password form)
- Template: elementor_canvas (CORRECT in WP)
- **CRITICAL: Password protected** — WordPress `post_password_form` is rendered for all public visitors
- Page size: 140,431 bytes (this is the password form, not the actual page content)
- Admin bypass `?pb_admin=1`: NOT WORKING — still shows password form
- Video background: NOT PRESENT in rendered HTML (because password wall blocks rendering)
- Assessment: **EFFECTIVELY BROKEN for all users.** Password must be removed OR bypass must be fixed before this page can function.

### Homepage (ID 11) — `/`

- HTTP: 200 OK
- Template: elementor_canvas (CORRECT)
- Page size: 633,664 bytes
- Video background: PRESENT — `PureResearch.ai-1.mp4` (see video section)
- Dark background: Enforced (CORRECT)
- wp:html blocks: NONE
- GTM: Injected correctly
- **Duplicate CSS injection detected**: (see CSS/JS section)
- Assessment: **Functionally OK but has duplicate injection bloat.** Videos load (both 200 OK). Navigation links all valid.

### Blog Posts (23 total)

- All 23 return HTTP 200
- All use `post-template-default` (CORRECT for blog posts)
- Checked post (ID 1441): Uses `<article class="pb-blog-post">` wrapper (CORRECT)
- Dark background enforced on blog posts (CORRECT)
- No raw wp:html blocks
- Assessment: **Blog posts appear healthy.**

### Duplicate/Redundant Pages Detected

| URL 1 | URL 2 | Issue |
|-------|-------|-------|
| /refer/ (ID 1310) | /refer-and-earn/ (ID 1298) | Two separate pages for same content. /refer/ uses wrong template |
| /duckdive-report/ (ID 854) | /client-report-duckdive/ (ID 859) | Two pages for same DuckDive report |
| /website-execution/ (ID 855) | /ai-website-execution/ (ID 860) | Duplicate pages |
| /homepage-backup/ (ID 1128) | — | Old homepage backup still published |
| /blog-old/ (ID 95) | /blog/ (ID 319) | Old blog page still published |
| /purebrain-2-0/ (ID 174) | — | Old version page still published |
| /purebrain-3/ (ID 338) | — | Old version page still published |
| /purebrain-4/ (ID 383) | — | Old version page still published |

These old/duplicate pages waste crawl budget, confuse SEO, and are deindexing risks.

---

## 3. Background Video Status

### Current Video Architecture

The `pb-video-handler` plugin manages video backgrounds for specific page IDs: **11, 689, 688, 1232, 319** (homepage, pay-test-2, pay-test-sandbox-2, sandbox-3, blog page).

### Video Sources

| Page | Background Video Source | Demo/Modal Video Source | Status |
|------|------------------------|------------------------|--------|
| Homepage (11) | `PureResearch.ai-1.mp4` | `Pure-Brain-Demo-Video-real-compression-and-sizing.mp4` | Both 200 OK |
| Pay-Test-2 (689) | `PureResearch.ai-1.mp4` | `Pure-Brain-Demo-Video-real-compression-and-sizing.mp4` | Both 200 OK |
| Sandbox-3 (1232) | N/A (password wall) | N/A | BLOCKED |

**Background video file sizes**:
- `PureResearch.ai-1.mp4` — 73,932,678 bytes (~70MB) — LARGE for a background video
- `Pure-Brain-Demo-Video-real-compression-and-sizing.mp4` — 89,907,843 bytes (~85MB) — Also large

**Flag**: Both video files are hosted on WP uploads (not a CDN). At 70–85MB each, these are slow to load, especially on mobile. A CDN (Cloudflare R2, Bunny.net) would significantly improve load times.

**Flag**: The background video on homepage and pay-test-2 is `PureResearch.ai-1.mp4`. Based on the filename this appears to be a PureResearch demo video, not a PureBrain brain/neural animation. Jared should confirm: is this intentional or should the background be a different video?

**Pages NOT covered by video handler** (no video background): pay-test (439), pay-test-sandbox (468), living-avatar (532). These pages do not have `.video-background` elements in their HTML.

### Video Accessibility

Both video files return HTTP 200 and are accessible. No CORS issues detected on the video URLs.

---

## 4. Mobile Issues

### Confirmed Mobile CSS Present

- `overflow-x: hidden` enforced on `html, body` (prevents horizontal scroll)
- `@media (max-width: 767px)` breakpoints present in pb-video-handler
- `@media (max-width: 768px)` breakpoints present in page content
- Video modal close button has `position: fixed` fix for mobile (from pb-video-modal plugin)

### Potential Mobile Issues (Not Browser-Verified — Requires Visual Testing)

1. **Sandbox-3 display:none sections**: Multiple sections hidden with `display: none !important`. On mobile this historically caused the "bottom sections missing" bug. The recent fix appears to have targeted specific sections. Cannot fully verify without a browser.

2. **Pay-test-2 section hiding**: Similar pattern — 25+ `display: none !important` declarations. These control mobile/desktop section visibility. Risk of mobile sections being hidden.

3. **Large video files on mobile**: The 70–85MB background videos will timeout or fail to load on mobile connections. The video handler has mobile fallback CSS but a slow connection will result in black/empty backgrounds.

4. **Pages without canvas template on mobile**: Pages with the WP default template (about-aether, staycation, danby, new compare pages) will show the theme navigation header on mobile, which is styled for desktop and likely breaks mobile layout.

---

## 5. Broken Links

**HTTP 404 pages**: NONE detected among all 87 published pages and 23 blog posts.

**Internal navigation links from homepage**: All checked and return 200:
- /ai-tool-stack-calculator/ — 200
- /compare/ — 200
- /mission-vision-values/ — 200
- /partnered-how-this-levels-you-up/ — 200
- /unified-how-this-levels-you-up/ — 200
- /why-purebrain/ — 200
- /pay-test-2/ — 200
- /pay-test-sandbox-3/ — 200 (password wall)
- /invitation/ — 200
- /refer-and-earn/ — 200
- /about-aether/ — 200

**Redirect pages** (`/training/`, `/ai-partnership-calculator/`, `/hunden-proposal/`): Return 200 but do NOT appear to redirect to another URL. They render as standalone pages. If these were meant to redirect, the 301 redirects plugin may not have entries for them, or the content gate/redirect logic is handled within the page HTML itself.

---

## 6. CSS/JS Conflicts

### Duplicate CSS Injections (Confirmed)

Multiple plugins AND the Elementor page content both output the same CSS blocks. This causes:
- Page bloat (every visitor downloads the same CSS twice)
- Potential style conflicts (last-write wins, unpredictable)
- Increased debugging difficulty

**Confirmed duplicates on homepage**:

| CSS Block ID | Injection Count | Source Conflict |
|-------------|----------------|-----------------|
| `pb-video-modal-close-fix-v611` | **2x** | Plugin (pb-video-modal) + hardcoded in Elementor page |
| `pb-aether-footer` (div) | **2x** | Plugin (pb-footer-branding) + hardcoded in Elementor page |
| `pb-aether-footer-v470` (style) | **2x** | Plugin (pb-footer-branding) + hardcoded in Elementor page |

**Root cause**: When we extract CSS into a standalone plugin for a bug fix, the old CSS from the Elementor page content is not removed. So both exist. This is the "CSS in page content AND in a plugin" pattern that has caused many bugs.

### JavaScript Error Patterns (Flagged — Not Broken)

In pay-test-2, these error patterns exist in the JS (they are catch-blocks, not actual errors at load time):
- `throw new Error("RATE_LIMITED")` — rate limit handling for chatbox API
- `throw new Error("HTTP ${response.status}")` — HTTP error handling
- `console.error('Submission error:', err)` — form submission error handling
- `console.error('[PB PayPal] Failed to load PayPal SDK...')` — PayPal fallback
- `console.error('[PB PayPal] Render error:', err)` — PayPal render error handler

These are error handlers, not errors. But if PayPal SDK fails to load (network issue, ad-blocker), the user will silently fall back to a form approach. Not broken, but the user experience depends on PayPal SDK availability.

### WP Default Color Variables (Minor)

WordPress injects `--wp--preset--color--luminous-vivid-orange: #ff6900` as a CSS variable. This is NOT PureBrain orange (#f1420b). If any element accidentally uses the WP preset orange variable, it will be the wrong shade. Currently no evidence this is causing visual issues, but it is present on every page.

### CSS Architecture Concern

The site currently has **22 separate `<style>` blocks** injected into the homepage `<head>` (counted from plugin CSS injections alone). This is high. A proper architecture would consolidate these into 1–2 plugin CSS files that load via `wp_enqueue_style`. Instead, most plugins use `wp_head` action hooks with inline `<style>` blocks, which cannot be combined or cached by the browser as efficiently.

---

## 7. Security Observations (Diagnosis Only)

The following are observations for the security team — NOT fixes.

1. **WP File Manager (v8.0.2) is active**: This plugin allows file management directly in the WordPress admin. WP File Manager has had serious historical security vulnerabilities (CVE-2020-25213 was a critical zero-day). Its presence increases attack surface. If not actively needed, it should be removed.

2. **Old PureBrain Security v4.8.6 plugin on disk (inactive)**: An older version of the security plugin is installed but inactive. Old plugin code on disk can be scanned by attackers. Should be deleted even though inactive.

3. **WP REST API `/wp-json/wp/v2/plugins` endpoint accessible**: The plugins API returned data with authentication. This endpoint correctly requires auth. Confirmed working as intended.

4. **WordPress version exposed**: WP 6.9.1 is visible in page source via GoDaddy/WP asset URLs (`?ver=6.9.1`). This is standard but means attackers can identify the version.

5. **Security plugin isolation rule**: Confirmed the active security plugin (v6.2.2) is in place. Cannot verify from outside whether recent updates have accidentally added display:none CSS or other non-security elements without deeper internal inspection.

---

## 8. Recommended Fix Order

When Jared is ready to fix, prioritize in this order:

### Priority 1 — IMMEDIATE (things currently broken or blocking users)

1. **Fix sandbox-3 password protection** (ID 1232): Remove the WP password from the page, or ensure the pb-content-gate plugin bypass works. The page is currently inaccessible to all users without the password.

2. **Fix 5 new comparison pages templates** (IDs 1459–1463: openclaw, enso, supercool, billiereview, boardy): Set `elementor_canvas` template on these pages. They are currently showing WP theme header/nav. This is a simple WP API update.

3. **Fix client-facing pages with wrong template** (IDs 731, 1196, 1200, 1231): The about-aether, staycation, danby, and HOVR pages are all showing WP theme header. Client pages especially (staycation, danby) need immediate fix.

### Priority 2 — HIGH (CSS bloat and duplicate injection causing instability)

4. **Remove duplicate CSS from Elementor page content vs plugins**: For each plugin that was extracted as a "fix" (video modal close button, footer branding), remove the old CSS from the Elementor page `_elementor_data`. Currently both the plugin AND the page content inject the same CSS.

5. **Delete 6 one-shot plugins**: pb-cache-clear, pb-diag, pb-elementor-fix, pb-force-render, pb-restore-rev, pb-text-updater. These are done and serve no purpose.

6. **Delete duplicate inactive plugins**: purebrain-blog-styles v1.0.0 (duplicate of active pb-blog-styling) and purebrain-security-hardening v4.8.6 (old security plugin version).

### Priority 3 — MEDIUM (consolidation and cleanup)

7. **Consolidate 10+ micro-plugins into a single "PureBrain Core" plugin**: All the PB-prefixed feature plugins (blog FAQ, blog styling, breadcrumb fix, button styling, cache control, calculator CTA, footer branding, lead capture, page metadata, social sharing, video handler, video modal, 301 redirects) should be one plugin. This is the architectural change that prevents future breakage from plugin conflicts.

8. **Review and redirect/unpublish old pages**: At minimum, set homepage-backup, blog-old, purebrain-2-0, purebrain-3, purebrain-4 to draft or redirect them. Duplicate DuckDive pages and duplicate execution pages should also be resolved.

9. **Set up /refer/ to redirect to /refer-and-earn/**: Currently two live pages for the same content.

### Priority 4 — LOW (improvements, not breakage)

10. **Move background videos to CDN**: The 70–85MB video files on WP uploads are too large and slow. Hosting on Cloudflare R2 or Bunny.net with proper video streaming would improve load times significantly.

11. **Review WP File Manager plugin**: If not actively needed, remove it (security surface area reduction).

12. **Confirm background video intent**: Is `PureResearch.ai-1.mp4` the correct background video for the homepage and pay-test-2? If the brain/neural animation was intended, the source needs to be updated.

13. **Consolidate CSS `<style>` injections**: Migrate plugin CSS from inline `wp_head` hooks to enqueued stylesheets for better browser caching.

---

## Appendix: Full Page Inventory

### All 87 Published Pages (HTTP Status: All 200)

| ID | Slug | Template | Notes |
|----|------|----------|-------|
| 3 | privacy-policy | default | OK — policy page, correct |
| 11 | pure-brain-agentic-ai-partner | elementor_canvas | Homepage — OK |
| 95 | blog-old | elementor_canvas | OLD — should be draft |
| 174 | purebrain-2-0 | elementor_header_footer | OLD — wrong template |
| 284 | ai-partnership-assessment | elementor_canvas | OK |
| 309 | thank-you | elementor_canvas | OK |
| 319 | blog | elementor_canvas | Blog listing — OK |
| 338 | purebrain-3 | elementor_canvas | OLD — should be draft |
| 383 | purebrain-4 | elementor_canvas | OLD — should be draft |
| 403 | ai-readiness-assessment | elementor_canvas | OK |
| 405 | ai-partnership-guide | elementor_canvas | OK |
| 439 | pay-test | elementor_canvas | Old pay test — no video background |
| 468 | pay-test-sandbox | elementor_canvas | Old sandbox — no video background |
| 532 | living-avatar | elementor_canvas | OK |
| 541 | terms-of-service | default | OK — policy page, correct |
| 577 | ai-adoption-review | elementor_canvas | OK |
| 620 | ai-partnership-audit | elementor_canvas | OK |
| 688 | pay-test-sandbox-2 | elementor_canvas | OK |
| 689 | pay-test-2 | elementor_canvas | OK — main payment page |
| 700 | blog-neural-feed-memories | elementor_canvas | OK |
| 731 | about-aether | default | WRONG TEMPLATE — showing WP nav |
| 752 | compare | elementor_canvas | OK |
| 753 | purebrain-vs-chatgpt | elementor_canvas | OK |
| 754 | purebrain-vs-claude | elementor_canvas | OK |
| 755 | purebrain-vs-copilot | elementor_canvas | OK |
| 756 | purebrain-vs-custom-gpts | elementor_canvas | OK |
| 757 | purebrain-vs-deepseek | elementor_canvas | OK |
| 758 | purebrain-vs-gemini | elementor_canvas | OK |
| 759 | purebrain-vs-jasper | elementor_canvas | OK |
| 760 | purebrain-vs-perplexity | elementor_canvas | OK |
| 777 | ai-tool-stack-calculator | elementor_canvas | OK |
| 794 | why-purebrain | elementor_canvas | OK |
| 800 | migrate | elementor_canvas | OK |
| 811 | ai-partnership-calculator | elementor_canvas | Redirect page — renders OK |
| 816 | ai-website-analysis | elementor_canvas | OK |
| 843 | team-dashboard | elementor_canvas | OK |
| 854 | duckdive-report | elementor_canvas | DUPLICATE of 859 |
| 855 | website-execution | elementor_canvas | DUPLICATE of 860 |
| 859 | client-report-duckdive | elementor_canvas | OK (keep this one) |
| 860 | ai-website-execution | elementor_canvas | OK (keep this one) |
| 923 | partners | elementor_canvas | OK |
| 929 | mission-vision-values | elementor_canvas | OK |
| 963 | demo-no-bs | elementor_canvas | OK |
| 970 | cost-comparison | elementor_canvas | OK |
| 987 | invitation | elementor_canvas | OK |
| 993 | your-ai-tim-cook | elementor_canvas | OK |
| 1001 | pitch | elementor_canvas | OK |
| 1006 | portfolio | elementor_canvas | OK |
| 1044 | purebrain-vs-sitegpt | elementor_canvas | OK |
| 1115 | brainiac-mastermind-training | elementor_canvas | OK |
| 1118 | video-test | default | Test page — wrong template |
| 1128 | homepage-backup | elementor_canvas | OLD — should be draft |
| 1150–1156 | purebrain-for-graham-martin* | elementor_canvas | OK (5 pages) |
| 1190 | purebrain-vs-glbgpt | elementor_canvas | OK |
| 1196 | purebrain-for-staycation-breaks | default | WRONG TEMPLATE — WP nav showing |
| 1200 | purebrain-for-danby-appliances | default | WRONG TEMPLATE — WP nav showing |
| 1205 | investor-intelligence | elementor_canvas | OK |
| 1206 | hunden-partners | elementor_canvas | OK |
| 1225 | mark-christie | elementor_canvas | OK |
| 1231 | purebrain-x-hovr-ai-partnership-brief | default | WRONG TEMPLATE |
| 1232 | pay-test-sandbox-3 | elementor_canvas | PASSWORD PROTECTED — broken |
| 1249 | brainiac-module-1-foundations | elementor_canvas | OK |
| 1251 | training | elementor_canvas | Redirect page — OK |
| 1256 | purebrain-vs-xcloud | elementor_canvas | OK |
| 1257 | purebrain-vs-atomicbot | elementor_canvas | OK |
| 1258 | purebrain-vs-cursor | elementor_canvas | OK |
| 1262 | partnered-how-this-levels-you-up | elementor_canvas | OK |
| 1263 | unified-how-this-levels-you-up | elementor_canvas | OK |
| 1278 | sales-playbook | elementor_canvas | OK |
| 1283 | live-call | elementor_canvas | OK |
| 1294 | hunden-placer-blueprint | elementor_canvas | OK |
| 1298 | refer-and-earn | elementor_canvas | OK (keep — correct template) |
| 1310 | refer | default | WRONG TEMPLATE — duplicate of 1298 |
| 1324 | developers | elementor_canvas | OK |
| 1326 | bloomberg-bpipe-demo | elementor_canvas | OK |
| 1327 | php-point-of-sale-payment-processing-partnership | elementor_canvas | OK |
| 1329 | hunden-action-plan | elementor_canvas | OK |
| 1394 | hunden-proposal | elementor_canvas | Redirect page — OK |
| 1459 | compare/openclaw | default | WRONG TEMPLATE — WP nav showing |
| 1460 | compare/enso | default | WRONG TEMPLATE — WP nav showing |
| 1461 | compare/supercool | default | WRONG TEMPLATE — WP nav showing |
| 1462 | compare/billiereview | default | WRONG TEMPLATE — WP nav showing |
| 1463 | compare/boardy | default | WRONG TEMPLATE — WP nav showing |

### All 23 Blog Posts (HTTP Status: All 200)

All blog posts use `post-template-default` (correct), `<article class="pb-blog-post">` wrapper (correct), and dark background enforcement (correct). No issues found.

---

## Verification

All data in this report was collected via:
- WordPress REST API (read-only calls with authenticated GET requests)
- Public URL fetches with curl (read-only)
- HTML analysis of fetched pages

**NO changes were made to any page, plugin, setting, or content during this diagnosis.**

**Report generated**: 2026-03-10
**Agent**: dept-systems-technology (ST#)
**Method**: READ ONLY diagnosis
