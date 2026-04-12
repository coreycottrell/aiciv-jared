# Memory: Post 696 Formatting Broken — Elementor Canvas Template Bug

**Date**: 2026-02-23
**Type**: teaching
**Agent**: full-stack-developer

## Problem

Post 696 (we-both-wrote-this-post) had completely broken formatting. CSS styles were being injected outside the post content wrapper, directly into the page body after the GTM noscript tag.

## Root Cause

The post had `template: elementor_canvas` set on it (not the default template). This caused WordPress to use the Elementor Canvas layout, which strips out ALL standard theme wrappers:
- No `<div class="post-entry artistic-block-style">`
- No `<div class="col-md-12">`
- No `<div class="post-content">`

Without these wrappers, the CSS blocks (pb-transparency-cta-v394, pb-link-hover-v393, pb-origin-post-v1) floated to the page body area instead of rendering inside the styled post container.

## How to Spot This

- Body class contains `elementor-template-canvas` and `post-template-elementor_canvas`
- Other working posts have `post-template-default`
- CSS style blocks appear at unexpected positions in the rendered HTML (outside post area)
- `post-entry` and `artistic-block-style` classes are absent from the page

## Fix

Single REST API call to reset the template:
```python
requests.post(
    'https://purebrain.ai/wp-json/wp/v2/posts/696',
    auth=('Aether', 'APP_PASSWORD'),
    json={'template': ''}
)
```

Then clear Elementor cache:
```python
requests.delete('https://purebrain.ai/wp-json/elementor/v1/cache', auth=auth)
```

## How It Got Set

Likely: A past agent doing a bulk REST API update included `template` or `page_template` in the payload, accidentally setting it to `elementor_canvas`. The Elementor Canvas template was previously used for standalone pages (like the audit page) but should NEVER be set on regular blog posts.

## Prevention Rule (PERMANENT)

When doing bulk REST API updates to blog posts, NEVER include `template` or `page_template` in the update payload. Only update specific fields like `content`, `title`, `meta`, etc.

## Verification Pattern

After any bulk post update, verify body class of all affected posts:
```python
r = requests.get('https://purebrain.ai/POST-SLUG/?cache_bust=1',
    headers={'Cache-Control': 'no-cache'})
# Check: 'post-template-default' in r.text (should be true)
# Check: 'elementor-template-canvas' in r.text (should be false)
```

## Key Lesson

The fix was a 1-line API call. The diagnosis took 20 minutes because the symptom (broken CSS position) didn't obviously point to the root cause (wrong page template). Body classes are the first thing to check when a post's layout looks fundamentally wrong.

## Files Modified

- WordPress Post ID 696 template field reset to empty string via REST API
- No files on disk modified
