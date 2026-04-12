"""
cc.purebrain.ai Diagnostic Script
Date: 2026-02-28
Purpose: Login, audit dashboard tabs, capture console errors, screenshot all states
"""
import asyncio
import json
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/cc-diagnostic-20260228"
REPORT_PATH = "/home/jared/projects/AI-CIV/aether/exports/cc-diagnostic-report-20260228.md"

URL = "https://cc.purebrain.ai/auth/login"
NAME = "Jared Sanborn"
EMAIL = "jared@puretechnology.nyc"
PASSWORD = "puretech2026"

console_logs = []
console_errors = []
console_warnings = []
network_errors = []

def capture_console(msg):
    entry = {
        "type": msg.type,
        "text": msg.text,
        "time": time.strftime("%H:%M:%S")
    }
    console_logs.append(entry)
    if msg.type == "error":
        console_errors.append(entry)
        print(f"[CONSOLE ERROR] {msg.text}")
    elif msg.type == "warning":
        console_warnings.append(entry)
        print(f"[CONSOLE WARN] {msg.text}")

def capture_network_error(request):
    network_errors.append({
        "url": request.url,
        "time": time.strftime("%H:%M:%S")
    })

async def screenshot(page, name, label):
    path = f"{SCREENSHOT_DIR}/{name}.png"
    await page.screenshot(path=path, full_page=True)
    print(f"[SCREENSHOT] {label} -> {name}.png")
    return path

async def wait_and_check(page, ms=2000):
    await page.wait_for_timeout(ms)

