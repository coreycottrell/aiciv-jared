# Witness Portal → PureBrain Reskin

**Date**: 2026-03-03
**Type**: pattern / technique
**Agent**: dept-systems-technology

## Summary

Reskinned the Witness AI collective portal to PureBrain branding. Portal is a real-time terminal stream + chat interface running at http://89.167.19.20:8097/

## Files Modified

- `/home/jared/purebrain_portal/portal-pb-styled.html` — 170KB frontend, 3028 lines
- `/home/jared/purebrain_portal/portal_server.py` — 48KB backend, comments/strings only

## What Changed in HTML

### CSS Variables (root)
- `--gold: #f59e0b` → `#2a93c1` (PT Blue — primary accent)
- `--gold-dim: #a16207` → `#1a6a91`
- `--gold-glow` → PT Blue rgba values
- `--teal: #2dd4bf` → `#f1420b` (PT Orange)
- `--teal-dim/glow` → PT Orange rgba values
- `--warn: #f59e0b` → `#f1420b` (PT Orange)
- `--bg: #080812` → `#080a12` (site standard dark bg)
- `--font-ui` — Oswald added as first font

### Head Section
- Title: `AiCIV — Mission Control` → `PureBrain Portal`
- Added Google Fonts import for Oswald

### Logo Elements
- Auth overlay logo: `Witness` → `<span style="color:#2a93c1">PUREBR</span><span style="color:#f1420b">AI</span><span style="color:#2a93c1">N</span>`
- Header logo: same PureBrain color-split pattern
- Added `font-family: 'Oswald'` to both `.auth-logo` and `.logo` CSS classes

### Text References
- `Auth-sub`: "AI Civilization · Mission Control" → "AI Platform · Mission Control"
- Terminal connecting text: "Connecting to Witness..." → "Connecting to Aether..."
- Chat placeholder: "Message Witness..." → "Message Aether..."
- Terminal pane title: "aiciv-primary · tmux stream" → "aether-primary · tmux stream"
- Restart button title: "Restart Witness" → "Restart Aether"
- Claude auth modal: "Your AiCIV needs..." → "Your PureBrain AI needs..."
- Chat no-messages text: "...with Witness" → "...with Aether"

### JavaScript
- Sender name: `'Corey'` → `'You'`, `'Witness'` → `'Aether'`
- localStorage keys: `aiciv_bookmarks` → `purebrain_bookmarks`, `aiciv_portal_cmds` → `purebrain_portal_cmds`
- CIV default name: `'witness'` → `'aether'`
- Fleet panel check: `name !== 'witness'` → `name !== 'aether'`
- SSH user default: `'aiciv'` → `'aether'`
- makeCard default: `'Witness'` → `'Aether'`

## What Changed in portal_server.py

- Module docstring: "Witness Portal Server" → "PureBrain Portal Server"
- CIV_NAME fallback: `"witness"` → `"aether"`
- Startup print: "Starting Witness Portal" → "Starting PureBrain Portal"
- Comments updated (tmux session finder, pane filter)
- "Telegram messages from Corey" comment → "from Jared"

## What Was NOT Changed

- Zero JavaScript functionality touched
- No API endpoints or WebSocket logic modified
- No auth mechanism changed
- Responsive layout preserved
- All panels working: terminal, chat, fleet status, settings

## Verification

- 16/16 brand checks passed via Python verification script
- Live curl confirmed: title, Oswald font, PT Blue/Orange vars, PureBrain logo HTML all served correctly
- Server running: PID on port 8097, uvicorn startup confirmed

## Pattern: Third-Party Portal Reskin

When reskinning a third-party portal:
1. Read the file first to map all CSS vars, text references, JS strings
2. Use a single Python script for all replacements (atomic, easy to verify)
3. Run a verification script checking key strings before/after
4. Check for nested references (JS localStorage keys, defaults in functions, comments)
5. Verify with live curl against the running server, not just file content

## PT Brand Color Reference

- PT Blue: `#2a93c1` — primary, used for PUREBR + N in logo, --gold CSS var
- PT Orange: `#f1420b` — accent, used for AI in logo, --teal CSS var
- Dark bg: `#080a12` — site-wide standard
- Logo pattern: `<span style="color:#2a93c1">PUREBR</span><span style="color:#f1420b">AI</span><span style="color:#2a93c1">N</span>`
