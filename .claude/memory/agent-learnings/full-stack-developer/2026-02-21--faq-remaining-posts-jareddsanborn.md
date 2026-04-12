# FAQ Deployment - Remaining Posts on jareddsanborn.com

**Date**: 2026-02-21
**Type**: operational + teaching
**Agent**: full-stack-developer
**Task**: Deploy FAQs to the last 2 published posts missing them on jareddsanborn.com

---

## Context

After the overnight 2026-02-20 session deployed FAQs to 10 posts (5 on purebrain.ai + 5 on jareddsanborn.com), two published posts on jareddsanborn.com were still missing FAQs:

| Post ID | Slug | Title |
|---------|------|-------|
| 998 | why-your-ai-should-have-a-name | Why Your AI Should Have a Name |
| 1045 | what-i-actually-do-all-day | What I Actually Do All Day |

## FAQ Content Matched

- **Post 998** → FAQ content from draft file "POST 1: How My Human Named Me" (5 Q&A pairs)
- **Post 1045** → Same FAQ content as purebrain.ai post 172 "What I Actually Do All Day" (6 Q&A pairs)

## Insertion Point for jareddsanborn.com Older Posts

These older posts do NOT have `<div class="blog-cta-block">` like purebrain.ai posts.

Structure at end of post:
```
[post body content]
<hr>
<p><em>Ready to meet your AI? <a href="...">...</a></em></p>
```

**Strategy**: Insert FAQ section BEFORE the final `<hr>` using `content.rfind("<hr>")`.

## Verification Results (REST API - WordPress DB)

- Post 998: 5 faq-section divs, FAQPage schema, FAQ before final hr ✓
- Post 1045: 6 faq-section divs, FAQPage schema, FAQ before final hr ✓

## Cache Issue (Known - Do Not Panic)

Live pages served cached HTML (Cloudflare HIT, 31-day TTL).
This is documented behavior. Data IS correctly saved in WordPress.
Cache clears when: Jared purges Cloudflare dashboard, or TTL expires.

## Scripts

- New script: `/home/jared/projects/AI-CIV/aether/tools/add_faqs_remaining_posts.py`
- Previous script (posts 565, 172): `/home/jared/projects/AI-CIV/aether/tools/add_faqs_to_posts.py`

## Complete FAQ State (2026-02-21)

### purebrain.ai (all 7 published posts have FAQs)
| ID | Slug | FAQs |
|----|------|------|
| 98 | how-my-human-named-me | 5 |
| 172 | what-i-actually-do-all-day | 6 |
| 316 | why-ai-memory-changes-everything | 5 |
| 373 | most-ai-agents-break... | 5 |
| 381 | ceo-vs-employee-ai-transformation-gap | 6 |
| 480 | why-your-ai-pilot-is-succeeding... | 6 |
| 565 | the-difference-between-using-ai... | 6 |

### jareddsanborn.com (all 8 published posts have FAQs)
| ID | Slug | FAQs |
|----|------|------|
| 998 | why-your-ai-should-have-a-name | 5 |
| 1039 | what-i-named-my-ai... | 5 |
| 1045 | what-i-actually-do-all-day | 6 |
| 1056 | why-ai-memory-changes-everything | 5 |
| 1060 | most-ai-agents-break... | 5 |
| 1065 | ceo-vs-employee-ai-transformation-gap | 6 |
| 1069 | ai-pilot-purgatory | 6 |
| 1074 | the-difference-between-using-ai... | 6 |

## Teaching: Audit Before Acting

The task brief said "remaining 4 posts" (381, 316, 373, 98) - but those were already done overnight.
ALWAYS do a live audit first before deploying:
```python
r = requests.get(f'{site}/wp-json/wp/v2/posts?context=edit&per_page=100&status=publish')
for post in r.json():
    has_faq = 'faq-section' in post['content']['raw']
```
This prevents re-running on already-deployed posts and reveals the actual current state.
