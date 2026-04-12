# Site Diagnosis: PureBrain.ai Full Audit — March 10, 2026

**Type**: diagnostic
**Scope**: Full site — all plugins, pages, videos, CSS/JS, mobile
**Method**: Read-only (WP REST API + public URL curl)

---

## Key Findings

### Plugin Situation (CRITICAL)
- 34 total plugins (22 active, 12 inactive)
- Jared expected 2 — we have drifted massively
- The root cause of breakage is plugin proliferation: every bug fix creates a new standalone plugin instead of consolidating
- 6 one-shot plugins left inactive on disk — should be deleted
- Duplicate security plugin (old v4.8.6) on disk — delete
- Duplicate blog styles plugin (inactive) — delete
- WP File Manager active — security risk

### Broken Pages
- **pay-test-sandbox-3 (ID 1232)** — PASSWORD PROTECTED. WordPress post password form blocks all visitors. `?pb_admin=1` bypass does NOT work. Page is effectively broken for all users.
- **11 pages with wrong template** — missing `elementor_canvas`, showing WP theme nav header
  - Most critical: about-aether (731), staycation (1196), danby (1200), and 5 new compare pages (1459–1463)
  - The 5 new compare pages (openclaw, enso, supercool, billiereview, boardy) were deployed without setting template

### CSS/JS Issues
- **Duplicate CSS injection** on homepage (at minimum): pb-video-modal-close-fix-v611, pb-aether-footer div, pb-aether-footer-v470 styles — all injected TWICE
- Root cause: plugin extracts CSS for a fix, but old CSS still in Elementor page content — both render
- 22 separate `<style>` inline blocks on homepage — should be enqueued files
- Pay-test-2 has 38 `<script>` tags — heavy

### Video Status
- Both main video files accessible (200 OK, hosted on WP uploads)
- `PureResearch.ai-1.mp4` (70MB) — used as background video on homepage AND pay-test-2
- `Pure-Brain-Demo-Video...mp4` (85MB) — used only in demo modal
- Video files are large — should move to CDN
- Sandbox-3 has no video because password wall blocks rendering

### Good News
- ZERO 404 pages across all 87 pages and 23 blog posts
- ZERO raw wp:html blocks exposed on any page
- All navigation links from homepage return 200
- Blog posts correctly use pb-blog-post wrapper and default template
- Dark background enforcement working site-wide
- GTM injection working correctly

---

## Prioritized Fix List

1. Remove password from sandbox-3 (ID 1232) or fix bypass
2. Set elementor_canvas on 5 new compare pages (IDs 1459–1463)
3. Set elementor_canvas on about-aether (731), staycation (1196), danby (1200), hovr (1231)
4. Remove duplicate CSS from Elementor page content (video modal, footer branding)
5. Delete 6 one-shot inactive plugins + 2 duplicate inactive plugins
6. Consolidate 10+ micro-plugins into single PureBrain Core plugin (architectural)
7. Draft old pages: blog-old, homepage-backup, purebrain-2-0, purebrain-3, purebrain-4
8. Redirect /refer/ to /refer-and-earn/
9. Move video files to CDN

---

## Patterns to Remember

- **Template omission pattern**: New pages deployed via API often miss the `template` field. Must always set `"template": "elementor_canvas"` on non-blog pages.
- **Plugin extract pattern causes duplicates**: When extracting CSS from page content to a plugin, the old CSS MUST be removed from `_elementor_data` or it renders twice.
- **One-shot plugins**: Never leave these on disk after use. Delete immediately after the task completes.
- **Password protection gotcha**: WP post passwords and pb-content-gate bypass are independent. Setting a WP post password requires WP post password to enter — the pb_admin bypass only works for pb-content-gate gate.

---

**Report file**: `/home/jared/projects/AI-CIV/aether/exports/site-diagnosis-2026-03-10.md`
