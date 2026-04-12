# Memory: Brainiac AI Training Snippets Implementation

**Date**: 2026-03-12
**Type**: teaching
**Agent**: full-stack-developer

## What Was Built

Added collapsible AI Training Snippets to the Brainiac Mastermind Training page (`exports/cf-pages-deploy/brainiac-mastermind-training/index.html`).

## Structure

- Two snippet blocks added as `<div class="ai-snippet-wrap" data-ai-training="module-N">` placed between each live module card in the static `.modules-grid` section
- Each snippet has a toggle button (collapsed by default) with `aria-expanded` for accessibility
- Content is fully present in DOM even when collapsed — AI agents can scan without expanding
- Hidden `<div id="ai-training-manifest">` at bottom with JSON metadata for AI routing

## Content Pattern Per Snippet

1. Meta bar (AI-Optimized pill, date, duration)
2. Two-column grid: Core Concepts (bullet list) + Key Techniques (numbered list)
3. Implementation Checklist (checkbox list) — actionable items for AI to run with user
4. Key Quotes section (blue left-border blockquotes with attribution)

## JS Pattern

`toggleSnippet(btn)` function:
- Toggles `.expanded` class on button and body sibling
- Updates `aria-expanded` attribute
- Exposed to `window.toggleSnippet` for inline onclick handlers

## CSS Classes

- `.ai-snippet-wrap` — grid-column spanning wrapper
- `.ai-snippet-toggle` / `.expanded` — toggle button state
- `.ai-snippet-body` / `.expanded` — collapsible content
- `.snippet-col-grid` — 2-col responsive grid (collapses to 1 col at 720px)
- `.snippet-block` — content block with styled ul/ol
- `.snippet-checklist` — checkbox-prefixed list
- `.snippet-quotes` — quote collection with left-border styling
- `.smp-ai` / `.smp-date` / `.smp-dur` — meta pill color variants

## Module Placement

- Module 1 snippet: placed immediately after Module 1 `.module-card` div, before MODULE 2 comment
- Module 2 snippet: placed immediately after Module 2 `.module-card` div, before MODULE 3 comment
- Both snippets are `grid-column: 1 / -1` so they span full grid width

## AI Manifest

Hidden div `#ai-training-manifest` with `data-ai-scannable="true"` at bottom of body. Contains `<script type="application/json">` with full module metadata including: id, title, date, duration, themes, frameworks, implementation item count, file paths.

## Deployment

- CF Pages project: `purebrain-staging` (branch: main)
- Deployed URL: https://fa2b1465.purebrain-staging.pages.dev
- CF cache purged for purebrain.ai zone (ID: 49400cad1527af716705f6cb8c22bb65)
- Zone lookup: `CF_GLOBAL_API_KEY` + email works for API auth; the hardcoded zone ID `97f10e7e3e498f15799a81fe3da61592` in CLAUDE.md does not match purebrain.ai

## Gotcha: CF Zone ID

The zone ID `97f10e7e3e498f15799a81fe3da61592` referenced in CLAUDE.md instructions does NOT match purebrain.ai. Correct zone ID for purebrain.ai is `49400cad1527af716705f6cb8c22bb65`. Found via API zone lookup.

## Password Gate Bypass

The `?bypass=portal` parameter check at top of `init()` IIFE was preserved intact. Password is `brainiac2026` — unchanged.
