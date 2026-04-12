# Data Room Migration - Google Drive API Pattern

**Date:** 2026-03-20
**Type:** operational + technique
**Topic:** Bulk Google Drive folder copy for investor data room migration

## Context

Migrated critical investor files from old MAKR data room to new organized investor data room.

## What Worked

Domain-Wide Delegation via service account with subject impersonation. Recursive folder copy with 0.1s rate limiting successfully handled 520 files across 26 subfolders.

## Gotchas

1. "cannotCopyFile" error: Some folders have Google-level copy restriction - cannot be bypassed by API. Need manual copy via Drive UI.
2. Search returns too many results: Filter by parent ID.
3. Pagination required for large folders.
4. Rate limiting: 0.1s sleep prevents quota exhaustion.

## Results

MAKR term sheet, Statement of Accuracy, Legal Due Diligence (520 files), pitch deck, video pitch, TAM/SAM docs - all copied successfully. CFIUS folder blocked by copy permission.
