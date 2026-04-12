# Plugin Reactivation Plan: PureBrain Security v4.7.2.1

**Prepared by**: dept-systems-technology (ST#)
**Date**: 2026-02-28
**Status**: PLAN ONLY — no site changes made
**Plugin file**: `exports/purebrain-security-plugin-v4721.php`
**Rollback file**: `exports/purebrain-security-plugin-v472-backup.php`

---

## 1. What Happened — The Full Story

### The Timeline

| Version | What Changed | Result |
|---------|-------------|--------|
| v4.7.2 | Added PayPal sandbox override for page 688. Working correctly. | GOOD |
| v4.7.3 | Added n1b (Discover Button UX Fix) + extended n2 (Session Timer Fix) to pages 439, 468 | BROKE bypass flow |
| v4.7.2.1 | Removed the n2 SESSION TIMER FIX block entirely from v4.7.2 | Safe candidate |

### What v4.7.3 Added That Caused the Break

**Section n1b — Chatbox Discover Button UX Fix** (new in v4.7.3):
- Updates button text to "Click to discover what [AI NAME] can do"
- DISABLES the input field when the discover button appears (`userInput.disabled = true`)
- Sets placeholder to "Click the button above" while disabled
- Re-enables input after button click via `showPersonalizedCapabilities` patch
- Adds 30-minute session timer override (replaces 15-minute timer)
- Applies to pages: 688, 689, 11, 439, 468

**Section n2 — Session Timer Fix** (existed in v4.7.2, extended in v4.7.3):
- The original n2 in v4.7.2 hides `.session-timer.active` with `display: none !important`
- Only reveals it when Discover button (`#seeWhatBtn`) is clicked (adds `.pb-timer-ready`)
- Extended in v4.7.3 to cover pages 439, 468 (was only 688, 689, 11)

### The Root Cause

The CSS rule `.session-timer.active { display: none !important }` hides elements that have both the `session-timer` and `active` classes. The bypass flow depends on certain elements being VISIBLE during the admin bypass sequence. When those elements carry the `session-timer active` classes, the CSS rule hides them and breaks the bypass.

This is the same category of problem documented in MEMORY.md (locked 2026-02-27):
> "NEVER add CSS that hides page elements with `display: none !important` — this breaks admin bypass flows"

---

## 2. What v4.7.2.1 Contains

v4.7.2.1 is v4.7.2 with the entire **n2 SESSION TIMER FIX block removed**. That is the only change.

### Diff Summary: v4.7.2 vs v4.7.2.1

**Removed** (59 lines, lines 4860-4918 of v4.7.2):

```
// n2) SESSION TIMER FIX (v4.6.9)
//     Pages: 688, 689, 11

add_action('wp_head', ...) {
    // CSS block:
    .session-timer.active { display: none !important; }
    .session-timer.active.pb-timer-ready { display: flex !important; }
    #sessionNote { display: none !important; }
    #sessionNote.pb-note-ready { display: block !important; }
}

add_action('wp_footer', ...) {
    // JS block: listens for #seeWhatBtn click,
    // adds .pb-timer-ready to #sessionTimer,
    // adds .pb-note-ready to #sessionNote
}
```

**Not removed** (preserved from v4.7.2):
- n1: Chatbox bypass override (v4.6.9 capturing event listeners + URL param bypass)
- n3: PayPal button routing fix (v4.7.1)
- n4: PayPal sandbox environment override for page 688 (v4.7.2)
- All dark background enforcement (v4.6.5 through v4.6.7)
- All site-wide security headers, CSP, HSTS
- All blog/nav/footer CSS fixes
- All Brevo proxy endpoints
- Aether footer credit bar

### Line Count Comparison

| Version | Lines |
|---------|-------|
| v4.7.2 (backup) | 5,086 |
| v4.7.3 | 5,215 |
| v4.7.2.1 (candidate) | 5,027 |

v4.7.2.1 is 59 lines shorter than v4.7.2, confirming exactly one block was removed.

---

## 3. What You Lose by Activating v4.7.2.1

The n2 timer block had two intended functions:

1. **Session timer visibility timing** — Timer was meant to only appear AFTER Discover button click, not immediately when AI declares its name. Without n2, the timer may appear earlier in the conversation than intended.

2. **#sessionNote visibility** — The identity-saved note (`#sessionNote`) was hidden until `.pb-note-ready` was added. Without n2, `#sessionNote` displays at its default CSS visibility.

Neither of these affects payments, bypass flow, or core chatbox functionality. They are UX polish features only.

---

## 4. Pre-Activation Checklist

Complete ALL of these before touching the Activate button.

### Step 1: Verify Current Live Version

```bash
source /home/jared/projects/AI-CIV/aether/.env
curl -s https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin \
  -H "Authorization: Basic $(echo -n 'Aether:FlFr2VOtlHiHaJWjzW96OHUJ' | base64)" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('Version:', d.get('version')); print('Status:', d.get('status'))"
```

Expected output before activation:
- Version: something other than 4.7.2.1
- Status: inactive (for v4.7.2.1)

### Step 2: Confirm Backup File Integrity

```bash
grep "Version:" /home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v472-backup.php | head -1
wc -l /home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v472-backup.php
```

Expected: Version 4.7.2, 5086 lines. This is your rollback.

### Step 3: Confirm Candidate File Has No Timer CSS

```bash
grep -c "session-timer.active" /home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v4721.php
```

Expected: `0` — confirms the problematic CSS rule is absent.

### Step 4: Spot-Check Candidate Has Critical Sections

```bash
grep -c "pb-paypal-routing-fix\|pb-sandbox-override\|pb-bypass-override" \
  /home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v4721.php
```

Expected: `3` — PayPal routing, sandbox override, and bypass are all present.

### Step 5: Save Fresh Deployment Cookies

Before attempting activation via WP admin, save fresh cookies in case GoDaddy WAF CAPTCHA activates:

```bash
source /home/jared/projects/AI-CIV/aether/.env
curl -s -c /tmp/wp_cookies_pre_activation.txt -b /tmp/wp_cookies_pre_activation.txt \
  -X POST "https://purebrain.ai/wp-login.php" \
  -d "log=Aether&pwd=${PUREBRAIN_WP_PASSWORD}&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1"
```

---

## 5. Step-by-Step Reactivation Procedure

Since v4.7.2.1 is already INSTALLED (uploaded), activation is a single toggle. Two methods are available:

### Method A: WP Admin UI (Easiest — Recommended First)

1. Log in to https://purebrain.ai/wp-admin/plugins.php
2. Find "PureBrain Security" in the plugin list
3. Confirm version shows 4.7.2.1
4. Click "Activate"
5. Page will reload — confirm "Plugin activated" green notice

### Method B: WP REST API (If admin UI fails)

```bash
source /home/jared/projects/AI-CIV/aether/.env
curl -s -X POST \
  https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin \
  -H "Authorization: Basic $(echo -n 'Aether:FlFr2VOtlHiHaJWjzW96OHUJ' | base64)" \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('Status:', d.get('status'), '| Version:', d.get('version'))"
```

Expected response: `Status: active | Version: 4.7.2.1`

### Method C: admin-ajax.php Cookie Method (If REST API fails)

This was the method used for the v4.6.9 deployment when GoDaddy WAF blocked direct login.

```bash
source /home/jared/projects/AI-CIV/aether/.env

# Step 1: Login and get cookies
curl -s -c /tmp/wp_cookies_activation.txt -b /tmp/wp_cookies_activation.txt \
  -X POST "https://purebrain.ai/wp-login.php" \
  -d "log=Aether&pwd=${PUREBRAIN_WP_PASSWORD}&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1"

# Step 2: Get activation nonce
NONCE=$(curl -s -b /tmp/wp_cookies_activation.txt \
  "https://purebrain.ai/wp-admin/plugins.php" \
  | grep -oP 'activate.*?_wpnonce=\K[^&"]+' | head -1)

# Step 3: Activate via GET request
curl -s -b /tmp/wp_cookies_activation.txt \
  "https://purebrain.ai/wp-admin/plugins.php?action=activate&plugin=purebrain-security%2Fpurebrain-security-plugin.php&_wpnonce=${NONCE}"
```

---

## 6. Post-Activation Verification Steps

Run these in order immediately after activation.

### Verification 1: Confirm Version and Status

```bash
curl -s https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin \
  -H "Authorization: Basic $(echo -n 'Aether:FlFr2VOtlHiHaJWjzW96OHUJ' | base64)" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('Version:', d.get('version')); print('Status:', d.get('status'))"
```

Pass condition: `Version: 4.7.2.1` and `Status: active`

### Verification 2: Dark Background Intact

```bash
curl -s https://purebrain.ai/ | grep -c "pb-calc-dark-bg\|#080a12"
```

Pass condition: count > 0 (dark bg CSS still loading)

### Verification 3: No Session Timer CSS on Live Pages

```bash
curl -s https://purebrain.ai/pay-test-2/ | grep -c "session-timer.active.*display.*none"
```

Pass condition: `0` — confirms the removed CSS is not being served

### Verification 4: Bypass Still Works — URL Param Method

Open in browser: `https://purebrain.ai/pay-test-2/?bypass=true`

Expected behavior: Bypass activates immediately, pricing revealed, no broken layout. Console should show `[PB-BYPASS] Bypass activated`.

### Verification 5: PayPal Button Still Routes Correctly

Open in browser: `https://purebrain.ai/pay-test-2/`

Expected behavior: Clicking any pricing tier opens PayPal modal (not Google Forms waitlist). Console should show `[PB-FIX] PayPal routing restored`.

### Verification 6: Sandbox Page Still Uses Sandbox

Open in browser: `https://purebrain.ai/?page_id=688`

Expected behavior: Console shows `[PB-SANDBOX] Sandbox PayPal SDK loaded`, NOT production SDK.

### Verification 7: CSP Headers Present

```bash
curl -sI https://purebrain.ai/ | grep -i "content-security-policy"
```

Pass condition: CSP header is present and includes `worker-src 'self' blob:` (PayPal WebWorker fix from v4.7.0).

---

## 7. Rollback Plan

If anything breaks after activation, you have two clean rollback options.

### Rollback Option A: Revert to v4.7.2 (via admin-ajax.php)

The backup file is at `exports/purebrain-security-plugin-v472-backup.php`.

```bash
source /home/jared/projects/AI-CIV/aether/.env

# Login
curl -s -c /tmp/wp_cookies_rollback.txt -b /tmp/wp_cookies_rollback.txt \
  -X POST "https://purebrain.ai/wp-login.php" \
  -d "log=Aether&pwd=${PUREBRAIN_WP_PASSWORD}&wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1"

# Get nonce
NONCE=$(curl -s -b /tmp/wp_cookies_rollback.txt \
  "https://purebrain.ai/wp-admin/plugin-editor.php?plugin=purebrain-security%2Fpurebrain-security-plugin.php&Submit=Select" \
  | grep -oP 'name="nonce" value="\K[^"]+')

# Deploy v4.7.2 backup
curl -s -b /tmp/wp_cookies_rollback.txt \
  -X POST "https://purebrain.ai/wp-admin/admin-ajax.php" \
  -F "action=edit-theme-plugin-file" \
  -F "nonce=${NONCE}" \
  -F "plugin=purebrain-security/purebrain-security-plugin.php" \
  -F "file=purebrain-security/purebrain-security-plugin.php" \
  -F "newcontent=</home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v472-backup.php"
```

### Rollback Option B: Deactivate (Nuclear/Immediate)

If you need the plugin off immediately and cannot deploy:

```bash
curl -s -X POST \
  https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin \
  -H "Authorization: Basic $(echo -n 'Aether:FlFr2VOtlHiHaJWjzW96OHUJ' | base64)" \
  -H "Content-Type: application/json" \
  -d '{"status":"inactive"}'
```

Warning: Deactivating the plugin removes all CSS/JS injections site-wide — dark backgrounds, nav fixes, security headers, PayPal routing, everything. The site will still load but will look different and payments may break.

---

## 8. Risk Assessment

### Risk Level: LOW

v4.7.2.1 is a SUBTRACTION from v4.7.2, not an addition. The only change is removing a CSS+JS block that was causing problems.

| Risk | Probability | Severity | Notes |
|------|------------|----------|-------|
| Bypass flow still broken | Very Low | High | The specific CSS `.session-timer.active { display: none !important }` has been confirmed removed from v4.7.2.1. That was the only diagnosed cause. |
| Dark background breaks | Very Low | Medium | Dark bg code is unchanged from v4.7.2. |
| PayPal breaks | Very Low | High | PayPal sections (n3, n4) are unchanged from v4.7.2. |
| Session timer appears too early | Low | Low | This is a UX-only side effect. Timer may show during naming phase instead of after Discover click. Not functionally harmful. |
| GoDaddy WAF blocks activation | Low | Medium | Can be mitigated with Method B (REST API) or Method C (saved cookies). |
| Elementor cache serves stale output | Low | Low | Clear cache after activation if pages look wrong: `DELETE /elementor/v1/cache` (may return 403, that is normal). |

### Known Safe: What v4.7.2.1 Leaves Alone

All of these were working correctly in v4.7.2 and are byte-for-byte identical in v4.7.2.1:
- Site-wide dark background enforcement (3-layer CSS+JS)
- Video background transparency for pages 688, 689, 987, homepage
- Chatbox bypass (n1 — URL param, keydown capture, submit capture)
- PayPal routing fix (n3)
- PayPal sandbox override for page 688 (n4)
- CSP with worker-src blob: (PayPal WebWorker fix)
- HSTS preload
- Security headers
- Brevo proxy endpoints
- All blog styling fixes
- Aether footer credit bar

---

## 9. Decision Summary

You have three choices:

**Option 1: Activate v4.7.2.1 now (Recommended)**
- Minimal risk. Single block removed. Everything else unchanged.
- Follow Sections 5 and 6 of this plan.
- Rollback is available in under 2 minutes if anything looks wrong.

**Option 2: Build v4.7.4 with a safer timer approach first**
- If you want the session timer UX behavior back without the `display: none` approach, a v4.7.4 can implement it differently (e.g., opacity, visibility, or JS-only approach instead of CSS display override).
- Safer but takes an engineering sprint before activation.

**Option 3: Keep v4.7.2.1 inactive for now**
- Current state. Site running without the plugin is working fine.
- No timer UX features, but no risk either.

---

## 10. Quick Reference

| Item | Value |
|------|-------|
| Candidate plugin file | `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v4721.php` |
| Rollback plugin file | `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v472-backup.php` |
| Current live plugin REST endpoint | `https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin` |
| WP REST auth header | `Authorization: Basic $(echo -n 'Aether:FlFr2VOtlHiHaJWjzW96OHUJ' | base64)` |
| WP admin password env var | `PUREBRAIN_WP_PASSWORD` (in `.env`) |
| Pages affected by removed timer CSS | 688, 689, 11 |
| Removed CSS rule | `.session-timer.active { display: none !important; }` |
| Removed JS behavior | Click listener on `#seeWhatBtn` adding `.pb-timer-ready` to `#sessionTimer` |
