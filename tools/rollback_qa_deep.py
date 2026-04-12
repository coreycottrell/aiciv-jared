#!/usr/bin/env python3
"""
Deep investigation of openWaitlistModal vs openPayPalCheckout after v4.6.4 rollback.
Focus: Why does openWaitlistModal call waitlist form instead of PayPal?
"""

import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/pay-test-sandbox-2/"
PASSWORD = "PureBrain.ai253443$$$"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            headless=True,
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        console_msgs = []
        def on_console(msg):
            console_msgs.append({"type": msg.type, "text": msg.text})
        page.on("console", on_console)

        # Navigate + unlock
        resp = await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        print(f"HTTP: {resp.status}")

        try:
            pw_input = await page.wait_for_selector('input[id^="pwbox-"]', timeout=10000)
            await pw_input.fill(PASSWORD)
            await page.evaluate("document.querySelector('.post-password-form').submit()")
        except:
            print("Page already unlocked or no password form found")

        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(10)

        print(f"URL after unlock: {page.url}")

        # ── Deep function inspection ──────────────────────────────────────────
        funcs = await page.evaluate("""() => {
            const report = {};

            // Check all relevant global functions
            const names = [
                'openWaitlistModal', 'openPayPalCheckout', 'openPayPalButtons',
                'renderPayPalButtons', 'initPayPal', 'showPayPal',
                'pb_open_paypal', 'pbPayPal', 'startPayment'
            ];
            names.forEach(name => {
                report[name] = {
                    defined: typeof window[name] !== 'undefined',
                    type: typeof window[name],
                    source_preview: typeof window[name] === 'function'
                        ? window[name].toString().substring(0, 400)
                        : null
                };
            });

            return report;
        }""")

        print("\n=== GLOBAL FUNCTION INVENTORY ===")
        for name, info in funcs.items():
            if info['defined']:
                print(f"\n[FOUND] {name} (type={info['type']})")
                if info['source_preview']:
                    print(f"  Source preview:\n{info['source_preview'][:300]}")
            else:
                print(f"[MISSING] {name}")

        # ── Check PayPal SDK state ─────────────────────────────────────────
        paypal_state = await page.evaluate("""() => {
            return {
                paypal_global: typeof window.paypal !== 'undefined',
                paypal_buttons: typeof window.paypal !== 'undefined' && typeof window.paypal.Buttons === 'function',
                paypal_namespace: typeof window.paypal !== 'undefined' ? Object.keys(window.paypal).join(', ') : 'NOT LOADED'
            };
        }""")

        print("\n=== PAYPAL SDK STATE ===")
        print(f"window.paypal defined: {paypal_state['paypal_global']}")
        print(f"window.paypal.Buttons: {paypal_state['paypal_buttons']}")
        print(f"PayPal namespace keys: {paypal_state['paypal_namespace']}")

        # ── Check PayPal scripts ───────────────────────────────────────────
        scripts = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('script[src]'))
                .filter(s => s.src.includes('paypal'))
                .map(s => ({ src: s.src, loaded: s.readyState || 'unknown' }));
        }""")

        print("\n=== PAYPAL SCRIPT TAGS ===")
        for s in scripts:
            print(f"  {s['src'][:150]}")

        # ── Check pb-paypal-buttons-container ─────────────────────────────
        container = await page.evaluate("""() => {
            const el = document.getElementById('pb-paypal-buttons-container');
            if (!el) return { found: false };
            return {
                found: true,
                display: window.getComputedStyle(el).display,
                visibility: window.getComputedStyle(el).visibility,
                height: window.getComputedStyle(el).height,
                children: el.children.length,
                innerHTML: el.innerHTML.substring(0, 500),
                parent_display: el.parentElement ? window.getComputedStyle(el.parentElement).display : 'n/a',
                parent_id: el.parentElement ? el.parentElement.id : 'n/a',
                parent_class: el.parentElement ? el.parentElement.className : 'n/a'
            };
        }""")

        print("\n=== #pb-paypal-buttons-container ===")
        for k, v in container.items():
            print(f"  {k}: {v}")

        # ── Check pricing cards ────────────────────────────────────────────
        pricing_cards = await page.evaluate("""() => {
            const cards = document.querySelectorAll('.pricing-card, [class*="pricing-card"]');
            return Array.from(cards).map(c => ({
                class: c.className,
                text_preview: c.innerText.substring(0, 100),
                onclick: c.getAttribute('onclick') || 'none',
                buttons: Array.from(c.querySelectorAll('button, a[href]')).map(b => ({
                    tag: b.tagName,
                    text: b.innerText,
                    onclick: b.getAttribute('onclick') || 'none',
                    href: b.getAttribute('href') || 'none'
                }))
            }));
        }""")

        print("\n=== PRICING CARDS & BUTTONS ===")
        for card in pricing_cards:
            print(f"\n  Card: {card['class'][:60]}")
            print(f"  Text: {card['text_preview'][:80]}")
            print(f"  Card onclick: {card['onclick'][:80]}")
            for btn in card['buttons']:
                print(f"    Button: [{btn['tag']}] '{btn['text'][:40]}' onclick='{btn['onclick'][:80]}' href='{btn['href'][:60]}'")

        # ── PB-FIX retry pattern - is there a PB-FIX script? ──────────────
        pb_fix = await page.evaluate("""() => {
            // Look for PB-FIX in inline scripts
            const inlineScripts = Array.from(document.querySelectorAll('script:not([src])'));
            const pbFixScripts = inlineScripts.filter(s => s.textContent.includes('PB-FIX') || s.textContent.includes('openPayPalCheckout'));
            return pbFixScripts.map(s => s.textContent.substring(0, 600));
        }""")

        print("\n=== PB-FIX / openPayPalCheckout INLINE SCRIPTS ===")
        if pb_fix:
            for i, script in enumerate(pb_fix):
                print(f"\n--- Script {i+1} ---\n{script}")
        else:
            print("  None found")

        # ── Console summary ────────────────────────────────────────────────
        print("\n=== CONSOLE MESSAGES SUMMARY ===")
        for msg in console_msgs:
            if 'paypal' in msg['text'].lower() or 'PB-FIX' in msg['text'] or 'openPayPal' in msg['text']:
                print(f"  [{msg['type'].upper()}] {msg['text'][:150]}")

        await browser.close()
        print("\nDeep investigation complete.")

asyncio.run(run())
