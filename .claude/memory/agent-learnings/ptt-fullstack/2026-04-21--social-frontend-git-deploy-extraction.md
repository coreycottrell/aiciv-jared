# Social Frontend Extracted to Git-Based CF Pages Deploy

**Date**: 2026-04-21
**Type**: operational
**Agent**: full-stack-developer

## What Was Done

Extracted the social.purebrain.ai frontend from an inline template literal in the social-api worker
to a standalone file deployed via CF Pages (git-based).

### Git Side
- Created `/home/jared/purebrain-site/social/index.html` (3547 lines)
- Curled live HTML from `https://social.purebrain.ai/`
- Committed and pushed to `puretechnyc/purebrain-site` main branch
- CF Pages auto-deploys, so it will be available at `https://purebrain.ai/social/index.html`

### Worker Side
- Removed `const FRONTEND_HTML` template literal (lines 92-3639, ~3547 lines of inline HTML)
- Added `getFrontendHtml()` async function that fetches from CF Pages URL with 60s in-memory cache
- Stale-while-error: if fetch fails, serves cached version; if no cache, serves fallback HTML
- Uses `cf: { cacheTtl: 60 }` for CF edge-level caching too
- Worker shrank from 6319 lines to 2808 lines
- `node --check` passes (no syntax errors)

### Route Change
- `GET /` now calls `await getFrontendHtml()` instead of referencing the old constant
- All `/api/*` routes unchanged

## Key Files
- Frontend: `/home/jared/purebrain-site/social/index.html`
- Worker: `/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js`

## Not Done (Intentional)
- Worker NOT deployed yet -- left for manual verification and deploy
- Future frontend edits should go to the git repo, not the worker

## Gotcha
- The fetch URL is `https://purebrain.ai/social/index.html` -- this depends on CF Pages deploying
  the purebrain-site repo to the `purebrain-production` project. If the Pages deploy hasn't run yet,
  the worker would get a 404 on first request (fallback HTML would show).
