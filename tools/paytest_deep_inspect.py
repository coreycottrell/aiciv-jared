"""
Deep inspection of pay-test page - focus on:
1. The orange/blank area between sections
2. PayPal section HTML structure
3. Chat "no response" issue
4. Comparison with main site
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/paytest-audit")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PAYTEST_URL = "https://purebrain.ai/pay-test/"

async def deep_inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        console_errors = []
        page.on("console", lambda m: console_errors.append({"type": m.type, "text": m.text}) if m.type in ("error", "warning") else None)

        await page.goto(PAYTEST_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(4)

        # 1. Get ALL sections and their heights, backgrounds
        all_sections = await page.evaluate("""() => {
            const elements = document.querySelectorAll('section, div[id], .et_pb_section, .section');
            return Array.from(elements).map(el => {
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return {
                    tag: el.tagName,
                    id: el.id,
                    className: el.className.substring(0, 100),
                    height: el.offsetHeight,
                    offsetTop: el.offsetTop,
                    backgroundColor: style.backgroundColor,
                    display: style.display,
                    visibility: style.visibility,
                    childCount: el.children.length,
                    textPreview: (el.textContent || '').trim().substring(0, 80)
                };
            }).filter(el => el.height > 50 && el.display !== 'none');
        }""")

        print("=== ALL SIGNIFICANT SECTIONS ===")
        for s in all_sections:
            if 'orange' in s['backgroundColor'] or 'rgb(241' in s['backgroundColor'] or 'rgb(242' in s['backgroundColor'] or '#f14' in s['backgroundColor'].lower():
                flag = " <-- ORANGE SECTION"
            else:
                flag = ""
            print(f"  [{s['tag']}#{s['id']}] top={s['offsetTop']} h={s['height']} bg={s['backgroundColor'][:40]} {flag}")
            if s['textPreview']:
                print(f"    text: '{s['textPreview']}'")

        # 2. Find the specific PayPal section
        paypal_section_html = await page.evaluate("""() => {
            // Find PayPal-related sections
            const results = [];

            // Check for PayPal overlay
            const overlay = document.getElementById('pb-paypal-overlay');
            if (overlay) results.push({name: 'pb-paypal-overlay', outerHTML: overlay.outerHTML.substring(0, 2000)});

            // Check for PayPal form
            const form = document.getElementById('pb-paypal-form');
            if (form) results.push({name: 'pb-paypal-form', outerHTML: form.outerHTML.substring(0, 2000)});

            // Check for PayPal button
            const btn = document.getElementById('pb-paypal-form-btn');
            if (btn) results.push({name: 'pb-paypal-form-btn', outerHTML: btn.outerHTML.substring(0, 500)});

            // Find all elements with 'pay' in id or class
            const payEls = document.querySelectorAll('[id*="pay"], [class*="paypal"]');
            payEls.forEach((el, i) => {
                if (i < 5) {
                    results.push({
                        name: `pay-element-${i}`,
                        id: el.id,
                        className: el.className.substring(0, 80),
                        display: window.getComputedStyle(el).display,
                        visibility: window.getComputedStyle(el).visibility,
                        height: el.offsetHeight,
                        tagName: el.tagName
                    });
                }
            });

            return results;
        }""")

        print("\n=== PAYPAL ELEMENTS ===")
        for item in paypal_section_html:
            print(f"  {item['name']}:")
            if 'outerHTML' in item:
                print(f"    HTML: {item['outerHTML'][:300]}")
            else:
                print(f"    tag={item.get('tagName')} id={item.get('id')} display={item.get('display')} h={item.get('height')}")

        # 3. Check the chat - what happens after sending?
        # Scroll to awakening section
        await page.evaluate("document.getElementById('awakening').scrollIntoView()")
        await asyncio.sleep(1)

        # Click begin
        begin_btn = await page.query_selector('.chat-initial__btn')
        if begin_btn:
            await begin_btn.click()
            await asyncio.sleep(1)

        # Type and submit
        user_input = await page.query_selector('#userInput')
        if user_input:
            await user_input.click()
            await user_input.type("Hello, is this chat working?")
            await asyncio.sleep(0.5)

        submit_btn = await page.query_selector('#submitBtn')
        if submit_btn:
            await submit_btn.click()
            # Wait for potential response
            await asyncio.sleep(5)

        # Check chat state after submission
        chat_state = await page.evaluate("""() => {
            const messages = document.querySelectorAll('.message--ai, .message--user, [class*="message"]');
            const chatContainer = document.querySelector('.chat-messages, #chatMessages, .messages, [class*="messages"]');
            const submitBtn = document.getElementById('submitBtn');
            const userInput = document.getElementById('userInput');

            return {
                messageCount: messages.length,
                messages: Array.from(messages).map(m => ({
                    className: m.className,
                    text: m.textContent.trim().substring(0, 200)
                })),
                chatContainerFound: !!chatContainer,
                submitBtnDisabled: submitBtn ? submitBtn.disabled : null,
                submitBtnText: submitBtn ? submitBtn.textContent.trim() : null,
                inputValue: userInput ? userInput.value : null,
                // Look for any "typing" or "loading" indicator
                loadingEl: !!document.querySelector('.typing, .loading, [class*="thinking"], [class*="loading"], [class*="typing"]'),
                // Look at the chat widget JS status
                chatWidgetExists: typeof window.purebrain !== 'undefined' || typeof window.PureBrain !== 'undefined',
                // Check what JS globals are set
                jsGlobals: Object.keys(window).filter(k => k.toLowerCase().includes('pure') || k.toLowerCase().includes('chat') || k.toLowerCase().includes('paypal'))
            };
        }""")

        print("\n=== CHAT STATE AFTER SUBMISSION ===")
        print(f"  Messages found: {chat_state['messageCount']}")
        for m in chat_state['messages']:
            print(f"    [{m['className'][:40]}]: {m['text'][:100]}")
        print(f"  Submit button disabled: {chat_state['submitBtnDisabled']}")
        print(f"  Input value: {chat_state['inputValue']}")
        print(f"  Loading indicator: {chat_state['loadingEl']}")
        print(f"  Chat widget JS: {chat_state['chatWidgetExists']}")
        print(f"  JS globals: {chat_state['jsGlobals']}")

        # Screenshot of chat after submission
        ss_chat_after = str(SCREENSHOTS_DIR / "20-chat-after-5s-wait.png")
        await page.screenshot(path=ss_chat_after, full_page=False)
        print(f"\nScreenshot saved: {ss_chat_after}")

        # 4. Check network - what did the chat try to call?
        # Extract script tags for chat-related code
        chat_script = await page.evaluate("""() => {
            const scripts = document.querySelectorAll('script:not([src])');
            const relevant = [];
            scripts.forEach(s => {
                const text = s.textContent || '';
                if (text.includes('chat') || text.includes('paypal') || text.includes('PayPal') || text.includes('PureBrain') || text.includes('awakening')) {
                    relevant.push(text.substring(0, 3000));
                }
            });
            return relevant;
        }""")

        print(f"\n=== RELEVANT INLINE SCRIPTS ({len(chat_script)}) ===")
        for i, script in enumerate(chat_script):
            print(f"\n--- Script {i+1} ---")
            print(script[:2000])

        # 5. Check if the orange section is a pricing/CTA section
        # Look at the section around scroll position 2400-3600
        orange_analysis = await page.evaluate("""() => {
            // Find the element at that position
            const elementsAtPos = [];
            for (let y = 2400; y <= 4000; y += 200) {
                const el = document.elementFromPoint(720, y);
                if (el) {
                    const style = window.getComputedStyle(el);
                    elementsAtPos.push({
                        y: y,
                        tag: el.tagName,
                        id: el.id,
                        className: el.className.substring(0, 80),
                        bg: style.backgroundColor,
                        text: (el.textContent || '').trim().substring(0, 80)
                    });
                }
            }
            return elementsAtPos;
        }""")

        print("\n=== ELEMENTS IN ORANGE AREA (Y:2400-4000) ===")
        for item in orange_analysis:
            print(f"  y={item['y']}: <{item['tag']}#{item['id']}> bg={item['bg'][:40]} text='{item['text'][:60]}'")

        # 6. Check the value-section (pricing)
        value_section = await page.evaluate("""() => {
            const section = document.getElementById('value');
            if (!section) return {found: false};
            const style = window.getComputedStyle(section);
            return {
                found: true,
                display: style.display,
                height: section.offsetHeight,
                offsetTop: section.offsetTop,
                backgroundColor: style.backgroundColor,
                innerHTML: section.innerHTML.substring(0, 3000),
                childElements: Array.from(section.querySelectorAll('[class*="price"], [class*="plan"], [class*="pay"], button')).map(el => ({
                    tag: el.tagName,
                    id: el.id,
                    className: el.className.substring(0, 60),
                    text: (el.textContent || '').trim().substring(0, 100),
                    display: window.getComputedStyle(el).display
                }))
            };
        }""")

        print("\n=== #value SECTION ===")
        print(f"  Found: {value_section.get('found')}")
        if value_section.get('found'):
            print(f"  Height: {value_section.get('height')}")
            print(f"  OffsetTop: {value_section.get('offsetTop')}")
            print(f"  Display: {value_section.get('display')}")
            print(f"  BG: {value_section.get('backgroundColor')}")
            print(f"  Child elements ({len(value_section.get('childElements', []))}):")
            for el in value_section.get('childElements', []):
                print(f"    <{el['tag']}#{el['id']}> class='{el['className']}' text='{el['text'][:60]}'")
            print(f"\n  HTML preview:\n{value_section.get('innerHTML', '')[:1500]}")

        # Scroll to value section and screenshot
        await page.evaluate("""
            const el = document.getElementById('value');
            if (el) el.scrollIntoView();
        """)
        await asyncio.sleep(1)
        ss_value = str(SCREENSHOTS_DIR / "21-value-section.png")
        await page.screenshot(path=ss_value, full_page=False)
        print(f"\nScreenshot value section: {ss_value}")

        await browser.close()

        print("\n=== CONSOLE ERRORS ===")
        for e in console_errors:
            print(f"  [{e['type'].upper()}] {e['text'][:300]}")

if __name__ == "__main__":
    asyncio.run(deep_inspect())
