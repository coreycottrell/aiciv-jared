#!/usr/bin/env python3
"""Directly inspect the CTA button element and its CSS resolution."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    // Find CTA link by text
    const links = document.querySelectorAll('a');
    let cta = null;
    for (const link of links) {
        if (link.textContent.includes('Start Your AI Partnership')) {
            cta = link;
            break;
        }
    }
    if (!cta) return {error: 'CTA not found'};

    // Build the element's ancestor chain
    let ancestors = [];
    let el = cta;
    while (el) {
        ancestors.push({
            tag: el.tagName,
            id: el.id || '',
            class: el.className ? (typeof el.className === 'string' ? el.className.substring(0, 80) : '') : '',
            color: getComputedStyle(el).color,
            inlineColor: el.style ? el.style.color : ''
        });
        el = el.parentElement;
    }

    // Check if cta is inside entry-meta or cat-links
    const inEntryMeta = !!cta.closest('.entry-meta');
    const inCatLinks = !!cta.closest('.cat-links');

    // Check the CTA's parent p element
    const parentP = cta.parentElement;
    const parentPStyle = parentP ? parentP.getAttribute('style') : 'N/A';
    const parentPComputed = parentP ? getComputedStyle(parentP).color : 'N/A';

    // Try to test the rule directly
    // Temporarily add a test class and check
    const testResult = {};

    // Check if the CTA is inside a div that has a matching color rule
    const ctaParentDiv = cta.closest('div');
    if (ctaParentDiv) {
        testResult.closestDiv = {
            class: ctaParentDiv.className ? ctaParentDiv.className.substring(0, 80) : '',
            color: getComputedStyle(ctaParentDiv).color,
            inlineStyle: (ctaParentDiv.getAttribute('style') || '').substring(0, 100)
        };
    }

    // The actual test: what color does the CTA have?
    // Check with getComputedStyle
    const computed = getComputedStyle(cta);

    // Check if inline style is being overridden
    testResult.inlineStyleAttr = cta.getAttribute('style');
    testResult.inlineStyleColor = cta.style.color;
    testResult.computedColor = computed.color;
    testResult.computedBg = computed.backgroundColor;
    testResult.computedBgImage = computed.backgroundImage;

    // Force set via JS and check
    const origColor = cta.style.color;
    cta.style.setProperty('color', '#00ff00', 'important');
    testResult.afterForceGreen = getComputedStyle(cta).color;
    cta.style.color = origColor; // restore

    return {
        inEntryMeta: inEntryMeta,
        inCatLinks: inCatLinks,
        ancestors: ancestors.reverse(),
        parentP: {
            style: parentPStyle,
            computed: parentPComputed
        },
        test: testResult
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
        print(f"In entry-meta: {result['inEntryMeta']}")
        print(f"In cat-links: {result['inCatLinks']}")

        print(f"\n=== Ancestor Chain ===")
        for a in result['ancestors']:
            tag = a['tag']
            cls = a['class'][:50] if a['class'] else ''
            color = a['color']
            inline = a['inlineColor']
            print(f"  <{tag} class='{cls}'> color={color} inline={inline}")

        print(f"\n=== Parent <p> ===")
        print(f"  Style: {result['parentP']['style']}")
        print(f"  Computed: {result['parentP']['computed']}")

        print(f"\n=== CTA Element ===")
        t = result['test']
        print(f"  Inline style attr: {t['inlineStyleAttr'][:100]}...")
        print(f"  inline.style.color: {t['inlineStyleColor']}")
        print(f"  Computed color: {t['computedColor']}")
        print(f"  Computed bg: {t['computedBg']}")
        print(f"  After force green !important: {t['afterForceGreen']}")
        print(f"  Closest div: {t.get('closestDiv', 'N/A')}")

    browser.close()
