#!/usr/bin/env python3
"""
QA Test: Unified How-This-Levels-You-Up Page
Date: 2026-03-04
URL: https://purebrain.ai/unified-how-this-levels-you-up/
Tests:
  1. Page loads with dark background
  2. Hero section with Unified tier branding
  3. Content sections with badges
  4. PayPal $999 button exists
  5. PayPal modal opens on click
"""

import asyncio
import os
import sys
from pathlib import Path

SESSION_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/unified-qa-20260304"
os.makedirs(SESSION_DIR, exist_ok=True)

TARGET_URL = "https://purebrain.ai/unified-how-this-levels-you-up/"

def log(msg):
    print(f"[QA] {msg}", flush=True)

async def run_qa():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # Collect console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type in ["error", "warning"] else None)

        log(f"Navigating to {TARGET_URL}")
        try:
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)  # Wait for JS/animations
        except Exception as e:
            log(f"Navigation error: {e}")

        # --- SCREENSHOT 1: Initial page load (top) ---
        log("Taking screenshot 1: Top of page")
        await page.screenshot(path=f"{SESSION_DIR}/001-page-top.png", full_page=False)

        # --- CHECK 1: Dark background ---
        bg_color = await page.evaluate("""
            () => {
                const body = document.body;
                const style = window.getComputedStyle(body);
                return style.backgroundColor;
            }
        """)
        log(f"Body background color: {bg_color}")

        # Check page background more specifically
        page_bg = await page.evaluate("""
            () => {
                const elements = [document.body, document.documentElement, document.querySelector('.site'), document.querySelector('#page'), document.querySelector('main')];
                return elements.filter(Boolean).map(el => ({
                    tag: el.tagName,
                    class: el.className.substring(0, 50),
                    bg: window.getComputedStyle(el).backgroundColor
                }));
            }
        """)
        log(f"Background colors: {page_bg}")

        # --- CHECK 2: Hero section ---
        hero_text = await page.evaluate("""
            () => {
                const h1 = document.querySelector('h1');
                const h2s = Array.from(document.querySelectorAll('h2')).map(h => h.textContent.trim()).slice(0, 3);
                return {
                    h1: h1 ? h1.textContent.trim() : 'NOT FOUND',
                    h2s: h2s
                };
            }
        """)
        log(f"Hero content: {hero_text}")

        # --- CHECK 3: Content with badges ---
        badges = await page.evaluate("""
            () => {
                const allText = document.body.innerText;
                return {
                    hasLive: allText.includes('Live'),
                    hasInDevelopment: allText.includes('In Development'),
                    hasPartnered: allText.includes('Partnered'),
                    hasUnified: allText.includes('Unified'),
                    wordCount: allText.split(/\s+/).length
                };
            }
        """)
        log(f"Content badges: {badges}")

        # --- CHECK 4: PayPal button ---
        paypal_info = await page.evaluate("""
            () => {
                // Look for PayPal button or button with $999
                const allButtons = Array.from(document.querySelectorAll('button, .paypal-button, [id*="paypal"], [class*="paypal"], input[type="submit"]'));
                const bodyText = document.body.innerHTML;

                return {
                    buttonCount: allButtons.length,
                    buttonTexts: allButtons.slice(0, 10).map(b => b.textContent.trim().substring(0, 60)),
                    hasPaypalScript: bodyText.includes('paypal'),
                    has999: bodyText.includes('999'),
                    paypalElements: Array.from(document.querySelectorAll('[id*="paypal"], [class*="paypal"]')).slice(0, 5).map(el => ({
                        tag: el.tagName,
                        id: el.id,
                        class: el.className.substring(0, 50)
                    }))
                };
            }
        """)
        log(f"PayPal info: {paypal_info}")

        # --- SCROLL DOWN AND SCREENSHOT ---
        log("Scrolling through page...")

        # Screenshot at 25% scroll
        await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight * 0.25)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{SESSION_DIR}/002-scroll-25pct.png", full_page=False)
        log("Screenshot 2: 25% scroll")

        # Screenshot at 50% scroll
        await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight * 0.5)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{SESSION_DIR}/003-scroll-50pct.png", full_page=False)
        log("Screenshot 3: 50% scroll")

        # Screenshot at 75% scroll
        await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight * 0.75)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{SESSION_DIR}/004-scroll-75pct.png", full_page=False)
        log("Screenshot 4: 75% scroll")

        # Screenshot at bottom
        await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"{SESSION_DIR}/005-bottom-paypal.png", full_page=False)
        log("Screenshot 5: Bottom - PayPal button area")

        # Full page screenshot
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{SESSION_DIR}/006-full-page.png", full_page=True)
        log("Screenshot 6: Full page")

        # --- CHECK 5: Try clicking PayPal button ---
        log("Attempting to click PayPal button...")
        paypal_button = await page.query_selector('.paypal-btn, #paypal-btn, [onclick*="paypal"], button:has-text("Pay"), button:has-text("999")')

        # Also try finding by text
        if not paypal_button:
            # Try finding any button near "999"
            paypal_button = await page.query_selector('button')
            buttons_list = await page.query_selector_all('button')
            log(f"Found {len(buttons_list)} buttons total")
            for btn in buttons_list:
                text = await btn.text_content()
                if text and ('999' in text or 'Pay' in text.lower() or 'PayPal' in text.lower() or 'Unified' in text.lower()):
                    paypal_button = btn
                    log(f"Found target button: '{text.strip()[:60]}'")
                    break

        if paypal_button:
            log("Clicking PayPal button...")
            await paypal_button.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await page.screenshot(path=f"{SESSION_DIR}/007-before-click.png", full_page=False)
            await paypal_button.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path=f"{SESSION_DIR}/008-after-click-modal.png", full_page=False)
            log("Screenshot 8: After click - checking for modal")

            # Check if modal/overlay appeared
            modal_check = await page.evaluate("""
                () => {
                    const modals = document.querySelectorAll('.modal, .paypal-modal, [class*="modal"], [class*="overlay"], iframe[src*="paypal"]');
                    const iframes = document.querySelectorAll('iframe');
                    return {
                        modalsFound: modals.length,
                        iframesFound: iframes.length,
                        iframeSrcs: Array.from(iframes).map(f => f.src.substring(0, 80))
                    };
                }
            """)
            log(f"After click modal check: {modal_check}")
        else:
            log("No PayPal button found to click - checking page source")
            # Get the raw HTML to understand what's there
            page_source_snippet = await page.evaluate("""
                () => {
                    // Find anything with 999 or paypal
                    const html = document.body.innerHTML;
                    const idx = html.toLowerCase().indexOf('999');
                    if (idx >= 0) return html.substring(Math.max(0, idx-200), idx+200);
                    return 'No 999 found in page HTML';
                }
            """)
            log(f"HTML around '999': {page_source_snippet[:500]}")

        # --- SUMMARY ---
        log("\n=== QA SUMMARY ===")
        log(f"Console errors: {len([e for e in console_errors if 'error' in e.lower()])}")
        for e in console_errors[:10]:
            log(f"  {e}")

        await browser.close()

        return {
            "bg_color": bg_color,
            "page_bg": page_bg,
            "hero_text": hero_text,
            "badges": badges,
            "paypal_info": paypal_info,
            "console_errors": console_errors[:10],
            "screenshots_dir": SESSION_DIR
        }

if __name__ == "__main__":
    result = asyncio.run(run_qa())
    print("\n=== FINAL RESULTS ===")
    import json
    print(json.dumps(result, indent=2, default=str))
