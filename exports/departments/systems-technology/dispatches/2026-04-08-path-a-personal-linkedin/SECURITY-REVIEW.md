# security-engineer-tech: LinkedIn Publisher Security Review

**Agent**: security-engineer-tech
**Domain**: Security Engineering
**Date**: 2026-04-08
**Wave**: 2 of 4 (BUILD -> **SECURITY** -> QA -> SHIP)
**Reviewer**: security-engineer-tech
**Artifacts audited**:
- `exports/departments/systems-technology/apex-migration/pureapex-worker/src/linkedin.js` (491 lines)
- `tools/social_publisher.py` (531 lines)
- `exports/departments/systems-technology/dispatches/2026-04-08-path-a-personal-linkedin/social-publisher.service`
- `exports/departments/systems-technology/apex-migration/pureapex-worker/migrations/0002_linkedin_rate_limit.sql`
- Filesystem permission spot-checks on `.env`

---

## VERDICT: **APPROVED WITH CONDITIONS**

Wave 3 (QA) and Wave 4 (SHIP) are blocked until the **P0 conditions** below are satisfied. The P0 items are simple, mechanical fixes — they do not require rearchitecture. P1 items SHOULD be fixed before first live post but can land as a fast follow if Jared explicitly accepts the residual risk.

**No single Critical finding exists in isolation, BUT one Critical exists in combination**: `.env` file permissions + systemd EnvironmentFile loading = local-user token exposure. That is a Critical when taken as a system. Everything else is High or below.

---

## Findings by Severity

### CRITICAL

#### [C-1] `.env` is world-readable (644) and contains `INTERNAL_AUTH_TOKEN`
- **Location**: `/home/jared/projects/AI-CIV/aether/.env` — `stat` reports mode `644 jared jared`
- **Impact**: Any local user on the host can read `INTERNAL_AUTH_TOKEN`. Since the systemd unit uses `EnvironmentFile=/home/jared/projects/AI-CIV/aether/.env` and the Worker trusts `X-Internal-Auth` for the `post-with-image` endpoint without any second factor, an attacker with a shell on the host (even as an unprivileged user) can post arbitrary LinkedIn content as Jared until rate limit exhausts.
- **Brief requirement violated**: Section E — "`.env` is not world-readable (check: `stat .env`)".
- **Remediation** (P0 — MUST fix before ship):
  ```bash
  chmod 600 /home/jared/projects/AI-CIV/aether/.env
  # Optional hardening: move to /etc/aether/social-publisher.env owned by root, mode 640,
  # group = a dedicated 'aether' group that the service user belongs to.
  ```
- **Verification**: `stat -c '%a' .env` must return `600` (or `640` with group restriction).

---

### HIGH

#### [H-1] Rate limit check-then-act race allows ceiling bypass
- **Location**: `linkedin.js` lines 43–55 (`checkAndIncrementRateLimit`)
- **Evidence**:
  ```javascript
  const current = results.length > 0 ? results[0].count : 0;
  if (current >= 5) return { ok: false, current };
  await env.DB.prepare(
    'INSERT INTO linkedin_rate_limit (hour_key, count) VALUES (?, ?) ' +
    'ON CONFLICT(hour_key) DO UPDATE SET count = count + 1'
  ).bind(hourKey, current + 1).run();
  ```
- **Impact**: Two (or five) concurrent Worker invocations can each `SELECT` `count = 4`, each pass the `current >= 5` gate, and each increment. Final count = 9 (not 5). The 5 posts/hour ceiling becomes advisory, not enforced. A malicious or buggy publisher client can burst well past the ceiling. Brief Section D explicitly requires: "Counter cannot be bypassed via clock skew or key collision".
- **Remediation** (P0 — MUST fix before ship): Make the check atomic. Increment first, then test the *returned* row and reject + decrement (or use a conditional update).
  ```javascript
  // Ensure row exists
  await env.DB.prepare(
    'INSERT INTO linkedin_rate_limit (hour_key, count) VALUES (?, 0) ON CONFLICT(hour_key) DO NOTHING'
  ).bind(hourKey).run();
  // Conditional increment
  const upd = await env.DB.prepare(
    'UPDATE linkedin_rate_limit SET count = count + 1 WHERE hour_key = ? AND count < 5'
  ).bind(hourKey).run();
  if (upd.meta.changes === 0) {
    return { ok: false };
  }
  return { ok: true };
  ```
  D1 serializes writes per-database so the conditional UPDATE is the correct primitive. Verify `upd.meta.changes` is available in your Workers runtime; if not, read back the row after.
