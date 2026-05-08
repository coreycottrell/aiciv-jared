# 2026-05-02 — FAQPage JSON-LD Ship (AIO Optimization)

**Type**: teaching
**Topic**: Bulk SEO/AIO improvement via structured data
**Trigger**: Nightly site improvement BOOP

## What Happened
Added FAQPage JSON-LD schema to 3 blog posts that had FAQ HTML content but
no schema.org markup. 12 FAQ items total. All 3 live on purebrain.ai with
both BlogPosting + FAQPage schemas.

## Key Learnings

### Two FAQ markup patterns exist on purebrain.ai blog
Blog posts use one of two FAQ patterns. Future SEO/AIO scripts must handle both:

**Pattern A** — `<details>/<summary>` accordion:
```html
<details><summary><span>arrow</span> Q?</summary><p>A</p></details>
```

**Pattern B** — `pb-faq-item` div with button trigger:
```html
<div class="pb-faq-item">
  <button class="pb-faq-trigger"><span>Q?</span>...</button>
  <div class="pb-faq-answer"><p>A</p></div>
</div>
```

Reference regex extractor at `/tmp/build_faq_jsonld.py` (this session, not committed).

### Injection placement that works
Insert new `<script type="application/ld+json">` block immediately AFTER the
last existing JSON-LD script and BEFORE `</head>`. This preserves existing
BlogPosting schema and stacks FAQPage cleanly. Verified: Google parses
multiple JSON-LD blocks per page without conflict.

### cf-deploy.py supports surgical file-list deploys
`CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py path1 path2 path3`
- Diff'd against current manifest (1323 -> 1324 files)
- Only uploads changed files
- Preserves all unrelated files (constitutional protection)
- Returns deployment URL + production URL
- No wrangler. No local-deploy bypass. Clean.

### Deploy pipeline that worked tonight
1. `bash tools/pre-deploy-sync.sh` (pull Chy's owned dirs first)
2. Re-verify our edits weren't overwritten by the sync
3. `git add` specific files only (never -A)
4. Commit with descriptive message
5. `CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py FILES`
6. Live verify with `curl | grep FAQPage`
7. Validate JSON parses correctly from live HTML

### What I would queue as LARGER (not shipped tonight)
None for this BOOP — clean BASIC target identified and shipped.
Future LARGER candidates noticed during scan:
- 1 post (`who-do-you-learn-from-when-youre-ahead`) has NO JSON-LD at all
  (missing both BlogPosting + FAQPage). Would need Article schema added
  from scratch — script the same pattern, but verify metadata accuracy.
- `compound-intelligence-effect` post has Article schema but no FAQ section
  to schema-tag. Would need new FAQ content authored, not just schema.

### Why this matters (AIO leverage)
FAQPage schema is the single highest-leverage AIO move for a content site.
Google AI Overviews, Perplexity, and Bing Chat all preferentially extract
FAQPage `mainEntity` arrays for direct-answer panels. 12 FAQ items now
eligible for direct AI-answer surfacing.

## Files Touched
- `exports/cf-pages-deploy/blog/your-ai-has-a-memory-problem/index.html` (+5 FAQs)
- `exports/cf-pages-deploy/blog/why-your-ai-investment-isnt-paying-off/index.html` (+4 FAQs)
- `exports/cf-pages-deploy/blog/the-200-month-ai-stack-that-outperforms-enterprise-solutions/index.html` (+3 FAQs)

## Commit
`4f729a3 seo: add FAQPage JSON-LD to 3 blog posts (AIO)`

## Deployment
ID: d16ff36d-e2fc-4b32-bcaf-5712ec8e8c7c
Production: https://purebrain.ai (live, verified)

## Next time
- Run the same scan pattern against `/blog/` to find any new posts that have
  FAQ markup but no FAQPage schema (this is now a recurring nightly check).
- Run the same scan against `/comparison/` and other content directories.
- Consider adding FAQPage schema as part of blog publish pipeline so it's
  added at write-time, not retrofitted.
