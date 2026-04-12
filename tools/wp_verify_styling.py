#!/usr/bin/env python3
"""
WordPress Styling Verifier
Takes screenshots of key pages to verify CSS changes
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp-screenshots"

def ensure_screenshot_dir():
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)

def take_screenshot(page, name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"Screenshot saved: {path}")
    return path

def verify_styling():
    """Take screenshots of blog page and single post"""
    ensure_screenshot_dir()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Clear cache - navigate to blog with cache-busting
            print("\n[Verification 1] Loading blog page (with cache bust)...")
            # Force bypass cache
            page.goto("https://purebrain.ai/blog?nocache=" + str(int(time.time())), wait_until='networkidle', timeout=60000)
            time.sleep(3)  # Let animations/CSS load
            screenshot1 = take_screenshot(page, "verify_blog_page")

            # Check for any post links
            print("\n[Verification 2] Finding a blog post...")
            post_links = page.query_selector_all('a[href*="/blog/"][href*="202"]')  # Posts from 2020+

            if post_links:
                # Get first actual post (not the blog landing)
                first_post_link = None
                for link in post_links:
                    href = link.get_attribute('href')
                    if href and '/blog/' in href and href != 'https://purebrain.ai/blog/':
                        first_post_link = link
                        break

                if first_post_link:
                    post_url = first_post_link.get_attribute('href')
                    print(f"Navigating to post: {post_url}")
                    page.goto(post_url + "?nocache=" + str(int(time.time())), wait_until='networkidle', timeout=60000)
                    time.sleep(3)
                    screenshot2 = take_screenshot(page, "verify_single_post")

                    # Also get category element to check color
                    print("\nChecking for category elements on post...")
                    cat_elements = page.query_selector_all('.cat-links a, [class*="category"] a, a[rel="category tag"]')
                    if cat_elements:
                        print(f"Found {len(cat_elements)} category link(s)")
                        for i, cat in enumerate(cat_elements[:3]):
                            text = cat.inner_text()
                            # Get computed color
                            color = page.evaluate('''(el) => {
                                return window.getComputedStyle(el).color;
                            }''', cat)
                            print(f"  Category '{text}': color = {color}")
                    else:
                        print("No category elements found on page")
                else:
                    print("Could not find post link with valid URL")
            else:
                print("No post links found - checking page content...")
                # Try alternative: check WordPress post titles
                titles = page.query_selector_all('.wp-block-latest-posts__post-title, .entry-title a')
                if titles:
                    first_title = titles[0]
                    href = first_title.get_attribute('href')
                    if href:
                        print(f"Found title link: {href}")
                        page.goto(href + "?nocache=" + str(int(time.time())), wait_until='networkidle', timeout=60000)
                        time.sleep(3)
                        take_screenshot(page, "verify_single_post")

            print("\n[Verification Complete]")
            print(f"Screenshots saved to: {SCREENSHOT_DIR}")
            return True

        except PlaywrightTimeout as e:
            print(f"Timeout: {e}")
            take_screenshot(page, "verify_error_timeout")
            return False
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "verify_error")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = verify_styling()
    sys.exit(0 if success else 1)
