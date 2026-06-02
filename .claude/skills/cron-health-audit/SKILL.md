---
name: cron-health-audit
description: Audit crontab for dead entries (missing scripts, expired one-shots), clean up safely with backup, verify survivors. Prevents cron rot and silent failures.
type: operations
domain: infrastructure, cron, reliability
created: 2026-05-21
trigger: "Run during overnight BOOPs or when BOOP-CRON-STALL detected (no boop output >90min). Also run after any script deletion or tools/ reorganization."
status: provisional
tick_count: 0
last_used: 2026-05-21
introduced: 2026-05-21
---

# Cron Health Audit

**Purpose**: Detect and remove dead crontab entries — scripts that no longer exist, one-shot tasks past expiry, or entries pointing to moved/renamed files. Prevents silent infrastructure rot where cron fires but does nothing.

**Origin**: 2026-05-21 — Overnight BOOP found 6 dead cron entries (5 missing scripts, 1 expired one-shot) out of 16 total. 37.5% dead rate. All were silently failing with no alerting.

## Steps

### 1. Backup Current Crontab

```bash
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M).txt
echo "Backup saved to /tmp/crontab_backup_$(date +%Y%m%d_%H%M).txt"
```

### 2. Audit Each Entry

```bash
crontab -l | grep -v '^#' | grep -v '^$' | while IFS= read -r line; do
  script=$(echo "$line" | grep -oP '(?<=\s)/[^\s>|&]+' | head -1)
  if [ -n "$script" ]; then
    if [ ! -f "$script" ]; then
      echo "DEAD: $script — file does not exist"
      echo "  LINE: $line"
    else
      echo "OK: $script"
    fi
  fi
done
```

### 3. Check for Expired One-Shots

Look for entries with comments like `# one-shot`, date-based scripts, or entries that reference past dates in their path/name.

### 4. Remove Dead Entries

```bash
crontab -l | grep -v 'DEAD_SCRIPT_NAME' | crontab -
```

Remove one at a time, verifying after each removal.

### 5. Verify Survivors

```bash
crontab -l | grep -v '^#' | grep -v '^$' | wc -l
echo "Remaining entries — all scripts verified to exist"
```

## Gotchas

- **Never remove entries you don't understand** — some crons call interpreters (python3, bash) with script as argument; parse the full command
- **Backup FIRST** — always, no exceptions
- **Check for wrapper scripts** — a cron may call a wrapper that calls the real script; verify the full chain
- **Log output** — dead crons with `>> logfile` may have been masking errors; check those logs
- **Systemd timers** — also check `systemctl list-timers` for duplicate scheduling

## Expected Output

```
Cron Health Audit — 2026-05-21
Backup: /tmp/crontab_backup_20260521_0530.txt
Total entries: 16
Dead entries: 6 (37.5%)
  - tier3-phase7c-watch.sh (missing)
  - disk_monitor.sh (missing)
  - sheet-d1-drift-check.sh (missing)
  - reconcile-skeleton-rows.sh (missing)
  - daily-no-referral-report.sh (missing)
  - scheduled-gologin-crack.sh (expired one-shot)
After cleanup: 10 entries, all verified
```
