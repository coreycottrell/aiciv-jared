#!/usr/bin/env python3
"""
Deploy purebrain-security plugin v4.6.7 via WordPress plugin editor.
Uses page.evaluate() to inject large file content directly into textarea.
Handles GoDaddy SSO login page (need to click "Log in with username and password" first).
"""

import asyncio
import sys
import os
import time

PLUGIN_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v466.php"
WP_LOGIN_URL = "https://purebrain.ai/wp-login.php"
PLUGIN_EDITOR_URL = "https://purebrain.ai/wp-admin/plugin-editor.php?plugin=purebrain-security%2Fpurebrain-security-plugin.php&Submit=Select"
WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"

async def deploy_plugin():
    from playwright.async_api import async_playwright

    # Read plugin content
    print(f"Reading plugin file: {PLUGIN_FILE}")
    with open(PLUGIN_FILE, 'r', encoding='utf-8') as f:
        plugin_content = f.read()
    print(f"Plugin content loaded: {len(plugin_content)} characters, {plugin_content.count(chr(10))} lines")

    # Verify version in content
    if "Version:     4.6.7" in plugin_content:
        print("Version 4.6.7 confirmed in plugin header.")
    else:
        print("WARNING: Could not find Version 4.6.7 in file header!")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        # Step 1: Navigate to login page
        print(f"\nNavigating to login page: {WP_LOGIN_URL}")
        await page.goto(WP_LOGIN_URL, wait_until="networkidle", timeout=30000)

        title = await page.title()
        print(f"Login page title: {title}")
        await page.screenshot(path="/tmp/plugin_deploy_01_login.png")

        # Check if GoDaddy SSO is shown - need to click "Log in with username and password"
        username_password_link = await page.query_selector("a:has-text('Log in with username and password')")
        if username_password_link:
            print("GoDaddy SSO detected. Clicking 'Log in with username and password'...")
            await username_password_link.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="/tmp/plugin_deploy_01b_after_sso_click.png")
            print("Screenshot saved: /tmp/plugin_deploy_01b_after_sso_click.png")

        # Now wait for the login form fields
        print("Waiting for login form fields...")
        await page.wait_for_selector("#user_login", state="visible", timeout=15000)

        # Fill login form
        await page.fill("#user_login", WP_USER)
        await page.fill("#user_pass", WP_PASS)
        print(f"Filled credentials: user={WP_USER}")

        await page.screenshot(path="/tmp/plugin_deploy_02_filled.png")
        print("Screenshot saved: /tmp/plugin_deploy_02_filled.png")

        # Click login button
        await page.click("#wp-submit")
        await page.wait_for_load_state("networkidle", timeout=30000)

        current_url = page.url
        print(f"After login, URL: {current_url}")
        await page.screenshot(path="/tmp/plugin_deploy_03_after_login.png")
        print("Screenshot saved: /tmp/plugin_deploy_03_after_login.png")

        if "wp-login.php" in current_url:
            print("ERROR: Still on login page. Login may have failed.")
            error_el = await page.query_selector(".notice-error, #login_error")
            if error_el:
                error_text = await error_el.text_content()
                print(f"Error message: {error_text}")
            await browser.close()
            return False

        print("Login successful!")

        # Step 2: Navigate to plugin editor
        print(f"\nNavigating to plugin editor: {PLUGIN_EDITOR_URL}")
        await page.goto(PLUGIN_EDITOR_URL, wait_until="networkidle", timeout=30000)

        current_url = page.url
        print(f"Plugin editor URL: {current_url}")
        await page.screenshot(path="/tmp/plugin_deploy_04_editor.png")
        print("Screenshot saved: /tmp/plugin_deploy_04_editor.png")

        # Check if editor loaded
        textarea = await page.query_selector("#newcontent")
        if not textarea:
            print("ERROR: Plugin editor textarea #newcontent not found!")
            # Check if there's a warning/error
            body_text = await page.text_content("body")
            print(f"Page content (first 800 chars): {body_text[:800]}")
            await browser.close()
            return False

        print("Plugin editor textarea found!")

        # Get current content to verify we have the right file
        current_content = await page.evaluate("document.getElementById('newcontent').value")
        if "PureBrain Security" in current_content:
            print("Current file is the correct plugin.")
            for line in current_content.split('\n')[:15]:
                if 'Version:' in line:
                    print(f"Current version in editor: {line.strip()}")
                    break
        else:
            print(f"WARNING: Editor may not have the right file. First 300 chars:\n{current_content[:300]}")

        # Step 3: Check for CodeMirror (WP plugin editor usually uses it)
        cm_present = await page.evaluate("typeof CodeMirror !== 'undefined'")
        print(f"\nCodeMirror present: {cm_present}")

        if cm_present:
            print("CodeMirror detected - injecting via CM instance...")
            cm_result = await page.evaluate("""
                (content) => {
                    try {
                        // Try all CodeMirror instances
                        const cmEls = document.querySelectorAll('.CodeMirror');
                        for (let el of cmEls) {
                            if (el.CodeMirror) {
                                el.CodeMirror.setValue(content);
                                // Also sync the underlying textarea
                                const ta = document.getElementById('newcontent');
                                if (ta) {
                                    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                                    setter.call(ta, content);
                                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                                }
                                return 'CodeMirror updated: ' + el.CodeMirror.getValue().length + ' chars';
                            }
                        }
                        return 'No .CodeMirror instance found, tried ' + cmEls.length + ' elements';
                    } catch(e) {
                        return 'Error: ' + e.message;
                    }
                }
            """, plugin_content)
            print(f"CodeMirror result: {cm_result}")
        else:
            # No CodeMirror - inject directly into textarea
            print("No CodeMirror - injecting directly into textarea...")
            inject_result = await page.evaluate("""
                (content) => {
                    const textarea = document.getElementById('newcontent');
                    if (!textarea) return 'textarea not found';
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                    setter.call(textarea, content);
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    textarea.dispatchEvent(new Event('change', { bubbles: true }));
                    return textarea.value.length + ' chars set';
                }
            """, plugin_content)
            print(f"Textarea inject result: {inject_result}")

        # Verify the content was set
        verify_length = await page.evaluate("""
            () => {
                const ta = document.getElementById('newcontent');
                return ta ? ta.value.length : -1;
            }
        """)
        print(f"Textarea length after inject: {verify_length} (expected {len(plugin_content)})")

        await page.screenshot(path="/tmp/plugin_deploy_05_content_set.png")
        print("Screenshot saved: /tmp/plugin_deploy_05_content_set.png")

        # Step 4: Submit the form
        print("\nSubmitting the plugin editor form (Update File)...")

        # Find submit button
        update_btn = await page.query_selector("#submit")
        if update_btn:
            btn_value = await update_btn.get_attribute("value") or "submit"
            print(f"Found #submit button: '{btn_value}'")
        else:
            update_btn = await page.query_selector("input[type='submit'][name='submit']")
            if update_btn:
                btn_value = await update_btn.get_attribute("value") or "submit"
                print(f"Found submit input: '{btn_value}'")
            else:
                print("No submit button found, trying JS form submit...")

        if update_btn:
            await update_btn.click()
        else:
            await page.evaluate("document.getElementById('template').submit()")

        await page.wait_for_load_state("networkidle", timeout=30000)

        current_url = page.url
        print(f"After submit, URL: {current_url}")
        await page.screenshot(path="/tmp/plugin_deploy_06_after_submit.png")
        print("Screenshot saved: /tmp/plugin_deploy_06_after_submit.png")

        # Step 5: Check for success message
        page_text = await page.text_content("body")

        # Look for WP success notice
        success_el = await page.query_selector(".updated, .notice-success")
        error_el = await page.query_selector(".notice-error, .error")

        if success_el:
            success_text = await success_el.text_content()
            print(f"\nSUCCESS notice found: {success_text.strip()}")
        elif error_el:
            error_text = await error_el.text_content()
            print(f"\nERROR notice found: {error_text.strip()}")
        else:
            # Search for known success text
            if "File edited successfully" in page_text:
                print("\nSUCCESS: 'File edited successfully' text found in page!")
            elif "parse error" in page_text.lower() or "syntax error" in page_text.lower():
                print("\nERROR: PHP parse/syntax error detected!")
                for line in page_text.split('\n'):
                    if 'error' in line.lower():
                        print(f"  {line.strip()}")
            else:
                print("\nNo clear success/error notice found.")

        # Step 6: Verify by re-reading the editor
        print("\nVerifying deployment by re-loading plugin editor...")
        await page.goto(PLUGIN_EDITOR_URL, wait_until="networkidle", timeout=30000)
        await page.screenshot(path="/tmp/plugin_deploy_07_verify.png")
        print("Screenshot saved: /tmp/plugin_deploy_07_verify.png")

        verify_content = await page.evaluate("""
            () => {
                const ta = document.getElementById('newcontent');
                return ta ? ta.value.substring(0, 500) : 'textarea not found';
            }
        """)

        print(f"\nVerification - first 300 chars of deployed plugin:\n{verify_content[:300]}")

        if "4.6.7" in verify_content:
            print("\nVERIFIED: Version 4.6.7 found in deployed plugin!")
            deploy_result = True
        else:
            print("\nWARNING: Version 4.6.7 NOT confirmed in editor post-deployment.")
            deploy_result = False

        await browser.close()
        return deploy_result

if __name__ == "__main__":
    result = asyncio.run(deploy_plugin())
    if result:
        print("\n=== DEPLOYMENT SUCCESSFUL: v4.6.7 is live on purebrain.ai ===")
        sys.exit(0)
    else:
        print("\n=== DEPLOYMENT FAILED or UNVERIFIED ===")
        sys.exit(1)
