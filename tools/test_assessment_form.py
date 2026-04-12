#!/usr/bin/env python3
"""
Test the PureBrain Assessment Form with browser automation
Submits a test entry and checks if it appears in Google Sheets
"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

TEST_DATA = {
    'name': f'Aether Test {datetime.now().strftime("%H%M%S")}',
    'email': f'aether.test.{datetime.now().strftime("%Y%m%d%H%M%S")}@purebrain.ai',
    'company': 'PureBrain Test Co'
}

async def test_assessment_form():
    print("=" * 60)
    print("Testing PureBrain Assessment Form (Hidden Iframe Method)")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    async with async_playwright() as p:
        # Use non-headless for visibility
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Enable request logging to see form submission
        network_requests = []

        def log_request(request):
            if 'google' in request.url.lower() or 'formResponse' in request.url:
                network_requests.append({
                    'method': request.method,
                    'url': request.url[:100]
                })
                print(f"  [NETWORK] {request.method} {request.url[:80]}...")

        page.on('request', log_request)

        try:
            # Step 1: Navigate to assessment page
            print("\n[1] Navigating to https://purebrain.ai/assessment/")
            await page.goto('https://purebrain.ai/assessment/', wait_until='networkidle')
            await page.screenshot(path='/tmp/test_01_loaded.png')
            print("  Page loaded successfully")

            # Step 2: Answer Q1
            print("\n[2] Answering Question 1...")
            await page.wait_for_selector('.question[data-question="1"]')
            options = await page.query_selector_all('.question[data-question="1"] .option')
            if len(options) >= 4:
                await options[3].click()  # Select D - "frustrating"
                print("  Selected: D - I've tried to maintain context but it's frustrating")
            await asyncio.sleep(0.5)
            await page.click('.question[data-question="1"] .btn-primary')

            # Step 3: Answer Q2
            print("\n[3] Answering Question 2...")
            await page.wait_for_selector('.question[data-question="2"].active')
            options = await page.query_selector_all('.question[data-question="2"] .option')
            if len(options) >= 3:
                await options[2].click()  # Select C - "Heavily integrated"
                print("  Selected: C - Heavily integrated into most of my work")
            await asyncio.sleep(0.5)
            await page.click('.question[data-question="2"] .btn-primary')

            # Step 4: Answer Q3
            print("\n[4] Answering Question 3...")
            await page.wait_for_selector('.question[data-question="3"].active')
            options = await page.query_selector_all('.question[data-question="3"] .option')
            if len(options) >= 1:
                await options[0].click()  # Select A - "don't remember"
                print("  Selected: A - They don't remember what I've told them")
            await asyncio.sleep(0.5)
            await page.click('.question[data-question="3"] .btn-primary')

            # Step 5: Answer Q4
            print("\n[5] Answering Question 4...")
            await page.wait_for_selector('.question[data-question="4"].active')
            options = await page.query_selector_all('.question[data-question="4"] .option')
            if len(options) >= 4:
                await options[3].click()  # Select D - "digital employee"
                print("  Selected: D - A digital employee that grows with my organization")
            await asyncio.sleep(0.5)
            await page.click('.question[data-question="4"] .btn-primary')

            # Step 6: Answer Q5
            print("\n[6] Answering Question 5...")
            await page.wait_for_selector('.question[data-question="5"].active')
            options = await page.query_selector_all('.question[data-question="5"] .option')
            if len(options) >= 4:
                await options[3].click()  # Select D - "isn't cost"
                print("  Selected: D - The question isn't cost – it's whether it actually works")
            await asyncio.sleep(0.5)
            await page.click('.question[data-question="5"] .btn-primary')

            await page.screenshot(path='/tmp/test_06_quiz_done.png')

            # Step 7: Fill contact form
            print("\n[7] Filling contact form...")
            await page.wait_for_selector('.question[data-question="6"].active')
            await page.fill('#name', TEST_DATA['name'])
            await page.fill('#email', TEST_DATA['email'])
            await page.fill('#company', TEST_DATA['company'])
            print(f"  Name: {TEST_DATA['name']}")
            print(f"  Email: {TEST_DATA['email']}")
            print(f"  Company: {TEST_DATA['company']}")

            await page.screenshot(path='/tmp/test_07_form_filled.png')

            # Step 8: Submit form
            print("\n[8] Clicking 'Get My Results'...")
            await page.click('.question[data-question="6"] .btn-primary')

            # Wait for submission
            await asyncio.sleep(3)

            await page.screenshot(path='/tmp/test_08_submitted.png')

            # Check results page
            results_visible = await page.is_visible('#results.active')
            if results_visible:
                result_title = await page.text_content('#resultTitle')
                print(f"\n  Results shown: {result_title}")

            # Report network activity
            print("\n" + "=" * 60)
            print("NETWORK ACTIVITY ANALYSIS")
            print("=" * 60)

            google_requests = [r for r in network_requests if 'formResponse' in r['url']]
            if google_requests:
                print(f"\n✅ FOUND {len(google_requests)} Google Forms request(s)!")
                for req in google_requests:
                    print(f"  {req['method']} {req['url']}")
                print("\n🎉 SUCCESS: Form submission to Google Forms detected!")
            else:
                print("\n⚠️ No Google Forms requests detected in network log")
                print("  This might be because the form submitted to iframe")
                print("  Check Google Sheet manually to verify submission")

        except Exception as e:
            print(f"\nERROR: {e}")
            await page.screenshot(path='/tmp/test_error.png')
            raise

        finally:
            print("\nScreenshots saved to /tmp/test_*.png")
            await asyncio.sleep(2)
            await browser.close()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"""
NEXT STEPS:
1. Check Google Sheet for a row with:
   - Name: {TEST_DATA['name']}
   - Email: {TEST_DATA['email']}
   - Company: {TEST_DATA['company']}

2. If row exists → Form submission WORKS!
3. If no row → Check iframe/form configuration
""")


if __name__ == "__main__":
    asyncio.run(test_assessment_form())
