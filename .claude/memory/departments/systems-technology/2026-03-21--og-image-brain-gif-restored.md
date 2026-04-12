# ST# OG Image: Brain GIF Restored on Homepage

**Date**: 2026-03-21
**Type**: operational
**Agent**: dept-systems-technology

## Task

Restore og:image on purebrain.ai homepage from static PNG back to the original brain GIF.

## What Was Done

1. Located `Pure-Brain-Vid-3.gif` at:
   - Local: `exports/cf-pages-deploy/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`
   - Size: 8.7MB original, 7.8MB after gifsicle optimization (minor savings)

2. Updated `exports/cf-pages-deploy/index.html` (line 116-119):
   - `og:image` → `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`
   - `og:image:type` → `image/gif`
   - width/height kept at 1200x630

3. Deployed to `purebrain-staging` CF Pages project.

4. Verified: `curl -sI` on the GIF URL returns `content-type: image/gif` HTTP 200.

## Key Facts

- GIF is already in the CF Pages deploy directory — no new upload needed.
- The GIF path is the same as the original WP URL: `/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`
- Jared confirmed LinkedIn DOES support GIFs — previous agent was wrong to switch to PNG.
- gifsicle provides minimal compression on this GIF (8.7MB → 7.8MB with lossy=120).

## CF Cache Note

- Only have `CF_PAGES_TOKEN` in .env — no zone ID or global API key for cache purge.
- Cache purge via zone API not possible with Pages token alone.
- Cache will expire naturally or Jared can purge via Cloudflare dashboard.

## File Changed

`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html`

## Tags
og-image, gif, brain-gif, linkedin, cf-pages, deploy, homepage
