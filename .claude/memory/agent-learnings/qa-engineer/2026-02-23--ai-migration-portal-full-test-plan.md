# QA Learning: AI Migration Portal — Full Test Plan

**Date**: 2026-02-23
**Type**: teaching
**Topic**: Comprehensive QA approach for file-upload migration portals with personalization promises

---

## What Was Built

A 715-line test plan covering the AI Migration Portal (4-step ChatGPT/Claude import wizard).
Full plan at: `/home/jared/projects/AI-CIV/aether/exports/migration-portal-test-plan.md`

---

## Key Patterns Documented

### 1. Personalization Promise = Falsifiable Test Requirements

When the product's value proposition is "we know you," generic output is a broken promise, not a bug. Every personalization claim must be written as a falsifiable assertion:
- RIGHT: "Insight card reads exactly '50 conversations' (matches count in test fixture)"
- WRONG: "Insight card feels personalized"

### 2. Test Fixture Generation Script Included

Migration portals are impossible to test without specific, controlled test data. The plan includes a full Python script (`generate_test_fixtures.py`) that creates 17 mock ChatGPT export ZIPs. This was the #1 thing that would have been missed without the fixture section.

Key fixtures:
- Valid small/large (50, 10,000 conversations)
- Empty array, missing file, malformed JSON
- XSS payload in conversation content
- Path traversal entry names in ZIP
- Long titles, special chars, non-English content
- Single conversation, all-same-topic

### 3. File Upload: Four Independent Security Controls Required

These do not subsume each other — all four must be tested independently:
1. Size limit (server-side, not just client-side — S-08)
2. MIME type via magic bytes, not extension (S-02)
3. ZIP bomb detection via decompression ratio (S-01)
4. Path traversal prevention via sandbox directory (S-04)

### 4. Temp File Deletion Must Be Verified on Error Path, Not Just Success Path

Common miss: cleanup job runs on success but not on processing failure. Two separate tests:
- S-06: Delete after successful processing
- S-07: Delete when processing FAILS (malformed JSON)

### 5. iOS Safari File Upload Requires Real Device Test

Safari on iOS defaults to camera roll, not Files app, when file input is tapped. Users need explicit guidance ("tap Browse to find your ZIP"). Cannot be caught in emulation — requires real device.

### 6. Test Execution Order to Surface Critical Blockers First

Phase 1 Smoke Tests (5 cases, 30 minutes) before all else. If any smoke test fails, stop and fix before investing in 16 hours of full testing.

### 7. Ship Criteria: Zero P0, Zero P1

P2s triaged and accepted with product sign-off. Explicit sign-off checklist with 10 items required before QA-approved stamp.

---

## Total Test Case Count

- Functional (F1–F9): 74 test cases
- Edge Cases (EC): 15 cases
- Responsive (R): 12 cases
- Accessibility (A): 18 cases
- Security (S): 18 cases
- Performance (P): 11 cases
- Acceptance Criteria (AC): 14 cases

**Total: 162 test cases**

---

## Estimated QA Time

14–16 hours for full execution. Recommend 2–3 QA cycles:
1. Developer self-test (smoke + functional)
2. QA engineer full pass (all modules)
3. Pre-ship verification (acceptance criteria + security sign-off)
