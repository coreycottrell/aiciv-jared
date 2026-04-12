# CTO Architecture: Video CSP R2 Fix - purebrain.ai

**Date**: 2026-03-01
**Type**: teaching + operational
**Topic**: Root cause analysis and fix architecture for HLS video failure on purebrain.ai

---

## The Problem

Three live pages (homepage, pay-test-2, pay-test-sandbox-2) had broken video:
1. Watch Demo modal: opened but video did not autoplay
2. Embedded video section: not playing at all

---

## Root Cause #1 (PRIMARY): CSP Missing R2 in connect-src

HLS.js uses XHR/fetch to download .m3u8 manifests and .ts video segments.
The Content-Security-Policy set by the plugin did NOT include the R2 bucket in connect-src.

**Effect**: Every HLS request was blocked. readyState=0, video never buffered.

**Fix**: Add to CSP connect-src:
```
https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev
```

**Also add** media-src directive for MSE blob: URLs:
```
media-src 'self' blob: https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev;
```

---

## Root Cause #2: openVideoModal() never triggered HLS

The function showed the modal div but never called HLS.loadSource() or video.play().
It was built for Cloudinary direct-MP4 era and never updated for HLS/R2 migration.

**Fix**: Rewrite openVideoModal() to:
1. Load HLS.js if not present (lazy CDN load)
2. Call Hls.loadSource(R2_HLS_URL)
3. Call Hls.attachMedia(video)
4. On MANIFEST_PARSED: video.play()

---

## Root Cause #3: Wrong HLS URL in embedded section

pb-demo-section used eaf39ae1_Portal_demo/master.m3u8 (Portal Demo).
New upload: 75114256_Pure-Brain-Demo-Video/master.m3u8 should be shown instead.

---

## Fix Architecture: Two-Part

### Plugin v4.7.4 (CSP)
- File: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v474.php`
- Build: `/home/jared/projects/AI-CIV/aether/tools/build_plugin_v474.py`
- Deploy: WP Admin plugin-editor.php (IPv4 forced, session cookie pattern)

### Elementor Data Fix (3 pages)
- Script: `/home/jared/projects/AI-CIV/aether/tools/deploy_video_fix_complete.py`
- Fixes: openVideoModal, closeVideoModal, pbDemoPlay IIFE, pb-demo-section HTML, awakening links

---

## Key Patterns for Future

1. **Any HLS.js video served from R2 needs R2 in CSP connect-src** - always check this first
2. **After video backend migration (Cloudinary -> R2), JS player functions need rewrite** - they don't auto-update
3. **media-src blob: is required for any MSE/HLS implementation** - standard requirement
4. **Diagnosis order**: Check CSP first (browser devtools Network tab shows blocked requests) before debugging JS

---

## Awakening Link Pattern

Each page's "Begin awakening" link must use page-specific URL, not site root:
- Homepage: https://purebrain.ai/#awakening
- Pay Test 2: https://purebrain.ai/pay-test-2/#awakening
- Pay Test Sandbox 2: https://purebrain.ai/pay-test-sandbox-2/#awakening

Using /#awakening from pay-test pages redirects to homepage, breaking the flow.

---

## Tags

video, hls, csp, cloudflare-r2, elementor, purebrain, homepage, pay-test, architecture
