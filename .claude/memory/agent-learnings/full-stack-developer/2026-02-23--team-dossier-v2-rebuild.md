# Memory: Pure Technology Team Dossier v2 Rebuild

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Rebuilt team dossier from Google Drive TEAM MASTER DOSSIERS folder

---

## What Was Done

Downloaded and processed all files from Google Drive folder `1kAy0ZeCfpYDKx7Qg3iX02IBSfmjMJ_8S` (TEAM MASTER DOSSIERS).

- **49 people** found with dossier folders
- **142 files** downloaded (Bio .docx, LinkedIn .docx, Resume .pdf files)
- **0 download errors**

## Key Patterns

### GDriveManager Usage
- `manager.list_files(folder_id)` works with direct folder IDs (not just folder names)
- Service account credentials at `.credentials/google-drive-service-account.json`
- EXPORT_FORMATS dict handles Google Docs → PDF/CSV conversion automatically
- .doc files (older Word format) sometimes fail with python-docx — use try/except
- For deduplication: use underscore-named directories (skip space-named ones that are duplicates)

### Document Extraction
- python-docx extracts text from .docx files reliably
- .doc (old format) fails with python-docx: "file is not a Word file, content type is themeManager+xml"
- LinkedIn docs can be very large (up to 80K chars) — truncate to 3-4K for dossier
- Bio docs are typically 500-2500 chars and are the most useful

### Org Structure
- Excel has two sheets: "TEAM MASTER INDEX" (org chart with roles/reports) and "TRACKING SHEET" (completion status)
- TEAM MASTER INDEX: columns = Name, Role, Reports To, Direct Reports, Primary Function, Secondary Strengths, Cross-Functional Partners
- 13 people are in org chart but have NO dossier folders — not included per instructions

### People WITHOUT Drive Folders (no dossier available)
Lauron Joie, Myers Bill, Quinan Emmanuel Mark, Mallari Christie, Hadap Angelica,
MalcosteMichael, Pateno Junri, Pateno Jonel, Bago-od Johna, Casquejo Serg,
Bayetta Grean, Cordero PJ, Esperno Joseph

## Output Files
- Dossier: `/home/jared/projects/AI-CIV/aether/exports/pure-tech-team-dossier-v2.md`
- Raw downloads: `/home/jared/projects/AI-CIV/aether/docs/team-dossiers/{Person_Name}/`
- Excel tracking sheet: `/home/jared/projects/AI-CIV/aether/docs/team-dossiers/TEAM MASTER INDEX & TRACKING SHEET.xlsx`
