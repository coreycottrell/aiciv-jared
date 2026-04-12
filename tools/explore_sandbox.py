#!/usr/bin/env python3
"""
Exploration script to understand the sandbox-2 page structure.
This runs BEFORE the main test to find the simulate button and understand
the post-payment overlay mechanics.
"""

import time
import json
from playwright.sync_api import sync_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_BASE = "/home/jared/projects/AI-CIV/aether/exports/screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()

    page.goto(PAGE_URL, timeout=60000, wait_until='domcontentloaded')
    time.sleep(4)

    # Enter password
    pw = page.query_selector('input[name="post_password"]')
    if pw:
        page.fill('input[name="post_password"]', PAGE_PASSWORD)
        page.click('input[type="submit"]')
        time.sleep(7)
        print("[PASSWORD] Submitted")
    else:
        print("[PASSWORD] Not needed")

    # Screenshot after password
    page.screenshot(path=f"{SCREENSHOT_BASE}/explore_01_after_password.png", full_page=True)

    # Look for sandbox-specific elements
    sandbox_info = page.evaluate("""
        () => {
            var result = {};

            // Post-payment overlay
            var pp = document.querySelector('.post-payment-overlay, #postPaymentOverlay');
            result.postPaymentEl = pp ? {class: pp.className, id: pp.id, visible: pp.offsetParent !== null} : null;

            // Sandbox banner
            var sandboxBanner = document.querySelector('.sandbox-banner, [class*="sandbox"]');
            result.sandboxBanner = sandboxBanner ? sandboxBanner.innerText.substring(0, 200) : null;

            // Page title
            result.pageTitle = document.title;

            // All IDs that look relevant
            result.relevantIds = Array.from(document.querySelectorAll('[id]'))
                .map(function(e) { return e.id; })
                .filter(function(id) {
                    return id.includes('chat') || id.includes('payment') ||
                           id.includes('post') || id.includes('overlay') ||
                           id.includes('sandbox') || id.includes('simulate');
                });

            // JS window keys that look relevant
            result.windowKeys = Object.keys(window).filter(function(k) {
                return k.toLowerCase().includes('payment') ||
                       k.toLowerCase().includes('sandbox') ||
                       k.toLowerCase().includes('post') ||
                       k.toLowerCase().includes('simulate') ||
                       k.toLowerCase().includes('pb');
            }).slice(0, 30);

            // Chat initial state
            var chatInitial = document.querySelector('.chat-initial');
            result.chatInitial = chatInitial ? {
                display: chatInitial.style.display,
                offsetParent: chatInitial.offsetParent !== null
            } : null;

            // Top-level page sections
            var sections = Array.from(document.querySelectorAll('section, .section, [class*="section"]'))
                .map(function(s) { return {id: s.id, class: s.className.substring(0, 80)}; })
                .slice(0, 15);
            result.sections = sections;

            return result;
        }
    """)
    print(f"\n[SANDBOX INFO]")
    print(json.dumps(sandbox_info, indent=2))

    # Look at HTML source for sandbox-related JS
    html_source = page.content()
    # Search for simulate/sandbox keywords in source
    lines = html_source.split('\n')
    relevant_lines = [l for l in lines if any(kw in l.lower() for kw in ['simulat', 'sandbox', 'post-payment', 'postpayment'])]
    print(f"\n[RELEVANT HTML LINES] ({len(relevant_lines)} found)")
    for l in relevant_lines[:30]:
        print(f"  {l.strip()[:200]}")

    # Now click Begin Awakening to enter the chat
    begin_btns = page.query_selector_all('.chat-initial__btn')
    print(f"\n[BEGIN BUTTONS] Found: {len(begin_btns)}")

    if begin_btns:
        # Scroll to the Begin Awakening section first
        page.evaluate("document.querySelector('.chat-initial__btn').scrollIntoView()")
        time.sleep(1)
        page.screenshot(path=f"{SCREENSHOT_BASE}/explore_02_before_begin.png")
        page.click('.chat-initial__btn')
        time.sleep(5)
        page.screenshot(path=f"{SCREENSHOT_BASE}/explore_03_after_begin.png", full_page=True)

        # Check state after clicking
        after_begin = page.evaluate("""
            () => {
                return {
                    chatVisible: !!document.querySelector('.pb-chat, #pbChat'),
                    userInputVisible: !!document.querySelector('#userInput'),
                    postPaymentVisible: !!document.querySelector('.post-payment-overlay'),
                    simulateVisible: Array.from(document.querySelectorAll('button')).filter(function(b) {
                        return b.innerText.toLowerCase().includes('simulat') && b.offsetParent !== null;
                    }).map(function(b) { return b.innerText; }),
                    allVisibleButtons: Array.from(document.querySelectorAll('button')).filter(function(b) {
                        return b.offsetParent !== null;
                    }).map(function(b) { return b.innerText.substring(0, 50); })
                };
            }
        """)
        print(f"\n[AFTER BEGIN CLICK]")
        print(json.dumps(after_begin, indent=2))

    # Also look for any JS functions that handle sandbox simulation
    js_funcs = page.evaluate("""
        () => {
            var funcs = [];
            // Look for sandbox-related functions
            for (var key in window) {
                try {
                    if (typeof window[key] === 'function') {
                        var src = window[key].toString().substring(0, 100);
                        if (src.toLowerCase().includes('simulat') || src.toLowerCase().includes('sandbox') ||
                            src.toLowerCase().includes('payment') || key.toLowerCase().includes('simulat')) {
                            funcs.push({name: key, preview: src});
                        }
                    }
                } catch(e) {}
            }
            return funcs;
        }
    """)
    print(f"\n[JS FUNCTIONS WITH SANDBOX/SIMULATE] {len(js_funcs)} found")
    for f in js_funcs:
        print(f"  {f['name']}: {f['preview'][:100]}")

    browser.close()
    print("\n[DONE] Exploration complete")
