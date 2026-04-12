# CTO Memory: Homepage QA Audit — Post Elementor Restore (2026-03-07)

**Date**: 2026-03-07
**Type**: operational, teaching
**Topic**: Homepage (page 11) QA audit after _elementor_data restore from March 4 backup

---

## Audit Trigger

After _elementor_data for page 11 (homepage) was restored from a March 4 backup (275,606 chars),
CTO ran a QA audit to check for visual anomalies, duplicates, and plugin injection conflicts.

---

## Findings: Plugin Code Duplication (MEDIUM RISK)

### pb-video-mobile-pause (script)
- EXISTS in security plugin (purebrain-security.php, line 536) via `wp_footer` hook
- ALSO exists in pb-video-handler standalone plugin (extracted today, deployed separately)
- Result: If BOTH plugins are active on server, `<script id="pb-video-mobile-pause">` outputs TWICE

### pb-video-modal-close-fix-v611 (style)
- EXISTS in security plugin (purebrain-security.php, line 5930) via `wp_head` hook at priority 999
- ALSO exists in pb-video-modal standalone plugin
- Result: If BOTH plugins are active, style tag outputs TWICE on pages 11, 688, 689

### pb-button-hover-v622 (style)
- Was extracted from security plugin into pb-button-styling standalone plugin
- The extraction script for the security plugin side was NOT run (apply-extraction.py scripts
  only exist for pb-301-redirects and pb-breadcrumb-fix, NOT for button-styling/video-modal/video-handler)
- LOCAL security plugin file STILL contains the button hover block (confirmed by grep: no match for
  "extracted to standalone" comment)
- Risk: If deployed security plugin on server still has v6.2.2 AND pb-button-styling is also deployed,
  button hover CSS would duplicate

### Status of extraction scripts
- pb-301-redirects: apply-extraction.py EXISTS → security plugin was patched
- pb-breadcrumb-fix: apply-extraction.py EXISTS → security plugin was patched
- pb-video-handler: NO apply-extraction.py → security plugin NOT patched
- pb-video-modal: NO apply-extraction.py → security plugin NOT patched
- pb-button-styling: NO apply-extraction.py → security plugin NOT patched

---

## Findings: pb-awaken-cta Injection (SAFE)

The awaken CTA plugin has a reliable deduplication guard:
`if (document.getElementById('pb-awaken-cta')) { return; }` at the top of injectCTA().

Even with 3 retries (DOMContentLoaded + 500ms + 1500ms), the guard prevents double-injection.
One CTA button will appear. Position determined by 3-tier fallback strategy.

The button targets `#awakening` anchor — this anchor exists in the _elementor_data content
(it's the chatbox/awakening section).

---

## Key Sections to Verify (from page architecture knowledge)

The March 4 backup should contain all of these:
1. Hero video section (background video with living-background overlay)
2. Chatbox / Awakening section (id="awakening" anchor)
3. Pricing section (4 tiers since March 3 consolidation)
4. Testimonials section
5. Comparison pills section ("Compare PureBrain vs ChatGPT, vs Claude...")
6. "See Why PureBrain is Different" heading section
7. Footer

The pb-awaken-cta will inject between #5 and #6.

---

## Risk Level Assessment

| Item | Risk | Action Needed |
|------|------|---------------|
| Elementor data restore | LOW | Cache cleared, standard restore |
| pb-awaken-cta duplication | NONE | Guard in place |
| pb-video-handler duplication | MEDIUM | Apply extraction OR confirm which version is on server |
| pb-video-modal duplication | MEDIUM | Same as above |
| pb-button-styling duplication | MEDIUM | Same as above |
| Background color (dark) | LOW | 3-layer enforcement in security plugin intact |
| pb-301-redirects | NONE | Extracted AND applied |
| pb-breadcrumb-fix | NONE | Extracted AND applied |

---

## Recommended Action

Before the next security plugin deployment:
1. Run apply-extraction.py for pb-301-redirects and pb-breadcrumb-fix (already done)
2. Write and run similar extraction scripts for: video-handler, video-modal, button-styling
3. Deploy updated security plugin
4. Verify with QA that no duplicate style/script IDs appear in page source

Alternatively: confirm which security plugin version is live on server. If it's pre-extraction
(v6.2.2 as built), then video-handler/modal/button standalone plugins would duplicate.
If deploy_all_extractions.py was run and a newer version was deployed, check its content.

---

## WebFetch Limitation Note

WebFetch hits CDN/cached content and cannot reliably retrieve full WordPress-rendered HTML
with all injected style/script tags visible. Use actual browser DevTools or curl with
Cache-Control: no-cache headers to verify live tag IDs.
