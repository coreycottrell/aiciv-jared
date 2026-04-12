# Blog Post Layout Fix: Missing FAQ, Transparency, Social Share Sections

**Date**: 2026-03-01
**Type**: gotcha + pattern
**Post Fixed**: page ID 1139 (your-ai-doesnt-work-for-you)
**Reference**: page ID 1084 (ai-doesnt-make-your-team-smarter)

---

## Root Cause

New blog posts published without the three standard section blocks that all reference posts have:
1. **Transparency section** - inline inside `<article class="pb-blog-post">`
2. **FAQ accordion** - 5 questions relevant to the post topic
3. **pt-social-share** - LinkedIn, X, Facebook, Email share buttons

The outer structure was correct:
- Template: empty string (default) - correct
- Wrapper: `<article class="pb-blog-post">` - correct
- Block: `<!-- wp:html -->` ... `<!-- /wp:html -->` - correct

But the content only had the main article text + blog-cta-block. It was missing the bottom section.

---

## Standard Blog Post Content Structure (CANONICAL)

```
<!-- wp:html -->
<article class="pb-blog-post">

  <p class="byline">...</p>

  [main article content: paragraphs, H2 headings, HRs]

  <hr>
  <!-- TRANSPARENCY SECTION -->
  <div class="transparency-section" style="margin-top: 48px; padding: 20px; border: 1px solid rgba(42,147,193,0.2); border-radius: 8px; background: rgba(42,147,193,0.05);">
  <p style="font-size: 0.85rem; color: rgba(255,255,255,0.5); margin: 0;">This post was developed with AI assistance. ...</p>
  </div>

  <hr>

  <!-- FAQ ACCORDION -->
  <h2>Frequently Asked Questions</h2>
  <style>[faq CSS]</style>
  [5 faq-section divs with topic-relevant Q&As]
  <script>[faq toggle JS]</script>

  <!-- Social Sharing Icons -->
  <style>[pt-social-share CSS]</style>
  <div class="pt-social-share">
    <span>Share:</span>
    [LinkedIn, X, Facebook, Email icons]
  </div>

  <div class="blog-cta-block" ...>
    [CTA with awakening link]
    [newsletter subscribe link]
  </div>

</article>
<!-- /wp:html -->
```

---

## Fix Applied

- Injected transparency + FAQ (5 questions tailored to "AI working for you" topic) + pt-social-share BEFORE the `blog-cta-block`
- Deployed via REST API: `POST /wp-json/wp/v2/posts/1139` with updated content
- Cleared Elementor cache: `DELETE /wp-json/elementor/v1/cache`
- Verified all sections present in live page

---

## Verification Results

After fix, post 1139 has:
- transparency-section: YES
- faq-section count: 14 (same as reference - 5 questions x styles/answers)
- pt-social-share: YES
- blog-cta-block: YES
- CTA + newsletter link: YES
- Template: default (empty string)
- Wrapper: `<article class="pb-blog-post">`

---

## Prevention Rule

Every new blog post MUST include all 4 sections below the main article text:
1. Transparency section (before FAQ)
2. FAQ accordion (5 questions, topic-specific)
3. pt-social-share (LinkedIn, X, Facebook, Email)
4. blog-cta-block (CTA button + newsletter link)

Reference FAQ/Social/Transparency blocks: extract from post 1084 raw content via REST API.
