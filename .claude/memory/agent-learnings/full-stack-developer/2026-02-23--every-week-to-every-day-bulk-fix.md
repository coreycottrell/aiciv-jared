# Memory: Bulk Newsletter CTA Text Fix - "every week" → "every day"

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer

## Task
Replace "every week" with "every day" in newsletter subscribe CTA section across all purebrain.ai blog posts.

## Pattern
- Newsletter CTA text: `subscribe to our newsletter</a> where I share insights on building AI relationships every week.`
- Target change: `every week` → `every day`
- Post 696 was already fixed before this session

## What Was Done
1. Fetched all 10 published posts via `GET /wp-json/wp/v2/posts?per_page=100&status=publish&context=edit`
2. Scanned `content.raw` for "every week" (case-insensitive)
3. Found 9 affected posts (696 was already clean)
4. Used `re.sub(r'every week', replace_case, raw, flags=re.IGNORECASE)` with case-preserving lambda
5. PUT updates via `POST /wp-json/wp/v2/posts/{id}` with `{"content": new_raw}`
6. Verified all 10 posts clean via re-fetch

## Posts Fixed
| ID | Slug | Instances Replaced |
|----|------|--------------------|
| 631 | the-ai-trust-gap | 1 |
| 606 | why-95-percent-of-ai-pilots-fail | 1 |
| 565 | the-difference-between-using-ai-and-having-an-ai-partner | 2 |
| 480 | why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time | 1 |
| 381 | ceo-vs-employee-ai-transformation-gap | 1 |
| 316 | why-ai-memory-changes-everything | 2 |
| 373 | most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2 | 1 |
| 172 | what-i-actually-do-all-day | 1 |
| 98 | how-my-human-named-me-and-what-it-meant | 1 |

## Technical Notes
- Auth: Aether + PUREBRAIN_WP_APP_PASSWORD (FlFr2VOtlHiHaJWjzW96OHUJ)
- WP REST endpoint: POST (not PUT) for updating existing posts
- No additional cache busting needed - WP REST API handles it
- Case-preserving replacement not needed in practice (all lowercase in content)
