# Security Review Memory: PureBrain Post-Payment Chatbox v3

**Agent**: security-engineer-tech
**Date**: 2026-02-22
**Type**: security-analysis
**Target**: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v3.js`
**Pre-audit reference**: `/home/jared/projects/AI-CIV/aether/exports/chatbox-security-pre-audit.md`
**Deployment Decision**: BLOCK — 2 CRITICAL issues remain, 1 NEW HIGH introduced, 2 NEW MEDIUM introduced

---

## What Changed v2 → v3 (Security Posture Summary)

| Issue | v2 Status | v3 Status |
|-------|-----------|-----------|
| CRIT-002: Claude API key rendered raw in chat | CRITICAL | PARTIALLY FIXED — masked in chat bubble but STILL SENT TO LOGGING BACKEND in plaintext |
| CRIT-003: Telegram bot token rendered raw in chat | CRITICAL | NOT FIXED — token rendered raw in chat bubble (line 1568) AND still sent to logging backend (line 76) |
| MED-001: innerHTML without sanitization | MEDIUM | PERSISTS with new vectors added (iconHtml, thank-you card, ai name in DOM) |
| MED-002: PII over-collection in log events | MEDIUM | PERSISTS — learn-more answers add new PII fields to each log payload |
| LOW-001: Raw error messages in UI | LOW | FIXED — error handler now uses textContent (line 1996), not innerHTML |

New issues introduced in v3:
- NEW HIGH: Portal URL reflected from backend response into a live href without sanitization (line 1897)
- NEW MED: aiName user-controlled string reflected into innerHTML via slide content (lines 808, 1544, multiple)
- NEW MED: learn-more PII (working style, friction points, 5-year vision, personal success) transmitted per-answer to logging backend without consent notice

---

## Key Line References for Future Reviews

- logPayTestData (payload construction): lines 63–155
- Claude API key collection + masking: lines 1148–1175
- Claude API key stored in payTestData.claudeSessionInfo: line 1175
- Telegram token rendered raw: line 1568
- Telegram token in log payload: line 76
- aiSay innerHTML bubble: line 910
- showSlide iconHtml innerHTML: line 958
- showSlide body innerHTML: line 967
- Thank-you card innerHTML: lines 1669–1709
- Portal URL insertion from backend: line 1897
- Error handler (FIXED to textContent): line 1996
- Dead code runClaudeMaxSetup: lines 1606–1611
- window.payTestData global exposure: lines 2012–2014
- learn-more loop PII logging: lines 1826–1831

---

## Patterns Learned

1. "Masked in UI" does not equal "not logged" — check both rendering AND logging pipeline separately
2. innerHTML chains: any user-supplied string that reaches innerHTML in a chain (aiName → slide content → innerHTML) is an XSS vector even when the string appears controlled
3. Portal URLs from backend responses need the same href sanitization as any other external source
4. Per-answer logging in progressive disclosure flows creates GDPR consent surface for new question types
5. Dead code in security-sensitive flows should be deleted, not commented — it becomes a maintenance liability and audit confusion source
