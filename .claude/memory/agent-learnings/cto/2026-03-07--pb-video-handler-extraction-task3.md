# CTO Memory: pb-video-handler Extraction (Task 3 of 14)

**Date**: 2026-03-07
**Type**: operational
**Topic**: Security plugin extraction — video handler standalone plugin

## What Was Done

Extracted the homepage video viewport handler from purebrain-security-plugin.php into a standalone plugin at:
`tools/security/pb-video-handler/pb-video-handler.php`

## Two Blocks Extracted

### Block 1: JS footer action (lines 520–605 in security plugin)
- `add_action( 'wp_footer', ...)` gated by `is_front_page()`
- Script tag id="pb-video-mobile-pause"
- Handles mobile z-index layering, living-background hiding, play/pause on visibilitychange
- Priority 20

### Block 2: CSS @media block (lines 1170–1190 in security plugin)
- Inside the large style tag for `pb-magic-cursor-body-override`
- `@media (max-width: 767px)` rules for `.video-background`, `.living-background`, `#content`, `.site-content`, `.elementor`
- NOTE: This is INSIDE a larger style tag — only the @media block plus its comment are removed, NOT the surrounding style tag

## Key Pattern for CSS Removal

The CSS @media block is embedded inside a much larger `<style>` output. The old_string for removal must be precise (comment + @media block only) so the rest of the style tag is untouched.

## File Produced

`/home/jared/projects/AI-CIV/aether/tools/security/pb-video-handler/pb-video-handler.php`
- Version: 1.0.0
- Plugin Name: PureBrain Video Handler
- wp_head action (priority 20) for CSS
- wp_footer action (priority 20) for JS, gated on is_front_page()

## Extraction Series Context

- Task 1: pb-301-redirects — complete, QA passed
- Task 2: pb-breadcrumb-fix — complete, QA passed
- Task 3: pb-video-handler — plugin created, edits documented
- Tasks 4-14: pending
