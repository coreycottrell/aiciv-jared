# DNS Resolution Failure — systemd-resolved Silent Failure

**Date**: 2026-02-25
**Context**: Session 43 — VPS network appeared healthy but DNS was broken

## Problem
- `ping 8.8.8.8` worked (raw IP connectivity fine)
- `curl https://api.telegram.org/...` failed (DNS resolution broken)
- systemd-resolved was silently failing — no obvious error

## Root Cause
systemd-resolved service was in a degraded state. Network worked at IP level but hostname resolution failed.

## Fix Applied
1. Added Google DNS servers (`8.8.8.8`, `8.8.4.4`) to `/etc/resolv.conf`
2. Added critical hostnames to `/etc/hosts` as fallback
3. Restarted systemd-resolved

## Diagnostic Pattern
When network seems "up" but services fail:
```bash
# Test raw connectivity
ping -c 1 8.8.8.8

# Test DNS specifically
nslookup api.telegram.org
dig api.telegram.org

# Check resolver status
systemctl status systemd-resolved
resolvectl status
```

## Lesson
**Always test DNS specifically** — ping to an IP proving "network works" is misleading. Many services depend on DNS, so a silent resolver failure breaks everything while appearing healthy.
