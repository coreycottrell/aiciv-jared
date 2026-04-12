# Blog Index: WP-Content to Local Paths Migration

**Date**: 2026-03-19
**Type**: operational + teaching
**Topic**: CF Pages blog index — dead wp-content URLs, missing posts, Brevo 401, CF Functions

## What Was Fixed

1. Only 11 of 31 posts listed — WP export captured a dynamic posts block rendered at export time only
2. All banner images broken — img src pointed to dead https://purebrain.ai/wp-content/... absolute URLs
3. Brevo subscribe form 401 — API key disabled in Brevo dashboard, key exposed in HTML
4. Background GIF + logo also used dead absolute wp-content URLs

## Root Cause

WP static export captures dynamic blocks at export time. As new posts are added to deploy folder, index is never updated. All WP asset URLs use absolute https://purebrain.ai/wp-content/... — these 404 on CF Pages but the files exist locally at /wp-content/uploads/...

## Fixes

Fix 1+2: Replaced entire WP posts ul block with all 31 posts using src="/blog/{slug}/banner.{ext}" local paths.
Fix 3: Created /functions/api/subscribe.js CF Pages Function to proxy Brevo server-side. Form now calls /api/subscribe. API key removed from HTML. ACTION REQUIRED: Re-enable Brevo key in app.brevo.com, set BREVO_API_KEY env var in CF Pages dashboard.
Fix 4: Logo and background GIF changed to relative paths.

## Key Paths

- Blog index: exports/cf-pages-deploy/blog/index.html
- Subscribe CF Function: exports/cf-pages-deploy/functions/api/subscribe.js
- Banner pattern: exports/cf-pages-deploy/blog/{slug}/banner.{ext}

## Lessons

1. After WP exports: scan and replace all wp-content absolute URLs with relative paths
2. Blog index needs manual maintenance when adding new posts
3. Never put API keys in static HTML — use CF Pages Functions
4. Brevo key test: curl -s https://api.brevo.com/v3/account -H "api-key: KEY" — "API Key is not enabled" = disabled in dashboard
