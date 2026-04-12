# iOS Video Autoplay Fix Patterns
**Date**: 2026-03-11
**Agent**: dept-systems-technology
**Type**: gotcha + technique
**File**: exports/cf-pages-deploy/index.html (purebrain-staging homepage)

---

## The Problem

iPhone Safari was showing the native play button instead of autoplaying the background brain video. Android worked fine.

## Root Causes Found (3 separate issues)

### 1. Missing `body.home` class (CRITICAL)
The `<body>` tag had NO classes. Every mobile CSS rule targeting `body.home .video-background` was dead code.

**Fix**: `<body class="home">`

### 2. `vid.muted` not set as JS property before first `play()` call
iOS Safari requires `vid.muted = true` at the JavaScript property level - NOT just as an HTML attribute (`muted`). The HTML `muted` attribute alone is insufficient for iOS autoplay. The original code only set `vid.muted = true` inside the user-interaction handler, not before the initial play attempts.

**Fix**: Add these lines before ANY `play()` call:
```js
vid.muted = true;
vid.setAttribute('muted', '');
```

### 3. Missing `loadedmetadata` / `canplay` / `loadeddata` event triggers
iOS needs play() triggered when video is actually ready to play, not just on script execution. These events are reliable iOS autoplay triggers.

**Fix**:
```js
vid.addEventListener('loadedmetadata', function() { vid.muted = true; vid.play().catch(function(){}); });
vid.addEventListener('canplay', function() { vid.muted = true; vid.play().catch(function(){}); });
vid.addEventListener('loadeddata', function() { vid.muted = true; vid.play().catch(function(){}); });
```

## iOS Autoplay Rules (locked in)

1. `autoplay` HTML attribute required
2. `muted` HTML attribute required
3. `playsinline` required (prevents fullscreen takeover)
4. `webkit-playsinline` required (older iOS)
5. `vid.muted = true` JS property MUST be set before any `play()` call
6. `vid.setAttribute('muted', '')` as belt-and-suspenders
7. `play()` should be triggered on `loadedmetadata`, `canplay`, `loadeddata` events

## Deployment

```bash
CF_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2)
CLOUDFLARE_API_TOKEN=$CF_TOKEN npx wrangler pages deploy exports/cf-pages-deploy --project-name=purebrain-staging --branch=main --commit-dirty=true
```

## Verification
- `<body class="home">` confirmed at line 7858
- `vid.muted = true` confirmed before first `play()` at line 12955
- Three new event listeners confirmed at lines 12967, 12971, 12975
- Deployed: https://fa3c656a.purebrain-staging.pages.dev
