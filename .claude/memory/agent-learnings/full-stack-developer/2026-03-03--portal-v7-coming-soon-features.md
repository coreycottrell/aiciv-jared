# Portal v7 — All v8 Features Added as Coming Soon

**Date**: 2026-03-03
**Type**: technique
**Topic**: Portal upgrade — all v8 features with Coming Soon popup modal

## What Was Done

Upgraded `/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-rebranded.html` from v6 to v7 by adding all v8 features as "Coming Soon" items with a popup modal.

## Changes Applied (14 total)

### CSS Additions
1. **Coming Soon modal** — Full modal with overlay, glassmorphism card, animated entry, sparkle icon, orange title, description, "Got it" button
2. **Header icon buttons** (`.hdr-icon-btn`) — 34x34 buttons for top bar
3. **Quick action pills** (`.quick-action`) — Pill-shaped buttons below input
4. **Input icon buttons** (`.input-icon-btn`) — Attachment + voice buttons in input bar
5. **Coming-soon items** — Changed from `opacity:0.4; cursor:default` to `opacity:0.7; cursor:pointer` so they're clickable

### HTML Additions
6. **Coming Soon modal HTML** — `#cs-modal-overlay` + `#cs-modal-card` before Three.js importmap
7. **Top bar icons** — Search, Dark/Light, New Chat, Share (orange), Artifacts, Keyboard Shortcuts in `chat-header__right`
8. **History nav item** — In Workspace section with orange badge "1"
9. **Conversations section** — Below Workspace, shows "New Chat · Just now"
10. **Projects/Goals/Tasks/Brains** — All `new-item-btn` elements made clickable with `onclick="showComingSoon(...)"`
11. **Brains Explore button** — New second item in Brains section
12. **Skills Update** — Updated to "New Skills Today · 2h ago" with Advanced Analytics + Design System Gen
13. **Quick action pills** — 5 pills: Check emails, Analytics, Landing page, Research, Schedule Task
14. **Input bar** — Attachment button (left), Voice button (right of textarea), before Send button
15. **User section** — "Guest User" with "2 referrals · $127.50 earned" sub-text

### JS Additions
- `window.showComingSoon(title, desc)` — shows modal with content
- `window.closeComingSoon()` — hides modal
- `window.handleCSOverlayClick(e)` — closes on overlay click
- `document.addEventListener('keydown')` — closes on Escape key

## Key Patterns

### Coming Soon Modal Architecture
- Modal lives outside the app-body div to ensure z-index stacks above everything
- Added BEFORE the Three.js importmap (before end of body)
- JS functions defined at TOP of portal logic script block (before IIFE)
- Modal uses `display:none` + `.active { display:flex }` pattern (not visibility:hidden) for animation compatibility

### Popup Trigger Pattern
All coming-soon items use: `onclick="showComingSoon('Title', 'Description text here'); return false;"`
- `return false` needed on `<a href="#">` elements to prevent page jump
- Button elements don't need `return false`

### Preserved Functionality
- Login (bypass token: `purebrain-admin-2026`)
- Chat WebSocket
- Terminal WebSocket
- Status panel
- 3D neural network background
- Canvas welcome hero animation
- Sidebar collapse button
- Mobile hamburger menu

## File Location
`/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-rebranded.html`
Size: 2710 lines, ~163KB

## Delivery
Sent via `tg_send.sh --file` to Jared