async def run_diagnostic():
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        # Attach console listener
        page.on("console", capture_console)
        page.on("requestfailed", lambda req: network_errors.append({"url": req.url, "failure": req.failure, "time": time.strftime("%H:%M:%S")}))

        results = {}

        # STEP 1: Navigate to login page
        print("\n=== STEP 1: Navigate to Login Page ===")
        try:
            response = await page.goto(URL, wait_until="networkidle", timeout=30000)
            results["login_page_status"] = response.status if response else "unknown"
            print(f"HTTP Status: {response.status if response else 'unknown'}")
        except Exception as e:
            print(f"Navigation error: {e}")
            results["login_page_status"] = f"ERROR: {e}"

        await wait_and_check(page, 2000)
        await screenshot(page, "001-login-page", "Login page initial state")

        # Get page title and URL
        results["login_page_title"] = await page.title()
        results["login_page_url"] = page.url
        print(f"Title: {results['login_page_title']}")
        print(f"URL: {results['login_page_url']}")

        # STEP 2: Inspect login form fields
        print("\n=== STEP 2: Inspect Form Fields ===")

        # Check for Name field
        name_selectors = [
            'input[name="name"]',
            'input[placeholder*="name" i]',
            'input[placeholder*="Name"]',
            'input[type="text"]:first-of-type',
            '#name',
            'label:has-text("Name") + input',
            'label:has-text("Name") ~ input',
        ]
        name_field = None
        for sel in name_selectors:
            try:
                el = page.locator(sel).first
                count = await el.count()
                if count > 0:
                    is_visible = await el.is_visible()
                    if is_visible:
                        name_field = sel
                        print(f"Name field found: {sel}")
                        break
            except:
                pass

        if not name_field:
            print("WARNING: Name field not found by standard selectors")
            # Try to inspect all inputs
            inputs = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input')).map(el => ({
                    type: el.type,
                    name: el.name,
                    id: el.id,
                    placeholder: el.placeholder,
                    'aria-label': el.getAttribute('aria-label'),
                    class: el.className
                }));
            }""")
            print(f"All inputs on page: {json.dumps(inputs, indent=2)}")
            results["all_inputs"] = inputs

        # Check for Email field
        email_selectors = [
            'input[name="email"]',
            'input[type="email"]',
            'input[placeholder*="email" i]',
            '#email',
        ]
        email_field = None
        for sel in email_selectors:
            try:
                el = page.locator(sel).first
                count = await el.count()
                if count > 0:
                    is_visible = await el.is_visible()
                    if is_visible:
                        email_field = sel
                        print(f"Email field found: {sel}")
                        break
            except:
                pass

        # Check for Password field
        password_field = None
        try:
            el = page.locator('input[type="password"]').first
            count = await el.count()
            if count > 0 and await el.is_visible():
                password_field = 'input[type="password"]'
                print(f"Password field found: {password_field}")
        except:
            pass

        results["fields"] = {
            "name": name_field,
            "email": email_field,
            "password": password_field
        }

        # STEP 3: Fill and submit the login form
        print("\n=== STEP 3: Fill Login Form ===")

        login_attempted = False
        login_success = False

        try:
            # Clear console log buffer before login to track login-specific errors
            pre_login_error_count = len(console_errors)

            # Fill Name field
            if name_field:
                await page.fill(name_field, NAME)
                print(f"Filled name: {NAME}")
            else:
                # Try to fill first text input
                try:
                    all_text_inputs = page.locator('input[type="text"], input:not([type])')
                    count = await all_text_inputs.count()
                    print(f"Found {count} text inputs, trying first")
                    if count > 0:
                        await all_text_inputs.first.fill(NAME)
                        print(f"Filled first text input with: {NAME}")
                except Exception as e:
                    print(f"Could not fill name: {e}")

            # Fill Email field
            if email_field:
                await page.fill(email_field, EMAIL)
                print(f"Filled email: {EMAIL}")

            # Fill Password field
            if password_field:
                await page.fill(password_field, PASSWORD)
                print(f"Filled password: ****")

            await wait_and_check(page, 500)
            await screenshot(page, "002-form-filled", "Login form filled (before submit)")

            # Find and click submit button
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'button:has-text("Continue")',
                'input[type="submit"]',
            ]

            submit_btn = None
            for sel in submit_selectors:
                try:
                    el = page.locator(sel).first
                    count = await el.count()
                    if count > 0 and await el.is_visible():
                        submit_btn = sel
                        print(f"Submit button found: {sel}")
                        break
                except:
                    pass

            if submit_btn:
                login_attempted = True
                await page.click(submit_btn)
                print("Clicked submit button")

                # Wait for navigation or response
                try:
                    await page.wait_for_load_state("networkidle", timeout=15000)
                except Exception as e:
                    print(f"Network idle timeout (may be ok): {e}")

                await wait_and_check(page, 3000)

                current_url = page.url
                results["post_login_url"] = current_url
                print(f"Post-login URL: {current_url}")

                if current_url != URL and "login" not in current_url.lower():
                    login_success = True
                    print("LOGIN SUCCESS: URL changed from login page")
                elif "dashboard" in current_url.lower() or "cc.purebrain.ai/" == current_url or current_url.rstrip("/") == "https://cc.purebrain.ai":
                    login_success = True
                    print("LOGIN SUCCESS: Redirected to dashboard")
                else:
                    print(f"LOGIN STATUS UNCLEAR: URL is {current_url}")

            else:
                print("ERROR: No submit button found")
                # Log all buttons
                buttons = await page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('button')).map(el => ({
                        text: el.textContent.trim(),
                        type: el.type,
                        class: el.className
                    }));
                }""")
                print(f"All buttons: {json.dumps(buttons, indent=2)}")
                results["all_buttons"] = buttons

        except Exception as e:
            print(f"Login form error: {e}")
            results["login_error"] = str(e)

        results["login_attempted"] = login_attempted
        results["login_success"] = login_success

        await screenshot(page, "003-post-login", "State after login attempt")

        # STEP 4: Check dashboard content
        print("\n=== STEP 4: Analyze Dashboard State ===")

        # Get page title and check for dashboard elements
        results["post_login_title"] = await page.title()
        results["post_login_url_final"] = page.url

        # Check for common dashboard elements
        dashboard_checks = {
            "main_content": 'main, #main, .main, [role="main"]',
            "dashboard_heading": 'h1, h2, .dashboard, .welcome',
            "nav_tabs": 'nav, [role="navigation"], .tabs, .tab',
            "tasks_tab": 'a:has-text("Tasks"), button:has-text("Tasks"), [data-tab="tasks"]',
            "team_tab": 'a:has-text("Team"), button:has-text("Team"), [data-tab="team"]',
            "calendar_tab": 'a:has-text("Calendar"), button:has-text("Calendar"), [data-tab="calendar"]',
            "email_tab": 'a:has-text("Email"), button:has-text("Email"), [data-tab="email"]',
            "error_message": '.error, .alert-error, [role="alert"]',
            "loading_spinner": '.loading, .spinner, .loader',
        }

        results["dashboard_elements"] = {}
        for name, selector in dashboard_checks.items():
            try:
                el = page.locator(selector).first
                count = await el.count()
                visible = await el.is_visible() if count > 0 else False
                text = ""
                if count > 0 and visible:
                    try:
                        text = (await el.text_content() or "").strip()[:100]
                    except:
                        pass
                results["dashboard_elements"][name] = {
                    "found": count > 0,
                    "visible": visible,
                    "text": text
                }
                if count > 0:
                    print(f"  {name}: found={count}, visible={visible}, text='{text[:50]}'")
            except Exception as e:
                results["dashboard_elements"][name] = {"error": str(e)}

        # Get page HTML structure overview
        page_structure = await page.evaluate("""() => {
            const body = document.body;
            if (!body) return "no body";
            return Array.from(body.children).map(el => ({
                tag: el.tagName,
                id: el.id,
                class: el.className.substring(0, 80),
                children: el.children.length
            }));
        }""")
        results["page_structure"] = page_structure
        print(f"\nPage structure: {json.dumps(page_structure, indent=2)}")

        # STEP 5: Test each tab
        print("\n=== STEP 5: Test Dashboard Tabs ===")

        tabs_to_test = ["Tasks", "Team", "Calendar", "Email"]
        tab_results = {}

        for tab_name in tabs_to_test:
            print(f"\n--- Testing tab: {tab_name} ---")
            tab_results[tab_name] = {"clicked": False, "content": "", "error": None}

            # Try various selectors for tab
            tab_selectors = [
                f'a:has-text("{tab_name}")',
                f'button:has-text("{tab_name}")',
                f'[role="tab"]:has-text("{tab_name}")',
                f'li:has-text("{tab_name}")',
                f'[data-tab="{tab_name.lower()}"]',
                f'.tab:has-text("{tab_name}")',
                f'nav a:has-text("{tab_name}")',
            ]

            tab_clicked = False
            for sel in tab_selectors:
                try:
                    el = page.locator(sel).first
                    count = await el.count()
                    if count > 0 and await el.is_visible():
                        await el.click()
                        tab_clicked = True
                        tab_results[tab_name]["clicked"] = True
                        print(f"  Clicked tab via: {sel}")
                        break
                except Exception as e:
                    pass

            if not tab_clicked:
                print(f"  WARNING: Could not find/click {tab_name} tab")
                tab_results[tab_name]["error"] = "Tab not found"

            await wait_and_check(page, 2000)

            # Capture tab content
            try:
                main_content = page.locator('main, #main, .main, [role="main"], .content, #content').first
                content_count = await main_content.count()
                if content_count > 0:
                    tab_text = (await main_content.text_content() or "").strip()[:300]
                    tab_results[tab_name]["content"] = tab_text
                    print(f"  Content: {tab_text[:100]}")
                else:
                    # Get body text
                    body_text = (await page.locator("body").text_content() or "").strip()[:200]
                    tab_results[tab_name]["content"] = body_text
            except Exception as e:
                tab_results[tab_name]["error"] = str(e)

            safe_tab = tab_name.lower()
            await screenshot(page, f"00{tabs_to_test.index(tab_name)+4}-tab-{safe_tab}", f"{tab_name} tab content")

        results["tabs"] = tab_results

        # STEP 6: Final console log capture
        print("\n=== STEP 6: Console Log Summary ===")
        print(f"Total console messages: {len(console_logs)}")
        print(f"Errors: {len(console_errors)}")
        print(f"Warnings: {len(console_warnings)}")
        print(f"Network failures: {len(network_errors)}")

        for err in console_errors:
            print(f"  [ERROR] {err['text'][:200]}")
        for warn in console_warnings:
            print(f"  [WARN] {warn['text'][:200]}")
        for net in network_errors:
            print(f"  [NET FAIL] {net['url'][:200]}")

        # Final screenshot
        await screenshot(page, "009-final-state", "Final state before close")

        await context.close()
        await browser.close()

        # Build report
        results["console_errors"] = console_errors
        results["console_warnings"] = console_warnings
        results["console_all"] = console_logs
        results["network_errors"] = network_errors

        return results