- **Note**: D1 is strongly consistent across Worker instances for writes to the same DB, so once the check is a single atomic UPDATE the multi-instance concern in Brief D is also satisfied.

---

#### [H-2] SSRF: `fetch(imageUrl)` follows redirects without re-validation
- **Location**: `linkedin.js` line 408 — `const imgResp = await fetch(imageUrl, { method: 'GET' });`
- **Impact**: The allowlist check runs on the *submitted* URL only. Cloudflare Workers `fetch` follows HTTP redirects by default. If any allowlisted host (`purebrain.ai`, `cdn.purebrain.ai`, `jareddsanborn.com`, etc.) is ever compromised, has an open-redirect endpoint, or serves attacker-controlled content, the redirect target is NOT re-checked against the allowlist. An attacker can chain `https://cdn.purebrain.ai/redirect?to=http://169.254.169.254/latest/meta-data/` and exfiltrate cloud metadata, internal services, etc. This is exactly the redirect-chain SSRF class the brief asks to flag.
- **Brief requirement violated**: Section C — "Rejects redirects to unsafe hosts (follow redirects manually and re-check, OR disable redirects)".
- **Remediation** (P0 — MUST fix before ship): Disable automatic redirects and fail closed.
  ```javascript
  const imgResp = await fetch(imageUrl, {
    method: 'GET',
    redirect: 'manual',  // Do not auto-follow
  });
  if (imgResp.status >= 300 && imgResp.status < 400) {
    return json({ success: false, error: 'redirect not allowed on image_url', stage: 'upload' }, 400);
  }
  if (!imgResp.ok) { ... }
  ```
  If redirects are actually needed (e.g., CDN signed URLs), manually follow them in a loop with a hop limit (max 3) and re-run `isImageUrlSafe` on each `Location` header.

---

#### [H-3] OAuth state parameter is set but never validated on callback
- **Location**: `linkedin.js` line 148 (sets `linkedin_oauth_state` cookie) and lines 154–240 (`/linkedin/callback` handler — never reads the cookie and never compares against `url.searchParams.get('state')`).
- **Impact**: OAuth CSRF. An attacker can trick a logged-in admin into visiting `/linkedin/callback?code=<attacker's code>` to bind the attacker's LinkedIn account to Pure Brain's D1 store. After this, every subsequent post goes to the attacker's LinkedIn profile. Note: this is pre-existing code not added in Wave 1, but it sits directly adjacent to the new endpoint and is exploitable today.
- **Brief requirement**: Not explicitly called out but falls under OWASP Broken Authentication (Section A / B scope).
- **Remediation** (P1 — SHOULD fix before first live post; can be fast-follow if Jared accepts residual risk):
  ```javascript
  const cookies = parseCookies(request.headers.get('Cookie'));
  const expectedState = cookies.linkedin_oauth_state;
  const receivedState = url.searchParams.get('state');
  if (!expectedState || !receivedState || !timingSafeEqual(expectedState, receivedState)) {
    return new Response('<h2>State mismatch</h2>', { status: 400, ... });
  }
  ```
  Also clear the cookie with `Max-Age=0` after successful exchange.

---

#### [H-4] Token refresh is not atomic — concurrent requests can invalidate each other
- **Location**: `linkedin.js` lines 58–101 (`getValidTokenRow`)
- **Impact**: Two concurrent `post-with-image` calls that arrive while the token is within the 5-minute refresh window will BOTH call LinkedIn's refresh endpoint with the same `refresh_token`. LinkedIn typically invalidates the old refresh token on first use and issues a new one. The second request will receive `invalid_grant` and the D1 row may be overwritten in an inconsistent order, potentially persisting a revoked refresh token and permanently breaking LinkedIn posting until manual re-authorization.
- **Brief requirement violated**: Section A — "Token refresh is atomic (no race where two requests both refresh)".
- **Remediation** (P1 — SHOULD fix before ship; acceptable as fast-follow because concurrent posts are rare at 5/hour ceiling):
  Use a D1 conditional UPDATE as a lightweight mutex. Example: add a `refresh_in_progress_until` column, `UPDATE ... SET refresh_in_progress_until = ? WHERE refresh_in_progress_until IS NULL OR refresh_in_progress_until < ?`, check `meta.changes`, if zero another request is refreshing — sleep 500ms and re-read the row. Alternatively, serialize through a Durable Object. Given publisher-side rate limit of 5/hour and `--once` polling style, real concurrency is essentially zero, so this is a correctness/defense-in-depth fix.

