# CTO Memory: Witness Seed Spec Audit — 5 Items

**Date**: 2026-03-07
**Agent**: cto
**Type**: teaching + operational
**Topic**: Audit of AETHER-SEED-SPEC.md changes against chatbox v44 + log server

---

## Summary

Audited 5 spec changes requested by Witness (Corey Cottrell) against:
- `exports/purebrain-chatbox-v44.html` (deployed to pages 1232 + 689)
- `tools/purebrain_log_server.py`

## Findings

| Item | Field | Status |
|------|-------|--------|
| 1 | `session_uuid` (UUIDv4) | MISSING — needs to be generated once at flow init |
| 2 | `naming_session_id` | WRONG FIELD NAME — exists as `prePurchaseSessionId`, must be renamed |
| 3 | `metadata.civ_name` | PARTIAL — set for naming ceremony sessions only; missing from pb-post payloads |
| 4 | Q5 / messages[9] goal | DONE — already working, confirmed 2026-03-04 |
| 5 | Port 8099 → 8200 | PORT CORRECT — seed intake already uses 8200; partner API key still needed from Witness |

## Critical Risk

Item 2 (`naming_session_id`) is a hard-denial failure. Birth will be rejected without it. The data exists — it is just sent under the wrong field name (`prePurchaseSessionId` vs `naming_session_id`).

## Files Requiring Change

- `exports/purebrain-chatbox-v44.html` → items 1, 2, 3 (deploy as v4.6)
- `tools/purebrain_log_server.py` → add fields to optional_fields list; add API key header

## Full Audit

`/home/jared/projects/AI-CIV/aether/exports/witness-seed-spec-audit-2026-03-07.md`
