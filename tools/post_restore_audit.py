#!/usr/bin/env python3
"""
Post-GoDaddy Restore Audit for pay-test-2 and pay-test-sandbox-2
Plugin: v4.6.3 (restored state)
Date: 2026-02-27
"""

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/post-restore-audit"
PASSWORD = "PureBrain.ai253443$$$"

PAGES = [
    {
        "name": "pay-test-2",
        "url": "https://purebrain.ai/pay-test-2/",
        "label": "PRODUCTION PayPal",
        "page_id": 689
    },
    {
        "name": "pay-test-sandbox-2",
        "url": "https://purebrain.ai/pay-test-sandbox-2/",
        "label": "SANDBOX PayPal",
        "page_id": 688
    }
]


async def screenshot(page, name, label):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    await page.screenshot(path=path, full_page=False)
    print(f"  [SCREENSHOT] {label} -> {path}")
    return path


async def enter_password(page, page_name):
    """Enter password on protected page."""
    print(f"\n  [AUTH] Entering password for {page_name}...")
    try:
        pwd_input = page.locator("input[type='password']")
        await pwd_input.wait_for(state="visible", timeout=10000)
        await pwd_input.fill(PASSWORD)
        await screenshot(page, f"{page_name}--01-password-field", "password field")
        submit = page.locator("input[type='submit'], button[type='submit']").first
        await submit.click()
        await page.wait_for_load_state("networkidle", timeout=15000)
        print(f"  [AUTH] Password submitted, waiting for page load...")
        await asyncio.sleep(3)
        return True
    except Exception as e:
        print(f"  [AUTH ERROR] {e}")
        return False


async def check_paypal_button(page, page_name):
    """Click a pricing tier button and check what modal appears."""
    print(f"\n  [PAYPAL CHECK] Testing pricing button clicks...")
    results = {}

    # Scroll to reveal pricing section
    try:
        await page.evaluate("""
            const pricing = document.getElementById('pricing');
            if (pricing) {
                pricing.classList.add('active');
                pricing.scrollIntoView({behavior: 'smooth', block: 'center'});
            }
        """)
        await asyncio.sleep(1)
    except Exception as e:
        print(f"  [PAYPAL] Pricing reveal error: {e}")

    # Check what openWaitlistModal actually does
    try:
        fn_src = await page.evaluate("typeof openWaitlistModal !== 'undefined' ? openWaitlistModal.toString().substring(0, 300) : 'NOT DEFINED'")
        results['openWaitlistModal_src'] = fn_src
        print(f"  [JS] openWaitlistModal source snippet:\n    {fn_src[:200]}")
    except Exception as e:
        results['openWaitlistModal_src'] = f"ERROR: {e}"

    # Check openPayPalCheckout
    try:
        pp_fn = await page.evaluate("typeof openPayPalCheckout !== 'undefined' ? openPayPalCheckout.toString().substring(0, 200) : 'NOT DEFINED'")
        results['openPayPalCheckout'] = pp_fn[:100]
        print(f"  [JS] openPayPalCheckout: {pp_fn[:80]}")
    except Exception as e:
        results['openPayPalCheckout'] = f"ERROR: {e}"

    # Check openPayPalModal
    try:
        ppm_fn = await page.evaluate("typeof openPayPalModal !== 'undefined' ? openPayPalModal.toString().substring(0, 200) : 'NOT DEFINED'")
        results['openPayPalModal'] = ppm_fn[:100]
        print(f"  [JS] openPayPalModal: {ppm_fn[:80]}")
    except Exception as e:
        results['openPayPalModal'] = f"ERROR: {e}"

    # Check PayPal SDK
    try:
        paypal_sdk = await page.evaluate("typeof window.paypal !== 'undefined' ? 'LOADED - version: ' + (window.paypal.version || 'unknown') : 'NOT LOADED'")
        results['paypal_sdk'] = paypal_sdk
        print(f"  [SDK] PayPal SDK: {paypal_sdk}")
    except Exception as e:
        results['paypal_sdk'] = f"ERROR: {e}"

    # Check PayPal client ID in inline scripts
    try:
        client_id_check = await page.evaluate("""
            const scripts = Array.from(document.querySelectorAll('script[src*="paypal"]'));
            scripts.map(s => s.src.substring(0, 150))
        """)
        results['paypal_script_srcs'] = client_id_check
        print(f"  [SDK] PayPal script src(s): {client_id_check}")
    except Exception as e:
        results['paypal_script_srcs'] = f"ERROR: {e}"

    # Screenshot pricing section
    await screenshot(page, f"{page_name}--02-pricing-section", "pricing section")

    # Find and click an Awakened button
    try:
        # Try to find the Awakened tier button
        awakened_btn = None
        for selector in [
            "text=Select Awakened",
            "text=Get Started",
            ".pricing-card__btn",
            ".ptc-pricing-btn",
            "[onclick*='Waitlist'], [onclick*='PayPal'], [onclick*='openWait'], [onclick*='openPay']"
        ]:
            try:
                btn = page.locator(selector).first
                if await btn.count() > 0:
                    awakened_btn = btn
                    print(f"  [BUTTON] Found button with selector: {selector}")
                    break
            except:
                continue

        if awakened_btn:
            # Get the onclick attribute
            onclick_attr = await awakened_btn.get_attribute("onclick")
            btn_text = await awakened_btn.inner_text()
            results['button_onclick'] = onclick_attr
            results['button_text'] = btn_text
            print(f"  [BUTTON] Text: '{btn_text}', onclick: '{onclick_attr}'")

            # Click it
            await awakened_btn.click()
            await asyncio.sleep(2)
            await screenshot(page, f"{page_name}--03-after-button-click", "after button click")

            # Check what modal is visible
            modal_check = await page.evaluate("""
                const modals = ['#waitlistModal', '#pb-paypal-modal', '.modal', '[id*="modal"]'];
                const results = {};
                modals.forEach(sel => {
                    const els = document.querySelectorAll(sel);
                    els.forEach((el, i) => {
                        const style = window.getComputedStyle(el);
                        results[sel + '[' + i + ']'] = {
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity,
                            id: el.id,
                            classes: el.className
                        };
                    });
                });
                return results;
            """)
            results['modal_visibility'] = modal_check
            print(f"  [MODAL] Visible modals after click: {modal_check}")

            # Determine if it's PayPal or waitlist
            paypal_modal_vis = await page.evaluate("""
                const m = document.getElementById('pb-paypal-modal');
                if (!m) return 'MODAL NOT FOUND';
                const s = window.getComputedStyle(m);
                return {display: s.display, opacity: s.opacity, visibility: s.visibility};
            """)
            waitlist_modal_vis = await page.evaluate("""
                const m = document.getElementById('waitlistModal');
                if (!m) return 'MODAL NOT FOUND';
                const s = window.getComputedStyle(m);
                return {display: s.display, opacity: s.opacity, visibility: s.visibility};
            """)
            results['paypal_modal_visibility'] = paypal_modal_vis
            results['waitlist_modal_visibility'] = waitlist_modal_vis
            print(f"  [MODAL] PayPal modal: {paypal_modal_vis}")
            print(f"  [MODAL] Waitlist modal: {waitlist_modal_vis}")

            # Check PayPal buttons rendered
            paypal_buttons = await page.evaluate("""
                const container = document.getElementById('pb-paypal-buttons-container');
                if (!container) return {found: false};
                const iframes = container.querySelectorAll('iframe');
                const divs = container.querySelectorAll('div');
                return {
                    found: true,
                    childCount: container.childElementCount,
                    iframeCount: iframes.length,
                    divCount: divs.length,
                    innerHTML: container.innerHTML.substring(0, 200)
                };
            """)
            results['paypal_buttons_container'] = paypal_buttons
            print(f"  [PAYPAL BUTTONS] Container state: {paypal_buttons}")
        else:
            results['button_onclick'] = 'NO BUTTON FOUND'
            print(f"  [BUTTON] WARNING: Could not find pricing button")

    except Exception as e:
        results['button_click_error'] = str(e)
        print(f"  [BUTTON ERROR] {e}")

    return results


