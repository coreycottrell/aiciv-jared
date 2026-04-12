#!/usr/bin/env python3
"""Inspect the DOM structure of the category page header/nav elements."""

import sys
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        page.set_default_timeout(60000)

        # Check category page structure
        print("=" * 60)
        print("Inspecting category page header/nav structure")
        print("=" * 60)

        page.goto("https://purebrain.ai/category/for-teams/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        # Get full header/nav HTML structure
        structure = page.evaluate("""
            () => {
                function getStructure(el, depth=0) {
                    if (!el || depth > 5) return '';
                    const tag = el.tagName.toLowerCase();
                    const id = el.id ? '#' + el.id : '';
                    const cls = el.className ? '.' + (typeof el.className === 'string' ? el.className.replace(/\\s+/g, '.') : '') : '';
                    const style = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    const indent = '  '.repeat(depth);
                    let result = `${indent}<${tag}${id}${cls.substring(0,80)}> display=${style.display} h=${Math.round(rect.height)}px w=${Math.round(rect.width)}px\\n`;

                    // Show inner text for small elements
                    if (el.children.length === 0 && el.textContent.trim()) {
                        result += `${indent}  TEXT: "${el.textContent.trim().substring(0, 60)}"\\n`;
                    }

                    for (let child of el.children) {
                        result += getStructure(child, depth + 1);
                    }
                    return result;
                }

                let result = '';

                // Get header element
                const header = document.querySelector('header') || document.querySelector('#masthead');
                if (header) {
                    result += '=== HEADER ===\\n';
                    result += getStructure(header);
                }

                // Get nav element
                const nav = document.querySelector('nav');
                if (nav) {
                    result += '\\n=== NAV ===\\n';
                    result += getStructure(nav);
                }

                // Get .navbar element
                const navbar = document.querySelector('.navbar');
                if (navbar) {
                    result += '\\n=== .NAVBAR ===\\n';
                    result += getStructure(navbar);
                }

                // Also get the breadcrumb area
                const breadcrumb = document.querySelector('.breadcrumb, .breadcrumbs, [class*="breadcrumb"]');
                if (breadcrumb) {
                    result += '\\n=== BREADCRUMB ===\\n';
                    result += getStructure(breadcrumb);
                }

                return result;
            }
        """)
        print(structure)

        # Also check: what does the header look like WITHOUT our override?
        # Let's check what actual navigation exists in the theme
        links_info = page.evaluate("""
            () => {
                // Find all links in the header area
                const header = document.querySelector('header') || document.querySelector('#masthead');
                if (!header) return 'No header found';

                const links = header.querySelectorAll('a');
                return Array.from(links).map(a => ({
                    text: a.textContent.trim().substring(0, 50),
                    href: a.href,
                    visible: a.getBoundingClientRect().height > 0 && getComputedStyle(a).display !== 'none'
                }));
            }
        """)
        print("\n=== HEADER LINKS ===")
        if isinstance(links_info, list):
            for link in links_info:
                vis = "VISIBLE" if link.get('visible') else "HIDDEN"
                print(f"  [{vis}] {link.get('text', '?')}: {link.get('href', '?')}")
        else:
            print(f"  {links_info}")

        # Check what blog post URLs exist (for later testing)
        print("\n=== Finding real blog post URLs ===")
        page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        post_urls = page.evaluate("""
            () => {
                // Find links that go to blog posts
                const links = document.querySelectorAll('a[href]');
                const postUrls = [];
                const seen = new Set();
                for (const link of links) {
                    const href = link.href;
                    // Blog posts typically have /year/month/day/ or just /post-slug/
                    if (href.includes('purebrain.ai/') &&
                        !href.includes('/category/') &&
                        !href.includes('/tag/') &&
                        !href.includes('/page/') &&
                        !href.includes('/blog/') &&
                        !href.includes('/wp-') &&
                        !href.includes('#') &&
                        !href.endsWith('purebrain.ai/') &&
                        href !== 'https://purebrain.ai/' &&
                        !seen.has(href)) {
                        seen.add(href);
                        postUrls.push({
                            text: link.textContent.trim().substring(0, 60),
                            href: href
                        });
                    }
                }
                return postUrls.slice(0, 10);
            }
        """)
        for p_url in post_urls:
            print(f"  {p_url.get('text', '?')}: {p_url.get('href', '?')}")

        # Test a real blog post
        if post_urls:
            real_post_url = post_urls[0]['href']
            print(f"\n=== Testing single post: {real_post_url} ===")
            page.goto(real_post_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)

            body_classes = page.evaluate("() => document.body.className")
            print(f"  Body classes: {body_classes[:200]}")

            nav_check = page.evaluate("""
                () => {
                    const selectors = ['nav', 'header', '.navbar', '#masthead'];
                    const results = {};
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            const style = getComputedStyle(el);
                            const rect = el.getBoundingClientRect();
                            results[sel] = {
                                display: style.display,
                                height: rect.height,
                                visible: rect.height > 0 && style.display !== 'none'
                            };
                        }
                    }
                    return results;
                }
            """)
            print(f"  Nav check: {nav_check}")

            path = f"{SCREENSHOT_DIR}/navverify_real_single_post_{TIMESTAMP}.png"
            page.screenshot(path=path, timeout=60000)
            print(f"  Screenshot: {path}")

        browser.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
