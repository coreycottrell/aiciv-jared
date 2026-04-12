#!/usr/bin/env python3
"""
Debug category element structure
"""

import sys
import time
from playwright.sync_api import sync_playwright

def debug_category():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            print("Loading single post page...")
            page.goto("https://purebrain.ai/how-my-human-named-me-and-what-it-meant/?nocache=" + str(int(time.time())), wait_until='networkidle', timeout=60000)
            time.sleep(3)

            # Get the HTML around the date/category area
            meta_html = page.evaluate('''() => {
                // Find the element containing "Uncategorized"
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node;
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('Uncategorized')) {
                        // Get parent element chain
                        let el = node.parentElement;
                        let chain = [];
                        while (el && chain.length < 5) {
                            chain.push({
                                tag: el.tagName,
                                id: el.id,
                                classes: el.className,
                                color: window.getComputedStyle(el).color
                            });
                            el = el.parentElement;
                        }
                        return {
                            found: true,
                            text: node.textContent,
                            parentChain: chain,
                            outerHTML: node.parentElement.outerHTML.substring(0, 500)
                        };
                    }
                }
                return { found: false };
            }''')

            if meta_html.get('found'):
                print(f"\nFound 'Uncategorized' text")
                print(f"Outer HTML: {meta_html.get('outerHTML')}")
                print(f"\nParent chain:")
                for i, el in enumerate(meta_html.get('parentChain', [])):
                    print(f"  {i}: <{el['tag']}> id='{el['id']}' class='{el['classes']}' color={el['color']}")
            else:
                print("Could not find 'Uncategorized' text")

            # Also check what's happening with the date
            date_html = page.evaluate('''() => {
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node;
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('February 14, 2026')) {
                        let el = node.parentElement;
                        return {
                            found: true,
                            tag: el.tagName,
                            classes: el.className,
                            color: window.getComputedStyle(el).color,
                            outerHTML: el.outerHTML.substring(0, 300)
                        };
                    }
                }
                return { found: false };
            }''')

            if date_html.get('found'):
                print(f"\nDate element:")
                print(f"  Tag: {date_html.get('tag')}, Classes: {date_html.get('classes')}")
                print(f"  Color: {date_html.get('color')}")
                print(f"  HTML: {date_html.get('outerHTML')}")

            return True

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    debug_category()