async def check_chatbox(page, page_name):
    """Check chatbox presence and state."""
    print(f"\n  [CHATBOX CHECK] Checking chatbox state...")
    results = {}

    try:
        chatbox_check = await page.evaluate("""
            const elements = {
                chatMessages: !!document.getElementById('chatMessages'),
                userInput: !!document.getElementById('userInput'),
                chatbox: !!document.querySelector('.chatbox, .chat-container, #chatbox, [id*="chat"]'),
                beginBtn: !!document.querySelector('.chat-initial__btn, [class*="begin"], [id*="begin"]'),
                oauthBtn: !!document.querySelector('[class*="oauth"], [id*="oauth"], [class*="claude-auth"]')
            };
            return elements;
        """)
        results['chatbox_elements'] = chatbox_check
        print(f"  [CHATBOX] Elements found: {chatbox_check}")
    except Exception as e:
        results['chatbox_elements'] = f"ERROR: {e}"

    await screenshot(page, f"{page_name}--04-chatbox-state", "chatbox state")
    return results


async def get_console_logs(page_name, logs):
    """Analyze and categorize console logs."""
    categorized = {
        'errors': [],
        'paypal': [],
        'pb_fix': [],
        'pb_sandbox': [],
        'birth_start': [],
        'pool_exhausted': [],
        'csp': [],
        'other': []
    }

    for log in logs:
        text = log.get('text', '')
        level = log.get('level', '')

        if level == 'error' or 'error' in text.lower():
            categorized['errors'].append(text)
        if '[paypal]' in text.lower() or 'paypal' in text.lower():
            categorized['paypal'].append(text)
        if '[pb-fix]' in text.lower() or '[pb paypal]' in text.lower():
            categorized['pb_fix'].append(text)
        if '[pb-sandbox]' in text.lower() or 'sandbox' in text.lower():
            categorized['pb_sandbox'].append(text)
        if 'birth' in text.lower() or 'start' in text.lower() and 'ptc' in text.lower():
            categorized['birth_start'].append(text)
        if 'pool_exhausted' in text.lower():
            categorized['pool_exhausted'].append(text)
        if 'content security policy' in text.lower() or 'csp' in text.lower():
            categorized['csp'].append(text)

    return categorized