---

### MEDIUM

#### [M-1] Image size cap is enforced AFTER full download (DoS vector)
- **Location**: `linkedin.js` lines 408–416
- **Evidence**:
  ```javascript
  const imgResp = await fetch(imageUrl, { method: 'GET' });
  ...
  const imgBytes = await imgResp.arrayBuffer();  // <-- reads entire body
  if (imgBytes.byteLength > 10 * 1024 * 1024) {
    return json({ success: false, error: 'image exceeds 10MB cap' }, 413);
  }
  ```
- **Impact**: An allowlisted host serving a 500 MB file will cause the Worker to fully buffer the response before rejecting. Workers have strict memory and CPU limits; a multi-GB response can crash the isolate or cause 1101/1102 errors, creating a DoS. Size cap must be pre-flight.
- **Remediation** (P1): Check `Content-Length` header first and reject early; additionally stream-bound the body.
  ```javascript
  const cl = parseInt(imgResp.headers.get('content-length') || '0', 10);
  if (cl > 10 * 1024 * 1024) {
    return json({ success: false, error: 'image exceeds 10MB cap (content-length)' }, 413);
  }
  const ct = (imgResp.headers.get('content-type') || '').toLowerCase();
  if (!ct.startsWith('image/')) {
    return json({ success: false, error: 'content-type must be image/*' }, 415);
  }
  const imgBytes = await imgResp.arrayBuffer();
  if (imgBytes.byteLength > 10 * 1024 * 1024) { ... }
  ```

#### [M-2] Missing `Content-Type: image/*` validation on fetched image
- **Location**: `linkedin.js` line 408 — image response content-type is never inspected before pushing bytes to LinkedIn.
- **Impact**: Not a direct RCE, but allows polyglot/MIME-confusion and enables an attacker who can write to an allowlisted host to upload non-image binary content to LinkedIn. Brief Section C explicitly requires this check.
- **Remediation** (P1): Add the `content-type` check shown in M-1 remediation above.

#### [M-3] SSRF allowlist does not explicitly block IP literals / private ranges
- **Location**: `linkedin.js` lines 31–40 (`isImageUrlSafe`)
- **Impact**: The `Set` match on `u.hostname` implicitly rejects IP literals today (no `127.0.0.1` in the set). However there is no defensive block for `localhost`, `127.*`, `10.*`, `169.254.169.254`, IPv6 `::1`, or Unicode homoglyphs (e.g. `purebrаin.ai` with Cyrillic `а`). Since the check is a hard `Set.has()` on the parsed `URL.hostname`, most of these fail naturally — but a hostname like `purebrain.ai.` (trailing dot) or certain IDN representations *could* bypass if Node/Workers URL parser preserves them. The brief explicitly asks for private-IP blocks.
- **Remediation** (P1): Add an explicit deny list as defense in depth:
  ```javascript
  const host = u.hostname.toLowerCase().replace(/\.$/, '');  // strip trailing dot
  if (/^(127\.|10\.|192\.168\.|169\.254\.|0\.|::1$|localhost$)/.test(host)) return false;
  if (/\d+\.\d+\.\d+\.\d+/.test(host)) return false;  // any bare IPv4
  if (host.includes(':')) return false;  // IPv6 literal
  return allowedHosts.has(host);
  ```

#### [M-4] Bearer token sent with LinkedIn upload URL PUT
- **Location**: `linkedin.js` lines 418–424 — `PUT uploadUrl` with `Authorization: Bearer accessToken`.
- **Impact**: The LinkedIn asset `uploadUrl` is a pre-signed URL pointing to `linkedin-com-media-*.s3.amazonaws.com` or similar infrastructure. Per LinkedIn's media upload spec, this URL is typically authenticated via the embedded signature and the `Bearer` header is unnecessary. Sending the token to third-party storage infrastructure is unnecessary exposure. Not exploitable today (LinkedIn controls the endpoint), but violates principle of least exposure.
- **Remediation** (P2 — nice-to-have): Drop the `Authorization` header on the PUT step. Verify against current LinkedIn docs.