def main():
    results = asyncio.run(run_diagnostic())

    # Write JSON report
    json_path = REPORT_PATH.replace(".md", ".json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[REPORT] JSON saved: {json_path}")

    # Write Markdown report
    with open(REPORT_PATH, "w") as f:
        f.write("# cc.purebrain.ai Diagnostic Report\n\n")
        f.write(f"**Date**: 2026-02-28\n")
        f.write(f"**URL**: https://cc.purebrain.ai/auth/login\n")
        f.write(f"**Credentials**: {EMAIL}\n\n")
        f.write("---\n\n")

        f.write("## Login Result\n\n")
        f.write(f"- HTTP Status: {results.get('login_page_status')}\n")
        f.write(f"- Login Attempted: {results.get('login_attempted')}\n")
        f.write(f"- Login Success: {results.get('login_success')}\n")
        f.write(f"- Post-Login URL: {results.get('post_login_url', 'N/A')}\n")
        f.write(f"- Page Title: {results.get('post_login_title', 'N/A')}\n\n")

        f.write("## Form Fields Detected\n\n")
        fields = results.get("fields", {})
        f.write(f"- Name field: `{fields.get('name', 'NOT FOUND')}`\n")
        f.write(f"- Email field: `{fields.get('email', 'NOT FOUND')}`\n")
        f.write(f"- Password field: `{fields.get('password', 'NOT FOUND')}`\n\n")

        f.write("## Dashboard Elements\n\n")
        for elem, data in results.get("dashboard_elements", {}).items():
            f.write(f"- {elem}: found={data.get('found')}, visible={data.get('visible')}, text='{data.get('text', '')[:60]}'\n")

        f.write("\n## Tab Testing Results\n\n")
        for tab, data in results.get("tabs", {}).items():
            f.write(f"### {tab}\n")
            f.write(f"- Clicked: {data.get('clicked')}\n")
            f.write(f"- Content preview: {data.get('content', '')[:150]}\n")
            if data.get('error'):
                f.write(f"- Error: {data.get('error')}\n")
            f.write("\n")

        f.write("## Console Errors\n\n")
        errors = results.get("console_errors", [])
        if errors:
            for e in errors:
                f.write(f"- [{e['time']}] `{e['text'][:200]}`\n")
        else:
            f.write("No console errors detected.\n")

        f.write("\n## Console Warnings\n\n")
        warnings = results.get("console_warnings", [])
        if warnings:
            for w in warnings:
                f.write(f"- [{w['time']}] `{w['text'][:200]}`\n")
        else:
            f.write("No console warnings detected.\n")

        f.write("\n## Network Errors\n\n")
        net_errs = results.get("network_errors", [])
        if net_errs:
            for n in net_errs:
                f.write(f"- [{n.get('time')}] `{n.get('url', '')}` — {n.get('failure', n.get('error', ''))}\n")
        else:
            f.write("No network errors detected.\n")

        f.write("\n## All Console Messages\n\n")
        for msg in results.get("console_all", []):
            f.write(f"- [{msg['time']}] [{msg['type'].upper()}] {msg['text'][:200]}\n")

    print(f"[REPORT] Markdown saved: {REPORT_PATH}")
    print(f"[SCREENSHOTS] Dir: {SCREENSHOT_DIR}")

    return results

if __name__ == "__main__":
    main()
