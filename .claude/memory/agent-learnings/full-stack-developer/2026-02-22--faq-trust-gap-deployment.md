# FAQ Deployment: Trust Gap Post (2026-02-22)

**Date**: 2026-02-22
**Agent**: full-stack-developer
**Type**: operational

---

## Summary

Deployed FAQ sections with JSON-LD FAQPage schema to the Trust Gap blog post on both sites.

- **purebrain.ai ID=631**: the-ai-trust-gap — 6 FAQs inserted before blog-cta-block
- **jareddsanborn.com ID=1122**: the-ai-trust-gap — 6 FAQs appended at end (stub post)

Both verified via REST API re-fetch. Elementor cache cleared on PB.

---

## Audit First Pattern (Confirmed Again)

Memory search revealed prior sessions had already deployed FAQs to all other posts.
The live audit confirmed only 2 of 19 total posts needed FAQs (the new Trust Gap post + its JDS mirror).

**Always run the audit script before deploying — prevents duplicate injections.**

Audit command:
```python
r = requests.get(f'{base_url}/posts?context=edit&per_page=100&status=publish', headers=headers)
for p in r.json():
    has_faq = 'faq-section' in p['content']['raw'] or 'FAQPage' in p['content']['raw']
```

---

## Final State After This Session

### purebrain.ai (9/9 posts have FAQs)

| ID  | Slug                                   | FAQ Divs |
|-----|----------------------------------------|----------|
| 631 | the-ai-trust-gap                       | 1 (NEW)  |
| 606 | why-95-percent-of-ai-pilots-fail       | 6        |
| 565 | the-difference-between-using-ai...     | 6        |
| 480 | why-your-ai-pilot-is-succeeding...     | 6        |
| 381 | ceo-vs-employee-ai-transformation-gap  | 6        |
| 316 | why-ai-memory-changes-everything       | 5        |
| 373 | most-ai-agents-break...                | 5        |
| 172 | what-i-actually-do-all-day             | 6        |
| 98  | how-my-human-named-me...               | 5        |

### jareddsanborn.com (10/10 posts have FAQs)

| ID   | Slug                                   | FAQ Divs |
|------|----------------------------------------|----------|
| 1122 | the-ai-trust-gap                       | 1 (NEW)  |
| 1092 | why-95-percent-of-ai-pilots-fail       | 6        |
| 1074 | the-difference-between-using-ai...     | 6        |
| 1069 | ai-pilot-purgatory                     | 6        |
| 1065 | ceo-vs-employee-ai-transformation-gap  | 6        |
| 1056 | why-ai-memory-changes-everything       | 5        |
| 1060 | most-ai-agents-break...                | 5        |
| 1045 | what-i-actually-do-all-day             | 6        |
| 1039 | what-i-named-my-ai...                  | 5        |
| 998  | why-your-ai-should-have-a-name         | 5        |

---

## JDS Post 1122 Was a Stub

JDS ID=1122 only contained style blocks + `<p>test-patch-check</p>`. No real article content.
It has NO blog-cta-block and NO `<hr>` — so the FAQ was appended at the end.
The FAQ was deployed successfully, but this post needs the full Trust Gap article content added.

---

## Script

`/home/jared/projects/AI-CIV/aether/tools/add_faqs_trust_gap.py`

Insertion priority:
1. Before `<div class="blog-cta-block"` (PB standard)
2. Before final `<hr>` (JDS older posts)
3. Append at end (fallback for stub posts)

---

## Trust Gap FAQ Content

6 Q&A pairs covering:
1. What is the AI trust gap?
2. Why don't organizations trust AI for strategic decisions?
3. What is AI pilot purgatory and how does it relate to trust?
4. How do you build trust with an AI system over time?
5. Is the AI trust gap really a bigger barrier than technology limitations?
6. What's the difference between testing AI capability and building AI trust?
