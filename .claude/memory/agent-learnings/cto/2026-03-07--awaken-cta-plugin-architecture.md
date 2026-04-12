# CTO Learning: Awaken CTA Plugin Architecture

**Date**: 2026-03-07
**Type**: operational
**Topic**: pb-awaken-cta v1.0.0 — DOM injection plugin for Elementor pages

---

## What Was Built

A standalone WordPress plugin (`pb-awaken-cta`) that injects the
"Awaken Your Personal AI Partner Today" CTA button between the Compare
section and the "See Why PureBrain is Different" section on three pages.

**Target pages**: 11 (homepage), 689 (pay-test-2), 1232 (pay-test-sandbox-3)

---

## Architecture Decision: Why DOM Injection Over _elementor_data

Editing `_elementor_data` JSON directly is high-risk:
- JSON is deeply nested and page-specific; a malformed edit blanks the page
- Must also clear Elementor render cache after every edit
- Any Elementor widget save in the admin overwrites the injected data

DOM injection via `wp_footer` hook is safer:
- Zero risk to existing page content
- Plugin can be deactivated instantly if something goes wrong
- Works across all three target pages from a single plugin
- No Elementor cache invalidation required

---

## Injection Strategy (3-tier fallback)

1. **Primary**: Find "See Why PureBrain is Different" heading → walk up to
   `.elementor-section` ancestor → insert CTA before that section.

2. **Secondary**: Find the Compare section by text content ("Compare PureBrain",
   "vs ChatGPT", "vs Claude") → insert CTA immediately after the last matching section.

3. **Fallback**: Insert before `<footer>` or append to `<body>`.

The JS runs at `DOMContentLoaded` and also retries at 500ms + 1500ms to handle
Elementor's async rendering.

---

## Button Spec

- Default: `background: #2a93c1` (PureBrain blue), white text
- Hover: `background: #f1420b` (PureBrain orange), white text preserved
- Link: `href="#awakening"` (scrolls to chatbox section)
- Font: Plus Jakarta Sans (falls back to system fonts)
- Transition: 0.3s ease on background, box-shadow, transform

---

## Deployment Pattern

Used same REST API zip-upload approach as `deploy_button_styling_v100.py`:
1. Build in-memory zip from single PHP file
2. POST to `/wp/v2/plugins` with multipart form
3. PATCH activate via `X-HTTP-Method-Override: PATCH`
4. Verify via plugin list API + homepage source check

---

## Files

- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/pb-awaken-cta/pb-awaken-cta.php`
- Deploy: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_awaken_cta_v100.py`

---

## Security Plugin Isolation Rule Compliance

This feature was NOT added to the security plugin. It is its own standalone
plugin (`pb-awaken-cta`), consistent with the SECURITY PLUGIN ISOLATION RULE
(locked 2026-03-05): only security-related code goes in the security plugin.
