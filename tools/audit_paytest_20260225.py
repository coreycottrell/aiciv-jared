"""
Pay-Test Pages Comprehensive Visual Audit
Date: 2026-02-25
Agent: browser-vision-tester

Tests both pages:
- https://purebrain.ai/pay-test-sandbox-2/ (Page 688 - sandbox)
- https://purebrain.ai/pay-test-2/ (Page 689 - production)

Uses single browser instance to avoid GoDaddy WAF rate limiting.
Password: PureBrain.ai253443$$$
"""

import asyncio
import json
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest-audit-20260225")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PASSWORD = "PureBrain.ai253443$$$"

PAGES = [
    {
        "name": "sandbox",
        "url": "https://purebrain.ai/pay-test-sandbox-2/",
        "page_id": 688,
        "label": "SANDBOX (Page 688)"
    },
    {
        "name": "production",
        "url": "https://purebrain.ai/pay-test-2/",
        "page_id": 689,
        "label": "PRODUCTION (Page 689)"
    }
]

results = {}

async def screenshot(page, filename, full_page=True):
    path = str(OUTPUT_DIR / filename)
    await page.screenshot(path=path, full_page=full_page)
    print(f"  SCREENSHOT: {filename}")
    return path

async def enter_password(page, url):
    """Navigate to page and enter WP password if prompted."""
    print(f"  Navigating to {url}")
    resp = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
    status = resp.status if resp else "unknown"
    print(f"  HTTP Status: {status}")
    await asyncio.sleep(3)

    current_url = page.url
    print(f"  Current URL: {current_url}")

    # Check for WAF block
    page_text = await page.inner_text("body")
    if "verify you are human" in page_text.lower() or "captcha" in page_text.lower():
        print("  WARNING: WAF CAPTCHA detected - rate limited!")
        return False, status

    # Check if password form is present
    pw_input = page.locator("input[id^='pwbox-']")
    if await pw_input.count() > 0:
        print("  Password form found - entering password...")
        await pw_input.first.fill(PASSWORD)
        await page.locator("input[type='submit']").first.click()
        await asyncio.sleep(5)
        print("  Password submitted, waiting for page load...")
        await asyncio.sleep(3)

        # Check again after password
        page_text2 = await page.inner_text("body")
        if "verify you are human" in page_text2.lower():
            print("  WARNING: WAF block after password submit!")
            return False, status
    else:
        # Check if already unlocked (cookie from previous page)
        print("  No password form found - checking if page loaded directly...")

    return True, status

