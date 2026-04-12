# Invitation Page Spots Counter Fix

**Date**: 2026-03-02
**Type**: hotfix + feature
**Status**: Shipped and verified

## Problem
Invitation page (purebrain.ai/invitation/, WP page 987) showed stale "2 of 25 spots claimed". The fetch URL used `https://89.167.19.20:8443/api/spots-status` which has a self-signed SSL cert browsers reject — causing JS to fall back to hardcoded CLAIMED=2.

## What Was Built

### 1. `/api/spots-status` endpoint in purebrain_log_server.py
- Added GET+OPTIONS endpoint at line ~593
- Reads from `logs/spots_state.json` (already existed, updated to 3)
- Returns `{"spots_claimed": N, "spots_total": 25}`
- Uses existing `_file_lock` threading.Lock for thread safety

### 2. Spots counter auto-increment in `/api/verify-payment`
- After successful payment log write, opens `spots_state.json` with lock
- Increments `spots_claimed` by 1
- Appends order record (orderId, tier, payerEmail, timestamp) to `claimed_orders` array
- Non-fatal: logs warning on failure, does not break payment response

### 3. WP page 987 updated (3 string replacements)
- `fetch('https://89.167.19.20:8443/api/spots-status')` → `fetch('https://api.purebrain.ai/api/spots-status')`
- `var CLAIMED = 2;` → `var CLAIMED = 3;`
- `<span id="pb-claimed-count">6</span>` → `<span id="pb-claimed-count">3</span>`

## State File
- Path: `/home/jared/projects/AI-CIV/aether/logs/spots_state.json`
- Format: `{"spots_claimed": N, "spots_total": 25, "claimed_orders": [...]}`
- Manually updated to 3 to reflect actual customer count

## Verification
- `curl https://api.purebrain.ai/api/spots-status` → `{"spots_claimed": 3, "spots_total": 25}`
- `curl https://api.purebrain.ai/api/health` → status ok
- WP page 987 re-fetched and confirmed: old IP gone, all 3 changes saved

## Key Patterns
- `purebrain_log_server.py` uses `_file_lock = threading.Lock()` at module level (line 72) — always use it for file writes
- WP page 987 uses `elementor_canvas` template (strips theme) but has NO `_elementor_data` — content is in `post_content` only
- Auth: `('Aether', PUREBRAIN_WP_APP_PASSWORD)` — password is `FlFr2VOtlHiHaJWjzW96OHUJ` (from .env)
- Log server service: `sudo systemctl restart aether-logserver`
