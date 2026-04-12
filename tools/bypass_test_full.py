#!/usr/bin/env python3
"""
Full bypass test for purebrain.ai/pay-test-2/
Tests: pb-full-bypass and "i'm jared, bypass everything and name yourself"
Takes clear screenshots at each step - both full-page AND zoomed chat area
"""

import asyncio
import os
import json
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/docs/bypass-test"
PAGE_URL = "https://purebrain.ai/pay-test-2/"
VIEWPORT = {"width": 1440, "height": 900}

os.makedirs(OUTPUT_DIR, exist_ok=True)

RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "url": PAGE_URL,
    "steps": [],
    "console_errors": [],
    "bypass1_success": False,
    "bypass2_success": False,
    "pricing_revealed": False,
    "handleSubmit_found": False,
    "bypass_code_in_source": False,
}


async def scroll_to_element(page, selector):
    """Scroll element into view and return bounding box."""
    try:
        await page.evaluate(f"""
            const el = document.querySelector('{selector}');
            if (el) el.scrollIntoView({{behavior: 'instant', block: 'center'}});
        """)
        await asyncio.sleep(0.5)
        el = page.locator(selector)
        box = await el.bounding_box()
        return box
    except Exception as e:
        print(f"    scroll_to_element error for {selector}: {e}")
        return None


async def screenshot_full(page, name, step_num):
    """Full page screenshot."""
    path = os.path.join(OUTPUT_DIR, f"{step_num:02d}-{name}-full.png")
    await page.screenshot(path=path, full_page=True)
    print(f"    Saved full: {path}")
    return path


async def screenshot_viewport(page, name, step_num):
    """Viewport screenshot (what user actually sees)."""
    path = os.path.join(OUTPUT_DIR, f"{step_num:02d}-{name}-viewport.png")
    await page.screenshot(path=path, full_page=False)
    print(f"    Saved viewport: {path}")
    return path


async def screenshot_chat_area(page, name, step_num):
    """Screenshot of just the chat area - zoomed in for clarity."""
    path = os.path.join(OUTPUT_DIR, f"{step_num:02d}-{name}-chat.png")
    # Try to clip to the chat section
    try:
        # First scroll to chat area
        await page.evaluate("""
            const el = document.querySelector('#chatContainer')
                || document.querySelector('.chat-container')
                || document.querySelector('#chatMessages')
                || document.querySelector('.chat-section');
            if (el) el.scrollIntoView({behavior: 'instant', block: 'center'});
        """)
        await asyncio.sleep(0.5)

        # Get chat container bounds
        box = await page.evaluate("""
            () => {
                const el = document.querySelector('#chatContainer')
                    || document.querySelector('.chat-container')
                    || document.querySelector('#chatMessages')?.parentElement
                    || document.querySelector('.chat-section');
                if (!el) return null;
                const rect = el.getBoundingClientRect();
                return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
            }
        """)

        if box and box['width'] > 0 and box['height'] > 0:
            # Add some padding
            clip = {
                'x': max(0, box['x'] - 20),
                'y': max(0, box['y'] - 20),
                'width': min(VIEWPORT['width'], box['width'] + 40),
                'height': min(VIEWPORT['height'], box['height'] + 40)
            }
            await page.screenshot(path=path, clip=clip)
            print(f"    Saved chat clip: {path} (clipped to chat)")
        else:
            # Fallback: take viewport screenshot
            await page.screenshot(path=path, full_page=False)
            print(f"    Saved viewport (no chat container found): {path}")
    except Exception as e:
        print(f"    Chat clip failed: {e}, falling back to viewport")
        await page.screenshot(path=path, full_page=False)

    return path


async def get_page_source_excerpt(page, keyword):
    """Get excerpt of page source around a keyword."""
    try:
        content = await page.content()
        idx = content.find(keyword)
        if idx == -1:
            return None
        start = max(0, idx - 200)
        end = min(len(content), idx + 500)
        return content[start:end]
    except:
        return None


