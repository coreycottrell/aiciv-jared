# Log Server StartLimitIntervalSec Fix + Payment Page Audit
**Date**: 2026-03-19
**Agent**: dept-systems-technology
**Type**: gotcha | teaching | operational

---

## TASK 1: Log Server Never-Die Fix

### Root Cause of 8-Hour Outage

The aether-logserver.service had `Restart=always` but did NOT have `StartLimitIntervalSec=0`.

Systemd default: `StartLimitIntervalUSec=10s` with `StartLimitBurst=5`.
If the server crashed 5 times within 10 seconds, systemd stops restarting entirely.
This is exactly what happened: some rapid crash loop caused the burst limit to trigger
at 02:22 UTC. Systemd gave up. Nobody noticed for 8+ hours.

### The Fix

Added to `[Unit]` section of `/etc/systemd/system/aether-logserver.service`:
  StartLimitIntervalSec=0

This disables the burst limit entirely. Systemd will retry FOREVER.
Also bumped RestartSec=10 (from 5) to add breathing room.

### Verification

  systemctl show aether-logserver.service --property=StartLimitIntervalUSec
  Result: StartLimitIntervalUSec=0  (confirmed)

### Rule for Critical Production Services

ALL services that must NEVER stay down need StartLimitIntervalSec=0 in [Unit].
Without it, rapid crash loops silently disable restart. Silent death — no alerts.

---

## TASK 2: Payment Page Audit Results

### All 6 Pages Exist
/live/, /insiders/, /awakened/, /partnered/, /unified/, /pay-test-sandbox-3/

### orderId Bug — /partnered/ and /pay-test-sandbox-3/

Both pages call launchPostPaymentFlow(tier) without passing orderId.
Function signature is also (tier) not (tier, orderId).
Result: initPayTestFlow gets orderId=null, seed data has no subscription ID.

Fix: change onPaymentComplete callback and function signature to match awakened/live/insiders/unified pattern.

### Plan ID Discrepancy: /insiders/
Insiders uses P-8AU4270420374002JNGY3VYQ for Awakened tier.
Awakened uses P-2SA65600MT088594TNGLTFKY for Awakened tier.
May be intentional insiders pricing. Needs Jared confirmation.

### Key Files
- Service: /etc/systemd/system/aether-logserver.service
- Pages: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/{page}/index.html