#### [M-5] OAuth callback leaks raw LinkedIn error body into HTML
- **Location**: `linkedin.js` line 189 — `<pre>${await tokenResp.text()}</pre>` on token exchange failure.
- **Impact**: Pre-existing. If LinkedIn returns an error response that includes sensitive context (request ID, partial client_id echo, etc.), it is rendered to the browser unescaped. This is also a reflected-HTML-injection surface if LinkedIn ever echoes attacker-controlled input.
- **Remediation** (P1): HTML-escape the body and/or return only `status` + a generic message.

#### [M-6] Systemd `ReadWritePaths` points to a file that may not exist
- **Location**: `social-publisher.service` line 28 — `ReadWritePaths=... /home/jared/projects/AI-CIV/aether/.social_publisher_state.json /home/jared/projects/AI-CIV/aether/data`
- **Impact**: systemd `ReadWritePaths` requires paths to exist at service start or the unit refuses to start. Also, granting rw to the entire `/data` directory is broader than the brief's intent ("logs + state file"). If `/data` contains secrets from other processes, this widens blast radius.
- **Remediation** (P1):
  - Pre-create `.social_publisher_state.json` in the install runbook, OR list its parent directory instead.
  - Remove `/data` unless the publisher actually writes there. Preferred:
    ```
    ReadWritePaths=/home/jared/projects/AI-CIV/aether/logs /home/jared/projects/AI-CIV/aether
    ```
    Actually, use narrower: make the state file path explicit and pre-touch it, keep logs dir.

---

### LOW

#### [L-1] `fire_post` logs worker response body on missing-url failure
- **Location**: `social_publisher.py` line 329 — `f"worker response missing linkedin_post_url: {data}"`
- **Impact**: If the Worker ever regresses and returns the access token in the response body (it currently does not), that token would be logged in plaintext and could be sent to Telegram via the alert path. Low because current Worker code is clean, but defensive pruning is cheap.
- **Remediation** (P2): Log only `data.keys()` or a whitelist of safe fields.

#### [L-2] Systemd unit log file permissions not set
- **Location**: `social-publisher.service` line 17–18 — `StandardOutput=append:/home/jared/projects/AI-CIV/aether/logs/social_publisher.systemd.log`
- **Impact**: systemd creates the log file with default umask. Combined with UMask=0027 in the unit it should be 640, but this is not explicitly verified. If Jared later runs the unit as root by accident, the log dir perms may flip.
- **Remediation** (P2): Document expected permissions in INSTALL runbook; add `chmod 640 logs/social_publisher.*.log` to install steps.

#### [L-3] Telegram alert on token-missing fires BEFORE masking
- **Location**: `social_publisher.py` lines 496–498
- **Impact**: Message is literal "INTERNAL_AUTH_TOKEN missing - aborted" — no secret in it. Safe. Informational only.
- **Remediation**: None.

---

### INFO (not counted toward verdict)

- **I-1**: `timingSafeEqual` in `linkedin.js` lines 20–28 — correctly short-circuits on length mismatch (a tiny timing leak for length but not for content, which is the industry-standard tradeoff). Early return on length is acceptable per NIST SP 800-107. The content comparison is constant-time. **PASS**.
- **I-2**: Fail-closed on unset `INTERNAL_AUTH_TOKEN` confirmed at line 341 (`!expected || !timingSafeEqual(...)`). **PASS**.
- **I-3**: D1 queries are all parameterized with `.bind()` — no string interpolation in SQL. **PASS**.
- **I-4**: Tokens never logged in `linkedin.js` or `social_publisher.py` — verified by grep. **PASS**.
- **I-5**: Systemd hardening is strong: `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome=read-only`, `PrivateDevices`, `CapabilityBoundingSet=` (empty), `MemoryDenyWriteExecute`, `SystemCallFilter=@system-service` with denies, `RestrictNamespaces`, `LockPersonality`, `RestrictSUIDSGID`, `ProtectKernel*`. Expect systemd-analyze score ~1.5–2.0 (GOOD). **PASS** subject to M-6 fix.
- **I-6**: Kill switch check happens first in every cycle (`run_cycle` line 381) before any action. **PASS**.
- **I-7**: Idempotency via `linkedin_post_url` check — uses fresh poll, not cached. **PASS**.
- **I-8**: Signal handlers (`SIGTERM`/`SIGINT`) flag shutdown cleanly without mid-cycle abort. **PASS**.
- **I-9**: Per-post try/except error isolation in cycle loop. **PASS**.
- **I-10**: Publisher-side rate limit (rolling 60-min window, persisted to state file) is separate from Worker-side limit. Defense in depth. **PASS**.
- **I-11**: No shell injection — publisher never uses `subprocess`/`shell=True`; all HTTP via `requests`/`urllib`. Logging uses `%s` formatting, not f-string interpolation into shell. **PASS**.
- **I-12**: No new pip dependencies beyond `requests` and `python-dotenv` which are already in the project. **PASS**.

