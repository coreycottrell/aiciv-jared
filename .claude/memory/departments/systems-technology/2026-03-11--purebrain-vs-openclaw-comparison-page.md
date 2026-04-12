# Memory: PureBrain vs OpenClaw Comparison Page Build

**Date**: 2026-03-11
**Type**: pattern
**Agent**: dept-systems-technology
**Task**: Overnight Task 10 — Hostinger OpenClaw Comparison Page

---

## What Was Built

Self-contained HTML comparison page: PureBrain vs OpenClaw.

- **Output path**: `/purebrain-site/public/purebrain-vs-openclaw/index.html`
- **Deploy path**: `/exports/cf-pages-deploy/purebrain-vs-openclaw/index.html`
- **Cloudflare deploy**: `https://d306dba9.purebrain-staging.pages.dev`
- **Live URL**: `https://purebrain.ai/purebrain-vs-openclaw/`
- **1221 lines**, fully self-contained, mobile responsive

---

## Key Research Findings (OpenClaw)

- **OpenClaw is NOT a SaaS** — self-hosted AI gateway, MIT licensed
- **Founder (Peter Steinberger) left Feb 14, 2026** to join OpenAI — major stability risk
- **Hostinger URL** = co-marketing page, not deep tech partnership — Hostinger VPS pre-configured with OpenClaw
- **Real cost**: ~$14–45/mo (VPS + API keys + time), despite "free software"
- **Strengths**: messaging-native access (13+ platforms), privacy-first, multi-model, open source, deep integrations
- **Weaknesses**: technical barrier, no persistent business memory, no support, foundation transition risk

---

## Build Decisions

### Format Used
Used "boardy-style" format (CSS variables, clean layout) rather than old WordPress-boilerplate format. The `purebrain-vs-*` pages in the WordPress site were WP-exported and not suitable as templates. Boardy and enso pages in `compare/` directory are the right format reference.

### Prior Research Existed
`exports/departments/pure-research/competitors/2026-03-09--competitor-01-openclaw-deep-research.md` — comprehensive, high-quality research already done. Also `compare/openclaw/index.html` existed but at a different path. Built new page at `purebrain-vs-openclaw/` per task spec.

### Compare Hub Update
Updated `deepDive: '/compare/openclaw'` → `deepDive: '/purebrain-vs-openclaw/'` in compare hub JS data. Used Python string replacement (NOT sed) to avoid the sed file-wipe issue.

---

## Critical Gotcha: sed -i Wipes Files

**DO NOT use `sed -i` with complex patterns in bash on this system.** The command wiped `compare/index.html` to 0 bytes. The file was restored from git (`git checkout purebrain-site/public/compare/index.html`). Use Python for in-place replacements on HTML files.

```python
# Safe pattern:
with open(path, 'r') as f:
    content = f.read()
content = content.replace(old, new, 1)
with open(path, 'w') as f:
    f.write(content)
```

---

## Page Sections

1. Hero with product names and subtitles
2. Verdict banner (two-column summary)
3. Quick stats (3-card grid: time, cost, target user)
4. Alert banner (OpenClaw leadership transition warning)
5. Setup comparison (step-by-step DIY vs managed)
6. Full comparison table (16 dimensions)
7. Audience fit cards (who each is right for)
8. Where PureBrain wins (6-card grid)
9. Pricing comparison (total cost breakdown)
10. What OpenClaw gets right (honest credit section)
11. Final CTA + footer

---

## Deployment Pattern

```bash
export $(grep -E "^CF_" /home/jared/projects/AI-CIV/aether/.env | xargs)
CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT_ID CLOUDFLARE_API_TOKEN=$CF_PAGES_TOKEN npx wrangler pages deploy /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ --project-name=purebrain-staging --branch=main --commit-dirty=true
```

Uploads only new/changed files (2 files this time: new page + updated compare hub).
