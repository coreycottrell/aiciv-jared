#!/usr/bin/env python3
"""
Second exploration: from bypass chat through to sandbox simulate button and post-payment flow
"""

import time
import json
from playwright.sync_api import sync_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_BASE = "/home/jared/projects/AI-CIV/aether/exports/screenshots"

def ss(page, name, full_page=False):
    try:
        page.screenshot(path=f"{SCREENSHOT_BASE}/ex2_{name}.png", full_page=full_page)
        print(f"[SS] ex2_{name}.png")
    except Exception as e:
        print(f"[SS FAIL] {e}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()

    page.goto(PAGE_URL, timeout=60000, wait_until='domcontentloaded')
    time.sleep(4)
    page.fill('input[name="post_password"]', PAGE_PASSWORD)
    page.click('input[type="submit"]')
    time.sleep(7)
    ss(page, "01_after_password", full_page=True)

    # Step 1: Click Begin Awakening
    page.click('.chat-initial__btn')
    time.sleep(4)
    ss(page, "02_after_begin")

    # Step 2: Type bypass code
    page.evaluate("""
        var input = document.getElementById('userInput');
        var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeSetter.call(input, 'pb-full-bypass');
        input.dispatchEvent(new Event('input', {bubbles: true}));
        document.getElementById('submitBtn').click();
    """)
    time.sleep(5)
    ss(page, "03_after_bypass")

    # Check for Discover button
    discover_btns = page.evaluate("""
        () => {
            var btns = Array.from(document.querySelectorAll('button, .btn, [role="button"]'));
            return btns.filter(function(b) {
                return b.innerText.toLowerCase().includes('discover') ||
                       b.innerText.toLowerCase().includes('keen can do');
            }).map(function(b) {
                return {text: b.innerText.substring(0, 60), id: b.id, class: b.className.substring(0, 60), visible: b.offsetParent !== null};
            });
        }
    """)
    print(f"[DISCOVER BUTTONS] {json.dumps(discover_btns, indent=2)}")

    # Click Discover
    result = page.evaluate("""
        () => {
            var btns = Array.from(document.querySelectorAll('button, .btn, [class*="discover"]'));
            var btn = btns.find(function(b) {
                return b.innerText.toLowerCase().includes('discover') ||
                       b.innerText.toLowerCase().includes('keen can do');
            });
            if (btn) {
                btn.click();
                return 'CLICKED: ' + btn.innerText.substring(0, 50);
            }
            return 'NOT FOUND';
        }
    """)
    print(f"[DISCOVER CLICK] {result}")
    time.sleep(5)
    ss(page, "04_after_discover", full_page=True)

    # Check for pricing section and sandbox button
    pricing_check = page.evaluate("""
        () => {
            var pricingSection = document.querySelector('.pricing-section, #pricing, [class*="pricing"]');
            var sandboxBtn = document.getElementById('pb-sandbox-bypass-btn');
            var paypalOverlay = document.getElementById('pb-paypal-overlay');
            var currentTier = window.currentTier;

            return {
                pricingVisible: pricingSection ? pricingSection.offsetParent !== null : false,
                sandboxBtnExists: !!sandboxBtn,
                sandboxBtnVisible: sandboxBtn ? sandboxBtn.offsetParent !== null : false,
                sandboxBtnText: sandboxBtn ? sandboxBtn.innerText : null,
                paypalOverlayExists: !!paypalOverlay,
                paypalOverlayVisible: paypalOverlay ? paypalOverlay.offsetParent !== null : false,
                currentTier: currentTier,
                windowPbState: window._pbState ? JSON.stringify(window._pbState).substring(0, 200) : null
            };
        }
    """)
    print(f"[PRICING CHECK] {json.dumps(pricing_check, indent=2)}")

    # Now try clicking a pricing CTA to open PayPal overlay (which shows sandbox button)
    pricing_cta_result = page.evaluate("""
        () => {
            // Try the Pro CTA
            var proCta = document.getElementById('proCta');
            if (proCta) {
                proCta.click();
                return 'CLICKED proCta';
            }
            // Try any pricing CTA
            var ctas = document.querySelectorAll('.pricing-card__cta');
            if (ctas.length > 0) {
                ctas[0].click();
                return 'CLICKED pricing CTA';
            }
            // Try "Activate Now" button
            var btns = Array.from(document.querySelectorAll('button'));
            var btn = btns.find(function(b) {
                return b.innerText.toLowerCase().includes('activate') ||
                       b.innerText.toLowerCase().includes('get started');
            });
            if (btn) {
                btn.click();
                return 'CLICKED: ' + btn.innerText.substring(0, 40);
            }
            return 'NO PRICING CTA FOUND';
        }
    """)
    print(f"[PRICING CTA CLICK] {pricing_cta_result}")
    time.sleep(4)
    ss(page, "05_after_pricing_click", full_page=True)

    # Check for PayPal overlay and sandbox button
    overlay_check = page.evaluate("""
        () => {
            var overlay = document.getElementById('pb-paypal-overlay');
            var sandboxBtn = document.getElementById('pb-sandbox-bypass-btn');
            var overlayHTML = overlay ? overlay.innerHTML.substring(0, 500) : 'NOT FOUND';
            return {
                overlayVisible: overlay ? overlay.offsetParent !== null : false,
                overlayDisplay: overlay ? overlay.style.display : 'N/A',
                sandboxBtnExists: !!sandboxBtn,
                sandboxBtnVisible: sandboxBtn ? sandboxBtn.offsetParent !== null : false,
                sandboxBtnText: sandboxBtn ? sandboxBtn.innerText : null,
                overlayHTML: overlayHTML
            };
        }
    """)
    print(f"[OVERLAY CHECK] {json.dumps(overlay_check, indent=2)}")

    # If sandbox button exists, click it
    if overlay_check.get('sandboxBtnExists'):
        sb_result = page.evaluate("""
            () => {
                var btn = document.getElementById('pb-sandbox-bypass-btn');
                if (btn) {
                    btn.click();
                    return 'CLICKED sandbox button';
                }
                return 'NOT FOUND';
            }
        """)
        print(f"[SANDBOX BTN CLICK] {sb_result}")
        time.sleep(5)
        ss(page, "06_after_sandbox_click", full_page=True)

        # Check for post-payment chat
        post_payment = page.evaluate("""
            () => {
                var pp = document.querySelector('.post-payment-overlay, #pay-test-post-payment, [id*="post-payment"]');
                var textarea = document.querySelector('textarea');
                var chatMsgs = document.querySelectorAll('[class*="message"]');
                return {
                    postPaymentElExists: !!pp,
                    postPaymentVisible: pp ? pp.offsetParent !== null : false,
                    textareaExists: !!textarea,
                    textareaVisible: textarea ? textarea.offsetParent !== null : false,
                    chatMsgCount: chatMsgs.length,
                    visibleText: document.body.innerText.substring(0, 800)
                };
            }
        """)
        print(f"[POST PAYMENT STATE] {json.dumps(post_payment, indent=2)}")
    else:
        print("[WARNING] Sandbox button not found - trying direct __pbPaymentYes with tier set")
        # Try setting tier and calling payment yes
        result2 = page.evaluate("""
            () => {
                window.currentTier = 'bonded';
                if (typeof window.__pbPaymentYes === 'function') {
                    window.__pbPaymentYes();
                    return 'CALLED __pbPaymentYes with tier bonded';
                }
                if (typeof window.onPaymentComplete === 'function') {
                    window.onPaymentComplete('bonded', 'SANDBOX-TEST-123', {email_address: 'test@test.com', name: {given_name: 'Test', surname: 'User'}});
                    return 'CALLED onPaymentComplete';
                }
                return 'NO PAYMENT FUNCTIONS FOUND';
            }
        """)
        print(f"[PAYMENT SIM] {result2}")
        time.sleep(5)
        ss(page, "06_after_payment_sim", full_page=True)

        # Final state check
        final_state = page.evaluate("""
            () => {
                var textarea = document.querySelector('textarea');
                return {
                    textareaExists: !!textarea,
                    textareaVisible: textarea ? textarea.offsetParent !== null : false,
                    visibleText: document.body.innerText.substring(0, 1000)
                };
            }
        """)
        print(f"[FINAL STATE] {json.dumps(final_state, indent=2)}")

    browser.close()
    print("\n[DONE]")
