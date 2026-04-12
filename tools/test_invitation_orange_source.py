#!/usr/bin/env python3
"""
Find the exact CSS rule setting body background to orange.
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

        # Find which stylesheet sets body background to orange
        source_search = await page.evaluate("""
        () => {
            const results = [];
            for (const sheet of document.styleSheets) {
                try {
                    const rules = sheet.cssRules || sheet.rules;
                    for (const rule of rules) {
                        if (rule.selectorText &&
                            (rule.selectorText === 'body' || rule.selectorText.includes('body')) &&
                            rule.style &&
                            rule.style.backgroundColor) {
                            results.push({
                                stylesheet: sheet.href || 'inline',
                                selector: rule.selectorText,
                                backgroundColor: rule.style.backgroundColor,
                                background: rule.style.background,
                                fullRule: rule.cssText.substring(0, 300)
                            });
                        }
                    }
                } catch(e) {
                    // Cross-origin stylesheet - skip
                }
            }
            return results;
        }
        """)
        print("CSS rules setting body background:")
        print(json.dumps(source_search, indent=2))

        # Also check inline styles on body
        body_inline = await page.evaluate("""
        () => {
            return {
                inlineStyle: document.body.getAttribute('style'),
                className: document.body.className.substring(0, 200)
            };
        }
        """)
        print("\nBody inline style and class:")
        print(json.dumps(body_inline, indent=2))

        # Check global-styles-inline-css (WordPress global styles)
        wp_global = await page.evaluate("""
        () => {
            const el = document.getElementById('global-styles-inline-css');
            if (!el) return { found: false };
            const content = el.textContent;
            // Find body-related rules
            const bodyRules = content.match(/body[^{]*{[^}]*}/g);
            return {
                found: true,
                bodyRules: bodyRules,
                snippet: content.substring(0, 1000)
            };
        }
        """)
        print("\nWordPress global-styles-inline-css body rules:")
        print(json.dumps(wp_global, indent=2))

        # Check wp-custom-css
        wp_custom = await page.evaluate("""
        () => {
            const el = document.getElementById('wp-custom-css');
            if (!el) return { found: false };
            const content = el.textContent;
            const bodyRules = content.match(/body[^{]*{[^}]*background[^}]*}/g);
            return {
                found: true,
                bodyRules: bodyRules,
                fullContent: content.substring(0, 2000)
            };
        }
        """)
        print("\nWordPress custom CSS body rules:")
        print(json.dumps(wp_custom, indent=2))

        # Check artistic-css-variable (theme variables)
        theme_vars = await page.evaluate("""
        () => {
            // Check all inline style elements for body background rules
            const styles = document.querySelectorAll('style');
            const bodyBgRules = [];
            for (const s of styles) {
                const content = s.textContent;
                if (content.includes('background') && content.includes('body') && content.includes('241')) {
                    bodyBgRules.push({
                        id: s.id,
                        snippet: content.substring(0, 500)
                    });
                }
            }
            return bodyBgRules;
        }
        """)
        print("\nStyle elements containing orange body background (241 in rgb):")
        print(json.dumps(theme_vars, indent=2))

        # What is the elementor_canvas template doing differently?
        # Check if there's a specific class on body causing this
        body_class_analysis = await page.evaluate("""
        () => {
            const bodyClasses = document.body.className.split(' ');
            return {
                classes: bodyClasses,
                hasElementorCanvas: bodyClasses.includes('page-template-elementor_canvas'),
                hasPageId987: bodyClasses.includes('page-id-987')
            };
        }
        """)
        print("\nBody class analysis:")
        print(json.dumps(body_class_analysis, indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
