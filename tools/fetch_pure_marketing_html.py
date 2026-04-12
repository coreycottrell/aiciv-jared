#!/usr/bin/env python3
"""
Fetch HTML from Pure Marketing V2 Replit app.
Uses Playwright for full page rendering and JavaScript execution.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

TARGET_URL = "https://pure-marketing-v-2.replit.app/"
OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/inbox")
HTML_OUTPUT = OUTPUT_DIR / "pure-marketing-v2-replit.html"
SCREENSHOT_OUTPUT = OUTPUT_DIR / "pure-marketing-v2-replit-screenshot.png"
CSS_OUTPUT = OUTPUT_DIR / "pure-marketing-v2-replit-styles.css"
JS_OUTPUT = OUTPUT_DIR / "pure-marketing-v2-replit-scripts.js"


def fetch_page_content():
    """Fetch complete page content using Playwright."""

    print(f"[{datetime.now().isoformat()}] Starting Playwright automation...")
    print(f"Target URL: {TARGET_URL}")

    with sync_playwright() as p:
        # Launch browser in headless mode
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)

        # Create context with reasonable viewport
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        # Enable console logging
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        try:
            print("Navigating to page...")
            # Navigate with extended timeout for Replit cold starts
            response = page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)

            if response:
                print(f"Response status: {response.status}")

            # Additional wait for any dynamic content
            print("Waiting for dynamic content...")
            page.wait_for_timeout(3000)  # 3 second extra wait

            # Try to wait for body to be fully loaded
            page.wait_for_selector("body", state="attached", timeout=10000)

            # Get the full HTML content
            print("Extracting HTML content...")
            html_content = page.content()

            # Save HTML
            HTML_OUTPUT.write_text(html_content, encoding="utf-8")
            print(f"HTML saved to: {HTML_OUTPUT}")
            print(f"HTML size: {len(html_content)} bytes")

            # Take screenshot
            print("Taking screenshot...")
            page.screenshot(path=str(SCREENSHOT_OUTPUT), full_page=True)
            print(f"Screenshot saved to: {SCREENSHOT_OUTPUT}")

            # Extract inline styles
            print("Extracting inline CSS...")
            styles = page.evaluate("""
                () => {
                    const styles = [];
                    // Get style tags
                    document.querySelectorAll('style').forEach(style => {
                        styles.push(style.textContent);
                    });
                    // Get linked stylesheets (that are same-origin)
                    document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                        styles.push(`/* External: ${link.href} */`);
                    });
                    return styles.join('\\n\\n/* --- */\\n\\n');
                }
            """)

            if styles:
                CSS_OUTPUT.write_text(styles, encoding="utf-8")
                print(f"CSS saved to: {CSS_OUTPUT}")

            # Extract inline scripts
            print("Extracting inline JavaScript...")
            scripts = page.evaluate("""
                () => {
                    const scripts = [];
                    document.querySelectorAll('script').forEach(script => {
                        if (script.src) {
                            scripts.push(`// External: ${script.src}`);
                        } else if (script.textContent.trim()) {
                            scripts.push(script.textContent);
                        }
                    });
                    return scripts.join('\\n\\n// --- \\n\\n');
                }
            """)

            if scripts:
                JS_OUTPUT.write_text(scripts, encoding="utf-8")
                print(f"JavaScript saved to: {JS_OUTPUT}")

            # Get page title and meta info
            title = page.title()
            print(f"Page title: {title}")

            # Print console messages if any
            if console_messages:
                print(f"\nConsole messages ({len(console_messages)}):")
                for msg in console_messages[:10]:  # First 10 only
                    print(f"  {msg}")

            print("\n=== SUCCESS ===")
            print(f"HTML: {HTML_OUTPUT} ({len(html_content)} bytes)")
            print(f"Screenshot: {SCREENSHOT_OUTPUT}")

            return True

        except PlaywrightTimeout as e:
            print(f"Timeout error: {e}")
            # Still try to get whatever content loaded
            try:
                html_content = page.content()
                HTML_OUTPUT.write_text(html_content, encoding="utf-8")
                page.screenshot(path=str(SCREENSHOT_OUTPUT))
                print(f"Partial content saved despite timeout")
                return True
            except Exception as e2:
                print(f"Failed to save partial content: {e2}")
                return False

        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            return False

        finally:
            browser.close()
            print("Browser closed.")


if __name__ == "__main__":
    success = fetch_page_content()
    sys.exit(0 if success else 1)
