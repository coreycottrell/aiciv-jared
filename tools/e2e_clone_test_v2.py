#!/usr/bin/env python3
"""
Full E2E chatbox test v2 for https://purebrain.ai/homepage-clone-test/
Now with correct selectors:
- Chat system: #userInput, #chatMessages, #chatInitial, .chat-input__field
- Chat start: button.chat-initial__btn "Begin Awakening"
- Chat messages: #chatMessages
- Waitlist form: #waitlistName, #waitlistEmail, #waitlistUseCase, #waitlistCompany, #waitlistRole
"""

import asyncio
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/clone-test-e2e-20260310"
URL = "https://purebrain.ai/homepage-clone-test/"
STEP = [0]

async def screenshot(page, label):
    STEP[0] += 1
    n = str(STEP[0]).zfill(3)
    path = f"{SCREENSHOT_DIR}/{n}-{label}.png"
    await page.screenshot(path=path, full_page=False)
    print(f"  [SS {n}] {label}")
    return path

async def run_e2e_test():
    print("=" * 70)
    print("E2E CHATBOX TEST v2: homepage-clone-test (correct selectors)")
    print("=" * 70)

    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()

        # Track console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text[:200]}") if msg.type in ["error"] else None)

        print("\n--- STEP 1: Load page ---")
        try:
            await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"  Load warning: {e}")
        await asyncio.sleep(3)
        print(f"  Title: {await page.title()}")
        await screenshot(page, "step1-page-loaded")

        # Verify chat elements exist
        print("\n--- STEP 2: Verify chat elements ---")
        chat_check = await page.evaluate("""
            () => {
                return {
                    chatMessages: !!document.querySelector('#chatMessages'),
                    chatInitial: !!document.querySelector('#chatInitial'),
                    beginBtn: !!document.querySelector('.chat-initial__btn'),
                    beginBtnText: document.querySelector('.chat-initial__btn')?.innerText?.trim(),
                    userInput: !!document.querySelector('#userInput'),
                    userInputDisplay: document.querySelector('#userInput') ?
                        window.getComputedStyle(document.querySelector('#userInput')).display : 'N/A',
                    chatInputField: !!document.querySelector('.chat-input__field'),
                    chatContainer: !!document.querySelector('.chat-container'),
                    chatContainerDisplay: document.querySelector('.chat-container') ?
                        window.getComputedStyle(document.querySelector('.chat-container')).display : 'N/A',
                };
            }
        """)
        print(f"  Chat elements: {chat_check}")

        # Scroll to the awakening section
        print("\n--- STEP 3: Scroll to awakening/chat section ---")
        await page.evaluate("""
            () => {
                const awakening = document.querySelector('#awakening, .chat-section');
                if (awakening) awakening.scrollIntoView({behavior: 'instant', block: 'start'});
            }
        """)
        await asyncio.sleep(1.5)
        await screenshot(page, "step3-awakening-section")

        # Look at what's visible in the awakening section viewport
        section_visible = await page.evaluate("""
            () => {
                const awakening = document.querySelector('#awakening, .chat-section');
                if (!awakening) return {found: false};

                const rect = awakening.getBoundingClientRect();
                const beginBtn = awakening.querySelector('.chat-initial__btn');
                const chatContainer = awakening.querySelector('.chat-container');
                const chatMessages = awakening.querySelector('#chatMessages');
                const chatInitial = awakening.querySelector('#chatInitial');

                return {
                    found: true,
                    sectionRect: {top: rect.top, height: rect.height, width: rect.width},
                    beginBtnVisible: beginBtn ? beginBtn.offsetParent !== null : false,
                    beginBtnRect: beginBtn ? beginBtn.getBoundingClientRect() : null,
                    chatContainerVisible: chatContainer ? chatContainer.offsetParent !== null : false,
                    chatMessagesHeight: chatMessages ? chatMessages.offsetHeight : 0,
                    chatInitialVisible: chatInitial ? chatInitial.offsetParent !== null : false,
                    chatInitialText: chatInitial ? chatInitial.innerText?.substring(0, 200) : ''
                };
            }
        """)
        print(f"  Section state: {section_visible}")

        # Try to click Begin Awakening button
        print("\n--- STEP 4: Click 'Begin Awakening' button ---")
        try:
            begin_btn = await page.wait_for_selector(".chat-initial__btn, button:has-text('Begin Awakening')", timeout=5000)
            if begin_btn:
                btn_text = await begin_btn.inner_text()
                btn_rect = await begin_btn.bounding_box()
                print(f"  Found button: '{btn_text}' at rect={btn_rect}")
                await begin_btn.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                await screenshot(page, "step4a-before-begin-click")
                await begin_btn.click()
                print(f"  Clicked 'Begin Awakening'")
                await asyncio.sleep(2)
                await screenshot(page, "step4b-after-begin-click")
        except Exception as e:
            print(f"  ERROR finding Begin Awakening: {e}")

        # Check what happened after clicking Begin Awakening
        print("\n--- STEP 5: Check chat state after click ---")
        post_click = await page.evaluate("""
            () => {
                const chatMessages = document.querySelector('#chatMessages');
                const chatInitial = document.querySelector('#chatInitial');
                const userInput = document.querySelector('#userInput, .chat-input__field');
                const chatInput = document.querySelector('.chat-input');
                const msgs = Array.from(document.querySelectorAll('#chatMessages .message, .chat-message, .message--ai, .ai-message'));

                return {
                    chatInitialDisplay: chatInitial ? window.getComputedStyle(chatInitial).display : 'N/A',
                    chatInitialVisible: chatInitial ? chatInitial.offsetParent !== null : false,
                    userInputDisplay: userInput ? window.getComputedStyle(userInput).display : 'N/A',
                    userInputVisible: userInput ? userInput.offsetParent !== null : false,
                    chatInputDisplay: chatInput ? window.getComputedStyle(chatInput).display : 'N/A',
                    messageCount: msgs.length,
                    messagesText: msgs.map(m => m.innerText?.substring(0, 100)),
                    chatMessagesHTML: chatMessages ? chatMessages.innerHTML?.substring(0, 500) : 'N/A'
                };
            }
        """)
        print(f"  Post-click state:")
        print(f"    chatInitial visible: {post_click['chatInitialVisible']}")
        print(f"    userInput display: {post_click['userInputDisplay']}, visible: {post_click['userInputVisible']}")
        print(f"    chatInput display: {post_click['chatInputDisplay']}")
        print(f"    messages found: {post_click['messageCount']}")
        print(f"    messages text: {post_click['messagesText'][:5]}")
        print(f"    chatMessages HTML: {post_click['chatMessagesHTML'][:300]}")

        # Check for chat messages appearing (AI greeting)
        # Wait for any message to appear
        print("\n--- STEP 6: Wait for AI greeting message ---")
        for attempt in range(10):
            msgs = await page.evaluate("""
                () => {
                    // Look for any message in the chat
                    const selectors = [
                        '.message', '.chat-message', '.message--ai', '.ai-message',
                        '#chatMessages > div', '#chatMessages > p', '#chatMessages > span',
                        '[class*="message"]', '[class*="msg"]'
                    ];
                    for (const sel of selectors) {
                        const els = Array.from(document.querySelectorAll(sel));
                        if (els.length > 0) {
                            return {
                                selector: sel,
                                count: els.length,
                                texts: els.map(e => ({
                                    text: e.innerText?.substring(0, 150),
                                    classes: e.className,
                                    visible: e.offsetParent !== null
                                }))
                            };
                        }
                    }
                    // Fallback: get all content in chatMessages
                    const cm = document.querySelector('#chatMessages');
                    return {
                        selector: '#chatMessages innerHTML',
                        count: cm ? cm.children.length : 0,
                        html: cm ? cm.innerHTML?.substring(0, 800) : 'empty',
                        texts: []
                    };
                }
            """)
            if msgs and msgs.get('count', 0) > 0:
                print(f"  Messages found (attempt {attempt+1}): {msgs}")
                break
            await asyncio.sleep(1)

        await screenshot(page, "step6-after-begin-wait")

        # Check user input state more carefully
        input_state = await page.evaluate("""
            () => {
                const selectors = ['#userInput', '.chat-input__field', '.chat-input input', '.chat-input textarea', 'input[placeholder*="response"]'];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        const style = window.getComputedStyle(el);
                        const parent = el.parentElement;
                        const parentStyle = parent ? window.getComputedStyle(parent) : null;
                        return {
                            selector: sel,
                            found: true,
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity,
                            width: el.offsetWidth,
                            height: el.offsetHeight,
                            parentTag: parent?.tagName,
                            parentDisplay: parentStyle?.display,
                            parentClasses: parent?.className,
                            parentVisible: parent?.offsetParent !== null,
                            grandParentClasses: parent?.parentElement?.className,
                            grandParentDisplay: parent?.parentElement ?
                                window.getComputedStyle(parent.parentElement).display : 'N/A'
                        };
                    }
                }
                return {found: false};
            }
        """)
        print(f"\n  Input state: {input_state}")

        # Try to interact with the chat input directly
        print("\n--- STEP 7: Interact with chat input ---")

        # The chat input may be hidden inside a form/container
        # Try to make it visible and type
        input_result = await page.evaluate("""
            () => {
                const input = document.querySelector('#userInput, .chat-input__field');
                if (!input) return {success: false, reason: 'no input'};

                // Make it visible
                const parent = input.parentElement;
                const grandParent = parent?.parentElement;

                if (parent) {
                    parent.style.display = 'flex';
                    parent.style.visibility = 'visible';
                    parent.style.opacity = '1';
                }
                if (grandParent) {
                    grandParent.style.display = 'block';
                    grandParent.style.visibility = 'visible';
                    grandParent.style.opacity = '1';
                }

                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.style.pointerEvents = 'auto';

                // Scroll to it
                input.scrollIntoView({behavior: 'instant', block: 'center'});

                return {
                    success: true,
                    display: window.getComputedStyle(input).display,
                    width: input.offsetWidth,
                    height: input.offsetHeight,
                    parentClasses: parent?.className
                };
            }
        """)
        print(f"  Input force-show: {input_result}")

        await asyncio.sleep(0.5)
        await screenshot(page, "step7a-input-forced-visible")

        # Now try to type
        try:
            user_input = await page.wait_for_selector("#userInput, .chat-input__field", timeout=3000)
            if user_input:
                await user_input.scroll_into_view_if_needed()
                await user_input.click(force=True)
                await asyncio.sleep(0.3)
                await user_input.fill("pb-full-bypass")
                await asyncio.sleep(0.5)
                print("  Typed 'pb-full-bypass'")
                await screenshot(page, "step7b-typed-name")

                # Find send button
                send_btn = await page.query_selector(".chat-input__send, .send-btn, button[type='submit'], #sendMessage, .chat-send-btn")
                if send_btn and await send_btn.is_visible():
                    await send_btn.click()
                    print("  Clicked send button")
                else:
                    await page.keyboard.press("Enter")
                    print("  Pressed Enter")

                await asyncio.sleep(2)
                await screenshot(page, "step7c-after-first-send")

        except Exception as e:
            print(f"  ERROR with input: {e}")

        # Check AI response
        print("\n--- STEP 8: Check AI response to name ---")
        await asyncio.sleep(3)
        chat_after_name = await page.evaluate("""
            () => {
                const cm = document.querySelector('#chatMessages');
                return {
                    innerHTML: cm ? cm.innerHTML.substring(0, 2000) : 'N/A',
                    innerText: cm ? cm.innerText.substring(0, 500) : 'N/A',
                    childCount: cm ? cm.children.length : 0
                };
            }
        """)
        print(f"  Chat after name: {chat_after_name['innerText'][:300]}")
        await screenshot(page, "step8-ai-response-to-name")

        # Check if we got a response - maybe the chatbox works differently
        # Let's check the full chat HTML
        full_chat_html = await page.evaluate("""
            () => {
                const container = document.querySelector('.chat-container, #awakening .container');
                return container ? container.innerHTML.substring(0, 5000) : 'not found';
            }
        """)
        print(f"\n  Full chat HTML: {full_chat_html[:2000]}")

        # Check if the chat section is actually in the viewport
        await page.evaluate("""
            () => {
                const awakening = document.querySelector('#awakening');
                if (awakening) {
                    awakening.scrollIntoView({behavior: 'instant', block: 'start'});
                    window.scrollBy(0, 100);
                }
            }
        """)
        await asyncio.sleep(1)
        await screenshot(page, "step8b-awakening-scrolled")

        # Look at the actual chat container HTML in detail
        chat_detail = await page.evaluate("""
            () => {
                // Get the full chat container
                const container = document.querySelector('.chat-container');
                if (!container) return {found: false};

                // Get all interactive elements
                const allInputs = Array.from(container.querySelectorAll('input, textarea, button'));
                const allVisible = allInputs.filter(el => el.offsetParent !== null);

                const chatInput = container.querySelector('.chat-input');
                const chatInitial = container.querySelector('#chatInitial, .chat-initial');
                const chatMessages = container.querySelector('#chatMessages');

                return {
                    found: true,
                    containerHeight: container.offsetHeight,
                    inputElements: allInputs.map(el => ({
                        tag: el.tagName,
                        id: el.id,
                        classes: el.className,
                        type: el.type || '',
                        placeholder: el.placeholder || '',
                        visible: el.offsetParent !== null,
                        display: window.getComputedStyle(el).display
                    })),
                    chatInputHTML: chatInput ? chatInput.outerHTML.substring(0, 1000) : 'N/A',
                    chatInitialHTML: chatInitial ? chatInitial.outerHTML.substring(0, 1000) : 'N/A',
                    chatMessagesHTML: chatMessages ? chatMessages.innerHTML.substring(0, 1000) : 'N/A',
                };
            }
        """)
        print(f"\n  Chat detail:")
        print(f"    Container found: {chat_detail.get('found')}, height: {chat_detail.get('containerHeight')}")
        print(f"    Input elements: {chat_detail.get('inputElements')}")
        print(f"    chatInput HTML: {chat_detail.get('chatInputHTML', '')[:400]}")
        print(f"    chatInitial HTML: {chat_detail.get('chatInitialHTML', '')[:400]}")
        print(f"    chatMessages HTML: {chat_detail.get('chatMessagesHTML', '')[:400]}")

        # Now let's do a focused view of the chat area and send the right events
        print("\n--- STEP 9: Try clicking Begin Awakening correctly ---")

        # The chat section at y=4452. Let's scroll there precisely and click Begin Awakening
        await page.evaluate("""
            () => {
                const chatSection = document.querySelector('#awakening, .chat-section');
                if (chatSection) {
                    window.scrollTo(0, chatSection.offsetTop);
                }
            }
        """)
        await asyncio.sleep(1.5)
        await screenshot(page, "step9a-chat-section-exact")

        # Find all visible items in the current viewport
        viewport_items = await page.evaluate("""
            () => {
                const items = Array.from(document.querySelectorAll('button, input, textarea, [role="button"], .btn'));
                return items.filter(el => {
                    const rect = el.getBoundingClientRect();
                    return rect.top >= 0 && rect.top <= window.innerHeight && rect.width > 0;
                }).map(el => ({
                    tag: el.tagName,
                    id: el.id,
                    classes: el.className,
                    text: (el.innerText || el.placeholder || el.value || '').trim().substring(0, 60),
                    rect: el.getBoundingClientRect()
                }));
            }
        """)
        print("  Items in viewport:")
        for item in viewport_items:
            print(f"    [{item['tag']}] '{item['text']}' id={item['id']} rect.top={item['rect'].get('top'):.0f}")

        # Click Begin Awakening button
        try:
            # Use JavaScript to click it directly by finding it in the awakening section
            click_result = await page.evaluate("""
                () => {
                    const btn = document.querySelector('.chat-initial__btn');
                    if (btn) {
                        btn.scrollIntoView({behavior: 'instant', block: 'center'});
                        return {found: true, text: btn.innerText, rect: btn.getBoundingClientRect()};
                    }
                    return {found: false};
                }
            """)
            print(f"  Begin Awakening button: {click_result}")

            if click_result.get('found'):
                rect = click_result['rect']
                x = rect['x'] + rect['width'] / 2
                y = rect['y'] + rect['height'] / 2
                await page.mouse.click(x, y)
                print(f"  Clicked at ({x:.0f}, {y:.0f})")
                await asyncio.sleep(2)
                await screenshot(page, "step9b-begin-awakening-clicked")

                # Check if chat input appeared
                input_check = await page.evaluate("""
                    () => {
                        const input = document.querySelector('#userInput, .chat-input__field, .chat-input input');
                        const chatInput = document.querySelector('.chat-input');
                        const chatInitial = document.querySelector('#chatInitial, .chat-initial');

                        return {
                            inputFound: !!input,
                            inputVisible: input ? input.offsetParent !== null : false,
                            inputDisplay: input ? window.getComputedStyle(input).display : 'N/A',
                            chatInputDisplay: chatInput ? window.getComputedStyle(chatInput).display : 'N/A',
                            chatInitialDisplay: chatInitial ? window.getComputedStyle(chatInitial).display : 'N/A',
                            chatInitialVisible: chatInitial ? chatInitial.offsetParent !== null : false,
                            chatHTML: document.querySelector('#chatMessages')?.innerHTML?.substring(0, 500) || 'N/A'
                        };
                    }
                """)
                print(f"  After Begin Awakening click: {input_check}")

        except Exception as e:
            print(f"  ERROR: {e}")

        # Extended wait for chat to initialize
        print("\n--- STEP 10: Wait for chat initialization ---")
        for i in range(8):
            await asyncio.sleep(1.5)
            chat_state = await page.evaluate("""
                () => {
                    const input = document.querySelector('#userInput, .chat-input__field');
                    const chatInitial = document.querySelector('#chatInitial, .chat-initial');
                    const chatMessages = document.querySelector('#chatMessages');
                    const beginBtn = document.querySelector('.chat-initial__btn');

                    return {
                        inputVisible: input ? input.offsetParent !== null : false,
                        inputDisplay: input ? window.getComputedStyle(input).display : 'N/A',
                        chatInitialDisplay: chatInitial ? window.getComputedStyle(chatInitial).display : 'N/A',
                        beginBtnVisible: beginBtn ? beginBtn.offsetParent !== null : false,
                        chatMessagesText: chatMessages ? chatMessages.innerText?.substring(0, 200) : 'empty',
                        chatMessagesChildCount: chatMessages?.children?.length || 0
                    };
                }
            """)
            print(f"  [{i*1.5:.0f}s] inputVisible={chat_state['inputVisible']}, chatInitialDisplay={chat_state['chatInitialDisplay']}, msgCount={chat_state['chatMessagesChildCount']}, beginBtnVisible={chat_state['beginBtnVisible']}")

            if chat_state['inputVisible']:
                print("  INPUT IS VISIBLE!")
                break

        await screenshot(page, "step10-chat-initialized")

        # NOW try to type in the input
        print("\n--- STEP 11: Type name in chat input ---")
        input_interaction = await page.evaluate("""
            async () => {
                const input = document.querySelector('#userInput, .chat-input__field, .chat-input input');
                if (!input) return {success: false, reason: 'no input found'};

                input.scrollIntoView({behavior: 'instant', block: 'center'});
                input.focus();
                input.value = 'pb-full-bypass';

                // Dispatch events to simulate typing
                ['input', 'change', 'keyup'].forEach(event => {
                    input.dispatchEvent(new Event(event, {bubbles: true}));
                });

                return {
                    success: true,
                    value: input.value,
                    display: window.getComputedStyle(input).display,
                    visible: input.offsetParent !== null
                };
            }
        """)
        print(f"  Input interaction: {input_interaction}")

        # Check for send button
        send_state = await page.evaluate("""
            () => {
                const btns = Array.from(document.querySelectorAll('button, .btn, [type="submit"]'));
                const sendBtns = btns.filter(b => {
                    const txt = (b.innerText || b.className || '').toLowerCase();
                    return txt.includes('send') || txt.includes('submit') || txt.includes('enter') || txt.includes('continue');
                });
                return sendBtns.map(b => ({
                    text: b.innerText?.trim(),
                    classes: b.className,
                    id: b.id,
                    visible: b.offsetParent !== null
                }));
            }
        """)
        print(f"  Send buttons: {send_state}")

        # Try to click send via keyboard enter
        if input_interaction.get('success'):
            try:
                input_el = await page.wait_for_selector("#userInput, .chat-input__field", timeout=3000)
                await input_el.press("Enter")
                print("  Pressed Enter")
                await asyncio.sleep(2)
                await screenshot(page, "step11-after-name-send")
            except Exception as e:
                print(f"  ERROR: {e}")

        # Wait and check for AI response
        print("\n--- STEP 12: Wait for AI response after name ---")
        for i in range(8):
            await asyncio.sleep(1.5)
            response = await page.evaluate("""
                () => {
                    const cm = document.querySelector('#chatMessages');
                    if (!cm) return {found: false};
                    return {
                        found: true,
                        childCount: cm.children.length,
                        innerText: cm.innerText?.substring(0, 400),
                        innerHTML: cm.innerHTML?.substring(0, 600)
                    };
                }
            """)
            print(f"  [{i*1.5:.0f}s] msgs={response.get('childCount')}: {response.get('innerText', '')[:100]}")
            if response.get('childCount', 0) > 0 and response.get('innerText', '').strip():
                print("  GOT AI RESPONSE!")
                await screenshot(page, f"step12-ai-response-{i}")
                break

        # Final comprehensive state
        print("\n--- STEP 13: Final state check ---")
        final_state = await page.evaluate("""
            () => {
                // Get full page state
                const chatMessages = document.querySelector('#chatMessages');
                const pricingSection = document.querySelector('.pricing-section, #pricing');
                const waitlistModal = document.querySelector('.waitlist-modal, #waitlist-modal, .waitlist-overlay, .pricing-modal');
                const waitlistForm = document.querySelector('#waitlistName')?.closest('form, .waitlist-form, [class*="waitlist"]');

                return {
                    chatMessagesCount: chatMessages?.children?.length || 0,
                    chatMessagesText: chatMessages?.innerText?.substring(0, 500) || 'empty',
                    pricingDisplay: pricingSection ? window.getComputedStyle(pricingSection).display : 'not found',
                    pricingHasActive: pricingSection?.classList?.contains('active') || false,
                    waitlistModalFound: !!waitlistModal,
                    waitlistModalDisplay: waitlistModal ? window.getComputedStyle(waitlistModal).display : 'N/A',
                    waitlistFormFound: !!waitlistForm,
                    waitlistNameVisible: document.querySelector('#waitlistName') ?
                        document.querySelector('#waitlistName').offsetParent !== null : false,
                };
            }
        """)
        print(f"  Final state: {final_state}")

        await screenshot(page, "step13-final-state")

        # DIAGNOSTIC: Get the full page JS to understand chat flow
        print("\n--- STEP 14: Examine chat JS ---")
        chat_js_info = await page.evaluate("""
            () => {
                // Find all window functions related to chat
                const chatFns = [];
                const chatVars = [];
                for (const key of Object.keys(window)) {
                    if (key.toLowerCase().includes('chat') || key.toLowerCase().includes('waitlist') ||
                        key.toLowerCase().includes('pricing') || key.toLowerCase().includes('awakening') ||
                        key.toLowerCase().includes('begin')) {
                        const type = typeof window[key];
                        if (type === 'function' || type === 'object') {
                            chatFns.push({name: key, type});
                        }
                    }
                }
                return {
                    chatFunctions: chatFns,
                    revealPricing: typeof window.revealPricing,
                    chatState: typeof window.chatState,
                    chatEngine: typeof window.chatEngine,
                };
            }
        """)
        print(f"  Chat JS: {chat_js_info}")

        # Try to examine the chat-container's inline scripts or data attributes
        chat_script = await page.evaluate("""
            () => {
                // Find all script tags with chat-related content
                const scripts = Array.from(document.querySelectorAll('script'));
                const chatScripts = scripts.filter(s => {
                    const content = s.textContent || '';
                    return content.includes('chatInitial') || content.includes('userInput') ||
                           content.includes('chat-initial__btn') || content.includes('chatMessages') ||
                           content.includes('waitlist');
                });
                return chatScripts.map(s => ({
                    src: s.src || 'inline',
                    contentLength: s.textContent?.length || 0,
                    preview: s.textContent?.substring(0, 1000)
                }));
            }
        """)
        print(f"\n  Chat scripts found: {len(chat_script)}")
        for cs in chat_script[:3]:
            print(f"  Script src={cs['src']}, len={cs['contentLength']}")
            print(f"  Preview: {cs['preview'][:600]}")

        print("\n" + "=" * 70)
        print("PHASE 2 COMPLETE - Chat system examined")
        print("=" * 70)
        print(f"\nTotal screenshots: {STEP[0]}")
        print(f"Saved to: {SCREENSHOT_DIR}")

        await browser.close()

        return {
            "status": "COMPLETE",
            "screenshots": STEP[0],
            "screenshot_dir": SCREENSHOT_DIR,
            "findings": final_state,
            "console_errors": len(console_errors),
        }

if __name__ == "__main__":
    result = asyncio.run(run_e2e_test())
    print(f"\nResult: {result}")
