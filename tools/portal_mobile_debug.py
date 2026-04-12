#!/usr/bin/env python3
"""
PureBrain Portal Mobile Portrait vs Landscape Debug
Diagnoses why messages are invisible on mobile portrait but visible on landscape.
"""

import json
import time
import os
from playwright.sync_api import sync_playwright

TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
PORTAL_URL = "https://app.purebrain.ai"
SCREENSHOT_DIR = "/tmp/portal_mobile_debug"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

CONSOLE_COMMANDS = [
    "JSON.stringify(document.querySelector('#chat-messages') ? document.querySelector('#chat-messages').getBoundingClientRect() : 'NOT FOUND')",
    "document.querySelector('#chat-messages') ? document.querySelector('#chat-messages').children.length : 'NOT FOUND'",
    "document.querySelector('#chat-messages') ? document.querySelector('#chat-messages').innerHTML.substring(0, 500) : 'NOT FOUND'",
    "document.querySelector('#chat-messages') ? getComputedStyle(document.querySelector('#chat-messages')).overflow : 'NOT FOUND'",
    "document.querySelector('#chat-messages') ? getComputedStyle(document.querySelector('#chat-messages')).overflowY : 'NOT FOUND'",
    "document.querySelector('#pb-canvas-container') ? getComputedStyle(document.querySelector('#pb-canvas-container')).display : 'not found'",
    "document.body.classList.contains('login-active')",
]

EXTRA_COMMANDS = [
    # Container height
    "document.querySelector('#chat-messages') ? getComputedStyle(document.querySelector('#chat-messages')).height : 'NOT FOUND'",
    # Parent container
    "document.querySelector('#chat-messages') ? document.querySelector('#chat-messages').parentElement.id + ' / ' + getComputedStyle(document.querySelector('#chat-messages').parentElement).height : 'NOT FOUND'",
    # Main layout container
    "document.querySelector('#chat-container') ? getComputedStyle(document.querySelector('#chat-container')).height + ' / display:' + getComputedStyle(document.querySelector('#chat-container')).display : 'not found'",
    # Is something covering the chat?
    "document.querySelector('#pb-canvas-container') ? getComputedStyle(document.querySelector('#pb-canvas-container')).height : 'not found'",
    # Z-index check on canvas
    "document.querySelector('#pb-canvas-container') ? getComputedStyle(document.querySelector('#pb-canvas-container')).zIndex : 'not found'",
    # Check for any fixed overlay covering
    "Array.from(document.querySelectorAll('[style*=\"position: fixed\"], [style*=\"position:fixed\"]')).map(el => el.id + '.' + el.className.substring(0,30)).join(', ')",
    # Mobile nav height
    "document.querySelector('#mobile-bottom-nav') ? getComputedStyle(document.querySelector('#mobile-bottom-nav')).height : 'not found'",
    # Check transform/translateY on chat-messages
    "document.querySelector('#chat-messages') ? getComputedStyle(document.querySelector('#chat-messages')).transform : 'NOT FOUND'",
    # Body scroll height vs client height
    "document.body.scrollHeight + ' / ' + document.documentElement.clientHeight",
    # Check visibility
    "document.querySelector('#chat-messages') ? getComputedStyle(document.querySelector('#chat-messages')).visibility : 'NOT FOUND'",
]


def run_commands(page, label):
    results = {}
    print(f"\n--- Console Commands ({label}) ---")
    for cmd in CONSOLE_COMMANDS + EXTRA_COMMANDS:
        try:
            val = page.evaluate(cmd)
            results[cmd[:60]] = val
            print(f"  {cmd[:60]}")
            print(f"    => {val}")
        except Exception as e:
            results[cmd[:60]] = f"ERROR: {e}"
            print(f"  {cmd[:60]}")
            print(f"    => ERROR: {e}")
    return results


def login(page):
    print(f"\nNavigating to {PORTAL_URL} ...")
    page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)

    # Take screenshot of login page
    page.screenshot(path=f"{SCREENSHOT_DIR}/00-login-page.png")
    print(f"Screenshot: {SCREENSHOT_DIR}/00-login-page.png")

    # Try to find password/token field
    print("Looking for login field...")

    # Check what fields exist
    inputs = page.query_selector_all("input")
    print(f"Found {len(inputs)} input(s):")
    for i, inp in enumerate(inputs):
        t = inp.get_attribute("type") or "text"
        name = inp.get_attribute("name") or ""
        placeholder = inp.get_attribute("placeholder") or ""
        id_attr = inp.get_attribute("id") or ""
        print(f"  [{i}] type={t} id={id_attr} name={name} placeholder={placeholder}")

    # Try password field first, then any text input
    field = (
        page.query_selector("input[type='password']")
        or page.query_selector("input[type='text']")
        or page.query_selector("input")
    )

    if field:
        field.fill(TOKEN)
        print(f"Filled token into field")
        field.press("Enter")
        print("Pressed Enter")
    else:
        print("ERROR: No login field found!")
        return False

    time.sleep(3)
    page.screenshot(path=f"{SCREENSHOT_DIR}/01-after-login.png")
    print(f"Screenshot: {SCREENSHOT_DIR}/01-after-login.png")

    # Check if we're past login
    url = page.url
    print(f"Current URL after login: {url}")

    # Check for login-active class
    has_login_active = page.evaluate("document.body.classList.contains('login-active')")
    print(f"Body has login-active class: {has_login_active}")

    return True


