# AI Partnership Guide - Content Gate Fix

**Date**: 2026-03-11
**Type**: bugfix + audit
**Agent**: dept-systems-technology

## Problem

Content below the email form on `/ai-partnership-guide/` was fully visible without email submission. Sections 4-6 and the conclusion were readable for free.

## Root Cause

The `#guide-locked-content` div had `style="position:relative;overflow:hidden;"` but NO `max-height` set. Without a height constraint, `overflow:hidden` has no visible effect — the full content rendered below the gate.

The `#guide-lock-overlay` was only 180px tall (gradient fade at top), leaving everything below the fold completely clear.

## Task 2 Audit: Email Destination

**REST endpoint**: `POST /wp-json/purebrain/v1/guide-unlock`
- Registered by the `pb-lead-capture` plugin (purebrain/v1 namespace)
- Endpoint WORKS — returns `{"success":true,"message":"unlocked"}` on valid email
- Adds email to **Brevo list 3 (The Neural Feed)**
- Built in Feb 2026 (v4.1.0 work documented in full-stack-developer memory)
- Rate limited: 5 req/IP/min

**Status**: Email capture IS connected to Brevo. Working correctly.

## Fix Applied

Three changes to `_elementor_data` of page ID 405 (widget ID: 3ee3c06):

### 1. `#guide-locked-content` — added height + blur
```
Before: style="position:relative;overflow:hidden;"
After:  style="position:relative;overflow:hidden;max-height:320px;filter:blur(4px);user-select:none;pointer-events:none;"
```

### 2. `#guide-lock-overlay` — full coverage, opaque at bottom
```
Before: height:180px; gradient stops at 92% opacity
After:  top:0;left:0;right:0;bottom:0; gradient 0%→100% reaching rgba(8,10,18,1.0)
```

### 3. `doUnlock()` function — clears blur on reveal
```
Before: locked.style.overflow = 'visible'; locked.style.maxHeight = 'none';
After:  + locked.style.filter = 'none'; locked.style.userSelect = ''; locked.style.pointerEvents = '';
```

## Deployment Process

1. Updated `post_content` via REST API — NOT effective (Elementor renders from `_elementor_data`)
2. Fetched `_elementor_data` from `/wp-json/wp/v2/pages/405?context=edit`
3. Updated `settings.html` inside the single HTML widget element
4. Posted updated `_elementor_data` back via meta update
5. Called `DELETE /wp-json/elementor/v1/cache` to flush Elementor render cache
6. Purged Cloudflare full zone cache

## Key Lesson: Elementor Data vs Post Content

Per MEMORY.md rule — this was a perfect example. The REST API `content.raw` showed our changes but the live page didn't update until we updated `_elementor_data`. Always update `_elementor_data` for Elementor-rendered pages.

## Verification

14/14 checks passed on live page:
- max-height:320px applied
- filter:blur(4px) applied
- user-select:none applied
- pointer-events:none applied
- overlay bottom:0 full coverage
- overlay rgba(8,10,18,1.0) fully opaque
- doUnlock clears filter
- localStorage persist working
- REST endpoint wired
- Section 4 inside gated area
