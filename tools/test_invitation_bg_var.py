#!/usr/bin/env python3
"""
Find exactly what --bg resolves to, where it's defined, and what the page CSS looks like.
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

        # Find what --bg is set to
        bg_var = await page.evaluate("""
        () => {
            const rootStyle = window.getComputedStyle(document.documentElement);
            const bodyStyle = window.getComputedStyle(document.body);
            return {
                rootBgVar: rootStyle.getPropertyValue('--bg').trim(),
                bodyBgVar: bodyStyle.getPropertyValue('--bg').trim(),
                // Also check --color-bg, --color-background etc
                colorBg: rootStyle.getPropertyValue('--color-bg').trim(),
                background: rootStyle.getPropertyValue('--background').trim(),
                // Check all CSS variables that might be orange
                allVarsWithOrange: (() => {
                    const allVars = {};
                    // Scan :root CSS rules for --bg
                    for (const sheet of document.styleSheets) {
                        try {
                            for (const rule of sheet.cssRules) {
                                if (rule.selectorText === ':root' && rule.style) {
                                    const bg = rule.style.getPropertyValue('--bg');
                                    if (bg) allVars['--bg in :root'] = bg;
                                }
                                if (rule.selectorText === 'body' && rule.style) {
                                    const bg = rule.style.getPropertyValue('--bg');
                                    if (bg) allVars['--bg in body'] = bg;
                                }
                            }
                        } catch(e) {}
                    }
                    return allVars;
                })()
            };
        }
        """)
        print("--bg variable resolution:")
        print(json.dumps(bg_var, indent=2))

        # Find the style block that defines --bg
        bg_definition = await page.evaluate("""
        () => {
            const styles = document.querySelectorAll('style');
            const results = [];
            for (const s of styles) {
                if (s.textContent.includes('--bg')) {
                    const content = s.textContent;
                    // Find lines with --bg
                    const lines = content.split(';').filter(l => l.includes('--bg'));
                    results.push({
                        id: s.id,
                        bgLines: lines.slice(0, 10),
                        snippet: content.substring(0, 1000)
                    });
                }
            }
            return results;
        }
        """)
        print("\nStyle elements defining --bg:")
        for r in bg_definition:
            print(f"\n  id={r['id']}")
            print(f"  bg lines: {r['bgLines']}")
            print(f"  snippet: {r['snippet'][:500]}")

        # Find the inline style block that contains `body { background: var(--bg)`
        body_rule_source = await page.evaluate("""
        () => {
            const styles = document.querySelectorAll('style');
            for (const s of styles) {
                if (s.textContent.includes('var(--bg)') && s.textContent.includes('body')) {
                    return {
                        id: s.id,
                        fullContent: s.textContent
                    };
                }
            }
            return null;
        }
        """)
        if body_rule_source:
            print(f"\nStyle block with 'body {{ background: var(--bg) }}':")
            print(f"  id: {body_rule_source['id']}")
            print(f"  FULL CONTENT:\n{body_rule_source['fullContent']}")
        else:
            print("\nNo style block found with var(--bg) in body rule")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
