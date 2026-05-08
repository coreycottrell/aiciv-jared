# Follow-Up Site Audit: purebrain.ai (Apr 25, 2026)
**Type**: operational
**Agent**: seo-specialist

## Key Findings

### Zero of five issues from Apr 24 were fixed
- Homepage + 4 landing pages still have wp-content og:image (BROKEN)
- Blog index still shows only 14 of 53 posts
- 7+ blog posts still missing from sitemap (102 URLs unchanged)
- Pricing pages have 3 conflicting og:image tags each (new finding)

### One issue confirmed fixed
- Brainiac training modules now have correct titles (not serving homepage)

### New issues discovered
- No 404.html exists -- CF Pages serves homepage with HTTP 200 for all invalid URLs
- /ai-partnership-assessment-v2/ does not exist in deploy folder
- /ai-partnership-assessment/ exists but has no meta description, og:image, or canonical
- /brainiac-module-1-foundations/ missing from sitemap
- /assessment-draft/ publicly accessible (possibly should not be)

### "Your AI Has a Memory Problem" blog post
- Live and resolving HTTP 200 on purebrain.ai
- og:image correct (banner.jpg, absolute URL, resolves)
- Missing: brand suffix in title, sitemap entry, blog index listing, second JSON-LD block
- Author credited as "Aether" (not Jared)

### Technical notes
- CF Pages 404 behavior: without 404.html, serves homepage as HTTP 200
- Pricing pages (/awakened/, /partnered/, /unified/) each have 3 og:image tags from WordPress export -- Yoast class tag + 2 wp-content GIFs
- Portal delivery requires files in ~/exports/portal-files/ (home dir), not project exports dir

## File paths
- Report: `/home/jared/projects/AI-CIV/aether/exports/portal-files/overnight-site-analysis-2026-04-25.md`
- Prior report: `/home/jared/projects/AI-CIV/aether/exports/portal-files/overnight-site-analysis-2026-04-24.md`
