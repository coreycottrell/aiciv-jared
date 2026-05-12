# Aether Scratch Pad

**Purpose**: Persistent state across BOOPs and sessions. Prevents redoing work.
**Last Updated**: 2026-05-12

## ✅ RESOLVED 2026-05-12 03:48 UTC — Synthetic Monitor False-Alert Storm
- **Issue**: `tools/synthetic-monitor-critical-pages.sh` writing 12 false alerts/hour for /user-guide/ (393 files accumulated) due to CF edge-config rewriting `?_cb=*` cache-bust query strings to 404 while clean URL serves 200. 4-BOOP convergence (00:46 / 01:47 / 02:47 sub-agent BOOPs + 03:48 main-thread).
- **Fix**: Patched script with paired-probe gate. Cache-bust 404 + clean 200 = log to `logs/critical-pages-edge-divergence.log` (informational, no alert). Both probes 404 = real-outage alert (preserved). Verified 0 new alerts after fix run.
- **Archive**: 390 noise files moved to `inbox/archived/monitor-false-alerts-2026-05-11-to-12/` (evidence preserved, not deleted).
- **Memory referenced**: `feedback_synthetic_monitors_must_match_real_user_traffic.md`, `feedback_query_string_routing_rules_can_break_cache_bust_probes.md`, `feedback_out_of_repo_edge_config_is_blind_spot.md`. Direct execution per "delegation chain structurally fails 2+ times" rule.

## 🔴 TIER-1 BLOCKER (2026-05-11) — STILL OPEN
- **PureSurf API auth broken**: surf.purebrain.ai health=200 but BOTH stored keys (jared `WtHJY1zr...` + aether `O_EnHpl...`) return `401 Invalid API key`. Discovered during morning profile-viewing BOOP — full LinkedIn profile-viewer + comment-scheduler pipeline BLOCKED.
- **Affected**: `tools/linkedin_profile_viewer.py`, `tools/linkedin_daily_pipeline.py`, `tools/linkedin_comment_scheduler.py`, surf.purebrain.ai consumers.
- **ROUTE**: ST# investigate PureSurf API key rotation/discovery. Likely keys rotated server-side without consumer update.
- **Day-3 default activation**: 17h+ elapsed since 09:03 UTC 2026-05-11 — pending main-thread Aether→ST# dispatch at next ~12:00 UTC wake-window per bundled-relay cadence.

## ACTIVE RIGHT NOW
- 777 Command Center v2 LIVE at 777.purebrain.ai (password: 777grind)
- Triangle OS fully operational (Aether + Chy, all 5 components)
- Intelligence Compounding Engine sent to full team (17 AIs)
- 53 BOOPs running, all verified working
- 7 logo options generated for 777 brand (in Drive Logos folder)
- Rimah/Vira seed fired — awaiting Witness magic link

## SESSION HIGHLIGHTS (Apr 10-11)
- 777 v2: 52 sections, 69 tabs mapped, Sheets API wired, CF Worker deployed
- 3-track strategic timeline: Investors/Crowdfunding/Sales with milestone offshoots
- Triangle Deliverables Log: daily/weekly/monthly/yearly tracking
- Historical Archives: 35,278 tasks (2019-2026) accessible from dashboard
- Triangle OS guide page: purebrain.ai/triangle-os/
- Team whitelist + routing SOP locked in with Chy (mandatory CC rules)
- BOOP overhaul: nightly agent activation, daily dept production, daily Chy mentorship
- Brainiac Module 6 processed from Zoom
- 8 HR tools + fin.ai added to calculator (292+ tools)
- Nightly tool discovery BOOP created
- Daily hub skill sync with auto-create/suggest/distribute
- Tailscale strategy researched + shared with Corey/ACG
- Onboarding E2E test passed (seed → Witness → magic link 4m44s)
- Customer portals fixed: Vantage (timestamp bug) + Delta (Chrome/CPU/tmux)
- Vishal testimonial updated across 12 pages
- 20+ team emails responded to with proper CC rules

## DO NOT RE-DO
- Everything listed above
- All previous scratch pad items
- 777 v2 deployed + wired to Sheets
- CF Worker at 777-api.purebrain.ai
- TOS spreadsheet populated by Chy
- Whitelist spreadsheet fully updated (3 tabs)
- Weekly-sunday BOOP bug FIXED (executor restarted)
- All disabled BOOPs removed (was 54 → now 53 active)
- Travis/Delta added to Investors tab of whitelist
- Pulse report BOOP changed to weekly-thursday

## CHRONIC ISSUES (STILL OPEN)
- Email welcome sequence: 14+ flags, NEVER built. Route to MA# ASAP.
- LinkedIn automated posting blocked: stale cookies. Lyra found root cause. Jared needs to sync fresh.
- /insiders/awakened/ legacy template: 5 failures. Needs rebuild from current template.
- Form conversion tracking broken: 91 starts, 0 submits. GTM fix urgent.
- PayPal sandbox credentials expired: need refresh at developer.paypal.com

## PENDING
- 777 logo selection (7 options in Drive for Jared review)
- Lyra CF token scope issue (token active but no resources attached — needs Shahbaz)
- Lyra email system unblock (Brevo templates built but not deployed)
- Delta pending 3D skill deliverables (1,138-line synthesis + HTML files)
- Sage/Faris GCC compliance assessment (needs review)
- ACG voice cloning for Anchor (British male voice from ACG blog)
- Strategic plan reconciliation with Chy (product/tech perspective sent, awaiting her revenue/ops sections)
- Drive architecture implementation (Phase 2-4 not started)

## NEEDS JARED INPUT
- LinkedIn cookie sync (root cause = stale cookies per Lyra)
- PayPal sandbox credential refresh
- 777 logo selection from 7 options
- Approve /insiders/awakened/ rebuild
