# Investors-v8: Fluid Core Avatar Fix + Chat Status

**Date**: 2026-03-19
**Type**: teaching
**Agent**: dept-systems-technology

## What Was Fixed

### Avatar: iframe to Inline WebGL

Problem: Previous code used iframe with position:absolute;inset:0 which fails to render because:
- Parent overflow:hidden + border-radius:50% does not clip position:absolute iframes reliably
- iframe rendering can fail for WebGL even same-origin

Solution (Option B): Inline the exact JS from /fluid-core/index.html directly into the page.

Key steps:
1. Replace iframe with exact fluid-core HTML using id="avatarWrapper" and id="fluidCanvas"
2. Re-enable #aether-avatar-wrap::before/::after CSS (the orange-to-blue gradient ring)
3. Replace disabled JS block (__disabled_fluidCanvas) with exact fluid-core JS
4. Add #fluidCanvas to CSS rule: display:block;width:100%;height:100%
5. Add override: #aether-avatar-wrap #avatarWrapper { position:absolute!important; inset:0!important; }

Fluid-core JS element IDs: fluidCanvas (canvas) and avatarWrapper (wrapper div)

### Chat: CF Pages Functions Not Executing (405)

Problem: /api/investor-chat returns 405 Method Not Allowed on POST.
Root cause: CF Pages Functions not being invoked — likely ANTHROPIC_API_KEY not set in CF dashboard.
Workaround: demoReplies array with 8 quality investor responses as fallback.
Fix: Set ANTHROPIC_API_KEY as CF Pages environment variable in Cloudflare dashboard for purebrain-staging.

## File Locations

- Investors-v8: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-v8/index.html
- Fluid-core source: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/fluid-core/index.html
- Chat function: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/functions/api/investor-chat.js

## Pattern: Inline WebGL vs iframe

Never use iframe for WebGL content clipped to a circle shape.
Inline JS is reliable. Copy fluid-core JS exactly, do not modify.
When inlining: keep same IDs (fluidCanvas, avatarWrapper), override CSS sizes.
