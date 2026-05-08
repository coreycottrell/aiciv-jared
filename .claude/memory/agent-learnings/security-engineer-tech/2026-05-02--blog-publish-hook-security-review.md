# security-engineer-tech: Blog Publish-Hook Security Review (B8)

**Agent**: security-engineer-tech
**Domain**: Security Engineering
**Date**: 2026-05-02
**Type**: teaching + operational
**Topic**: B8 SECURITY gate for blog-publish-hook Worker + social-api system-role bypass + bsky session healer

---

## Verdict

**READY FOR B9 QA** — with TWO HIGH findings that QA must verify and ONE HIGH operational follow-up. No CRITICAL findings. Patch is small, additive, and follows the same trust tier as the existing ContentRouter system path.

**Severity counts**: 0 CRITICAL · 2 HIGH · 4 MEDIUM · 4 LOW · 3 INFO

The system-role bypass is correctly bounded (read on for the multi-tenant analysis). The cron worker is idempotent under retry. The session healer doesn't leak credentials. Two HIGH issues are about hardening the trust assumption, not breaking it — they belong in the QA/SHIP window, not as a BUILD rework.

---

## Files Reviewed

- `/home/jared/projects/AI-CIV/aether/workers/blog-publish-hook/wrangler.toml`
- `/home/jared/projects/AI-CIV/aether/workers/blog-publish-hook/src/worker.js` (370 LOC)
- `/home/jared/projects/AI-CIV/aether/workers/blog-publish-hook/migrations/0001_published_blog_posts.sql`
- `/home/jared/projects/AI-CIV/aether/workers/blog-publish-hook/migrations/0002_content_items_metadata.sql`
- `/home/jared/projects/AI-CIV/aether/workers/blog-publish-hook/DEPLOY.md`
- `/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js` — patched `handleCreateContent` (lines 3928-3994) + `getSession()` (lines 3705-3737)
- `/home/jared/projects/AI-CIV/aether/tools/bsky-session-health/check_and_heal.py`
- Reference: `/home/jared/projects/AI-CIV/aether/shared/social-api-schema.sql` (social_accounts, content_items)
- Spec: `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md` v2

---

## Open-Question Decision (CTO requested explicit security ruling)

> Should the new optional `target_user_id` system-override field be gated to an allowlist of known house-account owners, or is the current trust model acceptable?

**Decision**: **Acceptable as written for B7 SHIP, BUT add a structural allowlist within 14 days post-ship.** Track as HIGH-2 below.

**Rationale**:

1. **Real blast radius today is bounded by token possession, not by `target_user_id` semantics.** Any caller already in possession of `ROUTER_API_KEY` (the synthetic system session) is at the same trust tier as ContentRouter. ContentRouter today already has `system` role permissions of `{read, create, edit, delete, approve, manage_roles}` (worker.js:3649). The optional `target_user_id` field does not grant a meaningfully larger capability than what `ROUTER_API_KEY` already implies.

2. **The bypass branch only reads `target_user_id` when `sess.role === "system"`** (worker.js:3955-3960). A compromised non-system token cannot trigger the override.

3. **However**, "target_user_id can be ANY user_id in the users table" violates least-privilege. Today there are exactly two known machine callers (ContentRouter + blog-publish-hook), each addressing exactly one or two house accounts (@purebrain.ai bsky, plus future house accounts). An attacker holding `ROUTER_API_KEY` could write content_items into any team's queue, attributable to that team's owner — a cross-tenant content-pollution / impersonation primitive. This is not a privilege escalation in the auth sense (they already have `system`, the highest role), but it IS an attribution-tampering primitive that bypasses "what user_id owns this content."

