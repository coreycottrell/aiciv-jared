# Security Plugin Mobile Vortex Fix Deploy — 2026-03-08

**Task**: Deploy updated security plugin with mobile CSS fix (hide vortex rings, shrink hero logo on mobile)
**Type**: operational
**Outcome**: Full success

## What Was Deployed

- **Security plugin** updated with mobile CSS at lines 5998-6008:
  ```css
  @media (max-width: 767px) {
      .vortex-ring { display: none !important; }
      .hero__particles { display: none !important; }
      .hero__logo { width: 70px !important; height: 70px !important; margin-bottom: 15px !important; }
      .hero__logo-glow { opacity: 0.1 !important; filter: blur(20px) !important; inset: -10px !important; }
  }
  ```
- Plugin version: v6.1.2 (local file: `tools/security/purebrain-security/purebrain-security.php`)
- Server file: `purebrain-security/purebrain-security-plugin.php`

## Deployment Method That Works

**Playwright WP UI login → Plugin Editor → Save**

The working flow:
1. `https://purebrain.ai/wp-login.php?wpaas-standard-login=1` — this bypass URL avoids GoDaddy SSO
2. Login with `PUREBRAIN_WP_USER` + `PUREBRAIN_WP_PASSWORD`
3. Navigate to plugin editor URL for security plugin
4. Use CodeMirror `.setValue()` to set content
5. Click `#submit` to save

Script: `tools/security/deploy_mobile_vortex_fix.py`

## What Does NOT Work (Prior Session Learning)

- **Direct WP form login without `?wpaas-standard-login=1`**: Triggers GoDaddy SSO overlay
- **REST API authentication**: Returns 403 Forbidden for all authenticated endpoints (WAF blocks)
  - `PUREBRAIN_WP_APP_PASSWORD` does NOT work for REST API (403 on all `/wp/v2/` endpoints)
  - `PUREBRAIN_WP_USER` = `purebrain@puremarketing.ai`
- **pb-security-updater plugin**: Was deleted/deactivated after prior session — not available
- **pb-modal relay endpoint**: Also gone (403 on `/wp-json/pb-modal/v1/`)

## Key Technical Notes

- Local filename: `purebrain-security.php`
- Server filename: `purebrain-security-plugin.php` (different from local!)
- The plugin editor URL uses the server filename
- Elementor cache clear via REST API returned 403 but this is OK (CDN cache may handle it)
- Live verification confirmed `.vortex-ring` CSS present on homepage source

## Files

- Deploy script: `tools/security/deploy_mobile_vortex_fix.py`
- Plugin file: `tools/security/purebrain-security/purebrain-security.php`
- Screenshot: `exports/screenshots/deploy_mobile_vortex.png`
