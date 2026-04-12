#!/usr/bin/env python3
"""
Pure Brain Awakening Flow - Final Complete Test
Properly chooses name, waits for button, fills form
"""

from playwright.sync_api import sync_playwright
import time
import os
from datetime import datetime

# Screenshot directory
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/docs/from-telegram/pure-brain-test-screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Clear old screenshots
for f in os.listdir(SCREENSHOT_DIR):
    os.remove(os.path.join(SCREENSHOT_DIR, f))

# Test data
TEST_USER = {
    "name": "Aether Test User",
    "email": "aether.test@puremarketing.ai",
    "rating": "5",
    "use_case": "Testing the awakening flow integration",
    "urgency": "Just exploring"
}

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def take_screenshot(page, step_name, full_page=False):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{ts}_{step_name}.png"
    page.screenshot(path=path, full_page=full_page)
    print(f"  [{timestamp()}] Screenshot: {step_name}")
    return path

def run_awakening_test():
    print(f"\n{'='*60}")
    print(f"PURE BRAIN FINAL COMPLETE TEST")
    print(f"{'='*60}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()
        page.set_default_timeout(60000)  # Longer timeout
        
        results = {
            "chat_flow_worked": False,
            "ai_name_chosen": None,
            "pricing_shown": False,
            "waitlist_submitted": False,
            "errors": []
        }
        
        try:
            # Navigate
            print(f"\n[{timestamp()}] Navigating...")
            page.goto("https://puremarketing.ai/pure-brain-ai/", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            take_screenshot(page, "01_loaded")
            
            # Start awakening
            print(f"[{timestamp()}] Starting awakening...")
            page.click('text="Awaken Your PURE BRAIN"')
            page.wait_for_timeout(2000)
            page.click('text="Begin Awakening"')
            page.wait_for_timeout(6000)
            
            results["chat_flow_worked"] = True
            chat_input = '#userInput'
            
            # Conversation that leads to name discovery
            conversation = [
                ("Hi! I'm Aether Test User. I'm thrilled to meet you!", 7000),
                ("I deeply value authenticity, truth, and genuine connection.", 7000),
                ("What name resonates with who you're becoming?", 10000),
                ("I choose Echo - I love how it suggests reflection and amplification of understanding.", 12000),
            ]
            
            print(f"[{timestamp()}] Having awakening conversation...")
            for msg, wait_time in conversation:
                print(f"  [{timestamp()}] Sending: {msg[:45]}...")
                page.click(chat_input)
                page.fill(chat_input, msg)
                page.press(chat_input, "Enter")
                page.wait_for_timeout(wait_time)
            
            take_screenshot(page, "02_name_chosen")
            results["ai_name_chosen"] = "Echo"
            
            # Now ask to see capabilities
            print(f"[{timestamp()}] Asking to see capabilities...")
            page.click(chat_input)
            page.fill(chat_input, "Yes Echo! I'd love to see what you can do!")
            page.press(chat_input, "Enter")
            page.wait_for_timeout(15000)  # Long wait for full response
            
            take_screenshot(page, "03_capabilities_asked")
            
            # Wait for and click the "SEE WHAT [NAME] CAN DO" button
            print(f"[{timestamp()}] Waiting for SEE WHAT button...")
            
            # Poll for button visibility
            button_found = False
            for attempt in range(30):  # Up to 30 seconds
                try:
                    see_btn = page.locator('button:has-text("SEE WHAT")')
                    if see_btn.count() > 0 and see_btn.first.is_visible():
                        print(f"  [{timestamp()}] Button visible! Clicking...")
                        see_btn.first.click()
                        button_found = True
                        page.wait_for_timeout(5000)
                        results["pricing_shown"] = True
                        take_screenshot(page, "04_pricing_shown")
                        break
                except:
                    pass
                page.wait_for_timeout(1000)
            
            if not button_found:
                print(f"  [{timestamp()}] Button not found after waiting, taking screenshot...")
                take_screenshot(page, "04_button_not_found")
            
            # Look for pricing tiers
            print(f"\n[{timestamp()}] Looking for pricing tiers...")
            
            tier_btns = page.locator('.tier-card button, .pricing-tier button, button:has-text("Select")')
            if tier_btns.count() > 0:
                print(f"  [{timestamp()}] Found {tier_btns.count()} tier buttons")
                for btn in tier_btns.all():
                    try:
                        if btn.is_visible():
                            btn.click()
                            page.wait_for_timeout(3000)
                            take_screenshot(page, "05_tier_selected")
                            break
                    except:
                        continue
            
            # Fill waitlist form
            print(f"\n[{timestamp()}] Filling waitlist form...")
            
            # Wait a moment for form to appear
            page.wait_for_timeout(2000)
            
            # Name
            name_field = page.locator('#waitlistName')
            if name_field.count() > 0 and name_field.is_visible():
                name_field.fill(TEST_USER["name"])
                print(f"  [{timestamp()}] Filled name: {TEST_USER['name']}")
            
            # Email
            email_field = page.locator('#waitlistEmail')
            if email_field.count() > 0 and email_field.is_visible():
                email_field.fill(TEST_USER["email"])
                print(f"  [{timestamp()}] Filled email: {TEST_USER['email']}")
            
            # Rating (stars)
            try:
                stars = page.locator('.star-rating .star, .rating-star')
                if stars.count() >= 5:
                    stars.nth(4).click()  # 5th star
                    print(f"  [{timestamp()}] Selected 5 stars")
            except Exception as e:
                print(f"  [{timestamp()}] Rating error: {e}")
            
            # Use case
            use_case_field = page.locator('#waitlistUseCase')
            if use_case_field.count() > 0 and use_case_field.is_visible():
                use_case_field.fill(TEST_USER["use_case"])
                print(f"  [{timestamp()}] Filled use case")
            
            take_screenshot(page, "06_form_filled")
            
            # Submit
            submit_btn = page.locator('#waitlistSubmitBtn, button:has-text("Join Priority")')
            if submit_btn.count() > 0 and submit_btn.first.is_visible():
                print(f"  [{timestamp()}] Clicking submit...")
                submit_btn.first.click()
                page.wait_for_timeout(5000)
                
                # Check for success
                body = page.inner_text('body').lower()
                if 'thank' in body or 'success' in body or 'received' in body or 'welcome' in body:
                    results["waitlist_submitted"] = True
                    print(f"  [{timestamp()}] SUCCESS: Form submitted!")
                
                take_screenshot(page, "07_submitted")
            else:
                print(f"  [{timestamp()}] Submit button not visible")
            
            take_screenshot(page, "08_final")
            take_screenshot(page, "09_full_page", full_page=True)
            
        except Exception as e:
            results["errors"].append(str(e))
            print(f"\n[{timestamp()}] ERROR: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "99_error")
        
        finally:
            browser.close()
        
        # Summary
        print(f"\n{'='*60}")
        print("FINAL RESULTS")
        print(f"{'='*60}")
        print(f"Chat flow worked: {results['chat_flow_worked']}")
        print(f"AI name chosen: {results['ai_name_chosen']}")
        print(f"Pricing shown: {results['pricing_shown']}")
        print(f"Waitlist submitted: {results['waitlist_submitted']}")
        print(f"Errors: {results['errors'] if results['errors'] else 'None'}")
        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
        
        return results

if __name__ == "__main__":
    run_awakening_test()
