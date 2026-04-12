#!/usr/bin/env python3
"""
Verify category color styling on posts
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp-screenshots"

def verify_category_color():
    """Check the computed color of category elements"""
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Go to a single post
            print("Loading single post page...")
            page.goto("https://purebrain.ai/how-my-human-named-me-and-what-it-meant/?nocache=" + str(int(time.time())), wait_until='networkidle', timeout=60000)
            time.sleep(3)

            # Check computed colors
            print("\nChecking element colors...")

            # Get date color
            date_result = page.evaluate('''() => {
                const dateEl = document.querySelector('.entry-meta .posted-on, time.entry-date, [class*="post-date"]');
                if (dateEl) {
                    return {
                        text: dateEl.innerText,
                        color: window.getComputedStyle(dateEl).color,
                        found: true
                    };
                }
                return { found: false };
            }''')

            if date_result.get('found'):
                print(f"Date element: '{date_result.get('text')}' - Color: {date_result.get('color')}")
            else:
                print("Date element not found via standard selectors")

            # Get category color - check multiple selectors
            category_result = page.evaluate('''() => {
                const selectors = [
                    '.cat-links a',
                    '[class*="category"] a',
                    'a[rel="category tag"]',
                    '.entry-meta a[href*="category"]',
                    '[class*="terms"] a'
                ];

                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        return {
                            text: el.innerText,
                            color: window.getComputedStyle(el).color,
                            selector: sel,
                            found: true
                        };
                    }
                }

                // Try finding any element with "category" in class
                const allEls = document.querySelectorAll('[class*="category"], [class*="term"]');
                if (allEls.length > 0) {
                    return {
                        text: allEls[0].innerText,
                        color: window.getComputedStyle(allEls[0]).color,
                        selector: 'generic category/term class',
                        found: true
                    };
                }

                return { found: false };
            }''')

            if category_result.get('found'):
                print(f"Category element: '{category_result.get('text')}' - Color: {category_result.get('color')}")
                print(f"  Found via: {category_result.get('selector')}")

                # Check if color is orange (rgb values close to #f1420b which is rgb(241, 66, 11))
                color = category_result.get('color')
                if 'rgb(241' in color or '241, 66' in color:
                    print("  SUCCESS: Category color is orange!")
                else:
                    print(f"  NOTE: Category color is {color}, expected orange (rgb(241, 66, 11))")
            else:
                print("Category element not found")

            # Get all visible text with "Uncategorized" or category names
            uncategorized = page.evaluate('''() => {
                const elements = Array.from(document.querySelectorAll('*'));
                const results = [];
                for (const el of elements) {
                    if (el.innerText && (el.innerText.includes('Uncategorized') || el.innerText.includes('AI'))) {
                        if (el.children.length === 0 || el.tagName === 'A') {  // Leaf nodes or links
                            const style = window.getComputedStyle(el);
                            if (style.display !== 'none') {
                                results.push({
                                    tag: el.tagName,
                                    text: el.innerText.substring(0, 50),
                                    color: style.color,
                                    classes: el.className
                                });
                            }
                        }
                    }
                    if (results.length >= 5) break;
                }
                return results;
            }''')

            print("\nElements containing 'Uncategorized' or 'AI':")
            for el in uncategorized:
                print(f"  <{el['tag']}> '{el['text']}' - color: {el['color']}")
                if el.get('classes'):
                    print(f"    classes: {el['classes'][:100]}")

            # Screenshot highlighting the meta area
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=f"{SCREENSHOT_DIR}/{timestamp}_category_check.png")
            print(f"\nScreenshot saved: {SCREENSHOT_DIR}/{timestamp}_category_check.png")

            # Also capture the blog page to check for floating logo
            print("\n--- Checking Blog Page ---")
            page.goto("https://purebrain.ai/blog?nocache=" + str(int(time.time())), wait_until='networkidle', timeout=60000)
            time.sleep(2)

            # Check for hidden elements
            floating_check = page.evaluate('''() => {
                const floatingEls = document.querySelectorAll('[class*="floating"], .elementor-widget-image img');
                const results = [];
                for (const el of floatingEls) {
                    const style = window.getComputedStyle(el);
                    results.push({
                        tag: el.tagName,
                        classes: el.className,
                        opacity: style.opacity,
                        visibility: style.visibility,
                        display: style.display,
                        zIndex: style.zIndex
                    });
                }
                return results;
            }''')

            print("\nFloating/image elements on blog page:")
            for el in floating_check[:5]:
                print(f"  <{el['tag']}> - opacity: {el['opacity']}, visibility: {el['visibility']}, z-index: {el['zIndex']}")

            page.screenshot(path=f"{SCREENSHOT_DIR}/{timestamp}_blog_floating_check.png")
            print(f"Screenshot saved: {SCREENSHOT_DIR}/{timestamp}_blog_floating_check.png")

            return True

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = verify_category_color()
    sys.exit(0 if success else 1)
