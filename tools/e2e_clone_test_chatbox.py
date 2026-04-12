#!/usr/bin/env python3
"""
Full E2E chatbox test for https://purebrain.ai/homepage-clone-test/
- Enter "pb-full-bypass" as name to trigger bypass flow
- Navigate through chatbox conversation
- When pricing appears, select a tier
- Fill out waitlist form
- Submit and check confirmation

Screenshots at every step saved to:
/home/jared/projects/AI-CIV/aether/exports/screenshots/clone-test-e2e-20260310/
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
    print(f"  [SCREENSHOT {n}] {label} -> {path}")
    return path

async def wait_and_screenshot(page, label, seconds=2):
    await asyncio.sleep(seconds)
    return await screenshot(page, label)

async def scroll_to_chat(page):
    """Scroll to chat/awakening section"""
    await page.evaluate("""
        const chat = document.querySelector('#chat, #awakening, .ptc-wrapper, #ptc-chat-wrapper, .awakening-section');
        if (chat) chat.scrollIntoView({behavior: 'smooth', block: 'center'});
    """)
    await asyncio.sleep(1.5)

async def find_chatbox_input(page):
    """Find the chatbox input element"""
    selectors = [
        "#ptc-input",
        "textarea.ptc-input",
        ".ptc-input",
        "#chat-input",
        "textarea[placeholder*='name']",
        "textarea[placeholder*='Name']",
        "input[placeholder*='name']",
        "input[placeholder*='Name']",
        ".chat-input",
        "#awakening-input",
    ]
    for sel in selectors:
        try:
            el = await page.wait_for_selector(sel, timeout=2000)
            if el:
                visible = await el.is_visible()
                if visible:
                    print(f"  Found chatbox input: {sel}")
                    return el, sel
        except:
            pass
    return None, None

async def find_send_button(page):
    """Find the send button"""
    selectors = [
        "#ptc-send-btn",
        ".ptc-send-btn",
        "button.ptc-send",
        "#send-btn",
        ".send-btn",
        "button[aria-label*='send']",
        "button[aria-label*='Send']",
    ]
    for sel in selectors:
        try:
            el = await page.query_selector(sel)
            if el:
                visible = await el.is_visible()
                if visible:
                    print(f"  Found send button: {sel}")
                    return el, sel
        except:
            pass
    return None, None

async def get_ai_messages(page):
    """Get all current AI messages"""
    msgs = await page.evaluate("""
        () => {
            const aiMsgs = document.querySelectorAll('.ptc-msg--ai, .ptc-ai-msg, .chat-msg--ai, .ai-message');
            return Array.from(aiMsgs).map(m => m.innerText.trim()).filter(t => t.length > 0);
        }
    """)
    return msgs

async def type_and_send(page, text, input_sel="#ptc-input"):
    """Type text into input and click send (or press Enter)"""
    try:
        inp = await page.wait_for_selector(input_sel, timeout=5000)
        await inp.click()
        await asyncio.sleep(0.3)
        await inp.fill(text)
        await asyncio.sleep(0.3)

        # Try send button first
        send_btn = await page.query_selector("#ptc-send-btn, .ptc-send-btn, button.send-btn")
        if send_btn and await send_btn.is_visible():
            await send_btn.click()
        else:
            await page.keyboard.press("Enter")

        print(f"  Sent: '{text}'")
        await asyncio.sleep(0.5)
        return True
    except Exception as e:
        print(f"  ERROR sending '{text}': {e}")
        return False

async def wait_for_ai_response(page, timeout=15):
    """Wait for new AI message to appear"""
    start = time.time()
    initial_count = len(await get_ai_messages(page))

    while time.time() - start < timeout:
        current_count = len(await get_ai_messages(page))
        if current_count > initial_count:
            await asyncio.sleep(1.5)  # Wait for full message
            return True
        await asyncio.sleep(0.5)
    return False

async def check_pricing_visible(page):
    """Check if pricing section is visible"""
    result = await page.evaluate("""
        () => {
            const ps = document.querySelector('.pricing-section, #pricing, .ptc-pricing');
            if (!ps) return {found: false};
            const style = window.getComputedStyle(ps);
            return {
                found: true,
                display: style.display,
                visible: style.display !== 'none' && style.visibility !== 'hidden',
                hasActive: ps.classList.contains('active'),
                height: ps.offsetHeight
            };
        }
    """)
    return result

async def check_for_pricing_cards(page):
    """Look for pricing tier buttons/cards"""
    result = await page.evaluate("""
        () => {
            // Look for any tier buttons or pricing cards
            const awakened = document.querySelector('.pricing-card--featured, [data-tier], .tier-btn, .ptc-tier');
            const allBtns = Array.from(document.querySelectorAll('button, .btn, [role="button"]'));
            const tierBtns = allBtns.filter(b => {
                const txt = b.innerText || b.textContent || '';
                return txt.includes('Awakened') || txt.includes('Awakening') ||
                       txt.includes('Reserve') || txt.includes('Begin') ||
                       txt.includes('Select') || txt.includes('Choose') ||
                       txt.includes('tier') || txt.includes('Tier');
            }).map(b => ({text: b.innerText?.trim(), classes: b.className, visible: b.offsetParent !== null}));

            return {
                hasPricingCard: !!awakened,
                tierButtons: tierBtns.slice(0, 10)
            };
        }
    """)
    return result

async def check_for_waitlist_form(page):
    """Check if waitlist form is visible"""
    result = await page.evaluate("""
        () => {
            // Look for form, modal, or popup
            const form = document.querySelector('#waitlist-form, .waitlist-form, .modal-form, .popup-form, form.intake-form, .ptc-form');
            const modal = document.querySelector('.modal, .popup, .overlay, #waitlist-modal, .waitlist-modal');
            const nameInput = document.querySelector('input[name="name"], input[placeholder*="Name"], input[placeholder*="name"]');
            const emailInput = document.querySelector('input[type="email"], input[name="email"]');

            return {
                hasForm: !!form,
                hasModal: !!modal,
                hasNameInput: !!nameInput,
                hasEmailInput: !!emailInput,
                formVisible: form ? form.offsetParent !== null : false,
                modalVisible: modal ? window.getComputedStyle(modal).display !== 'none' : false,
                nameInputVisible: nameInput ? nameInput.offsetParent !== null : false,
                emailInputVisible: emailInput ? emailInput.offsetParent !== null : false,
            };
        }
    """)
    return result

async def find_visible_inputs(page):
    """Find all currently visible form inputs"""
    result = await page.evaluate("""
        () => {
            const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
            return inputs.filter(i => {
                const style = window.getComputedStyle(i);
                return style.display !== 'none' && style.visibility !== 'hidden' && i.offsetParent !== null;
            }).map(i => ({
                tag: i.tagName,
                type: i.type || '',
                name: i.name || '',
                placeholder: i.placeholder || '',
                id: i.id || '',
                classes: i.className || '',
                value: i.value || ''
            }));
        }
    """)
    return result

async def find_visible_buttons(page):
    """Find all visible buttons"""
    result = await page.evaluate("""
        () => {
            const btns = Array.from(document.querySelectorAll('button, [role="button"], .btn, input[type="submit"], input[type="button"]'));
            return btns.filter(b => {
                const style = window.getComputedStyle(b);
                return style.display !== 'none' && style.visibility !== 'hidden' && b.offsetParent !== null;
            }).map(b => ({
                text: (b.innerText || b.textContent || b.value || '').trim().substring(0, 80),
                id: b.id || '',
                classes: b.className || '',
                type: b.type || '',
                disabled: b.disabled
            })).filter(b => b.text.length > 0);
        }
    """)
    return result

async def check_console_errors(page):
    """Get stored console errors"""
    return await page.evaluate("""
        () => window._consoleErrors || []
    """)

async def run_e2e_test():
    print("=" * 60)
    print("E2E CHATBOX TEST: homepage-clone-test")
    print("=" * 60)

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

        # Capture console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error", "warning"] else None)

        # Inject console error collector
        await page.add_init_script("""
            window._consoleErrors = [];
            const origError = console.error;
            console.error = function(...args) {
                window._consoleErrors.push(args.join(' '));
                origError.apply(console, args);
            };
        """)

        print("\n[STEP 1] Loading page...")
        try:
            await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"  WARNING: Page load exception: {e}")

        await asyncio.sleep(3)
        await screenshot(page, "01-page-loaded")
        print(f"  Page title: {await page.title()}")

        # Check for password gate
        pw_gate = await page.query_selector("#pwbox-0, input[name=post_password]")
        if pw_gate:
            print("  ERROR: Page is PASSWORD PROTECTED")
            await screenshot(page, "02-password-gate")
            await browser.close()
            return {"status": "BLOCKED", "reason": "password_gate"}

        print("\n[STEP 2] Checking page structure...")
        pricing_state = await check_pricing_visible(page)
        print(f"  Pricing section: {pricing_state}")

        # Scroll down to find chatbox
        print("\n[STEP 3] Looking for chatbox...")
        await page.evaluate("window.scrollTo(0, 4000)")
        await asyncio.sleep(1)

        # Try to find chatbox
        chatbox_info = await page.evaluate("""
            () => {
                const chatWrapper = document.querySelector('#pay-test-post-payment, #ptc-chat-wrapper, .ptc-wrapper, #awakening .chat-container, .chatbox-wrapper');
                const input = document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input');
                const inputRow = document.querySelector('#ptc-input-row, .ptc-input-row');

                return {
                    chatWrapperFound: !!chatWrapper,
                    chatWrapperDisplay: chatWrapper ? window.getComputedStyle(chatWrapper).display : 'N/A',
                    inputFound: !!input,
                    inputDisplay: input ? window.getComputedStyle(input).display : 'N/A',
                    inputRowFound: !!inputRow,
                    inputRowDisplay: inputRow ? window.getComputedStyle(inputRow).display : 'N/A',
                };
            }
        """)
        print(f"  Chatbox info: {chatbox_info}")

        await screenshot(page, "03-scroll-to-chat-area")

        # Try scrolling to the awakening/chat section
        await scroll_to_chat(page)
        await asyncio.sleep(2)
        await screenshot(page, "04-scrolled-to-chat")

        # Check all visible buttons in the current view
        visible_btns = await find_visible_buttons(page)
        print(f"\n  Visible buttons (first 15):")
        for b in visible_btns[:15]:
            print(f"    [{b['id']}] '{b['text']}' classes={b['classes'][:50]}")

        # Try to find and interact with the chatbox
        # First check if there's an "Awaken" button to start the chatbox
        print("\n[STEP 4] Looking for chat initiation...")

        # Try clicking "Awaken Your PURE BRAIN" or similar CTA to open chatbox
        awaken_btns = await page.evaluate("""
            () => {
                const btns = Array.from(document.querySelectorAll('button, a, [role="button"], .btn'));
                return btns.filter(b => {
                    const txt = (b.innerText || b.textContent || '').toLowerCase();
                    return txt.includes('awaken') || txt.includes('begin') || txt.includes('start') ||
                           txt.includes('chat') || txt.includes('open') || txt.includes('join');
                }).map(b => ({
                    text: (b.innerText || b.textContent || '').trim().substring(0, 80),
                    id: b.id,
                    classes: b.className,
                    href: b.href || '',
                    visible: b.offsetParent !== null,
                    tag: b.tagName
                })).filter(b => b.visible);
            }
        """)
        print(f"  Awaken/begin buttons found:")
        for b in awaken_btns[:8]:
            print(f"    [{b['tag']}] '{b['text']}' id={b['id']}")

        # Look for the main "Awaken" CTA button and click it
        # The chat might not be visible without clicking something
        main_cta_clicked = False

        # Try scrolling to the chatbox section specifically
        chat_section = await page.evaluate("""
            () => {
                // Look for the awakening section
                const sections = ['#awakening', '.awakening-section', '#chat-section', '.chat-section'];
                for (const sel of sections) {
                    const el = document.querySelector(sel);
                    if (el) {
                        el.scrollIntoView({behavior: 'smooth', block: 'center'});
                        return {found: sel, offsetTop: el.offsetTop};
                    }
                }
                return {found: null};
            }
        """)
        print(f"  Chat section scroll: {chat_section}")
        await asyncio.sleep(2)
        await screenshot(page, "05-chat-section")

        # Try directly looking for the chatbox input
        input_el, input_sel = await find_chatbox_input(page)

        if not input_el:
            print("  Chatbox input not yet visible - trying to activate...")
            # Try clicking "Awaken Your PURE BRAIN" button
            try:
                awaken_btn = await page.wait_for_selector(
                    "button:has-text('Awaken'), a:has-text('Awaken'), button:has-text('Begin Awakening'), a:has-text('Begin Awakening')",
                    timeout=3000
                )
                if awaken_btn:
                    await awaken_btn.click()
                    print("  Clicked Awaken button")
                    await asyncio.sleep(2)
                    await screenshot(page, "06-after-awaken-click")
            except:
                print("  No Awaken button found")

            # Try again after potential click
            input_el, input_sel = await find_chatbox_input(page)

        if input_el:
            print(f"  Found chatbox input: {input_sel}")
            await screenshot(page, "07-chatbox-visible")
        else:
            # More aggressive search - look at what's in the DOM
            print("  Still no input - checking DOM for any chat elements...")
            chat_state = await page.evaluate("""
                () => {
                    const allInputs = Array.from(document.querySelectorAll('input, textarea'));
                    const ptcElements = Array.from(document.querySelectorAll('[id*="ptc"], [class*="ptc"]'));
                    const chatElements = Array.from(document.querySelectorAll('[id*="chat"], [class*="chat"]'));

                    return {
                        inputCount: allInputs.length,
                        allInputs: allInputs.map(i => ({
                            id: i.id, type: i.type, placeholder: i.placeholder,
                            classes: i.className, visible: i.offsetParent !== null,
                            display: window.getComputedStyle(i).display
                        })),
                        ptcElementIds: ptcElements.map(e => e.id || e.className).slice(0, 10),
                        chatElementIds: chatElements.map(e => e.id || e.className).slice(0, 10)
                    };
                }
            """)
            print(f"  DOM state: {chat_state}")

        # Check if we need to try with ?bypass=true
        print("\n[STEP 5] Trying with bypass URL parameter...")
        try:
            await page.goto(URL + "?bypass=true", wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"  WARNING: {e}")
        await asyncio.sleep(3)

        # Check for payment bypass - the page might show the chatbox directly
        bypass_state = await page.evaluate("""
            () => {
                const postPayment = document.querySelector('#pay-test-post-payment, .post-payment-chat');
                const inputRow = document.querySelector('#ptc-input-row');
                const input = document.querySelector('#ptc-input');
                return {
                    postPaymentFound: !!postPayment,
                    postPaymentDisplay: postPayment ? window.getComputedStyle(postPayment).display : 'N/A',
                    inputRowFound: !!inputRow,
                    inputRowDisplay: inputRow ? window.getComputedStyle(inputRow).display : 'N/A',
                    inputFound: !!input,
                    inputVisible: input ? input.offsetParent !== null : false
                };
            }
        """)
        print(f"  Bypass state: {bypass_state}")
        await screenshot(page, "08-bypass-url-page")

        # Try clicking the "Begin Awakening" or main hero CTA
        print("\n[STEP 6] Looking for chat trigger buttons...")
        all_visible_btns = await find_visible_buttons(page)
        print("  All visible buttons:")
        for b in all_visible_btns[:20]:
            if b['text']:
                print(f"    id={b['id']} | '{b['text'][:60]}' | classes={b['classes'][:40]}")

        # Check if there's a chatbox section on page
        chat_on_page = await page.evaluate("""
            () => {
                // Check all elements that might be a chat interface
                const candidates = [
                    document.querySelector('#pay-test-post-payment'),
                    document.querySelector('#ptc-chat-wrapper'),
                    document.querySelector('.ptc-wrapper'),
                    document.querySelector('#ptc-input'),
                    document.querySelector('.ptc-input'),
                    document.querySelector('#awakening .ptc-messages'),
                    document.querySelector('.ptc-messages'),
                ];
                return candidates.map((el, i) => ({
                    index: i,
                    found: !!el,
                    display: el ? window.getComputedStyle(el).display : null,
                    id: el ? el.id : null,
                    classes: el ? el.className : null,
                    offsetTop: el ? el.offsetTop : null,
                    height: el ? el.offsetHeight : null
                }));
            }
        """)
        print("\n  Chat elements on page:")
        for c in chat_on_page:
            if c['found']:
                print(f"    [{c['index']}] id={c['id']} display={c['display']} h={c['height']} top={c['offsetTop']}")

        # Try scrolling to the awakening chat section
        await page.evaluate("""
            () => {
                const el = document.querySelector('#awakening, .awakening-section, .ptc-messages, #ptc-chat-wrapper');
                if (el) {
                    el.scrollIntoView({behavior: 'instant', block: 'start'});
                }
            }
        """)
        await asyncio.sleep(1.5)
        await screenshot(page, "09-scroll-to-ptc")

        # Check if there's a visible chatbox now
        input_el, input_sel = await find_chatbox_input(page)

        if not input_el:
            print("\n  Chatbox input still not found. Checking for alternative chat interfaces...")
            # Maybe the chat is at a specific location on page - look at the awakening section
            awakening_info = await page.evaluate("""
                () => {
                    const aw = document.querySelector('#awakening, .awakening-section');
                    if (!aw) return {found: false};

                    // Get all interactive elements inside it
                    const btns = Array.from(aw.querySelectorAll('button, input, textarea'));
                    const allInputs = Array.from(document.querySelectorAll('input, textarea')).map(i => ({
                        id: i.id, placeholder: i.placeholder, type: i.type,
                        display: window.getComputedStyle(i).display,
                        visibility: window.getComputedStyle(i).visibility,
                        offsetParent: i.offsetParent !== null,
                        width: i.offsetWidth,
                        height: i.offsetHeight
                    }));

                    return {
                        found: true,
                        offsetTop: aw.offsetTop,
                        height: aw.offsetHeight,
                        innerBtns: btns.map(b => ({tag: b.tagName, id: b.id, text: b.innerText || b.placeholder, type: b.type})),
                        allPageInputs: allInputs
                    };
                }
            """)
            print(f"  Awakening section: found={awakening_info.get('found')}, top={awakening_info.get('offsetTop')}, h={awakening_info.get('height')}")
            if awakening_info.get('allPageInputs'):
                print("  All inputs on page:")
                for inp in awakening_info['allPageInputs']:
                    print(f"    id={inp['id']} type={inp['type']} placeholder='{inp['placeholder']}' display={inp['display']} visible={inp['offsetParent']} {inp['width']}x{inp['height']}")

        # Now try the actual chatbox interaction
        # The chatbox might be in the page but we need to type "pb-full-bypass" as the name
        # The input might only become visible after the page's chat system starts

        print("\n[STEP 7] Attempting to interact with chatbox...")

        # Try scrolling to where the chat SHOULD be based on earlier audit (y ~4452-5392)
        await page.evaluate("window.scrollTo(0, 4800)")
        await asyncio.sleep(1.5)
        await screenshot(page, "10-scroll-y4800-chatbox-area")

        # Try to find any input
        inputs_at_4800 = await page.evaluate("""
            () => {
                const inputs = Array.from(document.querySelectorAll('input, textarea'));
                return inputs.filter(i => {
                    const rect = i.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.top < window.innerHeight;
                }).map(i => ({
                    id: i.id,
                    type: i.type,
                    placeholder: i.placeholder,
                    classes: i.className,
                    rect: i.getBoundingClientRect()
                }));
            }
        """)
        print(f"  Inputs visible at y4800: {inputs_at_4800}")

        # Get the ptc input visibility details
        ptc_state = await page.evaluate("""
            () => {
                const input = document.querySelector('#ptc-input, textarea.ptc-input');
                if (!input) return {found: false};
                const rect = input.getBoundingClientRect();
                const style = window.getComputedStyle(input);
                return {
                    found: true,
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    pointerEvents: style.pointerEvents,
                    width: input.offsetWidth,
                    height: input.offsetHeight,
                    offsetTop: input.offsetTop,
                    parentDisplay: window.getComputedStyle(input.parentElement).display,
                    parentVisibility: window.getComputedStyle(input.parentElement).visibility,
                    parentId: input.parentElement?.id,
                    parentClasses: input.parentElement?.className,
                    ancestors: (() => {
                        let el = input.parentElement;
                        const chain = [];
                        let depth = 0;
                        while (el && depth < 6) {
                            const s = window.getComputedStyle(el);
                            chain.push({
                                id: el.id,
                                classes: el.className?.substring(0, 40),
                                display: s.display,
                                visibility: s.visibility,
                                opacity: s.opacity
                            });
                            el = el.parentElement;
                            depth++;
                        }
                        return chain;
                    })()
                };
            }
        """)
        print(f"\n  #ptc-input state:")
        if ptc_state.get('found'):
            print(f"    display={ptc_state['display']}, visibility={ptc_state['visibility']}, opacity={ptc_state['opacity']}")
            print(f"    size={ptc_state['width']}x{ptc_state['height']}, offsetTop={ptc_state['offsetTop']}")
            print(f"    parent: id={ptc_state['parentId']} display={ptc_state['parentDisplay']}")
            print("    Ancestor chain:")
            for a in ptc_state.get('ancestors', []):
                print(f"      id={a['id']} | classes={a['classes']} | display={a['display']} | vis={a['visibility']}")
        else:
            print("    NOT FOUND IN DOM")

        # Try to scroll the ptc input into view and interact with it
        if ptc_state.get('found'):
            scroll_result = await page.evaluate("""
                () => {
                    const input = document.querySelector('#ptc-input, textarea.ptc-input');
                    if (input) {
                        input.scrollIntoView({behavior: 'instant', block: 'center'});
                        return {scrolled: true, offsetTop: input.offsetTop};
                    }
                    return {scrolled: false};
                }
            """)
            print(f"\n  Scrolled to ptc-input: {scroll_result}")
            await asyncio.sleep(1.5)
            await screenshot(page, "11-ptc-input-scrolled")

            # Try to click on it
            try:
                ptc_input = await page.wait_for_selector("#ptc-input", timeout=3000)
                if ptc_input:
                    await ptc_input.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await ptc_input.click(force=True)  # force=True bypasses visibility check
                    print("  Clicked ptc-input (forced)")
                    await asyncio.sleep(0.5)
                    await screenshot(page, "12-ptc-input-clicked")
            except Exception as e:
                print(f"  Could not click ptc-input: {e}")

        # Try checking for an alternative - maybe the chatbox is activated by scrolling/click on section
        # Check the "Begin Awakening" button which might activate the chatbox
        print("\n[STEP 8] Looking for activation triggers...")

        # Check awakening section for a button that starts chat
        begin_btn = await page.evaluate("""
            () => {
                const allBtns = Array.from(document.querySelectorAll('button, a[href], input[type="button"], input[type="submit"]'));
                // Filter visible ones
                const visible = allBtns.filter(b => {
                    const rect = b.getBoundingClientRect();
                    return b.offsetParent !== null;
                });

                // Look for chat-starting buttons
                return visible.map(b => ({
                    text: (b.innerText || b.textContent || b.value || '').trim().substring(0, 60),
                    id: b.id,
                    href: b.href || '',
                    classes: b.className?.substring(0, 60),
                    tag: b.tagName,
                    rect: b.getBoundingClientRect()
                })).filter(b => b.text.length > 0).slice(0, 30);
            }
        """)
        print("  All visible buttons:")
        for b in begin_btn:
            print(f"    [{b['tag']}] '{b['text']}' id={b['id']} href={b['href'][:40] if b['href'] else ''}")

        # Let's try scrolling to the specific chat section and take a screenshot to see what's there
        await page.evaluate("""
            () => {
                // Go to the awakening section specifically
                const awakening = document.querySelector('#awakening, section.awakening-section');
                if (awakening) {
                    awakening.scrollIntoView({behavior: 'instant', block: 'start'});
                }
            }
        """)
        await asyncio.sleep(1.5)
        await screenshot(page, "13-awakening-section-view")

        # Now try a more creative approach - look at the page source for the chatbox trigger
        page_source_snippet = await page.evaluate("""
            () => {
                // Look for the awakening/chatbox section HTML
                const awakening = document.querySelector('#awakening, .awakening-section, #ptc-chat-wrapper, #pay-test-post-payment');
                if (awakening) {
                    return awakening.outerHTML.substring(0, 2000);
                }
                // Fallback - look for ptc elements
                const ptc = document.querySelector('[id^="ptc"], [class^="ptc"]');
                if (ptc) return ptc.outerHTML.substring(0, 2000);
                return 'No chat section found';
            }
        """)
        print(f"\n  Chat section HTML (first 2000 chars):\n{page_source_snippet[:1000]}")

        # Check what sections are on the page and find the chat section
        sections_info = await page.evaluate("""
            () => {
                const sections = Array.from(document.querySelectorAll('section, [id]'));
                return sections.filter(s => s.id || s.className).map(s => ({
                    tag: s.tagName,
                    id: s.id,
                    classes: (s.className || '').substring(0, 50),
                    offsetTop: s.offsetTop,
                    height: s.offsetHeight,
                    display: window.getComputedStyle(s).display
                })).filter(s => s.height > 0).sort((a, b) => a.offsetTop - b.offsetTop).slice(0, 30);
            }
        """)
        print("\n  Page sections (by offsetTop):")
        for s in sections_info:
            print(f"    y={s['offsetTop']} h={s['height']} [{s['tag']}] id={s['id']} classes={s['classes'][:40]}")

        # Now let's look specifically for the chat messages container
        ptc_messages_info = await page.evaluate("""
            () => {
                const msgs = document.querySelector('.ptc-messages, #ptc-messages');
                const inputRow = document.querySelector('#ptc-input-row, .ptc-input-row');

                if (msgs) {
                    const children = Array.from(msgs.children).map(c => ({
                        tag: c.tagName,
                        id: c.id,
                        classes: c.className,
                        text: c.innerText?.substring(0, 100)
                    }));
                    return {
                        messagesFound: true,
                        messagesDisplay: window.getComputedStyle(msgs).display,
                        messagesHeight: msgs.offsetHeight,
                        messagesOffsetTop: msgs.offsetTop,
                        childCount: children.length,
                        firstChildren: children.slice(0, 5),
                        inputRowFound: !!inputRow,
                        inputRowDisplay: inputRow ? window.getComputedStyle(inputRow).display : 'N/A'
                    };
                }
                return {messagesFound: false, inputRowFound: !!inputRow};
            }
        """)
        print(f"\n  PTC messages info: {ptc_messages_info}")

        # Try directly interacting with the chatbox at its natural position
        # Scroll to ptc-messages offsetTop
        if ptc_messages_info.get('messagesFound') and ptc_messages_info.get('messagesOffsetTop'):
            top = ptc_messages_info['messagesOffsetTop']
            print(f"\n  PTC messages is at y={top}. Scrolling there...")
            await page.evaluate(f"window.scrollTo(0, {max(0, top - 200)})")
            await asyncio.sleep(1.5)
            await screenshot(page, "14-ptc-messages-viewport")

            # See if the input is visible from here
            input_el, input_sel = await find_chatbox_input(page)
            if input_el:
                print(f"  FOUND chatbox input: {input_sel}")

        # Last resort: Try scrolling through the page to find where chatbox is
        print("\n[STEP 9] Full page scan for chatbox...")

        # Check the ptc-input position on page
        ptc_exact = await page.evaluate("""
            () => {
                const el = document.querySelector('#ptc-input, textarea.ptc-input, .ptc-input');
                if (!el) return null;

                // Walk up to find first non-hidden ancestor
                let ancestor = el.parentElement;
                const chain = [];
                while (ancestor) {
                    const s = window.getComputedStyle(ancestor);
                    chain.push({
                        tag: ancestor.tagName,
                        id: ancestor.id,
                        classes: ancestor.className?.substring(0, 40),
                        display: s.display,
                        visibility: s.visibility,
                        overflow: s.overflow,
                        height: ancestor.offsetHeight,
                        position: s.position,
                        zIndex: s.zIndex
                    });
                    if (ancestor.tagName === 'BODY') break;
                    ancestor = ancestor.parentElement;
                }
                return {
                    inputId: el.id,
                    inputOffsetTop: el.offsetTop,
                    inputDisplay: window.getComputedStyle(el).display,
                    inputHeight: el.offsetHeight,
                    ancestorChain: chain.slice(0, 10)
                };
            }
        """)

        if ptc_exact:
            print(f"  #ptc-input offsetTop={ptc_exact['inputOffsetTop']} display={ptc_exact['inputDisplay']}")
            print("  Ancestor chain:")
            for a in ptc_exact.get('ancestorChain', [])[:10]:
                print(f"    [{a['tag']}] id={a['id']} classes={a['classes']} display={a['display']} h={a['height']} z={a['zIndex']}")

        # Try to interact with chatbox area directly by clicking coordinates
        # First get the viewport size and scroll to see the awakening section
        awakening_rect = await page.evaluate("""
            () => {
                // Find the chatbox/awakening section
                const selectors = ['#awakening', '.awakening-section', '#chat-section', '.begin-awakening'];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        return {
                            found: sel,
                            rect: el.getBoundingClientRect(),
                            offsetTop: el.offsetTop,
                            height: el.offsetHeight
                        };
                    }
                }
                return null;
            }
        """)
        print(f"\n  Awakening section rect: {awakening_rect}")

        if awakening_rect:
            scroll_y = awakening_rect['offsetTop']
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await asyncio.sleep(2)
            await screenshot(page, "15-at-awakening-section")

        # Check if there's a visible chat area with inputs NOW in viewport
        chat_now = await page.evaluate("""
            () => {
                const allInputs = Array.from(document.querySelectorAll('input, textarea'));
                const viewportInputs = allInputs.filter(i => {
                    const rect = i.getBoundingClientRect();
                    return rect.top >= 0 && rect.top <= window.innerHeight && rect.width > 10;
                });
                return viewportInputs.map(i => ({
                    tag: i.tagName,
                    id: i.id,
                    type: i.type,
                    placeholder: i.placeholder,
                    classes: i.className,
                    rect: i.getBoundingClientRect(),
                    display: window.getComputedStyle(i).display
                }));
            }
        """)
        print(f"\n  Inputs in viewport now: {chat_now}")

        # Now attempt the actual test interaction
        print("\n[STEP 10] Attempting direct chatbox interaction...")

        # Try to find the input within the chatbox section
        # If the input is display:none, we might need to trigger it

        # Check if there's a special JavaScript to initialize the chatbox
        ptc_js = await page.evaluate("""
            () => {
                // Check for ptc initialization functions
                const fns = [];
                const props = ['ptcInit', 'initPTC', 'startChat', 'openChat', 'initChat',
                               'ptcStart', 'revealPricing', 'onPaymentComplete',
                               'ptcEngine', 'chatEngine', 'PureBrainChat'];
                for (const p of props) {
                    if (typeof window[p] !== 'undefined') {
                        fns.push({name: p, type: typeof window[p]});
                    }
                }
                return fns;
            }
        """)
        print(f"  PTC JS functions available: {ptc_js}")

        # Check if input row visibility is controlled by a class
        input_row_state = await page.evaluate("""
            () => {
                const row = document.querySelector('#ptc-input-row, .ptc-input-row');
                if (!row) return {found: false};
                const style = window.getComputedStyle(row);
                return {
                    found: true,
                    id: row.id,
                    classes: row.className,
                    display: style.display,
                    visibility: style.visibility,
                    height: row.offsetHeight,
                    offsetTop: row.offsetTop
                };
            }
        """)
        print(f"  Input row state: {input_row_state}")

        # FINAL APPROACH: Use a more complete scroll-through to find where chatbox is visible
        # The chatbox might need scrolling to section AND clicking a visible button first

        # Let's try clicking the "Begin Awakening" or "Awaken Your PURE BRAIN" button in the HERO
        hero_cta = await page.evaluate("""
            () => {
                const btns = Array.from(document.querySelectorAll('button, a'));
                const heroBtn = btns.find(b => {
                    const txt = (b.innerText || b.textContent || '').trim();
                    return (txt.includes('Awaken') || txt.includes('Begin')) && b.offsetParent !== null;
                });
                if (heroBtn) {
                    return {
                        found: true,
                        text: heroBtn.innerText?.trim(),
                        id: heroBtn.id,
                        classes: heroBtn.className,
                        offsetTop: heroBtn.offsetTop,
                        href: heroBtn.href || ''
                    };
                }
                return {found: false};
            }
        """)
        print(f"\n  Hero CTA: {hero_cta}")

        # Scroll to top and click the hero CTA
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await screenshot(page, "16-hero-section")

        # Try clicking the main hero CTA
        try:
            hero_btn = await page.wait_for_selector(
                "button:has-text('Awaken'), a:has-text('Awaken'), button:has-text('Begin Awakening')",
                timeout=3000
            )
            if hero_btn:
                btn_text = await hero_btn.inner_text()
                print(f"  Found hero button: '{btn_text}'")
                await hero_btn.click()
                print("  Clicked hero CTA")
                await asyncio.sleep(2)
                await screenshot(page, "17-after-hero-click")

                # Check if this opened a chatbox
                input_el, input_sel = await find_chatbox_input(page)
                if input_el:
                    print(f"  CHATBOX ACTIVATED! Input: {input_sel}")
        except Exception as e:
            print(f"  No hero button found: {e}")

        # Final check - look for ALL forms and inputs visible right now
        all_forms = await page.evaluate("""
            () => {
                const forms = Array.from(document.querySelectorAll('form'));
                const visibleForms = forms.filter(f => f.offsetParent !== null);
                const allInputs = Array.from(document.querySelectorAll('input:not([type=hidden]), textarea'));
                const visibleInputs = allInputs.filter(i => i.offsetParent !== null);

                return {
                    totalForms: forms.length,
                    visibleForms: visibleForms.length,
                    totalInputs: allInputs.length,
                    visibleInputCount: visibleInputs.length,
                    visibleInputs: visibleInputs.map(i => ({
                        id: i.id, name: i.name, type: i.type,
                        placeholder: i.placeholder, classes: i.className
                    }))
                };
            }
        """)
        print(f"\n  Forms state: {all_forms}")

        # Now let's try a comprehensive approach - navigate to the chatbox section
        # and interact directly with the PTC input even if it appears hidden
        print("\n[STEP 11] Force-scrolling to chat and typing 'pb-full-bypass'...")

        # Find where the ptc-messages is and scroll there
        ptc_pos = await page.evaluate("""
            () => {
                const msgs = document.querySelector('.ptc-messages, #ptc-messages');
                const wrapper = document.querySelector('#pay-test-post-payment, #ptc-chat-wrapper, .ptc-wrapper');
                const input = document.querySelector('#ptc-input, textarea.ptc-input');

                return {
                    messagesTop: msgs ? msgs.offsetTop : null,
                    wrapperTop: wrapper ? wrapper.offsetTop : null,
                    wrapperHeight: wrapper ? wrapper.offsetHeight : null,
                    inputTop: input ? input.offsetTop : null,
                    inputDisplay: input ? window.getComputedStyle(input).display : null,
                    inputParentDisplay: input ? window.getComputedStyle(input.parentElement).display : null
                };
            }
        """)
        print(f"  PTC positions: {ptc_pos}")

        if ptc_pos.get('wrapperTop'):
            await page.evaluate(f"window.scrollTo(0, {max(0, ptc_pos['wrapperTop'] - 100)})")
        elif ptc_pos.get('messagesTop'):
            await page.evaluate(f"window.scrollTo(0, {max(0, ptc_pos['messagesTop'] - 100)})")

        await asyncio.sleep(1.5)
        await screenshot(page, "18-ptc-wrapper-view")

        # Look at what's visible in the chat section
        chat_visible = await page.evaluate("""
            () => {
                // Check what messages already exist
                const msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-ai-msg, .ai-message, .ptc-message'));
                return msgs.map(m => ({
                    classes: m.className,
                    text: m.innerText?.substring(0, 200),
                    visible: m.offsetParent !== null
                }));
            }
        """)
        print(f"\n  Current chat messages: {chat_visible}")

        # Check if there's an initial "What's your name?" message already showing
        if chat_visible:
            print("  Chat has messages! Chatbox might be active.")

        # Final attempt: Try to find and interact with the chatbox via JS execution
        # The chatbox might be visible but behind something
        interaction_result = await page.evaluate("""
            () => {
                const input = document.querySelector('#ptc-input, textarea.ptc-input');
                if (!input) return {success: false, reason: 'no input found'};

                // Try to force the input and its row to be visible
                const row = document.querySelector('#ptc-input-row, .ptc-input-row');
                if (row) {
                    row.style.display = 'flex';
                    row.style.visibility = 'visible';
                    row.style.opacity = '1';
                }

                // Show the input itself
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.style.pointerEvents = 'auto';

                // Scroll to it
                input.scrollIntoView({behavior: 'instant', block: 'center'});

                return {
                    success: true,
                    inputDisplay: window.getComputedStyle(input).display,
                    inputHeight: input.offsetHeight,
                    rowDisplay: row ? window.getComputedStyle(row).display : 'N/A'
                };
            }
        """)
        print(f"\n  Force-show input result: {interaction_result}")

        if interaction_result.get('success'):
            await asyncio.sleep(0.5)
            await screenshot(page, "19-input-force-shown")

        # Now try the actual typing
        try:
            input_handle = await page.wait_for_selector("#ptc-input, textarea.ptc-input", timeout=3000)
            if input_handle:
                await input_handle.click(force=True)
                await asyncio.sleep(0.3)
                await input_handle.fill("pb-full-bypass")
                await asyncio.sleep(0.5)
                await screenshot(page, "20-typed-pb-full-bypass")
                print("  Typed 'pb-full-bypass' into input")

                # Try to send
                send_btn = await page.query_selector("#ptc-send-btn, .ptc-send-btn")
                if send_btn:
                    await send_btn.click(force=True)
                    print("  Clicked send button")
                else:
                    await page.keyboard.press("Enter")
                    print("  Pressed Enter to send")

                await asyncio.sleep(2)
                await screenshot(page, "21-after-send-bypass")

                # Check for AI response
                ai_msgs = await get_ai_messages(page)
                print(f"  AI messages after sending: {ai_msgs}")

        except Exception as e:
            print(f"  Could not type in input: {e}")

        # Check console errors
        print(f"\n  Console errors: {console_errors[:10]}")

        # Final screenshot
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await screenshot(page, "22-final-state-top")

        print("\n" + "=" * 60)
        print("PHASE 1 COMPLETE - Collected initial page state and chatbox info")
        print("=" * 60)

        await browser.close()

        return {
            "screenshots_dir": SCREENSHOT_DIR,
            "screenshot_count": STEP[0],
            "chatbox_input_found": input_el is not None,
            "ptc_state": ptc_state,
            "ptc_messages": chat_visible,
            "console_errors": console_errors[:20]
        }

if __name__ == "__main__":
    result = asyncio.run(run_e2e_test())
    print(f"\nResult: {result}")
