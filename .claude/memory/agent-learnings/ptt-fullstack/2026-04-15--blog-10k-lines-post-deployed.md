# Blog Deploy: your-ai-wrote-10000-lines-how-many-shipped

**Date:** 2026-04-15
**Type:** operational
**Topic:** Deploying missing blog page using prompting-is-dead as March 20 template

## What worked

1. **Clone-and-swap approach**: Used `/exports/cf-pages-deploy/blog/prompting-is-dead/index.html` as canonical March 20 template (video bg + audio player + 4-FAQ + daily recap). Wrote a small Python script to string-replace title/desc/OG/JSON-LD/article body/FAQ/recap — preserves every locked feature, CTA block, related posts, subscribe form.
2. **cf-deploy.py with CF_PAGES_PROJECT=purebrain-production**: deploys specific files only (4 files). Preserves all 1164 existing production files. No risk of wrangler-style deletion.
3. **Sitemap edit**: simple `<url>` insert after existing 52-billion entry, priority 0.8, lastmod=today.
4. **Blog index swap**: prepended new `<li>` to wp-block-latest-posts list and dropped oldest (the-app-is-dead) to stay at 10 posts.
5. **Cache purge**: per-URL purge initially missed `/blog/` — needed `prefixes: ["purebrain.ai/blog/"]` purge to flush the index page.

## Verification outputs

- `curl -I https://purebrain.ai/blog/your-ai-wrote-10000-lines-how-many-shipped/` → HTTP/2 200, 40,429 bytes (confirms not homepage fallback)
- Title tag correct: "Your AI Wrote 10,000 Lines of Code Last Week. How Many Shipped? – PureBrain"
- `curl -I .../banner.png` → HTTP/2 200, 703,203 bytes, content-type image/png
- Sitemap contains new URL (grep count 1)
- Blog index contains new slug after prefix purge (grep count 1)
- Deployment ID: 4612649c-abb7-4db1-8568-ae2a936177cc
- Preview: https://4612649c.purebrain-production-23b.pages.dev

## Gotchas

- Default `cf-deploy.py` project is `purebrain-staging` which is the dev preview (staging.purebrain.ai has its own project, purebrain-staging-new). Production = `purebrain-production`. MUST set explicitly or customer-visible changes don't reach purebrain.ai. (See civ memory: 2026-04-15 /refer incident.)
- `curl` against `https://purebrain.ai/blog/` edge-cached the old index; per-URL purge didn't clear it reliably. Use `prefixes` purge for index pages.
- WordPress dual-publish to jaredsanborn.com NOT done in this task — left for separate WP publisher run (needs WP_USER/WP_PASS creds and `dual_blog_publish.py`). Task explicitly allowed this since CF Pages is primary.

## Files touched

- Created: `/exports/cf-pages-deploy/blog/your-ai-wrote-10000-lines-how-many-shipped/index.html` (40,425 bytes, 484 lines)
- Modified: `/exports/cf-pages-deploy/blog/index.html` (swapped top card, dropped oldest)
- Modified: `/exports/cf-pages-deploy/sitemap.xml` (added entry)
- Removed: `/exports/cf-pages-deploy/777-command-center/sed4aArC9` (stray empty file from earlier session)

## Commands (replay)

```bash
python3 /tmp/gen_10k_post.py  # generates index.html from template
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py \
  blog/your-ai-wrote-10000-lines-how-many-shipped/index.html \
  blog/your-ai-wrote-10000-lines-how-many-shipped/banner.png \
  blog/index.html \
  sitemap.xml
# then CF prefix purge for purebrain.ai/blog/
```
