# Memory: Birth Pipeline Proxy Full Audit — 2026-02-27

**Agent**: devops-engineer
**Type**: operational + teaching
**Topic**: Complete audit of purebrain_log_server.py birth proxy — proxy is correct, Witness is the failure point

---

## Key Findings

### Log Server Status
- Running: PID 1357088, port 8443, healthy
- SSL cert: valid until 2027-02-12
- Restart storm at 17:03 today: ~20 failed starts in 102s (something triggered restart while server was running)

### Proxy Endpoints
- All 3 endpoints (birth/start, birth/code, portal-status) correctly implemented
- WITNESS_BASE_URL = `http://104.248.239.98:8099` (correct)
- CORS restricted to purebrain.ai + jareddsanborn.com (correct)
- Rate limits, timeouts, error handling all solid
- NO code changes needed to proxy

### Birth Pipeline State
- birth:start:failed = 34 total across all history
- birth:start:url_ready = 4 total (all from early testing period)
- Zero successful completions for real paying customers
- Witness returning 500/503/timeout — THIS is the failure point

### Real Customers Affected
- Michael Hancock (Bonded, Metis) — 2026-02-26, hit 3x birth:start:failed
- Andrew Ryan "Ry" (Awakened, Flux) — 2026-02-27 00:40, hit 3x birth:start:failed
- Both completed questionnaire flow but could not get portal URL

### Witness Timeline Today
- 10:39:58 — ONE successful 200 response
- 10:40:35 — 500, then 503 (pool exhausted)
- 17:01-17:03 — Multiple 180s timeout (Witness not responding)

### /birth/seed Assessment
- Does NOT exist in proxy code
- NOT needed — seed is Witness internal, not browser-facing
- 3 endpoints cover complete browser-facing contract

### Pay-Test Logs
- 256 entries, all recent are sandbox/test (orderId=null, flowCompleted=false)
- Michael Hancock's Brevo emails may not have fired — check

## Action Items for Jared
1. Tell Witness team: their server is returning 500/503 and timing out
2. Verify Brevo emails fired for Michael Hancock (mthancock@gmail.com)
3. Investigate what triggered restart storm at 17:03
4. Add logrotate for purebrain_log_server.log (492k lines already)

## Audit Report Location
`/home/jared/projects/AI-CIV/aether/exports/log-server-birth-audit.md`
