# Aether Inbox

This folder is for uploading files that you want Aether to read and process.

## How to Use

1. **Upload files here** (via scp, file manager, or direct copy)
2. **Tell Aether** via Telegram: "Read my inbox" or "Check inbox"
3. **Aether will process** all files and respond

## Supported File Types

- PDFs
- Word documents (.docx)
- Excel spreadsheets (.xlsx)
- Text files (.txt, .md)
- Images (PNG, JPG)
- PowerPoint (.pptx)
- And more...

## Upload Methods

### SSH/SCP
```bash
scp your-file.pdf aiciv@server:/home/aiciv/user-civs/aiciv-jared/inbox/
```

### File Manager
Navigate to this folder and drag-and-drop files

### Direct Copy
If you have server access, copy files directly here

## Notes

- Files are processed on demand (when you ask)
- Aether can also monitor this folder automatically if needed
- No size limits (reasonable system limits apply)
- Files are stored until you delete them

---

**Created**: 2026-01-31
**Purpose**: Simple file upload interface for Jared → Aether communication
