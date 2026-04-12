# Blog Banner Full Visual Audit - 2026-03-18

## Task
Complete visual inspection of ALL 31 blog post banners in response to Jared's report that "half are wrong."

## Key Finding: Banners Are NOT Git-Tracked

Banner image files are NOT committed to git. This means:
- Git cannot restore them — no commit history exists for binary banner files
- The only git-tracked blog changes are to HTML files
- Source banners exist in exports/blog-content-*, exports/overnight-blog*, exports/blog-images/

## Complete Visual Audit Results

### CONFIRMED WRONG - Content Clearly Mismatched

1. most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/banner.jpg
   - Post title: "Most AI Agents Break the Moment You Ask Where the Data Goes"
   - Banner shows: "Enterprise AI That Learns How Your Business Runs"
   - Hash: 140a90485e75c4a130152ac3aac38d8d (170,146 bytes)
   - Best replacement: exports/blog-content/2026-02-15-enterprise-ready-ai/blog-header.png
     (shows AI face + security shield, thematically appropriate)

2. why-your-ai-should-have-a-name/banner.png
   - Post title: "Why Your AI Should Have a Name"
   - Banner shows: Generic abstract nebula/flower — no post title, no branding
   - Hash: b78a9afd329aeb52988b6ef9b9870586 (2,705,508 bytes)
   - Needs new banner generated

### QUALITY ISSUES (Typos in Banner Text)

3. why-enterprises-are-betting-on-agentic-ai/banner.png
   - Banner text has typos: "enterprisies", "bettting on on agentic AI"
   - This IS the original source — typos were in exports/blog-images/ too
   - Needs new banner generated with correct text

### ALL OTHERS VERIFIED CORRECT (28 posts confirmed visually correct)

## Architecture Notes
- No nightly scripts touch binary banner files
- fix_blog_banner_and_deploy.py only modifies HTML references
- Banner files never committed to git
