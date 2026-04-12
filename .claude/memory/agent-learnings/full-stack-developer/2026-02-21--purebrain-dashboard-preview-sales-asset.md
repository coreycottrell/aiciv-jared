# PureBrain Dashboard Preview - Sales Asset

**Date**: 2026-02-21
**Type**: technique
**Topic**: Self-contained HTML sales/marketing dashboard mockup for purebrain.ai

## What Was Built

A 1,830-line single-file HTML dashboard preview at:
`/home/jared/projects/AI-CIV/aether/exports/purebrain-dashboard-preview.html`

Converts Jared's rough prototype (`docs/from-telegram/dashboard-preview 1.html`) into a premium, fully self-contained marketing asset.

## Key Architecture Decisions

### Single File, Zero Dependencies
- All CSS in `<style>` tags, all JS in `<script>` tags
- No external CDN links, no fonts loaded from network
- Falls back gracefully to system sans-serif stack
- Verified with grep: `CLEAN - no external dependencies`

### BEM-style Namespaced CSS (`.dp-` prefix)
- All classes prefixed with `dp-` (dashboard preview) to prevent Elementor conflicts
- Safe to embed in any WordPress HTML widget without style collisions
- CSS custom properties (`--pb-blue`, `--pb-orange`, etc.) for easy theming

### Responsive Strategy
- Desktop (>900px): Full browser chrome mockup with grid layout
- Tablet (640-900px): Simplified grid, right column goes below chat
- Mobile (<640px): `dp-mockup-wrapper` hidden, `dp-mobile-cards` accordion shown

### Tooltip System
- Positioned absolutely on `.dp-feature` containers
- Three position variants: default (below), `--left`, `--top`
- CSS-only show/hide via `:hover` and `:focus-within`
- Sales-focused copy: benefit-first, not feature description

## Sales Copy Approach
Tooltip titles follow a "value over feature" pattern:
- Chat: "Never repeat yourself again" (not "Chat Interface")
- Memory: "You stay in full control" (not "Memory Panel")
- Tasks: "Work gets done while you sleep" (not "Task Queue")
- Insights: "It gets smarter every day" (not "Learning Insights")
- Settings: "Truly yours - not a generic chatbot" (not "Settings")

## Animations
- `dp-pulse`: Pulsing dot for "AI typing" indicator, memory recall badge
- `dp-spin-slow`: Glow pulse for running task status
- `dp-bar-grow`: CSS keyframe for progress bar growth (resets via IntersectionObserver)
- Counter animation: JS `requestAnimationFrame` eased counter for memory count + insight number
- SVG sparkline: Trend line in insights panel with gradient fill

## PureBrain Branding Applied
- Blue (#2a93c1): Primary interactive elements, borders, active states, dots
- Orange (#f1420b): Accent (logo gradient reference only, not overused)
- Dark navy (#0d1117, #141c26, #1a2535): Background hierarchy
- Glass panels: gradient backgrounds + rgba borders + subtle inset glow on hover
- Browser chrome dots: macOS-style colored dots with glow shadows

## Gotchas / Lessons Learned

1. **Elementor conflict prevention**: The `.dp-` prefix is non-negotiable. Elementor injects global styles that override common class names.

2. **Tooltip z-index**: Tooltips need `z-index: 200` to appear above sibling `.dp-feature` panels. Parent panel needs `overflow: visible` (not `hidden`) or tooltips get clipped.

3. **Mobile accordion `hidden` attribute**: Using native HTML `hidden` attribute is correct. CSS `display: none` on `[hidden]` elements works, but the `max-height` animation requires removing `hidden` AND relying on `max-height` transition. Must remove attribute, not just toggle a class.

4. **IntersectionObserver for animations**: Progress bars and counters animate only when scrolled into view - much better UX than animating on page load when the element may be offscreen.

5. **SVG icons vs unicode**: Used inline SVG for nav icons instead of HTML entities. Much cleaner rendering across all browsers, matches modern SaaS aesthetic.

## Deployment Instructions
- Embed directly in Elementor HTML widget
- No WordPress plugin needed
- Set widget container to `width: 100%; overflow: hidden;`
- The section has its own `padding: 72px 24px 80px` - may need to zero out Elementor section padding to avoid double-padding
