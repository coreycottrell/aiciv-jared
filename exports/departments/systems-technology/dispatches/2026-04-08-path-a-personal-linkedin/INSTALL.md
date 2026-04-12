# social-publisher.service -- INSTALL Runbook

**Agent**: devops-engineer
**Date**: 2026-04-08
**Wave**: 1c (BUILD)
**Target**: Host `aether` (Linux, systemd)

---

## Pre-Flight Checks (no sudo required)

Run these BEFORE installing the unit file. If any fails, stop and fix first.

```bash
# 1. Confirm the publisher script exists and is executable by python3
ls -l /home/jared/projects/AI-CIV/aether/tools/social_publisher.py
/usr/bin/python3 -c "import ast; ast.parse(open('/home/jared/projects/AI-CIV/aether/tools/social_publisher.py').read()); print('syntax ok')"

# 2. Confirm .env exists and contains INTERNAL_AUTH_TOKEN
test -f /home/jared/projects/AI-CIV/aether/.env && echo ".env present"
grep -q '^INTERNAL_AUTH_TOKEN=' /home/jared/projects/AI-CIV/aether/.env && echo "token set" || echo "MISSING TOKEN -- see Step 0"

# 3. Confirm log directory exists
mkdir -p /home/jared/projects/AI-CIV/aether/logs
touch /home/jared/projects/AI-CIV/aether/logs/social_publisher.systemd.log

# 4. Confirm state file exists (systemd ReadWritePaths needs it present OR parent dir writable)
touch /home/jared/projects/AI-CIV/aether/.social_publisher_state.json

# 5. Validate unit file syntax (no sudo needed)
systemd-analyze verify /home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/dispatches/2026-04-08-path-a-personal-linkedin/social-publisher.service
```

---

## Step 0: Generate INTERNAL_AUTH_TOKEN (if missing)

```bash
# Generate a 32-byte hex secret
TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "INTERNAL_AUTH_TOKEN=$TOKEN" >> /home/jared/projects/AI-CIV/aether/.env
echo "Token added. Save this same value for Wrangler secret in Wave 4:"
echo "$TOKEN"
```

**IMPORTANT**: The same token must be set as a Wrangler secret on the apex Worker (see Worker Deploy Runbook below).

---

## Step 1: Install the Unit File (REQUIRES SUDO)

```bash
# Copy unit file into systemd directory
sudo cp /home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/dispatches/2026-04-08-path-a-personal-linkedin/social-publisher.service /etc/systemd/system/social-publisher.service

# Lock down permissions
sudo chmod 644 /etc/systemd/system/social-publisher.service
sudo chown root:root /etc/systemd/system/social-publisher.service

# Reload systemd so it sees the new unit
sudo systemctl daemon-reload
```

## Step 2: Enable and Start

```bash
# Enable at boot + start immediately
sudo systemctl enable --now social-publisher.service
```

## Step 3: Verify

```bash
# Should show: active (running)
sudo systemctl status social-publisher.service

# Tail the log to watch startup
tail -f /home/jared/projects/AI-CIV/aether/logs/social_publisher.systemd.log

# journalctl fallback (if log file empty)
sudo journalctl -u social-publisher.service -f
```

**Expected signals of success**:
- `systemctl status` shows `Active: active (running)`
- Log shows publisher startup banner
- No `ProtectSystem=strict` violations (EACCES on writes)

---

## Rollback

```bash
sudo systemctl disable --now social-publisher.service
sudo rm /etc/systemd/system/social-publisher.service
sudo systemctl daemon-reload
```

---

## Security Hardening Applied

The unit file enforces defense-in-depth via the following systemd directives:

| Directive | Value | Effect |
|-----------|-------|--------|
| `NoNewPrivileges` | true | Process cannot gain privileges via setuid/fcaps |
| `ProtectSystem` | strict | `/`, `/usr`, `/boot`, `/etc` read-only |
| `ProtectHome` | read-only | `/home` read-only except ReadWritePaths |
| `ReadWritePaths` | logs, state, data | Only these dirs writable |
| `PrivateTmp` | true | Isolated `/tmp` and `/var/tmp` |
| `PrivateDevices` | true | No access to physical devices |
| `ProtectKernelTunables` | true | `/proc/sys`, `/sys` read-only |
| `ProtectKernelModules` | true | Cannot load kernel modules |
| `ProtectKernelLogs` | true | No kmsg access |
| `ProtectControlGroups` | true | cgroups read-only |
| `ProtectClock` | true | Cannot set system clock |
| `ProtectHostname` | true | Cannot change hostname |
| `ProtectProc` | invisible | Cannot see other users' processes |
| `ProcSubset` | pid | Only PID files in /proc |
| `CapabilityBoundingSet` | (empty) | All Linux capabilities dropped |
| `SystemCallFilter` | @system-service minus dangerous sets | Blocks @privileged, @mount, @debug, etc. |
| `SystemCallArchitectures` | native | No multi-arch syscall smuggling |
| `RestrictAddressFamilies` | AF_INET, AF_INET6, AF_UNIX | No raw/packet sockets |
| `RestrictNamespaces` | true | Cannot create namespaces |
| `RestrictRealtime` | true | No realtime scheduling |
| `RestrictSUIDSGID` | true | Cannot create setuid files |
| `LockPersonality` | true | Cannot change personality() |
| `MemoryDenyWriteExecute` | true | W^X enforcement (no JIT) |
| `LimitNOFILE` | 4096 | File descriptor cap |
| `LimitNPROC` | 512 | Process cap |
| `UMask` | 0027 | New files rw for owner only |

**Expected `systemd-analyze security social-publisher.service` score**: <= 2.0 (OK/GOOD range).

---

## Worker Deploy Runbook (Wave 4 - DO NOT RUN YET)

**Prerequisite**: Security + QA must green-light Wave 2/3 first.

```bash
cd /home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/apex-migration/pureapex-worker/

# 1. Set the INTERNAL_AUTH_TOKEN as a Wrangler secret (use SAME value as .env)
npx wrangler secret put INTERNAL_AUTH_TOKEN
# (paste the hex value from Step 0)

# 2. Deploy
npx wrangler deploy

# 3. If rate-limiting table is needed (check with Wave 2 security agent)
#    Replace <db-name> with actual D1 database name from wrangler.toml
npx wrangler d1 execute <db-name> --command="CREATE TABLE IF NOT EXISTS linkedin_rate_limit (hour_key TEXT PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0);"

# 4. Verify deploy
npx wrangler tail
```

---

## Post-Install Smoke Test

```bash
# Confirm service is running
systemctl is-active social-publisher.service  # expect: active

# Hit its health endpoint (if exposed; otherwise skip)
# curl -s http://localhost:PORT/health

# Confirm log is growing
wc -l /home/jared/projects/AI-CIV/aether/logs/social_publisher.systemd.log
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `status=226/NAMESPACE` | ReadWritePaths dir missing | Create the dir, `daemon-reload`, restart |
| `EACCES` writing state file | Not in ReadWritePaths | Add path, `daemon-reload`, restart |
| `ModuleNotFoundError` | Wrong python3 / missing deps | Point ExecStart at venv python, or `pip install` system-wide |
| Service silently exits | Missing INTERNAL_AUTH_TOKEN | Check Step 0, verify `.env` |
| `systemd-analyze verify` warns | Directive typo | Fix, re-copy, daemon-reload |

---

**END INSTALL.md**
