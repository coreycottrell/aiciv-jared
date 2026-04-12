"""
Indiegogo Browser — MVP wrapper for campaign automation.
Uses Camoufox + BrowserForge for undetectable browser sessions.

Usage:
    from indiegogo_browser import get_browser
    browser, page = get_browser()
    page.goto("https://www.indiegogo.com")
    # ... your automation here
    browser.close()
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from browser_manager import ProfileManager, launch_profile

PROFILE_NAME = "indiegogo-campaign"

def get_browser(headless=False):
    """Get a fingerprinted, persistent browser session for Indiegogo.
    
    Returns (browser, page) tuple ready for automation.
    Cookies and login state persist across restarts.
    """
    pm = ProfileManager(os.path.join(os.path.dirname(__file__), "profiles"))
    
    # Create profile if it doesn't exist
    if not pm.get_profile(PROFILE_NAME):
        pm.create_profile(
            name=PROFILE_NAME,
            locale="en-US",
            timezone="America/New_York"
        )
    
    browser, page = launch_profile(
        PROFILE_NAME,
        profiles_dir=os.path.join(os.path.dirname(__file__), "profiles"),
        headless=headless,
        humanize=True
    )
    
    return browser, page


if __name__ == "__main__":
    print("Launching Indiegogo browser session...")
    browser, page = get_browser(headless=False)
    page.goto("https://www.indiegogo.com")
    print(f"Page title: {page.title()}")
    input("Press Enter to close...")
    browser.close()
