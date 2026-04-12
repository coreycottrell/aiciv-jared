"""
OAuth Button Diagnosis Script v2 - 2026-02-27
Smarter flow handling after bypass.
"""

import asyncio
import json
import os
import time
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/oauth-diagnosis-20260227"
PASSWORD = "PureBrain.ai253443$$$"

PAGES = {
    "sandbox": "https://purebrain.ai/pay-test-sandbox-2/",
    "production": "https://purebrain.ai/pay-test-2/",
}

all_console_logs = {"sandbox": [], "production": []}
all_network_events = {"sandbox": [], "production": []}


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


async def screenshot(page, label, page_key):
    path = f"{SCREENSHOTS_DIR}/{page_key}-{label}.png"
    await page.screenshot(path=path, full_page=False)
    print(f"  [{ts()}] Screenshot: {os.path.basename(path)}")
    return path


async def diagnose_page(playwright, page_key, url):
    print(f"\n{'='*60}")
    print(f"DIAGNOSING: {page_key.upper()} -> {url}")
    print(f"{'='*60}")

    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ]
    )
    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        ignore_https_errors=True,
    )
    page = await context.new_page()

    def on_console(msg):
        entry = {"type": msg.type, "text": msg.text, "time": ts()}
        all_console_logs[page_key].append(entry)
        if msg.type in ("error", "warning"):
            print(f"  [{ts()}] CONSOLE {msg.type.upper()}: {msg.text[:200]}")

    page.on("console", on_console)

    def on_request(request):
        if any(keyword in request.url for keyword in ["api/birth", "oauth", "anthropic", "witness", "purebrain.ai/api"]):
            entry = {"type": "request", "method": request.method, "url": request.url, "time": ts()}
            all_network_events[page_key].append(entry)
            print(f"  [{ts()}] REQUEST: {request.method} {request.url[:120]}")

    def on_response(response):
        if any(keyword in response.url for keyword in ["api/birth", "oauth", "anthropic", "witness", "purebrain.ai/api"]):
            entry = {"type": "response", "status": response.status, "url": response.url, "time": ts()}
            all_network_events[page_key].append(entry)
            status_marker = "OK" if response.status < 400 else "FAIL"
            print(f"  [{ts()}] RESPONSE [{status_marker}] {response.status}: {response.url[:120]}")

    def on_request_failed(request):
        if any(keyword in request.url for keyword in ["api/birth", "oauth", "anthropic", "witness", "purebrain.ai/api"]):
            entry = {"type": "failed", "url": request.url, "failure": request.failure, "time": ts()}
            all_network_events[page_key].append(entry)
            print(f"  [{ts()}] REQUEST FAILED: {request.url[:120]} | {request.failure}")

    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)

    results = {
        "page_key": page_key,
        "url": url,
        "steps": [],
        "errors": [],
    }

    # --- Step 1: Navigate ---
    print(f"\n[Step 1] Navigating to {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(3)
    title = await page.title()
    print(f"  Title: {title}")
    await screenshot(page, "01-initial-load", page_key)

    # --- Step 2: Password ---
    print(f"\n[Step 2] Password form")
    pw_field = page.locator("input[id^='pwbox-']")
    if await pw_field.count() > 0:
        print(f"  Submitting password...")
        await pw_field.fill(PASSWORD)
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        await asyncio.sleep(6)
        await screenshot(page, "02-after-password", page_key)

    # --- Step 3: Extract script info before clicking anything ---
    print(f"\n[Step 3] Extracting script info")
    script_data = await page.evaluate("""() => {
        const scripts = Array.from(document.querySelectorAll('script'));
        const inlineScripts = scripts.filter(s => s.src === '' && s.textContent.length > 1000);

        let versions = [];
        let witnessHosts = [];
        let oauthPatterns = [];
        let birthApiRefs = [];
        let scriptExcerpts = {};

        for (let i = 0; i < inlineScripts.length; i++) {
            const text = inlineScripts[i].textContent;
            const size = text.length;

            // Only inspect the large scripts (pre-payment ~64k, post-payment ~88k)
            if (size < 10000) continue;

            // Version
            const vMatch = text.match(/v(\\d+\\.\\d+\\.\\d+)/g);
            if (vMatch) versions.push(...vMatch.slice(0, 5));

            // Witness host
            const wMatch = text.match(/WITNESS_WEBHOOK_HOST\\s*=\\s*['"]([^'"]+)['"]/g);
            if (wMatch) witnessHosts.push(...wMatch);

            // OAuth patterns - search broadly
            const oauthMatches = text.match(/[Oo][Aa][Uu][Tt][Hh][^\\n]{0,200}/g);
            if (oauthMatches) oauthPatterns.push(...oauthMatches.slice(0, 5));

            // /api/birth references
            const birthMatches = text.match(/\\/api\\/birth\\/[a-z-]+[^'"\\s]{0,100}/g);
            if (birthMatches) birthApiRefs.push(...birthMatches.slice(0, 10));

            // Claude.ai OAuth URL pattern
            const claudeOauth = text.match(/claude\\.ai\\/oauth[^'"\\s]{0,200}/g);
            if (claudeOauth) oauthPatterns.push(...claudeOauth.map(m => 'CLAUDE_OAUTH: ' + m));

            // Find startOauth or similar function signatures
            const oauthFnMatch = text.match(/(?:start|handle|init|trigger|launch|do|run)[Oo]auth[^{]{0,100}/g);
            if (oauthFnMatch) oauthPatterns.push(...oauthFnMatch.slice(0, 5).map(m => 'FN: ' + m));

            // Get lines around 'oauth' keyword (case insensitive) for context
            const lines = text.split('\\n');
            const oauthLines = lines.filter(l => l.toLowerCase().includes('oauth')).slice(0, 10);
            if (oauthLines.length > 0) {
                scriptExcerpts[`script_${size}`] = oauthLines;
            }
        }

        return {
            totalScripts: inlineScripts.length,
            scriptSizes: inlineScripts.map(s => s.textContent.length),
            versions: [...new Set(versions)],
            witnessHosts: [...new Set(witnessHosts)],
            oauthPatterns: [...new Set(oauthPatterns)].slice(0, 20),
            birthApiRefs: [...new Set(birthApiRefs)],
            scriptExcerpts: scriptExcerpts,
        };
    }""")

    print(f"  Script sizes: {script_data['scriptSizes']}")
    print(f"  Versions: {script_data['versions']}")
    print(f"  Witness hosts: {script_data['witnessHosts']}")
    print(f"  OAuth patterns found: {len(script_data['oauthPatterns'])}")
    for p in script_data['oauthPatterns']:
        print(f"    {p[:200]}")
    print(f"  /api/birth refs: {script_data['birthApiRefs']}")
    print(f"  Script excerpts with 'oauth':")
    for script_key, lines in script_data.get('scriptExcerpts', {}).items():
        print(f"    [{script_key}]:")
        for line in lines:
            print(f"      {line.strip()[:200]}")

    results["script_data"] = script_data

    # --- Step 4: Begin chat ---
    print(f"\n[Step 4] Starting pre-payment chat")
    begin_btn = page.locator(".chat-initial__btn")
    if await begin_btn.count() > 0:
        await begin_btn.click()
        await asyncio.sleep(6)  # Wait for AI to respond
        await screenshot(page, "03-after-begin", page_key)

    # --- Step 5: Bypass ---
    print(f"\n[Step 5] Applying bypass code")
    user_input = page.locator("#userInput")
    if await user_input.count() > 0:
        await user_input.fill("pb-full-bypass")
        await asyncio.sleep(0.3)
        submit_btn = page.locator("#submitBtn")
        if await submit_btn.count() > 0:
            await submit_btn.click()
        else:
            await page.keyboard.press("Enter")
        # Wait for bypass to complete and pricing to appear
        await asyncio.sleep(8)
        await screenshot(page, "04-after-bypass", page_key)

    # --- Step 6: Check what's visible now ---
    print(f"\n[Step 6] Inspecting page state after bypass")
    page_state = await page.evaluate("""() => {
        return {
            pricingSection: {
                exists: !!document.querySelector('.pricing-section'),
                display: document.querySelector('.pricing-section') ?
                    window.getComputedStyle(document.querySelector('.pricing-section')).display : 'n/a',
                hasCards: document.querySelectorAll('.pricing-card').length,
            },
            proCta: {
                exists: !!document.getElementById('proCta'),
                display: document.getElementById('proCta') ?
                    window.getComputedStyle(document.getElementById('proCta')).display : 'n/a',
                visible: document.getElementById('proCta') ?
                    document.getElementById('proCta').getBoundingClientRect().height > 0 : false,
                text: document.getElementById('proCta') ? document.getElementById('proCta').textContent.trim() : '',
            },
            allButtons: Array.from(document.querySelectorAll('button:not([style*="display: none"])')).slice(0, 20).map(b => ({
                id: b.id,
                class: b.className.substring(0, 60),
                text: b.textContent.trim().substring(0, 50),
                visible: b.getBoundingClientRect().height > 0,
                display: window.getComputedStyle(b).display,
            })),
            sandboxBypassBtn: {
                exists: !!document.getElementById('pb-sandbox-bypass-btn'),
                visible: document.getElementById('pb-sandbox-bypass-btn') ?
                    document.getElementById('pb-sandbox-bypass-btn').getBoundingClientRect().height > 0 : false,
            },
            ptcWrapper: {
                exists: !!document.querySelector('.ptc-wrapper'),
                display: document.querySelector('.ptc-wrapper') ?
                    window.getComputedStyle(document.querySelector('.ptc-wrapper')).display : 'n/a',
            },
        };
    }""")
    print(f"  Pricing section: {page_state['pricingSection']}")
    print(f"  #proCta: {page_state['proCta']}")
    print(f"  Sandbox bypass btn: {page_state['sandboxBypassBtn']}")
    print(f"  PTC wrapper: {page_state['ptcWrapper']}")
    print(f"  Visible buttons: {[b for b in page_state['allButtons'] if b['visible']]}")

    # --- Step 7: Scroll and find any visible pricing button ---
    print(f"\n[Step 7] Looking for any pricing or activation button")

    # Try scrolling to find pricing section
    await page.evaluate("window.scrollBy(0, 600)")
    await asyncio.sleep(1)
    await screenshot(page, "05-scrolled-down", page_key)

    # Try clicking via JavaScript (bypasses visibility check)
    click_result = await page.evaluate("""() => {
        // Try to find and reveal the pricing section
        const pricingSection = document.querySelector('.pricing-section');
        if (pricingSection) {
            pricingSection.style.display = 'block';
            pricingSection.style.opacity = '1';
            pricingSection.style.visibility = 'visible';
            pricingSection.scrollIntoView();
        }

        // Find the best pricing CTA button
        const candidates = [
            document.getElementById('proCta'),
            document.querySelector('.pricing-card__cta--primary'),
            document.querySelector('.pricing-card__cta'),
            ...document.querySelectorAll('button[onclick*="PayPal"]'),
            ...document.querySelectorAll('button[onclick*="Modal"]'),
        ].filter(Boolean);

        if (candidates.length > 0) {
            const btn = candidates[0];
            btn.scrollIntoView();
            // Force click via JS
            btn.click();
            return {
                found: true,
                clicked: btn.id || btn.className,
                text: btn.textContent.trim().substring(0, 50),
            };
        }
        return { found: false, candidates: candidates.length };
    }""")
    print(f"  JS click result: {click_result}")
    await asyncio.sleep(4)
    await screenshot(page, "06-after-js-click", page_key)

    # --- Step 8: Check for sandbox bypass button after PayPal modal might open ---
    print(f"\n[Step 8] Looking for sandbox bypass button (post-payment trigger)")
    sandbox_state = await page.evaluate("""() => {
        const bypassBtn = document.getElementById('pb-sandbox-bypass-btn');
        const paypalModal = document.querySelector('.paypal-modal, #paypal-modal, [id*="paypal-modal"]');
        const paypalBtns = document.querySelectorAll('iframe[name*="paypal"]');
        const allModals = document.querySelectorAll('[class*="modal"], [id*="modal"]');

        return {
            bypassBtn: bypassBtn ? {
                exists: true,
                visible: bypassBtn.getBoundingClientRect().height > 0,
                display: window.getComputedStyle(bypassBtn).display,
                text: bypassBtn.textContent.trim(),
            } : { exists: false },
            paypalModal: paypalModal ? { exists: true, display: window.getComputedStyle(paypalModal).display } : { exists: false },
            paypalIframes: paypalBtns.length,
            allModals: Array.from(allModals).map(m => ({
                id: m.id,
                class: m.className.substring(0, 50),
                display: window.getComputedStyle(m).display,
            })).filter(m => m.display !== 'none').slice(0, 5),
        };
    }""")
    print(f"  Sandbox bypass: {sandbox_state['bypassBtn']}")
    print(f"  PayPal modal: {sandbox_state['paypalModal']}")
    print(f"  PayPal iframes: {sandbox_state['paypalIframes']}")
    print(f"  Open modals: {sandbox_state['allModals']}")

    # Try clicking sandbox bypass if it's there
    if sandbox_state['bypassBtn']['exists']:
        print(f"  Clicking sandbox bypass button...")
        bypass_btn = page.locator("#pb-sandbox-bypass-btn")
        try:
            await bypass_btn.click(force=True)
        except Exception:
            await page.evaluate("document.getElementById('pb-sandbox-bypass-btn').click()")
        await asyncio.sleep(6)
        await screenshot(page, "07-after-sandbox-bypass", page_key)
    else:
        # No sandbox bypass — try production flow (skip payment, go direct to PTC)
        print(f"  No sandbox bypass. Trying to directly trigger post-payment chat...")
        # The post-payment chat might be triggerable via JS
        trigger_result = await page.evaluate("""() => {
            // Check if showPostPaymentChat or similar exists
            const fns = ['showPostPaymentChat', 'initPTC', 'startPTC', 'showPTC',
                         'displayPostPayment', 'triggerPostPayment'];
            for (const fn of fns) {
                if (typeof window[fn] === 'function') {
                    try {
                        window[fn]();
                        return { triggered: fn };
                    } catch(e) {
                        return { error: fn + ': ' + e.message };
                    }
                }
            }

            // Check for any payment success handler
            const successFns = ['handlePaymentSuccess', 'onPaymentApproved', 'paymentSuccess'];
            for (const fn of successFns) {
                if (typeof window[fn] === 'function') {
                    try {
                        window[fn]({ orderID: 'TEST-ORDER-123' });
                        return { triggered: fn };
                    } catch(e) {
                        return { error: fn + ': ' + e.message };
                    }
                }
            }

            return { not_found: true, available_fns: Object.keys(window).filter(k =>
                typeof window[k] === 'function' && k.toLowerCase().includes('pay')
            ).slice(0, 10) };
        }""")
        print(f"  Direct trigger result: {trigger_result}")
        await asyncio.sleep(4)
        await screenshot(page, "07-direct-trigger-attempt", page_key)

    # --- Step 9: Check for OAuth button in PTC ---
    print(f"\n[Step 9] Looking for OAuth button in post-payment chat")
    await asyncio.sleep(3)

    oauth_state = await page.evaluate("""() => {
        // Search for OAuth button broadly
        const ptcWrapper = document.querySelector('.ptc-wrapper');
        const ptcMessages = document.querySelectorAll('.ptc-msg--ai');
        const ptcButtons = document.querySelectorAll('.ptc-btn');
        const allInputs = document.querySelectorAll('input, textarea');

        // Specifically look for OAuth-related elements
        const oauthEls = [];
        document.querySelectorAll('*').forEach(el => {
            const text = (el.textContent || '').toLowerCase();
            const id = (el.id || '').toLowerCase();
            const cls = (el.className || '').toLowerCase();
            const onclick = (el.getAttribute('onclick') || '').toLowerCase();
            const href = (el.href || '').toLowerCase();

            if (text.includes('connect') && text.includes('claude') && el.children.length === 0) {
                oauthEls.push({ type: 'connect-claude-text', tag: el.tagName, text: el.textContent.trim().substring(0, 80) });
            }
            if (id.includes('oauth') || cls.includes('oauth') || onclick.includes('oauth') || href.includes('oauth')) {
                oauthEls.push({ type: 'oauth-attr', tag: el.tagName, id: el.id, text: el.textContent.trim().substring(0, 80), onclick: onclick.substring(0, 100) });
            }
            if (href.includes('claude.ai') || onclick.includes('claude.ai')) {
                oauthEls.push({ type: 'claude-ai-link', tag: el.tagName, href: href.substring(0, 150) });
            }
        });

        // Get all current ptc-btn elements and their state
        const currentBtns = Array.from(ptcButtons).map(b => ({
            id: b.id,
            class: b.className,
            text: b.textContent.trim().substring(0, 80),
            visible: b.getBoundingClientRect().height > 0,
            display: window.getComputedStyle(b).display,
        }));

        // Get latest AI messages
        const latestMessages = Array.from(ptcMessages).slice(-3).map(m => m.textContent.trim().substring(0, 200));

        return {
            ptcWrapperExists: !!ptcWrapper,
            ptcWrapperDisplay: ptcWrapper ? window.getComputedStyle(ptcWrapper).display : 'n/a',
            ptcMessageCount: ptcMessages.length,
            latestMessages: latestMessages,
            ptcButtonCount: ptcButtons.length,
            currentBtns: currentBtns,
            oauthEls: oauthEls,
            inputCount: allInputs.length,
        };
    }""")

    print(f"  PTC wrapper: exists={oauth_state['ptcWrapperExists']} display={oauth_state['ptcWrapperDisplay']}")
    print(f"  PTC messages: {oauth_state['ptcMessageCount']}")
    print(f"  Latest messages: {oauth_state['latestMessages']}")
    print(f"  PTC buttons: {oauth_state['ptcButtonCount']}")
    for btn in oauth_state['currentBtns']:
        print(f"    Btn: {btn}")
    print(f"  OAuth elements found: {len(oauth_state['oauthEls'])}")
    for el in oauth_state['oauthEls']:
        print(f"    OAuth el: {el}")

    results["oauth_state"] = oauth_state
    await screenshot(page, "08-ptc-oauth-check", page_key)

    # --- Step 10: Deep dive into PTC script for OAuth implementation ---
    print(f"\n[Step 10] Deep script analysis for OAuth implementation")
    oauth_deep = await page.evaluate("""() => {
        const scripts = Array.from(document.querySelectorAll('script'));
        const results = {
            oauthCodeSegments: [],
            birthStartRefs: [],
            claudeOauthUrl: null,
            redirectUri: null,
        };

        for (const s of scripts) {
            if (s.src !== '') continue;
            const text = s.textContent;
            if (text.length < 5000) continue;

            // Split into lines for context
            const lines = text.split('\\n');

            // Find lines containing oauth
            lines.forEach((line, idx) => {
                if (line.toLowerCase().includes('oauth')) {
                    // Get context (5 lines before and after)
                    const start = Math.max(0, idx - 2);
                    const end = Math.min(lines.length - 1, idx + 5);
                    const context = lines.slice(start, end).join('\\n');
                    results.oauthCodeSegments.push({
                        scriptSize: text.length,
                        lineNum: idx,
                        context: context.substring(0, 500),
                    });
                }

                // Find /api/birth/start references
                if (line.includes('/api/birth/start')) {
                    results.birthStartRefs.push({
                        scriptSize: text.length,
                        lineNum: idx,
                        line: line.trim().substring(0, 300),
                    });
                }
            });

            // Extract claude.ai OAuth URL
            const claudeMatch = text.match(/https:\/\/claude\.ai\/oauth[^'"\\s)]+/);
            if (claudeMatch) results.claudeOauthUrl = claudeMatch[0];

            // Extract redirect_uri
            const redirectMatch = text.match(/redirect_uri[^'"]*['"]([^'"]+)['"]/);
            if (redirectMatch) results.redirectUri = redirectMatch[1];
        }

        return results;
    }""")

    print(f"  Claude OAuth URL: {oauth_deep.get('claudeOauthUrl')}")
    print(f"  Redirect URI: {oauth_deep.get('redirectUri')}")
    print(f"  /api/birth/start refs: {len(oauth_deep.get('birthStartRefs', []))}")
    for ref in oauth_deep.get('birthStartRefs', []):
        print(f"    Line {ref['lineNum']} (script {ref['scriptSize']}): {ref['line'][:200]}")
    print(f"  OAuth code segments: {len(oauth_deep.get('oauthCodeSegments', []))}")
    for seg in oauth_deep.get('oauthCodeSegments', []):
        print(f"    === Script {seg['scriptSize']} Line {seg['lineNum']} ===")
        print(f"    {seg['context'][:400]}")

    results["oauth_deep"] = oauth_deep

    # --- Step 11: Try to manually call /api/birth/start ---
    print(f"\n[Step 11] Testing /api/birth/start endpoint directly")
    birth_start_result = await page.evaluate("""async () => {
        try {
            const res = await fetch('/api/birth/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({
                    container: 'test-container',
                    email: 'test@example.com',
                }),
            });
            const text = await res.text();
            return {
                status: res.status,
                statusText: res.statusText,
                body: text.substring(0, 500),
                contentType: res.headers.get('content-type'),
            };
        } catch(e) {
            return { error: e.message };
        }
    }""")
    print(f"  POST /api/birth/start: {birth_start_result}")
    results["birth_start_api"] = birth_start_result

    # Also try GET
    birth_start_get = await page.evaluate("""async () => {
        try {
            const res = await fetch('/api/birth/start', {
                method: 'GET',
                headers: {'Accept': 'application/json'},
            });
            const text = await res.text();
            return {
                status: res.status,
                statusText: res.statusText,
                body: text.substring(0, 500),
            };
        } catch(e) {
            return { error: e.message };
        }
    }""")
    print(f"  GET /api/birth/start: {birth_start_get}")
    results["birth_start_get"] = birth_start_get

    # --- Final screenshot ---
    await screenshot(page, "09-final", page_key)

    # Console summary
    errors = [l for l in all_console_logs[page_key] if l["type"] == "error"]
    warnings = [l for l in all_console_logs[page_key] if l["type"] == "warning"]
    results["console_summary"] = {
        "total": len(all_console_logs[page_key]),
        "errors": errors,
        "warnings": warnings[:10],
    }
    results["network_events"] = all_network_events[page_key]

    print(f"\n[Summary] Console: {len(all_console_logs[page_key])} entries ({len(errors)} errors, {len(warnings)} warnings)")
    print(f"[Summary] Network: {len(all_network_events[page_key])} events captured")

    await browser.close()
    return results


async def main():
    print(f"\nOAuth Button Diagnosis v2 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Screenshots: {SCREENSHOTS_DIR}")

    results = {}

    async with async_playwright() as playwright:
        print("\n\n### PHASE 1: SANDBOX PAGE ###")
        results["sandbox"] = await diagnose_page(playwright, "sandbox", PAGES["sandbox"])

        print(f"\nWaiting 25 seconds before production page (WAF avoidance)...")
        await asyncio.sleep(25)

        print("\n\n### PHASE 2: PRODUCTION PAGE ###")
        results["production"] = await diagnose_page(playwright, "production", PAGES["production"])

    # --- Final Comparison ---
    print("\n\n" + "="*70)
    print("FINAL COMPARISON REPORT")
    print("="*70)

    s = results["sandbox"]
    p = results["production"]

    print("\n[Script Sizes]")
    print(f"  Sandbox:    {s['script_data']['scriptSizes']}")
    print(f"  Production: {p['script_data']['scriptSizes']}")
    print(f"  Same? {s['script_data']['scriptSizes'] == p['script_data']['scriptSizes']}")

    print("\n[Versions]")
    print(f"  Sandbox:    {s['script_data']['versions']}")
    print(f"  Production: {p['script_data']['versions']}")

    print("\n[Witness Hosts]")
    print(f"  Sandbox:    {s['script_data']['witnessHosts']}")
    print(f"  Production: {p['script_data']['witnessHosts']}")

    print("\n[/api/birth/start API Response]")
    print(f"  Sandbox POST:    {s.get('birth_start_api')}")
    print(f"  Production POST: {p.get('birth_start_api')}")
    print(f"  Sandbox GET:     {s.get('birth_start_get')}")
    print(f"  Production GET:  {p.get('birth_start_get')}")

    print("\n[OAuth Deep Analysis]")
    print(f"  Sandbox claude_oauth_url: {s['oauth_deep'].get('claudeOauthUrl')}")
    print(f"  Prod claude_oauth_url:    {p['oauth_deep'].get('claudeOauthUrl')}")
    print(f"  Sandbox redirect_uri: {s['oauth_deep'].get('redirectUri')}")
    print(f"  Prod redirect_uri:    {p['oauth_deep'].get('redirectUri')}")

    s_birth = s['oauth_deep'].get('birthStartRefs', [])
    p_birth = p['oauth_deep'].get('birthStartRefs', [])
    print(f"\n  Sandbox /api/birth/start refs ({len(s_birth)}):")
    for r in s_birth[:3]:
        print(f"    {r['line'][:200]}")
    print(f"\n  Prod /api/birth/start refs ({len(p_birth)}):")
    for r in p_birth[:3]:
        print(f"    {r['line'][:200]}")

    s_oauth = s['oauth_deep'].get('oauthCodeSegments', [])
    p_oauth = p['oauth_deep'].get('oauthCodeSegments', [])
    print(f"\n  Sandbox OAuth code segments ({len(s_oauth)}):")
    for seg in s_oauth[:3]:
        print(f"    Script {seg['scriptSize']}, line {seg['lineNum']}:")
        print(f"    {seg['context'][:300]}")
    print(f"\n  Prod OAuth code segments ({len(p_oauth)}):")
    for seg in p_oauth[:3]:
        print(f"    Script {seg['scriptSize']}, line {seg['lineNum']}:")
        print(f"    {seg['context'][:300]}")

    print("\n[Console Errors]")
    s_errors = s['console_summary']['errors']
    p_errors = p['console_summary']['errors']
    print(f"  Sandbox errors ({len(s_errors)}):")
    for e in s_errors[:5]:
        print(f"    {e['text'][:150]}")
    print(f"  Production errors ({len(p_errors)}):")
    for e in p_errors[:5]:
        print(f"    {e['text'][:150]}")

    print("\n[Network Events (API calls)]")
    print(f"  Sandbox:    {len(s['network_events'])} API events")
    for ev in s['network_events']:
        print(f"    {ev['type']}: {ev.get('method', ev['type'])} {ev['url'][:100]} {ev.get('status', ev.get('failure', ''))}")
    print(f"  Production: {len(p['network_events'])} API events")
    for ev in p['network_events']:
        print(f"    {ev['type']}: {ev.get('method', ev['type'])} {ev['url'][:100]} {ev.get('status', ev.get('failure', ''))}")

    # Save results
    output_path = f"{SCREENSHOTS_DIR}/oauth_diagnosis_v2_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")
    print(f"Screenshots in: {SCREENSHOTS_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
