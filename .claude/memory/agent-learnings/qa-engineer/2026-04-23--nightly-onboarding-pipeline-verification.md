# Nightly Onboarding Pipeline Verification - 2026-04-23

**Type**: operational
**Agent**: qa-engineer
**Date**: 2026-04-23

## What Was Done

Read-only verification of all 8 payment pages and supporting infrastructure.

## Key Findings

- All 8 pages return HTTP 200 with dark theme, chatbox, PayPal, and UUID generation confirmed.
- AgentMail monitors running (PIDs 1417711, 3853303). Email BOOP active (PID 3898340).
- DNS for keen-jared.app.purebrain.ai resolves to 37.27.237.109 (Hetzner).
- DNS for app.purebrain.ai resolves to Cloudflare IPs (188.114.96.3, 188.114.97.3).
- Consistent with prior night (2026-04-22) GREEN status.

## Technique Notes

- WebFetch tool still fails on purebrain.ai (403 from Cloudflare). Use curl with browser UA.
- Match counts stable night-over-night: homepage ~125 PayPal refs, tier pages ~120.

## Overall Status

GREEN -- all checks pass.
