---
type: operational
topic: Email capture added to AI Tool Stack Calculator
date: 2026-03-21
---

# Calculator Email Capture — Implementation Record

## What Was Built

Added an email capture section to the AI Tool Stack Calculator page at:
`exports/cf-pages-deploy/ai-tool-stack-calculator/index.html`

## Feature Design

- Section appears below the tiers grid (inside `.calc-wrap` context, outside `</div><!-- /wrap -->` closing tag)
- Hidden by default (`display: none`), revealed via JS when user selects 3+ tools
- Dark theme matching existing page: `#080a12` bg, `--pb-blue` (#2a93c1) accents, gradient shimmer top border
- Form: email input + "Get My Audit" button (flex row, collapses to column on mobile <520px)
- Success state swaps in on submit (no page reload)
- Privacy note: "No spam. One email with your analysis."

## Trigger Logic

`maybeShowAuditCapture()` is called inside `refreshUI()` when `selectedTools.size >= 3`.
The `_auditCaptureFired` flag prevents re-triggering after the user has already seen it.

## Data Submitted

On submit, captures:
- User email
- Tool list with prices (from `selectedTools` + `findTool()`)
- Total monthly stack cost
- Recommended plan + savings
- Personal savings if entered
- Page URL

Payload sent to `https://api.purebrain.ai/api/investor-inquiry` with `type: 'calculator_audit_lead'`.
This reuses the existing investor inquiry endpoint which already notifies Jared.

## Why investor-inquiry endpoint

The calculator is a pure static CF Pages file — no server-side code available.
`api.purebrain.ai/api/investor-inquiry` accepts flexible message payloads and already has CORS enabled.
The `message` field carries the full stack audit data as structured text.

## Deployment

Deployed to `purebrain-staging` via:
```
CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true
```
Deployment URL: https://eeb47135.purebrain-staging.pages.dev
Live confirmation: `curl | grep calcAuditCapture` returned 10 matches.

## Files Changed

`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ai-tool-stack-calculator/index.html`
- +290 lines (CSS + HTML + JS)
- File went from 4808 → 5098 lines
