#!/usr/bin/env python3
"""
Mobile Responsiveness Audit for purebrain.ai
Tests pages at 375px width (iPhone viewport)
"""

import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Test URLs
URLS = [
    ("homepage", "https://purebrain.ai/"),
    ("blog-listing", "https://purebrain.ai/blog/"),
    ("blog-post", "https://purebrain.ai/blog/how-my-human-named-me-and-what-it-meant/"),
]

# Mobile viewport (iPhone SE/small iPhone)
VIEWPORT = {"width": 375, "height": 812}

# Output directory
OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/mobile-screenshots"

async def audit_page(page, name, url):
    """Audit a single page for mobile responsiveness."""
    print(f"\n{'='*60}")
    print(f"Auditing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    results = {
        "name": name,
        "url": url,
        "issues": [],
        "observations": [],
    }

    try:
        # Navigate to page - use domcontentloaded which is faster
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        # Wait for page to settle
        await asyncio.sleep(4)

        # Check for horizontal overflow (scrollbar)
        horizontal_overflow = await page.evaluate("""
            () => {
                return document.documentElement.scrollWidth > document.documentElement.clientWidth;
            }
        """)

        if horizontal_overflow:
            results["issues"].append("HORIZONTAL OVERFLOW: Page has horizontal scroll")
            scroll_width = await page.evaluate("() => document.documentElement.scrollWidth")
            client_width = await page.evaluate("() => document.documentElement.clientWidth")
            results["issues"].append(f"  - Scroll width: {scroll_width}px, Client width: {client_width}px")
        else:
            results["observations"].append("No horizontal overflow detected")

        # Check viewport meta tag
        viewport_meta = await page.evaluate("""
            () => {
                const meta = document.querySelector('meta[name="viewport"]');
                return meta ? meta.getAttribute('content') : null;
            }
        """)

        if viewport_meta:
            results["observations"].append(f"Viewport meta: {viewport_meta}")
        else:
            results["issues"].append("MISSING: No viewport meta tag found")

        # Check for text that's too small (less than 12px)
        small_text = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('p, span, div, li, a');
                let smallCount = 0;
                let examples = [];
                for (let el of elements) {
                    const style = window.getComputedStyle(el);
                    const fontSize = parseFloat(style.fontSize);
                    if (fontSize < 12 && el.textContent.trim().length > 0) {
                        smallCount++;
                        if (examples.length < 3) {
                            examples.push({
                                tag: el.tagName,
                                fontSize: fontSize,
                                text: el.textContent.trim().substring(0, 50)
                            });
                        }
                    }
                }
                return { count: smallCount, examples: examples };
            }
        """)

        if small_text["count"] > 0:
            results["issues"].append(f"SMALL TEXT: {small_text['count']} elements with font-size < 12px")
            for ex in small_text["examples"]:
                results["issues"].append(f"  - {ex['tag']}: {ex['fontSize']}px - '{ex['text'][:30]}...'")
        else:
            results["observations"].append("Text sizes appear adequate (>=12px)")

        # Check tap targets (buttons and links) - should be at least 44x44px for mobile
        small_tap_targets = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('a, button, [role="button"], input[type="submit"]');
                let smallCount = 0;
                let examples = [];
                for (let el of elements) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width < 44 || rect.height < 44) {
                        // Only count visible elements
                        if (rect.width > 0 && rect.height > 0) {
                            smallCount++;
                            if (examples.length < 5) {
                                examples.push({
                                    tag: el.tagName,
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height),
                                    text: el.textContent.trim().substring(0, 30) || el.getAttribute('aria-label') || 'no text'
                                });
                            }
                        }
                    }
                }
                return { count: smallCount, examples: examples };
            }
        """)

        if small_tap_targets["count"] > 0:
            results["issues"].append(f"SMALL TAP TARGETS: {small_tap_targets['count']} elements smaller than 44x44px")
            for ex in small_tap_targets["examples"]:
                results["issues"].append(f"  - {ex['tag']}: {ex['width']}x{ex['height']}px - '{ex['text']}'")
        else:
            results["observations"].append("Tap targets appear adequate (>=44x44px)")

        # Check for video elements
        video_info = await page.evaluate("""
            () => {
                const videos = document.querySelectorAll('video');
                const iframes = document.querySelectorAll('iframe[src*="youtube"], iframe[src*="vimeo"]');
                const bgVideos = document.querySelectorAll('[style*="background"]');

                let hasVideoBackground = false;
                for (let el of document.querySelectorAll('*')) {
                    const style = window.getComputedStyle(el);
                    if (style.backgroundImage && style.backgroundImage !== 'none') {
                        // Check for video-related classes or background
                        if (el.classList.contains('video') || el.id.includes('video')) {
                            hasVideoBackground = true;
                        }
                    }
                }

                return {
                    videoElements: videos.length,
                    iframes: iframes.length,
                    possibleVideoBackground: hasVideoBackground
                };
            }
        """)

        results["observations"].append(f"Video elements: {video_info['videoElements']}, Video iframes: {video_info['iframes']}")

        # Check for elements that might be cut off or overlapping
        overflow_elements = await page.evaluate("""
            () => {
                const viewportWidth = window.innerWidth;
                const elements = document.querySelectorAll('*');
                let issues = [];

                for (let el of elements) {
                    const rect = el.getBoundingClientRect();
                    // Check if element extends beyond viewport
                    if (rect.right > viewportWidth + 5) {
                        if (rect.width > 0 && rect.height > 0) {
                            const tag = el.tagName.toLowerCase();
                            const className = el.className ? `.${el.className.split(' ')[0]}` : '';
                            if (issues.length < 5 && !['script', 'style', 'link', 'meta'].includes(tag)) {
                                issues.push({
                                    element: tag + className,
                                    rightEdge: Math.round(rect.right),
                                    overflow: Math.round(rect.right - viewportWidth)
                                });
                            }
                        }
                    }
                }

                return issues;
            }
        """)

        if overflow_elements:
            results["issues"].append("OVERFLOW ELEMENTS: Some elements extend beyond viewport")
            for el in overflow_elements:
                results["issues"].append(f"  - {el['element']}: extends {el['overflow']}px beyond viewport")

        # Take full-page screenshot
        screenshot_path = os.path.join(OUTPUT_DIR, f"{name}-fullpage.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        results["screenshot_fullpage"] = screenshot_path
        print(f"Full page screenshot saved: {screenshot_path}")

        # Take viewport screenshot (above the fold)
        screenshot_viewport = os.path.join(OUTPUT_DIR, f"{name}-viewport.png")
        await page.screenshot(path=screenshot_viewport)
        results["screenshot_viewport"] = screenshot_viewport
        print(f"Viewport screenshot saved: {screenshot_viewport}")

        # Get page title
        title = await page.title()
        results["title"] = title

        # Check console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    except Exception as e:
        results["issues"].append(f"ERROR: {str(e)}")

    return results


async def main():
    """Run the mobile audit."""
    print(f"\nMobile Responsiveness Audit - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Viewport: {VIEWPORT['width']}x{VIEWPORT['height']}px")

    all_results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport=VIEWPORT,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
        )

        page = await context.new_page()

        for name, url in URLS:
            results = await audit_page(page, name, url)
            all_results.append(results)

        await browser.close()

    # Print summary
    print("\n" + "="*60)
    print("AUDIT SUMMARY")
    print("="*60)

    for result in all_results:
        print(f"\n{result['name'].upper()}")
        print(f"URL: {result['url']}")
        if result.get('title'):
            print(f"Title: {result['title']}")

        if result['issues']:
            print("\nISSUES FOUND:")
            for issue in result['issues']:
                print(f"  {issue}")
        else:
            print("\nNo issues found!")

        print("\nObservations:")
        for obs in result['observations']:
            print(f"  - {obs}")

    return all_results


if __name__ == "__main__":
    asyncio.run(main())
