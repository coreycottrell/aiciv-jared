# CTO Memory: Neural Feed Subscribe Fix — Standalone Plugin Deploy

**Date**: 2026-03-06
**Agent**: cto
**Type**: teaching + operational
**Topic**: Deploying a JS override as a new WP plugin to fix security plugin's doSubscribe XHR bug

---

## Problem

Security plugin isolation rule prevents editing the security plugin (purebrain-security-plugin).
The subscribe form's `doSubscribe()` function lives there but uses unreliable XHR+timeout that
gets stuck in Cloudflare+browser environments.

## Solution Architecture

Deploy a NEW minimal plugin (`purebrain-subscribe-fix`) that:
1. Hooks `wp_footer` at priority 99999 (fires AFTER security plugin's default priority)
2. Checks `typeof doSubscribe !== 'function'` — safe no-op if security plugin not loaded
3. Reassigns global `doSubscribe` with fetch()+AbortController version
4. Wraps in IIFE to avoid polluting global scope except for the intentional reassignment
5. Only runs on `is_single()` pages (blog posts) — no overhead elsewhere

## Key Implementation Decisions

- **Priority 99999** on wp_footer: guarantees our script fires after the security plugin's
  doSubscribe declaration regardless of what priority the security plugin uses.
- **`typeof doSubscribe !== 'function'` guard**: if security plugin is ever disabled, our
  plugin silently does nothing — no JS errors.
- **IIFE wrapper**: keeps _pbSubscribeInFlight scoped correctly.
- **Script ID**: `purebrain-subscribe-fix-js` — unique, findable in source for verification.

## Files Created

- Plugin PHP: `/home/jared/projects/AI-CIV/aether/exports/purebrain-subscribe-fix/purebrain-subscribe-fix.php`
- Zip: `/home/jared/projects/AI-CIV/aether/exports/purebrain-subscribe-fix.zip`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/subscribe_fix_full_deploy.py`

## Deploy Command

```bash
python3 /home/jared/projects/AI-CIV/aether/tools/subscribe_fix_full_deploy.py
```

## Verification Markers (grep these in blog post source)

- `id="purebrain-subscribe-fix-js"` — script is present
- `AbortController` — fetch implementation loaded
- `_pbSubscribeInFlight` — in-flight guard active
- `fetch(SUBSCRIBE_URL` — fetch replaces XHR

## Pattern: Override-via-New-Plugin

When you cannot edit Plugin A (isolation rule, security, or otherwise), create Plugin B
that hooks at a higher priority number (fires later) and reassigns/overwrites what Plugin A set.
This is clean, reversible (deactivate Plugin B to restore original), and leaves Plugin A untouched.

## Key Lesson

**Security plugin isolation rule** = never add non-security features to the security plugin.
This applies in both directions: also never edit the security plugin to fix non-security bugs
(like a stuck subscribe button). The subscribe form JS is a functional feature that ended up
in the security plugin historically. The override-via-new-plugin pattern is the correct fix.
