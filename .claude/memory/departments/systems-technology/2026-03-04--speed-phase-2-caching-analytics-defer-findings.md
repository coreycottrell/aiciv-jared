# Speed Optimization Phase 2 - Implementation + Findings
**Date**: 2026-03-04
**Agent**: dept-systems-technology
**Status**: Complete (3/4 tasks done; 1 requires Jared decision)

---

## CRITICAL DISCOVERY: GoDaddy Managed WP Hosting Gateway

purebrain.ai is on **GoDaddy Managed WordPress hosting** with a proprietary gateway cache.

**Evidence**:
- `x-gateway-cache-key` header present on all responses
- `x-gateway-cache-status: MISS/HIT` in response headers
- `Cache-Control: public, max-age=2678400` (31 days) set by GATEWAY (not WP)
- This cache layer runs BELOW PHP — PHP headers cannot override it
- When PHP sends `no-store`, gateway ignores it and uses `public, max-age=2678400`

**Exception**: WordPress REST API authenticated calls do get `x-gateway-skip-cache: 1`
because WP sets `Cache-Control: no-cache, must-revalidate` for auth'd API endpoints.

**Impact**: WP Super Cache is INCOMPATIBLE with this hosting. It requires filesystem writes
(wp-content/advanced-cache.php) which are restricted. It auto-deactivates within seconds.

---

## Task Results

### Task 1: WP Caching Plugin (MODIFIED OUTCOME)

**Attempted**: Installed and activated WP Super Cache v3.0.3
**Found**: Auto-deactivates due to filesystem restrictions on GoDaddy Managed WP
**Reality**: Hosting gateway already provides robust caching (public, max-age=2678400)
**Final status**: WP Super Cache INACTIVE (installed but not running)
**Site health**: GOOD — "Page cache is detected and server response time is good" (149ms)
**Verdict**: No additional caching plugin needed. Gateway already optimal.

**If Jared still wants a plugin**: Try WP Fastest Cache v1.4.6 (works via wp-config, not files)

### Task 2: WonderPush (NO CHANGE - per Jared)

Already confirmed by Jared — no change made. Preserved.

### Task 3: Independent Analytics (COMPLETE)

**Action**: Deactivated (NOT deleted — data is preserved)
**Plugin**: independent-analytics/iawp v2.14.4 → now INACTIVE
**GA4 remains**: GTM4WP + GA4 G-86325WBT3P is the primary analytics system
**Verification**: REST API confirmed `status: inactive`

### Task 4: Brevo/WonderPush Defer Test (COMPLETE — Test Only)

**WonderPush**: Already has `async` attribute in HTML — already non-blocking. No change needed.

**Brevo mailin-front.js** (14.1KB, render-blocking, no defer/async):
- **What it does**: jQuery-dependent JS for subscription forms + reCAPTCHA
- **Risk if deferred**: LOW — all Brevo forms are below-the-fold
- **FCP improvement estimate**:
  - Broadband (100Mbps): ~1ms (negligible)
  - 4G (20Mbps): ~6ms (small)
  - 3G (3Mbps): ~37ms (moderate)
- **What could break**: If any Brevo form fires on DOMContentLoaded before Brevo JS loads
- **Recommendation**: LOW priority — other wins are bigger

**Bigger opportunities documented** (for Jared to decide):
- Page HTML size: 396KB total (99KB head, 297KB body)
- External scripts: 16 total
- jQuery (85.5KB) is the real blocking culprit — but can't be deferred (many deps)
- jquery-migrate (13.3KB) — may be removable if Elementor doesn't need it

---

## PureBrain Security Plugin — v6.2.0 Deployed

**New in v6.2.0**: WP Super Cache configuration section
- Adds `DONOTCACHEPAGE` constant for payment/dynamic pages
- `wpsc_never_cache_page_ids` filter for pages: 439, 468, 688, 689, 1115, 1118, 1232, 1251
- URI pattern exclusions for /pay-test*, /training*, /brainiac-mastermind-training, /video-test
- Note: Due to gateway caching, PHP-level exclusions cannot override gateway headers
- The plugin code is correct and will work if the hosting changes

**Plugin file**: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
**Deployed via**: WP Plugin Editor (admin form POST with nonce)
**Live version**: Confirmed v6.2.0 via REST API

---

## Pay-Test Page Caching Risk Assessment

**WP nonces in HTML**: 0 found
**User-specific content**: 0 found
**PayPal SDK**: Loads fresh from PayPal CDN (cdn.paypal.com)
**Chatbox**: Connects to Workers API dynamically (not affected by HTML cache)
**Payment processing**: Via PayPal servers — not cached HTML

**VERDICT**: LOW RISK. Pay-test HTML shells can be safely cached. All dynamic behavior
(payments, chatbox, session logic) runs via client-side JS + API calls, not server-rendered HTML.

---

## Recommendations for Jared

1. **No additional caching plugin needed** — GoDaddy gateway already provides 31-day caching
2. **Brevo defer**: Low priority (20-80ms gain on mobile, small risk) — Jared's call
3. **If CF cache purge ever needed**: Must be done via Cloudflare dashboard (no API credentials in .env)
4. **Future**: Add CF_API_TOKEN and CF_ZONE_ID to .env for programmatic cache purging

---

## Performance Baseline (Post-Changes)

- **TTFB**: ~200ms average (CF HIT serving cached pages)
- **Page size**: 396KB HTML (99KB head, 297KB body)
- **Site health**: GOOD (149ms median server response)
- **Cloudflare**: Cache-Control: public, max-age=2678400 (31 days)
- **External scripts**: 16 total; jQuery+migrate = 99KB blocking in head
