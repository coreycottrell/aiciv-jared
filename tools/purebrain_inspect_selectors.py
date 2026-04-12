#!/usr/bin/env python3
"""
PureBrain Selector Inspector
Finds actual CSS selectors for orange elements
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime
import json

SCREENSHOT_DIR = "/tmp"

async def inspect_selectors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("PUREBRAIN SELECTOR INSPECTOR")
        print("=" * 60)

        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        # Find all elements with orange color and get their full selector path
        print("\n[1] Finding all orange-colored elements with full selectors...")

        orange_elements = await page.evaluate(r'''
            () => {
                const results = [];

                // Function to get a unique selector for an element
                function getSelector(el) {
                    if (el.id) return '#' + el.id;

                    let path = [];
                    while (el && el.nodeType === Node.ELEMENT_NODE) {
                        let selector = el.tagName.toLowerCase();
                        if (el.className && typeof el.className === 'string') {
                            const classes = el.className.trim().split(/\s+/).filter(c => c && !c.includes('elementor-'));
                            if (classes.length > 0) {
                                selector += '.' + classes.slice(0, 2).join('.');
                            }
                        }
                        path.unshift(selector);
                        el = el.parentElement;
                        if (path.length > 4) break;
                    }
                    return path.join(' > ');
                }

                // Walk through all elements
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    const color = style.color;

                    // Check if color is orange (rgb(241, 66, 11) or close)
                    const match = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
                    if (match) {
                        const [_, r, g, b] = match.map(Number);
                        if (r > 200 && g < 100 && b < 50) {
                            const text = el.innerText?.trim()?.substring(0, 60);
                            if (text && !results.some(r => r.text === text)) {
                                results.push({
                                    tag: el.tagName.toLowerCase(),
                                    id: el.id || '',
                                    classes: el.className || '',
                                    selector: getSelector(el),
                                    text: text,
                                    color: color,
                                    parentClasses: el.parentElement?.className || ''
                                });
                            }
                        }
                    }
                });

                return results.slice(0, 60);
            }
        ''')

        print(f"\nFound {len(orange_elements)} unique orange text elements:\n")

        for i, el in enumerate(orange_elements):
            print(f"[{i+1}] TEXT: '{el['text'][:40]}...' " if len(el['text']) > 40 else f"[{i+1}] TEXT: '{el['text']}'")
            print(f"    TAG: {el['tag']}")
            print(f"    ID: {el['id'] or '(none)'}")
            print(f"    CLASSES: {el['classes'][:80] or '(none)'}")
            print(f"    PARENT CLASSES: {el['parentClasses'][:60] or '(none)'}")
            print(f"    SELECTOR: {el['selector']}")
            print()

        # Now specifically look at the form labels
        print("\n[2] Specifically inspecting form labels...")

        form_labels = await page.evaluate(r'''
            () => {
                const labels = [];
                document.querySelectorAll('label').forEach(label => {
                    const style = window.getComputedStyle(label);
                    labels.push({
                        text: label.innerText?.trim(),
                        classes: label.className,
                        color: style.color,
                        parentClasses: label.parentElement?.className || '',
                        grandparentClasses: label.parentElement?.parentElement?.className || ''
                    });
                });
                return labels;
            }
        ''')

        print(f"\nFound {len(form_labels)} labels:")
        for label in form_labels:
            print(f"  '{label['text']}' - color: {label['color']}")
            print(f"    Classes: {label['classes'][:60] or '(none)'}")
            print(f"    Parent: {label['parentClasses'][:60] or '(none)'}")
            print()

        # Check body classes
        print("\n[3] Checking body classes for targeting...")
        body_classes = await page.evaluate("() => document.body.className")
        print(f"  Body classes: {body_classes}")

        # Get the page ID
        page_id = await page.evaluate(r'''
            () => {
                const classes = document.body.className;
                const match = classes.match(/page-id-(\d+)/);
                return match ? match[1] : null;
            }
        ''')
        print(f"  Page ID: {page_id}")

        await browser.close()
        return orange_elements

if __name__ == "__main__":
    asyncio.run(inspect_selectors())