4. **Right hardening posture**: `target_user_id` should be validated against an explicit allowlist — either:
   - A `social_accounts.is_house_account BOOLEAN` column, OR
   - A new `house_accounts(user_id, social_account_id, allowed_callers)` table, OR
   - At minimum a hard-coded allowlist constant in worker.js (least-good but acceptable for v1).

   Without this, a leaked `ROUTER_API_KEY` lets an attacker inject content into any user's account/feed for any user_id they pick. With the allowlist, the leak still grants `system` role but content attribution is bounded to known house accounts.

5. **For B7 SHIP**: the blog-publish-hook deploys WITHOUT calling `target_user_id` (it relies on the default `houseAcct.user_id` resolution path — see worker.js:3960 — and BLOG_HOOK_HOUSE_ACCOUNT_ID secret narrows the social_account_id input). So the *currently shipping caller* does not exercise the override. Ship as-is, then patch the override semantics in a follow-up PR.

**Locked HIGH-2 follow-up**: Within 14 days of B7 SHIP, social-api must constrain `target_user_id` to an allowlist (house accounts table or equivalent). Owner: ptt-fullstack. Track via dept-routing memo.

---

## Findings

### CRITICAL — None

---

### HIGH-1 — Token rotation creates a coupling foot-gun

**Location**: `workers/blog-publish-hook/wrangler.toml:10-11` + `workers/social-api/src/worker.js:3717` + `DEPLOY.md:161`

**Evidence**:
```toml
# wrangler secret put SOCIAL_API_SYSTEM_TOKEN     # value = social-api ROUTER_API_KEY
```
```javascript
// social-api worker.js:3716-3727
if (env.ROUTER_API_KEY && token === env.ROUTER_API_KEY) {
  return { user_id: "system", role: "system", ...
```

The hook Worker's `SOCIAL_API_SYSTEM_TOKEN` MUST equal social-api's `ROUTER_API_KEY` (string equality at line 3717). DEPLOY.md correctly notes this. Risk: when ROUTER_API_KEY is rotated (security best practice = quarterly), the hook silently 401s on every cron tick until SOCIAL_API_SYSTEM_TOKEN is updated. There's no monitoring on `result.failed > 0` aside from the `/status` endpoint that no one is paged on.

**Why HIGH not MEDIUM**: rotation is a foreseeable operation. Silent failure during rotation = repeat of the original 20-day @purebrain.ai dormancy this whole project exists to prevent.

**Remediation** (QA can validate):
1. Wire the cron tick's `result.failed` counter to the existing nightly monitor (the `OP#` poll over D1 `published_blog_posts` per spec v2.7)
2. DEPLOY.md should add a "Rotation Runbook" section — step-by-step paired secret update for both Workers in the same maintenance window
3. Consider supporting BOTH old and new ROUTER_API_KEY simultaneously during a rotation window (the existing `getSession()` branch could check `[ROUTER_API_KEY, ROUTER_API_KEY_PREVIOUS]`)

---

### HIGH-2 — `target_user_id` lacks allowlist (cross-tenant content injection primitive)

**Location**: `workers/social-api/src/worker.js:3960`

**Evidence**:
```javascript
ownerUserId = body.target_user_id || houseAcct.user_id;
```

System-role callers can set `target_user_id` to ANY value, which is then written verbatim as `content_items.user_id`. There is no check that the target user_id corresponds to a sanctioned house account or an account the caller is permitted to write on behalf of.

**Real risk**: anyone with `ROUTER_API_KEY` (a string secret) can inject draft kanban rows attributed to any team, with arbitrary body text. They could plant draft content in a competitor team's queue that, if approved by an unwary reviewer, posts to that team's social account. Or simply pollute a queue to cause noise/distrust.

**Why this didn't get a CRITICAL**: No real-world caller exercises this today (blog-publish-hook does not pass `target_user_id`). And the trust gate is still ROUTER_API_KEY possession, which already implies `system` role for everything else. So it's a defense-in-depth gap, not an active vulnerability.

