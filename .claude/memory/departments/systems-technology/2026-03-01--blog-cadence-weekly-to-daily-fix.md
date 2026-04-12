# Blog Cadence Fix: "every week" -> "every day" on purebrain.ai

**Date**: 2026-03-01
**Type**: bulk-content-fix
**Agent**: dept-systems-technology

## What Was Fixed

4 of 15 blog posts contained CTA newsletter text saying "every week" when cadence is DAILY.

## Posts Fixed

| Post ID | Title | Change |
|---------|-------|--------|
| 1139 | Your AI Doesn't Work For You — You Work For It | "AI partnerships every week" -> "AI partnerships every day" |
| 1084 | AI Doesn't Make Your Team Smarter. It Makes the Gap Bigger. | "AI relationships every week" -> "AI relationships every day" |
| 966 | The First 90 Days of an AI Partnership | "AI relationships every week" -> "AI relationships every day" |
| 950 | Your AI Has No Memory. Mine Does. | "AI relationships every week" -> "AI relationships every day" |

## Posts Already Clean (11 posts)

879, 696, 631, 606, 565, 480, 381, 316, 373, 172, 98

## Patterns in CTA Block

The affected posts all had this pattern at the bottom CTA:

```html
subscribe to our newsletter</a> where I share insights on building AI [partnerships/relationships] every week.
```

Changed to: "...every day."

## Pattern: context=edit Required

WordPress REST API requires `?context=edit` to return `content.raw`. Without it, the content object does NOT have a `.raw` key - it only has `.rendered`.

## Elementor Cache

Cleared after all updates via:
```
DELETE https://purebrain.ai/wp-json/elementor/v1/cache
```
Returns HTTP 200 with empty body (success).

## LOCKED RULE

Blog posting cadence is DAILY. Any CTA, newsletter reference, or footer text saying "weekly" or "every week" in the context of blog/newsletter cadence is WRONG and must be corrected to "daily" or "every day".

Do NOT change general usage of "week" (e.g., "last week's news", "a five-week program").
