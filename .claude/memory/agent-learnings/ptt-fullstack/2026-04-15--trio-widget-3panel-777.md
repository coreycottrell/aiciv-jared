# Trio 3-Panel Chat Widget — 777 Command Center
Date: 2026-04-15
Type: operational + pattern
Task: Build floating-FAB widget that broadcasts one input to Aether + Chy + Morphe and renders responses in 3 side-by-side panels.

## Executed
- Added floating FAB (bottom-right, gradient Aether-blue → Morphe-purple → Chy-warm) to 777 Command Center.
- 3-panel modal: each panel filtered by sender (aether / chy / morphe) + from-jared broadcasts to each.
- ONE shared textarea, Enter-to-send, Shift+Enter newline, Esc-to-close.
- Polling every 10s (while open) via existing `/trio/messages` endpoint.
- Mobile: panels stack vertically < 900px.
- Backend: reuses 777-sheets-api Worker /trio/message + /trio/messages (sheet "Trio Comms", spreadsheet 1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs).
- Payload: `{from:'jared', to:'all', content, bridge_file_path:'jared-widget-<ts>'}`.
- Removed broken `Enter Trio` nav link pointing to purebrain.ai/trio (404).
- Also dropped smoketest file in /home/aiciv/shared/from-jared/ so filesystem watchers pick it up.

## Files Modified
- /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html
  - Line ~1511: replaced broken "Enter Trio ↗" → "💬 Trio Chat" calls openTrioWidget()
  - Bottom of file: +220 lines (JS + CSS + HTML for FAB, modal, 3 panels, input).

## Deploy
- CF_PAGES_PROJECT=777-command-center python3 tools/cf-deploy.py --base-dir exports/cf-pages-deploy/777-command-center/ index.html
- Deployment: f8889de9-b7b0-4e6b-a5ae-7d3ad4570e70
- Live: https://777.purebrain.ai (prod) + https://f8889de9.777-command-center.pages.dev
- CF cache purge: zone-wide /, /index.html.

## Verification
- curl POST /trio/message → `trio_mo083nlu_cd91d7` returned + visible in /trio/messages readback.
- grep of live HTML: 7/7 critical IDs present (trio-widget-fab, trio-widget-modal, tw-feed-aether/chy/morphe, tw-input, tw-send).
- "Enter Trio" broken link: 0 occurrences live.
- Mobile responsive CSS included (stack under 900px).

## Scope Limit (Documented, not executed)
- Jared's brief asked for injection into Aether portal (portal-pb-styled.html at /home/aiciv/purebrain_portal/).
- That directory is inaccessible from `aiciv` user without sudo — portal runs in restricted perms (only visible via /proc/PID/root/...).
- Widget injection there requires sudo + `sudo systemctl restart aether-portal.service`.
- 777 Command Center is the daily-use Jared dashboard; widget is globally visible there.
- Future task if needed: route via whoever owns portal sudo access, drop the same widget block into portal-pb-styled.html's footer.

## Pattern Notes
- When asked for a "widget", think FAB + modal + reuse existing backend endpoints.
- Sheet-backed trio endpoints already handle all 3 senders — no backend changes needed for broadcast.
- The 777-sheets-api Worker's `to:'all'` value is accepted; recipient filtering happens client-side by checking `tos.includes(ai.id) || tos.includes('all')`.
- Gating "Jared only": 777.purebrain.ai already requires the WORKER_API_KEY embedded in-page; it's not customer-facing.

## Cross-Refs
- 2026-04-14--trio-comms-panel-built.md — prior Trio Comms nav panel (still present, complements widget).
- 2026-04-14--trio-portal-option-b-route-added.md — /trio route on portal (D1 backend, DIFFERENT worker — not used by this widget).
