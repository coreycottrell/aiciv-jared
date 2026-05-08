# Admin Token Hardcode Removal — 2026-05-08

**Type**: teaching
**Topic**: Removing client-side hardcoded auth literals safely with server-validated replacement
**Branch**: main (worktree `/tmp/aether-main-wt`)
**Commit**: 83439b4
**Outcome**: SHIPPED-AND-VERIFIED

---

## What Worked

### 1. Distinguish two distinct hardcoded usages before fixing
Initial grep found 7 occurrences across 4 files, but they fell into two categories:

- **Header injection** (1×) — token sent over the wire as `X-Admin-Token`. Replacement: pull from `state.token` / `pw` (already in scope).
- **Login gate compare** (5×) — client-side string compare `pw === 'literal'` deciding whether to grant access. Replacement: trust the typed value, send to server, let server's `ADMIN_TOKENS` allowlist be authoritative.
- **Bypass branch** (1× in rebranded.html) — entire conditional block that skipped server validation. Replacement: delete the bypass, force everyone through the existing `/api/status` validation already present in the function.

Without this triage, you'd write the wrong replacement for half the locations.

### 2. Use the server as oracle for "is this token valid?"
The pattern that replaced ALL login gates:

```js
async function doAuth() {
  const pw = document.getElementById('auth-pw').value;
  if (!pw) { errorMsg('Enter password'); return; }
  const res = await fetch(DIRECT_API + '/admin/stats', {
    headers: { 'X-Admin-Token': pw }
  });
  if (res.ok) { TOKEN = pw; sessionStorage.setItem('admin-token', pw); init(); }
  else { errorMsg('Invalid password'); }
}
```

`/admin/stats` is a cheap GET that's already authenticated — perfect probe. No new endpoint needed.

### 3. Revalidate stored sessions on page load
Sessions that survived the rotation needed to be invalidated when the OLD token dropped from CSV. Don't trust `sessionStorage` blindly:

```js
const stored = sessionStorage.getItem('admin-token');
if (stored) {
  fetch(DIRECT_API + '/admin/stats', { headers: { 'X-Admin-Token': stored } })
    .then(r => r.ok ? showApp() : sessionStorage.removeItem('admin-token'));
}
```

### 4. Verify token state with curl BEFORE dropping CSV
Before `wrangler secret put` to remove OLD token, ran 3 curls:
- OLD → 200 (still in CSV)
- NEW → 200 (rotation worked)
- junk → 401 (gate works)

After secret put, ran the same 3:
- OLD → 401 (drop worked)
- NEW → 200 (still works)

This 6-curl matrix proves the operation took effect cleanly.

### 5. Separate worktree saved the day
`main` was already checked out at `/tmp/aether-main-wt` (cwd was on `referral-v1`). `git checkout main` failed with "already used by worktree". Switched cwd to the existing worktree — no rebase, no stash, no risk to the `referral-v1` work in progress.

---

## Gotchas

### `wrangler secret get` does not exist
Cloudflare secrets are write-only. To "rotate by removing a value from a CSV" you need to:
1. Read the desired value from local secret storage (`tools/.secrets/<name>.txt`)
2. `wrangler secret put` the new value (overwrites)

If `tools/.secrets/` doesn't have the prior CSV state, you cannot reconstruct it — must reset to a known value.

### `wrangler` requires `CLOUDFLARE_API_TOKEN` env var in non-interactive shells
The `.env` here uses `CF_API_TOKEN` — must remap before invoking wrangler:
```bash
export CLOUDFLARE_API_TOKEN=$(grep '^CF_API_TOKEN=' .env | cut -d= -f2-)
```

### CF Pages domains return 404 to HEAD on healthy URLs
Per `cf-pages-health-check-get-not-head` skill — always use GET with `-w "%{http_code}"`, never `curl -sI`.

### `cf-deploy.py` requires `--base-dir` when paths are relative to a deploy root
When deploying `admin/referrals/index.html` (path inside the site), set `--base-dir exports/cf-pages-deploy/`. Default base is also that, but explicit is clearer.

### Rebranded portal HTML is NOT served via CF Pages
`exports/purebrain-portal-rebranded.html` ships through the portal-proxy → tunnel → nginx → portal container path. Committing to git secures the source for next portal deploy, but the literal lives on in the running container until that pipeline runs. ST# would need a follow-up portal redeploy if the running portal still has the old token.

---

## Files Modified

- `exports/cf-pages-deploy/admin/referrals/index.html` (lines 734, 783)
- `exports/cf-pages-deploy/admin/referrals-unified/index.html` (lines 677, 701)
- `exports/cf-pages-deploy/admin/partners/index.html` (lines 563, 587)
- `exports/purebrain-portal-rebranded.html` (line 1646 + 8-line bypass branch)
- `workers/purebrain-portal-proxy/src/worker.js` (line 180 — comment sanitized)

## Receipt
`exports/portal-files/admin-token-hardcode-fix-receipt-2026-05-08.md`

## Reference Constitutional Memory
`feedback_pre_deploy_credential_scan.md` — pre-deploy credential scanning skill caught the original leak.
