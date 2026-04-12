# Google Drive Folder Creation + Upload Pattern

**Date**: 2026-02-24
**Type**: operational
**Agent**: full-stack-developer

## Task
Upload 3 HTML deliverables to "004 - Website & Digital Assets" in Google Drive (Aether Inbox root).

## Key Finding: Folder Did Not Exist
The "004 - Website & Digital Assets" folder was NOT pre-existing in Aether Inbox.
The Aether Inbox has numbered training folders 000-015, but "004 - Website & Digital Assets" is a
DIFFERENT namespace from "004. Social Media Strategist..." which is a training folder.

Had to create it first, then upload.

## Working Pattern

### Step 1: List Aether Inbox contents to verify
```python
m.list_files('1yU6MVgbaNNa8FEzF213sSA2rDR9ZqOFd')  # Aether Inbox root ID
```

### Step 2: Create folder if missing
```python
folder_id = m.create_folder('004 - Website & Digital Assets', parent_id='1yU6MVgbaNNa8FEzF213sSA2rDR9ZqOFd')
```

### Step 3: Upload files using absolute paths
```python
file_id = m.upload_file('/absolute/path/to/file.html', folder_id)
```

## Results
- Folder ID: 1f_X7ueHoSbMX02YupE36Vx06kubkd21m
- purebrain-portal-login.html → ID: 1njw2a8IJ0iygieNn2_gZQMGkR4F7zy2l
- migration-portal-v2-updated.html → ID: 1zFYmAjcB6yvPDlX84cAaPLw4LRreKeIu
- purebrain-mission-vision-values.html → ID: 1W7TZhv_-DPwi0Cj_mFWqSl08ID1Q0VvZ

## Auth Note
Service account with domain-wide delegation works fine for create + upload.
gdrive_manager.py must be invoked from `/home/jared/projects/AI-CIV/aether/` directory.
