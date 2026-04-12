# Governance Architecture Deep Dive Page

**Date**: 2026-03-15
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Complete investor/partner-facing HTML page at `/governance/` answering 5 architecture questions
from Aether's perspective. Replaced existing governance page (which covered Governance Spine topic)
with a new architecture deep-dive oriented toward investor/partner due diligence.

## Key Patterns Used

- **Brand colors**: `#080a12` bg, `#2a93c1` PT Blue, `#f1420b` PT Orange — locked in as standard
- **Font stack**: Oswald for headings, Inter for body — import via Google Fonts
- **PureBrain logo**: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-1.png`
- **Logo text HTML**: `<span class="blue">PUREBR</span><span class="orange">AI</span><span class="blue">N</span>`

## Page Structure

1. Fixed nav with scroll effect
2. Hero with badge + stats row (30+ agents, 64+ skills, 15+ depts, 6,323+ invocations)
3. Page layout: 220px sticky TOC sidebar + main content (collapses on mobile <1080px)
4. Q1–Q5 as full sections with alternating bg (`#080a12` / `#0d1120` / `#111827`)
5. Comparison table (Orchestration Layer vs Aether Architecture)
6. Sister CIVs section (A-C-Gee with link + Witness)
7. CTA block + footer

## Deployment

- File: `exports/cf-pages-deploy/governance/index.html`
- Deploy: `CLOUDFLARE_API_TOKEN=$CF_PAGES_TOKEN npx wrangler pages deploy exports/cf-pages-deploy --project-name=purebrain-staging --branch=main --commit-dirty=true`
- CF cache purge: CF_PAGES_TOKEN is scoped pages-only — does NOT have zone-level cache purge. Need full CF API token for cache purge.

## Anti-Patterns Found

- The `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ZONE_ID` env vars are NOT in `.env` — only `CF_PAGES_TOKEN` exists. Cache purge always requires a zone-capable token stored elsewhere.