---

## Compliance Matrix vs Brief Checklist A–G

| Section | Item | Status |
|--------|------|--------|
| **A. Token Handling** | tokens never logged / in responses | PASS |
| | refresh handles failure gracefully | PASS |
| | refresh is atomic | **FAIL — H-4** |
| | D1 parameterized | PASS |
| | INTERNAL_AUTH_TOKEN never in error bodies | PASS |
| **B. Internal Auth** | constant-time compare | PASS |
| | 401 reveals nothing | PASS |
| | no bypass path | PASS |
| | secret from env, not body | PASS |
| **C. SSRF** | https only | PASS |
| | allowlist enforced (no regex holes) | PASS (Set match) |
| | rejects IP literals / localhost / private | PARTIAL — **M-3** |
| | rejects unsafe redirects | **FAIL — H-2** |
| | size cap | PARTIAL — **M-1** (post-download only) |
| | content-type check | **FAIL — M-2** |
| **D. Rate limits** | 5/hour on worker | FAIL (race) — **H-1** |
| | 5/hour on publisher | PASS |
| | cannot be bypassed via race | **FAIL — H-1** |
| **E. Publisher Service** | .env not world-readable | **FAIL — C-1** |
| | kill switch every cycle | PASS |
| | signal handlers work | PASS |
| | no shell injection | PASS |
| | telegram no secrets | PASS |
| | idempotency authoritative | PASS |
| **F. Systemd Unit** | NoNewPrivileges | PASS |
| | ProtectSystem=strict | PASS |
| | ReadWritePaths minimal | PARTIAL — **M-6** |
| | ProtectHome | PASS (read-only) |
| | non-root user | PASS (jared) |
| | env file not world-readable | **FAIL — C-1** |
| **G. Rotation Plan** | documented | **MISSING** (required below) |

---

## Green-Light Conditions (P0 — MUST satisfy before Wave 3 QA runs)

The following MUST be completed and verified. Wave 3 (QA) may begin immediately after P0 items are verified; Wave 4 (SHIP) may begin after P0 + P1 are resolved or Jared explicitly accepts residual risk on P1.

### P0 (ship blockers)
1. **[C-1]** `chmod 600 /home/jared/projects/AI-CIV/aether/.env` and verify with `stat -c '%a' .env` returning `600`.
2. **[H-1]** Replace `checkAndIncrementRateLimit` with the atomic conditional UPDATE pattern shown above. Add a Worker integration test that fires 10 concurrent requests and asserts final D1 count == 5.
3. **[H-2]** Add `redirect: 'manual'` to the `fetch(imageUrl)` call in `linkedin.js:408` and reject 3xx responses. Add a regression test against an allowlisted redirect endpoint.

### P1 (strongly recommended before first live post)
4. **[H-3]** Validate OAuth `state` parameter in `/linkedin/callback` against the `linkedin_oauth_state` cookie (constant-time compare). Pre-existing but exploitable.
5. **[H-4]** Add refresh-token mutex using a D1 conditional UPDATE on `linkedin_tokens` (e.g., `refresh_in_progress_until`).
6. **[M-1]** Pre-flight `Content-Length` check before buffering response body.
7. **[M-2]** Add `Content-Type: image/*` check on image fetch.
8. **[M-3]** Add explicit deny list for private IPs / localhost / IPv6 literals in `isImageUrlSafe`.
9. **[M-5]** HTML-escape the LinkedIn error body in `/linkedin/callback` error page.
10. **[M-6]** Fix `ReadWritePaths` — pre-create `.social_publisher_state.json` in INSTALL runbook and remove `/data` from `ReadWritePaths` unless actually needed.