async def audit_page(playwright, page_config):
    """Run full audit on a single page."""
    page_name = page_config['name']
    url = page_config['url']
    label = page_config['label']

    print(f"\n{'='*60}")
    print(f"AUDITING: {page_name} ({label})")
    print(f"URL: {url}")
    print(f"{'='*60}")

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        viewport={"width": 1280, "height": 900}
    )
    page = await context.new_page()

    # Collect console logs
    console_logs = []
    page.on("console", lambda msg: console_logs.append({
        'level': msg.type,
        'text': msg.text
    }))

    results = {
        'page_name': page_name,
        'url': url,
        'label': label,
        'auth_success': False,
        'paypal_check': {},
        'chatbox_check': {},
        'console_logs': []
    }

    try:
        # Navigate to page
        print(f"\n  [NAV] Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        await screenshot(page, f"{page_name}--00-initial", "initial load")

        # Enter password
        auth_ok = await enter_password(page, page_name)
        results['auth_success'] = auth_ok

        if auth_ok:
            # Wait for PayPal SDK to load (10-15 sec as instructed)
            print(f"\n  [WAIT] Waiting 12 seconds for PayPal SDK to load...")
            await asyncio.sleep(12)
            await screenshot(page, f"{page_name}--01b-after-wait", "after SDK load wait")

            # Run checks
            results['paypal_check'] = await check_paypal_button(page, page_name)
            results['chatbox_check'] = await check_chatbox(page, page_name)

        # Get final screenshot
        await screenshot(page, f"{page_name}--05-final", "final state")

    except Exception as e:
        print(f"\n  [PAGE ERROR] {e}")
        results['page_error'] = str(e)
        await screenshot(page, f"{page_name}--ERROR", "error state")

    # Process console logs
    results['console_logs'] = await get_console_logs(page_name, console_logs)
    print(f"\n  [CONSOLE] Captured {len(console_logs)} total log entries")
    for category, entries in results['console_logs'].items():
        if entries:
            print(f"    [{category.upper()}] {len(entries)} entries:")
            for e in entries[:5]:
                print(f"      - {e[:120]}")

    await browser.close()
    return results


async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    all_results = {}

    async with async_playwright() as playwright:
        for page_config in PAGES:
            result = await audit_page(playwright, page_config)
            all_results[page_config['name']] = result

    # Generate summary report
    print("\n\n" + "="*70)
    print("POST-RESTORE AUDIT SUMMARY")
    print("="*70)

    for page_name, data in all_results.items():
        print(f"\n### {page_name} ({data['label']})")
        print(f"  Auth: {'OK' if data['auth_success'] else 'FAILED'}")

        pc = data.get('paypal_check', {})
        if pc:
            wm_src = pc.get('openWaitlistModal_src', 'N/A')
            is_waitlist = 'waitlistForm' in wm_src or 'Full Name' in wm_src or 'waitlist' in wm_src.lower()
            is_paypal = 'paypal' in wm_src.lower() or 'PayPal' in wm_src

            print(f"  openWaitlistModal: {'WAITLIST FORM (BAD)' if is_waitlist else 'PAYPAL (GOOD)' if is_paypal else 'UNKNOWN'}")
            print(f"  PayPal SDK: {pc.get('paypal_sdk', 'N/A')}")
            print(f"  Button onclick: {pc.get('button_onclick', 'N/A')}")

            pm = pc.get('paypal_modal_visibility', {})
            wm = pc.get('waitlist_modal_visibility', {})
            pb_btns = pc.get('paypal_buttons_container', {})

            if isinstance(pm, dict):
                print(f"  PayPal Modal visible: opacity={pm.get('opacity','?')}, display={pm.get('display','?')}")
            if isinstance(wm, dict):
                print(f"  Waitlist Modal visible: opacity={wm.get('opacity','?')}, display={wm.get('display','?')}")
            if isinstance(pb_btns, dict):
                print(f"  PayPal Buttons container: childCount={pb_btns.get('childCount','?')}, iframes={pb_btns.get('iframeCount','?')}")

        cl = data.get('console_logs', {})
        if cl.get('errors'):
            print(f"  Console ERRORS: {len(cl['errors'])}")
        if cl.get('pool_exhausted'):
            print(f"  POOL EXHAUSTED: YES - {cl['pool_exhausted']}")
        if cl.get('pb_fix'):
            print(f"  PB-FIX msgs: {len(cl['pb_fix'])}")
        if cl.get('paypal'):
            print(f"  PayPal msgs: {len(cl['paypal'])}")

    return all_results


if __name__ == "__main__":
    results = asyncio.run(main())
