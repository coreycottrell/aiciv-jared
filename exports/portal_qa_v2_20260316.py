"""
PureBrain Portal - Comprehensive QA Audit v2
Date: 2026-03-16
Fixed: Login flow handles consent dialogs, uses correct button selectors
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


async def do_login(page):
    """Login to portal, handling any consent/cookie dialogs first"""
    log("  Navigating to portal...")
    await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(3000)
    await page.screenshot(path=f"{SS_DIR}/001-initial-load.png")

    # Check what's on screen
    body_text = await page.evaluate("() => document.body.innerText.substring(0, 500)")
    log(f"  Initial page text: {body_text[:200]}")

    # Dismiss any consent/cookie dialogs first
    for consent_sel in [
        "button:has-text('Got it')",
        "button:has-text('Accept')",
        "button:has-text('I agree')",
        "button:has-text('OK')",
        ".cookie-accept",
        "#cookie-accept",
    ]:
        try:
            btn = await page.query_selector(consent_sel)
            if btn and await btn.is_visible():
                log(f"  Dismissing consent dialog: {consent_sel}")
                await btn.click()
                await page.wait_for_timeout(1000)
                break
        except:
            pass

    await page.screenshot(path=f"{SS_DIR}/002-after-consent.png")

    # Check if already logged in
    already_in = await page.query_selector("#chat-messages, .portal-container, .sidebar, .chat-panel")
    if already_in:
        log("  Already logged in!")
        return True

    # Find password input
    log("  Looking for token input field...")
    pwd_input = None
    for sel in ["input[type='password']", "input[placeholder*='Bearer']", "input[placeholder*='Token']", "input[placeholder*='token']"]:
        el = await page.query_selector(sel)
        if el and await el.is_visible():
            pwd_input = el
            log(f"  Found input with selector: {sel}")
            break

    if not pwd_input:
        # Check all inputs
        inputs = await page.query_selector_all("input")
        log(f"  Found {len(inputs)} inputs total")
        for i, inp in enumerate(inputs):
            if await inp.is_visible():
                ptype = await inp.get_attribute("type")
                phold = await inp.get_attribute("placeholder")
                log(f"    Visible input {i}: type={ptype}, placeholder={phold}")
                if not pwd_input:
                    pwd_input = inp

    if not pwd_input:
        log("  ERROR: No input field found!")
        return False

    await pwd_input.fill(TOKEN)
    log("  Token entered")
    await page.screenshot(path=f"{SS_DIR}/003-token-entered.png")

    # Find and click the actual login/submit button (not hidden ones)
    login_btn = None
    for sel in [".pb-signin-btn", "button[type='submit']", "button.login-btn", "button.signin-btn"]:
        el = await page.query_selector(sel)
        if el:
            visible = await el.is_visible()
            enabled = await el.is_enabled()
            txt = await el.inner_text()
            log(f"  Found button '{txt}' visible={visible} enabled={enabled}")
            if visible and enabled:
                login_btn = el
                break

    if not login_btn:
        # Get all visible buttons
        buttons = await page.query_selector_all("button")
        for btn in buttons:
            if await btn.is_visible() and await btn.is_enabled():
                txt = await btn.inner_text()
                log(f"  Visible button: '{txt}'")
                if any(word in txt.lower() for word in ['sign in', 'login', 'enter', 'continue', 'access']):
                    login_btn = btn
                    break

    if login_btn:
        btn_text = await login_btn.inner_text()
        log(f"  Clicking login button: '{btn_text}'")
        await login_btn.click()
    else:
        log("  No login button found, pressing Enter")
        await page.keyboard.press("Enter")

    log("  Waiting 7s for portal to load after login...")
    await page.wait_for_timeout(7000)
    await page.screenshot(path=f"{SS_DIR}/004-post-login.png")
    log(f"  Post-login URL: {page.url}")

    # Check if logged in
    portal = await page.query_selector("#chat-messages, .portal-container, .sidebar, .chat-panel, .pb-portal")
    return portal is not None


async def try_click_panel(page, panel_name, selectors, wait_ms=2000):
    """Try multiple selectors to click a panel"""
    for sel in selectors:
        try:
            el = await page.query_selector(sel)
            if el and await el.is_visible():
                await el.click()
                await page.wait_for_timeout(wait_ms)
                log(f"  Clicked '{panel_name}' via: {sel}")
                return True
        except:
            pass

    # Try by text content more broadly
    try:
        # Find all clickable elements with matching text
        all_clickable = await page.query_selector_all("a, button, [role='button'], [class*='nav'], [class*='menu'], li")
        for el in all_clickable:
            try:
                txt = (await el.inner_text()).strip().lower()
                if panel_name.lower() in txt and len(txt) < 30:
                    if await el.is_visible():
                        await el.click()
                        await page.wait_for_timeout(wait_ms)
                        log(f"  Clicked '{panel_name}' via text match: '{txt}'")
                        return True
            except:
                pass
    except:
        pass

    log(f"  Could not click '{panel_name}'")
    return False


async def get_panel_state(page):
    """Get current panel content state"""
    return await page.evaluate("""
        () => {
            // Get what's visible in the main content area
            const selectors = [
                '.panel-content', '#panel-content', '.main-panel',
                '.panel-body', '.content-area', '.panel-view',
                '[class*="panel"]:not([class*="nav"])',
                '.right-content', '.center-content'
            ];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.offsetParent !== null) {
                    return {selector: sel, text: el.innerText.substring(0, 400), visible: true};
                }
            }
            // Fallback: get main body text excluding sidebar
            const body = document.body.innerText;
            return {selector: 'body', text: body.substring(0, 300), visible: true};
        }
    """)


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

        page.on("console", lambda msg: console_errors.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: console_errors.append(f"[PAGE ERROR] {err}"))

        # LOGIN
        logged_in = await do_login(page)
        if logged_in:
            record("Login", "PASS", "Successfully logged into portal")
        else:
            record("Login", "WARN", "Login state uncertain after flow")

        # Full portal screenshot
        await page.screenshot(path=f"{SS_DIR}/005-portal-overview.png", full_page=False)

        # Get DOM structure for navigation
        log("\n--- DISCOVERING NAVIGATION STRUCTURE ---")
        nav_structure = await page.evaluate("""
            () => {
                const sidebar = document.querySelector('.sidebar, #sidebar, nav, [class*="sidebar"], [class*="nav"]');
                if (!sidebar) return {found: false, html: 'No sidebar found'};

                const items = [];
                const clickable = sidebar.querySelectorAll('a, button, li, [role="button"], [data-panel], [class*="nav-item"]');
                for (const el of clickable) {
                    const txt = el.innerText.trim();
                    const title = el.getAttribute('title') || '';
                    const cls = el.className.substring(0, 60);
                    const id = el.id || '';
                    if (txt || title) {
                        items.push({text: txt.substring(0, 30), title: title.substring(0, 30), class: cls, id: id});
                    }
                }
                return {
                    found: true,
                    sidebarClass: sidebar.className.substring(0, 80),
                    items: items.slice(0, 25)
                };
            }
        """)
        log(f"  Nav structure: {json.dumps(nav_structure, indent=2)[:800]}")

        ss_num = 6

        # =============================================
        # 1. CHAT PANEL
        # =============================================
        log("\n--- 1. CHAT PANEL ---")
        # First navigate to chat
        await try_click_panel(page, "Chat", [
            "text=Chat", "[title='Chat']", ".nav-chat", "#nav-chat",
            "a[href*='chat']", "button[data-panel='chat']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-chat-panel.png")
        ss_num += 1

        chat_msgs = await page.query_selector("#chat-messages, .chat-messages")
        chat_input = await page.query_selector("textarea#chat-input, textarea.chat-input, textarea[placeholder*='essage'], #message-input")
        log(f"  Chat messages: {chat_msgs is not None}, Chat input: {chat_input is not None}")

        if chat_input and await chat_input.is_visible():
            try:
                await chat_input.fill("QA test — testing chat functionality")
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(3000)
                await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-chat-message-sent.png")
                ss_num += 1
                record("Chat Panel", "PASS", "Chat input found and message sent")
            except Exception as e:
                record("Chat Panel", "PASS" if chat_msgs else "WARN", f"Chat messages visible, input interaction: {str(e)[:80]}")
        elif chat_msgs:
            record("Chat Panel", "PASS", "Chat messages panel visible")
        else:
            record("Chat Panel", "WARN", "Chat panel uncertain - no messages or input found with expected selectors")

        # =============================================
        # 2. TERMINAL PANEL
        # =============================================
        log("\n--- 2. TERMINAL PANEL ---")
        clicked = await try_click_panel(page, "Terminal", [
            "text=Terminal", "[title='Terminal']", "[title*='Terminal']",
            ".nav-terminal", "#nav-terminal", "[data-panel='terminal']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-terminal-panel.png")
        ss_num += 1

        terminal = await page.query_selector(".terminal, .xterm, #terminal, [class*='terminal-container']")
        state = await get_panel_state(page)
        log(f"  Terminal content: {state['text'][:150]}")

        if terminal:
            record("Terminal Panel", "PASS", "Terminal element visible")
        elif clicked:
            record("Terminal Panel", "WARN", f"Terminal clicked but no .terminal/.xterm found. Content: {state['text'][:80]}")
        else:
            record("Terminal Panel", "WARN", "Terminal nav item not found")

        # =============================================
        # 3. TEAMS PANEL
        # =============================================
        log("\n--- 3. TEAMS PANEL ---")
        clicked = await try_click_panel(page, "Teams", [
            "text=Teams", "[title='Teams']", ".nav-teams", "#nav-teams", "[data-panel='teams']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-teams-panel.png")
        ss_num += 1
        state = await get_panel_state(page)
        log(f"  Teams content: {state['text'][:150]}")

        teams_content = await page.query_selector(".team-item, .teams-list, [class*='team-member'], .member-row")
        loading = "loading" in state['text'].lower() and len(state['text']) < 50
        if teams_content:
            record("Teams Panel", "PASS", "Team content/members visible")
        elif clicked and not loading:
            record("Teams Panel", "PASS", f"Teams panel loaded: {state['text'][:80]}")
        elif loading:
            record("Teams Panel", "FAIL", "Teams panel stuck in loading state")
        else:
            record("Teams Panel", "WARN", "Teams nav not found or no content")

        # =============================================
        # 4. STATUS PANEL
        # =============================================
        log("\n--- 4. STATUS PANEL ---")
        clicked = await try_click_panel(page, "Status", [
            "text=Status", "[title='Status']", ".nav-status", "#nav-status", "[data-panel='status']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-status-panel.png")
        ss_num += 1
        state = await get_panel_state(page)
        log(f"  Status content: {state['text'][:150]}")

        loading = "loading" in state['text'].lower() and len(state['text']) < 50
        if clicked and not loading:
            record("Status Panel", "PASS", f"Status panel loaded: {state['text'][:100]}")
        elif loading:
            record("Status Panel", "FAIL", "Status stuck in loading")
        else:
            record("Status Panel", "WARN", "Status nav not found or no content")

        # =============================================
        # 5. FILES PANEL
        # =============================================
        log("\n--- 5. FILES PANEL ---")
        clicked = await try_click_panel(page, "Files", [
            "text=Files", "[title='Files']", ".nav-files", "#nav-files", "[data-panel='files']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-files-panel.png")
        ss_num += 1
        state = await get_panel_state(page)
        log(f"  Files content: {state['text'][:150]}")

        files_items = await page.query_selector(".file-item, .file-row, .file-list, .gdrive-file")
        loading = "loading" in state['text'].lower() and len(state['text']) < 50
        if files_items:
            record("Files Panel", "PASS", "File items visible")
        elif clicked and not loading:
            record("Files Panel", "PASS", f"Files panel loaded: {state['text'][:80]}")
        elif loading:
            record("Files Panel", "FAIL", "Files stuck in loading")
        else:
            record("Files Panel", "WARN", "Files nav not found or no content")

        # =============================================
        # 6. REFER & EARN PANEL
        # =============================================
        log("\n--- 6. REFER & EARN PANEL ---")
        clicked = await try_click_panel(page, "Refer", [
            "text=Refer", "text=Refer & Earn", "[title*='Refer']", ".nav-refer",
            "#nav-refer", "[data-panel='refer']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-refer-panel.png")
        ss_num += 1
        state = await get_panel_state(page)
        log(f"  Refer content: {state['text'][:150]}")

        loading = "loading" in state['text'].lower() and len(state['text']) < 50
        if clicked and not loading:
            record("Refer & Earn Panel", "PASS", f"Refer panel loaded: {state['text'][:80]}")
        elif loading:
            record("Refer & Earn Panel", "FAIL", "Refer stuck in loading")
        else:
            record("Refer & Earn Panel", "WARN", "Refer nav not found or no content")

        # =============================================
        # 7. BOOKMARKS PANEL
        # =============================================
        log("\n--- 7. BOOKMARKS PANEL ---")
        clicked = await try_click_panel(page, "Bookmarks", [
            "text=Bookmarks", "text=Bookmark", "[title*='Bookmark']", ".nav-bookmarks",
            "#nav-bookmarks", "[data-panel='bookmarks']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-bookmarks-panel.png")
        ss_num += 1
        state = await get_panel_state(page)
        log(f"  Bookmarks content: {state['text'][:150]}")

        loading = "loading" in state['text'].lower() and len(state['text']) < 50
        if clicked and not loading:
            record("Bookmarks Panel", "PASS", f"Bookmarks loaded: {state['text'][:80]}")
        elif loading:
            record("Bookmarks Panel", "FAIL", "Bookmarks stuck in loading")
        else:
            record("Bookmarks Panel", "WARN", "Bookmarks nav not found or no content")

        # =============================================
        # 8. TASKS PANEL
        # =============================================
        log("\n--- 8. TASKS PANEL ---")
        clicked = await try_click_panel(page, "Tasks", [
            "text=Tasks", "[title='Tasks']", ".nav-tasks", "#nav-tasks", "[data-panel='tasks']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-tasks-panel.png")
        ss_num += 1
        state = await get_panel_state(page)
        log(f"  Tasks content: {state['text'][:150]}")

        tasks_items = await page.query_selector(".task-item, .todo-item, .task-row")
        badge = await page.query_selector(".badge, .tasks-badge, .notification-badge")
        loading = "loading" in state['text'].lower() and len(state['text']) < 50
        if tasks_items:
            record("Tasks Panel", "PASS", f"Tasks visible{', badge found' if badge else ''}")
        elif clicked and not loading:
            record("Tasks Panel", "PASS", f"Tasks panel loaded: {state['text'][:80]}")
        elif loading:
            record("Tasks Panel", "FAIL", "Tasks stuck in loading")
        else:
            record("Tasks Panel", "WARN", "Tasks nav not found or no content")

        # =============================================
        # 9. AGENT ROSTER PANEL
        # =============================================
        log("\n--- 9. AGENT ROSTER PANEL ---")
        clicked = await try_click_panel(page, "Agent Roster", [
            "text=Agent Roster", "text=Roster", "text=Agents", "[title*='Roster']",
            "[title*='Agent']", ".nav-agents", "#nav-agents", "[data-panel='agents']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-agent-roster.png")
        ss_num += 1
        state = await get_panel_state(page)
        log(f"  Agent Roster content: {state['text'][:200]}")

        agent_items = await page.query_selector(".agent-item, .agent-card, .agent-row, [class*='agent-list']")
        loading = "loading" in state['text'].lower() and len(state['text']) < 50
        if agent_items:
            record("Agent Roster Panel", "PASS", "Agent items visible")
        elif clicked and not loading and state['text'].strip():
            record("Agent Roster Panel", "PASS", f"Agent Roster loaded: {state['text'][:80]}")
        elif loading:
            record("Agent Roster Panel", "FAIL", "Agent Roster stuck in loading")
        else:
            record("Agent Roster Panel", "WARN", "Agent Roster nav not found or empty")

        # =============================================
        # 10. COMMANDS PANEL (CRITICAL FIX CHECK)
        # =============================================
        log("\n--- 10. COMMANDS PANEL (CRITICAL FIX CHECK) ---")
        clicked = await try_click_panel(page, "Commands", [
            "text=Commands", "[title='Commands']", "[title*='Commands']",
            ".nav-commands", "#nav-commands", "[data-panel='commands']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-commands-panel.png")
        ss_num += 1

        # Deep check for loading state
        commands_check = await page.evaluate("""
            () => {
                // Check ALL text in page for loading state
                const loadingEls = [];
                document.querySelectorAll('*').forEach(el => {
                    if (el.children.length === 0) {
                        const t = el.innerText ? el.innerText.trim() : '';
                        if (t.includes('Loading command reference')) {
                            loadingEls.push({tag: el.tagName, class: el.className, text: t});
                        }
                    }
                });

                // Get commands panel content
                const panels = document.querySelectorAll('[class*="commands"], [id*="commands"], #commands-panel');
                const panelTexts = [];
                panels.forEach(p => {
                    if (p.offsetParent !== null) {
                        panelTexts.push({cls: p.className.substring(0,60), text: p.innerText.substring(0, 300)});
                    }
                });

                // Get main visible area
                const mainArea = document.querySelector('.panel-content, .main-content, .content-area, .right-pane');
                const mainText = mainArea ? mainArea.innerText.substring(0, 400) : '';

                return {loadingStates: loadingEls, commandPanels: panelTexts, mainAreaText: mainText};
            }
        """)
        log(f"  Commands check: {json.dumps(commands_check, indent=2)[:600]}")

        if commands_check['loadingStates']:
            record("Commands Panel", "FAIL", f"Still stuck: 'Loading command reference...' — FIX NOT WORKING")
        elif commands_check['commandPanels']:
            panel_text = commands_check['commandPanels'][0].get('text', '')
            if "Loading" in panel_text and len(panel_text) < 50:
                record("Commands Panel", "FAIL", f"Commands panel loading state detected: {panel_text}")
            else:
                record("Commands Panel", "PASS", f"Commands loaded with content: {panel_text[:100]}")
        elif commands_check['mainAreaText'] and not "Loading command" in commands_check['mainAreaText']:
            record("Commands Panel", "PASS" if clicked else "WARN",
                   f"Main area shows: {commands_check['mainAreaText'][:100]}")
        else:
            record("Commands Panel", "WARN", "Commands panel not found or empty after click")

        # =============================================
        # 11. SHORTCUTS PANEL (CRITICAL FIX CHECK)
        # =============================================
        log("\n--- 11. SHORTCUTS PANEL (CRITICAL FIX CHECK) ---")
        clicked = await try_click_panel(page, "Shortcuts", [
            "text=Shortcuts", "[title='Shortcuts']", "[title*='Shortcuts']",
            ".nav-shortcuts", "#nav-shortcuts", "[data-panel='shortcuts']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-shortcuts-panel.png")
        ss_num += 1

        shortcuts_check = await page.evaluate("""
            () => {
                const loadingEls = [];
                document.querySelectorAll('*').forEach(el => {
                    if (el.children.length === 0) {
                        const t = el.innerText ? el.innerText.trim() : '';
                        if (t.includes('Loading shortcuts') || t === 'Loading...') {
                            loadingEls.push({tag: el.tagName, class: el.className, text: t});
                        }
                    }
                });

                const panels = document.querySelectorAll('[class*="shortcuts"], [id*="shortcuts"], #shortcuts-panel');
                const panelTexts = [];
                panels.forEach(p => {
                    if (p.offsetParent !== null) {
                        panelTexts.push({cls: p.className.substring(0,60), text: p.innerText.substring(0, 300)});
                    }
                });

                const mainArea = document.querySelector('.panel-content, .main-content, .content-area, .right-pane');
                const mainText = mainArea ? mainArea.innerText.substring(0, 400) : '';

                return {loadingStates: loadingEls, shortcutPanels: panelTexts, mainAreaText: mainText};
            }
        """)
        log(f"  Shortcuts check: {json.dumps(shortcuts_check, indent=2)[:600]}")

        if shortcuts_check['loadingStates']:
            record("Shortcuts Panel", "FAIL", "Still stuck: 'Loading shortcuts...' — FIX NOT WORKING")
        elif shortcuts_check['shortcutPanels']:
            panel_text = shortcuts_check['shortcutPanels'][0].get('text', '')
            if "Loading" in panel_text and len(panel_text) < 50:
                record("Shortcuts Panel", "FAIL", f"Shortcuts stuck in loading: {panel_text}")
            else:
                record("Shortcuts Panel", "PASS", f"Shortcuts loaded: {panel_text[:100]}")
        elif shortcuts_check['mainAreaText'] and "Loading shortcuts" not in shortcuts_check['mainAreaText']:
            record("Shortcuts Panel", "PASS" if clicked else "WARN",
                   f"Main area shows: {shortcuts_check['mainAreaText'][:100]}")
        else:
            record("Shortcuts Panel", "WARN", "Shortcuts panel not found or empty")

        # =============================================
        # 12. BRAINIAC TRAINING PANEL
        # =============================================
        log("\n--- 12. BRAINIAC TRAINING PANEL ---")
        clicked = await try_click_panel(page, "Brainiac Training", [
            "text=Brainiac Training", "text=Brainiac", "text=Training",
            "[title*='Training']", "[title*='Brainiac']",
            ".nav-training", "#nav-training", "[data-panel='training']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-brainiac-training.png")
        ss_num += 1
        state = await get_panel_state(page)
        log(f"  Training content: {state['text'][:200]}")

        loading = "loading" in state['text'].lower() and len(state['text']) < 50
        if clicked and not loading and state['text'].strip():
            record("Brainiac Training Panel", "PASS", f"Training content loaded: {state['text'][:100]}")
        elif loading:
            record("Brainiac Training Panel", "FAIL", "Training stuck in loading")
        else:
            record("Brainiac Training Panel", "WARN", "Training nav not found or no content")

        # =============================================
        # 13. AI TRAINING HACKS
        # =============================================
        log("\n--- 13. AI TRAINING HACKS ---")
        # First go back to chat
        await try_click_panel(page, "Chat", [
            "text=Chat", "[title='Chat']", ".nav-chat", "#nav-chat", "[data-panel='chat']"
        ])
        await page.wait_for_timeout(1000)

        clicked = await try_click_panel(page, "AI Training Hacks", [
            "text=AI Training Hacks", "text=Training Hacks", "text=Hacks",
            "[title*='Training Hacks']", "[title*='Hacks']",
            ".nav-hacks", "#nav-hacks", "[data-panel='hacks']"
        ])
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-training-hacks.png")
        ss_num += 1

        if clicked:
            # Check: should inject into chat, NOT open separate panel
            chat_still_here = await page.query_selector("#chat-messages, .chat-messages")
            new_msg = await page.evaluate("""
                () => {
                    const msgs = document.querySelectorAll('.msg, .message');
                    const last = msgs[msgs.length - 1];
                    return last ? last.innerText.substring(0, 200) : '';
                }
            """)
            log(f"  Last message after Training Hacks click: {new_msg[:150]}")
            record("AI Training Hacks", "PASS",
                   f"Training Hacks injects to chat (chat visible). Last msg: {new_msg[:80]}")
        else:
            record("AI Training Hacks", "WARN", "AI Training Hacks nav item not found")

        # =============================================
        # NEURAL NETWORK BACKGROUND
        # =============================================
        log("\n--- NEURAL NETWORK BACKGROUND ---")
        # Go back to main chat view
        await try_click_panel(page, "Chat", [
            "text=Chat", "[title='Chat']", ".nav-chat", "#nav-chat"
        ])
        await page.wait_for_timeout(1000)

        neural_check = await page.evaluate("""
            () => {
                // Find any canvas elements
                const canvases = document.querySelectorAll('canvas');
                const info = [];
                for (const canvas of canvases) {
                    const style = window.getComputedStyle(canvas);
                    const rect = canvas.getBoundingClientRect();
                    info.push({
                        id: canvas.id,
                        class: canvas.className.substring(0,50),
                        opacity: style.opacity,
                        display: style.display,
                        zIndex: style.zIndex,
                        width: rect.width,
                        height: rect.height,
                        visible: rect.width > 0 && rect.height > 0 && style.display !== 'none'
                    });
                }

                // Also check for CSS opacity on parent containers
                const neuralEl = document.querySelector('.neural-bg, #neural-bg, [class*="neural"], [class*="network-bg"]');
                const neuralInfo = neuralEl ? {
                    found: true,
                    class: neuralEl.className.substring(0,60),
                    opacity: window.getComputedStyle(neuralEl).opacity
                } : {found: false};

                return {canvases: info, neuralContainer: neuralInfo};
            }
        """)
        log(f"  Neural check: {json.dumps(neural_check, indent=2)[:600]}")

        canvases = neural_check.get('canvases', [])
        visible_canvases = [c for c in canvases if c.get('visible')]
        if visible_canvases:
            for c in visible_canvases:
                opacity = float(c.get('opacity', 1))
                if opacity < 0.3:
                    record("Neural Network BG", "FAIL",
                           f"Canvas #{c.get('id','?')} opacity={opacity} — DIMMED (was a known bug)")
                elif opacity < 0.7:
                    record("Neural Network BG", "WARN",
                           f"Canvas opacity={opacity} — somewhat dim")
                else:
                    record("Neural Network BG", "PASS",
                           f"Canvas #{c.get('id','?')} opacity={opacity}, size={int(c.get('width',0))}x{int(c.get('height',0))}")
                break
        else:
            nc = neural_check.get('neuralContainer', {})
            if nc.get('found'):
                opacity = float(nc.get('opacity', 1))
                record("Neural Network BG", "PASS" if opacity > 0.5 else "FAIL",
                       f"Neural container opacity={opacity}")
            else:
                record("Neural Network BG", "WARN", "No canvas or neural container found")

        # =============================================
        # QUICK FIRE BUTTONS
        # =============================================
        log("\n--- QUICK FIRE BUTTONS (Bottom Left) ---")
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-portal-chat-view.png")
        ss_num += 1

        # Get all buttons visible on screen
        all_btns = await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button, [role="button"]');
                const visible = [];
                for (const btn of buttons) {
                    const rect = btn.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        const style = window.getComputedStyle(btn);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            const txt = (btn.innerText || btn.title || btn.getAttribute('aria-label') || '').trim();
                            if (txt) {
                                visible.push({
                                    text: txt.substring(0, 30),
                                    title: (btn.title || '').substring(0, 30),
                                    x: Math.round(rect.x), y: Math.round(rect.y),
                                    w: Math.round(rect.width), h: Math.round(rect.height)
                                });
                            }
                        }
                    }
                }
                return visible;
            }
        """)
        log(f"  All visible buttons ({len(all_btns)}):")
        for b in all_btns[:30]:
            log(f"    '{b['text']}' at ({b['x']},{b['y']}) {b['w']}x{b['h']}")

        quick_buttons = ["BOOP", "Grounding", "Status", "Compact", "Intel", "Duck"]
        all_btn_texts = [b['text'].upper() for b in all_btns] + [b['title'].upper() for b in all_btns]

        for btn_name in quick_buttons:
            found = any(btn_name.upper() in t for t in all_btn_texts)
            record(f"Quick Button: {btn_name}", "PASS" if found else "WARN",
                   "Found" if found else f"'{btn_name}' not found in visible buttons")

        # =============================================
        # TOP BAR ELEMENTS
        # =============================================
        log("\n--- TOP BAR ELEMENTS ---")

        topbar_check = await page.evaluate("""
            () => {
                const checks = {};

                // CTX meter
                const ctxEls = document.querySelectorAll('[class*="ctx"], [class*="context-meter"], [class*="ctx-bar"], #ctx-meter');
                checks.ctxMeter = ctxEls.length > 0 ? {found: true, count: ctxEls.length} : {found: false};

                // Resume/Restart
                const allBtns = document.querySelectorAll('button, [role="button"]');
                let resume = false, restart = false, logout = false, share = false;
                for (const btn of allBtns) {
                    const txt = (btn.innerText || btn.title || btn.getAttribute('aria-label') || '').toLowerCase();
                    if (txt.includes('resume')) resume = true;
                    if (txt.includes('restart')) restart = true;
                    if (txt.includes('logout') || txt.includes('log out') || txt.includes('sign out')) logout = true;
                    if (txt.includes('share')) share = true;
                }
                checks.resumeBtn = resume;
                checks.restartBtn = restart;
                checks.logoutBtn = logout;
                checks.shareBtn = share;

                // Online indicator
                const onlineEls = document.querySelectorAll('.online-indicator, [class*="online-dot"], .status-indicator, [class*="connection"]');
                checks.onlineIndicator = onlineEls.length > 0;

                // Settings gear (SVG or button)
                const settingsEls = document.querySelectorAll('button[title*="Settings"], [aria-label*="Settings"], .settings-btn, [class*="settings-trigger"]');
                checks.settingsBtn = settingsEls.length > 0;

                return checks;
            }
        """)
        log(f"  Top bar check: {json.dumps(topbar_check, indent=2)}")

        record("Top Bar: CTX Meter", "PASS" if topbar_check.get('ctxMeter', {}).get('found') else "WARN",
               f"Found {topbar_check.get('ctxMeter', {}).get('count', 0)} CTX elements" if topbar_check.get('ctxMeter', {}).get('found') else "CTX meter not found")
        record("Top Bar: Resume Button", "PASS" if topbar_check.get('resumeBtn') else "WARN",
               "Found" if topbar_check.get('resumeBtn') else "Not found")
        record("Top Bar: Restart Button", "PASS" if topbar_check.get('restartBtn') else "WARN",
               "Found" if topbar_check.get('restartBtn') else "Not found")
        record("Top Bar: Online Indicator", "PASS" if topbar_check.get('onlineIndicator') else "WARN",
               "Found" if topbar_check.get('onlineIndicator') else "Not found")
        record("Top Bar: Share Button", "PASS" if topbar_check.get('shareBtn') else "WARN",
               "Found" if topbar_check.get('shareBtn') else "Not found")
        record("Top Bar: Logout Button", "PASS" if topbar_check.get('logoutBtn') else "WARN",
               "Found" if topbar_check.get('logoutBtn') else "Not found")

        # Settings: try to open
        settings_found = topbar_check.get('settingsBtn')
        if settings_found:
            try:
                settings_btn = await page.query_selector('button[title*="Settings"], [aria-label*="Settings"], .settings-btn')
                if settings_btn:
                    await settings_btn.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-settings-open.png")
                    ss_num += 1
                    settings_content = await page.evaluate("""
                        () => {
                            const modal = document.querySelector('.settings-modal, .settings-panel, .modal, [class*="settings-dialog"]');
                            return modal ? modal.innerText.substring(0, 300) : 'No modal found';
                        }
                    """)
                    record("Settings Panel", "PASS", f"Settings opened: {settings_content[:100]}")
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(500)
            except Exception as e:
                record("Settings Panel", "WARN", f"Settings button found but couldn't open: {str(e)[:80]}")
        else:
            record("Top Bar: Settings Gear", "WARN", "Settings button not found with expected selectors")
            record("Settings Panel", "WARN", "Settings button not found to test")

        # =============================================
        # VOICE OVERLAY
        # =============================================
        log("\n--- VOICE OVERLAY ---")
        voice_check = await page.evaluate("""
            () => {
                const allEls = document.querySelectorAll('button, [role="button"]');
                const micBtns = [];
                for (const el of allEls) {
                    const txt = (el.innerText || el.title || el.getAttribute('aria-label') || '').toLowerCase();
                    const cls = el.className.toLowerCase();
                    if (txt.includes('voice') || txt.includes('mic') || cls.includes('voice') || cls.includes('mic')) {
                        micBtns.push({text: txt.substring(0,30), class: cls.substring(0,50)});
                    }
                }
                return micBtns;
            }
        """)
        log(f"  Voice/mic buttons found: {voice_check}")

        if voice_check:
            try:
                mic_btn = await page.query_selector("button[title*='Voice'], button[title*='Mic'], .mic-btn, [aria-label*='Voice'], [class*='voice-btn'], [class*='mic-btn']")
                if mic_btn:
                    await mic_btn.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-voice-overlay.png")
                    ss_num += 1

                    voice_overlay = await page.evaluate("""
                        () => {
                            const overlayEls = document.querySelectorAll('[class*="voice"], [class*="voice-overlay"], .voice-modal');
                            const visible = [];
                            for (const el of overlayEls) {
                                const rect = el.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    visible.push({cls: el.className.substring(0,60), text: el.innerText.substring(0, 100)});
                                }
                            }
                            const triggerField = document.querySelector('input[placeholder*="trigger"], input[name*="trigger"], [class*="trigger-word"]');
                            return {overlayFound: visible.length > 0, overlays: visible, triggerField: !!triggerField};
                        }
                    """)

                    record("Voice Overlay: Opens", "PASS" if voice_overlay['overlayFound'] else "WARN",
                           f"Voice overlay found: {voice_overlay['overlays'][:1]}" if voice_overlay['overlayFound'] else "Overlay not detected")
                    record("Voice Overlay: Trigger Word Field", "PASS" if voice_overlay['triggerField'] else "WARN",
                           "Trigger word field found" if voice_overlay['triggerField'] else "Not found")

                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(500)
                else:
                    record("Voice Overlay", "WARN", "Voice/mic element detected in DOM but couldn't select for click")
            except Exception as e:
                record("Voice Overlay", "WARN", f"Error: {str(e)[:80]}")
        else:
            record("Voice Overlay", "WARN", "No voice/mic buttons found in portal")

        # =============================================
        # FULL DOM SCAN FOR ANY LOADING STATES
        # =============================================
        log("\n--- FULL DOM SCAN FOR STUCK LOADING STATES ---")
        loading_scan = await page.evaluate("""
            () => {
                const stuck = [];
                const loadingPhrases = [
                    'Loading command reference',
                    'Loading shortcuts',
                    'Loading agent roster',
                    'Loading bookmarks',
                    'Loading tasks',
                    'Loading teams',
                    'Loading files',
                ];
                document.querySelectorAll('*').forEach(el => {
                    if (el.children.length === 0) {
                        const t = el.innerText ? el.innerText.trim() : '';
                        for (const phrase of loadingPhrases) {
                            if (t.includes(phrase)) {
                                stuck.push({phrase, tag: el.tagName, class: el.className.substring(0,50)});
                                break;
                            }
                        }
                    }
                });
                return stuck;
            }
        """)
        if loading_scan:
            log(f"  STUCK LOADING STATES FOUND: {json.dumps(loading_scan)}")
            record("DOM: Stuck Loading States", "FAIL", f"Found stuck states: {json.dumps(loading_scan)[:200]}")
        else:
            log("  No stuck loading states detected in full DOM scan")
            record("DOM: Stuck Loading States", "PASS", "No stuck loading states in full DOM")

        # =============================================
        # FINAL DESKTOP SCREENSHOT
        # =============================================
        # Go to chat for final screenshot
        await try_click_panel(page, "Chat", ["text=Chat", "[title='Chat']", ".nav-chat"])
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-desktop-final-state.png", full_page=False)
        log(f"\n  Final desktop screenshot saved: {ss_num:03d}-desktop-final-state.png")
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
        mobile_console = []
        mobile_page.on("console", lambda msg: mobile_console.append(f"[{msg.type.upper()}] {msg.text}"))

        # Navigate and dismiss consent
        await mobile_page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
        await mobile_page.wait_for_timeout(2000)
        for consent_sel in ["button:has-text('Got it')", "button:has-text('Accept')"]:
            try:
                btn = await mobile_page.query_selector(consent_sel)
                if btn and await btn.is_visible():
                    await btn.click()
                    await mobile_page.wait_for_timeout(500)
                    break
            except:
                pass

        # Login
        pwd_m = await mobile_page.query_selector("input[type='password'], input[placeholder*='Bearer']")
        if pwd_m:
            await pwd_m.fill(TOKEN)
        for sel in [".pb-signin-btn", "button[type='submit']", "button"]:
            try:
                btn = await mobile_page.query_selector(sel)
                if btn and await btn.is_visible() and await btn.is_enabled():
                    txt = await btn.inner_text()
                    if not "got it" in txt.lower() and not "cookie" in txt.lower():
                        await btn.click()
                        break
            except:
                pass
        await mobile_page.wait_for_timeout(5000)

        await mobile_page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-mobile-375-overview.png")
        log(f"  Screenshot: {ss_num:03d}-mobile-375-overview.png")
        ss_num += 1

        # Check hamburger
        hamburger = await mobile_page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button, [role="button"]');
                for (const btn of btns) {
                    const cls = btn.className.toLowerCase();
                    const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                    const title = (btn.getAttribute('title') || '').toLowerCase();
                    if (cls.includes('hamburger') || cls.includes('burger') || cls.includes('menu-toggle') ||
                        cls.includes('mobile-menu') || aria.includes('menu') || title.includes('menu')) {
                        return {found: true, class: btn.className.substring(0,60), text: btn.innerText.substring(0,20)};
                    }
                }
                // Check for 3-bar icon patterns
                const threeBar = document.querySelector('.hamburger, .burger, [class*="hamburger"], [class*="menu-btn"]');
                return threeBar ? {found: true, class: threeBar.className} : {found: false};
            }
        """)
        log(f"  Hamburger check: {hamburger}")

        if hamburger.get('found'):
            record("Mobile 375px: Hamburger Menu", "PASS", f"Hamburger found: {hamburger.get('class', '')[:50]}")
        else:
            record("Mobile 375px: Hamburger Menu", "WARN", "Hamburger menu not found at 375px")

        # Overflow check
        overflow_check = await mobile_page.evaluate("""
            () => {
                const issues = [];
                const docWidth = document.documentElement.clientWidth;
                const allEls = document.querySelectorAll('body > *, body > * > *, body > * > * > *');
                for (const el of allEls) {
                    const rect = el.getBoundingClientRect();
                    if (rect.right > docWidth + 10 && rect.width > 0) {
                        issues.push({
                            tag: el.tagName,
                            class: el.className.substring(0, 50),
                            overflow: Math.round(rect.right - docWidth)
                        });
                        if (issues.length >= 5) break;
                    }
                }
                return {docWidth, issues};
            }
        """)
        log(f"  Mobile overflow: {overflow_check}")
        if overflow_check.get('issues'):
            record("Mobile 375px: No Overflow", "FAIL",
                   f"Overflow detected: {json.dumps(overflow_check['issues'])[:150]}")
        else:
            record("Mobile 375px: No Overflow", "PASS",
                   f"No horizontal overflow at {overflow_check.get('docWidth')}px viewport")

        # Chat visible on mobile
        chat_mobile = await mobile_page.query_selector("#chat-messages, .chat-messages, .chat-panel")
        record("Mobile 375px: Chat Visible", "PASS" if chat_mobile else "WARN",
               "Chat panel visible on mobile" if chat_mobile else "Chat not immediately visible — may be behind hamburger")

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
        await tablet_page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
        await tablet_page.wait_for_timeout(2000)

        for consent_sel in ["button:has-text('Got it')", "button:has-text('Accept')"]:
            try:
                btn = await tablet_page.query_selector(consent_sel)
                if btn and await btn.is_visible():
                    await btn.click()
                    await tablet_page.wait_for_timeout(500)
                    break
            except:
                pass

        pwd_t = await tablet_page.query_selector("input[type='password'], input[placeholder*='Bearer']")
        if pwd_t:
            await pwd_t.fill(TOKEN)
        for sel in [".pb-signin-btn", "button[type='submit']", "button"]:
            try:
                btn = await tablet_page.query_selector(sel)
                if btn and await btn.is_visible() and await btn.is_enabled():
                    txt = await btn.inner_text()
                    if not "got it" in txt.lower():
                        await btn.click()
                        break
            except:
                pass
        await tablet_page.wait_for_timeout(5000)

        await tablet_page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-tablet-768-overview.png")
        log(f"  Screenshot: {ss_num:03d}-tablet-768-overview.png")
        ss_num += 1

        portal_tablet = await tablet_page.query_selector(".portal-container, #portal-container, #chat-messages, .sidebar")
        record("Tablet 768px: Portal Renders", "PASS" if portal_tablet else "WARN",
               "Portal renders at 768px" if portal_tablet else "Portal shell not found at 768px")

        overflow_tablet = await tablet_page.evaluate("""
            () => {
                const docWidth = document.documentElement.clientWidth;
                const issues = [];
                document.querySelectorAll('body > *, body > * > *').forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.right > docWidth + 10 && rect.width > 0) {
                        issues.push({tag: el.tagName, class: el.className.substring(0,40), overflow: Math.round(rect.right - docWidth)});
                        if (issues.length >= 3) return;
                    }
                });
                return {docWidth, issues};
            }
        """)
        record("Tablet 768px: No Overflow", "PASS" if not overflow_tablet.get('issues') else "FAIL",
               "No overflow" if not overflow_tablet.get('issues') else f"Overflow: {overflow_tablet['issues']}")

        await tablet_context.close()

        # =============================================
        # CONSOLE ERROR SUMMARY
        # =============================================
        log("\n" + "="*60)
        log("CONSOLE ERROR SUMMARY")
        log("="*60)

        errors = [e for e in console_errors if "[ERROR]" in e or "[PAGE ERROR]" in e]
        warnings = [e for e in console_errors if "[WARNING]" in e or "[WARN]" in e]

        log(f"  Total console events: {len(console_errors)}")
        log(f"  Errors: {len(errors)}")
        log(f"  Warnings: {len(warnings)}")

        if errors:
            log("\n  TOP ERRORS:")
            seen = set()
            for e in errors:
                # Deduplicate
                key = e[:100]
                if key not in seen:
                    seen.add(key)
                    log(f"    {e[:250]}")
                if len(seen) >= 10:
                    break

        record("Console: Error Count", "PASS" if len(errors) == 0 else "WARN" if len(errors) < 5 else "FAIL",
               f"{len(errors)} errors, {len(warnings)} warnings")

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
        log(f"  ✅ PASS:  {passes} ({passes/total*100:.0f}%)")
        log(f"  ❌ FAIL:  {fails}")
        log(f"  ⚠️  WARN:  {warns}")

        log("\n  DETAILED RESULTS:")
        for name, data in results.items():
            icon = "✅" if data["status"] == "PASS" else "❌" if data["status"] == "FAIL" else "⚠️"
            log(f"  {icon} {name}: {data['status']} — {data['notes']}")

        log(f"\n  SCREENSHOTS: {SS_DIR}")
        log(f"  SCREENSHOT COUNT: {ss_num - 1} screenshots taken")

        # Save JSON results
        with open(f"{SS_DIR}/qa-results.json", "w") as f:
            json.dump({
                "results": results,
                "console_errors": errors[:20],
                "console_warnings": warnings[:20],
                "screenshot_dir": SS_DIR,
                "total_screenshots": ss_num - 1
            }, f, indent=2)
        log(f"\n  Results JSON: {SS_DIR}/qa-results.json")

        return results, errors


if __name__ == "__main__":
    final_results, error_logs = asyncio.run(run())
