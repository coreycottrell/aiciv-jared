# AI Migration Portal UI — 4-Step Self-Contained HTML

**Date**: 2026-02-23
**Type**: technique + operational
**Topic**: Built complete 4-step migration wizard as self-contained HTML — demo-ready, WP-safe

---

## What Was Built

`/home/jared/projects/AI-CIV/aether/exports/ai-migration-portal.html`

1937-line self-contained HTML file implementing the full AI Migration Portal spec.
Zero external dependencies. Works in Elementor HTML widget.

## Architecture

### Step 1: Connect Accounts
- Competitor detection via URL param `?from=chatgpt` (configurable)
- Drag-and-drop + click file upload zone
- File selected confirmation state with name + size
- Expandable "How to export" with tabbed instructions (ChatGPT / Claude)
- 4 secondary integration cards (Notion, HubSpot, Canva, Other) with Coming Soon badges
- Continue CTA

### Step 2: Review Import
- 3 removable import categories (conversations, custom instructions, GPT configs)
- Per-file upload group (shown only if file was uploaded in Step 1)
- Privacy note component (above CTA per spec)
- Remove/Restore toggle on each item (uses mig-removed CSS class + state tracking)

### Step 3: PureBrain Learns You (THE EMOTIONAL CORE)
- CSS animated PureBrain orb: breathing sphere + spinning ring with orbital dot
- Two orb states: `mig-orb-processing` (fast, intense) and idle (slow, calm)
- Progress bar with shimmer animation, non-linear speed (fast-slow-fast arc)
- 5 insight cards revealed sequentially via setTimeout tick loop
- 5-item checklist with active spinner → done checkmark transitions
- Status message updates throughout
- Auto-advances to Step 4 on completion with 1.2s pause

### Step 4: Guided First Tasks
- Migration Complete badge header
- 3-stat summary bar (conversations, patterns, date range)
- 3 personalized task cards with specific numbers from import data
- Each task card has "Start this task" button (API hook commented)
- Final CTA → triggers completion overlay

### Migration Complete Overlay
- Full-screen backdrop blur overlay
- Scale-in animation with checkmark pop
- Summary stats (conversations, patterns, connections)
- Dismiss to dashboard

## Key Implementation Patterns

### CSS WP Safety — All prefixed `mig-`
Every CSS class starts with `mig-` to avoid WordPress theme conflicts.
Variables scoped under `#mig-root` (not `:root` which WP can override).
Body background uses `!important` to override theme.

### Demo Simulation
`migRunLearningSimulation()` runs a 7-second ticker:
- Increments progress 0→100% with non-linear speed curve
- Triggers checklist items at % thresholds: [18, 36, 54, 72, 90]
- Reveals insight cards at % thresholds: [22, 40, 58, 76, 88]
- Updates status message every ~15%
- Auto-advances to Step 4 at 100% + 1.2s

### API Hooks (all clearly commented)
1. FILE UPLOAD: `fetch('/api/migration/upload', { method: 'POST', body: formData })`
2. PROCESSING STATUS POLL: `fetch('/api/migration/status')` with interval
3. START TASK: `window.location.href = '/purebrain?pre_prompt=' + encodeURIComponent(prompt)`
4. MARK COMPLETE: `fetch('/api/migration/complete', { method: 'POST' })`

### URL-Based Competitor Config
`?from=chatgpt` → shows ChatGPT branding
`?from=claude` → switches to Claude/Anthropic
`?from=gemini` → Gemini
`?from=other` → Generic

### State Object
```js
migState = {
  currentStep: 1,
  competitor: 'chatgpt',
  uploadedFile: null,     // File object
  removedItems: new Set(), // item IDs user removed
  migrationData: { ... }, // demo hardcoded, replace with API response
  migrationComplete: false
}
```

## CSS Orb Technical Details

The CSS orb (no WebGL, no canvas) achieves PureBrain glass look via:
- `radial-gradient` with multiple stops for sphere depth
- Multi-layer `box-shadow` for glow and inner shadow
- Breathing animation: `scale(1)` to `scale(1.06)` at 3.2s
- Processing state: 1.4s breathe + fast hue-shift animation
- Spinning ring with orbital dot via `::before` pseudo-element
- Blue color scheme: `#2a93c1` family

## Files Referenced
- Spec: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/ai-migration-portal-spec.md`
- Output: `/home/jared/projects/AI-CIV/aether/exports/ai-migration-portal.html`

## Design Decisions
- Chose CSS-only orb (not WebGL) for maximum WP compatibility
- All transitions 0.22s to feel snappy but not jarring
- Mobile stack: grid → 1-col, task cards → vertical layout at 600px
- Orange (#f1420b) for primary CTAs, blue (#2a93c1) for secondary/task buttons
- Insight cards use translateY(12px) → 0 with opacity 0 → 1 for natural pop-in
- `mig-check-active` shows rotating spinner (CSS animation) before `mig-check-done`
