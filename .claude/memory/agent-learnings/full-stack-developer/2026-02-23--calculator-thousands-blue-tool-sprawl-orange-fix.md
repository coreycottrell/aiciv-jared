# Calculator Hero H1 Color Fix - Thousands Blue, Tool Sprawl Orange

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching
**File**: exports/ai-tool-stack-calculator-v3.html → WP page 777

## Problem

The calculator hero H1 had "Thousands" styled as `<em>` with CSS `.calc-hero h1 em { color: var(--pb-orange) !important; }` - making it ORANGE.

Jared's GOOD design (reference photos 233557/233603) shows:
- "Thousands" = BLUE (#2a93c1)
- "Tool Sprawl" = ORANGE (#f1420b)

The BAD version had both words as white (magic cursor poison overriding despite exclusion list).

## Root Cause

The `<em>` tag + magic cursor exclusion `.calc-hero h1 em` wasn't reliably excluding the element from the magic cursor poison override. CSS specificity + `:not()` complexity was the issue.

## Fix Applied

1. Changed `.calc-hero h1 em` CSS to use blue instead of orange
2. Added `.calc-hero h1 .blue { color: var(--pb-blue) !important; }`
3. Changed HTML from `<em>Thousands</em>` to `<span class="blue">Thousands</span>`
4. Updated magic cursor exclusion to add `:not(.calc-hero h1 .blue)`

## Result Pattern

```html
<!-- CORRECT hero H1 pattern -->
<h1>You're Probably Wasting<br><span class="blue">Thousands</span> on AI <span class="orange">Tool Sprawl</span></h1>
```

```css
/* Both color classes need explicit !important and magic cursor exclusion */
.calc-hero h1 .blue { color: var(--pb-blue) !important; }
.calc-hero h1 .orange { color: var(--pb-orange) !important; }
```

## Lesson

When magic cursor poison override is interfering with specific text colors, use explicit class names (`.blue`, `.orange`) rather than semantic HTML tags (`em`, `strong`). Class-based selectors are more reliable in the `:not()` exclusion list.

## Deployment

- Deployed to WP page 777 via REST API
- Wrapped in `<!-- wp:html -->` block (mandatory per MEMORY.md)
- Verified live: `<span class="blue">Thousands</span> on AI <span class="orange">Tool Sprawl</span>`
