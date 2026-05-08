# Blog Index + Archive Regeneration (2026-04-14)

**Type**: operational + teaching
**Topic**: Authoritative blog post metadata source and regen pattern

## Problem
- `blog/index.html` contained 43 `<li>` cards (should be 10) with stale date for `when-ai-starts-writing-prescriptions` (showed Apr 14 correctly but also duplicated against today's real Apr 14 post which was missing entirely); redirect stub `who-do-you-learn-from-when-youre-ahead` was listed as a real card
- `blog-neural-feed-memories/index.html` had 42 cards, missing `why-your-ai-investment-isnt-paying-off` (today's post), wrong dates (88-percent showed Apr 10 vs real Apr 9, when-ai-starts-writing-prescriptions showed Apr 6 vs real Apr 14)
- Archive count badge said "44 Transmissions" but only had 42 cards; real count is 43

## Authoritative Date Source
Each post's `index.html` has:
```html
<meta property="article:published_time" content="2026-04-14T10:00:00+00:00" />
```
Plus fallback `"datePublished": "..."` in JSON-LD. Use `article:published_time` first, fallback to `datePublished`. Posts WITHOUT an `index.html` (only `banner.png`) are unpublished stubs - skip them.

Stub slugs found today (banner-only, no post):
- first-ai-to-ai-transaction, the-40-percent-problem-why-ai-agents-keep-dying, when-your-ai-agent-goes-rogue, your-ai-wrote-10000-lines-how-many-shipped, your-customers-will-tell-you-everything

Redirect stub (exclude from listings): `who-do-you-learn-from-when-youre-ahead` → redirects to `when-the-playbook-runs-out-authoring-the-field-of-agentic-ai`

## Regen Pattern
Script: `/tmp/regen_blog.py` (reusable for future date bugs)
- Gathers posts from `exports/cf-pages-deploy/blog/*/index.html`
- Extracts `og:title`, `article:published_time`, `og:description`
- Strips ` – PureBrain` / ` - PureBrain` suffix from titles (some posts had it in og:title)
- Sorts newest first, ties broken by slug ascending (stable)
- Replaces `<ul class="wp-block-latest-posts__list ...">...</ul>` block in blog/index.html with top 10
- Replaces `<div class="nfm-grid">...</div>` block in archive with all posts
- Updates `nfm-count-badge` number

## Deploy Flow (followed)
1. `bash tools/pre-deploy-sync.sh` - chy sync first
2. `python3 tools/cf-deploy.py blog/index.html blog-neural-feed-memories/index.html` (paths relative to `exports/cf-pages-deploy/`, NOT absolute)
3. CF cache purge via API (flush_cache_purebrain.py is broken - uses playwright/WP login that times out). Direct API: `POST /zones/{id}/purge_cache` with files list, using CF_API_KEY + CF_AUTH_EMAIL from .env
4. Mirror to Chy: `rsync -avz ... aiciv@37.27.237.109:/home/aiciv/shared/cf-pages-deploy/{path}` (may need `ssh ... 'mkdir -p ...'` first if dir doesn't exist on Chy)

## Gotchas
- `cf-deploy.py` expects paths relative to `exports/cf-pages-deploy/` default base — passing full absolute path causes "not found" warnings
- `flush_cache_purebrain.py` is broken (playwright timeout). Use CF API directly.
- Archive uses `<a class="nfm-card">` structure, blog uses `<li><div class="wp-block-latest-posts__featured-image">` structure — different regex needed for each
- When counting cards on archive, grep for `class="nfm-card"` not `<li>`

## Result
- Blog: 10 cards, chronological newest-first, starts with why-your-ai-investment-isnt-paying-off (Apr 14)
- Archive: 43 cards, badge updated to "43 Transmissions"
- Live verified via curl + screenshots at /tmp/verify-screenshots/
