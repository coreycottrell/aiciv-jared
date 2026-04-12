# Learning: Aether Footer v4.7.0 — PROMINENT Redesign

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: operational + teaching
**Topic**: Plugin wp_footer redesign — subtle gray bar to eye-catching advertisement

## What Was Changed

Upgraded the Aether footer credit bar from v4.6.0 (subtle, gray, 36px) to v4.7.0 (bold, 64px, orange glow).

**Before (v4.6.0)**:
- 36px height, 11px font
- Background #080a12 (near-black)
- AETHER in white (plain bold)
- Border-top: 1px solid rgba(255,255,255,0.06) — nearly invisible
- Text #6b7280 — muted gray

**After (v4.7.0)**:
- 64px height, 13px base font
- Background: linear-gradient(135deg, #0a0c14, #0d1120, #080c18)
- Border-top: 2px solid #f1420b — bright orange accent
- Box-shadow: orange glow below bar + blue trace
- AETHER: font-size 15px, font-weight 800, letter-spacing 0.12em, color #f1420b
- AETHER text-shadow: triple-layer orange glow (8px, 20px, 40px radii)
- AETHER pulse animation: opacity 1 → 0.75 → 1, 3s infinite
- Shimmer keyframe defined (available for future use)
- "Why Choose PureBrain?" is a styled pill button (border, bg, hover orange)
- Mobile: 52px height, CTA hidden on <600px
- Body padding-bottom: 64px (was 36px)

## Design Principles That Make It POP

1. **Orange accent border-top** — first thing eye catches when it enters view
2. **Glowing AETHER name** — text-shadow layers create depth, not flat text
3. **Pulse animation** — subtle breathing motion draws eye without distraction
4. **Gradient background** — subtle depth, not flat #000
5. **Pill CTA button** — "Why Choose PureBrain?" has hover state (orange fill + white text)
6. **Proper contrast**: white/light gray base text, orange for PureBrain.ai, blue for the others

## Plugin Location

`tools/security/purebrain-security/purebrain-security-plugin.php` (v4.7.0)

## Deploy Method

Standard Playwright + CodeMirror + WP REST cache bust.
Deploy script: `tools/security/deploy_plugin_v470_purebrain.py`

## Verification Results

8/8 checks on 4 pages (homepage, blog, blog post, calculator). All PASS.
- footer_div_present, footer_v470_css, aether_glow_animation, orange_border_top
- footer_height_64px, why_purebrain_cta, aether_bold_orange, page_loads

## Key Pattern: wp_footer is UNIVERSAL

The `add_action('wp_footer', ...)` hook fires on EVERY page WordPress renders —
pages, posts, archives, homepage, woocommerce, custom templates, everything.
No need to touch individual Elementor page data. One plugin change = ALL pages.
This is the correct approach for site-wide UI elements.

## CSS Architecture Notes

- Use `#pb-aether-footer .class` for high specificity without `!important` overuse
- `@keyframes` in the same `<style>` block as the component — self-contained
- `position: fixed; bottom: 0; z-index: 9999` = always visible, never scrolled away
- Mobile `@media` breakpoint in the same block — no extra CSS file needed