async def audit_page(page, page_info, screenshots):
    """Full audit of one pay-test page."""
    name = page_info["name"]
    label = page_info["label"]
    url = page_info["url"]

    print(f"\n{'='*60}")
    print(f"AUDITING: {label}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    page_results = {
        "name": name,
        "label": label,
        "url": url,
        "checks": {},
        "screenshots": [],
        "errors": [],
        "warnings": [],
        "console_errors": []
    }

    # Collect console errors
    console_errors = []
    page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}")
             if msg.type in ["error", "warning"] else None)

    # 1. Navigate and handle password
    success, http_status = await enter_password(page, url)
    page_results["checks"]["http_status"] = http_status

    if not success:
        page_results["errors"].append("WAF rate limit or navigation failure")
        sc = await screenshot(page, f"{name}_01_waf_block.png")
        screenshots.append(sc)
        page_results["screenshots"].append(sc)
        return page_results

    # 2. Full page desktop screenshot
    await asyncio.sleep(2)
    sc = await screenshot(page, f"{name}_01_desktop_full.png", full_page=True)
    screenshots.append(sc)
    page_results["screenshots"].append(sc)
    page_results["checks"]["page_loaded"] = True

    # 3. Above-fold screenshot
    sc = await screenshot(page, f"{name}_02_desktop_above_fold.png", full_page=False)
    screenshots.append(sc)
    page_results["screenshots"].append(sc)

    # 4. Check for blank/white page
    body_html = await page.evaluate("document.body.innerHTML")
    is_blank = len(body_html.strip()) < 500
    page_results["checks"]["not_blank"] = not is_blank
    if is_blank:
        page_results["errors"].append("Page appears blank - minimal HTML")

    # 5. Check PureBrain branding
    print("  Checking branding...")
    try:
        branding_html = await page.evaluate("""
            () => {
                // Look for PureBrain elements
                const all = document.querySelectorAll('*');
                let found = [];
                for (let el of all) {
                    if (el.textContent.includes('PUREBRAIN') || el.textContent.includes('PureBrain')) {
                        found.push({tag: el.tagName, class: el.className, text: el.textContent.substring(0, 100)});
                        if (found.length > 3) break;
                    }
                }
                return found;
            }
        """)
        page_results["checks"]["purebrain_branding"] = len(branding_html) > 0
        print(f"  Branding elements found: {len(branding_html)}")
    except Exception as e:
        page_results["warnings"].append(f"Branding check error: {e}")

    # 6. Check hero section
    print("  Checking hero section...")
    try:
        hero_info = await page.evaluate("""
            () => {
                const chatInit = document.querySelector('.chat-initial');
                const chatBtn = document.querySelector('.chat-initial__btn');
                const chatIntro = document.querySelector('.chat-initial__intro');
                return {
                    chat_initial_exists: !!chatInit,
                    begin_btn_exists: !!chatBtn,
                    begin_btn_text: chatBtn ? chatBtn.textContent.trim() : null,
                    intro_text: chatIntro ? chatIntro.textContent.trim().substring(0, 200) : null
                };
            }
        """)
        page_results["checks"]["hero_section"] = hero_info
        print(f"  Hero: chat_initial={hero_info.get('chat_initial_exists')}, begin_btn={hero_info.get('begin_btn_exists')}")
    except Exception as e:
        page_results["warnings"].append(f"Hero check error: {e}")

    # 7. Check pricing section visibility
    print("  Checking pricing section...")
    try:
        pricing_info = await page.evaluate("""
            () => {
                const section = document.querySelector('.pricing-section');
                if (!section) return {exists: false};
                const cards = document.querySelectorAll('.pricing-card');
                const tiers = Array.from(cards).map(c => {
                    const nameEl = c.querySelector('.pricing-card__name, h3, h4');
                    const priceEl = c.querySelector('.pricing-card__price, .price');
                    const btnEl = c.querySelector('.pricing-card__cta, button, .btn');
                    return {
                        name: nameEl ? nameEl.textContent.trim() : null,
                        price: priceEl ? priceEl.textContent.trim() : null,
                        btn: btnEl ? btnEl.textContent.trim() : null
                    };
                });
                const style = window.getComputedStyle(section);
                return {
                    exists: true,
                    display: style.display,
                    visibility: style.visibility,
                    card_count: cards.length,
                    tiers: tiers
                };
            }
        """)
        page_results["checks"]["pricing_section"] = pricing_info
        print(f"  Pricing: exists={pricing_info.get('exists')}, display={pricing_info.get('display')}, cards={pricing_info.get('card_count')}")
    except Exception as e:
        page_results["warnings"].append(f"Pricing check error: {e}")

    # 8. Check PayPal SDK loaded
    print("  Checking PayPal SDK...")
    try:
        paypal_check = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script[src]'));
                const ppScript = scripts.find(s => s.src.includes('paypal.com'));
                const ppObj = typeof window.paypal !== 'undefined';
                return {
                    sdk_script: ppScript ? ppScript.src : null,
                    paypal_object: ppObj
                };
            }
        """)
        page_results["checks"]["paypal_sdk"] = paypal_check
        print(f"  PayPal: script={bool(paypal_check.get('sdk_script'))}, object={paypal_check.get('paypal_object')}")
    except Exception as e:
        page_results["warnings"].append(f"PayPal check error: {e}")

    # 9. Check sandbox banner (sandbox page only)
    if name == "sandbox":
        print("  Checking sandbox banner...")
        try:
            sandbox_check = await page.evaluate("""
                () => {
                    const banners = Array.from(document.querySelectorAll('*'));
                    for (let el of banners) {
                        const text = el.textContent.trim();
                        if (text.includes('SANDBOX') || text.includes('sandbox') || text.includes('No real charges')) {
                            return {found: true, text: text.substring(0, 200), tag: el.tagName};
                        }
                    }
                    return {found: false};
                }
            """)
            page_results["checks"]["sandbox_banner"] = sandbox_check
            print(f"  Sandbox banner: {sandbox_check.get('found')} - '{sandbox_check.get('text', '')[:80]}'")
        except Exception as e:
            page_results["warnings"].append(f"Sandbox banner check error: {e}")

    # 10. Check for text contrast issues (orange on dark / white on white)
    print("  Checking for text visibility issues...")
    try:
        contrast_check = await page.evaluate("""
            () => {
                const issues = [];
                // Check orange text
                const allEls = document.querySelectorAll('*');
                for (let el of allEls) {
                    const style = window.getComputedStyle(el);
                    const color = style.color;
                    const bg = style.backgroundColor;
                    // Look for potentially problematic combos in visible text
                    if (el.children.length === 0 && el.textContent.trim().length > 3) {
                        if (color.includes('rgb(241, 66, 11)') || color.includes('rgb(255, 165, 0)')) {
                            issues.push({text: el.textContent.trim().substring(0,50), color, bg});
                        }
                    }
                    if (issues.length > 5) break;
                }
                return {count: issues.length, samples: issues.slice(0, 3)};
            }
        """)
        page_results["checks"]["text_contrast"] = contrast_check
        print(f"  Text contrast issues found: {contrast_check.get('count')}")
    except Exception as e:
        page_results["warnings"].append(f"Contrast check error: {e}")

    # 11. Check all images
    print("  Checking images...")
    try:
        img_check = await page.evaluate("""
            () => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const broken = imgs.filter(img => !img.complete || img.naturalWidth === 0);
                return {
                    total: imgs.length,
                    broken: broken.length,
                    broken_srcs: broken.slice(0,3).map(i => i.src)
                };
            }
        """)
        page_results["checks"]["images"] = img_check
        print(f"  Images: total={img_check.get('total')}, broken={img_check.get('broken')}")
    except Exception as e:
        page_results["warnings"].append(f"Image check error: {e}")

    # 12. Check footer
    print("  Checking footer...")
    try:
        footer_check = await page.evaluate("""
            () => {
                const footers = document.querySelectorAll('footer, .footer, .pb-footer-aether, [class*="footer"]');
                return {
                    count: footers.length,
                    texts: Array.from(footers).slice(0,3).map(f => f.textContent.trim().substring(0, 100))
                };
            }
        """)
        page_results["checks"]["footer"] = footer_check
        print(f"  Footers found: {footer_check.get('count')}")
    except Exception as e:
        page_results["warnings"].append(f"Footer check error: {e}")

    # 13. Check for broken links
    print("  Checking links...")
    try:
        link_check = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                const external = links.filter(l => l.href.startsWith('http')).length;
                const internal = links.filter(l => l.href.startsWith('/') || l.href.includes('purebrain.ai')).length;
                const anchors = links.filter(l => l.href.includes('#')).length;
                return {total: links.length, external, internal, anchors};
            }
        """)
        page_results["checks"]["links"] = link_check
        print(f"  Links: total={link_check.get('total')}, external={link_check.get('external')}, anchors={link_check.get('anchors')}")
    except Exception as e:
        page_results["warnings"].append(f"Link check error: {e}")

    # 14. Click "Begin Awakening" / "Begin Your Awakening" button
    print("  Testing chat flow - clicking Begin Awakening button...")
    try:
        begin_btn = page.locator(".chat-initial__btn").first
        if await begin_btn.count() > 0:
            await begin_btn.scroll_into_view_if_needed()
            await asyncio.sleep(1)

            # Screenshot before click
            sc = await screenshot(page, f"{name}_03_before_begin_click.png", full_page=False)
            screenshots.append(sc)
            page_results["screenshots"].append(sc)

            await begin_btn.click()
            print("  Begin button clicked, waiting for chat to appear...")
            await asyncio.sleep(3)

            # Screenshot after click - should show chat input
            sc = await screenshot(page, f"{name}_04_chat_initial_state.png", full_page=False)
            screenshots.append(sc)
            page_results["screenshots"].append(sc)

            # Check if user input appeared
            user_input = page.locator("#userInput").first
            input_visible = await user_input.count() > 0
            page_results["checks"]["chat_input_appears"] = input_visible
            print(f"  Chat input visible: {input_visible}")

            if input_visible:
                # Type a test message
                await user_input.fill("Hello")
                await asyncio.sleep(1)
                sc = await screenshot(page, f"{name}_05_chat_input_filled.png", full_page=False)
                screenshots.append(sc)
                page_results["screenshots"].append(sc)
                page_results["checks"]["chat_flow_starts"] = True
            else:
                page_results["errors"].append("Chat input did not appear after Begin Awakening click")
                page_results["checks"]["chat_flow_starts"] = False
        else:
            page_results["errors"].append("Begin Awakening button not found")
            page_results["checks"]["chat_flow_starts"] = False
    except Exception as e:
        page_results["errors"].append(f"Chat flow test error: {e}")
        page_results["checks"]["chat_flow_starts"] = False

    # 15. Mobile viewport test
    print("  Testing mobile viewport (375px)...")
    await asyncio.sleep(2)

    # Take pricing section screenshot (scroll to it if it exists)
    try:
        pricing_el = page.locator(".pricing-section").first
        if await pricing_el.count() > 0:
            await pricing_el.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            sc = await screenshot(page, f"{name}_06_pricing_section.png", full_page=False)
            screenshots.append(sc)
            page_results["screenshots"].append(sc)
    except Exception as e:
        page_results["warnings"].append(f"Pricing scroll error: {e}")

    # Store console errors
    page_results["console_errors"] = console_errors[:20]  # Cap at 20

    print(f"  Console errors collected: {len(console_errors)}")

    return page_results

