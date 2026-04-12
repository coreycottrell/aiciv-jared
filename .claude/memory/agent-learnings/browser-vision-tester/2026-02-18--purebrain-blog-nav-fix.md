# purebrain.ai/blog/ Navigation Fix

**Date**: 2026-02-18
**Type**: technique
**Agent**: browser-vision-tester

## Context

Investigated a reported hidden/broken navigation issue on purebrain.ai/blog/ (WordPress page ID 319).

## Root Cause Discovered

The `.blog-category-nav` div (category filter pills: For Individuals, For Teams, All Posts) was placed at the VERY BEGINNING of the page content - BEFORE the `<style>` block and BEFORE the main `<nav class="blog2-nav">` element.

This caused:
1. The category pills rendered at the very top of the page (position: static, no background styling)
2. The actual site nav (.blog2-nav) rendered below it at 95px from top instead of 0px
3. Users saw what appeared to be a confusing small unlabeled bar at the top

## What Playwright Inspection Revealed

- `nav.getBoundingClientRect().top` was 95.59px (not 0px) - key diagnostic signal
- The `.blog-category-nav` had `position: static; top: 20px; margin: 20px 0 32px`
- The main nav was there and visible, just not at the top

## Fix Applied

Moved `.blog-category-nav` from content start to inside `.blog-posts` section, after the `<h2 class="posts-heading">` tag. This places the category filter where it belongs - above the blog post list.

### WordPress REST API approach:
```python
auth = ('Aether', 'FlFr2VOtlHiHaJWjzW96OHUJ')
resp = requests.get('https://purebrain.ai/wp-json/wp/v2/pages/319?context=edit', auth=auth)
content = resp.json()['content']['raw']
# Surgical: find category-nav block, remove from top, insert after posts heading
update_resp = requests.post('https://purebrain.ai/wp-json/wp/v2/pages/319', auth=auth, json={'content': new_content})
```

## Verification Evidence

Before fix: `nav.getBoundingClientRect().top = 95.59`
After fix: `nav.getBoundingClientRect().top = 0`

Category nav moved from index 0 in content to index 20351 (after posts heading at 20295).

Click test: Clicking HOME link navigated to https://purebrain.ai/ successfully.

## Key Diagnostic Technique

When nav LOOKS hidden but CSS shows `display: flex; visibility: visible`:
- Check `getBoundingClientRect().top` - if not 0, something is pushing it down
- Check what elements render BEFORE the nav in the DOM
- Check `position: static` elements with margins above the sticky nav

## When to Apply

- Sticky nav not anchored at top despite correct CSS
- Nav visible but positioned lower than expected
- WordPress custom page content with multiple nav elements

## purebrain.ai WordPress Credentials (for reference)
- URL: https://purebrain.ai
- User: Aether
- App Password: FlFr2VOtlHiHaJWjzW96OHUJ
- Blog page ID: 319
