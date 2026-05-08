# Brevo (Sendinblue) API Key Rotation Plan — Push Protection Unblock

**Date**: 2026-05-07
**Trigger**: GitHub Push Protection blocked `git push origin main` (20 commits unpushed, includes today's MED-003 ship)
**Severity**: HIGH — key is live, embedded in client-side JS, can send email as `purebrain@puremarketing.ai`
**Mode**: READ-ONLY blueprint. No execution.

---

## 1. Leaked Key Location

| Field | Value |
|-------|-------|
| Commit | `107019b` (May 6, 2026) |
| File | `exports/cf-pages-deploy/contact-us/index.html` |
| Line | 700 |
| Key prefix | `xkeysib-9f` (full value never pasted here) |
| Label suffix | `b6IZ1DP4edoZ04N9` |

**Second key, same Brevo account**: suffix `OFEvnlWpddKYafW5`, hardcoded at `tools/deploy_v486_subscribe_fix.py:352`. Both share master `9f445c4c...` — **rotate together**.

---

## 2. Active Usage in Codebase

**Env-driven (good — just update `BREVO_API_KEY`)**:
- `tools/website_analysis_delivery.py`
- `tools/neural_feed_welcome_sequence.py`
- `tools/brevo_create_welcome_templates.py`
- `tools/create_brevo_workflow.py`

**Hardcoded (must scrub)**:
- `tools/deploy_v486_subscribe_fix.py:352` (`OFEvn...` variant)
- `exports/cf-pages-deploy/contact-us/index.html:700` (the leak)

**Sprawl**: 60+ historical files in `exports/` (HTML/JSON backups) contain the `OFEvn...` variant. Archives only — once keys are deactivated, these become harmless strings.

**Live status**: `https://purebrain.ai/contact-us/` returns **HTTP 404**. The leaked file is in source/commit but not currently deployed. Push Protection caught it before deploy.

---

## 3. Brevo Account Purpose

- Sender: `purebrain@puremarketing.ai` (PMG account, Jared admin)
- Used for: contact-form submissions, Neural Feed welcome sequence, WordPress subscribe plugin, website-analysis lead delivery
- Abuse risk: spoofed sends from PT domain, contact list extraction

---

## 4. Rotation Plan

1. **Login** https://app.brevo.com (PT admin)
2. **Navigate** Settings → SMTP & API → API Keys
3. **Identify** by labels `b6IZ1DP4edoZ04N9` + `OFEvnlWpddKYafW5`
4. **Generate** two new keys, descriptive labels (e.g., `prod-server-2026-05`, `wordpress-plugin-2026-05`)
5. **Update consumers** *before* deactivating old keys:
   - Local `.env` → `BREVO_API_KEY=...`
   - Cloudflare Worker secrets (`wrangler secret put BREVO_API_KEY`) if used
   - WordPress `wp-config.php` `define('BREVO_API_KEY', ...)`
   - Refactor `deploy_v486_subscribe_fix.py:352` to read env, not hardcode
   - **Do NOT redeploy `contact-us/index.html` with a new client-side key.** Refactor to CF Worker proxy (server-side only).
6. **Deactivate (don't delete)** old keys in Brevo — preserves audit log
7. **Verify**: send test email via `website_analysis_delivery.py`; confirm WP subscribe still works; check next welcome-sequence send
8. **Unblock GitHub**: follow Push Protection unblock URL from the original blocked-push terminal output, attest "secret revoked", retry `git push origin main`

---

## 5. Risks

- **Downtime**: Step 5 (update consumers) MUST precede Step 6 (deactivate). Otherwise contact form, welcome sequence, subscribe plugin all break. ~5 min coordinated window.
- **Audit recommended**: Before deactivating, pull Brevo's API key usage logs (last 30d). Look for unusual volumes, unknown source IPs, contact-list exports. Rotation alone is insufficient if abuse already occurred.
- **History persists**: Constitutional rule bans force-push, so leaked key stays in commit `107019b` forever. Push Protection unblock URL whitelists that specific blob — correct path.
- **Future-proofing**: Move all email sends server-side via CF Workers. Never put API keys in client-side `<script>` again.

---

## 6. Pre-Rotation Checklist (Jared)

- [ ] Brevo admin login confirmed
- [ ] `.env` ready to update
- [ ] WordPress admin access ready (`wp-config.php`)
- [ ] CF Worker secret path identified (if any)
- [ ] 5-min low-traffic window allocated
- [ ] Push Protection unblock URL saved from blocked-push output
- [ ] Decided: refactor `contact-us` to CF Worker before any redeploy

**Estimated time**: 15–20 min.

---

**Authored**: security-auditor (read-only, 2026-05-07)
**Compliance**: ✅ No execution. ✅ No full key values. ✅ Read-only.
