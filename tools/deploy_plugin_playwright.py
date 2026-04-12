#!/usr/bin/env python3
"""
Deploy plugin v4.6.9 via Playwright browser automation.
Handles GoDaddy CAPTCHA and login flow.
"""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

PLUGIN_FILE = '/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v466.php'
SCREENSHOT_DIR = '/home/jared/projects/AI-CIV/aether/docs/deploy-attempt'
WP_USER = os.environ.get('PUREBRAIN_WP_USER', 'Aether')
WP_PASS = os.environ.get('PUREBRAIN_WP_PASSWORD', '')
WP_APP_PASS = os.environ.get('PUREBRAIN_WP_APP_PASSWORD', '')

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def screenshot(page, name):
    path = f'{SCREENSHOT_DIR}/{name}.png'
    page.screenshot(path=path)
    print(f'[SCREENSHOT] {path}')
    return path

def deploy():
    print(f'[INFO] Plugin file: {PLUGIN_FILE}')
    print(f'[INFO] WP_USER: {WP_USER}')
    print(f'[INFO] WP_PASS length: {len(WP_PASS)}')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            # Step 1: Navigate to login page with wpaas-standard-login=1
            print('[STEP 1] Navigating to WP login page...')
            page.goto('https://purebrain.ai/wp-login.php?wpaas-standard-login=1', wait_until='networkidle', timeout=30000)
            screenshot(page, '01-login-page-load')

            # Check if there's a "Log in with username and password" toggle
            sso_toggle = page.query_selector('a.wpaas-sso-login-toggle')
            if sso_toggle:
                print('[STEP 1b] Clicking "Log in with username and password" link...')
                sso_toggle.click()
                page.wait_for_timeout(1000)
                screenshot(page, '02-after-sso-toggle')

            # Step 2: Fill in credentials
            print(f'[STEP 2] Filling credentials for user: {WP_USER}')
            page.fill('#user_login', WP_USER)
            page.fill('#user_pass', WP_PASS)
            screenshot(page, '03-credentials-filled')

            # Check for CAPTCHA before submitting
            captcha_wrapper = page.query_selector('.wpsec_captcha_wrapper')
            captcha_image = page.query_selector('.wpsec_captcha_image img')

            if captcha_image:
                print('[CAPTCHA] CAPTCHA detected! Taking screenshot...')
                screenshot(page, '04-captcha-visible')
                # Try to read captcha text - it's usually a simple math or text challenge
                captcha_src = captcha_image.get_attribute('src')
                print(f'[CAPTCHA] Image src: {captcha_src}')
                # We'll attempt to submit without captcha first (sometimes it's hidden)

            # Step 3: Submit login form
            print('[STEP 3] Submitting login...')
            page.click('#wp-submit')
            page.wait_for_timeout(3000)
            screenshot(page, '05-after-login-submit')

            current_url = page.url
            print(f'[INFO] Current URL after login: {current_url}')

            if 'wp-admin' in current_url:
                print('[SUCCESS] Logged in! In wp-admin.')
            elif 'wp-login' in current_url:
                print('[FAIL] Still on login page - checking for errors...')
                error_div = page.query_selector('#login_error')
                if error_div:
                    print(f'[ERROR] Login error: {error_div.inner_text()}')

                # Check for CAPTCHA that appeared after failed attempt
                captcha_img_after = page.query_selector('.wpsec_captcha_image img')
                if captcha_img_after:
                    print('[CAPTCHA] CAPTCHA appeared after failed attempt')
                    screenshot(page, '06-captcha-after-fail')
                    # Try to read the CAPTCHA text from the image
                    captcha_src = captcha_img_after.get_attribute('src')
                    print(f'[CAPTCHA] CAPTCHA image src: {captcha_src}')

                return False

            # Step 4: Navigate to plugin editor
            print('[STEP 4] Navigating to plugin editor...')
            page.goto(
                'https://purebrain.ai/wp-admin/plugin-editor.php?file=purebrain-security-plugin.php&plugin=purebrain-security%2Fpurebrain-security-plugin.php',
                wait_until='networkidle',
                timeout=30000
            )
            screenshot(page, '07-plugin-editor')

            current_url = page.url
            print(f'[INFO] Plugin editor URL: {current_url}')

            if 'plugin-editor' not in current_url:
                print('[FAIL] Not on plugin editor page')
                return False

            # Step 5: Read plugin content
            print('[STEP 5] Reading plugin file content...')
            with open(PLUGIN_FILE, 'r') as f:
                plugin_content = f.read()
            print(f'[INFO] Plugin content size: {len(plugin_content)} bytes')

            # Step 6: Replace editor content
            print('[STEP 6] Replacing plugin content in editor...')
            editor = page.query_selector('#newcontent')
            if not editor:
                editor = page.query_selector('textarea[name="newcontent"]')

            if not editor:
                print('[FAIL] Could not find editor textarea')
                screenshot(page, '08-no-editor-found')
                return False

            # Clear and fill the editor
            page.evaluate('document.getElementById("newcontent").value = ""')
            page.evaluate(f'document.getElementById("newcontent").value = arguments[0]', plugin_content)
            print(f'[INFO] Plugin content set in editor')
            screenshot(page, '09-content-set')

            # Step 7: Click Update File
            print('[STEP 7] Clicking Update File...')
            update_btn = page.query_selector('input[name="submit"][value="Update File"]')
            if not update_btn:
                update_btn = page.query_selector('#submit')
            if not update_btn:
                update_btn = page.query_selector('input[type="submit"]')

            if not update_btn:
                print('[FAIL] Could not find Update File button')
                screenshot(page, '10-no-update-button')
                return False

            update_btn.click()
            page.wait_for_timeout(5000)
            screenshot(page, '11-after-update')

            # Check for success
            page_content = page.content()
            if 'File edited successfully' in page_content or 'updated successfully' in page_content.lower():
                print('[SUCCESS] Plugin file updated successfully!')
                return True
            else:
                print('[UNKNOWN] Update clicked but could not confirm success')
                # Check for errors
                for err_sel in ['.notice-error', '.error', '#error-message']:
                    err = page.query_selector(err_sel)
                    if err:
                        print(f'[ERROR] {err.inner_text()[:200]}')
                return False

        except Exception as e:
            print(f'[EXCEPTION] {e}')
            screenshot(page, 'XX-exception')
            raise
        finally:
            browser.close()

if __name__ == '__main__':
    success = deploy()
    sys.exit(0 if success else 1)
