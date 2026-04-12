# Team View: Task Assignment Dashboard

**Date**: 2026-02-25
**File**: `exports/team-dashboard-v3.html`
**Deployed**: https://pure-tech-dashboard.netlify.app
**Deploy ID**: 699ee525c6901d3024133586

## What Was Built
Added a full "Team" view/tab to the existing Task Assignment Dashboard.

## Architecture
- View toggle: Tasks tab | Team tab (in topnav, as `.view-tabs` with `.view-tab` buttons)
- `#tasks-view` div wraps original main-container (hides via `.hidden` class)
- `#team-view` div is sibling inside `#app` (shows via `.visible` class)
- Both controlled by `switchView('tasks'|'team')` function

## Left Panel: Roster
- 49 members rendered from `TEAM_DATA` array (separate from login `TEAM_ROSTER`)
- Grouped by dept: Leadership, Strategy, Operations, Finance, Commercial, Marketing, Product, Technology, AI
- Dept filter buttons (9 categories + All)
- Search by name/role/dept
- Click → highlights row + shows profile on right

## Right Panel: Profile
- Glass card matching login card style
- Avatar (initials), name, role (dept color), meta (reportsTo, location)
- Key Strengths: pills from dossier
- A/B/C Routing: 3-column color-coded cards (blue=A/Aether, orange=B/Jared, green=C/them)
- Tasks: filtered from allTasks array by name matching

## Key Functions
- `switchView(view)` — toggles between tasks/team views
- `renderRoster()` — builds roster list with search + dept filter
- `selectRosterMember(name)` — renders full profile
- `getMemberTasks(name)` — filters allTasks for this person
- `buildProfileTasks(tasks, name)` — renders task rows on profile

## Pattern: Self-contained HTML Surgical Edit
Used bash split + reassemble pattern (5 parts) to inject new CSS, HTML, and JS into a large existing self-contained HTML file without corrupting it. Safer than in-place edit on 107KB file.

## File Size
- Before: 107,606 bytes (3,126 lines)  
- After: 163,724 bytes (4,650 lines)

## Memory Written
Path: `.claude/memory/departments/systems-technology/2026-02-25--team-view-dashboard-build.md`
