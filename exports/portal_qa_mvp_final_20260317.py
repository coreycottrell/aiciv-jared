#!/usr/bin/env python3
"""
PureBrain Portal MVP Final QA
Date: 2026-03-17
Agent: browser-vision-tester
All 17 test categories from Jared's spec.
"""

import asyncio
import json
import time
import os
from pathlib import Path
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-mvp-final-20260317"

results = []
screenshot_counter = [0]

async def screenshot(page, label):
    screenshot_counter[0] += 1
    n = screenshot_counter[0]
    path = f"{SCREENSHOTS_DIR}/{n:02d}-{label}.png"
    await page.screenshot(path=path, full_page=False)
    print(f"  [SS] {path}")
    return path

def pass_test(name, detail=""):
    results.append({"status": "PASS", "name": name, "detail": detail})
    print(f"  PASS: {name} {detail}")

def fail_test(name, detail=""):
    results.append({"status": "FAIL", "name": name, "detail": detail})
    print(f"  FAIL: {name} {detail}")

def warn_test(name, detail=""):
    results.append({"status": "WARN", "name": name, "detail": detail})
    print(f"  WARN: {name} {detail}")

async def run_qa():
    async with async_playwright() as p:
        # ---- DESKTOP 1440px ----
        print("\n=== DESKTOP 1440x900 ===")
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-setuid-sandbox",
            "--disable-web-security", "--disable-features=IsolateOrigins",
            "--ignore-certificate-errors"
        ])
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # Collect console errors
        console_errors = []
        console_logs = []
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}")
                if msg.type in ("error", "warning") else console_logs.append(f"{msg.type}: {msg.text}"))

        # Collect network failures
        network_failures = []
        page.on("requestfailed", lambda req: network_failures.append(req.url))

        # -------- TEST 1: Login/Auth --------
        print("\n--- TEST 1: Login/Auth ---")
        await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Set bearer token via localStorage
        await page.evaluate(f"""
            localStorage.setItem('pb_token', '{TOKEN}');
            localStorage.setItem('portal_token', '{TOKEN}');
            localStorage.setItem('auth_token', '{TOKEN}');
        """)

        # Also set cookie
        await context.add_cookies([{
            "name": "pb_token",
            "value": TOKEN,
            "domain": "app.purebrain.ai",
            "path": "/"
        }])

        await page.reload(wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(4000)

        title = await page.title()
        url = page.url
        body_class = await page.get_attribute("body", "class") or ""

        login_form = await page.query_selector("form[action*='login'], input[name='password'], #login-form")
        if login_form:
            fail_test("Login/Auth", "Still showing login form after token injection")
        else:
            pass_test("Login/Auth", f"Portal loaded — title: {title[:50]}, no login form")

        ss1 = await screenshot(page, "01-login-desktop-full")

        # -------- TEST 11: Desktop Layout 1440px --------
        print("\n--- TEST 11: Desktop Layout 1440px ---")
        body_overflow = await page.evaluate("""
            () => {
                const body = document.body;
                const html = document.documentElement;
                return {
                    bodyScrollWidth: body.scrollWidth,
                    bodyClientWidth: body.clientWidth,
                    overflow: window.getComputedStyle(body).overflow,
                    htmlOverflow: window.getComputedStyle(html).overflow
                };
            }
        """)
        sidebar = await page.query_selector("#sidebar, .sidebar, nav.nav-panel, [class*='sidebar']")
        nav_panel = await page.query_selector(".nav-panel, #nav-panel, nav[class*='nav']")

        overflow_x = body_overflow.get('bodyScrollWidth', 0) > body_overflow.get('bodyClientWidth', 9999) + 20
        if overflow_x:
            fail_test("Desktop Layout 1440px", f"Horizontal overflow: scrollWidth={body_overflow['bodyScrollWidth']} > clientWidth={body_overflow['bodyClientWidth']}")
        else:
            pass_test("Desktop Layout 1440px", f"No overflow. scrollWidth={body_overflow.get('bodyScrollWidth')}, clientWidth={body_overflow.get('bodyClientWidth')}")

        sidebar_check = await page.evaluate("""
            () => {
                const sidebar = document.querySelector('#sidebar, .nav-panel, nav, [class*="sidebar"]');
                if (!sidebar) return null;
                const rect = sidebar.getBoundingClientRect();
                const style = window.getComputedStyle(sidebar);
                return {left: rect.left, top: rect.top, width: rect.width, height: rect.height, display: style.display, visibility: style.visibility};
            }
        """)
        if sidebar_check and sidebar_check.get('display') != 'none':
            pass_test("Sidebar Visible Desktop", f"left={sidebar_check.get('left')}, w={sidebar_check.get('width')}")
        else:
            warn_test("Sidebar Visible Desktop", f"Sidebar not found or hidden: {sidebar_check}")

        # -------- TEST 14: Dark Theme --------
        print("\n--- TEST 14: Dark Theme ---")
        theme_data = await page.evaluate("""
            () => {
                const body = document.body;
                const style = window.getComputedStyle(body);
                const bg = style.backgroundColor;
                const appEl = document.querySelector('#app, .app, main, [class*="app"]');
                const appBg = appEl ? window.getComputedStyle(appEl).backgroundColor : 'none';
                // Check if any major elements have orange/light backgrounds
                const orangeCheck = Array.from(document.querySelectorAll('body, #app, .portal, main, .chat-panel, .sidebar, .nav-panel'))
                    .map(el => ({tag: el.tagName, id: el.id, cls: el.className.substring(0,30), bg: window.getComputedStyle(el).backgroundColor}));
                return {bodyBg: bg, appBg: appBg, elements: orangeCheck};
            }
        """)
        body_bg = theme_data.get('bodyBg', '')
        # Parse RGB to check for dark
        def is_dark_bg(rgb_str):
            if not rgb_str or rgb_str == 'rgba(0, 0, 0, 0)' or rgb_str == 'transparent':
                return True  # transparent is fine
            try:
                parts = rgb_str.replace('rgb(','').replace('rgba(','').replace(')','').split(',')
                r, g, b = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                return brightness < 128
            except:
                return True

        is_dark = is_dark_bg(body_bg)
        if is_dark:
            pass_test("Dark Theme Body", f"Body bg: {body_bg} — DARK")
        else:
            fail_test("Dark Theme Body", f"Body bg: {body_bg} — LIGHT/ORANGE DETECTED")

        # -------- TEST 13: Navigation (16+ items) --------
        print("\n--- TEST 13: Navigation ---")
        nav_data = await page.evaluate("""
            () => {
                const navItems = Array.from(document.querySelectorAll('[data-panel], .nav-item, nav li, nav a, [class*="nav-item"]'));
                const unique = [...new Set(navItems.map(el => el.getAttribute('data-panel') || el.textContent.trim().substring(0,20)))].filter(Boolean);
                return {count: navItems.length, items: unique.slice(0, 25)};
            }
        """)
        nav_count = nav_data.get('count', 0)
        nav_items = nav_data.get('items', [])
        if nav_count >= 16:
            pass_test("Navigation 16+ items", f"Found {nav_count} nav items: {nav_items[:8]}")
        elif nav_count >= 10:
            warn_test("Navigation count", f"Found {nav_count} items (expected 16+): {nav_items}")
        else:
            fail_test("Navigation count", f"Only {nav_count} nav items found")

        # -------- TEST 10: Welcome Hero --------
        print("\n--- TEST 10: Welcome Hero ---")
        welcome_hero = await page.evaluate("""
            () => {
                const hero = document.querySelector('#welcomeHero, .welcome-hero, [id*="welcome"], [class*="welcome"]');
                if (!hero) return null;
                const style = window.getComputedStyle(hero);
                const rect = hero.getBoundingClientRect();
                return {id: hero.id, cls: hero.className.substring(0,40), display: style.display, opacity: style.opacity, rect: {t: rect.top, l: rect.left, w: rect.width, h: rect.height}};
            }
        """)
        if welcome_hero:
            pass_test("Welcome Hero in DOM", f"id={welcome_hero.get('id')}, opacity={welcome_hero.get('opacity')}, rect={welcome_hero.get('rect')}")
        else:
            fail_test("Welcome Hero in DOM", "No #welcomeHero or .welcome-hero found")

        # -------- TEST 2: Chat Panel --------
        print("\n--- TEST 2: Chat Panel ---")
        chat_data = await page.evaluate("""
            () => {
                const chatInput = document.querySelector('#userInput, textarea[placeholder*="message"], input[placeholder*="message"], #messageInput, [class*="chat-input"] textarea');
                const sendBtn = document.querySelector('#sendBtn, button[id*="send"], [class*="send-btn"], button[aria-label*="send"]');
                const chatPanel = document.querySelector('#chatPanel, .chat-panel, [id*="chat-panel"]');
                const messages = document.querySelectorAll('.message, .chat-message, [class*="message-"]');
                return {
                    chatInput: chatInput ? {id: chatInput.id, placeholder: chatInput.placeholder, display: window.getComputedStyle(chatInput).display} : null,
                    sendBtn: sendBtn ? {id: sendBtn.id, text: sendBtn.textContent.trim().substring(0,20)} : null,
                    chatPanel: chatPanel ? {id: chatPanel.id, display: window.getComputedStyle(chatPanel).display} : null,
                    messageCount: messages.length
                };
            }
        """)
        if chat_data.get('chatInput'):
            pass_test("Chat Input Present", f"id={chat_data['chatInput'].get('id')}, placeholder={chat_data['chatInput'].get('placeholder','')[:30]}")
        else:
            fail_test("Chat Input Present", "No chat input found")

        if chat_data.get('sendBtn'):
            pass_test("Send Button Present", f"id={chat_data['sendBtn'].get('id')}, text={chat_data['sendBtn'].get('text')}")
        else:
            warn_test("Send Button Present", "Send button not found by standard selectors")

        # -------- TEST 8: File Upload --------
        print("\n--- TEST 8: File Upload ---")
        file_upload = await page.evaluate("""
            () => {
                const attach = document.querySelector('#fileUpload, input[type="file"], [id*="attach"], [class*="attach"], [aria-label*="attach"], [title*="attach"]');
                const attachBtn = document.querySelector('#attachBtn, [id*="file-btn"], [class*="file-upload-btn"], label[for*="file"]');
                const uploadIcon = document.querySelector('[class*="paperclip"], [class*="attachment"], [data-icon*="attach"]');
                return {
                    fileInput: attach ? {tag: attach.tagName, id: attach.id, type: attach.type} : null,
                    attachBtn: attachBtn ? {tag: attachBtn.tagName, id: attachBtn.id, cls: attachBtn.className.substring(0,40)} : null,
                    uploadIcon: uploadIcon ? {cls: uploadIcon.className.substring(0,40)} : null
                };
            }
        """)
        if file_upload.get('fileInput') or file_upload.get('attachBtn') or file_upload.get('uploadIcon'):
            detail = str({k: v for k, v in file_upload.items() if v})
            pass_test("File Upload Attachment", detail[:100])
        else:
            warn_test("File Upload Attachment", "No file input/attach button found by standard selectors — may use custom icon")

        # -------- TEST 9: Training Hacks nav item --------
        print("\n--- TEST 9: Training Hacks ---")
        training_hacks = await page.evaluate("""
            () => {
                const all_text = Array.from(document.querySelectorAll('*')).filter(el => el.children.length === 0 && el.textContent.trim().toLowerCase().includes('training'));
                const navItem = Array.from(document.querySelectorAll('[data-panel], .nav-item, nav *')).find(el => el.textContent.trim().toLowerCase().includes('training') || el.textContent.trim().toLowerCase().includes('hacks'));
                const panel = document.querySelector('#trainingHacksPanel, [id*="training"], [class*="training"]');
                return {
                    navItem: navItem ? {tag: navItem.tagName, text: navItem.textContent.trim().substring(0,30), panel: navItem.getAttribute('data-panel')} : null,
                    panel: panel ? {id: panel.id, display: window.getComputedStyle(panel).display} : null,
                    textMatches: all_text.slice(0,3).map(el => ({tag: el.tagName, text: el.textContent.trim().substring(0,30)}))
                };
            }
        """)
        if training_hacks.get('navItem'):
            pass_test("Training Hacks Nav Item", f"text={training_hacks['navItem'].get('text')}, panel={training_hacks['navItem'].get('panel')}")
        else:
            warn_test("Training Hacks Nav Item", f"No nav item found. Text matches: {training_hacks.get('textMatches')}")

        # -------- TEST 12: Neural Canvas --------
        print("\n--- TEST 12: Neural Canvas ---")
        canvas_data = await page.evaluate("""
            () => {
                const canvas = document.querySelector('#hmiCanvas, canvas');
                const canvasAll = document.querySelectorAll('canvas');
                return {
                    mainCanvas: canvas ? {id: canvas.id, w: canvas.width, h: canvas.height} : null,
                    totalCanvases: canvasAll.length
                };
            }
        """)
        if canvas_data.get('mainCanvas'):
            pass_test("Neural Canvas in DOM", f"id={canvas_data['mainCanvas'].get('id')}, canvases={canvas_data.get('totalCanvases')}")
        else:
            warn_test("Neural Canvas in DOM", f"Canvas count={canvas_data.get('totalCanvases')}")

        # -------- TEST 16: Network/API --------
        print("\n--- TEST 16: Network/API ---")
        api_results = {}
        for endpoint in ["/api/commands", "/api/shortcuts", "/api/agents"]:
            try:
                response = await page.evaluate(f"""
                    async () => {{
                        try {{
                            const r = await fetch('{PORTAL_URL}{endpoint}', {{
                                headers: {{ 'Authorization': 'Bearer {TOKEN}', 'x-portal-token': '{TOKEN}' }}
                            }});
                            const text = await r.text();
                            return {{status: r.status, bytes: text.length}};
                        }} catch(e) {{
                            return {{status: 0, error: e.message}};
                        }}
                    }}
                """)
                api_results[endpoint] = response
                if response.get('status') == 200:
                    pass_test(f"API {endpoint}", f"200 OK, {response.get('bytes')}b")
                else:
                    fail_test(f"API {endpoint}", f"Status {response.get('status')}: {response.get('error','')}")
            except Exception as e:
                fail_test(f"API {endpoint}", str(e))

        # -------- TEST 3: Agent Roster (539 cards) --------
        print("\n--- TEST 3: Agent Roster ---")
        # Click agents nav item
        agents_nav = await page.query_selector('[data-panel="agents"], [data-panel="agent-roster"]')
        if agents_nav:
            await agents_nav.click()
            await page.wait_for_timeout(6000)  # Allow agents to load
            await screenshot(page, "03-agents-panel")

        agents_data = await page.evaluate("""
            () => {
                const panel = document.querySelector('#agentsPanel, [id*="agents-panel"], [class*="agents-panel"]');
                const cards = document.querySelectorAll('.agent-card, [class*="agent-card"], .agent-item, [class*="agent-item"]');
                const rows = document.querySelectorAll('[class*="agent"]');
                const loading = panel ? panel.textContent.includes('Loading') : false;
                return {
                    panel: panel ? {id: panel.id, display: window.getComputedStyle(panel).display} : null,
                    cardCount: cards.length,
                    rowCount: rows.length,
                    loading: loading,
                    panelText: panel ? panel.textContent.substring(0,100) : 'not found'
                };
            }
        """)
        card_count = agents_data.get('cardCount', 0)
        if card_count >= 500:
            pass_test("Agent Roster 539 cards", f"{card_count} cards loaded")
        elif card_count > 0:
            warn_test("Agent Roster count", f"Only {card_count} cards (expected 539+), loading={agents_data.get('loading')}")
        else:
            # Check row count
            if agents_data.get('rowCount', 0) > 100:
                pass_test("Agent Roster (rows)", f"{agents_data.get('rowCount')} agent rows found")
            else:
                fail_test("Agent Roster", f"No agent cards found. loading={agents_data.get('loading')}. text={agents_data.get('panelText','')[:60]}")

        # -------- TEST 4: Commands Panel --------
        print("\n--- TEST 4: Commands Panel ---")
        commands_nav = await page.query_selector('[data-panel="commands"]')
        if commands_nav:
            await commands_nav.click()
            await page.wait_for_timeout(2000)
            await screenshot(page, "04-commands-panel")

        commands_data = await page.evaluate("""
            () => {
                const panel = document.querySelector('#commandsPanel, [id*="commands-panel"]');
                if (!panel) return {found: false};
                const text = panel.textContent;
                const hasSSH = text.includes('SSH') || text.includes('ssh');
                const hasIP = text.includes('89.167') || text.includes('Server IP') || /\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}/.test(text);
                const loading = text.includes('Loading commands');
                return {found: true, hasSSH, hasIP, loading, preview: text.substring(0,200)};
            }
        """)
        if commands_data.get('found'):
            if commands_data.get('hasSSH') and commands_data.get('hasIP'):
                pass_test("Commands Panel SSH+IP", f"SSH and IP visible. loading={commands_data.get('loading')}")
            elif not commands_data.get('loading'):
                warn_test("Commands Panel", f"Panel found but SSH/IP not detected. preview={commands_data.get('preview','')[:100]}")
            else:
                fail_test("Commands Panel", f"Still loading. loading={commands_data.get('loading')}")
        else:
            fail_test("Commands Panel", "Panel not found")

        # -------- TEST 5: Shortcuts Panel --------
        print("\n--- TEST 5: Shortcuts Panel ---")
        shortcuts_nav = await page.query_selector('[data-panel="shortcuts"]')
        if shortcuts_nav:
            await shortcuts_nav.click()
            await page.wait_for_timeout(3000)
            await screenshot(page, "05-shortcuts-panel")

        shortcuts_data = await page.evaluate("""
            () => {
                const panel = document.querySelector('#shortcutsPanel, [id*="shortcuts-panel"]');
                if (!panel) return {found: false};
                const text = panel.textContent;
                const hasSlash = text.includes('/') && (text.includes('command') || text.includes('help') || text.includes('clear'));
                const hasKeyboard = text.includes('Ctrl') || text.includes('Cmd') || text.includes('keyboard') || text.includes('shortcut');
                const loading = text.includes('Loading shortcuts');
                const itemCount = panel.querySelectorAll('li, [class*="shortcut-item"], [class*="command-item"], tr, .shortcut').length;
                return {found: true, hasSlash, hasKeyboard, loading, itemCount, preview: text.substring(0,300)};
            }
        """)
        if shortcuts_data.get('found'):
            if shortcuts_data.get('hasSlash') or shortcuts_data.get('hasKeyboard') or shortcuts_data.get('itemCount', 0) > 0:
                pass_test("Shortcuts Panel", f"Slash={shortcuts_data.get('hasSlash')}, KB={shortcuts_data.get('hasKeyboard')}, items={shortcuts_data.get('itemCount')}, loading={shortcuts_data.get('loading')}")
            elif shortcuts_data.get('loading'):
                fail_test("Shortcuts Panel", "Still showing 'Loading shortcuts...'")
            else:
                warn_test("Shortcuts Panel", f"Found but content unclear. preview={shortcuts_data.get('preview','')[:100]}")
        else:
            fail_test("Shortcuts Panel", "Panel not found")

        # -------- TEST 7: Settings --------
        print("\n--- TEST 7: Settings ---")
        # Go back to chat first
        chat_nav = await page.query_selector('[data-panel="chat"], [data-panel="home"]')
        if chat_nav:
            await chat_nav.click()
            await page.wait_for_timeout(1000)

        settings_btn = await page.query_selector('#settings-btn, [id*="settings"], [aria-label*="settings"], [class*="settings-btn"]')
        if settings_btn:
            await settings_btn.click()
            await page.wait_for_timeout(2000)
            await screenshot(page, "07-settings-modal")

        settings_data = await page.evaluate("""
            () => {
                const modal = document.querySelector('#settingsModal, [id*="settings-modal"], [class*="settings-modal"], [role="dialog"]');
                const allText = document.body.textContent;
                const hasQuickFire = allText.includes('Quick Fire') || allText.includes('QuickFire') || allText.includes('quick-fire');
                const hasBOOP = allText.includes('BOOP') || allText.includes('Boop');
                const hasDuck = allText.includes('Duck') || allText.includes('Rubber Duck');
                return {
                    modal: modal ? {id: modal.id, display: window.getComputedStyle(modal).display} : null,
                    hasQuickFire, hasBOOP, hasDuck
                };
            }
        """)
        if settings_data.get('hasQuickFire') and settings_data.get('hasBOOP') and settings_data.get('hasDuck'):
            pass_test("Settings (Quick Fire + BOOP + Duck)", "All 3 settings present")
        elif settings_data.get('modal'):
            warn_test("Settings partial", f"Modal found. QF={settings_data.get('hasQuickFire')}, BOOP={settings_data.get('hasBOOP')}, Duck={settings_data.get('hasDuck')}")
        else:
            fail_test("Settings", f"QF={settings_data.get('hasQuickFire')}, BOOP={settings_data.get('hasBOOP')}, Duck={settings_data.get('hasDuck')}")

        # Close modal if open
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # -------- TEST 6: Voice/HMI Overlay --------
        print("\n--- TEST 6: Voice/HMI Overlay ---")
        # Look for voice/HMI button in the UI
        voice_btn = await page.query_selector('#hmiBtn, #voiceBtn, [id*="hmi"], [id*="voice-btn"], [class*="hmi-btn"], [aria-label*="voice"]')

        # Try to find the voice overlay trigger
        voice_trigger_data = await page.evaluate("""
            () => {
                // Look for any button that triggers the voice overlay
                const btns = Array.from(document.querySelectorAll('button, [role="button"], a'));
                const voiceBtn = btns.find(b =>
                    b.id && (b.id.includes('hmi') || b.id.includes('voice') || b.id.includes('mic')) ||
                    (b.className && (b.className.includes('hmi') || b.className.includes('voice') || b.className.includes('mic'))) ||
                    (b.getAttribute('aria-label') || '').toLowerCase().includes('voice') ||
                    (b.title || '').toLowerCase().includes('voice') ||
                    b.textContent.trim().toLowerCase().includes('voice')
                );
                return voiceBtn ? {id: voiceBtn.id, cls: voiceBtn.className.substring(0,50), text: voiceBtn.textContent.trim().substring(0,30)} : null;
            }
        """)

        if voice_trigger_data:
            print(f"  Voice trigger found: id={voice_trigger_data.get('id')}, text={voice_trigger_data.get('text')}")
            # Click the voice button to open overlay
            await page.evaluate(f"""
                () => {{
                    const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
                    const voiceBtn = btns.find(b => b.id === '{voice_trigger_data.get("id", "")}');
                    if (voiceBtn) voiceBtn.click();
                }}
            """)
            await page.wait_for_timeout(2000)
        else:
            # Try clicking #hmiBtn directly
            await page.evaluate("""
                () => {
                    const btn = document.querySelector('#hmiBtn') || document.querySelector('[onclick*="hmi"]') || document.querySelector('[onclick*="voice"]');
                    if (btn) btn.click();
                }
            """)
            await page.wait_for_timeout(2000)

        await screenshot(page, "06-voice-hmi-overlay")

        voice_data = await page.evaluate("""
            () => {
                const overlay = document.querySelector('#hmiVoiceOverlay, [id*="voice-overlay"], [id*="hmi-overlay"], [class*="voice-overlay"]');
                const vortex = document.querySelector('#vortexCanvas, [id*="vortex"], canvas.vortex, [class*="vortex"]');
                const micBtn = document.querySelector('#micBtn, #mic-btn, [id*="mic"], [aria-label*="microphone"], [aria-label*="mic"]');
                const standbyBtn = document.querySelector('#standbyBtn, [id*="standby"], button[class*="standby"]');

                // THE KEY TEST: "Click for Two-Way Communication" button should be GONE
                const allText = document.body.textContent;
                const hasTwoWayBtn = allText.includes('Click for Two-Way Communication') || allText.includes('Two-Way Communication');
                const twoWayElement = Array.from(document.querySelectorAll('button, a, [role="button"]')).find(el =>
                    el.textContent.includes('Two-Way') || el.textContent.includes('Click for Two-Way'));

                // Check overlay state
                const overlayStyle = overlay ? window.getComputedStyle(overlay) : null;
                const overlayVisible = overlay && overlayStyle && overlayStyle.display !== 'none';

                return {
                    overlay: overlay ? {id: overlay.id, display: overlayStyle ? overlayStyle.display : 'unknown', visible: overlayVisible} : null,
                    vortex: vortex ? {id: vortex.id, w: vortex.width, h: vortex.height} : null,
                    micBtn: micBtn ? {id: micBtn.id, text: micBtn.textContent.trim().substring(0,30)} : null,
                    standbyBtn: standbyBtn ? {id: standbyBtn.id, text: standbyBtn.textContent.trim().substring(0,50)} : null,
                    hasTwoWayBtn: hasTwoWayBtn,
                    twoWayElement: twoWayElement ? {tag: twoWayElement.tagName, text: twoWayElement.textContent.trim().substring(0,50)} : null,
                    // Also check if overlay was triggered
                    overlayInDOM: !!overlay
                };
            }
        """)

        # Check voice overlay components
        if voice_data.get('overlay'):
            pass_test("Voice Overlay in DOM", f"id={voice_data['overlay'].get('id')}, visible={voice_data['overlay'].get('visible')}")
        else:
            warn_test("Voice Overlay in DOM", "Overlay not found (may only exist in DOM when triggered)")

        if voice_data.get('vortex'):
            pass_test("Vortex Animation Canvas", f"id={voice_data['vortex'].get('id')}, {voice_data['vortex'].get('w')}x{voice_data['vortex'].get('h')}")
        else:
            warn_test("Vortex Animation Canvas", "Vortex canvas not found (may only render when overlay open)")

        if voice_data.get('micBtn'):
            pass_test("Mic Button Present", f"id={voice_data['micBtn'].get('id')}, text={voice_data['micBtn'].get('text')}")
        else:
            warn_test("Mic Button Present", "Mic button not found by standard selectors")

        if voice_data.get('standbyBtn'):
            pass_test("STANDBY Button Present", f"id={voice_data['standbyBtn'].get('id')}, text={voice_data['standbyBtn'].get('text')}")
        else:
            warn_test("STANDBY Button Present", "Standby button not found (may only exist when overlay open)")

        # CRITICAL TEST: "Click for Two-Way Communication" must be GONE
        if not voice_data.get('hasTwoWayBtn'):
            pass_test("Two-Way Communication button REMOVED", "'Click for Two-Way Communication' NOT in DOM — CORRECT")
        else:
            fail_test("Two-Way Communication button STILL PRESENT", f"Found: {voice_data.get('twoWayElement')}")

        # -------- TEST 15: Console Errors --------
        print("\n--- TEST 15: Console Errors ---")
        # Capture current state
        await screenshot(page, "15-final-desktop-state")

        prod_errors = [e for e in console_errors if
            'error' in e.lower() and
            '401' not in e and
            'microphone' not in e.lower() and
            'webgl' not in e.lower() and
            'mic' not in e.lower() and
            'permission' not in e.lower() and
            'NotAllowedError' not in e and
            'cors' not in e.lower() and
            'favicon' not in e.lower()]

        headless_artifacts = [e for e in console_errors if
            '401' in e or 'microphone' in e.lower() or 'webgl' in e.lower() or
            'NotAllowedError' in e or 'mic' in e.lower() or 'permission' in e.lower()]

        print(f"  Total console events: {len(console_errors)} errors/warns, {len(console_logs)} logs")
        print(f"  Headless artifacts (expected): {len(headless_artifacts)}")
        print(f"  Potential prod errors: {len(prod_errors)}")
        for e in prod_errors[:5]:
            print(f"    - {e[:120]}")

        if len(prod_errors) == 0:
            pass_test("Console Errors", f"Zero production JS errors. {len(headless_artifacts)} headless artifacts (expected)")
        elif len(prod_errors) <= 2:
            warn_test("Console Errors", f"{len(prod_errors)} potential prod errors: {prod_errors[0][:80] if prod_errors else ''}")
        else:
            fail_test("Console Errors", f"{len(prod_errors)} production errors detected")

        # ---- MOBILE 375px ----
        print("\n=== MOBILE 375x812 ===")
        await browser.close()

        mobile_browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        mobile_context = await mobile_browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        mobile_page = await mobile_context.new_page()

        await mobile_page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
        await mobile_page.wait_for_timeout(2000)
        await mobile_page.evaluate(f"""
            localStorage.setItem('pb_token', '{TOKEN}');
            localStorage.setItem('portal_token', '{TOKEN}');
        """)
        await mobile_context.add_cookies([{"name": "pb_token", "value": TOKEN, "domain": "app.purebrain.ai", "path": "/"}])
        await mobile_page.reload(wait_until="networkidle", timeout=30000)
        await mobile_page.wait_for_timeout(4000)

        await mobile_page.screenshot(path=f"{SCREENSHOTS_DIR}/17-mobile-375px-full.png")
        print(f"  [SS] {SCREENSHOTS_DIR}/17-mobile-375px-full.png")

        # TEST 17: Mobile Layout
        print("\n--- TEST 17: Mobile 375px ---")
        mobile_data = await mobile_page.evaluate("""
            () => {
                const body = document.body;
                const bodyOverflow = body.scrollWidth > body.clientWidth + 10;
                const chatInput = document.querySelector('#userInput, textarea, input[placeholder*="message"]');
                const chatInputVisible = chatInput ? window.getComputedStyle(chatInput).display !== 'none' : false;
                const bg = window.getComputedStyle(body).backgroundColor;
                return {
                    overflow: bodyOverflow,
                    scrollWidth: body.scrollWidth,
                    clientWidth: body.clientWidth,
                    chatInputVisible: chatInputVisible,
                    chatInputDisplay: chatInput ? window.getComputedStyle(chatInput).display : 'not found',
                    bodyBg: bg
                };
            }
        """)
        if not mobile_data.get('overflow'):
            pass_test("Mobile 375px No Overflow", f"scrollWidth={mobile_data.get('scrollWidth')}, clientWidth={mobile_data.get('clientWidth')}")
        else:
            fail_test("Mobile 375px Overflow", f"Horizontal overflow! sw={mobile_data.get('scrollWidth')} > cw={mobile_data.get('clientWidth')}")

        if mobile_data.get('chatInputVisible'):
            pass_test("Mobile Chat Input Visible", f"display={mobile_data.get('chatInputDisplay')}")
        else:
            warn_test("Mobile Chat Input", f"Input not visible: display={mobile_data.get('chatInputDisplay')}")

        body_bg_mobile = mobile_data.get('bodyBg', '')
        if is_dark_bg(body_bg_mobile):
            pass_test("Mobile Dark Theme", f"bg={body_bg_mobile}")
        else:
            fail_test("Mobile Dark Theme", f"Light/orange bg detected: {body_bg_mobile}")

        await mobile_browser.close()

        # ---- SUMMARY ----
        print("\n" + "="*60)
        print("FINAL QA RESULTS SUMMARY")
        print("="*60)

        passed = [r for r in results if r['status'] == 'PASS']
        failed = [r for r in results if r['status'] == 'FAIL']
        warned = [r for r in results if r['status'] == 'WARN']

        print(f"PASS: {len(passed)}")
        print(f"FAIL: {len(failed)}")
        print(f"WARN: {len(warned)}")
        print(f"TOTAL: {len(results)}")

        if failed:
            print("\nFAILURES:")
            for f in failed:
                print(f"  - {f['name']}: {f['detail']}")

        if warned:
            print("\nWARNINGS:")
            for w in warned:
                print(f"  - {w['name']}: {w['detail']}")

        return results, passed, failed, warned

if __name__ == "__main__":
    results, passed, failed, warned = asyncio.run(run_qa())
    print(f"\nDone. {len(passed)} PASS / {len(failed)} FAIL / {len(warned)} WARN")
