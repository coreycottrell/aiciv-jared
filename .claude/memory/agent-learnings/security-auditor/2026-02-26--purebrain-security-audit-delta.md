# Security Audit: purebrain.ai Delta (2026-02-26)

**Date**: 2026-02-26
**Type**: operational + teaching
**Agent**: security-auditor

## Context

Full security audit of purebrain.ai, building on prior audit from 2026-02-20.
Prior audit resolved 14 of 14 initial findings (11 fully, 3 required Jared's dashboard access).
This audit checked what remains and found new issues.

## What Was Found

### Still Outstanding (from prior audit)
- HIGH-001: Cloudflare Worker authentication — CANNOT verify from code. Must check Cloudflare dashboard. Prior audit said "waiting on Jared."
- LOW-003 (prior): TLS minimum version — still unverifiable from code alone.

### New Findings
- HIGH-002: Company and role user inputs reach `bubble.innerHTML = text.replace(/\n/g, '<br>')` via `aiSay()` without sanitization. Lines 1178 and 1199 of pay-test-script-chat-flow-v4.js. `aiName` was sanitized in v4.2 but `company` and `role` were missed.
- MEDIUM-001: CSP has been in Report-Only mode since v1.3.0 (6 days). Never switched to enforcing mode. Change `Content-Security-Policy-Report-Only` to `Content-Security-Policy`.
- MEDIUM-002: telegramBotToken (user-submitted Telegram bot credentials) logged in plaintext to `logs/purebrain_pay_test.jsonl`. Should log presence flag only, not the credential itself.
- MEDIUM-003: `_get_real_client_ip()` trusts X-Forwarded-For header even on direct connections. Allows rate limit bypass by spoofing the header on direct requests to 89.167.19.20:8443.
- MEDIUM-004: WITNESS_BASE_URL = 'http://104.248.239.98:8099' and ACGEE_LANDING_CHAT_URL = 'http://5.161.90.32:3001' are plaintext HTTP. OAuth codes and conversation data in transit.
- LOW-002: Rate limiting only exists on birth proxy endpoints. Core endpoints (/api/log-conversation, /api/log-pay-test, /api/verify-payment) have no rate limiting.
- LOW-005: PayPal webhook processed even when sig_verified=False. Logs unverified events instead of rejecting them.
- XML-RPC not disabled in WordPress security plugin.

## Key Patterns Learned

### XSS Pattern: aiSay() as innerHTML sink
`aiSay()` deliberately uses innerHTML to support `<br>`, `<em>`, `<strong>` in trusted messages.
This creates risk whenever user input reaches aiSay() without prior sanitization.
The sanitizeText() helper exists but must be applied at COLLECTION point for every user-input variable.
v4.2 fixed aiName. company and role were missed. Pattern to watch: any new user input variable.

### Credential in Logs Pattern
telegramBotToken passed from client, stripped in one endpoint (log-conversation), but preserved in another (log-pay-test). Defense-in-depth: strip credentials at INGEST point, not just at some endpoints.

### Rate Limit Coverage Gap Pattern
Rate limiting was added for one class of endpoints (birth proxy) but not applied to the original endpoints. When adding rate limiting, audit ALL endpoints systematically.

### CSP Report-Only Never Switched Pattern
CSP launched in report-only mode (correct). But switching to enforcement was never scheduled. Recommend: set a specific date (2 weeks after report-only launch) to switch to enforcement.

## Overall Security Posture Score
7.2/10 (up from ~5.2/10 on 2026-02-20)

## Files Reviewed
- /home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js
- /home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py
- /home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php
- /home/jared/projects/AI-CIV/aether/to-jared/security-audit-proof.md
- /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/full-stack-developer/2026-02-20--purebrain-security-hardening.md
- /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/full-stack-developer/2026-02-20--security-plugin-v260-hardening.md
- /home/jared/projects/AI-CIV/aether/.env (credential presence only, values not inspected)
