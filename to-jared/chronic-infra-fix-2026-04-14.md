# Chronic Infra Fix — 2026-04-14

**Owner**: dept-systems-technology (ST#)
**Status**: Both tasks SHIPPED and QA-verified live. Day-17 analysis theater broken.

---

## Task 2: Blog Index Fixed ✅ DEPLOYED & VERIFIED

**Root cause**: `tools/fix_blog_index.py` had a hardcoded `POST_ORDER_NEWEST_FIRST` list frozen at 32 posts (Feb–Mar 20). 13 new posts were on disk but invisible to the rebuilder. Live index was showing only 8 posts.

**Fix**: Refactored `tools/fix_blog_index.py` to auto-discover all blog directories and pull dates from each post's HTML metadata (`datePublished` JSON-LD → `article:published_time` → `<time datetime>` → mtime fallback). No more manual slug lists — new posts now auto-index.

**Verification (live)**:
- https://purebrain.ai/blog/ — **45 unique post links** (was 8)
- Top of list: `the-200-month-ai-stack…` (2026-04-19) → newest-first order confirmed
- Deploy: `04644cdc.purebrain-staging.pages.dev` → CF cache purged via API

---

## Task 1: Sitemap Status ✅ FIXED + INSTRUCTIONS FOR GSC

**Live**: https://purebrain.ai/sitemap.xml — **105 URLs** (valid XML, HTTP 200, 19KB, referenced in robots.txt line: `Sitemap: https://purebrain.ai/sitemap.xml`)

**Fixed**: Sitemap was missing 1 blog post (`who-do-you-learn-from-when-youre-ahead`). Added + redeployed + purged. All 45 disk posts now indexed.

**GSC API submission**: No service account creds found in `.env` or `config/`. Programmatic submission not possible from this session — needs Jared's 2-minute manual submission:

### Jared — Submit Sitemap (3 clicks):
1. Open https://search.google.com/search-console
2. Select property **https://purebrain.ai** (or add it if not there; choose "URL prefix" + verify via DNS TXT record — CF token already has DNS perms if re-verification needed)
3. Left nav → **Sitemaps** → paste `sitemap.xml` in "Add a new sitemap" → **Submit**
4. Expected result: "Success" with ~105 URLs discovered over 24–48h

**Indexing issues to watch in GSC after 48h**:
- Any `lastmod` dates that look stale (sitemap uses real post dates, not today's date — correct per spec)
- URLs blocked by robots.txt: `/pay-test*/`, `/homepage-clone*/`, `/blog-old/`, `/assessment-draft/` (expected, these are disallowed)
- `Discovered – currently not indexed`: normal for new posts, should clear in 1–2 weeks

---

## Deploy trail (locked path followed)
`pre-deploy-sync.sh` ✅ → `cf-deploy.py blog/index.html` ✅ → `cf-deploy.py sitemap.xml` ✅ → CF cache purge API ✅ → curl verify ✅

## Next action for you
One thing: 3-click sitemap submission above. Report back confirmation number from GSC and I'll monitor indexing.
