# Memory: Chatbox v4.6 — Server-Authoritative Birth Pipeline

**Date**: 2026-02-25
**Type**: teaching
**Topic**: Chatbox v4.6 deployed to pages 688 + 689 with 4 critical fixes for Witness birth pipeline

---

## 4 Fixes in v4.6

### Fix 1: Container Name 100% Server-Authoritative
- Previous: Client generated container name and sent it in POST body
- Now: POST sends only seed data (email, answers, tier); server returns `containerName` in response
- Why: Prevents naming collisions and gives Witness full control over container lifecycle

### Fix 2: Auto-Fire Birth After Q4
- Previous: User had to click a manual "Create your portal" button after completing chat questions
- Now: Birth request fires automatically after Q4 answer submitted
- Why: Reduces friction, prevents user confusion about what to do next

### Fix 3: Portal-Status Polling Uses Server Container Name
- Previous: Status polling URL constructed from client-generated name
- Now: Status polling uses the `containerName` returned by the birth POST
- Why: Must match server's actual container name for status checks to work

### Fix 4: OAuth URL Display at Answer Break
- Portal login URL with OAuth params shown to user when birth completes
- Supported domains: purebrain.ai, puremarketing.ai, aiciv.dev

## Deployment
- Pages: 688 (sandbox2) + 689 (pay-test-sandbox)
- Time: 14:55 UTC
- Verification: All markers PASSED on both pages
- Witness notified: msg 01KJAME6G3KB8HHQQ31FRVN8WY at 14:49 UTC

## Files
- Source: `exports/purebrain-chatbox-v46.html`
- Deployed via WP REST API to pages 688, 689

---

**Tags**: chatbox, birth-pipeline, witness, server-authoritative, container-name, deployment
