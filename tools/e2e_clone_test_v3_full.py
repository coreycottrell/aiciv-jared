#!/usr/bin/env python3
"""
Full E2E chatbox test v3 - COMPLETE FLOW for https://purebrain.ai/homepage-clone-test/
Confirmed working selectors from v2:
- "Begin Awakening" button: .chat-initial__btn
- AI messages: .message.message--ai
- User input: #userInput (.chat-input__field)
- Submit: #submitBtn (.chat-input__submit) or Enter
- "CLICK TO DISCOVER": #seeWhatBtn
- Reveal pricing: window.revealPricing()
- Waitlist modal: window.openWaitlistModal(tier)
- JS functions: scrollToChat, openWaitlistModal, revealPricing, closeCelebrationAndShowPricing,
                handleWaitlistSubmit, submitToWaitlist, closeWaitlistModal

Full flow:
1. Load page
2. Scroll to chat, click Begin Awakening
3. Type "pb-full-bypass" -> bypass activated
4. Click "CLICK TO DISCOVER WHAT KEEN CAN DO"
5. Navigate chatbox conversation
6. Get to pricing section, click "Awakened" tier
7. Fill waitlist form: Name, Email, Rating (5), Use Case, Company, Role, Urgency
8. Submit form
9. Check confirmation popup
"""

import asyncio
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

async def get_chat_messages(page):
    msgs = await page.evaluate("""
        () => {
            const msgs = Array.from(document.querySelectorAll('.message'));
            return msgs.map(m => ({
                classes: m.className,
                text: m.innerText?.trim()?.substring(0, 200),
                isAI: m.classList.contains('message--ai'),
                isUser: m.classList.contains('message--user')
            }));
        }
    """)
    return msgs

async def get_latest_ai_message(page):
    msgs = await get_chat_messages(page)
    ai_msgs = [m for m in msgs if m.get('isAI')]
    if ai_msgs:
        return ai_msgs[-1].get('text', '')
    return ''

async def wait_for_new_ai_message(page, initial_count, timeout=20):
    """Wait for a new AI message to appear"""
    start = time.time()
    while time.time() - start < timeout:
        msgs = await get_chat_messages(page)
        ai_msgs = [m for m in msgs if m.get('isAI')]
        if len(ai_msgs) > initial_count:
            await asyncio.sleep(1.5)  # Wait for full message
            return True
        await asyncio.sleep(0.5)
    return False

async def get_visible_buttons(page, context_selector=None):
    """Get visible buttons in the page or within a context"""
    result = await page.evaluate(f"""
        () => {{
            const scope = document.querySelector('{context_selector or "body"}') || document.body;
            const btns = Array.from(scope.querySelectorAll('button, [role="button"], .btn, input[type="submit"]'));
            return btns.filter(b => b.offsetParent !== null && !b.disabled).map(b => ({{
                text: (b.innerText || b.value || '').trim().substring(0, 80),
                id: b.id,
                classes: b.className,
                visible: b.offsetParent !== null,
                disabled: b.disabled
            }})).filter(b => b.text.length > 0);
        }}
    """)
    return result

