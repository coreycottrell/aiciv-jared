# Gmail-Safe Welcome Email Template Rebuild

**Date**: 2026-04-16
**Type**: teaching
**Agent**: full-stack-developer

## What Was Done

Rebuilt the PureBrain welcome email template to be fully Gmail-compatible. Gmail strips `<style>` blocks, CSS gradients, `rgba()` colors, and `<a>` tag background colors.

## Gmail-Safe Email Rules (Reusable)

1. ALL styles must be inline (`style="..."` on every element)
2. Use `<table>` layout, never `<div>` flexbox/grid
3. Buttons: `<table><tr><td bgcolor="#color" style="background-color:#color;"><a style="color:#fff;">text</a></td></tr></table>`
4. No CSS gradients -- use solid colors only
5. No `<style>` blocks -- Gmail strips them entirely
6. Every text element needs explicit `color:` inline
7. Background colors: both `bgcolor=""` attribute AND `style="background-color:"` (belt + suspenders)
8. Images: absolute URLs, explicit `width`/`height` attributes, `alt` text
9. Font stacks inline on every text element
10. Max width 600px (email standard)
11. Use `role="presentation"` on all layout tables
12. `rgba()` not supported -- use hex colors only
13. MSO conditionals (`<!--[if mso]>`) only for Outlook-specific fixes

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/welcome-email-template-gmail-safe.html` -- new standalone template
- `/home/jared/projects/AI-CIV/aether/tools/agentmail_monitor.py` -- updated `_get_fallback_email_html()` and `send_welcome_email()`, added `_resolve_email_template()` helper

## Template Resolution Order

1. `tools/welcome-email-template-gmail-safe.html` (same dir as monitor, Gmail-safe)
2. `/tmp/welcome-email-template.html` (legacy primary)
3. `/tmp/magic-link-email-template.html` (legacy fallback)

## Placeholder Formats Supported

- `{HUMAN_FIRST}` / `{{HUMAN_FIRST_NAME}}` -- customer first name
- `{AI_NAME}` / `{{CIV_NAME}}` -- AI partner name
- `{MAGIC_LINK}` / `{{MAGIC_LINK}}` -- portal access URL
