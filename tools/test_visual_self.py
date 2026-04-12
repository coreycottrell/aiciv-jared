#!/usr/bin/env python3
"""Check VISUAL_SELF tag - is it visible to users or hidden in JS/system prompt?"""

import time
from playwright.sync_api import sync_playwright

PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            args=["--ignore-certificate-errors", "--ignore-ssl-errors"],
            headless=True,
        )
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
        )
        page = ctx.new_page()

        print("Loading pay-test...")
        page.goto("https://purebrain.ai/pay-test/#awakening", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        pw_input = page.query_selector('input[type="password"]')
        if pw_input:
            pw_input.fill(PAGE_PASSWORD)
            submit = page.query_selector('input[type="submit"]')
            if submit:
                submit.click()
            time.sleep(8)

        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight * 0.2)")
        time.sleep(2)

        begin = page.query_selector(".chat-initial__btn")
        if begin:
            begin.click()
            time.sleep(3)

        chat = page.query_selector("#userInput")
        if chat and chat.is_visible():
            chat.click()
            chat.fill("hello")
            page.keyboard.press("Enter")
            print("'hello' sent - waiting 15s...")
            time.sleep(15)

        # Get VISUAL_SELF context with surrounding HTML
        vs_info = page.evaluate("""
            () => {
                const html = document.documentElement.outerHTML;
                const idx = html.indexOf('VISUAL_SELF');
                if (idx === -1) return {found: false};

                // Get surrounding context
                const context = html.substring(Math.max(0, idx - 300), idx + 400);

                // Check if it's in a script tag
                const scriptCheck = html.substring(Math.max(0, idx - 1000), idx);
                const inScript = scriptCheck.lastIndexOf('<script') > scriptCheck.lastIndexOf('</script>');

                // Check if it's in a hidden element
                const templateCheck = html.substring(Math.max(0, idx - 500), idx);
                const inTemplate = templateCheck.lastIndexOf('<template') > templateCheck.lastIndexOf('</template>');

                // Check if it's in visible chat messages
                const chatMessages = document.querySelectorAll('.chat-message, .message, [class*=message], .chat-bubble');
                let inVisibleMessage = false;
                let messageText = '';
                for (const m of chatMessages) {
                    if (m.innerText && m.innerText.includes('VISUAL_SELF')) {
                        inVisibleMessage = true;
                        messageText = m.innerText.substring(0, 200);
                    }
                }

                return {
                    found: true,
                    context_html: context,
                    in_script: inScript,
                    in_template: inTemplate,
                    in_visible_message: inVisibleMessage,
                    visible_message_text: messageText,
                };
            }
        """)

        print(f"VISUAL_SELF analysis:")
        print(f"  Found: {vs_info.get('found')}")
        print(f"  In script tag: {vs_info.get('in_script')}")
        print(f"  In template tag: {vs_info.get('in_template')}")
        print(f"  In VISIBLE chat message: {vs_info.get('in_visible_message')}")
        if vs_info.get('visible_message_text'):
            print(f"  Visible message text: {vs_info['visible_message_text']}")
        print(f"  HTML context: {vs_info.get('context_html', '')[:500]}")

        # Check if system prompt is visible in page
        system_prompt_check = page.evaluate("""
            () => {
                // Look for any element containing [VISUAL_SELF:
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node;
                const found = [];
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('VISUAL_SELF')) {
                        found.push({
                            text: node.textContent.substring(0, 200),
                            parentTag: node.parentElement.tagName,
                            parentClass: node.parentElement.className.substring(0, 50),
                            parentVisible: node.parentElement.offsetParent !== null,
                        });
                    }
                }
                return found;
            }
        """)
        print(f"\nVISUAL_SELF in text nodes:")
        for item in system_prompt_check:
            print(f"  {item}")

        # Get visible chat message content
        chat_content = page.evaluate("""
            () => {
                const awakening = document.getElementById('awakening');
                return awakening ? awakening.innerText.substring(0, 1000) : 'awakening not found';
            }
        """)
        print(f"\nChat content (awakening section):")
        print(chat_content[:600])

        # Take a full-page screenshot to see everything
        page.screenshot(path=f"{SCREENSHOTS_DIR}/VISUAL_SELF_check.png", full_page=False)
        print(f"\nScreenshot: VISUAL_SELF_check.png")

        browser.close()


if __name__ == "__main__":
    main()
