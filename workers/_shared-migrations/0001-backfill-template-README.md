# Backfill SQL — generated locally, NEVER committed

The actual `INSERT OR IGNORE` backfill files are NOT in this repo because they
contain real user records (password_hash, emails, PII).

## How they were generated (2026-05-14 Day 1 EXTEND)

1. Source dump:
   ```bash
   npx wrangler d1 execute purebrain-social --remote --json --command \
     "SELECT id, team_id, email, name, role, billing_tier, password_hash, \
      oauth_provider_id, last_login_at, created_at, display_name FROM users;" \
     > /tmp/auth-day1-v3/source-users-full.json
   ```

2. Python builder emits one `INSERT OR IGNORE INTO <table> (...) VALUES (...)`
   per row, SQL-escaping single quotes. Output to:
   - `/tmp/auth-day1-v3/backfill-clients-users.sql` (Track 1)
   - `/tmp/auth-day1-v3/backfill-clients-team_invites.sql` (Track 1)
   - `/tmp/auth-day1-v3/backfill-refs-auth_users.sql` (Track 2)
   - `/tmp/auth-day1-v3/backfill-refs-auth_team_invites.sql` (Track 2)

3. Idempotent — re-running produces zero `rows_written` (verified G4).

## Storage

Local-only copies live at:
- `/home/jared/projects/AI-CIV/aether/.gitignore-data/auth-day1-v3/` (this repo, gitignored)
- `/tmp/auth-day1-v3/` (ephemeral)

If a future agent needs to re-run, they should regenerate from a live source
dump rather than restoring stale data.

## Backups (also gitignored)

- `/home/jared/projects/clients-api/backups/2026-05-14/purebrain-clients-pre-extend.sql`
  (sha256: 327d1580598107835086f4b5ba309cf26d1932b134eefc089ff08bff8539d94f)
- `/tmp/referrals-api/backups/2026-05-14/purebrain-referrals-pre-create.sql`
  (sha256: eef9467e4f053514749ded6103baa5652de8b4d087a7323bafb72c47aa52c1a1)
