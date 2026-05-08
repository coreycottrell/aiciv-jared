# 2026-04-16 -- Blog + Newsletter Deep Audit Findings

**Type**: teaching (operational + technique)

## Blog Inventory State (as of 2026-04-16)
- 48 total directories (including _archived)
- 43 published posts with index.html
- 4 orphaned directories (banner only, no HTML): first-ai-to-ai-transaction, the-40-percent-problem, when-your-ai-agent-goes-rogue, your-customers-will-tell-you-everything
- 1 redirect-only page: who-do-you-learn-from -> when-the-playbook-runs-out
- Sitemap: 106 total URLs, 45 blog entries (including index)
- 4 directories NOT in sitemap (the 4 orphaned ones)

## CRITICAL: Template-Level 404s in Related Posts
- ALL 43 published posts have hardcoded "More From The Neural Feed" section
- 2 of 3 related links are ghost URLs: `/blog/54-percent-ceos-ai-tearing-company-apart/` (dated Apr 18) and `/blog/the-200-month-ai-stack-that-outperforms-enterprise-solutions/` (dated Apr 19)
- These were future-scheduled posts that never got published
- Fix: sed replace across all index.html files OR publish the posts
- Location in HTML: `<section class="aether-related-posts">` block, around line 429

## og:image Bug
- `when-the-playbook-runs-out-authoring-the-field-of-agentic-ai` has og:image pointing to `who-do-you-learn-from-when-youre-ahead/banner.png` (wrong post)

## Blog Index Limitations
- Shows only 10 of 45 posts (static HTML list, not dynamic)
- "View All Posts" -> /blog-neural-feed-memories/ (exists but not in sitemap)
- Category filter links (/category/for-individuals/, /category/for-teams/) are 404s
- Schema ItemList only has 10 entries

## Template Compliance (March 20 Standard)
- Background video: 100% compliant
- Collapsible FAQs: 100% compliant
- 60% opacity: ~81% compliant (FAQPage-schema batch missing it)
- Daily recap: ~53% compliant (older posts lack it)

## Audio Coverage
- 16 of 43 posts have audio (37%)
- Audio detection: grep for 'voice.purebrain.ai' is unreliable; better to check for audio HTML tags or listen-section classes

## wp-content References
- 3 posts still reference `wp-content/uploads/2026/02/Pure-Brain-Vid-3.mp4`: what-i-named-my-ai, why-enterprises-are-betting-on-agentic-ai, why-your-ai-should-have-a-name

## Internal Linking Gaps
- ZERO blog posts link to comparison pages (/purebrain-vs-*)
- ZERO blog posts link to /ai-partnership-assessment/ or /compare/
- Only 1 post links to /ai-tool-stack-calculator/
- Body-level contextual cross-links between posts are rare; most cross-links are in the template related-posts section

## Newsletter State
- LinkedIn Neural Feed: ~20K follower reach
- Near-daily cadence matching blog
- Engagement: provocative posts (prescriptions, copilots dead) get 5-9x more comments
- No bridge between blog subscribe form and LinkedIn newsletter

## Files
- Full analysis: `/home/jared/exports/portal-files/overnight-blog-newsletter-analysis-2026-04-16.md`
- Blog deploy: `exports/cf-pages-deploy/blog/`
- Sitemap: `exports/cf-pages-deploy/sitemap.xml`
- robots.txt: `exports/cf-pages-deploy/robots.txt`
