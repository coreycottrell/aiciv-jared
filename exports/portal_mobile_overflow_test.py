"""
PureBrain Portal - Mobile Portrait Overflow Audit
Viewport: 375x812 (iPhone portrait)
Date: 2026-03-08
"""

import asyncio
import json
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-mobile-overflow-20260308"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 375, "height": 812},
            device_scale_factor=2,
            is_mobile=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()

        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_logs.append(f"[PAGE ERROR] {err}"))

        print("Step 1: Navigate to portal login page...")
        await page.goto(PORTAL_URL, wait_until="networkidle", timeout=30000)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/001-login-page.png", full_page=False)
        print("  Screenshot: 001-login-page.png")

        # Look for password field and enter token
        print("Step 2: Enter login token...")
        pwd_input = await page.query_selector("input[type='password']")
        if pwd_input:
            await pwd_input.click()
            await pwd_input.fill(TOKEN)
            print("  Token entered in password field")
        else:
            # Try any input field
            inputs = await page.query_selector_all("input")
            print(f"  No password input found. Found {len(inputs)} inputs total")
            for i, inp in enumerate(inputs):
                inp_type = await inp.get_attribute("type")
                inp_placeholder = await inp.get_attribute("placeholder")
                print(f"    Input {i}: type={inp_type}, placeholder={inp_placeholder}")
            if inputs:
                await inputs[0].fill(TOKEN)

        await page.screenshot(path=f"{SCREENSHOT_DIR}/002-token-entered.png", full_page=False)

        # Try to submit
        print("Step 3: Submit login...")
        submit = await page.query_selector("button[type='submit']")
        if not submit:
            submit = await page.query_selector("button")
        if submit:
            btn_text = await submit.inner_text()
            print(f"  Clicking button: '{btn_text}'")
            await submit.click()
        else:
            # Try pressing Enter
            await page.keyboard.press("Enter")
            print("  Pressed Enter to submit")

        # Wait for page to load after login
        await page.wait_for_timeout(3000)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/003-post-login.png", full_page=False)
        print("  Screenshot: 003-post-login.png")
        print(f"  Current URL: {page.url}")

        # Check if we're logged in - look for chat messages
        print("Step 4: Waiting for chat messages to load...")
        try:
            await page.wait_for_selector("#chat-messages, .msg, .chat-messages", timeout=10000)
            print("  Chat messages found")
        except:
            print("  WARNING: Chat messages selector not found within 10s")

        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/004-chat-loaded.png", full_page=False)
        print("  Screenshot: 004-chat-loaded.png")

        # Full page scroll screenshot
        await page.screenshot(path=f"{SCREENSHOT_DIR}/005-chat-full.png", full_page=True)
        print("  Screenshot: 005-chat-full.png (full page)")

        # Scroll through messages
        print("Step 5: Scrolling through messages...")
        chat_container = await page.query_selector("#chat-messages")
        if chat_container:
            # Scroll to top first
            await page.evaluate("document.querySelector('#chat-messages').scrollTop = 0")
            await page.wait_for_timeout(500)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/006-chat-top.png", full_page=False)

            # Scroll to middle
            await page.evaluate("""
                var el = document.querySelector('#chat-messages');
                el.scrollTop = el.scrollHeight / 2;
            """)
            await page.wait_for_timeout(500)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/007-chat-middle.png", full_page=False)

            # Scroll to bottom
            await page.evaluate("""
                var el = document.querySelector('#chat-messages');
                el.scrollTop = el.scrollHeight;
            """)
            await page.wait_for_timeout(500)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/008-chat-bottom.png", full_page=False)
            print("  Scrolled through messages - screenshots captured")

        # JS Check 1: Message overflow
        print("Step 6: Running JS overflow checks...")
        msg_overflow = await page.evaluate("""
            var msgs = document.querySelectorAll('.msg');
            var overflows = [];
            msgs.forEach(function(m, i) {
              var rect = m.getBoundingClientRect();
              if (rect.right > window.innerWidth || rect.left < 0) {
                overflows.push({index: i, left: rect.left, right: rect.right, width: rect.width, text: m.textContent.substring(0,50)});
              }
            });
            JSON.stringify({total: msgs.length, overflowing: overflows.length, details: overflows.slice(0,5)})
        """)
        print(f"  MSG overflow check: {msg_overflow}")

        # JS Check 2: Bubble overflow
        bubble_overflow = await page.evaluate("""
            var bubbles = document.querySelectorAll('.msg-bubble');
            var bubbleOverflows = [];
            bubbles.forEach(function(b, i) {
              var rect = b.getBoundingClientRect();
              if (rect.right > window.innerWidth || rect.left < 0) {
                bubbleOverflows.push({index: i, left: rect.left, right: rect.right, width: rect.width, text: b.textContent.substring(0,50)});
              }
            });
            JSON.stringify({total: bubbles.length, overflowing: bubbleOverflows.length, details: bubbleOverflows.slice(0,5)})
        """)
        print(f"  BUBBLE overflow check: {bubble_overflow}")

        # JS Check 3: Quote text overflow
        quote_overflow = await page.evaluate("""
            var quotes = document.querySelectorAll('.msg-quote-text');
            var quoteOverflows = [];
            quotes.forEach(function(q, i) {
              var rect = q.getBoundingClientRect();
              if (rect.right > window.innerWidth || rect.left < 0) {
                quoteOverflows.push({index: i, left: rect.left, right: rect.right, width: rect.width, whiteSpace: getComputedStyle(q).whiteSpace, text: q.textContent.substring(0,80)});
              }
            });
            JSON.stringify({total: quotes.length, overflowing: quoteOverflows.length, details: quoteOverflows.slice(0,5)})
        """)
        print(f"  QUOTE overflow check: {quote_overflow}")

        # JS Check 4: Horizontal scroll
        h_scroll = await page.evaluate("""
            var chatMsgs = document.querySelector('#chat-messages');
            JSON.stringify({
              bodyScrollWidth: document.body.scrollWidth,
              viewportWidth: window.innerWidth,
              hasHorizontalScroll: document.body.scrollWidth > window.innerWidth,
              chatMessagesScrollWidth: chatMsgs ? chatMsgs.scrollWidth : null,
              chatMessagesClientWidth: chatMsgs ? chatMsgs.clientWidth : null,
              chatHasHScroll: chatMsgs ? chatMsgs.scrollWidth > chatMsgs.clientWidth : null
            })
        """)
        print(f"  HORIZONTAL SCROLL check: {h_scroll}")

        # Additional: Check quote-text white-space computed style
        quote_style = await page.evaluate("""
            var qt = document.querySelector('.msg-quote-text');
            if (qt) {
                var cs = getComputedStyle(qt);
                JSON.stringify({
                    whiteSpace: cs.whiteSpace,
                    overflow: cs.overflow,
                    textOverflow: cs.textOverflow,
                    maxWidth: cs.maxWidth,
                    width: qt.offsetWidth,
                    scrollWidth: qt.scrollWidth
                });
            } else {
                JSON.stringify({found: false});
            }
        """)
        print(f"  QUOTE-TEXT computed style: {quote_style}")

        # Check body/html overflow
        body_overflow = await page.evaluate("""
            var bodyCS = getComputedStyle(document.body);
            var htmlCS = getComputedStyle(document.documentElement);
            JSON.stringify({
                bodyOverflowX: bodyCS.overflowX,
                bodyOverflowY: bodyCS.overflowY,
                htmlOverflowX: htmlCS.overflowX,
                htmlOverflowY: htmlCS.overflowY,
                bodyWidth: document.body.offsetWidth,
                bodyScrollWidth: document.body.scrollWidth
            })
        """)
        print(f"  BODY/HTML overflow styles: {body_overflow}")

        # Check if any elements extend beyond viewport
        wide_elements = await page.evaluate("""
            var allElems = document.querySelectorAll('*');
            var wide = [];
            allElems.forEach(function(el) {
                var rect = el.getBoundingClientRect();
                if (rect.right > window.innerWidth + 1 && rect.width > 10) {
                    var tag = el.tagName.toLowerCase();
                    var cls = el.className.toString().substring(0,40);
                    var id = el.id;
                    if (wide.length < 10) {
                        wide.push({tag: tag, cls: cls, id: id, right: Math.round(rect.right), width: Math.round(rect.width)});
                    }
                }
            });
            JSON.stringify({count: wide.length, elements: wide})
        """)
        print(f"  ALL WIDE ELEMENTS: {wide_elements}")

        # Final screenshot with console logs
        await page.screenshot(path=f"{SCREENSHOT_DIR}/009-final-state.png", full_page=False)

        print(f"\nConsole logs ({len(console_logs)} entries):")
        for log in console_logs[:20]:
            print(f"  {log}")

        await browser.close()
        print("\nTest complete.")

asyncio.run(run())