**Remediation** (locked as 14-day post-SHIP follow-up — see Open-Question Decision above):
1. Add `social_accounts.is_house_account BOOLEAN DEFAULT false` column
2. Mark @purebrain.ai bsky row + any future house accounts as `is_house_account = true`
3. In `handleCreateContent` system branch, if `target_user_id` provided, require it to match the user_id of a row where `is_house_account = true`
4. Add WARN log on every system-role write that uses `target_user_id` (visibility into legitimate-vs-anomalous use)

```javascript
// Proposed hardening
if (sess.role === "system") {
  const houseAcct = await env.DB.prepare(
    "SELECT id, user_id, is_house_account FROM social_accounts WHERE id = ?"
  ).bind(body.social_account_id).first();
  if (!houseAcct) return err(404, "social account not found");
  if (!houseAcct.is_house_account) return err(403, "system role may only write to house accounts");
  if (body.target_user_id) {
    if (body.target_user_id !== houseAcct.user_id) {
      // Strictly require target_user_id to match the house account's owner.
      // No cross-team write capability.
      return err(403, "target_user_id must match house_account.user_id");
    }
    console.warn(`[system-role-write] target_user_id=${body.target_user_id} acct=${body.social_account_id}`);
  }
  ownerUserId = body.target_user_id || houseAcct.user_id;
}
```

---

### MEDIUM-1 — `/run` admin endpoint reuses the SOCIAL_API_SYSTEM_TOKEN as its own auth secret

**Location**: `workers/blog-publish-hook/src/worker.js:333-340`

**Evidence**:
```javascript
if (url.pathname === "/run" && request.method === "POST") {
  const auth = request.headers.get("authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  if (!env.SOCIAL_API_SYSTEM_TOKEN || token !== env.SOCIAL_API_SYSTEM_TOKEN) {
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401, headers: { "content-type": "application/json" }
    });
  }
```

The manual-trigger endpoint authenticates with the same secret used for outbound social-api calls. Two issues:

1. **Token reuse blast radius** — leaking either the hook's manual trigger or social-api's ROUTER_API_KEY leaks BOTH capabilities (manual cron + system role on social-api).
2. **String comparison is non-constant-time** — `token !== env.SOCIAL_API_SYSTEM_TOKEN` is timing-attackable in principle. CF Workers run on isolates with short-lived state, and the practical attack surface is small (no user-controlled iteration), but it's a known anti-pattern.

**Remediation**:
1. Add a separate `BLOG_HOOK_ADMIN_TOKEN` secret for `/run` (different from outbound auth)
2. Use a constant-time compare for token comparisons in any future authenticated endpoints (CF Workers don't ship one natively; can implement: XOR-and-OR loop, only acceptable when lengths are equal — and require length equality first)

**Acceptable for B7 SHIP**: `/run` is a low-frequency admin endpoint, not user-facing, and the token is already the shared system tier. Address in a follow-up.

---

### MEDIUM-2 — D1 `markFailed()` truncates `last_error` to 500 chars without logging the full payload

**Location**: `workers/blog-publish-hook/src/worker.js:215-221`

**Evidence**:
```javascript
async function markFailed(env, slug, errorMsg, retryCount) {
  await env.DB.prepare(
    `UPDATE published_blog_posts SET status = 'failed', last_error = ?, retry_count = ? WHERE slug = ?`
  ).bind(errorMsg.slice(0, 500), retryCount, slug).run();
}
```

500 chars is fine for storage, but the full HTTP body from social-api is dropped (no `console.log(errorMsg)` of the full content before truncation). For debugging, full payload should be logged via `wrangler tail` even if D1 row is truncated.

`postToSocialApi()` already returns the full body, but errors are sliced at 300 chars in `runTick()` (line 305) before reaching `markFailed`. Minor security concern: an attacker probing the hook to learn social-api error semantics gets less info than they would from a verbose log. So this is **defense against information disclosure to the attacker** — but it ALSO hampers blue-team forensics. Wash.

**Remediation**: log full `errMsg` to `console.log` (which goes to `wrangler tail`, not D1), then truncate for D1 storage. Net effect: full info for ops, bounded info for D1.

---

### MEDIUM-3 — `metadata` column persists raw JSON-stringified object — no input validation on length or content

**Location**: `workers/social-api/src/worker.js:3970-3977`

**Evidence**:
```javascript
let metadataStr = null;
if (body.metadata != null) {
  metadataStr = (typeof body.metadata === "string")
    ? body.metadata
    : JSON.stringify(body.metadata);
}
```

The metadata field is opaque — accepted as-is and stored. A system-role caller (or anyone with ROUTER_API_KEY) could write arbitrarily large metadata blobs (D1 has no per-column length cap by default), causing storage bloat over time. Probably bounded in practice by D1's row-size limits, but no defensive cap.

Also: there's no validation that the JSON parses or is safe to render in the kanban UI. If the kanban UI ever interpolates `metadata` into HTML without escaping, this becomes a stored XSS vector. (Outside this PR's scope — flag for separate UI review.)

