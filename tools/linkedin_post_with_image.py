#!/usr/bin/env python3
"""LinkedIn Post with Image via PureSurf

DEPRECATED 2026-04-08: Superseded by Cloudflare Worker endpoint
    POST https://apex.purebrain.ai/api/linkedin/post-with-image
    Header: X-Internal-Auth: <INTERNAL_AUTH_TOKEN secret>
    Body:   { "text": "...", "image_url": "https://..." }

This browser-automation path is retained only as a fallback until the
Worker endpoint is QA-approved and deployed. Prefer the Worker API for
all new integrations (it's faster, has SSRF+auth+rate-limit guards, and
runs the canonical LinkedIn 3-step asset upload flow).

Reliable LinkedIn posting with image attachment.
Supports two approaches:
  1. Server-side: POST /social/adapters/linkedin/post with media_base64
  2. Client-side: Manual DOM manipulation via evaluate endpoint (fallback)

Usage:
  python3 tools/linkedin_post_with_image.py --image /path/to/image.png --text "Post content here"
  python3 tools/linkedin_post_with_image.py --image /path/to/image.png --text "Post content" --dry-run
  python3 tools/linkedin_post_with_image.py --image /path/to/image.png --text "Post content" --method client

Options:
  --image PATH     Path to image file (PNG, JPG, WEBP)
  --text TEXT      Post text content
  --dry-run        Open composer + attach image but do NOT click Post
  --method         "server" (default) or "client" (DOM-based fallback)
  --profile NAME   PureSurf profile name (default: jared-linkedin-fresh)
"""

import argparse
import asyncio
import base64
import json
import os
import sys
import time

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx")
    sys.exit(1)

# === Configuration ===
API_BASE = "http://157.180.69.225:8901"
API_KEY = "O_EnHpl-94xMLwvWZRNBIc6WGnfl5bkk9Ogk7eew_bg"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}
DEFAULT_PROFILE = "jared-linkedin-fresh"
SS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports", "linkedin-debug")
os.makedirs(SS_DIR, exist_ok=True)


def mime_from_path(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else "png"
    return {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
    }.get(ext, "image/png")


async def save_screenshot(client: httpx.AsyncClient, session_id: str, name: str) -> str:
    """Save a screenshot from the session."""
    r = await client.post(
        f"{API_BASE}/sessions/{session_id}/screenshot",
        headers=HEADERS,
        timeout=30,
    )
    if r.status_code == 200:
        path = os.path.join(SS_DIR, f"{name}_{int(time.time())}.png")
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"  Screenshot: {path} ({len(r.content)} bytes)")
        return path
    else:
        print(f"  Screenshot failed: {r.status_code}")
        return ""


async def js_eval(client: httpx.AsyncClient, session_id: str, script: str) -> dict:
    """Run JS in the browser session."""
    r = await client.post(
        f"{API_BASE}/sessions/{session_id}/evaluate",
        headers=HEADERS,
        json={"script": script},
        timeout=30,
    )
    return r.json()


async def ensure_session(client: httpx.AsyncClient, profile: str) -> str:
    """Ensure a PureSurf session exists, return session_id."""
    r = await client.get(f"{API_BASE}/sessions", headers=HEADERS, timeout=15)
    sessions = r.json().get("sessions", [])
    for s in sessions:
        if s.get("profile_name") == profile or s.get("session_id") == profile:
            sid = s["session_id"]
            print(f"  Reusing existing session: {sid}")
            return sid

    # Create new session
    print(f"  Creating new session for profile: {profile}")
    r = await client.post(
        f"{API_BASE}/sessions",
        headers=HEADERS,
        json={
            "profile_name": profile,
            "proxy_provider": "residential",
            "device": "macbook",
        },
        timeout=60,
    )
    if r.status_code != 200:
        print(f"  FATAL: Session creation failed: {r.status_code} {r.text[:300]}")
        sys.exit(1)
    data = r.json()
    sid = data.get("session_id", profile)
    print(f"  Created session: {sid}")
    return sid


