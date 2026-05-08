# Weft Rate-Limit 2nd-Pass Investigation

**Date**: 2026-04-14
**Type**: operational
**Topic**: Customer container OAuth isolation + shared-account theory disproved

## Findings

Inspected 13 customer containers on `37.27.237.109`. Read each `/home/aiciv/.claude/.credentials.json` inside the container.

### OAuth isolation is REAL (not shared)
Every container has a unique `accessToken`, `refreshToken`, and `expiresAt`. SHA256 hashes all differ. No two containers share an OAuth token. Provisioning per-customer works correctly.

### rateLimitTier discovery
The credentials file contains `rateLimitTier`. Observed values:
- `default_claude_max_20x`: weft-matthew, chy-jared, lumen-mireille
- `default_claude_max_5x`: keen-eric, sage-faris, alfred-bradley, bob-ian, thread-mark, torque-jay, vantage-vishal, mia-harrison

Most customer containers are on **Max 5x**, not 20x. That's a billing/provisioning question worth raising separately.

### Usage comparison (Weft vs same-tier baselines)
- Weft `/home/aiciv/.claude/projects`: **17M** total, **0 jsonl activity last 24h**, last active Apr 13 12:13
- Chy (20x): 437M, 9,411 messages last 24h
- Lumen (20x): 110M, 9,884 messages last 24h

**Weft is the LIGHTEST user of any 20x container**, not heaviest. The "Matt is a heavy user" theory is also disproved.

### CLI version
Weft = 2.1.77, Chy = 2.1.77 (healthy), Lumen = 2.1.80. Version isn't the differentiator.

## Evidence gap
We never actually saw a rate-limit error in Weft's logs/tmux. Matt's screenshot showed the Max 20x UI banner but we don't have the actual 429 payload / `retry-after` header. Next pass should:
1. Grab Matt's screenshot from the CTS ticket
2. Check container logs for 429 responses: `docker logs weft-matthew 2>&1 | grep -i "rate\|429\|limit"`
3. Ask Matt to paste the exact error text + timestamp

## Recommendation
First diagnosis (shared Max account) is WRONG — tokens are isolated.
Second hypothesis (Matt = heavy user) is WRONG — his volume is near-zero.
Need real error payload before any more theorizing. Do NOT change infrastructure based on speculation.