**Remediation**:
1. Cap `metadataStr.length` at e.g. 4096 chars before INSERT (return 400 if exceeded)
2. Optionally `JSON.parse` then `JSON.stringify` to canonicalize and reject malformed JSON

**For B7 SHIP**: not a blocker — the only system-role caller (blog-publish-hook) writes a fixed ~200-char metadata blob. Track for hardening sprint.

---

### MEDIUM-4 — Self-healing BOOP — re-login probe creates a second session and discards it

**Location**: `tools/bsky-session-health/check_and_heal.py:144-152`

**Evidence**:
```python
c = Client()
c.login(user, pw)
session_str = c.export_session_string()
# Verify the new session works before persisting (probe).
c2 = Client()
c2.login(session_string=session_str)
c2.get_author_feed(actor=HANDLE, limit=1)
written = write_session_string(session_str)
```

Each heal cycle creates two atproto sessions (the login + a session-string load to verify). atproto sessions are server-side records — Bluesky may rate-limit or revoke if heal cycles run pathologically often (e.g. a misconfigured `.env` triggers heal every cron tick = N session creations per day).

**Remediation**:
1. Add a heal-cycle rate limit — write a `last_heal_at` timestamp to a local file; refuse to heal more than once per 6 hours unless `--force` flag passed
2. Log the heal cycle to a dedicated audit log (`logs/bsky-session-health.log`), not just stdout/stderr, so OP# can see frequency

**For B7 SHIP**: heal triggers are gated by `status == "expired"` which in turn requires server rejection — not easily abusable. Run cadence is daily not per-tick. Acceptable but track.

---

### LOW-1 — `parseBlogIndex` regex is greedy on title text — minor XSS surface if title contains malicious markup

**Location**: `workers/blog-publish-hook/src/worker.js:63`

**Evidence**:
```javascript
const re = /<a\s+class="wp-block-latest-posts__post-title"\s+href="\/blog\/([a-z0-9][a-z0-9-]*)\/?"[^>]*>([^<]+)<\/a>\s*<time\s+datetime="([^"]+)"/gi;
```

Title capture is `[^<]+` — stops at first `<`. So angle-bracket-based XSS payloads in the WP title cannot escape the capture. HTML entities like `&amp;` are decoded by `decodeHtml()`. No `<script>` injection vector here.

