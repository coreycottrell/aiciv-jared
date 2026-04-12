#!/usr/bin/env python3
"""
Flush all caches on purebrain.ai to force new plugin code to take effect.
"""
import time
import json
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

        # Login
        print("[+] Logging in...")
        page.goto(WP_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_url("**/wp-admin/**", timeout=30000)
        print(f"[+] Logged in")

        # Get nonce
        page.goto("https://purebrain.ai/wp-admin/", wait_until="domcontentloaded", timeout=20000)
        nonce = page.evaluate("() => typeof wpApiSettings !== 'undefined' ? wpApiSettings.nonce : ''")
        print(f"[+] WP API nonce: {nonce[:20]}...")

        # Method 1: Try GoDaddy Managed WP cache (wpaas)
        print("\n[+] Method 1: GoDaddy wpaas cache flush...")
        result = page.evaluate("""async () => {
            var formData = new FormData();
            formData.append('action', 'wpaas_flush_cache');
            formData.append('_ajax_nonce', document.querySelector('#_wpnonce') ?
                document.querySelector('#_wpnonce').value : '');
            var resp = await fetch('/wp-admin/admin-ajax.php', {
                method: 'POST',
                body: formData
            });
            return {status: resp.status, text: await resp.text()};
        }""")
        print(f"[+] wpaas result: {result}")

        # Method 2: WordPress Transient / Object Cache flush
        print("\n[+] Method 2: WP REST API cache endpoint...")
        result2 = page.evaluate("""async (nonce) => {
            var resp = await fetch('/wp-json/wp/v2/settings', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: resp.status};
        }""", nonce)
        print(f"[+] REST API auth check: {result2}")

        # Method 3: Navigate to PHP info or trigger revalidation
        # Try Autoptimize if present
        print("\n[+] Method 3: Autoptimize cache clear...")
        page.goto("https://purebrain.ai/wp-admin/options-general.php?page=autoptimize", timeout=10000)
        try:
            page.click("input[name='deletecache']", timeout=3000)
            time.sleep(1)
            print("[+] Autoptimize cache clear clicked")
        except:
            print("[+] Autoptimize not present")

        # Method 4: WP Fastest Cache
        print("\n[+] Method 4: WP Fastest Cache...")
        page.goto("https://purebrain.ai/wp-admin/admin.php?page=WpFastestCacheOptions&tab=deleteCache", timeout=10000)
        time.sleep(1)
        print(f"[+] WP Fastest Cache URL: {page.url}")

        # Method 5: Try to bust via a PHP snippet through Plugin Editor
        # Create a tiny temp plugin that calls wp_cache_flush() and opcache_reset()
        print("\n[+] Method 5: Deploy cache-busting snippet via plugin editor...")

        # Use the pb-blog-styling plugin itself - add a cache flush trigger at top
        # Actually let's try a smarter approach: use the WP Admin > Tools > Site Health
        page.goto("https://purebrain.ai/wp-admin/site-health.php", wait_until="domcontentloaded", timeout=20000)
        print(f"[+] Site Health page loaded")

        # Method 6: Deactivate and reactivate the plugin
        print("\n[+] Method 6: Deactivate/reactivate pb-blog-styling plugin...")
        page.goto("https://purebrain.ai/wp-admin/plugins.php", wait_until="domcontentloaded", timeout=20000)
        time.sleep(1)

        # Find the deactivate link for pb-blog-styling
        deactivate_link = page.locator("tr[data-slug='pb-blog-styling'] a:has-text('Deactivate')")
        try:
            if deactivate_link.is_visible(timeout=3000):
                deactivate_href = deactivate_link.get_attribute("href")
                print(f"[+] Deactivate link found: {deactivate_href[:80]}...")
                deactivate_link.click()
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                time.sleep(1)
                print(f"[+] Plugin deactivated. URL: {page.url}")

                # Now reactivate
                activate_link = page.locator("tr[data-slug='pb-blog-styling'] a:has-text('Activate')")
                if activate_link.is_visible(timeout=3000):
                    activate_link.click()
                    page.wait_for_load_state("domcontentloaded", timeout=15000)
                    time.sleep(1)
                    print(f"[+] Plugin reactivated!")
                else:
                    print("[!] Could not find Activate link after deactivation")
            else:
                print("[!] Deactivate link not visible - plugin may not be active or slug differs")
                # Show all plugin rows
                rows = page.locator("table.plugins tr[data-slug]")
                count = rows.count()
                for i in range(min(count, 20)):
                    slug = rows.nth(i).get_attribute("data-slug")
                    print(f"    Plugin slug: {slug}")
        except Exception as e:
            print(f"[!] Deactivate/reactivate error: {e}")

        # Now load the blog post page and check
        print("\n[+] Loading blog post page to check...")
        page.goto(VERIFY_URL + "?cachebust=" + str(int(time.time())), wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        page_html = page.content()

        if STYLE_ID in page_html:
            print(f"[+] SUCCESS: '{STYLE_ID}' found in page!")
            import re
            idx = page_html.find(STYLE_ID)
            print(f"[+] Context: {page_html[max(0,idx-20):idx+200]}")
        else:
            print(f"[!] Still not found. Checking all pb- styles present:")
            import re
            styles = re.findall(r'<style id="([^"]+)"', page_html)
            pb_styles = [s for s in styles if 'pb' in s or 'purebrain' in s]
            print(f"    PB styles: {pb_styles}")

        browser.close()

    # Final HTTP check
    print("\n[+] Final HTTP verification...")
    import urllib.request, ssl
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        VERIFY_URL,
        headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    if STYLE_ID in html:
        print(f"[+] HTTP VERIFIED: '{STYLE_ID}' in page source!")
        return True
    else:
        print(f"[!] Still not in HTTP response - caching is aggressive")
        return False


if __name__ == "__main__":
    success = main()
    print(f"\n[+] Result: {'SUCCESS' if success else 'NEEDS CACHE FLUSH'}")
