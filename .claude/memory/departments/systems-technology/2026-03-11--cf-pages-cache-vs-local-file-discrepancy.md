# CF Pages Cache vs Local File Discrepancy — 2026-03-11

## Situation
Jared reported that sandbox-3 pricing page showed old content (wrong feature names, no strikethrough prices) even after hard-refresh and incognito. Local file was verified correct.

## Root Cause
Cloudflare Pages CDN edge cache lag. When wrangler deploys and shows "0 files uploaded (N already uploaded)", it means the asset hash matched — CF considered it already deployed. But the edge nodes serving the live URL had not yet propagated the latest build.

## Key Finding
`curl` from the server confirmed the live site WAS serving correct content at the time of investigation. The issue was browser-side caching or the user hitting a stale edge node that hadn't refreshed yet. CF Pages typically propagates within seconds to minutes, but edge nodes in specific regions can lag.

## What Fixed It
A fresh wrangler deploy (even with 0 new files) triggers a new deployment record with a unique deployment ID. This appears to force all edge nodes to invalidate and pull from the latest deployment snapshot. After the deploy, all 5 QA URLs confirmed correct content via curl.

## CF Pages Cache Purge Options (Investigated)
- No zone exists for `purebrain-staging.pages.dev` — cannot use zone-based cache purge
- `DELETE /accounts/{id}/pages/projects/{name}/deployments/cache` — returns 8000009 error (needs deployment ID in path, not a blanket purge)
- `POST .../purge_cache` — returns method_not_allowed
- **Working approach**: Simply re-run wrangler deploy. New deployment record forces edge refresh.

## Verification Pattern for Future
```bash
# Quick content check without browser:
curl -s "https://purebrain-staging.pages.dev/pay-test-sandbox-3/" | grep -E "Skills synch|Brain Stream Portal|197/mo"
# If curl shows correct → issue is browser/edge cache, not file content
# If curl shows wrong → actual deployment problem
```

## All 5 URLs — Final QA Status
- pay-test-sandbox-3: PASS (Skills synch, Brain Stream Portal, 3x strikethrough prices, no old strings)
- pay-test-2: PASS (same as above)
- pay-test-awakened: PASS ($149, $197/mo at launch strikethrough, Skills synch, Brain Stream Portal)
- pay-test-partnered: PASS ($499, $579/mo at launch strikethrough)
- pay-test-unified: PASS ($999, $1,089/mo at launch strikethrough)
