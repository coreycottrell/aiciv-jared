# 2026-05-04 -- R2 Public Domain to Proxy URL Migration

**Type**: technique + gotcha
**Topic**: R2 public domains break; use Worker proxy pattern instead

---

## Problem

R2 public domains (`*.r2.dev`) can silently break -- returning 404 for all objects even though the objects exist in the bucket. This is a Cloudflare configuration issue (public access must be explicitly enabled in dashboard).

## Solution Pattern

Instead of relying on R2 public domains, use a Worker proxy endpoint that reads from the R2 bucket binding directly:

```
OLD: https://pub-{hash}.r2.dev/{key}     -- fragile, depends on CF dashboard setting
NEW: https://social.purebrain.ai/media/{key}  -- Worker proxy, reads env.UPLOADS R2 binding
```

The proxy is ~10 lines of code:
```js
async function handleMediaProxy(request, env) {
  const key = decodeURIComponent(url.pathname.slice("/media/".length));
  const obj = await env.UPLOADS.get(key);
  if (!obj) return new Response("not found", { status: 404 });
  // Set content-type, cache headers, CORS
  return new Response(obj.body, { status: 200, headers });
}
```

## Key Locations

- Worker proxy: `workers/social-api/src/worker.js` L5403-5416
- Upload handler (now patched): L4935-4986
- Inline upload (was already correct): L4017-4028
- D1 migration: `tools/migrate_d1_r2_urls.py`
- File patches: `tools/apply_r2_proxy_patches.py`

## Gotchas

1. The inline `media_base64` PATCH path (L4024) already used proxy URLs -- only `handleUpload` (POST /api/uploads) was returning old public URLs
2. D1 `media_refs` stores JSON-encoded arrays of URLs -- use SQL `REPLACE` on the string, not JSON functions
3. `from-chy/worker-*.js` are historical snapshots -- patch them for hygiene but they are not deployed
4. `trio-comms` and `blog-publisher` workers use DIFFERENT R2 buckets/domains -- do not conflate
5. `r2_upload_results.json` and memory files are historical data -- do not patch

## Architectural Lesson

Never depend on R2 public domains for production URLs. Always use a Worker proxy:
- Proxy gives you control over caching, CORS, auth
- Proxy survives CF dashboard misconfigurations
- Proxy lets you change R2 bucket without changing public URLs
