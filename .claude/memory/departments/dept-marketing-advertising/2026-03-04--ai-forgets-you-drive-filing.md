# Drive Filing: The AI That Forgets You Every Single Time

**Date**: 2026-03-04
**Agent**: dept-marketing-advertising (CMO)
**Task**: File blog post package in Google Drive

---

## Summary

Filed the Prequel #1 blog post "The AI That Forgets You Every Single Time" (published 2026-03-04) into Google Drive per Jared's permanent blog post filing rule.

## Blog Post Details

- **Title**: The AI That Forgets You Every Single Time
- **Series**: Prequel #1 (Memory Series)
- **Published**: 2026-03-04
- **purebrain.ai URL**: https://purebrain.ai/the-ai-that-forgets-you-every-single-time/
- **jareddsanborn.com URL**: https://jareddsanborn.com/2026/03/04/the-ai-that-forgets-you-every-single-time/

## Drive Filing

- **Parent folder**: PureBrain.ai/blog content (ID: 1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv)
- **Subfolder created**: `the-ai-that-forgets-you-every-single-time-2026-03-04`
- **Subfolder ID**: 1E2hmbTRgLWW2LTpuVWXTTgsn9WAYKa4l
- **Subfolder link**: https://drive.google.com/drive/folders/1E2hmbTRgLWW2LTpuVWXTTgsn9WAYKa4l

## Files Filed (4 total)

| File | Drive ID | Source |
|------|----------|--------|
| the-ai-that-forgets-you-blog-post.md | 1ySHImHXUvbAgEFutZwhOzGyZie6idXez | docs/from-telegram/ |
| the-ai-that-forgets-you-banner-newsletter-size.png | 1R-ab4ffxdrKXzbr-E2XSKk6g-EGsCNGF | docs/from-telegram/ |
| deploy-results-ai-forgets-you.json | 1QEXQiFu71o--UUOwy0mn_I6mfDtaTLaR | exports/departments/dept-marketing-advertising/ |
| deploy-the-ai-that-forgets-you.py | 1v98GV05Js3I-Go0vEkULzhm0cFGQRSPe | exports/departments/dept-marketing-advertising/ |

## Key Learnings

- Blog Posts folder is named "PureBrain.ai/blog content" in Drive (ID: 1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv) — this is NOT findable by list-shared or list command; must be accessed via find_folder() or direct service.files().get()
- `GDriveManager` (not `DriveManager`) is the correct class name in tools/gdrive_manager.py
- `mgr.find_folder('Blog Posts', parent_id=AETHER_INBOX)` returned None because the folder is named "PureBrain.ai/blog content" not "Blog Posts"
- Direct `service.files().get(fileId=...)` is the reliable way to verify a folder ID is accessible
- HTML folder "Pure Brain - HTML" (ID: 1QaBu0gO7__my-AziZ2WD_PAuhkfLjQoN) was NOT used — no HTML generated for this post

## Verification

- Verified subfolder contents via `mgr.list_files(SUBFOLDER_ID)` — all 4 files present
- Telegram notification sent successfully (message_id: 17595)