async def navigate_to_feed(client: httpx.AsyncClient, session_id: str):
    """Navigate to LinkedIn feed."""
    print("  Navigating to LinkedIn feed...")
    r = await client.post(
        f"{API_BASE}/sessions/{session_id}/navigate",
        headers=HEADERS,
        json={"url": "https://www.linkedin.com/feed/", "wait_after": 5000},
        timeout=60,
    )
    if r.status_code != 200:
        print(f"  WARNING: Navigate returned {r.status_code}")
    await asyncio.sleep(3)


async def check_feed_state(client: httpx.AsyncClient, session_id: str) -> dict:
    """Check if we're on the feed and logged in."""
    result = await js_eval(client, session_id, """() => {
        return JSON.stringify({
            url: window.location.href,
            hasShareBox: !!document.querySelector('[aria-label="Start a post"]'),
            hasNav: !!document.querySelector('nav'),
            title: document.title,
            loginForm: !!document.querySelector('form.login__form')
        });
    }""")
    raw = result.get("result", "{}")
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


# ============================================================
# Shadow-DOM-aware composer helpers (LinkedIn 2026 redesign)
#
# The new LinkedIn composer is rendered inside an OPEN shadow root
# hosted on <div id="interop-outlet" class="theme--light">.
# All composer queries MUST go through that shadow root - top-level
# document.querySelector will return nothing for composer elements.
# ============================================================

SHADOW_HOST_JS = 'document.getElementById("interop-outlet")?.shadowRoot'

COMPOSER_SELECTORS = {
    # Trigger on main feed (wrapper div + inner role=button)
    "start_post_wrapper": '[aria-label="Start a post"]',
    # Inside shadow root:
    "editor": '.ql-editor[role="textbox"]',
    "editor_fallback": '[contenteditable="true"][role="textbox"]',
    "modal": '[role="dialog"].share-box-v2__modal',
    "add_media_btn": 'button[aria-label="Add media"]',
    "file_input": 'input#media-editor-file-selector__file-input[type="file"]',
    "file_input_fallback": 'input[type="file"][accept*="image"]',
    "next_btn": 'button.share-box-footer__primary-btn',
    "post_btn": 'button.share-actions__primary-action',
    "dismiss_btn": 'button[aria-label="Dismiss"]',
}


# ============================================================
# METHOD 1: Server-side (via /social/adapters/linkedin/post)
# ============================================================

