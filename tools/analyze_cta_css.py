#!/usr/bin/env python3
"""Analyze CSS rules overriding CTA button and newsletter link colors."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    // Find CTA link
    const links = document.querySelectorAll('a');
    let cta = null;
    let nl = null;
    for (const link of links) {
        if (link.textContent.includes('Start Your AI Partnership')) cta = link;
        if (link.textContent.includes('subscribe to our newsletter')) nl = link;
    }

    const result = {};

    if (cta) {
        const cs = getComputedStyle(cta);
        result.ctaText = cta.textContent.trim();
        result.ctaInlineStyle = cta.getAttribute('style');
        result.ctaComputedColor = cs.color;
        result.ctaComputedBg = cs.backgroundColor;
        result.ctaComputedBgImage = cs.backgroundImage;
    } else {
        result.ctaText = 'NOT FOUND';
    }

    if (nl) {
        const cs = getComputedStyle(nl);
        result.nlText = nl.textContent.trim();
        result.nlInlineStyle = nl.getAttribute('style');
        result.nlComputedColor = cs.color;
    } else {
        result.nlText = 'NOT FOUND';
    }

    result.bodyColor = getComputedStyle(document.body).color;

    // Find CSS rules that force color on links within article/entry-content
    let matchingRules = [];
    try {
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.selectorText && rule.style && rule.style.color) {
                        const sel = rule.selectorText;
                        const color = rule.style.color;
                        // Look for rules affecting links in single-post context
                        if (sel.includes('single-post') && sel.includes('a') && !sel.includes('nav')) {
                            matchingRules.push({
                                selector: sel.substring(0, 150),
                                color: color,
                                important: rule.cssText.includes('important')
                            });
                        }
                        // Also check for general link color overrides with important
                        if (rule.cssText.includes('important') && color.includes('241')) {
                            matchingRules.push({
                                selector: sel.substring(0, 150),
                                color: color,
                                important: true
                            });
                        }
                    }
                }
            } catch(e) { /* cross-origin */ }
        }
    } catch(e) {
        matchingRules.push({error: e.message});
    }

    result.matchingRules = matchingRules;

    // Check wp-custom-css specifically
    const customCssEl = document.querySelector('style#wp-custom-css');
    if (customCssEl) {
        const cssText = customCssEl.textContent;
        result.customCssLength = cssText.length;
        // Find rules mentioning color and single-post or a
        const lines = cssText.split('\\n');
        let relevantLines = [];
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('single-post') && (lines[i].includes('color') || lines[i].includes('a '))) {
                relevantLines.push({line: i, text: lines[i].trim().substring(0, 120)});
            }
        }
        result.customCssRelevantLines = relevantLines.slice(0, 30);
    } else {
        result.customCssLength = 'NOT FOUND';
    }

    // Check the entry-content link color specifically
    const entryContent = document.querySelector('.entry-content, .starter-entry-content, article .post-content');
    if (entryContent) {
        const links = entryContent.querySelectorAll('a');
        result.entryContentLinkCount = links.length;
        result.entryContentLinkSample = Array.from(links).slice(0, 5).map(l => ({
            text: l.textContent.trim().substring(0, 40),
            color: getComputedStyle(l).color,
            href: l.href.substring(0, 60)
        }));
    }

    return result;
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    page.goto("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    result = page.evaluate(JS_CODE)

    print("=== CTA Button Analysis ===")
    print(f"  Text: {result.get('ctaText')}")
    print(f"  Inline style: {result.get('ctaInlineStyle', 'N/A')}")
    print(f"  Computed color: {result.get('ctaComputedColor')}")
    print(f"  Computed bg: {result.get('ctaComputedBg')}")
    print(f"  Computed bg-image: {result.get('ctaComputedBgImage')}")

    print(f"\n=== Newsletter Link Analysis ===")
    print(f"  Text: {result.get('nlText')}")
    print(f"  Inline style: {result.get('nlInlineStyle', 'N/A')}")
    print(f"  Computed color: {result.get('nlComputedColor')}")

    print(f"\n=== Body ===")
    print(f"  Body color: {result.get('bodyColor')}")

    print(f"\n=== Custom CSS ===")
    print(f"  Length: {result.get('customCssLength')}")
    print(f"  Relevant lines:")
    for line in result.get('customCssRelevantLines', []):
        print(f"    Line {line['line']}: {line['text']}")

    print(f"\n=== Entry Content Links ===")
    print(f"  Count: {result.get('entryContentLinkCount')}")
    for link in result.get('entryContentLinkSample', []):
        print(f"    '{link['text']}' color={link['color']}")

    print(f"\n=== Matching CSS Rules ({len(result.get('matchingRules', []))}) ===")
    for rule in result.get('matchingRules', []):
        print(f"  {rule}")

    browser.close()
