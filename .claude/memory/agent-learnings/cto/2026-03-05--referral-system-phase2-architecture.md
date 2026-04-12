# CTO Memory: Referral System Phase 2 Architecture

**Date**: 2026-03-05
**Type**: teaching
**Agent**: cto
**Confidence**: high
**Tags**: referral-system, architecture, plugin, wordpress, phase2

---

## Context

Phase 1 referral system was already deployed as standalone plugin `purebrain-referral-system.php`.
Phase 2 added: frontend dashboard shortcode, registration shortcode, payment attribution,
reward ledger table, email notifications, rate limiting, and idempotency.

---

## Architecture Decisions Made

### Plugin Delivery: Shortcodes (not separate HTML files)
- `[pb_referral_register]` and `[pb_referral_dashboard]` shortcodes
- Jared places them on any WP page — no routing complexity
- Self-contained HTML/CSS/JS inline in PHP output buffer

### Attribution Storage: localStorage + Cookie (dual fallback)
- `/r/CODE` redirects to `/?ref=CODE` (existing Phase 1 behavior)
- `wp_footer` action injects JS that reads `?ref=` and stores in both localStorage and 30-day cookie
- `window.getPbRef()` global helper reads whichever is available at payment time
- Validation: `/^[A-Za-z0-9]{6,12}$/` regex before storing — prevents XSS

### Idempotency on /convert
- Checks existing completed row with matching `referrer_code + referred_email` (both raw and masked)
- Returns `{ok: true, duplicate: true}` on repeat call — does not double-count

### Reward Ledger Table
- `wp_pb_reward_ledger` table: id, referral_code, event_type ENUM, amount, source_referral_id, status ENUM, created_at
- event_type: `conversion_credit | milestone_bonus | revenue_share`
- status: `pending | approved | paid`
- Written by `/convert` endpoint, read by `/rewards` endpoint
- Payout logic stays out of scope for Phase 2

### Email Notification
- `wp_mail()` triggered inside `/convert` on every successful conversion
- From: `purebrain@puremarketing.ai`
- Reply-To: `jared@puretechnology.nyc`
- Click notifications explicitly excluded (high volume, low value)

---

## Files

- Plugin: `tools/security/purebrain-referral/purebrain-referral-system.php` (v2.0.0, 1092 lines)
- Deploy script: `tools/security/deploy_referral_v200.py`

---

## Security Review Findings

- All user inputs: `sanitize_text_field()`, `sanitize_email()`, `is_email()`
- XSS prevention: JS `pbEscape()` helper used everywhere innerHTML is written
- Stat numbers (totalClicks, etc.) used only in `textContent` assignment — safe
- Rate limiting: `/register` 3/IP/hour via WP transients
- Click rate limit: 20/IP/hour (existing from Phase 1)
- `?ref=` injection: validated with `/^[A-Za-z0-9]{6,12}$/` before localStorage write
- WP REST nonce: `X-WP-Nonce: wp_create_nonce('wp_rest')` on shortcode AJAX calls
- `/convert` is open (no auth) — accepted risk; protected by idempotency + business logic checks
- Dead code: `$nonce_action` variable declared but unused — minor cleanup item
- Duplicate `$history =` assignment in dashboard function (lines 689-706) — PHP uses second (correct) assignment; functional issue is nil

---

## Known Issues (Non-Blocking)

1. Duplicate `$history` query block in `pb_referral_api_dashboard()` — PHP overwrites with correct query, harmless but should be cleaned in v2.0.1
2. `/convert` open endpoint — Phase 3 should add server-side payment webhook verification

---

## QA Test Paths

Critical flows to verify post-deploy:
1. `GET /wp-json/pb-referral/v1/dashboard?code=JAREDSB0` → returns Jared's stats
2. `POST /wp-json/pb-referral/v1/register` with name+email → returns referral_link
3. `/r/JAREDSB0` → redirects to `/?ref=JAREDSB0`
4. Shortcode `[pb_referral_register]` renders without breaking dark theme
5. Shortcode `[pb_referral_dashboard]` renders with stats
6. `/convert` idempotency: second call returns `duplicate: true`
7. Rate limit on `/register`: 4th attempt returns 429
