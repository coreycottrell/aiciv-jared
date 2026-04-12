#!/usr/bin/env python3
"""
Reddit Browser Engagement Tool for PureBrain

Uses Playwright for human-like Reddit engagement.
Monitors subreddits, posts helpful comments, builds karma.

Usage:
    python tools/reddit_engagement.py login-test
    python tools/reddit_engagement.py check-feed
    python tools/reddit_engagement.py comment --url "https://reddit.com/r/..." --text "Your comment"
"""

import asyncio
import os
import sys
import json
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")

REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_EMAIL = os.getenv("REDDIT_EMAIL")

# Target subreddits for PureBrain (from strategy doc)
TARGET_SUBREDDITS = [
    "ChatGPT",
    "ClaudeAI",
    "artificial",
    "smallbusiness",
    "entrepreneur",
    "startups",
    "SaaS",
]

# Browser data directory for persistent session
BROWSER_DATA_DIR = Path(__file__).parent.parent / ".browser-data" / "reddit"
BROWSER_DATA_DIR.mkdir(parents=True, exist_ok=True)

async def create_browser():
    """Create browser with persistent context."""
    from playwright.async_api import async_playwright

    p = await async_playwright().start()
    browser = await p.chromium.launch_persistent_context(
        user_data_dir=str(BROWSER_DATA_DIR),
        headless=True,
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return p, browser

async def login_test():
    """Test Reddit login."""
    print("=" * 50)
    print("REDDIT LOGIN TEST")
    print("=" * 50)
    print(f"Username: {REDDIT_USERNAME}")
    print(f"Email: {REDDIT_EMAIL}")
    print()

    from playwright.async_api import async_playwright

    p, browser = await create_browser()
    page = await browser.new_page()

    try:
        # Go to Reddit
        print("[1] Loading Reddit...")
        await page.goto("https://www.reddit.com", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Check if already logged in
        print("[2] Checking login status...")

        # Look for user menu (indicates logged in)
        try:
            # Reddit has different UI states - check for login button or user avatar
            login_btn = page.locator("a[href*='login'], button:has-text('Log In')")
            if await login_btn.first.is_visible(timeout=3000):
                print("    Not logged in - proceeding to login...")
                await login_btn.first.click()
                await asyncio.sleep(2)
            else:
                print("    May already be logged in...")
        except:
            pass

        # Check if we're on login page or need to login
        current_url = page.url
        print(f"    Current URL: {current_url}")

        # Take screenshot
        screenshot_path = "/tmp/reddit-login-test.png"
        await page.screenshot(path=screenshot_path)
        print(f"    Screenshot: {screenshot_path}")

        # If we see a login form, fill it
        username_field = page.locator("input[name='username'], input[id='loginUsername']")
        if await username_field.first.is_visible(timeout=3000):
            print("[3] Filling login form...")
            await username_field.first.fill(REDDIT_USERNAME)
            await asyncio.sleep(0.5)

            password_field = page.locator("input[name='password'], input[id='loginPassword']")
            await password_field.first.fill(REDDIT_PASSWORD)
            await asyncio.sleep(0.5)

            # Click login button
            login_submit = page.locator("button[type='submit']:has-text('Log In'), button:has-text('Log In')")
            await login_submit.first.click()
            print("    Submitted login form...")
            await asyncio.sleep(5)

            # Take screenshot after login attempt
            await page.screenshot(path="/tmp/reddit-after-login.png")
            print("    Screenshot after login: /tmp/reddit-after-login.png")

        # Verify login by checking for username in page
        print("[4] Verifying login...")
        await asyncio.sleep(2)

        # Check current state
        page_content = await page.content()
        if REDDIT_USERNAME.lower() in page_content.lower():
            print(f"    ✅ SUCCESS: Logged in as {REDDIT_USERNAME}")
            return True
        else:
            # Take final screenshot
            await page.screenshot(path="/tmp/reddit-final-state.png")
            print("    ⚠️ Login status unclear - check /tmp/reddit-final-state.png")
            return False

    except Exception as e:
        print(f"    ❌ Error: {e}")
        await page.screenshot(path="/tmp/reddit-error.png")
        return False
    finally:
        await browser.close()
        await p.stop()

async def check_feed():
    """Check target subreddits for engagement opportunities."""
    print("=" * 50)
    print("REDDIT FEED CHECK")
    print("=" * 50)

    from playwright.async_api import async_playwright

    p, browser = await create_browser()
    page = await browser.new_page()

    opportunities = []

    try:
        for subreddit in TARGET_SUBREDDITS[:3]:  # Check first 3 for now
            print(f"\n[Checking r/{subreddit}]")
            await page.goto(f"https://www.reddit.com/r/{subreddit}/new", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            # Get post titles
            posts = await page.locator("a[data-click-id='body']").all()
            for i, post in enumerate(posts[:5]):
                try:
                    title = await post.text_content()
                    href = await post.get_attribute("href")
                    if title and href:
                        print(f"  {i+1}. {title[:60]}...")
                        opportunities.append({
                            "subreddit": subreddit,
                            "title": title,
                            "url": f"https://www.reddit.com{href}" if href.startswith("/") else href
                        })
                except:
                    continue

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await browser.close()
        await p.stop()

    return opportunities

async def post_comment(url: str, comment_text: str):
    """Post a comment on a Reddit thread."""
    print("=" * 50)
    print("POSTING REDDIT COMMENT")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Comment: {comment_text[:100]}...")
    print()

    from playwright.async_api import async_playwright

    p, browser = await create_browser()
    page = await browser.new_page()

    try:
        # Go to the post
        print("[1] Loading post...")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Find comment box
        print("[2] Looking for comment box...")
        comment_box = page.locator("div[contenteditable='true'], textarea[placeholder*='comment']")

        if await comment_box.first.is_visible(timeout=5000):
            print("[3] Typing comment...")
            await comment_box.first.click()
            await asyncio.sleep(0.5)

            # Type with human-like delays
            for char in comment_text:
                await page.keyboard.type(char, delay=random.randint(30, 80))

            await asyncio.sleep(1)

            # Find and click submit
            print("[4] Submitting...")
            submit_btn = page.locator("button:has-text('Comment'), button[type='submit']")
            await submit_btn.first.click()
            await asyncio.sleep(3)

            await page.screenshot(path="/tmp/reddit-comment-posted.png")
            print("✅ Comment posted! Screenshot: /tmp/reddit-comment-posted.png")
            return True
        else:
            print("❌ Could not find comment box - may need to log in first")
            await page.screenshot(path="/tmp/reddit-no-comment-box.png")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        await page.screenshot(path="/tmp/reddit-comment-error.png")
        return False
    finally:
        await browser.close()
        await p.stop()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "login-test":
        asyncio.run(login_test())
    elif command == "check-feed":
        asyncio.run(check_feed())
    elif command == "comment":
        if "--url" in sys.argv and "--text" in sys.argv:
            url_idx = sys.argv.index("--url") + 1
            text_idx = sys.argv.index("--text") + 1
            url = sys.argv[url_idx]
            text = sys.argv[text_idx]
            asyncio.run(post_comment(url, text))
        else:
            print("Usage: reddit_engagement.py comment --url URL --text 'Comment text'")
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
