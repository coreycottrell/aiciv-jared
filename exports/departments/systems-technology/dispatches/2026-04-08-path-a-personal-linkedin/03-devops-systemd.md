# Wave 1c: BUILD - Systemd Unit + Deploy Infra

**Agent**: devops-engineer
**Wave**: 1 of 4 (BUILD -> SECURITY -> QA -> SHIP)
**Priority**: P1 CRITICAL - SHIP TODAY
**From**: dept-systems-technology
**Date**: 2026-04-08

## Objective

Stand up the systemd service for `social_publisher.py` and stage all sudo-required commands for Jared.

## Deliverables

### 1. Systemd Unit File

Create at `/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/dispatches/2026-04-08-path-a-personal-linkedin/social-publisher.service` with:

```ini
[Unit]
Description=Aether Social Publisher (LinkedIn)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=jared
WorkingDirectory=/home/jared/projects/AI-CIV/aether
EnvironmentFile=/home/jared/projects/AI-CIV/aether/.env
ExecStart=/usr/bin/python3 /home/jared/projects/AI-CIV/aether/tools/social_publisher.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/jared/projects/AI-CIV/aether/logs/social_publisher.systemd.log
StandardError=append:/home/jared/projects/AI-CIV/aether/logs/social_publisher.systemd.log

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/home/jared/projects/AI-CIV/aether/logs /home/jared/projects/AI-CIV/aether/.social_publisher_state.json
PrivateTmp=true
ProtectHome=read-only

[Install]
WantedBy=multi-user.target
```

### 2. Staged Install Commands (for Jared to run)

Document in an `INSTALL.md` next to the service file:

```bash
# 1. Copy unit file
sudo cp /home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/dispatches/2026-04-08-path-a-personal-linkedin/social-publisher.service /etc/systemd/system/social-publisher.service

# 2. Reload systemd
sudo systemctl daemon-reload

# 3. Enable + start
sudo systemctl enable --now social-publisher.service

# 4. Verify
sudo systemctl status social-publisher.service
tail -f /home/jared/projects/AI-CIV/aether/logs/social_publisher.systemd.log
```

### 3. Worker Deploy Runbook

Document the apex Worker deploy steps (to be run AFTER security + QA green-light):

```bash
cd /home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/apex-migration/pureapex-worker/

# Set the internal auth secret (one-time, Jared runs)
npx wrangler secret put INTERNAL_AUTH_TOKEN
# (paste a 32-byte random hex value)

# Deploy
npx wrangler deploy

# If new D1 table needed for rate limiting:
npx wrangler d1 execute <db-name> --command="CREATE TABLE IF NOT EXISTS linkedin_rate_limit (hour_key TEXT PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0);"
```

### 4. Secret Generation Helper

```bash
# Generate a strong INTERNAL_AUTH_TOKEN
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Add the same value to `/home/jared/projects/AI-CIV/aether/.env` as `INTERNAL_AUTH_TOKEN=...` so the publisher can read it.

## Constraints

- DO NOT run sudo commands yourself — stage them for Jared
- DO NOT deploy the worker until security + QA clear Wave 2/3
- Verify the service file syntax with `systemd-analyze verify` if possible without sudo

## Verification Required

- Show the contents of the `.service` file
- Show the `INSTALL.md` runbook
- Memory written to `.claude/memory/agent-learnings/devops-engineer/2026-04-08--social-publisher-systemd.md`
