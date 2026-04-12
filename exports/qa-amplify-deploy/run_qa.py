"""
Visual QA script for PureBrain.ai pages:
1. purebrain.ai/your-ai-tim-cook/ (page 993)
2. purebrain.ai/pitch/ (page 1001)

Tests: image presence, layout, CTA links, dark theme, no orange bleed
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/qa-amplify-deploy")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RESULTS = []

def log(msg):
    print(msg)
    RESULTS.append(msg)

async def scroll_to_reveal(page):
    """Trigger scroll-reveal animations by scrolling down incrementally."""
    height = await page.evaluate("document.body.scrollHeight")
    for y in range(0, height, 300):
        await page.evaluate(f"window.scrollTo(0, {y})")
        await asyncio.sleep(0.05)
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)

async def take_screenshot(page, name, full_page=True):
    path = OUTPUT_DIR / f"{name}.png"
    await page.screenshot(path=str(path), full_page=full_page)
    log(f"  [screenshot] {path}")
    return path

async def check_background(page):
    """Return body background color."""
    bg = await page.evaluate("window.getComputedStyle(document.body).backgroundColor")
    return bg

async def check_images(page, expected_srcs):
    """Check images are present and loaded (not broken)."""
    results = {}
    all_imgs = await page.evaluate("""
        Array.from(document.querySelectorAll('img')).map(img => ({
            src: img.src,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
            alt: img.alt,
            complete: img.complete
        }))
    """)
    for expected in expected_srcs:
        found = None
        for img in all_imgs:
            if expected.lower() in img['src'].lower():
                found = img
                break
        results[expected] = {
            'found': found is not None,
            'loaded': found is not None and found['naturalWidth'] > 0,
            'src': found['src'] if found else None
        }
    return results, all_imgs

async def check_ctas(page):
    """Check all CTA buttons/links point to #awakening."""
    links = await page.evaluate("""
        Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim(),
            href: a.href
        })).filter(l => l.text && l.href)
    """)
    awakening_links = [l for l in links if '#awakening' in l['href']]
    other_links = [l for l in links if '#awakening' not in l['href'] and l['href'] and 'mailto:' not in l['href']]
    return awakening_links, other_links

async def get_console_errors(page):
    """Return list of console errors collected."""
    return []  # errors are collected via event listener below

