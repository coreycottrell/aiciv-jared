# Portal: Agent Roster, Commands & Shortcuts Feature

**Date**: 2026-03-15
**Type**: feature-build
**Status**: complete

## What Was Built

Added three new sidebar panels to the PureBrain portal:
1. **Agent Roster** (`data-panel="agents"`) — searchable, filterable grid/list/org-chart of AI agents
2. **Commands** (`data-panel="commands"`) — dynamic server command reference per deployment
3. **Shortcuts** (`data-panel="shortcuts"`) — slash commands, keyboard shortcuts, chat features reference

## Files Modified

- `/home/jared/purebrain_portal/portal_server.py` — Added ~300 lines of API code
- `/home/jared/purebrain_portal/portal-pb-styled.html` — Added CSS, panel HTML, nav items, JS IIFE

## Database

- New SQLite DB: `/home/jared/purebrain_portal/agents.db`
- Table: `agents` (id, user_id, name, description, type, status, capabilities JSON, department, is_lead, last_active, created_at)
- Seeded on first run with 77 agents from `.claude/agents/` manifests via YAML frontmatter parsing
- Constant `AGENTS_DB` added to server; `_init_agents_db()` called in `_startup()`

## API Endpoints

| Route | Function | Notes |
|-------|----------|-------|
| GET /api/agents | api_agents_list | Supports ?type=, ?status=, ?search= |
| GET /api/agents/stats | api_agents_stats | Count by status + dept count |
| GET /api/agents/orgchart | api_agents_orgchart | Grouped by 12 departments |
| GET /api/commands | api_commands | Dynamic — detects hostname, paths, tmux session |
| GET /api/shortcuts | api_shortcuts | Static reference data (slash cmds, keys, features) |

## Seed Data (Jared's CIV — 77 agents)

Seeded across 11 departments:
- AI & Strategy: 4 (lead: cto)
- Development: 14 (no dedicated lead — dept-systems-technology in Operations)
- Meta & Governance: 11 (lead: the-conductor)
- Communications: 12 (lead: human-liaison)
- Marketing: 6 (lead: marketing-automation-specialist)
- Sales: 2 (lead: sales-specialist)
- Research: 5
- Operations: 13 (lead: dept-pure-technology)
- Infrastructure: 4
- Design & UX: 3
- Legal: 3

## Commands Panel — Dynamic Behavior

The `/api/commands` endpoint dynamically detects:
- Hostname from `socket.gethostname()`
- SSH user from `Path.home().name`
- Server IP from `~/.aiciv-identity.json` (if present)
- tmux primary session from `get_tmux_session()`
- Portal URL from `~/.portal-cname` file (if present)
- All path values computed from actual `Path.home()` + project structure

Commands in the panel are constructed from these dynamic values, so each customer's deployment shows their own server info, not hardcoded values.

## Patterns Learned

- Portal panels need three things: CSS + panel HTML div + switchPanel hook + JS IIFE
- `switchPanel` hook pattern: `if (panel === 'agents') { if (window.loadAgents) window.loadAgents(); }`
- Lazy-load pattern: only fetch data when panel first opened (commandsLoaded / shortcutsLoaded flags)
- YAML frontmatter parsing for agent descriptions: `yaml.safe_load(raw[3:raw.find('---',3)])`
- Auth headers: check both `pb_token` and `portal_token` in localStorage
- Mobile hamburger: add `selectMobileMenuItem('panel-name')` items to `#mobile-more-menu` div

## Backups Created

- `portal_server.py.bak-agents-commands-shortcuts-20260315`
- `portal-pb-styled.html.bak-agents-commands-shortcuts-20260315`
