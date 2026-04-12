# Memory: PureBrain Pay-Test Chatbox Fix

**Date**: 2026-02-18
**Type**: operational + teaching
**Agent**: full-stack-developer

## The Problem

Jared reported: "chatbox on purebrain.ai/pay-test/ (page ID 439) not connected to anything"

## Root Cause Analysis

After thorough investigation:

### What was actually wrong:
1. **PayPal CLIENT_ID was a placeholder** (`'PAYPAL_CLIENT_ID'`) - payment buttons didn't connect to PayPal
2. **LOGGING_ENDPOINT was wrong** - was pointing to `sageandweaver-network.netlify.app/api/capture-proxy` instead of the actual log server at `89.167.19.20:8443`
3. `USE_SDK_APPROACH = true` with placeholder CLIENT_ID caused PayPal SDK to attempt loading with invalid credentials (graceful fallback but confusing)

### What was NOT wrong (common red herrings):
- The chat engine JavaScript was IDENTICAL to the working homepage
- Both API endpoints (`api.puremarketing.ai/v1/messages` and `pure-brain-dashboard-api.purebrain.workers.dev/v1/messages`) were working
- CORS was properly configured
- HTML structure was correct
- DOM elements all existed and were accessible

## Architecture Insight: WordPress + Elementor + Full HTML Pages

**Key pattern** for purebrain.ai:
- Pages use Elementor Canvas template (strips WP header/footer)
- All content lives in a SINGLE Elementor HTML widget (id=292c72a)
- The widget contains a FULL HTML document (DOCTYPE, html, head, body)
- WordPress REST API endpoint: `GET /wp-json/wp/v2/pages/{ID}?context=edit`
- The actual editable content is in `meta._elementor_data` (JSON), NOT `content.raw`
- `content.raw` returns the rendered HTML output (not suitable for editing)

**Double-rendering pattern** (GoDaddy hosting):
- Live pages show Elementor widget content rendered TWICE
- This appears to be a GoDaddy/Elementor behavior
- Both renders show identical content - doesn't affect functionality
- `document.getElementById()` still finds the correct element

## Fixes Applied to Page 439

1. **LOGGING_ENDPOINT**: Changed from sageandweaver proxy to `https://89.167.19.20:8443/api/log-conversation` with sageandweaver as fallback
2. **logConversationToBackend**: Updated to try actual log server first, then fallback
3. **USE_SDK_APPROACH = false**: Switched PayPal to "Approach B" (direct form POST) - works without Client ID
4. **Timestamp updated** in HTML comment

## Fix Method

```python
# How to update page content (correct method):
import requests, json
session = requests.Session()
session.auth = ('Aether', 'FlFr2VOtlHiHaJWjzW96OHUJ')

# Fetch Elementor data
resp = session.get('https://purebrain.ai/wp-json/wp/v2/pages/439?context=edit')
d = resp.json()
elementor_data = json.loads(d['meta']['_elementor_data'])

# Modify HTML widget content
elementor_data[0]['elements'][0]['settings']['html'] = fixed_html

# Push update
session.post('https://purebrain.ai/wp-json/wp/v2/pages/439', json={
    "meta": {"_elementor_data": json.dumps(elementor_data)}
})
```

## Key WP Credentials
- User: Aether
- App password: FlFr2VOtlHiHaJWjzW96OHUJ
- Page IDs: 11 (homepage), 439 (pay-test), 319 (blog)

## PayPal Setup Notes
- PayPal Approach B (form POST) works WITHOUT a Client ID
- Approach B uses `paypal.com/cgi-bin/webscr` with hidden form fields
- Business email: `support@puremarketing.ai`
- For Approach A (SDK), need real Client ID from developer.paypal.com
- PLAN_IDS must be set for subscription billing

## Log Server
- URL: `https://89.167.19.20:8443`
- Endpoints: `/api/health`, `/api/log-conversation`, `/api/log-pay-test`, `/api/verify-payment`
- Uses self-signed SSL cert (browsers may warn for direct access)
- Server code: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`
