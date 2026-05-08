# Blog QA Regression Report — 2026-05-02

**BOOP**: nightly-blog-qa
**Target**: https://purebrain.ai/blog/
**Reference standard**: March 20, 2026 locked-in template (4 features: 60% opacity bg, background video, collapsible FAQs, daily recap)
**Reference post**: `the-ai-that-gets-smarter-when-you-push-back` (passes all checks)

---

## REGRESSIONS FOUND

### 1. CRITICAL — Broken audio on LATEST post (Apr 30)
- **Post**: `/blog/the-compound-intelligence-effect-why-month-6-matters-more-t/`
- **Issue**: HTML contains `<audio controls>` referencing `audio.mp3`, but the file returns **HTTP 404**.
- **Impact**: Top-of-feed post has a visible audio player that fails to load. Customer-facing.
- **Verify**: `curl -I https://purebrain.ai/blog/the-compound-intelligence-effect-why-month-6-matters-more-t/audio.mp3` → 404

### 2. TEMPLATE DRIFT — 2 of 4 locked features missing on latest 2 posts
The March 20 standard requires: background video + 60% opacity bg + collapsible FAQs + daily recap section.

| Post | Date | bg-video | FAQ section | Daily Recap |
|------|------|----------|-------------|-------------|
| the-ai-that-gets-smarter-when-you-push-back (REFERENCE) | — | ✓ | ✓ | ✓ |
| the-compound-intelligence-effect (Apr 30) | LATEST | ✓ | ✗ MISSING | ✗ MISSING |
| the-3-am-test (Apr 26) | #2 | ✓ | ✗ MISSING | ✗ MISSING |
| your-ai-has-a-memory-problem (Apr 23) | #3 | ✓ | (not checked) | (not checked) |

The two newest posts are NOT using the locked template — neither has `pb-faq-section` markup nor `Daily Recap` block.

### 3. INDEX OVERFLOW — 11 posts shown (locked max = 10)
- `<li>` count on https://purebrain.ai/blog/ = **11**
- Standard says max 10 on index.

### 4. SEO REGRESSION — JSON-LD ItemList out of sync with rendered list
- Rendered HTML position 1 = `the-compound-intelligence-effect` (Apr 30)
- JSON-LD ItemList position 1 = `the-3-am-test` (Apr 26) — i.e. structured data is stale, missing the actual latest post.
- JSON-LD position 10 = `https://purebrain.ai/blog/when-ai-starts-writing-prescriptions/` — this URL is **not** in the rendered list. Likely orphan reference / removed post still in structured data.
- Search engines will see a different newest post than humans.

---

## PASSING CHECKS

- ✓ Sequential dates newest→oldest (Apr 30 → Apr 14)
- ✓ Latest post at top
- ✓ Oswald font loaded + applied to headings
- ✓ Dark theme palette (#0a0c14 / #0d1120 / #080c18 — same family as locked #080a12; minor variance only)
- ✓ Footer CTA links to `https://purebrain.ai/#awakening`
- ✓ All 4 sampled post URLs return HTTP 200
- ✓ Banner images present (jpg or png) on all sampled posts
- ✓ Background video present on all sampled posts
- ✓ `audio.mp3` resolves on reference post + the-3-am-test + your-ai-has-a-memory-problem
- ✓ Awakening CTA link present multiple times per post

---

## RECOMMENDED ROUTING

**ST# (Tech)**: Fix `audio.mp3` 404 on `the-compound-intelligence-effect` post — likely missing voice generation step in publish pipeline. Pin against same regression.

**ST# (Tech)**: Patch publish pipeline so JSON-LD ItemList regenerates from current `<li>` list, not a stale snapshot. Remove orphan `when-ai-starts-writing-prescriptions` reference.

**ST# (Tech)**: Cap blog index at 10 posts (currently 11).

**MA# (Marketing) + ST# (Tech)**: Verify why the-compound-intelligence-effect and the-3-am-test were published WITHOUT the FAQ section and Daily Recap block. Either they bypassed the post-blog skill or the template emitter regressed. The reference post `the-ai-that-gets-smarter-when-you-push-back` is the gold-standard markup to compare against.
