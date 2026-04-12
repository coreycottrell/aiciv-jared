# PureBrain App Netlify Deployment

**Date**: 2026-02-24
**Type**: operational
**Task**: Deploy purebrain-frontend-3d.html to Netlify at app.purebrain.ai

## What Was Done

Deployed the PureBrain 3D frontend (14,495 lines, ~895KB) to Netlify.

## Key Facts

- **Source file**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-frontend-3d.html`
- **Deploy dir**: `/tmp/purebrain-app-deploy/index.html`
- **Netlify Site ID**: `2139f9ed-32cc-4abd-8364-8bb81b94df9b`
- **Netlify Site Name**: `purebrain-app`
- **Netlify URL**: https://purebrain-app.netlify.app
- **Custom Domain Set**: app.purebrain.ai (SSL URL: https://app.purebrain.ai)
- **Account**: purebrain (account slug)

## Netlify CLI Notes

- Auth token NOW in `.env` as `NETLIFY_AUTH_TOKEN`
- Pinned CLI version `@23.15.1` works reliably (24.x had issues)
- `sites:create` is interactive - use REST API directly instead:
  ```bash
  curl -X POST -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name": "site-name", "account_slug": "purebrain"}' \
    "https://api.netlify.com/api/v1/sites"
  ```
- Set custom domain via PATCH (not domain_aliases endpoint):
  ```bash
  curl -X PATCH -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"custom_domain": "app.example.com"}' \
    "https://api.netlify.com/api/v1/sites/{site-id}"
  ```

## DNS Required

Jared must add this CNAME at his DNS provider (Cloudflare most likely):
```
app.purebrain.ai  CNAME  purebrain-app.netlify.app
```

## Deploy Pattern (Future Redeploys)

```bash
# Copy updated file
cp /home/jared/projects/AI-CIV/aether/exports/purebrain-frontend-3d.html /tmp/purebrain-app-deploy/index.html

# Deploy
NETLIFY_AUTH_TOKEN=nfp_sVF1Myk2EFtgEbSMnSE3aSPvWuGCqmZW5dc8 \
  npx netlify-cli@23.15.1 deploy --prod \
  --dir=/tmp/purebrain-app-deploy \
  --site=2139f9ed-32cc-4abd-8364-8bb81b94df9b
```

## Verification

- HTTP 200, Content-Type: text/html, Size: 894823 bytes confirmed via curl
