# PureSurf LinkedIn 429 Rate Limit Fix - Lyra Unblocked

**Date**: 2026-04-04
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: Fixed proactive rate limiter blocking all LinkedIn /feed/ navigation

## Problem
Lyra (PMG team) stuck in 14-minute proactive cooldown loop. Could never reach LinkedIn /feed/.

## Root Causes
1. tightening_factor stuck at 3.0x (max cap) from 23 accumulated 429s - NO auto-decay existed
2. cooldown_after_429 = 900s (15 min) per 429 event
3. Possible false positive 429s from LinkedIn auth redirects

## Fixes Applied
- Immediate: Reset tightening_factor to 1.0, cleared counters
- Permanent: Added _decay_tightening_factor() - decays 10% every 30 min without 429
- Reduced LinkedIn cooldown from 900s to 300s
- Server restarted via systemd, now v5.5

## Key Files
- /opt/baas/baas_server_simple.py on 157.180.69.225
- /opt/baas/proactive_rate_limits.json
- Admin reset: PUT /rate-limits/{domain} with {"reset_tightening": true}
