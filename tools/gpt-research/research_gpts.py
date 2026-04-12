#!/usr/bin/env python3
"""
ChatGPT Custom GPT Research Tool

This script uses Playwright to research custom GPTs on ChatGPT.
It launches a browser where you can log in, then navigates to each GPT
and captures their descriptions and capabilities.

Usage:
    python3 research_gpts.py

Requirements:
    - Playwright installed (pip install playwright)
    - ChatGPT account with access to the GPTs

The script will:
1. Launch a browser (not headless so you can log in if needed)
2. Navigate to each GPT URL
3. Take screenshots
4. Extract visible text about each GPT
5. Save a report with findings
"""

from playwright.sync_api import sync_playwright
import os
import json
from datetime import datetime

# Target GPTs to research
TARGET_GPTS = [
    {
        "name": "Personal Brand Copywriter",
        "short_name": "copywriter",
        "url": "https://chatgpt.com/g/g-695a985b2a788191981cb8dd59bcada8-personal-brand-copywriter-writes-like-you-not-ai"
    },
    {
        "name": "LI Social Content Performance Coach",
        "short_name": "li-coach",
        "url": "https://chatgpt.com/g/g-6960371d153c8191bb8bd99c9c40b521-li-social-content-performance-coach"
    },
    {
        "name": "Your Story Selling Social Media Profile Optimizer",
        "short_name": "story-selling",
        "url": "https://chatgpt.com/g/g-695892e1d1e88191a319be1521e401b7-your-story-selling-social-media-profile-optimizer"
    }
]

# Test prompts to send to each GPT
TEST_PROMPTS = [
    "What do you do? Give me a brief overview of your capabilities.",
    "What's your methodology or approach?",
    "Can you give me an example of how you would help me?"
]

# Output directory
OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/docs/research/gpt-analysis"
SCREENSHOT_DIR = f"{OUTPUT_DIR}/screenshots"
BROWSER_DATA_DIR = "/home/jared/projects/AI-CIV/aether/.browser-data/chatgpt"

def ensure_dirs():
    """Create output directories if they don't exist"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(BROWSER_DATA_DIR, exist_ok=True)

def take_screenshot(page, name):
    """Take and save a screenshot"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{name}_{timestamp}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  Screenshot saved: {path}")
    return path

def wait_for_response(page, timeout=30000):
    """Wait for ChatGPT to finish responding"""
    # Wait for the streaming to stop - look for the "Stop generating" button to disappear
    # or for the response to finish loading
    try:
        # Wait for either the copy button (response complete) or timeout
        page.wait_for_selector('button[data-testid="copy-turn-action-button"]', timeout=timeout, state='visible')
        print("  Response received")
    except:
        print("  Timeout waiting for response or different UI")
    # Small additional wait for full render
    page.wait_for_timeout(2000)

def get_visible_text(page, selector=None):
    """Extract visible text from page or selector"""
    try:
        if selector:
            elements = page.query_selector_all(selector)
            return [el.inner_text() for el in elements]
        else:
            return page.inner_text('body')
    except:
        return ""

def research_gpt(page, gpt_info, results):
    """Research a single GPT"""
    print(f"\n{'='*60}")
    print(f"Researching: {gpt_info['name']}")
    print(f"URL: {gpt_info['url']}")
    print(f"{'='*60}")

    gpt_results = {
        "name": gpt_info['name'],
        "url": gpt_info['url'],
        "screenshots": [],
        "initial_description": "",
        "conversation_responses": [],
        "observed_capabilities": [],
        "methodology": "",
        "timestamp": datetime.now().isoformat()
    }

    # Navigate to the GPT
    print("\n1. Navigating to GPT page...")
    page.goto(gpt_info['url'])
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(3000)  # Extra wait for dynamic content

    # Take initial screenshot
    screenshot_path = take_screenshot(page, f"{gpt_info['short_name']}_initial")
    gpt_results['screenshots'].append(screenshot_path)

    # Try to extract the GPT description from the page
    print("\n2. Extracting initial description...")
    try:
        # Look for the GPT description in various possible locations
        description_selectors = [
            '[data-testid="gpt-name"]',
            '[data-testid="gpt-description"]',
            '.gpt-description',
            'h1 + p',  # paragraph after the main heading
        ]
        for selector in description_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    for el in elements:
                        text = el.inner_text()
                        if text:
                            gpt_results['initial_description'] += text + "\n"
            except:
                continue
    except Exception as e:
        print(f"  Could not extract description: {e}")

    # Check if there's a chat input available
    print("\n3. Looking for chat input...")
    chat_input_selectors = [
        '#prompt-textarea',
        'textarea[data-id="root"]',
        'textarea[placeholder*="Message"]',
        '[data-testid="send-button"]',
    ]

    chat_input = None
    for selector in chat_input_selectors:
        try:
            el = page.query_selector(selector)
            if el:
                chat_input = selector
                print(f"  Found chat input: {selector}")
                break
        except:
            continue

    if not chat_input:
        print("  No chat input found - GPT may require authentication or different UI")
        gpt_results['observed_capabilities'].append("Chat interface not accessible - may need auth")
        results['gpts'].append(gpt_results)
        return

    # Send test prompts
    print("\n4. Sending test prompts...")
    for i, prompt in enumerate(TEST_PROMPTS, 1):
        print(f"\n  Prompt {i}: {prompt[:50]}...")

        try:
            # Find and clear the input
            page.fill('#prompt-textarea', '')
            page.wait_for_timeout(500)

            # Type the prompt
            page.fill('#prompt-textarea', prompt)
            page.wait_for_timeout(500)

            # Take screenshot showing prompt
            screenshot_path = take_screenshot(page, f"{gpt_info['short_name']}_prompt{i}")
            gpt_results['screenshots'].append(screenshot_path)

            # Send the message (press Enter or click send button)
            page.keyboard.press('Enter')

            # Wait for response
            print("  Waiting for GPT response...")
            wait_for_response(page)

            # Take screenshot of response
            screenshot_path = take_screenshot(page, f"{gpt_info['short_name']}_response{i}")
            gpt_results['screenshots'].append(screenshot_path)

            # Try to extract the response text
            try:
                # Get the last message in the conversation
                messages = page.query_selector_all('[data-message-author-role="assistant"]')
                if messages:
                    last_response = messages[-1].inner_text()
                    gpt_results['conversation_responses'].append({
                        "prompt": prompt,
                        "response": last_response[:2000]  # Truncate very long responses
                    })
                    print(f"  Response received ({len(last_response)} chars)")
            except Exception as e:
                print(f"  Could not extract response text: {e}")
                gpt_results['conversation_responses'].append({
                    "prompt": prompt,
                    "response": "[Could not extract - see screenshot]"
                })

            page.wait_for_timeout(1000)

        except Exception as e:
            print(f"  Error sending prompt: {e}")
            gpt_results['conversation_responses'].append({
                "prompt": prompt,
                "response": f"[Error: {e}]"
            })

    results['gpts'].append(gpt_results)
    print(f"\nCompleted research for: {gpt_info['name']}")

