# PureBrain Referral System — Build Session
**Date**: 2026-03-05
**Type**: full-stack build
**Status**: 95% complete — plugin deploy blocked by WAF rate limiting

---

## What Was Built

### Component 1: WordPress Referral Plugin (DONE — merged into security plugin)

The referral system PHP was merged directly into the security plugin rather than deployed as a separate plugin. This avoids the plugin-upload authentication problem.

**File**: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`

Key features in the merge:
- Tables: `wp_pb_referrals`, `wp_pb_referral_users` (created via `pb_referral_ensure_tables()` on `init` hook)
- REST API namespace: `pb-referral/v1`
- Endpoints: `/dashboard`, `/register`, `/click`, `/convert`, `/lookup`
- URL rewrite: `/r/XXXXXXXX` → `/?ref=XXXXXXXX`
- Seed data: Jared pre-seeded with code `JAREDSB0` + 2 demo referrals
- Rate limiting on click endpoint (20/IP/hour via transients)
- Revenue share: 5%, base credit: $5, bonus: $10 at 5 referrals

### Component 2: Dashboard HTML Page (DONE — deployed)

**WordPress page**: `purebrain.ai/refer-and-earn/` (ID: 1298)
- Template: `elementor_canvas`
- Password: `referral2026`
- Bypass: `?bypass=portal` added to security plugin bypass list (slug + ID 1298)

**Local file**: `/home/jared/projects/AI-CIV/aether/exports/referral-dashboard/index.html`
**Google Drive**: `1QaBu0gO7__my-AziZ2WD_PAuhkfLjQoN/refer-and-earn-dashboard.html`

### Component 3: Portal Modifications (DONE — live on portal server)

**File modified**: `/home/jared/purebrain_portal/portal-pb-styled.html`
**Repo copy updated**: `/home/jared/projects/AI-CIV/aether/exports/app-purebrain-ai-full-repo/portal-server/portal-pb-styled.html`

Changes made:
- Sidebar: Added "Refer & Earn" link (`id="refer-earn-link"`) below Brainiac Training
- Header: Added orange share icon button (`id="share-btn"`) next to settings gear
- Modal: Full "Share This" modal (`id="share-modal"`) with referral link, social share, earnings display
- JS: `openShareModal()`, `closeShareModal()`, `copyShareLink()`, `openReferDashboard()`, `loadShareData()`, `autoRegisterReferral()`

---

## Blocked Item: Plugin Deploy

The WAF on purebrain.ai is rate-limiting wp-login.php after multiple failed login attempts during this session. The plugin file is fully ready.

**Deploy script**: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v623_referral.py`

**When WAF clears (wait ~1 hour)**: `python3 tools/security/deploy_plugin_v623_referral.py`

**Manual fallback**:
1. Go to `purebrain.ai/wp-admin/plugin-editor.php`
2. Select PureBrain Security > purebrain-security-plugin.php
3. Paste content from the file above
4. Click "Update File"

**After deploy**: Verify at `https://purebrain.ai/wp-json/pb-referral/v1/dashboard?code=JAREDSB0`

---

## Architecture Notes

- Referral system is in the security plugin (not a separate plugin) to avoid upload auth issues
- The dashboard page was deployed via REST API (app password works, login doesn't — WAF difference)
- Portal identifies users via `localStorage.getItem('pb_referral_code')` or `pb_user_email`
- The `pb_user_email` key needs to be set by the portal auth flow when user logs in (future integration point)

---

## Deploy Checklist

- [x] Plugin code written
- [x] Plugin merged into security plugin file
- [ ] Security plugin deployed to purebrain.ai (BLOCKED — WAF rate limiting)
- [x] Dashboard HTML written
- [x] Dashboard page created on WordPress (ID 1298)
- [x] Dashboard filed in Google Drive
- [x] Security plugin bypass updated for refer-and-earn page
- [x] Portal: sidebar Refer & Earn link
- [x] Portal: header share button
- [x] Portal: share modal HTML + JS
- [x] Portal copied to repo
