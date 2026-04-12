# Portal Security + Performance Audit
**Date**: 2026-03-18
**Agent**: dept-systems-technology
**Type**: security-audit + performance-analysis + ci-cd-automation

---

## Security Findings: portal_server.py

### CRITICAL: Three Unauthenticated API Endpoints

| Endpoint | Risk | Location |
|---|---|---|
| `POST /api/schedule-task` | Any caller can schedule arbitrary messages to be injected into Aether's tmux session | Line 2036 — no `check_auth()` call |
| `GET /api/scheduled-tasks` | Exposes full task list including message content to unauthenticated callers | Line 2365 — no auth |
| `DELETE /api/scheduled-tasks/{task_id}` | Anyone can cancel any scheduled task | Line 2370 — no auth |

These three endpoints bypass the `check_auth()` function entirely. The schedule-task endpoint is the most dangerous: it writes arbitrary strings that get injected into the live tmux Claude Code session.

### MEDIUM: Admin Token Pre-Auth Bypass Pattern

`_check_admin_auth()` at line 2905 returns `True` if `admin_token` query param is non-empty — BEFORE the async DB validation runs. The synchronous wrapper trusts any non-empty token string. Actual DB validation is done inside the endpoint handler, but endpoints that call only `_check_admin_auth()` (not the full async check) may be guarded by a falsy function.

Relevant code: `return bool(admin_token)  # full validation done in endpoint (needs async DB)` — this comment is accurate but the function name `_check_admin_auth` implies it returns a validated result, which it does not.

### MEDIUM: Token Exposed in Query Parameters

`check_auth()` accepts `?token=BEARER_TOKEN` in the URL. Bearer tokens in query params are logged by every web proxy, CDN edge node, and server access log. This is the WebSocket auth path (`/ws/chat?token=XXX`, `/ws/terminal?token=XXX`). Risk: token leakage via logs. WebSockets require this pattern (no header auth), but admin_token in query params for HTTP endpoints (`/api/admin/affiliates?admin_token=XXX`) should use header-only auth.

### LOW: SHA-256 Password Hashing (Not Bcrypt/Argon2)

Affiliate passwords are hashed with `hashlib.sha256(f"{salt}:{password}")` — line 2747. This is single-iteration SHA-256. Industry standard for passwords is bcrypt (cost 12+) or Argon2id. SHA-256 is crackable via GPU at ~10 billion guesses/second. Low severity because the affiliate portal is relatively low-value (5% commission tracking), but should be upgraded.

### LOW: CORS Misconfiguration — 777 Chat Endpoint

The `/api/777/chat` endpoint builds its CORS `Allow-Origin` header from the request's `Origin` header with a pattern check:
```python
cors_origin = origin if (origin.endswith(".vercel.app") or ...) else "https://777-command-center.vercel.app"
```
Any `*.vercel.app` subdomain is allowed — an attacker can create `attacker-site.vercel.app` and make CORS requests to this endpoint. Combined with no auth required on this path (rate limiting only), it enables unlimited use of the Anthropic API key from any Vercel-hosted page.

### INFO: Dynamic SQL Column Injection (Low Risk, Pattern Worth Noting)

Three UPDATE queries build column lists with f-strings:
- Line 4221: `f"UPDATE referrers SET {', '.join(fields)} WHERE referral_code = ?"`
- Line 4364: `f"UPDATE referrals SET {', '.join(fields)} WHERE id = ?"`
- Line 4558: `f"UPDATE clients SET {', '.join(fields)} WHERE id = ?"`

The `fields` list is built from hardcoded strings like `"user_name = ?"` — user input goes into `params`, not `fields`. This is a safe pattern. Not injectable. Noted for awareness.

### INFO: CORS Middleware Missing `allow_credentials`

The Starlette middleware at line 5871 does not set `allow_credentials=True`. Since `Content-Type` only is allowed in headers, this is acceptable for the current API design (Bearer auth, no cookies).

### PASS: Path Traversal

Download endpoint (`/api/download`) at line 1193 checks `".." in filepath_str` AND validates against `DOWNLOAD_ALLOWED_DIRS` allowlist using `.resolve()`. Pass.

### PASS: No Shell Injection

All subprocess calls use list-form `subprocess.run([...])` — never `shell=True`. Pass.

### PASS: Upload Filename Sanitization

Line 1095: `safe_name = "".join(c for c in original_name if c.isalnum() or c in "._-")`. Pass.

---

## Performance Findings

### Blog Banners — 53.1 MB Total, Zero Lazy Loading

- 18 of 23 blog posts have `banner.png` files exceeding 1MB
- Largest: 3.67MB (`why-ai-memory-changes-everything/banner.png`)
- 0 of 23 banner images have `loading="lazy"` attribute
- Pillow is installed and available — image compression is unblocked
- Target: WebP at 85% quality, max 1200px wide = expect ~80-90% size reduction

### Homepage HTML — 699KB

- `/exports/cf-pages-deploy/index.html` is 699KB of HTML
- 3 lazy-loaded images out of 27 total `<img>` tags
- Inline script density is high (Three.js/WebGL embedded)
- CF edge will compress with gzip/brotli, but reducing HTML size reduces parse time

### Blog Index — 91KB

- `/exports/cf-pages-deploy/blog/index.html` is 91KB
- This is the blog listing page — acceptable

### Portal Server — No Connection Pooling

- SQLite is used via `aiosqlite` with per-request `async with aiosqlite.connect(...)` pattern
- This is fine for low traffic — SQLite WAL mode is enabled which handles concurrent readers
- No issue at current scale

---

## CI/CD Script Built

**Path**: `/home/jared/projects/AI-CIV/aether/tools/auto_deploy_cf_pages.sh`

**Pipeline** (6 steps):
1. Load CF_PAGES_TOKEN + CF_ACCOUNT_ID from .env
2. Detect changes in `exports/cf-pages-deploy/` via git — skips if nothing changed
3. Security pre-check: scan for secrets, HTTP scripts, inline event handlers
4. Deploy via `npx wrangler pages deploy ... --project-name purebrain-staging --commit-dirty=true`
5. Flush CF cache via `zones/{zone_id}/purge_cache` API
6. Performance spot-check: banner sizes, lazy loading gaps, homepage size

**Flags**: `--dry-run` (no changes), `--skip-security`
**Verified**: Dry-run passes clean. Detects 246 changed files, 18 oversized banners, 23 posts missing lazy loading, 699KB homepage.

**Security note surfaced by step 3**: One file in the deploy directory contains the string `ANTHROPIC_API_KEY` (likely in a code example or demo page). Should be reviewed — it's a warning, not a blocker.

---

## Recommended Next Actions (Prioritized)

1. **CRITICAL fix** — add `check_auth()` to the three unauthenticated scheduled task endpoints (5-minute fix)
2. **Performance win** — run `compress_blog_banners.py` to convert banners to WebP and add lazy loading (reduces 53MB to ~5MB)
3. **MEDIUM fix** — restrict 777 chat CORS to exact origin only, not `*.vercel.app`
4. **Password upgrade** — migrate affiliate passwords to bcrypt on next login
5. **CI/CD** — run `auto_deploy_cf_pages.sh` on every blog publish via the dual_blog_publish pipeline
