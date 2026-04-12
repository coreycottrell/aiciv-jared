#!/usr/bin/env python3
"""Upload sandbox3 E2E test package to Google Drive folder."""

import sys
import os
sys.path.insert(0, '/home/jared/projects/AI-CIV/aether/tools')

from gdrive_manager import GDriveManager as GoogleDriveManager

FOLDER_ID = "1syJIYG21LExaNnXSCXp8neZ-meaYExG_"

FILES = [
    "/home/jared/projects/AI-CIV/aether/exports/sandbox3-e2e-comprehensive-report-20260304.md",
    "/home/jared/projects/AI-CIV/aether/docs/witness-integration-spec-2026-03-04-v2.md",
    "/home/jared/projects/AI-CIV/aether/docs/witness-integration-spec-2026-03-04.md",
    "/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_v6_final.py",
]

SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-full-20260304"

def main():
    manager = GoogleDriveManager()

    print(f"Target folder ID: {FOLDER_ID}")
    print()

    # Upload main files
    print("=== Uploading main files ===")
    for f in FILES:
        if os.path.exists(f):
            try:
                file_id = manager.upload_file(f, FOLDER_ID)
                print(f"  OK: {os.path.basename(f)} -> {file_id}")
            except Exception as e:
                print(f"  ERROR: {os.path.basename(f)} -> {e}")
        else:
            print(f"  MISSING: {f}")

    # Create screenshots subfolder and upload
    print()
    print("=== Creating screenshots subfolder ===")
    try:
        screenshots_folder_id = manager.create_folder("screenshots-62-total", FOLDER_ID)
        print(f"  Screenshots folder ID: {screenshots_folder_id}")
    except Exception as e:
        print(f"  ERROR creating screenshots folder: {e}")
        screenshots_folder_id = None

    if screenshots_folder_id and os.path.isdir(SCREENSHOTS_DIR):
        screenshots = sorted(os.listdir(SCREENSHOTS_DIR))
        print(f"  Uploading {len(screenshots)} screenshots...")
        success = 0
        for fname in screenshots:
            fpath = os.path.join(SCREENSHOTS_DIR, fname)
            if os.path.isfile(fpath):
                try:
                    manager.upload_file(fpath, screenshots_folder_id)
                    success += 1
                    if success % 10 == 0:
                        print(f"  ... {success}/{len(screenshots)} done")
                except Exception as e:
                    print(f"  ERROR: {fname} -> {e}")
        print(f"  Uploaded {success}/{len(screenshots)} screenshots")

    # Get shareable link for parent folder
    print()
    print("=== Getting folder link ===")
    try:
        folder_link = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
        print(f"  Folder link: {folder_link}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print()
    print("=== DONE ===")
    print(f"Google Drive folder: https://drive.google.com/drive/folders/{FOLDER_ID}")

if __name__ == "__main__":
    main()
