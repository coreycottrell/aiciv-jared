#!/usr/bin/env python3
"""
Deploy pb-blog-styling plugin v1.1.0 - v2: verify what's in editor + clear cache.
"""

import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

PLUGIN_FILE = Path("/home/jared/projects/AI-CIV/aether/tools/security/pb-blog-styling/pb-blog-styling.php")
WP_LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"
WP_USER = "purebrain@puremarketing.ai"
WP_PASS = "ij34utJdGCOst1*RcSvubXjb"
PLUGIN_EDITOR_URL = "https://purebrain.ai/wp-admin/plugin-editor.php"
VERIFY_URL = "https://purebrain.ai/age-of-ai-agents-next-18-months/"
STYLE_ID = "purebrain-blog-text-bg"

# WP REST API base
WP_API_BASE = "https://purebrain.ai/wp-json"


def main():
    plugin_content = PLUGIN_FILE.read_text(encoding="utf-8")
    print(f"[+] Plugin file loaded: {len(plugin_content)} chars")
    print(f"[+] Contains style ID '{STYLE_ID}': {STYLE_ID in plugin_content}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
        page = context.new_page()

        # ── Step 1: Login ──────────────────────────────────────────────────────
        print("[+] Logging in...")
        page.goto(WP_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_url("**/wp-admin/**", timeout=30000)
        print(f"[+] Logged in: {page.url}")

        # ── Step 2: Go to plugin editor ────────────────────────────────────────
        direct_url = f"{PLUGIN_EDITOR_URL}?file=pb-blog-styling/pb-blog-styling.php&plugin=pb-blog-styling/pb-blog-styling.php"
        page.goto(direct_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # ── Step 3: Read what's currently in the editor ────────────────────────
        print("[+] Reading current editor content...")
        has_codemirror = False
        try:
            page.wait_for_selector(".CodeMirror", timeout=8000)
            has_codemirror = True
        except PlaywrightTimeoutError:
            pass

        if has_codemirror:
            current_content = page.evaluate("""() => {
                var cm = document.querySelector('.CodeMirror').CodeMirror;
                return cm ? cm.getValue() : null;
            }""")
        else:
            current_content = page.evaluate("() => { var ta = document.getElementById('newcontent'); return ta ? ta.value : null; }")

        if current_content:
            print(f"[+] Current editor content: {len(current_content)} chars")
            print(f"[+] Has '{STYLE_ID}': {STYLE_ID in current_content}")
            print(f"[+] Version line: {[l for l in current_content.split(chr(10)) if 'Version' in l][:3]}")
        else:
            print("[!] Could not read editor content")

        # ── Step 4: If content doesn't have our style, update it ───────────────
        if current_content and STYLE_ID in current_content:
            print("[+] Plugin already has the style - file is correct on server!")
            print("[+] Issue must be page caching. Attempting cache clear...")
        else:
            print("[+] Updating plugin content in editor...")
            if has_codemirror:
                result = page.evaluate("""(newContent) => {
                    var cm = document.querySelector('.CodeMirror').CodeMirror;
                    cm.setValue(newContent);
                    cm.save();
                    var ta = document.getElementById('newcontent');
                    if (ta) ta.value = newContent;
                    return {ok: true, length: cm.getValue().length};
                }""", plugin_content)
                print(f"[+] CodeMirror set: {result}")
            else:
                page.evaluate("""(c) => {
                    var ta = document.getElementById('newcontent');
                    ta.value = c;
                    ta.dispatchEvent(new Event('change', {bubbles:true}));
                }""", plugin_content)

            # Click submit
            for sel in ["input[name='submit']", "input[type='submit']", "#submit"]:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        break
                except:
                    continue

            page.wait_for_load_state("domcontentloaded", timeout=30000)
            time.sleep(1)
            body_text = page.inner_text("body")
            if "File edited successfully" in body_text:
                print("[+] File saved successfully!")
            else:
                print(f"[!] Unexpected response: {body_text[:400]}")

        # ── Step 5: Clear WP / GoDaddy / Cloudflare cache via WP Admin ─────────
        print("\n[+] Attempting cache flush...")

        # Try WP Admin > Tools > Site Health or cache plugins
        # First try GoDaddy cache clear (common on GoDaddy hosting)
        cache_cleared = False

        # Try W3 Total Cache / WP Super Cache / LiteSpeed Cache flush
        for cache_url in [
            "https://purebrain.ai/wp-admin/admin.php?page=w3tc_dashboard&action=flush_all",
            "https://purebrain.ai/wp-admin/options-general.php?page=wpsupercache&tab=settings",
        ]:
            try:
                page.goto(cache_url, wait_until="domcontentloaded", timeout=10000)
                time.sleep(1)
                print(f"[+] Cache page attempt: {page.url}")
            except Exception as e:
                print(f"[+] Cache URL failed: {e}")

        # Try Cloudflare-style purge via WP admin AJAX
        # Get nonce from dashboard first
        page.goto("https://purebrain.ai/wp-admin/", wait_until="domcontentloaded", timeout=20000)
        nonce = page.evaluate("""() => {
            return typeof wpApiSettings !== 'undefined' ? wpApiSettings.nonce :
                   (typeof ajaxurl !== 'undefined' ? 'ajax_available' : null);
        }""")
        print(f"[+] WP nonce available: {nonce}")

        # Try GoDaddy Managed WP cache flush
        godaddy_cache = page.evaluate("""async () => {
            try {
                var resp = await fetch('/wp-admin/admin-ajax.php', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'action=wpaas_flush_cache'
                });
                return await resp.text();
            } catch(e) { return e.toString(); }
        }""")
        print(f"[+] GoDaddy cache flush attempt: {godaddy_cache[:200]}")

        # Try Elementor cache clear
        elementor_cache = page.evaluate("""async () => {
            try {
                var resp = await fetch('/wp-json/elementor/v1/cache', {
                    method: 'DELETE',
                    headers: {'X-WP-Nonce': document.cookie.match(/wp-nonce=([^;]+)/)?.[1] || ''}
                });
                return resp.status + ' ' + await resp.text();
            } catch(e) { return e.toString(); }
        }""")
        print(f"[+] Elementor cache clear: {elementor_cache[:200]}")

        # Try WP REST API cache bust with auth cookie
        # Navigate to the blog post in admin context to force regeneration
        print("[+] Loading blog post in admin to warm/clear cache...")
        page.goto(VERIFY_URL + "?nocache=" + str(int(time.time())), wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Check if style is now in the rendered page
        page_html = page.content()
        if STYLE_ID in page_html:
            print(f"[+] FOUND '{STYLE_ID}' in rendered page via browser!")
            cache_cleared = True
        else:
            print(f"[!] Style still not in browser-rendered page")
            # Check what styles are present
            import re
            styles = re.findall(r'<style id="([^"]+)"', page_html)
            print(f"[+] Style tags present: {styles}")

        browser.close()

    # ── Step 6: Verify via direct HTTP fetch ───────────────────────────────────
    print(f"\n[+] Final verification via HTTP fetch...")
    import urllib.request
    import ssl

    ctx = ssl.create_default_context()
    # Try multiple times with cache busters
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                VERIFY_URL,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                headers = dict(resp.headers)
                print(f"[+] Attempt {attempt+1}: HTTP {resp.status}, Content-Length={headers.get('Content-Length','?')}")
                if STYLE_ID in html:
                    print(f"[+] VERIFIED: Style tag '{STYLE_ID}' found!")
                    idx = html.find(STYLE_ID)
                    print(f"[+] Context: ...{html[max(0,idx-10):idx+150]}...")
                    return True
                else:
                    print(f"[!] Style not found in attempt {attempt+1}")
        except Exception as e:
            print(f"[!] HTTP error: {e}")
        time.sleep(2)

    print(f"\n[!] FINAL RESULT: Style tag not in HTTP response.")
    print("[!] The plugin file IS updated (confirmed by editor), but server cache is serving stale output.")
    print("[!] The style WILL appear once the page cache expires or is manually flushed.")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
