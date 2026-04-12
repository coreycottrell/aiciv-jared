# Session Consolidation Learnings - 2026-02-19

## Learning 1: Cloudflare CDN Cache Blocks All REST API Updates
**Type**: technical-blocker
**Severity**: HIGH - blocks multiple workflows

GoDaddy WordPress hosting uses Cloudflare CDN with `max-age=2678400` (31 days). When you update content via REST API (either `content.raw` or `_elementor_data`), the database IS correctly updated but the live page continues to serve the cached version.

**What doesn't work for cache clearing:**
- Cache-busting query params (`?nocache=1234`) - Cloudflare ignores
- `Cache-Control: no-cache` headers on requests - Cloudflare ignores
- REST API cache-flush endpoints (404 - not registered)
- GoDaddy-specific ajax actions (`wpaas_flush_cache`) - returns 400
- Playwright login to wp-admin for manual flush - rate-limited after multiple attempts

**What works:**
- Jared manually clicking "Flush Cache" in GoDaddy admin bar
- Previous session: Playwright login + Elementor cache clear + GoDaddy CDN flush (but requires successful login with CAPTCHA solving)

**Implication**: For any Elementor page content changes, plan for a cache flush step. Either batch changes and ask Jared once, or ensure Playwright login works first.

## Learning 2: WordPress Private Pages > Yoast Noindex for Dev Pages
**Type**: technical-pattern
**Discovered by**: browser-vision-tester (a353b73)

When hiding dev/test pages from Google, setting pages to `private` status via REST API is superior to Yoast noindex because:
1. Google gets HTTP 404 (definitive) vs meta tag (advisory, can be ignored)
2. No dependency on Yoast's React state management (which doesn't save via API)
3. Pages still accessible to logged-in WordPress admins
4. `_yoast_wpseo_meta-robots-noindex` meta key is private (underscore-prefixed) and not registered with REST API on GoDaddy - writes are silently ignored

**Pattern**: `requests.post(url, auth=auth, json={'status': 'private'})`

## Learning 3: CSS Cascade with Multiple Style Blocks
**Type**: debugging-pattern
**Discovered by**: full-stack-developer (a7eff31)

When a page has multiple inline `<style>` blocks:
- `border: none` in Block 1 CAN be overridden by `border-color: X !important` in Block 2
- The `!important` on `border-color` re-enables a visible border even after `border: none`
- Fix: Use `border: none !important` in the later block too

**Lesson**: When fixing CSS, always check ALL style blocks on the page, not just the first one.

## Learning 4: Dual Publish Rule (LOCKED IN)
**Type**: operational-rule

Every blog post published to purebrain.ai/blog MUST also be published to jareddsanborn.com/blog. This is now in MEMORY.md and the blog footer template.

## Learning 5: Blog Post Footer Template (MANDATORY)
**Type**: operational-rule

Every blog post MUST include:
1. Social share icons (`.pt-social-share`)
2. CTA block (`.blog-cta-block`) with "Start Your AI Partnership" button
3. Template at: `.claude/skills/wordpress-publishing/blog-footer-template.html`
4. Replace `{slug}` in UTM params with post slug

Post 480 was published without this and Jared flagged it immediately.

## Meta-Learning: Batch Cache-Dependent Changes
**Type**: coordination-pattern

When multiple tasks require content changes to WordPress pages served through Cloudflare CDN, batch them all together and ask Jared for ONE cache flush rather than requesting multiple flushes. This session had two separate cache-dependent changes (pay-test fix + Google indexing) that could have been communicated as a single request.
