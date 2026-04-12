# Referral System & Client Admin Fix

**Date**: 2026-03-19
**Type**: operational
**Topic**: Portal referral tracking bugs, client admin registration, admin features

## Root Causes Discovered

### Client Admin Missing Signups
- Client admin is populated by scanning JSONL log files at ~/projects/AI-CIV/aether/logs/
- Import triggered by POST /api/admin/clients/import — was MANUAL ONLY before this fix
- New signups appear in logs immediately but not in admin until import runs
- Fix: added _auto_import_clients_loop() to portal startup — runs every 5 minutes

### Referral Click Tracking — Two Bugs
1. No API call: Landing page JS stored code in localStorage/cookie but NEVER called /api/referral/track
2. Regex blocked PB-format codes: ^[A-Za-z0-9]{6,12}$ — hyphens blocked. PB-K22P has hyphen.
   Fix: ^[A-Za-z0-9-]{4,16}$

### CORS Missing Methods
- Middleware only allowed GET/POST/OPTIONS
- Admin affiliate update uses PUT, delete uses DELETE
- Fix: add PUT, DELETE, PATCH to allow_methods

## Portal Server Architecture
- Port: 8097
- Token file: /home/jared/purebrain_portal/.portal-token
- DBs: clients.db, referrals.db, agents.db (SQLite in /home/jared/purebrain_portal/)
- Restart: cd /home/jared/purebrain_portal && bash restart.sh

## New Endpoints Added
- POST /api/admin/referral/assign — retroactively credit client to referrer
  Body: { referral_code, client_email, client_name? }

## Trigger Import Manually
TOKEN=$(cat /home/jared/purebrain_portal/.portal-token)
curl -s -X POST http://localhost:8097/api/admin/clients/import -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"
