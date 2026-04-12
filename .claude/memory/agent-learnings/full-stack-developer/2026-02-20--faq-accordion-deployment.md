# FAQ Accordion - Plugin v2.0.0 Deployment

**Date**: 2026-02-20
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Done

Added FAQ accordion behavior to all blog post FAQ sections on purebrain.ai via the security plugin (v2.0.0).

## Problem

FAQ sections on blog posts (added in previous session) were showing all questions + answers fully expanded at all times. Needed accordion behavior: collapsed by default, one-at-a-time expand/collapse with smooth animation.

## Solution

Added section `j` to `tools/security/purebrain-security-plugin.php` with:
- CSS: `.faq-answer` wrapper hidden via `max-height: 0`, revealed via `max-height: 600px` on `.faq-open`
- JS: `DOMContentLoaded` handler wraps `<p>` in `.faq-answer` div, attaches click handlers to `<h3>` triggers
- Deployed via existing Playwright plugin editor pattern (CodeMirror `setValue()`)

## FAQ HTML Structure in Posts

From memory `2026-02-20--blog-faq-implementation.md`:
```html
<div class="faq-section">
  <h3>Question text</h3>
  <p>Answer text</p>
</div>
```

The JS wraps `<p>` in a `<div class="faq-answer">` at runtime for animation support.

## Accordion Behavior Details

- All items start collapsed (questions visible, answers hidden via max-height: 0)
- Click `<h3>` to toggle
- One-at-a-time: clicking any item closes all others first
- Can click open item again to collapse it (toggle behavior)
- Smooth CSS transition: `max-height 0.35s ease` + `padding 0.25s ease`
- Blue chevron (SVG data-URI) rotates 180deg when open
- Active item gets blue left border: `border-left: 3px solid #2a93c1`
- Colors match PureBrain brand: blue #2a93c1, dark backgrounds

## Scoping

All CSS/JS scoped to `body.single-post .post-content .faq-section` so:
- Only loads on single blog post pages (`is_single()` PHP check)
- Only affects `.faq-section` divs inside `.post-content`
- Does NOT affect any other parts of the site

## Deployment Pattern

- Plugin file: `tools/security/purebrain-security-plugin.php`
- Deploy script: `tools/security/deploy_plugin_v200.py`
- Method: Playwright logs into WP Admin, opens Plugin Editor, CodeMirror `setValue()`, clicks Save
- Cache flush: GoDaddy flush URL found in options-general.php (wpaas_action=flush_cache)
- Verification: `urllib.request` fetch of live post + check for CSS/JS IDs in HTML

## Verification Results

Live post (purebrain.ai/ceo-vs-employee-ai-transformation-gap/):
- FAQ accordion CSS block present: YES
- FAQ accordion JS block present: YES
- `.faq-section` divs in content: YES (6 items)
- JS found 6 FAQ items on the page
- Screenshot confirmed all 6 collapsed (questions only visible)

## Files

- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` (v2.0.0)
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v200.py`
- Screenshot: `/home/jared/projects/AI-CIV/aether/exports/screenshots/plugin_v200_faq_live.png`

## Teaching: max-height Animation Pattern

CSS `height: 0 → height: auto` cannot be animated. The standard workaround is:
- Set `max-height: 0` (collapsed)
- Animate to `max-height: 600px` (expanded - set larger than max expected content)
- Combine with `overflow: hidden`
- The "ease" timing feels natural for accordion feel

The JS `<p>` wrapping is necessary because the `.faq-section` div itself has `overflow: hidden`, but the CSS targets `.faq-answer` for the height animation. Without wrapping, the raw `<p>` would need to be targeted directly, which is less robust.

## Posts Now with Accordion FAQs

All 6 posts (matching `2026-02-20--blog-faq-implementation.md`):
- Post 381: CEO vs Employee (6 FAQs)
- Post 316: Why AI Memory Changes Everything (5 FAQs)
- Post 373: AI Agents Break Moment You Ask (5 FAQs)
- Post 98: How My Human Named Me (5 FAQs)
- Post 480: AI Pilot Purgatory (6 FAQs)
- Post 172: (5 FAQs - ID from original FAQ deployment memory)
