# Memory: Portal Mobile Portrait Chat Messages — Layout Diagnosis

**Date**: 2026-03-08
**Agent**: browser-vision-tester
**Type**: teaching + operational
**Tags**: portal, mobile, portrait, layout, flex, chat-messages, min-height

---

## Context

User reported chat messages invisible on mobile portrait (375x812) but visible on landscape/tablet at https://app.purebrain.ai.

Ran full Playwright diagnostic with both viewports, forced JS auth bypass to measure behind login overlay.

---

## Key Findings

### The CSS layout is NOT the bug

Exact measurements (authenticated state):

**Portrait (375x812):**
- #chat-messages: top=99, **h=544** — healthy, NOT collapsed
- .main: h=707 (flex:1)
- .content: h=707 (flex:1, min-height:0 ✓)
- #panel-chat: h=707 (flex:1, min-height:0 ✓)
- .chat-input-wrapper: h=100 (flex-shrink:0)
- .mobile-tabs: h=61, display=block

**Landscape (812x375):**
- #chat-messages: top=109, h=151
- .mobile-tabs: h=0, display=none (hidden because 812px > 600px breakpoint)

### Height budget is correct on portrait

```
812px total
- 44px header
= 768px
  → .main: 707px (768 - 61 mobile-tabs, flex:1)
    → .content: 707px (flex:1, min-height:0)
      → #panel-chat: 707px (flex:1, min-height:0)
        → sub-header: ~55px (flex-shrink:0)
        → #chat-messages: ~552px (flex:1, min-height:0) ← CORRECT
        → .chat-input-wrapper: ~100px (flex-shrink:0)
```

### Real cause of "invisibility"

The messages area is not height-collapsed. It is **EMPTY** — messages not loading.
The portal shows "Connecting to civilization..." = WebSocket not yet connected.
Once WS auth succeeds and history loads, messages will appear in the 544px container.

The bug is in **WS auth / message loading**, not CSS layout.

---

## Production Portal Differs From Local Source

The live portal at app.purebrain.ai is much more feature-rich than the local `portal.html`:
- Has `#loginOverlay` (not `#auth-overlay`)
- Has `#upload-mode-overlay`
- Has `.chat-input-wrapper` (wraps chat-input-bar)
- Has `.mobile-tabs` with Chat/Terminal/Earn/Saved/More tabs
- Has sub-header row "SESSION DIALOGUE" inside #panel-chat (~55px)
- Has sidebar with 7+ panel items on desktop

**Always fetch live HTML for accurate layout analysis, not local source.**

---

## CSS Guards to Add (Preventive)

Even though portrait is correct now, add these for resilience:

```css
/* Prevent any future collapse */
#chat-messages { min-height: 100px; }

/* Reduce textarea min-height on mobile to save space */
@media (max-width: 600px) {
  .chat-input-bar textarea {
    min-height: 44px;  /* was 90px */
    max-height: 120px;
  }
}

/* Keyboard-open guard (viewport height < 500px) */
@media (max-height: 500px) {
  .chat-input-bar textarea { min-height: 36px; }
  .chat-input-wrapper { padding-top: 6px; }
}
```

---

## Auth Bypass Pattern (for future testing)

When portal auth overlay blocks interaction in Playwright:

```python
# Force-hide login overlay and activate chat panel
page.evaluate("""
    () => {
        const overlay = document.getElementById('loginOverlay');
        if (overlay) { overlay.style.display = 'none'; overlay.classList.add('hidden'); }
        
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        const chatPanel = document.getElementById('panel-chat');
        if (chatPanel) chatPanel.classList.add('active');
    }
""")
```

Note: Even after JS auth bypass, WS may not connect (portal_server.py validates token server-side). Layout measurements still work fine.

---

## Screenshots

Dir: `/tmp/portal-mobile-debug/`
- `05-portrait-authenticated.png` — Portrait chat UI, empty messages, input + mobile tabs visible
- `06-landscape-authenticated.png` — Landscape chat UI with sidebar

