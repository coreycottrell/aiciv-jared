#!/usr/bin/env python3
"""Test assessment form JavaScript functions"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def debug_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://purebrain.ai/assessment/', wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)

        # Check what functions are defined
        result = await page.evaluate("""() => {
            return {
                hasSubmitForm: typeof submitForm !== 'undefined',
                hasSelectOption: typeof selectOption !== 'undefined',
                hasAnswers: typeof answers !== 'undefined',
                hasGoogleForm: document.getElementById('googleForm') !== null,
                hasHiddenIframe: document.getElementById('hidden_iframe') !== null
            };
        }""")
        print('JavaScript check:')
        for k, v in result.items():
            print(f'  {k}: {v}')

        await browser.close()


async def test_form_submission():
    print('=' * 60)
    print('Testing Assessment Form Submission')
    print(f'Started: {datetime.now().isoformat()}')
    print('=' * 60)

    TEST_EMAIL = f'aether.test.{datetime.now().strftime("%Y%m%d%H%M%S")}@purebrain.ai'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Track network requests
        network_log = []
        def on_request(req):
            if 'formResponse' in req.url:
                network_log.append(req.url)
                print(f'  [NETWORK] Google Forms POST detected!')

        page.on('request', on_request)

        await page.goto('https://purebrain.ai/assessment/', wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)
        print('[1] Page loaded')

        # Check page has the form elements
        has_elements = await page.evaluate("""() => {
            return {
                googleForm: document.getElementById('googleForm') !== null,
                hiddenIframe: document.getElementById('hidden_iframe') !== null,
                gf_q1: document.getElementById('gf_q1') !== null,
                gf_email: document.getElementById('gf_email') !== null
            };
        }""")
        print(f'[2] Form elements: {has_elements}')

        if not has_elements.get('googleForm'):
            print('ERROR: Hidden form not found!')
            await browser.close()
            return

        # Set answers and navigate to Q6 using page.evaluate
        await page.evaluate("""() => {
            window.answers = {
                "1": "I've tried to maintain context but it's frustrating",
                "2": "Heavily integrated into most of my work",
                "3": "They don't remember what I've told them",
                "4": "A digital employee that grows with my organization",
                "5": "The question isn't cost – it's whether it actually works"
            };
            window.currentQuestion = 6;
            document.querySelectorAll(".question").forEach(q => q.classList.remove("active"));
            document.querySelector(".question[data-question='6']").classList.add("active");
        }""")
        print('[3] Set answers and navigated to Q6')

        await asyncio.sleep(0.5)

        # Fill contact form
        await page.fill('#name', 'Aether Test Bot')
        await page.fill('#email', TEST_EMAIL)
        await page.fill('#company', 'PureBrain Test')
        print(f'[4] Contact info filled: {TEST_EMAIL}')

        # Manually populate and submit the hidden form
        await page.evaluate("""() => {
            // Populate hidden form fields
            document.getElementById('gf_q1').value = window.answers["1"] || "";
            document.getElementById('gf_q2').value = window.answers["2"] || "";
            document.getElementById('gf_q3').value = window.answers["3"] || "";
            document.getElementById('gf_q4').value = window.answers["4"] || "";
            document.getElementById('gf_q5').value = window.answers["5"] || "";
            document.getElementById('gf_name').value = document.getElementById('name').value;
            document.getElementById('gf_email').value = document.getElementById('email').value;
            document.getElementById('gf_company').value = document.getElementById('company').value || "your organization";

            // Submit the hidden form to the iframe
            document.getElementById('googleForm').submit();

            // Show results
            document.querySelectorAll(".question").forEach(q => q.classList.remove("active"));
            document.getElementById("results").classList.add("active");
        }""")
        print('[5] Form submitted via hidden iframe')

        await asyncio.sleep(3)

        # Check results
        results_visible = await page.is_visible('#results.active')
        print(f'[6] Results visible: {results_visible}')

        print(f'\nNetwork requests to Google Forms: {len(network_log)}')
        for url in network_log:
            print(f'  {url[:100]}...')

        if network_log:
            print('\n✅ SUCCESS: Form submission to Google Forms detected!')
        else:
            print('\n⚠️ No network requests logged (iframe POST may not show in log)')
            print('   Check Google Sheet manually to verify submission')

        await browser.close()

    print('\n' + '=' * 60)
    print(f'Test email: {TEST_EMAIL}')
    print('Check Google Sheet "Form Responses 1" for this email')
    print('=' * 60)


if __name__ == "__main__":
    asyncio.run(test_form_submission())
