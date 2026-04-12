# Memory: 777 Command Center v2 Technical Specification

**Date**: 2026-04-10
**Type**: teaching
**Agent**: architect
**Task**: Full technical specification for 777 Command Center v2 — a 3-layer personal + company OS

---

## Pattern: Multi-Layer Single-HTML Dashboard Architecture

When a client-side dashboard needs to aggregate from 4+ API sources with independent failure modes, the correct pattern is:

**Promise.allSettled + per-section error states**

Each section owns its own loading/error/data state. `Promise.allSettled` at the orchestrator level ensures no single API failure cascades. This is especially critical when some sources (Google OAuth) require user interaction while others (Portal API) are automatic.

## Key Architectural Choices for This Project

1. **Single HTML file maintained despite complexity** — 20,000-25,000 lines is manageable with clear section comment headers. CF Pages deployment simplicity outweighs the cost of a build pipeline for a personal CEO dashboard.

2. **Tab-based 3-layer navigation with URL hash** — `#personal`, `#triangle`, `#team` enable deep-linking from Telegram. No client-side router needed — just CSS display toggling with `data-tab` attributes.

3. **Google OAuth2 implicit flow for client-side** — No server needed. Token in `sessionStorage` (not localStorage). Scope covers both Sheets and GA4 in one auth flow. Client ID exposed in source is acceptable for a password-gated personal tool.

4. **Write-back to source, not to intermediate store** — Morning Pulse priorities write to TOS Sheet. Content approval writes to BaaS API. No local state mutation before confirm — avoids stale UI after network failure.

5. **5-minute refresh for live layers, 60-minute for GA4** — GA4 Reporting API calls are expensive (quota). Separate intervals. Sheets and Portal API refresh every 5 min.

6. **CSS grid heatmap, not Chart.js** — Chart.js has no native calendar heatmap type. A 90-cell `<div>` grid with `background-color` per cell is simpler, lighter, and more responsive.

## Spreadsheet Schema Designed

- v1 sheet: untouched (Layer 1 reads exactly as before)
- TOS sheet: 4 tabs (Morning Pulse, Handshake Queue, EOD Report, Weekly Review) with specific column schemas
- Team whitelist sheet: 9 required columns (some may need to be added to existing sheet)

## Open Questions Left for Jared (before Phase 2 starts)

1. Portal API endpoint availability (`/api/activity`, `/api/boop/status`, etc.)
2. BaaS auth header format
3. Google OAuth client ID existence
4. TOS sheet tab structure (already exists or needs creating)
5. Color update (v2 uses Tailwind orange-500/blue-500 vs. v1 hex values)
6. Meeting data source for Layer 3

## Files Produced

- Spec: `/home/jared/exports/portal-files/777-v2-technical-spec.md`
  - 12 sections, architecture diagram, data flow map, UX wireframe, build plan (5 phases, 10-12 days), security model

## Context

- v1 at 777-command-center.vercel.app. Code at `exports/777-command-center/index.html`.
- v1 design system: `--bg: #080a12`, `--orange: #f1420b`, `--blue: #2a93c1`. v2 slightly warmer.
- Portal API at localhost:8097 (portal_server.py). BaaS at surf.purebrain.ai.
- TOS sheet ID: `1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs`
- Team whitelist ID: `1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E`