**However**: title is rendered into `body` of the kanban draft via `buildThreadDraft()`. If the kanban UI rendering treats `body` as HTML (it shouldn't, kanban renders as text), an `onclick=` or unicode-control-char payload in a title could surface in the UI.

**Remediation**: confirm the kanban frontend renders `body` as text (textContent / template-bind), not HTML (innerHTML / dangerouslySetInnerHTML). Out-of-scope for this PR but worth a `social-api-frontend` follow-up.

---

### LOW-2 — `decodeHtml()` is incomplete — only handles 6 entities

**Location**: `workers/blog-publish-hook/src/worker.js:80-88`

Only handles `&amp; &lt; &gt; &quot; &#39; &nbsp;`. WordPress titles can contain `&hellip;`, `&mdash;`, `&#8217;`, etc. These will display as raw entity strings in the kanban draft. Not a security issue, just a content-quality miss.

**Remediation**: use a more complete decoder, or accept the truncated entity set as known limitation. Not blocking.

---

### LOW-3 — Migration 0002 is non-idempotent

**Location**: `workers/blog-publish-hook/migrations/0002_content_items_metadata.sql:13`

```sql
ALTER TABLE content_items ADD COLUMN metadata TEXT;
```

D1's SQLite has no `ADD COLUMN IF NOT EXISTS`. Re-running this migration after the column exists will error. DEPLOY.md correctly mitigates with a manual `PRAGMA table_info` check first, but human ops will eventually skip the check.

**Remediation**: either ship a tiny idempotency wrapper script (PRAGMA + conditional ALTER) or accept the manual gate. Not blocking — DEPLOY.md is the authoritative source.

---

### LOW-4 — Telegram alerts in session healer use HTTP API but plaintext token in process env

**Location**: `tools/bsky-session-health/check_and_heal.py:65-76`

`TG_BOT_TOKEN` lives in `.env`. The healer reads it in plaintext, never logs it. Standard for the codebase. No credential exfil risk *in this script*. Flag only because Telegram tokens have full bot capability if leaked — keep `.env` perms tight.

**Remediation**: confirm `.env` is mode 600 (matches existing constitutional rule). Out-of-scope for this PR.

---

### INFO-1 — `getFirstDeployTimestamp()` race handling is correct (A5)

**Location**: `workers/blog-publish-hook/src/worker.js:103-120`

`INSERT OR IGNORE` followed by re-read pattern correctly handles the case where two cron ticks race on first deploy. Documented intent matches code. Good.

---

### INFO-2 — Cron retry idempotency is correct

**Location**: `workers/blog-publish-hook/src/worker.js:268-309`

Idempotency claim verified:
- `published_blog_posts.slug` is PRIMARY KEY → `INSERT ... ON CONFLICT(slug) DO NOTHING` blocks duplicate inserts (worker.js:208)
- New post path inserts BEFORE returning success → on Worker timeout mid-tick, the next tick sees the slug as `known`, skips the duplicate POST
- Failed-then-retry path uses UPDATE not INSERT — no duplicate FK on retry
- One subtle case: if `postToSocialApi()` succeeds but `insertPost()` fails (D1 outage during post-success window), the next tick will see the post as "new" and POST a duplicate to social-api. Mitigation: social-api could enforce uniqueness on `(metadata->>'slug')` but currently doesn't. Frequency = 0 in practice; D1 is highly available. Track as known small-window risk in INFO not LOW.

---

### INFO-3 — File permissions on `bsky_session.txt` correctly enforced

**Location**: `tools/bsky-session-health/check_and_heal.py:79-90`

`p.chmod(stat.S_IRUSR | stat.S_IWUSR)` = 0600. Both canonical paths receive the same perms. `mkdir(parents=True, exist_ok=True)` does NOT inherit 0700 on the parent dir — verify parent dir perms separately. Flag only.

**Recommendation for QA**: add a check that `.claude/` and `.claude/from-jared/bsky/bsky_automation/` are mode 700 or 755 (acceptable since session FILE is 600). Not blocking.

---

## Constitutional Compliance Check

| Rule | Status | Note |
|------|--------|------|
| No container deploys | ✅ PASS | All deploys are CF Workers / D1 / R2 |
| social.purebrain.ai is source of truth | ✅ PASS | Hook writes to `/api/content` first, never bypasses kanban |
| `wrangler pages deploy` BANNED | ✅ PASS | Uses `wrangler deploy` (Workers, not Pages) — A6 confirmed |
| No PII in logs | ✅ PASS | Logs slugs, status, error counts. No user data, no tokens. |
| Token storage 0600 | ✅ PASS | Healer enforces 0600 on session files |
| `.env` not committed | ✅ PASS (assumed) | Repo `.gitignore` covers `.env` per existing convention |
| Multi-tenant query scoping preserved | ✅ PASS | `handleListContent` still scopes `WHERE user_id = ?` (worker.js:3917) — system caller writes are attributed to real owners, so existing tenant queries still work without leakage |

---

## Multi-Tenant Scoping Analysis (CTO requested)

> Does the bypass correctly preserve multi-tenant query scoping?

**Yes** — verified by tracing the data flow:

1. Hook writes content_item with `user_id = houseAcct.user_id` (worker.js:3960). NOT `user_id = "system"`.
2. `handleListContent` (worker.js:3917) filters on `user_id = sess.user_id`. A system caller (with `sess.user_id = "system"`) hitting GET /api/content sees ZERO items because no items have `user_id = "system"`. This is correct: machine callers cannot list, only write.
3. Real human owners of @purebrain.ai bsky account see content_items they "own" (per the houseAcct.user_id). Other teams see nothing.
4. `handleUpdateContent` checks `existing.user_id !== sess.user_id` with role-based bypass for leader/system/admin/owner/reviewer (worker.js:4039) — system can edit cross-tenant, which is consistent with its current trust tier.

**Conclusion**: The bypass does not create a tenant-isolation regression. It cleanly maps system writes onto real human ownership records.

---

## Pattern Learned (memory-write)

**Pattern: System-role bypass with house-account ownership resolution**

When a machine caller needs to write into a multi-tenant system on behalf of a "shared" resource (a house account that multiple humans operate):

- Do NOT make the machine the owner (`user_id = "system"`) — this breaks tenant queries
- DO resolve the owning user_id from the resource (the social_account row in this case)
- DO require the resource lookup to succeed BEFORE accepting the write (404 on missing)
- DO gate the override field (`target_user_id`) to an allowlist of known house resources (the gap addressed in HIGH-2)

This pattern generalizes to any system where a cron/worker writes on behalf of a shared identity (welcome-email-api writing for "support", agentmail-webhook writing for "noreply", etc.).

**Anti-pattern**: filtering content visibility by `user_id = "system"` for machine writes — creates a parallel namespace that bypasses tenant scoping silently and accumulates orphaned records.

---

## Recommendations to QA (B9)

1. **Verify HIGH-1 monitoring path** — confirm `/status` endpoint surfaces failed counts, and that OP# pair-verify (B11) includes a check on `published_blog_posts.status='failed'` count.
2. **Verify HIGH-2 follow-up tracked** — confirm a dept-routing memo opens for the 14-day allowlist hardening before this review closes.
3. **Functional regression test** — non-system caller (real session token) POSTing `target_user_id` should be IGNORED (the override branch only fires under `sess.role === "system"`). Add explicit test: "regular user passing target_user_id can't change ownership."
4. **Smoke test the rotation runbook** — DEPLOY.md says rotation requires paired update; QA can simulate by changing SOCIAL_API_SYSTEM_TOKEN to a wrong value and confirming `result.failed` increments.
5. **Healer sanity check** — write a garbage session string, run healer, confirm both canonical paths refresh + perms stay 0600.

---

## Verdict for B9 dispatch

**READY FOR B9 QA.**

No CRITICAL findings. Two HIGH findings are operational hardening (rotation monitoring + target_user_id allowlist) — both acceptable to track post-SHIP because:
- HIGH-1's failure mode is detectable in monitoring (OP# B11 covers the human gate)
- HIGH-2's exploit requires `ROUTER_API_KEY` possession, which is already system-tier trust; the gap is defense-in-depth not active vuln, and the only shipping caller doesn't exercise the override

QA + ptt-qa can proceed. No BUILD rework needed.

— security-engineer-tech, 2026-05-02
