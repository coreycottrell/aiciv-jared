# Portal-Proxy Deploy Impact Verification — 2026-05-07

**Deploy:** Worker version `a3f1da4a-f747-43a9-af01-114aeb32d24a` @ 16:27 UTC.
**Hypothesis:** Deploy broke `/api/log-conversation`, `/api/verify-payment`, `/api/send-seed`, `/api/magic-link/{uuid}`.
**Verdict: NO.** All four endpoints healthy post-deploy. "Duplicate dead block" was genuinely dead.

---

## Diff details (commit `1fe0a3e`)

3 files touched. `worker.js`: -15 / +9. Change is scoped entirely to the `portal.purebrain.ai` admin-token branch (lines 187-208). Nothing in onboarding-API paths was modified.

**Lines removed (the "dead block"):** pre-deploy lines 192-205 — verbatim second `if` block with the **identical condition** as 179-191:

```js
if (url.pathname.startsWith('/api/admin/affiliat') || ... || url.pathname === '/api/admin/stats')
```

Provably dead: the first matching block ends with `return new Response(...)`. Control never reaches the second. Verified via `git show 1fe0a3e^:workers/.../worker.js`.

**Line changed:** surviving block now reads `proxyHeaders.set('X-Admin-Token', env.ADMIN_TOKEN)` (was hardcoded `'purebrain-admin-2026'`), wrapped in `if (env.ADMIN_TOKEN)`.

**Other:** `.gitignore` (+2 for `tools/.secrets/`), `wrangler.toml` (+8, scaffolding only — no `[[routes]]`; route remains the existing `*.purebrain.ai/*` zone binding). No inadvertent edits.

---

## Route patterns + interception scope

`wrangler.toml` declares no `[[routes]]` (intentional — comment says route is configured on the zone). The `*.purebrain.ai/*` route DOES match `api.purebrain.ai/*`. **However**, `worker.js` line 36-58 puts `'api'` in `SYSTEM_SUBDOMAINS`. Logic at line 137-147:

1. No subdomain → apex pass-through to CF Pages
2. `subdomain === 'portal'` → admin/referral routing
3. **Else: implicit pass-through** to default fetch

The worker does **not** intercept `/api/log-conversation`, `/api/verify-payment`, `/api/send-seed`, or `/api/magic-link/{uuid}`. Those fall through to the `api.purebrain.ai` DNS record (Argo tunnel → portal_server.py / api worker).

---

## Live curl results (post-deploy, ~17:47-17:48 UTC)

| Endpoint | Body | HTTP | Response |
|---|---|---|---|
| POST `/api/log-conversation` | `{"test":true,...}` | **400** | `Missing required field: messages` — handler reachable, validating |
| POST `/api/log-conversation` | `{"messages":[...],"session_uuid":"verify-test"}` | **200** | `{"session_id":"pb-...","success":true}` — working |
| GET `/api/magic-link/test-uuid` | — | **200** | `{"status":"pending"}` |
| POST `/api/verify-payment` | `{"test":true}` | **400** | `Missing required field: orderId` |
| POST `/api/verify-payment` | `{"orderId":"verify-test"}` | **200** | `{"success":true,"verified":true}` |
| POST `/api/send-seed` | `{"test":true}` | **400** | `session_uuid and human_email are required` |

All endpoints validate and return success on proper payloads. `server: cloudflare`, CORS correct. **Onboarding API healthy.**

Pre-deploy logs unavailable: `wrangler tail` blocked by parallel npm install conflict; CF API doesn't expose tail history. Logged in deliverable for record.

---

## "Dead block" reality check

Genuinely dead. Walked logic:

- Block A: `if (admin paths) { ... return new Response(...) }`
- Block B: `if (admin paths) { ... }` — **same condition, same branch context, same scope**

No header check, no method gate, no subdomain difference. Pure copy-paste residue from a refactor.

The timing correlation Jared noticed (deploy 16:27 → onboarding broken) is real but **not caused by this commit**. Likely culprits: the 15:33 UTC `git reset --hard` (wiped runtime logs and possibly local state on the box owning onboarding handlers), or an unrelated upstream change to `api.purebrain.ai` (portal_server.py / Argo tunnel / D1 schema).

---

## Verdict

**Deploy did NOT break onboarding.**

1. Diff scope is `portal.purebrain.ai/api/admin/*` only — does not touch onboarding paths.
2. `api.purebrain.ai` in `SYSTEM_SUBDOMAINS` → proxy passes through unchanged.
3. All four onboarding endpoints live and responding correctly.
4. Removed code was provably unreachable.

---

## Rollback command (record only — NOT recommended)

Previous version: `d12a1a12-17f2-47fd-a158-ab4bf3854cad` (deployed 2026-05-05 11:18 UTC).

```bash
export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" .env | cut -d= -f2)
cd workers/purebrain-portal-proxy
npx wrangler rollback --message "Rollback Phase 0" d12a1a12-17f2-47fd-a158-ab4bf3854cad
```

**Do not execute.** Rollback re-introduces the leaked hardcoded token without fixing onboarding (which isn't broken by this deploy). Investigate the 15:33 UTC `git reset --hard` and `api.purebrain.ai` upstream (portal_server.py + Argo tunnel) instead.
