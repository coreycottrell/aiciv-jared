#!/usr/bin/env python3
"""
Find what --e-global-color-black resolves to, and find the exact winning CSS rule for body background.
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

        # Resolve --e-global-color-black
        color_vars = await page.evaluate("""
        () => {
            const rootStyle = window.getComputedStyle(document.documentElement);
            const bodyStyle = window.getComputedStyle(document.body);
            return {
                eGlobalColorBlack: rootStyle.getPropertyValue('--e-global-color-black').trim(),
                eGlobalColorText: rootStyle.getPropertyValue('--e-global-color-text').trim(),
                bsBodyBg: rootStyle.getPropertyValue('--bs-body-bg').trim(),
                bsBodyBgRgb: rootStyle.getPropertyValue('--bs-body-bg-rgb').trim(),
                // also check on body
                bodyEGlobalColorBlack: bodyStyle.getPropertyValue('--e-global-color-black').trim(),
                // What does computed backgroundColor on body actually compute to?
                bodyComputedBg: bodyStyle.backgroundColor
            };
        }
        """)
        print("CSS custom property values:")
        print(json.dumps(color_vars, indent=2))

        # Check if the plugin's `body { background: none rgb(10,14,26) !important }` rule
        # is actually being applied by checking which stylesheet wins
        winning_rule = await page.evaluate("""
        () => {
            // Use getComputedStyle to see what wins
            const bodyBg = window.getComputedStyle(document.body).backgroundColor;

            // Scan ALL stylesheets for body background rules, ordered by specificity
            const rules = [];
            let sheetIndex = 0;
            for (const sheet of document.styleSheets) {
                try {
                    const cssRules = sheet.cssRules || sheet.rules;
                    let ruleIndex = 0;
                    for (const rule of cssRules) {
                        if (rule.selectorText === 'body' && rule.style && rule.style.background) {
                            rules.push({
                                sheetIndex,
                                ruleIndex,
                                href: sheet.href ? sheet.href.split('/').slice(-2).join('/') : 'inline',
                                selector: rule.selectorText,
                                background: rule.style.background,
                                backgroundColor: rule.style.backgroundColor,
                                important: rule.cssText.includes('!important'),
                                cssText: rule.cssText.substring(0, 200)
                            });
                        }
                        ruleIndex++;
                    }
                } catch(e) {}
                sheetIndex++;
            }
            return { computedBodyBg: bodyBg, bodyRules: rules };
        }
        """)
        print("\nAll 'body' CSS rules (bare selector only):")
        print(json.dumps(winning_rule, indent=2))

        # Check Elementor kit stylesheet specifically
        kit_check = await page.evaluate("""
        () => {
            const results = {};
            for (const sheet of document.styleSheets) {
                const href = sheet.href || '';
                if (href.includes('elementor') || href.includes('kit')) {
                    try {
                        const rules = sheet.cssRules || sheet.rules;
                        const bodyRules = Array.from(rules).filter(r =>
                            r.selectorText && (r.selectorText === 'body' || r.selectorText === ':root')
                        );
                        if (bodyRules.length > 0) {
                            results[href.split('/').slice(-2).join('/')] = bodyRules.map(r => r.cssText.substring(0, 300));
                        }
                    } catch(e) {}
                }
            }
            return results;
        }
        """)
        print("\nElementor kit stylesheet body/:root rules:")
        print(json.dumps(kit_check, indent=2))

        # Find what's in global-styles-inline-css that has color 241 (orange)
        global_styles = await page.evaluate("""
        () => {
            const el = document.getElementById('global-styles-inline-css');
            if (!el) return { found: false };
            const content = el.textContent;
            // Find all rules
            const lines = content.split('\\n');
            const orangeLines = lines.filter(l =>
                l.includes('241') || l.includes('f1420b') || l.includes('F1420B') ||
                l.includes('e-global-color')
            );
            return {
                found: true,
                totalLength: content.length,
                orangeLines: orangeLines.slice(0, 30),
                // First 3000 chars
                snippet: content.substring(0, 3000)
            };
        }
        """)
        print("\nglobal-styles-inline-css orange-related lines:")
        print(json.dumps(global_styles, indent=2))

        # Check if the plugin CSS (starter-starter rule) is actually in the page
        plugin_css = await page.evaluate("""
        () => {
            const styles = document.querySelectorAll('style');
            for (const s of styles) {
                if (s.textContent.includes('starter-starter') && s.textContent.includes('10, 14, 26')) {
                    return {
                        found: true,
                        id: s.id,
                        contentSnippet: s.textContent.substring(0, 500)
                    };
                }
            }
            return { found: false };
        }
        """)
        print("\nPlugin starter-starter CSS rule:")
        print(json.dumps(plugin_css, indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
