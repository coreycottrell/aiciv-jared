# Memory: Aether Transparency Section - Plugin v3.6.0

**Date**: 2026-02-21
**Type**: operational
**Topic**: WordPress plugin feature - Aether Transparency Section auto-injection

---

## What Was Built

Added the Aether Transparency Section to the PureBrain Security Plugin (bumped from v3.5.0 to v3.6.0).

### New Files Modified
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` (v3.6.0)
- `/home/jared/projects/AI-CIV/aether/tools/update_transparency_data.py` (new helper)

### Architecture Pattern Used
Same pattern as existing lead capture (v3.5.0):
1. `wp_head` hook (priority 30, `is_single()` only) — injects CSS only if data exists
2. `wp_footer` hook (priority 28, `is_single()` only) — renders HTML + JS injection
3. JS finds `.blog-cta-block` and inserts transparency section immediately before it
4. Fallback chain: `.blog-cta-block` → after `.post-content` → before `#purebrain-legal-footer`

### Data Storage
- wp_option key: `purebrain_transparency_data` (JSON string)
- Third argument to `update_option()` is `false` (no autoload - not needed on every page)
- Read with `get_option('purebrain_transparency_data', '')` — empty string is falsy

### REST Endpoint
- Route: `POST /wp-json/purebrain/v1/transparency-data`
- Auth: `manage_options` capability (admin only)
- Callback: `purebrain_update_transparency_data()`
- Returns: `{ success: true, week_of, updated_at, rows }`

### Graceful Fallback
CSS hook checks `get_option` early and returns if empty — no empty `<style>` tag injected.
HTML render hook does the same — zero DOM changes if option is missing.

## Key Design Decisions

1. **CSS only injected if data exists**: Checked in `wp_head` hook before outputting the `<style>` block. This prevents dead CSS on pages with no transparency data.

2. **HTML wrapped in display:none div**: The transparency section is rendered inside `<div id="pb-transparency-section" style="display:none;">` then JS moves the inner `.aether-transparency` div to the correct DOM position. The wrapper is then removed. This avoids visible flash of content in wrong position.

3. **Priority 28 for wp_footer**: Lead capture runs at priority 25, nav menu at default (10). Priority 28 sits between them cleanly.

4. **Animation keyframe namespaced**: Used `pb-transparency-pulse` instead of `pulse-dot` from the template to avoid collision with any other animations using that keyframe name.

5. **`manage_options` not `edit_posts`**: Transparency data is site-level configuration (not per-post), so `manage_options` is the correct capability. Other endpoints use `edit_posts` for post-meta changes.

## Helper Script Patterns

- Uses only stdlib (`urllib.request`, `json`, `base64`, `pathlib`) — no pip dependencies
- Reads `.env` from project root (two levels up from `tools/`)
- Supports both `--file JSON_FILE` and individual CLI args (mutually exclusive group)
- `--dry-run` flag prints payload without posting
- `--site` flag to target one site or both
- Returns exit code 1 if any site fails

## What to Watch For

- If the transparency section appears in the wrong position, check that `.blog-cta-block` exists in the DOM. If the theme changes this class, update the JS selector.
- The `updated_at` field is stored in the option so Aether can verify when data was last refreshed.
- The CTA button always links to `home_url('/#awakening')` regardless of current page — consistent with the CTA LINK RULE in MEMORY.md.
