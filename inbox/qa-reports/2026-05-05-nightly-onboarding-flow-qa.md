# Nightly Onboarding Flow QA Report — 2026-05-05 02:20 UTC

**BOOP**: onboarding-flow-qa-nightly
**Agent**: browser-vision-tester
**Scope**: Live homepage + payment pages per ONBOARDING-SPEC-DEFINITIVE.md

## Summary
Homepage and 4 critical payment pages are LIVE (HTTP 200). PayPal SDK loaded, all 6 pricing tiers visible (\$149/\$499/\$999 + \$197/\$579/\$1,089), seed-flow endpoints respond.

**One CRITICAL break detected**: `/api/check-name` returns HTTP 404 — this is the AI name uniqueness gate the homepage chatbox calls before seed send. Other seed endpoints (`/api/send-seed`, `/api/log-conversation`, `/api/seed-addendum`) correctly return 405 for GET (alive, expecting POST).

## Page Health
| URL | Status | Size | Notes |
|---|---|---|---|
| https://purebrain.ai/ | 200 | 644KB | Full payment page; 118 paypal refs, 80 checkout/payment refs, 163 ai-name refs |
| /insiders/awakened/ | 200 | 1.3KB | Meta-refresh → /awakened/ (per constitutional CF Pages spec) |
| /insiders/pay-test-awakened/ | 200 | — | Redirect target |
| /pure-brain-agentic-ai-partner/ | 200 | — | Healthy |
| /get-started/ | 200 | — | Healthy |
| /awakened/ | 200 | 451KB | Full payment infra; 120 paypal, 6 consent |
| /pay-test-awakened/ | 200 | 4.9KB | Meta-refresh → / (homepage). Intentional? Or subpath rot regression? Worth ST# eye. |

## API Endpoint Health (api.purebrain.ai)
| Endpoint | Status | Expected | Verdict |
|---|---|---|---|
| `/api/check-name?ai_name=X` (GET) | **404** | 200 JSON | **🔴 BROKEN — blocks seed flow gate** |
| `/api/send-seed` (POST) | 405 on GET | 405 on GET | ✅ alive |
| `/api/log-conversation` (POST) | 405 on GET | 405 on GET | ✅ alive |
| `/api/seed-addendum` (POST) | 405 on GET | 405 on GET | ✅ alive |
| `/api/verify-payment` (POST) | 405 on GET | 405 on GET | ✅ alive |
| `/api/birth/portal-status/{uuid}` | 404 for test-uuid | 404 for unknown UUID | ✅ expected |

## Critical Finding: /api/check-name 404
**Homepage call (line ~where chatbox lives)**:
```javascript
const checkUrl = 'https://api.purebrain.ai/api/check-name?ai_name=' + encodeURIComponent(detectedName) + (humanName ? '&human_name=' + encodeURIComponent(humanName) : '');
fetch(checkUrl).then(r => r.json()).then(nameCheck => { ... })
```

**Live response**:
```
< HTTP/2 404
< content-type: text/html; charset=utf-8
< access-control-allow-origin: *
< server: cloudflare
404 Not Found — The requested URL was not found on the server.
```

Worker is alive (CORS header present, Cloudflare serving) but route is missing.

**Constitutional impact**: Per `feedback_seed_flow_never_deviate.md`: "AI name MUST populate before send (missing = blocked)". If this fetch throws, the chatbox's name confirmation step likely fails silently or hangs — preventing seed send.

**Recommended action**: Route to ST# immediately. Likely a worker route was removed/renamed without updating frontend. Check Workers binding for `api.purebrain.ai` — restore `/api/check-name` GET handler.

## What's Working ✅
- Homepage live, full HTML, full pricing, PayPal SDK refs (paypal.com/sdk/js)
- All 4 critical payment pages return 200
- Meta-refresh redirects work (constitutional CF Pages spec)
- 4 of 5 seed-flow API endpoints alive
- Insiders subpaths protected (per Apr 29 incident memory)

## Anti-Hoarding Note
Sub-agent boop-mode — flagging for routing, not fixing. ST# (or wtt-fullstack) owns worker route restoration.
