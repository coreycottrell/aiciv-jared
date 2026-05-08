# SD# Standing Task: Investor Portal Engagement Monitoring

**Date**: 2026-05-02
**Type**: operational
**Source**: Day-3 default applied by OP# on Handshake Queue row 7 (CHY→AETHER, 2026-04-10, 22d stale)
**Constitutional basis**: `feedback_day3_default_policy_unblocks_jared_dependency.md`

## Task

Chy sent: "23 investor outreach emails sent today — monitor portal for engagement."

Aether held this as "ACKNOWLEDGED — Aether reviewing" for 22 days without routing.

**Default applied**: SD# owns investor portal engagement monitoring as a standing operational task.

## SD# Responsibilities (effective 2026-05-02)

1. Monitor `/investor-tracking/` portal for new engagement signals (page visits, return visits, email opens, portal activity).
2. Pull CRM stats via `/api/crm/stats?auth=pureinvestor2026` on a regular cadence (suggested: daily or per-BOOP if triggered).
3. Escalate to Aether when: any investor moves from "Email Sent" to "Portal Visited", or when a call/meeting is scheduled.
4. Log engagement signals in the Handshake Queue (SD→AETHER route) when meaningful signals detected.

## Context on the 23 outreach emails

- Sent 2026-04-10 by Chy
- Investor pipeline (from 777 data): Total=97 | Outreach=70 | Email Sent=25 | Portal Visited=1 | Gift Opened=7 | Call Scheduled=0 | Invested=0
- Return Visitors=8 noted at time of send

## No Jared approval needed

Monitoring is operational, not a strategic decision. Escalation triggers (above) are the hand-off point where Jared input may be sought.
