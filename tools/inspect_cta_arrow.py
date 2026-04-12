#!/usr/bin/env python3
"""
CTA Button Arrow Inspector
Finds the EXACT element and CSS properties of the arrow on the "Awaken Your PURE BRAIN" button
"""

import asyncio
from playwright.async_api import async_playwright
import json

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp-screenshots"

async def inspect_cta_arrow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(90000)

        print("=" * 70)
        print("CTA BUTTON ARROW INSPECTOR")
        print("Finding the EXACT element for the arrow on 'Awaken Your PURE BRAIN'")
        print("=" * 70)

        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=90000)
        await asyncio.sleep(5)  # Wait for JS to render

        # Take screenshot of the page
        await page.screenshot(path=f"{SCREENSHOT_DIR}/cta_button_inspection.png", full_page=False)
        print(f"\nScreenshot saved to {SCREENSHOT_DIR}/cta_button_inspection.png")

        # Find buttons containing "Awaken" or "PURE BRAIN"
        print("\n[1] Finding CTA buttons with 'Awaken' text...")

        cta_buttons = await page.evaluate(r'''
            () => {
                const results = [];

                // Find all elements that might be the CTA button
                const allElements = document.querySelectorAll('a, button, [role="button"]');

                allElements.forEach(el => {
                    const text = el.innerText || el.textContent || '';
                    if (text.includes('Awaken') || text.includes('PURE BRAIN')) {
                        results.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id || '',
                            classes: el.className || '',
                            text: text.trim().substring(0, 100),
                            href: el.href || '',
                            outerHTML: el.outerHTML.substring(0, 500),
                            childCount: el.children.length
                        });
                    }
                });

                return results;
            }
        ''')

        print(f"\nFound {len(cta_buttons)} CTA button(s):")
        for i, btn in enumerate(cta_buttons):
            print(f"\n--- Button {i+1} ---")
            print(f"  Tag: {btn['tag']}")
            print(f"  ID: {btn['id'] or '(none)'}")
            print(f"  Classes: {btn['classes']}")
            print(f"  Text: {btn['text']}")
            print(f"  Children: {btn['childCount']}")
            print(f"  HTML preview: {btn['outerHTML'][:300]}...")

        # Now do a DEEP inspection of the button structure
        print("\n\n[2] DEEP INSPECTION of button children and pseudo-elements...")

        deep_inspection = await page.evaluate(r'''
            () => {
                const results = [];

                // Find buttons with "Awaken" text
                const buttons = Array.from(document.querySelectorAll('a, button')).filter(
                    el => (el.innerText || '').includes('Awaken')
                );

                if (buttons.length === 0) return { error: 'No buttons found' };

                const btn = buttons[0]; // First matching button

                // Get ALL descendants
                function getAllDescendants(el, depth = 0) {
                    const children = [];
                    Array.from(el.children).forEach(child => {
                        const style = window.getComputedStyle(child);
                        const beforeStyle = window.getComputedStyle(child, '::before');
                        const afterStyle = window.getComputedStyle(child, '::after');

                        children.push({
                            depth: depth,
                            tag: child.tagName.toLowerCase(),
                            classes: child.className || '',
                            id: child.id || '',
                            text: (child.innerText || '').trim().substring(0, 50),
                            color: style.color,
                            fill: style.fill,
                            stroke: style.stroke,
                            backgroundColor: style.backgroundColor,
                            backgroundImage: style.backgroundImage?.substring(0, 100),
                            content: style.content,
                            // Check pseudo-elements
                            beforeContent: beforeStyle.content,
                            beforeColor: beforeStyle.color,
                            beforeBackgroundImage: beforeStyle.backgroundImage?.substring(0, 100),
                            afterContent: afterStyle.content,
                            afterColor: afterStyle.color,
                            afterBackgroundImage: afterStyle.backgroundImage?.substring(0, 100),
                            // SVG specific
                            viewBox: child.getAttribute?.('viewBox') || '',
                            d: child.getAttribute?.('d') || '',
                            // Image specific
                            src: child.src || child.getAttribute?.('src') || '',
                            // Icon font specific
                            fontFamily: style.fontFamily?.substring(0, 50),
                            // Full HTML for debugging
                            html: child.outerHTML?.substring(0, 200)
                        });

                        // Recursively get children
                        const subChildren = getAllDescendants(child, depth + 1);
                        children.push(...subChildren);
                    });
                    return children;
                }

                const descendants = getAllDescendants(btn);

                // Also check the button itself
                const btnStyle = window.getComputedStyle(btn);
                const btnBefore = window.getComputedStyle(btn, '::before');
                const btnAfter = window.getComputedStyle(btn, '::after');

                return {
                    button: {
                        tag: btn.tagName.toLowerCase(),
                        classes: btn.className,
                        id: btn.id,
                        color: btnStyle.color,
                        fill: btnStyle.fill,
                        afterContent: btnAfter.content,
                        afterColor: btnAfter.color,
                        beforeContent: btnBefore.content,
                        beforeColor: btnBefore.color,
                        html: btn.outerHTML?.substring(0, 400)
                    },
                    descendants: descendants
                };
            }
        ''')

        if 'error' in deep_inspection:
            print(f"ERROR: {deep_inspection['error']}")
        else:
            print("\n--- BUTTON ELEMENT ---")
            btn_info = deep_inspection['button']
            print(f"  Classes: {btn_info['classes']}")
            print(f"  Color: {btn_info['color']}")
            print(f"  ::before content: {btn_info['beforeContent']}")
            print(f"  ::before color: {btn_info['beforeColor']}")
            print(f"  ::after content: {btn_info['afterContent']}")
            print(f"  ::after color: {btn_info['afterColor']}")

            print("\n--- DESCENDANTS ---")
            for desc in deep_inspection['descendants']:
                indent = "  " * (desc['depth'] + 1)
                print(f"\n{indent}[{desc['tag']}]")
                if desc['classes']:
                    print(f"{indent}  Classes: {desc['classes']}")
                if desc['id']:
                    print(f"{indent}  ID: {desc['id']}")
                if desc['text']:
                    print(f"{indent}  Text: {desc['text']}")
                if desc['color'] and desc['color'] != 'rgba(0, 0, 0, 0)':
                    print(f"{indent}  Color: {desc['color']}")
                if desc['fill'] and desc['fill'] != 'none':
                    print(f"{indent}  Fill: {desc['fill']}")
                if desc['stroke'] and desc['stroke'] != 'none':
                    print(f"{indent}  Stroke: {desc['stroke']}")
                if desc['src']:
                    print(f"{indent}  SRC: {desc['src']}")
                if desc['viewBox']:
                    print(f"{indent}  viewBox: {desc['viewBox']}")
                if desc['backgroundImage'] and desc['backgroundImage'] != 'none':
                    print(f"{indent}  BG Image: {desc['backgroundImage']}")
                if desc['beforeContent'] and desc['beforeContent'] != 'none':
                    print(f"{indent}  ::before: {desc['beforeContent']} (color: {desc['beforeColor']})")
                if desc['afterContent'] and desc['afterContent'] != 'none':
                    print(f"{indent}  ::after: {desc['afterContent']} (color: {desc['afterColor']})")
                if desc['fontFamily'] and ('icon' in desc['fontFamily'].lower() or 'awesome' in desc['fontFamily'].lower() or 'eicons' in desc['fontFamily'].lower()):
                    print(f"{indent}  ICON FONT: {desc['fontFamily']}")

                # Show HTML for potential arrow elements
                if 'icon' in desc['classes'].lower() or 'arrow' in desc['classes'].lower() or desc['tag'] == 'svg' or desc['tag'] == 'i':
                    print(f"{indent}  HTML: {desc['html']}")

        # Look specifically for SVG elements inside the button
        print("\n\n[3] Looking for SVG elements anywhere in/near the button...")

        svg_info = await page.evaluate(r'''
            () => {
                const btn = Array.from(document.querySelectorAll('a, button')).find(
                    el => (el.innerText || '').includes('Awaken')
                );
                if (!btn) return { error: 'Button not found' };

                // Look for SVGs within button and siblings
                const svgs = btn.querySelectorAll('svg');
                const results = [];

                svgs.forEach(svg => {
                    const style = window.getComputedStyle(svg);
                    const paths = svg.querySelectorAll('path');
                    const pathData = [];

                    paths.forEach(path => {
                        const pathStyle = window.getComputedStyle(path);
                        pathData.push({
                            d: path.getAttribute('d')?.substring(0, 50),
                            fill: pathStyle.fill,
                            stroke: pathStyle.stroke,
                            color: pathStyle.color
                        });
                    });

                    results.push({
                        classes: svg.className?.baseVal || svg.className || '',
                        viewBox: svg.getAttribute('viewBox'),
                        width: svg.getAttribute('width'),
                        height: svg.getAttribute('height'),
                        fill: style.fill,
                        stroke: style.stroke,
                        color: style.color,
                        paths: pathData,
                        html: svg.outerHTML
                    });
                });

                return results;
            }
        ''')

        if svg_info:
            print(f"\nFound {len(svg_info)} SVG(s) inside the button:")
            for i, svg in enumerate(svg_info):
                print(f"\n--- SVG {i+1} ---")
                print(f"  Classes: {svg['classes']}")
                print(f"  viewBox: {svg['viewBox']}")
                print(f"  Fill: {svg['fill']}")
                print(f"  Stroke: {svg['stroke']}")
                print(f"  Color: {svg['color']}")
                print(f"\n  Full HTML:\n{svg['html']}")
                if svg['paths']:
                    print("\n  Paths:")
                    for j, path in enumerate(svg['paths']):
                        print(f"    Path {j+1}: fill={path['fill']}, stroke={path['stroke']}")
        else:
            print("\nNo SVG elements found inside the button")

        # Check for icon fonts (Font Awesome, Elementor icons)
        print("\n\n[4] Checking for icon font elements (i, span with icon classes)...")

        icon_elements = await page.evaluate(r'''
            () => {
                const btn = Array.from(document.querySelectorAll('a, button')).find(
                    el => (el.innerText || '').includes('Awaken')
                );
                if (!btn) return [];

                const icons = btn.querySelectorAll('i, span[class*="icon"], span[class*="arrow"]');
                const results = [];

                icons.forEach(icon => {
                    const style = window.getComputedStyle(icon);
                    const before = window.getComputedStyle(icon, '::before');

                    results.push({
                        tag: icon.tagName.toLowerCase(),
                        classes: icon.className,
                        color: style.color,
                        fontFamily: style.fontFamily,
                        content: style.content,
                        beforeContent: before.content,
                        beforeColor: before.color,
                        html: icon.outerHTML
                    });
                });

                return results;
            }
        ''')

        if icon_elements:
            print(f"\nFound {len(icon_elements)} icon element(s):")
            for i, icon in enumerate(icon_elements):
                print(f"\n--- Icon {i+1} ---")
                print(f"  Tag: {icon['tag']}")
                print(f"  Classes: {icon['classes']}")
                print(f"  Color: {icon['color']}")
                print(f"  Font Family: {icon['fontFamily']}")
                print(f"  ::before content: {icon['beforeContent']}")
                print(f"  ::before color: {icon['beforeColor']}")
                print(f"  HTML: {icon['html']}")
        else:
            print("\nNo icon font elements found")

        # Get specific Elementor button icon selector
        print("\n\n[5] Checking Elementor-specific button icon structure...")

        elementor_icon = await page.evaluate(r'''
            () => {
                const btn = Array.from(document.querySelectorAll('a, button')).find(
                    el => (el.innerText || '').includes('Awaken')
                );
                if (!btn) return { error: 'Button not found' };

                // Look for .elementor-button-icon specifically
                const iconWrapper = btn.querySelector('.elementor-button-icon');
                if (!iconWrapper) {
                    // Try broader search
                    const anyIcon = btn.querySelector('[class*="icon"]');
                    if (anyIcon) {
                        const style = window.getComputedStyle(anyIcon);
                        return {
                            found: true,
                            selector: anyIcon.className,
                            color: style.color,
                            fill: style.fill,
                            html: anyIcon.outerHTML
                        };
                    }
                    return { found: false, message: 'No icon wrapper found in button' };
                }

                const style = window.getComputedStyle(iconWrapper);
                const children = [];

                Array.from(iconWrapper.children).forEach(child => {
                    const childStyle = window.getComputedStyle(child);
                    children.push({
                        tag: child.tagName.toLowerCase(),
                        classes: child.className?.baseVal || child.className || '',
                        color: childStyle.color,
                        fill: childStyle.fill,
                        stroke: childStyle.stroke,
                        html: child.outerHTML
                    });
                });

                return {
                    found: true,
                    wrapperClasses: iconWrapper.className,
                    wrapperColor: style.color,
                    wrapperFill: style.fill,
                    wrapperHTML: iconWrapper.outerHTML,
                    children: children
                };
            }
        ''')

        print(json.dumps(elementor_icon, indent=2))

        await browser.close()

        print("\n" + "=" * 70)
        print("INSPECTION COMPLETE")
        print("=" * 70)

        return deep_inspection

if __name__ == "__main__":
    import os
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    asyncio.run(inspect_cta_arrow())
