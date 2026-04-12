# Memory: Migration Exodus Quiz — Standalone HTML Component

**Date**: 2026-02-23
**Type**: operational + teaching
**Agent**: full-stack-developer
**Topic**: Self-contained 4-question migration quiz demo page for PureBrain exodus pages

---

## What Was Built

Standalone HTML quiz component for PureBrain's exodus landing pages. Shows the 4 migration
intelligence questions (A-D from the Migration Portal spec), plus email capture gate and success
screen. All Brevo integration wired in.

**File**: `/home/jared/projects/AI-CIV/aether/exports/migration-exodus-quiz.html`

---

## Architecture Decisions

### Scoped Under `#pb-migration-quiz`

ALL CSS is scoped under `#pb-migration-quiz { }` to avoid conflicts when injected into
existing WordPress pages that already have styles. This was the critical lesson from the
HTML-to-WordPress conversion work (see `2026-02-21--audit-interactive-form-wp-deploy.md`).

### Single JS IIFE Pattern

Entire JS wrapped in `(function() { 'use strict'; })()` to avoid global scope pollution.
Exposes `window.pbMigrationQuiz` object for parent page integration.

### Parent Page Integration Interface

```javascript
// Read current state from parent page
var data = window.pbMigrationQuiz.getState();
// {
//   currentStep: 4,
//   answers: {
//     primary_use_cases: ['writing', 'research'],
//     usage_frequency: 'multiple_times_daily',
//     had_custom_config: 'fully_customized',
//     main_frustration: 'no_memory'
//   },
//   email: 'user@example.com',
//   firstName: 'Jane'
// }

// Hook into completion
window.pbMigrationQuiz.onComplete = function(data) {
  // fires after Brevo submit succeeds
};
```

---

## Question Flow

```
Step 0: Q-A (multi-select chips) — Primary use cases
Step 1: Q-B (single-select)     — Usage frequency
Step 2: Q-C (single-select)     — Customization level
Step 3: Q-D (single-select)     — Main frustration
Step 4: Email gate              — Name + email capture
Step 5: Success screen          — Data captured preview + CTA
```

### Navigation
- Forward: "Continue →" button (disabled until selection made)
- Back: "← Back" button on every step (hidden/invisible on step 0)
- Skip: not available — all 4 questions are required for migration profile

---

## Brevo Integration

Submits to `POST https://api.brevo.com/v3/contacts` with:
- `updateEnabled: true` (upsert — handles re-submissions)
- `listIds: [3]` (Neural Feed)
- `tags: ['migration-intent', 'from-{competitor}']`
- Attributes: `PRIMARY_USE_CASES`, `USAGE_FREQUENCY`, `HAD_CUSTOM_CONFIG`, `MAIN_FRUSTRATION`, `COMPETITOR`, `MIGRATION_INTENT`

**Error handling**: API errors are caught and logged but do NOT block the user flow.
The success screen shows regardless of Brevo API status. This is intentional — don't
penalize the user for a Brevo network hiccup.

**API key placeholder**: `BREVO_API_KEY_HERE` — must be replaced before production deploy.
For WordPress injection, switch to AJAX proxy pattern (see `2026-02-19--brevo-newsletter-subscription-system.md`)
to avoid exposing the key client-side.

---

## Competitor Name Detection

Reads from URL slug:
```javascript
var match = path.match(/(?:switching-from-|vs-|purebrain-vs-)([a-z0-9-]+)/i);
```

Supports: chatgpt, claude, gemini, copilot, custom-gpts, deepseek, perplexity, jasper.
Falls back to "ChatGPT" if no match (default for demo page).

---

## Progress Indicator

Dual pattern used:
1. Thin progress bar (gradient: blue → orange) with percentage fill
2. Five dots (4 questions + email gate step) — active=orange, done=blue

---

## CSS Patterns

- Multi-select chips: `.mq-chips` + `.mq-chip` with checkmark reveal on `.selected`
- Single-select: `.mq-options` + `.mq-option` (button elements, not input[radio])
- Transition between steps: `@keyframes mq-fadein` slide-in from right
- All CSS variables use `--pb-` prefix (blue, orange, dark, dark2, dark3, border)

---

## Accessibility

- Chip group: `role="group"` with `aria-label`
- Radio-style options: `role="radiogroup"` + `role="radio"` + `aria-checked`
- Error messages: `role="alert"` for screen reader announcement
- Keyboard support: Enter/Space on chips and options triggers click
- Tab order: natural document flow

---

## Mobile Breakpoints

- 600px: padding reduced, font sizes shrink, gate box padding compressed
- 400px: chip font/padding reduced further for small phones

---

## Integration with Existing Exodus Pages

The exodus pages (deployed 2026-02-23, see previous memory) already HAVE these questions
injected via Python scripts. This standalone file is the demo/development version that can
also be used as a standalone landing page separate from the existing exodus page quiz flow.

For injecting into a new page: copy the `#pb-migration-quiz` div + the `<style>` block +
the `<script>` block. No external dependencies.

---

## Files

- Component: `/home/jared/projects/AI-CIV/aether/exports/migration-exodus-quiz.html`
- Spec source: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/ai-migration-portal-spec.md` (Section 2)
- Related exodus pages: WordPress IDs 752-760 (see `2026-02-23--exodus-migration-quiz-update.md`)
