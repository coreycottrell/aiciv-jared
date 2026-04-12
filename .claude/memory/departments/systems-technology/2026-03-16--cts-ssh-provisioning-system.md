# CTS SSH Keypair Provisioning System

**Date**: 2026-03-16
**Type**: build-completion
**Department**: dept-systems-technology
**Team**: client-tech-support-team

---

## What Was Built

Full automated SSH keypair provisioning and remote support system for CTS team.

### Files Created

1. **`tools/cts_provision_keys.py`** — Ed25519 keypair provisioning
   - Commands: `provision`, `list`, `show`, `mark-active`, `revoke`
   - Naming convention: `{name}_portal` (e.g., `joe_portal`)
   - Private keys stored at: `exports/departments/client-tech-support/keys/` (gitignored)
   - Public keys stored at: `exports/departments/client-tech-support/pubkeys/`
   - Auto-updates markdown registry on every operation
   - 90-day rotation schedule enforced in metadata
   - Audit log written to `logs/cts_actions.log`

2. **`tools/cts_remote_diag.py`** — Remote diagnostics via SSH
   - Lookup by customer name (auto-derives slug)
   - Checks: connectivity, portal service, tmux/Claude session, disk %, memory %, recent errors
   - Tries multiple portal detection methods (pgrep, ss port 8097, systemctl)
   - Outputs formatted diagnostic report
   - Optionally saves report to file (`--output`)

3. **`tools/cts_restart_portal.py`** — Remote portal restart
   - Rate limit: 1 restart per customer per 5 minutes (stored in `logs/cts_restart_state.json`)
   - `--force` flag to override rate limit
   - 4-strategy cascade: aether-restart.sh → systemd → docker → process-relaunch
   - 10-second wait then verifies portal came back up
   - All events logged to `logs/cts_actions.log`

4. **`portal_server.py` additions** (in `exports/app-purebrain-ai-full-repo/portal-server/`):
   - `GET /api/cts/customers` — lists all customers (safe fields only, no private key paths)
   - `POST /api/cts/diagnose/{customer}` — runs remote diagnostics, returns JSON report
   - `POST /api/cts/restart/{customer}` — remote restart with 429 rate limit response
   - All three endpoints require Bearer token auth

### Infrastructure

- `exports/departments/client-tech-support/keys/` — 700 permissions, gitignored
- `exports/departments/client-tech-support/keys/revoked/` — revoked keys preserved for audit
- `exports/departments/client-tech-support/pubkeys/` — shareable public keys
- `exports/departments/client-tech-support/keys/_registry.json` — machine-readable registry

### Registry Integration

Machine-readable: `keys/_registry.json`
Human-readable: `exports/departments/client-tech-support/ssh-key-registry.md` (auto-regenerated on every provision/revoke/mark-active)

### First Customer Provisioned

- Customer: joe
- Slug: joe_portal
- Server: 37.27.237.109:2219 (root)
- Status: pending-install (waiting for Joe to add public key to authorized_keys)
- Fingerprint: SHA256:I/AgTq0pLfPyZ44m0GU3bua7mKTlQ6YrlcPzXm8v/fM
- Public key at: `exports/departments/client-tech-support/pubkeys/joe_portal.pub`

---

## Key Design Decisions

- **No passphrase on keys** — CTS ops automation needs non-interactive SSH access
- **_registry.json as source of truth** — markdown regenerated from it, never the reverse
- **Portal server uses relative path resolution** — `SCRIPT_DIR.parent.parent.parent` = CIV_ROOT
- **All 4 restart strategies** in cascade because customer deployments may vary (systemd vs docker vs bare process)
- **Safe API fields only** — private key paths never exposed via portal API

---

## Next Steps for CTS Team

1. Send Joe's public key to him for authorized_keys installation
2. Run `python3 tools/cts_provision_keys.py mark-active --name joe` once confirmed
3. Test: `python3 tools/cts_remote_diag.py --customer joe`
4. Portal restart is not needed (per CTO directive) — just code added
