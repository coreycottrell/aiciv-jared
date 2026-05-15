# disk-telemetry-ingest

Authenticated ingestion endpoint for fleet disk telemetry. Validates
HMAC-SHA256(body|nonce|ts) keyed by `INGEST_TOKEN`, rejects requests
outside a 30s timestamp window or with replayed nonce, stamps
`cf-connecting-ip` into D1.

## Endpoints

- `POST /ingest` — daemon writes one telemetry row
- `GET /health` — Worker self-health (no auth)
- `GET /civs/<civ_name>/recent?hours=N` — admin forensics read (Bearer `ADMIN_TOKEN`)

## Setup

```bash
# One-time D1 create (Aether)
wrangler d1 create disk-telemetry
# substitute returned database_id into wrangler.toml placeholder

# Apply schema
wrangler d1 execute disk-telemetry \
  --file=../_shared-migrations/0010-disk-telemetry-schema-2026-05-15.sql

# Secrets
wrangler secret put INGEST_TOKEN     # 64+ random bytes hex
wrangler secret put ADMIN_TOKEN      # forensics read auth

# Deploy (only after git commit per canonical deploy flow)
wrangler deploy
```

## Token rotation (CTO amendment #3)

Monthly cadence. During rotation window:

```bash
wrangler secret put INGEST_TOKEN_PREVIOUS   # set to old token
wrangler secret put INGEST_TOKEN            # set to new token
# daemons roll forward; after 7 days:
wrangler secret delete INGEST_TOKEN_PREVIOUS
```

Daemons fail-open to last-known-good for 5 min if new token rejected.

## Spec

`specs/disk-safety-telemetry-2026-05-15.md`
