# 777 Command Center v2 Build

**Date**: 2026-04-10
**Type**: operational
**Agent**: dept-systems-technology

## What Was Built

Complete 777 Command Center v2 - Jared's personal operating system dashboard.

- **File**: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html`
- **Size**: 3,045 lines, 110KB single HTML file
- **Live at**: `https://purebrain.ai/777-command-center/`
- **Deployed via**: `cf-deploy.py` to purebrain-staging CF Pages

## Architecture

Single HTML file with three tabbed layers:
1. **Personal OS** (Layer 1): Daily Pulse, 7 F's Compass, Goal Mountain, Money Map, Relationship Ring, Legacy Lens, Mandala Matrix, Thinking Exercises
2. **Triangle OS** (Layer 2): Morning Pulse, Handshake Queue, Ship Board, Company Health, Revenue Dashboard, Investor Pipeline, Financial Health, Sales Pipeline, Content Calendar, BOOP Health
3. **Team HQ** (Layer 3): Team Directory, Meeting Schedule, Email Activity, Weekly Review, Customer Board, Ops Metrics, Governance Calendar

## Key Technical Decisions

- Password gate preserved from v1 (777grind)
- Tab navigation with URL hash deep-linking (#personal, #triangle, #team)
- Default tab: #triangle (most used by Jared)
- Chart.js 4.4.0 for radar charts, bar charts
- Promise.allSettled for parallel API fetching
- Graceful degradation with demo data when APIs unavailable
- 5-minute auto-refresh for live data
- Stale data banner after 10 minutes
- AI Coach slide-in panel (right side)
- Thinking Exercises with localStorage persistence
- Toast notifications for user feedback

## Data Sources

- Google Sheets API (3 spreadsheets: personal, TOS, team whitelist)
- Portal API (localhost:8097): BOOP health, activity, customers, email, chat
- BaaS API (surf.purebrain.ai): content calendar, social stats
- Investor Sheet (1j5nT0f3wVbf): revenue, investor pipeline

## What Still Needs Configuration

- Google Sheets API key (CONFIG.sheetsApiKey)
- Portal token (CONFIG.portalToken)
- CORS on portal_server.py for 777.purebrain.ai origin
- GA4 integration (Phase 3)
- Portal nav link (portal-pb-styled.html)

## Spec Reference

Full spec at: `/home/jared/exports/portal-files/777-v2-technical-spec.md`
