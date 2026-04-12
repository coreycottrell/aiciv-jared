#!/usr/bin/env python3
"""Capture current state of purebrain.ai pages for before/after comparison."""
import time
import os
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = '/tmp/purebrain-fixes-2026-02-18'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = context.new_page()

    # 1. Category page for-teams
    print('Capturing category/for-teams...')
    page.goto('https://purebrain.ai/category/for-teams/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    page.screenshot(path=f'{SCREENSHOT_DIR}/01_before_category_for_teams.png', full_page=True)

    info = page.evaluate("""() => {
        const body = document.body;
        const cs = getComputedStyle(body);
        const breadcrumb = document.querySelector('.breadcrumb, .breadcrumbs, nav[aria-label*=bread], .starter-breadcrumbs, .starter-breadcrumb');
        const pageHeader = document.querySelector('.page-header, .archive-header, .starter-page-header, .starter-archive-header');
        return {
            bodyClasses: body.className,
            bodyBg: cs.backgroundColor,
            bodyColor: cs.color,
            breadcrumbExists: !!breadcrumb,
            breadcrumbTag: breadcrumb ? breadcrumb.tagName + '.' + breadcrumb.className : 'not found',
            pageHeaderExists: !!pageHeader,
            pageHeaderTag: pageHeader ? pageHeader.tagName + '.' + pageHeader.className : 'not found',
            pageHeaderBg: pageHeader ? getComputedStyle(pageHeader).backgroundColor : 'N/A'
        };
    }""")
    print(f'  Body classes: {info["bodyClasses"]}')
    print(f'  Body bg: {info["bodyBg"]}')
    print(f'  Breadcrumb: {info["breadcrumbTag"]}')
    print(f'  Page header: {info["pageHeaderTag"]}')
    print(f'  Page header bg: {info["pageHeaderBg"]}')

    # 2. Category page for-individuals
    print('\nCapturing category/for-individuals...')
    page.goto('https://purebrain.ai/category/for-individuals/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    page.screenshot(path=f'{SCREENSHOT_DIR}/02_before_category_for_individuals.png', full_page=True)

    # 3. Blog post - scroll to CTA area
    print('\nCapturing blog post CTA area...')
    page.goto('https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    page.screenshot(path=f'{SCREENSHOT_DIR}/03_before_blogpost_top.png', full_page=False)

    # Scroll to bottom to find CTA
    page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)")
    time.sleep(2)
    page.screenshot(path=f'{SCREENSHOT_DIR}/04_before_blogpost_cta_area.png', full_page=False)

    page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.85)")
    time.sleep(2)
    page.screenshot(path=f'{SCREENSHOT_DIR}/05_before_blogpost_bottom.png', full_page=False)

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)
    page.screenshot(path=f'{SCREENSHOT_DIR}/06_before_blogpost_very_bottom.png', full_page=False)

    # Get CTA button info
    cta_info = page.evaluate("""() => {
        // Find CTA button elements
        const buttons = document.querySelectorAll('a.cta-button, .partnership-cta a, a[href*="purebrain"], .cta-section a, a.btn-cta');
        const results = [];
        buttons.forEach(btn => {
            const cs = getComputedStyle(btn);
            results.push({
                tag: btn.tagName,
                text: btn.textContent.trim().substring(0, 60),
                href: btn.href,
                color: cs.color,
                bg: cs.backgroundColor,
                bgImage: cs.backgroundImage,
                display: cs.display,
                visibility: cs.visibility,
                className: btn.className
            });
        });

        // Also find newsletter links
        const newsletters = document.querySelectorAll('a[href*="newsletter"], a[href*="subscribe"]');
        const nlResults = [];
        newsletters.forEach(nl => {
            const cs = getComputedStyle(nl);
            nlResults.push({
                text: nl.textContent.trim().substring(0, 60),
                href: nl.href,
                color: cs.color,
                className: nl.className
            });
        });

        // Find social sharing containers
        const socialContainers = document.querySelectorAll('.social-sharing, .share-buttons, [class*="social-share"], [class*="share-icon"], .post-social-sharing');
        const socialResults = [];
        socialContainers.forEach(sc => {
            const cs = getComputedStyle(sc);
            socialResults.push({
                tag: sc.tagName,
                className: sc.className.substring(0, 80),
                display: cs.display,
                visibility: cs.visibility,
                childCount: sc.children.length,
                innerHTML: sc.innerHTML.substring(0, 200)
            });
        });

        return {
            ctaButtons: results,
            newsletterLinks: nlResults,
            socialContainers: socialResults
        };
    }""")
    print(f'  CTA buttons found: {len(cta_info["ctaButtons"])}')
    for btn in cta_info["ctaButtons"]:
        print(f'    - "{btn["text"]}" color={btn["color"]} bg={btn["bg"]} class={btn["className"]}')
    print(f'  Newsletter links found: {len(cta_info["newsletterLinks"])}')
    for nl in cta_info["newsletterLinks"]:
        print(f'    - "{nl["text"]}" color={nl["color"]}')
    print(f'  Social containers found: {len(cta_info["socialContainers"])}')
    for sc in cta_info["socialContainers"]:
        print(f'    - class={sc["className"]} display={sc["display"]} vis={sc["visibility"]} children={sc["childCount"]}')

    # 4. Full page screenshot of blog post for comprehensive view
    print('\nCapturing full blog post page...')
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    page.screenshot(path=f'{SCREENSHOT_DIR}/07_before_blogpost_fullpage.png', full_page=True)

    # 5. Check what content the blog post has (look for embedded CTA/sharing HTML)
    post_content = page.evaluate("""() => {
        const article = document.querySelector('article, .entry-content, .post-content, .starter-post-content');
        if (!article) return 'No article element found';
        const html = article.innerHTML;
        // Find CTA section
        const ctaIdx = html.indexOf('Start Your AI Partnership');
        if (ctaIdx > -1) {
            return 'CTA_FOUND at index ' + ctaIdx + ': ' + html.substring(Math.max(0, ctaIdx-200), ctaIdx+300);
        }
        // Find newsletter
        const nlIdx = html.indexOf('newsletter');
        if (nlIdx > -1) {
            return 'NEWSLETTER_FOUND at index ' + nlIdx + ': ' + html.substring(Math.max(0, nlIdx-200), nlIdx+200);
        }
        return 'Article length: ' + html.length + ' first 500: ' + html.substring(0, 500);
    }""")
    print(f'\n  Post content analysis: {post_content[:500]}')

    browser.close()
    print('\nAll before screenshots saved.')
