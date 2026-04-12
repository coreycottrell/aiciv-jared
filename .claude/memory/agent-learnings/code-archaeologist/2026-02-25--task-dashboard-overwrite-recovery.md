# Task Assignment Portal Recovery Investigation

**Date**: 2026-02-25
**Type**: operational
**Topic**: Pure Technology Task Assignment Portal overwritten by PureBrain Hub login redesign on Netlify

## What Happened

The Task Assignment Portal at https://pure-tech-dashboard.netlify.app was overwritten on 2026-02-25T11:01:37 when the PureBrain Hub login redesign (a Vite/React app) was deployed to the same Netlify site ID (`d2556d0a-5333-47ca-a8d6-8add4141f090`). The login redesign produced only a 678-byte index.html shell + JS/CSS assets, replacing the 202KB self-contained task dashboard.

## Recovery Status

**GOOD NEWS: Full recovery is possible.** Multiple copies of the original dashboard exist.

### Recovery Option 1: Netlify Rollback (fastest, no code changes)
- Rollback deploy ID: `699cf14b19933903f0d7b321` (2026-02-24T00:31:07)
- This was the last confirmed task dashboard deploy (202,544 bytes)
- Command: `curl -X POST "https://api.netlify.com/api/v1/sites/d2556d0a-5333-47ca-a8d6-8add4141f090/deploys/699cf14b19933903f0d7b321/restore" -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN"`
- The rollback API returned 200 OK when tested

### Recovery Option 2: Local file redeploy
- File: `/home/jared/projects/AI-CIV/aether/exports/team-dashboard.html`
- Size: 62,012 bytes / 1,863 lines
- This is slightly OLDER than the Feb 24 deployed version (Airtable backend vs Supabase backend)
- The Feb 24 deployed version (202KB) had Supabase sync added

## Version Archaeology

| Date | Version | Backend | Size | Location |
|------|---------|---------|------|----------|
| Feb 23 23:10 | v1 localStorage | Airtable | 62KB | `exports/team-dashboard.html` |
| Feb 24 00:17 | v2 Supabase | Supabase sync | ~202KB | Netlify deploy 699cee2f |
| Feb 24 00:23 | v2.1 fix | Supabase | ~202KB | Netlify deploy 699cef71 |
| Feb 24 00:31 | v2.2 final | Supabase + brain icon | ~202KB | Netlify deploy 699cf14b |
| Feb 24 21:12 | ??? | Unknown | ??? | Netlify deploy 699e143 |
| Feb 25 11:00 | OVERWRITE | PureBrain Hub React | 678 bytes | Current live |

## Original Dashboard Contents

### Authentication
- Select name from dropdown + password
- Admin (Jared/Aether): `puretech2026`
- Team members: `pureteam{firstname}` (e.g., `pureteamnathan`, `pureteamshahbaz`)

### Team Roster (49 members across departments)
C-Suite: Jared Sanborn, Melanie Salvador, Nils Waschkau, James Weinberg, Mike Daser, Eric Solomon, Michael Schuman, Charles Finkelstein, Timothy DeVore, Rimah Harb, Zenia Tata, Michael Hancock
Operations: Edward Brennan, Roger Beaini, Chris Ishii, Mireille Dirany, Linda Chaaya, Micheline Akel
Finance: Paula Bou Chaaya, Cora Salvador
Commercial: Alexander Logie, Marcie McGovern, John Smith, Jessie Cruz, Mohamad El Madhoun
Marketing: Phillip Bliss, Robert Orlowski, John Paris, Nathan Olson, Natasha Carrasco, Baruch Santana, Moises Guerra
(+ more in Product, Engineering, Strategy, etc.)

### Features
- Admin view: full task table + create/edit/delete
- My Tasks view: filtered card grid per user
- Status cycling: Pending → In Progress → Complete
- Filters: All/Pending/In Progress/Complete/High Priority + search
- Stats row: Total/In Progress/Pending/Completed/High Priority
- A/B/C delegation legend
- Supabase sync (30s polling when connected)
- localStorage fallback when offline
- Seed/demo tasks on first load

### Airtable Config (v1 local file)
- API Key: `patcjYGyBxRGQfjdj.c7363c42481a5a9f13c400842e930fe22be3f75bdafbce3ee580a2ec2c2cd7e4`
- Base ID: `app3PhIudYCZ8VCCF`
- Table: `Tasks`

## Related Files
- `exports/team-dashboard.html` — v1 Airtable version, local backup
- `docs/team-dossiers/` — full dossier per team member (100 directories)
- `exports/pure-tech-team-dossier-v2.md` — full team dossier source
- `docs/from-telegram/pure-tech-team-dossier-v2.md` — Telegram copy
- `exports/departments/operations-planning/plans/2026-02-25--task-assignments.md` — task register

## Key Lesson

When deploying a NEW app to Netlify, always create a NEW SITE rather than reusing an existing site ID. The `exports/team-dashboard/` directory shared its Netlify site ID with the PureBrain Hub project, causing the overwrite.

The correct architecture:
- `pure-tech-dashboard.netlify.app` → Task Assignment Portal (site d2556d0a)
- `purebrain-hub.netlify.app` → PureBrain Hub login redesign (new site)
