# Memory: Investor Data Room — SA Drive Quota Pattern

**Date**: 2026-03-20
**Type**: gotcha + synthesis
**Topic**: Service account Google Drive has zero storage quota; workaround strategy

## Context

Built complete investor data room for Pure Technology Inc. — 15 fully synthesized documents across 10 folders. All source material synthesized from:
- data-room-audit-report.md
- purebrain-product-overview.md
- purebrain-technology-architecture.md
- purebrain-customer-traction.md
- purebrain-competitive-analysis.md
- updated-executive-summary.md
- investor-data-room-knowledge-base.md
- pure-technology-knowledge-base.md

## Critical Gotcha: SA Drive Has Zero Storage

The service account `aether-drive-access@aether-integration.iam.gserviceaccount.com` has ZERO Drive storage quota allocated. This manifests as:
- `storageQuotaExceeded` 403 error on ANY file creation (even empty Google Docs)
- `about().get()` shows `"limit": "0"` — confirming zero quota
- Cannot upload even 1 byte

This is a hard limit on free service accounts without Workspace licenses.

## What DID Work

- Creating folders: WORKS (folders don't consume storage)
- Setting permissions: WORKS
- Listing files: WORKS
- Domain-wide delegation: NOT configured on this SA (can't impersonate Jared)
- Ownership transfer: FAILS (different org domains: aether-integration vs puretechnology.nyc)

## Workaround Applied

1. Created full folder structure (19 folders) — succeeded
2. Shared main folder with jared@puretechnology.nyc (writer access)
3. Created ZIP of all 15 docs organized by folder name
4. Sent ZIP via Telegram + Portal to Jared
5. Provided Drive link for manual upload

## Future Fix Options

1. Set up OAuth2 token (gdrive_oauth_setup.py) — gives Jared's account access, no quota issues
2. Enable domain-wide delegation for the SA in Google Workspace admin console
3. Add billing/storage to the SA's GCP project

## Synthesis Quality Notes

15 documents successfully synthesized from 8 source files. Key data points preserved:
- PureBrain: Y0 $441.8M, Y1 $3.5B, Y5 $50.7B
- Consolidated: Y1 $3.962B, Y5 $72.698B
- Subscribers: 420K → 12.9M
- ARPU: $345/mo, LTV:CAC: 28:1 → 225:1 → 550:1
- MAKR: $25M at $105M pre / $130M post
- Team: 48 people, hard cap 100

## File Locations

- ZIP: /home/jared/projects/AI-CIV/aether/exports/pure-tech-data-room-march2026.zip
- Source docs: /tmp/data-room-docs/ (15 .md files)
- Drive folder: https://drive.google.com/drive/folders/11sivCPcAVvVuwrcHRG-47tUH3fpBNaIx
- Drive folder ID: 11sivCPcAVvVuwrcHRG-47tUH3fpBNaIx
