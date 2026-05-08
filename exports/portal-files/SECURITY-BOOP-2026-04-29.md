# Security Posture BOOP — 2026-04-29

**Reviewer:** security-engineer-tech
**Scope:** uncommitted changes in `workers/` + recent commits (last 14 days)
**Verdict:** 🔴 **CRITICAL — payout system hijack possible**

---

## 🔴 CRITICAL #1 — Affiliate Payout Hijack (no auth on PayPal/payout endpoints)

**File:** `workers/referrals-api/src/worker.js` (uncommitted, ~lines 320–420)

Three public POST endpoints accept **only** the affiliate's `referral_code` (PB-XXXXXX) with **no password, no session token, no signature**:

| Endpoint | What attacker gets |
|---|---|
| `POST /paypal-email` | Change *any* affiliate's PayPal email to attacker-controlled address |
| `POST /payout-request` | Submit payout for *any* affiliate (any amount) |
| `GET /payout-history?referral_code=…` | Read *any* affiliate's payout history |

**Why it's catastrophic:** referral codes are public — they appear in the landing-page URL (`https://purebrain.ai/?ref=PB-XXXXXX`), the leaderboard endpoint, click-track payloads, and anywhere an affiliate shares their link. Codes are 6 alphanumeric chars (~36^6 = 2.1B keyspace) — but there is no rate-limit, so enumeration of *active* codes is trivial via `/lookup?code=…`.

**Attack chain (5 minutes):**
1. Read leaderboard → harvest codes with non-zero earnings
2. `POST /paypal-email` with `{referral_code: "PB-VICTIM", paypal_email: "attacker@evil.com"}`
3. Wait for next batch payout — funds go to attacker
4. Bonus: `POST /payout-request` to drain pending balance immediately

**Fix required:** every payout/PayPal-touching endpoint MUST require either:
- Bearer session token (validated against a real `sessions` table), OR
- The user's password posted with the request

---

## 🔴 CRITICAL #2 — Session tokens are decorative, not enforced

**File:** `workers/referrals-api/src/worker.js` line ~234

```js
const sessionToken = generateToken();
// ...
return json({ ok: true, session_token: sessionToken, ... });
```

The token is **generated, returned to client, and immediately forgotten**. It's never stored in D1, never validated on subsequent requests. The `/session` endpoint is effectively just a password verifier that issues a meaningless string. Combined with #1, the "auth" is purely UI theater.

**Fix required:** persist sessions in D1 (`sessions` table — already exists in `social-api`), set HttpOnly cookie with 12h TTL, validate on every state-changing request.

---

## 🟡 HIGH #3 — Weak password hashing (SHA-256 + static salt)

**File:** `workers/referrals-api/src/worker.js` lines 96–101

```js
async function hashPassword(password) {
  const data = encoder.encode("purebrain-salt:" + password);
  const hash = await crypto.subtle.digest("SHA-256", data);
  ...
}
```

Issues:
- Single static salt → identical passwords across users have identical hashes (rainbow-table-friendly)
- SHA-256 is a fast hash — a consumer GPU can do ~10B/s, so an 8-char password cracks in seconds if DB ever leaks
- No work factor / no per-user salt

**Fix required:** use bcrypt (via `bcryptjs` polyfill in Workers) or Argon2id. Cloudflare Workers don't natively expose bcrypt, but `@noble/hashes` includes scrypt/argon2 that work in the Workers runtime.

---

## 🟡 HIGH #4 — Reset tokens stored in plaintext

**File:** `workers/referrals-api/src/worker.js` line ~250 (forgot-password)

The 64-char reset token is stored in `password_reset_tokens.token` as plaintext. If the DB is ever exfiltrated, attacker gets live reset tokens for every pending request.

**Fix required:** store SHA-256(token) in DB; compare hashed value on `/reset-password`.

---

## 🟡 MEDIUM #5 — Email enumeration on `/lookup` and `/forgot-password`

`/lookup` returns 404 vs 200 depending on whether email exists.  
`/forgot-password` correctly returns the same message either way ✅, but `/session` returns "invalid credentials" vs "password_reset_required" — distinguishable.

**Fix:** uniform response shape regardless of whether account exists.

---

## 🟡 MEDIUM #6 — No rate limiting anywhere

`/session`, `/forgot-password`, `/lookup`, `/track`, `/register` — all unbounded. Enables:
- Password brute-force on `/session`
- Email-bombing victims via `/forgot-password`
- Spam click inflation via `/track` (fakes referral activity)

**Fix:** Cloudflare Rate Limiting rules per-endpoint, or `cf-connecting-ip`-keyed counter in KV.

---

## 🟡 MEDIUM #7 — Hardcoded admin token in proxy

**File:** `workers/purebrain-portal-proxy/src/worker.js` lines 206/219/233/247

```js
proxyHeaders.set('X-Admin-Token', 'purebrain-admin-2026');
```

Token is in plaintext in repo. Anyone with read access to the repo (or the `wrangler` deploy log) can call admin endpoints directly bypassing the portal.

**Fix:** move to Wrangler secret (`env.ADMIN_PROXY_TOKEN`), rotate the existing value (already exposed).

---

## 🟢 GOOD — Things done right
- Tool refactors (`agentmail_monitor.py`, `linkedin_*`, `purebrain_log_server.py`) **removed** hardcoded BAAS keys → env-only ✅
- `social-api` worker dropped 3,678 lines of inline HTML → moved to git/CF Pages (smaller attack surface) ✅
- `crypto.getRandomValues` used for token generation (correct CSPRNG) ✅
- D1 queries use parameterized `.bind(...)` everywhere I checked — no SQL injection ✅
- Password hash explicitly excluded from `REFERRER_PUBLIC_COLS` ✅

---

## Recommended Routing
- **Constitutional**: do NOT deploy current `workers/referrals-api/src/worker.js` to production until Critical #1 + #2 are fixed.
- Route to **ST#** (systems-technology) for the worker fixes.
- Route to **LC#** (legal-compliance) for breach-disclosure assessment if any production payouts have already been made through these endpoints.
- Rotate the `purebrain-admin-2026` token immediately.

---

**Next BOOP:** re-audit after referrals-api auth fixes land.
