# Nightly Onboarding Check - 2026-04-11
**Type**: operational
**Agent**: dept-systems-technology

## Key Findings
- All 8 pages HTTP 200, dark theme, chatbox, PayPal present
- Log server health endpoint is HTTPS: `https://localhost:8443/api/health` (not HTTP, not /health)
- Tier pages show tier-appropriate pricing (not all 3 prices) - this is expected, not a failure
- Vira/Rimah magic link (UUID b92f44f6) stored correctly but container pb2-02 unreachable
- seed_sent_uuids.json file no longer exists - may be deprecated
- 3,009 conversations logged in purebrain_web_conversations.jsonl

## Patterns
- Previous nightly check noted 5 failures on /insiders/+/awakened/ for "legacy template" - these were actually tier-appropriate pricing, not failures
- Log server false negative: using HTTP instead of HTTPS or wrong path (/health vs /api/health) causes false "not responding"

## Score
120/128 (93.8%) - up from 118/123
