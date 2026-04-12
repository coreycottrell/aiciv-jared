# Team Dashboard — Supabase Shared Backend Integration

**Date**: 2026-02-24
**Type**: teaching
**Topic**: Adding a shared Supabase backend to a pure localStorage frontend

## What Was Built

Added Supabase sync to the Pure Technology team task dashboard so tasks sync across all devices in near-realtime. Previous: localStorage only (per-device). Now: Supabase PostgreSQL as primary, localStorage as offline cache.

## Architecture Pattern

**No npm, no build step** — everything is a lightweight REST wrapper in vanilla JS. This is the right pattern for self-contained HTML dashboards deployed to Netlify.

```js
const sb = {
  _url, _key, _headers,
  init(url, key) { ... },
  ready() { return !!this._url; },
  async getAll() { ... },       // GET /rest/v1/tasks?select=*
  async upsert(task) { ... },   // POST with Prefer: resolution=merge-duplicates
  async upsertMany(tasks) { ... },
  async delete(id) { ... }      // DELETE /rest/v1/tasks?id=eq.{id}
}
```

## Supabase REST API Key Patterns

- All requests need `apikey` + `Authorization: Bearer {key}` headers
- Upsert = POST with `Prefer: resolution=merge-duplicates,return=representation`
- Delete by PK = `DELETE /rest/v1/tablename?pk_col=eq.{value}`
- Task IDs are text (not UUID) so use `text primary key` not `uuid`

## SQL Schema

```sql
create table tasks (
  id text primary key,
  title text not null,
  description text,
  "assignedTo" text,   -- camelCase must be quoted
  delegation text,
  priority text,
  status text,
  deadline text,
  files text,
  "createdAt" text,
  "createdBy" text
);
alter table tasks enable row level security;
create policy "public read" on tasks for select using (true);
create policy "public write" on tasks for all using (true);
```

**Important**: camelCase JS properties like `assignedTo`, `createdAt`, `createdBy` must use quoted column names in PostgreSQL SQL.

## UI Pattern: Self-Configuring Backend

Instead of hardcoding credentials, we:
1. Added a "Sync Setup" button (admin-only in nav)
2. Setup modal shows step-by-step instructions + SQL + form for URL/key
3. On connect: test by calling `getAll()`, then save config to localStorage
4. On every page load: check for saved config, init Supabase if found

This allows deploy-once, configure-later — Jared can add Supabase credentials without needing a code deploy.

## Sync Strategy

- **Load**: Try Supabase first → fall back to localStorage
- **Save**: Always write localStorage immediately (fast), then push to Supabase async
- **Delete**: Call `sb.delete()` + update localStorage
- **Poll**: Every 30s when connected, fetch remote and re-render
- **Status indicator**: Sync dot in nav shows offline/syncing/synced/error

## Async CRUD Updates Required

When upgrading localStorage-only CRUD to include remote sync:
- `loadTasksFromStorage()` → `async function` (awaited on init)
- `saveTasksToStorage(task)` → accepts optional task param for single upsert
- `deleteTask()` → `async function deleteTask()` to call `await sb.delete()`
- All CRUD must pass the changed task reference: `saveTasksToStorage(task)` / `saveTasksToStorage(savedTask)`

## Deployment

- Site ID: `d2556d0a-5333-47ca-a8d6-8add4141f090`
- URL: https://pure-tech-dashboard.netlify.app
- File: `/home/jared/projects/AI-CIV/aether/exports/team-dashboard/dist/index.html`
- Deploy: `npx netlify-cli deploy --prod --dir=./dist --auth=$NETLIFY_AUTH_TOKEN --site=d2556d0a-5333-47ca-a8d6-8add4141f090`

## What Jared Needs To Do

1. Go to supabase.com → New Project (free tier)
2. SQL Editor → run the create table script above
3. Settings → API → copy Project URL + anon key
4. Go to https://pure-tech-dashboard.netlify.app → login as admin → click "Sync Setup"
5. Paste URL and key → click Connect
6. Done — all devices now sync

## Lessons Learned

1. Supabase free tier is perfect for internal tools: generous limits, no credit card
2. Self-contained HTML dashboards should use Supabase REST API directly (no JS client library needed)
3. RLS policies must explicitly allow operations — `using (true)` for internal tools is fine
4. Always mirror remote data to localStorage immediately — provides offline resilience
5. Seed data handling: if remote is empty on first connect, push local tasks up
6. The "Sync Setup" UX pattern (in-app config modal) is better than hardcoding credentials
