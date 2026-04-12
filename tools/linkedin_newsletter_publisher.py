#!/usr/bin/env python3
"""
LinkedIn Newsletter Publisher via PureSurf
==========================================
Automates the full newsletter publishing flow:
  1. Navigate to The Neural Feed newsletter editor
  2. Paste newsletter title + body
  3. Upload banner image
  4. Click "Next" to get promotional post popup
  5. Paste promotional post text
  6. Click "Publish"
  7. Drop first comment with blog URL

Usage:
  python3 tools/linkedin_newsletter_publisher.py \\
    --newsletter /path/to/newsletter.md \\
    --promo /path/to/linkedin-post.md \\
    --banner /path/to/banner.png \\
    --blog-url "purebrain.ai/blog/slug/" \\
    [--dry-run]
"""

import argparse
import asyncio
import base64
import json
import os
import sys
import time
from pathlib import Path

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
NEWSLETTER_URL = "https://www.linkedin.com/newsletters/the-neural-feed-purebrain-ai-7428125791609192449/"

SS_DIR = Path("/home/jared/exports/linkedin-debug")
SS_DIR.mkdir(parents=True, exist_ok=True)


async def js_eval(client, session_id, script):
    """Execute JavaScript in the PureSurf session."""
    r = await client.post(
        f"{API_BASE}/sessions/{session_id}/evaluate",
        headers=HEADERS,
        json={"script": script},
        timeout=30,
    )
    return r.json()

async def save_screenshot(client, session_id, name):
    """Save a screenshot from the session."""
    r = await client.post(
        f"{API_BASE}/sessions/{session_id}/screenshot",
        headers=HEADERS,
        timeout=30,
    )
    if r.status_code == 200:
        path = SS_DIR / f"{name}_{int(time.time())}.png"
        # Handle both raw PNG and JSON-wrapped responses
        if len(r.content) > 0 and r.content[0:1] == b'\x89':
            with open(path, "wb") as fout:
                fout.write(r.content)
        else:
            try:
                data = r.json()
                img_data = data.get("data", data.get("screenshot", ""))
                if img_data:
                    with open(path, "wb") as fout:
                        fout.write(base64.b64decode(img_data))
            except Exception:
                with open(path, "wb") as fout:
                    fout.write(r.content)
        print(f"  Screenshot saved: {path}")
        return str(path)
    print(f"  WARNING: Screenshot failed ({r.status_code})")
    return None

async def ensure_session(client, profile):
    """Ensure a PureSurf session exists, return session_id."""
    r = await client.get(f"{API_BASE}/sessions", headers=HEADERS, timeout=15)
    sessions = r.json().get("sessions", [])
    for s in sessions:
        if s.get("profile_name") == profile or s.get("session_id") == profile:
            sid = s["session_id"]
            print(f"  Reusing existing session: {sid}")
            return sid

    print(f"  Creating new session for profile: {profile}")
    r = await client.post(
        f"{API_BASE}/sessions",
        headers=HEADERS,
        json={"profile_name": profile},
        timeout=60,
    )
    sid = r.json().get("session_id", "")
    print(f"  Created session: {sid}")
    return sid


async def navigate(client, session_id, url, wait_after=5000):
    """Navigate to a URL."""
    print(f"  Navigating to: {url}")
    r = await client.post(
        f"{API_BASE}/sessions/{session_id}/navigate",
        headers=HEADERS,
        json={"url": url, "wait_after": wait_after},
        timeout=60,
    )
    if r.status_code != 200:
        print(f"  WARNING: Navigate returned {r.status_code}")
    await asyncio.sleep(3)
    return r.status_code == 200


async def click_element(client, session_id, selector, description="element"):
    """Click an element by CSS selector."""
    print(f"  Clicking: {description}")
    script = f"""() => {{
        const el = document.querySelector('{selector}');
        if (el) {{ el.click(); return 'clicked'; }}
        return 'not_found';
    }}"""
    result = await js_eval(client, session_id, script)
    return result


async def type_text(client, session_id, selector, text, description="field"):
    """Type text into an element."""
    print(f"  Typing into: {description}")
    # Escape the text for JS
    escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    script = f"""() => {{
        const el = document.querySelector('{selector}');
        if (el) {{
            el.focus();
            el.innerText = `{escaped}`;
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            return 'typed';
        }}
        return 'not_found';
    }}"""
    result = await js_eval(client, session_id, script)
    return result


