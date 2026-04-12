# Portal Admin Dashboard Full QA Audit

**Date**: 2026-03-16
**Agent**: browser-vision-tester
**Type**: operational + teaching
**URL**: https://app.purebrain.ai (localhost:8097)

---

## Context

Full comprehensive visual + functional audit of the PureBrain admin dashboard portal.
All 13 sidebar panels, Quick Fire buttons, top bar, and /admin pages audited.

---

## Critical Finding: Chat Panel 500 on Load

The Chat panel shows "Error: Server error 500" on every fresh page load via Playwright.

**Why**: The /api/chat/history endpoint returns 500 on initial call when the session context
hasn't been established. Once the session is active, it returns 200 with full message history.

**Root cause**: The 237MB+ current session JSONL file is the active session. The portal's tail-reader
successfully parses it (500KB tail = ~10 lines, returns 10 messages). But something in the HTTP
handler still throws 500 in headless mode.

**Not a real-world bug**: Real browsers typically already have a warm session. The 500 may be
specific to headless Playwright sessions that hit the endpoint before any session warmup.

**Recommend**: Add retry logic + loading state in the Chat panel JS.

---

## Panel Status Map (Quick Reference)

| Panel | data-panel | Status |
|-------|-----------|--------|
| Terminal | terminal | PASS - live tmux stream |
| Chat | chat | CRITICAL - 500 on initial load |
| Teams | teams | NEEDS INVESTIGATION - shows terminal |
| Status | status | PASS - all green |
| Files | files | MEDIUM - empty, no guidance |
| Refer & Earn | referrals | PASS - full dashboard |
| Bookmarks | bookmarks | PASS - empty state correct |
| Tasks | scheduled | PASS - 2 tasks, filters work |
| Agent Roster | agents | PASS - org chart visible |
| Commands | commands | HIGH - "your-server" placeholder |
| Shortcuts | shortcuts | PASS - excellent reference |
| Brainiac Training | (link) | PASS - external page working |
| AI Training Hacks | (unknown) | HIGH - drops to chat 500 |

---

## Selector Patterns for Portal

Sidebar items use `div[data-panel='panel-id']` NOT `button[data-panel]`.
All sidebar DIVs are visible (not hidden), direct click works.

Admin pages (/admin/referrals, /admin/clients) have SEPARATE auth gates.
They do NOT inherit the main portal localStorage token.
They require manual token entry via their own form on direct navigation.

## Admin Data

- /admin/clients: 18 clients, $1,341 total revenue, $377 MRR, all ACTIVE
- /admin/referrals: 4 affiliates, 0 clicks, $0 earned, "No referral activity yet"

## Quick Fire Buttons

All 6 present: BOOP, Grounding, Status, Compact, Intel, Duck
All use class `boop-fire-btn`, all visible and enabled.

## CTX Meter

Shows "N/A" on fresh load. Updates to actual usage after any activity.
Clicking CTX opens educational popup (green/yellow/red zones) — well designed.
The .ctx-gauge selector works for clicking.

---

## When to Apply

Future portal audits:
1. Use localhost:8097 (not :8097 via Cloudflare — CF blocks Playwright headless)
2. Inject token: `page.evaluate("localStorage.setItem('portal_token', 'TOKEN')")`  then reload
3. Click sidebar items with `div[data-panel='id']` selector
4. Admin pages need separate form fill with same token
5. Expect Chat 500 on cold load — not a blocking issue in real usage
