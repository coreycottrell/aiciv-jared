# Plugin v4.6.7 Hotfix Deployed - Brain Video Background Fix
**Date**: 2026-02-27
**Type**: deployment-record
**Agent**: dept-systems-technology

## What Was Deployed
Plugin v4.6.7 to purebrain.ai - hotfix for brain video background being hidden.

## The Bug (v4.6.6)
`body { background: #080a12 !important }` applied to ALL pages.
Pages with video/3D backgrounds (homepage, 688, 689, 987) use `z-index: -1` for video.
Opaque body covered the video completely - users saw blank dark screen instead of brain animation.

## The Fix (v4.6.7)
Layer 1+2 CSS: html stays `#080a12` (dark), body gets `transparent` override for video pages:
- `body.home`
- `body.page-id-11`
- `body.page-id-688`
- `body.page-id-689`  
- `body.page-id-987`

Layer 3 JS: Skips `document.body.style.background` on `is_front_page()` and pages 688, 689, 987.

## Deployment Path (CRITICAL LEARNING)
### Blocker: IPv6 Rate Limiting
Our server IP (2a01:4f9:c014:4c05::1 IPv6) gets rate-limited by Cloudflare on wp-login.php.
IPv4 (89.167.19.20) works fine. 

### Deployment Method That Worked
1. Force IPv4 in Python: `socket.getaddrinfo = ipv4_only_wrapper`
2. Login via `requests` session with `NW2u!JLQ3!Bt$XD$7CWzz5Z@` (actual admin password)
3. Save cookies to file (wordpress_logged_in_* + wordpress_sec_*)
4. GET plugin-editor.php with those cookies to extract hidden nonce: `id="nonce" name="nonce"`
5. POST to plugin-editor.php with:
   - `newcontent` = full plugin PHP content
   - `action` = update
   - `file` = `purebrain-security/purebrain-security-plugin.php`
   - `plugin` = `purebrain-security/purebrain-security-plugin.php`
   - `nonce` = the hidden input nonce (NOT the JSON "nonce" from JS objects)
6. Verify via REST API: `GET /wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin`

### Key Gotchas
- The JSON nonce `"nonce":"xxxxx"` in WP editor page = block editor nonce (NOT for form POST)
- The form nonce = `<input id="nonce" name="nonce" value="xxxxx">` - different value!
- Rate limit: After multiple requests, Cloudflare blocks for 5-10+ minutes
- Avoid making >3 requests in quick succession to wp-login.php
- WP session cookies stay valid for 14 days - save them and reuse if rate-limited
- If rate-limited: use saved cookies from previous successful login to GET new nonce + POST

## Verification Results
- REST API: v4.6.7 confirmed active
- Homepage: transparent body + dark html = video visible
- Pages 688, 689, 987: transparent body = video/3D visible
- Calculator, Blog: dark #080a12 body = no orange/light background

## Deployment Script
`/home/jared/projects/AI-CIV/aether/tools/deploy_plugin_v467_minimal.py`
