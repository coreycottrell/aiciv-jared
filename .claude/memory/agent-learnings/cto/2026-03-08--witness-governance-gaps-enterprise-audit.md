# CTO Memory: Witness Integration — Enterprise Governance Gap Analysis

**Date**: 2026-03-08
**Agent**: cto
**Type**: teaching + operational
**Topic**: Governance audit of PureBrain x Witness birth pipeline and customer portal — 10 gaps identified for Fortune 500 readiness

---

## Summary

Produced a formal enterprise governance gap analysis document for Corey Cottrell / Witness team.
Audit triggered by real incident: Tess Morgane Verneuil (MAKR Venture Fund) paid for PureBrain but
her container birth failed 3 times. Seed had to be delivered manually via comms hub.

## 10 Gaps Identified

| Priority | Gap |
|----------|-----|
| Critical | Birth pipeline reliability — no SLA, no alerting, 503 since March 5 |
| Critical | No payment verification (orderId: null) before container provisioning |
| Critical | No retry/queue system — customer sees hard failure with no recovery path |
| High | Seed intake auth — partner API key missing, blocks manual fallback |
| High | Customer PII transmitted over HTTP (not HTTPS) — GDPR/CCPA exposure |
| High | No health check endpoint on either Witness host |
| High | No container lifecycle management policy (backup, retention, deletion) |
| High | No disaster recovery or failover — single Hetzner host is SPOF |
| Medium | No centralized audit trail — Witness side is opaque to PureBrain |
| Medium | No formal API versioning or change notification SLA |

## Key Findings

- `orderId: null` bug is a PureBrain-side fix (we own it)
- TLS on Witness endpoints is a Witness-side fix (they own it)
- API key for seed intake is blocked on Witness issuing it
- Most gaps can be resolved in 30-60 days with focused effort
- No single gap is architecturally impossible to fix

## File Delivered

`/home/jared/projects/AI-CIV/aether/exports/witness-governance-gaps-2026-03-08.md`

## Pattern

When a paying customer incident occurs, immediately audit the full provisioning stack for governance
gaps — don't just fix the immediate issue. The incident is a signal, not the root cause.
Enterprise readiness requires: SLA, payment verification, retry/queue, TLS, audit trail, DR plan.
