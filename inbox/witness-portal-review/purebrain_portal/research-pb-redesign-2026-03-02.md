# Team Web Scratchpad - 2026-03-02

## Objective
Map the current portal.html functionality onto PureBrain's design language.
Create `/home/aiciv/purebrain_portal/portal-pb-styled.html` — a single self-contained HTML file
that preserves all current portal functionality with PureBrain's visual style.

## Memory Search Results
- Searched: `/home/aiciv/.claude/memory/agent-learnings/web-dev/`
- Found: `20260226-frontend-gateway-diagnosis.md` — thorough analysis of gateway/frontend connection issues, CORS, auth patterns, zero-deps policy
- Applying: Zero external JS deps policy, same-origin architecture understanding, bearer auth pattern

## Agents Called
None (executed directly — task was design + implementation, well within scope of team lead)

## Decisions Made

### Design Language Extracted from PureBrain Frontend
- **Signature gradient**: `linear-gradient(135deg, #f1420b, #2a93c1)` — orange-to-blue, used everywhere
- **Colors**: --bright-orange #f1420b, --light-blue #2a93c1, --black #0a0a0a, --card-bg rgba(20,20,20,0.97)
- **Borders**: `rgba(255,255,255,0.1)`, border-radius 10-16px
- **Auth card**: Rounded card (border-radius 20px) with gradient logo, gradient button
- **Nav items**: 10px border-radius, orange tint on active, sidebar + mobile bottom nav
- **Chat bubbles**: User = gradient orange, AI = card-bg with border
- **Status dots**: Green with pulse animation
- **Submit buttons**: Gradient orange-to-blue, scale on hover
- **Font fallbacks**: system fonts (no Google Fonts — zero external deps)

### Key mapping decisions
1. Auth overlay → PureBrain login card style (gradient logo, clean form)
2. Sidebar nav → PureBrain nav-item style (rounded, orange active state)
3. Terminal → chrome-dot bar + dark output area
4. Chat bubbles → PureBrain message style (gradient user, card AI)
5. Status cards → PureBrain stat-card style
6. Mobile → PureBrain mobile-bottom-nav style
7. Header → gradient logo icon + gradient text name

## Issues Encountered
- PureBrain uses Google Fonts (Oswald, Plus Jakarta Sans, JetBrains Mono) — NOT included per zero-deps rule
- Used system font fallbacks instead: system-ui for body, monospace stack for code
- PureBrain is 13,535 lines — extracted only the design tokens and component patterns needed

## Deliverables
- `/home/aiciv/purebrain_portal/portal-pb-styled.html` — 980 lines, 37KB
  - All portal.html functionality preserved (terminal WS, JSONL chat, status, auth, mobile tabs)
  - PureBrain design language applied throughout
  - Zero external dependencies
  - Mobile-first bottom nav pattern
  - Auto-resize textarea for chat input

## React/Flutter Cross-Platform Note (for Corey's question)
"If we had them convert it to react or flutter could we use that on our AICIVs local machines?"

**React**: YES, viable for cross-platform. Could be a PWA (Progressive Web App) that runs in any browser including on Android/iOS home screen. Build step required (Create React App or Vite). Would enable component reuse across multiple portals but requires npm + build toolchain on each AiCIV VPS.

**Flutter**: YES, but different tradeoff. Flutter compiles to native Android/iOS, macOS, Windows, Linux, AND web. Single codebase for all platforms. Better mobile performance than React. Heavier to set up — requires Flutter SDK. The web output is still a single-page app that can be deployed to a VPS.

**For AiCIV local machines specifically**: The current single-file HTML approach is actually IDEAL for AiCIV VPS deployment (zero build step, scp one file). React/Flutter become valuable only if:
1. You want native mobile apps (not just mobile web)
2. You're building enough UI complexity to justify the component system
3. Multiple developers are working on the frontend

**Recommendation**: Keep single-file HTML for now. If portal grows beyond ~1500 lines of logic, migrate to React (not Flutter) for web-first AiCIV portals.

## Cross-References
- CROSS-REF: Gateway team should note that portal-pb-styled.html still uses same API contracts (`/api/status`, `/ws/terminal`, `/api/chat/*`) — no backend changes needed
- CROSS-REF: Fleet team may want to copy portal-pb-styled.html to VPS gateway to replace current portal.html

## Status: COMPLETE
