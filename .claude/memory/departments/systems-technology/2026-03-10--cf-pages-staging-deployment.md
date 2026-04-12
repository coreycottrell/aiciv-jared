# Cloudflare Pages Staging Deployment - purebrain.ai

**Date**: 2026-03-10
**Type**: deployment pattern
**Agent**: dept-systems-technology

## What Was Done

Deployed full WordPress export of purebrain.ai to Cloudflare Pages as staging site.

**Live URL**: https://purebrain-staging.pages.dev
**CF Project ID**: 7c467c82-7f69-46a4-a337-53c57a6e30cc
**Project Name**: purebrain-staging

## Directory Structure Built

```
/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/
  index.html                          ← homepage (page ID 11, slug: pure-brain-agentic-ai-partner)
  {page-slug}/index.html              ← 98 pages total
  blog/{post-slug}/index.html         ← 24 posts total
  wp-content/uploads/2026/02/*.png    ← 85 media files
```

Source: `/home/jared/projects/AI-CIV/aether/exports/wp-full-export/`
Manifest: `EXPORT-MANIFEST.json` (98 pages, 24 posts, 87 media)

## Key Technical Decisions

1. **Homepage mapping**: Page ID 11 (slug: `pure-brain-agentic-ai-partner`) maps to root `index.html` because its `link` field is `https://purebrain.ai/`.

2. **Blog URL structure**: WordPress posts live at `/blog/{slug}/index.html` to match standard blog URL path.

3. **Media path**: Kept at `/wp-content/uploads/...` to mirror WordPress URL structure — ensures any hardcoded image references in HTML still resolve.

4. **Oversized files excluded**: Two MP4 files exceeded Cloudflare Pages 25MB file size limit:
   - `Pure-Brain-Demo-Video-real-compression-and-sizing.mp4` (86MB)
   - `PureResearch.ai-1.mp4` (71MB)
   These are served from `video.purebrain.ai` (Cloudflare R2) in production anyway.

## Commands Used

```bash
# Create CF Pages project
curl -X POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects \
  -H "X-Auth-Email: ..." -H "X-Auth-Key: ..." \
  --data '{"name": "purebrain-staging", "production_branch": "main"}'

# Deploy via wrangler
CLOUDFLARE_ACCOUNT_ID=... CLOUDFLARE_API_KEY=... CLOUDFLARE_EMAIL=... \
npx wrangler pages deploy /path/to/cf-pages-deploy/ \
  --project-name=purebrain-staging --branch=main --commit-dirty=true
```

## Verification Results

| URL | Status |
|-----|--------|
| https://purebrain-staging.pages.dev/ | 200 OK |
| https://purebrain-staging.pages.dev/invitation/ | 200 OK |
| https://purebrain-staging.pages.dev/pay-test-2/ | 200 OK |
| https://purebrain-staging.pages.dev/compare/ | 200 OK |
| Media file (PURE-BRAIN-1.png) | 200 OK |

## Gotchas

- Wrangler 4.72.0 available system-wide (not via npx node_modules)
- `--commit-dirty=true` required when working directory is a git repo with uncommitted changes
- 25MB per-file Cloudflare limit is hard — video files must be excluded
- 522 errors on first check may be transient CDN propagation — retry before alarming

## Next Steps (Phase 3)

- DNS flip: Add CNAME `purebrain-staging.pages.dev` or use Cloudflare custom domain on the project
- For production cutover: add `purebrain.ai` as custom domain to the project, then update DNS