async def post_server_method(
    client: httpx.AsyncClient,
    session_id: str,
    text: str,
    image_path: str,
    dry_run: bool,
) -> dict:
    """Post via the PureSurf social adapter with media_base64."""
    print("\n=== SERVER METHOD: Using /social/adapters/linkedin/post ===")

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = f.read()
    b64 = base64.b64encode(image_data).decode("utf-8")
    mime = mime_from_path(image_path)
    print(f"  Image: {image_path} ({len(image_data)} bytes, {mime})")

    # Step 1: Create draft with image
    print("  Creating draft with image...")
    payload = {
        "session_id": session_id,
        "content": text,
        "media_base64": b64,
        "media_type": mime,
    }
    r = await client.post(
        f"{API_BASE}/social/adapters/linkedin/post",
        headers=HEADERS,
        json=payload,
        timeout=120,
    )

    if r.status_code != 200:
        print(f"  ERROR: Draft creation failed: {r.status_code}")
        print(f"  Response: {r.text[:500]}")
        return {"status": "failed", "error": r.text[:500]}

    draft_result = r.json()
    print(f"  Draft status: {draft_result.get('status')}")

    # Save draft screenshot
    if draft_result.get("screenshot_path"):
        print(f"  Draft screenshot on server: {draft_result['screenshot_path']}")
    await save_screenshot(client, session_id, "draft_with_image")

    # Step 2: Verify image is visible in composer (shadow-DOM-aware, 2026 redesign)
    print("  Verifying image in composer (shadow root)...")
    verify = await js_eval(client, session_id, """() => {
        const host = document.getElementById('interop-outlet');
        const sr = host ? host.shadowRoot : null;
        const root = sr || document;  // fallback to document for old LinkedIn
        const dialog = root.querySelector('[role="dialog"].share-box-v2__modal')
            || root.querySelector('[role="dialog"]')
            || root.querySelector('.share-box-v2__modal');
        if (!dialog) return JSON.stringify({hasDialog: false, shadowExists: !!sr});

        const imgs = dialog.querySelectorAll('img');
        const imgSrcs = Array.from(imgs).map(i => ({
            src: (i.src || '').substring(0, 100),
            w: i.naturalWidth,
            h: i.naturalHeight,
            vis: i.offsetParent !== null
        }));
        const previews = dialog.querySelectorAll(
            '.share-box-image-thumbnail, .media-preview, ' +
            '[data-test-image-upload], .share-creation-state__media, ' +
            '.share-box__media-container, .share-creation-state__detour-container img, ' +
            '.image-detour-preview'
        );
        const blobs = dialog.querySelectorAll('img[src^="blob:"]');
        const spinners = dialog.querySelectorAll('.artdeco-spinner, [role="progressbar"]');

        return JSON.stringify({
            hasDialog: true,
            shadowExists: !!sr,
            imgCount: imgs.length,
            imgSrcs: imgSrcs,
            previewCount: previews.length,
            blobCount: blobs.length,
            spinnerCount: spinners.length,
            dialogHTML: dialog.innerHTML.substring(0, 500)
        });
    }""")

    raw = verify.get("result", "{}")
    if isinstance(raw, str):
        verify_data = json.loads(raw)
    else:
        verify_data = raw

    has_image = (
        verify_data.get("previewCount", 0) > 0
        or verify_data.get("blobCount", 0) > 0
        or any(
            img.get("w", 0) > 50 and img.get("h", 0) > 50
            for img in verify_data.get("imgSrcs", [])
        )
    )

    print(f"  Image in composer: {has_image}")
    print(f"  Previews: {verify_data.get('previewCount', 0)}, Blobs: {verify_data.get('blobCount', 0)}, Images: {verify_data.get('imgCount', 0)}")

    if not has_image:
        print("  WARNING: Image may not be attached! Check screenshot.")
        print(f"  Dialog HTML preview: {verify_data.get('dialogHTML', '')[:200]}")

    if dry_run:
        print("\n  DRY RUN: Not clicking Post. Composer is open with content.")
        return {"status": "dry_run", "image_detected": has_image, "verify": verify_data}

    # Step 3: Confirm post
    print("  Confirming post (clicking Post button)...")
    r = await client.post(
        f"{API_BASE}/social/adapters/linkedin/confirm-post",
        headers=HEADERS,
        json={"session_id": session_id},
        timeout=60,
    )

    if r.status_code != 200:
        print(f"  ERROR: Confirm failed: {r.status_code} {r.text[:300]}")
        return {"status": "confirm_failed", "error": r.text[:300]}

    confirm_result = r.json()
    print(f"  Post status: {confirm_result.get('status')}")

    await asyncio.sleep(5)
    await save_screenshot(client, session_id, "after_post")

    return {
        "status": confirm_result.get("status", "unknown"),
        "image_detected": has_image,
    }


# ============================================================
# METHOD 2: Client-side DOM manipulation (fallback)
# ============================================================

