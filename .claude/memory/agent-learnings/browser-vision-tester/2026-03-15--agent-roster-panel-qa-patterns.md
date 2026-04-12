# Agent Roster Panel QA Patterns

**Date**: 2026-03-15
**Agent**: browser-vision-tester
**Type**: technique + gotcha

## Context

Full visual QA of the Agent Roster panel in the PureBrain portal at http://127.0.0.1:8097.

## Key Technical Discovery: Panel Navigation

**GOTCHA**: The Agent Roster panel is `id="panel-agents"` NOT `id="panel-agent-roster"`. The nav link text says "Agent Roster" but the DOM ID is `panel-agents`.

**Working navigation approach**:
```python
# Correct way to navigate to Agent Roster
await page.evaluate("""() => {
    const navItems = document.querySelectorAll('.nav-item');
    for (const item of navItems) {
        if (item.innerText.includes('Agent Roster')) {
            item.click();
            return;
        }
    }
}""")
```

**Then verify with**: `document.getElementById('panel-agents')` — NOT `panel-agent-roster`.

## Panel Architecture

```
#panel-agents
  .agents-header
    .agents-title → "✦ Agent Roster"
    .agents-stats
      .agents-stat-pill → "77 Total"
      .agents-stat-pill → "77 Idle"
    .agents-view-toggle
      button[data-view="grid"] → ▦
      button[data-view="list"] → ☰
      button[data-view="orgchart"] → ⬡
  .agents-filters
    #agents-search (input)
    #agents-filter-type (select) → "All Types, Core, Specialist, Pipeline, Orchestration, Governance"
    #agents-filter-status (select) → "All Status, Active, Idle, Working, Offline"
  .agents-grid (grid view)
    .agent-card × 77
      .agent-card-top
        .agent-status-dot.st-idle
        .agent-card-name
        .agent-type-badge.t-dept-manager | .t-specialist etc
      .agent-card-status-text → "idle · Last active: YYYY-MM-DD"
      .agent-card-desc
      .agent-card-caps (expanded only)
        .agent-cap-tag × N
      .agent-card-id-line (expanded only) → "ID: {id} · {dept}"
  #orgchart-container (org chart view)
    .orgchart-total-bar
      .orgchart-total-num → "77"
      .orgchart-total-label → "agents across 23 departments"
    .orgchart-legend
    .orgchart-dept × 23
      .orgchart-dept-header → clickable, expands dept
      .orgchart-dept-body (hidden until clicked)
        .orgchart-lead-card
          .orgchart-lead-dot
          .orgchart-lead-name
          .orgchart-lead-badge → "Lead"
        .orgchart-tree
          .orgchart-member × N
            .orgchart-member-dot
            .orgchart-member-name
            .orgchart-member-type → "specialist"
            .orgchart-member-id → "the-agent-id"
```

## View Toggle Buttons

Buttons are inside the panel header: `button[data-view="grid"|"list"|"orgchart"]`

NOT in the global header (which is Resume/Restart/Settings/Logout).

## Search Works Correctly

Search "content" → returns 9 agents. Stats pills update live to "9 Total / 9 Idle".
The search input has id `agents-search` and placeholder "Search agents...".

## Bug Found: Type Filter "Core" = 0 Results

`#agents-filter-type select_option(value="core")` → 0 agents found.
Likely cause: no agents tagged with exactly `type: "core"` in the agent data.
Other types (Specialist etc) may work — not tested in this session.

## Screenshot Capture Pattern

Since the portal SPA uses panel visibility switching, always screenshot the panel element directly:
```python
panel = page.locator("#panel-agents")
await panel.screenshot(path="/tmp/screenshot.png")
```

This avoids the issue where the full-page screenshot captures Chat (the default panel) even when Roster is active.

## Tags
portal, agent-roster, panel-navigation, panel-agents, orgchart, type-filter-bug
