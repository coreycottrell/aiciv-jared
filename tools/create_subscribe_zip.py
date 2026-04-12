#!/usr/bin/env python3
"""Create the plugin zip for purebrain-subscribe-fix."""
import zipfile
from pathlib import Path

BASE_DIR   = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_PHP = BASE_DIR / "exports" / "purebrain-subscribe-fix" / "purebrain-subscribe-fix.php"
ZIP_PATH   = BASE_DIR / "exports" / "purebrain-subscribe-fix.zip"

if ZIP_PATH.exists():
    ZIP_PATH.unlink()

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(PLUGIN_PHP, arcname="purebrain-subscribe-fix/purebrain-subscribe-fix.php")

print(f"Created: {ZIP_PATH}")
print(f"Size: {ZIP_PATH.stat().st_size} bytes")

# Verify contents
with zipfile.ZipFile(ZIP_PATH, "r") as zf:
    print(f"Contents: {zf.namelist()}")
