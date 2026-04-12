# CTO Memory: Portal Voice HMI + Referral SQLite Architecture

**Date**: 2026-03-12
**Type**: operational
**Topic**: Voice overlay extraction from v8 dashboard to portal-pb-styled.html; referral proxy replacement with SQLite backend

---

## Context

Two tasks deployed to ST# (dept-systems-technology) with full BUILD -> SECURITY -> QA -> SHIP pipeline.

## Task 1: Voice Interface

**Source**: `/home/jared/portal_uploads/from-portal/portal_20260312_224447_pure-brain-v8-aether-dashboard.html`
- CSS: lines 1522-1555 + mobile at 1746-1752
- HTML: lines 4517-4555
- JS: lines 12378-12738

**Key adaptations:**
- `messageInput` -> `chat-input`
- `sendMessage()` -> `document.getElementById('send-btn').click()`
- `AppState.ui.hmiVoiceOverlayOpen` -> `window._hmiVoiceOverlayOpen`
- `LOGO_URL` -> hardcoded PureBrain logo URL
- AI name populated dynamically from owner API after overlay opens
- `autoResizeTextarea()` calls removed (portal uses fixed rows=3 textarea)
- Mic button `id="mic-btn"` wired to `openHmiVoiceOverlay`

**TTS decision**: Browser speechSynthesis (free, built-in, zero latency). NOT Google TTS.
- `window._hmiTtsEnabled = true` (togglable via speaker button in overlay)
- `window._lastSendWasVoice = false` flag gates TTS to voice-initiated sends only
- TTS fires in the portal's AI message receive handler

## Task 2: Referral Backend

**Dead proxies replaced**: `api_referral_proxy`, `api_referral_register_proxy`, `api_referral_lookup_proxy`

**SQLite schema:**
- `referral_codes`: id, email (unique), name, code (unique), created_at
- `clicks`: id, code, clicked_at, ip_hash
- `referrals`: id, code, referred_email, joined_at, tier, value_usd
- Payouts: kept as existing JSONL (not migrated)

**Code generation**: `secrets.token_urlsafe(6).upper()`

**Auth rules:**
- `/api/referral/click` — NO auth (public, fires when visitor hits referral link)
- All other endpoints — standard portal auth

**Rate limit on click**: IP hash, 10 clicks per code per IP per hour

**CF Pages**: grep `purebrain.ai/wp-json/pb-referral/v1` in refer/index.html and purebrain-site/public/refer/index.html, replace with portal server base URL

**Payout JSONL**: preserved as-is at line 1905. `payout-history` endpoint reads same file.

## Architecture Principles Applied

- No new infrastructure for either task (browser APIs, SQLite)
- Existing payout mechanism untouched (if it ain't broke)
- Security review mandatory on click endpoint (unauthenticated = abuse surface)
- Parameterized SQL throughout — no string interpolation
