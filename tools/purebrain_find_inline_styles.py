#!/usr/bin/env python3
"""
Find inline styles causing orange text on PureBrain
"""

import asyncio
from playwright.async_api import async_playwright

async def find_inline_styles():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("FINDING INLINE STYLES")
        print("=" * 60)

        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        # Find elements with inline orange color
        print("\n[1] Finding elements with inline orange color...")

        inline_orange = await page.evaluate(r'''
            () => {
                const results = [];
                document.querySelectorAll('*').forEach(el => {
                    const inlineColor = el.style.color;
                    const cssText = el.style.cssText;

                    // Check for orange in inline style
                    if (inlineColor && (inlineColor.includes('241') || inlineColor.includes('f1420b') || inlineColor.includes('#f1'))) {
                        results.push({
                            tag: el.tagName,
                            id: el.id || '',
                            classes: el.className?.substring?.(0, 60) || '',
                            inlineColor: inlineColor,
                            text: el.innerText?.substring?.(0, 40) || ''
                        });
                    }
                    // Also check cssText
                    if (cssText && (cssText.includes('241') || cssText.includes('f1420b'))) {
                        results.push({
                            tag: el.tagName,
                            id: el.id || '',
                            classes: el.className?.substring?.(0, 60) || '',
                            inlineStyle: cssText,
                            text: el.innerText?.substring?.(0, 40) || ''
                        });
                    }
                });
                return results.slice(0, 20);
            }
        ''')

        print(f"\nFound {len(inline_orange)} elements with inline orange styles:")
        for el in inline_orange:
            print(f"\n  {el['tag']} #{el['id'] or '(no id)'}")
            print(f"    Classes: {el['classes']}")
            if 'inlineColor' in el:
                print(f"    Inline color: {el['inlineColor']}")
            if 'inlineStyle' in el:
                print(f"    Inline CSS: {el['inlineStyle']}")
            print(f"    Text: {el['text']}")

        # Find the style tags that might contain the orange color definition
        print("\n[2] Finding <style> tags with orange color...")

        style_tags = await page.evaluate(r'''
            () => {
                const results = [];
                document.querySelectorAll('style').forEach((style, i) => {
                    const content = style.textContent;
                    if (content.includes('f1420b') || content.includes('241, 66, 11') || content.includes('rgb(241')) {
                        // Find the actual rules
                        const lines = content.split('\n').filter(line =>
                            line.includes('f1420b') || line.includes('241') && line.includes('66') && line.includes('11')
                        );
                        results.push({
                            index: i,
                            id: style.id || '',
                            relevantRules: lines.slice(0, 10)
                        });
                    }
                });
                return results;
            }
        ''')

        print(f"\nFound {len(style_tags)} style tags with orange definitions:")
        for st in style_tags:
            print(f"\n  <style> #{st['index']}")
            print(f"    ID: {st['id'] or '(none)'}")
            for rule in st['relevantRules'][:5]:
                print(f"    Rule: {rule[:100]}")

        # Check computed styles for specific elements
        print("\n[3] Checking computed styles for key elements...")

        elements_to_check = [
            "p.hero__description",
            ".section__badge",
            ".exit-popup__text",
            ".waitlist-modal__badge",
            "body"
        ]

        for selector in elements_to_check:
            try:
                el = page.locator(selector).first
                if await el.count() > 0:
                    computed = await el.evaluate('''
                        el => {
                            const style = window.getComputedStyle(el);
                            return {
                                color: style.color,
                                colorImportant: el.style.getPropertyPriority('color'),
                                cssRules: Array.from(document.styleSheets).flatMap(sheet => {
                                    try {
                                        return Array.from(sheet.cssRules || [])
                                            .filter(rule => rule.selectorText && rule.cssText.includes('hero__description'))
                                            .map(rule => rule.cssText.substring(0, 100));
                                    } catch(e) {
                                        return [];
                                    }
                                }).slice(0, 3)
                            };
                        }
                    ''')
                    print(f"\n  {selector}:")
                    print(f"    Computed color: {computed['color']}")
                    print(f"    Has !important: {computed['colorImportant']}")
            except Exception as e:
                print(f"\n  {selector}: Error - {e}")

        # Check if there's a CSS custom property being used
        print("\n[4] Checking for CSS custom properties (variables)...")

        css_vars = await page.evaluate(r'''
            () => {
                const style = getComputedStyle(document.documentElement);
                const vars = [];
                for (let name of ['--e-global-color-primary', '--e-global-color-secondary', '--e-global-color-text', '--primary-color', '--text-color', '--brand-orange']) {
                    const value = style.getPropertyValue(name);
                    if (value && value.includes('241')) {
                        vars.push({name, value});
                    }
                }
                return vars;
            }
        ''')

        print(f"\nCSS variables with orange:")
        for v in css_vars:
            print(f"  {v['name']}: {v['value']}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_inline_styles())