async def post_client_method(
    client: httpx.AsyncClient,
    session_id: str,
    text: str,
    image_path: str,
    dry_run: bool,
) -> dict:
    """Post via direct DOM manipulation using evaluate endpoint.

    Updated 2026-04-08 for LinkedIn's shadow-DOM composer redesign.
    The composer lives inside the open shadow root of #interop-outlet.
    """
    print("\n=== CLIENT METHOD: Shadow-DOM-aware composer (2026 redesign) ===")

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = f.read()
    b64 = base64.b64encode(image_data).decode("utf-8")
    mime = mime_from_path(image_path)
    fname = os.path.basename(image_path)
    print(f"  Image: {image_path} ({len(image_data)} bytes, {mime})")

    # Step 1: Navigate to feed
    await navigate_to_feed(client, session_id)
    state = await check_feed_state(client, session_id)
    print(f"  Feed state: {json.dumps(state)}")

    if state.get("loginForm"):
        print("  ERROR: Not logged in. Login required first.")
        return {"status": "not_logged_in"}

    if not state.get("hasShareBox"):
        print("  WARNING: Share box wrapper not found, trying anyway...")

    # Step 2: Click "Start a post" (the wrapper has aria-label, but the real
    # clickable is a child [role=button] div - clicking the wrapper is a no-op).
    print("  Opening post composer (clicking child role=button)...")
    click_result = await js_eval(client, session_id, """() => {
        const wrapper = document.querySelector('[aria-label="Start a post"]');
        if (!wrapper) return 'no_wrapper';
        const clickable = wrapper.querySelector('[role="button"]') || wrapper;
        clickable.click();
        return 'clicked:' + clickable.tagName + (clickable.getAttribute('role') || '');
    }""")
    print(f"  Click result: {click_result.get('result', 'unknown')}")

    # Step 3: Poll for composer ready inside shadow root (modal loads async)
    # The modal mounts quickly but shows a spinner while the editor/buttons load.
    print("  Waiting for composer editor to mount (up to 20s)...")
    comp_data = {}
    for attempt in range(20):
        await asyncio.sleep(1)
        composer_check = await js_eval(client, session_id, """() => {
            const host = document.getElementById('interop-outlet');
            if (!host || !host.shadowRoot) {
                return JSON.stringify({hasShadow: false});
            }
            const sr = host.shadowRoot;
            const modal = sr.querySelector('[role="dialog"].share-box-v2__modal')
                || sr.querySelector('[role="dialog"]');
            const editor = sr.querySelector('.ql-editor[role="textbox"]')
                || sr.querySelector('[contenteditable="true"][role="textbox"]');
            const addMediaBtn = sr.querySelector('button[aria-label="Add media"]');
            const postBtn = sr.querySelector('button.share-actions__primary-action');
            const spinner = sr.querySelector('.artdeco-spinner, [role="progressbar"]');
            return JSON.stringify({
                hasShadow: true,
                hasModal: !!modal,
                hasEditor: !!editor,
                hasAddMedia: !!addMediaBtn,
                hasPostBtn: !!postBtn,
                hasSpinner: !!spinner,
                editorCls: editor ? editor.className.substring(0, 60) : null,
                editorPlaceholder: editor ? (editor.getAttribute('data-placeholder') || editor.getAttribute('aria-placeholder')) : null
            });
        }""")
        raw = composer_check.get("result", "{}")
        comp_data = json.loads(raw) if isinstance(raw, str) else raw
        if comp_data.get("hasEditor") and comp_data.get("hasAddMedia"):
            print(f"  Composer ready after {attempt + 1}s")
            break
    print(f"  Composer (shadow): {json.dumps(comp_data)}")

    if not comp_data.get("hasShadow") or not comp_data.get("hasEditor"):
        print("  ERROR: Composer editor did not open inside shadow root.")
        await save_screenshot(client, session_id, "no_composer")
        return {"status": "no_composer", "detail": comp_data}

    await save_screenshot(client, session_id, "composer_open")

    # Step 4: Click "Add media" to mount the file input, then inject file
    print("  Clicking Add media to mount file input...")
    add_media_result = await js_eval(client, session_id, """() => {
        const sr = document.getElementById('interop-outlet').shadowRoot;
        const btn = sr.querySelector('button[aria-label="Add media"]');
        if (!btn) return 'no_add_media_btn';
        if (btn.disabled) return 'add_media_disabled';
        btn.click();
        return 'clicked';
    }""")
    print(f"  Add media: {add_media_result.get('result', 'unknown')}")
    await asyncio.sleep(2)

    # Step 5: Inject file into the shadow-root file input
    # Embed base64 directly in script (PureSurf /evaluate doesn't support args).
    # We stash the base64 on window.__pttImgB64 via a prior call so the main
    # script doesn't balloon past any per-script size limit.
    print("  Stashing image base64 on window...")
    # Chunk base64 to avoid single-script size limits
    CHUNK = 200000
    chunks = [b64[i:i + CHUNK] for i in range(0, len(b64), CHUNK)]
    init_script = '() => { window.__pttImgB64 = ""; window.__pttImgChunks = 0; return "ok"; }'
    await js_eval(client, session_id, init_script)
    for idx, chunk in enumerate(chunks):
        append_script = (
            '() => { window.__pttImgB64 += '
            + json.dumps(chunk)
            + '; window.__pttImgChunks += 1; return "chunk_" + window.__pttImgChunks; }'
        )
        res = await js_eval(client, session_id, append_script)
        if idx == 0 or idx == len(chunks) - 1:
            print(f"    chunk {idx + 1}/{len(chunks)}: {res.get('result', '?')}")
    # Verify stash size
    verify_stash = await js_eval(client, session_id, '() => "len=" + window.__pttImgB64.length')
    print(f"  Stash verified: {verify_stash.get('result', '?')} (expected len={len(b64)})")

    print("  Injecting image into shadow-root file input...")
    inject_js = (
        "() => { "
        "try { "
        "const host = document.getElementById('interop-outlet'); "
        "if (!host || !host.shadowRoot) { return JSON.stringify({error: 'no_shadow_host'}); } "
        "const sr = host.shadowRoot; "
        "const b64 = window.__pttImgB64; "
        "if (!b64) { return JSON.stringify({error: 'no_stash'}); } "
        "const binary = atob(b64); "
        "const bytes = new Uint8Array(binary.length); "
        "for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i); "
        "const blob = new Blob([bytes], { type: " + json.dumps(mime) + " }); "
        "const file = new File([blob], " + json.dumps(fname) + ", { type: " + json.dumps(mime) + ", lastModified: Date.now() }); "
        "const fileInput = sr.querySelector('input#media-editor-file-selector__file-input[type=\"file\"]') "
        "  || sr.querySelector('input[type=\"file\"][accept*=\"image\"]') "
        "  || sr.querySelector('input[type=\"file\"]'); "
        "if (!fileInput) { return JSON.stringify({error: 'no_file_input_in_shadow', shadowInputs: sr.querySelectorAll('input').length}); } "
        "const dt = new DataTransfer(); "
        "dt.items.add(file); "
        "fileInput.files = dt.files; "
        "fileInput.dispatchEvent(new Event('change', { bubbles: true, composed: true })); "
        "fileInput.dispatchEvent(new Event('input', { bubbles: true, composed: true })); "
        "return JSON.stringify({fileSet: true, inputId: fileInput.id, filesCount: fileInput.files.length}); "
        "} catch(e) { return JSON.stringify({error: e.message}); } "
        "}"
    )

    r = await client.post(
        f"{API_BASE}/sessions/{session_id}/evaluate",
        headers=HEADERS,
        json={"script": inject_js},
        timeout=120,
    )
    if r.status_code == 200:
        inject_result = r.json()
        raw = inject_result.get("result", "{}")
        inject_data = json.loads(raw) if isinstance(raw, str) else raw
        print(f"  Inject result: {json.dumps(inject_data)}")
    else:
        print(f"  Inject HTTP failed: {r.status_code} {r.text[:200]}")
        return {"status": "inject_failed"}

    # Wait for upload processing (LinkedIn has to upload the image and enable Next)
    print("  Waiting for upload to process (up to 20s)...")
    next_enabled = False
    for i in range(20):
        await asyncio.sleep(1)
        check = await js_eval(client, session_id, """() => {
            const sr = document.getElementById('interop-outlet').shadowRoot;
            const nextBtn = sr.querySelector('button.share-box-footer__primary-btn');
            return JSON.stringify({
                hasNext: !!nextBtn,
                nextDisabled: nextBtn ? nextBtn.disabled : null,
                nextText: nextBtn ? nextBtn.textContent.trim().substring(0, 20) : null
            });
        }""")
        raw = check.get("result", "{}")
        d = json.loads(raw) if isinstance(raw, str) else raw
        if d.get("hasNext") and d.get("nextDisabled") is False:
            next_enabled = True
            print(f"  Next enabled after {i+1}s")
            break
    if not next_enabled:
        print("  WARNING: Next button never enabled - image may not have uploaded")

    await save_screenshot(client, session_id, "after_image_inject")

    # Step 6: Click Next to return from editor modal to main composer with image preview
    if next_enabled:
        print("  Clicking Next to commit image to composer...")
        next_click = await js_eval(client, session_id, """() => {
            const sr = document.getElementById('interop-outlet').shadowRoot;
            const nextBtn = sr.querySelector('button.share-box-footer__primary-btn');
            if (!nextBtn) return 'no_next_btn';
            if (nextBtn.disabled) return 'next_disabled';
            nextBtn.click();
            return 'clicked';
        }""")
        print(f"  Next: {next_click.get('result', 'unknown')}")
        await asyncio.sleep(3)

    # Step 7: Type the post text into the Quill editor inside shadow root
    print("  Typing post content into .ql-editor (shadow root)...")
    type_result = await js_eval(client, session_id, f"""() => {{
        const sr = document.getElementById('interop-outlet').shadowRoot;
        const editor = sr.querySelector('.ql-editor[role="textbox"]')
            || sr.querySelector('[contenteditable="true"][role="textbox"]');
        if (!editor) return 'no_editor';
        editor.focus();
        // Quill uses its own model - setting innerHTML then firing input is the safest
        // approach that doesn't break Quill's delta state.
        const text = {json.dumps(text)};
        // Clear first
        editor.innerHTML = '<p><br></p>';
        // Build paragraph nodes for newlines so Quill parses it right
        const paragraphs = text.split('\\n').map(line => {{
            const p = document.createElement('p');
            if (line.length === 0) {{
                p.innerHTML = '<br>';
            }} else {{
                p.textContent = line;
            }}
            return p;
        }});
        editor.innerHTML = '';
        paragraphs.forEach(p => editor.appendChild(p));
        editor.classList.remove('ql-blank');
        // Fire input event so Quill/React reconcile
        editor.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
        editor.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
        // Also dispatch a composition event to nudge Quill
        editor.dispatchEvent(new InputEvent('input', {{ bubbles: true, composed: true, inputType: 'insertText', data: text }}));
        return 'typed:' + editor.textContent.length;
    }}""")
    print(f"  Type result: {type_result.get('result', 'unknown')}")

    await asyncio.sleep(2)
    await save_screenshot(client, session_id, "text_and_image")

    # Step 8: Verify composer state (editor has text, image attached, Post enabled)
    print("  Verifying composer state...")
    verify = await js_eval(client, session_id, """() => {
        const sr = document.getElementById('interop-outlet').shadowRoot;
        const editor = sr.querySelector('.ql-editor[role="textbox"]');
        const postBtn = sr.querySelector('button.share-actions__primary-action');
        // Image indicators (2026 redesign - verified selectors)
        const previewContainer = sr.querySelector('.share-creation-state__preview-container');
        const updateImage = sr.querySelector('.update-components-image');
        const dataImgs = Array.from(sr.querySelectorAll('img')).filter(i =>
            (i.src || '').startsWith('data:image/') && i.naturalWidth > 200
        );
        const blobs = sr.querySelectorAll('img[src^="blob:"]');
        return JSON.stringify({
            editorText: editor ? editor.textContent.substring(0, 80) : null,
            editorTextLen: editor ? editor.textContent.length : 0,
            postDisabled: postBtn ? postBtn.disabled : null,
            postExists: !!postBtn,
            hasPreviewContainer: !!previewContainer,
            hasUpdateImage: !!updateImage,
            dataImgCount: dataImgs.length,
            blobCount: blobs.length
        });
    }""")
    raw = verify.get("result", "{}")
    v = json.loads(raw) if isinstance(raw, str) else raw
    print(f"  Verify: {json.dumps(v)}")
    has_image = (
        v.get("hasPreviewContainer")
        or v.get("hasUpdateImage")
        or v.get("dataImgCount", 0) > 0
        or v.get("blobCount", 0) > 0
    )
    has_text = (v.get("editorTextLen", 0) > 0)
    post_ready = v.get("postExists") and v.get("postDisabled") is False

    print(f"  Image: {has_image}, Text: {has_text}, Post ready: {post_ready}")

    if dry_run:
        print("\n  DRY RUN: Not clicking Post.")
        return {
            "status": "dry_run",
            "image_detected": has_image,
            "text_detected": has_text,
            "post_ready": post_ready,
        }

    if not post_ready:
        print("  ERROR: Post button not enabled. Refusing to click.")
        await save_screenshot(client, session_id, "post_not_ready")
        return {
            "status": "post_not_ready",
            "image_detected": has_image,
            "text_detected": has_text,
        }

    # Step 9: Click Post button (inside shadow root)
    print("  Clicking Post button...")
    post_result = await js_eval(client, session_id, """() => {
        const sr = document.getElementById('interop-outlet').shadowRoot;
        const btn = sr.querySelector('button.share-actions__primary-action');
        if (!btn) return 'no_post_button';
        if (btn.disabled) return 'post_disabled';
        btn.click();
        return 'clicked';
    }""")
    print(f"  Post click: {post_result.get('result', 'unknown')}")

    await asyncio.sleep(6)
    await save_screenshot(client, session_id, "after_post_click")

    # Step 10: Verify the post actually went out (composer should be closed)
    final_check = await js_eval(client, session_id, """() => {
        const sr = document.getElementById('interop-outlet')?.shadowRoot;
        if (!sr) return JSON.stringify({shadowGone: true});
        const editor = sr.querySelector('.ql-editor[role="textbox"]');
        const modal = sr.querySelector('[role="dialog"].share-box-v2__modal');
        return JSON.stringify({
            composerStillOpen: !!editor,
            modalStillOpen: !!modal
        });
    }""")
    raw = final_check.get("result", "{}")
    final = json.loads(raw) if isinstance(raw, str) else raw
    posted_successfully = (
        final.get("shadowGone")
        or not final.get("composerStillOpen", True)
    )
    print(f"  Final state: {json.dumps(final)}")
    print(f"  Posted successfully (composer closed): {posted_successfully}")

    return {
        "status": "posted" if posted_successfully else "post_click_but_composer_still_open",
        "image_detected": has_image,
        "text_detected": has_text,
        "composer_closed": posted_successfully,
    }