async def audit_mobile(browser, page_info, screenshots):
    """Run mobile audit separately."""
    name = page_info["name"]
    url = page_info["url"]

    print(f"\n  Mobile audit for {name}...")

    ctx = await browser.new_context(viewport={"width": 375, "height": 812})
    page = await ctx.new_page()

    try:
        success, _ = await enter_password(page, url)
        if not success:
            await ctx.close()
            return {"error": "WAF or navigation failure on mobile"}

        await asyncio.sleep(3)
        sc = await screenshot(page, f"{name}_07_mobile_full.png", full_page=True)
        screenshots.append(sc)

        sc = await screenshot(page, f"{name}_08_mobile_above_fold.png", full_page=False)
        screenshots.append(sc)

        # Mobile scroll checks
        mobile_results = await page.evaluate("""
            () => {
                return {
                    viewport_width: window.innerWidth,
                    scroll_width: document.documentElement.scrollWidth,
                    has_horizontal_scroll: document.documentElement.scrollWidth > window.innerWidth,
                    body_width: document.body.offsetWidth
                };
            }
        """)

        print(f"  Mobile viewport: {mobile_results.get('viewport_width')}px, scrollWidth: {mobile_results.get('scroll_width')}px")
        print(f"  Horizontal scroll: {mobile_results.get('has_horizontal_scroll')}")

        await ctx.close()
        return {"mobile_check": mobile_results, "screenshots": [sc]}

    except Exception as e:
        await ctx.close()
        return {"error": str(e)}

