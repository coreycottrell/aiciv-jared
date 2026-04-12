# Memory: /birth/seed Chatbox Wiring Analysis

**Date**: 2026-02-27
**Type**: teaching
**Agent**: full-stack-developer

## Context

Analyzed pages 688 and 689 chatbox code (v4.6.3) to plan /birth/seed wiring.
Files at: exports/pay-test-2-raw-content.html, exports/pay-test-sandbox-2-raw-content.html

## Key Learnings

### 1. learnMoreAnswers timing trap

`payTestData.learnMoreAnswers` is an empty array `[]` at `flow:complete`.
The learn-more loop runs AFTER flow:complete, triggered by the welcome button click.
Call order: runCompletion (flow:complete) → button click → runThankYouMessage → Learn More button → runLearnMoreLoop (learnMoreAnswers populated here).
If /birth/seed needs learn-more data, it must fire at `learn-more:complete`, not `flow:complete`.

### 2. tierPaid field name confusion

The initPayTestFlow() function takes `tierPaid` as a parameter but stores it as `payTestData.tier`.
`payTestData.tierPaid` does NOT exist. Always use `payTestData.tier`.
The /birth/seed spec draft says `tier: payTestData.tierPaid` — this is a bug in the spec. Use `payTestData.tier`.

### 3. Both pages use same WITNESS_WEBHOOK_HOST

As of v4.5, both page 688 (sandbox) and page 689 (production) use:
`const WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443';`
Previous versions had page 688 pointing to direct Witness IP for testing.

### 4. Proxy pattern is well-established

purebrain_log_server.py has a clean proxy pattern:
- `_proxy_to_witness(method, path, body, timeout)` — reusable for any new endpoint
- `_check_birth_rate_limit(client_ip, bucket, max_calls)` — reusable rate limiter
- `_CONTAINER_NAME_RE` — container name validation regex already defined
- New birth endpoints take ~30 lines each following the existing pattern

### 5. Body size limit for seed endpoint

Existing birth endpoints cap at 65536 bytes. For /birth/seed with full conversation history, use 524288 (512KB) instead — conversations can be large.

### 6. conversationHistory is already assembled in logPayTestData()

The exact same message-building logic (preMsgs + onboardingMsgs) needed for /birth/seed already exists in logPayTestData(). Copy it verbatim — don't reinvent it.

### 7. /birth/seed should be non-fatal

If /birth/seed fails (timeout, Witness error), the flow should continue. Container is already allocated from /birth/start. Portal polling continues regardless. Log the error to log-pay-test but don't throw.

## Files Analyzed

- exports/pay-test-2-raw-content.html (page 689, production)
- exports/pay-test-sandbox-2-raw-content.html (page 688, sandbox)
- tools/purebrain_log_server.py (proxy server)

## Output

Full wiring draft at: exports/birth-seed-wiring-draft.md
