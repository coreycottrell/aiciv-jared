# Memory: welcome-email-api CF Worker Architecture

**Date**: 2026-04-23
**Type**: teaching
**Agent**: architect
**Task**: Design CF Worker to replace Python/Gmail SMTP welcome email flow

---

## Pattern: "Extract single-responsibility email endpoint from a fat monitor process"

When a Python monitor process handles both watching/parsing (stateful, long-running) AND outbound email (stateless, IO-bound), extract email sending into a dedicated CF Worker. The monitor retains what it must be — a stateful loop — and delegates the fire-and-forget email operation to CF's edge.

This pattern applies any time you see:
- SMTP credentials embedded in a long-running daemon
- Template files in /tmp (reboot-volatile)
- No delivery log for transactional email
- Placeholder mismatch bugs from evolving templates without a schema

## Key Decisions Made

1. **Shared D1, new tables** — Do not create a new D1 database. Add `email_templates` and `email_delivery_log` tables to the existing `purebrain-social` D1 (625dde70-0a60-45e7-bf81-e18e5ac4d854). This is the pattern every other worker uses.

2. **Brevo over Gmail SMTP** — Gmail SMTP is rate-limited (~500/day), requires GOOGLE_APP_PASSWORD, produces no structured delivery receipts, and ties us to a human's app password. Brevo transactional API is the correct replacement.

3. **No auth on /send-welcome** — The endpoint is internal (called by VPS or Witness only). CF WAF IP restriction is the protection layer if needed. Adding Bearer auth would require credential sharing with agentmail_monitor.py and Witness — unnecessary complexity for an internal endpoint.

4. **BCC jared@puretechnology.nyc on every send** — Replaces the Telegram notification in agentmail_monitor.py. Jared gets a copy of every welcome email, which is more useful than a Telegram ping.

5. **Sandbox bypass preserved** — The sb-*@* redirect to jared@puretechnology.nyc from agentmail_monitor.py must survive in the Worker. Do not lose this during migration.

6. **Placeholder standardization** — agentmail_monitor.py had six different placeholder aliases. The Worker enforces {HUMAN_FIRST}, {AI_NAME}, {MAGIC_LINK}, {TIER} only. Template PUT endpoint validates these four are present before saving.

7. **ensureSchema() on cold start** — Single idempotent function that runs CREATE TABLE IF NOT EXISTS + seeds default template. No separate migration script to forget to run.

## Files Produced

- `/home/jared/projects/AI-CIV/aether/exports/portal-files/welcome-email-worker-spec.md`

## What Existing agentmail_monitor.py Does That Must Stay

- Watches agentmail inbox (polling)
- Parses Witness magic link emails
- Stores magic links in .magic-links.json keyed by session UUID
- Notifies Jared on Telegram when new customer arrives
- Handles sandbox email detection (some logic moves to Worker)

Only `send_welcome_email()` is replaced. The monitor is not eliminated until Phase 2 (Witness calls Worker directly).
