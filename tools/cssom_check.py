#!/usr/bin/env python3
"""Check CSSOM parsing of wp-custom-css."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    const style = document.querySelector('style#wp-custom-css');
    if (!style || !style.sheet) return {error: 'no sheet'};

    const sheet = style.sheet;
    const rules = sheet.cssRules;

    // Find rule 43 (body.single-post a)
    let rule43 = null;
    if (rules.length > 43) {
        const r = rules[43];
        rule43 = {
            type: r.type,
            selectorText: r.selectorText,
            color: r.style ? r.style.color : 'N/A',
            priority: r.style ? r.style.getPropertyPriority('color') : 'N/A',
            cssText: r.cssText ? r.cssText.substring(0, 300) : 'N/A'
        };
    }

    // List ALL rules from 40 to 50
    let rules40to50 = [];
    for (let i = Math.max(0, 40); i < Math.min(rules.length, 55); i++) {
        const r = rules[i];
        rules40to50.push({
            idx: i,
            type: r.type,
            selectorText: r.selectorText || 'N/A',
            colorProp: r.style ? r.style.color : 'N/A',
            colorPriority: r.style ? r.style.getPropertyPriority('color') : 'N/A',
            firstLine: r.cssText ? r.cssText.substring(0, 150) : 'N/A'
        });
    }

    // Check total parsed rules count
    const totalParsed = rules.length;

    // Check for any @media rules that might contain the body.single-post a rule
    let mediaRules = [];
    for (let i = 0; i < rules.length; i++) {
        const r = rules[i];
        if (r.type === CSSRule.MEDIA_RULE) {
            // Check inner rules
            for (let j = 0; j < r.cssRules.length; j++) {
                const inner = r.cssRules[j];
                if (inner.selectorText && inner.selectorText.includes('single-post') && inner.style && inner.style.color) {
                    mediaRules.push({
                        outerIdx: i,
                        mediaText: r.conditionText || r.media.mediaText,
                        innerIdx: j,
                        selector: inner.selectorText.substring(0, 100),
                        color: inner.style.color,
                        priority: inner.style.getPropertyPriority('color')
                    });
                }
            }
        }
    }

    // Try manually applying the color
    const links = document.querySelectorAll('a');
    let cta = null;
    for (const link of links) {
        if (link.textContent.includes('Start Your AI Partnership')) {
            cta = link;
            break;
        }
    }

    let ctaTest = {};
    if (cta) {
        ctaTest.before = getComputedStyle(cta).color;

        // Force via a new high-specificity style
        const newStyle = document.createElement('style');
        newStyle.textContent = 'body.single-post .blog-cta-block a { color: #00ff00 !important; }';
        document.head.appendChild(newStyle);
        ctaTest.afterNewStyle = getComputedStyle(cta).color;
        newStyle.remove();

        // Force via even higher specificity
        const newStyle2 = document.createElement('style');
        newStyle2.textContent = 'body.wp-singular.single.single-post .page-single-post .post-content .post-entry .blog-cta-block p a[href*="purebrain-4"] { color: #00ff00 !important; }';
        document.head.appendChild(newStyle2);
        ctaTest.afterVerySpecific = getComputedStyle(cta).color;
        newStyle2.remove();
    }

    return {
        totalParsedRules: totalParsed,
        rule43: rule43,
        rules40to50: rules40to50,
        mediaRules: mediaRules,
        ctaTest: ctaTest
    };
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    result = page.evaluate(JS_CODE)

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Total parsed rules: {result['totalParsedRules']}")

        print(f"\n=== Rule 43 ===")
        print(f"  {result['rule43']}")

        print(f"\n=== Rules 40-54 ===")
        for r in result['rules40to50']:
            print(f"  [{r['idx']}] type={r['type']} sel='{r['selectorText']}' color={r['colorProp']} priority={r['colorPriority']}")

        print(f"\n=== @media rules with single-post + color ===")
        for r in result['mediaRules']:
            print(f"  @media({r['mediaText']}) outer[{r['outerIdx']}] inner[{r['innerIdx']}]: {r['selector']} color={r['color']} {r['priority']}")

        print(f"\n=== CTA Color Test ===")
        ct = result.get('ctaTest', {})
        print(f"  Before: {ct.get('before')}")
        print(f"  After new style (.blog-cta-block a): {ct.get('afterNewStyle')}")
        print(f"  After very specific selector: {ct.get('afterVerySpecific')}")

    browser.close()
