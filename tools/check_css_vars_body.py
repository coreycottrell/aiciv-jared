#!/usr/bin/env python3
"""Check CSS variables defined on body and their sources."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    const body = document.body;
    const bodyCS = getComputedStyle(body);

    // Get all --e-global-color variables from body
    const vars = {};
    const important_vars = [
        '--e-global-color-primary',
        '--e-global-color-secondary',
        '--e-global-color-text',
        '--e-global-color-accent',
        '--e-global-color-accentsecondary',
        '--e-global-color-black',
        '--e-global-color-white'
    ];

    for (const v of important_vars) {
        vars[v] = bodyCS.getPropertyValue(v).trim();
    }

    // Also check on :root / html
    const rootCS = getComputedStyle(document.documentElement);
    const rootVars = {};
    for (const v of important_vars) {
        rootVars[v] = rootCS.getPropertyValue(v).trim();
    }

    // Find ALL style elements/sheets that define --e-global-color-accent
    let sources = [];
    for (const sheet of document.styleSheets) {
        try {
            for (const rule of sheet.cssRules) {
                if (!rule.style) continue;
                const cssText = rule.style.cssText;
                if (cssText.includes('--e-global-color-accent')) {
                    sources.push({
                        selector: rule.selectorText ? rule.selectorText.substring(0, 100) : 'N/A',
                        sheet: sheet.href ? sheet.href.split('/').pop().substring(0, 60) : (sheet.ownerNode ? sheet.ownerNode.id : 'inline'),
                        cssText: cssText.substring(0, 300)
                    });
                }
            }
        } catch(e) {}
    }

    // Also check the Elementor Kit CSS that may be embedded
    let elementorKitCSS = [];
    for (const el of document.querySelectorAll('style')) {
        const text = el.textContent;
        if (text.includes('elementor-kit') || text.includes('--e-global-color')) {
            const idx = text.indexOf('--e-global-color-accent');
            if (idx > -1) {
                elementorKitCSS.push({
                    id: el.id || 'no-id',
                    snippet: text.substring(Math.max(0, idx-100), idx+100)
                });
            }
        }
    }

    // Check which color the .post-entry a actually resolves to
    // Create a test element
    const postEntry = document.querySelector('.post-entry');
    let testColor = 'no .post-entry found';
    if (postEntry) {
        const testLink = document.createElement('a');
        testLink.href = '#test';
        testLink.textContent = 'TEST';
        testLink.style.cssText = '';  // no inline style
        postEntry.appendChild(testLink);
        testColor = getComputedStyle(testLink).color;
        testLink.remove();
    }

    return {
        bodyVars: vars,
        rootVars: rootVars,
        sources: sources,
        elementorKitCSS: elementorKitCSS,
        postEntryTestLinkColor: testColor,
        bodyColor: bodyCS.color,
        bodyBg: bodyCS.backgroundColor
    };
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    result = page.evaluate(JS_CODE)

    print("=== Body CSS Variables ===")
    for k, v in result['bodyVars'].items():
        print(f"  {k}: '{v}'")

    print(f"\n=== Root CSS Variables ===")
    for k, v in result['rootVars'].items():
        print(f"  {k}: '{v}'")

    print(f"\n=== Sources defining --e-global-color-accent ===")
    for s in result['sources']:
        print(f"  [{s['sheet']}] {s['selector']}")
        print(f"    {s['cssText'][:200]}")

    print(f"\n=== Elementor Kit inline styles ===")
    for e in result['elementorKitCSS']:
        print(f"  [{e['id']}]: ...{e['snippet']}...")

    print(f"\n=== Test link in .post-entry color: {result['postEntryTestLinkColor']}")
    print(f"Body color: {result['bodyColor']}")
    print(f"Body background: {result['bodyBg']}")

    browser.close()
