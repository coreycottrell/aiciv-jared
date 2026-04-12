# Memory: Seed Pipeline Diagnosis — Witness Down + orderId Bug

**Date**: 2026-02-27
**Type**: operational
**Agent**: full-stack-developer

## What Was Diagnosed

The pay-test-2 birth/seed pipeline to Witness/AICIV.

## Root Cause 1: Witness Server DOWN (P0)

- Witness at `104.248.239.98:8099` has been unreachable since 2026-02-25 23:49 UTC
- All `/api/birth/start` calls return 504 timeout via proxy at `https://89.167.19.20:8443/api/birth/start`
- Pattern: `birth:start:failed` events firing 3x per attempt (retry logic)
- Need to contact Witness team to restart server

## Root Cause 2: orderId Never Passed (P1)

- In `pay-test-integration-glue.js`, `launchPostPaymentFlow` calls `initPayTestFlow(container, aiName, tier)` — missing 4th argument (orderId)
- `initPayTestFlow` signature: `(chatContainer, aiName, tierPaid, orderId)`
- Fix: `window.initPayTestFlow(chatContainer, aiName, tier, window.payTestPaymentData?.orderId || null)`
- Result: `orderId` is null in ALL log entries

## Architecture Map (pay-test-2)

1. PayPal `onApprove` → `verifyPaymentServerSide(tier, orderId)` → `handlePaymentSuccess()` → `onPaymentComplete()`
2. Integration glue `onPaymentComplete` → `launchPostPaymentFlow(tier)` → `initPayTestFlow()`
3. Questionnaire Q1-Q4 → auto-fires `runBirthInit()` after Q4
4. `runBirthInit` → `POST /api/birth/start` (seed to Witness) → OAuth button
5. OAuth → `/api/birth/code` → container ready → portal polling
6. Flow complete → `logPayTestData({flowCompleted: true})` → Brevo emails fire

## Key Endpoints

- Log server: `https://89.167.19.20:8443` (our server, running)
- Birth proxy: `https://89.167.19.20:8443/api/birth/start` (proxies to Witness)
- Witness direct: `http://104.248.239.98:8099` (DOWN as of 2026-02-27)

## Log Files

- Conversations: `/home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl`
- Pay-test completions: `/home/jared/projects/AI-CIV/aether/logs/purebrain_pay_test.jsonl`
- Payments: `/home/jared/projects/AI-CIV/aether/logs/purebrain_payments.jsonl`

## What IS Working

- Log server healthy, all endpoints responding
- Q1-Q4 questionnaire data reaching log server correctly
- A-C-Gee and hub forwarding working
- Brevo email infrastructure ready (just waiting for flow:complete)

## Diagnosis Report

Full report: `/home/jared/projects/AI-CIV/aether/docs/diagnosis/seed-pipeline-diagnosis.md`
