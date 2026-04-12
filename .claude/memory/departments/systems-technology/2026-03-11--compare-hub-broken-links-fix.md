# Compare Hub Broken Link Fix — 2026-03-11

## Task
Audit and fix all broken "deep dive" links on the compare hub at purebrain-staging.pages.dev/compare/

## Root Cause
4 comparison pages (Enso, Supercool, Billie Review, Boardy) had deepDive URLs set to `/compare/enso`, `/compare/supercool`, `/compare/billiereview`, `/compare/boardy` in the JavaScript data object.

The actual deployed pages live at the top-level paths: `/enso/`, `/supercool/`, `/billiereview/`, `/boardy/` — NOT under a `/compare/` subdirectory.

## Pages Affected
- Enso.bot: `/compare/enso` → `/enso/`
- Supercool (Deal.ai): `/compare/supercool` → `/supercool/`
- Billie Review: `/compare/billiereview` → `/billiereview/`
- Boardy.ai: `/compare/boardy` → `/boardy/`

## Fix Applied
Updated deepDive URLs in the JavaScript `tools` data object in:
- `/home/jared/projects/AI-CIV/aether/purebrain-site/public/compare/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/compare/index.html`

## Verification
All 18 deep dive links verified HTTP 200 after deploy:
- 14 `/purebrain-vs-*` pages: all OK
- 4 top-level comparison pages (enso, supercool, billiereview, boardy): all OK

## Pattern Learned
When adding new comparison pages with `deepDive` URLs in compare hub, the URL must match the ACTUAL deploy path. These 4 pages were NOT in a `/compare/` subdirectory — they were deployed at root level. Future compare pages should either:
a) All go under `/compare/[name]/` (requires copying to that subdir in cf-pages-deploy), OR
b) All go at root level `/[name]/` and deepDive URLs should match

## Files Modified
- `purebrain-site/public/compare/index.html` (source)
- `exports/cf-pages-deploy/compare/index.html` (deploy target)

## Deployment
Cloudflare Pages: purebrain-staging — 1 file uploaded, deployment complete
URL: https://purebrain-staging.pages.dev/compare/
