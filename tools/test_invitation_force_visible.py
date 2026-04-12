"""
Invitation Page - Force all animations visible then screenshot every section.
Bypasses IntersectionObserver issues in headless Playwright.
"""

import asyncio
import os
from playwright.async_api import async_playwright

OUTPUT = "/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-26"
os.makedirs(OUTPUT, exist_ok=True)

TARGET_URL = "https://purebrain.ai/invitation/"
PASSWORD = "purebrain25"

# Must be wrapped in () => {} for page.evaluate
FORCE_VISIBLE_JS = """
() => {
    const style = document.createElement('style');
    style.id = 'force-visible-override';
    style.textContent = `
        .pb-fade-in,
        .pb-fade-up,
        .pb-slide-in,
        [class*="fade"],
        [class*="animate"],
        [class*="scroll-reveal"],
        [class*="aos"],
        [data-aos] {
            opacity: 1 !important;
            transform: none !important;
            visibility: visible !important;
            transition: none !important;
            animation: none !important;
        }
    `;
    document.head.appendChild(style);

    document.querySelectorAll('.pb-fade-in, .pb-fade-up').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
        el.style.visibility = 'visible';
    });

    return document.querySelectorAll('.pb-fade-in').length;
}
"""


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[1] Loading page...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        pw = page.locator("input[type='password']")
        if await pw.count() > 0:
            await pw.first.fill(PASSWORD)
            submit = page.locator("input[type='submit']")
            if await submit.count() > 0:
                await submit.first.click()
            else:
                await page.keyboard.press("Enter")
            print("[2] Password entered, waiting 10s...")
            await asyncio.sleep(10)

        forced_count = await page.evaluate(FORCE_VISIBLE_JS)
        print(f"[3] Forced {forced_count} fade-in elements visible")
        await asyncio.sleep(2)

        page_h = await page.evaluate("() => document.documentElement.scrollHeight")
        print(f"[4] Page height: {page_h}px")

        # Full page screenshot
        await page.screenshot(path=f"{OUTPUT}/FORCED-full-page.png", full_page=True)
        print("[5] Full page (forced visible) captured")

        # Section-by-section
        sections = [
            (0, "S1-hero"),
            (int(page_h * 0.12), "S2-feature-cards"),
            (int(page_h * 0.22), "S2b-feature-cards-lower"),
            (int(page_h * 0.30), "S3-awakening-pt1"),
            (int(page_h * 0.40), "S3-awakening-pt2"),
            (int(page_h * 0.50), "S4-pricing-pt1"),
            (int(page_h * 0.60), "S4-pricing-pt2"),
            (int(page_h * 0.68), "S4-pricing-pt3"),
            (int(page_h * 0.76), "S5-testimonial"),
            (int(page_h * 0.84), "S6-urgency"),
            (int(page_h * 0.90), "S7-final-cta-upper"),
            (page_h - 900, "S7-bottom"),
        ]

        for pos, name in sections:
            await page.evaluate(f"() => window.scrollTo(0, {pos})")
            await asyncio.sleep(1.5)
            await page.evaluate(FORCE_VISIBLE_JS)
            await asyncio.sleep(0.5)
            await page.screenshot(path=f"{OUTPUT}/FORCED-{name}.png", full_page=False)
            print(f"    Captured: {name} at {pos}px")

        # DOM inspection
        countdown_info = await page.evaluate("""
            () => {
                const wrap = document.querySelector('.pb-countdown-wrap');
                if (!wrap) return {found: false};
                const nums = Array.from(wrap.querySelectorAll('.pb-cd-num')).map(n => n.textContent.trim());
                const labels = Array.from(wrap.querySelectorAll('.pb-cd-label')).map(n => n.textContent.trim());
                return {
                    found: true,
                    display: window.getComputedStyle(wrap).display,
                    opacity: window.getComputedStyle(wrap).opacity,
                    numbers: nums,
                    labels: labels
                };
            }
        """)
        print(f"\n[COUNTDOWN]: {countdown_info}")

        dots_info = await page.evaluate("""
            () => {
                const spotsClaimedEl = document.querySelector('.pb-spots-claimed, [class*="spots-claimed"], [class*="claim-count"]');
                const spotsText = document.querySelector('.pb-spots-text, [class*="spots-text"]');
                const dotsGrid = document.querySelector('.pb-dots-grid, [class*="dots-grid"]');
                const body = document.body.textContent;
                const claimedMatch = body.match(/(\d+) of (\d+) spots claimed/);
                return {
                    claimedText: claimedMatch ? claimedMatch[0] : 'NOT FOUND IN TEXT',
                    spotsClaimedEl: spotsClaimedEl ? spotsClaimedEl.textContent.trim() : 'NOT FOUND',
                    dotsGridFound: !!dotsGrid,
                    dotsGridHtml: dotsGrid ? dotsGrid.outerHTML.substring(0, 500) : 'NOT FOUND'
                };
            }
        """)
        print(f"\n[SPOTS/DOTS]: {dots_info}")

        cards_detail = await page.evaluate("""
            () => {
                const grid = document.querySelector('.pb-cards-grid');
                if (!grid) return {error: 'GRID NOT FOUND'};
                const cards = grid.querySelectorAll('.pb-feature-card');
                const st = window.getComputedStyle(grid);
                return {
                    gridDisplay: st.display,
                    gridOpacity: st.opacity,
                    gridVisibility: st.visibility,
                    cardCount: cards.length,
                    cards: Array.from(cards).map(c => ({
                        opacity: window.getComputedStyle(c).opacity,
                        display: window.getComputedStyle(c).display,
                        title: (c.querySelector('.pb-feature-title') || {textContent:''}).textContent.trim(),
                        desc: (c.querySelector('.pb-feature-desc') || {textContent:''}).textContent.trim().substring(0, 80)
                    }))
                };
            }
        """)
        print(f"\n[FEATURE CARDS]: {cards_detail}")

        timeline_detail = await page.evaluate("""
            () => {
                const sections = document.querySelectorAll('section');
                return Array.from(sections).map((s, i) => {
                    const cls = (typeof s.className === 'string' ? s.className : '').substring(0, 80);
                    const h2 = s.querySelector('h2');
                    const h3s = s.querySelectorAll('h3');
                    return {
                        index: i,
                        cls: cls,
                        h2: h2 ? h2.textContent.trim().substring(0, 60) : '',
                        h3count: h3s.length,
                        opacity: window.getComputedStyle(s).opacity,
                        height: s.offsetHeight,
                        offsetTop: s.offsetTop
                    };
                });
            }
        """)
        print(f"\n[SECTIONS MAP]:")
        for s in timeline_detail:
            print(f"  [{s['index']}] top={s['offsetTop']}px h={s['height']}px op={s['opacity']} h2='{s['h2'][:40]}' [{s['cls'][:50]}]")

        pricing_detail = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll('.pb-price-card');
                return {
                    cardCount: cards.length,
                    cards: Array.from(cards).map(c => {
                        const cls = (typeof c.className === 'string' ? c.className : '').substring(0, 80);
                        const tierEl = c.querySelector('.pb-tier');
                        const priceEl = c.querySelector('.pb-price-current');
                        const ctaEl = c.querySelector('a');
                        return {
                            cls: cls,
                            isFeatured: cls.includes('featured'),
                            tier: tierEl ? tierEl.textContent.trim() : 'unknown',
                            price: priceEl ? priceEl.textContent.trim() : 'unknown',
                            ctaHref: ctaEl ? ctaEl.getAttribute('href') : 'none',
                            ctaText: ctaEl ? ctaEl.textContent.trim().substring(0, 40) : 'none',
                            opacity: window.getComputedStyle(c).opacity
                        };
                    })
                };
            }
        """)
        print(f"\n[PRICING CARDS]: {pricing_detail}")

        testimonial_detail = await page.evaluate("""
            () => {
                const blocks = document.querySelectorAll('.pb-testimonial, .pb-testimonial-card, blockquote, [class*="testimonial"]');
                return {
                    count: blocks.length,
                    items: Array.from(blocks).slice(0, 5).map(b => {
                        const cls = (typeof b.className === 'string' ? b.className : '').substring(0, 60);
                        return {
                            cls: cls,
                            text: b.textContent.trim().substring(0, 150),
                            opacity: window.getComputedStyle(b).opacity
                        };
                    }),
                    michaelContext: (() => {
                        const all = document.body.innerHTML;
                        const idx = all.indexOf('Michael');
                        return idx > -1 ? all.substring(idx, idx+300).replace(/<[^>]*>/g,'').trim() : 'NOT FOUND';
                    })()
                };
            }
        """)
        print(f"\n[TESTIMONIAL]: {testimonial_detail}")

        signature_detail = await page.evaluate("""
            () => {
                const sigEl = document.querySelector('.pb-signature, [class*="signature"], [class*="founder"]');
                const bodyText = document.body.textContent;
                const jIdx = bodyText.indexOf('Jared');
                return {
                    sigElFound: !!sigEl,
                    sigHtml: sigEl ? sigEl.outerHTML.substring(0, 400) : 'NOT FOUND',
                    jaredCtx: jIdx > -1 ? bodyText.substring(Math.max(0,jIdx-50), jIdx+200) : 'NOT FOUND'
                };
            }
        """)
        print(f"\n[JARED SIGNATURE]: {signature_detail}")

        await browser.close()
        files = sorted(os.listdir(OUTPUT))
        print(f"\n[DONE] Total screenshots: {len(files)}")
        print(f"       Directory: {OUTPUT}")


if __name__ == "__main__":
    asyncio.run(run())
