# CTO Task Assignment: Blog Transparency + FAQ Fix

**Date**: 2026-03-09
**Agent**: cto
**Type**: operational
**Topic**: Three-task assignment for blog transparency duplication + FAQ schema + accordion QA

---

## Context

Audit report found three issues on purebrain.ai blog posts:
1. Double transparency section + duplicate scripts on ALL single posts (site-wide bug)
2. 6 posts missing FAQPage JSON-LD schema
3. 8 older posts may have FAQ accordion rendering issues

## Root Cause Discovery (CTO Analysis)

### Double Injection
Two versions of security plugin coexist on server:
- v6.2.2 ACTIVE
- v4.8.6 INACTIVE but still on filesystem

WordPress may be loading both files. Fix: PHP constant dedup guard.
The local plugin source is at `tools/security/purebrain-security/purebrain-security-plugin.php` (v6.2.7 locally).

### Schema Auto-Injection Gap
Plugin v5.8.0 has PHP auto-schema at `wp_footer priority 14`.
It checks `strpos($raw_content, '"FAQPage"')` for backward compat.
For 6 specific posts (1245, 1189, 1139, 1084, 966, 950), the PHP parser is NOT finding FAQ pairs.
Confirmed via WebFetch on live pages: no FAQPage schema in rendered HTML.
Likely cause: these posts use different HTML structure than parser expects.

### Accordion JS
Plugin has TWO accordion handlers:
- Primary JS (j, priority 15): handles `.faq-section` class directly
- Extended JS (j2, priority 16): handles `pb-faq-item` + bare h3+p after h2[FAQ] by WRAPPING

Most older posts likely use bare h3+p structure — the extended JS handles this at runtime.
Real browser testing would confirm, but static analysis predicts most will PASS.

## Task Assignments

| Task | Assignee | Script |
|------|----------|--------|
| T1: Plugin dedup guard | security-engineer-tech | `tools/security/deploy_plugin_v628_dedup_guard.py` |
| T2: JSON-LD schema injection | full-stack-developer | `tools/security/inject_faq_schema.py` |
| T3: Accordion QA | qa-engineer | `tools/security/qa_verify_faq_accordion.py` |

## Key Learnings (CTO)

1. **Deploy scripts are better than direct file edits for large plugin files**
   The plugin is 6000+ lines. Direct edits risk corruption. Deploy script modifies
   in-memory copy and sends via WP admin editor. Zero risk to local source.

2. **Check rendered HTML, not post_content, for plugin-generated content**
   The audit checked `post_content` for schema — but the plugin generates schema
   at `wp_footer` time (PHP render). The "missing schema" in audit meant schema
   was not in `post_content` — but may not have been in rendered HTML either.
   WebFetch confirmed the rendered HTML also lacks schema for these posts.

3. **Dedup guard is the safest fix for double-load**
   No server file deletion needed. PHP constant is zero-overhead.
   Works regardless of whether issue is dual-file-load or internal duplication.

4. **The security plugin isolation rule must be strictly enforced**
   Only security engineer touches it, even for bug fixes unrelated to security.
   This is Jared's permanent lock. CTO respects it.

5. **WP REST API auth**
   - purebrain.ai: `PUREBRAIN_WP_USER` (purebrain@puremarketing.ai) + `PUREBRAIN_WP_APP_PASSWORD`
   - jareddsanborn.com: `WORDPRESS_USER` (jared) + `WORDPRESS_APP_PASSWORD`
   - The `context=edit` parameter is required to get `content.raw` (unfiltered HTML)

## Files

- Task brief: `exports/departments/systems-technology/reports/2026-03-09--cto-task-assignments.md`
- Execution status: `exports/departments/systems-technology/reports/2026-03-09--cto-task-execution-status.md`
- Audit source: `exports/departments/systems-technology/reports/2026-03-09--blog-transparency-faq-audit.md`
