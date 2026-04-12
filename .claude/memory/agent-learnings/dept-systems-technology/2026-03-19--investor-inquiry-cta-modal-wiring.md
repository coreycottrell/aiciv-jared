# Investor Inquiry CTA Modal Wiring
**Date**: 2026-03-19
**Agent**: dept-systems-technology
**Type**: teaching | operational

---

## What Was Built

Wired up the "Request More Info" and "Schedule a Call" buttons on investors-v8/index.html
to a new modal form + backend endpoint. Previously these were `<a href="mailto:...">` fallbacks.

## Three Button Locations in investors-v8

1. Hero section (~line 669): Was onclick="scrollToSec(13)" — changed to openInvestorModal('schedule_call')
2. AI chat panel (~line 1083): Was `<a href="mailto:...">` — changed to button with openInvestorModal('schedule_call')
3. Bottom CTA (~lines 1268-1269): Were two `<a href="mailto:...">` anchors — changed to buttons

## HTML Entity Encoding Gotcha

The original `<a>` tags in the HTML file used UNESCAPED & in query strings
(e.g. &body=), NOT HTML entity &amp;body=.
This is browser-spec-correct for href attributes but differs from what the Grep tool shows.
Always check the raw file when doing string replacement — Grep output may show entities.

## Modal Architecture

- Single modal #investor-modal handles both inquiry types
- openInvestorModal('request_info') / openInvestorModal('schedule_call') switches labels/fields
- schedule_call shows extra "Preferred Date/Time" row
- submitInvestorForm() POSTs to https://api.purebrain.ai/api/investor-inquiry
- On success: hides form, shows confirmation div with type-appropriate message
- On network error: shows inline error, re-enables submit

## Log Server Endpoint

Route: POST /api/investor-inquiry
File: /home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py
Log: /home/jared/projects/AI-CIV/aether/logs/investor_inquiries.jsonl

Required fields: name, email
Optional fields: type, company, phone, preferred_time, message

Sends AgentMail notification to aethergottaeat@agentmail.to in background thread.
Uses same pattern as governance_challenge endpoint (import send_agentmail from tools dir).

Also needed: make_response added to flask import for explicit CORS on OPTIONS 204 response.

## Smoke Test Result

curl -sk -X POST https://localhost:8443/api/investor-inquiry -H "Content-Type: application/json" \
  -d '{"type":"request_info","name":"Test","email":"test@example.com","message":"test"}'
Returns: {"id": "uuid", "ok": true}
Log confirmed written to investor_inquiries.jsonl.

## Key Files

- /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-v8/index.html
- /home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py (new endpoint ~line 926)
- /home/jared/projects/AI-CIV/aether/logs/investor_inquiries.jsonl (new log file)
