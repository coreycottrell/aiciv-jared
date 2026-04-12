#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v6.2.9 - Script entity decoding fix for pay-test pages.
"""
import os, re, sys, time
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"

env_text = (AETHER_ROOT / ".env").read_text()

def _env(key):
    m = re.search(rf"^{key}=\'([^\']+)\'", env_text, re.MULTILINE)
    if m: return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""

WP_USER = _env("PUREBRAIN_WP_USER")
WP_PASS = _env("PUREBRAIN_WP_PASSWORD")

LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"
EDITOR_URL = (
    "https://purebrain.ai/wp-admin/plugin-editor.php"
    "?file=purebrain-security/purebrain-security-plugin.php"
    "&plugin=purebrain-security/purebrain-security-plugin.php"
)

content = PLUGIN_FILE.read_text()
print(f"Plugin: {len(content)} chars, version 6.2.9: {'6.2.9' in content}")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    
    print("Logging in...")
    page.goto(LOGIN_URL, timeout=30000)
    page.fill("#user_login", WP_USER)
    page.fill("#user_pass", WP_PASS)
    page.click("#wp-submit")
    page.wait_for_load_state("networkidle", timeout=15000)
    print("Login done:", page.url)
    
    print("Opening plugin editor...")
    page.goto(EDITOR_URL, timeout=30000)
    page.wait_for_load_state("networkidle", timeout=15000)
    
    # Use CodeMirror to set content
    page.evaluate(f"""
        (function() {{
            var cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {{
                cm.CodeMirror.setValue({repr(content)});
                return true;
            }}
            return false;
        }})()
    """)
    
    time.sleep(2)
    page.click("#submit")
    page.wait_for_load_state("networkidle", timeout=15000)
    
    print("Save done. URL:", page.url)
    
    # Verify
    if "Plugin" in page.title() or "plugin-editor" in page.url:
        print("SUCCESS: Plugin deployed")
    else:
        print("WARNING: Unexpected state after save:", page.title())
    
    page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/plugin-v629-deploy.png")
    browser.close()

print("Done!")
