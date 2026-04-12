# Portal Org Chart Tree View Implementation
**Date**: 2026-03-16
**Type**: pattern + technique
**Topic**: Replacing collapsible list orgchart with visual tree hierarchy in portal

## What Was Done
Replaced the existing collapsible list "org chart" in the Agent Roster panel with a real visual org chart tree view.

## Key Files Modified
- `/home/jared/purebrain_portal/portal-pb-styled.html` — CSS + JS

## Architecture of the New Tree

### Visual Hierarchy
1. **Level 1**: Aether (Primary) — centered at top, gradient blue-orange styling
2. **Level 2**: CTO + CMO as direct reports — connected by horizontal line
3. **Level 3**: Tech teams under CTO (3 groups in dashed boxes), Marketing depts under CMO
4. **Level 4**: All other departments in a wrap grid at the bottom
5. **Expandable**: Click any dept manager node to show/hide individual agents beneath it

### Data Mapping
- Primary = The Conductor agent in Pure Technology dept
- CTO = 'cto' agent id in Systems & Technology dept
- CMO = lead of Marketing & Advertising (or 'cmo' id)
- Tech teams: Systems & Technology, Product Development, Pure Infrastructure
- Marketing: Marketing & Advertising, Pure Marketing Group
- All others: shown in the "All Departments" row

### CSS Classes Added (`oct-*` prefix)
- `.oct-tree` — outer flex container
- `.oct-row` — horizontal row of nodes
- `.oct-col` — vertical column (node + children)
- `.oct-node.tier-primary/l2/dept/agent` — node cards per tier
- `.oct-avatar` — circular avatar with status dot
- `.oct-stem-down`, `.oct-drop` — vertical connectors
- `.oct-tech-team-group` — dashed box grouping for tech teams
- `.oct-dept-agents` — collapsible agent list under dept node

### JS Functions
- `renderOrgChart(data)` — fully replaced, builds visual tree from API data
- `window.octToggleDept(expandId, nodeEl)` — toggles agent lists open/closed
- `makeNode(name, role, status, tier, opts)` — renders a single node card
- `makeAgentList(members, expandId)` — renders collapsible agent list

### API Data Shape
`/api/agents/orgchart` returns:
```json
{
  "departments": [
    {
      "name": "Systems & Technology",
      "count": 15,
      "lead": { "id": "dept-systems-technology", "name": "...", "status": "idle", ... },
      "members": [{ "id": "cto", "name": "CTO", ... }, ...]
    }
  ],
  "total": 72
}
```

## Patterns / Gotchas
- `_DEPT_ICONS` and `_DEPT_COLORS` were using generic keys ('Marketing', 'Sales'). Extended them with full dept name keys for proper color mapping.
- CTO agent is in `members[]` of Systems & Technology (not the lead). Filter it out when rendering tech team members list.
- The `hexToRgb()` helper is needed to use hex colors in rgba() for dynamic accent backgrounds.
- Script tag count mismatch (9 open vs 8 close) is PRE-EXISTING in the portal file, not caused by this change.
- The org chart button (&#x2B21; hexagon) and view toggle already existed — only the CSS/JS needed replacing.

## Design Decisions
- Used CSS-only connectors (vertical `div` stems + horizontal absolute `div` lines) — no SVG/Canvas needed
- Expandable dept nodes instead of showing all agents by default — keeps the chart readable at initial load
- Tech teams shown in dashed group boxes to visually distinguish them as "product teams" under CTO
