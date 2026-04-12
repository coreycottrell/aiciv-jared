"""
Visual E2E test of purebrain.ai/pay-test/ using headed Chromium via xvfb.
This gets past the WebGL canvas preloader that blocks headless mode.
Takes screenshots at every stage of the flow.
"""
import time
import os
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/paytest-screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def screenshot(page, name, step):
    path = f"{SCREENSHOTS_DIR}/{step:02d}_{name}.png"
    page.screenshot(path=path)
    print(f"  Screenshot: {path}")
    return path

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Headed mode - xvfb provides the display
            args=['--use-gl=swiftshader', '--enable-webgl']  # Software GL for WebGL
        )
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = ctx.new_page()

        print("=" * 60)
        print("PAY-TEST VISUAL E2E TEST")
        print("=" * 60)

        # Step 1: Load the page
        print("\n[1] Loading pay-test page...")
        page.goto("https://purebrain.ai/pay-test/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        screenshot(page, "initial_load", 1)

        # Wait for body to become visible (canvas preloader should complete)
        print("\n[2] Waiting for page to render (canvas preloader)...")
        for attempt in range(20):
            body_display = page.evaluate("() => window.getComputedStyle(document.body).display")
            body_opacity = page.evaluate("() => window.getComputedStyle(document.body).opacity")
            body_vis = page.evaluate("() => window.getComputedStyle(document.body).visibility")
            print(f"  Attempt {attempt+1}: display={body_display}, opacity={body_opacity}, visibility={body_vis}")
            if body_display != "none" and body_opacity != "0":
                print("  Body is visible!")
                break
            time.sleep(2)
        else:
            print("  WARNING: Body still hidden after 40s - forcing visible")
            page.evaluate("""() => {
                document.body.style.display = 'block';
                document.body.style.opacity = '1';
                document.body.style.visibility = 'visible';
            }""")
            time.sleep(1)

        screenshot(page, "page_rendered", 2)

        # Check page height
        height = page.evaluate("() => document.body.scrollHeight")
        print(f"  Page height: {height}px")

        # Step 3: Check for chat section
        print("\n[3] Looking for chat section...")
        has_chat = page.evaluate("""() => {
            const chat = document.getElementById('pb-chat-section') ||
                         document.querySelector('.chat-section') ||
                         document.querySelector('[class*="chat"]');
            return chat ? {id: chat.id, class: chat.className, visible: chat.offsetHeight > 0} : null;
        }""")
        print(f"  Chat section: {has_chat}")

        # Scroll to chat
        page.evaluate("""() => {
            const chat = document.getElementById('pb-chat-section') ||
                         document.querySelector('.chat-section') ||
                         document.querySelector('[class*="chat"]');
            if (chat) chat.scrollIntoView({behavior: 'instant'});
        }""")
        time.sleep(1)
        screenshot(page, "chat_section", 3)

        # Step 4: Start conversation
        print("\n[4] Starting awakening conversation...")
        # Check if startConversation exists
        has_start = page.evaluate("() => typeof window.startConversation === 'function'")
        print(f"  startConversation available: {has_start}")

        if has_start:
            page.evaluate("() => window.startConversation()")
            time.sleep(5)
            screenshot(page, "conversation_started", 4)

            # Read initial messages
            messages = page.evaluate("""() => {
                const msgs = document.querySelectorAll('.chat-message, .message, [class*="message"]');
                return Array.from(msgs).map(m => ({
                    text: m.textContent.substring(0, 100),
                    class: m.className
                }));
            }""")
            print(f"  Messages visible: {len(messages)}")
            for i, msg in enumerate(messages[:5]):
                print(f"    [{i}] {msg['text'][:80]}...")

        # Step 5: Send user message
        print("\n[5] Sending user message...")
        # Find input field
        input_sel = page.evaluate("""() => {
            const input = document.getElementById('pb-chat-input') ||
                          document.querySelector('input[type="text"]') ||
                          document.querySelector('textarea');
            return input ? {id: input.id, tag: input.tagName, type: input.type} : null;
        }""")
        print(f"  Input field: {input_sel}")

        if input_sel:
            sel = f"#{input_sel['id']}" if input_sel.get('id') else input_sel['tag'].lower()
            try:
                page.fill(sel, "Hi! My name is Alex and I'm a business consultant.")
                time.sleep(0.5)
                screenshot(page, "message_typed", 5)

                # Submit
                submit = page.evaluate("""() => {
                    const btn = document.getElementById('pb-send-btn') ||
                                document.querySelector('button[type="submit"]') ||
                                document.querySelector('.send-btn');
                    return btn ? {id: btn.id, text: btn.textContent} : null;
                }""")
                print(f"  Submit button: {submit}")

                if submit and submit.get('id'):
                    page.click(f"#{submit['id']}")
                else:
                    # Try pressing Enter
                    page.press(sel, "Enter")
                time.sleep(5)
                screenshot(page, "after_first_message", 6)
            except Exception as e:
                print(f"  Input interaction failed: {e}")
                # Fall back to JS
                page.evaluate("""() => {
                    if (window.handleSubmit) {
                        const input = document.getElementById('pb-chat-input');
                        if (input) input.value = "Hi! My name is Alex and I'm a business consultant.";
                        window.handleSubmit(new Event('submit'));
                    }
                }""")
                time.sleep(5)
                screenshot(page, "after_first_message_js", 6)
        else:
            # Fall back to direct JS call
            print("  No input field found - using JS directly")
            page.evaluate("""() => {
                if (window.handleSubmit) {
                    const input = document.getElementById('pb-chat-input');
                    if (input) input.value = "Hi! My name is Alex and I'm a business consultant.";
                    window.handleSubmit(new Event('submit'));
                }
            }""")
            time.sleep(5)
            screenshot(page, "after_first_message_js", 6)

        # Step 6: Continue conversation - name the AI
        print("\n[6] Naming the AI...")
        page.evaluate("""() => {
            const input = document.getElementById('pb-chat-input');
            if (input) input.value = "I'd like to call you Nova";
            if (window.handleSubmit) window.handleSubmit(new Event('submit'));
        }""")
        time.sleep(5)
        screenshot(page, "after_naming", 7)

        # Step 7: Ask to get started
        print("\n[7] Asking to get started...")
        page.evaluate("""() => {
            const input = document.getElementById('pb-chat-input');
            if (input) input.value = "I want to get started with Nova. Show me my options.";
            if (window.handleSubmit) window.handleSubmit(new Event('submit'));
        }""")
        time.sleep(5)
        screenshot(page, "after_get_started", 8)

        # Step 8: Look for the "See what X can do" button
        print("\n[8] Looking for capability button...")
        cap_btn = page.evaluate("""() => {
            const btns = document.querySelectorAll('button, .btn, [class*="btn"]');
            for (const b of btns) {
                if (b.textContent.includes('can do') || b.textContent.includes('See what')) {
                    return {text: b.textContent.trim(), id: b.id, visible: b.offsetHeight > 0};
                }
            }
            return null;
        }""")
        print(f"  Capability button: {cap_btn}")

        if cap_btn:
            # Click it
            page.evaluate("""() => {
                const btns = document.querySelectorAll('button, .btn, [class*="btn"]');
                for (const b of btns) {
                    if (b.textContent.includes('can do') || b.textContent.includes('See what')) {
                        b.click();
                        break;
                    }
                }
            }""")
            time.sleep(3)
            screenshot(page, "capabilities_section", 9)

        # Step 9: Look for pricing section
        print("\n[9] Looking for pricing section...")
        pricing = page.evaluate("""() => {
            const section = document.getElementById('pb-pricing-section') ||
                            document.querySelector('[class*="pricing"]') ||
                            document.querySelector('[class*="tier"]');
            if (!section) return null;
            return {
                id: section.id,
                visible: section.offsetHeight > 0,
                text: section.textContent.substring(0, 200)
            };
        }""")
        print(f"  Pricing section: {pricing}")

        # Scroll to pricing
        page.evaluate("""() => {
            const section = document.getElementById('pb-pricing-section') ||
                            document.querySelector('[class*="pricing"]');
            if (section) section.scrollIntoView({behavior: 'instant'});
        }""")
        time.sleep(2)
        screenshot(page, "pricing_section", 10)

        # Step 10: Check PayPal buttons
        print("\n[10] Checking PayPal integration...")
        paypal = page.evaluate("""() => {
            return {
                sdkLoaded: typeof window.paypal !== 'undefined',
                buttonsContainer: !!document.getElementById('pb-paypal-buttons-container'),
                modalOverlay: !!document.querySelector('.pb-paypal-overlay, [class*="paypal-overlay"]'),
                tierButtons: document.querySelectorAll('[class*="tier"], [class*="price-card"], [class*="pricing-card"]').length
            };
        }""")
        print(f"  PayPal SDK loaded: {paypal.get('sdkLoaded')}")
        print(f"  Buttons container: {paypal.get('buttonsContainer')}")
        print(f"  Tier buttons: {paypal.get('tierButtons')}")

        # Try clicking a pricing tier
        print("\n[11] Attempting to click a pricing tier...")
        clicked = page.evaluate("""() => {
            // Look for pricing cards/buttons
            const cards = document.querySelectorAll('[class*="tier"], [class*="price-card"], [class*="pricing-card"], [onclick*="paypal"], [onclick*="select"]');
            if (cards.length > 0) {
                cards[0].click();
                return {clicked: true, text: cards[0].textContent.substring(0, 100)};
            }
            // Look for "Choose" or "Select" or "Get Started" buttons
            const btns = document.querySelectorAll('button');
            for (const b of btns) {
                const t = b.textContent.toLowerCase();
                if (t.includes('choose') || t.includes('select') || t.includes('get started') || t.includes('$')) {
                    b.click();
                    return {clicked: true, text: b.textContent.substring(0, 100)};
                }
            }
            return {clicked: false, available: cards.length};
        }""")
        print(f"  Click result: {clicked}")
        time.sleep(3)
        screenshot(page, "after_tier_click", 11)

        # Check if PayPal modal appeared
        modal = page.evaluate("""() => {
            const overlay = document.querySelector('.pb-paypal-overlay, [class*="paypal-overlay"], [class*="paypal-modal"]');
            if (!overlay) return null;
            return {
                visible: overlay.offsetHeight > 0 && window.getComputedStyle(overlay).display !== 'none',
                html: overlay.innerHTML.substring(0, 300)
            };
        }""")
        print(f"  PayPal modal: {modal}")
        if modal:
            screenshot(page, "paypal_modal", 12)

        # Final full-page screenshot
        print("\n[12] Taking full-page screenshot...")
        page.screenshot(path=f"{SCREENSHOTS_DIR}/99_full_page.png", full_page=True)
        print(f"  Full page: {SCREENSHOTS_DIR}/99_full_page.png")

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        screenshots = [f for f in os.listdir(SCREENSHOTS_DIR) if f.endswith('.png')]
        screenshots.sort()
        print(f"Screenshots taken: {len(screenshots)}")
        for s in screenshots:
            size = os.path.getsize(f"{SCREENSHOTS_DIR}/{s}")
            print(f"  {s} ({size:,} bytes)")

        browser.close()
        return 0


if __name__ == "__main__":
    exit(main())
