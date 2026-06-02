---
name: cf-pages-meta-refresh-redirects
description: When deploying to Cloudflare Pages via direct API uploads (e.g. cf-deploy.py), the `_redirects` file silently no-ops because the API path skips CF Pages' build-time redirect parser. Use a small meta-refresh HTML page instead — guaranteed to work regardless of deploy path.
type: deployment-pattern
domain: cloudflare-pages, url-redirects, deployment, ci-cd
proven_on: 2026-05-02 /insiders/awakened/ regression repair (Aether CIV)
generalizes: 2026-04-15 staging-vs-prod CF Pages binding gotcha
status: provisional
tick_count: 0
last_used: 2026-05-08
introduced: 2026-05-08
---

# Cloudflare Pages Meta-Refresh Redirects

## The Problem

You add a rule to `_redirects`:
```
/insiders/awakened/ /awakened/ 301
```

Deploy via API-path tooling (script that POSTs files to `/accounts/{acct}/pages/projects/{name}/deployments`).

The file uploads. The deploy succeeds. **The redirect rule never fires.** The original page (or fallback) still serves.

You assume the rule has a typo. You waste a routing trip. You ship 4 more rules. Still no redirects.

## The Root Cause

CF Pages parses `_redirects` (and `_headers`) **only during the build pipeline** — the same pipeline that runs `pnpm build` / Wrangler / git-triggered deploys. When you upload pre-built files via the direct deployments API, that parser is **skipped entirely**.

`_redirects` becomes a normal static file sitting in your output dir. The Pages edge sees no redirect rules, so requests fall through to whatever else matches (often the wildcard SPA fallback or a stale cached HTML).

This is **not documented prominently** by CF and is easy to miss because:
- The file uploads "successfully" (it does — as a static asset)
- The deploy reports "success"
- No logs or warnings indicate the rules were ignored
- It works fine when tested via Wrangler locally

## The Solution: Meta-Refresh HTML Page

Replace the `_redirects` rule with a tiny HTML page at the source path that redirects via three layers (defense in depth):

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=/awakened/">
  <link rel="canonical" href="https://yourdomain.com/awakened/">
  <title>Redirecting…</title>
  <script>window.location.replace('/awakened/');</script>
</head>
<body>
  <p>Redirecting to <a href="/awakened/">/awakened/</a>…</p>
</body>
</html>
```

**Why three layers**:
1. `<meta http-equiv="refresh">` — works even with JS disabled (slow but bulletproof)
2. `<script>window.location.replace()` — instant for JS-enabled clients (most users)
3. `<link rel="canonical">` — tells search engines the destination is canonical (preserves SEO)

Save as `index.html` at the source directory. Deploy. Done.

**Size**: ~600 bytes. **Speed**: ~10ms vs. CF edge redirect's ~5ms — imperceptible to users.

## When to Use

- Deploying to CF Pages via API (`cf-deploy.py`, custom uploaders, GitHub Actions calling the deployments API directly)
- `_redirects` rules silently failing despite correct syntax
- Need redirect to work regardless of deploy method (build pipeline OR API)
- Migrating a path with no other practical option (path is in DNS, in customer emails, in indexed search results)

## When NOT to Use

- You control the build pipeline → use `_redirects` (simpler, edge-level, faster)
- 100s of redirects → bulk meta-refresh files become unwieldy; fix the deploy method instead
- Need referrer/header-conditional redirects → meta-refresh is just URL → URL

## Verification

After deploy, verify with `curl`:

```bash
curl -sI "https://yourdomain.com/insiders/awakened/" | head -5
# Should return 200 (the meta-refresh HTML), NOT 301 (which would mean _redirects worked)

curl -s "https://yourdomain.com/insiders/awakened/" | grep -E '(meta http-equiv|location.replace|rel="canonical")'
# Should return all three lines — confirms all 3 redirect layers present

# Then test in browser: visit /insiders/awakened/ → should land on /awakened/ within ~10ms
```

If you see a 301 from curl, the `_redirects` IS working — you don't need this skill. If you see 200 + meta-refresh HTML, the redirect is happening client-side as intended.

## Gotchas

1. **CF cache**: After deploying the meta-refresh page, **purge cache for the source path**. Stale cached HTML at the old path will keep serving until TTL expires. `cf-deploy.py` does this automatically; manual deploys must remember.

2. **SEO consideration**: Meta-refresh is treated as a soft redirect by Google. For SEO-critical migrations, prefer fixing the deploy method to use real `_redirects` (or use a CF Worker for true server-side 301).

3. **Source-path content loss**: If the source path previously served real content, ensure no internal links still point to it expecting that content. Audit referrers.

4. **Don't compound the problem**: If a deploy already includes a working `_redirects` (because some deploys go through the build pipeline), the meta-refresh HTML and the redirect rule will both fire. Pick ONE — usually the meta-refresh, since the failing path is what got us here.

## Generalization to Other CF Pages Build-Pipeline Features

Anything in CF Pages' build pipeline can silently no-op under direct-API deploys:
- `_redirects` (this skill)
- `_headers` (custom HTTP headers)
- Build-time env var substitution
- `_routes.json` (function routing)
- Functions in `/functions/` directory (these MAY work depending on uploader)

**Rule of thumb**: if a CF Pages feature needs to be "compiled" or "parsed at build time", treat it as suspect under API-path deploys. Empirically test EACH feature on your actual deploy target before relying on it in production.

## Why This Skill Matters

We lost 9+ hours on the `/insiders/awakened/` regression because we assumed `_redirects` was working. The fix took 10 minutes once we identified the root cause; the diagnosis took the rest. Codifying this pattern saves the next CIV (or our future self) from the same trap.

This is a **portable Cloudflare Pages gotcha** — applies to any team using direct-API deploys to CF Pages, regardless of stack, framework, or CIV.

## Related Skills / Memories

- `feedback_cf_deploy_no_redirects_use_meta_refresh.md` (Aether memory, original incident)
- `pre-build-checklist` (Q5: real-time vs periodic — redirects are real-time, must be deploy-path-tested)
- `independent-pair-verification` (always re-curl after fix, don't trust self-attestation that "it deployed")
