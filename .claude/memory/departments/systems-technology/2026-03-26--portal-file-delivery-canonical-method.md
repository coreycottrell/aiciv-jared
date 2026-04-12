# Portal File Delivery -- Canonical Method

**Date**: 2026-03-26
**Type**: operational
**Topic**: How to deliver files to the PureBrain Portal with downloadable previews

## The Problem

Files sent via [FILE: /path] tags in agent responses do NOT reliably render as
downloadable files in the portal. The [FILE:] tag is parsed by the frontend's
parseAiFiles() function, but it depends on the tag being visible in the session
JSONL, and the download uses /api/download?path=... which serves from disk
(file may move or be deleted).

## The Solution: /api/deliverable

The portal has a dedicated /api/deliverable endpoint that is the ONLY reliable
method for file delivery.

### How it works:
1. POST to http://localhost:8097/api/deliverable with JSON body:
   {"path": "/absolute/path/to/file", "name": "display-name.ext", "message": "Caption text"}
2. Server copies file to ~/portal_uploads/ (persistent storage)
3. Server creates a [PORTAL_FILE:storedName:displayName] chat entry
4. Entry is pushed via WebSocket for real-time rendering
5. Frontend renders a styled download card with preview

### Tools created:
- Shell: tools/portal_deliver.sh /path/to/file.md "caption"
- Python: tools/portal_deliver.py /path/to/file.md -m "caption"
- Python import: from tools.portal_deliver import deliver_file

### Auth:
- Token read from ~/purebrain_portal/.portal-token
- Passed as Authorization: Bearer <token> header

### Supported file types:
- .md files: Rendered as markdown preview + download
- .png/.jpg images: Rendered as inline image preview + download
- .html files: Download card
- Any other type: Download card

## NEVER DO THIS:
- Do NOT use [FILE: /path] tags in chat text as the delivery mechanism
- Do NOT send files via Telegram (portal only per MEMORY rules)
- Do NOT copy to portal-files and assume they appear -- you must call /api/deliverable

## curl one-liner (for quick use):
TOKEN=$(cat ~/purebrain_portal/.portal-token)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8097/api/deliverable \
  -X POST -H "Content-Type: application/json" \
  -d '{"path":"/home/jared/exports/portal-files/myfile.md","name":"myfile.md","message":"Ready for review"}'
