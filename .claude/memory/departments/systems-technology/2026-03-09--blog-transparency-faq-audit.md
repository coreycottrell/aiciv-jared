# Blog Transparency + FAQ Audit
**Date**: 2026-03-09
**Type**: pattern, gotcha

## KEY FINDING: Plugin Footer Duplication Bug
- Double transparency section on ALL purebrain.ai single posts is a PLUGIN bug, not post content
- Plugin v6.2.2 (active) + v4.8.6 (inactive) both present on server
- Entire wp_footer plugin output duplicated — 7 scripts + 14 styles all appear twice
- Fix requires security agent (cannot touch security plugin without them)

## STALE CSS BLOCKS PATTERN
- Old posts (published during plugin v3.9.x era) had CSS style blocks hardcoded into post_content
- These blocks: pb-transparency-cta-v394, pb-link-hover-v393, pb-tag-pills-v390, pb-social-share-v420
- Now handled by plugin via wp_head — having them in post content = duplicate CSS
- Fixed: 10 purebrain.ai posts + 11 jareddsanborn.com posts (total 21 posts cleaned)

## FAQ STATUS purebrain.ai
- 23 total posts, 15 have FAQ
- Only POST 879 is fully correct (FAQ + accordion + JSON-LD)
- 6 posts need JSON-LD added: 1245, 1189, 1139, 1084, 966, 950
- 8 older posts have JSON-LD but no accordion CSS class (plugin JS may handle at render time)

## FAQ STATUS jareddsanborn.com  
- 24 total posts, 17 have FAQ
- 10 have JSON-LD schema, 4 have accordion
- No double transparency (transparency plugin NOT on JDS)

## LESSON: Check plugin registry before assuming post content issue
- When Jared reports visual duplication on blog posts, first check `wp-json/wp/v2/plugins` for duplicate plugin registrations
- Pattern: `id="pb-transparency-section"` appearing twice in live HTML = plugin issue, not content

## REPORT
Path: exports/departments/systems-technology/reports/2026-03-09--blog-transparency-faq-audit.md
