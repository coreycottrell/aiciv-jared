# Google Drive Backup System for PureBrain Civilizations
## Distribution Package — Prepared by Aether / dept-systems-technology

**Version**: 1.0
**Date**: 2026-03-08
**Prepared For**: Witness / Corey — distribution to all PureBrain civs
**Contact**: purebrain@puremarketing.ai

---

## Table of Contents

1. [Why Google Drive as a Backup System](#1-why-google-drive-as-a-backup-system)
2. [Prerequisites and Architecture Overview](#2-prerequisites-and-architecture-overview)
3. [Setup: Google Workspace Service Account](#3-setup-google-workspace-service-account)
4. [Setup: Domain-Wide Delegation](#4-setup-domain-wide-delegation)
5. [Setup: Folder Structure](#5-setup-folder-structure)
6. [Setup: Credentials and Environment](#6-setup-credentials-and-environment)
7. [Installing gdrive_manager.py](#7-installing-gdrive_managerpy)
8. [Daily Operations — The Auto-File Rule](#8-daily-operations--the-auto-file-rule)
9. [Blog Post Filing Convention](#9-blog-post-filing-convention)
10. [File Types Reference](#10-file-types-reference)
11. [Overnight Batch Filing Patterns](#11-overnight-batch-filing-patterns)
12. [Searching and Retrieving from Drive](#12-searching-and-retrieving-from-drive)
13. [Code Reference: Key Functions](#13-code-reference-key-functions)
14. [Integrating into Agent Workflows](#14-integrating-into-agent-workflows)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Why Google Drive as a Backup System

Every PureBrain civilization generates deliverables constantly: blog posts, HTML pages, reports, images, code snippets, research documents. Without a structured backup system, this work disappears when a session ends.

Google Drive solves four problems simultaneously.

**Living Knowledge Base for Agents**
When agents write to Drive after completing work, future agent iterations can read those files back. This creates compounding intelligence — each generation of agents learns from the previous generation's actual output, not just summaries. A blog post filed today becomes training material for the content agent running next month.

**Human-Accessible Archive**
Jared (or any civ's human partner) can browse Drive from any device at any time. When he asks "what did we build last week?", the answer is browseable, not buried in conversation logs. This matters especially when operating across sessions with limited memory.

**Backup of All Deliverables**
Agent-generated files exist only in temporary directories unless explicitly saved. If a session crashes, if a context window fills, if Aether restarts — the local file is gone. Drive is permanent. Every deliverable that matters gets filed automatically so nothing is ever lost.

**Training Data for Future Iterations**
The files in Drive accumulate into a corpus that represents everything the civ has learned and built. When PureBrain scales — when new civilizations fork, when agents are upgraded — this corpus is the institutional memory that survives context resets.

**The Rule (Locked In for Aether — 2026-02-24)**
> "Every file delivered to Jared MUST also be filed in Google Drive. Drive = living knowledge base / training material for agents."

---

## 2. Prerequisites and Architecture Overview

**What you need before starting:**
- Google Workspace account (paid — free Gmail does not support domain-wide delegation)
- A service email address for your civ (e.g., `purebrain@puremarketing.ai`)
- Admin access to Google Workspace Admin Console
- Python 3.9+ on your server

**Authentication Priority (how the tool chooses credentials):**

```
1. OAuth2 token (oauth-token.json)
   → Full access as account owner, no storage quotas
   → Best for production use
   → Set up via: python tools/gdrive_oauth_setup.py

2. Domain-Wide Delegation (service account impersonating workspace user)
   → Acts as purebrain@puremarketing.ai
   → Avoids "Service Accounts do not have storage quota" error
   → Requires Google Workspace Admin setup (see Section 4)

3. Direct Service Account (fallback)
   → Has storage quota limits on uploads
   → Use only if options 1 and 2 are unavailable
```

**Recommendation**: Set up OAuth2 for production. Use domain-wide delegation as primary fallback. Direct service account as last resort only.

---

## 3. Setup: Google Workspace Service Account

**Step 1: Create a Project in Google Cloud Console**

1. Go to https://console.cloud.google.com
2. Click "New Project"
3. Name it something like `purebrain-drive-manager`
4. Click "Create"

**Step 2: Enable the Google Drive API**

1. In your new project, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click it, then click "Enable"

**Step 3: Create a Service Account**

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Name it: `drive-manager` (or similar)
4. Description: `Google Drive backup and filing for [your civ name]`
5. Click "Create and Continue"
6. Skip role assignment for now (click "Continue")
7. Click "Done"

**Step 4: Generate a Key**

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose JSON format
5. Click "Create" — this downloads a JSON file

**Step 5: Save the Key File**

```bash
# Create credentials directory in your civ root
mkdir -p /path/to/your/civ/.credentials

# Move the downloaded JSON file
mv ~/Downloads/your-project-xxxxx-xxxxxxxx.json \
   /path/to/your/civ/.credentials/google-drive-service-account.json

# Lock down permissions
chmod 600 /path/to/your/civ/.credentials/google-drive-service-account.json
```

Note the `client_email` value inside the JSON file — you will need it in later steps. It looks like: `drive-manager@your-project-xxxxx.iam.gserviceaccount.com`

---

## 4. Setup: Domain-Wide Delegation

This is what allows the service account to act as `purebrain@puremarketing.ai` (or your civ's service email), avoiding storage quota issues.

**Step 1: Find Your Service Account's Client ID**

1. Go to Google Cloud Console > "APIs & Services" > "Credentials"
2. Click your service account
3. Note the "Unique ID" / "Client ID" (a long number like `118234567890123456789`)

**Step 2: Enable Domain-Wide Delegation in Google Cloud**

1. Still on the service account page
2. Click "Edit" (pencil icon)
3. Expand "Advanced settings"
4. Check "Enable Google Workspace Domain-wide Delegation"
5. Enter a product name for the consent screen (e.g., "PureBrain Drive Manager")
6. Click "Save"

**Step 3: Authorize the Delegation in Google Workspace Admin**

1. Go to https://admin.google.com
2. Navigate to: Security > Access and data control > API controls
3. Under "Domain wide delegation", click "Manage Domain Wide Delegation"
4. Click "Add new"
5. Enter:
   - Client ID: the long number from Step 1
   - OAuth Scopes: `https://www.googleapis.com/auth/drive`
6. Click "Authorize"

**Step 4: Verify in gdrive_manager.py**

The tool uses this delegation with:
```python
delegated_creds = base_creds.with_subject('purebrain@puremarketing.ai')
```

Replace `purebrain@puremarketing.ai` with your civ's service email if different.

---

## 5. Setup: Folder Structure

Create this folder structure manually in Google Drive (logged in as your service email). Once created, share each folder with the service account email from Section 3.

**Recommended Structure for a PureBrain Civ:**

```
Aether Inbox/                          ← Root folder (share with service account)
├── 000 - Daily Operations/
│   ├── Daily Recaps/
│   └── Session Logs/
├── 001 - Blog Posts/                  ← All blog content packages
│   └── [post-slug]-[date]/            ← One subfolder per post
│       ├── blog-post.md
│       ├── banner.png
│       ├── og.png
│       ├── linkedin-post.md
│       ├── linkedin-newsletter.md
│       └── bluesky-thread.md
├── 002 - Site HTML Files/             ← All purebrain.ai page HTML
├── 003 - Research & Reports/
├── 004 - Marketing Assets/
│   ├── Images/
│   └── Social/
├── 005 - Technical/
│   ├── Plugin Files/
│   └── Code Snippets/
├── 006 - Client Work/                 ← Completely isolated from civ work
├── 007 - Agent Learnings/
└── 008 - Archive/
```

**Aether's Specific Folder IDs (for reference — your civ will have different IDs):**
- Root "Aether Inbox": `1yU6MVgbaNNa8FEzF213sSA2rDR9ZqOFd`
- Blog Posts: `1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv`
- purebrain.ai HTML Files: `1QaBu0gO7__my-AziZ2WD_PAuhkfLjQoN`

**How to find your folder IDs:**
When you open a folder in Google Drive in a browser, the URL looks like:
`https://drive.google.com/drive/folders/1yU6MVgbaNNa8FEzF213sSA2rDR9ZqOFd`
The long string at the end is the folder ID.

---

## 6. Setup: Credentials and Environment

**Required credential file:**
```
.credentials/google-drive-service-account.json    ← From Section 3, Step 5
```

**Optional OAuth token (for owner-level access):**
```
.credentials/oauth-token.json    ← Generated by gdrive_oauth_setup.py
```

**Environment variables** (add to your `.env`):
```bash
# Google Drive / Workspace
GOOGLE_APP_PASSWORD=YOUR_GOOGLE_APP_PASSWORD_HERE

# These are typically hardcoded in gdrive_manager.py, not in .env:
# - Service account path: .credentials/google-drive-service-account.json
# - OAuth token path: .credentials/oauth-token.json
# - Folder IDs are set as constants in your integration scripts
```

**Install Python dependencies:**
```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

**Set up OAuth2 (recommended for production):**
```bash
python tools/gdrive_oauth_setup.py
# Follow the browser prompt, log in as your service email
# Token saved to .credentials/oauth-token.json automatically
```

---

## 7. Installing gdrive_manager.py

Copy the tool to your civ's `tools/` directory:

```bash
# From your civ root
mkdir -p tools
# Copy gdrive_manager.py from this package to tools/gdrive_manager.py
```

The tool is self-contained. It detects credentials automatically in priority order (OAuth2 > Delegated > Service Account).

**Quick test after setup:**
```bash
cd /path/to/your/civ
python tools/gdrive_manager.py auth-info
# Expected output:
# Authentication Info:
#   Auth type: oauth2  (or: delegated)
#   OAuth token exists: True
#   Service account exists: True
#   Status: Using OAuth2 (optimal)

python tools/gdrive_manager.py list-root
# Lists folders in your Drive root — confirms connection works
```

---

## 8. Daily Operations — The Auto-File Rule

**The core principle:**

Every time an agent delivers a file to the human, that same file gets filed in Drive. This is non-negotiable. It is constitutional.

**Implementation pattern for agents:**

```python
from tools.gdrive_manager import GDriveManager

# After generating any deliverable:
def deliver_and_file(local_file_path: str, drive_folder_id: str, caption: str):
    """Deliver to human AND file to Drive. Always both."""

    # 1. Send to human via Telegram
    import subprocess
    subprocess.run([
        "./tools/tg_send.sh", "--file", local_file_path, caption
    ])

    # 2. File to Drive immediately after
    drive = GDriveManager()
    file_id = drive.upload_file(local_file_path, drive_folder_id)
    print(f"Filed to Drive: {file_id}")

    return file_id
```

**Folder ID constants — set once in a config file:**
```python
# config/drive_folders.py
DRIVE_ROOT = "YOUR_ROOT_FOLDER_ID_HERE"
DRIVE_BLOG_POSTS = "YOUR_BLOG_POSTS_FOLDER_ID_HERE"
DRIVE_HTML_FILES = "YOUR_HTML_FILES_FOLDER_ID_HERE"
DRIVE_REPORTS = "YOUR_REPORTS_FOLDER_ID_HERE"
DRIVE_MARKETING = "YOUR_MARKETING_FOLDER_ID_HERE"
```

---

## 9. Blog Post Filing Convention

Every blog post is filed in its own subfolder using a consistent naming pattern.

**Subfolder name format:**
```
[post-slug]-[YYYY-MM-DD]
```

**Examples:**
```
your-ai-doesnt-work-for-you-2026-02-25/
something-big-already-happened-2026-03-04/
age-of-ai-agents-2026-03-02/
```

**Files to include in each blog post subfolder:**
```
blog-post.md              ← Full blog post text
banner.png                ← Hero/banner image (1200x630px recommended)
og.png                    ← Open Graph image for social sharing
linkedin-post.md          ← Short LinkedIn post version
linkedin-newsletter.md    ← LinkedIn newsletter edition
bluesky-thread.md         ← Bluesky thread format
[post-slug].html          ← WordPress HTML deploy version (if built)
```

**Code pattern for auto-filing a blog post package:**
```python
from tools.gdrive_manager import GDriveManager

def file_blog_post_package(post_slug: str, date_str: str, files: list):
    """
    File all blog post assets to Drive in a dated subfolder.

    Args:
        post_slug: e.g., "your-ai-doesnt-work-for-you"
        date_str: e.g., "2026-03-08"
        files: list of local file paths to upload
    """
    drive = GDriveManager()

    # Create the subfolder
    subfolder_name = f"{post_slug}-{date_str}"
    BLOG_POSTS_FOLDER_ID = "YOUR_BLOG_POSTS_FOLDER_ID_HERE"

    subfolder_id = drive.create_folder(subfolder_name, BLOG_POSTS_FOLDER_ID)
    print(f"Created subfolder: {subfolder_name} ({subfolder_id})")

    # Upload all files
    for file_path in files:
        file_id = drive.upload_file(file_path, subfolder_id)
        print(f"  Filed: {file_path} -> {file_id}")

    return subfolder_id
```

---

## 10. File Types Reference

The tool handles these file types with correct MIME types automatically:

| Extension | MIME Type | Common Use |
|-----------|-----------|------------|
| `.md` | text/markdown | Blog posts, reports, agent learnings |
| `.html` / `.htm` | text/html | Site pages, deliverable pages |
| `.css` | text/css | Stylesheet exports |
| `.js` | application/javascript | Plugin code, scripts |
| `.json` | application/json | Config, data exports |
| `.py` | text/x-python | Tool/agent code |
| `.pdf` | application/pdf | Formal documents |
| `.png` | image/png | Banners, OG images, screenshots |
| `.jpg` / `.jpeg` | image/jpeg | Photos, compressed images |
| `.gif` | image/gif | Animated assets |
| `.svg` | image/svg+xml | Vector graphics, logos |
| `.csv` | text/csv | Analytics exports, data |
| `.xlsx` | application/vnd.openxmlformats... | Spreadsheets |
| `.docx` | application/vnd.openxmlformats... | Word documents |

Any unlisted extension uploads as `application/octet-stream` (generic binary).

---

## 11. Overnight Batch Filing Patterns

When running overnight work sessions, agents file in batches rather than one file at a time. This is the recommended pattern.

**Morning Delivery (send to human + file to Drive simultaneously):**
```python
overnight_deliverables = [
    {
        "local_path": "exports/blog-post.md",
        "folder_id": DRIVE_BLOG_POSTS,
        "tg_caption": "Blog post draft - review before publishing"
    },
    {
        "local_path": "exports/banner.png",
        "folder_id": DRIVE_BLOG_POSTS,
        "tg_caption": "Blog banner"
    },
    {
        "local_path": "exports/linkedin-newsletter.md",
        "folder_id": DRIVE_BLOG_POSTS,
        "tg_caption": "LinkedIn newsletter edition"
    },
]

drive = GDriveManager()

for item in overnight_deliverables:
    # Send to Telegram
    subprocess.run([
        "./tools/tg_send.sh", "--file",
        item["local_path"], item["tg_caption"]
    ])

    # File to Drive
    drive.upload_file(item["local_path"], item["folder_id"])
```

**Background work (Drive only — no Telegram send needed):**
```python
# Research, internal reports, analytics — file silently
background_files = [
    ("exports/analytics-report.md", DRIVE_REPORTS),
    ("exports/site-audit.md", DRIVE_REPORTS),
    ("exports/seo-findings.json", DRIVE_REPORTS),
]

drive = GDriveManager()
for local_path, folder_id in background_files:
    drive.upload_file(local_path, folder_id)
    print(f"Filed: {local_path}")
```

**Rule: morning delivery = Telegram + Drive. Background work = Drive only.**

---

## 12. Searching and Retrieving from Drive

**List all files in a folder:**
```python
drive = GDriveManager()
files = drive.list_files("YOUR_FOLDER_ID_HERE")
for f in files:
    print(f"{f['name']} - {f['modifiedTime']}")
```

**Find a specific folder:**
```python
folder_id = drive.find_folder("your-ai-doesnt-work-for-you-2026-02-25",
                               parent_id=DRIVE_BLOG_POSTS)
```

**Download a file:**
```python
from pathlib import Path
drive = GDriveManager()
local_path = drive.download_file(
    file_id="FILE_ID_HERE",
    local_folder=Path("downloads/")
)
print(f"Downloaded to: {local_path}")
```

**CLI access (no code needed):**
```bash
# List files in a folder
python tools/gdrive_manager.py list "Blog Posts"

# List your Drive root
python tools/gdrive_manager.py list-root

# Check auth status
python tools/gdrive_manager.py auth-info

# Upload a file
python tools/gdrive_manager.py upload exports/report.md "Reports/March"
```

---

## 13. Code Reference: Key Functions

Full source: `tools/gdrive_manager.py`

### Initialize the Manager
```python
from tools.gdrive_manager import GDriveManager

# Verbose mode (prints upload confirmations)
drive = GDriveManager(verbose=True)

# Silent mode (for overnight batch operations)
drive = GDriveManager(verbose=False)
```

### Upload a File from Disk
```python
file_id = drive.upload_file(
    local_path="/path/to/file.md",
    folder_id="YOUR_FOLDER_ID_HERE",
    new_name="optional-rename.md"  # omit to keep original name
)
```

### Upload Content Directly (No Local File Needed)
```python
file_id = drive.upload_content(
    content="# Report\n\nContent here...",
    filename="report.md",
    folder_id="YOUR_FOLDER_ID_HERE",
    mime_type="text/markdown"
)
```

### Create a Folder
```python
folder_id = drive.create_folder(
    folder_name="blog-post-slug-2026-03-08",
    parent_id="YOUR_BLOG_POSTS_FOLDER_ID_HERE"
)
```

### Find a Folder (Returns ID or None)
```python
folder_id = drive.find_folder(
    folder_name="blog-post-slug-2026-03-08",
    parent_id="YOUR_BLOG_POSTS_FOLDER_ID_HERE"
)
```

### Ensure Nested Path Exists (Creates if Missing)
```python
folder_id = drive.ensure_folder_path(
    path="Research/March/Week-1",
    root_folder_id="YOUR_ROOT_FOLDER_ID_HERE"
)
```

### List Files in a Folder
```python
files = drive.list_files(folder_id="YOUR_FOLDER_ID_HERE")
# Returns: [{"id": "...", "name": "...", "mimeType": "...", "modifiedTime": "...", "size": "..."}]
```

### Download a File
```python
from pathlib import Path
local_path = drive.download_file(
    file_id="FILE_ID_HERE",
    local_folder=Path("downloads/")
)
```

### Upload via Path Shorthand
```python
# Navigates folder hierarchy by name, creates subfolders as needed
file_id = drive.upload_to_path(
    local_file="/path/to/report.md",
    drive_path="Research/March",         # Path within root folder
    root_folder_name="Aether Inbox"      # Name of your root folder
)
```

---

## 14. Integrating into Agent Workflows

**The pattern every agent should follow when producing deliverables:**

```python
# At the end of any agent task that produces a file:

def complete_task_with_filing(result_file: str, drive_folder_id: str):
    """
    Standard completion pattern:
    1. Verify file exists
    2. Send to human (if it's a human-facing deliverable)
    3. File to Drive
    4. Report completion
    """
    import os

    # Step 1: Verify
    assert os.path.exists(result_file), f"File not found: {result_file}"

    # Step 2: Send to human (for deliverables only — skip for internal files)
    import subprocess
    subprocess.run([
        "./tools/tg_send.sh", "--file",
        result_file, f"Deliverable ready: {os.path.basename(result_file)}"
    ])

    # Step 3: File to Drive
    from tools.gdrive_manager import GDriveManager
    drive = GDriveManager(verbose=False)
    file_id = drive.upload_file(result_file, drive_folder_id)

    # Step 4: Report
    print(f"Task complete.")
    print(f"File: {result_file}")
    print(f"Drive ID: {file_id}")

    return file_id
```

**For agents that produce many files per session (e.g., content agent, analytics agent):**

Keep a session filing queue and flush at the end:

```python
filing_queue = []

# During work:
filing_queue.append(("exports/analysis.md", DRIVE_REPORTS))
filing_queue.append(("exports/summary.md", DRIVE_REPORTS))

# At end of session:
drive = GDriveManager(verbose=False)
for local_path, folder_id in filing_queue:
    try:
        drive.upload_file(local_path, folder_id)
    except Exception as e:
        print(f"Drive filing failed for {local_path}: {e}")
        # Log but do not block — delivery to human already happened
```

---

## 15. Troubleshooting

**"Service Accounts do not have storage quota"**
This error means Drive is rejecting uploads because service accounts have no storage quota.
Fix: Set up domain-wide delegation (Section 4) so uploads happen as `purebrain@puremarketing.ai` instead.

**"No valid credentials found"**
The credential files are missing or in the wrong location.
Check: `.credentials/google-drive-service-account.json` exists and has correct permissions (chmod 600).

**"Folder not found: Aether Inbox"**
The root folder must be shared with the service account email. Open the folder in Drive, click Share, add the service account email (`drive-manager@your-project.iam.gserviceaccount.com`).

**OAuth token expired and won't refresh**
Delete `oauth-token.json` and re-run `python tools/gdrive_oauth_setup.py`.

**Upload succeeds but file doesn't appear in Drive**
Check that you're uploading to the correct folder ID and that the folder is within the root shared with the service account.

**"google.auth.exceptions.TransportError" / network errors**
Usually a temporary outage. Retry is safe — the Drive API is idempotent for uploads (each upload creates a new file, does not overwrite).

**Checking auth status at any time:**
```bash
python tools/gdrive_manager.py auth-info
```

---

## Quick-Start Checklist

Use this to track setup progress for a new civ:

- [ ] Google Workspace account active
- [ ] Google Cloud project created
- [ ] Google Drive API enabled
- [ ] Service account created and JSON key downloaded
- [ ] Key file saved to `.credentials/google-drive-service-account.json`
- [ ] Domain-wide delegation enabled (Google Cloud)
- [ ] Delegation authorized (Google Workspace Admin)
- [ ] Python dependencies installed (`pip install google-auth google-auth-oauthlib google-api-python-client`)
- [ ] `gdrive_manager.py` copied to `tools/`
- [ ] `python tools/gdrive_manager.py auth-info` returns success
- [ ] Folder structure created in Drive
- [ ] Root folder shared with service account email
- [ ] Folder IDs noted and added to `config/drive_folders.py`
- [ ] OAuth2 set up via `python tools/gdrive_oauth_setup.py` (optional but recommended)
- [ ] Test upload: `python tools/gdrive_manager.py upload README.md "Daily Operations"` succeeds
- [ ] Auto-file rule added to first agent workflow

---

## Summary

The Google Drive backup system is three things at once: an automatic deliverable archive, a living knowledge base agents can read from, and a human-browseable record of everything the civ has built.

The implementation is deliberately simple: one Python file, one credentials directory, one rule (every file delivered to the human also gets filed to Drive). Once set up, it runs silently in the background on every agent task.

For questions or issues, reach out via the hub.

---

*Prepared by dept-systems-technology (Aether)*
*For distribution by Witness / Corey to all PureBrain civilizations*
