---
type: operational
topic: Brainiac Module 7 built and shipped to purebrain-production
date: 2026-04-15
---

# Brainiac Module 7 — Shipping & Measuring AI Output — SHIPPED

## What
Cloned Module 6 template to build Module 7 on the theme "Shipping & Measuring AI Output: Your Shipped-to-Generated Ratio" — tied directly to today's blog post "Your AI Wrote 10,000 Lines of Code Last Week. How Many Shipped?"

## 7-slide deck
1. Title — Shipping & Measuring AI Output
2. The Wake-Up Call — the 340%/19% story from the blog
3. Inputs vs Outputs — 6-row concrete table (lines generated → features shipped, etc.)
4. The 3 Monday Questions — ratio, deletion-why, velocity-vs-output
5. Practical Exercise — compute your own shipped-to-generated ratio from last sprint
6. Connections + FAQ + Daily Recap — links back to Module 5 (memory) + Module 6 (self-assessment); 4 collapsible FAQs; transparency recap box
7. Closing — call-to-action + Module 6 back + hub back

## 4 locked template features (all present)
- 60% opacity dark background (`background: rgba(8,10,18,0.60)` overlay)
- Background video (R2 neural-loop mp4, fixed layer, 0.28 opacity)
- Collapsible FAQs (4 items on slide 6, `toggleFaq()`)
- Daily recap / transparency block (slide 6, `.recap-box`)

## Changes
- NEW: `exports/cf-pages-deploy/brainiac-mastermind-training/brainiac-module-7-shipping-measurement/index.html` (30,441 bytes)
- CHANGED: `exports/cf-pages-deploy/brainiac-mastermind-training/index.html` — added M7 card (module-col 7), full AI Training Snippet (6 core concepts, 6 techniques, 10-item checklist, 3 quotes), and entry in TRAINING_VIDEOS array (id `module-7-shipping-measurement`)
- CHANGED: `exports/cf-pages-deploy/sitemap.xml` — added M7 URL + bumped mastermind hub lastmod to 2026-04-15
- LEFT ALONE: `brainiac-training-hub/index.html` (legacy page, stops at M2, not the real hub — no modification per "don't auto-modify approved content")

## Deploy
- Pre-deploy-sync with Chy: clean, she only touches investor-avatar / investor-tracking / gifts
- Command: `CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py brainiac-mastermind-training/brainiac-module-7-shipping-measurement/ brainiac-mastermind-training/index.html sitemap.xml`
- Deploy ID: `9ae13a7e-4b92-4009-b595-b5d3fabec6ac`
- Alias URL: `https://9ae13a7e.purebrain-production-23b.pages.dev`
- Production: `https://purebrain.ai`
- Manifest: 1 new, 2 changed, 1166 → 1167 files

## CF cache purge
Purged 3 URLs on zone `49400cad1527af716705f6cb8c22bb65`:
- `/brainiac-mastermind-training/`
- `/brainiac-mastermind-training/brainiac-module-7-shipping-measurement/`
- `/sitemap.xml`

## Verification (the ACTUAL output, not a guess)
- `curl -I https://purebrain.ai/brainiac-mastermind-training/brainiac-module-7-shipping-measurement/` → `HTTP/2 200`
- Body size: 30,441 bytes (target was >30KB — passes)
- Title: `Brainiac — Module 7: Shipping & Measuring AI Output`
- Hub page grep found all 4 M7 markers: `module-7-shipping-measurement`, `Module 07`, `Launch Module 7`, `module-col 7`

## Constraints honored
- March 20 locked template preserved (cloned Module 6 structure exactly)
- Wrangler NOT used — `cf-deploy.py` only (constitutional)
- Target: `purebrain-production` NOT staging (per corrected CLAUDE.md Apr 15 incident note)
- Existing Module 6 directory untouched (no in-place edits, new directory built)
- Brainiac weekly BOOP will now skip M7 (idempotent: dir exists) and target M8 next run

## Pattern to reuse
When a new Brainiac module comes due:
1. Read Module 6's index.html as canonical slide-deck template
2. Keep identical CSS except for bg-video/bg-overlay additions and FAQ/recap blocks
3. In the hub, the `module-col N` block + full AI-training-snippet + TRAINING_VIDEOS array entry must ALL be added — missing any one leaves the module half-connected
4. For modules with `hlsUrl: null` (no video yet), add `launchUrl` field so the JS-rendered card can still deep-link to the slide deck
5. Always sitemap + CF cache purge + live curl verification before calling done

## File paths
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/brainiac-module-7-shipping-measurement/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/sitemap.xml`
