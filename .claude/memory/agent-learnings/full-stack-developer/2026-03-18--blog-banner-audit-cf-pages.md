# Blog Banner Audit - CF Pages Site

**Date**: 2026-03-18
**Type**: operational
**Task**: Full audit of all blog post banners on CF Pages site

---

## Summary

Audited all 31 blog post banners deployed at `/exports/cf-pages-deploy/blog/*/banner.*`.

## Key Finding: Only ONE banner is definitively WRONG

`the-ai-trust-gap/banner.jpg` was showing an "Automation vs Strategy" concept image (completely wrong for the "AI Trust Gap" post). Replaced with correct TRUST GAP imagery from Google Drive.

## Fix Applied

- Post: `the-ai-trust-gap`
- Old: `banner_WRONG_BACKUP.jpg` (1280x720 JPEG showing "Automation vs Strategy" - wrong concept)
- New: 1920x1080 JPEG from Google Drive "AI Trust gap" folder, "the AI trust gap 2.png"
- Drive file ID: `1xcOpKWrGzdTgbzJCIN0i4kGWLuTSii0-`

## WordPress API Status

WP still at `purebrain.ai` but REST API returns CF Pages HTML (WAF blocks it).

## Google Drive as Source of Truth

Blog bundle folder: `1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv`
All original approved banners in subfolder per post.

## Style Variations (Jared Needs to Decide)

| Post | Deployed | Drive | Notes |
|------|----------|-------|-------|
| `the-context-tax` | Orange/flashy 1280x720 | Dark clean 1200x630 | Same stats, diff style |
| `prompting-is-dead` | Typewriter style | Retro computer style | Different approach |
| `the-age-of-ai-agents` | Infographic | Clean hexagon (overnight) | Need decision |

## Confirmed Matching Drive Originals (OK)

52-billion, age-of-ai-agents-next-18-months, something-big, the-ai-that-forgets-you, teach-your-ai, what-i-actually-do-all-day, how-my-human-named-me, the-difference, your-ai-has-no-idea-who-you-are, ceo-vs-employee
