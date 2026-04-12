# investors-v8: Real AI Chat + ElevenLabs Voice Wiring

**Date**: 2026-03-19
**Type**: operational + teaching
**Agent**: dept-systems-technology

## What Was Done

Wired investors-v8 chatbox and avatar TTS to real portal server endpoints.

### Changes Made

**1. investors-v8/index.html** (two URL changes via sed):
- /api/investor-tts → https://app.purebrain.ai/api/investor-tts
- /api/investor-chat → https://app.purebrain.ai/api/investor-chat
- File: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-v8/index.html

**2. portal_server.py** (ElevenLabs .env fallback added):
- api_investor_tts() now reads ELEVENLABS_API_KEY from portal env OR aether .env fallback
- File: /home/jared/purebrain_portal/portal_server.py line ~6429

## Verification Results

- POST https://app.purebrain.ai/api/investor-chat → 200 real GPT-4o response (tested)
- POST https://app.purebrain.ai/api/investor-tts → 503 (ElevenLabs key missing, by design)
- CORS: access-control-allow-origin: https://purebrain.ai confirmed on OPTIONS preflight
- Live page https://purebrain.ai/investors-v8/ already serves the portal URLs

## To Activate ElevenLabs

Add to /home/jared/purebrain_portal/.env:
ELEVENLABS_API_KEY=<key>
Then: sudo systemctl restart aether-portal.service

## CF Pages Token Issue

CF_PAGES_TOKEN lacks Account Read permission. Wrangler needs it for /memberships call.
Fix: Regenerate token at dash.cloudflare.com with Cloudflare Pages Edit + Account Read permissions.
