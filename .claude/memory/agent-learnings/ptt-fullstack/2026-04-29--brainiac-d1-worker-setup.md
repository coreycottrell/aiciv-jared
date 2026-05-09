# Brainiac Platform D1 + Worker Setup

**Date**: 2026-04-29
**Type**: operational
**Topic**: Brainiac training platform infrastructure setup

## What Was Done

1. **Git Repo**: `puretechnyc/brainiac-purebrain` on GitHub (private)
   - main + staging branches
   - Push via HTTPS with GH_TOKEN (SSH key is for coreycottrell org only)

2. **D1 Database**: `brainiac-platform` (ID: 57665337-3726-4a9c-a0a5-6f8be2d97fc7)
   - 4 tables: modules, users, sessions, progress
   - 8 training modules seeded
   - Region: EEUR

3. **CF Worker**: `brainiac-api` deployed at `brainiac-api.in0v8.workers.dev`
   - Endpoints: /api/modules, /api/modules/:id, /api/login, /api/progress, /api/health
   - CORS set to brainiac.purebrain.ai

4. **DNS Route**: `brainiac.purebrain.ai/api/*` -> brainiac-api worker

## Key Learnings

- CF API token `[REDACTED-2026-05-09-LEAK-CFUT]` lacks D1 permissions
- Must use Global API Key + Email + Account ID for D1 operations
- Account ID: d526a3e9498dd167509003004df03290
- Wildcard route `*.purebrain.ai/*` exists (portal-proxy) — more specific routes take priority
- `/health` without wildcard gets caught by portal proxy; use `/api/health` instead

## File Paths
- Worker code: `/home/jared/projects/brainiac-purebrain/workers/brainiac-api/src/worker.js`
- Migrations: `/home/jared/projects/brainiac-purebrain/workers/brainiac-api/migrations/`
- Wrangler config: `/home/jared/projects/brainiac-purebrain/workers/brainiac-api/wrangler.toml`
