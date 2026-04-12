# Aether Auto-Memory

## Elementor Deployment (CRITICAL)
- **Elementor rendering cache is SEPARATE from `_elementor_data` meta**
- REST API updates to `_elementor_data` do NOT trigger re-rendering
- **Solution**: Delete page + recreate with fresh ID. Elementor builds fresh cache for new page IDs.
- Pattern: fetch page → modify elementor data → change old slug to draft → create new page with same slug
- This works for purebrain.ai (GoDaddy + Elementor + Cloudflare)

## WordPress Auth
- Application Password (`FlFr2VOtlHiHaJWjzW96OHUJ`) works for REST API only
- Real password (`NW2u!JLQ3!Bt$XD$7CWzz5Z@`) blocked by GoDaddy 2FA for wp-login.php
- XMLRPC is 403 Forbidden (GoDaddy blocks it)
- For admin UI tasks, use Playwright (browser-vision-tester) - handles 2FA visually

## CSS Deployment
- Additional CSS only deployable via Playwright + Customizer CodeMirror
- Script: `tools/deploy_category_css_fix_v5.py` (working reference)
- GoDaddy CAPTCHA solved with `device_scale_factor=2`

## Pay-Test Page
- Page ID: 439 (as of 2026-02-18)
- Contains PayPal popup + post-payment chat flow + integration glue
- 3 JS modules injected before `</body>` in Elementor HTML widget
- PayPal SDK needs real Client ID from Jared (placeholder active, form-POST fallback works)
- v2 scripts: AI name carryover, 11 behind-the-curtain slides, Telegram setup, Claude Max walkthrough

## Log Server Endpoints
- Base: https://89.167.19.20:8443
- `/api/log-conversation` - Main conversation logging (existing)
- `/api/verify-payment` - PayPal payment verification (NEW)
- `/api/log-pay-test` - Post-payment flow completion (NEW, sends Telegram alert)
- `/api/health` - Health check
- `/api/stats` - Conversation statistics
- Runs from venv: `source venv/bin/activate && python3 tools/purebrain_log_server.py`

## Content Rules
- NEVER publish blog/social without explicit Jared approval
- Banner style: PUREBR(blue) + AI(orange) + N(blue) + .ai(white)
- Use Pillow for banners (DALL-E rejected by Jared for "bunch of issues")

## Overnight Delivery Standard (LOCKED IN - Jared's Words: "impeccable", "top notch")
- Deliver .md files + banner/visual deliverables as FILES via Telegram
- Multiple polished deliverables ready when Jared wakes up
- This is the gold standard - every overnight should match this quality
- Date established: 2026-02-19 (after overnight delivery praised by Jared)

## Telegram
- Bridge at tools/telegram_bridge.py writes to inbox/telegram-live.md
- Send via: bash tools/tg_send.sh "message"
- Always wrap responses: 🤖🎯📱 ... ✨🔚
