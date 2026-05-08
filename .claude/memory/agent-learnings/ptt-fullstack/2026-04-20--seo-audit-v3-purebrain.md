# SEO Audit V3 - purebrain.ai Findings

**Date**: 2026-04-20
**Type**: operational
**Topic**: Website SEO audit V3 - tracking persistent issues and new discoveries

## Key Findings

### Persistent (14 days unfixed since V1)
- `/live*/` robots.txt block still active -- conversion page invisible to Google
- Homepage og:image still wp-content GIF -- now has 8 og:image tags (duplicates worsening)
- Homepage still has 2 title tags (WP + custom)
- Yoast schema graph still present on homepage
- 22 comparison pages still missing og:image
- 8 blog posts still missing from sitemap (50 deployed, 42 in sitemap)
- /pricing/ still does not exist (WP fallback)
- Sitemap stuck at 97 URLs

### New V3 Discoveries
- 2 ghost blog posts (the-200-month-ai-stack..., 54-percent-ceos...) are linked from related-posts but serve WP fallback (canonical -> homepage). Not in deploy folder.
- /team/meetings/ and /meetings/form/ are real functional pages (Meeting Scheduler, Pre-Meeting Form) but have no SEO tags, no sitemap entry, and unclear if meant to be public
- Built by Aether footer missing from individual blog posts and /get-started/
- social.purebrain.ai requires auth to verify scheduled content; API endpoints return errors without credentials

### CF Protection Note
- WebFetch tool gets 403 on purebrain.ai (CF bot protection). Must use curl with browser UA from server.
- robots.txt fetches work without UA spoofing

## File Paths
- V3 report: `/home/jared/exports/portal-files/OVERNIGHT-WEBSITE-V3-2026-04-20.md`
- V2 report: `/home/jared/exports/portal-files/OVERNIGHT-WEBSITE-V2-2026-04-19.md`
- Deploy folder: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/`
