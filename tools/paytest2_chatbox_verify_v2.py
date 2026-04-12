#!/usr/bin/env python3
"""
Pay-Test-2 Chatbox Verification Script v2 - 2026-02-27
Uses pre-obtained cookie to bypass password form.
Verifies: Begin Awakening button visible, clickable, chatbox responds.
"""

import asyncio
import subprocess
import re
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-verify-20260227")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL = "https://purebrain.ai/pay-test-2/"
PASSWORD = "PureBrain.ai253443$"

def get_postpass_cookie():
    """Get wp-postpass cookie via curl (most reliable method)."""
    import urllib.parse
    encoded_pw = urllib.parse.quote(PASSWORD)

    cmd = [
        "curl", "-s",
        "-c", "/tmp/pb_cookies2.txt",
        "https://purebrain.ai/wp-login.php?action=postpass",
        "--data", f"post_password={encoded_pw}&Submit=Enter&redirect_to=https%3A%2F%2Fpurebrain.ai%2Fpay-test-2%2F",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "-H", "Referer: https://purebrain.ai/pay-test-2/",
        "-o", "/dev/null",
        "-w", "%{http_code}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"  curl POST status: {result.stdout.strip()}")

    # Read cookies
    try:
        cookie_file = Path("/tmp/pb_cookies2.txt")
        content = cookie_file.read_text()
        print(f"  Cookie file:\n{content}")

        # Extract the wp-postpass cookie
        for line in content.splitlines():
            if "wp-postpass" in line:
                parts = line.split("\t")
                if len(parts) >= 7:
                    cookie_name = parts[5]
                    cookie_value = parts[6]
                    return cookie_name, cookie_value
    except Exception as e:
        print(f"  Error reading cookies: {e}")

    return None, None

async def run():
    print("=== Pay-Test-2 Chatbox Verification v2 ===\n")

    # Step 1: Get auth cookie via curl
    print("Step 1: Getting authentication cookie via curl...")
    cookie_name, cookie_value = get_postpass_cookie()

    if not cookie_name:
        print("  ERROR: Could not obtain postpass cookie!")
        return

    print(f"  Cookie obtained: {cookie_name}={cookie_value[:20]}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )

        # Inject the auth cookie BEFORE navigating
        await context.add_cookies([{
            "name": cookie_name,
            "value": cookie_value,
            "domain": "purebrain.ai",
            "path": "/",
            "secure": True,
            "httpOnly": False
        }])
        print("\nStep 2: Cookie injected into browser context")

        page = await context.new_page()

        # Capture console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))

        # Capture network errors
        network_errors = []
        page.on("response", lambda r: network_errors.append(f"{r.status} {r.url}") if r.status >= 400 else None)

        print("\nStep 3: Navigating to pay-test-2 with auth cookie...")
        response = await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        print(f"  HTTP status: {response.status}")

        await asyncio.sleep(3)

        # Check if we got past the password wall
        pw_error = await page.query_selector(".post-password-form-invalid-password")
        pw_form = await page.query_selector("input[id^='pwbox-']")

        if pw_error or pw_form:
            print("  WARNING: Still seeing password form! Cookie injection may not have worked.")
            await page.screenshot(path=str(OUTPUT_DIR / "v2-001-still-password.png"))
        else:
            print("  SUCCESS: Password wall bypassed!")

        await page.screenshot(path=str(OUTPUT_DIR / "v2-001-after-cookie-nav.png"))
        print("  Screenshot v2-001 saved")

        # Wait for JS to initialize
        print("\nStep 4: Waiting for page JS to initialize...")
        await asyncio.sleep(5)

        await page.screenshot(path=str(OUTPUT_DIR / "v2-002-js-initialized.png"))
        print("  Screenshot v2-002 saved: JS initialization state")

        # Scroll to see the page
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=str(OUTPUT_DIR / "v2-003-top-of-page.png"))

        # Full page screenshot
        await page.screenshot(path=str(OUTPUT_DIR / "v2-004-full-page.png"), full_page=True)
        print("  Screenshot v2-004 saved: full page")

        # --- Look for Begin Awakening button ---
        print("\nStep 5: Looking for 'Begin Awakening' button...")

        # Check page content to understand what's rendered
        page_text = await page.evaluate("document.body.innerText")
        if "Begin Awakening" in page_text:
            print("  'Begin Awakening' text FOUND in page content")
        elif "Begin" in page_text:
            # Find what Begin text there is
            import re
            begin_matches = re.findall(r'.{0,30}Begin.{0,30}', page_text)
            print(f"  'Begin' found in context: {begin_matches[:3]}")
        else:
            print("  'Begin Awakening' text NOT found in page content")
            print(f"  Page text preview: {page_text[:500]}")

        # Try multiple selectors
        begin_btn = None
        found_selector = None
        for selector in [
            ".chat-initial__btn",
            "button:has-text('Begin Awakening')",
            ".chat-initial button",
            "button[onclick*='startConversation']",
            "button.begin-btn",
            "[class*='initial'] button",
            "button:has-text('Begin')",
            ".chat-start-btn",
            "[data-action='start']",
            "button",  # Find ANY button as fallback
        ]:
            try:
                el = await page.query_selector(selector)
                if el:
                    text = await el.inner_text()
                    is_vis = await el.is_visible()
                    print(f"  Selector '{selector}': FOUND (text='{text.strip()[:50]}', visible={is_vis})")
                    if not begin_btn and ("begin" in text.lower() or "awakening" in text.lower() or "start" in text.lower()):
                        begin_btn = el
                        found_selector = selector
                else:
                    pass  # Silently skip not-found
            except Exception as e:
                print(f"  Selector '{selector}': ERROR - {e}")

        # Also dump all buttons on the page
        all_buttons = await page.query_selector_all("button")
        print(f"\n  Total buttons on page: {len(all_buttons)}")
        for i, btn in enumerate(all_buttons[:10]):
            try:
                txt = await btn.inner_text()
                cls = await btn.get_attribute("class")
                vis = await btn.is_visible()
                print(f"    Button {i+1}: text='{txt.strip()[:60]}' class='{cls}' visible={vis}")
            except:
                pass

        # Check chat containers
        print("\nStep 6: Checking chatbox elements...")
        chat_elements = {}
        for selector in [
            "#chatMessages",
            ".chat-container",
            ".chat-initial",
            ".chat-wrapper",
            "[class*='chat']",
            "#chat-wrapper",
            ".chatbox",
            "#chatbox",
        ]:
            el = await page.query_selector(selector)
            if el:
                is_visible = await el.is_visible()
                inner_text = await el.inner_text()
                chat_elements[selector] = {"visible": is_visible, "text_preview": inner_text[:100]}
                print(f"  {selector}: found (visible={is_visible}, text='{inner_text[:80]}')")

        # --- Try clicking if Begin button found ---
        if begin_btn:
            print(f"\nStep 7: Found Begin button via '{found_selector}' - clicking...")
            await page.screenshot(path=str(OUTPUT_DIR / "v2-005-before-click.png"))
            print("  Screenshot v2-005 saved: before click state")

            try:
                await begin_btn.click()
                print("  Clicked! Waiting for response...")
                await asyncio.sleep(3)
                await page.screenshot(path=str(OUTPUT_DIR / "v2-006-after-click.png"))
                print("  Screenshot v2-006 saved: immediately after click")

                await asyncio.sleep(5)
                await page.screenshot(path=str(OUTPUT_DIR / "v2-007-5sec-after.png"))
                print("  Screenshot v2-007 saved: 5 seconds after click")

                await asyncio.sleep(10)
                await page.screenshot(path=str(OUTPUT_DIR / "v2-008-15sec-after.png"))
                print("  Screenshot v2-008 saved: 15 seconds after click (should have AI response)")

                # Check for typing indicator
                typing_el = await page.query_selector("#typingIndicator, .typing-indicator")
                if typing_el:
                    vis = await typing_el.is_visible()
                    print(f"  Typing indicator: found (visible={vis})")

                # Check for AI messages
                ai_msgs = await page.query_selector_all(".message--ai, .ptc-msg--ai, [class*='message-ai'], [class*='msg-ai']")
                user_msgs = await page.query_selector_all(".message--user, .ptc-msg--user, [class*='message-user']")
                print(f"  AI messages: {len(ai_msgs)}")
                print(f"  User messages: {len(user_msgs)}")

                if ai_msgs:
                    msg_text = await ai_msgs[0].inner_text()
                    print(f"  First AI message: '{msg_text[:300]}'")

                # Check chat input appeared
                chat_input = await page.query_selector("#userInput, textarea[placeholder*='Message'], .chat-input, [placeholder*='type']")
                if chat_input:
                    vis = await chat_input.is_visible()
                    print(f"  Chat input field: found (visible={vis})")

            except Exception as e:
                print(f"  Click error: {e}")
        else:
            print("\nStep 7: No Begin button found - investigating page structure...")

            # Get more page structure
            divs = await page.query_selector_all("[class*='chat'], [id*='chat'], [class*='initial'], [id*='chat']")
            print(f"  Elements with chat/initial in class/id: {len(divs)}")
            for div in divs[:8]:
                cls = await div.get_attribute("class")
                id_ = await div.get_attribute("id")
                tag = await div.evaluate("el => el.tagName")
                vis = await div.is_visible()
                txt = await div.inner_text()
                print(f"    {tag} class='{cls}' id='{id_}' visible={vis} text='{txt[:80]}'")

            # Dump page body snippet for debugging
            body_html = await page.content()
            # Find the chatbox section
            if "chat" in body_html.lower():
                chat_idx = body_html.lower().find("chat")
                snippet = body_html[max(0, chat_idx-200):chat_idx+2000]
                (OUTPUT_DIR / "v2-page-chat-section.txt").write_text(snippet)
                print(f"  Chat HTML section saved to v2-page-chat-section.txt")

            # Save full body
            (OUTPUT_DIR / "v2-full-page.txt").write_text(body_html[:20000])
            print("  First 20k of page HTML saved to v2-full-page.txt")

        # --- Console log analysis ---
        print("\n--- Console Messages ---")
        errors = [m for m in console_messages if m["type"] == "error"]
        warnings = [m for m in console_messages if m["type"] == "warning"]
        logs = [m for m in console_messages if m["type"] == "log"]

        print(f"  Errors: {len(errors)}")
        for e in errors[:8]:
            print(f"    ERROR: {e['text'][:250]}")

        print(f"  Warnings: {len(warnings)}")
        for w in warnings[:5]:
            print(f"    WARN: {w['text'][:250]}")

        # JSON/parse specific errors
        json_errors = [m for m in console_messages if any(x in m["text"].lower() for x in ["json", "parse", "syntax", "invalid", "unexpected token"])]
        if json_errors:
            print(f"\n  JSON/Parse/Syntax messages ({len(json_errors)}):")
            for j in json_errors:
                print(f"    {j['type'].upper()}: {j['text'][:400]}")

        # Network errors
        if network_errors:
            print(f"\n  Network errors ({len(network_errors)}):")
            for ne in network_errors[:5]:
                print(f"    {ne}")

        await browser.close()

        print(f"\n=== Screenshots saved to: {OUTPUT_DIR} ===")
        screenshots = sorted(OUTPUT_DIR.glob("v2-*.png"))
        for s in screenshots:
            print(f"  {s.name}")

if __name__ == "__main__":
    asyncio.run(run())
