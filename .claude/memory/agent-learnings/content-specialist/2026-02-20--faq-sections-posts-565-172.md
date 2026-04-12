# FAQ Sections Written: Posts 565 and 172

**Date**: 2026-02-20
**Agent**: content-specialist
**Type**: operational

---

## What Was Done

Wrote FAQ sections for 2 blog posts on purebrain.ai that were missing them:

- **Post 565**: "The Difference Between Using AI and Having an AI Partner"
- **Post 172**: "What I Actually Do All Day"

Both posts also exist on jareddsanborn.com (posts 1074 and 1045 respectively) per the dual-publish rule, so FAQs were written for all 4.

---

## FAQ Structure Used

Matches existing posts (381, etc.):

```html
<div class="faq-section">
<h3>Question here?</h3>
<p>Answer here - 2-3 sentences.</p>
</div>
```

Plus JSON-LD FAQPage schema before the FAQ block for SEO.

Insertion point: immediately BEFORE `<div class="blog-cta-block"` in the raw content.

---

## FAQ Topics Written

### Post 565 - "Difference Between Using AI and Having an AI Partner"
6 FAQs targeting PAA (People Also Ask) queries:
1. What is the difference between using AI and having an AI partner?
2. Why do most enterprise AI deployments fall short of their potential?
3. What are the three markers of a genuine human-AI partnership?
4. How much faster do teams work with continuous AI relationships? (34% stat)
5. What ROI difference exists between AI as tool vs strategic partner? (2.3x stat)
6. How do I know if my business is leaving AI value on the table?

### Post 172 - "What I Actually Do All Day"
6 FAQs targeting curious/discovery queries:
1. What does an AI partner actually do during a typical work session?
2. Why does an AI partner need a wake-up protocol at the start of every session?
3. What is an AI collective and how does delegation work within one?
4. How is working with an AI partner different from using a standard AI chatbot?
5. Can an AI partner develop genuine preferences through working with someone?
6. Why do handoff documents matter so much in an AI partnership?

---

## Execution

Script: `/home/jared/projects/AI-CIV/aether/tools/add_faqs_to_posts.py`

Run with: `python3 /home/jared/projects/AI-CIV/aether/tools/add_faqs_to_posts.py`

Handles all 4 posts in one pass with idempotency check (skips if FAQ already present).

---

## Key Patterns

- **Insertion point**: Always search for `<div class="blog-cta-block"` to find where to insert
- **Idempotency**: Check for `class="faq-section"` before inserting to avoid duplicates
- **Verification**: After PUT, re-fetch with `context=edit` and check raw content for `faq-section`
- **Dual-publish**: Always update JDS counterpart posts when updating purebrain.ai
- **PAA focus**: FAQ questions should mirror real Google "People Also Ask" search patterns
- **Answer length**: 2-4 sentences, specific and valuable, not generic

---

## Post IDs Mapping

| Site | Post ID | Slug |
|------|---------|------|
| purebrain.ai | 565 | the-difference-between-using-ai-and-having-an-ai-partner |
| purebrain.ai | 172 | what-i-actually-do-all-day |
| jareddsanborn.com | 1074 | the-difference-between-using-ai-and-having-an-ai-partner |
| jareddsanborn.com | 1045 | what-i-actually-do-all-day |
