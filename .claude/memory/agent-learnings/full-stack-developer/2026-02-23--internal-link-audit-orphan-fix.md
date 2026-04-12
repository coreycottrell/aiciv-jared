# Internal Link Audit & Orphan Fix - purebrain.ai

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: SEMRush internal linking score 85% - root cause was orphaned pages + redirect links, NOT broken 404s

---

## Key Finding: 85% SEMRush Score Was NOT Broken Links

When SEMRush flags "Internal Linking score: 85%", the issues are usually:
1. **Orphaned pages** (no inbound links from other pages)
2. **301 redirect links** (link equity lost at hop)
3. **Non-canonical URL patterns** (/blog/slug/ when real slug is /slug/)
4. **Thin pages** with few inbound links

Do NOT assume "broken links" means 404s. The real audit is:
- Count inbound links per page
- Find pages with 0 inbound links (crawlers can't discover them)
- Find links that 301-redirect instead of pointing to canonical URL

## Pages That Were Orphaned (0 inbound links)

On purebrain.ai as of 2026-02-23:
- `/about-aether/` - the Meet Aether page
- `/ai-adoption-review/` - qualification landing page
- `/terms-of-service/` - had 1 but purebrain-4 linked with wrong /terms URL
- `/ai-readiness-assessment/` - self-assessment page
- `/migrate/` - migration portal (newest page)
- `/purebrain-4/` (legacy, left alone)

## Redirect Links Found

Post 606 linked to `/blog/the-difference-between-using-ai.../` and `/blog/why-ai-memory.../` - these 301 to `/slug/` canonical. Fixed by removing /blog/ prefix.

Page 383 linked to `/terms` which 301s to `/terms-of-service/`. Fixed to use canonical.

## Where to Add Inbound Links for Orphaned Pages

Matching strategy used:
- `/about-aether/` → from post 696 ("We Both Wrote This Post" - literally about Aether)
- `/ai-adoption-review/` → from post 480 (AI pilot post - "assessing where you actually are")
- `/terms-of-service/` → from privacy-policy (cross-reference at end of Contact section)
- `/ai-readiness-assessment/` → from page 405 ai-partnership-guide ("AI Readiness Assessment framework")
- `/migrate/` → from page 700 neural-feed-memories (archive → migration is natural next step)

## WordPress REST API Pattern for Link Audit

```python
# Get raw content (NOT rendered - rendered doesn't have raw href values)
resp = requests.get(f"{BASE_URL}/wp-json/wp/v2/posts/{id}?context=edit", auth=AUTH)
raw = resp.json()['content']['raw']

# Extract links
href_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
links = href_pattern.findall(raw)

# Check status
resp = requests.head(url, allow_redirects=False)
# status 301/302 = redirect (bad for SEO, fix to canonical)
# status 404 = broken (remove or fix)
# status 200 = good
```

## How to Find Orphaned Pages

```python
# Build inbound_links dict: canonical_url -> list of source pages
inbound_links = defaultdict(list)
for item in all_items:
    for link in extract_links(item['content']['raw']):
        canonical = normalize(link)
        if canonical in known_pages and canonical != item['link']:
            inbound_links[canonical].append(item['url'])

# Find orphans
orphans = [url for url in all_canonical_urls if len(inbound_links[url]) == 0]
```

## Content Patterns for Natural Link Anchors

When adding links to orphaned pages, find CONTEXTUAL anchors, not generic "click here":
- About page → find first-person mention of the AI's name
- Assessment/qualification page → find "assessing", "qualify", "ready" context
- Terms page → add cross-reference in Privacy Policy contact section
- Migration page → add near archive/history content

## What NOT to Fix

- `/purebrain-vs-chatgpt/` etc. (VS pages) - these are SEO landing pages, their inbound is from homepage compare section. Not orphans.
- `/pay-test/`, `/pay-test-sandbox/` - internal tools, should NOT be indexed
- `/purebrain-3/`, `/purebrain-4/` - legacy pages, low priority

## Verification Method

After fixing, re-run inbound link check:
```python
def check_inbound(target_slug):
    for item in all_items:
        content = item['content']['raw']
        if target_slug in content:
            yield item['title']
```

## Files

- Crawler script: `/tmp/crawl_internal_links.py`
- SEMRush analysis: `/tmp/semrush_issues.py`
- Fix scripts: `/tmp/fix_links.py`, `/tmp/apply_orphan_fixes.py`, `/tmp/final_orphan_fixes.py`
- Report: `/home/jared/projects/AI-CIV/aether/exports/departments/marketing-advertising/broken-links-report.md`

---

**End of Memory**