async def publish_newsletter(
    newsletter_md,
    promo_text,
    banner_path,
    blog_url,
    dry_run=False,
    profile=DEFAULT_PROFILE,
):
    """
    Full newsletter publishing flow.
    Returns dict with status, screenshots, and any errors.
    """
    results = {
        "status": "started",
        "screenshots": [],
        "errors": [],
        "newsletter_url": None,
    }

    # Parse newsletter markdown - title is first # heading
    lines = newsletter_md.strip().split("\n")
    title = ""
    body_lines = []
    for i, line in enumerate(lines):
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        else:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()

    print(f"\n=== LinkedIn Newsletter Publisher ===")
    print(f"  Title: {title}")
    print(f"  Body length: {len(body)} chars")
    print(f"  Promo text length: {len(promo_text)} chars")
    print(f"  Banner: {banner_path}")
    print(f"  Blog URL: {blog_url}")
    print(f"  Dry run: {dry_run}")
    print()

    async with httpx.AsyncClient() as client:
        # Step 1: Get/create session
        session_id = await ensure_session(client, profile)
        if not session_id:
            results["status"] = "error"
            results["errors"].append("Failed to create PureSurf session")
            return results

        # Step 2: Navigate to newsletter editor
        # The newsletter URL shows the list; we need the "Write article" button
        await navigate(client, session_id, NEWSLETTER_URL, wait_after=6000)
        ss = await save_screenshot(client, session_id, "01_newsletter_page")
        if ss:
            results["screenshots"].append(ss)

        # Step 3: Click "Write article" or "New edition" button
        # LinkedIn newsletter pages have a button to start a new article
        print("  Looking for 'Write article' button...")
        write_result = await js_eval(client, session_id, """() => {
            // Look for various button texts
            const buttons = Array.from(document.querySelectorAll('button, a'));
            for (const btn of buttons) {
                const text = btn.textContent.trim().toLowerCase();
                if (text.includes('write article') || text.includes('new edition') ||
                    text.includes('write') || text.includes('create article')) {
                    btn.click();
                    return 'clicked: ' + btn.textContent.trim();
                }
            }
            // Also check for the article editor link
            const links = Array.from(document.querySelectorAll('a[href*="article/edit"]'));
            if (links.length > 0) { links[0].click(); return 'clicked article edit link'; }
            return 'not_found';
        }""")
        print(f"  Write button result: {write_result}")
        await asyncio.sleep(5)

        ss = await save_screenshot(client, session_id, "02_after_write_click")
        if ss:
            results["screenshots"].append(ss)

        # Step 4: Fill in the article editor
        # The LinkedIn article editor has a title field and a body area
        print("  Setting article title...")
        title_result = await js_eval(client, session_id, f"""() => {{
            // Title field is usually a header-like element or input
            const titleEl = document.querySelector('[data-placeholder*="Title"], .article-title, [role="textbox"][aria-label*="Title"], h1[contenteditable], .editor-title');
            if (titleEl) {{
                titleEl.focus();
                titleEl.innerText = {json.dumps(title)};
                titleEl.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'title_set';
            }}
            // Fallback: find any contenteditable that looks like title
            const editables = document.querySelectorAll('[contenteditable="true"]');
            if (editables.length > 0) {{
                editables[0].focus();
                editables[0].innerText = {json.dumps(title)};
                editables[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'title_set_fallback';
            }}
            return 'title_not_found';
        }}""")
        print(f"  Title result: {title_result}")
        await asyncio.sleep(2)

        # Step 5: Set article body
        print("  Setting article body...")
        # Convert markdown body to simple HTML paragraphs for LinkedIn editor
        html_body = ""
        for para in body.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            if para.startswith("## "):
                html_body += f"<h2>{para[3:]}</h2>"
            elif para.startswith("**") and para.endswith("**"):
                html_body += f"<p><strong>{para[2:-2]}</strong></p>"
            elif para.startswith("**"):
                # Bold start of paragraph
                html_body += f"<p>{para}</p>"
            else:
                html_body += f"<p>{para}</p>"

        body_result = await js_eval(client, session_id, f"""() => {{
            // Body is usually the second contenteditable or a specific body area
            const bodyEl = document.querySelector('[data-placeholder*="Write"], .article-body, [role="textbox"][aria-label*="content"], .editor-content');
            if (bodyEl) {{
                bodyEl.focus();
                bodyEl.innerHTML = {json.dumps(html_body)};
                bodyEl.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'body_set';
            }}
            const editables = document.querySelectorAll('[contenteditable="true"]');
            if (editables.length > 1) {{
                editables[1].focus();
                editables[1].innerHTML = {json.dumps(html_body)};
                editables[1].dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'body_set_fallback';
            }}
            return 'body_not_found';
        }}""")
        print(f"  Body result: {body_result}")
        await asyncio.sleep(2)

        # Step 6: Upload banner image
        if banner_path and os.path.exists(banner_path):
            print("  Uploading banner image...")
            with open(banner_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()

            # Try to find the cover image upload area and inject the image
            banner_result = await js_eval(client, session_id, f"""() => {{
                // Look for cover image button or upload area
                const coverBtn = document.querySelector('[aria-label*="cover"], [aria-label*="Cover"], .cover-image-btn, button[data-test-id*="cover"]');
                if (coverBtn) {{ coverBtn.click(); return 'cover_clicked'; }}

                // Look for any image upload trigger
                const imgBtns = Array.from(document.querySelectorAll('button'));
                for (const btn of imgBtns) {{
                    if (btn.textContent.toLowerCase().includes('cover image') ||
                        btn.getAttribute('aria-label')?.toLowerCase().includes('cover')) {{
                        btn.click();
                        return 'cover_btn_clicked: ' + btn.textContent;
                    }}
                }}
                return 'cover_not_found';
            }}""")
            print(f"  Banner upload result: {banner_result}")
            await asyncio.sleep(3)

            # If cover area opened, try to inject the file
            if "clicked" in str(banner_result):
                # Look for file input and inject
                file_result = await js_eval(client, session_id, """() => {
                    const inputs = document.querySelectorAll('input[type="file"]');
                    if (inputs.length > 0) { return 'file_input_found: ' + inputs.length; }
                    return 'no_file_input';
                }""")
                print(f"  File input check: {file_result}")

                # Use PureSurf file upload endpoint if available
                if "file_input_found" in str(file_result):
                    upload_r = await client.post(
                        f"{API_BASE}/sessions/{session_id}/upload",
                        headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
                        json={
                            "selector": "input[type='file']",
                            "data": img_b64,
                            "filename": "banner.png",
                            "mime_type": "image/png",
                        },
                        timeout=30,
                    )
                    print(f"  File upload result: {upload_r.status_code}")
                    await asyncio.sleep(3)

        ss = await save_screenshot(client, session_id, "03_article_filled")
        if ss:
            results["screenshots"].append(ss)

        if dry_run:
            print("\n  === DRY RUN - Stopping before publish ===")
            results["status"] = "dry_run_complete"
            return results

        # Step 7: Click "Next" button
        print("  Clicking 'Next' button...")
        next_result = await js_eval(client, session_id, """() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            for (const btn of buttons) {
                const text = btn.textContent.trim().toLowerCase();
                if (text === 'next') {
                    btn.click();
                    return 'next_clicked';
                }
            }
            // Try the top-right area
            const topBtns = document.querySelectorAll('.artdeco-button--primary, .share-box-footer__primary-btn');
            for (const btn of topBtns) {
                if (btn.textContent.trim().toLowerCase().includes('next')) {
                    btn.click();
                    return 'next_primary_clicked';
                }
            }
            return 'next_not_found';
        }""")
        print(f"  Next button result: {next_result}")
        await asyncio.sleep(4)

        ss = await save_screenshot(client, session_id, "04_promo_popup")
        if ss:
            results["screenshots"].append(ss)

        # Step 8: Paste promotional post text into the popup
        print("  Pasting promotional post text...")
        promo_result = await js_eval(client, session_id, f"""() => {{
            // The promotional popup has a text area for the feed post
            const textareas = document.querySelectorAll('textarea, [role="textbox"], [contenteditable="true"]');
            for (const ta of textareas) {{
                const placeholder = ta.getAttribute('placeholder') || ta.getAttribute('aria-label') || '';
                if (placeholder.toLowerCase().includes('network') || placeholder.toLowerCase().includes('tell') ||
                    placeholder.toLowerCase().includes('promotional') || placeholder.toLowerCase().includes('post')) {{
                    ta.focus();
                    if (ta.tagName === 'TEXTAREA') {{
                        ta.value = {json.dumps(promo_text)};
                    }} else {{
                        ta.innerText = {json.dumps(promo_text)};
                    }}
                    ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    return 'promo_set';
                }}
            }}
            // Fallback: last contenteditable or textarea
            if (textareas.length > 0) {{
                const last = textareas[textareas.length - 1];
                last.focus();
                if (last.tagName === 'TEXTAREA') {{
                    last.value = {json.dumps(promo_text)};
                }} else {{
                    last.innerText = {json.dumps(promo_text)};
                }}
                last.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'promo_set_fallback';
            }}
            return 'promo_not_found';
        }}""")
        print(f"  Promo text result: {promo_result}")
        await asyncio.sleep(2)

        ss = await save_screenshot(client, session_id, "05_promo_filled")
        if ss:
            results["screenshots"].append(ss)

        # Step 9: Click "Publish"
        print("  Clicking 'Publish' button...")
        publish_result = await js_eval(client, session_id, """() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            for (const btn of buttons) {
                const text = btn.textContent.trim().toLowerCase();
                if (text === 'publish' || text === 'post') {
                    btn.click();
                    return 'published: ' + btn.textContent.trim();
                }
            }
            return 'publish_not_found';
        }""")
        print(f"  Publish result: {publish_result}")
        await asyncio.sleep(5)

        ss = await save_screenshot(client, session_id, "06_after_publish")
        if ss:
            results["screenshots"].append(ss)

        if "published" in str(publish_result).lower() or "post" in str(publish_result).lower():
            results["status"] = "published"
        else:
            results["status"] = "publish_uncertain"
            results["errors"].append(f"Publish button result: {publish_result}")

        # Step 10: Drop first comment with blog URL
        print(f"  Dropping first comment: {blog_url}")
        await asyncio.sleep(5)  # Wait for post to be live

        # Navigate to the post we just created (should be in feed or newsletter)
        comment_text = f"Full article: {blog_url}"
        comment_result = await js_eval(client, session_id, f"""() => {{
            // Look for comment box on the current page
            const commentBtns = Array.from(document.querySelectorAll('button'));
            for (const btn of commentBtns) {{
                if (btn.textContent.toLowerCase().includes('comment') &&
                    !btn.textContent.toLowerCase().includes('comments')) {{
                    btn.click();
                    return 'comment_btn_clicked';
                }}
            }}
            return 'comment_btn_not_found';
        }}""")
        print(f"  Comment button: {comment_result}")
        await asyncio.sleep(2)

        if "clicked" in str(comment_result):
            # Type the comment
            first_comment_result = await js_eval(client, session_id, f"""() => {{
                const editors = document.querySelectorAll('[role="textbox"][contenteditable="true"], .comments-comment-box__form [contenteditable]');
                for (const ed of editors) {{
                    if (ed.closest('.comments-comment-box') || ed.closest('[data-test-id*="comment"]')) {{
                        ed.focus();
                        ed.innerText = {json.dumps(comment_text)};
                        ed.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return 'comment_typed';
                    }}
                }}
                // Fallback
                const allEditable = document.querySelectorAll('[contenteditable="true"]');
                if (allEditable.length > 0) {{
                    const last = allEditable[allEditable.length - 1];
                    last.focus();
                    last.innerText = {json.dumps(comment_text)};
                    last.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    return 'comment_typed_fallback';
                }}
                return 'comment_field_not_found';
            }}""")
            print(f"  Comment typed: {first_comment_result}")
            await asyncio.sleep(1)

            # Submit the comment
            submit_result = await js_eval(client, session_id, """() => {
                const submitBtns = document.querySelectorAll('button[type="submit"], button.comments-comment-box__submit-button');
                for (const btn of submitBtns) {
                    if (btn.closest('.comments-comment-box') || btn.textContent.toLowerCase().includes('post')) {
                        btn.click();
                        return 'comment_submitted';
                    }
                }
                return 'submit_not_found';
            }""")
            print(f"  Comment submit: {submit_result}")
            await asyncio.sleep(3)

            ss = await save_screenshot(client, session_id, "07_first_comment")
            if ss:
                results["screenshots"].append(ss)

        # Get current URL (may be the newsletter article URL)
        url_result = await js_eval(client, session_id, "() => window.location.href")
        results["newsletter_url"] = url_result.get("result", "")

    return results


async def main():
    parser = argparse.ArgumentParser(description="LinkedIn Newsletter Publisher")
    parser.add_argument("--newsletter", required=True, help="Path to newsletter markdown")
    parser.add_argument("--promo", required=True, help="Path to promotional post text")
    parser.add_argument("--banner", required=True, help="Path to banner image")
    parser.add_argument("--blog-url", required=True, help="Blog URL for first comment")
    parser.add_argument("--dry-run", action="store_true", help="Stop before publishing")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="PureSurf profile")
    args = parser.parse_args()

    # Read content files
    with open(args.newsletter) as f:
        newsletter_md = f.read()
    with open(args.promo) as f:
        promo_text = f.read().strip()

    results = await publish_newsletter(
        newsletter_md=newsletter_md,
        promo_text=promo_text,
        banner_path=args.banner,
        blog_url=args.blog_url,
        dry_run=args.dry_run,
        profile=args.profile,
    )

    print(f"\n=== RESULTS ===")
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    asyncio.run(main())
