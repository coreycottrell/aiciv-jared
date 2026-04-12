"""Test image visibility on purebrain.ai/your-ai-tim-cook/ with REAL scroll behavior."""
import asyncio
import os
from playwright.async_api import async_playwright

OUT = "/home/jared/projects/AI-CIV/aether/exports/qa-image-fix"
URL = "https://purebrain.ai/your-ai-tim-cook/"

# Ensure output directory exists
os.makedirs(OUT, exist_ok=True)

SCROLL_INTO_AMP = """() => {
    const imgs = Array.from(document.querySelectorAll('img'));
    const img = imgs.find(i => i.src.includes('amplify-founder'));
    if (img) {
        img.scrollIntoView({behavior: 'smooth', block: 'center'});
        return {found: true, src: img.src.substring(img.src.lastIndexOf('/'))};
    }
    return {found: false};
}"""

SCROLL_INTO_FOMO = """() => {
    const imgs = Array.from(document.querySelectorAll('img'));
    const img = imgs.find(i => i.src.includes('vc-fomo'));
    if (img) {
        img.scrollIntoView({behavior: 'smooth', block: 'center'});
        return {found: true, src: img.src.substring(img.src.lastIndexOf('/'))};
    }
    return {found: false};
}"""

CHECK_IMAGE_OPACITY = """() => {
    const imgs = Array.from(document.querySelectorAll('img[src*="amplify-founder"], img[src*="vc-fomo"]'));
    return imgs.map(img => ({
        src: img.src.substring(img.src.lastIndexOf('/')),
        inlineStyle: img.getAttribute('style') || 'none',
        computedOpacity: window.getComputedStyle(img).opacity,
        computedVisibility: window.getComputedStyle(img).visibility,
        parentClasses: (img.parentElement?.className || 'no-parent').substring(0, 80),
        isInViewport: img.getBoundingClientRect().top >= 0 && img.getBoundingClientRect().top <= window.innerHeight
    }));
}"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        print("Navigating to purebrain.ai/your-ai-tim-cook/...")
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        print("Page loaded. Waiting for initial render...")
        await page.wait_for_timeout(2000)

        # Screenshot 1: Hero section
        print("\n1. Capturing hero section...")
        await page.screenshot(path=os.path.join(OUT, "001-hero-section.png"))
        print("   Saved: 001-hero-section.png")

        # Scroll to amplify-founder image
        print("\n2. Scrolling to amplify-founder image...")
        amp_result = await page.evaluate(SCROLL_INTO_AMP)
        print(f"   Scroll result: {amp_result}")
        await page.wait_for_timeout(2000)  # Wait for scroll animation and IntersectionObserver

        # Check opacity before screenshot
        images_before = await page.evaluate(CHECK_IMAGE_OPACITY)
        print("   Image opacity check BEFORE screenshot:")
        for img in images_before:
            if 'amplify' in img['src']:
                print(f"     - amplify-founder: opacity={img['computedOpacity']}, visibility={img['computedVisibility']}")
                print(f"       In viewport: {img['isInViewport']}")
                print(f"       Inline style: {img['inlineStyle']}")

        await page.screenshot(path=os.path.join(OUT, "002-amplify-founder-image.png"))
        print("   Saved: 002-amplify-founder-image.png")

        # Continue scrolling to vc-fomo image
        print("\n3. Scrolling to vc-fomo image...")
        fomo_result = await page.evaluate(SCROLL_INTO_FOMO)
        print(f"   Scroll result: {fomo_result}")
        await page.wait_for_timeout(2000)  # Wait for scroll animation

        # Check opacity before screenshot
        images_before = await page.evaluate(CHECK_IMAGE_OPACITY)
        print("   Image opacity check BEFORE screenshot:")
        for img in images_before:
            if 'vc-fomo' in img['src']:
                print(f"     - vc-fomo: opacity={img['computedOpacity']}, visibility={img['computedVisibility']}")
                print(f"       In viewport: {img['isInViewport']}")
                print(f"       Inline style: {img['inlineStyle']}")

        await page.screenshot(path=os.path.join(OUT, "003-vc-fomo-image.png"))
        print("   Saved: 003-vc-fomo-image.png")

        # Final check: inspect both images
        print("\n4. Final opacity verification...")
        all_images = await page.evaluate(CHECK_IMAGE_OPACITY)
        print("\n   All target images found:")
        for img in all_images:
            status = "VISIBLE" if img['computedOpacity'] == "1" else "HIDDEN"
            print(f"     - {img['src']}: {status} (opacity={img['computedOpacity']})")
            if img['inlineStyle'] != 'none':
                print(f"       WARNING: Inline style present: {img['inlineStyle']}")

        await browser.close()

        print(f"\n✓ All screenshots saved to: {OUT}")
        print("\nTest Results:")
        print(f"  amplify-founder: {'VISIBLE' if any('amplify' in img['src'] and img['computedOpacity'] == '1' for img in all_images) else 'HIDDEN'}")
        print(f"  vc-fomo: {'VISIBLE' if any('vc-fomo' in img['src'] and img['computedOpacity'] == '1' for img in all_images) else 'HIDDEN'}")

asyncio.run(main())