async def test_tim_cook_page(browser):
    log("\n" + "="*60)
    log("PAGE 1: purebrain.ai/your-ai-tim-cook/ (page 993)")
    log("="*60)

    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    console_errors = []
    page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
    page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {str(err)}"))

    log("\n  Navigating to https://purebrain.ai/your-ai-tim-cook/ ...")
    await page.goto("https://purebrain.ai/your-ai-tim-cook/", wait_until="networkidle", timeout=60000)
    await asyncio.sleep(3)

    # 1. Check background (no orange bleed)
    bg = await check_background(page)
    log(f"\n  [1] Background color: {bg}")
    if "255, 65, 11" in bg or "241, 66, 11" in bg or "orange" in bg.lower():
        log("  [FAIL] Orange background detected!")
    else:
        log("  [PASS] No orange background bleed")

    # 2. Scroll to reveal all sections
    log("\n  [2] Scrolling to reveal all sections...")
    await scroll_to_reveal(page)
    await asyncio.sleep(1)

    # 3. Check hero headline
    hero_text = await page.evaluate("""
        (() => {
            const h1 = document.querySelector('h1');
            const h2 = document.querySelector('h2');
            return {
                h1: h1 ? h1.innerText.trim() : null,
                h2: h2 ? h2.innerText.trim() : null,
                bodyText: document.body.innerText.substring(0, 500)
            };
        })()
    """)
    log(f"\n  [3] Hero H1: {hero_text['h1']}")
    log(f"      Hero H2: {hero_text['h2']}")
    if "tim cook" in (hero_text['h1'] or '').lower() or "tim cook" in (hero_text['h2'] or '').lower():
        log("  [PASS] Tim Cook headline found")
    elif "visionary" in str(hero_text['bodyText']).lower():
        log("  [PASS] 'Visionary' keyword found in page content")
    else:
        log("  [WARN] Tim Cook / Visionary headline not found in h1/h2 — check body text")
        log(f"         Body text snippet: {hero_text['bodyText'][:200]}")

    # 4. Full page screenshot (after scroll-reveal)
    log("\n  [4] Taking full-page screenshot...")
    await take_screenshot(page, "tc-01-full-page")

    # Viewport hero screenshot
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)
    await take_screenshot(page, "tc-02-hero-viewport", full_page=False)

    # 5. Check for amplify-founder image
    log("\n  [5] Checking for 'amplify-founder' image (between Hero and The Problem)...")
    img_results, all_imgs = await check_images(page, ["amplify-founder", "amplify_founder"])
    found_amplify = False
    for key, result in img_results.items():
        if result['found']:
            log(f"  [PASS] Found '{key}' image: {result['src']}")
            log(f"         Loaded: {result['loaded']}")
            found_amplify = True

    if not found_amplify:
        # Search more broadly
        log("  Searching all images for amplify...")
        for img in all_imgs:
            if 'amplify' in img['src'].lower() or 'amplify' in (img.get('alt') or '').lower():
                log(f"  [PASS] Found amplify image: {img['src']} (loaded: {img['naturalWidth']}x{img['naturalHeight']})")
                found_amplify = True
        if not found_amplify:
            log(f"  [FAIL] 'amplify-founder' image NOT found")
            log(f"         Total images on page: {len(all_imgs)}")
            for img in all_imgs[:10]:
                log(f"           {img['src'][:80]} ({img['naturalWidth']}x{img['naturalHeight']})")

    # Scroll to amplify image area and take zoomed screenshot
    log("\n  [5b] Scrolling to amplify-founder image area...")
    viewport_h = await page.evaluate("window.innerHeight")
    page_h = await page.evaluate("document.body.scrollHeight")
    # Estimate: amplify image is between hero (~20%) and problem section (~35%)
    amplify_y = int(page_h * 0.22)
    await page.evaluate(f"window.scrollTo(0, {amplify_y})")
    await asyncio.sleep(0.5)
    await take_screenshot(page, "tc-03-amplify-founder-zone", full_page=False)

    # 6. Check for vc-fomo image
    log("\n  [6] Checking for 'vc-fomo' image (between Credibility and Closing CTA)...")
    img_results2, _ = await check_images(page, ["vc-fomo", "vc_fomo"])
    found_vcfomo = False
    for key, result in img_results2.items():
        if result['found']:
            log(f"  [PASS] Found '{key}' image: {result['src']}")
            found_vcfomo = True
    if not found_vcfomo:
        for img in all_imgs:
            if 'fomo' in img['src'].lower() or 'competition' in (img.get('alt') or '').lower():
                log(f"  [PASS] Found vc-fomo image: {img['src']}")
                found_vcfomo = True
        if not found_vcfomo:
            log(f"  [FAIL] 'vc-fomo' image NOT found")

    # Scroll to vc-fomo area (between credibility ~70% and closing ~85%)
    vcfomo_y = int(page_h * 0.72)
    await page.evaluate(f"window.scrollTo(0, {vcfomo_y})")
    await asyncio.sleep(0.5)
    await take_screenshot(page, "tc-04-vc-fomo-zone", full_page=False)

    # 7. CTA buttons
    log("\n  [7] Checking CTA buttons...")
    awakening_links, other_links = await check_ctas(page)
    log(f"  Links to #awakening: {len(awakening_links)}")
    for l in awakening_links[:5]:
        log(f"    '{l['text'][:50]}' -> {l['href']}")
    if len(awakening_links) > 0:
        log("  [PASS] CTA links to #awakening present")
    else:
        log("  [FAIL] No links to #awakening found")

    # 8. Console errors
    log(f"\n  [8] Console errors: {len(console_errors)}")
    for e in console_errors[:10]:
        log(f"    {e}")
    if len(console_errors) == 0:
        log("  [PASS] No console errors")

    # 9. Sections check
    log("\n  [9] Checking section content keywords...")
    page_text = await page.evaluate("document.body.innerText")
    sections_to_check = [
        ("The Problem", ["problem", "chaos", "overwhelm", "wearing too many hats"]),
        ("Section 2-6 content", ["vision", "execution", "agent", "team", "result"]),
        ("Credibility", ["results", "clients", "case study", "worked with", "testimonial"]),
        ("CTA", ["get started", "awakening", "apply", "book", "start", "join"]),
    ]
    for section_name, keywords in sections_to_check:
        found_kw = [kw for kw in keywords if kw.lower() in page_text.lower()]
        if found_kw:
            log(f"  [PASS] {section_name}: found keywords {found_kw}")
        else:
            log(f"  [WARN] {section_name}: no keywords found from {keywords}")

    await context.close()
    log("\n  Tim Cook page audit COMPLETE")
    return console_errors