def test_viewport(page, label, width, height, screenshot_prefix):
    print(f"\n{'='*60}")
    print(f"TESTING: {label} ({width}x{height})")
    print(f"{'='*60}")

    page.set_viewport_size({"width": width, "height": height})
    time.sleep(3)  # Wait for layout reflow and WebSocket messages

    # Screenshot
    path = f"{SCREENSHOT_DIR}/{screenshot_prefix}-screenshot.png"
    page.screenshot(path=path)
    print(f"Screenshot saved: {path}")

    # Run console commands
    results = run_commands(page, label)

    # Additional targeted checks
    print(f"\n--- Additional Targeted Checks ({label}) ---")

    # Check all elements that could be obscuring #chat-messages
    try:
        # Get bounding rect of chat-messages
        chat_rect = page.evaluate("""
            (function() {
                var el = document.querySelector('#chat-messages');
                if (!el) return null;
                var r = el.getBoundingClientRect();
                return {top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width, height: r.height};
            })()
        """)
        print(f"  chat-messages BoundingRect: {chat_rect}")

        # Check what element is at center of chat area
        if chat_rect and chat_rect.get('width', 0) > 0:
            cx = int(chat_rect['left'] + chat_rect['width'] / 2)
            cy = int(chat_rect['top'] + chat_rect['height'] / 2)
            if cy > 0:
                elem_at_center = page.evaluate(f"""
                    (function() {{
                        var el = document.elementFromPoint({cx}, {cy});
                        if (!el) return 'null';
                        return el.tagName + '#' + el.id + '.' + el.className.substring(0, 40);
                    }})()
                """)
                print(f"  Element at chat center ({cx},{cy}): {elem_at_center}")
    except Exception as e:
        print(f"  BoundingRect check error: {e}")

    # Check overall layout structure
    try:
        layout = page.evaluate("""
            (function() {
                var ids = ['#app', '#chat-container', '#chat-messages', '#chat-input-area',
                           '#mobile-bottom-nav', '#pb-canvas-container', '#sidebar', '#nav'];
                var result = {};
                ids.forEach(function(id) {
                    var el = document.querySelector(id);
                    if (el) {
                        var cs = getComputedStyle(el);
                        var r = el.getBoundingClientRect();
                        result[id] = {
                            display: cs.display,
                            height: cs.height,
                            overflow: cs.overflow,
                            position: cs.position,
                            top: cs.top,
                            zIndex: cs.zIndex,
                            rect_h: r.height,
                            rect_top: r.top
                        };
                    } else {
                        result[id] = 'NOT FOUND';
                    }
                });
                return result;
            })()
        """)
        print(f"\n  Layout structure:")
        for el_id, props in layout.items():
            print(f"    {el_id}: {props}")
    except Exception as e:
        print(f"  Layout check error: {e}")

    # Check for elements with height:0 that contain chat messages
    try:
        zero_height = page.evaluate("""
            (function() {
                var suspects = [];
                var chat = document.querySelector('#chat-messages');
                if (!chat) return 'chat-messages not found';
                var el = chat.parentElement;
                var depth = 0;
                while (el && depth < 10) {
                    var h = el.getBoundingClientRect().height;
                    var cs = getComputedStyle(el);
                    suspects.push({
                        tag: el.tagName,
                        id: el.id,
                        class: el.className.substring(0, 30),
                        height_rect: h,
                        height_css: cs.height,
                        overflow: cs.overflow,
                        display: cs.display
                    });
                    el = el.parentElement;
                    depth++;
                }
                return suspects;
            })()
        """)
        print(f"\n  Parent chain from #chat-messages:")
        if isinstance(zero_height, list):
            for item in zero_height:
                flag = " <-- ZERO HEIGHT!" if item.get('height_rect', 1) == 0 else ""
                print(f"    {item.get('tag')}#{item.get('id')}.{item.get('class')} | h={item.get('height_rect')} | css_h={item.get('height_css')} | overflow={item.get('overflow')} | display={item.get('display')}{flag}")
        else:
            print(f"    {zero_height}")
    except Exception as e:
        print(f"  Parent chain check error: {e}")

    return results


def main():
    print("PureBrain Portal Mobile Debug")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Use mobile context for authentic mobile UA
        context = browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        )

        page = context.new_page()

        # Collect console messages
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_msgs.append(f"[PAGE_ERROR] {err}"))

        # Login
        if not login(page):
            print("Login failed, aborting")
            browser.close()
            return

        # Wait for chat to load
        print("\nWaiting 5s for WebSocket + messages to load...")
        time.sleep(5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/02-after-wait.png")
        print(f"Screenshot: {SCREENSHOT_DIR}/02-after-wait.png")

        # Check if we're logged in or still on login page
        login_active = page.evaluate("document.body.classList.contains('login-active')")
        print(f"Still showing login screen (login-active): {login_active}")

        # Test PORTRAIT (375x812)
        portrait_results = test_viewport(page, "PORTRAIT", 375, 812, "03-portrait")

        # Test LANDSCAPE (812x375)
        landscape_results = test_viewport(page, "LANDSCAPE", 812, 375, "04-landscape")

        # Console messages
        print(f"\n--- Console Messages (all) ---")
        for msg in console_msgs[:50]:
            print(f"  {msg}")
        if len(console_msgs) > 50:
            print(f"  ... and {len(console_msgs) - 50} more")

        browser.close()

    print(f"\n{'='*60}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}/")
    print("Files:")
    for f in sorted(os.listdir(SCREENSHOT_DIR)):
        print(f"  {SCREENSHOT_DIR}/{f}")


if __name__ == "__main__":
    main()
