# Admin Token Hardcode Removal — Receipt

**Date**: 2026-05-08
**Greenlight**: Jared (CEO), 2026-05-08
**Branch**: `main` (worktree `/tmp/aether-main-wt`)
**Commit**: `83439b4`
**Status**: SHIPPED-AND-VERIFIED

---

## Per-File Changes

### 1. `exports/cf-pages-deploy/admin/referrals/index.html`

| Line | Before | After |
|------|--------|-------|
| 734  | `opts.headers['X-Admin-Token'] = 'purebrain-admin-2026';` | `opts.headers['X-Admin-Token'] = state.token \|\| '';` |
| 783  | `if (pw === 'purebrain-admin-2026') { setToken('staging-admin-token'); showApp(); }` | Server-validated: `setToken(pw)` + `fetch('/admin/stats')` probe; `showApp()` only on 200, else `logout()` |

### 2. `exports/cf-pages-deploy/admin/referrals-unified/index.html`

| Line | Before | After |
|------|--------|-------|
| 677  | `if (pw === 'purebrain-admin-2026') { TOKEN = pw; sessionStorage.setItem(...); init(); }` | `async doAuth()`: `fetch('/admin/stats', X-Admin-Token: pw)` probe; allow only on 200 |
| 701  | `if (stored === 'purebrain-admin-2026') { TOKEN = stored; ... }` | Stored token revalidated against server; cleared from sessionStorage if rejected |

### 3. `exports/cf-pages-deploy/admin/partners/index.html`

| Line | Before | After |
|------|--------|-------|
| 563  | Identical literal-compare login pattern as referrals-unified | Same server-validated `async doAuth` |
| 587  | Stored-session literal compare | Same revalidation pattern |

### 4. `exports/purebrain-portal-rebranded.html`

| Line | Before | After |
|------|--------|-------|
| 1646 | `var ADMIN_BYPASS_TOKEN = 'purebrain-admin-2026';` + 8-line bypass branch (1657–1665) skipping `/api/status` validation | Entire literal + bypass branch removed; comment notes removal date. All auth now flows through `/api/status` server validation. |

### 5. `workers/purebrain-portal-proxy/src/worker.js` (sanitization-only)

Comment at line 180 sanitized to remove the literal string from source.

---

## Local Grep Verification

```
$ grep -rn "purebrain-admin-2026" exports/cf-pages-deploy/ exports/*.html workers/
(no output — exit 1)
```

**Zero hits across all targets.**

---

## Deploy

- **Tool**: `tools/cf-deploy.py` (NOT wrangler pages — banned)
- **Project**: `purebrain-production`
- **Deployment ID**: `5ce6743a-7d0e-49c4-9581-c4c4e22bd383`
- **URL**: `https://5ce6743a.purebrain-production-23b.pages.dev` → `https://purebrain.ai`
- **Files uploaded**: 3 (1 changed, 2 new — referrals-unified + partners were not previously deployed under `/admin/`)

### Live Verification (GET, not HEAD — per cf-pages-health-check skill)

```
=== https://purebrain.ai/admin/referrals/         === HTTP 200, hardcoded-token hits: 0
=== https://purebrain.ai/admin/referrals-unified/ === HTTP 200, hardcoded-token hits: 0
=== https://purebrain.ai/admin/partners/          === HTTP 200, hardcoded-token hits: 0
```

`purebrain-portal-rebranded.html` is committed but not deployed via CF Pages — it ships through the portal container path (separate ST# concern, source secured).

---

## ADMIN_TOKENS CSV Cleanup (referrals-api)

**Action**: `npx wrangler secret put ADMIN_TOKENS --name referrals-api` with value = NEW token only.

### Before/After Behavior

| Token | Pre-drop | Post-drop |
|-------|----------|-----------|
| OLD `purebrain-admin-2026` | HTTP 200 | **HTTP 401** ✅ |
| NEW `pbap_…` (rotated 2026-05-07) | HTTP 200 | **HTTP 200** ✅ |
| Junk | HTTP 401 | HTTP 401 |

Leaked literal is now fully invalid in production. Grace period closed.

---

## Auth Architecture (Post-Fix)

All admin HTML pages now delegate authentication to the server. The flow:

1. Admin types password into login gate.
2. Page fires `GET /admin/stats` with `X-Admin-Token: <typed-pw>`.
3. `referrals-api` validates against `ADMIN_TOKENS` allowlist (server-authoritative).
4. On 200: store token in `sessionStorage`/`localStorage`, show app.
5. On 401/other: clear stored token, show error.

Stored sessions revalidate against the server on every page load.

**No more client-side string literals.** No more bypass branches.

---

## Constitutional Compliance

- [x] Branch: `main` only (verified `git branch --show-current` = `main` before edit)
- [x] No `--hard`, `--force-push`, `--no-verify`
- [x] Pre-commit hooks: only `.sample` present (no active hook to skip)
- [x] Read-back after every edit
- [x] Deploy via `tools/cf-deploy.py` (NOT `wrangler pages deploy`)
- [x] Health check via GET (not HEAD)
- [x] Constitutional reference: `feedback_pre_deploy_credential_scan.md`

---

**STATUS: SHIPPED-AND-VERIFIED**