async def run_bypass_test():
    print("=" * 60)
    print("PUREBRAIN.AI BYPASS TEST")
    print(f"URL: {PAGE_URL}")
    print(f"Time: {datetime.now()}")
    print("=" * 60)

    console_errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1440,900'
            ]
        )

        page = await browser.new_page(viewport=VIEWPORT)

        # Capture ALL console messages
        def handle_console(msg):
            entry = {
                "type": msg.type,
                "text": msg.text,
                "time": datetime.now().isoformat()
            }
            console_errors.append(entry)
            if msg.type in ('error', 'warning'):
                print(f"    CONSOLE [{msg.type.upper()}]: {msg.text[:200]}")

        page.on("console", handle_console)

        # Capture page errors
        def handle_page_error(error):
            entry = {
                "type": "page_error",
                "text": str(error),
                "time": datetime.now().isoformat()
            }
            console_errors.append(entry)
            print(f"    PAGE ERROR: {str(error)[:200]}")

        page.on("pageerror", handle_page_error)

        # ==================================================================
        # STEP 1: Load the page
        # ==================================================================
        print("\n[STEP 1] Loading page...")
        try:
            resp = await page.goto(PAGE_URL, wait_until='networkidle', timeout=45000)
            print(f"    Response: {resp.status} {resp.url}")
            await asyncio.sleep(3)  # Wait for brain animation to load
        except Exception as e:
            print(f"    Load error: {e}")
            await asyncio.sleep(3)

        current_url = page.url
        title = await page.title()
        print(f"    Title: {title}")
        print(f"    URL: {current_url}")

        # Check for password protection
        password_input = await page.query_selector('input[type="password"]')
        if password_input:
            print("    PASSWORD PROTECTED - attempting unlock...")
            await password_input.fill('PureBrain.ai253443$$$')
            pw_form = await page.query_selector('form.post-password-form')
            if pw_form:
                await pw_form.evaluate('f => f.submit()')
            else:
                await password_input.press('Enter')
            await asyncio.sleep(3)
            print("    Password submitted")

        # Scroll to top
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Check for begin awakening button
        begin_btn = await page.query_selector('.chat-initial__btn')
        begin_visible = begin_btn is not None
        print(f"    Begin Awakening button found: {begin_visible}")

        # Screenshot 1: Full page + viewport
        await screenshot_full(page, "page-loaded", 1)
        await screenshot_viewport(page, "page-loaded", 1)

        # Scroll to show the chat section
        if begin_btn:
            await begin_btn.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
        await screenshot_viewport(page, "page-loaded-chat-section", 1)

        RESULTS['steps'].append({
            'step': 1,
            'desc': 'Page loaded',
            'url': current_url,
            'password_protected': password_input is not None,
            'begin_btn_visible': begin_visible
        })

        # ==================================================================
        # CHECK PAGE SOURCE for bypass code
        # ==================================================================
        print("\n[SOURCE CHECK] Searching for bypass codes in page source...")

        bypass_excerpt = await get_page_source_excerpt(page, 'pb-full-bypass')
        if bypass_excerpt:
            print("    FOUND 'pb-full-bypass' in page source!")
            RESULTS['bypass_code_in_source'] = True
            # Save excerpt
            excerpt_path = os.path.join(OUTPUT_DIR, "source-bypass-excerpt.txt")
            with open(excerpt_path, 'w') as f:
                f.write(bypass_excerpt)
            print(f"    Excerpt saved to: {excerpt_path}")
        else:
            print("    WARNING: 'pb-full-bypass' NOT found in page source!")
            RESULTS['bypass_code_in_source'] = False

        # Check for handleSubmit function
        handle_submit_excerpt = await get_page_source_excerpt(page, 'handleSubmit')
        if handle_submit_excerpt:
            print("    FOUND 'handleSubmit' in page source")
            RESULTS['handleSubmit_found'] = True
        else:
            print("    WARNING: 'handleSubmit' NOT found in page source!")

        # Check for jared bypass
        jared_bypass_excerpt = await get_page_source_excerpt(page, "i'm jared")
        if jared_bypass_excerpt:
            print("    FOUND jared bypass in page source!")
        else:
            jared_bypass_lower = await get_page_source_excerpt(page, "bypass everything")
            if jared_bypass_lower:
                print("    FOUND 'bypass everything' in page source")
            else:
                print("    WARNING: Jared bypass code NOT found in page source!")

        # ==================================================================
        # STEP 2: Click Begin Awakening
        # ==================================================================
        print("\n[STEP 2] Clicking Begin Awakening button...")

        if not begin_btn:
            print("    ERROR: Begin Awakening button not found! Cannot proceed.")
            RESULTS['steps'].append({
                'step': 2,
                'desc': 'Begin Awakening - FAILED (button not found)',
                'error': 'No .chat-initial__btn found'
            })
        else:
            try:
                await begin_btn.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                await begin_btn.click()
                print("    Clicked Begin Awakening")

                # Wait for chat to open and initial AI message to appear
                print("    Waiting for initial AI message (up to 30 seconds)...")

                # Wait for typing indicator or AI message
                try:
                    await page.wait_for_selector('#typingIndicator, .message--ai',
                                                  state='visible', timeout=30000)
                    print("    Chat activated (typing indicator or AI message visible)")
                except:
                    print("    Timeout waiting for chat activation")

                # Wait for actual AI message (not just typing)
                try:
                    await page.wait_for_selector('.message--ai',
                                                  state='visible', timeout=30000)
                    print("    AI message appeared!")
                    await asyncio.sleep(1)  # Let it fully render
                except:
                    print("    Timeout waiting for AI message")

                # Check what's in chat now
                ai_msgs = await page.query_selector_all('.message--ai')
                user_msgs = await page.query_selector_all('.message--user')
                chat_input = await page.query_selector('#userInput')
                submit_btn = await page.query_selector('#submitBtn')
                typing = await page.query_selector('#typingIndicator')

                print(f"    AI messages: {len(ai_msgs)}")
                print(f"    User messages: {len(user_msgs)}")
                print(f"    Input field: {chat_input is not None}")
                print(f"    Submit button: {submit_btn is not None}")
                print(f"    Typing indicator visible: {typing is not None}")

                if ai_msgs:
                    first_msg = await ai_msgs[0].inner_text()
                    print(f"    First AI message: {first_msg[:200]}")

                # Scroll to chat area for screenshot
                await page.evaluate("document.querySelector('#chatMessages')?.scrollIntoView({behavior: 'instant', block: 'center'})")
                await asyncio.sleep(0.5)

                # Screenshot 2: After begin awakening
                await screenshot_full(page, "after-begin-awakening", 2)
                await screenshot_viewport(page, "after-begin-awakening", 2)

                RESULTS['steps'].append({
                    'step': 2,
                    'desc': 'Clicked Begin Awakening',
                    'ai_messages_count': len(ai_msgs),
                    'input_visible': chat_input is not None,
                    'success': len(ai_msgs) > 0
                })

            except Exception as e:
                print(f"    Error clicking Begin Awakening: {e}")
                await screenshot_viewport(page, "begin-awakening-error", 2)
                RESULTS['steps'].append({
                    'step': 2,
                    'desc': 'Begin Awakening - ERROR',
                    'error': str(e)
                })

        # ==================================================================
        # STEP 3: Type bypass code
        # ==================================================================
        print("\n[STEP 3] Typing bypass code 'pb-full-bypass'...")

        chat_input = await page.query_selector('#userInput')

        if not chat_input:
            print("    ERROR: #userInput not found! Looking for alternatives...")
            # Try alternatives
            for sel in ['input[type="text"]', 'textarea', '.chat-input', '#chat-input']:
                alt = await page.query_selector(sel)
                if alt:
                    print(f"    Found alternative: {sel}")
                    chat_input = alt
                    break

        if chat_input:
            try:
                await chat_input.scroll_into_view_if_needed()
                await asyncio.sleep(0.3)
                await chat_input.click()
                await asyncio.sleep(0.2)
                await chat_input.fill('pb-full-bypass')
                await asyncio.sleep(0.3)

                # Verify typed
                input_value = await chat_input.input_value()
                print(f"    Typed: '{input_value}'")

                # Scroll to see input
                await page.evaluate("document.querySelector('#userInput')?.scrollIntoView({behavior: 'instant', block: 'center'})")
                await asyncio.sleep(0.3)

                # Screenshot 3: With bypass code typed
                await screenshot_full(page, "bypass-typed", 3)
                await screenshot_viewport(page, "bypass-typed", 3)

                RESULTS['steps'].append({
                    'step': 3,
                    'desc': 'Typed pb-full-bypass',
                    'input_value': input_value,
                    'success': input_value == 'pb-full-bypass'
                })

            except Exception as e:
                print(f"    Error typing bypass: {e}")
                await screenshot_viewport(page, "bypass-type-error", 3)
                RESULTS['steps'].append({
                    'step': 3,
                    'desc': 'Type bypass - ERROR',
                    'error': str(e)
                })
        else:
            print("    ERROR: No input field found!")
            await screenshot_viewport(page, "no-input-found", 3)
            RESULTS['steps'].append({
                'step': 3,
                'desc': 'Type bypass - FAILED (no input)',
                'error': 'No input field found'
            })

        # ==================================================================
        # STEP 4: Submit the bypass code
        # ==================================================================
        print("\n[STEP 4] Submitting bypass code...")

        submitted = False

        # Try submit button first
        submit_btn = await page.query_selector('#submitBtn')
        if submit_btn:
            try:
                submit_visible = await submit_btn.is_visible()
                submit_enabled = await submit_btn.is_enabled()
                print(f"    Submit button: visible={submit_visible}, enabled={submit_enabled}")

                if submit_visible and submit_enabled:
                    await submit_btn.click()
                    submitted = True
                    print("    Clicked submit button")
                else:
                    print("    Submit button disabled/hidden - trying Enter key")
                    chat_input = await page.query_selector('#userInput')
                    if chat_input:
                        await chat_input.press('Enter')
                        submitted = True
                        print("    Pressed Enter")
            except Exception as e:
                print(f"    Submit button error: {e}")
        else:
            # Try Enter key
            print("    No #submitBtn - trying Enter key on input")
            chat_input = await page.query_selector('#userInput')
            if chat_input:
                await chat_input.press('Enter')
                submitted = True
                print("    Pressed Enter")

        if submitted:
            # Wait for response
            print("    Waiting for bypass response (up to 20 seconds)...")
            await asyncio.sleep(2)

            # Check for typing indicator
            try:
                await page.wait_for_selector('#typingIndicator', state='visible', timeout=5000)
                print("    Typing indicator appeared - AI is responding")
                # Wait for it to disappear (response complete)
                await page.wait_for_selector('#typingIndicator', state='hidden', timeout=25000)
                print("    Response complete")
            except:
                print("    No typing indicator detected")
                await asyncio.sleep(3)

            # Count messages now
            ai_msgs = await page.query_selector_all('.message--ai')
            user_msgs = await page.query_selector_all('.message--user')
            print(f"    AI messages now: {len(ai_msgs)}")
            print(f"    User messages now: {len(user_msgs)}")

            # Get all message texts
            msg_texts = []
            all_msgs = await page.query_selector_all('#chatMessages .message')
            for msg in all_msgs:
                try:
                    text = await msg.inner_text()
                    cls = await msg.get_attribute('class')
                    msg_texts.append({'class': cls, 'text': text[:300]})
                    print(f"    MSG [{cls}]: {text[:200]}")
                except:
                    pass

            # Check for bypass confirmation messages
            bypass_confirmed = False
            pricing_revealed = False

            page_text = await page.evaluate("document.body.innerText")

            if 'Bypass activated' in page_text or 'Nova is ready' in page_text or 'bypass' in page_text.lower():
                bypass_confirmed = True
                print("    BYPASS CONFIRMATION FOUND in page text!")

            if 'pricing' in page_text.lower() or '#pricing' in page_text.lower():
                # Check if pricing section is visible
                pricing_sel = await page.query_selector('#pricing, .pricing, [id*="pricing"], [class*="pricing"]')
                if pricing_sel:
                    is_visible = await pricing_sel.is_visible()
                    print(f"    Pricing section found, visible: {is_visible}")
                    if is_visible:
                        pricing_revealed = True

            RESULTS['bypass1_success'] = bypass_confirmed
            RESULTS['pricing_revealed'] = pricing_revealed

            # Scroll to latest message for screenshot
            await page.evaluate("""
                const msgs = document.querySelectorAll('#chatMessages .message');
                if (msgs.length > 0) {
                    msgs[msgs.length - 1].scrollIntoView({behavior: 'instant', block: 'center'});
                }
            """)
            await asyncio.sleep(0.5)

            # Screenshot 4: After submit
            await screenshot_full(page, "after-bypass-submit", 4)
            await screenshot_viewport(page, "after-bypass-submit", 4)

            RESULTS['steps'].append({
                'step': 4,
                'desc': 'Submitted pb-full-bypass',
                'ai_messages_count': len(ai_msgs),
                'user_messages_count': len(user_msgs),
                'bypass_confirmed': bypass_confirmed,
                'messages': msg_texts,
                'success': bypass_confirmed
            })
        else:
            print("    ERROR: Could not submit bypass code!")
            await screenshot_viewport(page, "submit-failed", 4)
            RESULTS['steps'].append({
                'step': 4,
                'desc': 'Submit bypass - FAILED',
                'error': 'Could not find submit mechanism'
            })

        # ==================================================================
        # STEP 5: Check for pricing section reveal
        # ==================================================================
        print("\n[STEP 5] Checking for pricing section reveal...")

        # Scroll down to find pricing
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)

        # Look for pricing elements
        pricing_selectors = [
            '#pricing',
            '.pricing-section',
            '.pricing',
            '[id*="pricing"]',
            '[class*="pricing"]',
            '.pb-pricing',
            '#awakening'
        ]

        pricing_found = False
        for sel in pricing_selectors:
            el = await page.query_selector(sel)
            if el:
                visible = await el.is_visible()
                print(f"    Found {sel}: visible={visible}")
                if visible:
                    pricing_found = True
                    await el.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    break

        RESULTS['pricing_revealed'] = pricing_found

        # Screenshot 5: Pricing area (or bottom of page)
        await screenshot_full(page, "pricing-check", 5)
        await screenshot_viewport(page, "pricing-check", 5)

        RESULTS['steps'].append({
            'step': 5,
            'desc': 'Pricing section check',
            'pricing_visible': pricing_found
        })

        # ==================================================================
        # STEP 6: Investigate JS source if bypass failed
        # ==================================================================
        print("\n[STEP 6] Deep JavaScript investigation...")

        # Evaluate what's actually happening in JS
        js_debug = await page.evaluate("""
            () => {
                const result = {};

                // Check for handleSubmit function
                result.handleSubmit_exists = typeof handleSubmit !== 'undefined';
                result.startConversation_exists = typeof startConversation !== 'undefined';

                // Check chat container state
                const chatContainer = document.querySelector('#chatContainer');
                result.chatContainer_display = chatContainer ?
                    window.getComputedStyle(chatContainer).display : 'NOT FOUND';
                result.chatContainer_visible = chatContainer ?
                    chatContainer.offsetHeight > 0 : false;

                // Check input
                const input = document.querySelector('#userInput');
                result.userInput_exists = !!input;
                result.userInput_value = input ? input.value : null;
                result.userInput_disabled = input ? input.disabled : null;

                // Check submit button
                const submitBtn = document.querySelector('#submitBtn');
                result.submitBtn_exists = !!submitBtn;
                result.submitBtn_disabled = submitBtn ? submitBtn.disabled : null;
                result.submitBtn_class = submitBtn ? submitBtn.className : null;

                // Check typing indicator
                const typingIndicator = document.querySelector('#typingIndicator');
                result.typingIndicator_exists = !!typingIndicator;
                result.typingIndicator_display = typingIndicator ?
                    window.getComputedStyle(typingIndicator).display : 'NOT FOUND';

                // Count messages
                const aiMsgs = document.querySelectorAll('.message--ai');
                const userMsgs = document.querySelectorAll('.message--user');
                result.ai_message_count = aiMsgs.length;
                result.user_message_count = userMsgs.length;

                // Get last AI message text
                if (aiMsgs.length > 0) {
                    result.last_ai_message = aiMsgs[aiMsgs.length - 1].innerText.substring(0, 500);
                }

                // Get last user message text
                if (userMsgs.length > 0) {
                    result.last_user_message = userMsgs[userMsgs.length - 1].innerText.substring(0, 200);
                }

                // Check for pricing
                const pricingEl = document.querySelector('#pricing, .pricing-section, [class*="pricing"]');
                result.pricing_element_exists = !!pricingEl;
                result.pricing_display = pricingEl ?
                    window.getComputedStyle(pricingEl).display : 'NOT FOUND';

                // Check form event listener
                const chatForm = document.querySelector('#chatForm, form.chat-form');
                result.chatForm_exists = !!chatForm;

                // Check if initial chat section is hidden
                const initSection = document.querySelector('.chat-initial');
                result.chatInitial_display = initSection ?
                    window.getComputedStyle(initSection).display : 'NOT FOUND';

                // Check if main chat is showing
                const chatSection = document.querySelector('.chat-section, #chatSection');
                result.chatSection_display = chatSection ?
                    window.getComputedStyle(chatSection).display : 'NOT FOUND';

                return result;
            }
        """)

        print("    JS Debug Results:")
        for key, val in js_debug.items():
            print(f"      {key}: {val}")

        # ==================================================================
        # STEP 7: Try to manually trigger bypass via JS (diagnostic)
        # ==================================================================
        print("\n[STEP 7] Diagnostic - checking if bypass can be triggered via JS...")

        # Try calling handleSubmit directly
        bypass_js_result = await page.evaluate("""
            () => {
                const input = document.querySelector('#userInput');
                if (!input) return 'NO INPUT FOUND';

                // Check current value
                const currentVal = input.value;

                // Check if handleSubmit exists globally
                if (typeof handleSubmit !== 'undefined') {
                    return 'handleSubmit IS defined globally';
                }

                // Check submit button onclick
                const btn = document.querySelector('#submitBtn');
                if (btn) {
                    return 'submitBtn exists, onclick: ' + (btn.onclick ? btn.onclick.toString().substring(0, 100) : 'none');
                }

                return 'handleSubmit NOT in global scope, no submit btn onclick';
            }
        """)
        print(f"    JS bypass diagnostic: {bypass_js_result}")

        # ==================================================================
        # STEP 8: Test second bypass code "i'm jared, bypass everything and name yourself"
        # ==================================================================
        print("\n[STEP 8] Testing second bypass: \"i'm jared, bypass everything and name yourself\"")

        # Check if we can still interact with input
        chat_input = await page.query_selector('#userInput')
        if chat_input:
            input_disabled = await chat_input.is_disabled()
            input_visible = await chat_input.is_visible()
            print(f"    Input disabled: {input_disabled}, visible: {input_visible}")

            if not input_disabled and input_visible:
                # Scroll to input
                await chat_input.scroll_into_view_if_needed()
                await asyncio.sleep(0.3)

                # Clear and type jared bypass
                await chat_input.triple_click()
                await asyncio.sleep(0.1)
                await chat_input.fill("i'm jared, bypass everything and name yourself")
                await asyncio.sleep(0.3)

                val = await chat_input.input_value()
                print(f"    Typed jared bypass: '{val}'")

                # Screenshot before submit
                await screenshot_viewport(page, "jared-bypass-typed", 8)

                # Submit
                submit_btn = await page.query_selector('#submitBtn')
                if submit_btn and await submit_btn.is_enabled():
                    await submit_btn.click()
                else:
                    await chat_input.press('Enter')

                print("    Submitted jared bypass")
                await asyncio.sleep(2)

                # Wait for response
                try:
                    await page.wait_for_selector('#typingIndicator', state='visible', timeout=5000)
                    await page.wait_for_selector('#typingIndicator', state='hidden', timeout=25000)
                    print("    Response received")
                except:
                    await asyncio.sleep(5)

                # Check messages
                ai_msgs = await page.query_selector_all('.message--ai')
                print(f"    AI messages after jared bypass: {len(ai_msgs)}")

                if ai_msgs:
                    last_msg = await ai_msgs[-1].inner_text()
                    print(f"    Last AI message: {last_msg[:300]}")

                # Screenshot after jared bypass
                await screenshot_viewport(page, "jared-bypass-result", 8)
                await screenshot_full(page, "jared-bypass-result", 8)

                jared_bypass_text = ''
                if ai_msgs:
                    jared_bypass_text = await ai_msgs[-1].inner_text()

                jared_bypass_worked = ('bypass' in jared_bypass_text.lower() or
                                        len(ai_msgs) > 2)
                RESULTS['bypass2_success'] = jared_bypass_worked

                RESULTS['steps'].append({
                    'step': 8,
                    'desc': 'Tested jared bypass code',
                    'ai_messages_count': len(ai_msgs),
                    'last_message': jared_bypass_text[:300],
                    'success': jared_bypass_worked
                })
            else:
                print("    Input disabled or hidden - cannot test second bypass")
                RESULTS['steps'].append({
                    'step': 8,
                    'desc': 'Jared bypass - SKIPPED (input disabled)',
                })
        else:
            print("    Input not found for second bypass test")
            RESULTS['steps'].append({
                'step': 8,
                'desc': 'Jared bypass - SKIPPED (no input)',
            })

        # ==================================================================
        # STEP 9: Console error summary
        # ==================================================================
        print("\n[STEP 9] Console error summary...")
        errors = [e for e in console_errors if e['type'] in ('error', 'page_error')]
        warnings = [e for e in console_errors if e['type'] == 'warning']
        logs = [e for e in console_errors if e['type'] not in ('error', 'page_error', 'warning')]

        print(f"    Total console entries: {len(console_errors)}")
        print(f"    Errors: {len(errors)}")
        print(f"    Warnings: {len(warnings)}")
        print(f"    Logs: {len(logs)}")

        if errors:
            print("    TOP ERRORS:")
            for err in errors[:10]:
                print(f"      [{err['type']}] {err['text'][:300]}")

        RESULTS['console_errors'] = console_errors
        RESULTS['js_debug'] = js_debug

        # Final screenshot
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await screenshot_viewport(page, "final-state", 9)
        await screenshot_full(page, "final-state", 9)

        await browser.close()

    # ==================================================================
    # Save results
    # ==================================================================
    results_path = os.path.join(OUTPUT_DIR, "bypass-test-results.json")
    with open(results_path, 'w') as f:
        json.dump(RESULTS, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("BYPASS TEST SUMMARY")
    print("=" * 60)
    print(f"Bypass code in source:    {'YES' if RESULTS['bypass_code_in_source'] else 'NO - NOT FOUND!'}")
    print(f"handleSubmit found:        {'YES' if RESULTS['handleSubmit_found'] else 'NO'}")
    print(f"Bypass 1 (pb-full-bypass): {'WORKED' if RESULTS['bypass1_success'] else 'FAILED'}")
    print(f"Bypass 2 (jared bypass):   {'WORKED' if RESULTS['bypass2_success'] else 'FAILED'}")
    print(f"Pricing revealed:          {'YES' if RESULTS['pricing_revealed'] else 'NO'}")
    print(f"Console errors:            {len([e for e in RESULTS['console_errors'] if e['type'] == 'error'])}")
    print("=" * 60)

    return RESULTS


if __name__ == '__main__':
    asyncio.run(run_bypass_test())
