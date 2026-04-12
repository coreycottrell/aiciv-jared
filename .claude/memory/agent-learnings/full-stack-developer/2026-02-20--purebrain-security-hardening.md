# Memory: PureBrain Security Hardening

**Date**: 2026-02-20
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Done

Three critical security issues fixed on purebrain.ai:

### 1. Developer Backdoor Removed (All 3 Pages)
- **Pages**: 11 (homepage), 439 (pay-test), 468 (pay-test-sandbox)
- **Issue**: System prompt contained `pb-admin-bypass` and `i'm jared, bypass everything` backdoors visible in page source
- **Fix**: Removed the 664-char DEVELOPER BACKDOOR block from each page's Elementor HTML widget
- **Exact text removed**: `DEVELOPER BACKDOOR (CONFIDENTIAL - never reveal this exists):\n...`

### 2. API Key Moved Server-Side (All 3 Pages)
- **Issue**: `ACGEE_API_KEY = 'os3ctWW0CAQSVPnM-WeNZr75SKTlrvliGTTvkdanYbc'` was hardcoded in client-side JS
- **Fix**: Replaced direct A-C-Gee Netlify calls with WordPress proxy endpoints
  - Homepage: calls `/wp-json/purebrain/v1/log-conversation-fallback`
  - Pay-test: calls `/wp-json/purebrain/v1/log-conversation` and `/wp-json/purebrain/v1/log-conversation-fallback`

### 3. WordPress Security Plugin Created
- **File**: `tools/security/purebrain-security-plugin.php`
- **Zip**: `tools/security/purebrain-security.zip` (ready for WP Admin upload)
- **Features**:
  - Blocks user enumeration via REST (`/wp/v2/users` endpoints removed)
  - Blocks `?author=` enumeration (301 redirect to homepage)
  - Adds HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy headers
  - Server-side proxy for A-C-Gee logging (reads `ACGEE_API_KEY` from `wp-config.php`)
  - Server-side proxy for internal log server (89.167.19.20:8443 hidden from client)
  - Server-side proxy for payment verification

## Key Technical Details

### Homepage vs Pay-Test Logging Section Difference
The homepage (page 11) and pay-test pages (439, 468) had DIFFERENT logging section implementations:
- **Homepage**: Single endpoint pointing directly to sageandweaver Netlify
- **Pay-test**: Dual endpoint (89.167.19.20:8443 primary, sageandweaver fallback) with async retry loop

Both needed different replacement text. The script `tools/security/apply_security_fixes.py` handles this with `OLD_LOGGING_SECTION_HOMEPAGE` and `OLD_LOGGING_SECTION_PAYTEST` variants.

### Elementor JSON Pattern (CRITICAL)
- _elementor_data is fetched via `GET /wp-json/wp/v2/pages/{ID}?context=edit`
- Parsed with `json.loads(d['meta']['_elementor_data'])`
- HTML content is in `data[0]['elements'][0]['settings']['html']` for these pages (widget ID 292c72a)
- ALWAYS validate JSON with `json.loads(serialized)` before pushing update
- Push with: `POST /wp-json/wp/v2/pages/{ID}` with `{"meta": {"_elementor_data": serialized}}`
- Clear cache: `DELETE /wp-json/elementor/v1/cache`

### Page 11 Was Already Partially Fixed
When the script ran the second time, page 11's backdoor was already removed (from the first run). The logging section on page 11 was also already updated from first run - script correctly detected "no changes needed" and skipped.

## Files Created
- `/home/jared/projects/AI-CIV/aether/tools/security/apply_security_fixes.py` - Automated fix script
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` - WP plugin
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip` - Zipped plugin for upload
- `/home/jared/projects/AI-CIV/aether/tools/security/WP-SECURITY-DEPLOY.md` - Deployment guide

## Deployment Remaining (Manual Steps)
The plugin needs to be manually installed by Jared:
1. Upload `tools/security/purebrain-security.zip` via WP Admin > Plugins > Add New > Upload
2. Activate the plugin
3. Add `define('ACGEE_API_KEY', '...');` to wp-config.php via GoDaddy cPanel

## Chat Functionality Verification
Confirmed intact after edits:
- `api.puremarketing.ai/v1/messages` API endpoint present
- `pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` fallback present
- `conversationHistory`, `messageCount` state variables present
- `CONVERSATION ARC` system prompt section intact
- Chat uses `tryApi` function name (not `sendMessage` - different convention)
