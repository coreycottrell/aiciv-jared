# QA Audit: PureBrain Plugin v2.5.0
**Date**: 2026-02-20
**Type**: operational
**Agent**: qa-engineer

## What Was Tested
Plugin v2.5.0 deployed at purebrain.ai. CTA button fix release.

## Key Technical Findings

### Testing Gotcha: WordPress Blog Post 404 via Curl
- purebrain.ai blog post URLs return 404 without a browser User-Agent header
- Cloudflare or WordPress config blocks curl's default UA for individual posts
- Homepage, blog listing (/blog/), and category pages work without UA
- Fix: always use `-H "User-Agent: Mozilla/5.0 Chrome/121.0"` for curl on individual posts
- Affected: /escaping-the-pilot-program-trap/ (also a genuinely invalid slug)
- Working slugs confirmed: /why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/

### CTA Button Architecture (Important Pattern)
- The "Start Your AI Partnership" button has BOTH:
  1. Inline style on the anchor tag (background: linear-gradient #f1420b, from post content)
  2. Plugin CSS via `a[href*="awakening"]` selector
- Inline style controls default orange appearance (higher specificity)
- Plugin CSS controls hover state (blue gradient via :hover pseudo-class)
- This means plugin CSS is essential for hover but redundant for default orange
- v2.5.0 correctly removed the overbroad v2.4.0 `p a { background: none }` rule

### Newsletter Link Architecture
- Newsletter link also has both inline style (`color: #2a93c1 !important; text-decoration: underline`)
- Plugin CSS selector `a[href*="neural-feed"]` provides additional styling
- The link href contains "neural-feed" matching the CSS selector correctly

### Plugin Style Block IDs (on blog posts)
Only two plugin style blocks inject on blog posts:
- `id="purebrain-blog-cta-hover"` (CTA + newsletter CSS)
- `id="purebrain-legal-footer"` (privacy/TOS footer)
- FAQ, nav, blog-desktop-padding blocks also inject (confirmed on real single-post)

### Security Headers Confirmed Active
- Strict-Transport-Security, CSP-Report-Only, Permissions-Policy, Referrer-Policy, X-Content-Type-Options, X-Frame-Options all present

## Test Results Summary
- 13/14 checks PASS
- 1 ADVISORY (not a failure): CTA default orange relies on inline style, plugin CSS is backup

## Files Referenced
- Plugin: /home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php
- Test URL: https://purebrain.ai/why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/
- Category: https://purebrain.ai/category/for-individuals/
