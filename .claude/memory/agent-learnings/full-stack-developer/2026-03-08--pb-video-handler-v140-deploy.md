# pb-video-handler v1.4.0 Deploy

**Date**: 2026-03-08
**Type**: operational
**Topic**: Deploy new WordPress plugin (pb-video-handler) when not yet installed

## What Happened

Deployed pb-video-handler v1.4.0 to purebrain.ai. Plugin was NOT previously installed — only appeared in local repo.

## Key Pattern: Plugin Not Installed = Two-Step Deploy

When a plugin file exists locally but is NOT in the WP plugins list:
1. **Create zip**: `zipfile.ZipFile` — must be `pb-video-handler/pb-video-handler.php` inside zip (folder name matches plugin slug)
2. **Upload via WP Admin**: `https://purebrain.ai/wp-admin/plugin-install.php?tab=upload` — use `#pluginzip` file input + `#install-plugin-submit`
3. **Activate**: Click "Activate Plugin" link on result page
4. **Then** run plugin editor deploy script normally

## Plugin Editor URL Pattern

`https://purebrain.ai/wp-admin/plugin-editor.php?file=pb-video-handler/pb-video-handler.php&plugin=pb-video-handler/pb-video-handler.php`

Format: `?file={folder}/{file}.php&plugin={folder}/{file}.php`

Both `file` and `plugin` params must match the actual installed path exactly.

## What v1.4.0 Added

Inside `@media (max-width: 767px)` block:
- `.portal-vortex { display: none !important; visibility: hidden !important; }`
- `.vortex-ring { display: none !important; visibility: hidden !important; }`
- `.hero__particles { display: none !important; }`
- `.hero__logo { width: 70px; height: 70px; margin-bottom: 15px; }`
- `.hero__logo-glow { opacity: 0.1; filter: blur(20px); }`

Purpose: spinning hexagon vortex rings were covering the video background on mobile.

## Verification Method

Curl homepage, check for presence of CSS class names in source:
```bash
curl -s https://purebrain.ai/ | grep -o 'portal-vortex'
curl -s https://purebrain.ai/ | grep -o '.vortex-ring'
```

## Notes

- Elementor REST DELETE /cache returns 403 (blocked) — expected
- No Cloudflare API credentials in .env — CF cache purge must be done manually from dashboard
- Deploy scripts: `tools/security/deploy_pb_video_handler.py`, `tools/security/install_pb_video_handler.py`