### Fast-follow (P2)
11. **[M-4]** Drop `Authorization` header from asset uploadUrl PUT.
12. **[L-1]** Tighten `fire_post` error logging to whitelist safe fields only.
13. **[L-2]** Document expected log file perms in INSTALL runbook.

---

## Secret Rotation Plan (Brief Section G)

**Required deliverable per brief — provided here:**

### Rotating `INTERNAL_AUTH_TOKEN`
1. Generate a new token: `openssl rand -hex 32` (32 bytes hex = 64 chars, min strength).
2. Update the Cloudflare Worker secret:
   ```bash
   cd exports/departments/systems-technology/apex-migration/pureapex-worker
   echo "NEW_TOKEN_VALUE" | npx wrangler secret put INTERNAL_AUTH_TOKEN
   ```
3. Update `.env`:
   ```bash
   chmod 600 .env
   sed -i "s/^INTERNAL_AUTH_TOKEN=.*/INTERNAL_AUTH_TOKEN=NEW_TOKEN_VALUE/" .env
   ```
4. Restart the publisher:
   ```bash
   sudo systemctl restart social-publisher.service
   sudo systemctl status social-publisher.service
   ```
5. Tail logs for ~2 minutes to verify next cycle succeeds:
   ```bash
   tail -f logs/social_publisher.log
   ```
6. Rollback plan: Keep the previous token value in a secure note for 1 hour; if the new token fails, re-run `wrangler secret put` with the old value and restart.

**Frequency**: Rotate every 90 days OR immediately on any suspected compromise.

### Rotating LinkedIn OAuth tokens
1. Visit `https://apex.purebrain.ai/linkedin/auth` while logged in as Jared.
2. Complete the LinkedIn OAuth flow. The callback handler auto-updates `linkedin_tokens` in D1 (`DELETE` + `INSERT`).
3. Verify with `GET /api/linkedin/status` showing `connected: true` and fresh `expires_at`.
4. LinkedIn refresh tokens live 365 days; re-auth before expiry.

**Frequency**: Whenever `linkedin_post_url` returns `invalid_grant` OR every 300 days proactively.

### Access Control
- **`.env` file**: Owner `jared`, mode `600`. Only the `jared` user and `root` can read.
- **Wrangler secret**: Only users with Cloudflare API token scoped to `purebrain-worker` can read/write. Limit to Jared + one backup admin.
- **D1 `linkedin_tokens` table**: Accessed only by the Worker runtime. No human dashboard reads the access_token column directly.
- **Telegram bot token**: In `config/telegram_config.json`, should be mode `600`. Verify separately.

---

## Summary

**Total findings**: 1 Critical, 4 High, 6 Medium, 3 Low, 12 Info-passed

**Verdict**: **APPROVED WITH CONDITIONS**

- The Wave 1 build is fundamentally sound. Hardening is thoughtful (constant-time compare, SSRF allowlist, kill switch, systemd lockdown, rate limiting, dry-run). The failures are mechanical, not architectural.
- The combination of `.env` being world-readable + systemd loading it = a Critical in context. Fixing `chmod 600` closes that gap in one command.
- The Rate-limit race (H-1) and SSRF-redirect gap (H-2) are both in the brief's hard-requirement list and MUST be fixed before first live post.
- OAuth state validation (H-3) is pre-existing but sits in the reviewed file — flagging it here so it doesn't get lost.

**Wave 3 (QA) may begin once P0 items 1–3 are fixed and verified.** QA should include the two regression tests noted (concurrent rate-limit burst; allowlisted-redirect rejection).

**Wave 4 (SHIP) requires P0 complete AND either P1 complete OR Jared's explicit written acceptance of residual risk on H-3/H-4/M-1/M-2/M-3/M-5/M-6.**

---

**Reviewer sign-off**: security-engineer-tech
**Date**: 2026-04-08
**Next reviewer**: QA agent (Wave 3) — proceed after P0 verification
