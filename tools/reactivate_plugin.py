#!/usr/bin/env python3
"""
Deactivate and reactivate pb-blog-styling to bust PHP opcode cache.
"""
import sys, time, re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

WP_LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"
WP_USER = "purebrain@puremarketing.ai"
WP_PASS = "ij34utJdGCOst1*RcSvubXjb"
VERIFY_URL = "https://purebrain.ai/age-of-ai-agents-next-18-months/"
STYLE_ID = "purebrain-blog-text-bg"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # Login with longer timeout
        print("[+] Logging in...")
        page.goto(WP_LOGIN_URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_selector("#user_login", timeout=15000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        # Wait for either wp-admin or redirect
        try:
            page.wait_for_url("**/wp-admin/**", timeout=45000)
        except PlaywrightTimeoutError:
            # Check if we're logged in via URL check
            if "wp-admin" not in page.url and "dashboard" not in page.url:
                print(f"[!] Login may have failed, URL: {page.url}")
                page.wait_for_load_state("networkidle", timeout=15000)
                print(f"[+] Current URL after wait: {page.url}")
        print(f"[+] Post-login URL: {page.url}")

        # Go to plugins page
        print("[+] Going to plugins page...")
        page.goto("https://purebrain.ai/wp-admin/plugins.php", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Show all plugin slugs for debugging
        rows = page.locator("table.plugins tr[data-slug]")
        count = rows.count()
        print(f"[+] Found {count} plugin rows")
        all_slugs = []
        for i in range(count):
            slug = rows.nth(i).get_attribute("data-slug")
            all_slugs.append(slug)
        print(f"[+] Plugin slugs: {all_slugs}")

        # Find pb-blog-styling
        target_slug = "pb-blog-styling"
        if target_slug not in all_slugs:
            # Try partial match
            matches = [s for s in all_slugs if "blog-styling" in s or "blog_styling" in s]
            if matches:
                target_slug = matches[0]
                print(f"[+] Using matched slug: {target_slug}")
            else:
                print(f"[!] Plugin not found in list. Slugs: {all_slugs}")
                browser.close()
                return False

        # Deactivate
        deact = page.locator(f"tr[data-slug='{target_slug}'] .deactivate a, tr[data-slug='{target_slug}'] a:has-text('Deactivate')")
        try:
            if deact.first.is_visible(timeout=3000):
                print(f"[+] Deactivating {target_slug}...")
                deact.first.click()
                page.wait_for_load_state("domcontentloaded", timeout=20000)
                time.sleep(1)
                print(f"[+] Deactivated. URL: {page.url}")
            else:
                print(f"[!] Plugin may already be inactive or deactivate link not visible")
        except Exception as e:
            print(f"[!] Deactivate error: {e}")

        # Reactivate
        act = page.locator(f"tr[data-slug='{target_slug}'] .activate a, tr[data-slug='{target_slug}'] a:has-text('Activate')")
        try:
            if act.first.is_visible(timeout=3000):
                print(f"[+] Activating {target_slug}...")
                act.first.click()
                page.wait_for_load_state("domcontentloaded", timeout=20000)
                time.sleep(1)
                print(f"[+] Activated. URL: {page.url}")
            else:
                print(f"[!] Activate link not found after deactivation")
        except Exception as e:
            print(f"[!] Activate error: {e}")

        # Now check the blog post
        print(f"\n[+] Checking blog post: {VERIFY_URL}")
        page.goto(VERIFY_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        html = page.content()

        if STYLE_ID in html:
            print(f"[+] SUCCESS (browser): '{STYLE_ID}' found in rendered page!")
            idx = html.find(STYLE_ID)
            print(f"[+] Snippet: {html[max(0,idx-20):idx+200]}")
        else:
            pb_styles = re.findall(r'<style id="([^"]+)"', html)
            print(f"[!] Not found. PB styles present: {[s for s in pb_styles if 'pb' in s.lower() or 'purebrain' in s.lower()]}")

        browser.close()

    # HTTP verification
    print("\n[+] HTTP verification...")
    import urllib.request, ssl
    ctx = ssl.create_default_context()
    for i in range(3):
        try:
            req = urllib.request.Request(
                VERIFY_URL,
                headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}
            )
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            if STYLE_ID in body:
                print(f"[+] HTTP VERIFIED: '{STYLE_ID}' present!")
                return True
            else:
                print(f"[!] Attempt {i+1}: not in HTTP response")
        except Exception as e:
            print(f"[!] HTTP error: {e}")
        time.sleep(3)

    return False


if __name__ == "__main__":
    ok = main()
    print(f"\nResult: {'SUCCESS' if ok else 'CACHE ISSUE - plugin is updated but cache serving stale'}")
    sys.exit(0 if ok else 1)
