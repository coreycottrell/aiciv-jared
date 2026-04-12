# investors-v8: Fluid Sim Fix + AI Chat Wiring
**Date**: 2026-03-19
**Type**: operational + teaching

## Root Cause: Fluid Sim Not Animating

The avatar's Navier-Stokes WebGL simulation ran immediately on script parse — before the page
fully rendered — so canvas.clientWidth/clientHeight returned 0. WebGL framebuffers initialized
at 0x0 and the update() loop rendered nothing.

**Fix**: Wrap entire avatar fluid script in window.addEventListener('load', function() { (function() { ... })(); });
window.load fires after layout completes, guaranteeing non-zero canvas dimensions.

## AI Chat Endpoint

Added /api/investor-chat and /api/investor-tts to portal_server.py (live: /home/jared/purebrain_portal/portal_server.py).
Uses OpenAI GPT-4o with .env fallback. Investor system prompt with full valuation/projection facts.
Routes inserted near /api/investor/question (line ~6353 in live server).

## Verification
- Portal syntax: PASS
- Endpoint test: curl localhost:8097/api/investor-chat returned real GPT-4o response
- CF Pages deployed: investors-v8/index.html updated
