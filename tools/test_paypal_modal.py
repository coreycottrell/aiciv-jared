"""Quick test: does openWaitlistModal('Bonded') trigger the PayPal modal?"""
import time
from playwright.sync_api import sync_playwright

SCREENSHOTS = "/home/jared/projects/AI-CIV/aether/exports/paytest-screenshots"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--use-gl=swiftshader', '--enable-webgl']
        )
        page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()

        print("[1] Loading page...")
        page.goto("https://purebrain.ai/pay-test/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        # Wait for body visible
        for i in range(15):
            d = page.evaluate("() => window.getComputedStyle(document.body).display")
            if d != "none":
                break
            time.sleep(2)

        print("[2] Checking openWaitlistModal type...")
        fn_type = page.evaluate("""() => {
            const fn = window.openWaitlistModal;
            if (!fn) return 'undefined';
            const src = fn.toString().substring(0, 200);
            return src;
        }""")
        print(f"  openWaitlistModal: {fn_type[:200]}")

        # Check if it's the PayPal version (should mention 'pb-paypal' or 'PayPal')
        is_paypal = 'paypal' in fn_type.lower() or 'pb-paypal' in fn_type.lower() or 'SDK' in fn_type
        print(f"  Is PayPal version: {is_paypal}")

        print("\n[3] Calling openWaitlistModal('Bonded')...")
        result = page.evaluate("""() => {
            try {
                window.openWaitlistModal('Bonded');
                return 'called';
            } catch(e) {
                return 'error: ' + e.message;
            }
        }""")
        print(f"  Result: {result}")
        time.sleep(3)

        # Check for PayPal modal
        print("\n[4] Checking for modals...")
        modals = page.evaluate("""() => {
            const results = {};
            // PayPal modal
            const ppOverlay = document.getElementById('pb-paypal-overlay');
            if (ppOverlay) {
                results.paypalOverlay = {
                    exists: true,
                    hasActiveClass: ppOverlay.classList.contains('pb-active'),
                    display: window.getComputedStyle(ppOverlay).display,
                    visibility: window.getComputedStyle(ppOverlay).visibility,
                    opacity: window.getComputedStyle(ppOverlay).opacity,
                    html: ppOverlay.innerHTML.substring(0, 500)
                };
            }
            // Original waitlist modal
            const wlModal = document.getElementById('waitlistModal');
            if (wlModal) {
                results.waitlistModal = {
                    exists: true,
                    hasActiveClass: wlModal.classList.contains('active'),
                    display: window.getComputedStyle(wlModal).display,
                };
            }
            return results;
        }""")

        import json
        print(json.dumps(modals, indent=2))

        page.screenshot(path=f"{SCREENSHOTS}/20_paypal_modal_test.png")
        print(f"\n  Screenshot saved")

        # If PayPal modal opened, take a screenshot of it
        if modals.get('paypalOverlay', {}).get('hasActiveClass'):
            print("\n[5] PayPal modal IS active!")
            # Check for PayPal buttons
            btns = page.evaluate("""() => {
                const container = document.getElementById('pb-paypal-buttons-container');
                if (!container) return 'no container';
                return {
                    innerHTML: container.innerHTML.substring(0, 500),
                    children: container.children.length,
                    visible: container.offsetHeight > 0
                };
            }""")
            print(f"  PayPal buttons: {btns}")
        else:
            print("\n[5] PayPal modal NOT active. Checking what DID open...")
            # Maybe the waitlist modal opened instead
            if modals.get('waitlistModal', {}).get('hasActiveClass'):
                print("  >>> WAITLIST modal opened instead of PayPal!")

        browser.close()

if __name__ == "__main__":
    main()
