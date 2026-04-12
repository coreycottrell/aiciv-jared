#!/usr/bin/env python3
"""Debug script to understand the pay-test-sandbox-2 page structure."""
import time
import json
from playwright.sync_api import sync_playwright

SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()

    print('Loading page...')
    page.goto('https://purebrain.ai/pay-test-sandbox-2/', timeout=30000)
    page.wait_for_load_state('domcontentloaded', timeout=15000)
    time.sleep(3)

    page.screenshot(path=f'{SS_DIR}/v3_debug_01_initial.png')

    pw_field = page.query_selector('input[name="post_password"]')
    print(f'Password field present: {pw_field is not None}')

    if pw_field:
        page.fill('input[name="post_password"]', 'PureBrain.ai253443$$')
        page.click('input[type="submit"]')
        print('Submitted password')
        time.sleep(8)

        print(f'URL after submit: {page.url}')
        print(f'Title: {page.title()}')

        page.screenshot(path=f'{SS_DIR}/v3_debug_02_after_pw.png', full_page=True)

        # Check DOM structure
        dom_info = page.evaluate("""
            () => {
                var info = {};
                info.pw_form_exists = document.querySelector('.post-password-form') !== null;
                info.entry_content = document.querySelector('.entry-content') !== null;
                info.elementor_exists = document.querySelector('.elementor') !== null;

                // Get all buttons
                var btns = document.querySelectorAll('button');
                info.buttons = [];
                for (var i = 0; i < btns.length; i++) {
                    info.buttons.push({
                        text: btns[i].innerText.trim().substring(0, 80),
                        id: btns[i].id,
                        classes: btns[i].className.substring(0, 100),
                        visible: btns[i].offsetParent !== null,
                        display: window.getComputedStyle(btns[i]).display
                    });
                }

                // Get all inputs
                var inputs = document.querySelectorAll('input,textarea');
                info.inputs = [];
                for (var i = 0; i < inputs.length; i++) {
                    info.inputs.push({
                        type: inputs[i].type,
                        name: inputs[i].name || '',
                        placeholder: inputs[i].placeholder || '',
                        id: inputs[i].id || '',
                        visible: inputs[i].offsetParent !== null
                    });
                }

                // Look for post-payment specific elements
                var ppElements = document.querySelectorAll('[id*="post-payment"], [class*="post-payment"], [id*="sandbox"], [class*="sandbox"]');
                info.pp_elements = [];
                for (var i = 0; i < ppElements.length; i++) {
                    info.pp_elements.push({
                        tag: ppElements[i].tagName,
                        id: ppElements[i].id,
                        classes: ppElements[i].className.substring(0, 100)
                    });
                }

                // Get scripts to understand what JS is loaded
                var scripts = document.querySelectorAll('script[src]');
                info.scripts = [];
                for (var i = 0; i < Math.min(scripts.length, 20); i++) {
                    var src = scripts[i].src;
                    if (src.includes('purebrain') || src.includes('paypal') || src.includes('custom')) {
                        info.scripts.push(src.substring(0, 100));
                    }
                }

                // Check body classes
                info.body_classes = document.body.className;

                // Get visible text
                info.visible_text_preview = document.body.innerText.substring(0, 500);

                return info;
            }
        """)

        print("\nDOM Info:")
        print(json.dumps(dom_info, indent=2))

        # Now try to scroll down and look for any hidden content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.screenshot(path=f'{SS_DIR}/v3_debug_03_scrolled_bottom.png')

        # Check for iframes
        iframes = page.query_selector_all('iframe')
        print(f"\nIframes found: {len(iframes)}")
        for frame in iframes:
            src = frame.get_attribute('src')
            print(f"  iframe src: {src}")

        # Try clicking the simulate payment button if it exists in the DOM (even if hidden)
        sim_btn_js = page.evaluate("""
            () => {
                // Search for simulate button in ALL elements including hidden
                var allElements = document.querySelectorAll('*');
                var found = [];
                for (var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    var text = el.innerText ? el.innerText.trim() : '';
                    if (text && text.length < 100 && (
                        text.toLowerCase().includes('simulate') ||
                        text.toLowerCase().includes('sandbox') ||
                        text.toLowerCase().includes('bypass') ||
                        (el.id && (el.id.includes('simulate') || el.id.includes('sandbox') || el.id.includes('payment')))
                    )) {
                        found.push({
                            tag: el.tagName,
                            id: el.id || '',
                            classes: el.className ? el.className.substring(0, 80) : '',
                            text: text.substring(0, 80),
                            display: window.getComputedStyle(el).display,
                            visibility: window.getComputedStyle(el).visibility,
                        });
                    }
                }
                return found;
            }
        """)
        print(f"\nSimulate/sandbox elements found: {json.dumps(sim_btn_js, indent=2)}")

        # Check what chatbot elements are in DOM
        chatbot_elements = page.evaluate("""
            () => {
                var selectors = [
                    '.chat-initial', '#chat-initial', '[class*="chat"]',
                    '.post-payment-overlay', '#post-payment-overlay',
                    '[id*="payment"]', '[class*="payment"]',
                    '.pb-chatbot', '#pb-chatbot',
                    '[class*="chatbot"]', '[id*="chatbot"]',
                    '.purebrain-chat', '#purebrain-chat',
                ];
                var results = {};
                for (var i = 0; i < selectors.length; i++) {
                    var sel = selectors[i];
                    var el = document.querySelector(sel);
                    if (el) {
                        results[sel] = {
                            display: window.getComputedStyle(el).display,
                            visibility: window.getComputedStyle(el).visibility,
                            opacity: window.getComputedStyle(el).opacity,
                            innerHTML_preview: el.innerHTML.substring(0, 200),
                        };
                    }
                }
                return results;
            }
        """)
        print(f"\nChatbot elements: {json.dumps(chatbot_elements, indent=2)}")

    browser.close()
    print("\nDebug complete. Screenshots saved.")
