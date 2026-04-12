# Team Task Dashboard - Netlify Deployment

**Date**: 2026-02-23
**Type**: operational
**Topic**: Pure Technology team task dashboard built and deployed to Netlify

## What Was Built

Self-contained HTML/JS/CSS dashboard at:
- Local: `/home/jared/projects/AI-CIV/aether/exports/team-dashboard/dist/index.html`
- Netlify: https://pt-team-dashboard.netlify.app
- Netlify Site ID: 81a04eb5-a7c1-46a7-90de-b4aaa76a8083

## Previous WordPress Deployment (still live)

- URL: https://purebrain.ai/team-dashboard/
- Page ID: 843
- Password: puretechteam

## Features Implemented (v2 - Netlify)

1. **Login**: Select name + password (no email needed)
2. **Passwords**: `puretech2026` for admin (Jared/Aether), `pureteam{firstname}` for team
3. **Admin view**: Full table of all tasks, Create Task button, Edit + Delete per task
4. **Admin toggle**: Switch between table view and card view
5. **My Tasks view**: Card grid filtered to current user, section headers by priority/status
6. **Task modal**: Create and edit tasks with full fields
7. **Status cycling**: Pending → In Progress → Complete → Pending (one click)
8. **Filters**: All / Pending / In Progress / Complete / High Priority + search
9. **Stats row**: Total / In Progress / Pending / Completed / High Priority
10. **A/B/C delegation legend** always visible
11. **LocalStorage backend**: Tasks persist across browser sessions, no external API
12. **Seed tasks**: 8 realistic demo tasks pre-loaded on first visit
13. **Assigned by field**: Shows who created each task

## File Structure

```
exports/team-dashboard/
├── netlify.toml          (build config, cache headers)
└── dist/
    ├── index.html        (full app - 2333 lines, 76KB)
    └── _redirects        (SPA routing)
```

## Team Roster

49 members from dossier v2. Password scheme:
- Jared Sanborn + Aether: `puretech2026`
- All others: `pureteam{firstname_lowercase}`
  - e.g. Nathan Olson: `pureteamnathan`
  - e.g. Shahbaz Ali: `pureteamshahbaz`

## Deployment Pattern

```bash
# Create site via API
curl -X POST "https://api.netlify.com/api/v1/sites" \
  -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
  -d '{"name":"pt-team-dashboard"}'

# Deploy
cd exports/team-dashboard && \
  npx netlify-cli deploy --prod --dir=./dist \
  --auth=$NETLIFY_AUTH_TOKEN --site=81a04eb5-a7c1-46a7-90de-b4aaa76a8083
```

## Lessons Learned

1. `netlify deploy --create-site` is the preferred one-shot command for new sites
2. Site must be created before `--prod` deploy via CLI (or use API)
3. `--site-name` is not a valid CLI flag - must use `--site={id}`
4. localStorage is ideal for MVP team tools - no backend cost, works offline
5. Password auth in client-side JS is fine for internal tools (no PII, just task data)
