# Nightly Onboarding Pipeline Verification - 2026-04-28

**Type**: operational
**Agent**: qa-engineer
**Date**: 2026-04-28

## What Was Done

Read-only verification of all 8 payment pages, 10 infrastructure checks, naming gate verification, and DNS fix confirmations.

## Key Findings

- All 8 pages return HTTP 200 with dark theme, chatbox, PayPal confirmed. Match counts stable vs prior nights.
- All 4 infrastructure processes running (AgentMail, Log Server, Telegram Bridge, Portal Server).
- DNS fixes for nova-michael and jaimee-jerome confirmed resolving to 46.62.187.74.
- Naming gate (line 10765 in index.html) confirmed: `shouldShowPricing && !state.pricingRevealed && state.aiName`.
- Seed block guard working: Michael Foley payment correctly held on Apr 27 due to "(not yet named)" AI name.
- Tess Verneuil container has TLS handshake failure (SSL internal error) -- known issue class, DNS resolves correctly.
- Welcome email API Worker healthy (HTTP 200, db connected).

## Technique Notes

- WebFetch still 403 on purebrain.ai (Cloudflare). Use curl with browser UA.
- Tess TLS issue: connection establishes to 37.27.237.109:443 but TLSv1.3 alert internal error during handshake. Not DNS, cert issue.

## Overall Status

GREEN -- all primary checks pass. Tess TLS is known/non-regression.
