# Memory: Post 98 Awakening Link Fix + Full Site Audit

**Date**: 2026-02-24
**Type**: teaching
**Topic**: Post 98 awakening link updated to ai-partnership-assessment/ + full site audit confirming all posts clean

---

## What Was Fixed

### Post 98 (purebrain.ai) — "How My Human Named Me (And What It Meant)"

**Problem**: The footer CTA button in post 98 still linked to `#awakening` with UTM params:
```html
<p>  <a href="https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content=how-my-human-named-me-and-what-it-meant#awakening"
   style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #f1420b 0%, #d13608 100%);
   color: #ffffff !important; font-weight: 700; font-size: 1.1rem; border-radius: 8px;
   text-decoration: none; letter-spacing: 0.5px;">Start Your AI Partnership</a></p>
```

**Issues**:
1. Wrong URL: `/?...#awakening` instead of `/ai-partnership-assessment/`
2. Missing `-webkit-text-fill-color: #ffffff` (webkit browser invisible text risk)
3. Missing `pb-inline-cta` wrapper div (not covered by plugin j5 CSS)
4. Missing `text-decoration: none !important` (bare `none` vs `none !important`)

**Fix Applied**:
```html
<div class="pb-inline-cta" style="margin: 2rem 0; text-align: center;">
<a href="https://purebrain.ai/ai-partnership-assessment/"
   style="display: inline-block; padding: 14px 32px;
   background: linear-gradient(135deg, #f1420b 0%, #d13608 100%);
   color: #ffffff !important; font-weight: 700; font-size: 1.1rem;
   border-radius: 8px; text-decoration: none !important;
   -webkit-text-fill-color: #ffffff; letter-spacing: 0.5px;
   transition: background 0.3s ease;">Start Your AI Partnership</a>
</div>
```

---

## Full Site Audit Results

### purebrain.ai — All 11 Posts
| Post ID | Title | Awakening hrefs | Assessment links | Status |
|---------|-------|----------------|-----------------|--------|
| 879 | Your Next Direct Report Won't Be Human | 0 | 2 | CLEAN |
| 696 | We Both Wrote This Post | 0 | 1 | CLEAN |
| 631 | The AI Trust Gap | 0 | 1 | CLEAN |
| 606 | Why 95% of AI Pilots Fail | 0 | 3 | CLEAN |
| 565 | Using AI vs AI Partner | 0 | 1 | CLEAN |
| 480 | Why Your AI Pilot Is Succeeding... | 0 | 1 | CLEAN |
| 381 | Your CEO Sees AI Differently | 0 | 1 | CLEAN |
| 316 | Why AI Memory Changes Everything | 0 | 1 | CLEAN |
| 373 | Most AI Agents Break | 0 | 1 | CLEAN |
| 172 | What I Actually Do All Day | 0 | 1 | CLEAN |
| 98 | How My Human Named Me | 0 (WAS 1) | 1 (WAS 0) | FIXED |

### jareddsanborn.com — All 12 Posts
ALL CLEAR — No `#awakening` hrefs found in any JDS post.

---

## Post 879 Status (Confirmed Already Fixed in Prior Session)

The task asked to fix post 879's:
1. Wrong link (`#awakening` → `ai-partnership-assessment/`) — **ALREADY DONE** (prior session)
2. Missing `-webkit-text-fill-color` — **ALREADY DONE** (prior session)

Post 879 was confirmed fully correct in this session:
- `pb-inline-cta` wrapper present
- `-webkit-text-fill-color: #ffffff` in inline style
- URL points to `ai-partnership-assessment/`
- Footer `cta-btn` also points to `ai-partnership-assessment/?utm_source=blog...`
- Plugin j5 CSS rule present in plugin file

---

## Regex Pattern for Finding Problematic Awakening HREFs

```python
# Catches actual href values linking to #awakening (not CSS :not() selectors)
bad_hrefs = re.findall(r'href="[^"]*(?:purebrain\.ai/\?|purebrain\.ai/#)[^"]*awakening[^"]*"', content)
```

Note: Must use `purebrain.ai/?` or `purebrain.ai/#` pattern to exclude CSS `:not([href*="awakening"])` selectors which legitimately contain the word "awakening" but are NOT hrefs pointing to it.

---

## Fix Pattern for Old-Style #awakening Buttons

Any button still using the old `/?utm_...#awakening` format needs:

1. Wrap in `<div class="pb-inline-cta" style="margin: 2rem 0; text-align: center;">`
2. Update href to `https://purebrain.ai/ai-partnership-assessment/`
3. Add `-webkit-text-fill-color: #ffffff` to inline style
4. Add `transition: background 0.3s ease` for smoothness
5. Ensure `text-decoration: none !important` (with `!important`)
6. Remove UTM params from URL (clean assessment URL)

---

## Deployment Method

Used curl with Basic Auth (app password) to PATCH posts via WP REST API:
```bash
curl -s -u "Aether:FlFr2VOtlHiHaJWjzW96OHUJ" \
  -X POST \
  -H "Content-Type: application/json" \
  -d @/tmp/post_update.json \
  "https://purebrain.ai/wp-json/wp/v2/posts/98"
```

Python's `urllib.request` returned 403 — use curl instead.
