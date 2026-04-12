#!/usr/bin/env python3
"""Patch social_suite.py to accept media_base64 on LinkedInPostReq
and convert it to a temp file passed via media_urls.

ROOT CAUSE: LinkedInPostReq only had media_urls (list of paths/URLs).
Callers sending media_base64 (raw base64 string) had it silently dropped by Pydantic.
"""

import os
import sys

SOURCE = "/opt/baas/social_suite.py"

with open(SOURCE, "r") as f:
    code = f.read()

# === 1. Add media_base64 and media_type to LinkedInPostReq ===
old_model = """class LinkedInPostReq(BaseModel):
    session_id: str
    content: str
    media_urls: List[str] = []"""

new_model = """class LinkedInPostReq(BaseModel):
    session_id: str
    content: str
    media_urls: List[str] = []
    media_base64: Optional[str] = None   # raw base64 image data
    media_type: Optional[str] = None     # e.g. "image/png", "image/jpeg" """

if old_model not in code:
    print("WARNING: LinkedInPostReq model already patched or has changed.")
    if "media_base64" in code.split("class LinkedInPostReq")[1].split("class ")[0]:
        print("  -> media_base64 already present in model. Skipping model patch.")
    else:
        print("FATAL: Cannot find LinkedInPostReq model to patch.")
        sys.exit(1)
else:
    code = code.replace(old_model, new_model)
    print("PATCHED: LinkedInPostReq model now accepts media_base64 + media_type")

# === 2. In the endpoint, convert media_base64 to a file and append to media_urls ===
# We need to find the endpoint and add the conversion logic
old_endpoint_body = "result = await _linkedin_post(sessions_ref, req.session_id, req.content, auto_confirm=False, media_urls=req.media_urls)"

new_endpoint_body = """# Convert media_base64 to a temp file and add to media_urls
        media_urls_final = list(req.media_urls)  # copy
        if req.media_base64:
            import base64 as _b64
            media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media_uploads')
            os.makedirs(media_dir, exist_ok=True)
            ext = 'png'
            b64_data = req.media_base64
            if req.media_type:
                if 'jpeg' in req.media_type or 'jpg' in req.media_type:
                    ext = 'jpg'
                elif 'gif' in req.media_type:
                    ext = 'gif'
                elif 'webp' in req.media_type:
                    ext = 'webp'
            # Handle data: URI prefix if present
            if b64_data.startswith('data:'):
                header_part, b64_data = b64_data.split(',', 1)
                if 'jpeg' in header_part or 'jpg' in header_part:
                    ext = 'jpg'
                elif 'gif' in header_part:
                    ext = 'gif'
            import time as _time
            fpath = os.path.join(media_dir, 'linkedin_b64_' + str(int(_time.time())) + '_' + os.urandom(4).hex() + '.' + ext)
            with open(fpath, 'wb') as f:
                f.write(_b64.b64decode(b64_data))
            media_urls_final.append(fpath)
            log.info('LinkedIn: converted media_base64 to file: %s (%d bytes)', fpath, os.path.getsize(fpath))

        result = await _linkedin_post(sessions_ref, req.session_id, req.content, auto_confirm=False, media_urls=media_urls_final)"""

if old_endpoint_body not in code:
    # Check if already patched
    if "media_urls_final" in code:
        print("WARNING: Endpoint already patched (media_urls_final found). Skipping.")
    else:
        print("FATAL: Cannot find endpoint call to patch.")
        sys.exit(1)
else:
    code = code.replace(old_endpoint_body, new_endpoint_body)
    print("PATCHED: Endpoint now converts media_base64 to temp file before calling _linkedin_post")

# === 3. Write patched file ===
with open(SOURCE, "w") as f:
    f.write(code)

print("\nSUCCESS: social_suite.py patched")
print("  - LinkedInPostReq now accepts media_base64 + media_type")
print("  - media_base64 is auto-converted to a temp file on disk")
print("  - File path is appended to media_urls before calling _linkedin_post")
print("  - Existing media_urls callers are unaffected")
print("\nRestart PureSurf to apply: systemctl restart puresurf")
