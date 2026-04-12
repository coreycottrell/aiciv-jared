#!/usr/bin/env python3
"""
Third exploration: after sandbox click, investigate why post-payment overlay is invisible
and try to force it visible / interact via JS.
"""

import time
import json
from playwright.sync_api import sync_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_BASE = "/home/jared/projects/AI-CIV/aether/exports/screenshots"

def ss(page, name, full_page=False):
    try:
        page.screenshot(path=f"{SCREENSHOT_BASE}/ex3_{name}.png", full_page=full_page)
        print(f"[SS] ex3_{name}.png")
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

    # Step 1: Begin Awakening + bypass
    page.click('.chat-initial__btn')
    time.sleep(3)
    page.evaluate("""
        var input = document.getElementById('userInput');
        var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeSetter.call(input, 'pb-full-bypass');
        input.dispatchEvent(new Event('input', {bubbles: true}));
        document.getElementById('submitBtn').click();
    """)
    time.sleep(5)

    # Step 2: Click Activate Now (proCta)
    page.evaluate("document.getElementById('proCta').click()")
    time.sleep(4)

    # Verify sandbox button visible
    sandbox_visible = page.evaluate("!!document.getElementById('pb-sandbox-bypass-btn') && document.getElementById('pb-sandbox-bypass-btn').offsetParent !== null")
    print(f"Sandbox button visible: {sandbox_visible}")

    # Click sandbox button
    page.evaluate("document.getElementById('pb-sandbox-bypass-btn').click()")
    time.sleep(5)
    ss(page, "01_after_sandbox_click")

    # Inspect the post-payment element
    pp_info = page.evaluate("""
        () => {
            var pp = document.querySelector('#pay-test-post-payment, .post-payment-overlay, [id*="post-payment"]');
            if (!pp) return {found: false};

            var computedStyle = window.getComputedStyle(pp);
            return {
                found: true,
                id: pp.id,
                class: pp.className,
                display: computedStyle.display,
                visibility: computedStyle.visibility,
                opacity: computedStyle.opacity,
                zIndex: computedStyle.zIndex,
                position: computedStyle.position,
                offsetParent: pp.offsetParent !== null,
                parentInfo: pp.parentElement ? {id: pp.parentElement.id, class: pp.parentElement.className.substring(0, 80)} : null,
                outerHTMLPreview: pp.outerHTML.substring(0, 300),
                childCount: pp.children.length
            };
        }
    """)
    print(f"\n[POST PAYMENT ELEMENT INFO]")
    print(json.dumps(pp_info, indent=2))

    # Check all message elements in post-payment
    msg_info = page.evaluate("""
        () => {
            var pp = document.querySelector('#pay-test-post-payment, .post-payment-overlay');
            if (!pp) return {found: false};

            var msgs = pp.querySelectorAll('[class*="message"], [class*="msg"], .pb-message, p');
            var msgData = Array.from(msgs).slice(0, 10).map(function(m) {
                return {
                    class: m.className,
                    text: m.innerText.substring(0, 100),
                    visible: m.offsetParent !== null
                };
            });

            var textarea = pp.querySelector('textarea');
            var inputs = pp.querySelectorAll('textarea, input[type=text]');

            return {
                found: true,
                msgCount: msgs.length,
                msgs: msgData,
                hasTextarea: !!textarea,
                textareaPlaceholder: textarea ? textarea.placeholder : null,
                inputCount: inputs.length
            };
        }
    """)
    print(f"\n[POST PAYMENT MESSAGES]")
    print(json.dumps(msg_info, indent=2))

    # The problem: post-payment container is likely hidden by CSS
    # Let's force it visible and take a screenshot
    force_result = page.evaluate("""
        () => {
            var pp = document.querySelector('#pay-test-post-payment, .post-payment-overlay, [id*="post-payment"]');
            if (!pp) return 'NOT FOUND';

            // Force display
            pp.style.display = 'flex';
            pp.style.visibility = 'visible';
            pp.style.opacity = '1';
            pp.style.zIndex = '9999';

            // Also make body and html visible
            document.body.style.visibility = 'visible';
            document.body.style.opacity = '1';

            return 'FORCED VISIBLE: ' + pp.id + '.' + pp.className.substring(0, 50);
        }
    """)
    print(f"\n[FORCE VISIBLE] {force_result}")
    time.sleep(1)
    ss(page, "02_after_force_visible", full_page=True)

    # Check textarea now
    textarea_info = page.evaluate("""
        () => {
            var ta = document.querySelector('textarea');
            if (!ta) return {found: false};
            return {
                found: true,
                id: ta.id,
                class: ta.className,
                placeholder: ta.placeholder,
                visible: ta.offsetParent !== null,
                display: window.getComputedStyle(ta).display
            };
        }
    """)
    print(f"\n[TEXTAREA INFO] {json.dumps(textarea_info, indent=2)}")

    # Now try sending a message via JS evaluate
    print("\n--- Attempting to send a test message via JS ---")
    send_result = page.evaluate("""
        () => {
            var textarea = document.querySelector('textarea');
            if (!textarea) return 'NO TEXTAREA';

            // Try setting value and submitting
            var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            if (nativeSetter) {
                nativeSetter.call(textarea, 'Test User');
            } else {
                textarea.value = 'Test User';
            }
            textarea.dispatchEvent(new Event('input', {bubbles: true}));

            // Look for submit button
            var submitBtn = document.querySelector('button[type="submit"], button.pb-chat__submit, button.submit');
            if (submitBtn) {
                submitBtn.click();
                return 'SENT via ' + submitBtn.className;
            }

            // Try Enter key
            textarea.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13, bubbles: true}));
            textarea.dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter', keyCode: 13, bubbles: true}));
            textarea.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter', keyCode: 13, bubbles: true}));
            return 'SENT via Enter key';
        }
    """)
    print(f"[SEND RESULT] {send_result}")
    time.sleep(15)  # Wait for AI response
    ss(page, "03_after_message_sent", full_page=True)

    # Check message count
    msg_count_after = page.evaluate("""
        () => {
            var pp = document.querySelector('#pay-test-post-payment, .post-payment-overlay');
            if (!pp) {
                // Search whole page
                var msgs = document.querySelectorAll('[class*="message"]');
                return {context: 'whole page', count: msgs.length};
            }
            var msgs = pp.querySelectorAll('[class*="message"]');
            return {context: 'post-payment container', count: msgs.length, lastMsg: msgs[msgs.length - 1] ? msgs[msgs.length - 1].innerText.substring(0, 200) : null};
        }
    """)
    print(f"\n[MSG COUNT AFTER SEND] {json.dumps(msg_count_after, indent=2)}")

    # Get all text visible in post-payment area
    pp_text = page.evaluate("""
        () => {
            var pp = document.querySelector('#pay-test-post-payment, .post-payment-overlay');
            if (pp) return pp.innerText.substring(0, 2000);

            // fallback: search for post-payment related text
            var allEl = Array.from(document.querySelectorAll('[class*="post"], [class*="payment"]'));
            return allEl.map(function(e) { return e.innerText.substring(0, 200); }).join(' | ');
        }
    """)
    print(f"\n[POST PAYMENT TEXT] {pp_text[:1000]}")

    browser.close()
    print("\n[DONE]")
