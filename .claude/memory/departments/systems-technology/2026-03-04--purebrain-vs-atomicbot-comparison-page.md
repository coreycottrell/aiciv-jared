# Memory: PureBrain vs Atomicbot Comparison Page Build

**Date**: 2026-03-04
**Agent**: dept-systems-technology
**Type**: build | deployment | pattern

---

## What Was Built

A complete PureBrain vs Atomicbot comparison page, following the exact same design pattern as the existing comparison pages (vs GLBGPT, vs SiteGPT).

**Live URL**: https://purebrain.ai/purebrain-vs-atomicbot/
**WordPress Page ID**: 1257
**Local export**: /home/jared/projects/AI-CIV/aether/exports/purebrain-vs-atomicbot.html

---

## Atomicbot.ai Research Summary

- **Product type**: Desktop + web app wrapping OpenClaw (open-source AI agent framework)
- **Core value**: Task automation — email, calendar, browser clicks, file management, form filling
- **Free tier**: Full functionality but requires user to bring own API keys (Claude/GPT/Gemini developer accounts)
- **Paid tier**: Removes API key requirement — pricing NOT publicly disclosed on website
- **Integrations**: 100+ apps (Gmail, Slack, Trello, Discord, GitHub, Figma, WhatsApp, Signal)
- **Skill marketplace**: 700+ pre-built skills
- **Memory**: Preference and task pattern level — does NOT build strategic business intelligence
- **Target audience**: Technically capable users wanting productivity automation
- **Platform**: Mac available; Windows + iOS listed as "coming soon"
- **Open source**: Built on OpenClaw — code is transparent and auditable
- **Local execution**: Genuine on-device option for privacy

**Key differentiator from PureBrain**: Atomicbot executes tasks. PureBrain builds compounding business intelligence. Completely different categories.

---

## Design Pattern Used

Matched exactly to existing comparison pages. Key elements:
- ID: `#pb-vs-atomicbot` (scoped all CSS to this ID to prevent conflicts)
- Gradient strip at top: `linear-gradient(90deg, #e85d04 0%, #2a93c1 100%)`
- Sticky nav with PUREBR[AI]N logo
- Product cards side by side (hero)
- 4-stat compare strip
- Honest caveat box (orange left border)
- Where Atomicbot Wins (3-col cards, orange left border)
- Where PureBrain Wins (3-col cards, blue left border)
- Feature comparison table (20 rows)
- Real-world scenarios (6 cards, 2-col grid — new section not in GLBGPT page)
- Pricing comparison (2-col)
- Decision grid (who should choose which)
- CTA section
- Footer

**WordPress deployment**:
- Template: `elementor_canvas`
- Wrapped in `<!-- wp:html -->` block
- Auth: PUREBRAIN_WP_USER + PUREBRAIN_WP_APP_PASSWORD from .env
- API endpoint: https://purebrain.ai/wp-json/wp/v2/pages

---

## Key Positioning Decisions

1. **Honest about Atomicbot's strengths**: Browser automation, free tier, 700+ skills, open source, local execution — all credited fairly
2. **Clear category separation**: Automation tool vs business intelligence partner — framed up front so readers self-select
3. **Scenarios section added**: 6 real-world scenario comparisons show practical differences without being preachy
4. **Pricing transparency note**: Called out that Atomicbot does not publish paid tier pricing — factual, not a cheap shot
5. **"Free" cost caveat**: Noted that free tier still incurs API costs from the AI providers themselves

---

## Pipeline Followed

BUILD (full-stack by dept-systems-technology directly, no sub-delegation needed for HTML page) -> DEPLOYED -> VERIFIED (HTTP 201, live URL confirmed) -> TELEGRAM SENT

---

## Files

- HTML export: `/home/jared/projects/AI-CIV/aether/exports/purebrain-vs-atomicbot.html`
- Memory: This file
