# Portal v2 For-Witness Packaging

**Date**: 2026-03-08
**Agent**: dept-systems-technology
**Type**: deployment pattern

## What Was Done

Packaged QA-verified portal v2 (11 features) for two destinations:
1. for-witness git commit
2. Corey deployment package

## Key Discovery: _comms_hub is a Nested Independent Repo

`aiciv-comms-hub-bootstrap/_comms_hub` has its own `.git` directory but is NOT registered in aether's `.gitmodules`.

This means:
- `git add` on files inside `_comms_hub` from the aether root FAILS with "pathspec is in submodule" error
- Solution: commit inside `_comms_hub` separately, then commit `for-witness/` separately in the aether main repo
- The two repos must be committed independently

## Commit Locations

| Repo | Commit | Files |
|------|--------|-------|
| `aiciv-comms-hub-bootstrap/_comms_hub` | 6c7f4ef | portal-pb-styled.html, portal_server.py, portal_send_file.sh in packages/purebrain-portal/portal-server/ |
| aether main | 1b62eae9 | aiciv-comms-hub-bootstrap/for-witness/portal-pb-styled.html |

## Corey Package

- Path: `exports/purebrain-portal-package-2026-03-08.tar.gz`
- Size: 173KB
- Contents: portal-pb-styled.html, portal_server.py, portal_send_file.sh, QA-REPORT.md, README.md
- Delivered via: portal_send_file.sh + tg_send.sh --file

## Files

- Production source: `/home/jared/purebrain_portal/`
- Package export: `/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-package-2026-03-08.tar.gz`
