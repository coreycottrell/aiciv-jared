# Memory: Blog Format Check v2 - Post-Fix Audit (3 URLs)

**Date**: 2026-02-26
**Type**: teaching + operational
**Topic**: Post-fix visual audit: PB 90Days fixed, JDS 90Days is Divi-expected, list styling minor residual issue

---

## Task

After template fix to purebrain.ai/the-first-90-days-of-an-ai-partnership/, audit all 3 URLs:
1. PB 90Days (was broken, just fixed)
2. JDS 90Days (Jared says was fine before, now broken?)
3. PB Memory (reference GOOD post)

---

## Critical Findings

### PB 90Days: SUBSTANTIALLY FIXED
- Container is now `.post-content` (was `.pb-blog-content` - the bug is gone)
- Hero banner is back (featured image displays)
- H2: 36px, margin-top 36px, margin-bottom 25.2px - MATCHES GOOD reference exactly
- REMAINING ISSUE: `UL list-style: disc` (should be `none`), `padding-left: 20px` (should be `0px`)
  - Plugin's custom CSS rule `.post-content ul { list-style: none; padding: 0; }` not applying to this post
  - Could be: inline style override in post HTML, CSS specificity conflict, or stale cache

### JDS 90Days: NOT BROKEN - DIVI THEME EXPECTED DIFFERENCES
- Container: `.entry-content` (Divi standard - correct)
- H2: 26px (Divi default vs PB's 36px) - NOT a bug, just Divi theme
- LI color: rgb(229,231,235) gray (Divi default) - NOT a bug
- NO Featured Image set in WP post settings - no hero banner header
- Content, share section, Transparency Report all present and rendering correctly
- "Broken" claim may be: Featured Image was previously set and got cleared

### PB Memory (GOOD reference): PERFECT
- All CSS correct, hero present, H2 correct, lists: `list-style: none; padding: 0`

---

## Container Selector Pattern (re-confirmed)

```python
# Quick diagnostic
good_container = document.querySelector('.post-content, .entry-content')
bad_container = document.querySelector('.pb-blog-content')
# If bad_container found -> broken deployment
```

## H2 Style Comparison (definitive values)

| Property | PureBrain (correct) | Divi/JDS (their theme) |
|---|---|---|
| font-size | 36px | 26px |
| margin-top | 36px | 52px |
| margin-bottom | 25.2px | 0px |
| color | rgb(255,255,255) | rgb(96,165,250) blue |
| font-weight | 700 | 500 |

## UL/LI Style Comparison

| Property | PureBrain (correct) | Divi/JDS |
|---|---|---|
| list-style | none (brand) | disc (browser default) |
| padding-left | 0px | 14-20px |
| LI color | rgba(255,255,255,0.9) | rgb(229,231,235) |

---

## When to Apply

- After any blog template fix: check container, H2 margins, UL styling, hero banner
- JDS posts will ALWAYS look different from PB posts - Divi theme, not a bug
- If lists show disc markers on PB: suspect CSS specificity issue or cache, not container bug

---

## Files

- Screenshots: `exports/screenshots/blog-format-check-v2/` (9 screenshots)
- Report: `exports/screenshots/blog-format-check-v2/BLOG-FORMAT-CHECK-V2-REPORT.md`
- Data: `exports/screenshots/blog-format-check-v2/inspection_results.json`
