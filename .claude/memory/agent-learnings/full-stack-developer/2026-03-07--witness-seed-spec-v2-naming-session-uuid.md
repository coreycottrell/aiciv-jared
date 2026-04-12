# Witness Seed Spec v2: naming_session_id + civ_name + session_uuid

**Date**: 2026-03-07
**Type**: operational, teaching
**Pages affected**: 689 (pay-test-2), 1232 (pay-test-sandbox-3)

## What Was Done

Added 3 new fields to the chatbox JS on both pay-test pages per Witness seed spec v2:

1. **`naming_session_id`** — mirrors `prePurchaseSessionId`. Added to both `convPayload` (after `session_id`) and `payTestPayload` (after `prePurchaseSessionId`).

2. **`metadata.civ_name`** — added to the `metadata` object inside `convPayload`. Value: `payTestData.aiName || ''`.

3. **`session_uuid`** — UUIDv4 generated once per flow via `crypto.randomUUID()` with UUID-v4 polyfill fallback. Assigned to `payTestData.sessionUuid` immediately after the `payTestData = {}` init block. Added to both `convPayload` and `payTestPayload`.

## Log Server Change

Added `'naming_session_id'` and `'session_uuid'` to `optional_fields` list in `/api/log-conversation` handler in `tools/purebrain_log_server.py`. Restarted via `sudo systemctl restart aether-logserver.service`.

## Key Pattern: Both pages have identical JS

Pages 689 and 1232 had identical `_elementor_data` lengths (485339 chars) and identical JS. The same string replacements worked for both with no variation.

## JS Location

The chatbox JS is in: `parsed[0]['elements'][0]['settings']['html']` — NOT in `settings.content`. This is an `html` widget (not `text` or `content`).

## Backups

- `/home/jared/projects/AI-CIV/aether/exports/backup_page_689_elementor_data_2026-03-07-seed-spec.json`
- `/home/jared/projects/AI-CIV/aether/exports/backup_page_1232_elementor_data_2026-03-07-seed-spec.json`
