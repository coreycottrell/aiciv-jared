"""
OAuth Button Diagnosis Script - 2026-02-27
Compares pay-test-sandbox-2 vs pay-test-2 OAuth button behavior.

Goals:
1. Load both pages (password protected)
2. Navigate through the chat flow to reach the OAuth button
3. Capture screenshots, console logs, and network events
4. Compare script versions, OAuth URLs, and API call behavior
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

console_logs = {"sandbox": [], "production": []}
network_events = {"sandbox": [], "production": []}
script_info = {"sandbox": {}, "production": {}}


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

    # --- Capture console logs ---
    def on_console(msg):
        entry = {
            "type": msg.type,
            "text": msg.text,
            "time": ts(),
        }
        console_logs[page_key].append(entry)
        if msg.type in ("error", "warning"):
            print(f"  [{ts()}] CONSOLE {msg.type.upper()}: {msg.text[:200]}")

    page.on("console", on_console)

    # --- Capture network events ---
    def on_request(request):
        if any(keyword in request.url for keyword in ["api", "birth", "oauth", "claude", "anthropic", "witness"]):
            entry = {"type": "request", "method": request.method, "url": request.url, "time": ts()}
            network_events[page_key].append(entry)
            print(f"  [{ts()}] REQUEST: {request.method} {request.url[:100]}")

    def on_response(response):
        if any(keyword in response.url for keyword in ["api", "birth", "oauth", "claude", "anthropic", "witness"]):
            entry = {"type": "response", "status": response.status, "url": response.url, "time": ts()}
            network_events[page_key].append(entry)
            status_marker = "OK" if response.status < 400 else "FAIL"
            print(f"  [{ts()}] RESPONSE [{status_marker}] {response.status}: {response.url[:100]}")

    def on_request_failed(request):
        entry = {"type": "failed", "url": request.url, "failure": request.failure, "time": ts()}
        network_events[page_key].append(entry)
        print(f"  [{ts()}] REQUEST FAILED: {request.url[:100]} | {request.failure}")

    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)

    results = {
        "page_key": page_key,
        "url": url,
        "steps": [],
        "oauth_button": None,
        "script_version": None,
        "errors": [],
    }

    # --- Step 1: Navigate ---
    print(f"\n[Step 1] Navigating to {url}")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        title = await page.title()
        print(f"  Title: {title}")
        await screenshot(page, "01-initial-load", page_key)
        results["steps"].append({"step": "navigate", "status": "ok", "title": title})
    except Exception as e:
        print(f"  ERROR during navigation: {e}")
        results["errors"].append(f"navigation: {str(e)}")
        await browser.close()
        return results

    # --- Step 2: Check for password form ---
    print(f"\n[Step 2] Checking for password form")
    pw_field = page.locator("input[id^='pwbox-']")
    pw_count = await pw_field.count()
    if pw_count > 0:
        print(f"  Password form found. Submitting...")
        await pw_field.fill(PASSWORD)
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        await asyncio.sleep(5)
        await screenshot(page, "02-after-password", page_key)
        results["steps"].append({"step": "password", "status": "submitted"})
    else:
        print(f"  No password form (already unlocked or different flow)")
        results["steps"].append({"step": "password", "status": "not_needed"})

    # --- Step 3: Extract script version info ---
    print(f"\n[Step 3] Extracting script version and configuration")
    script_data = await page.evaluate("""() => {
        // Look for script version markers
        const scripts = Array.from(document.querySelectorAll('script'));
        const inlineScripts = scripts.filter(s => s.src === '' && s.textContent.length > 1000);

        // Try to find version markers
        let versions = [];
        let oauthUrls = [];
        let birthUrls = [];
        let witnessHosts = [];

        for (const s of inlineScripts) {
            const text = s.textContent;

            // Look for version strings
            const vMatch = text.match(/v(\\d+\\.\\d+\\.\\d+)/g);
            if (vMatch) versions.push(...vMatch);

            // Look for OAuth-related URLs
            const oauthMatch = text.match(/(https?:\\/\\/[^"'\\s]+oauth[^"'\\s]*)/g);
            if (oauthMatch) oauthUrls.push(...oauthMatch);

            // Look for Claude auth URLs
            const claudeMatch = text.match(/(https?:\\/\\/[^"'\\s]*claude[^"'\\s]*)/g);
            if (claudeMatch) birthUrls.push(...claudeMatch);

            // Look for API birth URLs
            const apiMatch = text.match(/(https?:\\/\\/[^"'\\s]*\\/api\\/birth[^"'\\s]*)/g);
            if (apiMatch) birthUrls.push(...apiMatch);

            // Look for witness host
            const witnessMatch = text.match(/WITNESS_WEBHOOK_HOST\\s*=\\s*['"]([^'"]+)['"]/);
            if (witnessMatch) witnessHosts.push(witnessMatch[1]);
        }

        // Look for specific known variables
        let pbVersion = null;
        try { pbVersion = window.PB_VERSION || window.ptcVersion || null; } catch(e) {}

        // Check for sandbox detection
        let isSandbox = window.location.pathname.indexOf('sandbox') !== -1;

        // Check for birth/OAuth related globals
        let globals = {};
        const globalKeys = ['WITNESS_WEBHOOK_HOST', 'PB_OAUTH_URL', 'PB_CLAUDE_AUTH_URL', '_pbContainerName', 'ptcConfig'];
        for (const key of globalKeys) {
            try {
                if (window[key] !== undefined) globals[key] = String(window[key]);
            } catch(e) {}
        }

        return {
            inlineScriptCount: inlineScripts.length,
            inlineScriptSizes: inlineScripts.map(s => s.textContent.length),
            versions: [...new Set(versions)],
            oauthUrls: [...new Set(oauthUrls)],
            birthUrls: [...new Set(birthUrls)],
            witnessHosts: [...new Set(witnessHosts)],
            isSandbox: isSandbox,
            globals: globals,
            pbVersion: pbVersion,
        };
    }""")
    print(f"  Script sizes: {script_data.get('inlineScriptSizes', [])}")
    print(f"  Versions found: {script_data.get('versions', [])}")
    print(f"  Witness hosts: {script_data.get('witnessHosts', [])}")
    print(f"  OAuth URLs: {script_data.get('oauthUrls', [])}")
    print(f"  Birth URLs: {script_data.get('birthUrls', [])}")
    print(f"  Global vars: {script_data.get('globals', {})}")
    print(f"  Is sandbox: {script_data.get('isSandbox', 'unknown')}")
    script_info[page_key] = script_data
    results["script_version"] = script_data

    # --- Step 4: Start the chat flow ---
    print(f"\n[Step 4] Starting pre-payment chat flow")
    begin_btn = page.locator(".chat-initial__btn")
    begin_count = await begin_btn.count()
    if begin_count > 0:
        print(f"  Found 'Begin' button. Clicking...")
        await begin_btn.click()
        await asyncio.sleep(3)
        await screenshot(page, "03-after-begin-click", page_key)
        results["steps"].append({"step": "begin_chat", "status": "clicked"})
    else:
        print(f"  No begin button found — checking page state")
        await screenshot(page, "03-no-begin-button", page_key)
        results["steps"].append({"step": "begin_chat", "status": "button_not_found"})

    # --- Step 5: Use bypass to get past pre-payment ---
    print(f"\n[Step 5] Using bypass code to skip pre-payment chat")
    user_input = page.locator("#userInput")
    input_count = await user_input.count()
    if input_count > 0:
        await user_input.fill("pb-full-bypass")
        await asyncio.sleep(0.5)
        submit_btn = page.locator("#submitBtn")
        if await submit_btn.count() > 0:
            await submit_btn.click()
        else:
            await page.keyboard.press("Enter")
        await asyncio.sleep(5)
        await screenshot(page, "04-after-bypass", page_key)
        results["steps"].append({"step": "bypass", "status": "submitted"})
    else:
        print(f"  No user input field found")
        results["steps"].append({"step": "bypass", "status": "input_not_found"})

    # --- Step 6: Click "Activate Now" (proCta) ---
    print(f"\n[Step 6] Clicking Activate Now / proCta button")
    await asyncio.sleep(2)
    pro_cta = page.locator("#proCta")
    if await pro_cta.count() > 0:
        print(f"  Found #proCta. Clicking...")
        await pro_cta.click()
        await asyncio.sleep(3)
        await screenshot(page, "05-after-activate-now", page_key)
        results["steps"].append({"step": "activate_now", "status": "clicked"})
    else:
        print(f"  No #proCta found. Checking for alternative pricing buttons...")
        pricing_btns = page.locator(".pricing-btn, .btn-purchase, [data-plan]")
        count = await pricing_btns.count()
        print(f"  Alternative pricing buttons found: {count}")
        await screenshot(page, "05-no-procta", page_key)
        results["steps"].append({"step": "activate_now", "status": "not_found", "alternatives": count})

    # --- Step 7: Trigger sandbox payment bypass (sandbox only) ---
    if page_key == "sandbox":
        print(f"\n[Step 7] Triggering sandbox payment bypass")
        await asyncio.sleep(2)
        bypass_btn = page.locator("#pb-sandbox-bypass-btn")
        if await bypass_btn.count() > 0:
            print(f"  Found sandbox bypass button. Clicking...")
            await bypass_btn.click()
            await asyncio.sleep(5)
            await screenshot(page, "06-after-sandbox-bypass", page_key)
            results["steps"].append({"step": "sandbox_bypass", "status": "clicked"})
        else:
            print(f"  Sandbox bypass button NOT found")
            # Check if PayPal overlay appeared instead
            paypal_el = page.locator(".paypal-buttons, iframe[name*='paypal']")
            paypal_count = await paypal_el.count()
            print(f"  PayPal elements found: {paypal_count}")
            await screenshot(page, "06-no-sandbox-bypass", page_key)
            results["steps"].append({"step": "sandbox_bypass", "status": "not_found", "paypal_visible": paypal_count > 0})
    else:
        # For production page, we can't actually pay, so look at what we can see
        print(f"\n[Step 7] Production page - checking visible state after activate now")
        await asyncio.sleep(2)
        await screenshot(page, "06-production-state", page_key)
        results["steps"].append({"step": "post_payment_check", "status": "production_skipped"})

    # --- Step 8: Look for the post-payment chatbox and OAuth button ---
    print(f"\n[Step 8] Looking for post-payment chatbox and OAuth button")
    await asyncio.sleep(3)

    # Check if PTC wrapper is present
    ptc_wrapper = page.locator(".ptc-wrapper, #pay-test-post-payment")
    ptc_count = await ptc_wrapper.count()
    print(f"  PTC wrapper elements: {ptc_count}")

    # Comprehensive OAuth button search
    oauth_data = await page.evaluate("""() => {
        // Search for OAuth-related elements
        const allElements = document.querySelectorAll('*');
        let oauthButtons = [];
        let connectButtons = [];
        let allButtons = [];

        for (const el of allElements) {
            const text = (el.textContent || '').trim().toLowerCase();
            const id = el.id || '';
            const className = el.className || '';
            const href = el.href || '';
            const onclick = el.getAttribute('onclick') || '';

            // Check for OAuth-related buttons
            if (text.includes('oauth') || text.includes('connect with claude') ||
                text.includes('authenticate') || text.includes('authorize') ||
                id.includes('oauth') || className.includes('oauth') ||
                onclick.includes('oauth')) {
                oauthButtons.push({
                    tag: el.tagName,
                    id: el.id,
                    class: el.className,
                    text: el.textContent.trim().substring(0, 100),
                    href: el.href || '',
                    onclick: el.getAttribute('onclick') || '',
                    visible: el.offsetParent !== null || el.getBoundingClientRect().width > 0,
                    display: window.getComputedStyle(el).display,
                });
            }

            // Check for any button in ptc-wrapper
            if ((el.tagName === 'BUTTON' || el.tagName === 'A') &&
                (el.closest('.ptc-wrapper') || el.closest('#pay-test-post-payment'))) {
                allButtons.push({
                    tag: el.tagName,
                    id: el.id,
                    class: el.className,
                    text: el.textContent.trim().substring(0, 100),
                    href: el.href || '',
                    onclick: el.getAttribute('onclick') || '',
                    display: window.getComputedStyle(el).display,
                });
            }
        }

        // Also search all inline script content for oauth patterns
        const scripts = Array.from(document.querySelectorAll('script'));
        const oauthPatterns = [];
        for (const s of scripts) {
            if (s.src === '') {
                const text = s.textContent;
                // Find oauth function definitions
                const oauthFnMatch = text.match(/function\\s+(\\w*[Oo]auth\\w*)\\s*\\([^)]*\\)\\s*\\{[^}]{0,500}/g);
                if (oauthFnMatch) oauthPatterns.push(...oauthFnMatch.map(m => m.substring(0, 200)));

                // Find oauth button creation
                const oauthBtnMatch = text.match(/[Oo]auth[^;]{0,200}/g);
                if (oauthBtnMatch) {
                    for (const m of oauthBtnMatch.slice(0, 5)) {
                        oauthPatterns.push(m.substring(0, 200));
                    }
                }

                // Find /api/birth/start references
                const birthMatch = text.match(/\\/api\\/birth\\/start[^;'"]{0,100}/g);
                if (birthMatch) oauthPatterns.push(...birthMatch.map(m => 'API_BIRTH_START: ' + m));

                // Find Claude OAuth endpoint references
                const claudeOauthMatch = text.match(/claude\\.ai\\/oauth[^"'\\s]{0,100}/g);
                if (claudeOauthMatch) oauthPatterns.push(...claudeOauthMatch.map(m => 'CLAUDE_OAUTH: ' + m));
            }
        }

        return {
            oauthButtons: oauthButtons,
            ptcButtons: allButtons.slice(0, 20),
            oauthPatterns: [...new Set(oauthPatterns)].slice(0, 20),
            ptcWrapperExists: document.querySelector('.ptc-wrapper') !== null,
            ptcMessages: document.querySelectorAll('.ptc-msg--ai').length,
        };
    }""")

    print(f"  PTC wrapper in DOM: {oauth_data.get('ptcWrapperExists', False)}")
    print(f"  PTC AI messages: {oauth_data.get('ptcMessages', 0)}")
    print(f"  OAuth buttons found: {len(oauth_data.get('oauthButtons', []))}")

    for btn in oauth_data.get('oauthButtons', []):
        print(f"    OAuth btn: {btn}")

    print(f"  All PTC buttons: {len(oauth_data.get('ptcButtons', []))}")
    for btn in oauth_data.get('ptcButtons', [])[:5]:
        print(f"    PTC btn: {btn.get('tag')} | class={btn.get('class', '')[:50]} | text={btn.get('text', '')[:60]}")

    print(f"\n  OAuth patterns in scripts:")
    for pattern in oauth_data.get('oauthPatterns', [])[:10]:
        print(f"    {pattern[:200]}")

    results["oauth_button"] = oauth_data

    await screenshot(page, "07-ptc-state", page_key)

    # --- Step 9: Check network calls to /api/birth/start ---
    print(f"\n[Step 9] Attempting to manually call /api/birth/start to check response")
    birth_api_result = await page.evaluate("""async () => {
        try {
            const response = await fetch('/api/birth/start', {
                method: 'GET',
                headers: {'Accept': 'application/json'},
            });
            const text = await response.text();
            return {
                status: response.status,
                statusText: response.statusText,
                body: text.substring(0, 500),
                headers: Object.fromEntries([...response.headers.entries()].slice(0, 10)),
            };
        } catch(e) {
            return {error: e.message};
        }
    }""")
    print(f"  /api/birth/start GET response: {birth_api_result}")
    results["birth_api_check"] = birth_api_result

    # --- Step 10: Check if OAuth redirect URL is embedded in scripts ---
    print(f"\n[Step 10] Extracting OAuth URL details from scripts")
    oauth_url_data = await page.evaluate("""() => {
        const scripts = Array.from(document.querySelectorAll('script'));
        let findings = {
            oauth_start_url: null,
            claude_oauth_url: null,
            redirect_uri: null,
            client_id: null,
            state_param: null,
            api_birth_urls: [],
        };

        for (const s of scripts) {
            if (s.src !== '') continue;
            const text = s.textContent;

            // OAuth start URL patterns
            const oauthStartPatterns = [
                /oauth.*?start.*?['"]([^'"]+)['"]/gi,
                /['"]([^'"]*oauth[^'"]*)['"]/g,
                /window\.open\\(['"]([^'"]+oauth[^'"]*)['"]/g,
                /href\\s*=\\s*['"]([^'"]*oauth[^'"]*)['"]/g,
                /location.*?=.*?['"]([^'"]*oauth[^'"]*)['"]/g,
            ];

            for (const pattern of oauthStartPatterns) {
                let m;
                while ((m = pattern.exec(text)) !== null) {
                    if (m[1] && m[1].length > 5) {
                        findings.oauth_start_url = m[1];
                        break;
                    }
                }
            }

            // claude.ai OAuth URL
            const claudeMatch = text.match(/https:\/\/claude\.ai\/oauth[^\s"']+/);
            if (claudeMatch) findings.claude_oauth_url = claudeMatch[0];

            // Redirect URI
            const redirectMatch = text.match(/redirect_uri[=:]\s*['"]?([^'"&\s,)]+)/);
            if (redirectMatch) findings.redirect_uri = redirectMatch[1];

            // Client ID
            const clientMatch = text.match(/client_id[=:]\s*['"]?([^'"&\s,)]+)/);
            if (clientMatch) findings.client_id = clientMatch[1];

            // API birth URLs
            const birthMatches = text.match(/['"][^'"]*\/api\/birth[^'"]*['"]/g);
            if (birthMatches) findings.api_birth_urls.push(...birthMatches.map(m => m.replace(/['"]/g, '')));
        }

        findings.api_birth_urls = [...new Set(findings.api_birth_urls)];
        return findings;
    }""")
    print(f"  OAuth URL findings: {json.dumps(oauth_url_data, indent=2)}")
    results["oauth_url_data"] = oauth_url_data

    # --- Final: All console errors summary ---
    print(f"\n[Final] Console log summary for {page_key}")
    errors = [l for l in console_logs[page_key] if l["type"] == "error"]
    warnings = [l for l in console_logs[page_key] if l["type"] == "warning"]
    print(f"  Total console entries: {len(console_logs[page_key])}")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    for e in errors[:10]:
        print(f"    ERROR: {e['text'][:200]}")

    results["console_summary"] = {
        "total": len(console_logs[page_key]),
        "errors": errors[:20],
        "warnings": warnings[:10],
    }
    results["network_events"] = network_events[page_key]

    await screenshot(page, "08-final-state", page_key)
    await browser.close()
    return results


async def main():
    print(f"\nOAuth Button Diagnosis - {datetime.now().strftime('%Y-%02d-%Y %H:%M:%S')}")
    print(f"Screenshots: {SCREENSHOTS_DIR}")

    results = {}

    async with async_playwright() as playwright:
        # Test sandbox first
        print("\n\n### PHASE 1: SANDBOX PAGE ###")
        results["sandbox"] = await diagnose_page(playwright, "sandbox", PAGES["sandbox"])

        print(f"\nWaiting 20 seconds before loading production page (WAF avoidance)...")
        await asyncio.sleep(20)

        # Test production
        print("\n\n### PHASE 2: PRODUCTION PAGE ###")
        results["production"] = await diagnose_page(playwright, "production", PAGES["production"])

    # --- Comparison Report ---
    print("\n\n" + "="*60)
    print("COMPARISON REPORT")
    print("="*60)

    sandbox_scripts = results["sandbox"].get("script_version", {})
    prod_scripts = results["production"].get("script_version", {})

    print("\n[Script Sizes]")
    print(f"  Sandbox:    {sandbox_scripts.get('inlineScriptSizes', [])}")
    print(f"  Production: {prod_scripts.get('inlineScriptSizes', [])}")
    same_sizes = sandbox_scripts.get('inlineScriptSizes') == prod_scripts.get('inlineScriptSizes')
    print(f"  Same sizes? {same_sizes}")

    print("\n[Versions]")
    print(f"  Sandbox:    {sandbox_scripts.get('versions', [])}")
    print(f"  Production: {prod_scripts.get('versions', [])}")

    print("\n[Witness Hosts]")
    print(f"  Sandbox:    {sandbox_scripts.get('witnessHosts', [])}")
    print(f"  Production: {prod_scripts.get('witnessHosts', [])}")

    print("\n[OAuth URLs]")
    sandbox_oauth = results["sandbox"].get("oauth_url_data", {})
    prod_oauth = results["production"].get("oauth_url_data", {})
    print(f"  Sandbox claude_oauth_url: {sandbox_oauth.get('claude_oauth_url')}")
    print(f"  Prod claude_oauth_url:    {prod_oauth.get('claude_oauth_url')}")
    print(f"  Sandbox redirect_uri:     {sandbox_oauth.get('redirect_uri')}")
    print(f"  Prod redirect_uri:        {prod_oauth.get('redirect_uri')}")
    print(f"  Sandbox api_birth_urls:   {sandbox_oauth.get('api_birth_urls', [])}")
    print(f"  Prod api_birth_urls:      {prod_oauth.get('api_birth_urls', [])}")

    print("\n[/api/birth/start responses]")
    print(f"  Sandbox:    {results['sandbox'].get('birth_api_check')}")
    print(f"  Production: {results['production'].get('birth_api_check')}")

    print("\n[Console Errors]")
    sandbox_errors = results["sandbox"].get("console_summary", {}).get("errors", [])
    prod_errors = results["production"].get("console_summary", {}).get("errors", [])
    print(f"  Sandbox errors: {len(sandbox_errors)}")
    for e in sandbox_errors[:5]:
        print(f"    {e['text'][:150]}")
    print(f"  Production errors: {len(prod_errors)}")
    for e in prod_errors[:5]:
        print(f"    {e['text'][:150]}")

    print("\n[Network Events]")
    print(f"  Sandbox:    {len(results['sandbox'].get('network_events', []))} events")
    print(f"  Production: {len(results['production'].get('network_events', []))} events")

    # Save raw results
    output_path = f"{SCREENSHOTS_DIR}/oauth_diagnosis_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nRaw results saved to: {output_path}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