def generate_report(results):
    """Generate a markdown report from results"""
    report = f"""# ChatGPT Custom GPT Research Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Researcher**: browser-vision-tester (via Playwright automation)

---

## Executive Summary

Researched {len(results['gpts'])} custom GPTs for competitive analysis.

---

"""

    for gpt in results['gpts']:
        report += f"""## {gpt['name']}

**URL**: {gpt['url']}
**Research Time**: {gpt['timestamp']}

### Initial Description
{gpt['initial_description'] or "_No description extracted_"}

### Conversation Analysis

"""
        for i, conv in enumerate(gpt['conversation_responses'], 1):
            report += f"""#### Prompt {i}
> {conv['prompt']}

**Response:**
{conv['response']}

---

"""

        report += f"""### Screenshots
"""
        for ss in gpt['screenshots']:
            report += f"- {ss}\n"

        report += "\n---\n\n"

    return report

def main():
    """Main research function"""
    ensure_dirs()

    results = {
        "timestamp": datetime.now().isoformat(),
        "gpts": []
    }

    print("=" * 60)
    print("ChatGPT Custom GPT Research Tool")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Browser data: {BROWSER_DATA_DIR}")
    print(f"\nTargeting {len(TARGET_GPTS)} GPTs:")
    for gpt in TARGET_GPTS:
        print(f"  - {gpt['name']}")

    print("\nLaunching browser...")
    print("(If not logged in, you'll need to log in to ChatGPT)")
    print()

    with sync_playwright() as p:
        # Launch browser with persistent context (saves login)
        # Using chromium in headed mode so user can see and interact if needed
        context = p.chromium.launch_persistent_context(
            BROWSER_DATA_DIR,
            headless=False,  # Show the browser
            viewport={"width": 1400, "height": 900},
            args=['--disable-blink-features=AutomationControlled']
        )

        page = context.pages[0] if context.pages else context.new_page()

        # First navigate to ChatGPT to ensure we're logged in
        print("Checking ChatGPT login status...")
        page.goto("https://chatgpt.com")
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)

        # Take screenshot of initial state
        take_screenshot(page, "00_chatgpt_initial_state")

        # Check if we need to log in
        login_button = page.query_selector('button:has-text("Log in")')
        if login_button:
            print("\n" + "=" * 60)
            print("NOT LOGGED IN - Please log in to ChatGPT in the browser window")
            print("Script will continue automatically after you log in.")
            print("=" * 60 + "\n")

            # Wait for the user to log in (look for chat input to appear)
            try:
                page.wait_for_selector('#prompt-textarea', timeout=300000)  # 5 minute timeout
                print("Login detected! Continuing...")
                page.wait_for_timeout(3000)
            except:
                print("Login timeout - please try again")
                context.close()
                return
        else:
            print("Already logged in!")

        # Research each GPT
        for gpt in TARGET_GPTS:
            research_gpt(page, gpt, results)

        # Generate and save report
        print("\n" + "=" * 60)
        print("Generating report...")
        report = generate_report(results)

        report_path = f"{OUTPUT_DIR}/GPT-RESEARCH-REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"Report saved: {report_path}")

        # Save raw JSON results
        json_path = f"{OUTPUT_DIR}/gpt-research-results.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Raw data saved: {json_path}")

        print("\n" + "=" * 60)
        print("RESEARCH COMPLETE")
        print("=" * 60)
        print(f"\nResults saved to: {OUTPUT_DIR}/")
        print(f"Screenshots in: {SCREENSHOT_DIR}/")

        # Keep browser open briefly so user can see final state
        print("\nBrowser will close in 10 seconds...")
        page.wait_for_timeout(10000)

        context.close()

if __name__ == "__main__":
    main()
