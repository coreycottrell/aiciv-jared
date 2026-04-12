# CTO Memory: SSH Remote Support System

**Date**: 2026-03-12
**Type**: teaching
**Topic**: Customer SSH keypair provisioning + Aether self-healing restart

## What Was Built

Two scripts and one doc to enable remote SSH support for PureBrain:

### 1. Customer Keypair Provisioning
- `tools/ssh-keypair-provision.sh` — generates unique ed25519 keypairs per customer
- Vault: `.ops-vault/ssh-keys/` (gitignored, chmod 700)
- Naming: `purebrain-support-{customer-id}`
- Individually revocable (revoked keys moved to `revoked/` subdir, not deleted)
- Full audit log at `.ops-vault/audit.log`

### 2. Aether Self-Healing Restart
- `tools/aether-restart.sh` — idempotent restart script
- One-liner: `ssh jared@89.167.19.20 'bash ~/projects/AI-CIV/aether/tools/aether-restart.sh'`
- Kills old process, creates fresh tmux session, sends wake-up prompt, restarts bridge
- Sends Telegram notification on completion

## Key Decisions

- **ed25519 over RSA** — shorter, stronger, faster; matches fleet standard
- **Vault on disk, not in a secret manager** — pragmatic for current scale; if customer base grows to 50+ active keys, move to HashiCorp Vault or AWS Secrets Manager
- **Revoked keys kept, not deleted** — audit requirement; forensics in case of incident investigation
- **aether-restart.sh is Aether-specific** — hardcoded paths, direct Telegram. civ_recovery.sh is the general fleet tool. Keep them separate.

## Reference Context Found

- `civ-recovery` skill at `.claude/skills/civ-recovery/SKILL.md` — general fleet recovery
- `local-claude-helper` skill at `.claude/skills/local-claude-helper/SKILL.md` — for coaching humans
- Witness already sent `from-witness/local-claude-helper/FOR-YOUR-HUMAN.md` — companion doc for customers
- Existing `tools/civ_recovery.sh` — general fleet recovery, handles diagnosis, reauth, disk, OOM
- Server: `jared@89.167.19.20` (Hetzner VPS, confirmed in civ-recovery skill)

## Future Scaling Considerations

- If customer base grows beyond 20 active customers, add a customer registry JSON to track host/IP/port per ID
- Consider a nightly cron to verify all provisioned keys still have active SSH connections
- OAuth reauth cannot be automated — must involve human opening a browser URL
