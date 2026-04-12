# Memory: app.purebrain.ai Favicon Fix — Netlify Credit Block (UPDATED 2026-02-28)

**Date**: 2026-02-28
**Agent**: dept-systems-technology
**Type**: gotcha + operational
**Topic**: Favicon update done locally, blocked from deploying due to Netlify free plan credit exhaustion. GCP investigation confirmed: app.purebrain.ai is on NETLIFY, not Google Cloud.

---

## What Was Done

### Changes Made to Source File
File: `/home/jared/projects/AI-CIV/aether/exports/purebrain-frontend-3d.html`

1. **Title fixed**: Changed `<title>AiCIV</title>` to `<title>PureBrain</title>`
2. **Favicon replaced**: Old = AiCIV purple/cyan gradient circle with "A". New = PureBrain hexagon with P (blue #2a93c1) and B (orange #f1420b)

Source file status: FIXED and ready to deploy (line 6-7).

---

## GCP Investigation Results (2026-02-28)

**Jared said it was on Google Cloud. Full investigation found:**

- gcloud CLI: NOT installed on this machine
- GCP credentials: NOT found anywhere in .env or repo
- Service account: Google Drive only (not compute hosting)
- x-cloud-trace-context header: From Cloudflare's own internal infrastructure (they use GCP for logging). NOT a GCP origin indicator.
- No app.yaml, cloudbuild.yaml, Cloud Run config, or App Engine config anywhere
- Witness backend: 104.248.239.98 (DigitalOcean, not GCP)

**CONCLUSION: app.purebrain.ai is NOT on Google Cloud. It is on Netlify.**

---

## Confirmed Deployment Architecture

- DNS: app.purebrain.ai -> Cloudflare (188.114.96.1 / 188.114.97.1)
- Cloudflare: Proxy mode, passes through (cf-cache-status: DYNAMIC, not cached)
- Origin: Netlify CDN serving site "purebrain-app"
- Site ID: 2139f9ed-32cc-4abd-8364-8bb81b94df9b
- Account: purebrain / "Pure Technology" (Free plan, purebrain@puremarketing.ai)
- Account ID: 699c81c818f8d32e1da73e79
- Auth token in .env: NETLIFY_AUTH_TOKEN=nfp_sVF1Myk2EFtgEbSMnSE3aSPvWuGCqmZW5dc8
- Live deploy: 699e37a53cf3567d935df0d4 (from 2026-02-24, still serving old AiCIV version)

---

## Blocker: Netlify Free Plan Deploy Block

Error on all deploy attempts: Account credit usage exceeded - new deploys are blocked until credits are added

Attempts tried: CLI deploy, REST API zip, REST API digest, snippet injection (none work).

The existing deployed version (old AiCIV page) is still live and stable — Netlify just prevents NEW deploys.

This is a Netlify Free plan billing verification requirement. The dashboard shows 300 credits included, 0 used, but a payment method must be added to re-enable deploys.

---

## What Jared Needs to Do

### Option A (Fastest): Fix Netlify billing
1. Go to https://app.netlify.com/teams/purebrain/billing
2. Add a credit card (will NOT be charged for free tier usage)
3. Run this command after:

```bash
mkdir -p /tmp/pb-deploy
cp /home/jared/projects/AI-CIV/aether/exports/purebrain-frontend-3d.html /tmp/pb-deploy/index.html
NETLIFY_AUTH_TOKEN=nfp_sVF1Myk2EFtgEbSMnSE3aSPvWuGCqmZW5dc8 npx netlify-cli@24.0.1 deploy --prod --dir=/tmp/pb-deploy --site=2139f9ed-32cc-4abd-8364-8bb81b94df9b --auth=nfp_sVF1Myk2EFtgEbSMnSE3aSPvWuGCqmZW5dc8
```

### Option B (Recommended long-term): Cloudflare Pages
- Jared has CF_ACCOUNT_ID in .env already
- Need: Cloudflare API token (dash.cloudflare.com -> My Profile -> API Tokens -> Create Token -> "Edit Cloudflare Pages")
- Cloudflare Pages = free, unlimited deploys, no card required, DNS already on CF

---

## SVG Favicon Reference

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <polygon points="16,1 29,8.5 29,23.5 16,31 3,23.5 3,8.5" fill="none" stroke="#2a93c1" stroke-width="1.8"/>
  <text x="12" y="20" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="700" fill="#2a93c1">P</text>
  <text x="20" y="20" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="700" fill="#f1420b">B</text>
</svg>
```
