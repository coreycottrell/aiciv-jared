#!/usr/bin/env python3
"""
Check pb-aether-footer-v460 content and find what in wp-custom-css has orange+body.
Also check the artistics/style.css body rule which uses --e-global-color-black.
"""

import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/invitation/"
PASSWORD = "purebrain25"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except:
            pass
        await page.wait_for_timeout(2000)

        pw = await page.query_selector("input[type='password']")
        if pw:
            await pw.fill(PASSWORD)
            sub = await page.query_selector("input[type='submit']")
            if sub:
                await sub.click()
            await page.wait_for_timeout(10000)
        await page.wait_for_timeout(3000)

        # Check pb-aether-footer content
        footer_css = await page.evaluate("""
        () => {
            const el = document.getElementById('pb-aether-footer-v460');
            return el ? el.textContent : null;
        }
        """)
        print("pb-aether-footer-v460 CSS:")
        print(footer_css)

        # Check what wp-custom-css contains around f1420b + body
        wp_orange_body = await page.evaluate("""
        () => {
            const el = document.getElementById('wp-custom-css');
            if (!el) return null;
            const content = el.textContent;
            // Find all occurrences of f1420b
            const results = [];
            let idx = 0;
            while (true) {
                const found = content.indexOf('f1420b', idx);
                if (found === -1) break;
                // Get surrounding context
                const start = Math.max(0, found - 200);
                const end = Math.min(content.length, found + 200);
                const ctx = content.substring(start, end);
                if (ctx.includes('body') || ctx.includes(':root')) {
                    results.push({ position: found, context: ctx });
                }
                idx = found + 1;
            }
            return results.slice(0, 5);
        }
        """)
        print("\nwp-custom-css sections with f1420b near body/:root:")
        if wp_orange_body:
            for r in wp_orange_body:
                print(f"\n  Position {r['position']}:")
                print(f"  {r['context']}")

        # DEFINITIVE: Get the actual CSS text from artistics/style.css body rule
        artistics_body = await page.evaluate("""
        () => {
            for (const sheet of document.styleSheets) {
                if (sheet.href && sheet.href.includes('artistics/style.css')) {
                    try {
                        for (const rule of sheet.cssRules) {
                            if (rule.selectorText === 'body') {
                                return rule.cssText.substring(0, 500);
                            }
                        }
                    } catch(e) { return 'error: ' + e.message; }
                }
            }
            return 'not found';
        }
        """)
        print("\nartistics/style.css body rule:")
        print(artistics_body)

        # What does --e-global-color-black resolve to on the BODY (not root)?
        # This is key - the artistics theme may use --e-global-color-black which resolves differently on body
        body_black_var = await page.evaluate("""
        () => {
            // Use a temp element to check what --e-global-color-black computes to
            const temp = document.createElement('div');
            document.body.appendChild(temp);
            temp.style.backgroundColor = 'var(--e-global-color-black)';
            const computed = window.getComputedStyle(temp).backgroundColor;
            document.body.removeChild(temp);
            return computed;
        }
        """)
        print("\n--e-global-color-black computed value on body element:")
        print(body_black_var)

        # Check Elementor frontend CSS (not the kit file - the actual frontend)
        elementor_css_check = await page.evaluate("""
        () => {
            for (const sheet of document.styleSheets) {
                const href = sheet.href || '';
                if (href.includes('elementor')) {
                    try {
                        const rules = Array.from(sheet.cssRules || []);
                        const rootRules = rules.filter(r => r.selectorText === ':root');
                        if (rootRules.length > 0) {
                            return {
                                href: href,
                                rootRules: rootRules.map(r => r.cssText.substring(0, 500))
                            };
                        }
                    } catch(e) {
                        return { href: href, error: e.message };
                    }
                }
            }
            return null;
        }
        """)
        print("\nElementor frontend CSS :root rules:")
        print(json.dumps(elementor_css_check, indent=2))

        # Check artistics/css-variable.css which sets --e-global-color-black
        css_var_file = await page.evaluate("""
        () => {
            for (const sheet of document.styleSheets) {
                if (sheet.href && sheet.href.includes('css-variable')) {
                    try {
                        const rules = Array.from(sheet.cssRules || []);
                        return {
                            href: sheet.href,
                            rules: rules.map(r => r.cssText.substring(0, 500))
                        };
                    } catch(e) {
                        return { href: sheet.href, error: e.message };
                    }
                }
            }
            return null;
        }
        """)
        print("\ncss-variable.css content:")
        print(json.dumps(css_var_file, indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
