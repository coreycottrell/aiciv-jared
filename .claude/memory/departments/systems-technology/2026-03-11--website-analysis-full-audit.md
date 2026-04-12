# PureBrain.ai Website Analysis — March 11 Audit

**Date**: 2026-03-11
**Type**: audit | synthesis
**Topic**: Full site audit — performance, SEO, UX, technical debt

## New Findings (not in prior audits)

### Performance
- jQuery and jquery-migrate each load 3x on homepage — dequeue fix needed
- 808KB homepage HTML — mostly Elementor inline CSS/JS (compressed via Brotli by CF)
- Homepage TTFB 0.16s (cached), invitation page TTFB 0.68s (likely cache miss)
- 0 WebP images on homepage — all PNG/JPG
- 0 fetchpriority=high on any image — no LCP optimization hint
- 0 preload hints in <head>

### SEO
- 7 blog posts missing meta descriptions (IDs: 1441, 1423, 1378, 1307, 1281, 1245, 1228)
- Post 1441 has featured image set (ID 1440, PNG exists) but Yoast not generating OG image
- /pricing/ → 404, cached by Cloudflare for 31 days (cache-control: max-age=2678400)
- 5 new compare pages still missing elementor_canvas template (IDs 1459-1463)

### Open Issues from Prior Audits (Still Unfixed)
- robots.txt NOT blocking /wp-admin/ — flagged March 6, still open March 11
- 13 internal/test pages published and indexed (flagged March 10)
- Duplicate CSS injection — #pb-aether-footer CSS appears 103x on homepage

## Status of Previous Findings
- Social proof: FIXED (testimonials now on homepage)
- Pricing on homepage: PARTIAL (in chatbox, not above fold)
- GIF background: FIXED (now mp4)

## Report
- Local: `/home/jared/projects/AI-CIV/aether/exports/website-analysis-2026-03-11.md`
- Drive: https://drive.google.com/file/d/1KriAY4nnjF-A8xxhY9zEGtVq-2qf-Uti/view
- Telegram: Sent file + summary