async def run_full_e2e():
    print("=" * 70)
    print("E2E FULL FLOW v3: homepage-clone-test")
    print("=" * 70)

    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-web-security"]
        )
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()

        # Console error tracking
        console_log = []
        page.on("console", lambda msg: console_log.append(f"[{msg.type.upper()}] {msg.text[:200]}"))

        # ========================================
        # PHASE 1: Load page and scroll to chat
        # ========================================
        print("\n=== PHASE 1: PAGE LOAD + CHAT INIT ===")

        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        print(f"  Page: {await page.title()}")
        await screenshot(page, "P1-01-page-loaded")

        # Scroll to awakening section
        await page.evaluate("""
            () => {
                const aw = document.querySelector('#awakening');
                if (aw) window.scrollTo(0, aw.offsetTop);
            }
        """)
        await asyncio.sleep(1.5)
        await screenshot(page, "P1-02-scrolled-to-awakening")

        # Click "Begin Awakening"
        try:
            begin_btn = await page.wait_for_selector(".chat-initial__btn", timeout=5000)
            await begin_btn.scroll_into_view_if_needed()
            await asyncio.sleep(0.3)
            await screenshot(page, "P1-03-before-begin")
            await begin_btn.click()
            print("  Clicked 'Begin Awakening'")
            await asyncio.sleep(2.5)
            await screenshot(page, "P1-04-after-begin")
        except Exception as e:
            print(f"  ERROR clicking Begin Awakening: {e}")
            await screenshot(page, "P1-ERR-begin-not-found")
            await browser.close()
            return {"error": "Begin Awakening not found"}

        # Verify chat started
        msgs_after_begin = await get_chat_messages(page)
        ai_msgs = [m for m in msgs_after_begin if m.get('isAI')]
        print(f"  AI messages after Begin: {len(ai_msgs)}")
        if ai_msgs:
            print(f"  First AI message: {ai_msgs[0]['text'][:100]}")

        # Check input state
        input_check = await page.evaluate("""
            () => {
                const input = document.querySelector('#userInput');
                return {
                    visible: input ? input.offsetParent !== null : false,
                    placeholder: input ? input.placeholder : 'not found',
                    value: input ? input.value : ''
                };
            }
        """)
        print(f"  Input state: {input_check}")

        # ========================================
        # PHASE 2: Type pb-full-bypass
        # ========================================
        print("\n=== PHASE 2: BYPASS ACTIVATION ===")

        # Wait for input to be fully active
        await asyncio.sleep(1)

        # Type pb-full-bypass
        input_count_before = len([m for m in await get_chat_messages(page) if m.get('isAI')])
        print(f"  AI message count before bypass: {input_count_before}")

        try:
            user_input = await page.wait_for_selector("#userInput", timeout=5000)
            await user_input.click()
            await asyncio.sleep(0.3)
            await user_input.fill("pb-full-bypass")
            await asyncio.sleep(0.3)
            await screenshot(page, "P2-01-typed-bypass")
            print("  Typed 'pb-full-bypass'")

            # Submit
            submit_btn = await page.query_selector("#submitBtn")
            if submit_btn and await submit_btn.is_visible():
                await submit_btn.click()
                print("  Clicked submit button")
            else:
                await user_input.press("Enter")
                print("  Pressed Enter")

            await asyncio.sleep(1)
            await screenshot(page, "P2-02-bypass-submitted")

        except Exception as e:
            print(f"  ERROR typing bypass: {e}")

        # Wait for bypass response
        print("  Waiting for bypass response...")
        for i in range(10):
            await asyncio.sleep(1.5)
            msgs = await get_chat_messages(page)
            ai_msgs = [m for m in msgs if m.get('isAI')]
            user_msgs = [m for m in msgs if m.get('isUser')]
            if len(ai_msgs) > input_count_before:
                print(f"  Got bypass response! AI msgs: {len(ai_msgs)}, User msgs: {len(user_msgs)}")
                break
            print(f"  [{i*1.5:.0f}s] waiting... ai_msgs={len(ai_msgs)}")

        all_msgs = await get_chat_messages(page)
        print("\n  Full chat so far:")
        for m in all_msgs:
            role = "AI" if m.get('isAI') else "USER"
            print(f"    [{role}] {m['text'][:120]}")

        await screenshot(page, "P2-03-bypass-response")

        # ========================================
        # PHASE 3: Check for CLICK TO DISCOVER button
        # ========================================
        print("\n=== PHASE 3: CLICK TO DISCOVER ===")

        # Look for seeWhatBtn
        see_what_state = await page.evaluate("""
            () => {
                const btn = document.querySelector('#seeWhatBtn');
                return {
                    found: !!btn,
                    visible: btn ? btn.offsetParent !== null : false,
                    text: btn ? btn.innerText?.trim() : 'N/A',
                    display: btn ? window.getComputedStyle(btn).display : 'N/A'
                };
            }
        """)
        print(f"  seeWhatBtn: {see_what_state}")

        if see_what_state.get('visible'):
            see_btn = await page.query_selector("#seeWhatBtn")
            await see_btn.scroll_into_view_if_needed()
            await asyncio.sleep(0.3)
            await screenshot(page, "P3-01-see-what-visible")
            await see_btn.click()
            print("  Clicked seeWhatBtn")
            await asyncio.sleep(2)
            await screenshot(page, "P3-02-after-see-what")
        else:
            # Look for other buttons
            visible_btns = await get_visible_buttons(page)
            print(f"  Visible buttons: {visible_btns[:10]}")

            # Try clicking any "discover" or "what" button
            found_btn = False
            for btn_info in visible_btns:
                txt = btn_info['text'].lower()
                if 'discover' in txt or 'click' in txt or 'what' in txt or 'keen' in txt:
                    btn = await page.query_selector(f"#{btn_info['id']}" if btn_info['id'] else None)
                    if not btn:
                        # Try by text
                        try:
                            btn = await page.wait_for_selector(f"button:has-text('{btn_info['text'][:30]}')", timeout=2000)
                        except:
                            pass
                    if btn:
                        await btn.click()
                        print(f"  Clicked: '{btn_info['text']}'")
                        found_btn = True
                        await asyncio.sleep(2)
                        await screenshot(page, "P3-03-after-discover-btn")
                        break

        # Check chat state after discover click
        msgs_after_discover = await get_chat_messages(page)
        ai_msgs = [m for m in msgs_after_discover if m.get('isAI')]
        print(f"\n  Chat messages after discover: {len(msgs_after_discover)} total, {len(ai_msgs)} AI")
        for m in msgs_after_discover:
            role = "AI" if m.get('isAI') else "USER"
            print(f"    [{role}] {m['text'][:120]}")

        # ========================================
        # PHASE 4: Navigate conversation flow
        # ========================================
        print("\n=== PHASE 4: CONVERSATION FLOW ===")

        # The chat may now be asking questions. Let's answer them.
        # Look for any buttons that appeared in the chat messages
        chat_buttons_state = await page.evaluate("""
            () => {
                const chatMsgs = document.querySelector('#chatMessages');
                if (!chatMsgs) return {found: false};

                // Find all buttons within chat messages
                const btns = Array.from(chatMsgs.querySelectorAll('button, .btn, [role="button"]'));
                const visible = btns.filter(b => b.offsetParent !== null);

                return {
                    found: true,
                    buttonCount: btns.length,
                    visibleCount: visible.length,
                    buttons: visible.map(b => ({
                        text: b.innerText?.trim().substring(0, 80),
                        id: b.id,
                        classes: b.className,
                        onclick: b.getAttribute('onclick')
                    }))
                };
            }
        """)
        print(f"  Chat buttons: {chat_buttons_state}")

        # Look for option buttons in the conversation
        option_btns = await page.evaluate("""
            () => {
                // Look for option/choice buttons that AI presents
                const selectors = [
                    '.chat-options button', '.chat-choices button',
                    '.option-btn', '.choice-btn', '.conversation-option',
                    '.message--ai button', '[class*="option"]', '[class*="choice"]'
                ];
                const results = [];
                for (const sel of selectors) {
                    const els = Array.from(document.querySelectorAll(sel));
                    if (els.length > 0) {
                        results.push({
                            selector: sel,
                            count: els.length,
                            buttons: els.filter(e => e.offsetParent !== null).map(e => ({
                                text: e.innerText?.trim().substring(0, 60),
                                classes: e.className,
                                visible: e.offsetParent !== null
                            }))
                        });
                    }
                }
                return results;
            }
        """)
        print(f"  Option buttons: {option_btns}")

        # Wait a bit for any delayed AI messages
        print("  Waiting for more AI messages...")
        for i in range(6):
            await asyncio.sleep(2)
            current_msgs = await get_chat_messages(page)
            current_ai = [m for m in current_msgs if m.get('isAI')]
            print(f"  [{i*2}s] AI msgs: {len(current_ai)}")
            if i == 0:
                initial_ai_count = len(current_ai)
            elif len(current_ai) > initial_ai_count:
                print("  New AI message appeared!")
                await screenshot(page, f"P4-new-ai-msg-{i}")
                break

        # Get all current buttons (in chat, pricing buttons, etc.)
        all_btns_now = await get_visible_buttons(page)
        print(f"\n  ALL visible buttons now:")
        for b in all_btns_now:
            print(f"    id={b['id']!r:20} | '{b['text'][:60]}'")

        await screenshot(page, "P4-01-full-view")

        # ========================================
        # PHASE 5: Check pricing section
        # ========================================
        print("\n=== PHASE 5: PRICING SECTION ===")

        pricing_state = await page.evaluate("""
            () => {
                const ps = document.querySelector('.pricing-section');
                const cards = Array.from(document.querySelectorAll('.pricing-card'));

                return {
                    pricingDisplay: ps ? window.getComputedStyle(ps).display : 'not found',
                    pricingHasActive: ps?.classList?.contains('active') || false,
                    cardCount: cards.length,
                    cards: cards.map(c => ({
                        classes: c.className,
                        visible: c.offsetParent !== null,
                        title: c.querySelector('.pricing-card__tier')?.innerText?.trim() || '',
                        price: c.querySelector('.pricing-card__price, .price')?.innerText?.trim() || '',
                        ctaText: c.querySelector('button, .btn')?.innerText?.trim() || '',
                        ctaOnclick: c.querySelector('button, .btn')?.getAttribute('onclick') || ''
                    }))
                };
            }
        """)
        print(f"  Pricing state: display={pricing_state['pricingDisplay']}, hasActive={pricing_state['pricingHasActive']}")
        print(f"  Cards: {pricing_state['cardCount']}")
        for c in pricing_state['cards']:
            print(f"    [{c['classes'][:30]}] '{c['title']}' - visible={c['visible']} cta='{c['ctaText']}' onclick={c['ctaOnclick'][:60]}")

        # If pricing is not visible, try to reveal it
        if pricing_state['pricingDisplay'] == 'none':
            print("\n  Pricing hidden - trying to reveal...")

            # Option 1: Call revealPricing()
            reveal_result = await page.evaluate("""
                () => {
                    if (typeof window.revealPricing === 'function') {
                        window.revealPricing();
                        const ps = document.querySelector('.pricing-section');
                        return {
                            called: true,
                            display: ps ? window.getComputedStyle(ps).display : 'N/A',
                            hasActive: ps?.classList?.contains('active') || false
                        };
                    }
                    return {called: false};
                }
            """)
            print(f"  revealPricing() result: {reveal_result}")
            await asyncio.sleep(1)
            await screenshot(page, "P5-01-after-reveal-pricing")

            # Option 2: Try closeCelebrationAndShowPricing
            if reveal_result.get('display') == 'none' or not reveal_result.get('called'):
                close_result = await page.evaluate("""
                    () => {
                        if (typeof window.closeCelebrationAndShowPricing === 'function') {
                            window.closeCelebrationAndShowPricing();
                            const ps = document.querySelector('.pricing-section');
                            return {
                                called: true,
                                display: ps ? window.getComputedStyle(ps).display : 'N/A'
                            };
                        }
                        return {called: false};
                    }
                """)
                print(f"  closeCelebrationAndShowPricing() result: {close_result}")
                await asyncio.sleep(1)

        # Check pricing again
        pricing_check2 = await page.evaluate("""
            () => {
                const ps = document.querySelector('.pricing-section');
                return {
                    display: ps ? window.getComputedStyle(ps).display : 'not found',
                    hasActive: ps?.classList?.contains('active') || false,
                    height: ps ? ps.offsetHeight : 0
                };
            }
        """)
        print(f"  Pricing after reveal: {pricing_check2}")

        # Scroll to pricing section
        await page.evaluate("""
            () => {
                const ps = document.querySelector('.pricing-section, #pricing');
                if (ps) ps.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        """)
        await asyncio.sleep(1.5)
        await screenshot(page, "P5-02-pricing-section-view")

        # Look for tier buttons/cards
        tier_buttons = await page.evaluate("""
            () => {
                // Find all tier-related buttons
                const selectors = [
                    '.pricing-card button', '.pricing-card .btn',
                    '[onclick*="waitlist"]', '[onclick*="Awakened"]',
                    '[onclick*="openWaitlist"]', 'button[data-tier]',
                    '.reserve-btn', '.tier-select-btn'
                ];
                const results = [];
                for (const sel of selectors) {
                    const els = Array.from(document.querySelectorAll(sel));
                    if (els.length > 0) {
                        els.forEach(el => {
                            results.push({
                                selector: sel,
                                text: el.innerText?.trim().substring(0, 60),
                                id: el.id,
                                classes: el.className,
                                onclick: el.getAttribute('onclick'),
                                visible: el.offsetParent !== null,
                                parentTier: el.closest('.pricing-card')?.querySelector('.pricing-card__tier')?.innerText?.trim() || ''
                            });
                        });
                    }
                }
                // Also get all visible buttons with reserve/select/choose text
                const allBtns = Array.from(document.querySelectorAll('button, .btn'));
                allBtns.filter(b => {
                    const txt = (b.innerText || '').toLowerCase();
                    return (txt.includes('reserve') || txt.includes('select') || txt.includes('choose') || txt.includes('awakened')) && b.offsetParent !== null;
                }).forEach(b => {
                    results.push({
                        selector: 'text-match',
                        text: b.innerText?.trim().substring(0, 60),
                        id: b.id,
                        classes: b.className,
                        onclick: b.getAttribute('onclick'),
                        visible: b.offsetParent !== null,
                    });
                });
                return results;
            }
        """)
        print(f"\n  Tier buttons: {tier_buttons}")

        # ========================================
        # PHASE 6: Click pricing tier
        # ========================================
        print("\n=== PHASE 6: SELECT TIER ===")

        # Look for "Reserve Your AI Now" buttons or Awakened tier
        reserve_btn = await page.evaluate("""
            () => {
                // Find the featured pricing card (Awakened) button
                const featured = document.querySelector('.pricing-card--featured');
                if (featured) {
                    const btn = featured.querySelector('button, .btn, [onclick]');
                    if (btn) {
                        return {
                            found: true,
                            text: btn.innerText?.trim(),
                            onclick: btn.getAttribute('onclick'),
                            visible: btn.offsetParent !== null,
                            classes: btn.className,
                            id: btn.id
                        };
                    }
                }

                // Fallback: find any button with waitlist/reserve in onclick
                const btns = Array.from(document.querySelectorAll('button, .btn'));
                const reserveBtn = btns.find(b => {
                    const onclick = b.getAttribute('onclick') || '';
                    return onclick.includes('waitlist') || onclick.includes('Awakened') || onclick.includes('reserve');
                });
                if (reserveBtn) {
                    return {
                        found: true,
                        text: reserveBtn.innerText?.trim(),
                        onclick: reserveBtn.getAttribute('onclick'),
                        visible: reserveBtn.offsetParent !== null,
                        classes: reserveBtn.className,
                        id: reserveBtn.id
                    };
                }

                return {found: false};
            }
        """)
        print(f"  Reserve button: {reserve_btn}")

        # If pricing is still hidden, try manually making it visible and clicking
        if not reserve_btn.get('visible') or not reserve_btn.get('found'):
            print("  Pricing cards not visible - forcing display...")
            force_result = await page.evaluate("""
                () => {
                    const ps = document.querySelector('.pricing-section');
                    if (ps) {
                        ps.style.display = 'block';
                        ps.classList.add('active');
                        ps.scrollIntoView({behavior: 'instant', block: 'start'});
                    }
                    const cards = Array.from(document.querySelectorAll('.pricing-card'));
                    cards.forEach(c => {
                        c.style.display = 'block';
                    });
                    const pricingSection = document.querySelector('.pricing-section');
                    return {
                        display: pricingSection ? window.getComputedStyle(pricingSection).display : 'N/A',
                        cardCount: cards.length,
                        featuredCard: document.querySelector('.pricing-card--featured') ? 'found' : 'not found'
                    };
                }
            """)
            print(f"  Force pricing: {force_result}")
            await asyncio.sleep(1)
            await screenshot(page, "P6-01-pricing-forced")

        # Now try to find and click the Awakened button
        tier_click_result = await page.evaluate("""
            async () => {
                // Try the featured card first
                const featured = document.querySelector('.pricing-card--featured');
                if (featured) {
                    const btn = featured.querySelector('button, .btn, [onclick]');
                    if (btn) {
                        const onclick = btn.getAttribute('onclick') || '';
                        btn.scrollIntoView({behavior: 'instant', block: 'center'});
                        return {
                            found: true,
                            tier: 'featured',
                            text: btn.innerText?.trim(),
                            onclick: onclick,
                            rect: btn.getBoundingClientRect()
                        };
                    }
                }

                // Try any pricing card button
                const cards = Array.from(document.querySelectorAll('.pricing-card'));
                for (const card of cards) {
                    const btn = card.querySelector('button, .btn, [onclick]');
                    if (btn) {
                        const tier = card.querySelector('.pricing-card__tier, .tier-name')?.innerText?.trim() || 'unknown';
                        btn.scrollIntoView({behavior: 'instant', block: 'center'});
                        return {
                            found: true,
                            tier: tier,
                            text: btn.innerText?.trim(),
                            onclick: btn.getAttribute('onclick') || '',
                            rect: btn.getBoundingClientRect()
                        };
                    }
                }
                return {found: false};
            }
        """)
        print(f"  Tier click target: {tier_click_result}")

        if tier_click_result.get('found'):
            rect = tier_click_result.get('rect', {})
            onclick = tier_click_result.get('onclick', '')

            # Approach 1: Click via mouse coordinates
            if rect and rect.get('width', 0) > 0:
                x = rect['x'] + rect['width'] / 2
                y = rect['y'] + rect['height'] / 2
                await screenshot(page, "P6-02-before-tier-click")
                await page.mouse.click(x, y)
                print(f"  Clicked tier button at ({x:.0f}, {y:.0f})")
            elif onclick:
                # Execute the onclick directly
                await page.evaluate(f"eval(`{onclick}`)")
                print(f"  Executed onclick: {onclick[:80]}")
            else:
                # Try the openWaitlistModal directly
                await page.evaluate("""
                    () => {
                        if (typeof window.openWaitlistModal === 'function') {
                            window.openWaitlistModal('Awakened');
                        }
                    }
                """)
                print("  Called openWaitlistModal('Awakened') directly")

            await asyncio.sleep(2)
            await screenshot(page, "P6-03-after-tier-click")

        # Alternative: just call openWaitlistModal
        # Check if waitlist modal appeared
        modal_state = await page.evaluate("""
            () => {
                const modal = document.querySelector('.waitlist-modal, #waitlist-modal, .waitlist-overlay, [id*="waitlist"]');
                const tier = document.querySelector('#waitlistTier');
                return {
                    modalFound: !!modal,
                    modalDisplay: modal ? window.getComputedStyle(modal).display : 'N/A',
                    modalVisible: modal ? modal.offsetParent !== null : false,
                    tierValue: tier ? tier.value : 'N/A',
                    waitlistNameVisible: document.querySelector('#waitlistName') ?
                        document.querySelector('#waitlistName').offsetParent !== null : false
                };
            }
        """)
        print(f"  Modal state: {modal_state}")

        if not modal_state.get('modalVisible') and not modal_state.get('waitlistNameVisible'):
            print("  Modal not visible - trying openWaitlistModal directly...")
            open_modal = await page.evaluate("""
                () => {
                    if (typeof window.openWaitlistModal === 'function') {
                        window.openWaitlistModal('Awakened');
                        return {called: true};
                    }
                    return {called: false};
                }
            """)
            print(f"  openWaitlistModal result: {open_modal}")
            await asyncio.sleep(1.5)
            await screenshot(page, "P6-04-after-open-modal")

        # ========================================
        # PHASE 7: Fill waitlist form
        # ========================================
        print("\n=== PHASE 7: FILL WAITLIST FORM ===")

        # Check form visibility
        form_state = await page.evaluate("""
            () => {
                const fieldsToCheck = ['waitlistName', 'waitlistEmail', 'waitlistRatingValue',
                                       'waitlistUseCase', 'waitlistCompany', 'waitlistRole'];
                const results = {};
                for (const id of fieldsToCheck) {
                    const el = document.querySelector(`#${id}`);
                    if (el) {
                        results[id] = {
                            found: true,
                            type: el.type,
                            visible: el.offsetParent !== null,
                            display: window.getComputedStyle(el).display,
                            value: el.value
                        };
                    } else {
                        results[id] = {found: false};
                    }
                }

                // Find form container
                const formContainer = document.querySelector('.waitlist-modal, .waitlist-form, #waitlistForm, [id*="waitlist-form"]');
                results.container = {
                    found: !!formContainer,
                    display: formContainer ? window.getComputedStyle(formContainer).display : 'N/A',
                    visible: formContainer ? formContainer.offsetParent !== null : false
                };

                // Look for rating stars
                const stars = Array.from(document.querySelectorAll('[data-rating], .star, .rating-star, [class*="star"]'));
                results.stars = stars.filter(s => s.offsetParent !== null).map(s => ({
                    classes: s.className,
                    dataRating: s.getAttribute('data-rating'),
                    text: s.innerText?.trim()
                }));

                return results;
            }
        """)
        print(f"  Form state:")
        for key, val in form_state.items():
            print(f"    {key}: {val}")

        # Scroll to the form
        await page.evaluate("""
            () => {
                const form = document.querySelector('.waitlist-modal, .waitlist-form, #waitlist-modal, [class*="waitlist"]');
                if (form) form.scrollIntoView({behavior: 'instant', block: 'start'});
                else {
                    const name = document.querySelector('#waitlistName');
                    if (name) name.scrollIntoView({behavior: 'instant', block: 'center'});
                }
            }
        """)
        await asyncio.sleep(1)
        await screenshot(page, "P7-01-form-visible")

        # Fill Name
        print("\n  Filling form fields...")
        try:
            name_input = await page.wait_for_selector("#waitlistName", timeout=5000)
            await name_input.scroll_into_view_if_needed()
            await name_input.click(force=True)
            await asyncio.sleep(0.3)
            await name_input.fill("Aether E2E Test")
            print("  Name: 'Aether E2E Test'")
            await screenshot(page, "P7-02-name-filled")
        except Exception as e:
            print(f"  ERROR filling name: {e}")

        # Fill Email
        try:
            email_input = await page.wait_for_selector("#waitlistEmail", timeout=3000)
            await email_input.click(force=True)
            await asyncio.sleep(0.2)
            await email_input.fill("aether-e2e@purebrain.ai")
            print("  Email: 'aether-e2e@purebrain.ai'")
            await screenshot(page, "P7-03-email-filled")
        except Exception as e:
            print(f"  ERROR filling email: {e}")

        # Click rating star 5
        print("\n  Looking for rating stars...")
        star_result = await page.evaluate("""
            () => {
                // Look for rating stars with data-rating attribute
                const stars = Array.from(document.querySelectorAll('[data-rating], .rating-star, .star-rating span, .star'));
                const starInfo = stars.map(s => ({
                    tag: s.tagName,
                    classes: s.className,
                    dataRating: s.getAttribute('data-rating'),
                    text: s.innerText?.trim(),
                    visible: s.offsetParent !== null,
                    onclick: s.getAttribute('onclick')
                }));

                // Also check for label/input radio star rating
                const ratingInputs = Array.from(document.querySelectorAll('input[type="radio"][name*="rating"], .star-input, [name="rating"]'));
                const ratingLabels = Array.from(document.querySelectorAll('label[for*="star"], .star-label, .rating-label'));

                return {
                    stars: starInfo,
                    ratingInputs: ratingInputs.map(i => ({id: i.id, value: i.value, name: i.name})),
                    ratingLabels: ratingLabels.map(l => ({text: l.innerText?.trim(), htmlFor: l.htmlFor, classes: l.className}))
                };
            }
        """)
        print(f"  Rating elements: {star_result}")

        # Try to click star 5
        star_clicked = False
        try:
            # Look for star with data-rating="5"
            star5 = await page.query_selector("[data-rating='5'], [data-value='5'], .star[data-star='5']")
            if star5 and await star5.is_visible():
                await star5.click()
                print("  Clicked star 5 (data-rating)")
                star_clicked = True
            else:
                # Try JavaScript approach
                star_js = await page.evaluate("""
                    () => {
                        // Find all clickable star elements
                        const stars = Array.from(document.querySelectorAll('[data-rating], .star, span[class*="star"]'));
                        const star5 = stars.find(s => {
                            const rating = s.getAttribute('data-rating') || s.getAttribute('data-value') || s.getAttribute('data-star');
                            return rating === '5';
                        });
                        if (star5) {
                            star5.click();
                            return {clicked: true, element: star5.tagName, classes: star5.className};
                        }

                        // Try finding by position (5th star)
                        const allStars = Array.from(document.querySelectorAll('.rating-stars span, .stars span, .star-rating span, [class*="star-"]'));
                        if (allStars.length >= 5) {
                            allStars[4].click();
                            return {clicked: true, element: allStars[4].tagName, classes: allStars[4].className, method: '5th-star'};
                        }

                        // Set rating value directly
                        const ratingInput = document.querySelector('#waitlistRatingValue');
                        if (ratingInput) {
                            ratingInput.value = '5';
                            ratingInput.dispatchEvent(new Event('change', {bubbles: true}));
                            return {clicked: true, method: 'direct-value'};
                        }

                        return {clicked: false};
                    }
                """)
                print(f"  Star click JS: {star_js}")
                star_clicked = star_js.get('clicked', False)
        except Exception as e:
            print(f"  ERROR clicking star: {e}")

        await screenshot(page, "P7-04-rating-attempt")

        # Fill Use Case
        try:
            usecase_input = await page.wait_for_selector("#waitlistUseCase, textarea[placeholder*='Managing']", timeout=3000)
            await usecase_input.click(force=True)
            await asyncio.sleep(0.2)
            await usecase_input.fill("Full end-to-end browser test")
            print("  Use case: 'Full end-to-end browser test'")
            await screenshot(page, "P7-05-usecase-filled")
        except Exception as e:
            print(f"  ERROR filling use case: {e}")

        # Fill Company
        try:
            company_input = await page.wait_for_selector("#waitlistCompany", timeout=3000)
            await company_input.click(force=True)
            await asyncio.sleep(0.2)
            await company_input.fill("Pure Technology")
            print("  Company: 'Pure Technology'")
        except Exception as e:
            print(f"  ERROR filling company: {e}")

        # Fill Role
        try:
            role_input = await page.wait_for_selector("#waitlistRole", timeout=3000)
            await role_input.click(force=True)
            await asyncio.sleep(0.2)
            await role_input.fill("AI")
            print("  Role: 'AI'")
        except Exception as e:
            print(f"  ERROR filling role: {e}")

        # Look for urgency selector
        urgency_state = await page.evaluate("""
            () => {
                const urgency = document.querySelector('#waitlistUrgency, select[name="urgency"], [id*="urgency"]');
                const urgencyBtns = Array.from(document.querySelectorAll('[class*="urgency"], [data-urgency]'));
                return {
                    urgencyInputFound: !!urgency,
                    urgencyType: urgency ? urgency.tagName : 'N/A',
                    urgencyOptions: urgency && urgency.tagName === 'SELECT' ?
                        Array.from(urgency.options).map(o => ({value: o.value, text: o.text})) : [],
                    urgencyBtns: urgencyBtns.map(b => ({text: b.innerText?.trim(), classes: b.className}))
                };
            }
        """)
        print(f"\n  Urgency selector: {urgency_state}")

        # If urgency select exists, select an option
        if urgency_state.get('urgencyInputFound'):
            try:
                if urgency_state.get('urgencyType') == 'SELECT':
                    urgency_sel = await page.wait_for_selector("#waitlistUrgency, select[name='urgency']", timeout=3000)
                    # Select the first non-empty option
                    options = urgency_state.get('urgencyOptions', [])
                    if len(options) > 1:  # First is usually placeholder
                        await urgency_sel.select_option(options[1]['value'])
                        print(f"  Urgency: selected '{options[1]['text']}'")
                    elif options:
                        await urgency_sel.select_option(options[0]['value'])
                        print(f"  Urgency: selected '{options[0]['text']}'")
            except Exception as e:
                print(f"  ERROR with urgency: {e}")

        await screenshot(page, "P7-06-form-filled")

        # ========================================
        # PHASE 8: Submit form
        # ========================================
        print("\n=== PHASE 8: SUBMIT FORM ===")

        # Look for submit button
        submit_state = await page.evaluate("""
            () => {
                const submitBtns = Array.from(document.querySelectorAll(
                    'button[type="submit"], input[type="submit"], .waitlist-submit, .submit-waitlist, #submitWaitlist, [onclick*="submitToWaitlist"], [onclick*="handleWaitlist"]'
                ));
                return submitBtns.filter(b => b.offsetParent !== null).map(b => ({
                    text: (b.innerText || b.value || '').trim().substring(0, 60),
                    id: b.id,
                    classes: b.className,
                    type: b.type,
                    onclick: b.getAttribute('onclick')
                }));
            }
        """)
        print(f"  Submit buttons: {submit_state}")

        # Try to submit
        submitted = False
        try:
            # Look for submit button in form context
            submit_btn = None

            # Try various selectors
            for sel in ['button[type="submit"]', '.waitlist-form__submit', '.waitlist-submit', '[onclick*="submitToWaitlist"]', '[onclick*="handleWaitlist"]']:
                try:
                    btn = await page.wait_for_selector(sel, timeout=1000)
                    if btn and await btn.is_visible():
                        submit_btn = btn
                        print(f"  Found submit via: {sel}")
                        break
                except:
                    pass

            if submit_btn:
                await submit_btn.scroll_into_view_if_needed()
                await asyncio.sleep(0.3)
                await screenshot(page, "P8-01-before-submit")
                await submit_btn.click()
                print("  Clicked submit button")
                submitted = True
            else:
                # Try calling JS directly
                submit_js = await page.evaluate("""
                    () => {
                        if (typeof window.handleWaitlistSubmit === 'function') {
                            window.handleWaitlistSubmit(new Event('submit'));
                            return {called: 'handleWaitlistSubmit'};
                        }
                        if (typeof window.submitToWaitlist === 'function') {
                            window.submitToWaitlist();
                            return {called: 'submitToWaitlist'};
                        }
                        // Try submitting the form directly
                        const form = document.querySelector('.waitlist-form__form, form[onsubmit*="waitlist"], #waitlistForm');
                        if (form) {
                            form.dispatchEvent(new Event('submit', {bubbles: true}));
                            return {called: 'form.submit'};
                        }
                        return {called: null};
                    }
                """)
                print(f"  Submit JS: {submit_js}")
                submitted = True

        except Exception as e:
            print(f"  ERROR submitting: {e}")

        if submitted:
            await asyncio.sleep(2)
            await screenshot(page, "P8-02-after-submit")

        # Wait for confirmation
        print("\n=== PHASE 9: CHECK CONFIRMATION ===")
        for i in range(8):
            await asyncio.sleep(1.5)
            confirm_state = await page.evaluate("""
                () => {
                    // Look for confirmation popup, success message, etc.
                    const selectors = [
                        '.confirmation', '.success-popup', '.celebration',
                        '.waitlist-success', '.thank-you', '#confirmation',
                        '[class*="success"]', '[class*="confirm"]', '[class*="thank"]',
                        '.modal--success', '.popup--success'
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el && el.offsetParent !== null) {
                            return {
                                found: true,
                                selector: sel,
                                text: el.innerText?.substring(0, 300),
                                visible: el.offsetParent !== null
                            };
                        }
                    }

                    // Check if modal was replaced with success content
                    const modal = document.querySelector('.waitlist-modal, #waitlist-modal');
                    if (modal) {
                        return {
                            found: false,
                            modalDisplay: window.getComputedStyle(modal).display,
                            modalText: modal.innerText?.substring(0, 300)
                        };
                    }
                    return {found: false};
                }
            """)

            if confirm_state.get('found'):
                print(f"  CONFIRMATION FOUND at {i*1.5:.0f}s!")
                print(f"  {confirm_state}")
                await screenshot(page, f"P9-confirmation-at-{i}")
                break
            else:
                print(f"  [{i*1.5:.0f}s] No confirmation yet. Modal: {confirm_state.get('modalDisplay')} | {confirm_state.get('modalText', '')[:100]}")

        await screenshot(page, "P9-final-state")

        # ========================================
        # FINAL REPORT
        # ========================================
        print("\n=== FINAL REPORT ===")

        final_all = await page.evaluate("""
            () => {
                const chatMsgs = document.querySelector('#chatMessages');
                const pricingSection = document.querySelector('.pricing-section');
                const waitlistModal = document.querySelector('.waitlist-modal, #waitlist-modal');

                return {
                    chatMessageCount: chatMsgs ? chatMsgs.querySelectorAll('.message').length : 0,
                    chatAllText: chatMsgs ? chatMsgs.innerText?.substring(0, 800) : 'N/A',
                    pricingDisplay: pricingSection ? window.getComputedStyle(pricingSection).display : 'not found',
                    pricingHasActive: pricingSection?.classList?.contains('active') || false,
                    waitlistModalDisplay: waitlistModal ? window.getComputedStyle(waitlistModal).display : 'not found',
                    consoleErrorCount: 0
                };
            }
        """)

        errors = [e for e in console_log if '[ERROR]' in e]
        print(f"  Total chat messages: {final_all['chatMessageCount']}")
        print(f"  Chat content: {final_all['chatAllText'][:400]}")
        print(f"  Pricing section: display={final_all['pricingDisplay']}, hasActive={final_all['pricingHasActive']}")
        print(f"  Waitlist modal: display={final_all['waitlistModalDisplay']}")
        print(f"  Console errors: {len(errors)}")
        print(f"\n  Screenshots taken: {STEP[0]}")
        print(f"  Saved to: {SCREENSHOT_DIR}")

        # Print notable console errors
        if errors:
            print("\n  Notable errors:")
            for e in errors[:8]:
                print(f"    {e[:150]}")

        await browser.close()
        return {
            "status": "COMPLETE",
            "screenshots": STEP[0],
            "chat_messages": final_all['chatMessageCount'],
            "pricing_revealed": final_all['pricingHasActive'],
            "waitlist_modal": final_all['waitlistModalDisplay'],
            "console_errors": len(errors)
        }

if __name__ == "__main__":
    result = asyncio.run(run_full_e2e())
    print(f"\nFinal result: {result}")
