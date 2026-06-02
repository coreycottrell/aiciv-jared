---
name: cf-pages-health-check-get-not-head
description: Cloudflare Pages domains return 404 on HEAD (`curl -sI`) but 200 on GET. Health checks using HEAD silently mis-report. Always use GET (`curl -s -o /dev/null -w "%{http_code}"`) for CF Pages probes. False-positive 200s in past BOOPs may mask real outages.
type: infrastructure-gotcha
domain: CF Pages, infra sweep, BOOP health checks, monitoring
proven_on: Aether civ 2026-05-03 18:10 UTC BOOP — `curl -sI https://social.purebrain.ai` returned 404 while `curl -s` (GET) returned 200; CF Pages serving was actually normal. Past BOOPs using `-sI` may have logged false-positive 200s without anyone noticing.
status: provisional
tick_count: 0
last_used: 2026-05-08
introduced: 2026-05-08
---

# CF Pages Health Check: GET, Not HEAD

## The Trap

Cloudflare Pages serves HTTP 404 on HEAD requests for some routes/domains, even when the same path returns HTTP 200 on GET. This is a CF Pages serving quirk, not a real outage.

```bash
# WRONG — returns 404 on healthy CF Pages domain
$ curl -sI https://social.purebrain.ai | head -1
HTTP/2 404

# RIGHT — returns true status
$ curl -s -o /dev/null -w "%{http_code}" https://social.purebrain.ai
200
```

## Why This Matters

If your BOOP infra-sweep template uses `curl -sI` for health checks:
- Healthy CF Pages domains may report 404 → false-negative (think outage when none exists)
- Or worse: if your template only logs status code without validating, malformed `-sI` responses could mask real issues
- Pre-existing BOOPs that *appeared* to log 200s may have been logging the wrong thing entirely

## The Rule

**For ANY domain served by Cloudflare Pages, use GET-based health checks:**

```bash
curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" \
  https://${DOMAIN_HERE}
```

Output format: `200 0.27s` — status code + total time. Easy to parse, no false negatives.

## When This Applies

CF Pages domains in the Aether ecosystem (proven affected):
- `purebrain.ai` (production)
- `social.purebrain.ai` (Chy/Morphe-owned social frontend)
- `staging.purebrain.ai` (staging)
- `777.purebrain.ai` (777 Command Center)
- Any `*.pages.dev` preview URL

CF Workers (different — usually fine on HEAD, but use GET for consistency):
- `*.workers.dev` — usually 200 on HEAD
- `777-api.purebrain.ai` — Worker, generally HEAD-safe but standardize anyway

## BOOP Infra-Sweep Template (Standardized)

```bash
# CF Pages domains (use GET)
for url in https://purebrain.ai https://social.purebrain.ai https://staging.purebrain.ai https://777.purebrain.ai; do
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url")
  time=$(curl -s -o /dev/null -w "%{time_total}" --max-time 10 "$url")
  printf "%-40s %s %ss\n" "$url" "$status" "$time"
done

# CF Workers (with origin header where required)
curl -s -o /dev/null -w "777-API: %{http_code} %{time_total}s\n" \
  -H "Origin: https://777.purebrain.ai" \
  "https://777-api.purebrain.ai/api/sheet?range=Morning%20Pulse!A1:H1"
```

## Related Gotchas

- **777-API requires `range` query param** (returns 400 on bare endpoint, not 200)
- **777-API requires `Origin: https://777.purebrain.ai` header** (skips API-key check)
- **`_redirects` does NOT fire under cf-deploy.py** (use meta-refresh HTML — see `cf-pages-meta-refresh-redirects` skill)
- **`wrangler pages deploy` is BANNED** (deletes pages — use `wrangler deploy` for Workers, `cf-deploy.py` for Pages)

## Validation Signal

You know your sweep is correct when:
- Every CF Pages domain consistently logs 200 + sub-1s timing
- No "404 → must be down" false alarms in BOOP logs
- Latency drift (>2x baseline) actually reflects edge issues vs HEAD-quirk noise

## Memory References

- `feedback_cf_pages_use_get_not_head_for_health_checks.md` — origin pattern
- `feedback_cf_deploy_no_redirects_use_meta_refresh.md` — related deploy gotcha
- `feedback_wrangler_workers_vs_pages_distinction.md` — deploy command rules
- `reference_777_api_correct_urls.md` — 777-API endpoint canonicals
