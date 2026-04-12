#!/usr/bin/env python3
"""
Deploy pb-blog-styling plugin v1.1.0 to purebrain.ai via WP Admin Plugin Editor.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

PLUGIN_FILE = Path("/home/jared/projects/AI-CIV/aether/tools/security/pb-blog-styling/pb-blog-styling.php")
WP_LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"
WP_USER = "purebrain@puremarketing.ai"
WP_PASS = "ij34utJdGCOst1*RcSvubXjb"
PLUGIN_EDITOR_URL = "https://purebrain.ai/wp-admin/plugin-editor.php"
VERIFY_URL = "https://purebrain.ai/age-of-ai-agents-next-18-months/"
STYLE_ID = "purebrain-blog-text-bg"


def main():
    plugin_content = PLUGIN_FILE.read_text(encoding="utf-8")
    print(f"[+] Plugin file loaded: {len(plugin_content)} chars")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
        page = context.new_page()

        # ── Step 1: Login ──────────────────────────────────────────────────────
        print("[+] Navigating to WP login...")
        page.goto(WP_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_url("**/wp-admin/**", timeout=30000)
        print(f"[+] Logged in. Current URL: {page.url}")

        # ── Step 2: Navigate directly to Plugin File Editor with plugin selected ─
        direct_url = f"{PLUGIN_EDITOR_URL}?file=pb-blog-styling/pb-blog-styling.php&plugin=pb-blog-styling/pb-blog-styling.php"
        print(f"[+] Going directly to plugin file editor: {direct_url}")
        page.goto(direct_url, wait_until="domcontentloaded", timeout=30000)
        print(f"[+] Editor URL: {page.url}")

        # ── Step 3: Wait for CodeMirror editor ─────────────────────────────────
        print("[+] Waiting for editor to load...")
        time.sleep(2)  # give CodeMirror a moment

        has_codemirror = False
        try:
            page.wait_for_selector(".CodeMirror", timeout=8000)
            has_codemirror = True
            print("[+] CodeMirror editor detected")
        except PlaywrightTimeoutError:
            print("[+] No CodeMirror found, checking for textarea...")

        # Also check for textarea
        has_textarea = False
        try:
            page.wait_for_selector("#newcontent", timeout=3000)
            has_textarea = True
            print("[+] Plain textarea (#newcontent) detected")
        except PlaywrightTimeoutError:
            pass

        if not has_codemirror and not has_textarea:
            print("[!] ERROR: No editor found! Page content:")
            print(page.inner_text("body")[:1000])
            browser.close()
            return False

        # ── Step 4: Set content ────────────────────────────────────────────────
        if has_codemirror:
            # Set via CodeMirror API AND also update the underlying textarea
            result = page.evaluate("""(newContent) => {
                try {
                    var cmEl = document.querySelector('.CodeMirror');
                    if (!cmEl) return {ok: false, msg: 'no .CodeMirror element'};
                    var cm = cmEl.CodeMirror;
                    if (!cm) return {ok: false, msg: 'no .CodeMirror property'};
                    cm.setValue(newContent);
                    // Also force sync to underlying textarea
                    cm.save();
                    var ta = document.getElementById('newcontent');
                    if (ta) {
                        ta.value = newContent;
                    }
                    return {ok: true, length: cm.getValue().length};
                } catch(e) {
                    return {ok: false, msg: e.toString()};
                }
            }""", plugin_content)
            print(f"[+] CodeMirror set result: {result}")
        else:
            # Plain textarea
            page.evaluate("""(newContent) => {
                var ta = document.getElementById('newcontent');
                ta.value = newContent;
                ta.dispatchEvent(new Event('input', {bubbles: true}));
                ta.dispatchEvent(new Event('change', {bubbles: true}));
            }""", plugin_content)
            print("[+] Content set via textarea")

        # ── Step 5: Click Update File ──────────────────────────────────────────
        print("[+] Looking for submit/update button...")

        # WP plugin editor has input[type=submit] with name="submit"
        # Try multiple selectors
        update_clicked = False
        for selector in [
            "input[name='submit']",
            "input[type='submit']",
            "button[type='submit']",
            "#submit",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible():
                    print(f"[+] Found update button with selector: {selector}")
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    update_clicked = True
                    break
            except Exception as e:
                continue

        if not update_clicked:
            print("[!] Could not find update button, trying JS submit...")
            page.evaluate("document.querySelector('form#template').submit()")

        print("[+] Waiting for response after submit...")
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(1)

        # Check result
        page_text = page.inner_text("body")
        current_url = page.url
        print(f"[+] Post-update URL: {current_url}")

        if "File edited successfully" in page_text:
            print("[+] SUCCESS: 'File edited successfully' message found!")
        elif "error" in page_text.lower() and "php" in page_text.lower():
            print(f"[!] PHP error detected in response: {page_text[:500]}")
        else:
            # Show first 300 chars of visible text for debugging
            print(f"[+] Page text snippet: {page_text[:300]}")

        # Check if there's a success notice
        try:
            notice = page.locator(".notice-success, #message.updated, .updated").first
            if notice.is_visible():
                print(f"[+] Success notice: {notice.inner_text()[:200]}")
        except Exception:
            pass

        browser.close()

    # ── Step 6: Verify deployment ──────────────────────────────────────────────
    print(f"\n[+] Verifying deployment by fetching {VERIFY_URL} ...")
    import urllib.request
    import ssl

    # Try with cache buster
    verify_url_nocache = VERIFY_URL + "?nocache=" + str(int(time.time()))
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        verify_url_nocache,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Cache-Control": "no-cache, no-store",
            "Pragma": "no-cache",
        }
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    if STYLE_ID in html:
        print(f"[+] VERIFIED: Style tag '{STYLE_ID}' found in page source.")
        # Show the actual CSS snippet
        idx = html.find(STYLE_ID)
        print(f"[+] Context: {html[max(0,idx-20):idx+200]}")
        return True
    else:
        print(f"[!] VERIFICATION FAILED: Style tag '{STYLE_ID}' NOT found in page source.")
        # Show what purebrain-blog styles ARE there
        idx = html.find("purebrain-blog")
        while idx >= 0:
            print(f"    Found at {idx}: {html[idx:idx+60]}")
            idx = html.find("purebrain-blog", idx + 1)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
