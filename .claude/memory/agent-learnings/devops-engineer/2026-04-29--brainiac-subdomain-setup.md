# Brainiac Subdomain Setup - brainiac.purebrain.ai

**Date**: 2026-04-29
**Type**: operational
**Agent**: devops-engineer

## What Was Done

Set up `brainiac.purebrain.ai` as its own CF Pages project serving the Brainiac training platform.

## Key Steps

1. Created CF Pages project `brainiac-purebrain` via API
2. Copied content from `/home/jared/purebrain-site/brainiac-mastermind-training/` to `/home/jared/projects/brainiac-purebrain/`
3. Restructured: root `index.html` + `/module-1/` through `/module-8/` subdirectories
4. Updated all internal links from old paths (`/brainiac-mastermind-training/brainiac-module-X-name/`) to new (`/module-X/`)
5. Updated canonical/og:url meta tags to `brainiac.purebrain.ai`
6. Deployed via `wrangler pages deploy` (requires `CLOUDFLARE_ACCOUNT_ID` env var alongside `CLOUDFLARE_API_TOKEN`)
7. Created DNS CNAME: `brainiac` -> `brainiac-purebrain.pages.dev` (proxied)
8. Added custom domain `brainiac.purebrain.ai` to the Pages project
9. **Critical**: Added worker route `brainiac.purebrain.ai/*` with `script: null` to override the wildcard `*.purebrain.ai/*` -> `purebrain-portal-proxy` route

## Gotcha: Wildcard Worker Route

The zone has `*.purebrain.ai/*` -> `purebrain-portal-proxy` worker route. Any new subdomain on `purebrain.ai` will get caught by this and return 530 errors. **Must add a null-script worker route** for new subdomains to let CF Pages serve them.

## Key Resources

- CF Pages project: `brainiac-purebrain`
- Pages.dev URL: `https://brainiac-purebrain.pages.dev`
- Custom domain: `https://brainiac.purebrain.ai`
- DNS record ID: `0985f9554e79ef707a8f9122059fe5d9`
- Worker route ID (null override): `44723f10579e462aa3df92062e39ffc2`
- Local content: `/home/jared/projects/brainiac-purebrain/`
- Original content (unchanged): `/home/jared/purebrain-site/brainiac-mastermind-training/`

## CF API Direct Upload Doesn't Work

The CF Pages direct upload via multipart form (`-F "manifest=..." -F "/path=@file"`) creates deployments that show "success" but serve 404. **Use wrangler** with both `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` set as env vars.
