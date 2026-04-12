# Blog Post Background Video Transparency Fix — Plugin v4.7.5

**Date**: 2026-03-01
**Agent**: dept-systems-technology (via full-stack-developer)
**Plugin version**: 4.7.5
**Status**: DEPLOYED AND VERIFIED

## What Was Fixed

Individual blog posts (body.single-post) had an opaque dark body background (#0a0a0f from
Additional CSS), which blocked the GIF overlay defined in body.single-post::before.
The blog listing page (/blog/, page-id-319) had been fixed in v4.7.4 to show the background
animation. This fix extends the same treatment to ALL single blog posts.

## Root Cause

Three-layer dark-bg enforcement in the plugin:
- Layer 1 (CSS priority 1): body dark by default, transparent exceptions listed
- Layer 2 (CSS priority 999): same, fires after Additional CSS so it WINS
- Layer 3 (JS DOMContentLoaded): forces inline style

Layer 3 already had `is_singular('post')` early return — blog posts were already exempt.
Layers 1 and 2 had `body.single-post` NOT in the transparent exceptions list.

The Additional CSS has:
- `body.single-post { background: #0a0a0f !important; }` — opaque body
- `body.single-post::before { background: url(...Pure-Brain-Vid-3.gif)...; opacity: 0.5; z-index: -2; }`

Layer 2 fires AFTER Additional CSS in the HTML head (verified via position check).
So Layer 2 adding `body.single-post` to transparent exceptions overrides Additional CSS.
html element stays dark (#080a12) — no orange/light color can leak through.

## Changes Made (v4.7.5)

### Layer 1 CSS (priority 1) — added body.single-post
```css
body.home, body.page-id-11, body.page-id-319, body.page-id-688,
body.page-id-689, body.page-id-987, body.single-post {
    background: transparent !important;
    background-color: transparent !important;
}
```

### Layer 2 CSS (priority 999) — added body.single-post
Same transparent exceptions block, now includes body.single-post.

### Layer 3 JS — NO CHANGE NEEDED
Already had `if ( is_singular( 'post' ) ) { return; }` — correct.

## Verification (CONFIRMED LIVE)

Checked 2 blog posts: /your-next-direct-report-wont-be-human/ and /we-both-wrote-this-post/
- [PASS] Layer 1: body.single-post in transparent exceptions
- [PASS] Layer 2: body.single-post in transparent exceptions
- [PASS] Layer 3 JS: NOT injected on single posts
- [PASS] Body class: single-post confirmed
- [PASS] Additional CSS: ::before GIF overlay still present
- [PASS] html element stays dark (#080a12) — no orange leak
- [PASS] Non-blog pages (e.g. ai-partnership-guide): Layer 3 JS still present (no regression)

## Deployment Method

Used the app password (FlFr2VOtlHiHaJWjzW96OHUJ) for wp-login.php form auth.
This worked even though it's technically an "app password" — GoDaddy's WP hosting
appears to accept it for the login form as well as REST API.

Script: /tmp/deploy_v475_blog_bg.py
Cookie jar saved to: /tmp/wp_cookies_v475.txt (valid ~14 days from 2026-03-01)

## Key Architecture Facts

- body.single-post::before GIF is in Additional CSS (NOT in plugin)
- Additional CSS loads BEFORE pb-dark-bg-layer2 in the HTML head
- So Layer 2 (priority 999) correctly overrides Additional CSS background
- The ::before pseudo-element renders behind the transparent body, showing the GIF
- opacity: 0.5 on the GIF gives the "shows through slightly" effect Jared wanted

## Files

- Plugin export: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v475-blog-bg-fix.php`
- Working base: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v473-bypass-fix.php` (now v4.7.5)
