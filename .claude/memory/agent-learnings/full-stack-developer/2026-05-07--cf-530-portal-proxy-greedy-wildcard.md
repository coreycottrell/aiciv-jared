# CF 530 on `ce.purebrain.ai` — root cause was greedy Worker wildcard, not DNS/SSL

**Date:** 2026-05-07
**Type:** teaching (transferable wisdom)
**Topic:** CF Pages 530 diagnosis — when DNS/SSL look fine, suspect Worker routes

---

## Symptom

`ce.purebrain.ai` returned HTTP 530 while underlying `purebrain-production-23b.pages.dev` returned 200. Custom domain was registered, status `active`, SSL cert issued and valid, DNS CNAME correct, TLS handshake succeeded.

## Real Root Cause

The Worker route `*.purebrain.ai/*` → `purebrain-portal-proxy` matched first (more specific Pages binding does NOT override a Worker route). The proxy worker rewrites Host to `{subdomain}.ai-civ.com` to proxy customer containers on Witness, but `ce.ai-civ.com` doesn't exist → CF error 1016 (Origin DNS error) → wrapped as HTTP 530.

The error body was the smoking gun: CF's 1016 page literally said "unable to resolve ce.ai-civ.com" — NOT `ce.purebrain.ai`. **Always read the full 530 body** — CF embeds the actual upstream hostname it tried to resolve.

## Fix

Add a more specific Worker route with `script: null` to bypass the wildcard proxy. Pattern in production for many subdomains (`api.`, `creator.`, `777.`, `brainiac.`):

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE/workers/routes" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  --data '{"pattern":"ce.purebrain.ai/*","script":null}'
```

Edge propagation effectively instant (~3s).

Also added `'ce'` to `SYSTEM_SUBDOMAINS` in `workers/purebrain-portal-proxy/src/worker.js` for documentation/defense-in-depth (not deployed, route is enough).

## Diagnostic Pattern (reusable)

When a CF Pages custom domain returns 530 and basic checks pass:

1. Verify DNS: `dig +short CNAME <domain>` → should hit `*.pages.dev`
2. Verify Pages domain status via API: `GET /accounts/{acct}/pages/projects/{proj}/domains/{domain}` → `status: active`
3. Verify TLS: `curl -sv https://<domain>/ 2>&1 | grep -A2 "Server certificate"`
4. **If all 3 pass: list Worker routes on the zone** — `GET /zones/{zone}/workers/routes`. Look for greedy patterns like `*.<apex>/*` that could be intercepting.
5. **Read the 530 body** — CF often embeds the upstream hostname/error code (e.g. 1016 = origin DNS error, 1042 = secret missing).

## Gotchas captured

- HEAD vs GET: per `cf-pages-health-check-get-not-head` skill, always use GET for CF Pages health. HEAD on the *.pages.dev returned 200 here but on real Pages domains can falsely return 404.
- Worker routes beat Pages bindings — adding a custom domain to a Pages project does NOT bypass an existing Worker route covering that hostname. Most-specific wins among Worker routes.
- `wrangler pages deploy` BANNED. Modifying Worker routes via API is allowed and does not violate "never local deploy" rule (no Pages deploy occurred).
- Error body is the diagnostic gold mine for 530s — don't just read the status code.

## Files / IDs

- Worker route created: `eef98a8dc02d4bcc934060d05235171f` — pattern `ce.purebrain.ai/*`, script null
- Worker source updated: `/home/jared/projects/AI-CIV/aether/workers/purebrain-portal-proxy/src/worker.js` (added `'ce'` to `SYSTEM_SUBDOMAINS`)
- Deliverable: `/home/jared/projects/AI-CIV/aether/exports/portal-files/dns-fix-ce-purebrain-ai-2026-05-07.md`

## Open issue handed back

`ce.purebrain.ai` and `purebrain.ai` are both bound to the same `purebrain-production` Pages project, so they serve identical content. To serve distinct CE SME content, either move `ce.purebrain.ai` to its own Pages project or add Pages Functions host-routing on the existing project.
