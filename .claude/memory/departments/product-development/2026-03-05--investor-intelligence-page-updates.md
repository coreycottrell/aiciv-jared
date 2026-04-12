# PD# Memory: Investor Intelligence Page Updates

**Date**: 2026-03-05
**Type**: operational + gotcha
**Agent**: dept-product-development (VP Product)
**Page**: https://purebrain.ai/investor-intelligence/ (Page ID: 1205)

---

## What Was Done

### Task 1: Agent Horizon METR Timeline Restored
- The METR Autonomy Timeline (30min → 5hrs → 14.5hrs → ∞) was previously in the hero section
- During a rollback, it was removed. Now restored as a dedicated section
- Placement: between Section 9 (last data section) and Section 10 (CTA)
- Section ID: `agent-horizon`
- Visual: four-step horizontal timeline, current (14.5hrs) highlighted in blue with "Current" badge, projected future in orange

### Task 2: Email Capture Flow Wired
- Old behavior: `submitInvestorBrief()` opened mailto: window — nothing captured
- New behavior: POST to `/wp-json/purebrain/v1/investor-lead` → Brevo list 20 → thank-you modal
- Fallback: if API call fails, falls through to mailto: (belt-and-suspenders)
- Thank-you modal: full-screen overlay with "You're on the List" message + direct email fallback link
- "Schedule a Call → jared@puretechnology.nyc" button untouched

---

## Key Technical Discoveries

### CRITICAL: This Page Uses Elementor
- Page 1205 template = `elementor_canvas`
- Has `_elementor_data` (82k JSON) with a single HTML widget
- Updating `post_content` via REST API does NOTHING — Elementor ignores it
- Must update `meta._elementor_data` to change what renders
- After updating `_elementor_data`: must clear Elementor cache AND flush hosting cache

### Cache Clearing Flow (GoDaddy + Cloudflare)
1. POST to WP pages API with `meta._elementor_data` updated
2. DELETE `/wp-json/elementor/v1/cache` (Elementor cache)
3. Navigate to `/wp-admin/?wpaas_action=flush_cache&wpaas_nonce={nonce}` via Playwright
4. Cloudflare re-fetches from GoDaddy origin on next request (MISS → new content cached)

### New Plugin Endpoint: purebrain/v1/investor-lead
- Added to purebrain-security-plugin v6.2.3
- Public POST endpoint, no auth required
- Rate limited: 5/min per IP
- Sends to Brevo list 20 ("Investor Brief Requests")
- Returns `{success: true, message: "captured"}`

### Brevo Setup
- New list: ID 20 = "Investor Brief Requests"
- Existing `/pb-security/v1/subscribe` hardcodes list 3 — can't be reused
- Created new endpoint specifically for investor leads

---

## Files Modified
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` — bumped v6.2.2 → v6.2.3, added investor-lead endpoint
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip` — updated zip

## Verification
- Plugin endpoint: `curl -X POST https://purebrain.ai/wp-json/purebrain/v1/investor-lead -d '{"email":"test@test.com"}'` → `{"success":true}`
- Brevo list 20 confirmed receiving contacts
- Live page: all markers present (verified via curl)
- agent-horizon section: position 154786, before cta at 161976 ✓
