# Portal v4: v8 Dashboard Design Merge

**Date**: 2026-03-03
**Type**: pattern
**Agent**: dept-systems-technology

## What Was Done

Rebuilt the PureBrain portal's post-login dashboard to visually match the v8 dashboard design, while preserving all existing login/auth functionality.

## Key Pattern: Design-Only Merge Without Feature Build-Out

When Jared wants a portal to LOOK like a reference design without having all features coded:
1. Extract CSS variables + layout classes from reference
2. Keep ALL auth/login HTML unchanged
3. Replace only the post-login HTML structure
4. For every non-functional feature: apply `.nav-item.coming-soon` + opacity:0.4 + `<span class="nav-cs-tag">Soon</span>`
5. Keep all existing JS functional — just update DOM element IDs to match new HTML

## File Paths

- **Portal file**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-rebranded.html`
- **v8 reference**: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/pure-brain-v8-aether-dashboard.html`

## v8 Sidebar Structure (Replicated Exactly)

```
sidebar
  sidebar__header (logo icon + wordmark + collapse btn)
  sidebar__new-chat btn
  sidebar__collapsible
    ai-profile (AI avatar card with name — clickable for voice)
    sidebar__nav
      nav-section "Workspace" — Chat, Terminal, Command Center(CS)
      nav-section "Recent Conversations" — chat history list
      nav-section "Projects" — New Project (CS)
      nav-section "Goals" — New Goal (CS)
      nav-section "Tasks" — Schedule Task (CS)
      nav-section "Brains" — New Brain (CS)
      skills-update card
      nav-section "Account" — System Status, Settings(CS), Refer(CS)
  sidebar__user (avatar + name + status)
```

CS = Coming Soon (opacity 0.4, tooltip, `.nav-cs-tag`)

## Panel Switch Pattern

```javascript
window.showPanelChat = function() { switchPanel('chat'); };
window.showPanelTerminal = function() { switchPanel('terminal'); };
window.showPanelStatus = function() { switchPanel('status'); };
```

Panels use `class="panel"` + `class="panel active"` for display toggling.
Default active panel: `chat` (not terminal as in old v3).

## Bypass Token

`purebrain-admin-2026` — unchanged, works exactly as before.

## AI Name Flow

Login page input `ainame-input` → stored in `storedAIName` → `updateSidebarAIName()` called in `boot()` → updates `#aiName`, `#chatEmptyName`, `#chatEmptyInitial`.

## Verification Result

53/53 checks passed. File: 134KB, 2070 lines.
