# PureBrain SSH Remote Support System

**Version**: 1.0.0
**Date**: 2026-03-12
**Owner**: CTO / Systems Technology

---

## Overview

This document describes the two-part SSH remote support infrastructure for PureBrain:

1. **Customer SSH Keypair System** — unique ed25519 keys per portal customer, enabling ops-team support access
2. **Aether Self-Healing Restart** — one-liner Jared can run from anywhere to bring Aether back online

---

## Part 1: Customer SSH Keypair Provisioning

### Architecture Decision

Each PureBrain portal customer deployment gets its own unique ed25519 SSH keypair:
- **We hold the private key** in a local ops vault (never shared, never committed to git)
- **Customer machine holds the public key** in `~/.ssh/authorized_keys`
- Keys are **individually revocable** without affecting other customers
- Every action is **audit-logged** with timestamp, operator, and reason

### Why ed25519

- Shorter keys, stronger security than RSA-4096
- Faster signature verification
- Industry standard for new deployments (used by Witness fleet, civ-recovery skill)

### Key Naming Convention

```
purebrain-support-{customer-id}
```

Examples:
- `purebrain-support-cust_abc123`
- `purebrain-support-corey_v1`
- `purebrain-support-pilot_march2026`

### Ops Vault Location

```
/home/jared/projects/AI-CIV/aether/.ops-vault/ssh-keys/
```

- `.gitignore`-protected (automatically added on first run)
- `chmod 700` on the directory
- `chmod 600` on private keys and metadata
- Revoked keys moved to `.ops-vault/ssh-keys/revoked/` (not deleted — preserved for audit)

### Provisioning Flow

```
1. New customer signs up / deploys portal
2. Run: ./tools/ssh-keypair-provision.sh CUSTOMER_ID EMAIL
3. Script generates ed25519 keypair in vault
4. Script outputs public key
5. Bundle public key into customer's setup script OR
   manually append to customer's ~/.ssh/authorized_keys
6. Test: ssh -i .ops-vault/ssh-keys/purebrain-support-CUST_ID USER@HOST 'echo ok'
7. Audit entry auto-written
```

### Revocation Procedure

When a customer churns, a support engagement ends, or a key is compromised:

```bash
# Step 1: Revoke in vault
./tools/ssh-keypair-provision.sh revoke CUSTOMER_ID "customer churned"

# Step 2: Remove public key from customer's machine (output shown by revoke command)
ssh USER@CUSTOMER_HOST \
  'grep -v "purebrain-support-CUST_ID" ~/.ssh/authorized_keys > /tmp/ak && mv /tmp/ak ~/.ssh/authorized_keys'

# Step 3: Confirm removal
ssh -i .ops-vault/ssh-keys/revoked/KEY_FILE USER@CUSTOMER_HOST 'echo test' 2>&1
# Should return: Permission denied (publickey)
```

### Audit Log

Every provision, revoke, and list action is appended to:

```
/home/jared/projects/AI-CIV/aether/.ops-vault/audit.log
```

Format: `timestamp | operator | action | customer_id | detail`

View: `./tools/ssh-keypair-provision.sh audit`

---

## Part 2: Aether Self-Healing Restart

### The One-Liner

From Jared's laptop, phone (via Termius), or any machine with SSH access to the server:

```bash
ssh jared@89.167.19.20 'bash /home/jared/projects/AI-CIV/aether/tools/aether-restart.sh'
```

That's it. One command. No arguments needed.

### What It Does (in order)

1. Kills any existing Claude processes
2. Cleans stale tmux sessions (preserves one for forensics)
3. Creates a new tmux session named `aether-recovery-YYYYMMDD-HHMM`
4. Launches `claude --dangerously-skip-permissions`
5. Writes new session name to `.current_session` (Telegram bridge reads this)
6. Waits 10 seconds for Claude to initialize
7. Sends wake-up prompt — Aether runs full CLAUDE.md protocol
8. Restarts Telegram bridge if it died
9. Sends Telegram notification to Jared confirming restart

### SSH Config for Easy Access (Jared's laptop)

Add to `~/.ssh/config`:

```
Host aether
    HostName 89.167.19.20
    User jared
    IdentityFile ~/.ssh/id_ed25519
    ConnectTimeout 10
```

Then the one-liner becomes:

```bash
ssh aether 'bash /home/jared/projects/AI-CIV/aether/tools/aether-restart.sh'
```

### Phone Access (Termius)

In Termius (iOS/Android):
1. Create a host: `89.167.19.20`, user `jared`, port 22
2. Add your SSH key
3. Create a "Snippet" with the one-liner above
4. Tap the snippet → Aether restarts

### Safety Properties

- **Idempotent**: Safe to run even when Aether is mid-session
- **No data loss**: Memory, vault, and logs are untouched
- **Auto-bridge-restart**: Telegram bridge comes back up automatically
- **Immediate confirmation**: Telegram message arrives within ~30 seconds
- **Session traceability**: Recovery sessions are named with timestamps

### Relationship to civ_recovery.sh

`aether-restart.sh` is Aether-specific and opinionated (hardcoded paths, direct Telegram notification).

`civ_recovery.sh` is the general fleet recovery tool that works on any CIV. For fleet use, use `civ_recovery.sh`. For Jared's daily use, `aether-restart.sh` is simpler.

---

## Quick Reference

| Task | Command |
|------|---------|
| Provision new customer key | `./tools/ssh-keypair-provision.sh CUST_ID EMAIL` |
| Revoke customer key | `./tools/ssh-keypair-provision.sh revoke CUST_ID` |
| List all keys | `./tools/ssh-keypair-provision.sh list` |
| View audit log | `./tools/ssh-keypair-provision.sh audit` |
| Get SSH config for customer | `./tools/ssh-keypair-provision.sh connect-info CUST_ID HOST` |
| Restart Aether (from server) | `bash /home/jared/projects/AI-CIV/aether/tools/aether-restart.sh` |
| Restart Aether (from laptop) | `ssh aether 'bash ~/projects/AI-CIV/aether/tools/aether-restart.sh'` |
| Full recovery with diagnosis | `./tools/civ_recovery.sh jared@89.167.19.20 --diagnose` |

---

## Files Created

| File | Purpose |
|------|---------|
| `tools/ssh-keypair-provision.sh` | Customer keypair generation, revocation, audit |
| `tools/aether-restart.sh` | Aether self-healing restart (one-liner target) |
| `docs/ssh-support-system.md` | This document |
| `.ops-vault/` | Private key vault (gitignored, auto-created) |
| `.ops-vault/audit.log` | Immutable audit trail |
