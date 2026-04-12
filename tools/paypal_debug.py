#!/usr/bin/env python3
"""Debug script to check Pure Brain 2.0 page structure"""

from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Login
        print("Logging in...")
        page.goto(WP_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        password_login_link = page.get_by_text("Log in with username and password")
        if password_login_link.count() > 0:
            password_login_link.click()
            page.wait_for_timeout(2000)

        if page.locator("#user_login").is_visible():
            page.fill("#user_login", WP_USER)
            page.fill("#user_pass", WP_PASS)
            page.click("#wp-submit")
            try:
                page.wait_for_url("**/wp-admin/**", timeout=15000)
            except:
                pass
            page.wait_for_timeout(3000)

        print(f"Logged in: {page.url}")

        # Get page info via API
        print("\n=== Page 174 (Pure Brain 2.0) Info ===")
        result = page.evaluate('''
            async () => {
                const nonce = window.wpApiSettings?.nonce;
                if (!nonce) return { error: 'No nonce' };

                const resp = await fetch('/wp-json/wp/v2/pages/174', {
                    headers: { 'X-WP-Nonce': nonce }
                });

                if (!resp.ok) return { error: resp.status };

                const data = await resp.json();
                return {
                    id: data.id,
                    title: data.title.rendered,
                    slug: data.slug,
                    status: data.status,
                    template: data.template,
                    content_length: (data.content.raw || data.content.rendered || '').length,
                    has_paypal: (data.content.raw || data.content.rendered || '').includes('paypal'),
                    content_type: data.content.raw ? 'raw' : 'rendered',
                    content_sample: (data.content.raw || data.content.rendered || '').substring(0, 500)
                };
            }
        ''')
        print(f"Result: {result}")

        # List all pages to see structure
        print("\n=== All Pages ===")
        pages = page.evaluate('''
            async () => {
                const nonce = window.wpApiSettings?.nonce;
                if (!nonce) return [];

                const resp = await fetch('/wp-json/wp/v2/pages?per_page=50', {
                    headers: { 'X-WP-Nonce': nonce }
                });

                if (!resp.ok) return [];

                const data = await resp.json();
                return data.map(p => ({
                    id: p.id,
                    title: p.title.rendered,
                    slug: p.slug,
                    status: p.status,
                    template: p.template
                }));
            }
        ''')

        for p_info in pages:
            print(f"  [{p_info['id']:4}] {p_info['status']:10} | {p_info['slug']:30} | {p_info['title']}")

        # Check if the page uses Elementor data
        print("\n=== Checking for Elementor ===")
        elementor_check = page.evaluate('''
            async () => {
                const nonce = window.wpApiSettings?.nonce;
                if (!nonce) return { error: 'No nonce' };

                const resp = await fetch('/wp-json/wp/v2/pages/174', {
                    headers: { 'X-WP-Nonce': nonce }
                });

                const data = await resp.json();
                return {
                    meta_keys: Object.keys(data.meta || {}),
                    has_elementor_data: data.meta?._elementor_data ? true : false,
                    content_raw_exists: !!data.content?.raw,
                    rendered_exists: !!data.content?.rendered
                };
            }
        ''')
        print(f"Elementor check: {elementor_check}")

        # Check actual front-end for paypal forms
        print("\n=== Front-end Check ===")
        page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # Get page source
        html = page.content()
        has_paypal_in_source = 'paypal.com' in html
        print(f"PayPal in page source: {has_paypal_in_source}")

        if has_paypal_in_source:
            # Find where it is
            idx = html.find('paypal.com')
            print(f"Found at index {idx}")
            print(f"Context: ...{html[max(0,idx-100):idx+200]}...")

        browser.close()

if __name__ == "__main__":
    main()
