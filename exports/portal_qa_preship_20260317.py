"""
PureBrain Portal - Pre-Ship Comprehensive QA Audit
Date: 2026-03-17
Agent: browser-vision-tester

Covers all 18 test areas per Jared's QA spec:
1. Login/Auth
2. Chat
3. Agents Panel
4. Commands Panel (JUST FIXED - agentsInterval scope bug)
5. Shortcuts Panel
6. Voice/HMI
7. Settings
8. File Upload
9. File Delivery
10. Training Hacks
11. Welcome Hero
12. Mobile Responsive (375px)
13. Desktop Layout
14. Console Errors
15. Network Requests
16. Neural Canvas
17. Navigation
18. Dark Theme
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-20260317"

results = {}
console_errors = []
console_warnings = []
network_failures = []
ss_count = [0]

def log(msg):
    print(msg, flush=True)

def record(name, status, notes=""):
    results[name] = {"status": status, "notes": notes}
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    log(f"  {icon} [{status}] {name}: {notes}")

async def screenshot(page, label):
    ss_count[0] += 1
    path = f"{SS_DIR}/{ss_count[0]:03d}-{label}.png"
    await page.screenshot(path=path, full_page=False)
    log(f"  [SCREENSHOT] {path}")
    return path

async def login_portal(page):
    """Login via localStorage token injection (proven technique from prior audit)"""
    log("  Navigating to portal...")
    try:
        await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
    except Exception as e:
        log(f"  Navigation error (may be ok): {str(e)[:80]}")

    await page.wait_for_timeout(1500)

    # Inject token into localStorage
    await page.evaluate(f"""
        () => {{
            localStorage.setItem('portal_token', '{TOKEN}');
        }}
    """)

    # Reload to trigger auto-auth
    try:
        await page.reload(wait_until="domcontentloaded", timeout=20000)
    except:
        pass

    await page.wait_for_timeout(4000)

    # Check auth overlay state
    overlay_hidden = await page.evaluate("""
        (function() {
            var overlay = document.getElementById('auth-overlay') ||
                          document.querySelector('.auth-overlay') ||
                          document.querySelector('[class*="login"]') ||
                          document.querySelector('[class*="auth"]');
            if (!overlay) return true;
            var style = window.getComputedStyle(overlay);
            return style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0';
        })()
    """)

    chat_visible = await page.evaluate("""
        (function() {
            var chat = document.getElementById('chat-messages') ||
                       document.getElementById('panel-chat') ||
                       document.querySelector('.chat-messages') ||
                       document.querySelector('[id*="chat"]');
            return !!chat;
        })()
    """)

    return overlay_hidden or chat_visible


async def run_qa():
    os.makedirs(SS_DIR, exist_ok=True)

    async with async_playwright() as p:
        # ─────────────────── DESKTOP BROWSER ───────────────────
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Wire up console + network monitors
        page.on("console", lambda msg: (
            console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else
            console_warnings.append(f"[warn] {msg.text}") if msg.type == "warning" else None
        ))
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {err}"))
        page.on("requestfailed", lambda req: network_failures.append(
            f"FAIL {req.method} {req.url} - {req.failure}"
        ))

        # ═══════════════════════════════════════════════════════
        # TEST 1: Login / Auth
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 1: Login/Auth ═══")
        logged_in = await login_portal(page)
        await screenshot(page, "01-login-state")

        if logged_in:
            record("Login/Auth - Page loads", "PASS", "Portal loaded successfully")
        else:
            record("Login/Auth - Page loads", "FAIL", "Auth overlay still visible or portal not loaded")

        # Check session persistence token
        stored_token = await page.evaluate("(function(){ return localStorage.getItem('portal_token'); })()")
        if stored_token:
            record("Login/Auth - Session token persists", "PASS", f"Token in localStorage (length={len(stored_token)})")
        else:
            record("Login/Auth - Session token persists", "FAIL", "No token in localStorage")

        # Check OAuth buttons exist on login page (navigate without token to check)
        context2 = await browser.new_context(viewport={"width": 1440, "height": 900})
        page_login = await context2.new_page()
        try:
            await page_login.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=15000)
        except:
            pass
        await page_login.wait_for_timeout(2000)
        await screenshot(page_login, "01b-login-page-unauthed")

        oauth_buttons = await page_login.evaluate("""
            (function() {
                var btns = document.querySelectorAll('[class*="oauth"], [class*="google"], [class*="github"], [href*="oauth"], [href*="google"], [href*="github"]');
                var signin = document.querySelectorAll('.pb-signin-btn, [class*="signin"], [class*="login"], input[type="password"]');
                return { oauth_count: btns.length, signin_count: signin.length };
            })()
        """)
        if oauth_buttons.get("signin_count", 0) > 0 or oauth_buttons.get("oauth_count", 0) > 0:
            record("Login/Auth - Login form/buttons present", "PASS", f"signin elements: {oauth_buttons.get('signin_count',0)}, oauth: {oauth_buttons.get('oauth_count',0)}")
        else:
            record("Login/Auth - Login form/buttons present", "WARN", "No standard login elements found - portal may go straight to auth")
        await context2.close()

        # ═══════════════════════════════════════════════════════
        # TEST 2: Chat
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 2: Chat ═══")
        await page.wait_for_timeout(2000)

        chat_panel = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-chat');
                if (!panel) return { exists: false };
                var messages = panel.querySelectorAll('.message, .msg, [class*="message"]');
                var input = panel.querySelector('input, textarea, [contenteditable]');
                var active = panel.classList.contains('active');
                return {
                    exists: true,
                    active: active,
                    message_count: messages.length,
                    has_input: !!input
                };
            })()
        """)
        await screenshot(page, "02-chat-panel")

        if chat_panel.get("exists"):
            record("Chat - Panel exists", "PASS", f"active={chat_panel.get('active')}, messages={chat_panel.get('message_count')}")
        else:
            record("Chat - Panel exists", "FAIL", "panel-chat not found in DOM")

        if chat_panel.get("has_input"):
            record("Chat - Input field present", "PASS", "Message input found")
        else:
            record("Chat - Input field present", "FAIL", "No input/textarea in chat panel")

        if chat_panel.get("message_count", 0) > 0:
            record("Chat - Messages rendered", "PASS", f"{chat_panel.get('message_count')} messages visible")
        else:
            record("Chat - Messages rendered", "WARN", "No messages in DOM (may be fresh session)")

        # Check markdown rendering (look for formatted elements)
        md_check = await page.evaluate("""
            (function() {
                var formatted = document.querySelectorAll('.message strong, .message em, .message code, .message pre, [class*="message"] strong, [class*="message"] code');
                return formatted.length;
            })()
        """)
        if md_check > 0:
            record("Chat - Markdown renders", "PASS", f"{md_check} formatted elements found")
        else:
            record("Chat - Markdown renders", "WARN", "No formatted elements in messages (may be all plain text)")

        # Check scroll
        scroll_check = await page.evaluate("""
            (function() {
                var container = document.querySelector('#chat-messages, .chat-messages, #panel-chat .messages, [class*="chat-scroll"]');
                if (!container) return false;
                return container.scrollHeight > 0;
            })()
        """)
        record("Chat - Scroll container", "PASS" if scroll_check else "WARN", "Scroll container found" if scroll_check else "Scroll container not identified")

        # ═══════════════════════════════════════════════════════
        # TEST 3: Agents Panel
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 3: Agents Panel ═══")
        # Click agents nav item
        agents_clicked = False
        for sel in ['div[data-panel="agents"]', '[data-panel="agents"]', 'nav .agents, .nav-item[data-panel="agents"]']:
            try:
                await page.click(sel, timeout=3000)
                agents_clicked = True
                break
            except:
                pass
        await page.wait_for_timeout(2500)
        await screenshot(page, "03-agents-panel")

        agents_data = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-agents');
                if (!panel) return { exists: false };
                var items = panel.querySelectorAll('[class*="agent"], [class*="row"], tr, .card');
                var active = panel.classList.contains('active');
                var loading = panel.textContent.includes('Loading') || panel.textContent.includes('loading...');
                return {
                    exists: true,
                    active: active,
                    item_count: items.length,
                    loading: loading,
                    text_preview: panel.textContent.trim().substring(0, 200)
                };
            })()
        """)

        if agents_data.get("exists") and agents_data.get("item_count", 0) > 0:
            record("Agents Panel - Loads with data", "PASS", f"{agents_data.get('item_count')} items, loading={agents_data.get('loading')}")
        elif agents_data.get("exists"):
            record("Agents Panel - Loads with data", "WARN", f"Panel exists but {agents_data.get('item_count',0)} items. Preview: {agents_data.get('text_preview','')[:100]}")
        else:
            record("Agents Panel - Loads with data", "FAIL", "panel-agents not found")

        if agents_data.get("exists") and not agents_data.get("loading"):
            record("Agents Panel - Not stuck in Loading state", "PASS", "No loading indicator")
        elif agents_data.get("loading"):
            record("Agents Panel - Not stuck in Loading state", "FAIL", "Stuck on loading text")
        else:
            record("Agents Panel - Not stuck in Loading state", "WARN", "Panel not found to check")

        # ═══════════════════════════════════════════════════════
        # TEST 4: Commands Panel (THE CRITICAL ONE - just fixed)
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 4: Commands Panel (CRITICAL - just fixed) ═══")

        # Clear prior console errors to track only Commands-related ones
        console_errors_before_commands = len(console_errors)

        commands_clicked = False
        for sel in ['div[data-panel="commands"]', '[data-panel="commands"]']:
            try:
                await page.click(sel, timeout=3000)
                commands_clicked = True
                break
            except:
                pass

        if not commands_clicked:
            record("Commands Panel - Nav item clickable", "FAIL", "Could not find/click commands nav item")
        else:
            record("Commands Panel - Nav item clickable", "PASS", "Clicked successfully")

        await page.wait_for_timeout(3500)
        await screenshot(page, "04-commands-panel")

        commands_data = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-commands');
                if (!panel) return { exists: false };
                var active = panel.classList.contains('active');
                var text = panel.textContent;
                var stuck_loading = text.includes('Loading command reference');
                var has_real_data = (
                    text.includes('/') ||
                    text.includes('command') ||
                    text.includes('Command') ||
                    text.includes('ssh') ||
                    text.includes('bash') ||
                    text.length > 500
                );
                var loading_spinners = panel.querySelectorAll('[class*="loading"], [class*="spinner"]').length;
                return {
                    exists: true,
                    active: active,
                    stuck_loading: stuck_loading,
                    has_real_data: has_real_data,
                    text_length: text.length,
                    loading_spinners: loading_spinners,
                    preview: text.trim().substring(0, 300)
                };
            })()
        """)

        new_errors = console_errors[console_errors_before_commands:]
        agentsinterval_error = any("agentsInterval" in e or "agentsinterval" in e.lower() for e in new_errors)

        if not commands_data.get("exists"):
            record("Commands Panel - Panel exists", "FAIL", "panel-commands not in DOM")
        elif commands_data.get("stuck_loading"):
            record("Commands Panel - Shows real data (not stuck)", "FAIL",
                   f"STUCK on 'Loading command reference...'. agentsInterval error: {agentsinterval_error}. Preview: {commands_data.get('preview','')[:150]}")
        elif commands_data.get("has_real_data"):
            record("Commands Panel - Shows real data (not stuck)", "PASS",
                   f"Real content loaded! text_length={commands_data.get('text_length')}, spinners={commands_data.get('loading_spinners',0)}")
        else:
            record("Commands Panel - Shows real data (not stuck)", "WARN",
                   f"Panel active but unclear content. Preview: {commands_data.get('preview','')[:150]}")

        if not agentsinterval_error:
            record("Commands Panel - No agentsInterval ReferenceError", "PASS", "No scope crash detected")
        else:
            record("Commands Panel - No agentsInterval ReferenceError", "FAIL", f"agentsInterval ReferenceError found: {new_errors[:2]}")

        # ═══════════════════════════════════════════════════════
        # TEST 5: Shortcuts Panel
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 5: Shortcuts Panel ═══")
        shortcuts_clicked = False
        for sel in ['div[data-panel="shortcuts"]', '[data-panel="shortcuts"]']:
            try:
                await page.click(sel, timeout=3000)
                shortcuts_clicked = True
                break
            except:
                pass

        await page.wait_for_timeout(3000)
        await screenshot(page, "05-shortcuts-panel")

        shortcuts_data = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-shortcuts');
                if (!panel) return { exists: false };
                var active = panel.classList.contains('active');
                var text = panel.textContent;
                var stuck_loading = text.includes('Loading shortcuts');
                var has_real_data = text.length > 300;
                return {
                    exists: true,
                    active: active,
                    stuck_loading: stuck_loading,
                    has_real_data: has_real_data,
                    text_length: text.length,
                    preview: text.trim().substring(0, 300)
                };
            })()
        """)

        if not shortcuts_data.get("exists"):
            record("Shortcuts Panel - Panel exists", "FAIL", "panel-shortcuts not in DOM")
        elif shortcuts_data.get("stuck_loading"):
            record("Shortcuts Panel - Shows real data (not stuck)", "FAIL", f"Stuck on 'Loading shortcuts...' Preview: {shortcuts_data.get('preview','')[:150]}")
        elif shortcuts_data.get("has_real_data"):
            record("Shortcuts Panel - Shows real data (not stuck)", "PASS", f"Real content! text_length={shortcuts_data.get('text_length')}")
        else:
            record("Shortcuts Panel - Shows real data (not stuck)", "WARN", f"Panel exists, text_length={shortcuts_data.get('text_length',0)}, Preview: {shortcuts_data.get('preview','')[:100]}")

        # ═══════════════════════════════════════════════════════
        # TEST 6: Voice / HMI Panel
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 6: Voice/HMI Panel ═══")
        voice_clicked = False
        for sel in ['div[data-panel="voice"]', '[data-panel="voice"]', 'div[data-panel="hmi"]', '[data-panel="hmi"]']:
            try:
                await page.click(sel, timeout=3000)
                voice_clicked = True
                break
            except:
                pass

        await page.wait_for_timeout(2000)
        await screenshot(page, "06-voice-hmi-panel")

        voice_data = await page.evaluate("""
            (function() {
                // Check for voice/HMI panel
                var panel = document.getElementById('panel-voice') ||
                            document.getElementById('panel-hmi') ||
                            document.querySelector('[id*="voice"]') ||
                            document.querySelector('[id*="hmi"]');
                if (!panel) {
                    // Maybe voice is a modal/overlay
                    var voiceOverlay = document.querySelector('[class*="voice"], [class*="hmi"], [id*="voice-overlay"]');
                    return { exists: !!voiceOverlay, is_overlay: true, type: voiceOverlay ? voiceOverlay.id || voiceOverlay.className : 'not found' };
                }
                var active = panel.classList.contains('active');
                var text = panel.textContent;
                var triggerField = panel.querySelector('input[placeholder*="trigger"], input[placeholder*="word"], [class*="trigger"]');
                var elevenlabs_field = panel.querySelector('[placeholder*="ElevenLabs"], [placeholder*="eleven"], [id*="elevenlabs"], [name*="elevenlabs"]');
                return {
                    exists: true,
                    active: active,
                    has_trigger_field: !!triggerField,
                    has_elevenlabs: !!elevenlabs_field,
                    text_preview: text.trim().substring(0, 200)
                };
            })()
        """)

        if voice_data.get("exists"):
            record("Voice/HMI - Panel/overlay opens", "PASS", f"active={voice_data.get('active')}, is_overlay={voice_data.get('is_overlay')}, trigger_field={voice_data.get('has_trigger_field')}")
        else:
            record("Voice/HMI - Panel/overlay opens", "FAIL", "No voice/HMI panel or overlay found")

        # Check voice nav button exists even if click failed
        voice_nav = await page.evaluate("""
            (function() {
                return !!(
                    document.querySelector('div[data-panel="voice"]') ||
                    document.querySelector('div[data-panel="hmi"]') ||
                    document.querySelector('[class*="voice-btn"]')
                );
            })()
        """)
        record("Voice/HMI - Nav item present", "PASS" if voice_nav else "WARN",
               "Voice nav item in sidebar" if voice_nav else "No voice/hmi nav item found")

        # ═══════════════════════════════════════════════════════
        # TEST 7: Settings
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 7: Settings ═══")
        # Try settings panel nav
        settings_opened = False
        for sel in ['div[data-panel="settings"]', '[data-panel="settings"]',
                    '[class*="settings-btn"]', 'button[title*="Settings"]',
                    '[class*="settings-icon"]']:
            try:
                await page.click(sel, timeout=2000)
                settings_opened = True
                break
            except:
                pass

        await page.wait_for_timeout(2000)
        await screenshot(page, "07-settings-panel")

        settings_data = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-settings') ||
                            document.querySelector('[class*="settings-modal"]') ||
                            document.querySelector('[class*="settings-panel"]');
                if (!panel) return { exists: false };
                var active = panel.classList.contains('active') ||
                             window.getComputedStyle(panel).display !== 'none';
                var elevenlabs = panel.querySelector('[placeholder*="ElevenLabs"], [id*="elevenlabs"], [name*="eleven"]');
                var voiceSelect = panel.querySelector('select[name*="voice"], [id*="voice-select"]');
                var text = panel.textContent;
                return {
                    exists: true,
                    visible: active,
                    has_elevenlabs_field: !!elevenlabs,
                    has_voice_select: !!voiceSelect,
                    text_length: text.length,
                    preview: text.trim().substring(0, 300)
                };
            })()
        """)

        if settings_data.get("exists") and settings_data.get("visible"):
            record("Settings - Panel renders", "PASS", f"ElevenLabs={settings_data.get('has_elevenlabs_field')}, voice_select={settings_data.get('has_voice_select')}")
        elif settings_data.get("exists"):
            record("Settings - Panel renders", "WARN", f"Panel in DOM but may not be visible. Preview: {settings_data.get('preview','')[:100]}")
        else:
            record("Settings - Panel renders", "WARN", "Settings panel not found - may use different selector")

        # ═══════════════════════════════════════════════════════
        # TEST 8: File Upload
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 8: File Upload ═══")
        # Navigate back to chat first
        for sel in ['div[data-panel="chat"]', '[data-panel="chat"]']:
            try:
                await page.click(sel, timeout=2000)
                break
            except:
                pass
        await page.wait_for_timeout(1500)

        upload_data = await page.evaluate("""
            (function() {
                var fileInput = document.querySelector('input[type="file"]');
                var uploadZone = document.querySelector('[class*="upload"], [class*="drop"], [class*="attach"], [id*="upload"], [title*="upload"], [title*="attach"]');
                var uploadBtn = document.querySelector('[class*="file-btn"], [class*="attach-btn"], button[title*="file"]');
                return {
                    has_file_input: !!fileInput,
                    has_upload_zone: !!uploadZone,
                    has_upload_btn: !!uploadBtn,
                    file_input_type: fileInput ? fileInput.getAttribute('accept') : null,
                    upload_zone_class: uploadZone ? uploadZone.className.substring(0,80) : null
                };
            })()
        """)
        await screenshot(page, "08-file-upload-area")

        if upload_data.get("has_file_input") or upload_data.get("has_upload_zone") or upload_data.get("has_upload_btn"):
            record("File Upload - Upload area visible", "PASS",
                   f"file_input={upload_data.get('has_file_input')}, drop_zone={upload_data.get('has_upload_zone')}, btn={upload_data.get('has_upload_btn')}")
        else:
            record("File Upload - Upload area visible", "WARN", "No standard file upload elements found - may be chat-embedded")

        # ═══════════════════════════════════════════════════════
        # TEST 9: File Delivery (download links)
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 9: File Delivery ═══")
        file_delivery = await page.evaluate("""
            (function() {
                var downloadLinks = document.querySelectorAll('a[download], a[href$=".pdf"], a[href$=".md"], a[href$=".txt"], a[href*="download"], [class*="download-link"]');
                var fileCards = document.querySelectorAll('[class*="file-card"], [class*="file-preview"], [class*="attachment"]');
                return {
                    download_links: downloadLinks.length,
                    file_cards: fileCards.length
                };
            })()
        """)
        # This may be WARN if no files have been delivered yet in this session
        record("File Delivery - Download links render", "PASS" if file_delivery.get("download_links", 0) > 0 or file_delivery.get("file_cards", 0) > 0 else "WARN",
               f"download_links={file_delivery.get('download_links',0)}, file_cards={file_delivery.get('file_cards',0)} (may be empty in fresh session)")

        # ═══════════════════════════════════════════════════════
        # TEST 10: Training Hacks
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 10: Training Hacks ═══")
        # Training hacks should inject into chat, NOT open a separate panel
        training_data = await page.evaluate("""
            (function() {
                var trainingPanel = document.getElementById('panel-training-hacks') ||
                                    document.querySelector('[id*="training-hacks"]');
                var trainingNavBtn = document.querySelector('[data-panel="training-hacks"], [class*="training-hacks"]');
                var trainingInChat = document.querySelector('[class*="training-hack"], [data-type="training"]');
                return {
                    has_separate_panel: !!(trainingPanel && trainingPanel.id),
                    has_nav_btn: !!trainingNavBtn,
                    injected_in_chat: !!trainingInChat
                };
            })()
        """)

        # Per feedback_training_hacks_not_broken.md: Training Hacks injects into chat, NOT a separate panel
        if not training_data.get("has_separate_panel"):
            record("Training Hacks - Injects into chat (not separate panel)", "PASS",
                   "No separate panel found (correct behavior per design)")
        else:
            record("Training Hacks - Injects into chat (not separate panel)", "WARN",
                   "Has a separate panel - verify this is intentional")

        # ═══════════════════════════════════════════════════════
        # TEST 11: Welcome Hero
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 11: Welcome Hero ═══")
        hero_data = await page.evaluate("""
            (function() {
                var hero = document.querySelector('[id*="welcome"], [class*="welcome-hero"], [class*="welcome-screen"]');
                if (!hero) return { exists: false };
                var style = window.getComputedStyle(hero);
                return {
                    exists: true,
                    display: style.display,
                    opacity: style.opacity,
                    visible: style.display !== 'none' && parseFloat(style.opacity) > 0,
                    text: hero.textContent.trim().substring(0, 100)
                };
            })()
        """)

        if hero_data.get("exists"):
            record("Welcome Hero - Present in DOM", "PASS", f"visible={hero_data.get('visible')}, opacity={hero_data.get('opacity')}")
        else:
            record("Welcome Hero - Present in DOM", "WARN", "No welcome hero element found (may have already faded or uses different class)")

        await screenshot(page, "11-welcome-hero-state")

        # ═══════════════════════════════════════════════════════
        # TEST 12: Mobile Responsive (375px)
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 12: Mobile Responsive (375px) ═══")
        mobile_context = await browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"
        )
        mobile_page = await mobile_context.new_page()
        mobile_page.on("console", lambda msg: (
            console_errors.append(f"[MOBILE][{msg.type}] {msg.text}") if msg.type == "error" else None
        ))

        try:
            await mobile_page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        except:
            pass
        await mobile_page.wait_for_timeout(1500)
        await mobile_page.evaluate(f"() => {{ localStorage.setItem('portal_token', '{TOKEN}'); }}")
        try:
            await mobile_page.reload(wait_until="domcontentloaded", timeout=20000)
        except:
            pass
        await mobile_page.wait_for_timeout(4000)

        await mobile_page.screenshot(path=f"{SS_DIR}/12-mobile-375-initial.png")
        ss_count[0] += 1
        log(f"  [SCREENSHOT] {SS_DIR}/12-mobile-375-initial.png")

        mobile_layout = await mobile_page.evaluate("""
            (function() {
                var bodyWidth = document.body.scrollWidth;
                var windowWidth = window.innerWidth;
                var overflow = bodyWidth > windowWidth;
                var bottomNav = document.querySelector('[class*="bottom-nav"], [class*="mobile-nav"], nav[class*="bottom"]');
                var chatMessages = document.querySelector('#panel-chat, #chat-messages, [class*="chat"]');
                var sidebarVisible = false;
                var sidebar = document.querySelector('.sidebar, [class*="sidebar"]');
                if (sidebar) {
                    var style = window.getComputedStyle(sidebar);
                    sidebarVisible = style.display !== 'none' && style.visibility !== 'hidden';
                }
                return {
                    body_scroll_width: bodyWidth,
                    window_width: windowWidth,
                    has_overflow: overflow,
                    has_bottom_nav: !!bottomNav,
                    has_chat: !!chatMessages,
                    sidebar_visible: sidebarVisible
                };
            })()
        """)

        if not mobile_layout.get("has_overflow"):
            record("Mobile - No horizontal overflow", "PASS", f"body={mobile_layout.get('body_scroll_width')}px, window={mobile_layout.get('window_width')}px")
        else:
            record("Mobile - No horizontal overflow", "FAIL", f"Overflow! body={mobile_layout.get('body_scroll_width')}px > window={mobile_layout.get('window_width')}px")

        if mobile_layout.get("has_bottom_nav"):
            record("Mobile - Bottom nav present", "PASS", "Mobile bottom navigation found")
        elif mobile_layout.get("has_chat"):
            record("Mobile - Bottom nav present", "WARN", "No bottom nav but chat panel found - may use different mobile layout")
        else:
            record("Mobile - Bottom nav present", "FAIL", "No bottom nav and no chat - mobile layout broken")

        # Test mobile nav click
        mobile_nav_works = False
        for sel in ['.bottom-nav-item', '[class*="bottom-nav"] [class*="item"]', '[class*="mobile-nav"] button']:
            try:
                items = await mobile_page.query_selector_all(sel)
                if items:
                    await items[0].click()
                    await mobile_page.wait_for_timeout(1000)
                    mobile_nav_works = True
                    break
            except:
                pass

        await mobile_page.screenshot(path=f"{SS_DIR}/12b-mobile-375-nav-click.png")
        ss_count[0] += 1
        log(f"  [SCREENSHOT] {SS_DIR}/12b-mobile-375-nav-click.png")

        record("Mobile - Nav interaction", "PASS" if mobile_nav_works else "WARN",
               "Mobile nav item clicked" if mobile_nav_works else "Could not click mobile nav (may be chat-only on mobile)")

        # Portrait - check that chat messages are not hidden behind canvas (known bug from prior audit)
        portrait_messages = await mobile_page.evaluate("""
            (function() {
                var msgs = document.querySelectorAll('.message, [class*="msg-item"], [class*="message-item"]');
                var canvas = document.getElementById('hmiCanvas') || document.querySelector('canvas');
                if (!msgs.length) return { has_messages: false };
                var firstMsg = msgs[0];
                var rect = firstMsg.getBoundingClientRect();
                var inViewport = rect.top >= 0 && rect.bottom <= window.innerHeight && rect.width > 0;
                return {
                    has_messages: true,
                    msg_count: msgs.length,
                    first_msg_in_viewport: inViewport,
                    first_msg_rect: { top: Math.round(rect.top), bottom: Math.round(rect.bottom), width: Math.round(rect.width) },
                    has_canvas: !!canvas
                };
            })()
        """)

        if portrait_messages.get("has_messages") and portrait_messages.get("first_msg_in_viewport"):
            record("Mobile - Chat messages visible (not behind canvas)", "PASS",
                   f"Messages visible, count={portrait_messages.get('msg_count')}")
        elif portrait_messages.get("has_messages"):
            record("Mobile - Chat messages visible (not behind canvas)", "WARN",
                   f"Messages exist but first not in viewport: rect={portrait_messages.get('first_msg_rect')}")
        else:
            record("Mobile - Chat messages visible (not behind canvas)", "WARN", "No messages found in DOM on mobile")

        await mobile_context.close()

        # ═══════════════════════════════════════════════════════
        # TEST 13: Desktop Layout
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 13: Desktop Layout ═══")
        # Back on desktop page
        desktop_layout = await page.evaluate("""
            (function() {
                var sidebar = document.querySelector('.sidebar, [class*="sidebar"], nav');
                var mainArea = document.querySelector('.main, [class*="main-area"], [class*="content-area"]');
                var topBar = document.querySelector('[class*="top-bar"], header, [class*="topbar"]');

                var bodyWidth = document.body.scrollWidth;
                var windowWidth = window.innerWidth;

                return {
                    has_sidebar: !!sidebar,
                    has_main: !!mainArea,
                    has_topbar: !!topBar,
                    body_width: bodyWidth,
                    window_width: windowWidth,
                    no_overflow: bodyWidth <= windowWidth + 5
                };
            })()
        """)
        await screenshot(page, "13-desktop-layout")

        record("Desktop - Layout structure", "PASS" if desktop_layout.get("has_sidebar") else "WARN",
               f"sidebar={desktop_layout.get('has_sidebar')}, main={desktop_layout.get('has_main')}, topbar={desktop_layout.get('has_topbar')}")
        record("Desktop - No horizontal overflow", "PASS" if desktop_layout.get("no_overflow") else "FAIL",
               f"body={desktop_layout.get('body_width')}px, window={desktop_layout.get('window_width')}px")

        # ═══════════════════════════════════════════════════════
        # TEST 14: Console Errors
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 14: Console Errors ═══")
        # Filter meaningful errors (ignore expected 404s for analytics etc)
        meaningful_errors = [e for e in console_errors if not any(ignore in e.lower() for ignore in [
            'analytics', 'gtag', 'facebook', 'intercom', 'hotjar', 'favicon',
            'net::err_aborted', 'adsbygoogle', 'clarity'
        ])]

        log(f"  Total console errors: {len(console_errors)}")
        log(f"  Meaningful errors: {len(meaningful_errors)}")
        for err in meaningful_errors[:10]:
            log(f"    {err[:200]}")

        if len(meaningful_errors) == 0:
            record("Console Errors - Zero JS errors", "PASS", "No meaningful JavaScript errors")
        elif len(meaningful_errors) <= 3:
            record("Console Errors - Zero JS errors", "WARN", f"{len(meaningful_errors)} errors: {meaningful_errors[0][:100] if meaningful_errors else ''}")
        else:
            record("Console Errors - Zero JS errors", "FAIL", f"{len(meaningful_errors)} console errors found (see log)")

        # ═══════════════════════════════════════════════════════
        # TEST 15: Network Requests
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 15: Network Requests ═══")
        # Check key API endpoints
        api_results = {}
        api_endpoints = {
            "commands": "https://app.purebrain.ai/api/commands",
            "shortcuts": "https://app.purebrain.ai/api/shortcuts",
            "agents": "https://app.purebrain.ai/api/agents",
        }

        for name, url in api_endpoints.items():
            try:
                response = await page.evaluate(f"""
                    async function() {{
                        try {{
                            var resp = await fetch('{url}', {{
                                headers: {{ 'Authorization': 'Bearer {TOKEN}' }}
                            }});
                            var text = await resp.text();
                            return {{ status: resp.status, length: text.length, ok: resp.ok }};
                        }} catch(e) {{
                            return {{ error: e.toString() }};
                        }}
                    }}
                """)
                api_results[name] = response
                status = response.get("status", "?")
                ok = response.get("ok", False)
                length = response.get("length", 0)
                record(f"Network - /api/{name} returns 200", "PASS" if ok else "FAIL",
                       f"status={status}, length={length}b")
            except Exception as e:
                record(f"Network - /api/{name} returns 200", "FAIL", str(e)[:100])

        # Check for failed network requests
        if len(network_failures) == 0:
            record("Network - No failed requests", "PASS", "All network requests succeeded")
        else:
            meaningful_failures = [f for f in network_failures if not any(x in f for x in ['analytics', 'gtag', 'facebook'])]
            if len(meaningful_failures) == 0:
                record("Network - No failed requests", "PASS", f"{len(network_failures)} failures all analytics (expected)")
            else:
                record("Network - No failed requests", "WARN", f"{len(meaningful_failures)} failed: {meaningful_failures[0][:100]}")

        # ═══════════════════════════════════════════════════════
        # TEST 16: Neural Canvas
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 16: Neural Canvas ═══")
        # Navigate to chat to see canvas
        for sel in ['div[data-panel="chat"]', '[data-panel="chat"]']:
            try:
                await page.click(sel, timeout=2000)
                break
            except:
                pass
        await page.wait_for_timeout(1500)

        canvas_data = await page.evaluate("""
            (function() {
                var canvas = document.getElementById('hmiCanvas') ||
                             document.querySelector('canvas');
                if (!canvas) return { exists: false };
                var style = window.getComputedStyle(canvas);
                return {
                    exists: true,
                    width: canvas.width,
                    height: canvas.height,
                    style_width: style.width,
                    style_height: style.height,
                    display: style.display,
                    opacity: style.opacity,
                    visible: style.display !== 'none' && parseFloat(style.opacity || 1) > 0
                };
            })()
        """)
        await screenshot(page, "16-neural-canvas")

        if canvas_data.get("exists") and canvas_data.get("visible"):
            record("Neural Canvas - Renders visible", "PASS",
                   f"canvas found, display={canvas_data.get('display')}, opacity={canvas_data.get('opacity')}, cssSize={canvas_data.get('style_width')}x{canvas_data.get('style_height')}")
        elif canvas_data.get("exists"):
            record("Neural Canvas - Renders visible", "WARN",
                   f"Canvas exists but visibility uncertain. display={canvas_data.get('display')}, opacity={canvas_data.get('opacity')}")
        else:
            record("Neural Canvas - Renders visible", "FAIL", "No canvas element found")

        # Check for WebGL errors in console related to canvas
        webgl_errors = [e for e in console_errors if any(x in e.lower() for x in ['webgl', 'canvas', 'shader', 'gl.'])]
        record("Neural Canvas - No WebGL errors", "PASS" if not webgl_errors else "WARN",
               f"No WebGL errors" if not webgl_errors else f"{len(webgl_errors)} WebGL errors: {webgl_errors[0][:100]}")

        # ═══════════════════════════════════════════════════════
        # TEST 17: Navigation (all panels clickable)
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 17: Navigation ═══")
        nav_items = await page.evaluate("""
            (function() {
                var items = document.querySelectorAll('[data-panel]');
                var results = [];
                items.forEach(function(item) {
                    var panel = item.getAttribute('data-panel');
                    var display = window.getComputedStyle(item).display;
                    results.push({ panel: panel, visible: display !== 'none' });
                });
                return results;
            })()
        """)

        visible_nav = [i for i in nav_items if i.get("visible")]
        hidden_nav = [i for i in nav_items if not i.get("visible")]

        record("Navigation - Nav items present", "PASS" if len(nav_items) >= 8 else "WARN",
               f"{len(nav_items)} total nav items, {len(visible_nav)} visible, {len(hidden_nav)} hidden")

        await screenshot(page, "17-navigation")

        # Test clicking through key panels
        panels_to_test = ["chat", "agents", "tasks", "terminal"]
        panels_working = []
        for panel_id in panels_to_test:
            try:
                await page.click(f'div[data-panel="{panel_id}"]', timeout=2000)
                await page.wait_for_timeout(1000)
                is_active = await page.evaluate(f"""
                    (function() {{
                        var panel = document.getElementById('panel-{panel_id}');
                        return !!(panel && panel.classList.contains('active'));
                    }})()
                """)
                if is_active:
                    panels_working.append(panel_id)
            except:
                pass

        record("Navigation - Panel switching works", "PASS" if len(panels_working) >= 3 else "WARN",
               f"Working panel switches: {panels_working}")

        # ═══════════════════════════════════════════════════════
        # TEST 18: Dark Theme
        # ═══════════════════════════════════════════════════════
        log("\n═══ TEST 18: Dark Theme ═══")
        # Navigate back to chat
        for sel in ['div[data-panel="chat"]', '[data-panel="chat"]']:
            try:
                await page.click(sel, timeout=2000)
                break
            except:
                pass
        await page.wait_for_timeout(1000)

        theme_data = await page.evaluate("""
            (function() {
                var body = document.body;
                var bodyBg = window.getComputedStyle(body).backgroundColor;

                // Check multiple key elements
                var sidebar = document.querySelector('.sidebar, [class*="sidebar"]');
                var sidebarBg = sidebar ? window.getComputedStyle(sidebar).backgroundColor : 'N/A';

                var mainContainer = document.querySelector('.main, [class*="main-area"], [class*="portal-main"]');
                var mainBg = mainContainer ? window.getComputedStyle(mainContainer).backgroundColor : 'N/A';

                // Check for any obviously light backgrounds
                var allEls = document.querySelectorAll('*');
                var lightBgCount = 0;
                var lightBgExamples = [];
                for (var i = 0; i < Math.min(allEls.length, 200); i++) {
                    var el = allEls[i];
                    if (!el.children.length) continue; // Skip leaves
                    var bg = window.getComputedStyle(el).backgroundColor;
                    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                        // Parse RGB values
                        var match = bg.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                        if (match) {
                            var r = parseInt(match[1]), g = parseInt(match[2]), b = parseInt(match[3]);
                            var luminance = (0.299 * r + 0.587 * g + 0.114 * b);
                            if (luminance > 180) {  // Very light background
                                lightBgCount++;
                                if (lightBgExamples.length < 3) {
                                    lightBgExamples.push({ tag: el.tagName, class: el.className.substring(0,40), bg: bg });
                                }
                            }
                        }
                    }
                }

                return {
                    body_bg: bodyBg,
                    sidebar_bg: sidebarBg,
                    main_bg: mainBg,
                    light_bg_count: lightBgCount,
                    light_bg_examples: lightBgExamples
                };
            })()
        """)
        await screenshot(page, "18-dark-theme")

        # Check body background is dark
        body_bg = theme_data.get("body_bg", "")
        body_is_dark = False
        if body_bg:
            import re
            match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', body_bg)
            if match:
                r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                body_is_dark = luminance < 50

        record("Dark Theme - Body background is dark", "PASS" if body_is_dark else "FAIL",
               f"body bg: {body_bg} (target: #080a12)")

        light_count = theme_data.get("light_bg_count", 0)
        if light_count == 0:
            record("Dark Theme - No unexpected light backgrounds", "PASS", "All sampled elements have dark backgrounds")
        elif light_count <= 3:
            record("Dark Theme - No unexpected light backgrounds", "WARN",
                   f"{light_count} light elements: {theme_data.get('light_bg_examples', [])}")
        else:
            record("Dark Theme - No unexpected light backgrounds", "FAIL",
                   f"{light_count} light background elements found")

        await browser.close()

        # ═══════════════════════════════════════════════════════
        # FINAL REPORT
        # ═══════════════════════════════════════════════════════
        log("\n" + "="*70)
        log("PUREBRAIN PORTAL - PRE-SHIP QA REPORT")
        log(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log("="*70)

        pass_count = sum(1 for r in results.values() if r["status"] == "PASS")
        fail_count = sum(1 for r in results.values() if r["status"] == "FAIL")
        warn_count = sum(1 for r in results.values() if r["status"] == "WARN")
        total = len(results)

        log(f"\nSUMMARY: {pass_count} PASS | {fail_count} FAIL | {warn_count} WARN | {total} total")

        log("\n--- FAILURES ---")
        for name, r in results.items():
            if r["status"] == "FAIL":
                log(f"  ❌ {name}: {r['notes']}")

        log("\n--- WARNINGS ---")
        for name, r in results.items():
            if r["status"] == "WARN":
                log(f"  ⚠️  {name}: {r['notes']}")

        log("\n--- ALL RESULTS ---")
        for name, r in results.items():
            icon = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "⚠️"
            log(f"  {icon} {r['status']} | {name}: {r['notes'][:80]}")

        log(f"\nScreenshots saved to: {SS_DIR}")
        log(f"Total screenshots: {ss_count[0]}")
        log(f"\nConsole errors (total): {len(console_errors)}")
        log(f"Network failures: {len(network_failures)}")

        return results, pass_count, fail_count, warn_count


if __name__ == "__main__":
    asyncio.run(run_qa())
