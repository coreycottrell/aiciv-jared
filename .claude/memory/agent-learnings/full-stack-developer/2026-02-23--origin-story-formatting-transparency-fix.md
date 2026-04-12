# Origin Story Blog Fix - Formatting & Transparency Section

**Date**: 2026-02-23
**Type**: operational, teaching
**Posts Fixed**: purebrain.ai Post 696, jareddsanborn.com Post 1180

---

## Root Cause Analysis: "Formatting is all off"

### What was wrong

Post 696 was published WITHOUT the standard plugin CSS blocks that all other posts have:
- `<style id="pb-transparency-cta-v394">` — CTA button white text fix
- `<style id="pb-link-hover-v393">` — in-text link hover (orange → white on hover)

These CSS blocks are normally injected by the purebrain-security plugin into ALL posts via a content filter. Post 696 was published before or separately from that filter applying.

Additionally, post 696 had an ANONYMOUS `<style>` tag (no `id=` attribute) with `.pb-origin-post a` rules that conflicted with the plugin's `.pb-origin-post a` rules injected later.

### Fix applied

1. Added `<style id="pb-transparency-cta-v394">` at top — same CSS as other posts
2. Added `<style id="pb-link-hover-v393">` — extended to include `.pb-origin-post a` selectors
3. Changed anonymous `<style>` to `<style id="pb-origin-post-v1">` and removed conflicting `a` link rules (now handled by v393)

### Key pattern

**When a post is "formatted differently" from other posts**: First check if it has the plugin CSS blocks at top. Posts without `pb-transparency-cta-v394` or `pb-link-hover-v393` style IDs are missing plugin injection. Fix by adding those CSS blocks to the post content directly.

---

## Transparency Section Update Pattern

### What was wrong

Old transparency section used:
- `blog-transparency-section` class with simple "How this post was made" text
- No stats/data, just description

### Fix applied

Replaced with a full stats section showing Feb 22 daily recap data:
- Stats table with 7 metrics (AI hours, founder hours, tasks, agents, lines of code, security fixes, value)
- Work breakdown as styled list with 8 categories
- "How this post was made" description preserved above the stats
- NO proper names (rule compliance: "founder" not "Jared", role titles not agent names)

### Data source

`/home/jared/projects/AI-CIV/aether/exports/daily-recap-2026-02-22.md`

---

## Deployment Pattern

For posts with custom HTML (not pure Elementor):
1. `curl -X POST wp-json/wp/v2/posts/{id}` with JSON payload
2. `curl -X DELETE wp-json/elementor/v1/cache` after
3. Both PureBrain (Post 696) and JDS (Post 1180) need updating simultaneously
4. Verify: re-fetch the live page, check for key CSS IDs and content

## Credentials

- purebrain.ai: `Aether:FlFr2VOtlHiHaJWjzW96OHUJ`
- jareddsanborn.com: `AetherPureBrain.ai:u3GO 3dvG rUqG 3QgM EYqd 8KfP`

## False positive warnings for verification

When checking live pages, these items appear from OTHER page elements (not post content):
- `v2.9.0` — appears in plugin CSS comments in `<head>` (not content)
- `3D mastery sprint` — appears in the SITE-WIDE transparency section widget in page footer
- When scoping checks, target `<div class="blog-transparency-section"` specifically
