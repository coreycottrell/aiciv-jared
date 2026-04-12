# Memory: pay-test-2 WAF Block + WP REST API Fallback Pattern

**Date**: 2026-02-27
**Type**: teaching + operational
**Topic**: When browser can't access password-protected page due to WAF, use WP REST API with context=edit to verify content integrity

---

## Situation

Jared asked for visual verification of pay-test-2 after a JSON corruption fix.
URL: https://purebrain.ai/pay-test-2/ (WP Page ID: 689)

## Problem: WAF Rate Limit Blocked Browser Access

Our server IP (89.167.19.20) was rate-limited by GoDaddy WAF:
- Tried `fill()` then form.submit() — password rejected ("Invalid password")
- WAF was blocking the postpass endpoint (HTTP 429 on curl tests)
- wp-login.php also blocked by reCAPTCHA
- Basic Auth headers do NOT bypass WP content password protection (only REST API auth)

## Root Cause of Password Rejection

Browser's `fill()` + `form.submit()` pattern worked fine on previous pages, but here the WAF had rate-limited `/wp-login.php?action=postpass` from our IP. The password itself (`PureBrain.ai253443$`) is correct — confirmed via REST API.

## Solution: WP REST API Content Verification

When browser can't access a password-protected page due to WAF:

```python
import base64, requests

APP_PASS = "your_wp_app_password"
auth_b64 = base64.b64encode(f"Aether:{APP_PASS}".encode()).decode()

# Pass the content password as query param, auth via Basic Auth header
resp = requests.get(
    "https://purebrain.ai/wp-json/wp/v2/pages?include=689&password=PureBrain.ai253443%24&context=edit",
    headers={"Authorization": f"Basic {auth_b64}"}
)
content = resp.json()[0]["content"]["raw"]
# content has the full 435k char page source
```

This gives full raw HTML including all video elements, scripts, CSS, etc.

## Key Checks to Run on Content

```python
import re

# Video check
videos = re.findall(r'<video[^>]*>.*?</video>', content, re.DOTALL | re.IGNORECASE)
for v in videos:
    has_autoplay = 'autoplay' in v
    has_src = re.search(r'src=["\']([^"\']+)["\']', v)

# Chatbox check
chat = re.search(r'id=["\']awakening["\'].*?</section>', content, re.DOTALL)

# Heading check
headings = re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.DOTALL)
```

## What Was Found on Page 689

- bgVideo: autoplay=True, muted=True, loop=True, src=PureResearch.ai-1.mp4 (73.9MB, HTTP 200)
- demoVideo: muted modal video
- "Begin Your Awakening" H2 heading: PRESENT
- chat-section with Begin Awakening button: PRESENT (57k chars of chat section)
- Content last modified: 2026-02-27T12:51:09 (JSON fix timestamp)
- Total content: 435,117 chars (healthy, not truncated)

## When To Use This Pattern

1. WAF blocks our server IP from accessing password-protected pages
2. Need to verify page content after a fix without browser access
3. Quick integrity check before waiting for WAF to clear

## WAF Recovery

- GoDaddy WAF blocks: 15-20 min minimum recovery
- Triggered by: 3+ postpass form submissions from same IP in ~30 min window
- Our IP: 89.167.19.20
- Workaround: Ask Jared to check from his browser + report back

## Files

- Report: `exports/paytest2-json-fix-verification-20260227.md`
- Screenshots (partial): `exports/screenshots/paytest2-json-fix-20260227/`
- WAF screenshot: `020-wp-login.png` (shows reCAPTCHA block)

**Tags**: purebrain, pay-test-2, page-689, waf, godaddy, postpass, wp-rest-api, password-bypass, content-verification
