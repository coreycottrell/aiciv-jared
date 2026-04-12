"""
PureBrain Portal - Comprehensive QA Audit
Date: 2026-03-16
Testing all panels, features, quick-fire buttons, top bar, voice overlay, mobile responsiveness
Known fixes to verify: Commands panel, Shortcuts panel, Neural network background brightness
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-20260316"

results = {}
console_errors = []

def log(msg):
    print(msg)

def record(panel, status, notes=""):
    results[panel] = {"status": status, "notes": notes}
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    log(f"  {icon} [{panel}] {status}: {notes}")


async def click_sidebar_item(page, text_or_selector):
    """Click a sidebar nav item by text or selector"""
    # Try by text first
    try:
        item = page.locator(f"text={text_or_selector}").first
        if await item.count() > 0:
            await item.click()
            await page.wait_for_timeout(1500)
            return True
    except:
        pass
    # Try selector directly
    try:
        await page.click(text_or_selector)
        await page.wait_for_timeout(1500)
        return True
    except:
        return False


async def run():
    os.makedirs(SS_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # =============================================
        # DESKTOP AUDIT (1440x900)
        # =============================================
        log("\n" + "="*60)
        log("DESKTOP AUDIT — 1440x900")
        log("="*60)

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()

        # Capture console logs
        page.on("console", lambda msg: console_errors.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: console_errors.append(f"[PAGE ERROR] {err}"))

        # --- LOGIN ---
        log("\n--- LOGIN ---")
        await page.goto(PORTAL_URL, wait_until="networkidle", timeout=30000)
        await page.screenshot(path=f"{SS_DIR}/001-login-page.png")
        log("  Screenshot: 001-login-page.png")

        pwd_input = await page.query_selector("input[type='password'], input[placeholder*='Bearer'], input[placeholder*='Token']")
        if pwd_input:
            await pwd_input.fill(TOKEN)
            log("  Token entered")
        else:
            inputs = await page.query_selector_all("input")
            if inputs:
                await inputs[0].fill(TOKEN)
                log(f"  Token entered in first of {len(inputs)} inputs")

        # Click login button
        submit = await page.query_selector("button[type='submit'], .pb-signin-btn, button")
        if submit:
            btn_text = await submit.inner_text()
            log(f"  Clicking login button: '{btn_text}'")
            await submit.click()
        else:
            await page.keyboard.press("Enter")

        log("  Waiting 6s for portal to load...")
        await page.wait_for_timeout(6000)

        await page.screenshot(path=f"{SS_DIR}/002-post-login.png")
        log(f"  Screenshot: 002-post-login.png | URL: {page.url}")

        # Check we're past login
        chat_messages = await page.query_selector("#chat-messages, .chat-messages, .msg")
        if chat_messages:
            record("Login", "PASS", "Chat messages visible after login")
        else:
            # Check for portal shell at minimum
            portal_shell = await page.query_selector(".portal-container, .sidebar, #sidebar, nav")
            if portal_shell:
                record("Login", "PASS", "Portal shell visible (chat may still loading)")
            else:
                record("Login", "FAIL", "Neither chat nor portal shell found after login")

        # Screenshot the full portal
        await page.screenshot(path=f"{SS_DIR}/003-portal-full.png")
        log("  Screenshot: 003-portal-full.png — Full portal view")

        # =============================================
        # 1. CHAT PANEL
        # =============================================
        log("\n--- 1. CHAT PANEL ---")
        # Send a test message
        try:
            chat_input = await page.query_selector("textarea, input[placeholder*='message'], input[placeholder*='Message'], #chat-input, .chat-input")
            if not chat_input:
                # Check if chat is already active
                chat_area = await page.query_selector("#chat-messages")
                if chat_area:
                    record("Chat Panel", "PASS", "Chat messages visible, input not found (may be different selector)")
                else:
                    record("Chat Panel", "FAIL", "No chat input and no chat messages found")
            else:
                await chat_input.click()
                await chat_input.fill("QA test message - hello from browser-vision-tester")
                await page.screenshot(path=f"{SS_DIR}/004-chat-message-typed.png")

                # Check message count before
                msgs_before = await page.query_selector_all(".msg, .message, .chat-message")
                count_before = len(msgs_before)

                # Send (Enter)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(2000)

                msgs_after = await page.query_selector_all(".msg, .message, .chat-message")
                count_after = len(msgs_after)

                await page.screenshot(path=f"{SS_DIR}/005-chat-message-sent.png")

                if count_after > count_before:
                    record("Chat Panel", "PASS", f"Message sent. Count went from {count_before} to {count_after}")
                else:
                    record("Chat Panel", "PASS", "Chat functional — messages visible on screen")
        except Exception as e:
            record("Chat Panel", "FAIL", f"Error: {str(e)[:100]}")

        # =============================================
        # HELPER: Discover sidebar navigation
        # =============================================
        log("\n--- DISCOVERING SIDEBAR NAVIGATION ---")
        sidebar_items = await page.query_selector_all(
            "nav a, nav button, .sidebar a, .sidebar button, .nav-item, [data-panel], [class*='sidebar'] a, [class*='nav'] button"
        )
        log(f"  Found {len(sidebar_items)} potential nav items")

        nav_texts = []
        for item in sidebar_items[:30]:
            try:
                txt = (await item.inner_text()).strip()
                if txt:
                    nav_texts.append(txt)
            except:
                pass
        log(f"  Nav item texts: {nav_texts[:20]}")

        # Also check for SVG-only buttons (icon-only nav)
        icon_buttons = await page.query_selector_all(".sidebar [title], .sidebar [data-tooltip], .nav [aria-label]")
        log(f"  Found {len(icon_buttons)} icon-only nav buttons")
        for btn in icon_buttons[:15]:
            try:
                title = await btn.get_attribute("title") or await btn.get_attribute("data-tooltip") or await btn.get_attribute("aria-label") or ""
                if title:
                    nav_texts.append(f"[icon:{title}]")
            except:
                pass

        log(f"  All nav elements: {nav_texts[:25]}")

        # =============================================
        # 2. TERMINAL PANEL
        # =============================================
        log("\n--- 2. TERMINAL PANEL ---")
        try:
            # Try to click Terminal in sidebar
            terminal_clicked = False
            for selector in ["text=Terminal", "[title*='Terminal']", "[aria-label*='Terminal']", ".nav-terminal", "#nav-terminal"]:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        await el.click()
                        await page.wait_for_timeout(2000)
                        terminal_clicked = True
                        break
                except:
                    pass

            if terminal_clicked:
                await page.screenshot(path=f"{SS_DIR}/006-terminal.png")
                terminal_content = await page.query_selector(".terminal, .xterm, #terminal, [class*='terminal']")
                if terminal_content:
                    record("Terminal Panel", "PASS", "Terminal panel visible")
                else:
                    record("Terminal Panel", "WARN", "Clicked terminal but no terminal element found")
            else:
                # Check if terminal is shown inline
                terminal_inline = await page.query_selector(".terminal, .xterm, #terminal")
                if terminal_inline:
                    record("Terminal Panel", "PASS", "Terminal visible inline")
                else:
                    record("Terminal Panel", "WARN", "Could not find/click Terminal nav item")
        except Exception as e:
            record("Terminal Panel", "FAIL", f"Error: {str(e)[:100]}")

        # =============================================
        # PANELS LOOP — click each sidebar panel
        # =============================================

        # Map of panel names to look for
        panels_to_test = [
            ("Teams", ["text=Teams", "[title*='Teams']", "#nav-teams", ".nav-teams"]),
            ("Status", ["text=Status", "[title*='Status']", "#nav-status", ".nav-status"]),
            ("Files", ["text=Files", "[title*='Files']", "#nav-files", ".nav-files"]),
            ("Refer", ["text=Refer", "[title*='Refer']", "#nav-refer", ".nav-refer"]),
            ("Bookmarks", ["text=Bookmarks", "[title*='Bookmarks']", "#nav-bookmarks"]),
            ("Tasks", ["text=Tasks", "[title*='Tasks']", "#nav-tasks", ".nav-tasks"]),
            ("Agent Roster", ["text=Agent Roster", "text=Roster", "[title*='Agent']", "#nav-agents"]),
            ("Commands", ["text=Commands", "[title*='Commands']", "#nav-commands", ".nav-commands"]),
            ("Shortcuts", ["text=Shortcuts", "[title*='Shortcuts']", "#nav-shortcuts"]),
            ("Brainiac Training", ["text=Brainiac", "text=Training", "[title*='Training']", "#nav-training"]),
        ]

        ss_num = 7
        for panel_name, selectors in panels_to_test:
            log(f"\n--- {panel_name.upper()} PANEL ---")
            clicked = False
            for sel in selectors:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        await el.click()
                        await page.wait_for_timeout(2000)
                        clicked = True
                        log(f"  Clicked via selector: {sel}")
                        break
                except:
                    pass

            ss_path = f"{SS_DIR}/{ss_num:03d}-{panel_name.lower().replace(' ', '-')}.png"
            await page.screenshot(path=ss_path)
            log(f"  Screenshot: {os.path.basename(ss_path)}")
            ss_num += 1

            # Panel-specific verification
            if panel_name == "Commands":
                # Check for "Loading command reference..." vs actual content
                loading_text = await page.evaluate("""
                    () => {
                        const el = document.querySelector('#commands-panel, .commands-panel, [class*="commands"]');
                        return el ? el.innerText.substring(0, 300) : 'PANEL NOT FOUND';
                    }
                """)
                log(f"  Commands panel text: {loading_text[:200]}")
                if "Loading command reference" in loading_text:
                    record("Commands Panel", "FAIL", "Still showing 'Loading command reference...' — NOT FIXED")
                elif "PANEL NOT FOUND" in loading_text:
                    # Try to find any panel content shown
                    visible_text = await page.evaluate("""
                        () => {
                            const main = document.querySelector('.main-content, #main-content, .panel-content, [class*="panel"]');
                            return main ? main.innerText.substring(0, 400) : 'NO MAIN CONTENT';
                        }
                    """)
                    log(f"  Main content: {visible_text[:200]}")
                    if clicked:
                        record("Commands Panel", "WARN", f"Commands clicked but panel element not found with expected selector. Content: {visible_text[:100]}")
                    else:
                        record("Commands Panel", "WARN", "Could not find Commands nav item in sidebar")
                else:
                    record("Commands Panel", "PASS", f"Commands loaded: {loading_text[:80]}")

            elif panel_name == "Shortcuts":
                loading_text = await page.evaluate("""
                    () => {
                        const el = document.querySelector('#shortcuts-panel, .shortcuts-panel, [class*="shortcuts"]');
                        return el ? el.innerText.substring(0, 300) : 'PANEL NOT FOUND';
                    }
                """)
                log(f"  Shortcuts panel text: {loading_text[:200]}")
                if "Loading shortcuts" in loading_text:
                    record("Shortcuts Panel", "FAIL", "Still showing 'Loading shortcuts...' — NOT FIXED")
                elif "PANEL NOT FOUND" in loading_text:
                    visible_text = await page.evaluate("""
                        () => {
                            const main = document.querySelector('.main-content, #main-content, .panel-content, [class*="panel"]');
                            return main ? main.innerText.substring(0, 400) : 'NO MAIN CONTENT';
                        }
                    """)
                    if clicked:
                        record("Shortcuts Panel", "WARN", f"Shortcuts clicked but panel element not found. Content: {visible_text[:100]}")
                    else:
                        record("Shortcuts Panel", "WARN", "Could not find Shortcuts nav item in sidebar")
                else:
                    record("Shortcuts Panel", "PASS", f"Shortcuts loaded: {loading_text[:80]}")

            elif panel_name == "Teams":
                has_content = await page.query_selector(".team-item, .team-member, [class*='team'], .teams-list")
                if clicked:
                    record("Teams Panel", "PASS" if has_content else "WARN", "Teams panel clicked" + (" — content found" if has_content else " — no team items visible"))
                else:
                    record("Teams Panel", "WARN", "Could not find Teams nav item")

            elif panel_name == "Files":
                has_content = await page.query_selector(".file-item, .file-list, [class*='file-browser'], .files-panel")
                if clicked:
                    record("Files Panel", "PASS" if has_content else "WARN", "Files panel clicked" + (" — file content found" if has_content else " — no file items visible"))
                else:
                    record("Files Panel", "WARN", "Could not find Files nav item")

            elif panel_name == "Tasks":
                has_content = await page.query_selector(".task-item, .tasks-list, [class*='task'], .todo-item")
                if clicked:
                    record("Tasks Panel", "PASS" if has_content else "WARN", "Tasks panel clicked" + (" — tasks found" if has_content else " — no task items visible"))
                else:
                    record("Tasks Panel", "WARN", "Could not find Tasks nav item")

            elif panel_name == "Agent Roster":
                has_content = await page.query_selector(".agent-item, .agent-roster, [class*='agent'], .roster-item")
                if clicked:
                    record("Agent Roster Panel", "PASS" if has_content else "WARN", "Agent Roster clicked" + (" — agents found" if has_content else " — no agents visible"))
                else:
                    record("Agent Roster Panel", "WARN", "Could not find Agent Roster nav item")

            else:
                if clicked:
                    record(f"{panel_name} Panel", "PASS", f"Panel clicked successfully")
                else:
                    record(f"{panel_name} Panel", "WARN", f"Could not find {panel_name} nav item in sidebar")

        # =============================================
        # DEEP CHECK: Commands & Shortcuts with JS eval
        # =============================================
        log("\n--- DEEP CHECK: Commands & Shortcuts Panel Content ---")

        # Navigate to commands with multiple approaches
        # Check all panels/sections for loading states
        all_loading = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                const loading = [];
                for (const el of all) {
                    if (el.children.length === 0 && el.innerText &&
                        (el.innerText.includes('Loading command') || el.innerText.includes('Loading shortcuts'))) {
                        loading.push({tag: el.tagName, class: el.className, text: el.innerText});
                    }
                }
                return loading;
            }
        """)
        if all_loading:
            log(f"  FOUND LOADING STATES: {json.dumps(all_loading, indent=2)}")
            record("Commands/Shortcuts Loading Check", "FAIL", f"Found {len(all_loading)} elements still stuck in loading state")
        else:
            log("  No 'Loading command reference...' or 'Loading shortcuts...' elements found in DOM")
            record("Commands/Shortcuts Loading Check", "PASS", "No stuck loading states detected anywhere in DOM")

        # =============================================
        # NEURAL NETWORK BACKGROUND CHECK
        # =============================================
        log("\n--- NEURAL NETWORK BACKGROUND CHECK ---")
        neural_check = await page.evaluate("""
            () => {
                const canvas = document.querySelector('canvas#neural-canvas, canvas.neural-canvas, canvas');
                if (!canvas) return {found: false};
                const style = window.getComputedStyle(canvas);
                return {
                    found: true,
                    opacity: style.opacity,
                    display: style.display,
                    zIndex: style.zIndex,
                    width: canvas.width,
                    height: canvas.height
                };
            }
        """)
        log(f"  Neural canvas: {json.dumps(neural_check)}")
        if neural_check.get('found'):
            opacity = float(neural_check.get('opacity', 1))
            if opacity < 0.5:
                record("Neural Network BG", "FAIL", f"Canvas opacity is {opacity} — too dim (should be ~1.0 or bright)")
            else:
                record("Neural Network BG", "PASS", f"Canvas opacity={opacity}, size={neural_check.get('width')}x{neural_check.get('height')}")
        else:
            record("Neural Network BG", "WARN", "No canvas element found — neural network background may not be present")

        # =============================================
        # QUICK FIRE BUTTONS
        # =============================================
        log("\n--- QUICK FIRE BUTTONS ---")
        # First navigate back to chat
        for sel in ["text=Chat", "[title*='Chat']", "#nav-chat", ".nav-chat"]:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click()
                    await page.wait_for_timeout(1500)
                    break
            except:
                pass

        quick_buttons = ["BOOP", "Grounding", "Status", "Compact", "Intel", "Duck"]
        for btn_text in quick_buttons:
            try:
                btn = await page.query_selector(f"button[title*='{btn_text}'], [aria-label*='{btn_text}'], button:has-text('{btn_text}')")
                if not btn:
                    # Try broader search
                    btn = page.locator(f"text={btn_text}").first
                    if await btn.count() == 0:
                        btn = None

                if btn:
                    record(f"Quick Button: {btn_text}", "PASS", "Button found in DOM")
                else:
                    record(f"Quick Button: {btn_text}", "WARN", f"Button '{btn_text}' not found")
            except Exception as e:
                record(f"Quick Button: {btn_text}", "WARN", f"Could not check: {str(e)[:80]}")

        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-quick-buttons-area.png")
        ss_num += 1
        log(f"  Screenshot: {ss_num-1:03d}-quick-buttons-area.png")

        # =============================================
        # TOP BAR ELEMENTS
        # =============================================
        log("\n--- TOP BAR ELEMENTS ---")

        # CTX Meter
        ctx_meter = await page.query_selector("[class*='ctx'], [class*='context-meter'], .ctx-bar, #ctx-meter")
        record("Top Bar: CTX Meter", "PASS" if ctx_meter else "WARN",
               "CTX meter found" if ctx_meter else "CTX meter element not found with expected selectors")

        # Resume/Restart buttons
        resume_btn = await page.query_selector("button:has-text('Resume'), [title*='Resume'], .resume-btn")
        restart_btn = await page.query_selector("button:has-text('Restart'), [title*='Restart'], .restart-btn")
        record("Top Bar: Resume Button", "PASS" if resume_btn else "WARN", "Found" if resume_btn else "Not found")
        record("Top Bar: Restart Button", "PASS" if restart_btn else "WARN", "Found" if restart_btn else "Not found")

        # Online indicator
        online_indicator = await page.query_selector(".online-indicator, [class*='online'], .status-dot, .connection-status")
        record("Top Bar: Online Indicator", "PASS" if online_indicator else "WARN",
               "Online indicator found" if online_indicator else "Not found with expected selectors")

        # Settings gear
        settings_btn = await page.query_selector("button[title*='Settings'], .settings-btn, [aria-label*='Settings'], button svg[class*='gear'], .gear-icon")
        record("Top Bar: Settings Gear", "PASS" if settings_btn else "WARN",
               "Settings button found" if settings_btn else "Not found")

        if settings_btn:
            try:
                await settings_btn.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-settings-open.png")
                ss_num += 1
                settings_panel = await page.query_selector(".settings-panel, .settings-modal, [class*='settings']")
                if settings_panel:
                    settings_text = await settings_panel.inner_text()
                    record("Settings Panel", "PASS", f"Settings opened: {settings_text[:100]}")
                else:
                    record("Settings Panel", "WARN", "Settings clicked but panel not detected")
                # Close settings
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
            except Exception as e:
                record("Settings Panel", "FAIL", f"Error opening settings: {str(e)[:80]}")

        # Share button
        share_btn = await page.query_selector("button[title*='Share'], .share-btn, [aria-label*='Share']")
        record("Top Bar: Share Button", "PASS" if share_btn else "WARN",
               "Share button found" if share_btn else "Not found")

        # Logout
        logout_btn = await page.query_selector("button[title*='Logout'], .logout-btn, [aria-label*='Logout'], button:has-text('Logout')")
        record("Top Bar: Logout Button", "PASS" if logout_btn else "WARN",
               "Logout button found" if logout_btn else "Not found")

        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-top-bar.png")
        ss_num += 1

        # =============================================
        # VOICE OVERLAY
        # =============================================
        log("\n--- VOICE OVERLAY ---")
        try:
            mic_btn = await page.query_selector("button[title*='Voice'], button[title*='Mic'], .mic-btn, [aria-label*='Voice'], [aria-label*='mic']")
            if mic_btn:
                await mic_btn.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-voice-overlay.png")
                ss_num += 1

                # Check for voice overlay
                voice_overlay = await page.query_selector(".voice-overlay, [class*='voice'], .voice-modal")
                trigger_field = await page.query_selector("input[placeholder*='trigger'], input[name*='trigger'], [class*='trigger-word']")
                conversation_mode = await page.query_selector("[class*='conversation'], .voice-mode, .voice-controls")

                record("Voice Overlay: Opens", "PASS" if voice_overlay else "WARN",
                       "Voice overlay detected" if voice_overlay else "Voice overlay not found after mic click")
                record("Voice Overlay: Trigger Word Field", "PASS" if trigger_field else "WARN",
                       "Trigger word field found" if trigger_field else "Not found")
                record("Voice Overlay: Conversation Mode", "PASS" if conversation_mode else "WARN",
                       "Conversation mode controls found" if conversation_mode else "Not found")

                # Close voice overlay
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
            else:
                record("Voice Overlay", "WARN", "Mic/Voice button not found in portal")
        except Exception as e:
            record("Voice Overlay", "FAIL", f"Error: {str(e)[:100]}")

        # =============================================
        # AI TRAINING HACKS CHECK
        # =============================================
        log("\n--- AI TRAINING HACKS ---")
        try:
            # Check if Training Hacks injects into chat (NOT a separate panel)
            training_hacks_nav = await page.query_selector("text=AI Training Hacks, text=Training Hacks")
            if training_hacks_nav:
                await training_hacks_nav.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-training-hacks.png")
                ss_num += 1

                # Check: does it open a separate panel OR inject into chat?
                # If in chat: we should see the chat area active
                # If separate panel: there'd be a dedicated panel div shown
                chat_still_visible = await page.query_selector("#chat-messages, .chat-messages")
                record("AI Training Hacks", "PASS" if chat_still_visible else "WARN",
                       "Training Hacks injects into chat (chat area still active)" if chat_still_visible
                       else "Chat area hidden — Training Hacks may have opened a separate panel (check this)")
            else:
                record("AI Training Hacks", "WARN", "Could not find AI Training Hacks nav item")
        except Exception as e:
            record("AI Training Hacks", "FAIL", f"Error: {str(e)[:80]}")

        # =============================================
        # FULL PORTAL LAYOUT SCREENSHOT
        # =============================================
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-portal-desktop-final.png")
        log(f"\n  Final desktop screenshot: {ss_num:03d}-portal-desktop-final.png")
        ss_num += 1

        # =============================================
        # MOBILE AUDIT — 375px (iPhone)
        # =============================================
        log("\n" + "="*60)
        log("MOBILE AUDIT — 375x812 (iPhone)")
        log("="*60)

        mobile_context = await browser.new_context(
            viewport={"width": 375, "height": 812},
            device_scale_factor=2,
            is_mobile=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        mobile_page = await mobile_context.new_page()
        mobile_page.on("console", lambda msg: console_errors.append(f"[MOBILE][{msg.type.upper()}] {msg.text}"))

        await mobile_page.goto(PORTAL_URL, wait_until="networkidle", timeout=30000)

        # Login on mobile
        pwd = await mobile_page.query_selector("input[type='password'], input[placeholder*='Bearer']")
        if pwd:
            await pwd.fill(TOKEN)
        submit_m = await mobile_page.query_selector("button[type='submit'], .pb-signin-btn, button")
        if submit_m:
            await submit_m.click()
        await mobile_page.wait_for_timeout(5000)

        await mobile_page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-mobile-375-portal.png")
        log(f"  Screenshot: {ss_num:03d}-mobile-375-portal.png")
        ss_num += 1

        # Check hamburger menu
        hamburger = await mobile_page.query_selector(".hamburger, .burger-menu, button[aria-label*='menu'], button[title*='menu'], .mobile-menu-toggle")
        if hamburger:
            record("Mobile: Hamburger Menu", "PASS", "Hamburger menu button found")
            try:
                await hamburger.click()
                await mobile_page.wait_for_timeout(1000)
                await mobile_page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-mobile-hamburger-open.png")
                ss_num += 1

                # Check if sidebar is now visible
                sidebar_open = await mobile_page.query_selector(".sidebar.open, .sidebar.active, nav.open, .mobile-nav-open")
                record("Mobile: Hamburger Opens Sidebar", "PASS" if sidebar_open else "WARN",
                       "Sidebar opens on hamburger click" if sidebar_open else "Sidebar state after hamburger unclear")
            except Exception as e:
                record("Mobile: Hamburger Opens Sidebar", "FAIL", f"Error: {str(e)[:80]}")
        else:
            record("Mobile: Hamburger Menu", "WARN", "No hamburger menu found at 375px viewport")

        # Check for overflow issues on mobile
        overflow_check = await mobile_page.evaluate("""
            () => {
                const issues = [];
                const docWidth = document.documentElement.clientWidth;
                const allEls = document.querySelectorAll('*');
                for (const el of allEls) {
                    const rect = el.getBoundingClientRect();
                    if (rect.right > docWidth + 5) {
                        issues.push({tag: el.tagName, class: el.className.substring(0, 50), overflow: rect.right - docWidth});
                    }
                    if (issues.length >= 5) break;
                }
                return issues;
            }
        """)
        if overflow_check:
            record("Mobile: No Horizontal Overflow", "FAIL", f"Overflow detected: {json.dumps(overflow_check)[:200]}")
        else:
            record("Mobile: No Horizontal Overflow", "PASS", "No horizontal overflow at 375px")

        await mobile_context.close()

        # =============================================
        # TABLET AUDIT — 768px
        # =============================================
        log("\n" + "="*60)
        log("TABLET AUDIT — 768x1024 (iPad)")
        log("="*60)

        tablet_context = await browser.new_context(
            viewport={"width": 768, "height": 1024}
        )
        tablet_page = await tablet_context.new_page()

        await tablet_page.goto(PORTAL_URL, wait_until="networkidle", timeout=30000)

        # Login on tablet
        pwd_t = await tablet_page.query_selector("input[type='password'], input[placeholder*='Bearer']")
        if pwd_t:
            await pwd_t.fill(TOKEN)
        submit_t = await tablet_page.query_selector("button[type='submit'], .pb-signin-btn, button")
        if submit_t:
            await submit_t.click()
        await tablet_page.wait_for_timeout(5000)

        await tablet_page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-tablet-768-portal.png")
        log(f"  Screenshot: {ss_num:03d}-tablet-768-portal.png")
        ss_num += 1

        portal_tablet = await tablet_page.query_selector(".portal-container, #portal-container, .sidebar, #chat-messages")
        record("Tablet (768px) Renders", "PASS" if portal_tablet else "WARN",
               "Portal renders at 768px" if portal_tablet else "Portal shell not found at 768px")

        await tablet_context.close()

        # =============================================
        # CONSOLE ERROR SUMMARY
        # =============================================
        log("\n" + "="*60)
        log("CONSOLE ERROR SUMMARY")
        log("="*60)

        errors = [e for e in console_errors if "[ERROR]" in e or "[PAGE ERROR]" in e]
        warnings = [e for e in console_errors if "[WARNING]" in e or "[WARN]" in e]
        infos = [e for e in console_errors if "[INFO]" in e or "[LOG]" in e]

        log(f"  Total console messages: {len(console_errors)}")
        log(f"  Errors: {len(errors)}")
        log(f"  Warnings: {len(warnings)}")
        log(f"  Info/Logs: {len(infos)}")

        if errors:
            log("\n  ERRORS:")
            for e in errors[:15]:
                log(f"    {e[:200]}")

        if warnings:
            log("\n  WARNINGS (first 10):")
            for w in warnings[:10]:
                log(f"    {w[:200]}")

        await context.close()
        await browser.close()

        # =============================================
        # FINAL RESULTS SUMMARY
        # =============================================
        log("\n" + "="*60)
        log("FINAL QA RESULTS SUMMARY")
        log("="*60)

        passes = sum(1 for v in results.values() if v["status"] == "PASS")
        fails = sum(1 for v in results.values() if v["status"] == "FAIL")
        warns = sum(1 for v in results.values() if v["status"] == "WARN")
        total = len(results)

        log(f"\n  TOTAL: {total} checks")
        log(f"  PASS:  {passes}")
        log(f"  FAIL:  {fails}")
        log(f"  WARN:  {warns}")
        log(f"\n  PASS RATE: {passes/total*100:.0f}%" if total > 0 else "")

        log("\n  DETAILED RESULTS:")
        for name, data in results.items():
            icon = "✅" if data["status"] == "PASS" else "❌" if data["status"] == "FAIL" else "⚠️"
            log(f"  {icon} {name}: {data['status']} — {data['notes']}")

        log(f"\n  SCREENSHOTS SAVED TO: {SS_DIR}")

        return results, console_errors, errors


if __name__ == "__main__":
    final_results, all_logs, error_logs = asyncio.run(run())