# ============================================================
# Main
# ============================================================

async def main():
    parser = argparse.ArgumentParser(description="LinkedIn Post with Image via PureSurf")
    parser.add_argument("--image", required=True, help="Path to image file")
    parser.add_argument("--text", required=True, help="Post text content")
    parser.add_argument("--dry-run", action="store_true", help="Don't click Post")
    parser.add_argument("--method", choices=["server", "client"], default="server",
                        help="Posting method (default: server)")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="PureSurf profile name")
    args = parser.parse_args()

    if not os.path.isfile(args.image):
        print(f"ERROR: Image file not found: {args.image}")
        sys.exit(1)

    print(f"LinkedIn Post with Image")
    print(f"  Method: {args.method}")
    print(f"  Image: {args.image}")
    print(f"  Text: {args.text[:80]}...")
    print(f"  Dry run: {args.dry_run}")
    print(f"  Profile: {args.profile}")

    async with httpx.AsyncClient(timeout=120) as client:
        # Ensure session exists
        print("\n[1/4] Ensuring session...")
        session_id = await ensure_session(client, args.profile)

        # Check if we need to navigate to feed
        print("\n[2/4] Checking feed state...")
        state = await check_feed_state(client, session_id)
        print(f"  Current URL: {state.get('url', 'unknown')}")

        if state.get("loginForm"):
            print("  ERROR: Not logged in! Use PureSurf to log in first.")
            sys.exit(1)

        if not state.get("hasShareBox"):
            print("  Share box not found. Navigating to feed...")
            await navigate_to_feed(client, session_id)
            state = await check_feed_state(client, session_id)
            if not state.get("hasShareBox"):
                print("  WARNING: Still no share box. Login may be needed.")

        # Post
        print(f"\n[3/4] Posting via {args.method} method...")
        if args.method == "server":
            result = await post_server_method(client, session_id, args.text, args.image, args.dry_run)
        else:
            result = await post_client_method(client, session_id, args.text, args.image, args.dry_run)

        # Summary
        print(f"\n[4/4] Result:")
        print(f"  Status: {result.get('status')}")
        print(f"  Image detected: {result.get('image_detected', 'unknown')}")

        if result.get("status") == "posted" and not result.get("image_detected"):
            print("\n  *** WARNING: Post submitted but image may not have been attached! ***")
            print("  *** Check the live post on LinkedIn immediately! ***")

        return result


if __name__ == "__main__":
    asyncio.run(main())