async def test_pitch_page(browser):
    log("\n" + "="*60)
    log("PAGE 2: purebrain.ai/pitch/ (page 1001)")
    log("="*60)

    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    console_errors = []
    page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
    page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {str(err)}"))

    log("\n  Navigating to https://purebrain.ai/pitch/ ...")
    await page.goto("https://purebrain.ai/pitch/", wait_until="networkidle", timeout=60000)
    await asyncio.sleep(3)

    # 1. Template check (elementor_canvas = no header/footer)
    log("\n  [1] Checking elementor_canvas template (no header/footer)...")
    has_header = await page.evaluate("!!document.querySelector('header, .site-header, #masthead, #site-header')")
    has_footer = await page.evaluate("!!document.querySelector('footer, .site-footer, #footer, #colophon')")
    log(f"  Header present: {has_header}")
    log(f"  Footer present: {has_footer}")
    if not has_header and not has_footer:
        log("  [PASS] elementor_canvas template confirmed (no header/footer)")
    elif has_header or has_footer:
        log("  [WARN] Header or footer found — may not be elementor_canvas template")

    # 2. Background color
    bg = await check_background(page)
    log(f"\n  [2] Background color: {bg}")
    if "255, 65, 11" in bg or "241, 66, 11" in bg:
        log("  [FAIL] Orange background bleed detected!")
    else:
        log("  [PASS] No orange background bleed")

    # 3. Scroll to reveal
    log("\n  [3] Scrolling to reveal all sections...")
    await scroll_to_reveal(page)
    await asyncio.sleep(1)

    # 4. Full page screenshot
    log("\n  [4] Taking full-page screenshot...")
    await take_screenshot(page, "pitch-01-full-page")

    # Viewport hero
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)
    await take_screenshot(page, "pitch-02-hero-viewport", full_page=False)

    # 5. PureBrain wordmark colors
    log("\n  [5] Checking PUREBRAIN wordmark colors (blue/orange/blue)...")
    wordmark = await page.evaluate("""
        (() => {
            const spans = Array.from(document.querySelectorAll('.blue, .orange, [class*="blue"], [class*="orange"]'));
            return spans.slice(0, 10).map(s => ({
                text: s.innerText,
                class: s.className,
                color: window.getComputedStyle(s).color
            }));
        })()
    """)
    log(f"  Wordmark color spans found: {len(wordmark)}")
    for w in wordmark[:6]:
        log(f"    '{w['text']}' class='{w['class']}' color={w['color']}")

    # Also check page text for PUREBRAIN
    pb_html = await page.evaluate("""
        (() => {
            const els = Array.from(document.querySelectorAll('*')).filter(el =>
                el.children.length > 0 && el.innerText && el.innerText.includes('PUREBR'));
            return els.slice(0,3).map(el => el.innerHTML.substring(0, 200));
        })()
    """)
    log(f"\n  PUREBR HTML snippets:")
    for snippet in pb_html[:3]:
        log(f"    {snippet}")

    # 6. vc-hero image
    log("\n  [6] Checking for 'vc-hero' image (between Hero and Compounding Clock)...")
    _, all_imgs = await check_images(page, ["vc-hero", "vc_hero"])
    found_vchero = False
    for img in all_imgs:
        if 'vc-hero' in img['src'].lower() or 'vc_hero' in img['src'].lower():
            log(f"  [PASS] Found vc-hero image: {img['src']} ({img['naturalWidth']}x{img['naturalHeight']})")
            found_vchero = True
    if not found_vchero:
        # Search more broadly
        for img in all_imgs:
            if 'growth' in img['src'].lower() or 'curve' in img['src'].lower() or 'superpow' in img['src'].lower():
                log(f"  [PASS] Found vc-hero-like image: {img['src']}")
                found_vchero = True
        if not found_vchero:
            log("  [FAIL] vc-hero image NOT found")
            log(f"  All images on page: {len(all_imgs)}")
            for img in all_imgs[:12]:
                log(f"    {img['src'][:80]} ({img['naturalWidth']}x{img['naturalHeight']})")

    # Zoom to hero->compounding clock transition zone
    page_h = await page.evaluate("document.body.scrollHeight")
    vchero_y = int(page_h * 0.15)
    await page.evaluate(f"window.scrollTo(0, {vchero_y})")
    await asyncio.sleep(0.5)
    await take_screenshot(page, "pitch-03-vc-hero-zone", full_page=False)

    # 7. Department team wall (23 departments grid)
    log("\n  [7] Checking department team wall (23 departments grid)...")
    dept_check = await page.evaluate("""
        (() => {
            const bodyText = document.body.innerText;
            const hasDept = bodyText.includes('Department') || bodyText.includes('department') ||
                            bodyText.includes('dept') || bodyText.includes('DEPT');

            // Look for grid containers
            const grids = Array.from(document.querySelectorAll('[class*="grid"], [class*="department"], [class*="dept"], [class*="team"]'));

            // Count department-like mentions
            const deptKeywords = ['Marketing', 'Sales', 'Finance', 'Engineering', 'HR', 'Legal',
                                  'Operations', 'Product', 'Design', 'Research', 'IT', 'Support',
                                  'Accounting', 'Technology', 'Infrastructure', 'Capital'];
            const foundDepts = deptKeywords.filter(d => bodyText.includes(d));

            return {
                hasDeptWord: hasDept,
                gridCount: grids.length,
                foundDepts: foundDepts,
                bodySnippet: bodyText.substring(500, 1200)
            };
        })()
    """)
    log(f"  Department keyword found: {dept_check['hasDeptWord']}")
    log(f"  Grid elements found: {dept_check['gridCount']}")
    log(f"  Dept keywords in page: {dept_check['foundDepts']}")
    if len(dept_check['foundDepts']) >= 5:
        log("  [PASS] Multiple department names found — team wall likely rendering")
    else:
        log("  [WARN] Few department names found — team wall may not be rendering")
        log(f"  Body snippet: {dept_check['bodySnippet'][:300]}")

    # Scroll to ~50% for department wall
    dept_y = int(page_h * 0.50)
    await page.evaluate(f"window.scrollTo(0, {dept_y})")
    await asyncio.sleep(0.5)
    await take_screenshot(page, "pitch-04-dept-wall-zone", full_page=False)

    # 8. Pricing section
    log("\n  [8] Checking pricing section (4 tiers)...")
    pricing = await page.evaluate("""
        (() => {
            const bodyText = document.body.innerText;
            return {
                has179: bodyText.includes('179') || bodyText.includes('$179'),
                has349: bodyText.includes('349') || bodyText.includes('$349'),
                has999: bodyText.includes('999') || bodyText.includes('$999'),
                has1999: bodyText.includes('1,999') || bodyText.includes('$1,999') || bodyText.includes('1999'),
            };
        })()
    """)
    log(f"  $179 tier: {pricing['has179']}")
    log(f"  $349 tier: {pricing['has349']}")
    log(f"  $999 tier: {pricing['has999']}")
    log(f"  $1,999 tier: {pricing['has1999']}")
    tiers_found = sum([pricing['has179'], pricing['has349'], pricing['has999'], pricing['has1999']])
    if tiers_found == 4:
        log("  [PASS] All 4 pricing tiers present")
    elif tiers_found >= 2:
        log(f"  [WARN] Only {tiers_found}/4 pricing tiers found")
    else:
        log(f"  [FAIL] Only {tiers_found}/4 pricing tiers found")

    # Scroll to pricing area (~75%)
    pricing_y = int(page_h * 0.75)
    await page.evaluate(f"window.scrollTo(0, {pricing_y})")
    await asyncio.sleep(0.5)
    await take_screenshot(page, "pitch-05-pricing-zone", full_page=False)

    # 9. CTA buttons -> #awakening
    log("\n  [9] Checking CTA buttons link to #awakening...")
    awakening_links, _ = await check_ctas(page)
    log(f"  Links to #awakening: {len(awakening_links)}")
    for l in awakening_links[:5]:
        log(f"    '{l['text'][:50]}' -> {l['href']}")
    if len(awakening_links) > 0:
        log("  [PASS] CTA links to #awakening present")
    else:
        log("  [FAIL] No #awakening CTA links found")

    # 10. Console errors
    log(f"\n  [10] Console errors: {len(console_errors)}")
    for e in console_errors[:10]:
        log(f"    {e}")
    if len(console_errors) == 0:
        log("  [PASS] No console errors")

    # Bottom of page screenshot
    await page.evaluate(f"window.scrollTo(0, {page_h})")
    await asyncio.sleep(0.5)
    await take_screenshot(page, "pitch-06-bottom", full_page=False)

    await context.close()
    log("\n  Pitch page audit COMPLETE")
    return console_errors


async def main():
    log("PureBrain.ai Visual QA — Amplify Deploy Verification")
    log(f"Output directory: {OUTPUT_DIR}")
    log("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        tc_errors = await test_tim_cook_page(browser)
        pitch_errors = await test_pitch_page(browser)

        await browser.close()

    log("\n" + "="*60)
    log("SUMMARY")
    log("="*60)
    log(f"Tim Cook page console errors: {len(tc_errors)}")
    log(f"Pitch page console errors: {len(pitch_errors)}")
    log(f"\nAll screenshots saved to: {OUTPUT_DIR}")
    log("\nFiles generated:")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        log(f"  {f}")

    # Write results log
    results_path = OUTPUT_DIR / "qa-results.txt"
    with open(results_path, "w") as f:
        f.write("\n".join(RESULTS))
    log(f"\nResults log: {results_path}")


if __name__ == "__main__":
    asyncio.run(main())
