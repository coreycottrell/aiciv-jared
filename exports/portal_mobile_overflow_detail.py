"""
PureBrain Portal - Detailed overflow diagnosis
Get CSS details on overflowing elements
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

        print("Navigating to portal...")
        await page.goto(PORTAL_URL, wait_until="networkidle", timeout=30000)

        pwd_input = await page.query_selector("input[type='password']")
        await pwd_input.fill(TOKEN)
        submit = await page.query_selector("button[type='submit']")
        await submit.click()

        await page.wait_for_selector(".msg", timeout=10000)
        await page.wait_for_timeout(2000)

        # Scroll to bottom first
        await page.evaluate("document.querySelector('#chat-messages').scrollTop = document.querySelector('#chat-messages').scrollHeight")
        await page.wait_for_timeout(500)

        print("\n=== DETAILED OVERFLOW DIAGNOSIS ===\n")

        # Get detailed CSS on overflowing bubbles
        detail = await page.evaluate("""
            var bubbles = document.querySelectorAll('.msg-bubble');
            var overflows = [];
            bubbles.forEach(function(b, i) {
              var rect = b.getBoundingClientRect();
              if (rect.right > window.innerWidth || rect.left < 0) {
                var cs = getComputedStyle(b);
                var parentMsg = b.closest('.msg');
                var parentRow = b.closest('.msg-row');
                var parentMsgRect = parentMsg ? parentMsg.getBoundingClientRect() : null;
                var parentRowRect = parentRow ? parentRow.getBoundingClientRect() : null;
                overflows.push({
                    index: i,
                    bubbleRect: {left: Math.round(rect.left), right: Math.round(rect.right), width: Math.round(rect.width)},
                    parentMsgRect: parentMsgRect ? {left: Math.round(parentMsgRect.left), right: Math.round(parentMsgRect.right), width: Math.round(parentMsgRect.width)} : null,
                    parentRowRect: parentRowRect ? {left: Math.round(parentRowRect.left), right: Math.round(parentRowRect.right), width: Math.round(parentRowRect.width)} : null,
                    css: {
                        maxWidth: cs.maxWidth,
                        width: cs.width,
                        boxSizing: cs.boxSizing,
                        padding: cs.padding,
                        overflowX: cs.overflowX,
                        wordBreak: cs.wordBreak,
                        whiteSpace: cs.whiteSpace
                    },
                    parentMsgClass: parentMsg ? parentMsg.className : 'none',
                    text: b.textContent.substring(0,100)
                });
              }
            });
            JSON.stringify({total_checked: bubbles.length, overflowing: overflows.length, details: overflows})
        """)
        print("OVERFLOWING BUBBLES:")
        data = json.loads(detail)
        print(f"  Total bubbles: {data['total_checked']}")
        print(f"  Overflowing: {data['overflowing']}")
        for d in data['details']:
            print(f"\n  Bubble #{d['index']}:")
            print(f"    Text: {d['text'][:80]}")
            print(f"    Parent msg class: {d['parentMsgClass']}")
            print(f"    Bubble rect: {d['bubbleRect']}")
            print(f"    Parent .msg rect: {d['parentMsgRect']}")
            print(f"    Parent .msg-row rect: {d['parentRowRect']}")
            print(f"    CSS: max-width={d['css']['maxWidth']}, width={d['css']['width']}, box-sizing={d['css']['boxSizing']}")
            print(f"    CSS: overflow-x={d['css']['overflowX']}, word-break={d['css']['wordBreak']}, white-space={d['css']['whiteSpace']}")

        # Check .msg-row CSS
        msg_row_css = await page.evaluate("""
            var rows = document.querySelectorAll('.msg-row');
            var sample = rows[0];
            if (!sample) return JSON.stringify({found: false});
            var cs = getComputedStyle(sample);
            return JSON.stringify({
                display: cs.display,
                flexDirection: cs.flexDirection,
                width: cs.width,
                maxWidth: cs.maxWidth,
                overflowX: cs.overflowX,
                offsetWidth: sample.offsetWidth,
                scrollWidth: sample.scrollWidth
            });
        """)
        print(f"\n.msg-row CSS: {msg_row_css}")

        # Check chat-messages container CSS
        chat_css = await page.evaluate("""
            var el = document.querySelector('#chat-messages');
            if (!el) return JSON.stringify({found: false});
            var cs = getComputedStyle(el);
            return JSON.stringify({
                display: cs.display,
                flexDirection: cs.flexDirection,
                width: cs.width,
                maxWidth: cs.maxWidth,
                overflowX: cs.overflowX,
                overflowY: cs.overflowY,
                padding: cs.padding,
                offsetWidth: el.offsetWidth,
                scrollWidth: el.scrollWidth,
                clientWidth: el.clientWidth
            });
        """)
        print(f"\n#chat-messages CSS: {chat_css}")

        # Check .msg CSS for overflowing ones
        msg_css = await page.evaluate("""
            var msgs = document.querySelectorAll('.msg');
            var sample = null;
            msgs.forEach(function(m) {
                var rect = m.getBoundingClientRect();
                // Find one that contains overflowing bubble
                var bubble = m.querySelector('.msg-bubble');
                if (bubble) {
                    var br = bubble.getBoundingClientRect();
                    if (br.right > window.innerWidth) {
                        sample = m;
                    }
                }
            });
            if (!sample) return JSON.stringify({found: false});
            var cs = getComputedStyle(sample);
            return JSON.stringify({
                display: cs.display,
                flexDirection: cs.flexDirection,
                alignSelf: cs.alignSelf,
                alignItems: cs.alignItems,
                width: cs.width,
                maxWidth: cs.maxWidth,
                overflowX: cs.overflowX,
                offsetWidth: sample.offsetWidth,
                scrollWidth: sample.scrollWidth,
                className: sample.className
            });
        """)
        print(f"\nOverflowing .msg CSS: {msg_css}")

        # Check welcome-hero size
        hero_css = await page.evaluate("""
            var el = document.querySelector('.welcome-hero');
            if (!el) return JSON.stringify({found: false});
            var cs = getComputedStyle(el);
            return JSON.stringify({
                width: cs.width,
                maxWidth: cs.maxWidth,
                offsetWidth: el.offsetWidth,
                scrollWidth: el.scrollWidth
            });
        """)
        print(f"\n.welcome-hero CSS: {hero_css}")

        # Check header-right
        header_right_css = await page.evaluate("""
            var el = document.querySelector('.header-right');
            if (!el) return JSON.stringify({found: false});
            var cs = getComputedStyle(el);
            return JSON.stringify({
                display: cs.display,
                width: cs.width,
                offsetWidth: el.offsetWidth,
                scrollWidth: el.scrollWidth,
                childCount: el.children.length,
                children: Array.from(el.children).map(function(c) { return {tag: c.tagName, cls: c.className, offsetWidth: c.offsetWidth}; })
            });
        """)
        print(f"\n.header-right CSS: {header_right_css}")

        # Screenshot the overflow area - zoom in on a problematic message
        await page.evaluate("""
            // Scroll to the first overflowing bubble
            var bubbles = document.querySelectorAll('.msg-bubble');
            for (var i = 0; i < bubbles.length; i++) {
                var rect = bubbles[i].getBoundingClientRect();
                if (rect.right > window.innerWidth) {
                    bubbles[i].scrollIntoView({behavior: 'instant', block: 'center'});
                    break;
                }
            }
        """)
        await page.wait_for_timeout(300)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/010-overflow-bubble-detail.png", full_page=False)
        print(f"\nScreenshot: 010-overflow-bubble-detail.png")

        await browser.close()
        print("\nDetail diagnosis complete.")

asyncio.run(run())