async def main():
    print("Starting Pay-Test Pages Comprehensive Visual Audit")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    all_screenshots = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        # Main desktop audit - one context for both pages to reuse WP cookie
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()

        # Audit sandbox first
        sandbox_results = await audit_page(page, PAGES[0], all_screenshots)
        results["sandbox"] = sandbox_results

        # Wait before loading next page (WAF protection)
        print(f"\nWaiting 20 seconds before loading next page (WAF protection)...")
        await asyncio.sleep(20)

        # Audit production
        prod_results = await audit_page(page, PAGES[1], all_screenshots)
        results["production"] = prod_results

        await ctx.close()

        # Mobile audits - wait between
        print("\nWaiting 30 seconds before mobile tests (WAF protection)...")
        await asyncio.sleep(30)

        # Mobile sandbox
        mobile_sandbox = await audit_mobile(browser, PAGES[0], all_screenshots)
        results["sandbox"]["mobile"] = mobile_sandbox

        print("Waiting 20 seconds before mobile production test...")
        await asyncio.sleep(20)

        # Mobile production
        mobile_prod = await audit_mobile(browser, PAGES[1], all_screenshots)
        results["production"]["mobile"] = mobile_prod

        await browser.close()

    # Save raw results
    results_file = str(OUTPUT_DIR / "raw_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nRaw results saved to: {results_file}")

    print(f"\nTotal screenshots captured: {len(all_screenshots)}")
    for sc in all_screenshots:
        print(f"  {sc}")

    return results

if __name__ == "__main__":
    asyncio.run(main())
