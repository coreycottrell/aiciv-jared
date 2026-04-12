#!/usr/bin/env python3
"""
Form Test Automation Script
Tests the Experiential Engine form with specified test data
"""

from playwright.sync_api import sync_playwright
import time
import os

# Test data
TEST_DATA = {
    "email": "aether.test@example.com",
    "company_name": "AETHER TEST COMPANY",
    "website": "https://aethertest.com",
    "role": "Other",
    "industry": "Tech / Apps / SaaS",
    "big_moment": "Product launch",
    "primary_goal": "Grow email/SMS list (first-party data)",
    "prize_type": "Mixed",
    "budget": "$100k-$250k",
    "timeline": "8-16 weeks",
    "compliance": "Not sure",
    "anything_else": "THIS IS A TEST SUBMISSION FROM AETHER - PLEASE CONFIRM IN GOOGLE SHEET"
}

# Screenshot directory
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/docs/from-telegram/form-test-screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(page, step_name):
    """Take and save screenshot"""
    path = f"{SCREENSHOT_DIR}/{step_name}.png"
    page.screenshot(path=path)
    print(f"  Screenshot saved: {path}")
    return path

def click_visible_continue(page):
    """Click the visible Continue button within the active step"""
    page.click('.form-step.active button.btn-primary:has-text("Continue")')

def click_visible_submit(page):
    """Click the visible Submit button within the active step"""
    page.click('.form-step.active button.btn-submit:has-text("Submit")')

def run_form_test():
    with sync_playwright() as p:
        # Launch browser (headless for automation)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # Open the form
        form_path = "file:///home/jared/projects/AI-CIV/aether/docs/from-telegram/experiential-engine-form-google.html"
        print(f"\n=== STEP 1: Opening form ===")
        print(f"URL: {form_path}")
        page.goto(form_path)
        page.wait_for_load_state("networkidle")
        take_screenshot(page, "01-form-loaded")
        print("  Form loaded successfully - showing email input (Question 1/12)")

        # Q1: Email
        print(f"\n=== STEP 2: Filling Email (Q1/12) ===")
        print(f"  Entering: {TEST_DATA['email']}")
        page.fill('input[type="email"]', TEST_DATA['email'])
        take_screenshot(page, "02-email-filled")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q2")

        # Q2: Company Name
        print(f"\n=== STEP 3: Filling Company Name (Q2/12) ===")
        print(f"  Entering: {TEST_DATA['company_name']}")
        page.fill('.form-step.active input[type="text"]', TEST_DATA['company_name'])
        take_screenshot(page, "03-company-filled")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q3")

        # Q3: Website
        print(f"\n=== STEP 4: Filling Website (Q3/12) ===")
        print(f"  Entering: {TEST_DATA['website']}")
        page.fill('.form-step.active input[type="url"]', TEST_DATA['website'])
        take_screenshot(page, "04-website-filled")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q4")

        # Q4: Role
        print(f"\n=== STEP 5: Selecting Role (Q4/12) ===")
        print(f"  Selecting: {TEST_DATA['role']}")
        page.click(f'.form-step.active label.option-item:has-text("{TEST_DATA["role"]}")')
        take_screenshot(page, "05-role-selected")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q5")

        # Q5: Industry
        print(f"\n=== STEP 6: Selecting Industry (Q5/12) ===")
        print(f"  Selecting: {TEST_DATA['industry']}")
        page.click(f'.form-step.active label.option-item:has-text("{TEST_DATA["industry"]}")')
        take_screenshot(page, "06-industry-selected")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q6")

        # Q6: Big Moment
        print(f"\n=== STEP 7: Selecting Big Moment (Q6/12) ===")
        print(f"  Selecting: {TEST_DATA['big_moment']}")
        page.click(f'.form-step.active label.option-item:has-text("{TEST_DATA["big_moment"]}")')
        take_screenshot(page, "07-moment-selected")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q7")

        # Q7: Primary Goal (checkbox)
        print(f"\n=== STEP 8: Selecting Primary Goal (Q7/12) ===")
        print(f"  Selecting: {TEST_DATA['primary_goal']}")
        page.click(f'.form-step.active label.option-item:has-text("{TEST_DATA["primary_goal"]}")')
        take_screenshot(page, "08-goal-selected")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q8")

        # Q8: Prize Type
        print(f"\n=== STEP 9: Selecting Prize Type (Q8/12) ===")
        print(f"  Selecting: {TEST_DATA['prize_type']}")
        page.click(f'.form-step.active label.option-item:has-text("{TEST_DATA["prize_type"]}")')
        take_screenshot(page, "09-prize-selected")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q9")

        # Q9: Budget
        print(f"\n=== STEP 10: Selecting Budget (Q9/12) ===")
        print(f"  Selecting: {TEST_DATA['budget']}")
        page.click(f'.form-step.active label.option-item:has-text("{TEST_DATA["budget"]}")')
        take_screenshot(page, "10-budget-selected")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q10")

        # Q10: Timeline
        print(f"\n=== STEP 11: Selecting Timeline (Q10/12) ===")
        print(f"  Selecting: {TEST_DATA['timeline']}")
        # Timeline has special characters, click by partial match
        page.click('.form-step.active label.option-item:has-text("8")')
        take_screenshot(page, "11-timeline-selected")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q11")

        # Q11: Compliance
        print(f"\n=== STEP 12: Selecting Compliance (Q11/12) ===")
        print(f"  Selecting: {TEST_DATA['compliance']}")
        page.click('.form-step.active label.option-item:has-text("Not sure")')
        take_screenshot(page, "12-compliance-selected")
        click_visible_continue(page)
        page.wait_for_timeout(500)
        print("  Clicked Continue -> Moving to Q12")

        # Q12: Anything Else
        print(f"\n=== STEP 13: Filling Anything Else (Q12/12) ===")
        print(f"  Entering: {TEST_DATA['anything_else']}")
        page.fill('.form-step.active textarea', TEST_DATA['anything_else'])
        take_screenshot(page, "13-anything-else-filled")

        # Submit
        print(f"\n=== STEP 14: Submitting Form ===")
        print("  Clicking Submit button...")
        click_visible_submit(page)

        # Wait for submission and success message
        print("  Waiting for form submission...")
        page.wait_for_timeout(3000)  # Wait 3 seconds for form submission
        take_screenshot(page, "14-after-submit")

        # Check for success container
        success_visible = page.is_visible('.success-container.active')

        if success_visible:
            print("\n=== FORM SUBMISSION SUCCESSFUL ===")
            print("  SUCCESS MESSAGE IS VISIBLE!")
            take_screenshot(page, "15-success-message")

            # Get success message text
            success_title = page.query_selector('.success-title')
            if success_title:
                print(f"  Title: {success_title.inner_text()}")
            success_subtitle = page.query_selector('.success-subtitle')
            if success_subtitle:
                print(f"  Subtitle: {success_subtitle.inner_text()}")
        else:
            print("\n=== CHECKING FORM STATE ===")
            # Check what's visible
            active_step = page.query_selector('.form-step.active')
            if active_step:
                print(f"  Still on form step - may be validation error")
            take_screenshot(page, "15-final-state")

        browser.close()

        print(f"\n=== TEST COMPLETE ===")
        print(f"Screenshots saved to: {SCREENSHOT_DIR}")
        return success_visible

if __name__ == "__main__":
    success = run_form_test()
    if success:
        print("\n[PASS] Form test completed successfully - thank you message displayed")
    else:
        print("\n[CHECK] Form test completed - verify screenshots for final state")
