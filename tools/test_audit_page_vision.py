#!/usr/bin/env python3
"""
Visual verification of https://purebrain.ai/ai-partnership-audit/
Takes screenshots at desktop and mobile viewports, scrolled to key sections.
Single browser instance to avoid GoDaddy WAF rate limiting.
"""

import time
import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
PREFIX = "audit_page_verify_"
URL = "https://purebrain.ai/ai-partnership-audit/"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_screenshot(page, name, description=""):
    path = os.path.join(OUTPUT_DIR, f"{PREFIX}{name}.png")
    page.screenshot(path=path, full_page=False)
    print(f"  [SAVED] {path} - {description}")
    return path

def get_page_height(page):
    return page.evaluate("() => document.body.scrollHeight")

def scroll_to_percent(page, percent):
    height = get_page_height(page)
    y = int(height * percent / 100)
    page.evaluate(f"window.scrollTo(0, {y})")
    time.sleep(1.5)

def scroll_to_bottom(page):
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1.5)

def check_background_color(page):
    """Check if the page has the dark background (not orange/default)"""
    bg = page.evaluate("""() => {
        const body = document.body;
        const computed = window.getComputedStyle(body);
        return {
            bodyBg: computed.backgroundColor,
            htmlBg: window.getComputedStyle(document.documentElement).backgroundColor,
            firstSection: (() => {
                const el = document.querySelector('section, .elementor-section, main, #pb-audit-page, .e-con');
                return el ? window.getComputedStyle(el).backgroundColor : 'none found';
            })()
        };
    }""")
    return bg

def check_cta_buttons(page):
    """Check visibility and styling of CTA buttons"""
    btns = page.evaluate("""() => {
        const buttons = document.querySelectorAll('a.elementor-button, button, .elementor-button-wrapper a, input[type=submit]');
        return Array.from(buttons).slice(0, 10).map(b => ({
            text: b.textContent.trim().substring(0, 60),
            visible: b.offsetParent !== null,
            bg: window.getComputedStyle(b).backgroundColor,
            color: window.getComputedStyle(b).color,
            tagName: b.tagName
        }));
    }""")
    return btns

def check_form_elements(page):
    """Check for form/interactive elements"""
    forms = page.evaluate("""() => {
        const inputs = document.querySelectorAll('input, textarea, select');
        return Array.from(inputs).slice(0, 10).map(i => ({
            type: i.type || i.tagName,
            name: i.name || i.id || '',
            visible: i.offsetParent !== null,
            placeholder: i.placeholder || ''
        }));
    }""")
    return forms

def check_console_errors(page):
    """Return collected console errors"""
    return []

results = []
console_errors = []

with sync_playwright() as p:
    print("\n=== Launching browser ===")
    browser = p.chromium.launch(headless=True)

    # ---- DESKTOP 1440px ----
    print("\n--- DESKTOP 1440px ---")
    ctx_desktop = browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )
    page_desktop = ctx_desktop.new_page()

    # Collect console errors
    page_desktop.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)

    print(f"  Navigating to {URL}...")
    page_desktop.goto(URL, wait_until="networkidle", timeout=30000)
    time.sleep(2)

    # Check if redirected or blocked
    current_url = page_desktop.url
    print(f"  Current URL: {current_url}")

    # Check background color
    bg_info = check_background_color(page_desktop)
    print(f"  Background colors: {bg_info}")

    # Check CTA buttons
    btns = check_cta_buttons(page_desktop)
    print(f"  Found {len(btns)} button-like elements")
    for btn in btns[:5]:
        print(f"    [{btn['tagName']}] '{btn['text'][:40]}' visible={btn['visible']} bg={btn['bg']}")

    # Check form elements
    forms = check_form_elements(page_desktop)
    print(f"  Found {len(forms)} form inputs")

    # Screenshot 1: Desktop top
    page_desktop.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    path = save_screenshot(page_desktop, "01_desktop_1440_top", "Desktop 1440px - top of page")
    results.append({"file": path, "desc": "Desktop 1440px - top/hero section"})

    # Screenshot 2: Desktop middle (form section)
    page_h = get_page_height(page_desktop)
    print(f"  Page height: {page_h}px")
    scroll_to_percent(page_desktop, 40)
    path = save_screenshot(page_desktop, "02_desktop_1440_middle", "Desktop 1440px - middle/form section")
    results.append({"file": path, "desc": "Desktop 1440px - middle/form section (40%)"})

    # Screenshot 3: Desktop bottom
    scroll_to_bottom(page_desktop)
    path = save_screenshot(page_desktop, "03_desktop_1440_bottom", "Desktop 1440px - bottom of page")
    results.append({"file": path, "desc": "Desktop 1440px - bottom section"})

    ctx_desktop.close()
    print("  Desktop context closed. Waiting before mobile...")
    time.sleep(5)

    # ---- MOBILE 375px ----
    print("\n--- MOBILE 375px ---")
    ctx_mobile = browser.new_context(
        viewport={"width": 375, "height": 812},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        is_mobile=True,
        has_touch=True
    )
    page_mobile = ctx_mobile.new_page()
    page_mobile.on("console", lambda msg: console_errors.append(f"[MOBILE][{msg.type}] {msg.text}") if msg.type == "error" else None)

    print(f"  Navigating mobile to {URL}...")
    page_mobile.goto(URL, wait_until="networkidle", timeout=30000)
    time.sleep(2)

    mob_bg = check_background_color(page_mobile)
    print(f"  Mobile background: {mob_bg}")

    # Screenshot 4: Mobile top
    page_mobile.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    path = save_screenshot(page_mobile, "04_mobile_375_top", "Mobile 375px - top of page")
    results.append({"file": path, "desc": "Mobile 375px - top of page"})

    # Screenshot 5: Mobile scrolled down
    scroll_to_percent(page_mobile, 40)
    path = save_screenshot(page_mobile, "05_mobile_375_scrolled", "Mobile 375px - scrolled 40%")
    results.append({"file": path, "desc": "Mobile 375px - scrolled down (40%)"})

    ctx_mobile.close()

    browser.close()
    print("\n=== Browser closed ===")

print("\n=== SCREENSHOTS SAVED ===")
for r in results:
    print(f"  {r['file']}")
    print(f"    {r['desc']}")

print("\n=== CONSOLE ERRORS ===")
errors_only = [e for e in console_errors if "[error]" in e.lower()]
if errors_only:
    for e in errors_only[:15]:
        print(f"  {e}")
else:
    print("  No errors captured")

print("\n=== ALL CONSOLE MESSAGES (first 20) ===")
for msg in console_errors[:20]:
    print(f"  {msg}")
