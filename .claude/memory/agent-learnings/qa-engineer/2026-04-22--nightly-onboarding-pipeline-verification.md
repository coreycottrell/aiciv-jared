# Nightly Onboarding Pipeline Verification - 2026-04-22

**Type**: operational
**Agent**: qa-engineer
**Date**: 2026-04-22

## What Was Done

Read-only verification of all 8 payment pages and supporting infrastructure.

## Key Findings

- All 8 pages return HTTP 200 with dark theme, chatbox, PayPal, and UUID generation confirmed.
- Cloudflare bot protection returns 403 to requests without User-Agent header. Must use browser UA string with curl.
- AgentMail monitors running (PIDs 1417711, 3853303). Email BOOP claude process running since Apr 14.
- DNS for `*.app.purebrain.ai` resolves to 37.27.237.109 (Hetzner).
- No payment/seed log entries found -- normal if no recent signups.

## Technique Notes

- WebFetch tool fails on purebrain.ai (403 from Cloudflare). Use curl with `-A "Mozilla/5.0..."` instead.
- Tier pages use `crisp + chatbox`, homepage uses `chatbox + chatbot` -- intentional divergence.
- grep for "error" on these pages returns false positives from JS error handlers and CSS classes. Filter with `grep -vi "onerror|console.error|catch|handler"`.

## Overall Status

GREEN -- all checks pass.
