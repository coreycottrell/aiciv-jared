---
type: technique
topic: PureBrain Blog Post Title Hover Color Fix - Orange to White
date: 2026-02-18
agent: browser-vision-tester
tags: [css, purebrain, hover, blog, post-title, rest-api, page-319, white]
confidence: high
---

# PureBrain Blog Post Title Hover Color - White Fix

## Context

Jared reported that blog post title pills/buttons on purebrain.ai/blog/ turn ORANGE on hover.
These are the clickable "Why AI Memory Changes Everything" style pill buttons.
They should turn WHITE on hover (not orange), as they're on a dark background.

## Root Cause

In the embedded style block (Style Block 1 - 15KB) in page 319 content, these rules exist:

```css
.blog-posts article h2 a:hover,
.wp-block-latest-posts__post-title:hover {
    color: #f1420b !important;
}

.related-post-title:hover {
    color: #f1420b;
}
```

These rules appear MULTIPLE TIMES in the original style block (3x each), all setting hover to orange.

## Post Title Selectors

- `.wp-block-latest-posts__post-title` - main blog post titles (pill/button style)
- `.blog-posts article h2 a` - alternative selector for same elements
- `.related-post-title` - "You Might Also Like" section post titles

These elements are `<a>` tags styled as pills with:
- background: linear-gradient(135deg, #2a93c1 0%, #1a7aa8 100%) - BLUE pill background
- padding: 12px 25px
- display: inline-flex
- color: #ffffff (white text)

## Solution

Appended to the EXISTING override <style> block at the end of page 319 content (Style Block 2):

```css
/* ========== POST TITLE HOVER FIX - Feb 18, 2026 ========== */
.blog-posts article h2 a:hover,
.wp-block-latest-posts__post-title:hover {
    color: #ffffff !important;
}

.related-post-title:hover {
    color: #ffffff !important;
}
/* ========== END POST TITLE HOVER FIX ========== */
```

## Why This Works (CSS Cascade)

Both conflicting rules use `!important`. The LATER rule in the document wins when both have
equal specificity. Since Style Block 2 (our override) comes AFTER Style Block 1 (original),
our white color wins over the original orange.

## Verification

Computed color during hover: `rgb(255, 255, 255)` (WHITE) - confirmed via Playwright.

Card hover effects that remain orange (intentional - adds visual feedback):
- Card border: `rgba(241, 66, 11, 0.5)` - orange glow on card border
- Card box-shadow: includes `rgba(241, 66, 11, 0.1)` orange ambient
- Card transform: `translateY(-5px)` - card lifts up

The TITLE TEXT itself stays WHITE. The card BORDER can stay orange (it's a subtle glow effect).

## REST API Update Pattern

```python
import requests
auth = ("Aether", "FlFr2VOtlHiHaJWjzW96OHUJ")
resp = requests.get("https://purebrain.ai/wp-json/wp/v2/pages/319?context=edit", auth=auth)
content = resp.json()["content"]["raw"]

# Find last </style> and insert before it (adds to existing override block)
last_style_close = content.rfind("</style>")
new_css = "\n/* your css here */\n"
new_content = content[:last_style_close] + new_css + content[last_style_close:]

requests.post("https://purebrain.ai/wp-json/wp/v2/pages/319", auth=auth, json={"content": new_content})
```

## Files

- Screenshots: /tmp/purebrain-hover-fix-2026-02-18/
- Key: 08_card_normal_WIDE.png (orange pill, white text)
- Key: 09_card_hover_WIDE.png (blue pill with white text on hover, card border orange)

## When to Apply

- Any time hover colors need changing on the blog listing page
- Always insert into the LAST </style> block in page 319 (the override block)
- Never modify Style Block 1 (the 15KB original) - just override in Block 2
- The pattern: later !important beats earlier !important at same specificity

---

**Tags**: css, wordpress, purebrain, hover, post-title, white, blog-listing, page-319
