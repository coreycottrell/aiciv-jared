#!/usr/bin/env python3
"""
Focused test: pricing section + PayPal button on pay-test page.
"""

import time
from playwright.sync_api import sync_playwright

PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            args=[
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--disable-blink-features=AutomationControlled",
            ],
            headless=True,
        )
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        )
        page = ctx.new_page()

        print("Loading pay-test...")
        page.goto("https://purebrain.ai/pay-test/#awakening", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        # Enter page password
        pw_input = page.query_selector('input[type="password"]')
        if pw_input and pw_input.is_visible():
            pw_input.fill(PAGE_PASSWORD)
            submit = page.query_selector('input[type="submit"]')
            if submit:
                submit.click()
            time.sleep(8)

        # Scroll to chat
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight * 0.2)")
        time.sleep(2)

        # Click Begin Awakening
        begin = page.query_selector(".chat-initial__btn")
        if begin:
            begin.click()
            time.sleep(3)

        # Send bypass
        chat = page.query_selector("#userInput")
        if chat and chat.is_visible():
            chat.click()
            chat.fill("pb-full-bypass")
            page.keyboard.press("Enter")
            print("Bypass sent - waiting 15s...")
            time.sleep(15)

        # Click Discover
        discover = page.query_selector(".chat-cta__btn")
        if discover and discover.is_visible():
            discover.click()
            print("Discover clicked - waiting 20s for Keen to talk...")
            time.sleep(20)
        else:
            print("Discover not visible - checking text...")
            print(page.evaluate("() => document.body.innerText")[:500])

        # Screenshot current state
        page.screenshot(path=f"{SCREENSHOTS_DIR}/PRICING_01_after_discover.png")
        print("Screenshot: PRICING_01_after_discover.png")

        # Get parent chain of pricing-section to understand why it's hidden
        parent_chain = page.evaluate("""
            () => {
                const section = document.querySelector('.pricing-section');
                if (!section) return 'NO PRICING SECTION';
                let el = section;
                let chain = [];
                let depth = 0;
                while (el && el !== document.body && depth < 15) {
                    const cs = window.getComputedStyle(el);
                    chain.push({
                        tag: el.tagName,
                        id: el.id || '',
                        cls: el.className.substring(0, 40),
                        display: cs.display,
                        visibility: cs.visibility,
                        height: cs.height,
                        overflow: cs.overflow,
                        opacity: cs.opacity,
                    });
                    el = el.parentElement;
                    depth++;
                }
                return chain;
            }
        """)
        print("Pricing section parent chain:")
        if isinstance(parent_chain, list):
            for item in parent_chain:
                print(f"  {item}")
        else:
            print(f"  {parent_chain}")

        # Force-show pricing section by making all ancestors visible
        page.evaluate("""
            () => {
                const section = document.querySelector('.pricing-section');
                if (!section) return;
                let el = section;
                let depth = 0;
                while (el && el !== document.body && depth < 15) {
                    el.style.display = 'block';
                    el.style.visibility = 'visible';
                    el.style.opacity = '1';
                    el.style.height = 'auto';
                    el.style.maxHeight = 'none';
                    el.style.overflow = 'visible';
                    el.style.position = 'relative';
                    el = el.parentElement;
                    depth++;
                }
                // Also scroll to it
                section.scrollIntoView({block: 'start'});
            }
        """)
        time.sleep(1)

        page.screenshot(path=f"{SCREENSHOTS_DIR}/PRICING_02_forced_visible.png")
        print("Screenshot: PRICING_02_forced_visible.png")

        # Get pricing card info
        pricing_cards = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('.pricing-card')).map(c => {
                    const nameEl = c.querySelector('.pricing-card__name');
                    const priceEl = c.querySelector('.pricing-card__price, .price, [class*=price]');
                    const ctaEl = c.querySelector('.pricing-card__cta');
                    const badgeEl = c.querySelector('.pricing-card__badge');
                    return {
                        name: nameEl ? nameEl.innerText.trim() : '',
                        price: priceEl ? priceEl.innerText.trim() : '',
                        cta: ctaEl ? ctaEl.innerText.trim() : '',
                        popular: badgeEl ? badgeEl.innerText.trim() : '',
                        full_text: c.innerText.substring(0, 200),
                        cta_visible: ctaEl ? ctaEl.offsetParent !== null : false,
                    };
                });
            }
        """)
        print("\nPricing card details:")
        for card in pricing_cards:
            print(f"  {card}")

        # Check for PayPal-related HTML
        paypal_in_html = page.evaluate("""
            () => {
                const html = document.body.innerHTML.toLowerCase();
                const checks = {
                    paypal_sdk: html.includes('paypal.com/sdk'),
                    paypal_button: html.includes('paypal-button') || html.includes('paypalButton'),
                    paypal_container: !!document.querySelector('.paypal-button-container, [id*=paypal]'),
                    subscription_id: html.includes('P-1AG9360') || html.includes('P-2SA6560'),
                };
                return checks;
            }
        """)
        print(f"\nPayPal in HTML: {paypal_in_html}")

        # Try clicking first CTA via JS (bypasses visibility check)
        print("\nClicking first pricing CTA via JS...")
        page.evaluate("""
            () => {
                const btn = document.querySelector('.pricing-card__cta');
                if (btn) {
                    // Make it visible first
                    btn.style.display = 'block';
                    btn.style.visibility = 'visible';
                    btn.style.opacity = '1';
                    btn.click();
                    return 'clicked: ' + btn.innerText;
                }
                return 'no button found';
            }
        """)
        print("Waiting 10s for PayPal modal...")
        time.sleep(10)

        page.screenshot(path=f"{SCREENSHOTS_DIR}/PRICING_03_paypal_attempt.png")
        print("Screenshot: PRICING_03_paypal_attempt.png")

        paypal_result = page.evaluate("""
            () => {
                // Check for PayPal iframes
                const iframes = Array.from(document.querySelectorAll('iframe'));
                for (const f of iframes) {
                    if (f.src && f.src.includes('paypal')) return 'paypal iframe: ' + f.src.substring(0, 100);
                }
                // Check for paypal elements
                const ppEl = document.querySelector('.paypal-button-container, [id*=paypal], [class*=paypal]');
                if (ppEl) return 'paypal element found: ' + ppEl.className.substring(0, 80);
                // Check for visible modals
                const modals = Array.from(document.querySelectorAll('.modal, .overlay, [class*=modal], [class*=popup]'));
                for (const m of modals) {
                    if (m.offsetParent !== null) return 'modal visible: ' + m.className.substring(0, 60);
                }
                // Check text
                const body = document.body.innerHTML.toLowerCase();
                if (body.includes('paypal')) return 'paypal text in DOM';
                return 'PayPal NOT detected';
            }
        """)
        print(f"PayPal result: {paypal_result}")

        # Get the full text to see what modal appeared if any
        modal_text = page.evaluate("""
            () => {
                const modals = document.querySelectorAll('.modal, [class*=modal], [class*=popup], [class*=dialog], [class*=overlay]');
                const visible = Array.from(modals).filter(m => m.offsetParent !== null);
                return visible.length > 0 ? visible[0].innerText.substring(0, 300) : 'no visible modal';
            }
        """)
        print(f"Modal text: {modal_text}")

        browser.close()
        print("\nDone.")


if __name__ == "__main__":
    main()
