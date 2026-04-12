"""
PureBrain.ai /pay-test/ page visual audit.
Captures screenshots, tests chatbox, tests PayPal buttons, checks console.
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/paytest-audit")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PAYTEST_URL = "https://purebrain.ai/pay-test/"
MAIN_URL = "https://purebrain.ai/"

console_logs = []
console_errors = []
network_requests = []

def record_console(msg):
    entry = {"type": msg.type, "text": msg.text}
    console_logs.append(entry)
    if msg.type in ("error", "warning"):
        console_errors.append(entry)

def record_request(request):
    network_requests.append({"url": request.url, "method": request.method})

async def audit_paytest():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # --- Phase 1: pay-test full page ---
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("console", record_console)
        page.on("request", record_request)

        print("Navigating to pay-test page...")
        await page.goto(PAYTEST_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Full page screenshot
        ss1 = str(SCREENSHOTS_DIR / "01-paytest-fullpage.png")
        await page.screenshot(path=ss1, full_page=True)
        print(f"Screenshot 1 saved: {ss1}")

        # Above-fold screenshot
        ss2 = str(SCREENSHOTS_DIR / "02-paytest-above-fold.png")
        await page.screenshot(path=ss2, full_page=False)
        print(f"Screenshot 2 saved: {ss2}")

        # --- Phase 2: DOM inspection ---
        # Check for chat elements
        chat_elements = await page.evaluate("""() => {
            const selectors = [
                '.chat-initial__btn',
                '#userInput',
                '#submitBtn',
                '.chat-container',
                '#awakening',
                '.message--ai',
                '.message--user',
                '[class*="chat"]',
                '[id*="chat"]',
                '[class*="paypal"]',
                '[id*="paypal"]',
                'iframe[src*="paypal"]',
                '.pp-ABCDE',
                '[data-pp-button]',
                '[class*="pay"]',
                '[id*="pay"]'
            ];
            const results = {};
            selectors.forEach(sel => {
                const els = document.querySelectorAll(sel);
                results[sel] = {
                    count: els.length,
                    visible: Array.from(els).filter(el => {
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
                    }).length,
                    text: els.length > 0 ? (els[0].textContent || '').trim().substring(0, 100) : ''
                };
            });
            return results;
        }""")
        print("\nDOM elements found:")
        for sel, info in chat_elements.items():
            if info['count'] > 0:
                print(f"  {sel}: count={info['count']}, visible={info['visible']}, text='{info['text']}'")

        # Page sections / major content
        page_sections = await page.evaluate("""() => {
            const sections = document.querySelectorAll('section, .et_pb_section, [class*="section"]');
            return Array.from(sections).map((s, i) => ({
                index: i,
                id: s.id,
                className: s.className.substring(0, 80),
                visible: window.getComputedStyle(s).display !== 'none',
                height: s.offsetHeight
            })).filter(s => s.height > 10);
        }""")
        print(f"\nPage sections ({len(page_sections)} total):")
        for s in page_sections[:20]:
            print(f"  [{s['index']}] id='{s['id']}' class='{s['className'][:50]}' h={s['height']}")

        # Check for iframes (PayPal often uses iframes)
        iframes = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('iframe')).map(f => ({
                src: f.src,
                id: f.id,
                name: f.name,
                width: f.width,
                height: f.height,
                visible: window.getComputedStyle(f).display !== 'none'
            }));
        }""")
        print(f"\nIframes found ({len(iframes)}):")
        for iframe in iframes:
            print(f"  src='{iframe['src'][:100]}' id='{iframe['id']}' visible={iframe['visible']}")

        # --- Phase 3: Scroll down to find payment section ---
        # Scroll to middle
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await asyncio.sleep(1)
        ss3 = str(SCREENSHOTS_DIR / "03-paytest-middle-scroll.png")
        await page.screenshot(path=ss3, full_page=False)
        print(f"\nScreenshot 3 (middle): {ss3}")

        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        ss4 = str(SCREENSHOTS_DIR / "04-paytest-bottom.png")
        await page.screenshot(path=ss4, full_page=False)
        print(f"Screenshot 4 (bottom): {ss4}")

        # --- Phase 4: Interact with chat ---
        print("\nAttempting to interact with chat widget...")

        # Try to find and click the chat begin button
        begin_btn = await page.query_selector('.chat-initial__btn')
        if begin_btn:
            print("Found .chat-initial__btn - clicking...")
            await begin_btn.click()
            await asyncio.sleep(1.5)
            ss5 = str(SCREENSHOTS_DIR / "05-after-begin-click.png")
            await page.screenshot(path=ss5, full_page=False)
            print(f"Screenshot 5 (after begin click): {ss5}")
        else:
            print("No .chat-initial__btn found - trying to scroll to chat section")
            # Try scrolling to #awakening section
            awakening = await page.query_selector('#awakening')
            if awakening:
                await awakening.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                ss5 = str(SCREENSHOTS_DIR / "05-chat-section-scroll.png")
                await page.screenshot(path=ss5, full_page=False)
                print(f"Screenshot 5 (chat section): {ss5}")
            else:
                print("No #awakening section found either")
                ss5 = str(SCREENSHOTS_DIR / "05-no-chat-found.png")
                await page.screenshot(path=ss5, full_page=False)

        # Try typing in the chat input
        user_input = await page.query_selector('#userInput')
        if user_input:
            print("Found #userInput - typing test message...")
            await user_input.click()
            await asyncio.sleep(0.5)
            await user_input.type("Hello, is this chat working?")
            await asyncio.sleep(0.5)
            ss6 = str(SCREENSHOTS_DIR / "06-chat-typed.png")
            await page.screenshot(path=ss6, full_page=False)
            print(f"Screenshot 6 (typed message): {ss6}")

            # Try submit
            submit_btn = await page.query_selector('#submitBtn')
            if submit_btn:
                print("Found #submitBtn - clicking submit...")
                await submit_btn.click()
                await asyncio.sleep(3)  # Wait for response
                ss7 = str(SCREENSHOTS_DIR / "07-after-submit.png")
                await page.screenshot(path=ss7, full_page=False)
                print(f"Screenshot 7 (after submit): {ss7}")
            else:
                print("No #submitBtn found")
                await page.keyboard.press("Enter")
                await asyncio.sleep(3)
                ss7 = str(SCREENSHOTS_DIR / "07-after-enter.png")
                await page.screenshot(path=ss7, full_page=False)
                print(f"Screenshot 7 (after enter): {ss7}")
        else:
            print("No #userInput found - chat input not present on pay-test page")

        # --- Phase 5: Test PayPal buttons ---
        print("\nLooking for PayPal buttons...")
        paypal_buttons = await page.query_selector_all('iframe[src*="paypal"], [class*="paypal"], [id*="paypal"], .pp-button, [data-funding-source]')
        print(f"PayPal-related elements: {len(paypal_buttons)}")

        # Check for any button with "pay" text
        pay_buttons = await page.evaluate("""() => {
            const all = document.querySelectorAll('button, a, [role="button"]');
            return Array.from(all)
                .filter(el => {
                    const text = (el.textContent || '').toLowerCase();
                    return text.includes('pay') || text.includes('purchase') || text.includes('subscribe') || text.includes('buy');
                })
                .map(el => ({
                    tag: el.tagName,
                    text: el.textContent.trim().substring(0, 100),
                    id: el.id,
                    className: el.className.substring(0, 80),
                    visible: window.getComputedStyle(el).display !== 'none'
                }));
        }""")
        print(f"Payment-related buttons ({len(pay_buttons)}):")
        for btn in pay_buttons:
            print(f"  <{btn['tag']}> text='{btn['text']}' id='{btn['id']}' visible={btn['visible']}")

        # --- Phase 6: Main site for comparison ---
        print("\n--- Capturing main site for comparison ---")
        page_main = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page_main.goto(MAIN_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        ss_main = str(SCREENSHOTS_DIR / "08-main-site-fullpage.png")
        await page_main.screenshot(path=ss_main, full_page=True)
        print(f"Screenshot 8 (main site full): {ss_main}")

        ss_main_fold = str(SCREENSHOTS_DIR / "09-main-site-above-fold.png")
        await page_main.screenshot(path=ss_main_fold, full_page=False)
        print(f"Screenshot 9 (main site above fold): {ss_main_fold}")

        # Main site sections
        main_sections = await page_main.evaluate("""() => {
            const sections = document.querySelectorAll('section, .et_pb_section, [class*="section"]');
            return Array.from(sections).map((s, i) => ({
                index: i,
                id: s.id,
                className: s.className.substring(0, 80),
                visible: window.getComputedStyle(s).display !== 'none',
                height: s.offsetHeight
            })).filter(s => s.height > 10);
        }""")
        print(f"\nMain site sections ({len(main_sections)} total)")

        await page_main.close()

        # --- Phase 7: Check pay-test for broken sections by scrolling through ---
        # Take targeted viewport captures at every 900px
        print("\nCapturing pay-test page in viewport strips...")
        total_height = await page.evaluate("document.body.scrollHeight")
        print(f"Total page height: {total_height}px")

        strips = []
        y = 0
        strip_idx = 10
        while y < total_height:
            await page.evaluate(f"window.scrollTo(0, {y})")
            await asyncio.sleep(0.3)
            strip_path = str(SCREENSHOTS_DIR / f"{strip_idx:02d}-paytest-strip-{y}.png")
            await page.screenshot(path=strip_path, full_page=False)
            strips.append(strip_path)
            strip_idx += 1
            y += 800
        print(f"Captured {len(strips)} viewport strips")

        await page.close()
        await browser.close()

        # --- Report ---
        print("\n" + "="*60)
        print("CONSOLE LOGS SUMMARY")
        print("="*60)
        print(f"Total console messages: {len(console_logs)}")
        print(f"Errors/Warnings: {len(console_errors)}")
        for entry in console_errors[:20]:
            print(f"  [{entry['type'].upper()}] {entry['text'][:200]}")

        print(f"\nAll console messages ({len(console_logs)}):")
        for entry in console_logs[:40]:
            print(f"  [{entry['type']}] {entry['text'][:150]}")

        print(f"\nNetwork requests to chat/AI endpoints:")
        for req in network_requests:
            url = req['url']
            if any(kw in url.lower() for kw in ['chat', 'api', 'log', 'ai', 'openai', 'purebrain', 'paypal']):
                print(f"  {req['method']} {url[:120]}")

        # Save results to JSON
        results = {
            "console_errors": console_errors,
            "console_logs": console_logs[:50],
            "network_requests": [r for r in network_requests if any(
                kw in r['url'].lower() for kw in ['chat', 'api', 'log', 'ai', 'openai', 'paypal', 'purebrain']
            )],
            "chat_elements": {k: v for k, v in chat_elements.items() if v['count'] > 0},
            "iframes": iframes,
            "pay_buttons": pay_buttons,
            "total_height": total_height,
            "sections_count": {"paytest": len(page_sections), "main": len(main_sections)},
            "screenshots": [ss1, ss2, ss3, ss4, ss_main, ss_main_fold] + strips
        }

        results_path = str(SCREENSHOTS_DIR / "audit-results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {results_path}")

if __name__ == "__main__":
    asyncio.run(audit_paytest())
