# investors-v8: Three Upgrades — Data Room Brain, ROI Button Fix, Avatar Greeting

Date: 2026-03-20
Type: teaching + operational
Files changed:
- /home/jared/purebrain_portal/portal_server.py — _INVESTOR_SYSTEM_PROMPT
- /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-v8/index.html

## Task 1: Data Room Knowledge in Chat Brain

Replaced the short bullet-list _INVESTOR_SYSTEM_PROMPT in portal_server.py (line ~6359) with the full investor data room content from exports/investor-agent-system-prompt.md.

New prompt includes: company identity, problem/solution, Pure Phone specs, revenue model (~$1,792/user/year), 5-year financials, market TAM, full investment terms (MAKR $25M Series A, $105M pre-money), leadership team, tech stack, product portfolio, key differentiators, Q&A for common investor questions.

Portal restart required after: sudo systemctl restart aether-portal.service

## Task 2: scrollToSec Bug Fix

THE BUG: scrollToSec(idx) used document.querySelectorAll('[data-section]')[idx] which matched ALL elements with data-section attribute. Nav dots (14 of them, lines 611-624) come before content sections in DOM. scrollToSec(7) hit nav dot 7, not section 7.

THE FIX: document.querySelector('.content-section[data-section="' + idx + '"]') — targets specific section by value directly. Works for all 14 sections.

## Task 3: Auto-Greeting with Web Speech API

Added script block before </body>:
- triggerAvatarGreeting() waits 3s after gate dissolves, then:
  - Appends greeting bubble to #chat-messages
  - Calls multipleSplats(6/4/3) staggered at 600ms for fluid animation
  - Sets avatar state 3 (speaking) via setAvatarState(3)
  - Speaks via window.speechSynthesis (free, no ElevenLabs cost)
  - Voice preference: Google en-US first, any en-US, then voices[0]
  - Handles voice load delay via onvoiceschanged + 1000ms fallback

- MutationObserver watches #gate for class change to 'dissolved' — fires greeting (works for both password and ?open=1 bypass)

Greeting text: "Welcome. I'm Aether, the AI Co-CEO of Pure Technology. Ask me anything about our business, technology, or investment opportunity."

KEY PATTERN: Use MutationObserver to hook into existing gate logic rather than patching gate functions directly.

## Deployment
- CF Pages: purebrain-staging deployed
- Portal: restarted via systemd
- Cache: purged via CF API
- Live: https://purebrain.ai/investors-v8/?open=1
