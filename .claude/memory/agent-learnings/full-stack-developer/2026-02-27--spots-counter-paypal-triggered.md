# Spots Counter — PayPal-Triggered System for Invitation Page

**Date**: 2026-02-27
**Type**: operational
**Topic**: PayPal-triggered spots counter for purebrain.ai/invitation/

## What Was Built

1. **State file**: `logs/spots_state.json` — JSON with total_spots, spots_claimed, claimed_orders array. Pre-seeded with 2 (Ryan + Jared test).

2. **`_increment_spots_counter(tier, payer_email, order_id)`** in `tools/purebrain_log_server.py`:
   - Located right after `_log_payment` (line ~718)
   - Uses `_file_lock` (the existing threading.Lock()) for thread safety
   - Deduplicates by `order_id` — safe to call multiple times, idempotent
   - Atomic write via `.tmp` + `os.replace()`

3. **Hook in `verify-payment`** endpoint: Called inside `if pp['success']:` block, after `_log_payment(payment_entry)` and before Telegram notification. Line ~1274.

4. **`/api/spots-status` GET endpoint** (line ~1741): Returns `{total_spots, spots_claimed, spots_remaining}`. Added just before `@app.errorhandler(400)`.

5. **Frontend** (`exports/purebrain-invite-only.html`): Replaced hardcoded spots block with `renderSpots(claimed)` function + `fetch('https://89.167.19.20:8443/api/spots-status')`. Falls back to 2 silently on fetch error. Renders immediately with fallback, then re-renders on successful fetch.

## Key Patterns

- **CSP**: No CSP meta tag in the standalone HTML file. CSP is at WP plugin level. Since other endpoints on 89.167.19.20:8443 already work from purebrain.ai, no CSP change needed.
- **CORS**: Already configured in `create_app()` to allow purebrain.ai — new endpoint is under `/api/*` so it's covered automatically.
- **Log server restart**: `kill <PID> && nohup python3 tools/purebrain_log_server.py >> logs/purebrain_log_server.log 2>&1 &` (no systemd unit for this server)
- **Test**: `curl -sk https://89.167.19.20:8443/api/spots-status` returns JSON

## Verification

- `curl -sk https://89.167.19.20:8443/api/spots-status` returned `{"spots_claimed": 2, "spots_remaining": 23, "total_spots": 25}`
- Health endpoint still returning `{"status": "ok"}` after restart
- State file at `logs/spots_state.json` with 2 pre-seeded orders

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
- `/home/jared/projects/AI-CIV/aether/exports/purebrain-invite-only.html`
- `/home/jared/projects/AI-CIV/aether/logs/spots_state.json` (new)
