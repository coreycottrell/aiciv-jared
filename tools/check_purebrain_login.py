#!/usr/bin/env python3
"""Quick login check for PureBrain WordPress"""

import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

USERNAME = os.getenv('PUREBRAIN_WP_USER', 'Aether')
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '').strip("'\"")
SHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/login-check"

def main():
    import pathlib
    pathlib.Path(SHOT_DIR).mkdir(parents=True, exist_ok=True)

    print(f"User: {USERNAME}")
    print(f"Pass: {PASSWORD[:4]}...{PASSWORD[-4:]}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        print("\n1. Going to wp-admin...")
        page.goto("https://purebrain.ai/wp-admin", wait_until='load', timeout=60000)
        page.screenshot(path=f"{SHOT_DIR}/01_initial.png")
        print(f"   URL: {page.url}")

        print("\n2. Checking for GoDaddy SSO...")
        link = page.query_selector('text="Log in with username and password"')
        if link:
            print("   Found SSO, clicking...")
            link.click()
            time.sleep(2)
            page.screenshot(path=f"{SHOT_DIR}/02_after_sso_click.png")

        print("\n3. Looking for login form...")
        user_input = page.query_selector('#user_login')
        pass_input = page.query_selector('#user_pass')
        submit_btn = page.query_selector('#wp-submit')

        print(f"   user_login: {user_input is not None}")
        print(f"   user_pass: {pass_input is not None}")
        print(f"   wp-submit: {submit_btn is not None}")

        if user_input and pass_input:
            print("\n4. Filling credentials...")
            page.fill('#user_login', USERNAME)
            page.fill('#user_pass', PASSWORD)
            page.screenshot(path=f"{SHOT_DIR}/03_filled.png")

            print("\n5. Submitting...")
            page.click('#wp-submit')
            time.sleep(8)
            page.screenshot(path=f"{SHOT_DIR}/04_after_submit.png")

            print(f"\n6. Final URL: {page.url}")

            # Check result
            if 'wp-admin' in page.url and 'wp-login' not in page.url:
                print("   SUCCESS! Logged in.")
            else:
                error = page.query_selector('#login_error')
                if error:
                    print(f"   LOGIN ERROR: {error.inner_text()}")
                else:
                    print("   UNKNOWN STATE")

        browser.close()

if __name__ == "__main__":
    main()
